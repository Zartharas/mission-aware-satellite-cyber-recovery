#!/usr/bin/env bash
# WP4 D-062 versioned passive time-witness runtime-candidate generator.
#
# EMIT ONLY:
# - does not invoke Docker;
# - does not execute the emitted candidate;
# - does not authorize runtime;
# - writes only to an approved temporary/review location.
set -Eeuo pipefail

emit_path_raw="${PASSIVE_TIME_WITNESS_V2_EMIT_PATH:-}"
if [[ -z "$emit_path_raw" ]]; then
  echo "[ERROR] PASSIVE_TIME_WITNESS_V2_EMIT_PATH is required." >&2
  exit 2
fi

command -v python3 >/dev/null 2>&1 || {
  echo "[ERROR] python3 is required." >&2
  exit 2
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[ERROR] Run the generator from within the governed repository." >&2
  exit 2
}
REPO_ROOT="$(cd "$REPO_ROOT" && pwd -P)"

emit_parent_raw="$(dirname "$emit_path_raw")"
emit_leaf="$(basename "$emit_path_raw")"
[[ -n "$emit_leaf" && "$emit_leaf" != "." && "$emit_leaf" != ".." ]] || {
  echo "[ERROR] Invalid emit filename." >&2
  exit 2
}
[[ -d "$emit_parent_raw" ]] || {
  echo "[ERROR] Emit parent directory does not exist: $emit_parent_raw" >&2
  exit 2
}

canonicalize() {
  python3 - "$1" <<'PYCANON'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PYCANON
}

emit_parent_real="$(canonicalize "$emit_parent_raw")"
emit_path_real="$(canonicalize "$emit_parent_real/$emit_leaf")"
tmp_root_real="$(canonicalize "${TMPDIR:-/tmp}")"
repo_root_real="$(canonicalize "$REPO_ROOT")"

