#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
E4_TLM_PORT=5013
GATEWAY_PORT=19091
OPERATIONAL_VISIBILITY_CAPTURE_SECONDS=3

[[ "$#" -eq 1 ]] || {
  echo "usage: $0 <W01|W02|W03>" >&2
  exit 2
}

CASE_ID="$1"
case "$CASE_ID" in
  W01) CELL_ID="A22"; SEED="9911" ;;
  W02) CELL_ID="A23"; SEED="9912" ;;
  W03) CELL_ID="A24"; SEED="9913" ;;
  *)
    echo "[ERROR] R-059 E4 route validation supports W01-W03 only" >&2
    exit 2
    ;;
esac

cd "$ROOT"
for command in docker git python3 shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before R-059 runtime validation" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e4_runtime_adapter \
  validate-static

TOKEN="$(python3 - <<'PY'
import uuid
print(uuid.uuid4().hex)
PY
)"
CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r059-${CASE_SAFE}-s${SEED}-${TOKEN}}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-r059-e4-proxy"
OBSERVER="mascr-$SAFE_ID-r059-e4-observer"
GATEWAY="mascr-$SAFE_ID-r059-e4-gateway"
PROXY_ALIAS="r059-e4-proxy"
OBSERVER_ALIAS="r059-e4-observer"
GATEWAY_ALIAS="r059-e4-gateway"

EVIDENCE="$ROOT/results/wp9/development/r059/e4/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
ENABLE_JSON="$GROUND/enable-output.json"
EVENT_SEND_JSON="$GROUND/event-send-data-types.json"
POST_SEND_JSON="$GROUND/post-response-send-data-types.json"
NOOP_JSON="$GROUND/post-response-authorized-noop.json"
TRUTH_JSONL="$GROUND/telemetry-truth.jsonl"
VISIBLE_JSONL="$OBS/policy-visible.jsonl"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
MEASUREMENT_JSON="$OBS/e4-route-measurement.json"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
REPO_COMMIT="unknown"
RUN_START_NS=""
RUN_START_UTC=""
EVENT_ACTIVATION_NS=""
POLICY_SELECTION_NS=""
POLICY_ENFORCEMENT_NS=""
EVENT_SUCCESS_NS=""
POST_PROBE_NS=""
AUTHORIZED_NOOP_NS=""
OBSERVATION_COMPLETE_NS=""

mono_ns() {
  python3 - <<'PY'
import time
print(time.monotonic_ns())
PY
}

wait_until_ns() {
  local deadline_ns="$1" now
  while true; do
    now="$(mono_ns)"
    [[ "$now" -ge "$deadline_ns" ]] && return 0
    sleep 0.05
  done
}

count_mid() {
  python3 - "$1" "$2" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
mid = int(sys.argv[2], 0)
if not path.exists():
    print(0)
    raise SystemExit(0)
count = 0
for line in path.read_text(encoding="utf-8").splitlines():
    if line.strip() and json.loads(line).get("mid") == mid:
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

wait_decision_count() {
  local expected="$1" count
  for _ in $(seq 1 50); do
    count="$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
if not path.exists():
    print(0)
else:
    print(sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()))
PY
)"
    [[ "$count" -eq "$expected" ]] && return 0
    [[ "$count" -gt "$expected" ]] && return 2
    sleep 0.1
  done
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
      "$@" --result-json "/evidence/$result_file" >/dev/null
}

emit_invalid() {
  local rc="$1"
  mkdir -p "$EVIDENCE"
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$CELL_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json, sys
from pathlib import Path
path, run_id, case_id, cell_id, seed, phase, rc, commit = sys.argv[1:]
record = {
    "schema": 1,
    "decision_id": "R-059",
    "classification": "WP9_R059_E4_ROUTE_VALIDATION_RUN_INVALID",
    "run_id": run_id,
    "case_id": case_id,
    "cell_id": cell_id,
    "development_seed": int(seed),
    "failed_phase": phase,
    "exit_code": int(rc),
    "repo_commit": commit,
    "development_validation_only": True,
    "development_runtime_data": False,
    "campaign_seed_consumed": False,
    "campaign_data_generated": False,
    "final_campaign_failure_claimed": False,
    "automatic_retry_allowed": False,
    "automatic_next_case_allowed": False,
}
Path(path).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R059_E4_ROUTE_VALIDATION_RUNTIME=PASS"
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
    echo "WP9_R059_E4_ROUTE_VALIDATION_RUNTIME=FAIL" >&2
    echo "case_id=$CASE_ID" >&2
    echo "cell_id=$CELL_ID" >&2
    echo "failed_phase=$PHASE" >&2
    echo "campaign_seed_consumed=false" >&2
    echo "campaign_data_generated=false" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

PHASE="DOCKER_PREFLIGHT"
docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}
REPO_COMMIT="$(git rev-parse HEAD)"
mkdir -p "$GROUND" "$OBS"
: > "$TRUTH_JSONL"
: > "$VISIBLE_JSONL"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"
echo "r059_docker_daemon=PASS"
echo "r059_pinned_image=PASS"
echo "campaign_seed_consumed=false"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" \
DURATION_SECONDS=90 \
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

