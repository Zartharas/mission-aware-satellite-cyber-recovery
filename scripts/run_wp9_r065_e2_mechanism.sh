#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CASE_ID="Z02"
CELL_ID="A21"
SEED="9942"
GATEWAY_PORT=19091
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
  echo "[BLOCKED] R-065 development runtime authorization is not active" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_CASE:-}" == "$CASE_ID" ]] || {
  echo "[BLOCKED] R-065 authorization is not for Z02" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_SEED:-}" == "$SEED" ]] || {
  echo "[BLOCKED] R-065 authorization is not for development seed 9942" >&2
  exit 3
}
[[ "${WP9_R065_AUTHORIZED_REPO_SHA:-}" == "$REPO_COMMIT" ]] || {
  echo "[BLOCKED] R-065 authorization SHA does not match current HEAD" >&2
  exit 3
}
test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before R-065 Z02 runtime" >&2
  exit 1
}

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver \
  validate-request --request-json "$REQUEST_JSON" >/dev/null

read -r REQUEST_CASE REQUEST_CELL REQUEST_SEED REQUEST_SHA RUN_ID ACTION REQUEST_EVIDENCE <<EOF_REQUEST
$(python3 - "$REQUEST_JSON" <<'PY'
import json, sys
from pathlib import Path
row=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(row["case_id"], row["cell_id"], row["development_seed"], row["repo_commit"], row["run_id"], row["selected_action"], row["evidence_directory"])
PY
)
EOF_REQUEST
[[ "$REQUEST_CASE" == "$CASE_ID" ]]
[[ "$REQUEST_CELL" == "$CELL_ID" ]]
[[ "$REQUEST_SEED" == "$SEED" ]]
[[ "$REQUEST_SHA" == "$REPO_COMMIT" ]]
[[ "$ACTION" == "ISOLATE_MODELED_SOURCE" ]]

EXPECTED_EVIDENCE="results/wp9/development/r065/integration/$RUN_ID"
[[ "$REQUEST_EVIDENCE" == "$EXPECTED_EVIDENCE" ]] || {
  echo "[ERROR] Z02 evidence directory escaped R-065 development namespace" >&2
  exit 1
}
EVIDENCE="$ROOT/$EXPECTED_EVIDENCE"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
mkdir -p "$GROUND" "$OBS"
EXPECTED_REQUEST="$GROUND/r065-execution-request.json"
EXPECTED_OUTPUT="$OBS/z02-driver-result.json"
[[ "$(cd "$(dirname "$REQUEST_JSON")" && pwd)/$(basename "$REQUEST_JSON")" == "$EXPECTED_REQUEST" ]] || {
  echo "[ERROR] Z02 request path is not retained evidence path" >&2
  exit 1
}
[[ "$(cd "$(dirname "$OUTPUT_JSON")" && pwd)/$(basename "$OUTPUT_JSON")" == "$EXPECTED_OUTPUT" ]] || {
  echo "[ERROR] Z02 output path is not retained evidence path" >&2
  exit 1
}

SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-r065-e2-gateway"
GATEWAY_ALIAS="r065-e2-gateway"

SETUP_JSON="$GROUND/setup-reset.json"
INTERVENING_JSON="$GROUND/intervening-authorized-noop.json"
REPLAY_JSON="$GROUND/replay-send.json"
AUTHORIZED_JSON="$GROUND/post-response-authorized-noop.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
MEASUREMENT_JSON="$OBS/e2-route-measurement.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"
EFFECT_NS_FILE="$OBS/replay-effect-observed-ns.txt"

PRE_PID=""
WATCH_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
DEVELOPMENT_SEED_CONSUMED=false
RUN_START_NS=""
RUN_START_UTC=""
EVENT_ACTIVATION_NS=""
POLICY_ENFORCEMENT_NS=""
REPLAY_DECISION_NS=""
AUTHORIZED_NOOP_NS=""
OBSERVATION_COMPLETE_NS=""

mono_ns() { python3 -c 'import time; print(time.monotonic_ns())'; }
count_reset_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: RESET counters command received' || true; }
count_noop_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true; }

wait_exact_delta() {
  local counter="$1" before="$2" delta="$3" label="$4" now expected
  expected=$((before + delta))
  for _ in $(seq 1 50); do
    now="$("$counter")"
    [[ "$now" -eq "$expected" ]] && { printf '%s\n' "$now"; return 0; }
    [[ "$now" -gt "$expected" ]] && { echo "[ERROR] $label exceeded expected count" >&2; return 2; }
    sleep 0.1
  done
  echo "[ERROR] $label timeout" >&2
  return 1
}

