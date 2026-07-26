#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="mission-aware-satellite-cyber-recovery"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
SHIM="$ROOT/scripts/radio_socket_metadata_shim.c"
SELFTEST="$ROOT/scripts/radio_socket_metadata_shim_selftest.c"
TMP=""

cleanup() {
  local rc=$?
  [[ -z "$TMP" ]] || rm -rf "$TMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$CONTRACT" "$SHIM" "$SELFTEST"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m json.tool "$CONTRACT" >/dev/null
python3 - "$CONTRACT" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert contract["contract_version"] == "0.4.0"
assert contract["status"] == "RADIO_SOCKET_METADATA_SHIM_STATIC_VALIDATION_PENDING"
assert contract["scientific_outcome_allowed"] is False
assert contract["event_injection_allowed"] is False
assert contract["command_transmission_allowed"] is False
assert contract["baseline_execution_allowed"] is False
assert contract["cryptographic_semantics_claim_allowed"] is False
shim = contract["radio_socket_metadata_shim"]
assert shim["captures_packet_content"] is False
assert shim["captures_ip_addresses"] is False
assert shim["observed_ingress_local_port"] == 5011
assert shim["observed_egress_destination_port"] == 8011
assert shim["pinned_radio_source_modified"] is False
assert shim["packet_capture_capability_required"] is False
assert shim["host_network_required"] is False
assert shim["docker_socket_mount_required"] is False
assert contract["gate"]["diagnostic_runtime_authorized"] is False
assert contract["gate"]["diagnostic_runtime_attempts_authorized"] == 0
assert contract["gate"]["baseline_run_1_authorized"] is False
assert contract["gate"]["baseline_run_2_authorized"] is False
assert contract["gate"]["event_injection_authorized"] is False
PY

for required in \
  'event=%s' \
  'local_port=%d' \
  'peer_port=%d' \
  'requested=%zu' \
  'result=%zd' \
  'local_port == 5011' \
  'peer_port == 8011'; do
  grep -Fq -- "$required" "$SHIM" || {
    echo "[ERROR] Shim requirement missing: $required" >&2
    exit 1
  }
done

for forbidden in 'payload=' 'payload_sha' 'hex=' 'address=' 'ip_address='; do
  if grep -Fq -- "$forbidden" "$SHIM"; then
    echo "[ERROR] Shim contains forbidden content-capture token: $forbidden" >&2
    exit 1
  fi
done

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

TMP="$(mktemp -d "${TMPDIR:-/tmp}/radio-socket-shim.XXXXXX")"
chmod 755 "$TMP"

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$ROOT/scripts,target=/src,readonly" \
  --mount "type=bind,source=$TMP,target=/out" \
  "$IMAGE" bash -lc '
set -Eeuo pipefail
cc -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared \
  /src/radio_socket_metadata_shim.c \
  -o /out/libradio_socket_metadata_shim.so \
  -ldl
cc -std=c11 -Wall -Wextra -Werror -O2 \
  /src/radio_socket_metadata_shim_selftest.c \
  -o /out/radio_socket_metadata_shim_selftest
RADIO_SOCKET_TRACE_PATH=/out/trace.log \
LD_PRELOAD=/out/libradio_socket_metadata_shim.so \
  /out/radio_socket_metadata_shim_selftest
' | tee "$TMP/selftest-output.txt"

grep -Fxq 'RADIO_SOCKET_METADATA_SHIM_SELF_TEST=PASS' "$TMP/selftest-output.txt" || {
  echo "[ERROR] Shim self-test PASS marker missing." >&2
  exit 1
}
[[ -s "$TMP/libradio_socket_metadata_shim.so" ]] || {
  echo "[ERROR] Shim shared object was not produced." >&2
  exit 1
}
[[ -s "$TMP/trace.log" ]] || {
  echo "[ERROR] Shim trace was not produced." >&2
  exit 1
}

trace_lines="$(wc -l < "$TMP/trace.log" | tr -d ' ')"
recv_count="$(grep -Ec 'event=recvfrom .*local_port=5011 .*requested=16 result=4 errno=0$' "$TMP/trace.log" || true)"
send_count="$(grep -Ec 'event=sendto .*local_port=5011 peer_port=8011 requested=4 result=4 errno=0$' "$TMP/trace.log" || true)"
[[ "$trace_lines" == 2 ]] || {
  echo "[ERROR] Expected exactly two filtered metadata records; found $trace_lines." >&2
  cat "$TMP/trace.log" >&2
  exit 1
}
[[ "$recv_count" == 1 ]] || {
  echo "[ERROR] Expected one UDP 5011 recvfrom metadata record; found $recv_count." >&2
  cat "$TMP/trace.log" >&2
  exit 1
}
[[ "$send_count" == 1 ]] || {
  echo "[ERROR] Expected one UDP 8011 sendto metadata record; found $send_count." >&2
  cat "$TMP/trace.log" >&2
  exit 1
}
if grep -Eqi 'payload|hex=|data=|address=|ip=' "$TMP/trace.log"; then
  echo "[ERROR] Trace contains forbidden packet-content or address material." >&2
  cat "$TMP/trace.log" >&2
  exit 1
fi

after_containers="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
after_networks="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$after_containers" == 0 && "$after_networks" == 0 ]] || {
  echo "[ERROR] Static verification left project-labeled Docker resources." >&2
  exit 1
}

echo "shim_source_sha256=$(shasum -a 256 "$SHIM" | awk '{print $1}')"
echo "shim_selftest_source_sha256=$(shasum -a 256 "$SELFTEST" | awk '{print $1}')"
echo "shim_linux_shared_object_sha256=$(shasum -a 256 "$TMP/libradio_socket_metadata_shim.so" | awk '{print $1}')"
echo "trace_metadata_records=$trace_lines"
echo "recvfrom_5011_records=$recv_count"
echo "sendto_8011_records=$send_count"
echo "docker_network_mode=none"
echo "packet_content_captured=0"
echo "ip_addresses_captured=0"
echo "packet_capture_capability_required=0"
echo "pinned_radio_source_modified=0"
echo "host_network_used=0"
echo "docker_socket_mounted=0"
echo "command_source_present=0"
echo "diagnostic_runtime_launched=0"
echo "RADIO_SOCKET_METADATA_SHIM_STATIC_VERIFICATION_STATUS=PASS"
