#!/usr/bin/env bash
# Paper 2 P2X Phase A Environment v2: prospectively rebuild NOS3 twice offline.
# Source and July locks remain immutable; does not start NOS3 or issue any command.
set -Eeuo pipefail
MODE="inspect"
if [ "$#" -gt 0 ]; then MODE="$1"; fi
case "$MODE" in inspect|build) ;; *) echo "usage: bash scripts/build_paper2x_phase_a_nos3_v2.sh [inspect|build]" >&2; exit 2;; esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOS3="$ROOT/external/nos3"
FT="$ROOT/external/fortytwo"
AUTH="$ROOT/paper2x/phase_a/ENVIRONMENT_V2_AUTHORIZATION_2026-10-03.json"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
PIN_NOS3="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
PIN_LC="5daef363c95d71c1ff3c5e9dcd4dddab560e8b39"
PIN_HW="d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
PIN_42="eda252bf31f27850e867e698cfdd963e143ead1f"
HASH_42="b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
OUT=""
fail() { echo "P2X_PHASE_A_NOS3_V2_HOLD=$*" >&2; exit 1; }
cleanup() {
  rc=$?
  if [ -n "$OUT" ] && [ -d "$OUT" ]; then
    printf 'terminal_exit_code=%s\n' "$rc" >> "$OUT/operator-status.txt"
    if [ "$rc" -ne 0 ]; then echo "P2X_PHASE_A_BUILD_EVIDENCE=$OUT" >&2; fi
  fi
}
trap cleanup EXIT

test "$(basename "$ROOT")" = "mission-aware-satellite-cyber-recovery" || fail "wrong_project_root"
case "$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)" in
 https://github.com/Zartharas/mission-aware-satellite-cyber-recovery|https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery.git|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery.git) ;;
 *) fail "wrong_research_origin";;
esac
for cmd in git docker python3 shasum awk grep cp du df; do
 command -v "$cmd" >/dev/null 2>&1 || fail "missing_command_$cmd"
done
test -z "$(git -C "$ROOT" status --porcelain)" || fail "research_tree_dirty"
test -f "$AUTH" || fail "v2_authorization_missing"
python3 - "$AUTH" <<'PY'
import json,sys
v=json.load(open(sys.argv[1],encoding="utf8"))
assert v["record_id"]=="P2X-PHASE-A-ENVIRONMENT-V2-AUTHORIZATION-2026-10-03"
assert v["decision"]=="AUTHOR_APPROVED_PROSPECTIVE_V2_CANDIDATE_POLICY"
assert v["nos3"]["independent_builds_required"]==2
assert v["authorization_scope"]["offline_build"] is True
assert v["authorization_scope"]["scientific_fault_campaign"] is False
assert v["environment_final_acceptance"] is False
PY
test -d "$NOS3/.git" || fail "nos3_source_checkout_missing"
test "$(git -C "$NOS3" rev-parse HEAD)" = "$PIN_NOS3" || fail "nos3_revision_drift"
test "$(git -C "$NOS3/fsw/apps/lc" rev-parse HEAD)" = "$PIN_LC" || fail "LC_gitlink_drift"
test "$(git -C "$NOS3/fsw/apps/hwlib" rev-parse HEAD)" = "$PIN_HW" || fail "HWLIB_gitlink_drift"
test -z "$(git -C "$NOS3" status --porcelain)" || fail "nos3_source_dirty"
subdrift="$(git -C "$NOS3" submodule status --recursive | grep -E '^[+-U]' || true)"
test -z "$subdrift" || fail "recursive_submodule_drift"
test -d "$FT/.git" || fail "fortytwo_source_checkout_missing"
test "$(git -C "$FT" rev-parse HEAD)" = "$PIN_42" || fail "fortytwo_revision_drift"
test -z "$(git -C "$FT" status --porcelain)" || fail "fortytwo_source_dirty"
test -f "$FT/42" || fail "fortytwo_candidate_missing"
test "$(shasum -a 256 "$FT/42" | awk '{print $1}')" = "$HASH_42" || fail "v2_fortytwo_candidate_hash_drift"
docker info >/dev/null 2>&1 || fail "docker_unavailable"
test "$(docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}' 2>/dev/null)" = linux/amd64 || fail "locked_image_wrong_arch"
bash "$ROOT/scripts/verify_nos3_source_lock.sh" || fail "source_image_lock_validation"

# Must never overwrite a partial or already populated NOS3 generated directory.
for rel in cfg/build fsw/build sims/build gsw/build; do
 if [ -e "$NOS3/$rel" ] || [ -L "$NOS3/$rel" ]; then
   fail "preexisting_build_dir_no_overwrite:$rel"
 fi
