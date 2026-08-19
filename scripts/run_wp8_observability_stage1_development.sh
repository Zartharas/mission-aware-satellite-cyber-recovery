#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 O01 <development-seed>" >&2
  exit 2
fi

CELL_ID="$1"
DEVELOPMENT_SEED="$2"

if [[ "$CELL_ID" != "O01" ]]; then
  echo "[ERROR] only frozen Stage-1 observability cell O01 is supported" >&2
  exit 2
fi

SEED="$DEVELOPMENT_SEED"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp8-observability-o01-dev}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-e4-proxy"
POLICY="mascr-$SAFE_ID-e4-policy"
GATEWAY="mascr-$SAFE_ID-p4-gateway"

E4_TLM_PORT=5013
GATEWAY_PORT=19091
GATEWAY_HOST="wp8-observability-gateway"
VISIBILITY_DEADLINE_NS=3000000000

EVIDENCE="$ROOT/results/wp8/runtime-binding/observability-executor-development/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

FACTOR_JSON="$GROUND/factor-context.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/policy-decision.json"

TRUTH_JSONL="$GROUND/telemetry-truth.jsonl"
POLICY_VISIBLE_JSONL="$OBS/policy-visible.jsonl"

ENABLE_JSON="$GROUND/enable-output.json"
EVENT_SEND_JSON="$GROUND/event-send-data-types.json"
POST_SEND_JSON="$GROUND/post-enforcement-send-data-types.json"

EVENT_SUCCESS_JSON="$GROUND/event-success.json"
POST_EFFECT_JSON="$GROUND/post-enforcement-effect.json"
P4_PROBE_JSON="$GROUND/p4-authorized-command-probe.json"
P4_GATEWAY_TRUTH="$GROUND/p4-command-gateway-truth.jsonl"
P4_GATEWAY_DECISIONS="$OBS/p4-command-gateway-decisions.jsonl"
HEALTH_JSON="$GROUND/observability-health.json"
MANIFEST_JSON="$GROUND/observability-evidence-manifest.json"
SUMMARY_JSON="$GROUND/observability-observation-summary.json"

OBSERVATION_JSON="$EVIDENCE/runtime-binding-observation.json"
RUN_RECORD="$EVIDENCE/run-record.json"
PROVENANCE="$EVIDENCE/binding-provenance.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"
TOOLCHAIN="$ROOT/configs/toolchain-lock.json"
SCHEMA="$ROOT/configs/experiment_run.schema.json"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

count_mid() {
  python3 - "$1" "$2" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
mid = int(sys.argv[2], 0)

if not path.exists():
    print(0)
    raise SystemExit(0)

count = 0
for line in path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    if json.loads(line).get("mid") == mid:
        count += 1
print(count)
PY
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

count_tolab_enable_markers() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'TO telemetry output enabled for IP ' || true
}

last_tolab_destination() {
  docker logs "$CFS" 2>&1 |
    grep -F 'TO telemetry output enabled for IP ' |
    tail -1 |
    sed -E 's/.*TO telemetry output enabled for IP ([^[:space:]]+).*/\1/'
}

assert_e4_destination_stable() {
  local observed_count observed_destination

  observed_count="$(count_tolab_enable_markers)"
  observed_destination="$(last_tolab_destination)"

  if [[ "$observed_count" -ne "$E4_TOLAB_ENABLE_COUNT" ]] ||
     [[ "$observed_destination" != "e4-proxy" ]]
  then
    echo "[ERROR] TO_LAB destination changed during E4 measurement." >&2
    echo "[ERROR] expected_enable_count=$E4_TOLAB_ENABLE_COUNT observed_enable_count=$observed_count" >&2
    echo "[ERROR] expected_destination=e4-proxy observed_destination=$observed_destination" >&2
    docker logs "$CFS" 2>&1 |
      grep -F 'TO telemetry output enabled for IP ' >&2 || true
    return 1
  fi
}

wait_until_ns() {
  local deadline_ns="$1"
  while true; do
    now="$(mono_ns)"
    if [[ "$now" -ge "$deadline_ns" ]]; then
      return 0
    fi
    sleep 0.05
  done
}

