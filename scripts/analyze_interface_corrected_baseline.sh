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
PROBE="$GROUND/probe"
POLICY="$RUN_DIR/policy-visible"
RESULT="$PROBE/probe-result.json"
RUNTIME_CONFIG="$ORCH/runtime-config/nos3-simulator.xml"
SOURCE_CONFIG="$ROOT/external/nos3/sims/build/bin/nos3-simulator.xml"

for file in "$MANIFEST" "$RESULT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required evidence: $file" >&2
    exit 1
  }
done

find_log() {
  local suffix="$1"
  find "$ORCH" -maxdepth 1 -type f -name "*-$suffix.log" -print -quit
}

find_inspect() {
  local suffix="$1"
  find "$ORCH" -maxdepth 1 -type f -name "inspect-*-$suffix.json" -print -quit
}

PROBE_LOG="$(find_log ground-probe)"
CRYPTO_LOG="$(find_log cryptolib)"
RADIO_LOG="$(find_log generic-radio-sim)"
CFS_LOG="$(find_log cfs)"
RADIO_INSPECT="$(find_inspect generic-radio-sim)"
LIVENESS="$ORCH/liveness.csv"

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

echo "INTERFACE_CORRECTED_BASELINE_ANALYSIS"
echo "run_dir=$RUN_DIR"
echo "manifest=$MANIFEST"
printf 'probe_log=%s\ncryptolib_log=%s\nradio_log=%s\ncfs_log=%s\nradio_inspect=%s\n' \
  "$PROBE_LOG" "$CRYPTO_LOG" "$RADIO_LOG" "$CFS_LOG" "$RADIO_INSPECT"

echo
echo "[MANIFEST]"
for key in \
  run_id phase telemetry_activation ground_setup_command_transmissions \
  to_lab_destination_alias to_lab_destination_port ci_application ci_listen_port \
  runtime_radio_ci_port_override runtime_simulator_config_edit_method \
  runtime_simulator_config_sha256 ground_probe_exit_state \
  ground_probe_classification baseline_status terminal_classification exit_code \
  cleanup_project_containers_remaining cleanup_project_networks_remaining \
  evidence_capture_failed cleanup_failed immutable_ground_hash_failed policy_visible_hash_failed; do
  printf '%s=%s\n' "$key" "$(value "$MANIFEST" "$key")"
done

echo
echo "[PROBE_RESULT]"
python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
command = result.get("command", {})
activation = result.get("telemetry_activation", {})
print(f"classification={result.get('classification')}")
print(f"reason={result.get('reason')}")
print(f"sample_packets_received={result.get('sample_packets_received')}")
print(f"ground_setup_transmissions={activation.get('ground_setup_transmissions')}")
print(f"measured_transmissions={command.get('transmissions')}")
print(f"command_packet_sha256={command.get('packet_sha256')}")
print(f"before_present={result.get('before') is not None}")
print(f"after_present={result.get('after') is not None}")
if result.get("before") is not None:
    before = result["before"]
    print(f"before_counters={before.get('cmd_count')},{before.get('cmd_err_count')},{before.get('device_err_count')}")
if result.get("after") is not None:
    after = result["after"]
    print(f"after_counters={after.get('cmd_count')},{after.get('cmd_err_count')},{after.get('device_err_count')}")
PY

config_present=0
config_single_diff=0
config_ci_5012=0
active_gs_alias=0
ci_lab_5012=0
to_lab_active_gs=0
radio_uplink_5012=0
radio_downlink_5011=0
radio_cryptolib_tcp=0
probe_ready=0
probe_hk_seen=0
probe_command_sent=0
probe_pass=0
runtime_nonrunning=0
cleanup_clean=0
ground_hash_ok=0
policy_hash_ok=0

if [[ -f "$RUNTIME_CONFIG" && -f "$SOURCE_CONFIG" ]]; then
  config_present=1
  read -r config_single_diff config_ci_5012 < <(
    python3 - "$SOURCE_CONFIG" "$RUNTIME_CONFIG" <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8")
runtime = Path(sys.argv[2]).read_text(encoding="utf-8")
differences = [i for i, pair in enumerate(zip(source, runtime)) if pair[0] != pair[1]]
same_length = len(source) == len(runtime)
single = int(same_length and len(differences) == 1 and source[differences[0]] == "0" and runtime[differences[0]] == "2") if differences else 0
marker = "<name>generic-radio-sim</name>"
ci = 0
if runtime.count(marker) == 1:
    marker_index = runtime.index(marker)
    start = runtime.rfind("<simulator>", 0, marker_index)
    end_marker = runtime.find("</simulator>", marker_index)
    if start >= 0 and end_marker >= 0:
        block = runtime[start:end_marker + len("</simulator>")]
        ci = int("<ci-port>5012</ci-port>" in block)
print(single, ci)
PY
  )
fi

if [[ -n "$RADIO_INSPECT" && -f "$RADIO_INSPECT" ]]; then
  active_gs_alias="$(python3 - "$RADIO_INSPECT" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
item = payload[0] if isinstance(payload, list) else payload
aliases = []
for network in item.get("NetworkSettings", {}).get("Networks", {}).values():
    aliases.extend(network.get("Aliases") or [])
print(int("active-gs" in aliases))
PY
  )"
fi

if [[ -n "$CFS_LOG" && -f "$CFS_LOG" ]]; then
  grep -Fq 'CI_LAB listening on UDP port: 5012' "$CFS_LOG" && ci_lab_5012=1 || true
  grep -Fq 'TO telemetry output enabled for IP active-gs' "$CFS_LOG" && to_lab_active_gs=1 || true
fi

