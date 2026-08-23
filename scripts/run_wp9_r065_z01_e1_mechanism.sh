#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CASE_ID="Z01"
CELL_ID="A06"
SEED="9941"
GATEWAY_PORT=19091
EFFECT_SETTLE_SECONDS="0.8"
NOMINAL_DURATION_SECONDS=90

[[ "$#" -eq 4 && "$1" == "--request-json" && "$3" == "--output-json" ]] || {
  echo "usage: $0 --request-json <path> --output-json <path>" >&2
  exit 2
}
REQUEST_JSON="$2"
OUTPUT_JSON="$4"

cd "$ROOT"

for command in git python3 docker; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

REPO_COMMIT="$(git rev-parse HEAD)"
[[ "${WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}" == "1" ]] || {
  echo "[BLOCKED] R-065 Z01 development runtime authorization is not active" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_CASE:-}" == "$CASE_ID" ]] || {
  echo "[BLOCKED] R-065 authorization is not for Z01" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_SEED:-}" == "$SEED" ]] || {
  echo "[BLOCKED] R-065 authorization is not for development seed 9941" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_REPO_SHA:-}" == "$REPO_COMMIT" ]] || {
  echo "[BLOCKED] R-065 authorization SHA does not match current HEAD" >&2
  exit 3
}

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before R-065 Z01 runtime" >&2
  exit 1
}

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_r065_runtime_mechanism_driver \
  validate-request --request-json "$REQUEST_JSON" >/dev/null

read -r REQUEST_CASE REQUEST_CELL REQUEST_SEED REQUEST_SHA RUN_ID SELECTED_ACTION REQUEST_EVIDENCE <<EOF_REQUEST
$(python3 - "$REQUEST_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(
    row["case_id"],
    row["cell_id"],
    row["development_seed"],
    row["repo_commit"],
    row["run_id"],
    row["selected_action"],
    row["evidence_directory"],
)
PY
)
EOF_REQUEST

[[ "$REQUEST_CASE" == "$CASE_ID" ]]
[[ "$REQUEST_CELL" == "$CELL_ID" ]]
[[ "$REQUEST_SEED" == "$SEED" ]]
[[ "$REQUEST_SHA" == "$REPO_COMMIT" ]]

EXPECTED_EVIDENCE="results/wp9/development/r065/integration/$RUN_ID"
[[ "$REQUEST_EVIDENCE" == "$EXPECTED_EVIDENCE" ]] || {
  echo "[ERROR] R-065 Z01 evidence directory differs from development namespace" >&2
  exit 1
}

EVIDENCE="$ROOT/$EXPECTED_EVIDENCE"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
EXPECTED_REQUEST="$GROUND/r065-execution-request.json"
EXPECTED_OUTPUT="$OBS/z01-driver-result.json"
[[ "$(cd "$(dirname "$REQUEST_JSON")" && pwd)/$(basename "$REQUEST_JSON")" == "$EXPECTED_REQUEST" ]] || {
  echo "[ERROR] R-065 Z01 request path is not the retained evidence path" >&2
  exit 1
}
[[ "$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")" == "$EXPECTED_OUTPUT" ]] || {
  echo "[ERROR] R-065 Z01 output path is not the retained evidence path" >&2
  exit 1
}

SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-r065-z01-gateway"
GATEWAY_ALIAS="r065-z01-gateway"

EVENT_JSON="$GROUND/event-instance.json"
EVENT_SEND_JSON="$GROUND/event-activation-send.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
ATTACKER1_JSON="$GROUND/attacker-reset-probe-1.json"
ATTACKER2_JSON="$GROUND/attacker-reset-probe-2.json"
AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"
MEASUREMENT_JSON="$OBS/e1-route-measurement.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"
EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"
EVENT_RESET_AFTER_FILE="$OBS/event-reset-after.txt"

PRE_PID=""
EVENT_WATCH_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
RUN_START_NS=""
RUN_START_UTC=""
EVENT_ACTIVATION_NS=""
EVENT_SUCCESS_NS=""
POLICY_SELECTION_NS=""
POLICY_ENFORCEMENT_NS=""
SECOND_ATTACKER_PROBE_NS=""
AUTHORIZED_NOOP_NS=""
OBSERVATION_COMPLETE_NS=""
DEVELOPMENT_SEED_CONSUMED=false

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

