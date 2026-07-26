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
manifest_path = run_dir / "baseline-manifest.txt"
terminal_path = orch / "terminal-state.txt"


def parse_kv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key] = value
    return values


def first_glob(pattern: str) -> Path | None:
    return next(iter(sorted(orch.glob(pattern))), None)


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def marker_count(payload: str, token: str) -> int:
    return payload.count(token)


def verify_tree(directory: Path) -> tuple[str, int, int]:
    checksum_manifest = directory / "sha256-manifest.txt"
    if not checksum_manifest.is_file():
        return "MISSING_MANIFEST", 0, 0
    valid_line = re.compile(r"^([0-9a-f]{64})  (.+)$")
    entries = 0
    failures = 0
    for raw in checksum_manifest.read_text(encoding="utf-8", errors="replace").splitlines():
        match = valid_line.match(raw)
        if match is None:
            continue
        entries += 1
        expected, relative = match.groups()
        target = directory / relative
        if not target.is_file():
            failures += 1
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            failures += 1
    if entries == 0:
        return "EMPTY_UNVERIFIABLE", 0, 0
    if failures:
        return "FAIL", entries, failures
    return "PASS", entries, 0


def extract_packets(payload: str, mode: str, action: str) -> dict[int, tuple[int, str]]:
    pattern = re.compile(
        rf"TELEMETRY_WITNESS_{action} mode={mode} sequence=(\d+).*?length=(\d+) sha256=([0-9a-f]{{64}})"
    )
    packets: dict[int, tuple[int, str]] = {}
    for sequence, length, digest in pattern.findall(payload):
        packets[int(sequence)] = (int(length), digest)
    return packets


def find_source(filename: str) -> Path | None:
    candidates = sorted((root / "external" / "nos3").rglob(filename))
    return candidates[0] if candidates else None


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


manifest = parse_kv(manifest_path)
terminal = parse_kv(terminal_path)
proxy_log_path = first_glob("*-to-radio-witness.log")
sink_log_path = first_glob("*-radio-egress-witness.log")
radio_log_path = first_glob("*-generic-radio-sim.log")
engine_log_path = first_glob("*-engine.log")
time_log_path = first_glob("*-time.log")
radio_inspect_path = first_glob("inspect-*-generic-radio-sim.json")
sink_inspect_path = first_glob("inspect-*-radio-egress-witness.json")
runtime_xml_path = orch / "runtime-config" / "nos3-simulator.xml"
liveness_path = orch / "liveness.csv"

proxy = read_text(proxy_log_path)
sink = read_text(sink_log_path)
radio = read_text(radio_log_path)
engine = read_text(engine_log_path)
time_log = read_text(time_log_path)
runtime_xml = read_text(runtime_xml_path)

received = extract_packets(proxy, "proxy", "RECEIVED")
forwarded = extract_packets(proxy, "proxy", "FORWARDED")
sink_received = extract_packets(sink, "sink", "RECEIVED")
pairs_match = received == forwarded and bool(received)
forwarded_bytes = sum(length for length, _digest in forwarded.values())

radio_source_path = find_source("generic_radio_hardware_model.cpp")
radio_source = read_text(radio_source_path)
sim_config_path = find_source("sim_config.cpp")
sim_config_source = read_text(sim_config_path)

source_queue_enqueue = int("_message_queue_udp_downlink.push(message)" in radio_source)
source_queue_callback = int("process_forward_loop_message_queue" in radio_source)
source_ingress_trace = int("received %ld bytes" in radio_source and "forward_loop" in radio_source)
source_release_sendto = int("_fwd_addr_udp_downlink" in radio_source and "sendto" in radio_source)
source_trace_configurable = int("log-config-file" in sim_config_source and "Logger::configure" in sim_config_source)

