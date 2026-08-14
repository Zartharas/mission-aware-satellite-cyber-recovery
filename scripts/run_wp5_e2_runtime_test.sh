#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp5/e2/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
EVENT_JSON="$GROUND/event-instance.json"
SETUP_JSON="$GROUND/setup-result.json"
REPLAY_JSON="$GROUND/replay-result.json"
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
  if [[ "$RESULT" == E2_RUNTIME_ADAPTER_PASS && "$rc" -eq 0 ]]; then
    echo "WP5_E2_RUNTIME_TEST=PASS"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP5_E2_RUNTIME_TEST=FAIL" >&2
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

PYTHONPATH="$ROOT" python3 - "$EVENT_JSON" <<'PY'
import json, sys
from pathlib import Path
from src.mission_recovery.events import materialize_event

event=materialize_event(
    "E2",
    mission_state="M0",
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

count_noop() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

# Establish a quiet pre-setup baseline so unrelated runtime activity cannot
# masquerade as the setup acceptance.
before="$(count_noop)"
sleep 3
quiet_after="$(count_noop)"
[[ "$quiet_after" -eq "$before" ]] || {
  echo "[ERROR] NOOP marker changed during pre-setup quiet window" >&2
  exit 1
}
echo "pre_setup_quiet_baseline=PASS"

# Setup/control: send one harmless, valid NOOP and persist send evidence.
# -i is required because the Python program is supplied on stdin.
docker run --rm -i --platform linux/amd64 \
  --network "$NETWORK" \
  --network-alias e2-setup-adapter \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 - /evidence/setup-result.json <<'PY'
import hashlib, json, socket, sys
from pathlib import Path
from src.mission_recovery.nos3_e1_adapter import build_sample_noop_packet

packet=build_sample_noop_packet()
sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent=sock.sendto(packet, ("nos-fsw", 5012))
sock.close()
assert sent == len(packet)

result={
    "role":"previously_accepted_control_command",
    "target":"nos-fsw:5012",
    "datagrams_sent":1,
    "bytes_sent":sent,
    "packet_hex":packet.hex(),
    "packet_sha256":hashlib.sha256(packet).hexdigest(),
}
Path(sys.argv[1]).write_text(
    json.dumps(result,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
print(json.dumps(result,sort_keys=True))
PY

test -f "$SETUP_JSON" || {
  echo "[ERROR] setup send evidence file missing" >&2
  exit 1
}

python3 - "$SETUP_JSON" <<'PY'
import json, sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert d["role"] == "previously_accepted_control_command"
assert d["datagrams_sent"] == 1
assert d["bytes_sent"] == 8
assert d["packet_hex"] == "18fac000000100dc"
assert d["packet_sha256"] == "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"
print("setup_send_evidence=PASS")
PY

after_setup="$before"
for _ in $(seq 1 15); do
  after_setup="$(count_noop)"
  [[ "$after_setup" -eq $((before + 1)) ]] && break
  sleep 1
done

[[ "$after_setup" -eq $((before + 1)) ]] || {
  echo "[ERROR] setup acceptance marker did not increment exactly once" >&2
  exit 1
}
echo "setup_acceptance_delta=PASS"

# Establish a second quiet window before replay.
sleep 2
pre_replay="$(count_noop)"
[[ "$pre_replay" -eq "$after_setup" ]] || {
  echo "[ERROR] NOOP marker changed during pre-replay quiet window" >&2
  exit 1
}
echo "pre_replay_quiet_baseline=PASS"

# E2 event: resend the exact same packet once.
docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --network-alias e2-replay-adapter \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$EVENT_JSON,target=/event/event.json,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.nos3_e2_adapter \
    --event-json /event/event.json \
    --result-json /evidence/replay-result.json

test -f "$REPLAY_JSON" || {
  echo "[ERROR] replay send evidence file missing" >&2
  exit 1
}

python3 - "$SETUP_JSON" "$REPLAY_JSON" <<'PY'
import json, sys
from pathlib import Path
setup=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
replay=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
assert replay["event_id"] == "E2"
assert replay["role"] == "replay_event"
assert replay["datagrams_sent"] == 1
assert setup["packet_hex"] == replay["packet_hex"]
assert setup["packet_sha256"] == replay["packet_sha256"]
print("replayed_packet_byte_identical=PASS")
PY

after_replay="$after_setup"
for _ in $(seq 1 15); do
  after_replay="$(count_noop)"
  [[ "$after_replay" -eq $((after_setup + 1)) ]] && break
  sleep 1
done

[[ "$after_replay" -eq $((after_setup + 1)) ]] || {
  echo "[ERROR] replay acceptance marker did not increment exactly once" >&2
  exit 1
}
echo "replay_acceptance_delta=PASS"

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed after E2: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"

NOMINAL_MANIFEST_SHA="$(
  shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" |
  awk '{print $1}'
)"

python3 - \
  "$EVENT_JSON" "$SETUP_JSON" "$REPLAY_JSON" "$SUMMARY" \
  "$before" "$after_setup" "$after_replay" "$RUN_ID" "$NOMINAL_MANIFEST_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

event_path, setup_path, replay_path, summary_path, before, after_setup, after_replay, run_id, runtime_sha = sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
setup=json.loads(Path(setup_path).read_text(encoding="utf-8"))
replay=json.loads(Path(replay_path).read_text(encoding="utf-8"))

assert event["event_id"] == "E2"
assert event["ground_truth"]["replay"] is True
assert event["ground_truth"]["command_authorized"] is False
assert setup["datagrams_sent"] == 1
assert replay["datagrams_sent"] == 1
assert setup["packet_sha256"] == replay["packet_sha256"]
assert int(after_setup) == int(before) + 1
assert int(after_replay) == int(after_setup) + 1

summary={
    "schema":1,
    "run_id":run_id,
    "classification":"WP5_E2_RUNTIME_ADAPTER_PASS",
    "scientific_claim_boundary":"replay-delivery validation only; no anti-replay policy effectiveness claim",
    "event_id":"E2",
    "replay_ground_truth":True,
    "replay_authorized":False,
    "command_syntactically_valid":True,
    "pre_setup_quiet_baseline":True,
    "setup_datagrams_sent":1,
    "setup_accepted":True,
    "pre_replay_quiet_baseline":True,
    "replay_datagrams_sent":1,
    "replay_accepted":True,
    "replayed_packet_byte_identical":True,
    "packet_sha256":replay["packet_sha256"],
    "sample_noop_marker_before":int(before),
    "sample_noop_marker_after_setup":int(after_setup),
    "sample_noop_marker_after_replay":int(after_replay),
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "operational_target":False,
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="E2_RUNTIME_ADAPTER_PASS"

echo "event_id=E2"
echo "pre_setup_quiet_baseline=true"
echo "setup_datagrams_sent=1"
echo "setup_accepted=true"
echo "pre_replay_quiet_baseline=true"
echo "replay_datagrams_sent=1"
echo "replay_accepted=true"
echo "replayed_packet_byte_identical=true"
echo "validated_nominal_runtime_pass=true"
echo "policy_effectiveness_claim=false"
