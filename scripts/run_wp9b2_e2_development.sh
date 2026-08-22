#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
OBSERVATION_WINDOW_SECONDS=3

[[ "$#" -eq 1 ]] || {
  echo "usage: $0 <D03|D04|D05>" >&2
  exit 2
}
CASE_ID="$1"
case "$CASE_ID" in
  D03|D04|D05) ;;
  *) echo "[ERROR] E2 development runner supports D03-D05 only" >&2; exit 2 ;;
esac

cd "$ROOT"

for command in docker git python3 shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before WP9-B2 development runtime" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_development validate

SEED="$(
  PYTHONPATH="$ROOT" python3 - "$CASE_ID" <<'PY'
import sys
from src.mission_recovery.wp9b2_development import development_case
print(development_case(sys.argv[1])["development_seed"])
PY
)"
TOKEN="$(python3 - <<'PY'
import uuid
print(uuid.uuid4().hex)
PY
)"
CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9b2-${CASE_SAFE}-s${SEED}-${TOKEN}}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-wp9b2-e2-gateway"
GATEWAY_ALIAS="wp9b2-e2-gateway"

EVIDENCE="$ROOT/results/wp9/development/wp9b2/e2/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
CONTRACT_JSON="$GROUND/e2-replay-effect-contract.json"
SETUP_JSON="$GROUND/setup-reset.json"
INTERVENING_JSON="$GROUND/intervening-authorized-noop.json"
REPLAY_JSON="$GROUND/replay-send.json"
GATEWAY_TRUTH="$GROUND/gateway-ingress.jsonl"
GATEWAY_DECISIONS="$GROUND/gateway-decisions.jsonl"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"
REPO_COMMIT="unknown"

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
  for _ in $(seq 1 40); do
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

emit_invalid() {
  local rc="$1"
  mkdir -p "$EVIDENCE"
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json, sys
from pathlib import Path
path, run_id, case_id, seed, phase, rc, commit = sys.argv[1:]
record = {
    "schema": 1,
    "decision_id": "R-046",
    "classification": "WP9B2_DEVELOPMENT_RUN_INVALID",
    "run_id": run_id,
    "case_id": case_id,
    "development_seed": int(seed),
    "failed_phase": phase,
    "exit_code": int(rc),
    "repo_commit": commit,
    "development_runtime_data": False,
    "campaign_seed_consumed": False,
    "campaign_data": False,
    "final_campaign_failure_claimed": False,
    "automatic_next_case": False,
}
Path(path).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9B2_E2_DEVELOPMENT_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "development_seed=$SEED"
    echo "development_runtime_data=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data=false"
    echo "automatic_next_case=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9B2_E2_DEVELOPMENT_RUNTIME=FAIL" >&2
    echo "case_id=$CASE_ID" >&2
    echo "failed_phase=$PHASE" >&2
    echo "campaign_seed_consumed=false" >&2
    echo "campaign_data=false" >&2
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
echo "wp9b2_docker_daemon=PASS"
echo "wp9b2_pinned_image=PASS"

REPO_COMMIT="$(git rev-parse HEAD)"
mkdir -p "$GROUND" "$OBS"
: > "$GATEWAY_TRUTH"
: > "$GATEWAY_DECISIONS"

PHASE="DEVELOPMENT_PLAN"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_development plan \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-plan-json "$PLAN_JSON" \
  --output-event-json "$EVENT_JSON" \
  --output-policy-json "$POLICY_JSON" \
  --output-e2-contract-json "$CONTRACT_JSON"
echo "wp9b2_development_plan=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
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
echo "setup_quiet_baseline=PASS"

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
record = {
    "role": "previously_accepted_authorized_command_before_treatment",
    "source_id": "authorized_ground",
    "command_class": "sample_reset_counters",
    "target": "nos-fsw:5012",
    "datagrams_sent": 1,
    "bytes_sent": sent,
    "packet_hex": packet.hex(),
    "packet_sha256": hashlib.sha256(packet).hexdigest(),
}
Path(sys.argv[1]).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
RESET_AFTER_SETUP="$(wait_exact_delta count_reset_marker "$RESET_BEFORE_SETUP" 1 setup_reset)"
echo "setup_reset_marker_delta=1"

PHASE="INTERVENING_AUTHORIZED_NOOP"
NOOP_BEFORE="$(count_noop_marker)"
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
record = {
    "role": "intervening_authorized_probe",
    "source_id": "authorized_ground",
    "command_class": "sample_noop",
    "target": "nos-fsw:5012",
    "datagrams_sent": 1,
    "bytes_sent": sent,
    "packet_hex": packet.hex(),
    "packet_sha256": hashlib.sha256(packet).hexdigest(),
}
Path(sys.argv[1]).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
NOOP_AFTER="$(wait_exact_delta count_noop_marker "$NOOP_BEFORE" 1 intervening_noop)"
RESET_BEFORE_REPLAY="$(count_reset_marker)"
[[ "$RESET_BEFORE_REPLAY" -eq "$RESET_AFTER_SETUP" ]] || {
  echo "[ERROR] RESET marker changed during intervening NOOP" >&2
  exit 1
}
echo "intervening_authorized_noop_delta=1"
echo "pre_replay_reset_baseline=PASS"

PHASE="POLICY_GATEWAY_START"
ACTION="$(python3 - "$POLICY_JSON" <<'PY'
import json, sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["selected_action"])
PY
)"
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
for _ in $(seq 1 30); do
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
  echo "[ERROR] WP9-B2 E2 gateway did not bind" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}
[[ -z "$(docker port "$GATEWAY")" ]]
echo "policy_gateway_ready=PASS"

PHASE="BYTE_IDENTICAL_REPLAY"
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
    "probe_variant": "wp9_byte_identical_replay_effect",
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

sleep "$OBSERVATION_WINDOW_SECONDS"
RESET_AFTER_REPLAY="$(count_reset_marker)"
DECISION_COUNT="$(python3 - "$GATEWAY_DECISIONS" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1])
print(sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip()))
PY
)"
[[ "$DECISION_COUNT" -eq 1 ]] || {
  echo "[ERROR] expected exactly one replay gateway decision, got $DECISION_COUNT" >&2
  exit 1
}
echo "fixed_post_replay_observation_window_s=$OBSERVATION_WINDOW_SECONDS"
echo "replay_gateway_decision_count=1"

PHASE="E2_ACCEPTANCE"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_development finalize-e2 \
  --plan-json "$PLAN_JSON" \
  --setup-json "$SETUP_JSON" \
  --intervening-json "$INTERVENING_JSON" \
  --replay-json "$REPLAY_JSON" \
  --gateway-decisions-jsonl "$GATEWAY_DECISIONS" \
  --reset-before-setup "$RESET_BEFORE_SETUP" \
  --reset-after-setup "$RESET_AFTER_SETUP" \
  --reset-before-replay "$RESET_BEFORE_REPLAY" \
  --reset-after-replay "$RESET_AFTER_REPLAY" \
  --noop-before "$NOOP_BEFORE" \
  --noop-after "$NOOP_AFTER" \
  --output-summary-json "$SUMMARY_JSON"
echo "wp9b2_e2_acceptance=PASS"

docker rm -f "$GATEWAY" >/dev/null

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
if docker inspect "$CFS" >/dev/null 2>&1; then
  echo "[ERROR] residual cFS container remains after nominal runtime" >&2
  exit 1
fi
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  echo "[ERROR] residual WP9-B2 network remains after nominal runtime" >&2
  exit 1
fi
echo "residual_runtime=none"

RESULT="PASS"
