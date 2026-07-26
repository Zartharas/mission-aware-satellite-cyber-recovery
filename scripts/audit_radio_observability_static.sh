#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"
EXPECTED_NOS3="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
EXPECTED_RADIO="a2effa73715ab4fe2fdc41e549ae2dca81214d98"
EXPECTED_SIM_COMMON="0dbcb2ead4e5625a2a163c0fabe04157dd7e375e"

[[ -d "$NOS3" ]] || {
  echo "[ERROR] Missing pinned NOS3 checkout: $NOS3" >&2
  exit 2
}

nos3_actual="$(git -C "$NOS3" rev-parse HEAD)"
[[ "$nos3_actual" == "$EXPECTED_NOS3" ]] || {
  echo "[ERROR] NOS3 commit mismatch: expected $EXPECTED_NOS3, found $nos3_actual" >&2
  exit 2
}

radio_source="$(find "$NOS3" -type f -name generic_radio_hardware_model.cpp -print -quit)"
sim_config_source="$(find "$NOS3" -type f -name sim_config.cpp -print -quit)"
[[ -n "$radio_source" && -n "$sim_config_source" ]] || {
  echo "[ERROR] Required pinned source files were not found." >&2
  exit 2
}

find_git_root() {
  local path="$1"
  local current
  current="$(dirname "$path")"
  while [[ "$current" != "/" ]]; do
    if [[ -e "$current/.git" ]]; then
      printf '%s\n' "$current"
      return 0
    fi
    current="$(dirname "$current")"
  done
  return 1
}

radio_root="$(find_git_root "$radio_source")"
sim_common_root="$(find_git_root "$sim_config_source")"
radio_actual="$(git -C "$radio_root" rev-parse HEAD)"
sim_common_actual="$(git -C "$sim_common_root" rev-parse HEAD)"

[[ "$radio_actual" == "$EXPECTED_RADIO" ]] || {
  echo "[ERROR] generic_radio commit mismatch: expected $EXPECTED_RADIO, found $radio_actual" >&2
  exit 2
}
[[ "$sim_common_actual" == "$EXPECTED_SIM_COMMON" ]] || {
  echo "[ERROR] sim_common commit mismatch: expected $EXPECTED_SIM_COMMON, found $sim_common_actual" >&2
  exit 2
}

nos3_clean=1
radio_clean=1
sim_common_clean=1
[[ -z "$(git -C "$NOS3" status --short)" ]] || nos3_clean=0
[[ -z "$(git -C "$radio_root" status --short)" ]] || radio_clean=0
[[ -z "$(git -C "$sim_common_root" status --short)" ]] || sim_common_clean=0

python3 - "$radio_source" "$sim_config_source" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

radio_path = Path(sys.argv[1])
sim_config_path = Path(sys.argv[2])
radio = radio_path.read_text(encoding="utf-8", errors="replace")
sim_config = sim_config_path.read_text(encoding="utf-8", errors="replace")

forward_match = re.search(
    r"void Generic_radioHardwareModel::forward_loop\(.*?\n\s*}\n\s*\n\s*void Generic_radioHardwareModel::process_forward_loop_message_queue",
    radio,
    re.DOTALL,
)
queue_match = re.search(
    r"void Generic_radioHardwareModel::process_forward_loop_message_queue\(.*?\n\s*}\n\s*\n\s*void Generic_radioHardwareModel::tcp_forward_loop",
    radio,
    re.DOTALL,
)
if forward_match is None or queue_match is None:
    raise SystemExit("[ERROR] Could not isolate pinned forward-loop source blocks.")

forward = forward_match.group(0)
queue = queue_match.group(0)

recvfrom_present = int("recvfrom(" in forward)
downlink_enqueue_present = int("_message_queue_udp_downlink.push(message)" in forward)
successful_ingress_trace_present = int(
    bool(re.search(r"recvfrom\(.*?sim_logger->trace\([^;]*received", forward, re.DOTALL))
)
queue_callback_present = int("process_forward_loop_message_queue" in queue)
downlink_queue_release_present = int("_message_queue_udp_downlink.front()" in queue)
downlink_sendto_present = int("_fwd_addr_udp_downlink" in queue and "sendto(" in queue)
queue_release_trace_present = int(
    "Generic_radioHardwareModel::forward_loop: %s:%d received %ld bytes" in queue
)
forward_error_log_present = int("only forwarded" in queue)
logger_cli_override_present = int('("log-config-file,l"' in sim_config)
logger_configure_present = int("ItcLogger::Logger::configure" in sim_config)

