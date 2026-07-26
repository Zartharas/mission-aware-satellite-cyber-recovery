#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_RUNNER="$ROOT/scripts/run_benign_baseline_interface_corrected.sh"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
RELAY="$ROOT/scripts/benign_plaintext_transport_relay.py"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"
TEMP_RUNNER=""

cleanup_wrapper() {
  local rc=$?
  [[ -z "$TEMP_RUNNER" ]] || rm -f "$TEMP_RUNNER"
  trap - EXIT
  exit "$rc"
}
trap cleanup_wrapper EXIT

for file in "$SOURCE_RUNNER" "$PREPARER" "$RELAY" "$CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PREPARER" "$RELAY"
python3 "$PREPARER" --self-test >/dev/null
python3 "$RELAY" --self-test >/dev/null
bash -n "$SOURCE_RUNNER"
python3 -m json.tool "$CONTRACT" >/dev/null

python3 - "$CONTRACT" <<'PY'
import json
import sys
from pathlib import Path
contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert contract["contract_version"] == "0.6.0"
assert contract["event_injection_allowed"] is False
assert contract["baseline_transport"]["profile"] == "PLAINTEXT_UDP_RELAY"
assert contract["baseline_transport"]["cryptographic_semantics"] == "DEFERRED"
assert contract["baseline_transport"]["relay_alias"] == "cryptolib"
assert contract["baseline_transport"]["relay_alias_role"] == "compatibility_only_not_cryptolib"
assert contract["baseline_transport"]["allowed_command_sha256"] == "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"
assert contract["baseline_transport"]["maximum_command_transmissions"] == 1
assert contract["transport"]["radio_ground_mode"] == "UDP"
assert contract["transport"]["ground_to_relay"]["port"] == 6010
assert contract["transport"]["relay_to_radio"]["port"] == 8010
assert contract["transport"]["radio_to_relay"]["port"] == 8011
assert contract["transport"]["relay_to_ground"]["port"] == 6011
PY

source_sha_before="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
TEMP_RUNNER="$(mktemp "$ROOT/scripts/.run-benign-plaintext-relay.XXXXXX.sh")"

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
    'PHASE="wp4-benign-baseline-plaintext-relay"',
    "phase",
)
updated = replace_once(
    updated,
    'PROBE_SCRIPT="$ROOT/scripts/benign_ground_probe_measurement.py"\n',
    'PROBE_SCRIPT="$ROOT/scripts/benign_ground_probe_measurement.py"\nRELAY_SCRIPT="$ROOT/scripts/benign_plaintext_transport_relay.py"\n',
    "relay variable",
)
updated = replace_once(
    updated,
    'for file in "$CONTRACT" "$PROBE_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n',
    'for file in "$CONTRACT" "$PROBE_SCRIPT" "$RELAY_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n',
    "required files",
)
updated = replace_once(
    updated,
    'record runtime_radio_ci_port_override 5010_to_5012\n',
    'record runtime_radio_ci_port_override 5010_to_5012\n'
    'record runtime_simulator_config_edit_method bounded_text_single_character\n'
    'record baseline_transport_profile plaintext_udp_relay\n'
    'record cryptographic_semantics_status deferred\n'
    'record transport_relay_alias cryptolib\n'
    'record transport_relay_alias_role compatibility_only_not_cryptolib\n'
    'record transport_relay_maximum_commands 1\n'
    'record transport_relay_allowed_command_sha256 722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd\n',
    "manifest transport fields",
)
updated = replace_once(
    updated,
    'record probe_script_sha256 "$(shasum -a 256 "$PROBE_SCRIPT" | awk \'{print $1}\')"\n',
    'record probe_script_sha256 "$(shasum -a 256 "$PROBE_SCRIPT" | awk \'{print $1}\')"\n'
    'record transport_relay_script_sha256 "$(shasum -a 256 "$RELAY_SCRIPT" | awk \'{print $1}\')"\n',
    "relay hash",
)
updated = replace_once(
    updated,
    'check_container_isolation "$PREFIX-ground-probe"\n\nstart engine nos-engine-server true \\\n',
    'check_container_isolation "$PREFIX-ground-probe"\n\n'
    'start plaintext-relay cryptolib true \\\n'
    '  --network-alias plaintext-relay \\\n'
    '  --mount "type=bind,source=$RELAY_SCRIPT,target=/relay/benign_plaintext_transport_relay.py,readonly" \\\n'
    '  "$IMAGE" python3 -u /relay/benign_plaintext_transport_relay.py \\\n'
    '    --bind-host 0.0.0.0 \\\n'
    '    --ground-command-port 6010 \\\n'
    '    --radio-command-port 8010 \\\n'
    '    --radio-telemetry-port 8011 \\\n'
    '    --ground-telemetry-port 6011 \\\n'
    '    --radio-host radio-sim \\\n'
    '    --ground-host ground-probe \\\n'
    '    --resolve-timeout 45\n'
    'wait_for_log_marker "$PREFIX-plaintext-relay" PLAINTEXT_RELAY_READY 20 plaintext_relay_ready\n'
    'check_container_isolation "$PREFIX-plaintext-relay"\n\n'
    'start engine nos-engine-server true \\\n',
    "relay startup",
)
updated = replace_once(
    updated,
    '--env TCP_GROUND=1 --env MULTI_GDS=0 \\\n',
    '--env TCP_GROUND=0 --env MULTI_GDS=0 \\\n',
    "radio UDP mode",
)
cryptolib_block = '''start cryptolib cryptolib true \\
  --interactive \\
  --env STANDALONE_TCP=1 --env CRYPTO_HOST=0.0.0.0 --env GSWALIAS=ground-probe \\
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/gsw/build \\
  "$IMAGE" ./support/standalone
'''
updated = replace_once(updated, cryptolib_block, "", "CryptoLib launch removal")

