#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"
FORTYTWO="$ROOT/external/fortytwo"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
FORTYTWO_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
PROJECT="mission-aware-satellite-cyber-recovery"
PHASE="wp4-nominal-runtime-preflight"
DURATION="${DURATION_SECONDS:-60}"
GRACE="${STARTUP_GRACE_SECONDS:-20}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
PREFIX="mascr-$SAFE_ID"
EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
INOUT="$EVIDENCE/fortytwo/NOS3InOut"
MANIFEST="$EVIDENCE/runtime-manifest.txt"
NAMES="$EVIDENCE/container-names.txt"
RESULT="RUN_INVALID"

value() {
  awk -F= -v key="$2" '$1 == key {print substr($0,index($0,"=")+1)}' "$1" | tail -n 1
}

record() {
  printf '%s=%s\n' "$1" "$2" >> "$MANIFEST"
}

capture() {
  local name="$1"
  docker inspect "$name" > "$EVIDENCE/inspect-$name.json" 2>/dev/null || true
  docker logs --timestamps "$name" > "$EVIDENCE/$name.log" 2>&1 || true
}

cleanup() {
  local rc=$?
  set +e
  if [[ -f "$NAMES" ]]; then
    while IFS= read -r name; do
      [[ -n "$name" ]] && capture "$name"
    done < "$NAMES"
  fi
  docker network inspect "$NETWORK" > "$EVIDENCE/network-final.json" 2>/dev/null || true
  docker ps -a --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-final.jsonl" 2>/dev/null || true
  ids="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID")"
  [[ -z "$ids" ]] || docker rm -f $ids >/dev/null 2>&1
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
  record cleanup_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  record terminal_classification "$RESULT"
  record exit_code "$rc"
  if [[ "$RESULT" == RUNTIME_PREFLIGHT_PASS && "$rc" -eq 0 ]]; then
    echo "NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS"
  else
    echo "NOMINAL_RUNTIME_PREFLIGHT_STATUS=FAIL" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
}

for number in "$DURATION" "$GRACE"; do
  [[ "$number" =~ ^[0-9]+$ ]] || { echo "[ERROR] Runtime values must be integers." >&2; exit 1; }
done
(( DURATION >= 30 && DURATION <= 300 )) || { echo "[ERROR] DURATION_SECONDS must be 30-300." >&2; exit 1; }
(( GRACE >= 5 && GRACE <= 60 )) || { echo "[ERROR] STARTUP_GRACE_SECONDS must be 5-60." >&2; exit 1; }

mkdir -p "$EVIDENCE" "$INOUT"
: > "$MANIFEST"
: > "$NAMES"
trap cleanup EXIT
trap 'exit 130' INT TERM

record run_id "$RUN_ID"
record started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record project "$PROJECT"
record phase "$PHASE"
record duration_seconds "$DURATION"
record startup_grace_seconds "$GRACE"
record event_injection disabled

for command in docker git awk shasum python3; do
  command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] Missing command: $command" >&2; exit 1; }
done
docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not reachable." >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2; exit 1; }

NOS3_LOCK="$ROOT/artifacts/nos3-submodule-lock.txt"
FORTYTWO_LOCK="$ROOT/artifacts/fortytwo-lock.txt"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
for file in "$NOS3_LOCK" "$FORTYTWO_LOCK" "$BUILD_LOCK"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing lock: $file" >&2; exit 1; }
done
[[ "$(value "$FORTYTWO_LOCK" fortytwo_build_status)" == PASS ]] || { echo "[ERROR] 42 lock is not PASS." >&2; exit 1; }
[[ "$(value "$BUILD_LOCK" build_status)" == PASS ]] || { echo "[ERROR] NOS3 build lock is not PASS." >&2; exit 1; }
[[ "$(git -C "$NOS3" rev-parse HEAD)" == "$NOS3_COMMIT" ]] || { echo "[ERROR] NOS3 commit mismatch." >&2; exit 1; }
[[ "$(git -C "$FORTYTWO" rev-parse HEAD)" == "$FORTYTWO_COMMIT" ]] || { echo "[ERROR] 42 commit mismatch." >&2; exit 1; }
[[ -z "$(git -C "$NOS3" status --short)" ]] || { echo "[ERROR] NOS3 worktree is not clean." >&2; exit 1; }
[[ -z "$(git -C "$FORTYTWO" status --short)" ]] || { echo "[ERROR] 42 worktree is not clean." >&2; exit 1; }

required=(
  "$NOS3/cfg/build/InOut/Inp_Sim.txt"
  "$NOS3/fsw/build/exe/cpu1/core-cpu1"
  "$NOS3/sims/build/bin/nos3-all-simulators"
  "$NOS3/sims/build/bin/nos3-single-simulator"
  "$NOS3/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$NOS3/sims/build/bin/nos_engine_server_config.json"
  "$NOS3/sims/build/bin/nos3-simulator.xml"
  "$NOS3/gsw/build/support/standalone"
  "$FORTYTWO/42"
)
for file in "${required[@]}"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing runtime artifact: $file" >&2; exit 1; }
done