wait_until_ns() {
  local deadline_ns="$1" now
  while true; do
    now="$(mono_ns)"
    [[ "$now" -ge "$deadline_ns" ]] && return 0
    sleep 0.05
  done
}

count_reset_marker() {
  docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: RESET counters command received' || true
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true
}

decision_count() {
  python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
if not path.exists():
    print(0)
else:
    print(sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()))
PY
}

wait_decision_count() {
  local expected="$1" count
  for _ in $(seq 1 75); do
    count="$(decision_count)"
    [[ "$count" -eq "$expected" ]] && return 0
    [[ "$count" -gt "$expected" ]] && return 2
    sleep 0.2
  done
  return 1
}

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
      --gateway-host "$GATEWAY_ALIAS" \
      --result-json "/evidence/$result_file" >/dev/null
}

emit_invalid() {
  local rc="$1"
  mkdir -p "$EVIDENCE"
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$PHASE" "$rc" "$REPO_COMMIT" "$DEVELOPMENT_SEED_CONSUMED" <<'PY'
import json
import sys
from pathlib import Path
path, run_id, phase, rc, commit, consumed = sys.argv[1:]
record = {
    "schema": 1,
    "decision_id": "R-065",
    "classification": "WP9_R065_Z01_BOUNDED_INTEGRATION_RUN_INVALID",
    "run_id": run_id,
    "case_id": "Z01",
    "cell_id": "A06",
    "development_seed": 9941,
    "development_seed_consumed": consumed == "true",
    "failed_phase": phase,
    "exit_code": int(rc),
    "repo_commit": commit,
    "development_validation_only": True,
    "invalid_attempt_retained": True,
    "campaign_seed_consumed": False,
    "campaign_data_generated": False,
    "final_campaign_execution_authorized": False,
    "automatic_retry_performed": False,
    "automatic_next_case_performed": False,
}
Path(path).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if [[ -n "$EVENT_WATCH_PID" ]] && kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1; then
    kill -TERM "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
    wait "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  docker network rm "$NETWORK" >/dev/null 2>&1 || true

  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R065_Z01_E1_MECHANISM_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "cell_id=$CELL_ID"
    echo "development_seed=$SEED"
    echo "development_seed_consumed=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data_generated=false"
    echo "automatic_retry_allowed=false"
    echo "automatic_next_case_allowed=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9_R065_Z01_E1_MECHANISM_RUNTIME=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "automatic_retry_allowed=false" >&2
    echo "automatic_next_case_allowed=false" >&2
    echo "campaign_seed_consumed=false" >&2
    echo "campaign_data_generated=false" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

mkdir -p "$GROUND" "$OBS"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"

PHASE="PREFLIGHT"
docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}
echo "r065_z01_runtime_authorization=PASS"
echo "authorized_case=$CASE_ID"
echo "authorized_seed=$SEED"
echo "authorized_repo_sha=$REPO_COMMIT"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"

