#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

[[ "$#" -eq 1 ]] || {
  echo "usage: $0 <V01|V02|V03>" >&2
  exit 2
}

CASE_ID="$1"
case "$CASE_ID" in
  V01) CELL_ID="A19"; SEED="9901" ;;
  V02) CELL_ID="A20"; SEED="9902" ;;
  V03) CELL_ID="A21"; SEED="9903" ;;
  *)
    echo "[ERROR] R-057 E2 route validation supports V01-V03 only" >&2
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
  echo "[ERROR] repository worktree must be clean before R-057 runtime validation" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e2_runtime_adapter \
  validate-static

TOKEN="$(python3 - <<'PY'
import uuid
print(uuid.uuid4().hex)
PY
)"
CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r057-${CASE_SAFE}-s${SEED}-${TOKEN}}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-r057-e2-gateway"
GATEWAY_ALIAS="r057-e2-gateway"

EVIDENCE="$ROOT/results/wp9/development/r057/e2/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
SETUP_JSON="$GROUND/setup-reset.json"
INTERVENING_JSON="$GROUND/intervening-authorized-noop.json"
REPLAY_JSON="$GROUND/replay-send.json"
AUTHORIZED_JSON="$GROUND/post-response-authorized-noop.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
MEASUREMENT_JSON="$OBS/e2-route-measurement.json"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"
EFFECT_NS_FILE="$OBS/replay-effect-observed-ns.txt"

PRE_PID=""
WATCH_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
REPO_COMMIT="unknown"
RUN_START_NS=""
RUN_START_UTC=""
EVENT_ACTIVATION_NS=""
POLICY_ENFORCEMENT_NS=""
REPLAY_DECISION_NS=""
AUTHORIZED_NOOP_NS=""
OBSERVATION_COMPLETE_NS=""

mono_ns() {
  python3 - <<'PY'
import time
print(time.monotonic_ns())
PY
}

count_reset_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: RESET counters command received' || true
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

wait_exact_delta() {
  local counter="$1" before="$2" delta="$3" label="$4"
  local now expected
  expected=$((before + delta))
  for _ in $(seq 1 50); do
    now="$("$counter")"
    if [[ "$now" -eq "$expected" ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] $label exceeded expected count: now=$now expected=$expected" >&2
      return 2
    fi
    sleep 0.1
  done
  now="$("$counter")"
  echo "[ERROR] $label timeout: now=$now expected=$expected" >&2
  return 1
}

wait_decision_count() {
  local expected="$1"
  local count
  for _ in $(seq 1 50); do
    count="$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1])
print(sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip()))
PY
)"
    [[ "$count" -eq "$expected" ]] && return 0
    [[ "$count" -gt "$expected" ]] && {
      echo "[ERROR] gateway decision count exceeded $expected: $count" >&2
      return 2
    }
    sleep 0.1
  done
  echo "[ERROR] gateway decision count did not reach $expected" >&2
  return 1
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
    "decision_id": "R-057",
    "classification": "WP9_R057_E2_ROUTE_VALIDATION_RUN_INVALID",
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
  if [[ -n "$WATCH_PID" ]] && kill -0 "$WATCH_PID" >/dev/null 2>&1; then
    kill -TERM "$WATCH_PID" >/dev/null 2>&1 || true
    wait "$WATCH_PID" >/dev/null 2>&1 || true
  fi
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9_R057_E2_ROUTE_VALIDATION_RUNTIME=PASS"
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
    echo "WP9_R057_E2_ROUTE_VALIDATION_RUNTIME=FAIL" >&2
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
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"
rm -f "$EFFECT_NS_FILE"

echo "r057_docker_daemon=PASS"
echo "r057_pinned_image=PASS"
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
[[ "$CI_READY" -eq 1 ]] || {
  echo "[ERROR] CI_LAB UDP 5012 not observed" >&2
  exit 1
}
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]

echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

PHASE="SETUP_QUIET_BASELINE"
RESET_BEFORE_SETUP="$(count_reset_marker)"
sleep 2
[[ "$(count_reset_marker)" -eq "$RESET_BEFORE_SETUP" ]] || {
  echo "[ERROR] RESET marker changed during setup quiet baseline" >&2
  exit 1
}