wait_for_mid_delta() {
  local path="$1" mid="$2" before="$3" delta="$4" label="$5"
  local expected now
  expected=$((before + delta))
  for _ in $(seq 1 40); do
    now="$(count_mid "$path" "$mid")"
    if [[ "$now" -eq "$expected" ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] $label count exceeded expected: now=$now expected=$expected" >&2
      return 2
    fi
    sleep 0.1
  done
  now="$(count_mid "$path" "$mid")"
  echo "[ERROR] $label timeout: now=$now expected=$expected" >&2
  return 1
}

wait_for_gateway_decision() {
  local expected_source="$1"
  for _ in $(seq 1 40); do
    if [[ -s "$P4_GATEWAY_DECISIONS" ]] && \
       python3 - "$P4_GATEWAY_DECISIONS" "$expected_source" <<'PY' >/dev/null 2>&1
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert rows
row = rows[-1]
assert row["source_id"] == sys.argv[2]
assert row["command_class"] == "sample_noop"
assert row["action"] == "ENTER_SAFE_MODE"
assert row["forwarded"] is False
PY
    then
      return 0
    fi
    sleep 0.1
  done
  echo "[ERROR] P4 gateway decision not observed" >&2
  return 1
}

run_e4_adapter() {
  local result_file="$1"
  shift
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.nos3_e4_adapter \
      "$@" \
      --result-json "/evidence/$result_file"
}

bind_invalid_observation() {
  [[ -f "$FACTOR_JSON" ]] || return 0
  [[ ! -f "$RUN_RECORD" ]] || return 0

  local invalid_reason
  invalid_reason="$(
    printf '%s' "$PHASE" |
    tr '[:upper:]' '[:lower:]' |
    tr -cs 'a-z0-9_' '_'
  )"
  invalid_reason="development_preflight_failure_phase_${invalid_reason}"

  PYTHONPATH="$ROOT" python3 - \
    "$FACTOR_JSON" "$TOOLCHAIN" "$EVIDENCE" \
    "$RUN_RECORD" "$PROVENANCE" "$invalid_reason" "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.wp8_runtime_binding import (
    bind_invalid_runtime_observation,
    environment_from_toolchain_lock,
)

(
    factor_path,
    toolchain_path,
    evidence_dir,
    run_record_path,
    provenance_path,
    invalid_reason,
    root_path,
) = sys.argv[1:]

factor = json.loads(Path(factor_path).read_text(encoding="utf-8"))
toolchain = json.loads(Path(toolchain_path).read_text(encoding="utf-8"))
root = Path(root_path)
evidence = Path(evidence_dir)

refs = []
for path in sorted(evidence.rglob("*")):
    if path.is_file():
        try:
            refs.append(str(path.relative_to(root)))
        except ValueError:
            refs.append(str(path))

result = bind_invalid_runtime_observation(
    factor_context=factor,
    environment=environment_from_toolchain_lock(
        toolchain,
        snapshot_id=f"repo-{factor['repo_commit']}",
        host_architecture=None,
    ),
    invalid_run_reason=invalid_reason,
    source_observation_refs=refs,
    notes=(
        "WP8 observability-family runtime-binding development preflight "
        "failed; retained as RUN_INVALID and is not pilot data."
    ),
)

