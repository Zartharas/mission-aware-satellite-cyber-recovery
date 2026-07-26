#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_RUNNER="$ROOT/scripts/run_benign_baseline_interface_corrected.sh"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
WITNESS="$ROOT/scripts/telemetry_path_witness.py"
BASELINE_CONTRACT="$ROOT/configs/benign-baseline-contract.json"
DIAGNOSTIC_CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
TEMP_RUNNER=""

cleanup_wrapper() {
  local rc=$?
  [[ -z "$TEMP_RUNNER" ]] || rm -f "$TEMP_RUNNER"
  trap - EXIT
  exit "$rc"
}
trap cleanup_wrapper EXIT

for file in "$SOURCE_RUNNER" "$PREPARER" "$WITNESS" "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PREPARER" "$WITNESS"
python3 "$PREPARER" --self-test >/dev/null
python3 "$WITNESS" --self-test >/dev/null
bash -n "$SOURCE_RUNNER"
python3 -m json.tool "$BASELINE_CONTRACT" >/dev/null
python3 -m json.tool "$DIAGNOSTIC_CONTRACT" >/dev/null

python3 - "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT" <<'PY'
import json
import os
import sys
from pathlib import Path

baseline = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
diagnostic = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
verify_only = os.environ.get("DOWNLINK_DIAGNOSTIC_VERIFY_ONLY") == "1"

assert baseline["contract_version"] == "0.6.2"
assert baseline["status"] == "PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False

assert diagnostic["contract_version"] == "0.1.0"
assert diagnostic["scientific_outcome_allowed"] is False
assert diagnostic["event_injection_allowed"] is False
assert diagnostic["command_transmission_allowed"] is False
assert diagnostic["baseline_execution_allowed"] is False
assert diagnostic["topology"]["to_radio_witness"]["mode"] == "proxy"
assert diagnostic["topology"]["to_radio_witness"]["alias"] == "active-gs"
assert diagnostic["topology"]["to_radio_witness"]["bind_port"] == 5011
assert diagnostic["topology"]["to_radio_witness"]["forward_destination"] == "radio-sim"
assert diagnostic["topology"]["to_radio_witness"]["forward_port"] == 5011
assert diagnostic["topology"]["radio_egress_witness"]["mode"] == "sink"
assert diagnostic["topology"]["radio_egress_witness"]["alias"] == "cryptolib"
assert diagnostic["topology"]["radio_egress_witness"]["bind_port"] == 8011
assert diagnostic["gate"]["baseline_run_1_authorized"] is False
assert diagnostic["gate"]["baseline_run_2_authorized"] is False
assert diagnostic["gate"]["event_injection_authorized"] is False
if verify_only:
    assert diagnostic["status"] == "STATIC_VALIDATION_PENDING"
    assert diagnostic["gate"]["diagnostic_runtime_authorized"] is False
else:
    assert diagnostic["status"] == "STATIC_GATE_PASS_RUNTIME_PENDING"
    assert diagnostic["gate"]["diagnostic_runtime_authorized"] is True
PY

source_sha_before="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
TEMP_RUNNER="$(mktemp "$ROOT/scripts/.run-downlink-diagnostic.XXXXXX.sh")"

python3 - "$SOURCE_RUNNER" "$TEMP_RUNNER" <<'PYWRAP'
from pathlib import Path
import sys

source_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8")


def replace_once(payload: str, old: str, new: str, label: str) -> str:
    count = payload.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor; found {count}")
    return payload.replace(old, new, 1)


start_marker = 'python3 - "$INOUT/Inp_Sim.txt" "$RUNTIME_SIM_CONFIG" <<\'PY\'\n'
start = text.find(start_marker)
if start < 0 or text.count(start_marker) != 1:
    raise SystemExit("expected exactly one embedded runtime-configuration block")
end_marker = "\nPY\n"
end = text.find(end_marker, start + len(start_marker))
if end < 0:
    raise SystemExit("embedded runtime-configuration block terminator not found")
