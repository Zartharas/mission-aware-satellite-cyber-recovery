#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOMINAL_DURATION_SECONDS=60
CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-r063-rollback.tmp"

[[ "$#" -eq 1 ]] || {
  echo "usage: $0 <Y01|Y02|Y03|Y04|Y05|Y06>" >&2
  exit 2
}

CASE_ID="$1"
case "$CASE_ID" in
  Y01) CELL_ID="A13"; SEED="9931" ;;
  Y02) CELL_ID="A11"; SEED="9932" ;;
  Y03) CELL_ID="A15"; SEED="9933" ;;
  Y04) CELL_ID="A16"; SEED="9934" ;;
  Y05) CELL_ID="A17"; SEED="9935" ;;
  Y06) CELL_ID="A18"; SEED="9936" ;;
  *)
    echo "[ERROR] R-063 E3 route validation supports Y01-Y06 only" >&2
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
  src.mission_recovery.wp9_campaign_e3_runtime_adapter \
  validate-static >/dev/null

REPO_COMMIT="$(git rev-parse HEAD)"
RUNTIME_AUTHORIZED="${WP9_R063_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}"
AUTHORIZED_CASE="${WP9_R063_AUTHORIZED_CASE:-}"
AUTHORIZED_REPO_SHA="${WP9_R063_AUTHORIZED_REPO_SHA:-}"

[[ "$RUNTIME_AUTHORIZED" == "1" ]] || {
  echo "[BLOCKED] R-063 development runtime remains blocked; explicit per-case authorization is required" >&2
  exit 3
}

[[ "$AUTHORIZED_CASE" == "$CASE_ID" ]] || {
  echo "[BLOCKED] R-063 authorization is not for requested case $CASE_ID" >&2
  exit 3
}

[[ "$AUTHORIZED_REPO_SHA" == "$REPO_COMMIT" ]] || {
  echo "[BLOCKED] R-063 authorization SHA does not match current repository HEAD" >&2
  exit 3
}

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before R-063 development runtime" >&2
  exit 1
}

for command in docker shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

echo "r063_per_case_runtime_authorization=PASS"
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
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r063-${CASE_SAFE}-s${SEED}-${TOKEN}}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-r063-e3-gateway"
GATEWAY_ALIAS="r063-e3-gateway"

EVIDENCE="$ROOT/results/wp9/development/r063/e3/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

AUTH_JSON="$GROUND/development-runtime-authorization.json"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
HANDOFF_JSON="$GROUND/p6-to-p5-handoff.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
ROLLBACK_JSON="$GROUND/rollback-preparation.json"
GROUND_AUTH_JSON="$GROUND/synthetic-ground-authorization.json"
AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"
ATTACKER1_JSON="$GROUND/attacker-reset-probe-1.json"
ATTACKER2_JSON="$GROUND/attacker-reset-probe-2.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
POST_SLOT_JSON="$GROUND/post-response-slot.json"
TERMINAL_VERIFY="$GROUND/terminal-recovery-verification.json"
RUNTIME_HEALTH_JSON="$GROUND/runtime-health.json"
CRITERIA_JSON="$GROUND/recovery-criteria.json"

MEASUREMENT_JSON="$OBS/e3-route-measurement.json"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
EVENT_WATCH_LOG="$OBS/event-slot-watcher.log"
EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"
EVENT_SLOT_SHA_FILE="$OBS/event-slot-sha256.txt"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

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
RESPONSE_BOUNDARY_NS=""
AUTHORIZATION_OBSERVED_NS=""
HANDOFF_NS=""
ROLLBACK_COMPLETE_NS=""
AUTHORIZED_NOOP_NS=""
OBSERVATION_COMPLETE_NS=""

ROLLBACK_VALIDATED=false
SOURCE_VERIFIED=false
GROUND_AUTH_WAITED=false
AUTH_AVAILABLE_AT_BOUNDARY=false
MISSED_CONTACT_WINDOWS=0
TRUSTED_RECOVERY_CONFIRMED=false
TRUSTED_RECOVERY_NS=""
RUNTIME_HEALTH_PASSED=false

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

wait_until_ns() {
  local deadline_ns="$1"
  local now
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
    print(sum(
        1 for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ))
PY
}

wait_decision_count() {
  local expected="$1"
  local count
  for _ in $(seq 1 75); do
    count="$(decision_count)"
    [[ "$count" -eq "$expected" ]] && return 0
    [[ "$count" -gt "$expected" ]] && return 2
    sleep 0.2
  done
  return 1
}

