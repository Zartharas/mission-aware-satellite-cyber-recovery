#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
GATEWAY_PORT=19091
EFFECT_SETTLE_SECONDS="0.8"
NOMINAL_DURATION_SECONDS=90

[[ "$#" -eq 1 ]] || {
  echo "usage: $0 <X01|X02|X03|X04|X05>" >&2
  exit 2
}

CASE_ID="$1"
case "$CASE_ID" in
  X01) CELL_ID="A05"; SEED="9921" ;;
  X02) CELL_ID="A08"; SEED="9922" ;;
  X03) CELL_ID="A02"; SEED="9923" ;;
  X04) CELL_ID="A06"; SEED="9924" ;;
  X05) CELL_ID="A09"; SEED="9925" ;;
  *)
    echo "[ERROR] R-061 E1 route validation supports X01-X05 only" >&2
    exit 2
    ;;
esac

cd "$ROOT"

for command in git python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e1_runtime_adapter \
  validate-static >/dev/null

REPO_COMMIT="$(git rev-parse HEAD)"
RUNTIME_AUTHORIZED="${WP9_R061_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}"
AUTHORIZED_CASE="${WP9_R061_AUTHORIZED_CASE:-}"
AUTHORIZED_REPO_SHA="${WP9_R061_AUTHORIZED_REPO_SHA:-}"

[[ "$RUNTIME_AUTHORIZED" == "1" ]] || {
  echo "[BLOCKED] R-061 development runtime remains blocked; explicit per-case authorization is required" >&2
  exit 3
}

[[ "$AUTHORIZED_CASE" == "$CASE_ID" ]] || {
  echo "[BLOCKED] R-061 authorization is not for requested case $CASE_ID" >&2
  exit 3
}

[[ "$AUTHORIZED_REPO_SHA" == "$REPO_COMMIT" ]] || {
  echo "[BLOCKED] R-061 authorization SHA does not match current repository HEAD" >&2
  exit 3
}

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before R-061 development runtime" >&2
  exit 1
}

for command in docker; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

echo "r061_per_case_runtime_authorization=PASS"
echo "authorized_case=$CASE_ID"
echo "authorized_repo_sha=$AUTHORIZED_REPO_SHA"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}

TOKEN="$(python3 - <<'PY'
import uuid
print(uuid.uuid4().hex)
PY
)"
CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r061-${CASE_SAFE}-s${SEED}-${TOKEN}}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-r061-e1-gateway"
GATEWAY_ALIAS="r061-e1-gateway"

EVIDENCE="$ROOT/results/wp9/development/r061/e1/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
AUTH_JSON="$GROUND/development-runtime-authorization.json"
EVENT_JSON="$GROUND/event-instance.json"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_SEND_JSON="$GROUND/event-activation-send.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
ATTACKER1_JSON="$GROUND/attacker-reset-probe-1.json"
ATTACKER2_JSON="$GROUND/attacker-reset-probe-2.json"
AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"
MEASUREMENT_JSON="$OBS/e1-route-measurement.json"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
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
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: RESET counters command received' || true
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
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
  python3 - \
    "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$CELL_ID" "$SEED" \
    "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json
