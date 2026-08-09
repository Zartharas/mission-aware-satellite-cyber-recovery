#!/usr/bin/env bash
# WP4 v3 passive time-witness runtime-candidate generator. Emit only.
set -Eeuo pipefail

readonly V2_GENERATOR_SHA256="504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b"

fail() {
  echo "[ERROR] $*" >&2
  exit 2
}

canonicalize() {
  python3 - "$1" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
}

emit_path_raw="${PASSIVE_TIME_WITNESS_V3_EMIT_PATH:-}"
[[ -n "$emit_path_raw" ]] || fail "PASSIVE_TIME_WITNESS_V3_EMIT_PATH is required."
command -v python3 >/dev/null 2>&1 || fail "python3 is required."
command -v git >/dev/null 2>&1 || fail "git is required."

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || \
  fail "Run the generator from within the governed repository."
repo_root="$(cd "$repo_root" && pwd -P)"
v2_generator="$repo_root/scripts/prepare_passive_time_witness_runtime_candidate_v2.sh"
[[ -f "$v2_generator" && ! -L "$v2_generator" ]] || fail "Protected v2 generator is not a regular file."
[[ "$(shasum -a 256 "$v2_generator" | awk '{print $1}')" == "$V2_GENERATOR_SHA256" ]] || \
  fail "Protected v2 generator identity mismatch."

emit_parent_raw="$(dirname "$emit_path_raw")"
emit_leaf="$(basename "$emit_path_raw")"
[[ "$emit_leaf" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ && "$emit_leaf" != "." && "$emit_leaf" != ".." ]] || \
  fail "Invalid emit filename."
[[ -d "$emit_parent_raw" && ! -L "$emit_parent_raw" ]] || \
  fail "Emit parent must be an existing non-symlink directory."

emit_parent_real="$(canonicalize "$emit_parent_raw")"
emit_path_real="$emit_parent_real/$emit_leaf"
tmp_root_real="$(canonicalize "${TMPDIR:-/tmp}")"
repo_root_real="$(canonicalize "$repo_root")"
repo_review_root="$repo_root_real/review-evidence"

allowed=0
repository_local=0

