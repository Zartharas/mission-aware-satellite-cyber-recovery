#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBE="$ROOT/scripts/benign_ground_probe_measurement.py"
RUNNER="$ROOT/scripts/run_benign_baseline_interface_corrected.sh"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"
SOURCE_CONFIG="$ROOT/external/nos3/sims/build/bin/nos3-simulator.xml"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

for file in "$PROBE" "$RUNNER" "$CONTRACT" "$SOURCE_CONFIG"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PROBE"
python3 "$PROBE" --self-test
bash -n "$RUNNER"
python3 -m json.tool "$CONTRACT" >/dev/null

python3 - "$CONTRACT" "$SOURCE_CONFIG" <<'PY'
import json
import sys
import xml.etree.ElementTree as ET
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

root = ET.parse(sys.argv[2]).getroot()
radio = next(
    simulator
    for simulator in root.findall("./simulators/simulator")
    if (simulator.findtext("name") or "").strip() == "generic-radio-sim"
)
connections = radio.findall("./hardware-model/connections/connection")
fsw = next(c for c in connections if (c.findtext("name") or "").strip() == "fsw")
gsw = next(c for c in connections if (c.findtext("name") or "").strip() == "gsw")
assert (fsw.findtext("ci-port") or "").strip() == "5010"
assert (fsw.findtext("to-port") or "").strip() == "5011"
assert (gsw.findtext("ip") or "").strip() == "cryptolib"
assert (gsw.findtext("cmd-port") or "").strip() == "8010"
assert (gsw.findtext("tlm-port") or "").strip() == "8011"
PY

grep -Fq 'ci_port.text = "5012"' "$RUNNER"
grep -Fq -- '--network-alias active-gs' "$RUNNER"
grep -Fq 'CI_LAB listening on UDP port: 5012' "$RUNNER"
grep -Fq 'TO telemetry output enabled for IP active-gs' "$RUNNER"
grep -Fq 'ground_setup_command_transmissions 0' "$RUNNER"
grep -Fq 'maximum_command_transmissions 1' "$RUNNER"
grep -Fq 'event_injection disabled' "$RUNNER"

if grep -Fq '1880c0000013021d726164696f2d73696d000000000000009313' "$RUNNER"; then
  echo "[ERROR] Corrected runner still contains the deprecated ground setup packet." >&2
  exit 1
fi
if grep -Fq 'transmitted-setup-command.bin' "$PROBE"; then
  echo "[ERROR] Measurement-only probe contains setup-command evidence logic." >&2
  exit 1
fi

for command in docker; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

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

echo "BENIGN_BASELINE_INTERFACE_VERIFICATION_STATUS=PASS"
