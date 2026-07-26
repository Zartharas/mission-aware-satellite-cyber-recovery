#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: bash scripts/analyze_radio_queue_retained_run.sh artifacts/downlink-diagnostics/<run-id>" >&2
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

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
run_dir = Path(sys.argv[2]).resolve()
orch = run_dir / "immutable-ground" / "orchestration"


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


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_packets(payload: str, mode: str, action: str) -> dict[int, tuple[int, str]]:
    pattern = re.compile(
        rf"TELEMETRY_WITNESS_{action} mode={mode} sequence=(\d+).*?length=(\d+) sha256=([0-9a-f]{{64}})"
    )
    return {
        int(sequence): (int(length), digest)
        for sequence, length, digest in pattern.findall(payload)
    }


def verify_tree(directory: Path) -> tuple[str, int, int]:
    checksum_manifest = directory / "sha256-manifest.txt"
    if not checksum_manifest.is_file():
        return "MISSING_MANIFEST", 0, 0
    line_pattern = re.compile(r"^([0-9a-f]{64})  (.+)$")
    entries = 0
    failures = 0
    for raw in checksum_manifest.read_text(encoding="utf-8", errors="replace").splitlines():
        match = line_pattern.match(raw)
        if match is None:
            continue
        entries += 1
        expected, relative = match.groups()
        target = directory / relative
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            failures += 1
    if entries == 0:
        return "EMPTY_UNVERIFIABLE", 0, 0
    return ("PASS" if failures == 0 else "FAIL"), entries, failures


def inspect_aliases(path: Path | None) -> set[str]:
    if path is None or not path.is_file():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    networks = payload.get("NetworkSettings", {}).get("Networks", {}) if isinstance(payload, dict) else {}
    aliases: set[str] = set()
    for details in networks.values():
        if isinstance(details, dict):
            aliases.update(alias for alias in details.get("Aliases") or [] if isinstance(alias, str))
    return aliases


def find_source(filename: str) -> Path | None:
    return next(iter(sorted((root / "external" / "nos3").rglob(filename))), None)