wait_noop_observation() {
  local before="$1"
  local now
  for _ in $(seq 1 20); do
    now="$(count_noop_marker)"
    [[ "$now" -ge "$before" ]] || return 2
    [[ "$now" -gt "$before" ]] && return 0
    sleep 0.1
  done
  return 0
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

send_authorized_noop() {
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
      send-authorized-noop \
      --output-json /evidence/authorized-noop-probe.json >/dev/null
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
    "decision_id": "R-063",
    "classification": "WP9_R063_E3_ROUTE_VALIDATION_RUN_INVALID",
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

  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f \
      "$STAGE_BACKING" "$TEMP_BACKING" >/dev/null 2>&1 || true
  fi

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

  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R063_E3_ROUTE_VALIDATION_RUNTIME=PASS"
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
    echo "WP9_R063_E3_ROUTE_VALIDATION_RUNTIME=FAIL" >&2
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
    "decision_id": "R-063",
    "classification": (
        "WP9_R063_EXPLICIT_PER_CASE_DEVELOPMENT_RUNTIME_AUTHORIZATION"
    ),
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
echo "r063_authorization_record=PASS"

PHASE="DEVELOPMENT_PLAN"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e3_runtime_adapter \
  plan-development \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-json "$PLAN_JSON"
echo "r063_development_plan=PASS"

PHASE="ARTIFACT_MATERIALIZATION"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e3_runtime_adapter \
  materialize-artifacts \
  --plan-json "$PLAN_JSON" \
  --event-json "$EVENT_JSON" \
  --approved "$APPROVED" \
  --tampered "$TAMPERED" \
  --manifest-json "$MANIFEST" \
  --tampered-verification-json "$VERIFY_TAMPERED"
echo "r063_event_materialization=PASS"

APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"
test "$APPROVED_SHA" = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
test "$TAMPERED_SHA" = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"

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
[[ "$CI_READY" -eq 1 ]]
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
docker exec "$CFS" test -d "$CF_BACKING_DIR"
docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PHASE="EVENT_OBSERVER_PREPOSITION"
: > "$EVENT_WATCH_LOG"
(
  set +e
  docker exec "$CFS" sh -lc '
    slot="$1"
    expected="$2"
    echo R063_EVENT_SLOT_WATCHER_READY
    i=0
    while [ "$i" -lt 3000 ]; do
      if [ -f "$slot" ]; then
        observed_sha="$(
          sha256sum "$slot" 2>/dev/null |
          awk "{print \$1}"
        )"
        if [ "$observed_sha" = "$expected" ]; then
          echo "R063_EVENT_SLOT_SHA=$observed_sha"
          exit 0
        fi
        if [ -n "$observed_sha" ]; then
          echo "R063_EVENT_SLOT_UNEXPECTED_SHA=$observed_sha" >&2
          exit 2
        fi
      fi
      i=$((i + 1))
      sleep 0.01
    done
    echo R063_EVENT_SLOT_WATCHER_TIMEOUT >&2
    exit 1
  ' sh "$STAGE_BACKING" "$TAMPERED_SHA" \
    >"$EVENT_WATCH_LOG" 2>&1

  watcher_rc=$?
  if [[ "$watcher_rc" -eq 0 ]]; then
    observed_sha="$(
      awk -F= '
        /^R063_EVENT_SLOT_SHA=/ {
          print $2
          exit
        }
      ' "$EVENT_WATCH_LOG"
    )"
    [[ "$observed_sha" == "$TAMPERED_SHA" ]] || exit 3
    mono_ns > "$EVENT_SUCCESS_NS_FILE"
    printf '%s\n' "$observed_sha" > "$EVENT_SLOT_SHA_FILE"
  fi
  exit "$watcher_rc"
) &
EVENT_WATCH_PID=$!

EVENT_WATCH_READY=0
for _ in $(seq 1 200); do
  if grep -Fq 'R063_EVENT_SLOT_WATCHER_READY' "$EVENT_WATCH_LOG" 2>/dev/null; then
    EVENT_WATCH_READY=1
    break
  fi
  if ! kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1; then
    break
  fi
  sleep 0.01
done
[[ "$EVENT_WATCH_READY" -eq 1 ]]
echo "event_observer_prepositioned=PASS"

