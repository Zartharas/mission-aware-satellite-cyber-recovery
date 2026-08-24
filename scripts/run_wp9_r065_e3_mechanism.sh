#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOMINAL_DURATION_SECONDS=60
CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-r065-rollback.tmp"

[[ "$#" -eq 4 && "$1" == "--request-json" && "$3" == "--output-json" ]] || {
  echo "usage: $0 --request-json <path> --output-json <path>" >&2
  exit 2
}
REQUEST_JSON="$2"
OUTPUT_JSON="$4"
cd "$ROOT"
for command in git python3 docker shasum; do command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] missing command: $command" >&2; exit 1; }; done
REPO_COMMIT="$(git rev-parse HEAD)"
[[ "${WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}" == "1" ]] || { echo "[BLOCKED] R-065 development runtime authorization is not active" >&2; exit 3; }
test -z "$(git status --short)" || { echo "[ERROR] repository worktree must be clean before R-065 E3 runtime" >&2; exit 1; }

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver validate-request --request-json "$REQUEST_JSON" >/dev/null
read -r CASE_ID CELL_ID SEED REQUEST_SHA RUN_ID EFFECTIVE_POLICY SELECTED_ACTION CONTACT EVIDENCE_CONDITION RUNTIME_VARIANT REQUEST_EVIDENCE <<EOF_REQUEST
$(python3 - "$REQUEST_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); f=r["factor_context"]
print(r["case_id"],r["cell_id"],r["development_seed"],r["repo_commit"],r["run_id"],r["actual_effective_policy_id"],r["selected_action"],f["contact_condition_id"],f["evidence_condition_id"],r["runtime_variant"],r["evidence_directory"])
PY
)
EOF_REQUEST
case "$CASE_ID" in Z04|Z05|Z06|Z07|Z08|Z09) ;; *) echo "[BLOCKED] E3 harness supports Z04-Z09 only" >&2; exit 3 ;; esac
[[ "${WP9_R065_AUTHORIZED_CASE:-}" == "$CASE_ID" ]] || { echo "[BLOCKED] R-065 authorization case mismatch" >&2; exit 3; }
[[ "${WP9_R065_AUTHORIZED_SEED:-}" == "$SEED" ]] || { echo "[BLOCKED] R-065 authorization seed mismatch" >&2; exit 3; }
[[ "${WP9_R065_AUTHORIZED_REPO_SHA:-}" == "$REPO_COMMIT" && "$REQUEST_SHA" == "$REPO_COMMIT" ]] || { echo "[BLOCKED] R-065 authorization SHA mismatch" >&2; exit 3; }
EXPECTED_EVIDENCE="results/wp9/development/r065/integration/$RUN_ID"; [[ "$REQUEST_EVIDENCE" == "$EXPECTED_EVIDENCE" ]] || exit 1
EVIDENCE="$ROOT/$EXPECTED_EVIDENCE"; GROUND="$EVIDENCE/immutable-ground"; OBS="$EVIDENCE/runtime-observation"; mkdir -p "$GROUND" "$OBS"
EXPECTED_REQUEST="$GROUND/r065-execution-request.json"; EXPECTED_OUTPUT="$OBS/${CASE_ID:l}-driver-result.json"
[[ "$(cd "$(dirname "$REQUEST_JSON")" && pwd)/$(basename "$REQUEST_JSON")" == "$EXPECTED_REQUEST" ]]
[[ "$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")" == "$EXPECTED_OUTPUT" ]]

SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"; NETWORK="mascr-$SAFE_ID"; CFS="mascr-$SAFE_ID-cfs"; GATEWAY="mascr-$SAFE_ID-r065-e3-gateway"; GATEWAY_ALIAS="r065-e3-gateway"
EVENT_JSON="$GROUND/event-instance.json"; POLICY_JSON="$GROUND/runtime-policy-decision.json"; HANDOFF_JSON="$GROUND/p6-to-p5-handoff.json"; APPROVED="$GROUND/approved-update.pkg"; TAMPERED="$GROUND/tampered-update.pkg"; MANIFEST="$GROUND/approved-manifest.json"; VERIFY_TAMPERED="$GROUND/verify-tampered.json"; ROLLBACK_JSON="$GROUND/rollback-preparation.json"; GROUND_AUTH_JSON="$GROUND/synthetic-ground-authorization.json"; AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"; GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"; GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"; POST_SLOT_JSON="$GROUND/post-response-slot.json"; TERMINAL_VERIFY="$GROUND/terminal-recovery-verification.json"; RUNTIME_HEALTH_JSON="$GROUND/runtime-health.json"; CRITERIA_JSON="$GROUND/recovery-criteria.json"
MEASUREMENT_JSON="$OBS/e3-route-measurement.json"; INVALID_JSON="$EVIDENCE/development-run-invalid.json"; NOMINAL_LOG="$OBS/nominal-runtime.log"; EVENT_WATCH_LOG="$OBS/event-slot-watcher.log"; EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"; EVENT_SLOT_SHA_FILE="$OBS/event-slot-sha256.txt"; NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"; RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"
PRE_PID=""; EVENT_WATCH_PID=""; RESULT="RUN_INVALID"; PHASE="INITIALIZATION"; DEVELOPMENT_SEED_CONSUMED=false
RUN_START_NS=""; RUN_START_UTC=""; EVENT_ACTIVATION_NS=""; EVENT_SUCCESS_NS=""; POLICY_SELECTION_NS=""; POLICY_ENFORCEMENT_NS=""; RESPONSE_BOUNDARY_NS=""; AUTHORIZATION_OBSERVED_NS=""; HANDOFF_NS=""; ROLLBACK_COMPLETE_NS=""; AUTHORIZED_NOOP_NS=""; OBSERVATION_COMPLETE_NS=""
ROLLBACK_VALIDATED=false; SOURCE_VERIFIED=false; GROUND_AUTH_WAITED=false; AUTH_AVAILABLE_AT_BOUNDARY=false; MISSED_CONTACT_WINDOWS=0; TRUSTED_RECOVERY_CONFIRMED=false; TRUSTED_RECOVERY_NS=""; RUNTIME_HEALTH_PASSED=false
mono_ns(){ python3 -c 'import time; print(time.monotonic_ns())'; }
wait_until_ns(){ local d="$1" n; while true; do n="$(mono_ns)"; [[ "$n" -ge "$d" ]] && return 0; sleep 0.05; done; }
count_reset_marker(){ docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: RESET counters command received' || true; }
count_noop_marker(){ docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true; }
decision_count(){ python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); print(0 if not p.exists() else sum(1 for x in p.read_text(encoding="utf-8").splitlines() if x.strip()))
PY
}
wait_decision_count(){ local e="$1" c; for _ in $(seq 1 75); do c="$(decision_count)"; [[ "$c" -eq "$e" ]] && return 0; [[ "$c" -gt "$e" ]] && return 2; sleep 0.2; done; return 1; }
wait_noop_observation(){ local b="$1" n; for _ in $(seq 1 20); do n="$(count_noop_marker)"; [[ "$n" -lt "$b" ]] && return 2; [[ "$n" -gt "$b" ]] && return 0; sleep 0.1; done; return 0; }
send_gateway_command(){ local s="$1" c="$2" f="$3"; docker run --rm --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.policy_gateway send --source-id "$s" --command-class "$c" --gateway-host "$GATEWAY_ALIAS" --result-json "/evidence/$f" >/dev/null; }
send_authorized_noop(){ docker run --rm --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.wp8_recovery_runtime_executor send-authorized-noop --output-json /evidence/authorized-noop-probe.json >/dev/null; }

emit_invalid(){ local rc="$1"; [[ -f "$INVALID_JSON" ]] && return 0; python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$CELL_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" "$DEVELOPMENT_SEED_CONSUMED" <<'PY'
import json,sys
from pathlib import Path
p,r,cid,cell,seed,ph,rc,commit,cons=sys.argv[1:]; Path(p).write_text(json.dumps({"schema":1,"decision_id":"R-065","classification":"WP9_R065_E3_BOUNDED_INTEGRATION_RUN_INVALID","run_id":r,"case_id":cid,"cell_id":cell,"development_seed":int(seed),"development_seed_consumed":cons=="true","failed_phase":ph,"exit_code":int(rc),"repo_commit":commit,"development_validation_only":True,"invalid_attempt_retained":True,"campaign_seed_consumed":False,"campaign_data_generated":False,"final_campaign_execution_authorized":False,"automatic_retry_performed":False,"automatic_next_case_performed":False},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
}
cleanup(){ local rc=$?; set +e; docker rm -f "$GATEWAY" >/dev/null 2>&1 || true; if docker inspect "$CFS" >/dev/null 2>&1; then docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING" >/dev/null 2>&1 || true; fi; [[ -n "$EVENT_WATCH_PID" ]] && kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1 && { kill -TERM "$EVENT_WATCH_PID" >/dev/null 2>&1 || true; wait "$EVENT_WATCH_PID" >/dev/null 2>&1 || true; }; [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1 && { kill -TERM "$PRE_PID" >/dev/null 2>&1 || true; wait "$PRE_PID" >/dev/null 2>&1 || true; }; docker network rm "$NETWORK" >/dev/null 2>&1 || true; if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then echo "WP9_R065_E3_MECHANISM_RUNTIME=PASS"; echo "case_id=$CASE_ID"; echo "cell_id=$CELL_ID"; echo "development_seed=$SEED"; echo "development_seed_consumed=true"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "evidence_directory=$EVIDENCE"; else emit_invalid "$rc" || true; echo "WP9_R065_E3_MECHANISM_RUNTIME=FAIL" >&2; echo "case_id=$CASE_ID" >&2; echo "failed_phase=$PHASE" >&2; echo "automatic_retry_allowed=false" >&2; echo "automatic_next_case_allowed=false" >&2; echo "campaign_seed_consumed=false" >&2; echo "campaign_data_generated=false" >&2; echo "evidence_directory=$EVIDENCE" >&2; fi; exit "$rc"; }
trap cleanup EXIT; trap 'exit 130' INT TERM

: > "$GATEWAY_TRUTH"; : > "$GATEWAY_DECISIONS"
PHASE="PREFLIGHT"; docker info >/dev/null 2>&1 || exit 1; docker image inspect "$IMAGE" >/dev/null 2>&1 || exit 1
echo "r065_e3_runtime_authorization=PASS"; echo "authorized_case=$CASE_ID"; echo "authorized_seed=$SEED"; echo "authorized_repo_sha=$REPO_COMMIT"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"

PHASE="ARTIFACT_MATERIALIZATION"
python3 - "$REQUEST_JSON" "$EVENT_JSON" "$APPROVED" "$TAMPERED" "$MANIFEST" "$VERIFY_TAMPERED" <<'PY'
import json,sys
from pathlib import Path
from src.mission_recovery.update_artifacts import build_approved_update,build_tampered_update,build_manifest,sha256_hex,verify_candidate
req,event_path,approved_path,tampered_path,manifest_path,verify_path=sys.argv[1:]; r=json.loads(Path(req).read_text(encoding="utf-8")); approved=build_approved_update(); tampered=build_tampered_update(); manifest=build_manifest(); verify=verify_candidate(tampered,manifest)
assert sha256_hex(approved)=="42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"; assert sha256_hex(tampered)=="ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"; assert verify["accepted"] is False
Path(event_path).write_text(json.dumps(r["event_instance"],sort_keys=True,indent=2)+"\n",encoding="utf-8"); Path(approved_path).write_bytes(approved); Path(tampered_path).write_bytes(tampered); Path(manifest_path).write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8"); Path(verify_path).write_text(json.dumps(verify,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"; TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

PHASE="NOMINAL_RUNTIME_LAUNCH"; RUN_ID="$RUN_ID" DURATION_SECONDS="$NOMINAL_DURATION_SECONDS" STARTUP_GRACE_SECONDS=20 bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 & PRE_PID=$!
PHASE="CFS_READINESS"; CFS_READY=0; for _ in $(seq 1 180); do kill -0 "$PRE_PID" >/dev/null 2>&1 || break; [[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && { CFS_READY=1; break; }; sleep 1; done; [[ "$CFS_READY" -eq 1 ]] || { tail -120 "$NOMINAL_LOG" >&2 || true; exit 1; }
CI_READY=0; for _ in $(seq 1 90); do kill -0 "$PRE_PID" >/dev/null 2>&1 || break; if docker exec "$CFS" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'" >/dev/null 2>&1; then CI_READY=1; break; fi; sleep 1; done; [[ "$CI_READY" -eq 1 ]]; [[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]; [[ -z "$(docker port "$CFS")" ]]; docker exec "$CFS" test -d "$CF_BACKING_DIR"; docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"; DEVELOPMENT_SEED_CONSUMED=true
echo "nominal_runtime_ready=PASS"; echo "nominal_isolation=PASS"; RUN_START_NS="$(mono_ns)"; RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PHASE="EVENT_OBSERVER_PREPOSITION"; : > "$EVENT_WATCH_LOG"
(
 set +e
 docker exec "$CFS" sh -lc 'slot="$1"; expected="$2"; echo R065_EVENT_SLOT_WATCHER_READY; i=0; while [ "$i" -lt 3000 ]; do if [ -f "$slot" ]; then observed="$(sha256sum "$slot" 2>/dev/null | awk "{print \$1}")"; [ "$observed" = "$expected" ] && { echo "R065_EVENT_SLOT_SHA=$observed"; exit 0; }; [ -n "$observed" ] && { echo "R065_EVENT_SLOT_UNEXPECTED_SHA=$observed" >&2; exit 2; }; fi; i=$((i+1)); sleep 0.01; done; exit 1' sh "$STAGE_BACKING" "$TAMPERED_SHA" >"$EVENT_WATCH_LOG" 2>&1
 wrc=$?; if [[ "$wrc" -eq 0 ]]; then observed="$(awk -F= '/^R065_EVENT_SLOT_SHA=/{print $2;exit}' "$EVENT_WATCH_LOG")"; [[ "$observed" == "$TAMPERED_SHA" ]] || exit 3; mono_ns > "$EVENT_SUCCESS_NS_FILE"; printf '%s\n' "$observed" > "$EVENT_SLOT_SHA_FILE"; fi; exit "$wrc"
) & EVENT_WATCH_PID=$!
READY=0; for _ in $(seq 1 200); do grep -Fq R065_EVENT_SLOT_WATCHER_READY "$EVENT_WATCH_LOG" 2>/dev/null && { READY=1; break; }; kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1 || break; sleep 0.01; done; [[ "$READY" -eq 1 ]]

PHASE="EVENT_ACTIVATION"; EVENT_ACTIVATION_NS="$(mono_ns)"; docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"; echo "e3_modeled_activation=PASS"
PHASE="POLICY_SELECTION"; POLICY_SELECTION_NS="$(mono_ns)"
python3 - "$REQUEST_JSON" "$POLICY_JSON" <<'PY'
import json,sys
from pathlib import Path
from src.mission_recovery.wp9_static_contracts import evaluate_wp9_policy
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); f=r["factor_context"]; d=evaluate_wp9_policy(f["policy_id"],r["event_instance"]); assert d["delegated_policy_id"]==r["actual_effective_policy_id"]; assert d["selected_action"]==r["selected_action"]; assert d["oracle_ground_truth_read"] is False; Path(sys.argv[2]).write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
echo "actual_effective_policy_id=$EFFECTIVE_POLICY"; echo "selected_action=$SELECTED_ACTION"; echo "policy_trigger_uses_ground_truth=false"; echo "policy_selection_not_gated_on_event_success=true"
PHASE="EVENT_SUCCESS_CONFIRMATION"; set +e; wait "$EVENT_WATCH_PID"; WATCH_RC=$?; set -e; EVENT_WATCH_PID=""; [[ "$WATCH_RC" -eq 0 ]]; EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"; [[ "$(cat "$EVENT_SLOT_SHA_FILE")" == "$TAMPERED_SHA" ]]

PHASE="POLICY_ENFORCEMENT"
if [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then
 docker run -d --platform linux/amd64 --name "$GATEWAY" --hostname "$GATEWAY_ALIAS" --network "$NETWORK" --network-alias "$GATEWAY_ALIAS" --env PYTHONPATH=/research --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" python3 -m src.mission_recovery.policy_gateway serve --action "$SELECTED_ACTION" --isolated-source modeled_attacker --truth-jsonl /evidence/gateway-ingress.jsonl --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null
 READY=0; HEX="$(printf '%04X' 19091)"; for _ in $(seq 1 75); do if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && docker exec "$GATEWAY" sh -lc "awk '\$2 ~ /:${HEX}$/ {f=1} END {exit f?0:1}' /proc/net/udp" >/dev/null 2>&1; then READY=1; break; fi; sleep 0.2; done; [[ "$READY" -eq 1 ]]; POLICY_ENFORCEMENT_NS="$(mono_ns)"; RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"
elif [[ "$SELECTED_ACTION" == "REQUEST_VERIFIED_ROLLBACK" ]]; then
 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor prepare-rollback --event-json "$EVENT_JSON" --policy-json "$POLICY_JSON" --output-json "$ROLLBACK_JSON" >/dev/null
 POLICY_ENFORCEMENT_NS="$(mono_ns)"; RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"
 read -r ROLLBACK_VALIDATED SOURCE_VERIFIED <<EOF_R
$(python3 - "$ROLLBACK_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text()); print(str(r["rollback_request_validated"]).lower(),str(r["replacement_source_verified"]).lower())
PY
)
EOF_R
 [[ "$ROLLBACK_VALIDATED" == true && "$SOURCE_VERIFIED" == true ]]; docker cp "$APPROVED" "$CFS:$TEMP_BACKING"; docker exec "$CFS" sh -lc "mv '$TEMP_BACKING' '$STAGE_BACKING'"; ROLLBACK_COMPLETE_NS="$(mono_ns)"
elif [[ "$SELECTED_ACTION" == "WAIT_FOR_GROUND_AUTHORIZATION" ]]; then
 POLICY_ENFORCEMENT_NS="$(mono_ns)"; RESPONSE_BOUNDARY_NS="$POLICY_ENFORCEMENT_NS"; GROUND_AUTH_WAITED=true
 if [[ "$CONTACT" == C1 ]]; then AUTH_AVAILABLE_AT_BOUNDARY=false; MISSED_CONTACT_WINDOWS=1; wait_until_ns "$((RESPONSE_BOUNDARY_NS + 10 * 1000000000))"; else [[ "$CONTACT" == C0 ]]; AUTH_AVAILABLE_AT_BOUNDARY=true; MISSED_CONTACT_WINDOWS=0; fi
 AUTHORIZATION_OBSERVED_NS="$(mono_ns)"
 python3 - "$GROUND_AUTH_JSON" "$CONTACT" "$AUTH_AVAILABLE_AT_BOUNDARY" "$MISSED_CONTACT_WINDOWS" "$AUTHORIZATION_OBSERVED_NS" <<'PY'
import json,sys
from pathlib import Path
p,c,a,m,n=sys.argv[1:]; Path(p).write_text(json.dumps({"schema":1,"decision_id":"R-065","source":"synthetic_ground_authorization_schedule","contact_condition_id":c,"available_at_response_boundary":a=="true","missed_contact_windows":int(m),"authorization_current":True,"authorization_observed_ns":int(n),"real_ground_contact":False,"real_human_operator":False},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
 python3 - "$REQUEST_JSON" "$HANDOFF_JSON" <<'PY'
import json,sys
from pathlib import Path
from src.mission_recovery.wp9_static_contracts import evaluate_wp9_policy
r=json.loads(Path(sys.argv[1]).read_text()); d=evaluate_wp9_policy("P5",r["event_instance"]); assert d["delegated_policy_id"]=="P5" and d["selected_action"]=="REQUEST_VERIFIED_ROLLBACK" and d["oracle_ground_truth_read"] is False; Path(sys.argv[2]).write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
 HANDOFF_NS="$(mono_ns)"; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor prepare-rollback --event-json "$EVENT_JSON" --policy-json "$HANDOFF_JSON" --output-json "$ROLLBACK_JSON" >/dev/null
 read -r ROLLBACK_VALIDATED SOURCE_VERIFIED <<EOF_R
$(python3 - "$ROLLBACK_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text()); print(str(r["rollback_request_validated"]).lower(),str(r["replacement_source_verified"]).lower())
PY
)
EOF_R
 [[ "$ROLLBACK_VALIDATED" == true && "$SOURCE_VERIFIED" == true ]]; docker cp "$APPROVED" "$CFS:$TEMP_BACKING"; docker exec "$CFS" sh -lc "mv '$TEMP_BACKING' '$STAGE_BACKING'"; ROLLBACK_COMPLETE_NS="$(mono_ns)"
else echo "[ERROR] unsupported R-065 E3 action: $SELECTED_ACTION" >&2; exit 1; fi
[[ "$EVENT_SUCCESS_NS" -le "$POLICY_ENFORCEMENT_NS" ]]

PHASE="POST_RESPONSE_PROBES"; MATCHED_ATTACKER_PROBES=0; ATTACKER_RESET_DELTA=0; GATEWAY_DECISION_COUNT=0; ATTACKER_FORWARDED_COUNT=0; AUTHORIZED_GATEWAY_FORWARDED=false
if [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then RESET_BEFORE="$(count_reset_marker)"; NOOP_BEFORE="$(count_noop_marker)"; send_gateway_command modeled_attacker sample_reset_counters attacker-reset-probe-1.json; send_gateway_command modeled_attacker sample_reset_counters attacker-reset-probe-2.json; send_gateway_command authorized_ground sample_noop authorized-noop-probe.json; wait_decision_count 3; sleep 0.8; RESET_AFTER="$(count_reset_marker)"; NOOP_AFTER="$(count_noop_marker)"; MATCHED_ATTACKER_PROBES=2; ATTACKER_RESET_DELTA=$((RESET_AFTER-RESET_BEFORE)); AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER-NOOP_BEFORE)); AUTHORIZED_NOOP_NS="$(mono_ns)"; read -r GATEWAY_DECISION_COUNT ATTACKER_FORWARDED_COUNT AUTHORIZED_GATEWAY_FORWARDED <<EOF_G
$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import json,sys
from pathlib import Path
rows=[json.loads(x) for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]; auth=[x for x in rows if x.get("source_id")=="authorized_ground"]; print(len(rows),sum(1 for x in rows if x.get("source_id")=="modeled_attacker" and x.get("forwarded") is True),str(len(auth)==1 and auth[0].get("forwarded") is True).lower())
PY
)
EOF_G
else NOOP_BEFORE="$(count_noop_marker)"; send_authorized_noop; wait_noop_observation "$NOOP_BEFORE"; NOOP_AFTER="$(count_noop_marker)"; AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER-NOOP_BEFORE)); AUTHORIZED_NOOP_NS="$(mono_ns)"; fi

PHASE="POST_RESPONSE_SLOT_OBSERVATION"; POST_SLOT_SHA="$(docker exec "$CFS" sh -lc "sha256sum '$STAGE_BACKING' | awk '{print \$1}'")"; POST_SLOT_NS="$(mono_ns)"; docker exec "$CFS" test ! -e "$TEMP_BACKING"; TEMP_ABSENT=true
python3 - "$POST_SLOT_JSON" "$POST_SLOT_SHA" "$POST_SLOT_NS" <<'PY'
import json,sys
from pathlib import Path
p,s,n=sys.argv[1:]; Path(p).write_text(json.dumps({"sha256":s,"observed_ns":int(n)},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
PHASE="RUNTIME_HEALTH"; [[ "$(docker inspect "$CFS" --format '{{.State.Status}}')" == running ]]; docker exec "$CFS" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'"; [[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]; [[ -z "$(docker port "$CFS")" ]]; RUNTIME_HEALTH_NS="$(mono_ns)"; RUNTIME_HEALTH_PASSED=true
python3 - "$RUNTIME_HEALTH_JSON" "$RUNTIME_HEALTH_NS" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"schema":1,"cfs_running":True,"ci_lab_udp_5012_observed":True,"internal_network":True,"published_ports_absent":True,"runtime_health_passed":True,"observed_ns":int(sys.argv[2])},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY

if [[ "$EFFECTIVE_POLICY" == P2 ]]; then [[ "$POST_SLOT_SHA" == "$TAMPERED_SHA" ]]; wait_until_ns "$((EVENT_ACTIVATION_NS + 30 * 1000000000))"; OBSERVATION_COMPLETE_NS="$(mono_ns)"; TRUSTED_RECOVERY_CONFIRMED=false
else
 [[ "$POST_SLOT_SHA" == "$APPROVED_SHA" ]]; PHASE="TERMINAL_RECOVERY_VERIFICATION"; docker cp "$CFS:$STAGE_BACKING" "$OBS/terminal-recovered-candidate.pkg" >/dev/null
 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - "$OBS/terminal-recovered-candidate.pkg" "$MANIFEST" "$TAMPERED_SHA" "$TERMINAL_VERIFY" <<'PY'
import json,sys
from pathlib import Path
from src.mission_recovery.trusted_recovery import verify_terminal_recovery
r=verify_terminal_recovery(terminal_candidate=Path(sys.argv[1]).read_bytes(),manifest=json.loads(Path(sys.argv[2]).read_text()),rejected_candidate_sha256=sys.argv[3]); assert r["trusted_recovery_verified"] is True and r["terminal_matches_approved"] is True and r["terminal_differs_from_rejected"] is True and r["reasons"]==[]; Path(sys.argv[4]).write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
 PHASE="RECOVERY_CRITERIA"; CRITERIA_NS="$(mono_ns)"
 python3 - "$CRITERIA_JSON" "$POST_SLOT_JSON" "$ROLLBACK_JSON" "$AUTHORIZED_JSON" "$RUNTIME_HEALTH_JSON" "$MANIFEST" "$TERMINAL_VERIFY" "$AUTHORIZED_NOOP_DELTA" "$CRITERIA_NS" <<'PY'
import json,sys
from pathlib import Path
out,slot,rollback,noop,health,manifest,terminal,delta,ns=sys.argv[1:]; delta=int(delta); refs={"approved_version":slot,"integrity_measurement_valid":terminal,"authorization_valid":rollback,"measured_state_current":slot,"authorized_command_path_restored":noop,"ground_spacecraft_state_agreed":slot,"required_telemetry_restored":health,"health_checks_passed":health,"no_residual_unauthorized_state":slot,"recovery_manifest_complete":manifest}; sat={k:True for k in refs}; sat["authorized_command_path_restored"]=delta==1; rows={k:{"available_current":True,"criterion_satisfied":bool(sat[k]),"evidence_ref":str(Path(v)),"observed_ns":int(ns)} for k,v in refs.items()}; Path(out).write_text(json.dumps(rows,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
 ALL_CRITERIA="$(python3 - "$CRITERIA_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text()); print(str(all(x["available_current"] and x["criterion_satisfied"] for x in r.values())).lower())
PY
)"
 if [[ "$ALL_CRITERIA" == true ]]; then TRUSTED_RECOVERY_CONFIRMED=true; TRUSTED_RECOVERY_NS="$(mono_ns)"; OBSERVATION_COMPLETE_NS="$(mono_ns)"; else TRUSTED_RECOVERY_CONFIRMED=false; wait_until_ns "$((EVENT_ACTIVATION_NS + 30 * 1000000000))"; OBSERVATION_COMPLETE_NS="$(mono_ns)"; fi
fi

PHASE="MEASUREMENT_BINDING"
python3 - "$MEASUREMENT_JSON" "$CRITERIA_JSON" "$RUN_ID" "$RUN_START_UTC" "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" "$RESPONSE_BOUNDARY_NS" "$OBSERVATION_COMPLETE_NS" "$POST_SLOT_SHA" "$RUNTIME_HEALTH_PASSED" "$AUTHORIZED_NOOP_DELTA" "$EFFECTIVE_POLICY" "$MATCHED_ATTACKER_PROBES" "$GATEWAY_DECISION_COUNT" "$ATTACKER_FORWARDED_COUNT" "$AUTHORIZED_GATEWAY_FORWARDED" "$ATTACKER_RESET_DELTA" "$ROLLBACK_VALIDATED" "$SOURCE_VERIFIED" "$TEMP_ABSENT" "${ROLLBACK_COMPLETE_NS:-0}" "$TRUSTED_RECOVERY_CONFIRMED" "${TRUSTED_RECOVERY_NS:-0}" "$GROUND_AUTH_WAITED" "${AUTHORIZATION_OBSERVED_NS:-0}" "${HANDOFF_NS:-0}" "$AUTH_AVAILABLE_AT_BOUNDARY" "$MISSED_CONTACT_WINDOWS" <<'PY'
import json,sys
from pathlib import Path
(p,criteria,run_id,utc,start,act,success,sel,enf,bound,complete,slot,health,noop,effective,attackers,decisions,afwd,gfwd,adelta,rb,src,temp,rbns,trusted,tns,gwait,authns,handoff,available,missed)=sys.argv[1:]; b=lambda x:x.lower()=="true"
row={"schema":1,"run_id":run_id,"run_start_utc":utc,"run_start_ns":int(start),"event_activation_ns":int(act),"event_success_observed_ns":int(success),"policy_selection_ns":int(sel),"policy_enforcement_ns":int(enf),"response_boundary_ns":int(bound),"observation_complete_ns":int(complete),"event_activation_observed":True,"event_slot_sha256":"ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d","runtime_health_passed":b(health),"policy_selection_not_gated_on_event_success":True,"authorized_noop_attempted":1,"authorized_noop_marker_delta":int(noop),"post_response_slot_sha256":slot,"ground_authorization_waited":b(gwait)}
if effective=="P2": row.update({"update_containment_observed":False,"matched_attacker_probe_count":int(attackers),"gateway_decision_count":int(decisions),"attacker_gateway_forwarded_count":int(afwd),"authorized_noop_gateway_forwarded":b(gfwd),"gateway_action":"RESTRICT_HIGH_RISK_COMMANDS","observed_post_enforcement_attacker_reset_marker_delta":int(adelta)})
else:
 row.update({"rollback_request_validated":b(rb),"approved_replacement_source_verified":b(src),"temporary_recovery_state_absent":b(temp),"rollback_complete_ns":int(rbns),"trusted_recovery_confirmed":b(trusted),"recovery_criteria":json.loads(Path(criteria).read_text())})
 if b(trusted): row["trusted_recovery_observed_ns"]=int(tns)
 if effective=="P6": row.update({"ground_authorization_source":"synthetic_ground_authorization_schedule","ground_authorization_current":True,"authorization_observed_ns":int(authns),"handoff_ns":int(handoff),"authorization_available_at_response_boundary":b(available),"missed_contact_windows_observed":int(missed),"post_authorization_delegate":"P5","post_authorization_action":"REQUEST_VERIFIED_ROLLBACK"})
Path(p).write_text(json.dumps(row,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver finalize-case --request-json "$REQUEST_JSON" --measurement-json "$MEASUREMENT_JSON" --output-json "$OUTPUT_JSON" >/dev/null

PHASE="AUXILIARY_CLEANUP"; docker rm -f "$GATEWAY" >/dev/null 2>&1 || true; docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"; PHASE="NOMINAL_RUNTIME_COMPLETION"; set +e; wait "$PRE_PID"; PRE_RC=$?; set -e; PRE_PID=""; [[ "$PRE_RC" -eq 0 ]] || { tail -160 "$NOMINAL_LOG" >&2 || true; exit 1; }; grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"; test -f "$RUNTIME_MANIFEST"
PHASE="CLEANUP_AUDIT"; docker rm -f "$GATEWAY" "$CFS" >/dev/null 2>&1 || true; docker network rm "$NETWORK" >/dev/null 2>&1 || true; if docker ps -a --format '{{.Names}}' | grep -Fq "$SAFE_ID"; then echo "[ERROR] residual R-065 E3 container remains" >&2; exit 1; fi; if docker network inspect "$NETWORK" >/dev/null 2>&1; then echo "[ERROR] residual R-065 E3 network remains" >&2; exit 1; fi
echo "residual_runtime=none"; echo "automatic_retry_allowed=false"; echo "automatic_next_case_allowed=false"; echo "campaign_seed_consumed=false"; echo "campaign_data_generated=false"; RESULT="PASS"