end += len(end_marker)
replacement = '''python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys

inp_sim = Path(sys.argv[1])
lines = inp_sim.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[index] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
inp_sim.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
PY

python3 "$ROOT/scripts/prepare_runtime_radio_config.py" \\
  "$NOS3/sims/build/bin/nos3-simulator.xml" \\
  "$RUNTIME_SIM_CONFIG"
'''
updated = text[:start] + replacement + text[end:]

updated = replace_once(
    updated,
    'PHASE="wp4-benign-baseline-interface-corrected"',
    'PHASE="wp4-telemetry-only-downlink-diagnostic"',
    "phase",
)
updated = replace_once(
    updated,
    'EVIDENCE="$ROOT/artifacts/baselines/$RUN_ID"',
    'EVIDENCE="$ROOT/artifacts/downlink-diagnostics/$RUN_ID"',
    "evidence directory",
)
if updated.count('RESULT="RUN_INVALID"') != 3:
    raise SystemExit("unexpected RUN_INVALID assignment count")
updated = updated.replace('RESULT="RUN_INVALID"', 'RESULT="DOWNLINK_DIAGNOSTIC_INVALID"')

updated = replace_once(
    updated,
    'CONTRACT="$ROOT/configs/benign-baseline-contract.json"\nPROBE_SCRIPT="$ROOT/scripts/benign_ground_probe_measurement.py"\n',
    'CONTRACT="$ROOT/configs/benign-baseline-contract.json"\n'
    'DIAGNOSTIC_CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"\n'
    'WITNESS_SCRIPT="$ROOT/scripts/telemetry_path_witness.py"\n',
    "diagnostic variables",
)
updated = replace_once(
    updated,
    'for file in "$CONTRACT" "$PROBE_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n',
    'for file in "$CONTRACT" "$DIAGNOSTIC_CONTRACT" "$WITNESS_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n',
    "required files",
)
updated = replace_once(
    updated,
    'python3 "$PROBE_SCRIPT" --self-test >/dev/null\n',
    'python3 "$WITNESS_SCRIPT" --self-test >/dev/null\n',
    "witness self test",
)

contract_marker = 'python3 - "$CONTRACT" <<\'PY\'\n'
contract_start = updated.find(contract_marker)
if contract_start < 0 or updated.count(contract_marker) != 1:
    raise SystemExit("expected exactly one generated-runner contract block")
contract_end = updated.find("\nPY\n", contract_start + len(contract_marker))
if contract_end < 0:
    raise SystemExit("generated-runner contract block terminator not found")
contract_end += len("\nPY\n")
contract_replacement = '''python3 - "$CONTRACT" "$DIAGNOSTIC_CONTRACT" <<'PY'
import json
import sys
baseline=json.load(open(sys.argv[1],encoding="utf-8"))
diagnostic=json.load(open(sys.argv[2],encoding="utf-8"))
assert baseline["contract_version"]=="0.6.2"
assert baseline["status"]=="PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False
assert diagnostic["contract_version"]=="0.1.0"
assert diagnostic["status"]=="STATIC_GATE_PASS_RUNTIME_PENDING"
assert diagnostic["command_transmission_allowed"] is False
assert diagnostic["baseline_execution_allowed"] is False
assert diagnostic["event_injection_allowed"] is False
assert diagnostic["gate"]["diagnostic_runtime_authorized"] is True
assert diagnostic["gate"]["baseline_run_1_authorized"] is False
assert diagnostic["gate"]["baseline_run_2_authorized"] is False
PY
'''
updated = updated[:contract_start] + contract_replacement + updated[contract_end:]