case "$emit_path_real" in
  "$tmp_root_real"/*) allowed=1 ;;
esac

review_dir_raw="${PASSIVE_TIME_WITNESS_V3_REVIEW_DIR:-}"
if [[ -n "$review_dir_raw" ]]; then
  [[ -d "$review_dir_raw" && ! -L "$review_dir_raw" ]] || \
    fail "PASSIVE_TIME_WITNESS_V3_REVIEW_DIR must be an existing non-symlink directory."

  review_dir_real="$(canonicalize "$review_dir_raw")"

  case "$emit_path_real" in
    "$review_dir_real"/*)
      case "$review_dir_real" in
        "$repo_root_real"|"$repo_root_real"/*)
          case "$review_dir_real" in
            "$repo_review_root"|"$repo_review_root"/*) ;;
            *)
              fail "Repository-local review root must be beneath review-evidence."
              ;;
          esac

          case "$emit_path_real" in
            "$repo_review_root"/*) ;;
            *)
              fail "Repository-local emit path must be beneath review-evidence."
              ;;
          esac

          python3 - \
            "$repo_root_real" \
            "$repo_review_root" \
            "$review_dir_raw" \
            "$review_dir_real" \
            "$emit_parent_raw" \
            "$emit_parent_real" <<'PY_NOSYMLINK'
import os
import stat
import sys

root = os.path.realpath(sys.argv[1])
review_root = os.path.realpath(sys.argv[2])

raw_and_physical = (
    (sys.argv[3], sys.argv[4]),
    (sys.argv[5], sys.argv[6]),
)

for raw_target, expected_physical in raw_and_physical:
    lexical_target = os.path.abspath(raw_target)
    physical_target = os.path.realpath(lexical_target)

    if physical_target != expected_physical:
        raise SystemExit(1)

    try:
        lexical_common = os.path.commonpath((root, lexical_target))
        physical_common = os.path.commonpath((root, physical_target))
        review_common = os.path.commonpath(
            (review_root, physical_target)
        )
    except ValueError:
        raise SystemExit(1)

    if lexical_common != root:
        raise SystemExit(1)

    if physical_common != root:
        raise SystemExit(1)

    if review_common != review_root:
        raise SystemExit(1)

    relative = os.path.relpath(lexical_target, root)

    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        raise SystemExit(1)

    current = root

    if relative == ".":
        continue

    for component in relative.split(os.sep):
        current = os.path.join(current, component)
        current_stat = os.lstat(current)

        if stat.S_ISLNK(current_stat.st_mode):
            raise SystemExit(1)
PY_NOSYMLINK

          candidate_relative="${emit_path_real#"$repo_root_real"/}"

          git -C "$repo_root_real" \
            check-ignore \
            -q \
            --no-index \
            -- "$candidate_relative" || \
            fail "Repository-local candidate path is not Git-ignored."

          repository_local=1
          allowed=1
          ;;
        *)
          allowed=1
          ;;
      esac
      ;;
  esac
fi

(( allowed == 1 )) || \
  fail "Emit path escapes approved temporary/review roots."

if (( repository_local == 0 )); then
  case "$emit_path_real" in
    "$repo_root_real"|"$repo_root_real"/*)
      fail "Emit path targets an unapproved repository location."
      ;;
  esac
fi

case "$emit_path_real" in
  */.git/*|*/artifacts/*|*/configs/*|*/tracker/*|*/evidence/*|*/data/*|*/manifests/*|*/external/*)
    fail "Emit path targets a retained-state directory."
    ;;
esac

[[ ! -e "$emit_path_real" && ! -L "$emit_path_real" ]] || \
  fail "Emit destination already exists."

umask 077
v2_tmp_dir="$(mktemp -d "$tmp_root_real/.wp4-v3-v2.XXXXXX")"
base_candidate="$v2_tmp_dir/candidate-v2.sh"
tmp_emit="$(mktemp "$emit_parent_real/.${emit_leaf}.v3.XXXXXX")"

cleanup_emit() {
  local rc=$?

  rm -f -- "$base_candidate" "$tmp_emit"
  rmdir "$v2_tmp_dir" 2>/dev/null || true

  trap - EXIT
  exit "$rc"
}
trap cleanup_emit EXIT

PASSIVE_TIME_WITNESS_V2_EMIT_PATH="$base_candidate" \
  PASSIVE_TIME_WITNESS_V2_REVIEW_DIR="$v2_tmp_dir" \
  bash "$v2_generator" >/dev/null

[[ -f "$base_candidate" && ! -L "$base_candidate" ]] || \
  fail "v2 candidate emission failed."

python3 - "$base_candidate" "$tmp_emit" <<'PYTRANSFORM'
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
output = pathlib.Path(sys.argv[2])

source = source.replace("V2", "V3").replace("v2", "v3")

start = source.index('ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"')
end_marker = 'echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_GATE=AUTHORIZED"'
end = source.index(end_marker, start) + len(end_marker)

prelude = r'''ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[FAIL-CLOSED] candidate must be launched from within the governed repository." >&2
  echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
}
ROOT="$(cd "$ROOT" && pwd -P)"
cd "$ROOT"
NOS3="$ROOT/external/nos3"
FORTYTWO="$ROOT/external/fortytwo"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
FORTYTWO_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
PROJECT="mission-aware-satellite-cyber-recovery"
PHASE="wp4-passive-time-witness-v3"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
PREFIX="mascr-$SAFE_ID"

readonly OBSERVATION_DURATION_SECONDS=70
readonly READINESS_TIMEOUT_SECONDS=60
readonly DOCKER_STOP_GRACE_SECONDS=10
readonly CLEANUP_COMMAND_TIMEOUT_SECONDS=15
readonly NETWORK_REMOVAL_TIMEOUT_SECONDS=15
readonly POST_CLEANUP_ASSERT_RETRIES=10
readonly POST_CLEANUP_RETRY_INTERVAL_SECONDS=1
readonly BASELINE_TIMEOUT=240
readonly PROBE_READINESS_TIMEOUT=150
readonly ACCEPTANCE_TIMEOUT=30

CONTRACT_PATH="$ROOT/configs/downlink-diagnostic-contract.json"
CANONICAL_MANIFEST="$ROOT/manifests/nos3-runtime-material-manifest.json"
TRANSACTION_TOOL="$ROOT/scripts/nos3_runtime_transaction_v1.py"
CANDIDATE_SELF="$(python3 - "${BASH_SOURCE[0]:-$0}" <<'PYSELF'
import os, sys
print(os.path.realpath(sys.argv[1]))
PYSELF
)"
DOCKER_BIN="docker"

EVIDENCE="$ROOT/artifacts/downlink-diagnostics/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
PROBE_GROUND="$GROUND/probe"
ORCHESTRATION="$GROUND/orchestration"
WITNESS_SCRIPT="$ORCHESTRATION/telemetry_path_witness_v3.py"
SOCKET_METADATA_DIR="$GROUND/radio-socket-metadata"
SHIM_BUILD_DIR="$ORCHESTRATION/radio-socket-shim"
SHIM_SOURCE="$ROOT/scripts/radio_socket_metadata_shim.c"
SHIM_SO="$SHIM_BUILD_DIR/libradio_socket_metadata_shim.so"
SOCKET_TRACE="$SOCKET_METADATA_DIR/radio-socket-metadata.log"
EXPECTED_SHIM_SOURCE_SHA256="d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b"
EXPECTED_SHIM_SO_SHA256="5a1e4f0cb2b5567ee70defa893f7c976453c788b6c9ac70e4f7d646c16223205"
PASSIVE_WITNESS_SOURCE="$ROOT/scripts/passive_nos_engine_time_witness.cpp"
PASSIVE_WITNESS_VALIDATOR="$ROOT/scripts/validate_passive_time_witness_trace.py"
PASSIVE_WITNESS_DIR="$GROUND/passive-time-witness"
PASSIVE_WITNESS_TRACE="$PASSIVE_WITNESS_DIR/trace.jsonl"
PASSIVE_WITNESS_LAUNCHER="$ORCHESTRATION/passive-time-witness-launcher.sh"
PASSIVE_WITNESS_CORRELATION="$PASSIVE_WITNESS_DIR/correlation-summary.json"
POLICY="$EVIDENCE/policy-visible"
FORTYTWO_INOUT_CONTAINER="/work/fortytwo-inout"
RUNTIME_SIM_CONFIG="$ORCHESTRATION/runtime-config/nos3-simulator.xml"
MANIFEST="$ORCHESTRATION/runtime-manifest.txt"
NAMES="$ORCHESTRATION/container-names.txt"
RUNTIME_NAMES="$ORCHESTRATION/runtime-container-names.txt"
LIVENESS="$ORCHESTRATION/liveness.csv"
ROOT_HASH_LOCK="$EVIDENCE/evidence-root-hashes.txt"
RESULT="PASSIVE_TIME_WITNESS_RUNTIME_INVALID"
NETWORK_CREATED=0
CREATED_CONTAINERS=()
TRANSACTION_PUBLISHED=0

command -v python3 >/dev/null 2>&1 || {
  echo "[FAIL-CLOSED] python3 is required for authorization validation." >&2
  echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
}

if ! python3 - "$ROOT" "$CONTRACT_PATH" "$CANDIDATE_SELF" "$TRANSACTION_TOOL" "$CANONICAL_MANIFEST" <<'PYGATE'
import hashlib, json, os, stat, sys

root, contract_path, candidate_path, tool_path, manifest_path = sys.argv[1:]

def closed(condition):
    if not condition:
        raise SystemExit(1)

def read_regular(path):
    st = os.stat(path, follow_symlinks=False)
    closed(stat.S_ISREG(st.st_mode) and st.st_nlink == 1)
    with open(path, "rb") as stream:
        raw = stream.read()
    st2 = os.stat(path, follow_symlinks=False)
    closed((st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_size) ==
           (st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size))
    closed(len(raw) == st.st_size)
    return raw, hashlib.sha256(raw).hexdigest()

try:
    contract_raw, contract_sha = read_regular(contract_path)
    candidate_raw, candidate_sha = read_regular(candidate_path)
    tool_raw, tool_sha = read_regular(tool_path)
    manifest_raw, manifest_sha = read_regular(manifest_path)
    contract = json.loads(contract_raw.decode("utf-8"))
except Exception:
    raise SystemExit(1)

closed(isinstance(contract, dict))
gate = contract.get("gate")
amendment = contract.get("passive_time_witness_runtime_candidate_v3_design_amendment_1")
closed(isinstance(gate, dict) and isinstance(amendment, dict))
closed(type(gate.get("passive_time_witness_runtime_candidate_v3_contract_schema")) is int)
closed(gate["passive_time_witness_runtime_candidate_v3_contract_schema"] == 1)
closed(gate.get("passive_time_witness_runtime_candidate_v3_static_verification") == "PASS")
accepted = gate.get("accepted_runtime_entrypoint_v3_sha256")
closed(type(accepted) is str and len(accepted) == 64)
closed(accepted == accepted.lower() and all(c in "0123456789abcdef" for c in accepted))
closed(accepted == candidate_sha)
closed(gate.get("accepted_runtime_entrypoint_v3_identity_only_not_authorized") is False)
closed(type(gate.get("diagnostic_runtime_authorized")) is bool)
closed(gate["diagnostic_runtime_authorized"] is True)
closed(type(gate.get("diagnostic_runtime_attempts_authorized")) is int)
closed(gate["diagnostic_runtime_attempts_authorized"] == 1)
for key in ("scientific_outcome_allowed", "event_injection_allowed",
            "command_transmission_allowed", "baseline_execution_allowed",
            "cryptographic_semantics_claim_allowed"):
    closed(type(contract.get(key)) is bool and contract[key] is False)
for key in ("baseline_run_1_authorized", "baseline_run_2_authorized",
            "event_injection_authorized"):
    closed(type(gate.get(key)) is bool and gate[key] is False)
closed(type(amendment.get("runtime_authorized")) is bool)
closed(amendment["runtime_authorized"] is True)
closed(type(amendment.get("runtime_attempts")) is int)
closed(amendment["runtime_attempts"] == 1)
closed(amendment.get("d064_status") == "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT")
implementation = amendment.get("passive_time_witness_runtime_candidate_v3_implementation")
closed(isinstance(implementation, dict))
tool = implementation.get("runtime_material_tool")
manifest = implementation.get("canonical_manifest")
closed(isinstance(tool, dict) and isinstance(manifest, dict))
closed(tool.get("path") == "scripts/nos3_runtime_transaction_v1.py")
closed(tool.get("sha256") == tool_sha)
closed(manifest.get("path") == "manifests/nos3-runtime-material-manifest.json")
closed(manifest.get("sha256") == manifest_sha)
closed(os.path.realpath(root) == root)
PYGATE
then
  echo "[FAIL-CLOSED] passive time-witness v3 runtime is not authorized by the current contract." >&2
  echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
fi

if ! python3 - "$ROOT" "$CANDIDATE_SELF" <<'PY_LOCAL_CANDIDATE'
import os
import sys

root = os.path.realpath(sys.argv[1])
candidate = os.path.realpath(sys.argv[2])

try:
    common = os.path.commonpath((root, candidate))
except ValueError:
    raise SystemExit(1)

raise SystemExit(
    0
    if common == root and candidate != root
    else 1
)
PY_LOCAL_CANDIDATE
then
  echo "[FAIL-CLOSED] authorized candidate must be physically repository-local." >&2
  echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
fi

echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_GATE=AUTHORIZED"'''

source = source[:start] + prelude + source[end:]

transaction = r'''

AUTHORIZED_TRANSACTION_ROOT="${PASSIVE_TIME_WITNESS_V3_AUTHORIZED_ROOT:-}"
[[ -n "$AUTHORIZED_TRANSACTION_ROOT" ]] || {
  echo "[ERROR] PASSIVE_TIME_WITNESS_V3_AUTHORIZED_ROOT is required after authorization." >&2
  exit 1
}
TRANSACTION_BASENAME="wp4-passive-time-witness-v3-$SAFE_ID"
TRANSACTION_DIR="$AUTHORIZED_TRANSACTION_ROOT/$TRANSACTION_BASENAME"
WS_NOS_ENGINE="$TRANSACTION_DIR/workspaces/nos_engine/work/nos3"
WS_TIME_DRIVER="$TRANSACTION_DIR/workspaces/time_driver/work/nos3"
WS_CMD_BUS_BRIDGE="$TRANSACTION_DIR/workspaces/cmd_bus_bridge/work/nos3"
WS_CFS="$TRANSACTION_DIR/workspaces/cfs/work/nos3"
INOUT="$TRANSACTION_DIR/fortytwo-config/cfg/build/InOut"

cleanup_transaction_only() {
  local rc=$?
  trap - EXIT INT TERM HUP
  set +e
  if (( TRANSACTION_PUBLISHED == 1 )) && [[ "$TRANSACTION_DIR" == "$AUTHORIZED_TRANSACTION_ROOT/$TRANSACTION_BASENAME" ]]; then
    rm -rf -- "$TRANSACTION_DIR"
  fi
  exit "$rc"
}
trap cleanup_transaction_only EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

if ! transaction_output="$(python3 "$TRANSACTION_TOOL" \
  --materialize-v3-transaction \
  --repo-root "$ROOT" \
  --contract "$CONTRACT_PATH" \
  --manifest "$CANONICAL_MANIFEST" \
  --candidate "$CANDIDATE_SELF" \
  --authorized-root "$AUTHORIZED_TRANSACTION_ROOT" \
  --final-basename "$TRANSACTION_BASENAME")"; then
  echo "[ERROR] v3 transaction materialization failed." >&2
  exit 1
fi
[[ "$transaction_output" == "V3_TRANSACTION_MATERIALIZATION=PASS" ]] || {
  echo "[ERROR] transaction output did not contain exactly one exact success marker." >&2
  exit 1
}
TRANSACTION_PUBLISHED=1

python3 - "$ROOT" "$CONTRACT_PATH" "$CANDIDATE_SELF" "$TRANSACTION_TOOL" \
  "$CANONICAL_MANIFEST" "$AUTHORIZED_TRANSACTION_ROOT" "$TRANSACTION_BASENAME" <<'PYRECEIPT'
import hashlib, json, os, stat, sys

(root, contract_path, candidate_path, tool_path, manifest_path,
 authorized_root, final_basename) = sys.argv[1:]
transaction = os.path.join(authorized_root, final_basename)
receipt_path = os.path.join(transaction, "transaction-receipt.json")

def require(value, message):
    if not value:
        raise SystemExit(message)

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

raw = open(receipt_path, "rb").read()
require(not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw,
        "receipt encoding invalid")
require(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
        "receipt final LF invalid")
receipt = json.loads(raw.decode("utf-8"))
canonical = (json.dumps(receipt, ensure_ascii=True, sort_keys=True,
                        separators=(",", ":")) + "\n").encode("utf-8")
require(raw == canonical, "receipt serialization is not canonical")

expected_keys = {
    "receipt_schema", "status", "final_basename", "transaction_tool_sha256",
    "repository", "contract", "candidate", "executing_tool",
    "canonical_manifest", "authorized_root", "component_ids",
    "component_count", "workspace_count", "fortytwo_scratch_disposition",
    "fortytwo_scratch_present", "workspaces", "aggregate_included_file_count",
    "aggregate_included_byte_count", "aggregate_directory_count",
    "aggregate_exclusion_count", "collision_counts",
    "no_replace_publication_disposition", "publication_method",
    "runtime_attempt", "d064_disposition", "exclusive_writer_prerequisite",
    "runtime_authorized", "runtime_attempts", "docker_invoked",
}
require(set(receipt) == expected_keys, "receipt fields do not match production schema")
component_ids = (["cfs", "cmd_bus_bridge"] +
                 ["hw_sim_%02d" % i for i in range(1, 15)] +
                 ["nos_engine", "time_driver"])
require(type(receipt["receipt_schema"]) is int and receipt["receipt_schema"] == 1,
        "receipt schema invalid")
require(receipt["status"] == "TRANSACTION_COMPLETE_PENDING_PUBLICATION",
        "receipt status invalid")
require(receipt["final_basename"] == final_basename, "final basename mismatch")
require(receipt["component_ids"] == component_ids, "component IDs mismatch")
require(type(receipt["component_count"]) is int and receipt["component_count"] == 18,
        "component count invalid")
require(type(receipt["workspace_count"]) is int and receipt["workspace_count"] == 18,
        "workspace count invalid")
require(receipt["fortytwo_scratch_disposition"] == "SEPARATE_NOT_COUNTED_AS_WORKSPACE",
        "Fortytwo disposition invalid")
require(receipt["fortytwo_scratch_present"] is True, "Fortytwo presence invalid")
require(type(receipt["aggregate_included_file_count"]) is int and
        receipt["aggregate_included_file_count"] == 1822,
        "aggregate file count invalid")
require(type(receipt["aggregate_included_byte_count"]) is int and
        receipt["aggregate_included_byte_count"] == 971336386,
        "aggregate byte count invalid")
require(type(receipt["aggregate_directory_count"]) is int and
        receipt["aggregate_directory_count"] == 121,
        "aggregate directory count invalid")
require(type(receipt["aggregate_exclusion_count"]) is int and
        receipt["aggregate_exclusion_count"] == 43,
        "aggregate exclusion count invalid")
require(receipt["collision_counts"] == {
    "duplicate_file_target_count": 0,
    "duplicate_directory_target_count": 0,
    "file_directory_collision_count": 0,
    "prefix_collision_count": 0,
}, "collision counts invalid")
require(receipt["no_replace_publication_disposition"] == "ATOMIC_NOREPLACE_PUBLISHED",
        "publication disposition invalid")
expected_publication = ("renameatx_np_RENAME_EXCL" if sys.platform == "darwin"
                        else "renameat2_RENAME_NOREPLACE")
require(receipt["publication_method"] == expected_publication,
        "publication method invalid")
require(type(receipt["runtime_attempt"]) is int and receipt["runtime_attempt"] == 1,
        "runtime attempt invalid")
require(receipt["d064_disposition"] == "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT",
        "D-064 disposition invalid")
require(receipt["exclusive_writer_prerequisite"] ==
        "SATISFIED_DEEP_IMMUTABLE_CONTEXT", "exclusive-writer reference invalid")
require(receipt["runtime_authorized"] is False and
        type(receipt["runtime_attempts"]) is int and receipt["runtime_attempts"] == 0 and
        receipt["docker_invoked"] is False, "transaction boundary fields invalid")

repo_st = os.stat(root, follow_symlinks=False)
root_st = os.stat(authorized_root, follow_symlinks=False)
require(receipt["repository"] == {"dev": repo_st.st_dev, "inode": repo_st.st_ino},
        "repository identity mismatch")
require(receipt["authorized_root"] == {"device": root_st.st_dev, "inode": root_st.st_ino},
        "authorized-root identity mismatch")

def validate_file_record(key, path):
    st = os.stat(path, follow_symlinks=False)
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, key + " not regular/nlink1")
    rel = os.path.relpath(os.path.realpath(path), root)
    expected = {"relative_path": rel, "device": st.st_dev, "inode": st.st_ino,
                "size": st.st_size, "mode": st.st_mode, "nlink": st.st_nlink,
                "sha256": sha(path)}
    require(receipt[key] == expected, key + " identity mismatch")

validate_file_record("contract", contract_path)
validate_file_record("candidate", candidate_path)
validate_file_record("executing_tool", tool_path)
validate_file_record("canonical_manifest", manifest_path)
require(receipt["transaction_tool_sha256"] == sha(tool_path),
        "transaction tool SHA mismatch")

workspaces = receipt["workspaces"]
require(type(workspaces) is list and len(workspaces) == 18,
        "workspace receipt list invalid")
seen_inodes = set()
for index, component_id in enumerate(component_ids):
    record = workspaces[index]
    simulator = component_id != "cfs"
    expected = {
        "component_id": component_id,
        "relative_root": "workspaces/%s/work/nos3" % component_id,
        "file_count": 25 if simulator else 1361,
        "byte_count": 54427517 if simulator else 45877946,
        "directory_count": 2 if simulator else 86,
        "exclusion_count": 2 if simulator else 9,
        "verification": "VERIFIED",
    }
    require(record == expected, "workspace receipt mismatch: " + component_id)
    path = os.path.join(transaction, record["relative_root"])
    st = os.stat(path, follow_symlinks=False)
    require(stat.S_ISDIR(st.st_mode) and not os.path.islink(path),
            "workspace root invalid: " + component_id)
    require((st.st_dev, st.st_ino) not in seen_inodes,
            "workspace root identity alias: " + component_id)
    seen_inodes.add((st.st_dev, st.st_ino))

manifest = json.load(open(manifest_path, encoding="utf-8"))
fortytwo_root = os.path.join(transaction, "fortytwo-config")
require(os.path.isdir(fortytwo_root) and not os.path.islink(fortytwo_root),
        "Fortytwo scratch root invalid")
configuration = [e for e in manifest["included_regular_file_entries"]
                 if e.get("source_root") == "configuration"]
require(len(configuration) == 36, "Fortytwo manifest file count invalid")
for entry in configuration:
    path = os.path.join(fortytwo_root, entry["destination_relative"])
    st = os.stat(path, follow_symlinks=False)
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1,
            "Fortytwo scratch file invalid")
    require(st.st_size == entry["size"] and sha(path) == entry["sha256"],
            "Fortytwo scratch identity mismatch")

print("V3_TRANSACTION_RECEIPT_SHA256=" + hashlib.sha256(raw).hexdigest())
PYRECEIPT

'''

anchor = '\nHARDWARE_SIMS=(\n'
source = source.replace(anchor, transaction + anchor, 1)

source = source.replace('  "$POLICY" \\\n  "$INOUT"', '  "$POLICY"', 1)
source = source.replace('cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"\n', '', 1)
source = source.replace('cp "$NOS3/sims/build/bin/nos3-simulator.xml" "$RUNTIME_SIM_CONFIG"',
                        'cp "$WS_TIME_DRIVER/sims/build/bin/nos3-simulator.xml" "$RUNTIME_SIM_CONFIG"', 1)

old_contract_check = '''python3 - "$CONTRACT" "$DIAGNOSTIC_CONTRACT" <<'PY'
import json
import sys

baseline = json.load(open(sys.argv[1], encoding="utf-8"))
diagnostic = json.load(open(sys.argv[2], encoding="utf-8"))
gate = diagnostic["gate"]
control = diagnostic["passive_time_witness_runtime_control_v3"]

assert baseline["contract_version"] == "0.6.2"
assert baseline["status"] == "PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False

assert diagnostic["status"] == "PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED"
assert diagnostic["scientific_outcome_allowed"] is False
assert diagnostic["command_transmission_allowed"] is False
assert diagnostic["baseline_execution_allowed"] is False
assert diagnostic["event_injection_allowed"] is False
assert diagnostic["cryptographic_semantics_claim_allowed"] is False
assert gate["diagnostic_runtime_authorized"] is True
assert gate["diagnostic_runtime_attempts_authorized"] == 1
assert gate["passive_time_witness_runtime_candidate_v3_static_verification"] == "PASS"
assert gate["baseline_run_1_authorized"] is False
assert gate["baseline_run_2_authorized"] is False
assert gate["event_injection_authorized"] is False
assert control["observation_duration_seconds"] == 70
assert control["proposed_runtime_attempts"] == 1
PY'''
new_contract_check = '''python3 - "$CONTRACT" "$PASSIVE_WITNESS_SOURCE" "$PASSIVE_WITNESS_VALIDATOR" "$FORTYTWO/42" <<'PY'
import hashlib
import json
import sys

def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

baseline = json.load(open(sys.argv[1], encoding="utf-8"))
assert digest(sys.argv[1]) == "86d365fe08d7ee177e74192cead71dc366e9c546e81668261c770350003e37ca"
assert digest(sys.argv[2]) == "830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e"
assert digest(sys.argv[3]) == "f75131770ab9020c8c2dfb41102121e12ffd664c02a8a2e03bd8aa8c7b8d9027"
assert digest(sys.argv[4]) == "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
assert baseline["contract_version"] == "0.6.2"
assert baseline["status"] == "PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False
PY'''
if old_contract_check not in source:
    raise SystemExit("expected v2 post-gate contract check missing")
source = source.replace(old_contract_check, new_contract_check, 1)

old_required = '''  "$NOS3/cfg/build/InOut/Inp_Sim.txt"
  "$NOS3/cfg/build/InOut/Inp_IPC.txt"
  "$NOS3/fsw/build/exe/cpu1/core-cpu1"
  "$NOS3/sims/build/bin/nos3-single-simulator"
  "$NOS3/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$NOS3/sims/build/bin/nos_engine_server_config.json"
  "$NOS3/sims/build/bin/nos3-simulator.xml"'''
new_required = '''  "$INOUT/Inp_Sim.txt"
  "$INOUT/Inp_IPC.txt"
  "$WS_CFS/fsw/build/exe/cpu1/core-cpu1"
  "$WS_TIME_DRIVER/sims/build/bin/nos3-single-simulator"
  "$WS_CMD_BUS_BRIDGE/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$WS_NOS_ENGINE/sims/build/bin/nos_engine_server_config.json"
  "$WS_TIME_DRIVER/sims/build/bin/nos3-simulator.xml"'''
source = source.replace(old_required, new_required, 1)

replacements = [
    ('source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin',
     'source=$WS_NOS_ENGINE,target=/work/nos3" --workdir /work/nos3/sims/build/bin'),
    ('source=$NOS3,target=/work/nos3" \\\n  --mount "type=bind,source=$RUNTIME_SIM_CONFIG',
     'source=$WS_TIME_DRIVER,target=/work/nos3" \\\n  --mount "type=bind,source=$RUNTIME_SIM_CONFIG'),
    ('source=$NOS3,target=/work/nos3" \\\n  --mount "type=bind,source=$RUNTIME_SIM_CONFIG',
     'source=$WS_CMD_BUS_BRIDGE,target=/work/nos3" \\\n  --mount "type=bind,source=$RUNTIME_SIM_CONFIG'),
    ('source=$NOS3,target=/work/nos3" \\\n  --env USER=nos3',
     'source=$WS_CFS,target=/work/nos3" \\\n  --env USER=nos3'),
]
for old, new in replacements:
    if old not in source:
        raise SystemExit("expected v2 mount pattern missing")
    source = source.replace(old, new, 1)

loop = 'for sim in "${HARDWARE_SIMS[@]}"; do\n'
source = source.replace(loop, 'hw_index=0\n' + loop +
                        '  ((hw_index+=1))\n'
                        '  printf -v hw_component "hw_sim_%02d" "$hw_index"\n'
                        '  hw_workspace="$TRANSACTION_DIR/workspaces/$hw_component/work/nos3"\n', 1)
source = source.replace('source=$NOS3,target=/work/nos3"',
                        'source=$hw_workspace,target=/work/nos3"')

cleanup_anchor = '  # Remove any same-run labeled container left by an interrupted foreground\n'
transaction_cleanup = '''  if (( TRANSACTION_PUBLISHED == 1 )) && [[ "$TRANSACTION_DIR" == "$AUTHORIZED_TRANSACTION_ROOT/$TRANSACTION_BASENAME" ]]; then
    rm -rf -- "$TRANSACTION_DIR" || cleanup_failed=1
    TRANSACTION_PUBLISHED=0
  fi

'''
source = source.replace(cleanup_anchor, transaction_cleanup + cleanup_anchor, 1)

trap_anchor = 'trap cleanup EXIT\n'
source = source.replace(trap_anchor,
                        'trap - EXIT INT TERM HUP\n' + trap_anchor, 1)

for forbidden in ('source=$NOS3,target=/work/nos3', 'source=$FORTYTWO,target=/work/fortytwo"'):
    if forbidden == 'source=$FORTYTWO,target=/work/fortytwo"':
        continue
    if forbidden in source:
        raise SystemExit("live NOS3 runtime mount remains")
if source.count('source=$hw_workspace,target=/work/nos3') != 2:
    raise SystemExit("hardware workspace mount count changed")
if source.count('source=$WS_NOS_ENGINE,target=/work/nos3') != 1:
    raise SystemExit("NOS Engine workspace mount missing")
if source.count('source=$WS_TIME_DRIVER,target=/work/nos3') != 1:
    raise SystemExit("TimeDriver workspace mount missing")
if source.count('source=$WS_CMD_BUS_BRIDGE,target=/work/nos3') != 1:
    raise SystemExit("bridge workspace mount missing")
if source.count('source=$WS_CFS,target=/work/nos3') != 1:
    raise SystemExit("cFS workspace mount missing")

with output.open("w", encoding="utf-8", newline="\n") as handle:
    handle.write(source)
PYTRANSFORM

bash -n "$tmp_emit"
chmod 700 "$tmp_emit"

rm -f -- "$base_candidate"
rmdir "$v2_tmp_dir" || \
  fail "Private v2 intermediate directory was not empty."

[[ ! -e "$emit_path_real" && ! -L "$emit_path_real" ]] || \
  fail "Emit destination appeared during generation."

ln "$tmp_emit" "$emit_path_real" || \
  fail "Atomic no-replace publication failed."

rm -f -- "$tmp_emit"
trap - EXIT

candidate_sha="$(shasum -a 256 "$emit_path_real" | awk '{print $1}')"
echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_SHA256=$candidate_sha"
echo "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE"
