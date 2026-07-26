#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: bash scripts/analyze_downlink_path_diagnostic.sh artifacts/downlink-diagnostics/<run-id>" >&2
  exit 2
fi

if [[ "$RUN_DIR" != /* ]]; then
  RUN_DIR="$ROOT/$RUN_DIR"
fi

[[ -d "$RUN_DIR" ]] || {
  echo "[ERROR] Diagnostic run directory not found: $RUN_DIR" >&2
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


def count(text: str, token: str) -> int:
    return text.count(token)


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
        if not isinstance(details, dict):
            continue
        for alias in details.get("Aliases") or []:
            if isinstance(alias, str):
                aliases.add(alias)
    return aliases


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
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            failures += 1
    if entries == 0:
        return "EMPTY_UNVERIFIABLE", 0, 0
    if failures:
        return "FAIL", entries, failures
    return "PASS", entries, 0


manifest = parse_kv(manifest_path)
terminal = parse_kv(terminal_path)
cfs_log = first_glob("*-cfs.log")
to_witness_log = first_glob("*-to-radio-witness.log")
egress_witness_log = first_glob("*-radio-egress-witness.log")
to_witness_inspect = first_glob("inspect-*-to-radio-witness.json")
radio_inspect = first_glob("inspect-*-generic-radio-sim.json")

cfs = read_text(cfs_log)
to_witness = read_text(to_witness_log)
egress_witness = read_text(egress_witness_log)
to_aliases = inspect_aliases(to_witness_inspect)
radio_aliases = inspect_aliases(radio_inspect)

cfs_to_initialized = int("TO Lab Initialized" in cfs)
cfs_operational = int("CFE_ES_Main entering OPERATIONAL state" in cfs)
ci_ready = int("CI_LAB listening on UDP port: 5012" in cfs)
to_enabled = int("TO telemetry output enabled for IP active-gs" in cfs)
sample_initialized = int("SAMPLE App Initialized" in cfs)

error_tokens = (
    "TO Can't register table",
    "TO Can't load table",
    "TO Can't get table addr",
    "TO Can't create cmd pipe",
    "TO Can't create Tlm pipe",
    "TO Can't subscribe",
    "TO TLM socket error",
    "TO sendto error",
    "Tlm output suppressed",
)
to_error_lines = [
    line for line in cfs.splitlines()
    if any(token in line for token in error_tokens)
]

to_ready = count(to_witness, "TELEMETRY_WITNESS_READY mode=proxy")
to_received = count(to_witness, "TELEMETRY_WITNESS_RECEIVED mode=proxy")
to_forwarded = count(to_witness, "TELEMETRY_WITNESS_FORWARDED mode=proxy")
to_invalid = count(to_witness, "TELEMETRY_WITNESS_INVALID")
egress_ready = count(egress_witness, "TELEMETRY_WITNESS_READY mode=sink")
egress_received = count(egress_witness, "TELEMETRY_WITNESS_RECEIVED mode=sink")
egress_invalid = count(egress_witness, "TELEMETRY_WITNESS_INVALID")

active_gs_on_to_witness = int("active-gs" in to_aliases)
active_gs_on_radio = int("active-gs" in radio_aliases)

immutable_state, immutable_entries, immutable_failures = verify_tree(run_dir / "immutable-ground")
policy_state, policy_entries, policy_failures = verify_tree(run_dir / "policy-visible")

if active_gs_on_to_witness == 0:
    diagnosis = "ACTIVE_GS_WITNESS_ALIAS_MISSING"
elif cfs_to_initialized == 0:
    diagnosis = "TO_LAB_INITIALIZATION_UNCONFIRMED"
elif to_error_lines:
    diagnosis = "TO_LAB_TABLE_SUBSCRIPTION_SOCKET_OR_SEND_ERROR_OBSERVED"
elif to_enabled == 0:
    diagnosis = "TO_LAB_OUTPUT_ENABLE_UNCONFIRMED"
elif to_received == 0:
    diagnosis = "TO_LAB_PACKET_PRODUCTION_OR_DESTINATION_RESOLUTION_UNOBSERVED"
elif to_forwarded == 0:
    diagnosis = "TO_WITNESS_FORWARDING_FAILURE"
elif egress_received == 0:
    diagnosis = "RADIO_RECEIVE_OR_SIMULATION_TIME_QUEUE_RELEASE_FAILURE"
else:
    diagnosis = "DOWNLINK_PATH_THROUGH_RADIO_OBSERVED"

if policy_state == "EMPTY_UNVERIFIABLE":
    evidence_diagnosis = "POLICY_VISIBLE_TREE_EMPTY_MANIFEST_UNVERIFIABLE"
elif immutable_state != "PASS" or policy_state != "PASS":
    evidence_diagnosis = "EVIDENCE_TREE_VERIFICATION_FAILURE"
else:
    evidence_diagnosis = "EVIDENCE_TREES_VERIFIED"

print("DOWNLINK_PATH_DIAGNOSTIC_ANALYSIS")
print(f"run_dir={run_dir}")
print("\n[MANIFEST]")
for key in (
    "run_id",
    "phase",
    "diagnostic_type",
    "scientific_outcome_allowed",
    "command_transmission_allowed",
    "measured_command_transmissions",
    "event_injection",
    "radio_egress_witness_ready",
    "to_radio_witness_ready",
    "truth_sink_connection",
    "radio_udp_8010_listener",
    "radio_udp_5011_listener",
    "ci_lab_udp_5012",
    "to_lab_active_gs",
    "terminal_classification",
    "exit_code",
    "cleanup_project_containers_remaining",
    "cleanup_project_networks_remaining",
):
    print(f"{key}={manifest.get(key, '')}")

print("\n[CONTROL_EVIDENCE]")
print(f"to_witness_active_gs_alias_present={active_gs_on_to_witness}")
print(f"radio_active_gs_alias_present={active_gs_on_radio}")
print(f"cfs_operational_observed={cfs_operational}")
print(f"ci_lab_5012_observed={ci_ready}")
print(f"to_lab_initialized_observed={cfs_to_initialized}")
print(f"to_lab_active_gs_enable_observed={to_enabled}")
print(f"sample_initialized_observed={sample_initialized}")
print(f"to_lab_error_lines={len(to_error_lines)}")
print(f"to_witness_ready_markers={to_ready}")
print(f"to_witness_received_markers={to_received}")
print(f"to_witness_forwarded_markers={to_forwarded}")
print(f"to_witness_invalid_markers={to_invalid}")
print(f"radio_egress_ready_markers={egress_ready}")
print(f"radio_egress_received_markers={egress_received}")
print(f"radio_egress_invalid_markers={egress_invalid}")
print(f"immutable_ground_tree_verification={immutable_state}")
print(f"immutable_ground_manifest_entries={immutable_entries}")
print(f"immutable_ground_verification_failures={immutable_failures}")
print(f"policy_visible_tree_verification={policy_state}")
print(f"policy_visible_manifest_entries={policy_entries}")
print(f"policy_visible_verification_failures={policy_failures}")
print(f"transport_diagnosis={diagnosis}")
print(f"evidence_diagnosis={evidence_diagnosis}")

if to_error_lines:
    print("\n[TO_LAB_ERRORS]")
    for line in to_error_lines:
        print(line)

print("\n[INTERPRETATION]")
if diagnosis == "TO_LAB_PACKET_PRODUCTION_OR_DESTINATION_RESOLUTION_UNOBSERVED":
    print("The active-gs witness was correctly attached and ready, but it received no UDP telemetry after TO_LAB reported output enabled. The radio was never given a witnessed packet, so radio queue behavior was not evaluated. Retained logs cannot distinguish absence of subscribed telemetry from failure to resolve or send to the witness address.")
elif diagnosis == "DOWNLINK_PATH_THROUGH_RADIO_OBSERVED":
    print("Telemetry was observed at both witness points. This is diagnostic transport evidence only and is not a benign baseline or scientific outcome.")
else:
    print("The diagnosis above identifies the earliest unsupported or failed control in the retained diagnostic path.")
if evidence_diagnosis == "POLICY_VISIBLE_TREE_EMPTY_MANIFEST_UNVERIFIABLE":
    print("The policy-visible tree was empty, producing a checksum manifest with zero entries. Future diagnostics require a non-sensitive policy-visible scope marker and must reject empty evidence manifests.")

print("DOWNLINK_PATH_DIAGNOSTIC_ANALYSIS_STATUS=COMPLETE")
PY