[[ -z "$(docker ps -aq --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime containers found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}

docker ps -a --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-before.jsonl"
docker network ls --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-networks-before.jsonl"
cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"
python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[i] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
grep -q '^FALSE[[:space:]]*![[:space:]]*Graphics Front End?' "$INOUT/Inp_Sim.txt" || {
  echo "[ERROR] 42 runtime configuration is not headless." >&2
  exit 1
}

record network "$NETWORK"
record network_mode internal_bridge
record nos3_commit "$NOS3_COMMIT"
record fortytwo_commit "$FORTYTWO_COMMIT"
record image "$IMAGE"
record image_id "$(docker image inspect "$IMAGE" --format '{{.Id}}')"
record build_lock_sha256 "$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')"
record runtime_inp_sim_sha256 "$(shasum -a 256 "$INOUT/Inp_Sim.txt" | awk '{print $1}')"

docker network create --driver bridge --internal \
  --label "research.project=$PROJECT" \
  --label "research.phase=$PHASE" \
  --label "research.run_id=$RUN_ID" \
  "$NETWORK" >/dev/null
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]] || {
  echo "[ERROR] Runtime network is not internal." >&2
  exit 1
}
docker network inspect "$NETWORK" > "$EVIDENCE/network-created.json"

start() {
  local logical="$1" alias="$2"
  shift 2
  local name="$PREFIX-$logical"
  docker run -d --platform linux/amd64 --name "$name" --hostname "$alias" \
    --network "$NETWORK" --network-alias "$alias" \
    --label "research.project=$PROJECT" \
    --label "research.phase=$PHASE" \
    --label "research.run_id=$RUN_ID" \
    --log-driver json-file --log-opt max-size=10m --log-opt max-file=2 \
    "$@" >/dev/null
  echo "$name" >> "$NAMES"
}

start engine nos-engine-server \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" /usr/bin/nos_engine_server_standalone -f nos_engine_server_config.json
sleep 2
start time nos-time-driver \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml time
start fortytwo fortytwo \
  --mount "type=bind,source=$FORTYTWO,target=/work/fortytwo,readonly" \
  --mount "type=bind,source=$INOUT,target=/work/fortytwo/NOS3InOut" --workdir /work/fortytwo \
  "$IMAGE" ./42 NOS3InOut
start simulators nos3-simulators \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-all-simulators -f nos3-simulator.xml
start bridge nos-sim-bridge \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-sim-cmdbus-bridge -f nos3-simulator.xml
start cryptolib cryptolib \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/gsw/build \
  "$IMAGE" ./support/standalone
start cfs nos-fsw \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --env USER=nos3 --env LD_LIBRARY_PATH=/work/nos3/fsw/build/exe/cpu1:/usr/lib:/usr/local/lib \
  --workdir /work/nos3/fsw/build/exe/cpu1 --sysctl fs.mqueue.msg_max=10000 \
  --ulimit rtprio=99 --cap-add SYS_NICE \
  "$IMAGE" bash -lc 'exec ./core-cpu1 -R PO'

record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'timestamp_utc,phase,container,state_exit_code\n' > "$EVIDENCE/liveness.csv"
sleep "$GRACE"

check() {
  local phase="$1" failed=0
  while IFS= read -r name; do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    code="$(docker inspect "$name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
    printf '%s,%s,%s,%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$phase" "$name" "$state:$code" >> "$EVIDENCE/liveness.csv"
    [[ "$state" == running ]] || { echo "[ERROR] $name is $state (exit $code)." >&2; failed=1; }
    networks="$(docker inspect "$name" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
    [[ "$networks" == "$NETWORK" ]] || { echo "[ERROR] Unexpected network for $name: $networks" >&2; failed=1; }
    [[ -z "$(docker port "$name")" ]] || { echo "[ERROR] Host port published by $name." >&2; failed=1; }
    docker inspect "$name" --format '{{range .Mounts}}{{println .Source .Destination}}{{end}}' | \
      grep -q '/var/run/docker.sock' && { echo "[ERROR] Docker socket mounted in $name." >&2; failed=1; }
  done < "$NAMES"
  return "$failed"
}

check startup
elapsed=0
while (( elapsed < DURATION )); do
  sleep 5
  elapsed=$((elapsed + 5))
  check "observation-$elapsed"
done

while IFS= read -r name; do
  capture "$name"
  record "log_bytes_$name" "$(wc -c < "$EVIDENCE/$name.log" | tr -d ' ')"
done < "$NAMES"
docker ps --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" \
  --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-running.jsonl"

RESULT="RUNTIME_PREFLIGHT_PASS"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_preflight_status PASS

echo "[OK] Runtime remained live on the project internal network."
echo "[OK] No host ports or Docker-socket mounts were detected."
echo "[OK] Evidence retained at: $EVIDENCE"