done
for f in artifacts/fortytwo-lock.txt artifacts/nominal-build-lock.txt artifacts/nominal-runtime-preflight-lock.txt artifacts/nos3-submodule-lock.txt; do
 test -s "$ROOT/$f" || fail "historical_lock_missing:$f"
done
echo "P2X_PHASE_A_V2_BUILD_INSPECT=PASS"
echo "fortytwo_candidate_sha256=$HASH_42"
echo "nos3_source=$PIN_NOS3"
echo "offline_image=$IMAGE"
echo "old_NOS3_build_directories=ABSENT"
if [ "$MODE" = inspect ]; then
 echo "P2X_PHASE_A_V2_NOS3_BUILD=NOT_RUN"
 echo "P2X_PHASE_A_V2_RUNTIME=NOT_RUN"
 exit 0
fi

# Check free disk before making independent source copy and generating two build trees.
src_kib="$(du -sk "$NOS3" | awk '{print $1}')"
avail_kib="$(df -Pk "$ROOT" | awk 'NR==2{print $4}')"
test "$avail_kib" -gt "$(( 3 * src_kib + 1048576 ))" || fail "insufficient_disk_for_source_copy_and_offline_build"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
OUT="$ROOT/artifacts/runtime/p2xa-nos3-v2-build-$STAMP"
test ! -e "$OUT" || fail "evidence_collision"
mkdir -p "$OUT/repeat"
SNAPSHOT="$OUT/repeat/source"
ORIGINAL_LOCKS="$OUT/original-locks-sha256.txt"
for f in artifacts/fortytwo-lock.txt artifacts/nominal-build-lock.txt artifacts/nominal-runtime-preflight-lock.txt artifacts/nos3-submodule-lock.txt; do
 shasum -a 256 "$ROOT/$f" >> "$ORIGINAL_LOCKS"
done
printf 'P2X_ENV_V2_BUILD_STARTED_UTC=%s\npin_source=%s\npin_image=%s\nfortytwo_candidate=%s\nnetwork=none\nhistorical_locks_unchanged_required=YES\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PIN_NOS3" "$IMAGE" "$HASH_42" > "$OUT/build-provenance.txt"

# Capture the independent source copy BEFORE the first compile.
cp -R "$NOS3" "$SNAPSHOT"
test -d "$SNAPSHOT/.git" || fail "independent_source_git_missing"
test "$(git -C "$SNAPSHOT" rev-parse HEAD)" = "$PIN_NOS3" || fail "independent_source_pin_drift"
test -z "$(git -C "$SNAPSHOT" status --porcelain)" || fail "independent_source_dirty"
repeatdrift="$(git -C "$SNAPSHOT" submodule status --recursive | grep -E '^[+-U]' || true)"
test -z "$repeatdrift" || fail "independent_source_recursive_submodule_drift"
for rel in cfg/build fsw/build sims/build gsw/build; do
 if [ -e "$SNAPSHOT/$rel" ] || [ -L "$SNAPSHOT/$rel" ]; then fail "independent_copy_contains_build_outputs:$rel"; fi
done
echo "P2X_PHASE_A_INDEPENDENT_SOURCE_COPY=PASS"

build_once() {
 label="$1"
 source="$2"
 echo "P2X_NOS3_V2_BUILD_CANDIDATE=$label"
 docker run --rm --platform linux/amd64 --network none \
   --user "$(id -u):$(id -g)" -e HOME=/tmp \
   --mount "type=bind,source=$source,target=/work/nos3" \
   --workdir /work/nos3 "$IMAGE" \
   bash -lc '
     set -Eeuo pipefail
     printf "container_workdir=%s\n" "$(pwd -P)"
     gcc --version | head -n 1
     ld --version | head -n 1
     bash ./scripts/cfg/config.sh
     make build-fsw
     make build-sim
     make build-cryptolib
   ' 2>&1 | tee "$OUT/$label-build.log"
 test -z "$(git -C "$source" status --porcelain)" || fail "source_mutated_after_build:$label"
}

build_once primary "$NOS3"
build_once repeat "$SNAPSHOT"

python3 - "$ROOT" "$NOS3" "$SNAPSHOT" "$OUT" "$IMAGE" "$HASH_42" <<'PY'
from pathlib import Path
import hashlib,json,sys,datetime
root,primary,repeat,out=map(Path,sys.argv[1:5])
image,ft=sys.argv[5:7]
five=["cfg/build/launch.sh","fsw/build/exe/cpu1/core-cpu1",
      "sims/build/bin/nos3-single-simulator","sims/build/bin/nos3-sim-cmdbus-bridge",
      "gsw/build/support/standalone"]