if [[ -n "$RADIO_LOG" && -f "$RADIO_LOG" ]]; then
  grep -Eq 'Port = 5012|to UDP nos-fsw:5012' "$RADIO_LOG" && radio_uplink_5012=1 || true
  grep -Eq 'Port = 5011|UDP radio-sim:5011' "$RADIO_LOG" && radio_downlink_5011=1 || true
  grep -Eq 'Connection accepted from|Successfully connected to TCP server' "$RADIO_LOG" && radio_cryptolib_tcp=1 || true
fi

if [[ -n "$PROBE_LOG" && -f "$PROBE_LOG" ]]; then
  grep -Fq 'GROUND_PROBE_READY' "$PROBE_LOG" && probe_ready=1 || true
  grep -Fq 'GROUND_PROBE_TELEMETRY' "$PROBE_LOG" && probe_hk_seen=1 || true
  grep -Fq 'GROUND_PROBE_PRECOMMAND_STABLE' "$PROBE_LOG" && probe_hk_seen=1 || true
  grep -Fq 'GROUND_PROBE_COMMAND_SENT' "$PROBE_LOG" && probe_command_sent=1 || true
  grep -Fq 'GROUND_PROBE_PASS' "$PROBE_LOG" && probe_pass=1 || true
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

show_matches "GROUND_PROBE" "$PROBE_LOG" \
  'GROUND_PROBE_(READY|TELEMETRY|PRECOMMAND_STABLE|COMMAND_SENT|PASS|FAIL|INVALID|EVIDENCE_HASHED)'
show_matches "RADIO_FORWARDING" "$RADIO_LOG" \
  '5011|5012|8010|8011|TCP|UDP|Connection accepted|Successfully connected|received [0-9]+ bytes|error|failed'
show_matches "CFS_RUNTIME" "$CFS_LOG" \
  'entering OPERATIONAL state|CI_LAB listening|TO telemetry output enabled|active-gs|5012|SAMPLE|checksum|invalid|error|failed'
show_matches "CRYPTOLIB" "$CRYPTO_LOG" \
  '6010|6011|8010|8011|ApplySecurity|ProcessSecurity|received|encrypted|decrypted|error|failed'

echo
echo "[CONTROL_EVIDENCE]"
echo "runtime_config_present=$config_present"
echo "runtime_config_single_character_diff=$config_single_diff"
echo "runtime_config_radio_ci_5012=$config_ci_5012"
echo "radio_active_gs_alias_present=$active_gs_alias"
echo "ci_lab_listener_5012_observed=$ci_lab_5012"
echo "to_lab_active_gs_activation_observed=$to_lab_active_gs"
echo "radio_uplink_destination_5012_observed=$radio_uplink_5012"
echo "radio_downlink_5011_observed=$radio_downlink_5011"
echo "radio_cryptolib_tcp_observed=$radio_cryptolib_tcp"
echo "ground_probe_ready_observed=$probe_ready"
echo "ground_probe_sample_hk_observed=$probe_hk_seen"
echo "ground_probe_command_sent_observed=$probe_command_sent"
echo "ground_probe_pass_observed=$probe_pass"
echo "runtime_nonrunning_rows=$runtime_nonrunning"
echo "cleanup_clean=$cleanup_clean"
echo "immutable_ground_hashes_valid=$ground_hash_ok"
echo "policy_visible_hashes_valid=$policy_hash_ok"

classification="$(python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("classification") or "")
PY
)"
reason="$(python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("reason") or "")
PY
)"
samples="$(python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path
print(int(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("sample_packets_received") or 0))
PY
)"
transmissions="$(python3 - "$RESULT" <<'PY'
import json
import sys
from pathlib import Path
print(int(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("command", {}).get("transmissions") or 0))
PY
)"

echo "probe_reason=$reason"

if (( config_present == 0 || config_single_diff == 0 || config_ci_5012 == 0 )); then
  diagnosis="RUNTIME_INTERFACE_COPY_INVALID_OR_UNCONFIRMED"
elif (( active_gs_alias == 0 )); then
  diagnosis="TO_LAB_ACTIVE_GS_ALIAS_MISSING"
elif (( ci_lab_5012 == 0 )); then
  diagnosis="CI_LAB_5012_READINESS_UNCONFIRMED"
elif (( to_lab_active_gs == 0 )); then
  diagnosis="TO_LAB_ACTIVE_GS_ACTIVATION_UNCONFIRMED"
elif (( radio_uplink_5012 == 0 )); then
  diagnosis="RADIO_UPLINK_5012_OVERRIDE_UNCONFIRMED"
elif (( radio_downlink_5011 == 0 )); then
  diagnosis="RADIO_DOWNLINK_5011_PATH_UNCONFIRMED"
elif (( radio_cryptolib_tcp == 0 )); then
  diagnosis="RADIO_CRYPTOLIB_TCP_PATH_UNCONFIRMED"
elif (( samples == 0 )); then
  diagnosis="CONFIGURED_DOWNLINK_PATH_BUT_SAMPLE_HK_NOT_OBSERVED"
elif (( transmissions == 0 )); then
  diagnosis="SAMPLE_HK_RECEIVED_BUT_STABLE_BASELINE_NOT_ESTABLISHED"
elif [[ "$classification" == "BENIGN_BASELINE_FAIL" ]]; then
  diagnosis="MEASURED_COMMAND_SENT_BUT_ACCEPTANCE_ASSERTION_FAILED"
elif [[ "$classification" == "BENIGN_BASELINE_PASS" ]]; then
  diagnosis="BENIGN_BASELINE_PASS_CONFIRMED"
else
  diagnosis="POST_COMMAND_RUNTIME_OR_EVIDENCE_FAILURE"
fi

echo "transport_diagnosis=$diagnosis"
echo "INTERFACE_CORRECTED_BASELINE_ANALYSIS_STATUS=COMPLETE"
