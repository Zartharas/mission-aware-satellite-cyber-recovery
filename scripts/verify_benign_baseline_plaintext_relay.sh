#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBE="$ROOT/scripts/benign_ground_probe_measurement.py"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
RELAY="$ROOT/scripts/benign_plaintext_transport_relay.py"
RUNNER="$ROOT/scripts/run_benign_baseline_plaintext_relay.sh"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
PROJECT="mission-aware-satellite-cyber-recovery"

for file in "$PROBE" "$PREPARER" "$RELAY" "$RUNNER" "$CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

for command in python3 bash docker; do
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

python3 -m py_compile "$PROBE" "$PREPARER" "$RELAY"
python3 "$PROBE" --self-test
python3 "$PREPARER" --self-test
python3 "$RELAY" --self-test
bash -n "$RUNNER"
python3 -m json.tool "$CONTRACT" >/dev/null

python3 - "$CONTRACT" "$RUNNER" "$RELAY" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
runner = Path(sys.argv[2]).read_text(encoding="utf-8")
relay = Path(sys.argv[3]).read_text(encoding="utf-8")

assert contract["contract_version"] == "0.6.0"
assert contract["status"] == "PLAINTEXT_RELAY_RUNNER_VALIDATION_PENDING"
assert contract["event_injection_allowed"] is False
baseline = contract["baseline_transport"]
assert baseline["profile"] == "PLAINTEXT_UDP_RELAY"
assert baseline["scope"] == "nominal_command_telemetry_gate_only"
assert baseline["cryptographic_semantics"] == "DEFERRED"
assert baseline["relay_alias"] == "cryptolib"
assert baseline["relay_alias_role"] == "compatibility_only_not_cryptolib"
assert baseline["allowed_command_hex"] == "18fac000000100dc"
assert baseline["allowed_command_sha256"] == "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"
assert baseline["maximum_command_transmissions"] == 1
assert baseline["event_injection_capability"] is False
assert contract["evidence"]["cryptographic_semantics_claim_allowed"] is False
assert contract["gate"]["required_clean_passes"] == 2
assert contract["gate"]["event_injection_unblocked_after_gate"] is False

transport = contract["transport"]
assert transport["radio_ground_mode"] == "UDP"
assert transport["cfs_ci"]["port"] == 5012
assert transport["cfs_to"]["port"] == 5011
assert transport["ground_to_relay"] == {
    "protocol": "udp", "destination": "cryptolib", "port": 6010
}
assert transport["relay_to_radio"] == {
    "protocol": "udp", "destination": "radio-sim", "port": 8010
}
assert transport["radio_to_relay"] == {
    "protocol": "udp", "destination": "cryptolib", "port": 8011
}
assert transport["relay_to_ground"] == {
    "protocol": "udp", "destination": "ground-probe", "port": 6011
}
assert transport["host_ports_allowed"] is False
assert transport["docker_socket_mount_allowed"] is False
assert transport["external_egress_allowed"] is False

for token in (
    "TCP_GROUND=0",
    "start plaintext-relay cryptolib true",
    "PLAINTEXT_RELAY_VERIFY_ONLY",
    "cryptographic_semantics_status deferred",
    "transport_relay_command_forwarded_count",
    "./support/standalone",
):
    assert token in runner, token
for token in (
    "EXPECTED_COMMAND = bytes.fromhex(\"18fac000000100dc\")",
    "maximum_commands=1",
    "validate_allowed_command",
    "PLAINTEXT_RELAY_INVALID",
):
    assert token in relay, token
PY

project_containers_before="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
project_networks_before="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$project_containers_before" == 0 && "$project_networks_before" == 0 ]] || {
  echo "[ERROR] Existing project-labeled resources found before verification." >&2
  exit 1
}

PLAINTEXT_RELAY_VERIFY_ONLY=1 bash "$RUNNER"

for self_test in \
  "scripts/benign_ground_probe_measurement.py" \
  "scripts/prepare_runtime_radio_config.py" \
  "scripts/benign_plaintext_transport_relay.py"; do
  docker run --rm --platform linux/amd64 --network none \
    --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
    --workdir /work/project \
    "$IMAGE" python3 "$self_test" --self-test
done

project_containers_after="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
project_networks_after="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$project_containers_after" == 0 && "$project_networks_after" == 0 ]] || {
  echo "[ERROR] Verification left project-labeled resources behind." >&2
  exit 1
}

echo "BENIGN_BASELINE_PLAINTEXT_RELAY_VERIFICATION_STATUS=PASS"