Path(run_record_path).write_text(
    json.dumps(result["run_record"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(provenance_path).write_text(
    json.dumps(result["binding_provenance"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("invalid_run_retained=PASS")
print("invalid_run_reason=" + invalid_reason)
PY
}

cleanup() {
  local rc=$?
  set +e

  docker rm -f "$GATEWAY" "$PROXY" "$POLICY" >/dev/null 2>&1 || true

  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP8_OBSERVABILITY_STAGE1_DEVELOPMENT_EXECUTOR=PASS"
    echo "development_preflight=true"
    echo "pilot_data=false"
    echo "evidence_directory=$EVIDENCE"
  else
    bind_invalid_observation || true
    echo "WP8_OBSERVABILITY_STAGE1_DEVELOPMENT_EXECUTOR=FAIL" >&2
    echo "failure_phase=$PHASE" >&2
    echo "development_preflight=true" >&2
    echo "pilot_data=false" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi

  exit "$rc"
}
trap cleanup EXIT

for cmd in docker git python3 shasum; do
  command -v "$cmd" >/dev/null || {
    echo "[ERROR] missing required command: $cmd" >&2
    exit 1
  }
done

test -z "$(git -C "$ROOT" status --short)" || {
  echo "[ERROR] repository worktree must be clean before development runtime" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -   "$PILOT_CONFIG" "$CELL_ID" "$SEED" <<'PY'
import json
import sys
from pathlib import Path

pilot_path, cell_id, seed = sys.argv[1:]
pilot = json.loads(Path(pilot_path).read_text(encoding="utf-8"))
seed = int(seed)

reserved = {
    int(pilot["stage_1_control_validity"]["seed"]),
    *(
        int(value)
        for value in pilot["stage_2_variability"]["additional_seeds"]
    ),
}

if seed <= 0:
    raise SystemExit("development seed must be positive")

if seed in reserved:
    raise SystemExit(
        f"development seed collides with frozen pilot seed: {seed}"
    )

cells = {
    row["cell_id"]: row
    for row in pilot["cells"]
}

if cell_id != "O01" or cell_id not in cells:
    raise SystemExit("only frozen Stage-1 observability cell O01 is supported")

cell = cells[cell_id]

expected = {
    "family": "observability_p7",
    "event_id": "E4",
    "mission_state_id": "M2",
    "contact_condition_id": "C0",
    "evidence_condition_id": "T0",
    "policy_id": "P7",
    "expected_effective_policy_id": "P4",
}

for key, value in expected.items():
    if cell[key] != value:
        raise SystemExit(
            f"O01 frozen factor changed: {key}={cell[key]!r}"
        )

print("o01_development_seed_preflight=PASS")
print("o01_pilot_seed_collision=false")
PY

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

mkdir -p "$GROUND" "$OBS"
: > "$TRUTH_JSONL"
: > "$POLICY_VISIBLE_JSONL"
: > "$P4_GATEWAY_TRUTH"
: > "$P4_GATEWAY_DECISIONS"

REPO_COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
RUNNER_SHA="$(shasum -a 256 "$ROOT/scripts/run_wp8_observability_stage1_development.sh" | awk '{print $1}')"

PHASE="FACTOR_EVENT_MATERIALIZATION"

PYTHONPATH="$ROOT" python3 - \
  "$PILOT_CONFIG" "$FACTOR_JSON" "$EVENT_JSON" \
  "$RUN_ID" "$CELL_ID" "$SEED" "$REPO_COMMIT" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event

(
    pilot_path,
    factor_path,
    event_path,
    run_id,
    cell_id,
    seed,
    repo_commit,
) = sys.argv[1:]

seed = int(seed)
pilot = json.loads(
    Path(pilot_path).read_text(encoding="utf-8")
)

cells = {
    row["cell_id"]: row
    for row in pilot["cells"]
}
cell = cells[cell_id]

assert cell_id == "O01"
assert cell["family"] == "observability_p7"
assert cell["event_id"] == "E4"
assert cell["mission_state_id"] == "M2"
assert cell["contact_condition_id"] == "C0"
assert cell["evidence_condition_id"] == "T0"
assert cell["policy_id"] == "P7"
assert cell["expected_effective_policy_id"] == "P4"

event = materialize_event(
    cell["event_id"],
    mission_state=cell["mission_state_id"],
    contact_condition=cell["contact_condition_id"],
    evidence_condition=cell["evidence_condition_id"],
    seed=seed,
)

assert event["event_id"] == "E4"
assert event["policy_visible_evidence"]["telemetry_stream_present"] is True
assert event["policy_visible_evidence"]["high_value_channels_complete"] is False
assert event["policy_visible_evidence"]["evidence_fresh"] is False
assert event["policy_visible_evidence"]["state_estimate_complete"] is False
assert event["ground_truth"]["telemetry_truth_available"] is True

factor = {
    "run_id": run_id,
    "model_version": pilot["model_version"],
    "seed": seed,
    "mission_state_id": cell["mission_state_id"],
    "event_id": cell["event_id"],
    "policy_id": cell["policy_id"],
    "contact_condition_id": cell["contact_condition_id"],
    "evidence_condition_id": cell["evidence_condition_id"],
    "repo_commit": repo_commit,
}

Path(factor_path).write_text(
    json.dumps(factor, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(event_path).write_text(
    json.dumps(event, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("observability_factor_event_materialization=PASS")
PY

echo "development_seed=$SEED"
echo "pilot_seed_consumed=false"
echo "study_cell=O01"
echo "study_event=E4"
echo "requested_policy=P7"
echo "expected_effective_policy=P4"

PHASE="NOMINAL_RUNTIME_LAUNCH"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=45 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"

CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  if [[ "$state" == running ]]; then
    CFS_READY=1
    break
  fi
  sleep 1
done

[[ "$CFS_READY" -eq 1 ]] || {
  echo "[ERROR] nominal cFS container not observed" >&2
  tail -120 "$NOMINAL_LOG" >&2 || true
  exit 1
}

echo "nominal_cfs_running=PASS"

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394\$/ {found=1} END {exit found ? 0 : 1}'" \
    >/dev/null 2>&1
  then
    CI_READY=1
    break
  fi
  sleep 1
done

[[ "$CI_READY" -eq 1 ]] || {
  echo "[ERROR] cFS CI_LAB UDP 5012 not ready" >&2
  exit 1
}

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]

echo "nominal_ci_lab_udp_5012=PASS"
echo "nominal_isolation=PASS"

PHASE="NOMINAL_TOLAB_DESTINATION_SETTLE"

NOMINAL_TOLAB_READY=0
for _ in $(seq 1 60); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker logs "$CFS" 2>&1 |
    grep -Fq 'TO telemetry output enabled for IP active-gs'
  then
    NOMINAL_TOLAB_READY=1
    break
  fi
  sleep 0.2
done

[[ "$NOMINAL_TOLAB_READY" -eq 1 ]] || {
  echo "[ERROR] nominal TO_LAB destination initialization was not observed" >&2
  exit 1
}

NOMINAL_TOLAB_ENABLE_COUNT="$(count_tolab_enable_markers)"
NOMINAL_TOLAB_LAST_DESTINATION="$(last_tolab_destination)"

[[ "$NOMINAL_TOLAB_LAST_DESTINATION" == "active-gs" ]] || {
  echo "[ERROR] nominal TO_LAB destination did not settle on active-gs" >&2
  exit 1
}

echo "nominal_tolab_destination_settle=PASS"
echo "nominal_tolab_destination=active-gs"
echo "nominal_tolab_enable_count=$NOMINAL_TOLAB_ENABLE_COUNT"

PHASE="E4_MEASUREMENT_PLANE"

docker run -d --platform linux/amd64 \
  --name "$POLICY" \
  --hostname e4-policy \
  --network "$NETWORK" \
  --network-alias e4-policy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$OBS,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility observer \
    --jsonl /evidence/policy-visible.jsonl \
    --port 19090 >/dev/null

docker run -d --platform linux/amd64 \
  --name "$PROXY" \
  --hostname e4-proxy \
  --network "$NETWORK" \
  --network-alias e4-proxy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/truth" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility proxy \
    --truth-jsonl /truth/telemetry-truth.jsonl \
    --mode degraded \
    --listen-port "$E4_TLM_PORT" \
    --policy-host e4-policy \
    --policy-port 19090 >/dev/null

PROXY_READY=0
HEX_TLM_PORT="$(printf '%04X' "$E4_TLM_PORT")"
for _ in $(seq 1 30); do
  if [[ "$(docker inspect "$PROXY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$PROXY" sh -lc \
       "awk '\$2 ~ /:${HEX_TLM_PORT}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1 &&
     [[ "$(docker inspect "$POLICY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]
  then
    PROXY_READY=1
    break
  fi
  sleep 0.2
done

[[ "$PROXY_READY" -eq 1 ]] || {
  echo "[ERROR] degraded E4 measurement plane not ready" >&2
  exit 1
}

run_e4_adapter "$(basename "$ENABLE_JSON")" enable-output --destination e4-proxy

ENABLE_READY=0
for _ in $(seq 1 30); do
  if docker logs "$CFS" 2>&1 |
    grep -Fq 'TO telemetry output enabled for IP e4-proxy'
  then
    ENABLE_READY=1
    break
  fi
  sleep 0.2
done

[[ "$ENABLE_READY" -eq 1 ]]

E4_TOLAB_ENABLE_COUNT="$(count_tolab_enable_markers)"
E4_TOLAB_LAST_DESTINATION="$(last_tolab_destination)"

test "$E4_TOLAB_ENABLE_COUNT" -eq $((NOMINAL_TOLAB_ENABLE_COUNT + 1))
test "$E4_TOLAB_LAST_DESTINATION" = "e4-proxy"

echo "e4_tolab_destination_ownership=PASS"
echo "e4_tolab_destination=e4-proxy"
echo "e4_tolab_enable_count=$E4_TOLAB_ENABLE_COUNT"

PHASE="E4_DESTINATION_STABILITY"
assert_e4_destination_stable

TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POLICY_BEFORE="$(count_mid "$POLICY_VISIBLE_JSONL" 0x08E9)"
test "$TRUTH_BEFORE" -eq 0
test "$POLICY_BEFORE" -eq 0

echo "degraded_e4_measurement_plane_ready=PASS"
echo "high_value_mid=0x08E9"
echo "visibility_deadline_s=3.0"

RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PHASE="E4_DESTINATION_STABILITY"
assert_e4_destination_stable

PHASE="EVENT_ACTIVATION"

EVENT_ACTIVATION_NS="$(mono_ns)"
EVENT_DEADLINE_NS=$((EVENT_ACTIVATION_NS + VISIBILITY_DEADLINE_NS))

run_e4_adapter "$(basename "$EVENT_SEND_JSON")" send-data-types

echo "e4_high_value_sample_injected=PASS"
echo "event_activation_before_response=true"

PHASE="POLICY_SELECTION"

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$POLICY_JSON" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.policies import evaluate_policy

event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision = evaluate_policy("P7", event)

assert event["event_id"] == "E4"
assert event["mission_state"] == "M2"
assert event["contact_condition"] == "C0"
assert event["evidence_condition"] == "T0"

assert decision["requested_policy_id"] == "P7"
assert decision["delegated_policy_id"] == "P4"
assert decision["selected_action"] == "ENTER_SAFE_MODE"
assert decision["decision_basis"] == "evidence_insufficient"
assert decision["evidence_insufficient"] is True
assert decision["oracle_ground_truth_read"] is False

Path(sys.argv[2]).write_text(
    json.dumps(decision, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("p7_observability_policy_selection=PASS")
print("effective_policy=P4")
print("selected_action=ENTER_SAFE_MODE")
print("policy_trigger_uses_ground_truth=false")
PY

POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS"

PHASE="POLICY_ENFORCEMENT"

docker run -d --platform linux/amd64 \
  --name "$GATEWAY" \
  --hostname p4-gateway \
  --network "$NETWORK" \
  --network-alias "$GATEWAY_HOST" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/ground" \
  --mount "type=bind,source=$OBS,target=/obs" \
  "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway serve \
    --action ENTER_SAFE_MODE \
    --truth-jsonl /ground/p4-command-gateway-truth.jsonl \
    --decision-jsonl /obs/p4-command-gateway-decisions.jsonl >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' "$GATEWAY_PORT")"
for _ in $(seq 1 30); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$GATEWAY" sh -lc \
       "awk '\$2 ~ /:${HEX_GATEWAY_PORT}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 0.2
done

[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] P4 command gate not ready" >&2
  exit 1
}

POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"

echo "p4_modeled_command_gate_enforcement=PASS"
echo "p4_native_safe_mode_claim=false"
echo "p4_telemetry_restoration_claim=false"

PHASE="EVENT_SUCCESS_OBSERVATION"

wait_until_ns "$EVENT_DEADLINE_NS"

PHASE="E4_DESTINATION_STABILITY"
assert_e4_destination_stable
PHASE="EVENT_SUCCESS_OBSERVATION"

TRUTH_EVENT_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POLICY_EVENT_AFTER="$(count_mid "$POLICY_VISIBLE_JSONL" 0x08E9)"

test "$TRUTH_EVENT_AFTER" -eq $((TRUTH_BEFORE + 1))
test "$POLICY_EVENT_AFTER" -eq "$POLICY_BEFORE"

EVENT_SUCCESS_NS="$(mono_ns)"
test "$EVENT_SUCCESS_NS" -ge "$EVENT_DEADLINE_NS"
test "$EVENT_SUCCESS_NS" -ge "$POLICY_ENFORCEMENT_NS"

python3 - \
  "$EVENT_SUCCESS_JSON" \
  "$EVENT_ACTIVATION_NS" "$EVENT_DEADLINE_NS" "$EVENT_SUCCESS_NS" \
  "$TRUTH_BEFORE" "$TRUTH_EVENT_AFTER" \
  "$POLICY_BEFORE" "$POLICY_EVENT_AFTER" <<'PY'
import json
import sys
from pathlib import Path

(
    path,
    event_activation_ns,
    deadline_ns,
    observed_ns,
    truth_before,
    truth_after,
    policy_before,
    policy_after,
) = sys.argv[1:]

payload = {
    "schema": 1,
    "event_id": "E4",
    "high_value_mid": "0x08E9",
    "event_activation_ns": int(event_activation_ns),
    "visibility_deadline_ns": int(deadline_ns),
    "event_success_observed_ns": int(observed_ns),
    "truth_high_value_delta": int(truth_after) - int(truth_before),
    "policy_visible_high_value_delta": int(policy_after) - int(policy_before),
    "event_success": True,
    "predicate": (
        "immutable_truth_observes_required_high_value_telemetry_and_"
        "no_matching_policy_visible_record_is_observed_before_"
        "the_frozen_visibility_deadline"
    ),
}

assert payload["truth_high_value_delta"] == 1
assert payload["policy_visible_high_value_delta"] == 0
assert payload["event_success_observed_ns"] >= payload["visibility_deadline_ns"]

Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("e4_event_success_after_3s_deadline=PASS")
PY

echo "event_success_observed=true"
echo "event_success_truth_delta=1"
echo "event_success_policy_visible_delta=0"
echo "policy_selection_not_gated_on_event_success=true"
echo "policy_enforcement_not_gated_on_event_success=true"

PHASE="POST_ENFORCEMENT_P4_COMMAND_COST"

NOOP_BEFORE="$(count_noop_marker)"

docker run --rm -i --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 - "$GATEWAY_HOST" "/evidence/$(basename "$P4_PROBE_JSON")" <<'PY'
import hashlib
import json
import socket
import sys
from pathlib import Path

from src.mission_recovery.policy_gateway import (
    GATEWAY_PORT,
    build_sample_noargs_packet,
)

gateway_host = sys.argv[1]
result_path = Path(sys.argv[2])

packet = build_sample_noargs_packet("sample_noop")
packet_sha256 = hashlib.sha256(packet).hexdigest()

assert packet.hex() == "18fac000000100dc"
assert packet_sha256 == (
    "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"
)

envelope = {
    "schema": 1,
    "event_id": None,
    "study_event": False,
    "probe_variant": "observability_p4_legitimate_command_cost",
    "source_id": "authorized_ground",
    "command_class": "sample_noop",
    "declared_risk_class": "low",
    "packet_hex": packet.hex(),
    "packet_sha256": packet_sha256,
}

encoded = (
    json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n"
).encode("utf-8")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sent = sock.sendto(encoded, (gateway_host, GATEWAY_PORT))

assert sent == len(encoded)

result = {
    "schema": 1,
    "study_event": False,
    "event_id": None,
    "role": "P4_legitimate_command_availability_probe",
    "source_id": "authorized_ground",
    "command_class": "sample_noop",
    "gateway": f"{gateway_host}:{GATEWAY_PORT}",
    "packet_hex": packet.hex(),
    "packet_sha256": packet_sha256,
    "envelope_bytes_sent": sent,
}

result_path.write_text(
    json.dumps(result, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(result, sort_keys=True))
PY

wait_for_gateway_decision "authorized_ground"
sleep 0.5

NOOP_AFTER="$(count_noop_marker)"
test "$NOOP_AFTER" -eq "$NOOP_BEFORE"

python3 - "$P4_GATEWAY_DECISIONS" <<'PY'
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert rows
row = rows[-1]

assert row["action"] == "ENTER_SAFE_MODE"
assert row["source_id"] == "authorized_ground"
assert row["command_class"] == "sample_noop"
assert row["forwarded"] is False

print("p4_authorized_noop_rejected=PASS")
PY

echo "legitimate_commands_attempted=1"
echo "legitimate_commands_rejected=1"
echo "legitimate_command_rejection_rate_expected=1.0"
echo "p4_command_availability_cost_observed=true"

PHASE="E4_DESTINATION_STABILITY"
assert_e4_destination_stable

PHASE="POST_ENFORCEMENT_EFFECT_PROBE"

POST_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_POLICY_BEFORE="$(count_mid "$POLICY_VISIBLE_JSONL" 0x08E9)"
POST_PROBE_ACTIVATION_NS="$(mono_ns)"
POST_PROBE_DEADLINE_NS=$((POST_PROBE_ACTIVATION_NS + VISIBILITY_DEADLINE_NS))

run_e4_adapter "$(basename "$POST_SEND_JSON")" send-data-types

wait_until_ns "$POST_PROBE_DEADLINE_NS"

PHASE="E4_DESTINATION_STABILITY"
assert_e4_destination_stable
PHASE="POST_ENFORCEMENT_EFFECT_PROBE"

POST_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_POLICY_AFTER="$(count_mid "$POLICY_VISIBLE_JSONL" 0x08E9)"

test "$POST_TRUTH_AFTER" -eq $((POST_TRUTH_BEFORE + 1))
test "$POST_POLICY_AFTER" -eq "$POST_POLICY_BEFORE"

POST_EFFECT_NS="$(mono_ns)"

python3 - \
  "$POST_EFFECT_JSON" \
  "$POST_PROBE_ACTIVATION_NS" "$POST_PROBE_DEADLINE_NS" "$POST_EFFECT_NS" \
  "$POST_TRUTH_BEFORE" "$POST_TRUTH_AFTER" \
  "$POST_POLICY_BEFORE" "$POST_POLICY_AFTER" <<'PY'
import json
import sys
from pathlib import Path

(
    path,
    probe_activation_ns,
    deadline_ns,
    observed_ns,
    truth_before,
    truth_after,
    policy_before,
    policy_after,
) = sys.argv[1:]

payload = {
    "schema": 1,
    "high_value_mid": "0x08E9",
    "probe_activation_ns": int(probe_activation_ns),
    "visibility_deadline_ns": int(deadline_ns),
    "observation_ns": int(observed_ns),
    "truth_high_value_delta": int(truth_after) - int(truth_before),
    "policy_visible_high_value_delta": int(policy_after) - int(policy_before),
    "containment_observed": False,
    "required_telemetry_restored": False,
    "p4_changed_telemetry_path": False,
}

assert payload["truth_high_value_delta"] == 1
assert payload["policy_visible_high_value_delta"] == 0
assert payload["containment_observed"] is False
assert payload["required_telemetry_restored"] is False

Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("post_enforcement_matched_telemetry_probe=PASS")
print("observability_containment_observed=false")
print("required_telemetry_restored=false")
PY

echo "time_to_containment_expected=null"
echo "time_to_verified_recovery_expected=null"
echo "p4_selection_is_not_observability_containment=true"

PHASE="OBSERVABILITY_EVIDENCE_MANIFEST"

[[ "$(docker inspect "$CFS" --format '{{.State.Status}}')" == running ]]
[[ "$(docker inspect "$PROXY" --format '{{.State.Status}}')" == running ]]
[[ "$(docker inspect "$POLICY" --format '{{.State.Status}}')" == running ]]
[[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}')" == running ]]

docker exec "$CFS" sh -lc \
  "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394\$/ {found=1} END {exit found ? 0 : 1}'"

HEALTH_NS="$(mono_ns)"

python3 - \
  "$HEALTH_JSON" "$HEALTH_NS" \
  "$TRUTH_JSONL" "$POLICY_VISIBLE_JSONL" \
  "$P4_GATEWAY_DECISIONS" "$EVENT_SUCCESS_JSON" "$POST_EFFECT_JSON" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

(
    path,
    health_ns,
    truth_path,
    policy_path,
    gateway_decisions_path,
    event_success_path,
    post_effect_path,
) = sys.argv[1:]

event_success = json.loads(
    Path(event_success_path).read_text(encoding="utf-8")
)
post_effect = json.loads(
    Path(post_effect_path).read_text(encoding="utf-8")
)

gateway_rows = [
    json.loads(line)
    for line in Path(gateway_decisions_path).read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]
assert gateway_rows
gateway = gateway_rows[-1]

payload = {
    "schema": 1,
    "health_check_monotonic_ns": int(health_ns),
    "cfs_running": True,
    "ci_lab_udp_5012_ready": True,
    "immutable_truth_available": True,
    "policy_visible_plane_available": True,
    "p4_command_gate_running": True,
    "p4_authorized_noop_forwarded": gateway["forwarded"],
    "event_success_confirmed": event_success["event_success"],
    "post_enforcement_containment_observed": post_effect["containment_observed"],
    "required_telemetry_restored": post_effect["required_telemetry_restored"],
    "truth_sha256": hashlib.sha256(
        Path(truth_path).read_bytes()
    ).hexdigest(),
    "policy_visible_sha256": hashlib.sha256(
        Path(policy_path).read_bytes()
    ).hexdigest(),
    "gateway_decisions_sha256": hashlib.sha256(
        Path(gateway_decisions_path).read_bytes()
    ).hexdigest(),
    "health_checks_passed": True,
}

assert payload["p4_authorized_noop_forwarded"] is False
assert payload["event_success_confirmed"] is True
assert payload["post_enforcement_containment_observed"] is False
assert payload["required_telemetry_restored"] is False
assert payload["health_checks_passed"] is True

Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("observability_health_snapshot=PASS")
PY

MANIFEST_READY_NS="$(mono_ns)"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_observability_evidence manifest \
  --root "$ROOT" \
  --output "$MANIFEST_JSON" \
  --event-json "$EVENT_JSON" \
  --policy-json "$POLICY_JSON" \
  --event-success-json "$EVENT_SUCCESS_JSON" \
  --post-effect-json "$POST_EFFECT_JSON" \
  --p4-probe-json "$P4_PROBE_JSON" \
  --p4-gateway-truth "$P4_GATEWAY_TRUTH" \
  --p4-gateway-decisions "$P4_GATEWAY_DECISIONS" \
  --truth-jsonl "$TRUTH_JSONL" \
  --policy-visible-jsonl "$POLICY_VISIBLE_JSONL" \
  --health-json "$HEALTH_JSON" \
  --event-activation-ns "$EVENT_ACTIVATION_NS" \
  --policy-selection-ns "$POLICY_SELECTION_NS" \
  --policy-enforcement-ns "$POLICY_ENFORCEMENT_NS" \
  --event-success-ns "$EVENT_SUCCESS_NS" \
  --post-effect-ns "$POST_EFFECT_NS" \
  --health-ns "$HEALTH_NS" \
  --manifest-ready-ns "$MANIFEST_READY_NS"
RUN_END_NS="$(mono_ns)"
RUN_END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "observability_terminal_candidate=RECOVERY_FAILED"
echo "observability_terminal_claim_is_spacecraft_failure=false"
echo "containment_right_censored=true"
echo "trusted_recovery_right_censored=true"

PHASE="POST_RUN_NOMINAL_VALIDATION"

docker rm -f "$GATEWAY" "$PROXY" "$POLICY" >/dev/null

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$RUNTIME_MANIFEST"

echo "validated_nominal_runtime_pass=true"

PHASE="OBSERVATION_BINDING"

REL="results/wp8/runtime-binding/observability-executor-development/$RUN_ID"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_observability_evidence materialize \
  --factor-json "$FACTOR_JSON" \
  --summary-json "$SUMMARY_JSON" \
  --observation-json "$OBSERVATION_JSON" \
  --run-start-ns "$RUN_START_NS" \
  --event-activation-ns "$EVENT_ACTIVATION_NS" \
  --event-success-ns "$EVENT_SUCCESS_NS" \
  --policy-selection-ns "$POLICY_SELECTION_NS" \
  --policy-enforcement-ns "$POLICY_ENFORCEMENT_NS" \
  --run-end-ns "$RUN_END_NS" \
  --run-start-utc "$RUN_START_UTC" \
  --run-end-utc "$RUN_END_UTC" \
  --repo-commit "$REPO_COMMIT" \
  --runner-sha "$RUNNER_SHA" \
  --rel "$REL"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_runtime_binding \
  --observation-json "$OBSERVATION_JSON" \
  --pilot-config "$PILOT_CONFIG" \
  --toolchain-lock "$TOOLCHAIN" \
  --snapshot-id "repo-$REPO_COMMIT" \
  --host-architecture "$(uname -m)" \
  --output-run-json "$RUN_RECORD" \
  --output-provenance-json "$PROVENANCE"

PHASE="BOUND_RECORD_VALIDATION"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_observability_evidence validate \
  --schema "$SCHEMA" \
  --run-record "$RUN_RECORD" \
  --provenance "$PROVENANCE" \
  --summary "$SUMMARY_JSON" \
  --manifest "$MANIFEST_JSON"
RESULT="PASS"
PHASE="COMPLETE"
