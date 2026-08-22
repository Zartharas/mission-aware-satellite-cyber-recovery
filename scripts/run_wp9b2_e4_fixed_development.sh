#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
VISIBILITY_DEADLINE_SECONDS=3
E4_TLM_PORT=5013
GATEWAY_PORT=19091

[[ "$#" -eq 1 ]] || {
  echo "usage: WP9B2_CONFIRM=EXECUTE-D09 $0 <D09|D10>" >&2
  exit 2
}
CASE_ID="$1"
case "$CASE_ID" in
  D09|D10) ;;
  *) echo "[ERROR] fixed-E4 runner supports D09-D10 only" >&2; exit 2 ;;
esac
EXPECTED_CONFIRM="EXECUTE-$CASE_ID"
[[ "${WP9B2_CONFIRM:-}" == "$EXPECTED_CONFIRM" ]] || {
  echo "[ERROR] exact confirmation required: WP9B2_CONFIRM=$EXPECTED_CONFIRM" >&2
  exit 2
}

cd "$ROOT"
for command in docker git python3 shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9b2_e4_fixed_development validate

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon unavailable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}
echo "wp9b2_e4_fixed_docker_daemon=PASS"
echo "wp9b2_e4_fixed_pinned_image=PASS"

REPO_COMMIT="$(git rev-parse HEAD)"
SEED="$(python3 - "$ROOT/configs/wp9b2_development_cases.json" "$CASE_ID" <<'PY'
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(next(x for x in d["cases"] if x["case_id"]==sys.argv[2])["development_seed"])
PY
)"
CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9b2-${CASE_SAFE}-s${SEED}-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-e4-proxy"
OBSERVER="mascr-$SAFE_ID-e4-observer"
GATEWAY="mascr-$SAFE_ID-e4-gateway"
GATEWAY_HOST="wp9b2-e4-gateway"

EVIDENCE="$ROOT/results/wp9/development/wp9b2/e4-fixed/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
TRUTH_JSONL="$GROUND/telemetry-truth.jsonl"
VISIBLE_JSONL="$OBS/policy-visible.jsonl"
GATEWAY_TRUTH="$GROUND/p4-command-gateway-truth.jsonl"
GATEWAY_DECISIONS="$OBS/p4-command-gateway-decisions.jsonl"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
ENABLE_JSON="$GROUND/enable-output.json"
EVENT_SEND_JSON="$GROUND/event-send-data-types.json"
POST_SEND_JSON="$GROUND/post-response-send-data-types.json"
P4_PROBE_JSON="$GROUND/p4-authorized-noop-probe.json"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

count_mid() {
  python3 - "$1" "$2" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); mid=int(sys.argv[2],0)
if not path.exists():
    print(0); raise SystemExit(0)
count=0
for line in path.read_text(encoding="utf-8").splitlines():
    if line.strip() and json.loads(line).get("mid")==mid:
        count+=1
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

