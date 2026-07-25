#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/scripts/run_benign_baseline.sh"
PROJECT="mission-aware-satellite-cyber-recovery"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
PREFIX="mascr-$SAFE_ID"
EVIDENCE="$ROOT/artifacts/baselines/$RUN_ID"
MANIFEST="$EVIDENCE/baseline-manifest.txt"
TRIGGER="$EVIDENCE/immutable-ground/probe/start-baseline.trigger"
TRIGGER_WAIT="${SETUP_TRIGGER_WAIT_SECONDS:-90}"
CHILD_PID=""

for command in bash docker grep python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

[[ -f "$RUNNER" ]] || {
  echo "[ERROR] Missing bounded runner: $RUNNER" >&2
  exit 1
}

[[ "$TRIGGER_WAIT" =~ ^[0-9]+$ ]] || {
  echo "[ERROR] SETUP_TRIGGER_WAIT_SECONDS must be an integer." >&2
  exit 1
}
(( TRIGGER_WAIT >= 30 && TRIGGER_WAIT <= 180 )) || {
  echo "[ERROR] SETUP_TRIGGER_WAIT_SECONDS must be 30-180." >&2
  exit 1
}

interrupt_child() {
  if [[ -n "$CHILD_PID" ]] && kill -0 "$CHILD_PID" >/dev/null 2>&1; then
    kill -TERM "$CHILD_PID" >/dev/null 2>&1 || true
    wait "$CHILD_PID" >/dev/null 2>&1 || true
  fi
  exit 130
}
trap interrupt_child INT TERM

RUN_ID="$RUN_ID" \
BASELINE_TIMEOUT_SECONDS="${BASELINE_TIMEOUT_SECONDS:-240}" \
PROBE_READINESS_TIMEOUT_SECONDS="${PROBE_READINESS_TIMEOUT_SECONDS:-150}" \
ACCEPTANCE_TIMEOUT_SECONDS="${ACCEPTANCE_TIMEOUT_SECONDS:-30}" \
bash "$RUNNER" &
CHILD_PID=$!

cfs_name="$PREFIX-cfs"
radio_name="$PREFIX-generic-radio-sim"
deadline=$((SECONDS + TRIGGER_WAIT))
trigger_written=0

while kill -0 "$CHILD_PID" >/dev/null 2>&1; do
  cfs_state="$(docker inspect "$cfs_name" --format '{{.State.Status}}' 2>/dev/null || true)"
  radio_state="$(docker inspect "$radio_name" --format '{{.State.Status}}' 2>/dev/null || true)"
  cfs_logs="$(docker logs "$cfs_name" 2>&1 || true)"
  radio_logs="$(docker logs "$radio_name" 2>&1 || true)"

  if [[ "$cfs_state" == running && "$radio_state" == running ]] && \
     grep -Fq 'entering OPERATIONAL state' <<< "$cfs_logs" && \
     grep -Fq 'Successfully connected to TCP server!' <<< "$radio_logs"; then
    sleep 2
    mkdir -p "$(dirname "$TRIGGER")"
    temporary="$TRIGGER.tmp"
    trigger_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    cat > "$temporary" <<EOF
run_id=$RUN_ID
triggered_utc=$trigger_utc
cfs_readiness=entering_OPERATIONAL_state
radio_cryptolib_telemetry_transport=connected
setup_command=TO_ENABLE_OUTPUT
setup_destination=radio-sim:5011
event_injection=disabled
EOF
    mv "$temporary" "$TRIGGER"
    trigger_written=1
    echo "[OK] Released one recorded TO_ENABLE_OUTPUT setup command after runtime readiness."
    break
  fi

  if (( SECONDS >= deadline )); then
    echo "[ERROR] Runtime readiness markers were not observed within ${TRIGGER_WAIT}s." >&2
    break
  fi
  sleep 1
done

set +e
wait "$CHILD_PID"
child_rc=$?
set -e
CHILD_PID=""

if [[ "$trigger_written" -ne 1 ]]; then
  [[ -f "$MANIFEST" ]] && {
    printf 'setup_wrapper_status=RUN_INVALID\n' >> "$MANIFEST"
    printf 'setup_wrapper_reason=readiness_trigger_not_released\n' >> "$MANIFEST"
    printf 'terminal_classification=RUN_INVALID\n' >> "$MANIFEST"
    printf 'exit_code=3\n' >> "$MANIFEST"
  }
  echo "BENIGN_BASELINE_SETUP_WRAPPER_STATUS=RUN_INVALID" >&2
  exit 3
fi

if [[ "$child_rc" -ne 0 ]]; then
  [[ -f "$MANIFEST" ]] && {
    printf 'setup_wrapper_status=CHILD_NONZERO\n' >> "$MANIFEST"
    printf 'setup_wrapper_child_exit_code=%s\n' "$child_rc" >> "$MANIFEST"
  }
  echo "BENIGN_BASELINE_SETUP_WRAPPER_STATUS=CHILD_NONZERO" >&2
  exit "$child_rc"
fi

PROBE_RESULT="$EVIDENCE/immutable-ground/probe/probe-result.json"
SETUP_PACKET="$EVIDENCE/immutable-ground/probe/transmitted-setup-command.bin"

python3 - "$PROBE_RESULT" "$SETUP_PACKET" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

result_path = Path(sys.argv[1])
setup_path = Path(sys.argv[2])
expected_hex = "1880c0000013021d726164696f2d73696d000000000000009313"
expected_sha = "c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb"

result = json.loads(result_path.read_text(encoding="utf-8"))
setup = result["setup_command"]
measured = result["command"]
assert result["classification"] == "BENIGN_BASELINE_PASS"
assert setup["name"] == "TO_ENABLE_OUTPUT"
assert setup["transmissions"] == 1
assert setup["packet_hex"] == expected_hex
assert setup["packet_sha256"] == expected_sha
assert measured["name"] == "SAMPLE_NOOP_CC"
assert measured["transmissions"] == 1
assert setup_path.read_bytes().hex() == expected_hex
assert hashlib.sha256(setup_path.read_bytes()).hexdigest() == expected_sha
PY

printf 'setup_wrapper_status=PASS\n' >> "$MANIFEST"
printf 'setup_wrapper_trigger_file=immutable-ground/probe/start-baseline.trigger\n' >> "$MANIFEST"
printf 'setup_command_name=TO_ENABLE_OUTPUT\n' >> "$MANIFEST"
printf 'setup_command_packet_hex=1880c0000013021d726164696f2d73696d000000000000009313\n' >> "$MANIFEST"
printf 'setup_command_packet_sha256=c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb\n' >> "$MANIFEST"
printf 'setup_command_transmissions=1\n' >> "$MANIFEST"
printf 'measured_command_transmissions=1\n' >> "$MANIFEST"

echo "BENIGN_BASELINE_SETUP_WRAPPER_STATUS=PASS"
