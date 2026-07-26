#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="mission-aware-satellite-cyber-recovery"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
WRAPPER="$ROOT/scripts/run_radio_socket_metadata_diagnostic.sh"
SHIM="$ROOT/scripts/radio_socket_metadata_shim.c"
SHIM_GATE_LOCK="$ROOT/artifacts/radio-socket-metadata-shim-static-gate-lock.txt"
TMP=""

cleanup() {
  local rc=$?
  [[ -z "$TMP" ]] || rm -rf "$TMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$CONTRACT" "$WRAPPER" "$SHIM" "$SHIM_GATE_LOCK"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m json.tool "$CONTRACT" >/dev/null
bash -n "$WRAPPER"
python3 - "$CONTRACT" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert contract["contract_version"] == "0.4.2"
assert contract["status"] == "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VALIDATION_PENDING"
assert contract["scientific_outcome_allowed"] is False
assert contract["event_injection_allowed"] is False
assert contract["command_transmission_allowed"] is False
assert contract["baseline_execution_allowed"] is False
assert contract["cryptographic_semantics_claim_allowed"] is False
assert contract["gate"]["radio_socket_metadata_shim_static_verification"] == "PASS"
assert contract["gate"]["radio_socket_metadata_runtime_wrapper_static_verification"] == "PENDING"
assert contract["gate"]["diagnostic_runtime_authorized"] is False
assert contract["gate"]["diagnostic_runtime_attempts_authorized"] == 0
assert contract["gate"]["baseline_run_1_authorized"] is False
assert contract["gate"]["baseline_run_2_authorized"] is False
assert contract["gate"]["event_injection_authorized"] is False
requirements = contract["runtime_wrapper_requirements"]
assert requirements["shim_mounted_only_into_generic_radio"] is True
assert requirements["trace_path_immutable_ground_only"] is True
assert requirements["command_source_forbidden"] is True
assert requirements["event_injection_forbidden"] is True
PY

lock_value() {
  awk -F= -v key="$2" '$1 == key {print substr($0,index($0,"=")+1)}' "$1" | tail -n 1
}

expected_shim_source_sha="$(lock_value "$SHIM_GATE_LOCK" shim_source_sha256)"
expected_shim_so_sha="$(lock_value "$SHIM_GATE_LOCK" shim_linux_shared_object_sha256)"
[[ "$expected_shim_source_sha" == d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b ]] || {
  echo "[ERROR] Accepted shim source hash lock mismatch." >&2
  exit 1
}
[[ "$expected_shim_so_sha" == 5a1e4f0cb2b5567ee70defa893f7c976453c788b6c9ac70e4f7d646c16223205 ]] || {
  echo "[ERROR] Accepted shim shared-object hash lock mismatch." >&2
  exit 1
}
[[ "$(shasum -a 256 "$SHIM" | awk '{print $1}')" == "$expected_shim_source_sha" ]] || {
  echo "[ERROR] Shim source no longer matches the accepted static gate." >&2
  exit 1
}

before_containers="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
before_networks="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$before_containers" == 0 && "$before_networks" == 0 ]] || {
  echo "[ERROR] Project-labeled Docker resources already exist." >&2
  exit 1
}

docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/radio-metadata-wrapper.XXXXXX")"
chmod 755 "$TMP"

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$SHIM,target=/src/radio_socket_metadata_shim.c,readonly" \
  --mount "type=bind,source=$TMP,target=/out" \
  "$IMAGE" bash -lc '
set -Eeuo pipefail
cc -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared \
  /src/radio_socket_metadata_shim.c \
  -o /out/libradio_socket_metadata_shim.so \
  -ldl
'

[[ -s "$TMP/libradio_socket_metadata_shim.so" ]] || {
  echo "[ERROR] Network-disabled wrapper verification did not produce the shim shared object." >&2
  exit 1
}
actual_shim_so_sha="$(shasum -a 256 "$TMP/libradio_socket_metadata_shim.so" | awk '{print $1}')"
[[ "$actual_shim_so_sha" == "$expected_shim_so_sha" ]] || {
  echo "[ERROR] Runtime-wrapper shim build differs from the accepted component gate." >&2
  exit 1
}

EMITTED="$TMP/generated-radio-socket-metadata-runtime.sh"
RADIO_SOCKET_METADATA_WRAPPER_VERIFY_ONLY=1 \
RADIO_SOCKET_METADATA_EMIT_PATH="$EMITTED" \
bash "$WRAPPER"

[[ -s "$EMITTED" ]] || {
  echo "[ERROR] Metadata wrapper did not emit the generated runtime." >&2
  exit 1
}
bash -n "$EMITTED"

python3 - "$EMITTED" <<'PY'
import ast
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

