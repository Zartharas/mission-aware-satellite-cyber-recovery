#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: bash scripts/audit_radio_queue_eligibility_and_time_callback.sh artifacts/downlink-diagnostics/<run-id>" >&2
  exit 2
fi

if [[ "$RUN_DIR" != /* ]]; then
  RUN_DIR="$ROOT/$RUN_DIR"
fi

[[ -d "$RUN_DIR" ]] || {
  echo "[ERROR] Retained run directory not found: $RUN_DIR" >&2
  exit 2
}

python3 - "$ROOT" "$RUN_DIR" <<'PY'
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
run_dir = Path(sys.argv[2]).resolve()
orch = run_dir / "immutable-ground" / "orchestration"
external = root / "external" / "nos3"

EXPECTED = {
    "nos3": "5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
    "generic_radio": "a2effa73715ab4fe2fdc41e549ae2dca81214d98",
    "sim_common": "0dbcb2ead4e5625a2a163c0fabe04157dd7e375e",
    "nos_time_driver": "0c097273431cf8a4882559518b704d8c8621b74f",
}


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_kv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            values[key] = value
    return values


def first_glob(pattern: str) -> Path | None:
    return next(iter(sorted(orch.glob(pattern))), None)


def first_source(filename: str) -> Path | None:
    return next(iter(sorted(external.rglob(filename))), None)


def git_root(path: Path | None) -> Path | None:
    if path is None:
        return None
    current = path.parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def git_head(path: Path | None) -> str:
    repository = git_root(path)
    if repository is None:
        return ""
    try:
        return subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def inspect_aliases(path: Path | None) -> set[str]:
    if path is None or not path.is_file():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    networks = payload.get("NetworkSettings", {}).get("Networks", {}) if isinstance(payload, dict) else {}
    aliases: set[str] = set()
    for details in networks.values():
        if isinstance(details, dict):
            aliases.update(alias for alias in details.get("Aliases") or [] if isinstance(alias, str))
    return aliases


def xml_value(block: str, tag: str) -> str:
    match = re.search(rf"<{re.escape(tag)}>\s*([^<]+?)\s*</{re.escape(tag)}>", block)
    return match.group(1).strip() if match else ""


def isolate_function(text: str, start_name: str, next_name: str) -> str:
    match = re.search(
        rf"void\s+Generic_radioHardwareModel::{re.escape(start_name)}\(.*?\n\s*}}\n\s*\n\s*void\s+Generic_radioHardwareModel::{re.escape(next_name)}",
        text,
        re.DOTALL,
    )
    return match.group(0) if match else ""


manifest = parse_kv(run_dir / "baseline-manifest.txt")
runtime_xml_path = orch / "runtime-config" / "nos3-simulator.xml"
runtime_xml = read_text(runtime_xml_path)
radio_log = read_text(first_glob("*-generic-radio-sim.log"))
time_log = read_text(first_glob("*-time.log"))
engine_log = read_text(first_glob("*-engine.log"))
trace_path = run_dir / "immutable-ground" / "radio-socket-metadata" / "radio-socket-metadata.log"
trace = read_text(trace_path)
engine_inspect = first_glob("inspect-*-engine.json")

radio_source_path = first_source("generic_radio_hardware_model.cpp")
provider_source_path = first_source("generic_radio_42_data_provider.cpp")
sim_common_path = first_source("sim_i_hardware_model.hpp")
time_driver_path = first_source("time_driver.cpp")

for label, path in (
    ("generic_radio_hardware_model.cpp", radio_source_path),
    ("generic_radio_42_data_provider.cpp", provider_source_path),
    ("sim_i_hardware_model.hpp", sim_common_path),
    ("time_driver.cpp", time_driver_path),
):
    if path is None:
        raise SystemExit(f"[ERROR] Missing pinned source: {label}")

nos3_head = subprocess.check_output(
    ["git", "-C", str(external), "rev-parse", "HEAD"],
    text=True,
    stderr=subprocess.DEVNULL,
).strip()
heads = {
    "nos3": nos3_head,
    "generic_radio": git_head(radio_source_path),
    "sim_common": git_head(sim_common_path),
    "nos_time_driver": git_head(time_driver_path),
}
for key, expected in EXPECTED.items():
    if heads[key] != expected:
        raise SystemExit(f"[ERROR] {key} commit mismatch: expected {expected}, found {heads[key]}")

radio_source = read_text(radio_source_path)
provider_source = read_text(provider_source_path)
sim_common_source = read_text(sim_common_path)
time_driver_source = read_text(time_driver_path)

radio_start = runtime_xml.find("<name>generic-radio-sim</name>")
if radio_start < 0:
    raise SystemExit("[ERROR] Retained runtime generic-radio block not found")
radio_end = runtime_xml.find("</simulator>", radio_start)
if radio_end < 0:
    raise SystemExit("[ERROR] Retained runtime generic-radio block is unterminated")
radio_block = runtime_xml[radio_start:radio_end]

criteria = xml_value(radio_block, "downlink-close-criteria")
delay_on = xml_value(radio_block, "downlink-delay-on").lower()
comm_downlink = xml_value(radio_block, "comm-downlink")
fsw_to_port = xml_value(radio_block, "to-port")
gsw_tlm_port = xml_value(radio_block, "tlm-port")
gsw_ip = xml_value(radio_block, "ip")
common_connection = xml_value(runtime_xml, "nos-connection-string")
override_connection = xml_value(runtime_xml, "nos-connection-string-override")

forward = isolate_function(radio_source, "forward_loop", "process_forward_loop_message_queue")
callback = isolate_function(radio_source, "process_forward_loop_message_queue", "tcp_forward_loop")
if not forward or not callback:
    raise SystemExit("[ERROR] Could not isolate pinned generic-radio queue functions")

source_provider_reads_config = all(
    token in provider_source
    for token in (
        'config.get("simulator.hardware-model.data-provider.downlink-close-criteria", "none")',
        'config.get("simulator.hardware-model.data-provider.downlink-delay-on", false)',
    )
)
source_none_allows = 'else { // downlink_close_criteria == "none" or anything else\n                    communication_capable = true;' in forward
source_delay_zero_default = "delay = 0;" in forward
source_downlink_enqueue = "_message_queue_udp_downlink.push(message)" in forward
source_enqueue_after_eligibility = forward.find("if (status != -1 && communication_capable)") < forward.find("_message_queue_udp_downlink.push(message)")
source_timestamp_from_bus = "_time_bus->get_time()" in forward and "message.time_to_send" in forward
source_callback_registered = "add_time_tick_callback(std::bind(&Generic_radioHardwareModel::process_forward_loop_message_queue" in radio_source
source_callback_downlink_queue = "while(!_message_queue_udp_downlink.empty())" in callback
source_callback_due_compare = "message.time_to_send <= _absolute_start_time + _sim_microseconds_per_tick * time / 1000000.0" in callback
source_callback_sendto = "_fwd_addr_udp_downlink" in callback and "sendto(" in callback
source_time_parameters_shared = all(
    token in sim_common_source
    for token in (
        '_absolute_start_time(config.get("common.absolute-start-time"',
        '_sim_microseconds_per_tick(config.get("common.sim-microseconds-per-tick"',
    )
)
source_time_driver_sets_time = "time_bus->set_time(_time_counter)" in time_driver_source

trace_recv = len(re.findall(r"event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$", trace, flags=re.MULTILINE))
trace_send_success = len(re.findall(r"event=sendto .*peer_port=8011 .*result=[1-9][0-9]* errno=0$", trace, flags=re.MULTILINE))
trace_send_failure = len(re.findall(r"event=sendto .*peer_port=8011 .*result=-1 errno=[1-9][0-9]*$", trace, flags=re.MULTILINE))

ansi = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
clean_time_log = ansi.sub("", time_log)
tick_values = [int(value) for value in re.findall(r"tick\s*=\s*(\d+)", clean_time_log)]
time_tick_min = min(tick_values) if tick_values else -1
time_tick_max = max(tick_values) if tick_values else -1
time_tick_distinct = len(set(tick_values))
time_sender_created = clean_time_log.count("Time sender created")
time_bus_disconnects = clean_time_log.count("time bus disconnected")

radio_time_bus_markers = radio_log.count("Now on time bus named")
radio_construction_markers = radio_log.count("Construction complete")
radio_queue_release_markers = len(re.findall(r"Generic_radioHardwareModel::forward_loop: .*:5011 received \d+ bytes", radio_log))
radio_forward_errors = sum(1 for line in radio_log.splitlines() if "only forwarded" in line)

aliases = inspect_aliases(engine_inspect)
engine_alias_common = "nos-engine-server" in aliases
engine_alias_override = "sc01-nos-engine-server" in aliases
engine_alias_converged = engine_alias_common and engine_alias_override

eligibility_unconditional = (
    criteria == "none"
    and delay_on == "false"
    and source_provider_reads_config
    and source_none_allows
    and source_delay_zero_default
)
queue_enqueue_expected = (
    trace_recv > 0
    and eligibility_unconditional
    and source_downlink_enqueue
    and source_enqueue_after_eligibility
)
callback_path_complete = (
    source_callback_registered
    and source_callback_downlink_queue
    and source_callback_due_compare
    and source_callback_sendto
    and source_timestamp_from_bus
    and source_time_parameters_shared
    and source_time_driver_sets_time
)
retained_time_progress_proven = time_tick_distinct >= 2 and time_tick_max > time_tick_min

if not eligibility_unconditional:
    diagnosis = "PACKET_ELIGIBILITY_NOT_PROVEN_UNCONDITIONAL"
elif not queue_enqueue_expected:
    diagnosis = "DOWNLINK_QUEUE_ENQUEUE_NOT_PROVEN"
elif not callback_path_complete:
    diagnosis = "PINNED_CALLBACK_PATH_INCOMPLETE"
elif not engine_alias_converged:
    diagnosis = "TIME_BUS_ENGINE_ALIAS_CONVERGENCE_FAILURE"
elif retained_time_progress_proven and trace_send_success == 0 and trace_send_failure == 0:
    diagnosis = "RADIO_CALLBACK_DELIVERY_OR_QUEUE_VISIBILITY_FAILURE"
else:
    diagnosis = "RADIO_TIME_PROGRESS_OR_CALLBACK_INVOCATION_UNPROVEN_BY_RETAINED_LOG"

print("RADIO_QUEUE_ELIGIBILITY_AND_TIME_CALLBACK_AUDIT")
print(f"run_dir={run_dir}")
print(f"run_id={manifest.get('run_id', '')}")
print("runtime_launched=0")
print("docker_invoked=0")
print("retained_evidence_modified=0")
print("\n[SOURCE_LOCKS]")
for key in ("nos3", "generic_radio", "sim_common", "nos_time_driver"):
    print(f"{key}_expected={EXPECTED[key]}")
    print(f"{key}_actual={heads[key]}")
print("\n[RETAINED_CONFIGURATION]")
print(f"runtime_fsw_to_port={fsw_to_port}")
print(f"runtime_gsw_ip={gsw_ip}")
print(f"runtime_gsw_tlm_port={gsw_tlm_port}")
print(f"runtime_comm_downlink={comm_downlink}")
print(f"runtime_downlink_close_criteria={criteria}")
print(f"runtime_downlink_delay_on={delay_on}")
print(f"runtime_common_nos_connection_string={common_connection}")
print(f"runtime_time_override_connection_string={override_connection}")
print("\n[PINNED_SOURCE]")
print(f"source_provider_reads_downlink_config={int(source_provider_reads_config)}")
print(f"source_none_criteria_allows_communication={int(source_none_allows)}")
print(f"source_delay_zero_default={int(source_delay_zero_default)}")
print(f"source_downlink_enqueue_present={int(source_downlink_enqueue)}")
print(f"source_enqueue_after_eligibility={int(source_enqueue_after_eligibility)}")
print(f"source_timestamp_uses_time_bus={int(source_timestamp_from_bus)}")
print(f"source_callback_registered={int(source_callback_registered)}")
print(f"source_callback_downlink_queue_present={int(source_callback_downlink_queue)}")
print(f"source_callback_due_compare_present={int(source_callback_due_compare)}")
print(f"source_callback_sendto_8011_present={int(source_callback_sendto)}")
print(f"source_shared_time_parameters_present={int(source_time_parameters_shared)}")
print(f"source_time_driver_set_time_present={int(source_time_driver_sets_time)}")
print("\n[ENGINE_AND_TIME_EVIDENCE]")
print(f"engine_alias_nos_engine_server={int(engine_alias_common)}")
print(f"engine_alias_sc01_nos_engine_server={int(engine_alias_override)}")
print(f"engine_aliases_converged={int(engine_alias_converged)}")
print(f"time_log_bytes={len(time_log.encode('utf-8'))}")
print(f"time_sender_created_markers={time_sender_created}")
print(f"time_bus_disconnect_markers={time_bus_disconnects}")
print(f"time_tick_marker_count={len(tick_values)}")
print(f"time_tick_distinct_values={time_tick_distinct}")
print(f"time_tick_min={time_tick_min}")
print(f"time_tick_max={time_tick_max}")
print(f"retained_time_progress_proven={int(retained_time_progress_proven)}")
print(f"engine_log_bytes={len(engine_log.encode('utf-8'))}")
print(f"radio_time_bus_registration_markers={radio_time_bus_markers}")
print(f"radio_construction_complete_markers={radio_construction_markers}")
print("\n[RETAINED_TRANSPORT]")
print(f"radio_socket_recvfrom_5011_records={trace_recv}")
print(f"radio_socket_sendto_8011_success_records={trace_send_success}")
print(f"radio_socket_sendto_8011_failure_records={trace_send_failure}")
print(f"radio_queue_release_log_markers={radio_queue_release_markers}")
print(f"radio_forward_error_lines={radio_forward_errors}")
print("\n[ASSESSMENT]")
print(f"downlink_eligibility_unconditional={int(eligibility_unconditional)}")
print(f"downlink_queue_enqueue_expected={int(queue_enqueue_expected)}")
print(f"callback_path_structurally_complete={int(callback_path_complete)}")
print(f"read_only_diagnosis={diagnosis}")
print("scientific_outcome=false")
print("additional_runtime_authorized=false")
print("RADIO_QUEUE_ELIGIBILITY_AND_TIME_CALLBACK_AUDIT_STATUS=COMPLETE")
PY
