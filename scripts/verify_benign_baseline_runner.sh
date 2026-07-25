#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/scripts/run_benign_baseline.sh"
PROBE="$ROOT/scripts/benign_ground_probe.py"
CONTRACT="$ROOT/configs/benign-baseline-contract.json"

for command in bash python3 grep awk; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

for file in "$RUNNER" "$PROBE" "$CONTRACT"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

bash -n "$RUNNER"
python3 -m py_compile "$PROBE"
python3 "$PROBE" --self-test
python3 -m json.tool "$CONTRACT" >/dev/null

required_markers=(
  'PHASE="wp4-benign-baseline"'
  'record event_injection disabled'
  'record maximum_command_transmissions 1'
  'record expected_runtime_component_count 21'
  'record expected_total_component_count 22'
  'docker network create --driver bridge --internal'
  '--env STANDALONE_TCP=1 --env CRYPTO_HOST=0.0.0.0 --env GSWALIAS=ground-probe'
  'start ground-probe ground-probe false'
  'check_container_isolation "$PREFIX-ground-probe"'
  'BENIGN_BASELINE_STATUS=PASS'
)
for marker in "${required_markers[@]}"; do
  grep -Fq -- "$marker" "$RUNNER" || {
    echo "[ERROR] Runner safety marker missing: $marker" >&2
    exit 1
  }
done

if grep -Eq -- '--network([=[:space:]]+)host|--privileged|--publish([=[:space:]])|-p[[:space:]][0-9]' "$RUNNER"; then
  echo "[ERROR] Runner contains a prohibited Docker option." >&2
  exit 1
fi

probe_line="$(grep -nF 'start ground-probe ground-probe false' "$RUNNER" | head -n 1 | cut -d: -f1)"
cryptolib_line="$(grep -nF 'start cryptolib cryptolib true' "$RUNNER" | head -n 1 | cut -d: -f1)"
cfs_line="$(grep -nF 'start cfs nos-fsw true' "$RUNNER" | head -n 1 | cut -d: -f1)"
[[ "$probe_line" -lt "$cryptolib_line" && "$cryptolib_line" -lt "$cfs_line" ]] || {
  echo "[ERROR] Ground-probe, CryptoLib, and cFS startup order is incorrect." >&2
  exit 1
}

python3 - "$CONTRACT" <<'PY'
import json
import sys

contract = json.load(open(sys.argv[1], encoding="utf-8"))
assert contract["event_injection_allowed"] is False
assert contract["command"]["maximum_transmissions_per_run"] == 1
assert contract["command"]["expected_packet_hex"] == "18fac000000100dc"
assert contract["assertions"]["acceptance_timeout_seconds"] == 30
assert contract["transport"]["host_ports_allowed"] is False
assert contract["transport"]["docker_socket_mount_allowed"] is False
assert contract["transport"]["external_egress_allowed"] is False
PY

echo "BENIGN_BASELINE_RUNNER_VERIFICATION_STATUS=PASS"
