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

MANIFEST="$RUN_DIR/baseline-manifest.txt"
GROUND="$RUN_DIR/immutable-ground"
ORCH="$GROUND/orchestration"
POLICY="$RUN_DIR/policy-visible"
RUNTIME_CONFIG="$ORCH/runtime-config/nos3-simulator.xml"
SOURCE_CONFIG="$ROOT/external/nos3/sims/build/bin/nos3-simulator.xml"
LIVENESS="$ORCH/liveness.csv"
TERMINAL="$ORCH/terminal-state.txt"

[[ -f "$MANIFEST" ]] || {
  echo "[ERROR] Missing baseline manifest: $MANIFEST" >&2
  exit 1
}

find_log() {
  local suffix="$1"
  find "$ORCH" -maxdepth 1 -type f -name "*-$suffix.log" -print -quit
}

find_inspect() {
  local suffix="$1"
  find "$ORCH" -maxdepth 1 -type f -name "inspect-*-$suffix.json" -print -quit
}

value() {
  awk -F= -v key="$2" '$1 == key {print substr($0,index($0,"=")+1)}' "$1" | tail -n 1
}

show_matches() {
  local title="$1" file="$2" pattern="$3"
  echo
  echo "[$title]"
  if [[ -z "$file" || ! -f "$file" ]]; then
    echo "log_missing=true"
    return
  fi
  echo "log_bytes=$(wc -c < "$file" | tr -d ' ')"
  grep -niE "$pattern" "$file" || true
}

PROBE_LOG="$(find_log ground-probe)"
RELAY_LOG="$(find_log plaintext-relay)"
RADIO_LOG="$(find_log generic-radio-sim)"
CFS_LOG="$(find_log cfs)"
RADIO_INSPECT="$(find_inspect generic-radio-sim)"
RELAY_INSPECT="$(find_inspect plaintext-relay)"

runtime_config_valid=0
active_gs_alias=0
relay_alias=0
radio_udp_5011=0
radio_udp_8010=0
radio_destination_8011=0
radio_time_bus=0
radio_42_connected=0
radio_forward_errors=0
cfs_operational=0
ci_lab_5012=0
to_lab_active_gs=0
sample_initialized=0
relay_ready=0
relay_telemetry=0
relay_command_received=0
relay_command_forwarded=0
relay_invalid=0
probe_ready=0
probe_telemetry=0
probe_command=0
runtime_nonrunning=0
cleanup_clean=0
ground_hash_ok=0
policy_hash_ok=0

if [[ -f "$SOURCE_CONFIG" && -f "$RUNTIME_CONFIG" ]]; then
  runtime_config_valid="$(python3 - "$SOURCE_CONFIG" "$RUNTIME_CONFIG" <<'PY'
import sys
from pathlib import Path
source = Path(sys.argv[1]).read_text(encoding="utf-8")
runtime = Path(sys.argv[2]).read_text(encoding="utf-8")
if len(source) != len(runtime):
    print(0)
    raise SystemExit
changes = [(i, a, b) for i, (a, b) in enumerate(zip(source, runtime)) if a != b]
valid = len(changes) == 1 and changes[0][1:] == ("0", "2") and "<ci-port>5012</ci-port>" in runtime
print(int(valid))
PY
)"
fi

if [[ -n "$RADIO_INSPECT" && -f "$RADIO_INSPECT" ]]; then
  active_gs_alias="$(python3 - "$RADIO_INSPECT" <<'PY'
import json, sys
from pathlib import Path
payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
item=payload[0] if isinstance(payload,list) else payload
aliases=[]
for network in item.get("NetworkSettings",{}).get("Networks",{}).values():
    aliases.extend(network.get("Aliases") or [])
print(int("active-gs" in aliases))
PY
)"
fi

if [[ -n "$RELAY_INSPECT" && -f "$RELAY_INSPECT" ]]; then
  relay_alias="$(python3 - "$RELAY_INSPECT" <<'PY'
import json, sys
from pathlib import Path
payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
item=payload[0] if isinstance(payload,list) else payload
aliases=[]
for network in item.get("NetworkSettings",{}).get("Networks",{}).values():
    aliases.extend(network.get("Aliases") or [])
print(int("cryptolib" in aliases and "plaintext-relay" in aliases))
PY
)"
fi