required = (
    'SOCKET_METADATA_DIR="$GROUND/radio-socket-metadata"',
    'SHIM_BUILD_DIR="$ORCHESTRATION/radio-socket-shim"',
    'EXPECTED_SHIM_SOURCE_SHA256="d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b"',
    'EXPECTED_SHIM_SO_SHA256="5a1e4f0cb2b5567ee70defa893f7c976453c788b6c9ac70e4f7d646c16223205"',
    'docker run --rm --platform linux/amd64 --network none',
    '--env LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so',
    '--env RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log',
    '--mount "type=bind,source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly"',
    '--mount "type=bind,source=$SOCKET_METADATA_DIR,target=/evidence-socket-metadata"',
    'wait_for_socket_trace "$PREFIX-generic-radio-sim" 60 radio_socket_recvfrom_5011',
    'record radio_socket_recvfrom_5011_records "$recv_success"',
    'record radio_socket_sendto_8011_success_records "$send_success"',
    'record transport_diagnosis "$transport_diagnosis"',
    'RESULT="RADIO_SOCKET_METADATA_DIAGNOSTIC_COMPLETE"',
    'RADIO_SOCKET_METADATA_DIAGNOSTIC_STATUS=COMPLETE',
    'record measured_command_transmissions 0',
    'record ground_command_sources 0',
)
for token in required:
    if token not in text:
        raise SystemExit(f"generated runtime requirement missing: {token}")

if text.count('LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so') != 1:
    raise SystemExit("LD_PRELOAD must occur exactly once")
if text.count('RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log') != 1:
    raise SystemExit("socket trace environment must occur exactly once")
if text.count('source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly') != 1:
    raise SystemExit("shim shared-object mount must occur exactly once")

radio_start = text.find('if [[ "$sim" == generic-radio-sim ]]; then')
radio_end = text.find('\n  else\n', radio_start)
if radio_start < 0 or radio_end < 0:
    raise SystemExit("generic-radio start block not found")
radio_block = text[radio_start:radio_end]
for token in (
    'LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so',
    'RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log',
    'source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly',
    'source=$SOCKET_METADATA_DIR,target=/evidence-socket-metadata',
):
    if token not in radio_block:
        raise SystemExit(f"generic-radio block missing: {token}")
outside_radio = text[:radio_start] + text[radio_end:]
for token in (
    'LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so',
    'RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log',
    'source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly',
):
    if token in outside_radio:
        raise SystemExit(f"generic-radio-only token escaped its block: {token}")

for forbidden in (
    '--network host',
    '/var/run/docker.sock',
    '--cap-add NET_RAW',
    '--cap-add NET_ADMIN',
    'tcpdump',
    'tshark',
    'scapy',
    'benign_ground_probe',
    'SAMPLE_NOOP_CC',
    'start cryptolib cryptolib true',
    'STANDALONE_TCP=1',
    '--command-host',
    'transmitted-command',
):
    if forbidden in text:
        raise SystemExit(f"forbidden generated runtime token present: {forbidden}")

lines = text.splitlines()
marker = re.compile(r"<<'(?P<delimiter>PY[A-Z0-9_]*)'")
index = 0
parsed = 0
while index < len(lines):
    match = marker.search(lines[index])
    if match is None:
        index += 1
        continue
    delimiter = match.group("delimiter")
    start = index + 1
    index = start
    while index < len(lines) and lines[index] != delimiter:
        index += 1
    if index >= len(lines):
        raise SystemExit(f"unterminated Python heredoc: {delimiter}")
    ast.parse("\n".join(lines[start:index]) + "\n", filename=f"<{delimiter}>")
    parsed += 1
    index += 1
if parsed < 2:
    raise SystemExit(f"expected at least two generated Python heredocs; found {parsed}")
PY

after_containers="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
after_networks="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$after_containers" == 0 && "$after_networks" == 0 ]] || {
  echo "[ERROR] Wrapper static verification left project-labeled Docker resources." >&2
  exit 1
}

echo "runtime_wrapper_sha256=$(shasum -a 256 "$WRAPPER" | awk '{print $1}')"
echo "generated_runtime_sha256=$(shasum -a 256 "$EMITTED" | awk '{print $1}')"
echo "shim_source_sha256=$expected_shim_source_sha"
echo "shim_linux_shared_object_sha256=$actual_shim_so_sha"
echo "docker_network_mode=none"
echo "shim_mount_scope=generic_radio_only"
echo "trace_evidence_scope=immutable_ground_only"
echo "packet_content_captured=0"
echo "ip_addresses_captured=0"
echo "packet_capture_capability_required=0"
echo "host_network_used=0"
echo "docker_socket_mounted=0"
echo "command_source_present=0"
echo "event_injection_present=0"
echo "diagnostic_runtime_launched=0"
echo "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VERIFICATION_STATUS=PASS"