decision_count() {
  python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1])
print(0 if not p.exists() else sum(1 for x in p.read_text(encoding="utf-8").splitlines() if x.strip()))
PY
}
wait_decision_count() {
  local expected="$1" count
  for _ in $(seq 1 50); do
    count="$(decision_count)"
    [[ "$count" -eq "$expected" ]] && return 0
    [[ "$count" -gt "$expected" ]] && return 2
    sleep 0.1
  done
  return 1
}

emit_invalid() {
  local rc="$1"
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$PHASE" "$rc" "$REPO_COMMIT" "$DEVELOPMENT_SEED_CONSUMED" <<'PY'
import json, sys
from pathlib import Path
path, run_id, phase, rc, commit, consumed = sys.argv[1:]
Path(path).write_text(json.dumps({
 "schema":1,"decision_id":"R-065","classification":"WP9_R065_Z02_BOUNDED_INTEGRATION_RUN_INVALID",
 "run_id":run_id,"case_id":"Z02","cell_id":"A21","development_seed":9942,
 "development_seed_consumed":consumed=="true","failed_phase":phase,"exit_code":int(rc),"repo_commit":commit,
 "development_validation_only":True,"invalid_attempt_retained":True,"campaign_seed_consumed":False,
 "campaign_data_generated":False,"final_campaign_execution_authorized":False,
 "automatic_retry_performed":False,"automatic_next_case_performed":False
}, sort_keys=True, indent=2)+"\n", encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  [[ -n "$WATCH_PID" ]] && kill -0 "$WATCH_PID" >/dev/null 2>&1 && { kill -TERM "$WATCH_PID" >/dev/null 2>&1 || true; wait "$WATCH_PID" >/dev/null 2>&1 || true; }
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1 && { kill -TERM "$PRE_PID" >/dev/null 2>&1 || true; wait "$PRE_PID" >/dev/null 2>&1 || true; }
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R065_Z02_E2_MECHANISM_RUNTIME=PASS"
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
    echo "WP9_R065_Z02_E2_MECHANISM_RUNTIME=FAIL" >&2
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

: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"
rm -f "$EFFECT_NS_FILE"
PHASE="PREFLIGHT"
docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not reachable" >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] pinned NOS3 image unavailable" >&2; exit 1; }
echo "r065_z02_runtime_authorization=PASS"
echo "authorized_case=$CASE_ID"
echo "authorized_seed=$SEED"
echo "authorized_repo_sha=$REPO_COMMIT"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" DURATION_SECONDS="$NOMINAL_DURATION_SECONDS" STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

PHASE="CFS_READINESS"
CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  [[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && { CFS_READY=1; break; }
  sleep 1
done
[[ "$CFS_READY" -eq 1 ]] || { echo "[ERROR] nominal cFS container not observed" >&2; tail -120 "$NOMINAL_LOG" >&2 || true; exit 1; }
CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {f=1} END {exit f?0:1}'" >/dev/null 2>&1; then CI_READY=1; break; fi
  sleep 1
done
[[ "$CI_READY" -eq 1 ]]
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
DEVELOPMENT_SEED_CONSUMED=true
echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

PHASE="SETUP_QUIET_BASELINE"
RESET_BEFORE_SETUP="$(count_reset_marker)"
sleep 2
[[ "$(count_reset_marker)" -eq "$RESET_BEFORE_SETUP" ]]

PHASE="AUTHORIZED_SETUP_RESET"
docker run --rm -i --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
  python3 - /evidence/"$(basename "$SETUP_JSON")" <<'PY'
import hashlib,json,socket,sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
packet=build_sample_noargs_packet("sample_reset_counters")
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sent=s.sendto(packet,("nos-fsw",5012)); s.close(); assert sent==len(packet)
Path(sys.argv[1]).write_text(json.dumps({"role":"previously_accepted_authorized_command_before_treatment","source_id":"authorized_ground","command_class":"sample_reset_counters","target":"nos-fsw:5012","datagrams_sent":1,"bytes_sent":sent,"packet_hex":packet.hex(),"packet_sha256":hashlib.sha256(packet).hexdigest()},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
RESET_AFTER_SETUP="$(wait_exact_delta count_reset_marker "$RESET_BEFORE_SETUP" 1 setup_reset)"

PHASE="INTERVENING_AUTHORIZED_NOOP"
NOOP_BEFORE_INTERVENING="$(count_noop_marker)"
docker run --rm -i --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
  python3 - /evidence/"$(basename "$INTERVENING_JSON")" <<'PY'
import hashlib,json,socket,sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
packet=build_sample_noargs_packet("sample_noop")
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sent=s.sendto(packet,("nos-fsw",5012)); s.close(); assert sent==len(packet)
Path(sys.argv[1]).write_text(json.dumps({"role":"intervening_authorized_probe_before_treatment","source_id":"authorized_ground","command_class":"sample_noop","target":"nos-fsw:5012","datagrams_sent":1,"bytes_sent":sent,"packet_hex":packet.hex(),"packet_sha256":hashlib.sha256(packet).hexdigest()},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
NOOP_AFTER_INTERVENING="$(wait_exact_delta count_noop_marker "$NOOP_BEFORE_INTERVENING" 1 intervening_noop)"
[[ "$(count_reset_marker)" -eq "$RESET_AFTER_SETUP" ]]

PHASE="EVENT_ACTIVATION_AND_POLICY_ENFORCEMENT"
RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EVENT_ACTIVATION_NS="$(mono_ns)"
docker run -d --platform linux/amd64 --name "$GATEWAY" --hostname "$GATEWAY_ALIAS" \
  --network "$NETWORK" --network-alias "$GATEWAY_ALIAS" --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway serve --action "$ACTION" --isolated-source modeled_attacker \
  --truth-jsonl /evidence/gateway-ingress.jsonl --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null
GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' "$GATEWAY_PORT")"
for _ in $(seq 1 50); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && docker exec "$GATEWAY" sh -lc "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {f=1} END {exit f?0:1}' /proc/net/udp" >/dev/null 2>&1; then GATEWAY_READY=1; break; fi
  sleep 0.1
done
[[ "$GATEWAY_READY" -eq 1 ]]
POLICY_ENFORCEMENT_NS="$(mono_ns)"
echo "actual_effective_policy_id=P1"
echo "selected_action=$ACTION"
echo "policy_trigger_uses_ground_truth=false"

PHASE="BYTE_IDENTICAL_REPLAY"
RESET_BEFORE_REPLAY="$(count_reset_marker)"
(
  for _ in $(seq 1 300); do
    now="$(count_reset_marker)"
    [[ "$now" -eq $((RESET_BEFORE_REPLAY + 1)) ]] && { mono_ns > "$EFFECT_NS_FILE"; exit 0; }
    [[ "$now" -gt $((RESET_BEFORE_REPLAY + 1)) ]] && exit 2
    sleep 0.1
  done
  exit 0
) &
WATCH_PID=$!
docker run --rm -i --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
  python3 - "$GATEWAY_ALIAS" /evidence/"$(basename "$REPLAY_JSON")" <<'PY'
import hashlib,json,socket,sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
host,out=sys.argv[1:]; packet=build_sample_noargs_packet("sample_reset_counters")
envelope={"schema":1,"event_id":"E2","probe_variant":"wp9_r065_byte_identical_replay","role":"byte_identical_stale_replay_after_treatment","source_id":"modeled_attacker","command_class":"sample_reset_counters","declared_risk_class":"high_surrogate","packet_hex":packet.hex(),"packet_sha256":hashlib.sha256(packet).hexdigest()}
encoded=(json.dumps(envelope,sort_keys=True,separators=(",",":"))+"\n").encode(); s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sent=s.sendto(encoded,(host,19091)); s.close(); assert sent==len(encoded)
record=dict(envelope); record.update({"gateway":f"{host}:19091","datagrams_sent":1,"envelope_bytes_sent":sent}); Path(out).write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
wait_decision_count 1
REPLAY_DECISION_NS="$(mono_ns)"

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"
NOOP_BEFORE_RESPONSE="$(count_noop_marker)"
docker run --rm --platform linux/amd64 --network "$NETWORK" --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" --mount "type=bind,source=$GROUND,target=/evidence" "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway send --source-id authorized_ground --command-class sample_noop \
  --gateway-host "$GATEWAY_ALIAS" --result-json /evidence/"$(basename "$AUTHORIZED_JSON")" >/dev/null
wait_decision_count 2
sleep 1
NOOP_AFTER_RESPONSE="$(count_noop_marker)"
AUTHORIZED_NOOP_NS="$(mono_ns)"

PHASE="FROZEN_ANALYSIS_HORIZON"
python3 - "$EVENT_ACTIVATION_NS" <<'PY'
import sys,time
target=int(sys.argv[1])+30_000_000_000
remaining=(target-time.monotonic_ns())/1_000_000_000
if remaining>0: time.sleep(remaining)
PY
OBSERVATION_COMPLETE_NS="$(mono_ns)"
set +e; wait "$WATCH_PID"; WATCH_RC=$?; set -e; WATCH_PID=""
[[ "$WATCH_RC" -eq 0 ]]
RESET_AFTER_REPLAY="$(count_reset_marker)"
REPLAY_DELTA=$((RESET_AFTER_REPLAY - RESET_BEFORE_REPLAY))
[[ "$REPLAY_DELTA" -eq 0 || "$REPLAY_DELTA" -eq 1 ]]

PHASE="RUNTIME_HEALTH"
set +e; wait "$PRE_PID"; PRE_RC=$?; set -e; PRE_PID=""
[[ "$PRE_RC" -eq 0 ]] || { tail -160 "$NOMINAL_LOG" >&2 || true; exit 1; }
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$RUNTIME_MANIFEST"

PHASE="MEASUREMENT_BINDING"
python3 - "$MEASUREMENT_JSON" "$GATEWAY_DECISIONS" "$RUN_ID" "$RUN_START_UTC" "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$POLICY_ENFORCEMENT_NS" "$REPLAY_DECISION_NS" "$AUTHORIZED_NOOP_NS" "$OBSERVATION_COMPLETE_NS" "$REPLAY_DELTA" "$NOOP_AFTER_RESPONSE" "$NOOP_BEFORE_RESPONSE" "$EFFECT_NS_FILE" "$ACTION" <<'PY'
import json,sys
from pathlib import Path
(out,decisions,run_id,start_utc,start_ns,activation_ns,enforcement_ns,replay_ns,noop_ns,complete_ns,replay_delta,noop_after,noop_before,effect_path,action)=sys.argv[1:]
rows=[json.loads(x) for x in Path(decisions).read_text(encoding="utf-8").splitlines() if x.strip()]; assert len(rows)==2
replay_row,noop_row=rows; effect=Path(effect_path); effect_ns=int(effect.read_text().strip()) if effect.is_file() else None
payload={"schema":1,"run_id":run_id,"run_start_utc":start_utc,"run_start_ns":int(start_ns),"event_activation_ns":int(activation_ns),"policy_enforcement_ns":int(enforcement_ns),"replay_gateway_decision_ns":int(replay_ns),"replay_effect_observed_ns":effect_ns,"authorized_noop_probe_observed_ns":int(noop_ns),"observation_complete_ns":int(complete_ns),"setup_reset_marker_delta":1,"intervening_authorized_noop_marker_delta":1,"post_replay_reset_marker_delta":int(replay_delta),"post_response_authorized_noop_attempted":1,"post_response_authorized_noop_marker_delta":int(noop_after)-int(noop_before),"gateway_decision_count":2,"replayed_packet_byte_identical":True,"runtime_health_passed":True,"replay_gateway_action":action,"replay_gateway_forwarded":bool(replay_row["forwarded"]),"authorized_noop_gateway_action":action,"authorized_noop_gateway_forwarded":bool(noop_row["forwarded"])}
Path(out).write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver finalize-case \
  --request-json "$REQUEST_JSON" --measurement-json "$MEASUREMENT_JSON" --output-json "$OUTPUT_JSON" >/dev/null

PHASE="CLEANUP_AUDIT"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
docker network rm "$NETWORK" >/dev/null 2>&1 || true
if docker ps -a --format '{{.Names}}' | grep -Fq "$SAFE_ID"; then echo "[ERROR] residual Z02 container remains" >&2; exit 1; fi
if docker network inspect "$NETWORK" >/dev/null 2>&1; then echo "[ERROR] residual Z02 network remains" >&2; exit 1; fi
echo "residual_runtime=none"
echo "automatic_retry_allowed=false"
echo "automatic_next_case_allowed=false"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"
RESULT="PASS"
