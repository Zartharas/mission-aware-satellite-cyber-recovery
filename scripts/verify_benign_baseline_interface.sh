#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBE="$ROOT/scripts/benign_ground_probe_measurement.py"
ENGINE="$ROOT/scripts/run_benign_baseline_interface_corrected.sh"
RUNNER="$ROOT/scripts/run_benign_baseline_interface_textsafe.sh"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"
SOURCE_CONFIG="$ROOT/external/nos3/sims/build/bin/nos3-simulator.xml"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
TEMP_DIR=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP_DIR" ]] || rm -rf "$TEMP_DIR"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$PROBE" "$ENGINE" "$RUNNER" "$PREPARER" "$CONTRACT" "$SOURCE_CONFIG"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PROBE" "$PREPARER"
python3 "$PROBE" --self-test
python3 "$PREPARER" --self-test
bash -n "$ENGINE"
bash -n "$RUNNER"
python3 -m json.tool "$CONTRACT" >/dev/null

python3 - "$CONTRACT" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert contract["contract_version"] == "0.5.0"
assert contract["event_injection_allowed"] is False
assert contract["telemetry_activation"]["mechanism"] == "SC_RTS001_TO_LAB_OUTPUT_ENABLE"
assert contract["telemetry_activation"]["ground_setup_transmissions"] == 0
assert contract["measured_command"]["name"] == "SAMPLE_NOOP_CC"
assert contract["measured_command"]["maximum_transmissions_per_run"] == 1
assert contract["measured_command"]["expected_packet_hex"] == "18fac000000100dc"
assert contract["command_accounting"]["total_expected_ground_transmissions"] == 1
assert contract["transport"]["cfs_ci"]["application"] == "CI_LAB"
assert contract["transport"]["cfs_ci"]["port"] == 5012
assert contract["transport"]["cfs_to"]["application"] == "TO_LAB"
assert contract["transport"]["cfs_to"]["destination_alias"] == "active-gs"
assert contract["transport"]["cfs_to"]["port"] == 5011
assert contract["transport"]["runtime_radio_interface_override"]["source_ci_port"] == 5010
assert contract["transport"]["runtime_radio_interface_override"]["runtime_ci_port"] == 5012
assert contract["transport"]["host_ports_allowed"] is False
assert contract["transport"]["docker_socket_mount_allowed"] is False
assert contract["transport"]["external_egress_allowed"] is False
PY

TEMP_DIR="$(mktemp -d)"
RUNTIME_CONFIG="$TEMP_DIR/nos3-simulator.xml"
source_sha_before="$(shasum -a 256 "$SOURCE_CONFIG" | awk '{print $1}')"
python3 "$PREPARER" "$SOURCE_CONFIG" "$RUNTIME_CONFIG"
source_sha_after="$(shasum -a 256 "$SOURCE_CONFIG" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Source NOS3 simulator configuration changed during verification." >&2
  exit 1
}

python3 - "$SOURCE_CONFIG" "$RUNTIME_CONFIG" <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8")
runtime = Path(sys.argv[2]).read_text(encoding="utf-8")
assert "<42-css-scale-factor>" in source
assert "<42-css-scale-factor>" in runtime
assert len(source) == len(runtime)
differences = [index for index, pair in enumerate(zip(source, runtime)) if pair[0] != pair[1]]
assert len(differences) == 1, differences
index = differences[0]
assert source[index] == "0"
assert runtime[index] == "2"
marker = "<name>generic-radio-sim</name>"
assert source.count(marker) == 1
assert runtime.count(marker) == 1
start = runtime.rfind("<simulator>", 0, runtime.index(marker))
end = runtime.index("</simulator>", runtime.index(marker)) + len("</simulator>")
radio = runtime[start:end]
assert "<ci-port>5012</ci-port>" in radio
assert "<ci-port>5010</ci-port>" not in radio
assert "<to-port>5011</to-port>" in radio
assert "<ip>cryptolib</ip>" in radio
assert "<cmd-port>8010</cmd-port>" in radio
assert "<tlm-port>8011</tlm-port>" in radio
print("RUNTIME_RADIO_CONFIG_BOUNDED_DIFF_VERIFICATION=PASS")
PY

TEXTSAFE_VERIFY_ONLY=1 bash "$RUNNER"

grep -Fq -- '--network-alias active-gs' "$ENGINE"
grep -Fq 'CI_LAB listening on UDP port: 5012' "$ENGINE"
grep -Fq 'TO telemetry output enabled for IP active-gs' "$ENGINE"
grep -Fq 'ground_setup_command_transmissions 0' "$ENGINE"
grep -Fq 'maximum_command_transmissions 1' "$ENGINE"
grep -Fq 'event_injection disabled' "$ENGINE"
grep -Fq 'prepare_runtime_radio_config.py' "$RUNNER"
grep -Fq 'bounded_text_single_character' "$RUNNER"

if grep -Fq '1880c0000013021d726164696f2d73696d000000000000009313' "$ENGINE"; then
  echo "[ERROR] Corrected runtime engine still contains the deprecated ground setup packet." >&2
  exit 1
fi
if grep -Fq 'transmitted-setup-command.bin' "$PROBE"; then
  echo "[ERROR] Measurement-only probe contains setup-command evidence logic." >&2
  exit 1
fi

command -v docker >/dev/null 2>&1 || {
  echo "[ERROR] Missing command: docker" >&2
  exit 1
}
docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
  --workdir /work/project \
  "$IMAGE" python3 scripts/benign_ground_probe_measurement.py --self-test

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
  --workdir /work/project \
  "$IMAGE" python3 scripts/prepare_runtime_radio_config.py --self-test

echo "BENIGN_BASELINE_INTERFACE_VERIFICATION_STATUS=PASS"
