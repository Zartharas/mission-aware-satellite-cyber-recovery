#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp5/e1/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
EVENT_JSON="$GROUND/event-instance.json"
SEND_JSON="$GROUND/send-result.json"
SUMMARY="$EVIDENCE/summary.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"

cleanup() {
  local rc=$?
  set +e

  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" == E1_RUNTIME_ADAPTER_PASS && "$rc" -eq 0 ]]; then
    echo "WP5_E1_RUNTIME_TEST=PASS"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP5_E1_RUNTIME_TEST=FAIL" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

for cmd in docker git python3 shasum; do
  command -v "$cmd" >/dev/null || {
    echo "[ERROR] missing required command: $cmd" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}

echo "runner_docker_daemon=PASS"
echo "runner_pinned_image=PASS"

# Materialize the immutable E1 truth before runtime starts.
PYTHONPATH="$ROOT" python3 - "$EVENT_JSON" <<'PY'
import json, sys
from pathlib import Path
from src.mission_recovery.events import materialize_event

event = materialize_event(
    "E1",
    mission_state="M0",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
Path(sys.argv[1]).write_text(
    json.dumps(event, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

# Launch the retained, already-validated nominal topology unchanged.
RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"
echo "nominal_runtime_pid=$PRE_PID"

# Wait for the cFS container created by the nominal runtime.
CFS_READY=0
for _ in $(seq 1 180); do
  if ! kill -0 "$PRE_PID" >/dev/null 2>&1; then
    break
  fi

  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  if [[ "$state" == running ]]; then
    CFS_READY=1
    break
  fi

  sleep 1
done

[[ "$CFS_READY" -eq 1 ]] || {
  echo "[ERROR] nominal runtime did not produce a running cFS container" >&2
  tail -120 "$NOMINAL_LOG" >&2 || true
  exit 1
}
echo "nominal_cfs_running=PASS"

# Objective CI_LAB readiness: UDP port 5012 == 0x1394.
CI_READY=0
for _ in $(seq 1 90); do
  if ! kill -0 "$PRE_PID" >/dev/null 2>&1; then
    break
  fi

  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  [[ "$state" == running ]] || break

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
  echo "[ERROR] CI_LAB UDP 5012 not observed in validated nominal runtime" >&2
  docker logs "$CFS" 2>&1 | tail -120 >&2 || true
  tail -120 "$NOMINAL_LOG" >&2 || true
  exit 1
}
echo "nominal_ci_lab_udp_5012=PASS"

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]] || {
  echo "[ERROR] nominal network is not internal" >&2
  exit 1
}
[[ -z "$(docker port "$CFS")" ]] || {
  echo "[ERROR] cFS unexpectedly publishes host ports" >&2
  exit 1
}
echo "nominal_isolation=PASS"

before="$(
  docker logs "$CFS" 2>&1 |
  grep -Fc 'SAMPLE: NOOP command received' || true
)"

# Exactly one synthetic E1 datagram, directly to CI_LAB inside the known-good
# isolated runtime. No host port and no RF/radio path is involved.
docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --network-alias e1-ground-adapter \
  --label research.project=mission-aware-satellite-cyber-recovery \
  --label research.phase=wp5-e1-runtime-test \
  --label "research.run_id=$RUN_ID" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$EVENT_JSON,target=/event/event.json,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.nos3_e1_adapter \
    --event-json /event/event.json \
    --result-json /evidence/send-result.json

after="$before"
for _ in $(seq 1 15); do
  after="$(
    docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
  )"
  [[ "$after" -eq $((before + 1)) ]] && break
  sleep 1
done

[[ "$after" -eq $((before + 1)) ]] || {
  echo "[ERROR] Sample NOOP acceptance marker did not increment exactly once" >&2
  docker logs "$CFS" 2>&1 | tail -120 >&2 || true
  exit 1
}
echo "sample_noop_acceptance_delta=PASS"

# Allow the validated nominal run to finish its own liveness observation and
# bounded cleanup.
set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime preflight failed after E1 injection: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG" || {
  echo "[ERROR] nominal runtime PASS marker absent" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt" || {
  echo "[ERROR] nominal runtime manifest missing" >&2
  exit 1
}

NOMINAL_MANIFEST_SHA="$(
  shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" |
  awk '{print $1}'
)"

python3 - \
  "$EVENT_JSON" \
  "$SEND_JSON" \
  "$SUMMARY" \
  "$before" \
  "$after" \
  "$RUN_ID" \
  "$NOMINAL_MANIFEST_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

event_path, send_path, summary_path, before, after, run_id, runtime_sha = sys.argv[1:]
event = json.loads(Path(event_path).read_text(encoding="utf-8"))
send = json.loads(Path(send_path).read_text(encoding="utf-8"))

assert event["event_id"] == "E1"
assert event["ground_truth"]["command_authorized"] is False
assert event["ground_truth"]["command_syntactically_valid"] is True
assert send["datagrams_sent"] == 1
assert send["packet_hex"] == "18fac000000100dc"
assert int(after) == int(before) + 1

summary = {
    "schema": 1,
    "run_id": run_id,
    "classification": "WP5_E1_RUNTIME_ADAPTER_PASS",
    "scientific_claim_boundary": "event-delivery validation only; no response-policy effectiveness claim",
    "event_id": "E1",
    "authorization_ground_truth": False,
    "command_syntactically_valid": True,
    "datagrams_sent": 1,
    "sample_noop_marker_before": int(before),
    "sample_noop_marker_after": int(after),
    "simulator_command_accepted": True,
    "ci_lab_udp_5012_observed": True,
    "validated_nominal_runtime_pass": True,
    "nominal_runtime_manifest_sha256": runtime_sha,
    "network_internal": True,
    "host_port_published": False,
    "operational_target": False,
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="E1_RUNTIME_ADAPTER_PASS"

echo "event_id=E1"
echo "authorization_ground_truth=false"
echo "command_syntactically_valid=true"
echo "datagrams_sent=1"
echo "sample_noop_marker_before=$before"
echo "sample_noop_marker_after=$after"
echo "simulator_command_accepted=true"
echo "validated_nominal_runtime_pass=true"
echo "nominal_runtime_manifest_sha256=$NOMINAL_MANIFEST_SHA"
echo "policy_effectiveness_claim=false"
