#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
OBSERVATION_WINDOW_SECONDS=2

[[ "$#" -eq 1 ]] || { echo "usage: WP9B2_CONFIRM=EXECUTE-D06 $0 <D06|D07|D08>" >&2; exit 2; }
CASE_ID="$1"
case "$CASE_ID" in D06|D07|D08) ;; *) echo "[ERROR] fixed-E3 runner supports D06-D08 only" >&2; exit 2 ;; esac
EXPECTED_CONFIRM="EXECUTE-$CASE_ID"
[[ "${WP9B2_CONFIRM:-}" == "$EXPECTED_CONFIRM" ]] || { echo "[ERROR] exact confirmation required: WP9B2_CONFIRM=$EXPECTED_CONFIRM" >&2; exit 2; }

cd "$ROOT"
for command in docker git python3 shasum; do command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] missing command: $command" >&2; exit 1; }; done
test -z "$(git status --short)" || { echo "[ERROR] repository worktree must be clean" >&2; exit 1; }
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development validate

docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon unavailable" >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] pinned NOS3 image unavailable" >&2; exit 1; }
echo "wp9b2_e3_fixed_docker_daemon=PASS"
echo "wp9b2_e3_fixed_pinned_image=PASS"

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
GATEWAY="mascr-$SAFE_ID-e3-gateway"

EVIDENCE="$ROOT/results/wp9/development/wp9b2/e3-fixed/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST_JSON="$GROUND/approved-manifest.json"
TAMPERED_VERIFY_JSON="$GROUND/tampered-verification.json"
REQUEST_JSON="$GROUND/rollback-request.json"
REQUEST_VALIDATION_JSON="$GROUND/rollback-request-validation.json"
REPLACEMENT_JSON="$GROUND/replacement-source-verification.json"
GATEWAY_TRUTH="$GROUND/gateway-truth.jsonl"
GATEWAY_DECISIONS="$OBS/gateway-decisions.jsonl"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"

SLOT="/work/nos3/fsw/build/exe/cpu1/cf/mission-aware-wp9b2-e3-event.pkg"
TEMP="/work/nos3/fsw/build/exe/cpu1/cf/mission-aware-wp9b2-e3-approved.tmp"
PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

count_reset_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: RESET counters command received' || true; }
count_noop_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true; }
slot_sha() { docker exec "$CFS" sh -lc 'sha256sum "$1" | awk "{print \$1}"' sh "$SLOT"; }

