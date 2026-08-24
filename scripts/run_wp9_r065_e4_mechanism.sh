#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CASE_ID="Z03"
CELL_ID="A24"
SEED="9943"
E4_TLM_PORT=5013
GATEWAY_PORT=19091
CAPTURE_SECONDS=3
NOMINAL_DURATION_SECONDS=90

[[ "$#" -eq 4 && "$1" == "--request-json" && "$3" == "--output-json" ]] || {
  echo "usage: $0 --request-json <path> --output-json <path>" >&2
  exit 2
}
REQUEST_JSON="$2"
OUTPUT_JSON="$4"
cd "$ROOT"
for command in git python3 docker; do command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] missing command: $command" >&2; exit 1; }; done
REPO_COMMIT="$(git rev-parse HEAD)"
[[ "${WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}" == "1" ]] || { echo "[BLOCKED] R-065 development runtime authorization is not active" >&2; exit 3; }
[[ "${WP9_R065_AUTHORIZED_CASE:-}" == "$CASE_ID" ]] || { echo "[BLOCKED] R-065 authorization is not for Z03" >&2; exit 3; }
[[ "${WP9_R065_AUTHORIZED_SEED:-}" == "$SEED" ]] || { echo "[BLOCKED] R-065 authorization is not for development seed 9943" >&2; exit 3; }
[[ "${WP9_R065_AUTHORIZED_REPO_SHA:-}" == "$REPO_COMMIT" ]] || { echo "[BLOCKED] R-065 authorization SHA does not match current HEAD" >&2; exit 3; }
test -z "$(git status --short)" || { echo "[ERROR] repository worktree must be clean before R-065 Z03 runtime" >&2; exit 1; }

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver validate-request --request-json "$REQUEST_JSON" >/dev/null
read -r REQUEST_CASE REQUEST_CELL REQUEST_SEED REQUEST_SHA RUN_ID ACTION REQUEST_EVIDENCE <<EOF_REQUEST
$(python3 - "$REQUEST_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); print(r["case_id"],r["cell_id"],r["development_seed"],r["repo_commit"],r["run_id"],r["selected_action"],r["evidence_directory"])
PY
)
EOF_REQUEST
[[ "$REQUEST_CASE" == "$CASE_ID" && "$REQUEST_CELL" == "$CELL_ID" && "$REQUEST_SEED" == "$SEED" && "$REQUEST_SHA" == "$REPO_COMMIT" ]]
[[ "$ACTION" == "ENTER_SAFE_MODE" ]]
EXPECTED_EVIDENCE="results/wp9/development/r065/integration/$RUN_ID"
[[ "$REQUEST_EVIDENCE" == "$EXPECTED_EVIDENCE" ]] || { echo "[ERROR] Z03 evidence directory escaped development namespace" >&2; exit 1; }
EVIDENCE="$ROOT/$EXPECTED_EVIDENCE"; GROUND="$EVIDENCE/immutable-ground"; OBS="$EVIDENCE/runtime-observation"; mkdir -p "$GROUND" "$OBS"
EXPECTED_REQUEST="$GROUND/r065-execution-request.json"; EXPECTED_OUTPUT="$OBS/z03-driver-result.json"
[[ "$(cd "$(dirname "$REQUEST_JSON")" && pwd)/$(basename "$REQUEST_JSON")" == "$EXPECTED_REQUEST" ]]
[[ "$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")" == "$EXPECTED_OUTPUT" ]]

SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"; CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-r065-e4-proxy"; OBSERVER="mascr-$SAFE_ID-r065-e4-observer"; GATEWAY="mascr-$SAFE_ID-r065-e4-gateway"
PROXY_ALIAS="r065-e4-proxy"; OBSERVER_ALIAS="r065-e4-observer"; GATEWAY_ALIAS="r065-e4-gateway"
ENABLE_JSON="$GROUND/enable-output.json"; EVENT_SEND_JSON="$GROUND/event-send-data-types.json"; POST_SEND_JSON="$GROUND/post-response-send-data-types.json"; NOOP_JSON="$GROUND/post-response-authorized-noop.json"
TRUTH_JSONL="$GROUND/telemetry-truth.jsonl"; VISIBLE_JSONL="$OBS/policy-visible.jsonl"; GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"; GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
MEASUREMENT_JSON="$OBS/e4-route-measurement.json"; INVALID_JSON="$EVIDENCE/development-run-invalid.json"; NOMINAL_LOG="$OBS/nominal-runtime.log"; NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"; RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"
PRE_PID=""; RESULT="RUN_INVALID"; PHASE="INITIALIZATION"; DEVELOPMENT_SEED_CONSUMED=false
RUN_START_NS=""; RUN_START_UTC=""; EVENT_ACTIVATION_NS=""; POLICY_SELECTION_NS=""; POLICY_ENFORCEMENT_NS=""; EVENT_SUCCESS_NS=""; POST_PROBE_NS=""; AUTHORIZED_NOOP_NS=""; OBSERVATION_COMPLETE_NS=""
mono_ns(){ python3 -c 'import time; print(time.monotonic_ns())'; }
wait_until_ns(){ local d="$1" n; while true; do n="$(mono_ns)"; [[ "$n" -ge "$d" ]] && return 0; sleep 0.05; done; }
count_mid(){ python3 - "$1" "$2" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); mid=int(sys.argv[2],0); print(0 if not p.exists() else sum(1 for x in p.read_text(encoding="utf-8").splitlines() if x.strip() and json.loads(x).get("mid")==mid))
PY
}
count_noop_marker(){ docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true; }
count_tolab_enable_markers(){ docker logs "$CFS" 2>&1 | grep -Fc 'TO telemetry output enabled for IP ' || true; }
last_tolab_destination(){ docker logs "$CFS" 2>&1 | grep -F 'TO telemetry output enabled for IP ' | tail -1 | sed -E 's/.*TO telemetry output enabled for IP ([^[:space:]]+).*/\1/'; }
decision_count(){ python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); print(0 if not p.exists() else sum(1 for x in p.read_text(encoding="utf-8").splitlines() if x.strip()))
PY
}
wait_decision_count(){ local e="$1" c; for _ in $(seq 1 50); do c="$(decision_count)"; [[ "$c" -eq "$e" ]] && return 0; [[ "$c" -gt "$e" ]] && return 2; sleep 0.1; done; return 1; }
run_e4_adapter(){ local f="$1"; shift; docker run --rm --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.nos3_e4_adapter "$@" --result-json "/evidence/$f" >/dev/null; }