PHASE="NOMINAL_TOLAB_SETTLE"
TOLAB_READY=0
for _ in $(seq 1 60); do
  if docker logs "$CFS" 2>&1 |
    grep -Fq 'TO telemetry output enabled for IP active-gs'
  then
    TOLAB_READY=1
    break
  fi
  sleep 0.2
done
[[ "$TOLAB_READY" -eq 1 ]] || {
  echo "[ERROR] nominal TO_LAB destination not observed" >&2
  exit 1
}
NOMINAL_ENABLE_COUNT="$(count_tolab_enable_markers)"
[[ "$(last_tolab_destination)" == "active-gs" ]]

PHASE="E4_MEASUREMENT_PLANE"
docker run -d --platform linux/amd64 \
  --name "$OBSERVER" --hostname "$OBSERVER_ALIAS" \
  --network "$NETWORK" --network-alias "$OBSERVER_ALIAS" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$OBS,target=/evidence" \
  "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility observer \
    --jsonl /evidence/policy-visible.jsonl --port 19090 >/dev/null

docker run -d --platform linux/amd64 \
  --name "$PROXY" --hostname "$PROXY_ALIAS" \
  --network "$NETWORK" --network-alias "$PROXY_ALIAS" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/truth" \
  "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility proxy \
    --truth-jsonl /truth/telemetry-truth.jsonl \
    --mode degraded --listen-port "$E4_TLM_PORT" \
    --policy-host "$OBSERVER_ALIAS" --policy-port 19090 >/dev/null