import sys
from pathlib import Path
(
    path, run_id, case_id, cell_id, seed,
    phase, rc, commit,
) = sys.argv[1:]
record = {
    "schema": 1,
    "decision_id": "R-061",
    "classification": "WP9_R061_E1_ROUTE_VALIDATION_RUN_INVALID",
    "run_id": run_id,
    "case_id": case_id,
    "cell_id": cell_id,
    "development_seed": int(seed),
    "failed_phase": phase,
    "exit_code": int(rc),
    "repo_commit": commit,
    "development_validation_only": True,
    "development_runtime_data": False,
    "per_case_runtime_authorized": True,
    "campaign_seed_consumed": False,
    "campaign_data_generated": False,
    "final_campaign_failure_claimed": False,
    "automatic_retry_allowed": False,
    "automatic_next_case_allowed": False,
}
Path(path).write_text(
    json.dumps(record, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY
}

cleanup() {
  local rc=$?
  set +e

  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true

  if [[ -n "$EVENT_WATCH_PID" ]] && \
     kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1
  then
    kill -TERM "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
    wait "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R061_E1_ROUTE_VALIDATION_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "cell_id=$CELL_ID"
    echo "development_seed=$SEED"
    echo "development_runtime_data=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data_generated=false"
    echo "automatic_retry_allowed=false"
    echo "automatic_next_case_allowed=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9_R061_E1_ROUTE_VALIDATION_RUNTIME=FAIL" >&2
    echo "case_id=$CASE_ID" >&2
    echo "cell_id=$CELL_ID" >&2
    echo "failed_phase=$PHASE" >&2
    echo "campaign_seed_consumed=false" >&2
    echo "campaign_data_generated=false" >&2
    echo "automatic_retry_allowed=false" >&2
    echo "automatic_next_case_allowed=false" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

mkdir -p "$GROUND" "$OBS"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"

PHASE="AUTHORIZATION_RECORD"
python3 - \
  "$AUTH_JSON" "$CASE_ID" "$CELL_ID" "$SEED" "$REPO_COMMIT" <<'PY'
import json
import sys
from pathlib import Path
path, case_id, cell_id, seed, commit = sys.argv[1:]
record = {
    "schema": 1,
    "decision_id": "R-061",
    "classification": "WP9_R061_EXPLICIT_PER_CASE_DEVELOPMENT_RUNTIME_AUTHORIZATION",
    "case_id": case_id,
    "cell_id": cell_id,
    "development_seed": int(seed),
    "authorized_repo_sha": commit,
    "authorization_scope": "one_case_per_invocation",
    "campaign_execution_authorized": False,
    "automatic_retry_allowed": False,
    "automatic_next_case_allowed": False,
}
Path(path).write_text(
    json.dumps(record, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

echo "r061_authorization_record=PASS"

PHASE="EVENT_MATERIALIZATION"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$CELL_ID" "$SEED" <<'PY'
import json
import sys
from pathlib import Path
from src.mission_recovery.events import materialize_event
from src.mission_recovery.wp9_static_contracts import load_campaign_design

path, cell_id, seed = sys.argv[1:]
cells = {row["cell_id"]: row for row in load_campaign_design()["cells"]}
cell = cells[cell_id]
assert cell["event_id"] == "E1"
event = materialize_event(
    "E1",
    mission_state=cell["mission_state_id"],
    contact_condition=cell["contact_condition_id"],
    evidence_condition=cell["evidence_condition_id"],
    seed=int(seed),
)
Path(path).write_text(
    json.dumps(event, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

echo "r061_event_materialization=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" \
DURATION_SECONDS="$NOMINAL_DURATION_SECONDS" \
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
    --result-json /evidence/event-activation-send.json >/dev/null

python3 - "$EVENT_SEND_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["command_class"] == "sample_reset_counters"
assert row["target"] == "nos-fsw:5012"
assert row["datagrams_sent"] == 1
assert row["packet_sha256"] == (
    "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
)
print("e1_direct_reset_activation=PASS")
PY

echo "event_activation_before_response=true"
echo "policy_trigger_uses_ground_truth=false"

PHASE="POLICY_SELECTION"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e1_runtime_adapter \
  plan-development \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-json "$PLAN_JSON" >/dev/null
POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS"

read -r SELECTED_ACTION ACTUAL_EFFECTIVE <<EOF_PLAN
$(python3 - "$PLAN_JSON" "$EVENT_JSON" <<'PY'
import json
import sys
from pathlib import Path
plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
event = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
assert plan["event_instance"] == event
assert plan["runtime_family"] == "command"
assert plan["runtime_variant"] == "e1_command_gateway"
assert plan["development_runtime_execution_authorized"] is False
assert plan["campaign_seed_consumed"] is False
assert plan["campaign_data_generated"] is False
assert plan["final_campaign_execution_authorized"] is False
assert plan["runtime_policy_decision"]["oracle_ground_truth_read"] is False
print(
    plan["runtime_policy_decision"]["selected_action"],
    plan["runtime_policy_decision"]["delegated_policy_id"],
)
PY
)
EOF_PLAN

echo "r061_development_plan=PASS"
echo "actual_effective_policy_id=$ACTUAL_EFFECTIVE"
echo "selected_action=$SELECTED_ACTION"

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
  echo "[ERROR] R-061 command gateway did not become ready" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}
POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"
echo "policy_gateway_ready=PASS"
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

PHASE="POST_ENFORCEMENT_ATTACKER_PROBES"
RESET_BEFORE_ATTACKER="$(count_reset_marker)"

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER1_JSON")"
wait_decision_count 1 || {
  echo "[ERROR] first R-061 gateway decision not observed exactly" >&2
  exit 1
}

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER2_JSON")"
wait_decision_count 2 || {
  echo "[ERROR] second R-061 gateway decision not observed exactly" >&2
  exit 1
}

sleep "$EFFECT_SETTLE_SECONDS"
RESET_AFTER_ATTACKER="$(count_reset_marker)"
ATTACKER_DELTA=$((RESET_AFTER_ATTACKER - RESET_BEFORE_ATTACKER))
[[ "$ATTACKER_DELTA" -ge 0 && "$ATTACKER_DELTA" -le 2 ]] || {
  echo "[ERROR] attacker reset-marker delta outside 0..2: $ATTACKER_DELTA" >&2
  exit 1
}
SECOND_ATTACKER_PROBE_NS="$(mono_ns)"
echo "matched_attacker_reset_probe_count=2"
echo "observed_post_enforcement_attacker_reset_marker_delta=$ATTACKER_DELTA"

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"
NOOP_BEFORE="$(count_noop_marker)"
send_gateway_command \
  authorized_ground sample_noop \
  "$(basename "$AUTHORIZED_JSON")"
wait_decision_count 3 || {
  echo "[ERROR] expected exactly three R-061 gateway decisions" >&2
  exit 1
}
sleep "$EFFECT_SETTLE_SECONDS"
NOOP_AFTER="$(count_noop_marker)"
NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
[[ "$NOOP_DELTA" -ge 0 && "$NOOP_DELTA" -le 1 ]] || {
  echo "[ERROR] authorized NOOP marker delta outside 0..1: $NOOP_DELTA" >&2
  exit 1
}
AUTHORIZED_NOOP_NS="$(mono_ns)"
echo "post_response_authorized_noop_attempted=1"
echo "observed_authorized_noop_marker_delta=$NOOP_DELTA"

read -r DECISION_COUNT ATTACKER_ACTION ATTACKER_FORWARDED_COUNT AUTH_ACTION AUTH_FORWARDED <<EOF_DECISIONS
$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json
import sys
from pathlib import Path
rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(rows) == 3
assert [row["source_id"] for row in rows] == [
    "modeled_attacker",
    "modeled_attacker",
    "authorized_ground",
]
assert [row["command_class"] for row in rows] == [
    "sample_reset_counters",
    "sample_reset_counters",
    "sample_noop",
]
assert rows[0]["action"] == rows[1]["action"] == rows[2]["action"]
print(
    len(rows),
    rows[0]["action"],
    sum(1 for row in rows[:2] if bool(row["forwarded"])),
    rows[2]["action"],
    str(bool(rows[2]["forwarded"])).lower(),
)
PY
)
EOF_DECISIONS

test "$DECISION_COUNT" -eq 3

echo "gateway_decision_count=3"
echo "attacker_gateway_forwarded_count=$ATTACKER_FORWARDED_COUNT"
echo "authorized_noop_gateway_forwarded=$AUTH_FORWARDED"

PHASE="FROZEN_ANALYSIS_HORIZON"
ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))
wait_until_ns "$ANALYSIS_END_NS"
OBSERVATION_COMPLETE_NS="$(mono_ns)"
kill -0 "$PRE_PID" >/dev/null 2>&1 || {
  echo "[ERROR] nominal runtime ended before frozen E1 analysis horizon" >&2
  exit 1
}
[[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] || {
  echo "[ERROR] cFS unavailable at frozen E1 analysis horizon" >&2
  exit 1
}
[[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] || {
  echo "[ERROR] policy gateway unavailable at frozen E1 analysis horizon" >&2
  exit 1
}
echo "post_event_analysis_horizon_s=30"
echo "runner_duration_used_as_metric_input=false"
echo "runtime_health_passed=true"
echo "frozen_analysis_horizon_complete=PASS"

PHASE="AUXILIARY_CLEANUP"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
echo "auxiliary_e1_cleanup=PASS"

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
echo "nominal_runtime_completion=PASS"

PHASE="MEASUREMENT_BINDING"
python3 - \
  "$MEASUREMENT_JSON" "$RUN_ID" "$RUN_START_UTC" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$SECOND_ATTACKER_PROBE_NS" "$AUTHORIZED_NOOP_NS" \
  "$OBSERVATION_COMPLETE_NS" \
  "$RESET_BEFORE_EVENT" "$RESET_AFTER_EVENT" \
  "$ATTACKER_DELTA" "$NOOP_DELTA" \
  "$DECISION_COUNT" "$ATTACKER_FORWARDED_COUNT" "$AUTH_FORWARDED" \
  "$ATTACKER_ACTION" "$AUTH_ACTION" <<'PY'
import json
import sys
from pathlib import Path
(
    path, run_id, run_start_utc,
    run_start_ns, event_activation_ns, event_success_ns,
    policy_selection_ns, policy_enforcement_ns,
    second_attacker_ns, authorized_noop_ns, observation_complete_ns,
    reset_before_event, reset_after_event,
    attacker_delta, noop_delta,
    decision_count, attacker_forwarded_count, authorized_forwarded,
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
    "event_activation_reset_marker_delta": (
        int(reset_after_event) - int(reset_before_event)
    ),
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
Path(path).write_text(
    json.dumps(record, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e1_runtime_adapter \
  finalize-development \
  --plan-json "$PLAN_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$SUMMARY_JSON" >/dev/null

python3 - "$SUMMARY_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["acceptance_status"] == "PASS"
assert row["treatment_fidelity_valid"] is True
assert row["raw_metric_inputs_complete"] is True
assert row["campaign_seed_consumed"] is False
assert row["campaign_data_generated"] is False
assert row["final_campaign_execution_authorized"] is False
print("r061_observation_binding=PASS")
print(
    "outcome_matches_predeclared_expectation="
    + str(bool(row["outcome_matches_predeclared_expectation"])).lower()
)
print(
    "unexpected_scientific_outcome_retained="
    + str(bool(row["unexpected_scientific_outcome_would_be_retained_in_campaign"])).lower()
)
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
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"

RESULT="PASS"
