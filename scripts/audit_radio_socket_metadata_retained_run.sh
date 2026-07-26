#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"
PROJECT="mission-aware-satellite-cyber-recovery"

if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: bash scripts/audit_radio_socket_metadata_retained_run.sh artifacts/downlink-diagnostics/<run-id>" >&2
  exit 2
fi

if [[ "$RUN_DIR" != /* ]]; then
  RUN_DIR="$ROOT/$RUN_DIR"
fi

[[ -d "$RUN_DIR" ]] || {
  echo "[ERROR] Retained run directory not found: $RUN_DIR" >&2
  exit 2
}

python3 - "$RUN_DIR" <<'PY'
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]).resolve()
manifest_path = run_dir / "baseline-manifest.txt"
terminal_path = run_dir / "immutable-ground" / "orchestration" / "terminal-state.txt"
orch = run_dir / "immutable-ground" / "orchestration"
trace_path = run_dir / "immutable-ground" / "radio-socket-metadata" / "radio-socket-metadata.log"


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


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def first_glob(pattern: str) -> Path | None:
    return next(iter(sorted(orch.glob(pattern))), None)


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


def inspect_state(path: Path) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, "UNREADABLE"
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    state = payload.get("State", {}) if isinstance(payload, dict) else {}
    running = bool(state.get("Running", False))
    status = str(state.get("Status", ""))
    return running, status


manifest = parse_kv(manifest_path)
terminal = parse_kv(terminal_path)
trace = read_text(trace_path)
to_log = read_text(first_glob("*-to-radio-witness.log"))
egress_log = read_text(first_glob("*-radio-egress-witness.log"))

trace_records = len(re.findall(r"^RADIO_SOCKET_METADATA ", trace, flags=re.MULTILINE))
recv_5011 = len(re.findall(r"event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$", trace, flags=re.MULTILINE))
send_8011_success = len(re.findall(r"event=sendto .*peer_port=8011 .*result=[1-9][0-9]* errno=0$", trace, flags=re.MULTILINE))
send_8011_failure = len(re.findall(r"event=sendto .*peer_port=8011 .*result=-1 errno=[1-9][0-9]*$", trace, flags=re.MULTILINE))
forbidden_trace_lines = sum(
    1
    for line in trace.splitlines()
    if re.search(r"payload|payload_sha|hex=|data=|address=|ip=", line, flags=re.IGNORECASE)
)

to_ready = to_log.count("TELEMETRY_WITNESS_READY mode=proxy")
to_received = to_log.count("TELEMETRY_WITNESS_RECEIVED mode=proxy")
to_forwarded = to_log.count("TELEMETRY_WITNESS_FORWARDED mode=proxy")
to_invalid = to_log.count("TELEMETRY_WITNESS_INVALID")
egress_ready = egress_log.count("TELEMETRY_WITNESS_READY mode=sink")
egress_received = egress_log.count("TELEMETRY_WITNESS_RECEIVED mode=sink")
egress_invalid = egress_log.count("TELEMETRY_WITNESS_INVALID")

inspect_paths = sorted(orch.glob("inspect-*.json"))
inspect_running = 0
inspect_nonrunning = 0
inspect_unreadable = 0
for path in inspect_paths:
    running, status = inspect_state(path)
    if status == "UNREADABLE":
        inspect_unreadable += 1
    elif running:
        inspect_running += 1
    else:
        inspect_nonrunning += 1

immutable_state, immutable_entries, immutable_failures = verify_tree(run_dir / "immutable-ground")
policy_state, policy_entries, policy_failures = verify_tree(run_dir / "policy-visible")

if send_8011_failure >= 1:
    derived_diagnosis = "RADIO_EGRESS_SEND_FAILURE"
elif send_8011_success >= 1 and egress_received >= 1:
    derived_diagnosis = "DOWNLINK_PATH_THROUGH_RADIO_OBSERVED"
elif send_8011_success >= 1:
    derived_diagnosis = "RADIO_EGRESS_DESTINATION_OR_DELIVERY_FAILURE"
elif recv_5011 >= 1:
    derived_diagnosis = "RADIO_SIMULATION_TIME_QUEUE_RELEASE_FAILURE"
else:
    derived_diagnosis = "RADIO_UDP_5011_INGRESS_FAILURE"

manifest_diagnosis = manifest.get("transport_diagnosis", "")
manifest_status = manifest.get("diagnostic_status", "")
terminal_classification = manifest.get("terminal_classification", terminal.get("terminal_classification", ""))
measured_commands = manifest.get("measured_command_transmissions", "")
ground_command_sources = manifest.get("ground_command_sources", "")

checks = {
    "run_id_matches": manifest.get("run_id", "") == run_dir.name,
    "trace_present": trace_path.is_file() and trace_records >= 1,
    "recvfrom_5011_present": recv_5011 >= 1,
    "diagnosis_matches": manifest_diagnosis == derived_diagnosis,
    "to_witness_received": to_received >= 1,
    "to_witness_forwarded": to_forwarded >= 1,
    "witness_invalid_zero": to_invalid == 0 and egress_invalid == 0,
    "trace_forbidden_content_zero": forbidden_trace_lines == 0,
    "immutable_hashes_pass": immutable_state == "PASS",
    "policy_hashes_pass": policy_state == "PASS",
    "inspect_snapshots_present": len(inspect_paths) >= 1,
    "inspect_snapshots_running": inspect_nonrunning == 0 and inspect_unreadable == 0,
    "measured_commands_zero": measured_commands == "0",
    "ground_command_sources_zero": ground_command_sources == "0",
}

audit_status = "PASS" if all(checks.values()) else "REVIEW_REQUIRED"

print("RADIO_SOCKET_METADATA_RETAINED_RUN_AUDIT")
print(f"run_dir={run_dir}")
print(f"run_id={manifest.get('run_id', '')}")
print(f"manifest_diagnostic_status={manifest_status}")
print(f"terminal_classification={terminal_classification}")
print(f"manifest_transport_diagnosis={manifest_diagnosis}")
print(f"derived_transport_diagnosis={derived_diagnosis}")
print(f"radio_socket_metadata_records={trace_records}")
print(f"radio_socket_recvfrom_5011_records={recv_5011}")
print(f"radio_socket_sendto_8011_success_records={send_8011_success}")
print(f"radio_socket_sendto_8011_failure_records={send_8011_failure}")
print(f"radio_socket_trace_forbidden_content_lines={forbidden_trace_lines}")
print(f"to_witness_ready_markers={to_ready}")
print(f"to_witness_received_markers={to_received}")
print(f"to_witness_forwarded_markers={to_forwarded}")
print(f"to_witness_invalid_markers={to_invalid}")
print(f"radio_egress_ready_markers={egress_ready}")
print(f"radio_egress_received_markers={egress_received}")
print(f"radio_egress_invalid_markers={egress_invalid}")
print(f"inspect_snapshot_count={len(inspect_paths)}")
print(f"inspect_running_count={inspect_running}")
print(f"inspect_nonrunning_count={inspect_nonrunning}")
print(f"inspect_unreadable_count={inspect_unreadable}")
print(f"immutable_ground_tree_verification={immutable_state}")
print(f"immutable_ground_manifest_entries={immutable_entries}")
print(f"immutable_ground_verification_failures={immutable_failures}")
print(f"policy_visible_tree_verification={policy_state}")
print(f"policy_visible_manifest_entries={policy_entries}")
print(f"policy_visible_verification_failures={policy_failures}")
print(f"measured_command_transmissions={measured_commands}")
print(f"ground_command_sources={ground_command_sources}")
for key, value in checks.items():
    print(f"check_{key}={str(value).lower()}")
print(f"retained_evidence_audit_status={audit_status}")
PY

containers_remaining="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
networks_remaining="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"

echo "cleanup_project_containers_remaining=$containers_remaining"
echo "cleanup_project_networks_remaining=$networks_remaining"

if [[ "$containers_remaining" == 0 && "$networks_remaining" == 0 ]]; then
  echo "cleanup_audit_status=PASS"
else
  echo "cleanup_audit_status=REVIEW_REQUIRED"
fi

echo "RADIO_SOCKET_METADATA_RETAINED_RUN_AUDIT_STATUS=COMPLETE"