PROXY_READY=0
HEX_TLM_PORT="$(printf '%04X' "$E4_TLM_PORT")"
for _ in $(seq 1 40); do
  if [[ "$(docker inspect "$PROXY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     [[ "$(docker inspect "$OBSERVER" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$PROXY" sh -lc \
       "awk '\$2 ~ /:${HEX_TLM_PORT}$/ {f=1} END {exit f?0:1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    PROXY_READY=1
    break
  fi
  sleep 0.2
done
[[ "$PROXY_READY" -eq 1 ]] || {
  echo "[ERROR] E4 degraded measurement plane not ready" >&2
  exit 1
}

run_e4_adapter "$(basename "$ENABLE_JSON")" enable-output --destination "$PROXY_ALIAS"
ENABLE_READY=0
for _ in $(seq 1 40); do
  if docker logs "$CFS" 2>&1 |
    grep -Fq "TO telemetry output enabled for IP $PROXY_ALIAS"
  then
    ENABLE_READY=1
    break
  fi
  sleep 0.2
done
[[ "$ENABLE_READY" -eq 1 ]]
E4_ENABLE_COUNT="$(count_tolab_enable_markers)"
[[ "$E4_ENABLE_COUNT" -eq $((NOMINAL_ENABLE_COUNT + 1)) ]]
[[ "$(last_tolab_destination)" == "$PROXY_ALIAS" ]]
echo "e4_degraded_measurement_plane_ready=PASS"
echo "operational_visibility_capture_s=$OPERATIONAL_VISIBILITY_CAPTURE_SECONDS"
echo "operational_visibility_capture_used_as_analysis_horizon=false"

EVENT_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
EVENT_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
[[ "$EVENT_TRUTH_BEFORE" -eq 0 ]]
[[ "$EVENT_VISIBLE_BEFORE" -eq 0 ]]

PHASE="EVENT_ACTIVATION"
RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EVENT_ACTIVATION_NS="$(mono_ns)"
run_e4_adapter "$(basename "$EVENT_SEND_JSON")" send-data-types
echo "e4_high_value_sample_injected=PASS"

PHASE="POLICY_SELECTION"
PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e4_runtime_adapter \
  plan-development \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-json "$PLAN_JSON"
POLICY_SELECTION_NS="$(mono_ns)"
ACTION="$(python3 - "$PLAN_JSON" <<'PY'
import json, sys
from pathlib import Path
plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(plan["runtime_policy_decision"]["selected_action"])
PY
)"
echo "r059_development_plan=PASS"
echo "selected_action=$ACTION"
echo "policy_trigger_uses_ground_truth=false"

PHASE="POLICY_GATEWAY_START"
docker run -d --platform linux/amd64 \
  --name "$GATEWAY" --hostname "$GATEWAY_ALIAS" \
  --network "$NETWORK" --network-alias "$GATEWAY_ALIAS" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/ground" \
  "$IMAGE" python3 -m src.mission_recovery.policy_gateway serve \
    --action "$ACTION" \
    --truth-jsonl /ground/gateway-ingress.jsonl \
    --decision-jsonl /ground/gateway-decisions.jsonl >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' "$GATEWAY_PORT")"
for _ in $(seq 1 40); do
  if docker exec "$GATEWAY" sh -lc \
    "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {f=1} END {exit f?0:1}' /proc/net/udp" \
    >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 0.2
done
[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] E4 policy gateway not ready" >&2
  exit 1
}
POLICY_ENFORCEMENT_NS="$(mono_ns)"
echo "policy_gateway_ready=PASS"

PHASE="EVENT_TREATMENT_FIDELITY"
EVENT_CAPTURE_DEADLINE_NS=$((EVENT_ACTIVATION_NS + OPERATIONAL_VISIBILITY_CAPTURE_SECONDS * 1000000000))
wait_until_ns "$EVENT_CAPTURE_DEADLINE_NS"
EVENT_SUCCESS_NS="$(mono_ns)"
EVENT_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
EVENT_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
EVENT_TRUTH_DELTA=$((EVENT_TRUTH_AFTER - EVENT_TRUTH_BEFORE))
EVENT_VISIBLE_DELTA=$((EVENT_VISIBLE_AFTER - EVENT_VISIBLE_BEFORE))
[[ "$EVENT_TRUTH_DELTA" -eq 1 ]] || {
  echo "[ERROR] E4 immutable-truth event sample delta=$EVENT_TRUTH_DELTA" >&2
  exit 1
}
[[ "$EVENT_VISIBLE_DELTA" -eq 0 ]] || {
  echo "[ERROR] E4 degraded policy-visible treatment failed: delta=$EVENT_VISIBLE_DELTA" >&2
  exit 1
}
echo "event_truth_high_value_delta=1"
echo "event_policy_visible_high_value_delta=0"

PHASE="POST_RESPONSE_TELEMETRY_PROBE"
POST_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
POST_SEND_NS="$(mono_ns)"
run_e4_adapter "$(basename "$POST_SEND_JSON")" send-data-types
POST_CAPTURE_DEADLINE_NS=$((POST_SEND_NS + OPERATIONAL_VISIBILITY_CAPTURE_SECONDS * 1000000000))
wait_until_ns "$POST_CAPTURE_DEADLINE_NS"
POST_PROBE_NS="$(mono_ns)"
POST_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
POST_TRUTH_DELTA=$((POST_TRUTH_AFTER - POST_TRUTH_BEFORE))
POST_VISIBLE_DELTA=$((POST_VISIBLE_AFTER - POST_VISIBLE_BEFORE))
[[ "$POST_TRUTH_DELTA" -eq 1 ]] || {
  echo "[ERROR] E4 post-response immutable-truth probe delta=$POST_TRUTH_DELTA" >&2
  exit 1
}
[[ "$POST_VISIBLE_DELTA" -eq 0 || "$POST_VISIBLE_DELTA" -eq 1 ]] || {
  echo "[ERROR] E4 post-response visible delta outside 0/1: $POST_VISIBLE_DELTA" >&2
  exit 1
}
echo "post_response_truth_high_value_delta=$POST_TRUTH_DELTA"
echo "post_response_policy_visible_high_value_delta=$POST_VISIBLE_DELTA"

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"
NOOP_BEFORE="$(count_noop_marker)"
docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" python3 -m src.mission_recovery.policy_gateway send \
    --source-id authorized_ground \
    --command-class sample_noop \
    --gateway-host "$GATEWAY_ALIAS" \
    --result-json "/evidence/$(basename "$NOOP_JSON")"
wait_decision_count 1 || {
  echo "[ERROR] expected exactly one E4 gateway decision" >&2
  exit 1
}
sleep 0.5
NOOP_AFTER="$(count_noop_marker)"
NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
[[ "$NOOP_DELTA" -eq 0 || "$NOOP_DELTA" -eq 1 ]] || {
  echo "[ERROR] post-response authorized NOOP marker delta outside 0/1: $NOOP_DELTA" >&2
  exit 1
}
AUTHORIZED_NOOP_NS="$(mono_ns)"
read -r DECISION_ACTION DECISION_FORWARDED <<EOF
$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json, sys
from pathlib import Path
rows = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if line.strip()]
assert len(rows) == 1
print(rows[0]["action"], str(bool(rows[0]["forwarded"])).lower())
PY
)
EOF
echo "post_response_authorized_noop_attempted=1"
echo "post_response_authorized_noop_marker_delta=$NOOP_DELTA"
echo "authorized_noop_gateway_forwarded=$DECISION_FORWARDED"