updated = replace_once(
    updated,
    '  "$NOS3/gsw/build/support/standalone"\n',
    '',
    "standalone artifact removal",
)
updated = replace_once(
    updated,
    'record command_name SAMPLE_NOOP_CC\n'
    'record command_packet_hex 18fac000000100dc\n'
    'record command_packet_sha256 722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd\n'
    'record maximum_command_transmissions 1\n',
    'record diagnostic_type telemetry_only_downlink_witness\n'
    'record scientific_outcome_allowed false\n'
    'record command_transmission_allowed false\n'
    'record measured_command_transmissions 0\n'
    'record event_injection disabled\n',
    "diagnostic manifest fields",
)
updated = replace_once(updated, 'record expected_runtime_component_count 21\n', 'record expected_runtime_component_count 20\n', "runtime count")
updated = replace_once(updated, 'record expected_total_component_count 22\n', 'record expected_total_component_count 22\n', "total count")
updated = replace_once(
    updated,
    'record simulator_launch_mode individual_pinned_headless_set_runtime_interface_override\n',
    'record simulator_launch_mode individual_pinned_headless_telemetry_witness\n',
    "launch mode",
)
updated = replace_once(
    updated,
    'record probe_script_sha256 "$(shasum -a 256 "$PROBE_SCRIPT" | awk \'{print $1}\')"\n',
    'record telemetry_witness_script_sha256 "$(shasum -a 256 "$WITNESS_SCRIPT" | awk \'{print $1}\')"\n'
    'record diagnostic_contract_sha256 "$(shasum -a 256 "$DIAGNOSTIC_CONTRACT" | awk \'{print $1}\')"\n',
    "witness hashes",
)

probe_block = '''start ground-probe ground-probe false \\
  --mount "type=bind,source=$PROBE_SCRIPT,target=/probe/benign_ground_probe_measurement.py,readonly" \\
  --mount "type=bind,source=$PROBE_GROUND,target=/evidence-ground" \\
  --mount "type=bind,source=$POLICY,target=/evidence-policy" \\
  "$IMAGE" python3 -u /probe/benign_ground_probe_measurement.py \\
    --run-id "$RUN_ID" \\
    --ground-dir /evidence-ground \\
    --policy-dir /evidence-policy \\
    --telemetry-bind 0.0.0.0 \\
    --telemetry-port 6011 \\
    --command-host cryptolib \\
    --command-port 6010 \\
    --readiness-timeout "$PROBE_READINESS_TIMEOUT" \\
    --acceptance-timeout "$ACCEPTANCE_TIMEOUT" \\
    --minimum-stable 2
wait_for_log_marker "$PREFIX-ground-probe" GROUND_PROBE_READY 20 ground_probe_udp_6011
check_container_isolation "$PREFIX-ground-probe"
'''
witness_block = '''start radio-egress-witness cryptolib false \\
  --network-alias radio-egress-witness \\
  --mount "type=bind,source=$WITNESS_SCRIPT,target=/witness/telemetry_path_witness.py,readonly" \\
  "$IMAGE" python3 -u /witness/telemetry_path_witness.py \\
    --mode sink --bind-host 0.0.0.0 --bind-port 8011
wait_for_log_marker "$PREFIX-radio-egress-witness" "TELEMETRY_WITNESS_READY mode=sink" 20 radio_egress_witness_ready
check_container_isolation "$PREFIX-radio-egress-witness"

start to-radio-witness active-gs false \\
  --network-alias telemetry-witness \\
  --mount "type=bind,source=$WITNESS_SCRIPT,target=/witness/telemetry_path_witness.py,readonly" \\
  "$IMAGE" python3 -u /witness/telemetry_path_witness.py \\
    --mode proxy --bind-host 0.0.0.0 --bind-port 5011 \\
    --forward-host radio-sim --forward-port 5011 --resolve-timeout 45
wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_READY mode=proxy" 20 to_radio_witness_ready
check_container_isolation "$PREFIX-to-radio-witness"
'''
updated = replace_once(updated, probe_block, witness_block, "witness startup")