emit_invalid() {
  local rc="$1"
  [[ -d "$EVIDENCE" ]] || return 0
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json,sys
from pathlib import Path
p,run_id,case_id,seed,phase,rc,commit=sys.argv[1:]
Path(p).write_text(json.dumps({
 "schema":1,"classification":"WP9B2_E3_FIXED_DEVELOPMENT_RUN_INVALID",
 "run_id":run_id,"case_id":case_id,"development_seed":int(seed),
 "failed_phase":phase,"exit_code":int(rc),"repo_commit":commit,
 "development_runtime_data":True,"campaign_seed_consumed":False,
 "campaign_data":False,"scientific_failure_claim":False,
 "automatic_next_case":False
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if docker inspect "$CFS" >/dev/null 2>&1; then docker exec "$CFS" rm -f "$SLOT" "$TEMP" >/dev/null 2>&1 || true; fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then kill -TERM "$PRE_PID" >/dev/null 2>&1 || true; wait "$PRE_PID" >/dev/null 2>&1 || true; fi
  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP9B2_E3_FIXED_DEVELOPMENT_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "development_seed=$SEED"
    echo "development_runtime_data=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data=false"
    echo "automatic_next_case=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9B2_E3_FIXED_DEVELOPMENT_RUNTIME=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

mkdir -p "$GROUND" "$OBS"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"

PHASE="DEVELOPMENT_PLAN"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development plan \
  --case-id "$CASE_ID" --run-id "$RUN_ID" --repo-commit "$REPO_COMMIT" \
  --output-plan-json "$PLAN_JSON" --output-event-json "$EVENT_JSON" \
  --output-approved "$APPROVED" --output-tampered "$TAMPERED" \
  --output-manifest-json "$MANIFEST_JSON" \
  --output-tampered-verification-json "$TAMPERED_VERIFY_JSON"
echo "wp9b2_e3_fixed_development_plan=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" DURATION_SECONDS=90 STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!
echo "nominal_runtime_launch=PASS"

CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  [[ "$state" == running ]] && { CFS_READY=1; break; }
  sleep 1
done
[[ "$CFS_READY" -eq 1 ]] || { echo "[ERROR] nominal cFS not observed" >&2; exit 1; }
CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'" >/dev/null 2>&1; then CI_READY=1; break; fi
  sleep 1
done
[[ "$CI_READY" -eq 1 ]]
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
docker exec "$CFS" rm -f "$SLOT" "$TEMP"
echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

PHASE="EVENT_ACTIVATION"
EVENT_ACTIVATION_NS="$(python3 -c 'import time; print(time.monotonic_ns())')"
docker cp "$TAMPERED" "$CFS:$SLOT"
EVENT_SLOT_SHA="$(slot_sha)"
EVENT_SUCCESS_NS="$(python3 -c 'import time; print(time.monotonic_ns())')"
[[ "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS" ]]
echo "e3_event_activation_observed=PASS"

PHASE="RUNTIME_POLICY"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development observe-policy \
  --plan-json "$PLAN_JSON" --output-policy-json "$POLICY_JSON"

if [[ "$CASE_ID" == D06 || "$CASE_ID" == D07 ]]; then
  PHASE="P2_GATEWAY_LAUNCH"
  ACTION="$(python3 - "$POLICY_JSON" <<'PY'
import json,sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["selected_action"])
PY
)"
  docker run -d --rm --platform linux/amd64 --name "$GATEWAY" \
    --network "$NETWORK" --network-alias wp9b2-e3-gateway \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/ground" \
    --mount "type=bind,source=$OBS,target=/obs" \
    "$IMAGE" python3 -m src.mission_recovery.policy_gateway serve \
      --action "$ACTION" --truth-jsonl /ground/gateway-truth.jsonl \
      --decision-jsonl /obs/gateway-decisions.jsonl >/dev/null

  GW_READY=0
  for _ in $(seq 1 50); do
    if docker exec "$GATEWAY" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:4A93$/ {f=1} END {exit f?0:1}'" >/dev/null 2>&1; then GW_READY=1; break; fi
    sleep 0.1
  done
  [[ "$GW_READY" -eq 1 ]] || { echo "[ERROR] P2 gateway not ready" >&2; exit 1; }
  echo "p2_gateway_ready=PASS"

  RESET_BEFORE="$(count_reset_marker)"
  NOOP_BEFORE="$(count_noop_marker)"
  for N in 1 2; do
    docker run --rm --platform linux/amd64 --network "$NETWORK" \
      --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
      --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
      python3 -m src.mission_recovery.policy_gateway send \
        --source-id modeled_attacker --command-class sample_reset_counters \
        --gateway-host wp9b2-e3-gateway --result-json "/evidence/attacker-$N.json" >/dev/null
  done
  docker run --rm --platform linux/amd64 --network "$NETWORK" \
    --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id authorized_ground --command-class sample_noop \
      --gateway-host wp9b2-e3-gateway --result-json /evidence/authorized-noop.json >/dev/null

  echo "fixed_post_response_observation_window_s=$OBSERVATION_WINDOW_SECONDS"
  sleep "$OBSERVATION_WINDOW_SECONDS"
  RESET_AFTER="$(count_reset_marker)"
  NOOP_AFTER="$(count_noop_marker)"
  POST_SLOT_SHA="$(slot_sha)"
  DECISION_COUNT="$(grep -cve '^[[:space:]]*$' "$GATEWAY_DECISIONS" || true)"
  echo "p2_gateway_decision_count=$DECISION_COUNT"

  PHASE="P2_ACCEPTANCE"
  PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development finalize-p2 \
    --plan-json "$PLAN_JSON" --policy-json "$POLICY_JSON" \
    --gateway-decisions-jsonl "$GATEWAY_DECISIONS" \
    --event-slot-sha256 "$EVENT_SLOT_SHA" --post-response-slot-sha256 "$POST_SLOT_SHA" \
    --reset-before "$RESET_BEFORE" --reset-after "$RESET_AFTER" \
    --noop-before "$NOOP_BEFORE" --noop-after "$NOOP_AFTER" \
    --output-summary-json "$SUMMARY_JSON"
else
  PHASE="P5_ROLLBACK_REQUEST"
  PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development build-rollback \
    --plan-json "$PLAN_JSON" --policy-json "$POLICY_JSON" \
    --output-request-json "$REQUEST_JSON" --output-validation-json "$REQUEST_VALIDATION_JSON" \
    --output-replacement-json "$REPLACEMENT_JSON"

  PHASE="P5_MODELED_ROLLBACK"
  docker cp "$APPROVED" "$CFS:$TEMP"
  docker exec "$CFS" sh -lc 'mv "$1" "$2"' sh "$TEMP" "$SLOT"
  POST_SLOT_SHA="$(slot_sha)"
  echo "approved_replacement_runtime_activation=PASS"

  NOOP_BEFORE="$(count_noop_marker)"
  docker run --rm -i --platform linux/amd64 --network "$NETWORK" \
    --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    "$IMAGE" python3 - <<'PY'
import socket
from src.mission_recovery.nos3_e1_adapter import build_sample_noop_packet
p=build_sample_noop_packet(); s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sent=s.sendto(p,("nos-fsw",5012)); s.close(); assert sent==len(p)
PY
  sleep "$OBSERVATION_WINDOW_SECONDS"
  NOOP_AFTER="$(count_noop_marker)"
  NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))

  PHASE="P5_ACCEPTANCE"
  PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_e3_fixed_development finalize-p5 \
    --plan-json "$PLAN_JSON" --policy-json "$POLICY_JSON" \
    --request-json "$REQUEST_JSON" --validation-json "$REQUEST_VALIDATION_JSON" \
    --replacement-json "$REPLACEMENT_JSON" --event-slot-sha256 "$EVENT_SLOT_SHA" \
    --post-response-slot-sha256 "$POST_SLOT_SHA" --authorized-noop-delta "$NOOP_DELTA" \
    --output-summary-json "$SUMMARY_JSON"
fi

echo "wp9b2_e3_fixed_acceptance=PASS"

PHASE="NOMINAL_RUNTIME_COMPLETION"
set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""
[[ "$PRE_RC" -eq 0 ]] || { echo "[ERROR] nominal runtime failed: rc=$PRE_RC" >&2; tail -120 "$NOMINAL_LOG" >&2 || true; exit 1; }
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"
echo "nominal_runtime_completion=PASS"

docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
echo "auxiliary_gateway_cleanup=PASS"

PHASE="RESIDUE_CHECK"
RESIDUAL="$(docker ps --format '{{.Names}}' | grep "^mascr-$SAFE_ID" || true)"
[[ -z "$RESIDUAL" ]] || { echo "[ERROR] residual runtime remains: $RESIDUAL" >&2; exit 1; }
echo "residual_runtime=none"
echo "trusted_recovery_claim=false"
echo "campaign_seed_consumed=false"
echo "campaign_data=false"
echo "automatic_next_case=false"
RESULT="PASS"