additional=["cfg/build/InOut/Inp_Sim.txt","cfg/build/InOut/Inp_IPC.txt",
            "sims/build/bin/nos_engine_server_config.json","sims/build/bin/nos3-simulator.xml"]
historic={}
inside=False
for line in (root/"artifacts/nominal-build-lock.txt").read_text().splitlines():
    if line=="artifact_sha256_begin":inside=True;continue
    if line=="artifact_sha256_end":break
    if inside:
        parts=line.split()
        if len(parts)==2:
            for rel in five:
                if parts[1].endswith("/external/nos3/"+rel):
                    historic[rel]=parts[0]
assert set(historic)==set(five),"HISTORIC_HASH_INVENTORY_INCOMPLETE"
def digest(path):
    assert path.is_file() and path.stat().st_size>0, "MISSING_OR_EMPTY:"+str(path)
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
data=[]
for rel in five+additional:
    a,b=digest(primary/rel),digest(repeat/rel)
    data.append({"path":rel,"sha256_primary":a,"sha256_repeat":b,
       "repeat_match":a==b,"july_reference_sha256":historic.get(rel),
       "july_reference_match":a==historic[rel] if rel in historic else None})
with (out/"artifact-hash-comparison.tsv").open("w") as f:
    f.write("relative_path\tprimary_sha256\trepeat_sha256\trepeat_match\tjuly_reference_sha256\tjuly_reference_match\n")
    for d in data:
        f.write("\t".join(str(d[k]) for k in ("path","sha256_primary","sha256_repeat",
                                            "repeat_match","july_reference_sha256","july_reference_match"))+"\n")
match=all(d["repeat_match"] for d in data)
manifest={"schema":1,"experiment_id":"P2X-NOS3-RG-001",
 "phase":"PHASE_A_ENVIRONMENT_V2_OFFLINE_BUILD_ONLY",
 "classification":"TWO_INDEPENDENT_OFFLINE_BUILDS_MATCH__RUNTIME_UNTESTED" if match else "BUILD_BYTE_REPRODUCTION_HOLD",
 "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "nos3_revision":"5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
 "fortytwo_revision":"eda252bf31f27850e867e698cfdd963e143ead1f",
 "fortytwo_p2x_sha256":ft,
 "image":image,"image_platform":"linux/amd64","network":"none",
 "build_recipe":["bash ./scripts/cfg/config.sh","make build-fsw","make build-sim","make build-cryptolib"],
 "primary_source_root":str(primary),"repeat_source_root":str(repeat),
 "artifacts":data,"required_artifact_count":len(data),
 "repeat_match_all":match,"historical_july_build_lock_replaced":False,
 "no_runtime_performed":True,"no_scientific_observations":True,
 "environment_final_acceptance":False}
m=out/"p2x-v2-build-manifest.json"
m.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print("P2X_PHASE_A_V2_BUILD_MANIFEST="+str(m))
print("P2X_PHASE_A_V2_9_ARTIFACT_REPEAT_MATCH="+("PASS" if match else "HOLD"))
print("P2X_PHASE_A_V2_HISTORICAL_JULY_COMPARISON=DESCRIPTIVE_ONLY")
if not match:raise SystemExit("P2X_V2_OFFLINE_BUILD_NONDETERMINISTIC_HOLD")
PY

shasum -a 256 -c "$ORIGINAL_LOCKS" || fail "historical_lock_modified_by_v2_build"
test -z "$(git -C "$ROOT" status --porcelain)" || fail "research_tracked_files_mutated"
test -z "$(git -C "$NOS3" status --porcelain)" || fail "nos3_tracked_files_mutated"
test -z "$(git -C "$FT" status --porcelain)" || fail "fortytwo_tracked_files_mutated"
test "$(shasum -a 256 "$FT/42" | awk '{print $1}')" = "$HASH_42" || fail "fortytwo_candidate_changed"
python3 "$ROOT/scripts/verify_paper2x_phase_a_v2.py" "$OUT/p2x-v2-build-manifest.json" || fail "independent_manifest_validation"
echo "P2X_PHASE_A_V2_OFFLINE_BUILD=PASS"
echo "P2X_PHASE_A_V2_ENVIRONMENT_FINAL_ACCEPTANCE=NO"
echo "P2X_PHASE_A_V2_RUNTIME_EXECUTED=NO"
echo "P2X_PHASE_A_V2_EVIDENCE=$OUT"