emit_invalid(){ local rc="$1"; [[ -f "$INVALID_JSON" ]] && return 0; python3 - "$INVALID_JSON" "$RUN_ID" "$PHASE" "$rc" "$REPO_COMMIT" "$DEVELOPMENT_SEED_CONSUMED" <<'PY'
import json,sys
from pathlib import Path
p,r,ph,rc,c,cons=sys.argv[1:]; Path(p).write_text(json.dumps({"schema":1,"decision_id":"R-065","classification":"WP9_R065_Z03_BOUNDED_INTEGRATION_RUN_INVALID","run_id":r,"case_id":"Z03","cell_id":"A24","development_seed":9943,"development_seed_consumed":cons=="true","failed_phase":ph,"exit_code":int(rc),"repo_commit":c,"development_validation_only":True,"invalid_attempt_retained":True,"campaign_seed_consumed":False,"campaign_data_generated":False,"final_campaign_execution_authorized":False,"automatic_retry_performed":False,"automatic_next_case_performed":False},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
}
cleanup(){ local rc=$?; set +e; docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true; [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1 && { kill -TERM "$PRE_PID" >/dev/null 2>&1 || true; wait "$PRE_PID" >/dev/null 2>&1 || true; }; docker network rm "$NETWORK" >/dev/null 2>&1 || true; if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then echo "WP9_R065_Z03_E4_MECHANISM_RUNTIME=PASS"; echo "case_id=$CASE_ID"; echo "cell_id=$CELL_ID"; echo "development_seed=$SEED"; echo "development_seed_consumed=true"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "evidence_directory=$EVIDENCE"; else emit_invalid "$rc" || true; echo "WP9_R065_Z03_E4_MECHANISM_RUNTIME=FAIL" >&2; echo "failed_phase=$PHASE" >&2; echo "automatic_retry_allowed=false" >&2; echo "automatic_next_case_allowed=false" >&2; echo "campaign_seed_consumed=false" >&2; echo "campaign_data_generated=false" >&2; echo "evidence_directory=$EVIDENCE" >&2; fi; exit "$rc"; }
trap cleanup EXIT; trap 'exit 130' INT TERM

: > "$TRUTH_JSONL"; : > "$VISIBLE_JSONL"; : > "$GATEWAY_TRUTH"; : > "$GATEWAY_DECISIONS"
PHASE="PREFLIGHT"; docker info >/dev/null 2>&1 || exit 1; docker image inspect "$IMAGE" >/dev/null 2>&1 || exit 1
echo "r065_z03_runtime_authorization=PASS"; echo "authorized_case=$CASE_ID"; echo "authorized_seed=$SEED"; echo "authorized_repo_sha=$REPO_COMMIT"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"

PHASE="NOMINAL_RUNTIME_LAUNCH"; RUN_ID="$RUN_ID" DURATION_SECONDS="$NOMINAL_DURATION_SECONDS" STARTUP_GRACE_SECONDS=20 bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 & PRE_PID=$!
PHASE="CFS_READINESS"; CFS_READY=0
for _ in $(seq 1 180); do kill -0 "$PRE_PID" >/dev/null 2>&1 || break; [[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && { CFS_READY=1; break; }; sleep 1; done
[[ "$CFS_READY" -eq 1 ]] || { tail -120 "$NOMINAL_LOG" >&2 || true; exit 1; }
CI_READY=0; for _ in $(seq 1 90); do kill -0 "$PRE_PID" >/dev/null 2>&1 || break; if docker exec "$CFS" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'" >/dev/null 2>&1; then CI_READY=1; break; fi; sleep 1; done
[[ "$CI_READY" -eq 1 ]]; [[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]; [[ -z "$(docker port "$CFS")" ]]; DEVELOPMENT_SEED_CONSUMED=true
echo "nominal_runtime_ready=PASS"; echo "nominal_isolation=PASS"

PHASE="NOMINAL_TOLAB_SETTLE"; TOLAB_READY=0
for _ in $(seq 1 60); do docker logs "$CFS" 2>&1 | grep -Fq 'TO telemetry output enabled for IP active-gs' && { TOLAB_READY=1; break; }; sleep 0.2; done
[[ "$TOLAB_READY" -eq 1 ]]; NOMINAL_ENABLE_COUNT="$(count_tolab_enable_markers)"; [[ "$(last_tolab_destination)" == "active-gs" ]]

PHASE="E4_MEASUREMENT_PLANE"
docker run -d --platform linux/amd64 --name "$OBSERVER" --hostname "$OBSERVER_ALIAS" --network "$NETWORK" --network-alias "$OBSERVER_ALIAS" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$OBS,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility observer --jsonl /evidence/policy-visible.jsonl --port 19090 >/dev/null
docker run -d --platform linux/amd64 --name "$PROXY" --hostname "$PROXY_ALIAS" --network "$NETWORK" --network-alias "$PROXY_ALIAS" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/truth" "$IMAGE" python3 -m src.mission_recovery.telemetry_visibility proxy --truth-jsonl /truth/telemetry-truth.jsonl --mode degraded --listen-port "$E4_TLM_PORT" --policy-host "$OBSERVER_ALIAS" --policy-port 19090 >/dev/null
PROXY_READY=0; HEX_TLM_PORT="$(printf '%04X' "$E4_TLM_PORT")"
for _ in $(seq 1 40); do if [[ "$(docker inspect "$PROXY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running && "$(docker inspect "$OBSERVER" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && docker exec "$PROXY" sh -lc "awk '\$2 ~ /:${HEX_TLM_PORT}$/ {f=1} END {exit f?0:1}' /proc/net/udp" >/dev/null 2>&1; then PROXY_READY=1; break; fi; sleep 0.2; done
[[ "$PROXY_READY" -eq 1 ]]; run_e4_adapter "$(basename "$ENABLE_JSON")" enable-output --destination "$PROXY_ALIAS"
ENABLE_READY=0; for _ in $(seq 1 40); do docker logs "$CFS" 2>&1 | grep -Fq "TO telemetry output enabled for IP $PROXY_ALIAS" && { ENABLE_READY=1; break; }; sleep 0.2; done
[[ "$ENABLE_READY" -eq 1 ]]; E4_ENABLE_COUNT="$(count_tolab_enable_markers)"; [[ "$E4_ENABLE_COUNT" -eq $((NOMINAL_ENABLE_COUNT + 1)) ]]; [[ "$(last_tolab_destination)" == "$PROXY_ALIAS" ]]
echo "e4_degraded_measurement_plane_ready=PASS"

EVENT_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"; EVENT_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"; [[ "$EVENT_TRUTH_BEFORE" -eq 0 && "$EVENT_VISIBLE_BEFORE" -eq 0 ]]
PHASE="EVENT_ACTIVATION"; RUN_START_NS="$(mono_ns)"; RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; EVENT_ACTIVATION_NS="$(mono_ns)"; run_e4_adapter "$(basename "$EVENT_SEND_JSON")" send-data-types
PHASE="POLICY_SELECTION"; POLICY_SELECTION_NS="$(mono_ns)"; echo "actual_effective_policy_id=P4"; echo "selected_action=$ACTION"; echo "policy_trigger_uses_ground_truth=false"
PHASE="POLICY_GATEWAY_START"
docker run -d --platform linux/amd64 --name "$GATEWAY" --hostname "$GATEWAY_ALIAS" --network "$NETWORK" --network-alias "$GATEWAY_ALIAS" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/ground" "$IMAGE" python3 -m src.mission_recovery.policy_gateway serve --action "$ACTION" --truth-jsonl /ground/gateway-ingress.jsonl --decision-jsonl /ground/gateway-decisions.jsonl >/dev/null
GATEWAY_READY=0; HEX_GATEWAY_PORT="$(printf '%04X' "$GATEWAY_PORT")"; for _ in $(seq 1 40); do if docker exec "$GATEWAY" sh -lc "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {f=1} END {exit f?0:1}' /proc/net/udp" >/dev/null 2>&1; then GATEWAY_READY=1; break; fi; sleep 0.2; done; [[ "$GATEWAY_READY" -eq 1 ]]; POLICY_ENFORCEMENT_NS="$(mono_ns)"

PHASE="EVENT_TREATMENT_FIDELITY"; wait_until_ns "$((EVENT_ACTIVATION_NS + CAPTURE_SECONDS * 1000000000))"; EVENT_SUCCESS_NS="$(mono_ns)"; EVENT_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"; EVENT_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"; EVENT_TRUTH_DELTA=$((EVENT_TRUTH_AFTER-EVENT_TRUTH_BEFORE)); EVENT_VISIBLE_DELTA=$((EVENT_VISIBLE_AFTER-EVENT_VISIBLE_BEFORE)); [[ "$EVENT_TRUTH_DELTA" -eq 1 && "$EVENT_VISIBLE_DELTA" -eq 0 ]]

PHASE="POST_RESPONSE_TELEMETRY_PROBE"; POST_TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"; POST_VISIBLE_BEFORE="$(count_mid "$VISIBLE_JSONL" 0x08E9)"; POST_SEND_NS="$(mono_ns)"; run_e4_adapter "$(basename "$POST_SEND_JSON")" send-data-types; wait_until_ns "$((POST_SEND_NS + CAPTURE_SECONDS * 1000000000))"; POST_PROBE_NS="$(mono_ns)"; POST_TRUTH_AFTER="$(count_mid "$TRUTH_JSONL" 0x08E9)"; POST_VISIBLE_AFTER="$(count_mid "$VISIBLE_JSONL" 0x08E9)"; POST_TRUTH_DELTA=$((POST_TRUTH_AFTER-POST_TRUTH_BEFORE)); POST_VISIBLE_DELTA=$((POST_VISIBLE_AFTER-POST_VISIBLE_BEFORE)); [[ "$POST_TRUTH_DELTA" -eq 1 ]]; [[ "$POST_VISIBLE_DELTA" -eq 0 || "$POST_VISIBLE_DELTA" -eq 1 ]]

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"; NOOP_BEFORE="$(count_noop_marker)"
docker run --rm --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.policy_gateway send --source-id authorized_ground --command-class sample_noop --gateway-host "$GATEWAY_ALIAS" --result-json "/evidence/$(basename "$NOOP_JSON")" >/dev/null
wait_decision_count 1; sleep 0.5; NOOP_AFTER="$(count_noop_marker)"; NOOP_DELTA=$((NOOP_AFTER-NOOP_BEFORE)); [[ "$NOOP_DELTA" -eq 0 || "$NOOP_DELTA" -eq 1 ]]; AUTHORIZED_NOOP_NS="$(mono_ns)"
read -r DECISION_ACTION DECISION_FORWARDED <<EOF_DECISION
$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json,sys
from pathlib import Path
rows=[json.loads(x) for x in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if x.strip()]; assert len(rows)==1; print(rows[0]["action"],str(bool(rows[0]["forwarded"])).lower())
PY
)
EOF_DECISION

PHASE="FROZEN_ANALYSIS_HORIZON"; wait_until_ns "$((EVENT_ACTIVATION_NS + 30 * 1000000000))"; OBSERVATION_COMPLETE_NS="$(mono_ns)"; kill -0 "$PRE_PID" >/dev/null 2>&1; echo "post_event_analysis_horizon_s=30"
PHASE="AUXILIARY_CLEANUP"; docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true
PHASE="NOMINAL_RUNTIME_COMPLETION"; set +e; wait "$PRE_PID"; PRE_RC=$?; set -e; PRE_PID=""; [[ "$PRE_RC" -eq 0 ]] || { tail -120 "$NOMINAL_LOG" >&2 || true; exit 1; }; grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"; test -f "$RUNTIME_MANIFEST"

PHASE="MEASUREMENT_BINDING"
python3 - "$MEASUREMENT_JSON" "$RUN_ID" "$RUN_START_UTC" "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" "$EVENT_SUCCESS_NS" "$POST_PROBE_NS" "$AUTHORIZED_NOOP_NS" "$OBSERVATION_COMPLETE_NS" "$EVENT_TRUTH_DELTA" "$EVENT_VISIBLE_DELTA" "$POST_TRUTH_DELTA" "$POST_VISIBLE_DELTA" "$NOOP_DELTA" "$DECISION_ACTION" "$DECISION_FORWARDED" <<'PY'
import json,sys
(p,r,u,s,a,sel,enf,success,post,noop,complete,et,ev,pt,pv,nd,act,fwd)=sys.argv[1:]
row={"schema":1,"run_id":r,"run_start_utc":u,"run_start_ns":int(s),"event_activation_ns":int(a),"policy_selection_ns":int(sel),"policy_enforcement_ns":int(enf),"event_success_observed_ns":int(success),"post_response_probe_observed_ns":int(post),"authorized_noop_probe_observed_ns":int(noop),"observation_complete_ns":int(complete),"event_truth_high_value_delta":int(et),"event_policy_visible_high_value_delta":int(ev),"post_response_truth_high_value_delta":int(pt),"post_response_policy_visible_high_value_delta":int(pv),"post_response_authorized_noop_attempted":1,"post_response_authorized_noop_marker_delta":int(nd),"gateway_decision_count":1,"immutable_truth_separate":True,"runtime_health_passed":True,"authorized_noop_gateway_action":act,"authorized_noop_gateway_forwarded":fwd=="true"}
from pathlib import Path; Path(p).write_text(json.dumps(row,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver finalize-case --request-json "$REQUEST_JSON" --measurement-json "$MEASUREMENT_JSON" --output-json "$OUTPUT_JSON" >/dev/null

PHASE="CLEANUP_AUDIT"; docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER" >/dev/null 2>&1 || true; docker network rm "$NETWORK" >/dev/null 2>&1 || true
if docker ps -a --format '{{.Names}}' | grep -Fq "$SAFE_ID"; then echo "[ERROR] residual Z03 container remains" >&2; exit 1; fi
if docker network inspect "$NETWORK" >/dev/null 2>&1; then echo "[ERROR] residual Z03 network remains" >&2; exit 1; fi
echo "residual_runtime=none"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"; RESULT="PASS"