PHASE="EVENT_ACTIVATION"
EVENT_ACTIVATION_NS="$(mono_ns)"
docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"
echo "e3_modeled_activation=PASS"
echo "event_activation_before_response=true"

PHASE="POLICY_SELECTION"
POLICY_SELECTION_NS="$(mono_ns)"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e3_runtime_adapter \
  select-policy \
  --plan-json "$PLAN_JSON" \
  --output-json "$POLICY_JSON"

POLICY_VALUES="$(python3 - "$POLICY_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(row["delegated_policy_id"])
print(row["selected_action"])
PY
)"
EFFECTIVE_POLICY="$(printf '%s\n' "$POLICY_VALUES" | sed -n '1p')"
SELECTED_ACTION="$(printf '%s\n' "$POLICY_VALUES" | sed -n '2p')"

echo "actual_effective_policy_id=$EFFECTIVE_POLICY"
echo "selected_action=$SELECTED_ACTION"
echo "policy_trigger_uses_ground_truth=false"
echo "policy_selection_not_gated_on_event_success=true"

PHASE="EVENT_SUCCESS_CONFIRMATION"
set +e
wait "$EVENT_WATCH_PID"
WATCH_RC=$?
set -e
EVENT_WATCH_PID=""
[[ "$WATCH_RC" -eq 0 ]]
EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"
EVENT_SLOT_SHA="$(cat "$EVENT_SLOT_SHA_FILE")"
test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"
test "$EVENT_SLOT_SHA" = "$TAMPERED_SHA"
echo "event_success_observed=true"

PHASE="POLICY_ENFORCEMENT"
if [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then
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
  HEX_PORT="$(printf '%04X' 19091)"
  for _ in $(seq 1 75); do
    if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] &&
       docker exec "$GATEWAY" sh -lc \
         "awk '\$2 ~ /:${HEX_PORT}$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
         >/dev/null 2>&1
    then
      GATEWAY_READY=1
      break
    fi
    sleep 0.2
  done
  [[ "$GATEWAY_READY" -eq 1 ]]
  POLICY_ENFORCEMENT_NS="$(mono_ns)"
  RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"

elif [[ "$SELECTED_ACTION" == "REQUEST_VERIFIED_ROLLBACK" ]]; then
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
    src.mission_recovery.wp8_recovery_runtime_executor \
    prepare-rollback \
    --event-json "$EVENT_JSON" \
    --policy-json "$POLICY_JSON" \
    --output-json "$ROLLBACK_JSON"

  POLICY_ENFORCEMENT_NS="$(mono_ns)"
  RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"

  ROLLBACK_VALUES="$(python3 - "$ROLLBACK_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(row["rollback_request_validated"]).lower())
print(str(row["replacement_source_verified"]).lower())
PY
)"
  ROLLBACK_VALIDATED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '1p')"
  SOURCE_VERIFIED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '2p')"
  [[ "$ROLLBACK_VALIDATED" == true ]]
  [[ "$SOURCE_VERIFIED" == true ]]

  docker cp "$APPROVED" "$CFS:$TEMP_BACKING"
  docker exec "$CFS" sh -lc "mv '$TEMP_BACKING' '$STAGE_BACKING'"
  ROLLBACK_COMPLETE_NS="$(mono_ns)"

elif [[ "$SELECTED_ACTION" == "WAIT_FOR_GROUND_AUTHORIZATION" ]]; then
  POLICY_ENFORCEMENT_NS="$(mono_ns)"
  RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"
  GROUND_AUTH_WAITED=true

  CONTACT="$(
    python3 - "$PLAN_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(row["factor_context"]["contact_condition_id"])
PY
  )"

  if [[ "$CONTACT" == "C1" ]]; then
    AUTH_AVAILABLE_AT_BOUNDARY=false
    MISSED_CONTACT_WINDOWS=1
    wait_until_ns "$((RESPONSE_BOUNDARY_NS + 10 * 1000000000))"
  else
    test "$CONTACT" = "C0"
    AUTH_AVAILABLE_AT_BOUNDARY=true
    MISSED_CONTACT_WINDOWS=0
  fi

  AUTHORIZATION_OBSERVED_NS="$(mono_ns)"

  python3 - \
    "$GROUND_AUTH_JSON" "$CONTACT" "$AUTH_AVAILABLE_AT_BOUNDARY" \
    "$MISSED_CONTACT_WINDOWS" "$AUTHORIZATION_OBSERVED_NS" <<'PY'
