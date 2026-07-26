#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
WITNESS="$ROOT/scripts/telemetry_path_witness.py"
RUNNER="$ROOT/scripts/run_downlink_path_diagnostic_hardened.sh"
BASE_RUNNER="$ROOT/scripts/run_downlink_path_diagnostic.sh"
BASELINE_CONTRACT="$ROOT/configs/benign-baseline-contract.json"
DIAGNOSTIC_CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
PROJECT="mission-aware-satellite-cyber-recovery"

for file in "$PREPARER" "$WITNESS" "$RUNNER" "$BASE_RUNNER" "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

for command in python3 bash docker shasum; do
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

python3 -m py_compile "$PREPARER" "$WITNESS"
python3 "$PREPARER" --self-test
python3 "$WITNESS" --self-test
bash -n "$BASE_RUNNER"
bash -n "$RUNNER"
python3 -m json.tool "$BASELINE_CONTRACT" >/dev/null
python3 -m json.tool "$DIAGNOSTIC_CONTRACT" >/dev/null

python3 - "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT" "$WITNESS" "$BASE_RUNNER" "$RUNNER" <<'PY'
import json
import sys
from pathlib import Path

baseline = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
diagnostic = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
witness = Path(sys.argv[3]).read_text(encoding="utf-8")
base_runner = Path(sys.argv[4]).read_text(encoding="utf-8")
hardened_runner = Path(sys.argv[5]).read_text(encoding="utf-8")

assert baseline["contract_version"] == "0.6.2"
assert baseline["status"] == "PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False

assert diagnostic["contract_version"] == "0.1.0"
assert diagnostic["status"] == "STATIC_VALIDATION_PENDING"
assert diagnostic["scientific_outcome_allowed"] is False
assert diagnostic["event_injection_allowed"] is False
assert diagnostic["command_transmission_allowed"] is False
assert diagnostic["baseline_execution_allowed"] is False
assert diagnostic["cryptographic_semantics_claim_allowed"] is False
assert diagnostic["gate"]["diagnostic_runtime_authorized"] is False
assert diagnostic["gate"]["baseline_run_1_authorized"] is False
assert diagnostic["gate"]["baseline_run_2_authorized"] is False
assert diagnostic["gate"]["event_injection_authorized"] is False
assert diagnostic["topology"]["to_radio_witness"] == {
    "mode": "proxy",
    "alias": "active-gs",
    "bind_port": 5011,
    "forward_destination": "radio-sim",
    "forward_port": 5011,
    "byte_preserving": True,
}
assert diagnostic["topology"]["radio_egress_witness"] == {
    "mode": "sink",
    "alias": "cryptolib",
    "bind_port": 8011,
    "forwarding": False,
}

for token in (
    "TELEMETRY_PATH_WITNESS_SELF_TEST=PASS",
    "TELEMETRY_WITNESS_RECEIVED",
    "TELEMETRY_WITNESS_FORWARDED",
    "TELEMETRY_WITNESS_INVALID",
    "socket.SOCK_DGRAM",
):
    assert token in witness, token
for forbidden in (
    "SAMPLE_NOOP_CC",
    "18fac000000100dc",
    "command-host",
    "command-port",
    "event injection",
):
    assert forbidden not in witness, forbidden

for token in (
    "start radio-egress-witness cryptolib false",
    "start to-radio-witness active-gs false",
    "command_transmission_allowed false",
    "measured_command_transmissions 0",
    "ground_command_sources 0",
    "DOWNLINK_DIAGNOSTIC_STATUS=PASS",
):
    assert token in base_runner, token
for token in (
    "start radio-egress-witness cryptolib true",
    "start to-radio-witness active-gs true",
    "record expected_runtime_component_count 22",
    "DOWNLINK_DIAGNOSTIC_HARDENED_WRAPPER_VERIFICATION_STATUS=PASS",
):
    assert token in hardened_runner, token
PY

containers_before="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
networks_before="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$containers_before" == 0 && "$networks_before" == 0 ]] || {
  echo "[ERROR] Existing project-labeled resources found before verification." >&2
  exit 1
}

DOWNLINK_DIAGNOSTIC_VERIFY_ONLY=1 bash "$RUNNER"

for self_test in \
  "scripts/prepare_runtime_radio_config.py" \
  "scripts/telemetry_path_witness.py"; do
  docker run --rm --platform linux/amd64 --network none \
    --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
    --workdir /work/project \
    "$IMAGE" python3 "$self_test" --self-test
done

containers_after="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
networks_after="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$containers_after" == 0 && "$networks_after" == 0 ]] || {
  echo "[ERROR] Verification left project-labeled resources behind." >&2
  exit 1
}

echo "DOWNLINK_DIAGNOSTIC_STATIC_VERIFICATION_STATUS=PASS"