PHASE="EVENT_MATERIALIZATION"
python3 - "$REQUEST_JSON" "$EVENT_JSON" <<'PY'
import json
import sys
from pathlib import Path
request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
Path(sys.argv[2]).write_text(
    json.dumps(request["event_instance"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

echo "r065_z01_event_materialization=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" \
DURATION_SECONDS="$NOMINAL_DURATION_SECONDS" \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

PHASE="CFS_READINESS"
CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  [[ "$state" == running ]] && { CFS_READY=1; break; }
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
[[ "$CI_READY" -eq 1 ]] || {
  echo "[ERROR] CI_LAB UDP 5012 not observed" >&2
  exit 1
}
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DEVELOPMENT_SEED_CONSUMED=true

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
    [[ "$now" -le $((RESET_BEFORE_EVENT + 1)) ]] || exit 2
    sleep 0.1
  done
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
    --result-json /evidence/event-activation-send.json >/dev/null

python3 - "$EVENT_SEND_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["command_class"] == "sample_reset_counters"
assert row["target"] == "nos-fsw:5012"
assert row["datagrams_sent"] == 1
assert row["packet_sha256"] == "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
PY

PHASE="POLICY_SELECTION"
POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS"
echo "actual_effective_policy_id=P2"
echo "selected_action=$SELECTED_ACTION"
echo "policy_trigger_uses_ground_truth=false"

PHASE="POLICY_ENFORCEMENT"
docker run -d --platform linux/amd64 \
  --name "$GATEWAY" \
  --hostname "$GATEWAY_ALIAS" \
  --network "$NETWORK" \
  --network-alias "$GATEWAY_ALIAS" \
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
HEX_GATEWAY_PORT="$(printf '%04X' "$GATEWAY_PORT")"
for _ in $(seq 1 75); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
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
  echo "[ERROR] R-065 Z01 command gateway did not become ready" >&2
  exit 1
}
POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"

PHASE="EVENT_SUCCESS_CONFIRMATION"
set +e
wait "$EVENT_WATCH_PID"
EVENT_WATCH_RC=$?
set -e
EVENT_WATCH_PID=""
[[ "$EVENT_WATCH_RC" -eq 0 ]] || {
  echo "[ERROR] immutable event-success watcher failed" >&2
  exit 1
}
EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"
RESET_AFTER_EVENT="$(cat "$EVENT_RESET_AFTER_FILE")"
test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"
test "$RESET_AFTER_EVENT" -eq $((RESET_BEFORE_EVENT + 1))
echo "policy_selection_not_gated_on_event_success=true"

PHASE="POST_ENFORCEMENT_ATTACKER_PROBES"
RESET_BEFORE_ATTACKER="$(count_reset_marker)"
send_gateway_command modeled_attacker sample_reset_counters "$(basename "$ATTACKER1_JSON")"
wait_decision_count 1
send_gateway_command modeled_attacker sample_reset_counters "$(basename "$ATTACKER2_JSON")"
wait_decision_count 2
sleep "$EFFECT_SETTLE_SECONDS"
RESET_AFTER_ATTACKER="$(count_reset_marker)"
ATTACKER_DELTA=$((RESET_AFTER_ATTACKER - RESET_BEFORE_ATTACKER))
[[ "$ATTACKER_DELTA" -ge 0 && "$ATTACKER_DELTA" -le 2 ]]
SECOND_ATTACKER_PROBE_NS="$(mono_ns)"

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"
NOOP_BEFORE="$(count_noop_marker)"
send_gateway_command authorized_ground sample_noop "$(basename "$AUTHORIZED_JSON")"
wait_decision_count 3
sleep "$EFFECT_SETTLE_SECONDS"
NOOP_AFTER="$(count_noop_marker)"
NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
[[ "$NOOP_DELTA" -ge 0 && "$NOOP_DELTA" -le 1 ]]
AUTHORIZED_NOOP_NS="$(mono_ns)"

read -r DECISION_COUNT ATTACKER_ACTION ATTACKER_FORWARDED_COUNT AUTH_ACTION AUTH_FORWARDED <<EOF_DECISIONS
$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json
import sys
from pathlib import Path
rows = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if line.strip()]
assert len(rows) == 3
assert [r["source_id"] for r in rows] == ["modeled_attacker", "modeled_attacker", "authorized_ground"]
assert [r["command_class"] for r in rows] == ["sample_reset_counters", "sample_reset_counters", "sample_noop"]
assert rows[0]["action"] == rows[1]["action"] == rows[2]["action"]
print(len(rows), rows[0]["action"], sum(1 for r in rows[:2] if bool(r["forwarded"])), rows[2]["action"], str(bool(rows[2]["forwarded"])).lower())
PY
)
EOF_DECISIONS