import json
import sys
from pathlib import Path
path, contact, available, missed, observed_ns = sys.argv[1:]
row = {
    "schema": 1,
    "decision_id": "R-063",
    "source": "synthetic_ground_authorization_schedule",
    "contact_condition_id": contact,
    "available_at_response_boundary": available.lower() == "true",
    "missed_contact_windows": int(missed),
    "authorization_current": True,
    "authorization_observed_ns": int(observed_ns),
    "real_ground_contact": False,
    "real_human_operator": False,
}
Path(path).write_text(
    json.dumps(row, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
    src.mission_recovery.wp9_campaign_e3_runtime_adapter \
    build-p5-handoff \
    --plan-json "$PLAN_JSON" \
    --policy-json "$POLICY_JSON" \
    --output-json "$HANDOFF_JSON"

  HANDOFF_NS="$(mono_ns)"

  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
    src.mission_recovery.wp8_recovery_runtime_executor \
    prepare-rollback \
    --event-json "$EVENT_JSON" \
    --policy-json "$HANDOFF_JSON" \
    --output-json "$ROLLBACK_JSON"

  ROLLBACK_VALUES="$(python3 - "$ROLLBACK_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(row["rollback_request_validated"]).lower())
print(str(row["replacement_source_verified"]).lower())
PY
)"
  ROLLBACK_VALIDATED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '1p')"
  SOURCE_VERIFIED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '2p')"
  [[ "$ROLLBACK_VALIDATED" == true ]]
  [[ "$SOURCE_VERIFIED" == true ]]

  docker cp "$APPROVED" "$CFS:$TEMP_BACKING"
  docker exec "$CFS" sh -lc "mv '$TEMP_BACKING' '$STAGE_BACKING'"
  ROLLBACK_COMPLETE_NS="$(mono_ns)"
else
  echo "[ERROR] unsupported R-063 action: $SELECTED_ACTION" >&2
  exit 1
fi

test "$EVENT_SUCCESS_NS" -le "$POLICY_ENFORCEMENT_NS"
echo "policy_enforcement=PASS"
echo "event_success_observed_by_enforcement=PASS"

PHASE="POST_RESPONSE_PROBES"
MATCHED_ATTACKER_PROBES=0
ATTACKER_RESET_DELTA=0
GATEWAY_DECISION_COUNT=0
ATTACKER_FORWARDED_COUNT=0
AUTHORIZED_GATEWAY_FORWARDED=false

if [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then
  RESET_BEFORE="$(count_reset_marker)"
  NOOP_BEFORE="$(count_noop_marker)"

  send_gateway_command \
    modeled_attacker sample_reset_counters attacker-reset-probe-1.json
  send_gateway_command \
    modeled_attacker sample_reset_counters attacker-reset-probe-2.json
  send_gateway_command \
    authorized_ground sample_noop authorized-noop-probe.json

  wait_decision_count 3
  sleep 0.8

  RESET_AFTER="$(count_reset_marker)"
  NOOP_AFTER="$(count_noop_marker)"
  MATCHED_ATTACKER_PROBES=2
  ATTACKER_RESET_DELTA=$((RESET_AFTER - RESET_BEFORE))
  AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
  AUTHORIZED_NOOP_NS="$(mono_ns)"

  GATEWAY_VALUES="$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json
import sys
from pathlib import Path
rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
print(len(rows))
print(sum(
    1 for row in rows
    if row.get("source_id") == "modeled_attacker"
    and row.get("forwarded") is True
))
authorized = [
    row for row in rows
    if row.get("source_id") == "authorized_ground"
]
print(str(
    len(authorized) == 1
    and authorized[0].get("forwarded") is True
).lower())
PY
  )"
  GATEWAY_DECISION_COUNT="$(printf '%s\n' "$GATEWAY_VALUES" | sed -n '1p')"
  ATTACKER_FORWARDED_COUNT="$(printf '%s\n' "$GATEWAY_VALUES" | sed -n '2p')"
  AUTHORIZED_GATEWAY_FORWARDED="$(printf '%s\n' "$GATEWAY_VALUES" | sed -n '3p')"

  test "$GATEWAY_DECISION_COUNT" -eq 3
  test "$ATTACKER_FORWARDED_COUNT" -eq 0
  test "$AUTHORIZED_GATEWAY_FORWARDED" = true
  test "$ATTACKER_RESET_DELTA" -ge 0
  test "$ATTACKER_RESET_DELTA" -le 2
  test "$AUTHORIZED_NOOP_DELTA" -ge 0
  test "$AUTHORIZED_NOOP_DELTA" -le 1
