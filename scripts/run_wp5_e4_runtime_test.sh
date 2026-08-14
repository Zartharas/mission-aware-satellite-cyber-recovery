#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

MODE="${E4_MODE:?E4_MODE must be control or degraded}"
case "$MODE" in
  control|degraded) ;;
  *) echo "[ERROR] invalid E4_MODE=$MODE" >&2; exit 1 ;;
esac

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-e4-$MODE}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-e4-proxy"
POLICY="mascr-$SAFE_ID-e4-policy"
E4_TLM_PORT=5013

EVIDENCE="$ROOT/results/wp5/e4/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

EVENT_JSON="$GROUND/event-instance.json"
TRUTH_JSONL="$GROUND/telemetry-truth.jsonl"
POLICY_JSONL="$OBS/policy-visible.jsonl"
ENABLE_JSON="$GROUND/enable-output.json"
SEND_JSON="$GROUND/send-data-types.json"
SUMMARY="$EVIDENCE/summary.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"
: > "$TRUTH_JSONL"
: > "$POLICY_JSONL"

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$PROXY" "$POLICY" >/dev/null 2>&1 || true
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP5_E4_MATCHED_TRIAL=PASS"
    echo "mode=$MODE"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP5_E4_MATCHED_TRIAL=FAIL" >&2
    echo "mode=$MODE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

PYTHONPATH="$ROOT" python3 - "$EVENT_JSON" <<'PY'
import json, sys
from pathlib import Path
from src.mission_recovery.events import materialize_event

event=materialize_event(
    "E4",
    mission_state="M2",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
Path(sys.argv[1]).write_text(
    json.dumps(event,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"
echo "matched_trial_mode=$MODE"

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
[[ "$CI_READY" -eq 1 ]]
echo "nominal_ci_lab_udp_5012=PASS"

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_isolation=PASS"

docker run -d --platform linux/amd64 \
  --name "$POLICY" \
  --hostname e4-policy \
  --network "$NETWORK" \
  --network-alias e4-policy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$OBS,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility observer \
    --jsonl /evidence/policy-visible.jsonl \
    --port 19090 >/dev/null

docker run -d --platform linux/amd64 \
  --name "$PROXY" \
  --hostname e4-proxy \
  --network "$NETWORK" \
  --network-alias e4-proxy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/truth" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility proxy \
    --truth-jsonl /truth/telemetry-truth.jsonl \
    --mode "$MODE" \
    --listen-port "$E4_TLM_PORT" \
    --policy-host e4-policy \
    --policy-port 19090 >/dev/null

PROXY_READY=0
HEX_TLM_PORT="$(printf '%04X' "$E4_TLM_PORT")"
for _ in $(seq 1 15); do
  if [[ "$(docker inspect "$PROXY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$PROXY" sh -lc \
       "awk '\$2 ~ /:${HEX_TLM_PORT}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    PROXY_READY=1
    break
  fi
  sleep 1
done
[[ "$PROXY_READY" -eq 1 ]] || {
  echo "[ERROR] E4 proxy did not bind UDP $E4_TLM_PORT" >&2
  exit 1
}
[[ "$(docker inspect "$POLICY" --format '{{.State.Status}}')" == running ]]
echo "e4_proxy_udp_receiver_ready=PASS"

run_adapter() {
  local result_file="$1"
  shift
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.nos3_e4_adapter \
      "$@" \
      --result-json "/evidence/$result_file"
}

count_mid() {
  python3 - "$1" "$2" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
mid=int(sys.argv[2],0)
print(sum(
    1 for line in p.read_text(encoding="utf-8").splitlines()
    if line.strip() and json.loads(line).get("mid")==mid
) if p.exists() else 0)
PY
}

wait_for_count() {
  local path="$1" mid="$2" expected="$3" label="$4"
  local now
  for _ in $(seq 1 15); do
    now="$(count_mid "$path" "$mid")"
    if [[ "$now" -eq "$expected" ]]; then
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] $label count exceeded expected: now=$now expected=$expected" >&2
      return 2
    fi
    sleep 1
  done
  now="$(count_mid "$path" "$mid")"
  echo "[ERROR] $label timeout: now=$now expected=$expected" >&2
  return 1
}

run_adapter "$(basename "$ENABLE_JSON")" enable-output --destination e4-proxy

ENABLE_READY=0
for _ in $(seq 1 15); do
  if docker logs "$CFS" 2>&1 | grep -Fq 'TO telemetry output enabled for IP e4-proxy'; then
    ENABLE_READY=1
    break
  fi
  sleep 1
done
[[ "$ENABLE_READY" -eq 1 ]]
echo "to_lab_output_enable=PASS"

test "$(count_mid "$TRUTH_JSONL" 0x08E9)" -eq 0
test "$(count_mid "$POLICY_JSONL" 0x08E9)" -eq 0

run_adapter "$(basename "$SEND_JSON")" send-data-types

wait_for_count "$TRUTH_JSONL" 0x08E9 1 "${MODE}_truth"

if [[ "$MODE" == control ]]; then
  wait_for_count "$POLICY_JSONL" 0x08E9 1 control_policy
else
  sleep 3
  test "$(count_mid "$POLICY_JSONL" 0x08E9)" -eq 0 || {
    echo "[ERROR] degraded packet became policy-visible" >&2
    exit 1
  }
fi

python3 - "$TRUTH_JSONL" "$MODE" <<'PY'
import json, sys
from pathlib import Path

rows=[
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip() and json.loads(line).get("mid")==0x08E9
]
assert len(rows)==1
expected=(sys.argv[2]=="control")
assert rows[0]["forwarded_to_policy"] is expected
print(f"{sys.argv[2]}_truth_forwarding_decision=PASS")
PY

echo "${MODE}_truth_high_value_delta=PASS"
if [[ "$MODE" == control ]]; then
  echo "control_policy_high_value_delta=PASS"
else
  echo "degraded_policy_high_value_delta=PASS"
fi

docker rm -f "$PROXY" "$POLICY" >/dev/null

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
TRUTH_SHA="$(shasum -a 256 "$TRUTH_JSONL" | awk '{print $1}')"
POLICY_SHA="$(shasum -a 256 "$POLICY_JSONL" | awk '{print $1}')"

python3 - \
  "$EVENT_JSON" "$SEND_JSON" "$SUMMARY" "$MODE" "$RUN_ID" \
  "$TRUTH_SHA" "$POLICY_SHA" "$RUNTIME_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

event_path, send_path, summary_path, mode, run_id, truth_sha, policy_sha, runtime_sha=sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
send=json.loads(Path(send_path).read_text(encoding="utf-8"))

summary={
    "schema":1,
    "run_id":run_id,
    "classification":"WP5_E4_MATCHED_TRIAL_PASS",
    "event_id":"E4",
    "mode":mode,
    "mission_state":"M2",
    "contact_condition":"C0",
    "evidence_condition":"T0",
    "seed":1,
    "send_data_types_command_sha256":send["packet_sha256"],
    "immutable_truth_sha256":truth_sha,
    "policy_visible_sha256":policy_sha,
    "truth_high_value_delta":1,
    "policy_high_value_delta":1 if mode=="control" else 0,
    "forwarded_to_policy":mode=="control",
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "operational_target":False,
    "rf_interference":False
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="PASS"
echo "validated_nominal_runtime_pass=true"
echo "policy_effectiveness_claim=false"