PHASE="FROZEN_ANALYSIS_HORIZON"
ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))
wait_until_ns "$ANALYSIS_END_NS"
OBSERVATION_COMPLETE_NS="$(mono_ns)"
kill -0 "$PRE_PID" >/dev/null 2>&1
[[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]
[[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]
echo "post_event_analysis_horizon_s=30"
echo "runtime_health_passed=true"

PHASE="AUXILIARY_CLEANUP"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true

PHASE="NOMINAL_RUNTIME_COMPLETION"
set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""
[[ "$PRE_RC" -eq 0 ]] || {
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$RUNTIME_MANIFEST"

PHASE="MEASUREMENT_BINDING"
python3 - \
  "$MEASUREMENT_JSON" "$RUN_ID" "$RUN_START_UTC" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$SECOND_ATTACKER_PROBE_NS" "$AUTHORIZED_NOOP_NS" "$OBSERVATION_COMPLETE_NS" \
  "$RESET_BEFORE_EVENT" "$RESET_AFTER_EVENT" "$ATTACKER_DELTA" "$NOOP_DELTA" \
  "$DECISION_COUNT" "$ATTACKER_FORWARDED_COUNT" "$AUTH_FORWARDED" \
  "$ATTACKER_ACTION" "$AUTH_ACTION" <<'PY'
import json
import sys
from pathlib import Path
(
 path, run_id, run_start_utc, run_start_ns, event_activation_ns, event_success_ns,
 policy_selection_ns, policy_enforcement_ns, second_attacker_ns, authorized_noop_ns,
 observation_complete_ns, reset_before_event, reset_after_event, attacker_delta,
 noop_delta, decision_count, attacker_forwarded_count, authorized_forwarded,
 attacker_action, authorized_action,
) = sys.argv[1:]
record = {
 "schema": 1,
 "run_id": run_id,
 "run_start_utc": run_start_utc,
 "run_start_ns": int(run_start_ns),
 "event_activation_ns": int(event_activation_ns),
 "event_success_observed_ns": int(event_success_ns),
 "policy_selection_ns": int(policy_selection_ns),
 "policy_enforcement_ns": int(policy_enforcement_ns),
 "second_attacker_probe_observed_ns": int(second_attacker_ns),
 "authorized_noop_probe_observed_ns": int(authorized_noop_ns),
 "observation_complete_ns": int(observation_complete_ns),
 "event_activation_reset_marker_delta": int(reset_after_event) - int(reset_before_event),
 "post_enforcement_attacker_probe_count": 2,
 "post_enforcement_attacker_reset_marker_delta": int(attacker_delta),
 "legitimate_commands_attempted": 1,
 "authorized_noop_marker_delta": int(noop_delta),
 "gateway_decision_count": int(decision_count),
 "attacker_gateway_forwarded_count": int(attacker_forwarded_count),
 "authorized_noop_gateway_forwarded": authorized_forwarded == "true",
 "runtime_health_passed": True,
 "policy_selection_not_gated_on_event_success": True,
 "attacker_gateway_action": attacker_action,
 "authorized_noop_gateway_action": authorized_action,
}
Path(path).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_r065_runtime_mechanism_driver \
  finalize-z01 \
  --request-json "$REQUEST_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$OUTPUT_JSON" >/dev/null

python3 - "$OUTPUT_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["case_id"] == "Z01"
assert row["cell_id"] == "A06"
assert row["development_seed"] == 9941
assert row["development_seed_consumed"] is True
assert row["treatment_fidelity_valid"] is True
assert row["runtime_execution_performed"] is True
assert row["campaign_seed_consumed"] is False
assert row["campaign_data_generated"] is False
assert row["automatic_retry_performed"] is False
assert row["automatic_next_case_performed"] is False
assert row["final_campaign_execution_authorized"] is False
PY

PHASE="CLEANUP_AUDIT"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
docker network rm "$NETWORK" >/dev/null 2>&1 || true
for name in "$CFS" "$GATEWAY"; do
  if docker inspect "$name" >/dev/null 2>&1; then
    echo "[ERROR] residual runtime container remains: $name" >&2
    exit 1
  fi
done
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  echo "[ERROR] residual runtime network remains: $NETWORK" >&2
  exit 1
fi
echo "residual_runtime=none"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"

RESULT="PASS"