else
  NOOP_BEFORE="$(count_noop_marker)"
  send_authorized_noop
  wait_noop_observation "$NOOP_BEFORE"
  NOOP_AFTER="$(count_noop_marker)"
  AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
  AUTHORIZED_NOOP_NS="$(mono_ns)"
  test "$AUTHORIZED_NOOP_DELTA" -ge 0
  test "$AUTHORIZED_NOOP_DELTA" -le 1
fi

echo "post_response_authorized_noop_attempted=1"
echo "observed_authorized_noop_marker_delta=$AUTHORIZED_NOOP_DELTA"

PHASE="POST_RESPONSE_SLOT_OBSERVATION"
POST_SLOT_SHA="$(
  docker exec "$CFS" sh -lc \
    "sha256sum '$STAGE_BACKING' | awk '{print \$1}'"
)"
POST_SLOT_NS="$(mono_ns)"
docker exec "$CFS" test ! -e "$TEMP_BACKING"
TEMP_ABSENT=true

python3 - "$POST_SLOT_JSON" "$POST_SLOT_SHA" "$POST_SLOT_NS" <<'PY'
import json
import sys
from pathlib import Path
path, sha, ns = sys.argv[1:]
Path(path).write_text(
    json.dumps(
        {"sha256": sha, "observed_ns": int(ns)},
        sort_keys=True,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)
PY

PHASE="RUNTIME_HEALTH"
CFS_STATE="$(docker inspect "$CFS" --format '{{.State.Status}}')"
test "$CFS_STATE" = running
docker exec "$CFS" sh -lc \
  "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {found=1} END {exit found ? 0 : 1}'"
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
RUNTIME_HEALTH_NS="$(mono_ns)"
RUNTIME_HEALTH_PASSED=true

python3 - "$RUNTIME_HEALTH_JSON" "$RUNTIME_HEALTH_NS" <<'PY'
import json
import sys
from pathlib import Path
path, observed_ns = sys.argv[1:]
row = {
    "schema": 1,
    "cfs_running": True,
    "ci_lab_udp_5012_observed": True,
    "internal_network": True,
    "published_ports_absent": True,
    "runtime_health_passed": True,
    "observed_ns": int(observed_ns),
}
Path(path).write_text(
    json.dumps(row, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

if [[ "$EFFECTIVE_POLICY" == "P2" ]]; then
  test "$POST_SLOT_SHA" = "$TAMPERED_SHA"
  ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))
  wait_until_ns "$ANALYSIS_END_NS"
  OBSERVATION_COMPLETE_NS="$(mono_ns)"
  echo "frozen_analysis_horizon_complete=PASS"
  echo "trusted_recovery_confirmed=false"
else
  test "$POST_SLOT_SHA" = "$APPROVED_SHA"

  PHASE="TERMINAL_RECOVERY_VERIFICATION"
  docker cp "$CFS:$STAGE_BACKING" "$OBS/terminal-recovered-candidate.pkg" >/dev/null

  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - \
    "$OBS/terminal-recovered-candidate.pkg" "$MANIFEST" \
    "$TAMPERED_SHA" "$TERMINAL_VERIFY" <<'PY'
import json
import sys
from pathlib import Path
from src.mission_recovery.trusted_recovery import verify_terminal_recovery

candidate = Path(sys.argv[1]).read_bytes()
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
result = verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)
assert result["trusted_recovery_verified"] is True
assert result["terminal_matches_approved"] is True
assert result["terminal_differs_from_rejected"] is True
assert result["reasons"] == []
Path(sys.argv[4]).write_text(
    json.dumps(result, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

  PHASE="RECOVERY_CRITERIA"
  CRITERIA_NS="$(mono_ns)"
  python3 - \
    "$CRITERIA_JSON" "$POST_SLOT_JSON" "$ROLLBACK_JSON" \
    "$AUTHORIZED_JSON" "$RUNTIME_HEALTH_JSON" "$MANIFEST" \
    "$TERMINAL_VERIFY" "$AUTHORIZED_NOOP_DELTA" "$CRITERIA_NS" <<'PY'
import json
import sys
from pathlib import Path

(
    out_path,
    post_slot,
    rollback,
    noop,
    health,
    manifest,
    terminal,
    noop_delta,
    observed_ns,
) = sys.argv[1:]

noop_delta = int(noop_delta)
evidence = {
    "approved_version": post_slot,
    "integrity_measurement_valid": terminal,
    "authorization_valid": rollback,
    "measured_state_current": post_slot,
    "authorized_command_path_restored": noop,
    "ground_spacecraft_state_agreed": post_slot,
    "required_telemetry_restored": health,
    "health_checks_passed": health,
    "no_residual_unauthorized_state": post_slot,
    "recovery_manifest_complete": manifest,
}
satisfied = {
    "approved_version": True,
    "integrity_measurement_valid": True,
    "authorization_valid": True,
    "measured_state_current": True,
    "authorized_command_path_restored": noop_delta == 1,
    "ground_spacecraft_state_agreed": True,
    "required_telemetry_restored": True,
    "health_checks_passed": True,
    "no_residual_unauthorized_state": True,
    "recovery_manifest_complete": True,
}
rows = {}
for criterion, ref in evidence.items():
    rows[criterion] = {
        "available_current": True,
        "criterion_satisfied": bool(satisfied[criterion]),
        "evidence_ref": str(Path(ref)),
        "observed_ns": int(observed_ns),
    }
Path(out_path).write_text(
    json.dumps(rows, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
print(str(all(
    row["available_current"] and row["criterion_satisfied"]
    for row in rows.values()
)).lower())
PY

  ALL_CRITERIA="$(
    python3 - "$CRITERIA_JSON" <<'PY'
import json
import sys
from pathlib import Path
rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(all(
    row["available_current"] and row["criterion_satisfied"]
    for row in rows.values()
)).lower())
PY
  )"

  if [[ "$ALL_CRITERIA" == true ]]; then
    TRUSTED_RECOVERY_CONFIRMED=true
    TRUSTED_RECOVERY_NS="$(mono_ns)"
    OBSERVATION_COMPLETE_NS="$(mono_ns)"
    echo "early_absorbing_trusted_recovery=true"
  else
    TRUSTED_RECOVERY_CONFIRMED=false
    ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))
    wait_until_ns "$ANALYSIS_END_NS"
    OBSERVATION_COMPLETE_NS="$(mono_ns)"
    echo "frozen_analysis_horizon_complete=PASS"
  fi
  echo "trusted_recovery_confirmed=$TRUSTED_RECOVERY_CONFIRMED"