if [[ -n "$RADIO_LOG" && -f "$RADIO_LOG" ]]; then
  grep -Eq 'radio-sim.*Port = 5011|radio-sim:5011' "$RADIO_LOG" && radio_udp_5011=1 || true
  grep -Eq 'radio-sim.*Port = 8010|radio-sim:8010' "$RADIO_LOG" && radio_udp_8010=1 || true
  grep -Eq 'Initial = cryptolib.*Port = 8011|to cryptolib:8011' "$RADIO_LOG" && radio_destination_8011=1 || true
  grep -Fq 'Now on time bus named command' "$RADIO_LOG" && radio_time_bus=1 || true
  grep -Eq 'Successfully connected TELEMETRY host fortytwo, port 4286|connected.*fortytwo.*4286' "$RADIO_LOG" && radio_42_connected=1 || true
  radio_forward_errors="$(grep -ciE 'only forwarded|Socker bind error|Socket bind error|Invalid IP resolution|Failed to resolve host Cryptolib IP after|recvfrom.*error|sendto.*error' "$RADIO_LOG" || true)"
fi

if [[ -n "$CFS_LOG" && -f "$CFS_LOG" ]]; then
  grep -Fq 'CFE_ES_Main entering OPERATIONAL state' "$CFS_LOG" && cfs_operational=1 || true
  grep -Fq 'CI_LAB listening on UDP port: 5012' "$CFS_LOG" && ci_lab_5012=1 || true
  grep -Fq 'TO telemetry output enabled for IP active-gs' "$CFS_LOG" && to_lab_active_gs=1 || true
  grep -Fq 'SAMPLE App Initialized' "$CFS_LOG" && sample_initialized=1 || true
fi

if [[ -n "$RELAY_LOG" && -f "$RELAY_LOG" ]]; then
  grep -Fq 'PLAINTEXT_RELAY_READY' "$RELAY_LOG" && relay_ready=1 || true
  relay_telemetry="$(grep -Fc 'PLAINTEXT_RELAY_TELEMETRY_FORWARDED' "$RELAY_LOG" || true)"
  relay_command_received="$(grep -Fc 'PLAINTEXT_RELAY_COMMAND_RECEIVED' "$RELAY_LOG" || true)"
  relay_command_forwarded="$(grep -Fc 'PLAINTEXT_RELAY_COMMAND_FORWARDED' "$RELAY_LOG" || true)"
  relay_invalid="$(grep -Fc 'PLAINTEXT_RELAY_INVALID' "$RELAY_LOG" || true)"
fi

if [[ -n "$PROBE_LOG" && -f "$PROBE_LOG" ]]; then
  grep -Fq 'GROUND_PROBE_READY' "$PROBE_LOG" && probe_ready=1 || true
  grep -Eq 'GROUND_PROBE_TELEMETRY|GROUND_PROBE_PRECOMMAND_STABLE' "$PROBE_LOG" && probe_telemetry=1 || true
  grep -Fq 'GROUND_PROBE_COMMAND_SENT' "$PROBE_LOG" && probe_command=1 || true
fi

if [[ -f "$LIVENESS" ]]; then
  runtime_nonrunning="$(awk -F, 'NR > 1 && $4 != "running:0" {count++} END {print count+0}' "$LIVENESS")"
fi

if [[ "$(value "$MANIFEST" cleanup_project_containers_remaining)" == 0 && \
      "$(value "$MANIFEST" cleanup_project_networks_remaining)" == 0 && \
      "$(value "$MANIFEST" evidence_capture_failed)" == 0 && \
      "$(value "$MANIFEST" cleanup_failed)" == 0 ]]; then
  cleanup_clean=1
fi

if [[ -f "$GROUND/sha256-manifest.txt" ]]; then
  (cd "$GROUND" && shasum -a 256 -c sha256-manifest.txt >/dev/null 2>&1) && ground_hash_ok=1 || true
fi
if [[ -f "$POLICY/sha256-manifest.txt" ]]; then
  (cd "$POLICY" && shasum -a 256 -c sha256-manifest.txt >/dev/null 2>&1) && policy_hash_ok=1 || true
fi

echo "PLAINTEXT_RELAY_READINESS_ANALYSIS"
echo "run_dir=$RUN_DIR"
echo

echo "[MANIFEST]"
for key in \
  run_id phase baseline_transport_profile cryptographic_semantics_status \
  plaintext_relay_ready radio_udp_8010_listener radio_udp_5011_listener \
  plaintext_relay_telemetry_flow ground_probe_exit_state ground_probe_classification \
  baseline_status terminal_classification exit_code evidence_capture_failed cleanup_failed \
  cleanup_project_containers_remaining cleanup_project_networks_remaining \
  immutable_ground_hash_failed policy_visible_hash_failed; do
  printf '%s=%s\n' "$key" "$(value "$MANIFEST" "$key")"
