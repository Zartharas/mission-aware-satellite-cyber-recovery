#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "$RUN_DIR" ]]; then
  RUN_DIR="$(find "$ROOT/artifacts/baselines" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
elif [[ "$RUN_DIR" != /* ]]; then
  RUN_DIR="$ROOT/$RUN_DIR"
fi

[[ -d "$RUN_DIR" ]] || {
  echo "[ERROR] Baseline run directory not found: $RUN_DIR" >&2
  exit 1
}

GROUND="$RUN_DIR/immutable-ground"
ORCH="$GROUND/orchestration"
PROBE="$GROUND/probe"
RESULT="$PROBE/probe-result.json"

[[ -f "$RESULT" ]] || {
  echo "[ERROR] Missing probe result: $RESULT" >&2
  exit 1
}

find_log() {
  local suffix="$1"
  find "$ORCH" -maxdepth 1 -type f -name "*-$suffix.log" -print -quit
}

PROBE_LOG="$(find_log ground-probe)"
CRYPTO_LOG="$(find_log cryptolib)"
RADIO_LOG="$(find_log generic-radio-sim)"
CFS_LOG="$(find_log cfs)"
SETUP_HEX="1880c0000013021d726164696f2d73696d000000000000009313"

echo "BENIGN_BASELINE_TRANSPORT_ANALYSIS"
echo "run_dir=$RUN_DIR"
printf 'probe_log=%s\ncryptolib_log=%s\nradio_log=%s\ncfs_log=%s\n' \
  "$PROBE_LOG" "$CRYPTO_LOG" "$RADIO_LOG" "$CFS_LOG"

python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
setup = result.get("setup_command", {})
measured = result.get("command", {})
print(f"classification={result.get('classification')}")
print(f"reason={result.get('reason')}")
print(f"sample_packets_received={result.get('sample_packets_received')}")
print(f"setup_transmissions={setup.get('transmissions')}")
print(f"setup_packet_sha256={setup.get('packet_sha256')}")
print(f"measured_transmissions={measured.get('transmissions')}")
PY

show_matches() {
  local title="$1"
  local file="$2"
  local pattern="$3"
  echo
  echo "[$title]"
  if [[ -z "$file" || ! -f "$file" ]]; then
    echo "log_missing=true"
    return
  fi
  echo "log_bytes=$(wc -c < "$file" | tr -d ' ')"
  grep -niE "$pattern" "$file" || true
}

show_matches "GROUND_PROBE" "$PROBE_LOG" \
  'GROUND_PROBE_(READY|TRIGGER_OBSERVED|SETUP_COMMAND_SENT|PRECOMMAND_STABLE|COMMAND_SENT|PASS|FAIL|INVALID|EVIDENCE_HASHED)'
show_matches "CRYPTOLIB_TC" "$CRYPTO_LOG" \
  'crypto_standalone_tc_apply|ApplySecurity|TC_APPLY|6010|8010|error|failed|received|encrypted'
show_matches "RADIO_FORWARDING" "$RADIO_LOG" \
  '5010|5011|5012|8010|8011|received [0-9]+ bytes|forwarded|Successfully connected|Connection accepted|error|failed'
show_matches "CFS_RUNTIME" "$CFS_LOG" \
  'entering OPERATIONAL state|CI_LAB listening|TO telemetry output enabled|TO Lab Initialized|active-gs|5012|checksum|invalid|error|failed'

crypto_received=0
crypto_applied=0
ci_lab_5012=0
radio_ci_5010=0
to_lab_active_gs=0
cfs_setup_error=0

if [[ -n "$CRYPTO_LOG" && -f "$CRYPTO_LOG" ]]; then
  grep -Fq "$SETUP_HEX" "$CRYPTO_LOG" && crypto_received=1 || true
  grep -Eq 'crypto_standalone_tc_apply - status = 0, encrypted|ApplySecurity.*status = 0' "$CRYPTO_LOG" && crypto_applied=1 || true
fi

if [[ -n "$RADIO_LOG" && -f "$RADIO_LOG" ]]; then
  grep -Eq 'Port = 5010|to UDP nos-fsw:5010' "$RADIO_LOG" && radio_ci_5010=1 || true
fi

if [[ -n "$CFS_LOG" && -f "$CFS_LOG" ]]; then
  grep -Fq 'CI_LAB listening on UDP port: 5012' "$CFS_LOG" && ci_lab_5012=1 || true
  grep -Fq 'TO telemetry output enabled for IP active-gs' "$CFS_LOG" && to_lab_active_gs=1 || true
  grep -Ei 'TO telemetry output|CI_LAB' "$CFS_LOG" | grep -Eiq 'failed|error|invalid' && cfs_setup_error=1 || true
fi

echo
echo "[HOP_EVIDENCE]"
echo "cryptolib_exact_setup_packet_observed=$crypto_received"
echo "cryptolib_apply_success_observed=$crypto_applied"
echo "radio_uplink_destination_5010_observed=$radio_ci_5010"
echo "ci_lab_listener_5012_observed=$ci_lab_5012"
echo "to_lab_active_gs_activation_observed=$to_lab_active_gs"
echo "cfs_runtime_setup_error_observed=$cfs_setup_error"

if (( radio_ci_5010 == 1 && ci_lab_5012 == 1 && to_lab_active_gs == 1 )); then
  diagnosis="CI_LAB_TO_LAB_RUNTIME_INTERFACE_MISMATCH_CONFIRMED"
elif (( ci_lab_5012 == 1 && radio_ci_5010 == 1 )); then
  diagnosis="CI_LAB_RADIO_UPLINK_PORT_MISMATCH_CONFIRMED"
elif (( to_lab_active_gs == 1 )); then
  diagnosis="TO_LAB_STARTUP_ACTIVATION_CONFIRMED_DOWNLINK_ALIAS_UNCONFIRMED"
elif (( crypto_received == 1 && crypto_applied == 1 )); then
  diagnosis="POST_CRYPTOLIB_UPLINK_OR_CI_PROCESSING_UNCONFIRMED"
elif (( crypto_received == 1 )); then
  diagnosis="CRYPTOLIB_TC_APPLY_UNCONFIRMED_OR_FAILED"
else
  diagnosis="GROUND_TO_CRYPTOLIB_PROCESSING_UNCONFIRMED"
fi

echo "transport_diagnosis=$diagnosis"
echo "BENIGN_BASELINE_TRANSPORT_ANALYSIS_STATUS=COMPLETE"