fi

PHASE="MEASUREMENT_BINDING"
python3 - \
  "$MEASUREMENT_JSON" "$PLAN_JSON" "$RUN_ID" "$RUN_START_UTC" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$RESPONSE_BOUNDARY_NS" "$OBSERVATION_COMPLETE_NS" \
  "$POST_SLOT_SHA" "$RUNTIME_HEALTH_PASSED" \
  "$AUTHORIZED_NOOP_DELTA" "$SELECTED_ACTION" \
  "$EFFECTIVE_POLICY" "$MATCHED_ATTACKER_PROBES" \
  "$GATEWAY_DECISION_COUNT" "$ATTACKER_FORWARDED_COUNT" \
  "$AUTHORIZED_GATEWAY_FORWARDED" "$ATTACKER_RESET_DELTA" \
  "$ROLLBACK_VALIDATED" "$SOURCE_VERIFIED" "$TEMP_ABSENT" \
  "${ROLLBACK_COMPLETE_NS:-0}" "$TRUSTED_RECOVERY_CONFIRMED" \
  "${TRUSTED_RECOVERY_NS:-0}" "$GROUND_AUTH_WAITED" \
  "${AUTHORIZATION_OBSERVED_NS:-0}" "${HANDOFF_NS:-0}" \
  "$AUTH_AVAILABLE_AT_BOUNDARY" "$MISSED_CONTACT_WINDOWS" \
  "$CRITERIA_JSON" <<'PY'
import json
import sys
from pathlib import Path

(
    path,
    plan_path,
    run_id,
    run_start_utc,
    run_start_ns,
    event_activation_ns,
    event_success_ns,
    policy_selection_ns,
    policy_enforcement_ns,
    response_boundary_ns,
    observation_complete_ns,
    post_slot_sha,
    runtime_health,
    noop_delta,
    selected_action,
    effective_policy,
    attacker_count,
    gateway_decisions,
    attacker_forwarded,
    authorized_gateway_forwarded,
    attacker_delta,
    rollback_validated,
    source_verified,
    temp_absent,
    rollback_ns,
    trusted,
    trusted_ns,
    ground_waited,
    auth_ns,
    handoff_ns,
    auth_available,
    missed,
    criteria_path,
) = sys.argv[1:]

plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
b = lambda value: value.lower() == "true"

row = {
    "schema": 1,
    "run_id": run_id,
    "run_start_utc": run_start_utc,
    "run_start_ns": int(run_start_ns),
    "event_activation_ns": int(event_activation_ns),
    "event_success_observed_ns": int(event_success_ns),
    "policy_selection_ns": int(policy_selection_ns),
    "policy_enforcement_ns": int(policy_enforcement_ns),
    "response_boundary_ns": int(response_boundary_ns),
    "observation_complete_ns": int(observation_complete_ns),
    "event_activation_observed": True,
    "event_slot_sha256": (
        "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"
    ),
    "runtime_health_passed": b(runtime_health),
    "policy_selection_not_gated_on_event_success": True,
    "authorized_noop_attempted": 1,
    "authorized_noop_marker_delta": int(noop_delta),
    "post_response_slot_sha256": post_slot_sha,
    "ground_authorization_waited": b(ground_waited),
}

if effective_policy == "P2":
    row.update({
        "update_containment_observed": False,
        "matched_attacker_probe_count": int(attacker_count),
        "gateway_decision_count": int(gateway_decisions),
        "attacker_gateway_forwarded_count": int(attacker_forwarded),
        "authorized_noop_gateway_forwarded": b(
            authorized_gateway_forwarded
        ),
        "gateway_action": selected_action,
        "observed_post_enforcement_attacker_reset_marker_delta": int(
            attacker_delta
        ),
    })
else:
    row.update({
        "rollback_request_validated": b(rollback_validated),
        "approved_replacement_source_verified": b(source_verified),
        "temporary_recovery_state_absent": b(temp_absent),
        "rollback_complete_ns": int(rollback_ns),
        "trusted_recovery_confirmed": b(trusted),
        "recovery_criteria": json.loads(
            Path(criteria_path).read_text(encoding="utf-8")
        ),
    })
    if b(trusted):
        row["trusted_recovery_observed_ns"] = int(trusted_ns)

    if effective_policy == "P6":
        row.update({
            "ground_authorization_source": (
                "synthetic_ground_authorization_schedule"
            ),
            "ground_authorization_current": True,
            "authorization_observed_ns": int(auth_ns),
            "handoff_ns": int(handoff_ns),
            "authorization_available_at_response_boundary": b(
                auth_available
            ),
            "missed_contact_windows_observed": int(missed),
            "post_authorization_delegate": "P5",
            "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
        })

Path(path).write_text(
    json.dumps(row, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e3_runtime_adapter \
  finalize-development \
  --plan-json "$PLAN_JSON" \
  --policy-json "$POLICY_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$SUMMARY_JSON"

echo "r063_observation_binding=PASS"

SUMMARY_VALUES="$(
  python3 - "$SUMMARY_JSON" <<'PY'
import json
import sys
from pathlib import Path
row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(row["outcome_matches_predeclared_expectation"]).lower())
print(str(
    row[
        "unexpected_scientific_outcome_would_be_retained_in_campaign"
    ]
).lower())
PY
)"
echo "outcome_matches_predeclared_expectation=$(printf '%s\n' "$SUMMARY_VALUES" | sed -n '1p')"
echo "unexpected_scientific_outcome_retained=$(printf '%s\n' "$SUMMARY_VALUES" | sed -n '2p')"
echo "post_event_analysis_horizon_s=30"
echo "runner_duration_used_as_metric_input=false"

PHASE="AUXILIARY_CLEANUP"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
echo "auxiliary_e3_cleanup=PASS"

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

PHASE="CLEANUP_AUDIT"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
docker rm -f "$CFS" >/dev/null 2>&1 || true
docker network rm "$NETWORK" >/dev/null 2>&1 || true

if docker ps -a --format '{{.Names}}' | grep -Fq "$SAFE_ID"; then
  echo "[ERROR] residual R-063 container remains" >&2
  exit 1
fi
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  echo "[ERROR] residual R-063 network remains" >&2
  exit 1
fi

echo "residual_runtime=none"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"

RESULT="PASS"