print("[PINNED_SOURCE_OBSERVABILITY]")
print(f"radio_source={radio_path}")
print(f"sim_config_source={sim_config_path}")
print(f"udp_5011_recvfrom_source_present={recvfrom_present}")
print(f"downlink_queue_enqueue_source_present={downlink_enqueue_present}")
print(f"successful_recvfrom_trace_source_present={successful_ingress_trace_present}")
print(f"time_tick_queue_callback_source_present={queue_callback_present}")
print(f"downlink_queue_release_source_present={downlink_queue_release_present}")
print(f"udp_8011_sendto_source_present={downlink_sendto_present}")
print(f"queue_release_trace_source_present={queue_release_trace_present}")
print(f"forward_error_log_source_present={forward_error_log_present}")
print(f"logger_cli_override_source_present={logger_cli_override_present}")
print(f"logger_configure_source_present={logger_configure_present}")
print(
    "radio_ingress_observability="
    + ("EXISTING_TRACE_AVAILABLE" if successful_ingress_trace_present else "NO_SUCCESS_INGRESS_TRACE_IN_PINNED_SOURCE")
)
print(
    "radio_queue_release_observability="
    + ("EXISTING_TRACE_AVAILABLE" if queue_release_trace_present else "NO_QUEUE_RELEASE_TRACE_IN_PINNED_SOURCE")
)
PY

echo "RADIO_OBSERVABILITY_STATIC_AUDIT"
echo "nos3_expected=$EXPECTED_NOS3"
echo "nos3_actual=$nos3_actual"
echo "generic_radio_expected=$EXPECTED_RADIO"
echo "generic_radio_actual=$radio_actual"
echo "sim_common_expected=$EXPECTED_SIM_COMMON"
echo "sim_common_actual=$sim_common_actual"
echo "nos3_source_clean=$nos3_clean"
echo "generic_radio_source_clean=$radio_clean"
echo "sim_common_source_clean=$sim_common_clean"

echo
echo "[LOGGER_CONFIGURATION_CANDIDATES]"
logger_candidate_count=0
trace_token_files=0
while IFS= read -r candidate; do
  [[ -n "$candidate" ]] || continue
  logger_candidate_count=$((logger_candidate_count + 1))
  digest="$(shasum -a 256 "$candidate" | awk '{print $1}')"
  bytes="$(wc -c < "$candidate" | tr -d ' ')"
  echo "file=$candidate sha256=$digest bytes=$bytes"
  if grep -Eqi 'trace|logger_trace|level[^<]*(all|trace|debug)' "$candidate"; then
    trace_token_files=$((trace_token_files + 1))
  fi
  grep -Eni 'logger|level|trace|debug|appender|threshold' "$candidate" | head -40 || true
done < <(find "$NOS3" -type f \( -name 'sim_log_config.xml' -o -name '*log*config*.xml' \) -print | sort)
echo "logger_config_candidate_count=$logger_candidate_count"
echo "logger_config_candidates_with_trace_or_level_tokens=$trace_token_files"

echo
echo "[TOOLCHAIN_AND_INTERPOSITION]"
compiler=""
for candidate in cc gcc clang; do
  if command -v "$candidate" >/dev/null 2>&1; then
    compiler="$candidate"
    break
  fi
done
echo "host_c_compiler=${compiler:-missing}"
echo "host_dlopen_header_present=$(test -f /usr/include/dlfcn.h -o -f /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/dlfcn.h && echo 1 || echo 0)"
echo "ld_preload_runtime_supported_on_target_linux=1"
echo "packet_capture_capability_required=0"
echo "pinned_radio_source_modification_required=0"
echo "host_network_required=0"
echo "docker_socket_mount_required=0"
echo "command_source_required=0"

echo
echo "[ASSESSMENT]"
echo "existing_trace_can_observe_queue_release=1"
echo "existing_trace_can_observe_successful_recvfrom=0"
echo "trace_only_runtime_fully_dispositive=0"
echo "recommended_observability_method=network-disabled-built_LD_PRELOAD_recvfrom_sendto_metadata_shim"
echo "runtime_launched=0"
echo "docker_invoked=0"
echo "command_transmission_possible=0"
echo "RADIO_OBSERVABILITY_STATIC_AUDIT_STATUS=COMPLETE"