udp_wait = '''wait_for_udp_listener() {
  local name="$1" port="$2" timeout_seconds="$3" manifest_key="$4"
  local hex_port attempt state
  hex_port="$(printf '%04X' "$port")"
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before UDP port $port became ready." >&2
      return 1
    }
    if docker exec "$name" sh -lc \\
      "awk '\\$2 ~ /:${hex_port}\\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \\
      >/dev/null 2>&1; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not expose UDP listener $port within ${timeout_seconds}s." >&2
  return 1
}

'''
updated = replace_once(updated, 'check_runtime() {\n', udp_wait + 'check_runtime() {\n', "UDP wait helper")
updated = replace_once(
    updated,
    '      --network-alias generic-radio-sim --network-alias active-gs \\\n'
    '      --env TCP_GROUND=1 --env MULTI_GDS=0 \\\n',
    '      --network-alias generic-radio-sim \\\n'
    '      --env TCP_GROUND=0 --env MULTI_GDS=0 \\\n',
    "radio UDP aliases",
)
updated = replace_once(
    updated,
    'wait_for_tcp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_tcp_8010_listener\n',
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_udp_8010_listener\n'
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 5011 45 radio_udp_5011_listener\n',
    "radio UDP listeners",
)
cryptolib_block = '''start cryptolib cryptolib true \\
  --interactive \\
  --env STANDALONE_TCP=1 --env CRYPTO_HOST=0.0.0.0 --env GSWALIAS=ground-probe \\
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/gsw/build \\
  "$IMAGE" ./support/standalone
'''
updated = replace_once(updated, cryptolib_block, '', "CryptoLib launch removal")
updated = replace_once(
    updated,
    'wait_for_log_marker "$PREFIX-generic-radio-sim" "Successfully connected to TCP server!" 45 radio_cryptolib_downlink\n',
    '',
    "legacy TCP readiness removal",
)
updated = replace_once(
    updated,
    'wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs\n',
    'wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs\n'
    'wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_RECEIVED mode=proxy" 60 to_witness_received\n'
    'wait_for_log_marker "$PREFIX-to-radio-witness" "TELEMETRY_WITNESS_FORWARDED mode=proxy" 60 to_witness_forwarded\n'
    'wait_for_log_marker "$PREFIX-radio-egress-witness" "TELEMETRY_WITNESS_RECEIVED mode=sink" 60 radio_egress_received\n',
    "functional diagnostic markers",
)
updated = replace_once(
    updated,
    'active_gs_ip="$(docker inspect "$PREFIX-generic-radio-sim" --format \'{{(index .NetworkSettings.Networks "\'"$NETWORK"\'").IPAddress}}\')"\n'
    '[[ -n "$active_gs_ip" ]] || { echo "[ERROR] Radio container has no project-network address." >&2; exit 1; }\n'
    'record active_gs_radio_ip "$active_gs_ip"\n',
    'active_gs_ip="$(docker inspect "$PREFIX-to-radio-witness" --format \'{{(index .NetworkSettings.Networks "\'"$NETWORK"\'").IPAddress}}\')"\n'
    '[[ -n "$active_gs_ip" ]] || { echo "[ERROR] TO witness has no project-network address." >&2; exit 1; }\n'
    'record active_gs_witness_ip "$active_gs_ip"\n',
    "active-gs witness address",
)

tail_marker = 'record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"\n'
tail_start = updated.find(tail_marker)
if tail_start < 0 or updated.count(tail_marker) != 1:
    raise SystemExit("expected exactly one runtime tail marker")