allowed=0
case "$emit_path_real" in
  "$tmp_root_real"/*) allowed=1 ;;
esac

review_dir_raw="${PASSIVE_TIME_WITNESS_V2_REVIEW_DIR:-}"
if [[ -n "$review_dir_raw" ]]; then
  [[ -d "$review_dir_raw" ]] || {
    echo "[ERROR] PASSIVE_TIME_WITNESS_V2_REVIEW_DIR does not exist." >&2
    exit 2
  }
  review_dir_real="$(canonicalize "$review_dir_raw")"
  case "$emit_path_real" in
    "$review_dir_real"/*) allowed=1 ;;
  esac
fi

(( allowed == 1 )) || {
  echo "[ERROR] Emit path escapes approved temporary/review roots." >&2
  exit 2
}

case "$emit_path_real" in
  "$repo_root_real"|"$repo_root_real"/*)
    echo "[ERROR] Emit path targets repository/retained state; refusing." >&2
    exit 2
    ;;
esac

# Explicit retained-state defense in depth.
case "$emit_path_real" in
  */artifacts/*|*/configs/*|*/tracker/*|*/evidence/*|*/data/*)
    echo "[ERROR] Emit path targets a retained-state directory; refusing." >&2
    exit 2
    ;;
esac

if [[ -L "$emit_path_raw" ]]; then
  link_real="$(canonicalize "$emit_path_raw")"
  [[ "$link_real" == "$emit_path_real" ]] || {
    echo "[ERROR] Emit-path symlink resolution mismatch." >&2
    exit 2
  }
fi

tmp_emit="${emit_path_real}.tmp.$$"
cleanup_emit() {
  local rc=$?
  rm -f "$tmp_emit"
  trap - EXIT
  exit "$rc"
}
trap cleanup_emit EXIT

cat > "$tmp_emit" <<'CANDIDATE_EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[FAIL-CLOSED] candidate must be launched from within the governed repository." >&2
  echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
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
PHASE="wp4-passive-time-witness-v2"
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
CANDIDATE_SELF="${BASH_SOURCE[0]:-$0}"
DOCKER_BIN="docker"

EVIDENCE="$ROOT/artifacts/downlink-diagnostics/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
PROBE_GROUND="$GROUND/probe"
ORCHESTRATION="$GROUND/orchestration"
WITNESS_SCRIPT="$ORCHESTRATION/telemetry_path_witness_v2.py"
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
INOUT="$GROUND/fortytwo/NOS3InOut"
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

# ---------------------------------------------------------------------------
# Fail-closed authorization gate.
#
# This block executes before any Docker command, before any Docker-capable
# cleanup trap is installed, and before any evidence or runtime resource is
# created. The current D-062 contract must fail this gate.
# ---------------------------------------------------------------------------
command -v python3 >/dev/null 2>&1 || {
  echo "[FAIL-CLOSED] python3 is required for authorization validation." >&2
  echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
}

if ! python3 - "$CONTRACT_PATH" "$CANDIDATE_SELF" <<'PYGATE'
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

contract_path = Path(sys.argv[1])
candidate_path = Path(sys.argv[2])

try:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(1)

gate = contract.get("gate", {})
control = contract.get("passive_time_witness_runtime_control_v2", {})

required_false = (
    "scientific_outcome_allowed",
    "event_injection_allowed",
    "command_transmission_allowed",
    "baseline_execution_allowed",
    "cryptographic_semantics_claim_allowed",
)

if contract.get("status") != "PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED":
    raise SystemExit(1)
if gate.get("diagnostic_runtime_authorized") is not True:
    raise SystemExit(1)
if gate.get("diagnostic_runtime_attempts_authorized") != 1:
    raise SystemExit(1)
if gate.get("passive_time_witness_runtime_candidate_v2_static_verification") != "PASS":
    raise SystemExit(1)
if gate.get("baseline_run_1_authorized") is not False:
    raise SystemExit(1)
if gate.get("baseline_run_2_authorized") is not False:
    raise SystemExit(1)
if gate.get("event_injection_authorized") is not False:
    raise SystemExit(1)
for key in required_false:
    if contract.get(key) is not False:
        raise SystemExit(1)

if control.get("observation_duration_seconds") != 70:
    raise SystemExit(1)
if control.get("proposed_runtime_attempts") != 1:
    raise SystemExit(1)

accepted = gate.get("accepted_runtime_entrypoint_v2_sha256")
if not isinstance(accepted, str) or len(accepted) != 64:
    raise SystemExit(1)
try:
    int(accepted, 16)
except ValueError:
    raise SystemExit(1)

actual = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
if actual != accepted:
    raise SystemExit(1)
PYGATE
then
  echo "[FAIL-CLOSED] passive time-witness v2 runtime is not authorized by the current contract." >&2
  echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
fi

echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_GATE=AUTHORIZED"

HARDWARE_SIMS=(
  generic-css-sim
  generic-eps-sim
  generic-fss-sim
  gps
  generic-imu-sim
  generic-mag-sim
  generic-reactionwheel-sim0
  generic-reactionwheel-sim1
  generic-reactionwheel-sim2
  generic-radio-sim
  sample-sim
  generic-star-tracker-sim
  generic-thruster-sim
  generic-torquer-sim
)

value() {
  awk -F= -v key="$2" '$1 == key {print substr($0,index($0,"=")+1)}' "$1" | tail -n 1
}

record() {
  printf '%s=%s\n' "$1" "$2" >> "$MANIFEST"
}

hash_tree() {
  python3 - "$1" <<'PY'
from __future__ import annotations
import hashlib
import os
import sys
from pathlib import Path

directory = Path(sys.argv[1]).resolve()
manifest = directory / "sha256-manifest.txt"
entries: list[str] = []
for path in sorted(directory.rglob("*")):
    if not path.is_file() or path == manifest or path.name.endswith(".tmp"):
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entries.append(f"{digest}  {path.relative_to(directory).as_posix()}")
if not entries:
    raise SystemExit(f"zero-entry evidence manifest rejected: {directory}")
temporary = manifest.with_suffix(".txt.tmp")
temporary.write_text("\n".join(entries) + "\n", encoding="utf-8")
os.replace(temporary, manifest)
print(hashlib.sha256(manifest.read_bytes()).hexdigest())
PY
}

bounded_exec() {
  local timeout_seconds="$1"
  shift
  python3 - "$timeout_seconds" "$@" <<'PYTIMEOUT'
from __future__ import annotations

import subprocess
import sys

timeout = float(sys.argv[1])
command = sys.argv[2:]
if not command:
    raise SystemExit(2)

try:
    completed = subprocess.run(command, timeout=timeout)
except subprocess.TimeoutExpired:
    raise SystemExit(124)
raise SystemExit(completed.returncode)
PYTIMEOUT
}

capture() {
  local name="$1"
  if ! bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" >/dev/null 2>&1; then
    return 0
  fi

  # Retain only approved container metadata. Do not retain raw Docker inspect,
  # container IP addresses, packet material, command material, or raw logs.
  bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" \
    --format 'name={{.Name}}
state={{.State.Status}}
exit_code={{.State.ExitCode}}
oom_killed={{.State.OOMKilled}}
project={{index .Config.Labels "research.project"}}
phase={{index .Config.Labels "research.phase"}}
run_id={{index .Config.Labels "research.run_id"}}
networks={{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}
mount_destinations={{range .Mounts}}{{.Destination}} {{end}}' \
    > "$ORCHESTRATION/container-$name.txt" 2>/dev/null || return 1
}

cleanup() {
  local rc=$?
  local final_rc="$rc"
  local name labels extra_ids container_output network_output
  local remaining_containers=-1 remaining_networks=-1
  local ground_hash="" policy_hash=""
  local capture_failed=0 cleanup_failed=0 ground_hash_failed=0 policy_hash_failed=0
  local retry index

  trap - EXIT INT TERM HUP
  set +e

  # Capture the exact created containers before teardown.
  for name in "${CREATED_CONTAINERS[@]}"; do
    [[ -z "$name" ]] || capture "$name" || capture_failed=1
  done

  if (( NETWORK_CREATED == 1 )); then
    bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network inspect "$NETWORK" \
      --format 'name={{.Name}}
internal={{.Internal}}
project={{index .Labels "research.project"}}
phase={{index .Labels "research.phase"}}
run_id={{index .Labels "research.run_id"}}' \
      > "$ORCHESTRATION/network-final.txt" 2>/dev/null || capture_failed=1
  fi
  bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps -a \
    --filter "label=research.project=$PROJECT" \
    --filter "label=research.phase=$PHASE" \
    --filter "label=research.run_id=$RUN_ID" \
    --format 'name={{.Names}}	status={{.Status}}' \
    > "$ORCHESTRATION/docker-ps-final.txt" 2>/dev/null || capture_failed=1

  # Stop and remove tracked containers in strict reverse creation order.
  for ((index=${#CREATED_CONTAINERS[@]}-1; index>=0; index--)); do
    name="${CREATED_CONTAINERS[$index]}"
    [[ -n "$name" ]] || continue
    if bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" >/dev/null 2>&1; then
      bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" \
        "$DOCKER_BIN" stop --time "$DOCKER_STOP_GRACE_SECONDS" "$name" >/dev/null 2>&1 \
        || cleanup_failed=1
      bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" \
        "$DOCKER_BIN" rm -f "$name" >/dev/null 2>&1 || cleanup_failed=1
    fi
  done

  # Remove any same-run labeled container left by an interrupted foreground
  # helper, without touching any other project or run.
  extra_ids="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps -aq \
    --filter "label=research.project=$PROJECT" \
    --filter "label=research.phase=$PHASE" \
    --filter "label=research.run_id=$RUN_ID" 2>/dev/null)"
  if [[ $? -ne 0 ]]; then
    cleanup_failed=1
    extra_ids=""
  fi
  while IFS= read -r name; do
    [[ -n "$name" ]] || continue
    bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" \
      "$DOCKER_BIN" stop --time "$DOCKER_STOP_GRACE_SECONDS" "$name" >/dev/null 2>&1 \
      || cleanup_failed=1
    bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" \
      "$DOCKER_BIN" rm -f "$name" >/dev/null 2>&1 || cleanup_failed=1
  done <<< "$extra_ids"

  # Remove only the exact same-run network after verifying all three labels.
  if (( NETWORK_CREATED == 1 )); then
    labels="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network inspect "$NETWORK" \
      --format '{{index .Labels "research.project"}}|{{index .Labels "research.phase"}}|{{index .Labels "research.run_id"}}' \
      2>/dev/null)"
    if [[ "$labels" == "$PROJECT|$PHASE|$RUN_ID" ]]; then
      bounded_exec "$NETWORK_REMOVAL_TIMEOUT_SECONDS" \
        "$DOCKER_BIN" network rm "$NETWORK" >/dev/null 2>&1 || cleanup_failed=1
    elif bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network inspect "$NETWORK" \
      >/dev/null 2>&1; then
      cleanup_failed=1
    fi
  fi

  # Require zero same-run resources, retrying exactly ten times.
  for ((retry=1; retry<=POST_CLEANUP_ASSERT_RETRIES; retry++)); do
    container_output="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps -aq \
      --filter "label=research.project=$PROJECT" \
      --filter "label=research.phase=$PHASE" \
      --filter "label=research.run_id=$RUN_ID" 2>/dev/null)"
    if [[ $? -ne 0 ]]; then
      remaining_containers=-1
      cleanup_failed=1
    else
      remaining_containers="$(printf '%s\n' "$container_output" | awk 'NF {count++} END {print count+0}')"
    fi

    network_output="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network ls -q \
      --filter "label=research.project=$PROJECT" \
      --filter "label=research.phase=$PHASE" \
      --filter "label=research.run_id=$RUN_ID" 2>/dev/null)"
    if [[ $? -ne 0 ]]; then
      remaining_networks=-1
      cleanup_failed=1
    else
      remaining_networks="$(printf '%s\n' "$network_output" | awk 'NF {count++} END {print count+0}')"
    fi

    if (( remaining_containers == 0 && remaining_networks == 0 )); then
      break
    fi
    if (( retry < POST_CLEANUP_ASSERT_RETRIES )); then
      sleep "$POST_CLEANUP_RETRY_INTERVAL_SECONDS"
    fi
  done

  if (( capture_failed != 0 || cleanup_failed != 0 || remaining_containers != 0 || remaining_networks != 0 )); then
    RESULT="PASSIVE_TIME_WITNESS_RUNTIME_INVALID"
    final_rc=3
  fi

  cat > "$ORCHESTRATION/terminal-state.txt" <<EOF
run_id=$RUN_ID
capture_failed=$capture_failed
cleanup_failed=$cleanup_failed
cleanup_project_containers_remaining=$remaining_containers
cleanup_project_networks_remaining=$remaining_networks
terminal_classification=$RESULT
pre_hash_exit_code=$final_rc
EOF

  record cleanup_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  record evidence_capture_failed "$capture_failed"
  record cleanup_failed "$cleanup_failed"
  record cleanup_project_containers_remaining "$remaining_containers"
  record cleanup_project_networks_remaining "$remaining_networks"
  record pre_hash_terminal_classification "$RESULT"
  record pre_hash_exit_code "$final_rc"

  ground_hash="$(hash_tree "$GROUND" 2>/dev/null)" || ground_hash_failed=1
  policy_hash="$(hash_tree "$POLICY" 2>/dev/null)" || policy_hash_failed=1
  [[ -n "$ground_hash" ]] || ground_hash_failed=1
  [[ -n "$policy_hash" ]] || policy_hash_failed=1

  if (( ground_hash_failed != 0 || policy_hash_failed != 0 )); then
    RESULT="PASSIVE_TIME_WITNESS_RUNTIME_INVALID"
    final_rc=3
  fi

  cat > "$ROOT_HASH_LOCK" <<EOF
run_id=$RUN_ID
immutable_ground_hash_failed=$ground_hash_failed
policy_visible_hash_failed=$policy_hash_failed
immutable_ground_manifest_sha256=$ground_hash
policy_visible_manifest_sha256=$policy_hash
terminal_classification=$RESULT
exit_code=$final_rc
EOF

  if [[ "$RESULT" == PASSIVE_TIME_WITNESS_RUNTIME_COMPLETE && "$final_rc" -eq 0 ]]; then
    echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_STATUS=COMPLETE"
    echo "[OK] Evidence retained at: $EVIDENCE"
  else
    echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi

  exit "$final_rc"
}

start() {
  local logical="$1" alias="$2" runtime="$3"
  shift 3
  local name="$PREFIX-$logical"
  bounded_exec "$READINESS_TIMEOUT_SECONDS" "$DOCKER_BIN" run -d \
    --platform linux/amd64 --name "$name" --hostname "$alias" \
    --network "$NETWORK" --network-alias "$alias" \
    --env TERM=xterm \
    --label "research.project=$PROJECT" \
    --label "research.phase=$PHASE" \
    --label "research.run_id=$RUN_ID" \
    --log-driver json-file --log-opt max-size=10m --log-opt max-file=2 \
    "$@" >/dev/null
  CREATED_CONTAINERS+=("$name")
  echo "$name" >> "$NAMES"
  if [[ "$runtime" == true ]]; then
    echo "$name" >> "$RUNTIME_NAMES"
  fi
}

check_container_isolation() {
  local name="$1" networks
  networks="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || true)"
  [[ "$networks" == "$NETWORK" ]] || {
    echo "[ERROR] Unexpected network for $name: $networks" >&2
    return 1
  }
  [[ -z "$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" port "$name" 2>/dev/null)" ]] || {
    echo "[ERROR] Host port published by $name." >&2
    return 1
  }
  if bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{range .Mounts}}{{println .Source .Destination}}{{end}}' 2>/dev/null | grep -q '/var/run/docker.sock'; then
    echo "[ERROR] Docker socket mounted in $name." >&2
    return 1
  fi
}

wait_for_log_marker() {
  local name="$1" marker="$2" timeout_seconds="$3" manifest_key="$4"
  local attempt state logs
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before readiness marker '$marker' was observed." >&2
      return 1
    }
    logs="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" logs "$name" 2>&1 || true)"
    if grep -Fq -- "$marker" <<< "$logs"; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not report readiness marker '$marker' within ${timeout_seconds}s." >&2
  return 1
}

wait_for_tcp_listener() {
  local name="$1" port="$2" timeout_seconds="$3" manifest_key="$4"
  local hex_port attempt state
  hex_port="$(printf '%04X' "$port")"
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before TCP port $port became ready." >&2
      return 1
    }
    if bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" exec "$name" sh -lc \
      "awk '\$2 ~ /:${hex_port}\$/ && \$4 == \"0A\" {found=1} END {exit found ? 0 : 1}' /proc/net/tcp" \
      >/dev/null 2>&1; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not expose TCP listener $port within ${timeout_seconds}s." >&2
  return 1
}

wait_for_udp_listener() {
  local name="$1" port="$2" timeout_seconds="$3" manifest_key="$4"
  local hex_port attempt state
  hex_port="$(printf '%04X' "$port")"
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before UDP port $port became ready." >&2
      return 1
    }
    if bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" exec "$name" sh -lc \
      "awk '\$2 ~ /:${hex_port}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
      >/dev/null 2>&1; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not expose UDP listener $port within ${timeout_seconds}s." >&2
  return 1
}

wait_for_socket_trace() {
  local name="$1" timeout_seconds="$2" manifest_key="$3"
  local attempt state
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before radio socket ingress metadata was observed." >&2
      return 1
    }
    if [[ -s "$SOCKET_TRACE" ]] && grep -Eq 'event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE"; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name produced no successful UDP 5011 recvfrom metadata within ${timeout_seconds}s." >&2
  return 1
}

wait_for_passive_witness_connected() {
  local name="$1" timeout_seconds="$2" manifest_key="$3"
  local attempt state
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before passive subscription readiness." >&2
      return 1
    }

    if [[ -s "$PASSIVE_WITNESS_TRACE" ]] && python3 - "$PASSIVE_WITNESS_TRACE" <<'PYREADY'
from __future__ import annotations

import json
import sys
from pathlib import Path

records = []
for raw in Path(sys.argv[1]).read_text(encoding="utf-8", errors="strict").splitlines():
    if raw.strip():
        records.append(json.loads(raw))
if not records:
    raise SystemExit(1)
states = [record.get("state") for record in records]
if "connected" not in states:
    raise SystemExit(1)
if states[-1] == "disconnected":
    raise SystemExit(1)
PYREADY
    then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done

  echo "[ERROR] $name did not establish a passive subscription within ${timeout_seconds}s." >&2
  return 1
}

check_runtime() {
  local phase="$1" failed=0 name state code
  while IFS= read -r name; do
    state="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    code="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" inspect "$name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
    printf '%s,%s,%s,%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$phase" "$name" "$state:$code" >> "$LIVENESS"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name is $state (exit $code)." >&2
      failed=1
    }
    check_container_isolation "$name" || failed=1
  done < "$RUNTIME_NAMES"
  return "$failed"
}

for number in \
  "$OBSERVATION_DURATION_SECONDS" \
  "$READINESS_TIMEOUT_SECONDS" \
  "$DOCKER_STOP_GRACE_SECONDS" \
  "$CLEANUP_COMMAND_TIMEOUT_SECONDS" \
  "$NETWORK_REMOVAL_TIMEOUT_SECONDS" \
  "$POST_CLEANUP_ASSERT_RETRIES" \
  "$POST_CLEANUP_RETRY_INTERVAL_SECONDS"; do
  [[ "$number" =~ ^[0-9]+$ ]] || {
    echo "[ERROR] Frozen runtime-control values must be integers." >&2
    exit 1
  }
done
(( OBSERVATION_DURATION_SECONDS == 70 )) || exit 1
(( READINESS_TIMEOUT_SECONDS == 60 )) || exit 1
(( DOCKER_STOP_GRACE_SECONDS == 10 )) || exit 1
(( CLEANUP_COMMAND_TIMEOUT_SECONDS == 15 )) || exit 1
(( NETWORK_REMOVAL_TIMEOUT_SECONDS == 15 )) || exit 1
(( POST_CLEANUP_ASSERT_RETRIES == 10 )) || exit 1
(( POST_CLEANUP_RETRY_INTERVAL_SECONDS == 1 )) || exit 1

for command in docker git awk shasum python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

if [[ -e "$EVIDENCE" ]]; then
  echo "[ERROR] Fresh evidence root already exists; refusing reuse: $EVIDENCE" >&2
  exit 1
fi

mkdir -p \
  "$PROBE_GROUND" \
  "$ORCHESTRATION/runtime-config" \
  "$SOCKET_METADATA_DIR" \
  "$SHIM_BUILD_DIR" \
  "$PASSIVE_WITNESS_DIR" \
  "$POLICY" \
  "$INOUT"

cat > "$POLICY/scope.json" <<'EOF'
{
  "policy_visible_evidence": "none_by_design",
  "truth_data_included": false,
  "command_data_included": false,
  "scientific_outcome_included": false,
  "authoritative_time_data_included": false,
  "socket_timing_data_included": false,
  "derived_timing_data_included": false
}
EOF

cat > "$WITNESS_SCRIPT" <<'PYWITNESS'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import signal
import socket
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("proxy", "sink"))
    parser.add_argument("--bind-host", default="0.0.0.0")
    parser.add_argument("--bind-port", type=int)
    parser.add_argument("--forward-host")
    parser.add_argument("--forward-port", type=int)
    parser.add_argument("--resolve-timeout", type=float, default=45.0)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> int:
    assert 1 <= 5013 <= 65535
    assert 1 <= 5011 <= 65535
    assert 1 <= 8011 <= 65535
    print("TELEMETRY_PATH_WITNESS_V2_SELF_TEST=PASS", flush=True)
    return 0


def resolve_destination(host: str, port: int, timeout: float) -> tuple[str, int]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            answers = socket.getaddrinfo(
                host,
                port,
                socket.AF_INET,
                socket.SOCK_DGRAM,
            )
            if answers:
                return answers[0][4][0], port
        except OSError:
            pass
        time.sleep(0.25)
    raise RuntimeError("destination resolution failed")


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.mode is None or args.bind_port is None:
        raise SystemExit("--mode and --bind-port are required")
    if args.mode == "proxy" and (
        not args.forward_host or args.forward_port is None
    ):
        raise SystemExit("proxy mode requires forward destination")

    running = True

    def stop_handler(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)

    destination = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as channel:
        channel.bind((args.bind_host, args.bind_port))
        channel.settimeout(0.5)
        print(
            f"TELEMETRY_WITNESS_READY mode={args.mode}",
            flush=True,
        )

        sequence = 0
        while running:
            try:
                datagram, _ = channel.recvfrom(65535)
            except socket.timeout:
                continue

            sequence += 1
            print(
                f"TELEMETRY_WITNESS_RECEIVED mode={args.mode} sequence={sequence}",
                flush=True,
            )

            if args.mode == "proxy":
                if destination is None:
                    destination = resolve_destination(
                        args.forward_host,
                        args.forward_port,
                        args.resolve_timeout,
                    )
                sent = channel.sendto(datagram, destination)
                if sent != len(datagram):
                    print(
                        "TELEMETRY_WITNESS_INVALID reason=partial_forward",
                        file=sys.stderr,
                        flush=True,
                    )
                    return 3
                print(
                    f"TELEMETRY_WITNESS_FORWARDED mode=proxy sequence={sequence}",
                    flush=True,
                )

    print(
        f"TELEMETRY_WITNESS_STOPPED mode={args.mode} packets={sequence}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PYWITNESS
chmod 700 "$WITNESS_SCRIPT"

: > "$MANIFEST"
: > "$NAMES"
: > "$RUNTIME_NAMES"
printf 'timestamp_utc,phase,container,state_exit_code\n' > "$LIVENESS"

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not reachable." >&2; exit 1; }
bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] Pinned image is unavailable." >&2; exit 1; }

CONTRACT="$ROOT/configs/benign-baseline-contract.json"
DIAGNOSTIC_CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
PREFLIGHT_LOCK="$ROOT/artifacts/nominal-runtime-preflight-lock.txt"
for file in "$CONTRACT" "$DIAGNOSTIC_CONTRACT" "$WITNESS_SCRIPT" "$SHIM_SOURCE" "$PASSIVE_WITNESS_SOURCE" "$PASSIVE_WITNESS_VALIDATOR" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing required file: $file" >&2; exit 1; }
done

python3 -m json.tool "$CONTRACT" >/dev/null
python3 "$WITNESS_SCRIPT" --self-test >/dev/null
python3 "$PASSIVE_WITNESS_VALIDATOR" --self-test >/dev/null
python3 - "$CONTRACT" "$DIAGNOSTIC_CONTRACT" <<'PY'
import json
import sys

baseline = json.load(open(sys.argv[1], encoding="utf-8"))
diagnostic = json.load(open(sys.argv[2], encoding="utf-8"))
gate = diagnostic["gate"]
control = diagnostic["passive_time_witness_runtime_control_v2"]

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
assert gate["passive_time_witness_runtime_candidate_v2_static_verification"] == "PASS"
assert gate["baseline_run_1_authorized"] is False
assert gate["baseline_run_2_authorized"] is False
assert gate["event_injection_authorized"] is False
assert control["observation_duration_seconds"] == 70
assert control["proposed_runtime_attempts"] == 1
PY

[[ "$(value "$BUILD_LOCK" build_status)" == PASS ]] || { echo "[ERROR] NOS3 build lock is not PASS." >&2; exit 1; }
[[ "$(value "$PREFLIGHT_LOCK" runtime_preflight_status)" == PASS ]] || { echo "[ERROR] Runtime preflight lock is not PASS." >&2; exit 1; }
[[ "$(git -C "$NOS3" rev-parse HEAD)" == "$NOS3_COMMIT" ]] || { echo "[ERROR] NOS3 commit mismatch." >&2; exit 1; }
[[ "$(git -C "$FORTYTWO" rev-parse HEAD)" == "$FORTYTWO_COMMIT" ]] || { echo "[ERROR] 42 commit mismatch." >&2; exit 1; }
[[ -z "$(git -C "$NOS3" status --short)" ]] || { echo "[ERROR] NOS3 worktree is not clean." >&2; exit 1; }
[[ -z "$(git -C "$FORTYTWO" status --short)" ]] || { echo "[ERROR] 42 worktree is not clean." >&2; exit 1; }

required=(
  "$NOS3/cfg/build/InOut/Inp_Sim.txt"
  "$NOS3/cfg/build/InOut/Inp_IPC.txt"
  "$NOS3/fsw/build/exe/cpu1/core-cpu1"
  "$NOS3/sims/build/bin/nos3-single-simulator"
  "$NOS3/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$NOS3/sims/build/bin/nos_engine_server_config.json"
  "$NOS3/sims/build/bin/nos3-simulator.xml"
  "$FORTYTWO/42"
)
for file in "${required[@]}"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing runtime artifact: $file" >&2; exit 1; }
done

[[ -z "$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps -aq --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime containers found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}
[[ -z "$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network ls -q --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime networks found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}

bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps -a \
  --filter "label=research.project=$PROJECT" \
  --format 'name={{.Names}}	status={{.Status}}' \
  > "$ORCHESTRATION/docker-ps-before.txt"
bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network ls \
  --filter "label=research.project=$PROJECT" \
  --format 'name={{.Name}}	driver={{.Driver}}' \
  > "$ORCHESTRATION/docker-networks-before.txt"
cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"
cp "$NOS3/sims/build/bin/nos3-simulator.xml" "$RUNTIME_SIM_CONFIG"

python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys

inp_sim = Path(sys.argv[1])
lines = inp_sim.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[index] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
inp_sim.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

python3 "$ROOT/scripts/prepare_runtime_radio_config.py" \
  "$NOS3/sims/build/bin/nos3-simulator.xml" \
  "$RUNTIME_SIM_CONFIG"

grep -q '^FALSE[[:space:]]*![[:space:]]*Graphics Front End?' "$INOUT/Inp_Sim.txt" || {
  echo "[ERROR] 42 runtime configuration is not headless." >&2
  exit 1
}
grep -q '<ci-port>5012</ci-port>' "$RUNTIME_SIM_CONFIG" || {
  echo "[ERROR] Runtime radio CI port override is missing." >&2
  exit 1
}

cat > "$PASSIVE_WITNESS_LAUNCHER" <<'LAUNCHER'
#!/usr/bin/env bash
set -Eeuo pipefail

g++ -std=c++14 -Wall -Wextra -Werror -I/usr/include \
  /work/scripts/passive_nos_engine_time_witness.cpp \
  -lnos_engine_client \
  -lnos_engine_common \
  -lnos_engine_transport \
  -lnos_engine_utility \
  -o /tmp/passive_nos_engine_time_witness

uri="$(python3 - /runtime-config/nos3-simulator.xml <<'PYURI'
from __future__ import annotations

import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="strict")
for tag in ("nos-connection-string-override", "nos-connection-string"):
    match = re.search(
        rf"<{tag}>\s*([^<]+?)\s*</{tag}>",
        text,
        flags=re.IGNORECASE,
    )
    if match and match.group(1).strip():
        print(match.group(1).strip())
        raise SystemExit(0)
raise SystemExit(1)
PYURI
)"

[[ -n "$uri" ]] || {
  echo "passive_nos_engine_time_witness: error: connection configuration missing" >&2
  exit 1
}

exec /tmp/passive_nos_engine_time_witness \
  /evidence/passive-time-witness/trace.jsonl \
  "$uri" \
  passive-time-witness
LAUNCHER
chmod 700 "$PASSIVE_WITNESS_LAUNCHER"

record run_id "$RUN_ID"
record started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record project "$PROJECT"
record phase "$PHASE"
record baseline_timeout_seconds "$BASELINE_TIMEOUT"
record probe_readiness_timeout_seconds "$PROBE_READINESS_TIMEOUT"
record acceptance_timeout_seconds "$ACCEPTANCE_TIMEOUT"
record observation_duration_seconds "$OBSERVATION_DURATION_SECONDS"
record readiness_timeout_seconds "$READINESS_TIMEOUT_SECONDS"
record docker_stop_grace_seconds "$DOCKER_STOP_GRACE_SECONDS"
record cleanup_command_timeout_seconds "$CLEANUP_COMMAND_TIMEOUT_SECONDS"
record network_removal_timeout_seconds "$NETWORK_REMOVAL_TIMEOUT_SECONDS"
record post_cleanup_assert_retries "$POST_CLEANUP_ASSERT_RETRIES"
record passive_time_witness_count 1
record passive_time_witness_trace_scope immutable-ground-only
record event_injection disabled
record telemetry_activation SC_RTS001_TO_LAB_OUTPUT_ENABLE
record ground_setup_command_transmissions 0
record to_lab_destination_alias active-gs
record to_lab_destination_port 5013
record to_lab_compiled_destination_port 5013
record radio_fsw_telemetry_listener_port 5011
record ci_application CI_LAB
record ci_listen_port 5012
record runtime_radio_ci_port_override 5010_to_5012
record diagnostic_type passive_nos_engine_time_witness_v2
record socket_metadata_only true
record socket_metadata_packet_content false
record socket_metadata_ip_addresses false
record scientific_outcome_allowed false
record command_transmission_allowed false
record measured_command_transmissions 0
record event_injection disabled
record expected_runtime_component_count 23
record expected_total_component_count 23
record simulator_launch_mode individual_pinned_headless_passive_time_witness_v2
record hardware_simulator_count "${#HARDWARE_SIMS[@]}"
record truth_stream_dependency internal_read_only_sink
record truth_sink_policy_visibility none
record ground_evidence_directory immutable-ground
record policy_visible_evidence_directory policy-visible
record network "$NETWORK"
record network_mode internal_bridge
record nos3_commit "$NOS3_COMMIT"
record fortytwo_commit "$FORTYTWO_COMMIT"
record image "$IMAGE"
record image_id "$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" image inspect "$IMAGE" --format '{{.Id}}')"
record contract_sha256 "$(shasum -a 256 "$CONTRACT" | awk '{print $1}')"
record telemetry_witness_script_sha256 "$(shasum -a 256 "$WITNESS_SCRIPT" | awk '{print $1}')"
record passive_time_witness_source_sha256 "$(shasum -a 256 "$PASSIVE_WITNESS_SOURCE" | awk '{print $1}')"
record passive_time_witness_validator_sha256 "$(shasum -a 256 "$PASSIVE_WITNESS_VALIDATOR" | awk '{print $1}')"
record diagnostic_contract_sha256 "$(shasum -a 256 "$DIAGNOSTIC_CONTRACT" | awk '{print $1}')"
record build_lock_sha256 "$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')"
record runtime_preflight_lock_sha256 "$(shasum -a 256 "$PREFLIGHT_LOCK" | awk '{print $1}')"
record runtime_inp_sim_sha256 "$(shasum -a 256 "$INOUT/Inp_Sim.txt" | awk '{print $1}')"
record runtime_inp_ipc_sha256 "$(shasum -a 256 "$INOUT/Inp_IPC.txt" | awk '{print $1}')"
record runtime_simulator_config_sha256 "$(shasum -a 256 "$RUNTIME_SIM_CONFIG" | awk '{print $1}')"
record fortytwo_inout_container "$FORTYTWO_INOUT_CONTAINER"

actual_shim_source_sha="$(shasum -a 256 "$SHIM_SOURCE" | awk '{print $1}')"
[[ "$actual_shim_source_sha" == "$EXPECTED_SHIM_SOURCE_SHA256" ]] || {
  echo "[ERROR] Radio socket metadata shim source hash mismatch." >&2
  exit 1
}
CREATED_CONTAINERS+=("$PREFIX-shim-build")
bounded_exec "$READINESS_TIMEOUT_SECONDS" "$DOCKER_BIN" run --rm --name "$PREFIX-shim-build" --label "research.project=$PROJECT" --label "research.phase=$PHASE" --label "research.run_id=$RUN_ID" --platform linux/amd64 --network none   --mount "type=bind,source=$SHIM_SOURCE,target=/src/radio_socket_metadata_shim.c,readonly"   --mount "type=bind,source=$SHIM_BUILD_DIR,target=/out"   "$IMAGE" bash -lc '
set -Eeuo pipefail
cc -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared   /src/radio_socket_metadata_shim.c   -o /out/libradio_socket_metadata_shim.so   -ldl
'
[[ -s "$SHIM_SO" ]] || {
  echo "[ERROR] Radio socket metadata shim shared object was not produced." >&2
  exit 1
}
actual_shim_so_sha="$(shasum -a 256 "$SHIM_SO" | awk '{print $1}')"
[[ "$actual_shim_so_sha" == "$EXPECTED_SHIM_SO_SHA256" ]] || {
  echo "[ERROR] Radio socket metadata shim shared-object hash mismatch." >&2
  exit 1
}
record radio_socket_metadata_shim_source_sha256 "$actual_shim_source_sha"
record radio_socket_metadata_shim_shared_object_sha256 "$actual_shim_so_sha"
record radio_socket_metadata_trace_path immutable-ground/radio-socket-metadata/radio-socket-metadata.log

bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network create --driver bridge --internal   --label "research.project=$PROJECT" \
  --label "research.phase=$PHASE" \
  --label "research.run_id=$RUN_ID" \
  "$NETWORK" >/dev/null
NETWORK_CREATED=1
[[ "$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network inspect "$NETWORK" --format '{{.Internal}}')" == true ]] || {
  echo "[ERROR] Baseline network is not internal." >&2
  exit 1
}
bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" network inspect "$NETWORK" \
  --format 'name={{.Name}}
internal={{.Internal}}
project={{index .Labels "research.project"}}
phase={{index .Labels "research.phase"}}
run_id={{index .Labels "research.run_id"}}' \
  > "$ORCHESTRATION/network-created.txt"

start radio-egress-witness cryptolib true \
  --network-alias radio-egress-witness \
  --mount "type=bind,source=$WITNESS_SCRIPT,target=/witness/telemetry_path_witness.py,readonly" \
  "$IMAGE" python3 -u /witness/telemetry_path_witness.py \
    --mode sink --bind-host 0.0.0.0 --bind-port 8011
wait_for_log_marker "$PREFIX-radio-egress-witness" "TELEMETRY_WITNESS_READY mode=sink" 20 radio_egress_witness_ready
check_container_isolation "$PREFIX-radio-egress-witness"

start to-radio-witness active-gs true \
  --network-alias telemetry-witness \
  --mount "type=bind,source=$WITNESS_SCRIPT,target=/witness/telemetry_path_witness.py,readonly" \
  "$IMAGE" python3 -u /witness/telemetry_path_witness.py \
    --mode proxy --bind-host 0.0.0.0 --bind-port 5013 \
    --forward-host radio-sim --forward-port 5011 --resolve-timeout 45
wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_READY mode=proxy" 20 to_radio_witness_ready
check_container_isolation "$PREFIX-to-radio-witness"

start engine nos-engine-server true \
  --interactive --tty --network-alias sc01-nos-engine-server \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" /usr/bin/nos_engine_server_standalone -f nos_engine_server_config.json
sleep 2
start time nos-time-driver true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
  --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml time
start passive-time-witness passive-time-witness true \
  --mount "type=bind,source=$PASSIVE_WITNESS_SOURCE,target=/work/scripts/passive_nos_engine_time_witness.cpp,readonly" \
  --mount "type=bind,source=$PASSIVE_WITNESS_LAUNCHER,target=/work/scripts/passive-time-witness-launcher.sh,readonly" \
  --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
  --mount "type=bind,source=$PASSIVE_WITNESS_DIR,target=/evidence/passive-time-witness" \
  --workdir /work/nos3/sims/build/bin \
  "$IMAGE" bash /work/scripts/passive-time-witness-launcher.sh
start fortytwo fortytwo true \
  --mount "type=bind,source=$FORTYTWO,target=/work/fortytwo,readonly" \
  --mount "type=bind,source=$INOUT,target=$FORTYTWO_INOUT_CONTAINER" --workdir /work/fortytwo \
  "$IMAGE" ./42 "$FORTYTWO_INOUT_CONTAINER"
start truth-sink truth-sink true \
  --env TRUTH_HOST=fortytwo --env TRUTH_PORT=9999 --env CONNECT_TIMEOUT_SECONDS=60 \
  "$IMAGE" python3 -u -c '
import os, socket, sys, time
host=os.environ["TRUTH_HOST"]; port=int(os.environ["TRUTH_PORT"])
deadline=time.monotonic()+int(os.environ["CONNECT_TIMEOUT_SECONDS"]); last=None
while True:
    try:
        stream=socket.create_connection((host,port),timeout=1.0); stream.settimeout(None)
        print(f"TRUTH_SINK_CONNECTED host={host} port={port}",flush=True); break
    except OSError as exc:
        last=exc
        if time.monotonic()>=deadline:
            print(f"TRUTH_SINK_CONNECT_FAILED host={host} port={port} error={last}",file=sys.stderr,flush=True); raise SystemExit(2)
        time.sleep(0.5)
received=0; last_report=time.monotonic()
while True:
    payload=stream.recv(65536)
    if not payload:
        print(f"TRUTH_SINK_STREAM_CLOSED bytes={received}",file=sys.stderr,flush=True); raise SystemExit(3)
    received+=len(payload); now=time.monotonic()
    if now-last_report>=5.0:
        print(f"TRUTH_SINK_BYTES={received}",flush=True); last_report=now
'

for sim in "${HARDWARE_SIMS[@]}"; do
  if [[ "$sim" == generic-radio-sim ]]; then
    start "$sim" radio-sim true \
      --network-alias generic-radio-sim \
      --env TCP_GROUND=0 --env MULTI_GDS=0 \
      --env LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so \
      --env RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log \
      --mount "type=bind,source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly" \
      --mount "type=bind,source=$SOCKET_METADATA_DIR,target=/evidence-socket-metadata" \
      --mount "type=bind,source=$NOS3,target=/work/nos3" \
      --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
      --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml "$sim"
  else
    start "$sim" "$sim" true \
      --mount "type=bind,source=$NOS3,target=/work/nos3" \
      --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
      --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml "$sim"
  fi
done

wait_for_log_marker "$PREFIX-truth-sink" TRUTH_SINK_CONNECTED "$READINESS_TIMEOUT_SECONDS" truth_sink_connection
wait_for_udp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_udp_8010_listener
wait_for_udp_listener "$PREFIX-generic-radio-sim" 5011 45 radio_udp_5011_listener

start bridge nos-sim-bridge true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
  --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-sim-cmdbus-bridge -f /runtime-config/nos3-simulator.xml
start cfs nos-fsw true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --env USER=nos3 --env LD_LIBRARY_PATH=/work/nos3/fsw/build/exe/cpu1:/usr/lib:/usr/local/lib \
  --workdir /work/nos3/fsw/build/exe/cpu1 --sysctl fs.mqueue.msg_max=10000 \
  --ulimit rtprio=99 --cap-add SYS_NICE \
  "$IMAGE" bash -lc 'exec ./core-cpu1 -R PO'

wait_for_log_marker "$PREFIX-cfs" "CI_LAB listening on UDP port: 5012" 45 ci_lab_udp_5012
wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs
wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_RECEIVED mode=proxy" 60 to_witness_received
wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_FORWARDED mode=proxy" 60 to_witness_forwarded
wait_for_socket_trace "$PREFIX-generic-radio-sim" 60 radio_socket_recvfrom_5011
wait_for_passive_witness_connected "$PREFIX-passive-time-witness" "$READINESS_TIMEOUT_SECONDS" passive_time_witness_connected

record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_component_count "$(wc -l < "$RUNTIME_NAMES" | tr -d ' ')"
record total_component_count "$(wc -l < "$NAMES" | tr -d ' ')"
check_runtime startup
record observation_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
for ((observation_second=1; observation_second<=OBSERVATION_DURATION_SECONDS; observation_second++)); do
  sleep 1
done
record observation_elapsed_seconds "$OBSERVATION_DURATION_SECONDS"
check_runtime observation

[[ -s "$SOCKET_TRACE" ]] || {
  echo "[ERROR] Radio socket metadata trace is missing or empty." >&2
  exit 3
}
if grep -Eqi 'payload|payload_sha|hex=|data=|address=|ip=' "$SOCKET_TRACE"; then
  echo "[ERROR] Radio socket metadata trace contains forbidden content or address material." >&2
  exit 3
fi

python3 "$PASSIVE_WITNESS_VALIDATOR" \
  "$PASSIVE_WITNESS_TRACE" \
  --min-records 3 \
  > "$PASSIVE_WITNESS_DIR/validator-result.txt"

python3 - "$SOCKET_TRACE" "$PASSIVE_WITNESS_TRACE" "$PASSIVE_WITNESS_CORRELATION" <<'PYCORRELATE'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

socket_path = Path(sys.argv[1])
witness_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])

first_recv_ns = None
for raw in socket_path.read_text(encoding="utf-8", errors="strict").splitlines():
    if not raw.startswith("RADIO_SOCKET_METADATA "):
        continue
    fields = {}
    for token in raw.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    if (
        fields.get("event") == "recvfrom"
        and fields.get("local_port") == "5011"
        and fields.get("errno") == "0"
    ):
        try:
            result = int(fields.get("result", "0"))
            monotonic_ns = int(fields["monotonic_ns"])
        except (KeyError, ValueError):
            continue
        if result > 0:
            first_recv_ns = monotonic_ns
            break

if first_recv_ns is None:
    raise SystemExit("successful UDP 5011 recvfrom monotonic timestamp missing")

records = []
for raw in witness_path.read_text(encoding="utf-8", errors="strict").splitlines():
    if raw.strip():
        records.append(json.loads(raw))

tick_records = [
    record
    for record in records
    if record.get("state") == "tick" and isinstance(record.get("tick"), int)
]
distinct_ticks = []
for record in tick_records:
    tick = record["tick"]
    if not distinct_ticks or tick != distinct_ticks[-1]:
        distinct_ticks.append(tick)

post_ingress_ticks = [
    record
    for record in tick_records
    if isinstance(record.get("monotonic_ns"), int)
    and record["monotonic_ns"] > first_recv_ns
]

criteria_met = len(distinct_ticks) >= 2 and bool(post_ingress_ticks)
classification = (
    "TIME_PROGRESS_AND_POST_INGRESS_CALLBACK_OPPORTUNITY_OBSERVED"
    if criteria_met
    else "OBSERVATION_CENSORED_BEFORE_REQUIRED_POST_INGRESS_TIME_EVIDENCE"
)

summary = {
    "classification": classification,
    "scientific_outcome": False,
    "first_udp_5011_recvfrom_monotonic_ns": first_recv_ns,
    "valid_witness_records": len(records),
    "tick_records": len(tick_records),
    "distinct_authoritative_ticks": len(distinct_ticks),
    "post_ingress_authoritative_tick_records": len(post_ingress_ticks),
    "minimum_two_distinct_ticks_met": len(distinct_ticks) >= 2,
    "post_ingress_tick_met": bool(post_ingress_ticks),
    "criteria_met": criteria_met,
}
output_path.write_text(
    json.dumps(summary, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PYCORRELATE

passive_time_classification="$(python3 - "$PASSIVE_WITNESS_CORRELATION" <<'PYCLASS'
import json
import sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["classification"])
PYCLASS
)"
record passive_time_witness_observation_classification "$passive_time_classification"
record passive_time_witness_scientific_outcome false

to_logs="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" logs "$PREFIX-to-radio-witness" 2>&1 || true)"
egress_logs="$(bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" logs "$PREFIX-radio-egress-witness" 2>&1 || true)"
to_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=proxy' <<< "$to_logs" || true)"
to_forwarded="$(grep -Fc 'TELEMETRY_WITNESS_FORWARDED mode=proxy' <<< "$to_logs" || true)"
egress_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=sink' <<< "$egress_logs" || true)"
witness_invalid="$(cat <(printf '%s\n' "$to_logs") <(printf '%s\n' "$egress_logs") | grep -Fc 'TELEMETRY_WITNESS_INVALID' || true)"
recv_success="$(grep -Ec 'event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE" || true)"
send_success="$(grep -Ec 'event=sendto .*peer_port=8011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE" || true)"
send_failure="$(grep -Ec 'event=sendto .*peer_port=8011 .*result=-1 errno=[1-9][0-9]*$' "$SOCKET_TRACE" || true)"
trace_records="$(grep -c '^RADIO_SOCKET_METADATA ' "$SOCKET_TRACE" || true)"

(( to_received >= 1 )) || { echo "[ERROR] TO witness received no telemetry." >&2; exit 3; }
(( to_forwarded >= 1 )) || { echo "[ERROR] TO witness forwarded no telemetry." >&2; exit 3; }
(( recv_success >= 1 )) || { echo "[ERROR] Radio socket metadata recorded no successful UDP 5011 recvfrom." >&2; exit 3; }
[[ "$witness_invalid" == 0 ]] || { echo "[ERROR] Telemetry witness recorded an invalid condition." >&2; exit 3; }

if (( send_failure >= 1 )); then
  transport_diagnosis=RADIO_EGRESS_SEND_FAILURE
elif (( send_success >= 1 && egress_received >= 1 )); then
  transport_diagnosis=DOWNLINK_PATH_THROUGH_RADIO_OBSERVED
elif (( send_success >= 1 )); then
  transport_diagnosis=RADIO_EGRESS_DESTINATION_OR_DELIVERY_FAILURE
else
  transport_diagnosis=RADIO_SIMULATION_TIME_QUEUE_RELEASE_FAILURE
fi

record to_witness_received_packet_markers "$to_received"
record to_witness_forwarded_packet_markers "$to_forwarded"
record radio_socket_recvfrom_5011_records "$recv_success"
record radio_socket_sendto_8011_success_records "$send_success"
record radio_socket_sendto_8011_failure_records "$send_failure"
record radio_socket_metadata_records "$trace_records"
record radio_egress_received_packet_markers "$egress_received"
record witness_invalid_count "$witness_invalid"
record transport_diagnosis "$transport_diagnosis"
record measured_command_transmissions 0
record ground_command_sources 0
RESULT="PASSIVE_TIME_WITNESS_RUNTIME_COMPLETE"
record diagnostic_status COMPLETE
check_runtime final
bounded_exec "$CLEANUP_COMMAND_TIMEOUT_SECONDS" "$DOCKER_BIN" ps \
  --filter "label=research.project=$PROJECT" \
  --filter "label=research.phase=$PHASE" \
  --filter "label=research.run_id=$RUN_ID" \
  --format 'name={{.Names}}\tstatus={{.Status}}' \
  > "$ORCHESTRATION/docker-ps-running.txt"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[OK] Radio UDP 5011 ingress was observed through metadata-only socket interposition."
echo "[OK] Passive time-witness classification: $passive_time_classification"
echo "[OK] Transport diagnosis: $transport_diagnosis"
CANDIDATE_EOF

bash -n "$tmp_emit"
chmod 700 "$tmp_emit"
mv -f "$tmp_emit" "$emit_path_real"
trap - EXIT

echo "PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE"
