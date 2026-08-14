#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

POLICY_ID="${POLICY_ID:?POLICY_ID must be P0 or P1}"
case "$POLICY_ID" in
  P0|P1) ;;
  *) echo "[ERROR] unsupported POLICY_ID=$POLICY_ID" >&2; exit 1 ;;
esac

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp6-$POLICY_ID}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-wp6-gateway"

EVIDENCE="$ROOT/results/wp6/p01/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/policy-decision.json"
INGRESS_JSONL="$GROUND/gateway-ingress.jsonl"
DECISION_JSONL="$GROUND/gateway-decisions.jsonl"
ATTACK_SEND="$GROUND/attacker-send.json"
LEGIT_SEND="$GROUND/authorized-send.json"
SUMMARY="$EVIDENCE/summary.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"
: > "$INGRESS_JSONL"
: > "$DECISION_JSONL"

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP6_P01_POLICY_EFFECT_TRIAL=PASS"
    echo "policy_id=$POLICY_ID"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP6_P01_POLICY_EFFECT_TRIAL=FAIL" >&2
    echo "policy_id=$POLICY_ID" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

PYTHONPATH="$ROOT" python3 - "$EVENT_JSON" "$POLICY_JSON" "$POLICY_ID" <<'PY'
import json, sys
from pathlib import Path
from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy

event=materialize_event(
    "E1",
    mission_state="M0",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
decision=evaluate_policy(sys.argv[3],event)
Path(sys.argv[1]).write_text(
    json.dumps(event,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(sys.argv[2]).write_text(
    json.dumps(decision,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

ACTION="$(
python3 - "$POLICY_JSON" <<'PY'
import json, sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["selected_action"])
PY
)"

case "$POLICY_ID:$ACTION" in
  P0:OBSERVE_ONLY|P1:ISOLATE_MODELED_SOURCE) ;;
  *) echo "[ERROR] unexpected policy action: $POLICY_ID -> $ACTION" >&2; exit 1 ;;
esac

echo "policy_decision=PASS"
echo "policy_id=$POLICY_ID"
echo "policy_action=$ACTION"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"

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
echo "nominal_cfs_running=PASS"

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394\$/ {found=1} END {exit found ? 0 : 1}'" \
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
echo "nominal_ci_lab_udp_5012=PASS"

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_isolation=PASS"

docker run -d --platform linux/amd64 \
  --name "$GATEWAY" \
  --hostname wp6-gateway \
  --network "$NETWORK" \
  --network-alias wp6-gateway \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway serve \
    --action "$ACTION" \
    --isolated-source modeled_attacker \
    --truth-jsonl /evidence/gateway-ingress.jsonl \
    --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' 19091)"
for _ in $(seq 1 15); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$GATEWAY" sh -lc \
       "awk '\$2 ~ /:${HEX_GATEWAY_PORT}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 1
done
[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] WP6 gateway did not bind UDP 19091" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}
[[ -z "$(docker port "$GATEWAY")" ]]
echo "policy_gateway_ready=PASS"

count_marker() {
  docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true
}

wait_marker_exact() {
  local before="$1" expected_delta="$2" label="$3"
  local now
  for _ in $(seq 1 15); do
    now="$(count_marker)"
    if [[ "$now" -eq $((before + expected_delta)) ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt $((before + expected_delta)) ]]; then
      echo "[ERROR] $label exceeded expected acceptance delta" >&2
      return 2
    fi
    sleep 1
  done
  now="$(count_marker)"
  echo "[ERROR] $label acceptance timeout: before=$before now=$now expected_delta=$expected_delta" >&2
  return 1
}

send_source() {
  local source_id="$1" result_file="$2"
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id "$source_id" \
      --gateway-host wp6-gateway \
      --result-json "/evidence/$result_file"
}

BASELINE="$(count_marker)"
send_source modeled_attacker "$(basename "$ATTACK_SEND")"

if [[ "$POLICY_ID" == P0 ]]; then
  AFTER_ATTACK="$(wait_marker_exact "$BASELINE" 1 attacker)"
  echo "attacker_noop_acceptance_delta=1"
else
  sleep 3
  AFTER_ATTACK="$(count_marker)"
  test "$AFTER_ATTACK" -eq "$BASELINE" || {
    echo "[ERROR] P1 attacker command reached cFS" >&2
    exit 1
  }
  echo "attacker_noop_acceptance_delta=0"
fi

send_source authorized_ground "$(basename "$LEGIT_SEND")"
AFTER_LEGIT="$(wait_marker_exact "$AFTER_ATTACK" 1 authorized)"
echo "authorized_noop_acceptance_delta=1"

python3 - "$INGRESS_JSONL" "$DECISION_JSONL" "$POLICY_ID" <<'PY'
import json, sys
from pathlib import Path

def rows(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

ingress=rows(sys.argv[1])
decisions=rows(sys.argv[2])
policy=sys.argv[3]

assert len(ingress)==2, ingress
assert len(decisions)==2, decisions
assert [r["source_id"] for r in ingress]==[
    "modeled_attacker",
    "authorized_ground",
]
assert ingress[0]["packet_sha256"]==ingress[1]["packet_sha256"]
assert ingress[0]["packet_sha256"]=="722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"

expected=[True,True] if policy=="P0" else [False,True]
actual=[r["forwarded"] for r in decisions]
assert actual==expected,(actual,expected)

print("gateway_ingress_pair=PASS")
print("gateway_forwarding_decisions=PASS")
print("command_packet_identity=PASS")
PY

docker rm -f "$GATEWAY" >/dev/null

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
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"

RUNTIME_SHA="$(shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" | awk '{print $1}')"
INGRESS_SHA="$(shasum -a 256 "$INGRESS_JSONL" | awk '{print $1}')"
DECISIONS_SHA="$(shasum -a 256 "$DECISION_JSONL" | awk '{print $1}')"

python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$SUMMARY" "$POLICY_ID" \
  "$BASELINE" "$AFTER_ATTACK" "$AFTER_LEGIT" \
  "$INGRESS_SHA" "$DECISIONS_SHA" "$RUNTIME_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

(
 event_path, policy_path, summary_path, policy_id,
 baseline, after_attack, after_legit,
 ingress_sha, decisions_sha, runtime_sha
)=sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
decision=json.loads(Path(policy_path).read_text(encoding="utf-8"))

baseline=int(baseline)
after_attack=int(after_attack)
after_legit=int(after_legit)

attacker_delta=after_attack-baseline
authorized_delta=after_legit-after_attack

expected_attacker=1 if policy_id=="P0" else 0
assert attacker_delta==expected_attacker
assert authorized_delta==1

summary={
    "schema":1,
    "classification":"WP6_P01_POLICY_EFFECT_TRIAL_PASS",
    "policy_id":policy_id,
    "policy_action":decision["selected_action"],
    "event_id":"E1",
    "mission_state":"M0",
    "contact_condition":"C0",
    "evidence_condition":"T0",
    "seed":1,
    "event_instance_sha256":event["instance_sha256"],
    "decision_sha256":decision["decision_sha256"],
    "command_packet_sha256":"722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
    "attacker_noop_acceptance_delta":attacker_delta,
    "authorized_noop_acceptance_delta":authorized_delta,
    "modeled_unauthorized_effect_completed":policy_id=="P0",
    "legitimate_command_rejection_rate":0.0,
    "unaffected_command_path_preserved":True,
    "gateway_ingress_sha256":ingress_sha,
    "gateway_decisions_sha256":decisions_sha,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "containment_latency_claim":False,
    "trusted_recovery_claim":False,
    "native_cfs_identity_enforcement_claim":False
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="PASS"
echo "modeled_unauthorized_effect_completed=$([[ "$POLICY_ID" == P0 ]] && echo true || echo false)"
echo "legitimate_command_rejection_rate=0.0"
echo "unaffected_command_path_preserved=true"
echo "validated_nominal_runtime_pass=true"
echo "containment_latency_claim=false"
echo "trusted_recovery_claim=false"