PHASE="AUTHORIZED_SETUP_RESET"
docker run --rm -i --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 - /evidence/"$(basename "$SETUP_JSON")" <<'PY'
import hashlib, json, socket, sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
packet = build_sample_noargs_packet("sample_reset_counters")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent = sock.sendto(packet, ("nos-fsw", 5012))
sock.close()
assert sent == len(packet)
Path(sys.argv[1]).write_text(json.dumps({
    "role": "previously_accepted_authorized_command_before_treatment",
    "source_id": "authorized_ground",
    "command_class": "sample_reset_counters",
    "target": "nos-fsw:5012",
    "datagrams_sent": 1,
    "bytes_sent": sent,
    "packet_hex": packet.hex(),
    "packet_sha256": hashlib.sha256(packet).hexdigest(),
}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
RESET_AFTER_SETUP="$(wait_exact_delta count_reset_marker "$RESET_BEFORE_SETUP" 1 setup_reset)"
echo "setup_reset_marker_delta=1"

PHASE="INTERVENING_AUTHORIZED_NOOP"
NOOP_BEFORE_INTERVENING="$(count_noop_marker)"
docker run --rm -i --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 - /evidence/"$(basename "$INTERVENING_JSON")" <<'PY'
import hashlib, json, socket, sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
packet = build_sample_noargs_packet("sample_noop")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent = sock.sendto(packet, ("nos-fsw", 5012))
sock.close()
assert sent == len(packet)
Path(sys.argv[1]).write_text(json.dumps({
    "role": "intervening_authorized_probe_before_treatment",
    "source_id": "authorized_ground",
    "command_class": "sample_noop",
    "target": "nos-fsw:5012",
    "datagrams_sent": 1,
    "bytes_sent": sent,
    "packet_hex": packet.hex(),
    "packet_sha256": hashlib.sha256(packet).hexdigest(),
}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
NOOP_AFTER_INTERVENING="$(wait_exact_delta count_noop_marker "$NOOP_BEFORE_INTERVENING" 1 intervening_noop)"
[[ "$(count_reset_marker)" -eq "$RESET_AFTER_SETUP" ]] || {
  echo "[ERROR] RESET marker changed during intervening NOOP" >&2
  exit 1
}
echo "intervening_authorized_noop_marker_delta=1"

PHASE="EVENT_ACTIVATION_AND_POLICY_SELECTION"
RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EVENT_ACTIVATION_NS="$(mono_ns)"

PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e2_runtime_adapter \
  plan-development \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-json "$PLAN_JSON"

ACTION="$(python3 - "$PLAN_JSON" <<'PY'
import json, sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["runtime_policy_decision"]["selected_action"])
PY
)"

echo "r057_development_plan=PASS"
echo "selected_action=$ACTION"
echo "policy_trigger_uses_ground_truth=false"

PHASE="POLICY_GATEWAY_START"
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
    --action "$ACTION" \
    --isolated-source modeled_attacker \
    --truth-jsonl /evidence/"$(basename "$GATEWAY_TRUTH")" \
    --decision-jsonl /evidence/"$(basename "$GATEWAY_DECISIONS")" >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' 19091)"
for _ in $(seq 1 50); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$GATEWAY" sh -lc \
       "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 0.1
done
[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] R-057 E2 gateway did not bind" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}
[[ -z "$(docker port "$GATEWAY")" ]]
POLICY_ENFORCEMENT_NS="$(mono_ns)"
echo "policy_gateway_ready=PASS"

PHASE="BYTE_IDENTICAL_REPLAY"
RESET_BEFORE_REPLAY="$(count_reset_marker)"
(
  for _ in $(seq 1 300); do
    now="$(count_reset_marker)"
    if [[ "$now" -eq $((RESET_BEFORE_REPLAY + 1)) ]]; then
      mono_ns > "$EFFECT_NS_FILE"
      exit 0
    fi
    if [[ "$now" -gt $((RESET_BEFORE_REPLAY + 1)) ]]; then
      echo "[ERROR] replay RESET marker exceeded one observed effect" >&2
      exit 2
    fi
    sleep 0.1
  done
  exit 0
) &
WATCH_PID=$!

docker run --rm -i --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 - "$GATEWAY_ALIAS" /evidence/"$(basename "$REPLAY_JSON")" <<'PY'
import hashlib, json, socket, sys
from pathlib import Path
from src.mission_recovery.policy_gateway import build_sample_noargs_packet
host, output = sys.argv[1:]
packet = build_sample_noargs_packet("sample_reset_counters")
envelope = {
    "schema": 1,
    "event_id": "E2",
    "probe_variant": "wp9_r057_byte_identical_replay",
    "role": "byte_identical_stale_replay_after_treatment",
    "source_id": "modeled_attacker",
    "command_class": "sample_reset_counters",
    "declared_risk_class": "high_surrogate",
    "packet_hex": packet.hex(),
    "packet_sha256": hashlib.sha256(packet).hexdigest(),
}
encoded = (json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent = sock.sendto(encoded, (host, 19091))
sock.close()
assert sent == len(encoded)
record = dict(envelope)
record.update({"gateway": f"{host}:19091", "datagrams_sent": 1, "envelope_bytes_sent": sent})
Path(output).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
wait_decision_count 1
REPLAY_DECISION_NS="$(mono_ns)"
echo "replay_gateway_decision_count=1"

PHASE="POST_RESPONSE_AUTHORIZED_NOOP"
NOOP_BEFORE_RESPONSE="$(count_noop_marker)"
docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway send \
    --source-id authorized_ground \
    --command-class sample_noop \
    --gateway-host "$GATEWAY_ALIAS" \
    --result-json /evidence/"$(basename "$AUTHORIZED_JSON")"
wait_decision_count 2
sleep 1
NOOP_AFTER_RESPONSE="$(count_noop_marker)"
AUTHORIZED_NOOP_NS="$(mono_ns)"
echo "post_response_authorized_noop_attempted=1"
echo "post_response_authorized_noop_marker_delta=$((NOOP_AFTER_RESPONSE - NOOP_BEFORE_RESPONSE))"

PHASE="FROZEN_ANALYSIS_HORIZON"
python3 - "$EVENT_ACTIVATION_NS" <<'PY'
import sys, time
origin=int(sys.argv[1])
target=origin+30_000_000_000
remaining=(target-time.monotonic_ns())/1_000_000_000
if remaining > 0:
    time.sleep(remaining)
PY
OBSERVATION_COMPLETE_NS="$(mono_ns)"

set +e
wait "$WATCH_PID"
WATCH_RC=$?
set -e
WATCH_PID=""
[[ "$WATCH_RC" -eq 0 ]] || {
  echo "[ERROR] replay effect watcher failed: rc=$WATCH_RC" >&2
  exit 1
}

RESET_AFTER_REPLAY="$(count_reset_marker)"
REPLAY_DELTA=$((RESET_AFTER_REPLAY - RESET_BEFORE_REPLAY))
[[ "$REPLAY_DELTA" -eq 0 || "$REPLAY_DELTA" -eq 1 ]] || {
  echo "[ERROR] post-replay RESET delta outside {0,1}: $REPLAY_DELTA" >&2
  exit 1
}

PHASE="RUNTIME_HEALTH"
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

PHASE="MEASUREMENT_MATERIALIZATION"
python3 - \
  "$MEASUREMENT_JSON" "$PLAN_JSON" "$GATEWAY_DECISIONS" \
  "$RUN_ID" "$RUN_START_UTC" "$RUN_START_NS" \
  "$EVENT_ACTIVATION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$REPLAY_DECISION_NS" "$AUTHORIZED_NOOP_NS" \
  "$OBSERVATION_COMPLETE_NS" "$REPLAY_DELTA" \
  "$NOOP_AFTER_RESPONSE" "$NOOP_BEFORE_RESPONSE" \
  "$EFFECT_NS_FILE" <<'PY'
import json, sys
from pathlib import Path
(
    out, plan_path, decisions_path, run_id, run_start_utc,
    run_start_ns, event_activation_ns, policy_enforcement_ns,
    replay_decision_ns, authorized_noop_ns, observation_complete_ns,
    replay_delta, noop_after, noop_before, effect_path,
) = sys.argv[1:]
plan=json.loads(Path(plan_path).read_text(encoding="utf-8"))
rows=[json.loads(line) for line in Path(decisions_path).read_text(encoding="utf-8").splitlines() if line.strip()]
if len(rows) != 2:
    raise SystemExit(f"expected exactly two gateway decisions, got {len(rows)}")
replay_row, noop_row = rows
selected=plan["runtime_policy_decision"]["selected_action"]
effect_file=Path(effect_path)
effect_ns=int(effect_file.read_text(encoding="utf-8").strip()) if effect_file.is_file() else None
payload={
    "schema": 1,
    "run_id": run_id,
    "run_start_utc": run_start_utc,
    "run_start_ns": int(run_start_ns),
    "event_activation_ns": int(event_activation_ns),
    "policy_enforcement_ns": int(policy_enforcement_ns),
    "replay_gateway_decision_ns": int(replay_decision_ns),
    "replay_effect_observed_ns": effect_ns,
    "authorized_noop_probe_observed_ns": int(authorized_noop_ns),
    "observation_complete_ns": int(observation_complete_ns),
    "setup_reset_marker_delta": 1,
    "intervening_authorized_noop_marker_delta": 1,
    "post_replay_reset_marker_delta": int(replay_delta),
    "post_response_authorized_noop_attempted": 1,
    "post_response_authorized_noop_marker_delta": int(noop_after)-int(noop_before),
    "gateway_decision_count": 2,
    "replayed_packet_byte_identical": True,
    "runtime_health_passed": True,
    "replay_gateway_action": selected,
    "replay_gateway_forwarded": bool(replay_row["forwarded"]),
    "authorized_noop_gateway_action": selected,
    "authorized_noop_gateway_forwarded": bool(noop_row["forwarded"]),
}
Path(out).write_text(json.dumps(payload, sort_keys=True, indent=2)+"\n", encoding="utf-8")
PY

PHASE="R057_OBSERVATION_FINALIZE"
PYTHONPATH="$ROOT" python3 -m \
  src.mission_recovery.wp9_campaign_e2_runtime_adapter \
  finalize-development \
  --plan-json "$PLAN_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --output-json "$SUMMARY_JSON"

echo "r057_observation_binding=PASS"

PHASE="CLEANUP_AUDIT"
docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
if docker inspect "$CFS" >/dev/null 2>&1; then
  echo "[ERROR] residual cFS container remains after nominal runtime" >&2
  exit 1
fi
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  echo "[ERROR] residual R-057 network remains after nominal runtime" >&2
  exit 1
fi

echo "residual_runtime=none"
echo "campaign_seed_consumed=false"
echo "campaign_data_generated=false"

RESULT="PASS"
PHASE="COMPLETE"