PHASE="FROZEN_ANALYSIS_HORIZON"
ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))
wait_until_ns "$ANALYSIS_END_NS"
OBSERVATION_COMPLETE_NS="$(mono_ns)"
kill -0 "$PRE_PID" >/dev/null 2>&1 || {
  echo "[ERROR] nominal runtime ended before frozen E4 analysis horizon" >&2
  exit 1
}
echo "post_event_analysis_horizon_s=30"
echo "frozen_analysis_horizon_complete=PASS"

PHASE="AUXILIARY_CLEANUP"
docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true
echo "auxiliary_e4_cleanup=PASS"

PHASE="NOMINAL_RUNTIME_COMPLETION"
set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""
[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed: rc=$PRE_RC" >&2
  tail -120 "$NOMINAL_LOG" >&2 || true
  exit 1
}
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$RUNTIME_MANIFEST"
echo "nominal_runtime_completion=PASS"

PHASE="MEASUREMENT_BINDING"
python3 - "$MEASUREMENT_JSON" \
  "$RUN_ID" "$RUN_START_UTC" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$EVENT_SUCCESS_NS" "$POST_PROBE_NS" "$AUTHORIZED_NOOP_NS" \
  "$OBSERVATION_COMPLETE_NS" \
  "$EVENT_TRUTH_DELTA" "$EVENT_VISIBLE_DELTA" \
  "$POST_TRUTH_DELTA" "$POST_VISIBLE_DELTA" \
  "$NOOP_DELTA" "$DECISION_ACTION" "$DECISION_FORWARDED" <<'PY'
import json, sys
from pathlib import Path
(
    path, run_id, run_start_utc,
    run_start_ns, event_activation_ns,
    policy_selection_ns, policy_enforcement_ns,
    event_success_ns, post_probe_ns, authorized_noop_ns,
    observation_complete_ns,
    event_truth, event_visible, post_truth, post_visible,
    noop_delta, decision_action, decision_forwarded,
) = sys.argv[1:]
record = {
    "schema": 1,
    "run_id": run_id,
    "run_start_utc": run_start_utc,
    "run_start_ns": int(run_start_ns),
    "event_activation_ns": int(event_activation_ns),
    "policy_selection_ns": int(policy_selection_ns),
    "policy_enforcement_ns": int(policy_enforcement_ns),
    "event_success_observed_ns": int(event_success_ns),
    "post_response_probe_observed_ns": int(post_probe_ns),
    "authorized_noop_probe_observed_ns": int(authorized_noop_ns),
    "observation_complete_ns": int(observation_complete_ns),
    "event_truth_high_value_delta": int(event_truth),
    "event_policy_visible_high_value_delta": int(event_visible),
    "post_response_truth_high_value_delta": int(post_truth),
    "post_response_policy_visible_high_value_delta": int(post_visible),
    "post_response_authorized_noop_attempted": 1,
    "post_response_authorized_noop_marker_delta": int(noop_delta),
    "gateway_decision_count": 1,
    "immutable_truth_separate": True,
    "runtime_health_passed": True,
    "authorized_noop_gateway_action": decision_action,
    "authorized_noop_gateway_forwarded": decision_forwarded == "true",
}
Path(path).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY

PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e4_runtime_adapter \
  finalize-development \
  --plan-json "$PLAN_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$SUMMARY_JSON"
echo "r059_observation_binding=PASS"

PHASE="CLEANUP_AUDIT"
docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true
docker network rm "$NETWORK" >/dev/null 2>&1 || true
for name in "$CFS" "$GATEWAY" "$PROXY" "$OBSERVER"; do
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
RESULT="PASS"
