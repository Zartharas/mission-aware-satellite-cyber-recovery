#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 <C01-C07> <development-seed>" >&2
  exit 2
fi

CELL_ID="$1"
DEVELOPMENT_SEED="$2"

CELL_SAFE="$(printf '%s' "$CELL_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp8-command-${CELL_SAFE}-dev}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-wp8-gateway"

EVIDENCE="$ROOT/results/wp8/runtime-binding/command-executor-development/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

PLAN_JSON="$GROUND/execution-plan.json"
FACTOR_JSON="$GROUND/factor-context.json"
EVENT_JSON="$GROUND/event-instance.json"
EVENT_SEND_JSON="$GROUND/event-activation-send.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
INGRESS_JSONL="$GROUND/gateway-ingress.jsonl"
DECISION_JSONL="$GROUND/gateway-decisions.jsonl"
ATTACKER1_JSON="$GROUND/attacker-reset-probe-1.json"
ATTACKER2_JSON="$GROUND/attacker-reset-probe-2.json"
AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"
MEASUREMENT_JSON="$GROUND/command-runtime-measurement.json"
DERIVED_JSON="$GROUND/command-runtime-observation-derived.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"

PRE_PID=""
EVENT_WATCH_PID=""
EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"
EVENT_RESET_AFTER_FILE="$OBS/event-reset-after.txt"

RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
EFFECT_SETTLE_SECONDS="0.8"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

count_reset_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: RESET counters command received' || true
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

decision_count() {
  python3 - "$DECISION_JSONL" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    print(0)
else:
    print(
        sum(
            1
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    )
PY
}

wait_decision_count() {
  local expected="$1"
  local now
  for _ in $(seq 1 75); do
    now="$(decision_count)"
    if [[ "$now" -eq "$expected" ]]; then
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] gateway decision count exceeded $expected" >&2
      return 2
    fi
    sleep 0.2
  done
  echo "[ERROR] gateway decision count did not reach $expected" >&2
  return 1
}

emit_invalid_evidence() {
  local rc="$1"
  [[ -d "$EVIDENCE" ]] || return 0
  [[ -f "$INVALID_JSON" ]] && return 0

  python3 - \
    "$INVALID_JSON" "$RUN_ID" "$CELL_ID" "$DEVELOPMENT_SEED" \
    "$PHASE" "$rc" "${REPO_COMMIT:-unknown}" <<'PY'
import json
import sys
from pathlib import Path

path, run_id, cell_id, seed, phase, rc, commit = sys.argv[1:]
payload = {
    "schema": 1,
    "classification": "WP8_COMMAND_EXECUTOR_DEVELOPMENT_RUN_INVALID",
    "run_id": run_id,
    "cell_id": cell_id,
    "development_seed": int(seed),
    "failed_phase": phase,
    "exit_code": int(rc),
    "repo_commit": commit,
    "development_preflight": True,
    "pilot_data": False,
    "pilot_seed_consumed": False,
    "fabricated_primary_metrics": False,
    "runtime_binding_performed": False,
}
Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY
}

cleanup() {
  local rc=$?
  set +e

  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true

  if [[ -n "$EVENT_WATCH_PID" ]] &&
     kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1
  then
    kill -TERM "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
    wait "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" != "PASS" || "$rc" -ne 0 ]]; then
    emit_invalid_evidence "$rc" || true
    echo "WP8_COMMAND_STAGE1_DEVELOPMENT_EXECUTOR=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  else
    echo "WP8_COMMAND_STAGE1_DEVELOPMENT_EXECUTOR=PASS"
    echo "development_preflight=true"
    echo "pilot_data=false"
    echo "pilot_seed_consumed=false"
    echo "runtime_binding_performed=false"
    echo "evidence_directory=$EVIDENCE"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

cd "$ROOT"

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before development runtime" >&2
  exit 1
}

for command in docker git python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable" >&2
  exit 1
}

REPO_COMMIT="$(git rev-parse HEAD)"

mkdir -p "$GROUND" "$OBS"
: > "$INGRESS_JSONL"
: > "$DECISION_JSONL"