done

[[ -f "$TERMINAL" ]] && { echo; echo "[TERMINAL_STATE]"; cat "$TERMINAL"; }

show_matches "PLAINTEXT_RELAY" "$RELAY_LOG" \
  'PLAINTEXT_RELAY_(READY|TELEMETRY_FORWARDED|COMMAND_RECEIVED|COMMAND_FORWARDED|INVALID|STOPPED)'
show_matches "RADIO" "$RADIO_LOG" \
  'Construction complete|Now on time bus|fortytwo|4286|5011|5012|8010|8011|forward_loop|received [0-9]+ bytes|only forwarded|bind error|error|failed|exception'
show_matches "CFS" "$CFS_LOG" \
  'entering OPERATIONAL state|CI_LAB listening|TO telemetry output enabled|active-gs|SAMPLE App Initialized|SAMPLE.*housekeeping|error|failed'
show_matches "GROUND_PROBE" "$PROBE_LOG" \
  'GROUND_PROBE_(READY|TELEMETRY|PRECOMMAND_STABLE|COMMAND_SENT|PASS|FAIL|INVALID|EVIDENCE_HASHED)'

echo
echo "[CONTROL_EVIDENCE]"
echo "runtime_config_single_character_5010_to_5012=$runtime_config_valid"
echo "radio_active_gs_alias_present=$active_gs_alias"
echo "relay_cryptolib_and_plaintext_aliases_present=$relay_alias"
echo "radio_udp_5011_listener_observed=$radio_udp_5011"
echo "radio_udp_8010_listener_observed=$radio_udp_8010"
echo "radio_downlink_destination_8011_observed=$radio_destination_8011"
echo "radio_time_bus_registration_observed=$radio_time_bus"
echo "radio_42_connection_observed=$radio_42_connected"
echo "radio_udp_forward_error_lines=$radio_forward_errors"
echo "cfs_operational_observed=$cfs_operational"
echo "ci_lab_5012_observed=$ci_lab_5012"
echo "to_lab_active_gs_observed=$to_lab_active_gs"
echo "sample_initialized_observed=$sample_initialized"
echo "relay_ready_observed=$relay_ready"
echo "relay_telemetry_forwarded_count=$relay_telemetry"
echo "relay_command_received_count=$relay_command_received"
echo "relay_command_forwarded_count=$relay_command_forwarded"
echo "relay_invalid_count=$relay_invalid"
echo "probe_ready_observed=$probe_ready"
echo "probe_telemetry_observed=$probe_telemetry"
echo "probe_command_sent_observed=$probe_command"
echo "runtime_nonrunning_rows=$runtime_nonrunning"
echo "cleanup_clean=$cleanup_clean"
echo "immutable_ground_hashes_valid=$ground_hash_ok"
echo "policy_visible_hashes_valid=$policy_hash_ok"

if (( runtime_config_valid == 0 || active_gs_alias == 0 || relay_alias == 0 )); then
  diagnosis="RUNTIME_ALIAS_OR_CONFIG_INVALID"
elif (( relay_ready == 0 || radio_udp_5011 == 0 || radio_udp_8010 == 0 )); then
  diagnosis="UDP_ENDPOINT_READINESS_INCOMPLETE"
elif (( cfs_operational == 0 || ci_lab_5012 == 0 || to_lab_active_gs == 0 || sample_initialized == 0 )); then
  diagnosis="CFS_OR_TO_LAB_READINESS_INCOMPLETE"
elif (( relay_telemetry > 0 )); then
  diagnosis="TELEMETRY_REACHED_RELAY_RUNNER_MARKER_TIMING_OR_CAPTURE_MISMATCH"
elif (( radio_destination_8011 == 0 )); then
  diagnosis="RADIO_TO_RELAY_DESTINATION_RESOLUTION_UNCONFIRMED"
elif (( radio_time_bus == 0 || radio_42_connected == 0 )); then
  diagnosis="RADIO_SIMULATION_TIME_FORWARD_QUEUE_UNCONFIRMED"
elif (( radio_forward_errors > 0 )); then
  diagnosis="RADIO_UDP_FORWARDING_ERROR_OBSERVED"
else
  diagnosis="TO_LAB_TO_RADIO_RECEIVE_OR_RADIO_QUEUE_RELEASE_UNRESOLVED"
fi

echo "transport_diagnosis=$diagnosis"
echo "PLAINTEXT_RELAY_READINESS_ANALYSIS_STATUS=COMPLETE"