diagnostic_tail = '''record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_component_count "$(wc -l < "$RUNTIME_NAMES" | tr -d ' ')"
record total_component_count "$(wc -l < "$NAMES" | tr -d ' ')"
check_runtime startup
sleep 10
check_runtime observation

to_logs="$(docker logs "$PREFIX-to-radio-witness" 2>&1 || true)"
egress_logs="$(docker logs "$PREFIX-radio-egress-witness" 2>&1 || true)"
to_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=proxy' <<< "$to_logs" || true)"
to_forwarded="$(grep -Fc 'TELEMETRY_WITNESS_FORWARDED mode=proxy' <<< "$to_logs" || true)"
egress_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=sink' <<< "$egress_logs" || true)"
witness_invalid="$(cat <(printf '%s\\n' "$to_logs") <(printf '%s\\n' "$egress_logs") | grep -Fc 'TELEMETRY_WITNESS_INVALID' || true)"
(( to_received >= 1 )) || { echo "[ERROR] TO witness received no telemetry." >&2; exit 3; }
(( to_forwarded >= 1 )) || { echo "[ERROR] TO witness forwarded no telemetry." >&2; exit 3; }
(( egress_received >= 1 )) || { echo "[ERROR] Radio egress witness received no telemetry." >&2; exit 3; }
[[ "$witness_invalid" == 0 ]] || { echo "[ERROR] Telemetry witness recorded an invalid condition." >&2; exit 3; }
record to_witness_received_packet_markers "$to_received"
record to_witness_forwarded_packet_markers "$to_forwarded"
record radio_egress_received_packet_markers "$egress_received"
record witness_invalid_count "$witness_invalid"
record measured_command_transmissions 0
record ground_command_sources 0
RESULT="DOWNLINK_DIAGNOSTIC_PASS"
record diagnostic_status PASS
check_runtime final
docker ps --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" \\
  --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-running.jsonl"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[OK] TO_LAB telemetry reached the active-gs witness and was forwarded byte-for-byte to the radio."
echo "[OK] Radio egress telemetry reached the cryptolib-alias sink with no command-producing component present."
'''
updated = updated[:tail_start] + diagnostic_tail

cleanup_status = '''  if [[ "$RESULT" == BENIGN_BASELINE_PASS && "$final_rc" -eq 0 ]]; then
    echo "BENIGN_BASELINE_STATUS=PASS"
    echo "[OK] Evidence retained at: $EVIDENCE"
  elif [[ "$RESULT" == BENIGN_BASELINE_FAIL ]]; then
    echo "BENIGN_BASELINE_STATUS=FAIL" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  else
    echo "BENIGN_BASELINE_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
'''
diagnostic_status = '''  if [[ "$RESULT" == DOWNLINK_DIAGNOSTIC_PASS && "$final_rc" -eq 0 ]]; then
    echo "DOWNLINK_DIAGNOSTIC_STATUS=PASS"
    echo "[OK] Evidence retained at: $EVIDENCE"
  else
    echo "DOWNLINK_DIAGNOSTIC_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
'''
updated = replace_once(updated, cleanup_status, diagnostic_status, "cleanup terminal output")

for forbidden in (
    "benign_ground_probe_measurement.py",
    "GROUND_PROBE_READY",
    "SAMPLE_NOOP_CC",
    "transmitted-command",
    "start cryptolib cryptolib true",
    "STANDALONE_TCP=1",
    "TCP_GROUND=1",
    "BENIGN_BASELINE_STATUS=",
):
    if forbidden in updated:
        raise SystemExit(f"forbidden command or baseline content remained: {forbidden}")
required = (
    'start radio-egress-witness cryptolib false',
    'start to-radio-witness active-gs false',
    '--mode sink --bind-host 0.0.0.0 --bind-port 8011',
    '--mode proxy --bind-host 0.0.0.0 --bind-port 5011',
    '--forward-host radio-sim --forward-port 5011',
    'TCP_GROUND=0',
    'TELEMETRY_WITNESS_RECEIVED mode=proxy',
    'TELEMETRY_WITNESS_FORWARDED mode=proxy',
    'TELEMETRY_WITNESS_RECEIVED mode=sink',
    'measured_command_transmissions 0',
    'ground_command_sources 0',
    'DOWNLINK_DIAGNOSTIC_STATUS=PASS',
)
for token in required:
    if token not in updated:
        raise SystemExit(f"required diagnostic token missing: {token}")

output_path.write_text(updated, encoding="utf-8")
PYWRAP

chmod 700 "$TEMP_RUNNER"
bash -n "$TEMP_RUNNER"
source_sha_after="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Canonical interface runner changed during diagnostic preparation." >&2
  exit 1
}

echo "[OK] Generated a telemetry-only downlink diagnostic runner without modifying the canonical source."
if [[ "${DOWNLINK_DIAGNOSTIC_VERIFY_ONLY:-0}" == 1 ]]; then
  echo "DOWNLINK_DIAGNOSTIC_WRAPPER_VERIFICATION_STATUS=PASS"
  exit 0
fi

bash "$TEMP_RUNNER" "$@"