PHASE="DEVELOPMENT_PLAN_PREFLIGHT"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_command_runtime_executor \
  plan \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --development-seed "$DEVELOPMENT_SEED" \
  --run-id "$RUN_ID" \
  --output-plan-json "$PLAN_JSON" \
  --output-factor-json "$FACTOR_JSON" \
  --output-event-json "$EVENT_JSON"

echo "development_plan_preflight=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"

PHASE="CFS_READINESS"

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

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {found=1} END {exit found ? 0 : 1}'" \
    >/dev/null 2>&1
  then
    CI_READY=1
    break
  fi
  sleep 1
done

[[ "$CI_READY" -eq 1 ]]
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]

echo "nominal_cfs_running=PASS"
echo "nominal_ci_lab_udp_5012=PASS"
echo "nominal_isolation=PASS"

PHASE="EVENT_ACTIVATION"

RESET_BEFORE_EVENT="$(count_reset_marker)"
EVENT_ACTIVATION_NS="$(mono_ns)"

(
  for _ in $(seq 1 150); do
    now="$(count_reset_marker)"
    if [[ "$now" -eq $((RESET_BEFORE_EVENT + 1)) ]]; then
      mono_ns > "$EVENT_SUCCESS_NS_FILE"
      printf '%s\n' "$now" > "$EVENT_RESET_AFTER_FILE"
      exit 0
    fi
    if [[ "$now" -gt $((RESET_BEFORE_EVENT + 1)) ]]; then
      echo "[ERROR] event activation reset marker exceeded expected delta" >&2
      exit 2
    fi
    sleep 0.1
  done
  echo "[ERROR] event activation reset marker not observed" >&2
  exit 1
) &
EVENT_WATCH_PID=$!

docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.nos3_e1_adapter \
    --event-json /evidence/event-instance.json \
    --command-class sample_reset_counters \
    --result-json /evidence/event-activation-send.json

python3 - "$EVENT_SEND_JSON" <<'PY'
import json
import sys
from pathlib import Path

row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["command_class"] == "sample_reset_counters"
assert row["target"] == "nos-fsw:5012"
assert row["packet_sha256"] == (
    "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
)
print("e1_direct_reset_activation=PASS")
PY

echo "event_activation_before_response=true"
echo "policy_trigger_uses_ground_truth=false"

PHASE="POLICY_SELECTION"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_command_runtime_executor \
  select-policy \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --event-json "$EVENT_JSON" \
  --output-policy-json "$POLICY_JSON"

SELECTED_ACTION="$(
  python3 - "$POLICY_JSON" <<'PY'
import json
import sys
from pathlib import Path

row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(row["selected_action"])
PY
)"

POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS"

echo "runtime_policy_selection=PASS"
echo "selected_action=$SELECTED_ACTION"

PHASE="POLICY_ENFORCEMENT"

docker run -d --platform linux/amd64 \
  --name "$GATEWAY" \
  --hostname wp8-gateway \
  --network "$NETWORK" \
  --network-alias wp8-gateway \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway serve \
    --action "$SELECTED_ACTION" \
    --isolated-source modeled_attacker \
    --truth-jsonl /evidence/gateway-ingress.jsonl \
    --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' 19091)"
for _ in $(seq 1 75); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] &&
     docker exec "$GATEWAY" sh -lc \
       "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 0.2
done

[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] WP8 command gateway did not become ready" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}

POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"

echo "policy_gateway_ready=PASS"
echo "policy_enforcement_after_event_activation=true"
echo "policy_enforcement_waits_for_event_success=false"

PHASE="EVENT_SUCCESS_CONFIRMATION"

set +e
wait "$EVENT_WATCH_PID"
EVENT_WATCH_RC=$?
set -e
EVENT_WATCH_PID=""

[[ "$EVENT_WATCH_RC" -eq 0 ]] || {
  echo "[ERROR] immutable event-success watcher failed: rc=$EVENT_WATCH_RC" >&2
  exit 1
}

EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"
RESET_AFTER_EVENT="$(cat "$EVENT_RESET_AFTER_FILE")"

test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"
test "$RESET_AFTER_EVENT" -eq $((RESET_BEFORE_EVENT + 1))

echo "immutable_ground_truth_watcher=PASS"
echo "event_success_observed=true"
echo "policy_selection_not_gated_on_event_success=true"