radio_time_bus_marker = marker_count(radio, "Now on time bus named")
radio_construction_marker = marker_count(radio, "Construction complete")
radio_destination_resolution_marker = marker_count(radio, "forward_loop - Initial = cryptolib")
radio_42_connection_marker = marker_count(radio, "Successfully connected TELEMETRY host fortytwo, port 4286")
radio_ingress_trace_markers = len(
    re.findall(r"Generic_radioHardwareModel::forward_loop: .*:5011 received \d+ bytes", radio)
)
radio_queue_release_trace_markers = len(
    re.findall(r"Generic_radioHardwareModel::forward_loop: .* received \d+ bytes", radio)
)
radio_forward_error_lines = [
    line for line in radio.splitlines()
    if "only forwarded" in line or "sendto" in line.lower() and "error" in line.lower()
]

engine_activity = int(bool(engine.strip()))
time_activity = int(bool(time_log.strip()))
radio_aliases = inspect_aliases(radio_inspect_path)
sink_aliases = inspect_aliases(sink_inspect_path)
cryptolib_on_sink = int("cryptolib" in sink_aliases)
radio_runtime_ip_present = int("radio-sim" in runtime_xml)
runtime_fsw_5011 = int(bool(re.search(r"<to-port>\s*5011\s*</to-port>", runtime_xml)))
runtime_gsw_8011 = int(bool(re.search(r"<tlm-port>\s*8011\s*</tlm-port>", runtime_xml)))
runtime_gsw_cryptolib = int(bool(re.search(r"<name>\s*gsw\s*</name>.*?<ip>\s*cryptolib\s*</ip>", runtime_xml, re.DOTALL)))

