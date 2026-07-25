#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBE="$ROOT/scripts/benign_ground_probe.py"
RUNNER="$ROOT/scripts/run_benign_baseline.sh"
WRAPPER="$ROOT/scripts/run_benign_baseline_with_setup.sh"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

for file in "$PROBE" "$RUNNER" "$WRAPPER" "$CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing file: $file" >&2
    exit 1
  }
done

python3 -m json.tool "$CONTRACT" >/dev/null
python3 - "$CONTRACT" <<'PY'
import json
import sys

contract = json.load(open(sys.argv[1], encoding="utf-8"))
assert contract["contract_version"] == "0.4.1"
assert contract["event_injection_allowed"] is False
assert contract["implementation"]["runtime_runner"] == "scripts/run_benign_baseline_with_setup.sh"
setup = contract["setup_command"]
measured = contract["measured_command"]
legacy = contract["command"]
accounting = contract["command_accounting"]
assert setup["name"] == "TO_ENABLE_OUTPUT"
assert setup["maximum_transmissions_per_run"] == 1
assert setup["expected_packet_hex"] == "1880c0000013021d726164696f2d73696d000000000000009313"
assert setup["expected_packet_sha256"] == "c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb"
assert measured["name"] == "SAMPLE_NOOP_CC"
assert measured["maximum_transmissions_per_run"] == 1
assert legacy["compatibility_role"] == "legacy_alias_for_measured_command_used_by_lower_level_runner"
assert legacy["expected_packet_hex"] == measured["expected_packet_hex"]
assert legacy["expected_packet_sha256"] == measured["expected_packet_sha256"]
assert accounting == {
    "setup_command_transmissions": 1,
    "measured_command_transmissions": 1,
    "total_expected_transmissions": 2,
    "setup_command_excluded_from_sample_counter_baseline": True,
    "measured_command_sent_only_after_stable_sample_housekeeping": True,
}
PY

python3 -m py_compile "$PROBE"
python3 "$PROBE" --self-test
bash -n "$RUNNER"
bash -n "$WRAPPER"

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
  "$IMAGE" python3 scripts/benign_ground_probe.py --self-test

grep -Fq '1880c0000013021d726164696f2d73696d000000000000009313' "$PROBE"
grep -Fq 'c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb' "$PROBE"
grep -Fq 'entering OPERATIONAL state' "$WRAPPER"
grep -Fq 'Successfully connected to TCP server!' "$WRAPPER"
grep -Fq 'event_injection=disabled' "$WRAPPER"

echo "BENIGN_BASELINE_SETUP_VERIFICATION_STATUS=PASS"