wait_until_ns() {
  local deadline_ns="$1" now
  while true; do
    now="$(mono_ns)"
    [[ "$now" -ge "$deadline_ns" ]] && return 0
    sleep 0.05
  done
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
  [[ -d "$EVIDENCE" ]] || return 0
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json,sys
from pathlib import Path
p,run_id,case_id,seed,phase,rc,commit=sys.argv[1:]
Path(p).write_text(json.dumps({
  "schema":1,
  "classification":"WP9B2_E4_FIXED_DEVELOPMENT_RUN_INVALID",
  "run_id":run_id,
  "case_id":case_id,
  "development_seed":int(seed),
  "failed_phase":phase,
  "exit_code":int(rc),
  "repo_commit":commit,
  "development_runtime_data":True,
  "campaign_seed_consumed":False,
  "campaign_data":False,
  "scientific_failure_claim":False,
  "automatic_next_case":False
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
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
  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP9B2_E4_FIXED_DEVELOPMENT_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "development_seed=$SEED"
    echo "development_runtime_data=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data=false"
    echo "automatic_next_case=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9B2_E4_FIXED_DEVELOPMENT_RUNTIME=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

mkdir -p "$GROUND" "$OBS"
: > "$TRUTH_JSONL"
: > "$VISIBLE_JSONL"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"

PHASE="DEVELOPMENT_PLAN"
PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9b2_e4_fixed_development plan \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-plan-json "$PLAN_JSON" \
  --output-event-json "$EVENT_JSON"
echo "wp9b2_e4_fixed_development_plan=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!
echo "nominal_runtime_launch=PASS"

CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  [[ "$state" == running ]] && { CFS_READY=1; break; }
  sleep 1
done
[[ "$CFS_READY" -eq 1 ]] || {
  echo "[ERROR] nominal cFS not observed" >&2
  exit 1
}

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'" \
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
echo "nominal_tolab_destination=active-gs"

PHASE="E4_MEASUREMENT_PLANE"
docker run -d --platform linux/amd64 \
  --name "$OBSERVER" --hostname e4-observer \
  --network "$NETWORK" --network-alias e4-observer \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$OBS,target=/evidence" \
  "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility observer \
    --jsonl /evidence/policy-visible.jsonl --port 19090 >/dev/null

docker run -d --platform linux/amd64 \
  --name "$PROXY" --hostname e4-proxy \
  --network "$NETWORK" --network-alias e4-proxy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/truth" \
  "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility proxy \
    --truth-jsonl /truth/telemetry-truth.jsonl \
    --mode degraded --listen-port "$E4_TLM_PORT" \
    --policy-host e4-observer --policy-port 19090 >/dev/null

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

run_e4_adapter "$(basename "$ENABLE_JSON")" enable-output --destination e4-proxy
ENABLE_READY=0
for _ in $(seq 1 40); do
  if docker logs "$CFS" 2>&1 |
    grep -Fq 'TO telemetry output enabled for IP e4-proxy'
  then
    ENABLE_READY=1
    break
  fi
  sleep 0.2
done
[[ "$ENABLE_READY" -eq 1 ]]
E4_ENABLE_COUNT="$(count_tolab_enable_markers)"
[[ "$E4_ENABLE_COUNT" -eq $((NOMINAL_ENABLE_COUNT + 1)) ]]
[[ "$(last_tolab_destination)" == "e4-proxy" ]]
echo "e4_degraded_measurement_plane_ready=PASS"
echo "e4_tolab_destination=e4-proxy"
echo "visibility_deadline_s=$VISIBILITY_DEADLINE_SECONDS"

EVENT_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
EVENT_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
[[ "$EVENT_TRUTH_BEFORE" -eq 0 ]]
[[ "$EVENT_VISIBLE_BEFORE" -eq 0 ]]

PHASE="EVENT_ACTIVATION"
EVENT_ACTIVATION_NS="$(mono_ns)"
EVENT_DEADLINE_NS=$((EVENT_ACTIVATION_NS + VISIBILITY_DEADLINE_SECONDS * 1000000000))
run_e4_adapter "$(basename "$EVENT_SEND_JSON")" send-data-types
echo "e4_high_value_sample_injected=PASS"

PHASE="POLICY_SELECTION"
PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9b2_e4_fixed_development observe-policy \
  --plan-json "$PLAN_JSON" \
  --event-json "$EVENT_JSON" \
  --output-policy-json "$POLICY_JSON"
POLICY_SELECTION_NS="$(mono_ns)"
[[ "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS" ]]

NOOP_BEFORE="$(count_noop_marker)"
NOOP_AFTER="$NOOP_BEFORE"

if [[ "$CASE_ID" == D10 ]]; then
  PHASE="P4_GATEWAY_LAUNCH"
  docker run -d --rm --platform linux/amd64 \
    --name "$GATEWAY" --hostname e4-gateway \
    --network "$NETWORK" --network-alias "$GATEWAY_HOST" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/ground" \
    --mount "type=bind,source=$OBS,target=/obs" \
    "$IMAGE" python3 -m src.mission_recovery.policy_gateway serve \
      --action ENTER_SAFE_MODE \
      --truth-jsonl /ground/p4-command-gateway-truth.jsonl \
      --decision-jsonl /obs/p4-command-gateway-decisions.jsonl >/dev/null

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
    echo "[ERROR] P4 modeled command gate not ready" >&2
    exit 1
  }
  echo "p4_modeled_command_gate=PASS"
  echo "p4_native_safe_mode_claim=false"

  PHASE="P4_AUTHORIZED_NOOP_PROBE"
  docker run --rm -i --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" python3 - "$GATEWAY_HOST" "/evidence/$(basename "$P4_PROBE_JSON")" <<'PY'
import hashlib,json,socket,sys
from pathlib import Path
from src.mission_recovery.policy_gateway import GATEWAY_PORT, build_sample_noargs_packet
packet=build_sample_noargs_packet("sample_noop")
envelope={
  "schema":1,"event_id":None,"study_event":False,
  "probe_variant":"wp9b2_e4_p4_legitimate_command_cost",
  "source_id":"authorized_ground","command_class":"sample_noop",
  "declared_risk_class":"low","packet_hex":packet.hex(),
  "packet_sha256":hashlib.sha256(packet).hexdigest()
}
encoded=(json.dumps(envelope,sort_keys=True,separators=(",",":"))+"\n").encode()
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
    sent=sock.sendto(encoded,(sys.argv[1],GATEWAY_PORT))
assert sent==len(encoded)
Path(sys.argv[2]).write_text(json.dumps({
  "schema":1,"study_event":False,"role":"P4_legitimate_command_probe",
  "packet_sha256":envelope["packet_sha256"],"envelope_bytes_sent":sent
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY

  DECISION_READY=0
  for _ in $(seq 1 40); do
    DECISION_COUNT="$(grep -cve '^[[:space:]]*$' "$GATEWAY_DECISIONS" || true)"
    if [[ "$DECISION_COUNT" -eq 1 ]]; then
      DECISION_READY=1
      break
    fi
    [[ "$DECISION_COUNT" -gt 1 ]] && break
    sleep 0.1
  done
  [[ "$DECISION_READY" -eq 1 ]] || {
    echo "[ERROR] expected exactly one P4 gateway decision" >&2
    exit 1
  }
  sleep 0.5
  NOOP_AFTER="$(count_noop_marker)"
  echo "p4_gateway_decision_count=1"
fi

PHASE="EVENT_SUCCESS_OBSERVATION"
wait_until_ns "$EVENT_DEADLINE_NS"
EVENT_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
EVENT_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
echo "event_truth_high_value_delta=$((EVENT_TRUTH_AFTER - EVENT_TRUTH_BEFORE))"
echo "event_policy_visible_high_value_delta=$((EVENT_VISIBLE_AFTER - EVENT_VISIBLE_BEFORE))"

PHASE="POST_RESPONSE_TELEMETRY_PROBE"
POST_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
POST_ACTIVATION_NS="$(mono_ns)"
POST_DEADLINE_NS=$((POST_ACTIVATION_NS + VISIBILITY_DEADLINE_SECONDS * 1000000000))
run_e4_adapter "$(basename "$POST_SEND_JSON")" send-data-types
wait_until_ns "$POST_DEADLINE_NS"
POST_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POST_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"
echo "post_response_truth_high_value_delta=$((POST_TRUTH_AFTER - POST_TRUTH_BEFORE))"
echo "post_response_policy_visible_high_value_delta=$((POST_VISIBLE_AFTER - POST_VISIBLE_BEFORE))"

PHASE="ACCEPTANCE"
FINALIZE_ARGS=(
  --plan-json "$PLAN_JSON"
  --policy-json "$POLICY_JSON"
  --event-truth-before "$EVENT_TRUTH_BEFORE"
  --event-truth-after "$EVENT_TRUTH_AFTER"
  --event-visible-before "$EVENT_VISIBLE_BEFORE"
  --event-visible-after "$EVENT_VISIBLE_AFTER"
  --post-truth-before "$POST_TRUTH_BEFORE"
  --post-truth-after "$POST_TRUTH_AFTER"
  --post-visible-before "$POST_VISIBLE_BEFORE"
  --post-visible-after "$POST_VISIBLE_AFTER"
  --noop-before "$NOOP_BEFORE"
  --noop-after "$NOOP_AFTER"
  --output-summary-json "$SUMMARY_JSON"
)
if [[ "$CASE_ID" == D10 ]]; then
  FINALIZE_ARGS+=(--gateway-decisions-jsonl "$GATEWAY_DECISIONS")
fi
PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9b2_e4_fixed_development finalize \
  "${FINALIZE_ARGS[@]}"
echo "wp9b2_e4_fixed_acceptance=PASS"

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
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"
echo "nominal_runtime_completion=PASS"

PHASE="RESIDUE_CHECK"
RESIDUAL="$(docker ps --format '{{.Names}}' | grep "^mascr-$SAFE_ID" || true)"
[[ -z "$RESIDUAL" ]] || {
  echo "[ERROR] residual runtime remains: $RESIDUAL" >&2
  exit 1
}
echo "residual_runtime=none"
echo "p4_native_safe_mode_claim=false"
echo "p4_telemetry_restoration_claim=false"
echo "spacecraft_failure_claim=false"
echo "campaign_seed_consumed=false"
echo "campaign_data=false"
echo "automatic_next_case=false"
RESULT="PASS"