runtime_rows = 0
runtime_nonrunning_rows = 0
if liveness_path.is_file():
    for index, raw in enumerate(liveness_path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if index == 0 or not raw.strip():
            continue
        runtime_rows += 1
        columns = raw.split(",")
        if len(columns) < 4 or columns[3] != "running:0":
            runtime_nonrunning_rows += 1

immutable_state, immutable_entries, immutable_failures = verify_tree(run_dir / "immutable-ground")
policy_state, policy_entries, policy_failures = verify_tree(run_dir / "policy-visible")
policy_scope_present = int((run_dir / "policy-visible" / "scope.json").is_file())

if not received:
    diagnosis = "TO_LAB_TO_PROXY_TRAFFIC_NOT_OBSERVED"
elif not pairs_match:
    diagnosis = "PROXY_BYTE_PRESERVATION_FAILURE"
elif sink_received:
    diagnosis = "DOWNLINK_PATH_THROUGH_RADIO_OBSERVED"
elif radio_ingress_trace_markers > 0 and radio_queue_release_trace_markers == 0:
    diagnosis = "RADIO_DOWNLINK_QUEUE_RELEASE_NOT_OBSERVED"
elif radio_queue_release_trace_markers > 0 and not sink_received:
    diagnosis = "RADIO_EGRESS_DESTINATION_OR_SEND_PATH_FAILURE"
elif radio_forward_error_lines:
    diagnosis = "RADIO_UDP_FORWARD_ERROR_OBSERVED"
else:
    diagnosis = "RADIO_INGRESS_OR_SIMULATION_TIME_QUEUE_RELEASE_UNRESOLVED_AT_CURRENT_LOG_LEVEL"

if immutable_state == "PASS" and policy_state == "PASS" and policy_scope_present:
    evidence_diagnosis = "EVIDENCE_TREES_AND_POLICY_SCOPE_VERIFIED"
else:
    evidence_diagnosis = "EVIDENCE_CONTROL_FAILURE_OR_INCOMPLETE"

print("RADIO_QUEUE_RETAINED_RUN_ANALYSIS")
print(f"run_dir={run_dir}")
print("\n[MANIFEST]")
for key in (
    "run_id",
    "phase",
    "diagnostic_type",
    "to_lab_destination_port",
    "to_lab_compiled_destination_port",
    "radio_fsw_telemetry_listener_port",
    "measured_command_transmissions",
    "terminal_classification",
    "exit_code",
    "cleanup_project_containers_remaining",
    "cleanup_project_networks_remaining",
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
print(f"runtime_radio_name_present={radio_runtime_ip_present}")
print(f"runtime_fsw_to_port_5011={runtime_fsw_5011}")
print(f"runtime_gsw_ip_cryptolib={runtime_gsw_cryptolib}")
print(f"runtime_gsw_tlm_port_8011={runtime_gsw_8011}")
print(f"radio_container_alias_count={len(radio_aliases)}")

print("\n[PINNED_SOURCE_BEHAVIOR]")
print(f"generic_radio_source={radio_source_path or ''}")
print(f"generic_radio_source_head={git_head(radio_source_path)}")
print(f"source_downlink_queue_enqueue_present={source_queue_enqueue}")
print(f"source_time_tick_queue_callback_present={source_queue_callback}")
print(f"source_ingress_trace_present={source_ingress_trace}")
print(f"source_queue_release_sendto_present={source_release_sendto}")
print(f"source_trace_log_configuration_supported={source_trace_configurable}")

print("\n[RETAINED_RADIO_OBSERVABILITY]")
print(f"radio_log_bytes={len(radio.encode('utf-8'))}")
print(f"radio_time_bus_registration_markers={radio_time_bus_marker}")
print(f"radio_construction_complete_markers={radio_construction_marker}")
print(f"radio_cryptolib_resolution_markers={radio_destination_resolution_marker}")
print(f"radio_42_connection_markers={radio_42_connection_marker}")
print(f"radio_ingress_trace_markers={radio_ingress_trace_markers}")
print(f"radio_queue_release_trace_markers={radio_queue_release_trace_markers}")
print(f"radio_forward_error_lines={len(radio_forward_error_lines)}")
print(f"engine_log_nonempty={engine_activity}")
print(f"time_log_nonempty={time_activity}")

print("\n[LIVENESS_AND_EVIDENCE]")
print(f"liveness_rows={runtime_rows}")
print(f"runtime_nonrunning_rows={runtime_nonrunning_rows}")
print(f"immutable_ground_tree_verification={immutable_state}")
print(f"immutable_ground_manifest_entries={immutable_entries}")
print(f"immutable_ground_verification_failures={immutable_failures}")
print(f"policy_visible_tree_verification={policy_state}")
print(f"policy_visible_manifest_entries={policy_entries}")
print(f"policy_visible_verification_failures={policy_failures}")
print(f"policy_visible_scope_present={policy_scope_present}")
print(f"transport_diagnosis={diagnosis}")
print(f"evidence_diagnosis={evidence_diagnosis}")

if radio_forward_error_lines:
    print("\n[RADIO_FORWARD_ERRORS]")
    for line in radio_forward_error_lines:
        print(line)

print("\n[INTERPRETATION]")
if diagnosis == "RADIO_INGRESS_OR_SIMULATION_TIME_QUEUE_RELEASE_UNRESOLVED_AT_CURRENT_LOG_LEVEL":
    print("The corrected proxy delivered a sustained byte-preserving telemetry stream to radio-sim UDP 5011, but the egress witness received nothing. The pinned radio enqueues received downlink datagrams and releases them only from a NOS Engine time-tick callback. Both ingress and release success are TRACE-level messages, so the retained log cannot distinguish socket receipt from queue-release failure at its current logging level.")
elif diagnosis == "RADIO_DOWNLINK_QUEUE_RELEASE_NOT_OBSERVED":
    print("Radio ingress was observed at TRACE level, but no queue-release trace reached the retained log. The next correction should focus on the radio time-tick callback and queued-message timing.")
elif diagnosis == "RADIO_EGRESS_DESTINATION_OR_SEND_PATH_FAILURE":
    print("The radio queue-release trace was observed but the egress witness remained empty. The next correction should focus on the resolved cryptolib destination and UDP send path.")
else:
    print("The diagnosis above identifies the earliest retained-evidence boundary that failed or remained unsupported.")
print("No runtime was launched by this analyzer.")
print("RADIO_QUEUE_RETAINED_RUN_ANALYSIS_STATUS=COMPLETE")
PY