udp_wait_function = '''wait_for_udp_listener() {
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
updated = replace_once(updated, 'check_runtime() {\n', udp_wait_function + 'check_runtime() {\n', "UDP wait helper")
updated = replace_once(
    updated,
    'wait_for_tcp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_tcp_8010_listener\n',
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_udp_8010_listener\n',
    "radio command listener",
)
updated = replace_once(
    updated,
    'wait_for_log_marker "$PREFIX-generic-radio-sim" "Successfully connected to TCP server!" 45 radio_cryptolib_downlink\n',
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 5011 45 radio_udp_5011_listener\n',
    "radio downlink listener",
)
updated = replace_once(
    updated,
    'wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs\n',
    'wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs\n'
    'wait_for_log_marker "$PREFIX-plaintext-relay" PLAINTEXT_RELAY_TELEMETRY_FORWARDED 60 plaintext_relay_telemetry_flow\n',
    "functional telemetry readiness",
)
relay_acceptance = '''    relay_logs="$(docker logs "$PREFIX-plaintext-relay" 2>&1 || true)"
    relay_command_received_count="$(grep -Fc 'PLAINTEXT_RELAY_COMMAND_RECEIVED' <<< "$relay_logs" || true)"
    relay_command_forwarded_count="$(grep -Fc 'PLAINTEXT_RELAY_COMMAND_FORWARDED' <<< "$relay_logs" || true)"
    relay_command_hash_match_count="$(awk '/PLAINTEXT_RELAY_COMMAND_FORWARDED/ && /sha256=722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd/ {count++} END {print count+0}' <<< "$relay_logs")"
    relay_telemetry_forwarded_count="$(grep -Fc 'PLAINTEXT_RELAY_TELEMETRY_FORWARDED' <<< "$relay_logs" || true)"
    relay_invalid_count="$(grep -Fc 'PLAINTEXT_RELAY_INVALID' <<< "$relay_logs" || true)"
    [[ "$relay_command_received_count" == 1 ]] || {
      echo "[ERROR] Relay command receive count is $relay_command_received_count; expected 1." >&2
      exit 3
    }
    [[ "$relay_command_forwarded_count" == 1 && "$relay_command_hash_match_count" == 1 ]] || {
      echo "[ERROR] Relay command-forward evidence is incomplete or non-deterministic." >&2
      exit 3
    }
    (( relay_telemetry_forwarded_count >= 1 )) || {
      echo "[ERROR] Relay did not record telemetry forwarding." >&2
      exit 3
    }
    [[ "$relay_invalid_count" == 0 ]] || {
      echo "[ERROR] Relay recorded an invalid condition." >&2
      exit 3
    }
    record transport_relay_command_received_count "$relay_command_received_count"
    record transport_relay_command_forwarded_count "$relay_command_forwarded_count"
    record transport_relay_telemetry_forwarded_log_markers "$relay_telemetry_forwarded_count"
    record transport_relay_invalid_count "$relay_invalid_count"
'''
updated = replace_once(
    updated,
    '    RESULT="BENIGN_BASELINE_PASS"\n',
    relay_acceptance + '    RESULT="BENIGN_BASELINE_PASS"\n',
    "relay acceptance evidence",
)
updated = replace_once(
    updated,
    'echo "[OK] CI_LAB/TO_LAB interface correction and evidence separation remained active."\n',
    'echo "[OK] CI_LAB/TO_LAB plaintext relay and evidence separation remained active."\n',
    "success message",
)

for forbidden in (
    "xml.etree.ElementTree",
    "./support/standalone",
    "STANDALONE_TCP=1",
    "TCP_GROUND=1",
    'forward_loop - Initial = cryptolib',
):
    if forbidden in updated:
        raise SystemExit(f"forbidden legacy transport content remained: {forbidden}")
required_exact_tokens = (
    'TCP_GROUND=0',
    'RELAY_SCRIPT="$ROOT/scripts/benign_plaintext_transport_relay.py"',
    'start plaintext-relay cryptolib true',
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 8010',
    'wait_for_udp_listener "$PREFIX-generic-radio-sim" 5011',
    'wait_for_log_marker "$PREFIX-plaintext-relay" PLAINTEXT_RELAY_TELEMETRY_FORWARDED 60 plaintext_relay_telemetry_flow',
    'baseline_transport_profile plaintext_udp_relay',
    'cryptographic_semantics_status deferred',
    'transport_relay_command_forwarded_count',
)
for token in required_exact_tokens:
    if updated.count(token) != 1:
        raise SystemExit(f"required generated-runner token missing or ambiguous: {token}")

output_path.write_text(updated, encoding="utf-8")
PYWRAP

chmod 700 "$TEMP_RUNNER"
bash -n "$TEMP_RUNNER"

source_sha_after="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Canonical interface runner changed during plaintext-relay preparation." >&2
  exit 1
}

echo "[OK] Generated an allowlisted plaintext-relay runner without modifying the canonical source."
if [[ "${PLAINTEXT_RELAY_VERIFY_ONLY:-0}" == 1 ]]; then
  echo "BENIGN_BASELINE_PLAINTEXT_RELAY_WRAPPER_VERIFICATION_STATUS=PASS"
  exit 0
fi

bash "$TEMP_RUNNER" "$@"