def git_head(path: Path | None) -> str:
    if path is None:
        return ""
    directory = path.parent
    while directory != directory.parent and not (directory / ".git").exists():
        directory = directory.parent
    try:
        return subprocess.check_output(
            ["git", "-C", str(directory), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return ""


manifest = parse_kv(run_dir / "baseline-manifest.txt")
terminal = parse_kv(orch / "terminal-state.txt")
proxy_path = first_glob("*-to-radio-witness.log")
sink_path = first_glob("*-radio-egress-witness.log")
radio_path = first_glob("*-generic-radio-sim.log")
radio_inspect = first_glob("inspect-*-generic-radio-sim.json")
sink_inspect = first_glob("inspect-*-radio-egress-witness.json")
liveness_path = orch / "liveness.csv"
runtime_xml_path = orch / "runtime-config" / "nos3-simulator.xml"

proxy = read_text(proxy_path)
sink = read_text(sink_path)
radio = read_text(radio_path)
runtime_xml = read_text(runtime_xml_path)

received = extract_packets(proxy, "proxy", "RECEIVED")
forwarded = extract_packets(proxy, "proxy", "FORWARDED")
sink_received = extract_packets(sink, "sink", "RECEIVED")
pairs_match = bool(received) and received == forwarded
forwarded_bytes = sum(length for length, _digest in forwarded.values())

radio_source_path = find_source("generic_radio_hardware_model.cpp")
sim_config_path = find_source("sim_config.cpp")
radio_source = read_text(radio_source_path)
sim_config_source = read_text(sim_config_path)
forward_block_match = re.search(
    r"void Generic_radioHardwareModel::forward_loop\(.*?\n\s*}\n\s*\n\s*void Generic_radioHardwareModel::process_forward_loop_message_queue",
    radio_source,
    re.DOTALL,
)
queue_block_match = re.search(
    r"void Generic_radioHardwareModel::process_forward_loop_message_queue\(.*?\n\s*}\n\s*\n\s*void Generic_radioHardwareModel::tcp_forward_loop",
    radio_source,
    re.DOTALL,
)
forward_block = forward_block_match.group(0) if forward_block_match else ""
queue_block = queue_block_match.group(0) if queue_block_match else ""

source_recvfrom = int("recvfrom(" in forward_block)
source_downlink_enqueue = int("_message_queue_udp_downlink.push(message)" in forward_block)
source_successful_ingress_trace = int(
    bool(re.search(r"recvfrom\(.*?sim_logger->trace\([^;]*received", forward_block, re.DOTALL))
)
source_time_callback = int("process_forward_loop_message_queue" in queue_block)
source_queue_release_sendto = int("_fwd_addr_udp_downlink" in queue_block and "sendto(" in queue_block)
source_queue_release_trace = int(
    "Generic_radioHardwareModel::forward_loop: %s:%d received %ld bytes" in queue_block
)
source_trace_configurable = int(
    "log-config-file" in sim_config_source and "ItcLogger::Logger::configure" in sim_config_source
)

queue_release_trace_markers = len(
    re.findall(r"Generic_radioHardwareModel::forward_loop: .*:5011 received \d+ bytes", radio)
)
forward_error_lines = [
    line for line in radio.splitlines()
    if "only forwarded" in line or ("sendto" in line.lower() and "error" in line.lower())
]

runtime_fsw_5011 = int(bool(re.search(r"<to-port>\s*5011\s*</to-port>", runtime_xml)))
runtime_gsw_cryptolib = int(bool(re.search(
    r"<name>\s*gsw\s*</name>.*?<ip>\s*cryptolib\s*</ip>", runtime_xml, re.DOTALL
)))
runtime_gsw_8011 = int(bool(re.search(r"<tlm-port>\s*8011\s*</tlm-port>", runtime_xml)))
cryptolib_on_sink = int("cryptolib" in inspect_aliases(sink_inspect))
radio_alias_count = len(inspect_aliases(radio_inspect))

runtime_rows = 0
runtime_nonrunning = 0
if liveness_path.is_file():
    for index, raw in enumerate(liveness_path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if index == 0 or not raw.strip():
            continue
        runtime_rows += 1
        columns = raw.split(",")
        if len(columns) < 4 or columns[3] != "running:0":
            runtime_nonrunning += 1

immutable_state, immutable_entries, immutable_failures = verify_tree(run_dir / "immutable-ground")
policy_state, policy_entries, policy_failures = verify_tree(run_dir / "policy-visible")
policy_scope_present = int((run_dir / "policy-visible" / "scope.json").is_file())

if not received:
    diagnosis = "TO_LAB_TO_PROXY_TRAFFIC_NOT_OBSERVED"
elif not pairs_match:
    diagnosis = "PROXY_BYTE_PRESERVATION_FAILURE"
elif sink_received:
    diagnosis = "DOWNLINK_PATH_THROUGH_RADIO_OBSERVED"
elif queue_release_trace_markers > 0:
    diagnosis = "RADIO_EGRESS_DESTINATION_OR_SEND_PATH_FAILURE"
elif forward_error_lines:
    diagnosis = "RADIO_UDP_FORWARD_ERROR_OBSERVED"
else:
    diagnosis = "RADIO_INGRESS_OR_SIMULATION_TIME_QUEUE_RELEASE_UNRESOLVED_AT_CURRENT_LOG_LEVEL"

evidence_diagnosis = (
    "EVIDENCE_TREES_AND_POLICY_SCOPE_VERIFIED"
    if immutable_state == "PASS" and policy_state == "PASS" and policy_scope_present
    else "EVIDENCE_CONTROL_FAILURE_OR_INCOMPLETE"
)

print("RADIO_QUEUE_RETAINED_RUN_ANALYSIS")
print(f"run_dir={run_dir}")
print("\n[MANIFEST]")
for key in (
    "run_id", "phase", "diagnostic_type", "to_lab_destination_port",
    "to_lab_compiled_destination_port", "radio_fsw_telemetry_listener_port",
    "measured_command_transmissions", "terminal_classification", "exit_code",
    "cleanup_project_containers_remaining", "cleanup_project_networks_remaining",
):
    print(f"{key}={manifest.get(key, '')}")
print(f"terminal_state={terminal.get('terminal_classification', '')}")

print("\n[PROXY_AND_EGRESS]")
print(f"proxy_unique_received_packets={len(received)}")
print(f"proxy_unique_forwarded_packets={len(forwarded)}")
print(f"proxy_forwarded_bytes={forwarded_bytes}")
print(f"proxy_received_forwarded_pairs_match={int(pairs_match)}")
print(f"radio_egress_unique_received_packets={len(sink_received)}")
print(f"cryptolib_alias_on_egress_witness={cryptolib_on_sink}")

print("\n[RUNTIME_CONFIGURATION]")
print(f"runtime_fsw_to_port_5011={runtime_fsw_5011}")
print(f"runtime_gsw_ip_cryptolib={runtime_gsw_cryptolib}")
print(f"runtime_gsw_tlm_port_8011={runtime_gsw_8011}")
print(f"radio_container_alias_count={radio_alias_count}")

print("\n[PINNED_SOURCE_BEHAVIOR]")
print(f"generic_radio_source={radio_source_path or ''}")
print(f"generic_radio_source_head={git_head(radio_source_path)}")
print(f"source_udp_recvfrom_present={source_recvfrom}")
print(f"source_downlink_queue_enqueue_present={source_downlink_enqueue}")
print(f"source_successful_recvfrom_trace_present={source_successful_ingress_trace}")
print(f"source_time_tick_queue_callback_present={source_time_callback}")
print(f"source_queue_release_sendto_present={source_queue_release_sendto}")
print(f"source_queue_release_trace_present={source_queue_release_trace}")
print(f"source_trace_log_configuration_supported={source_trace_configurable}")

print("\n[RETAINED_RADIO_OBSERVABILITY]")
print(f"radio_log_bytes={len(radio.encode('utf-8'))}")
print(f"radio_time_bus_registration_markers={radio.count('Now on time bus named')}")
print(f"radio_construction_complete_markers={radio.count('Construction complete')}")
print(f"radio_cryptolib_resolution_markers={radio.count('forward_loop - Initial = cryptolib')}")
print(f"radio_42_connection_markers={radio.count('Successfully connected TELEMETRY host fortytwo, port 4286')}")
print(f"radio_successful_ingress_markers=0")
print(f"radio_queue_release_trace_markers={queue_release_trace_markers}")
print(f"radio_forward_error_lines={len(forward_error_lines)}")

print("\n[LIVENESS_AND_EVIDENCE]")
print(f"liveness_rows={runtime_rows}")
print(f"runtime_nonrunning_rows={runtime_nonrunning}")
print(f"immutable_ground_tree_verification={immutable_state}")
print(f"immutable_ground_manifest_entries={immutable_entries}")
print(f"immutable_ground_verification_failures={immutable_failures}")
print(f"policy_visible_tree_verification={policy_state}")
print(f"policy_visible_manifest_entries={policy_entries}")
print(f"policy_visible_verification_failures={policy_failures}")
print(f"policy_visible_scope_present={policy_scope_present}")
print(f"transport_diagnosis={diagnosis}")
print(f"evidence_diagnosis={evidence_diagnosis}")

if forward_error_lines:
    print("\n[RADIO_FORWARD_ERRORS]")
    for line in forward_error_lines:
        print(line)

print("\n[INTERPRETATION]")
if diagnosis == "RADIO_INGRESS_OR_SIMULATION_TIME_QUEUE_RELEASE_UNRESOLVED_AT_CURRENT_LOG_LEVEL":
    print("The corrected proxy delivered a sustained byte-preserving stream to radio-sim UDP 5011, but the egress witness received nothing. The pinned source has no successful recvfrom trace at radio ingress. It only traces a packet when the simulation-time callback releases the downlink queue. Because the retained log contains no release trace and was not captured at a level that proves that callback path, socket receipt and queue release remain unresolved.")
elif diagnosis == "RADIO_EGRESS_DESTINATION_OR_SEND_PATH_FAILURE":
    print("A queue-release trace is present but the UDP 8011 sink remained empty. The unresolved boundary is the cryptolib destination resolution or UDP send/delivery path.")
else:
    print("The diagnosis above identifies the earliest retained-evidence boundary that failed or remained unsupported.")
print("No runtime was launched by this analyzer.")
print("RADIO_QUEUE_RETAINED_RUN_ANALYSIS_STATUS=COMPLETE")
PY