send_gateway_command() {
  local source_id="$1"
  local command_class="$2"
  local result_file="$3"

  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id "$source_id" \
      --command-class "$command_class" \
      --gateway-host wp8-gateway \
      --result-json "/evidence/$result_file"
}

PHASE="POST_ENFORCEMENT_ATTACKER_PROBES"

RESET_BEFORE_ATTACKER="$(count_reset_marker)"

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER1_JSON")"
wait_decision_count 1

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER2_JSON")"
wait_decision_count 2

sleep "$EFFECT_SETTLE_SECONDS"

RESET_AFTER_ATTACKER="$(count_reset_marker)"
SECOND_ATTACKER_PROBE_OBSERVED_NS="$(mono_ns)"

echo "matched_attacker_reset_probe_count=2"
echo "observed_post_enforcement_attacker_reset_marker_delta=$((RESET_AFTER_ATTACKER - RESET_BEFORE_ATTACKER))"

PHASE="AUTHORIZED_SERVICE_PROBE"

NOOP_BEFORE="$(count_noop_marker)"

send_gateway_command \
  authorized_ground sample_noop \
  "$(basename "$AUTHORIZED_JSON")"
wait_decision_count 3

sleep "$EFFECT_SETTLE_SECONDS"

NOOP_AFTER="$(count_noop_marker)"
AUTHORIZED_NOOP_PROBE_OBSERVED_NS="$(mono_ns)"

echo "legitimate_commands_attempted=1"
echo "observed_authorized_noop_marker_delta=$((NOOP_AFTER - NOOP_BEFORE))"

docker rm -f "$GATEWAY" >/dev/null

PHASE="NOMINAL_RUNTIME_COMPLETION"

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

RUN_END_NS="$(mono_ns)"

PHASE="RAW_OBSERVATION_MATERIALIZATION"

python3 - \
  "$MEASUREMENT_JSON" "$RUN_ID" \
  "$RESET_BEFORE_EVENT" "$RESET_AFTER_EVENT" \
  "$RESET_BEFORE_ATTACKER" "$RESET_AFTER_ATTACKER" \
  "$NOOP_BEFORE" "$NOOP_AFTER" \
  "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_ENFORCEMENT_NS" \
  "$SECOND_ATTACKER_PROBE_OBSERVED_NS" \
  "$AUTHORIZED_NOOP_PROBE_OBSERVED_NS" \
  "$RUN_END_NS" <<'PY'
import json
import sys
from pathlib import Path

(
    path,
    run_id,
    reset_before_event,
    reset_after_event,
    reset_before_attacker,
    reset_after_attacker,
    noop_before,
    noop_after,
    event_activation_ns,
    event_success_ns,
    policy_enforcement_ns,
    second_attacker_probe_observed_ns,
    authorized_noop_probe_observed_ns,
    run_end_ns,
) = sys.argv[1:]

payload = {
    "schema": 1,
    "run_id": run_id,
    "counts": {
        "reset_before_event": int(reset_before_event),
        "reset_after_event": int(reset_after_event),
        "reset_before_attacker": int(reset_before_attacker),
        "reset_after_attacker": int(reset_after_attacker),
        "noop_before": int(noop_before),
        "noop_after": int(noop_after),
    },
    "timestamps_ns": {
        "event_activation_ns": int(event_activation_ns),
        "event_success_ns": int(event_success_ns),
        "policy_enforcement_ns": int(policy_enforcement_ns),
        "second_attacker_probe_observed_ns": int(
            second_attacker_probe_observed_ns
        ),
        "authorized_noop_probe_observed_ns": int(
            authorized_noop_probe_observed_ns
        ),
        "run_end_ns": int(run_end_ns),
    },
    "development_preflight": True,
    "pilot_data": False,
    "pilot_seed_consumed": False,
}
Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

PHASE="RAW_OBSERVATION_VALIDATION"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_command_runtime_executor \
  finalize-observation \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --factor-json "$FACTOR_JSON" \
  --policy-json "$POLICY_JSON" \
  --gateway-decisions-jsonl "$DECISION_JSONL" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$DERIVED_JSON"

echo "command_runtime_raw_observation=PASS"
echo "runtime_binding_performed=false"
echo "primary_metrics_emitted=false"
echo "terminal_state_emitted=false"

RESULT="PASS"
PHASE="COMPLETE"
