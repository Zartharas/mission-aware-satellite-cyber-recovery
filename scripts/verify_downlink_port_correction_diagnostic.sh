#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/scripts/run_downlink_port_correction_diagnostic.sh"
HISTORICAL_RUNNER="$ROOT/scripts/run_downlink_path_diagnostic.sh"
AUDITOR="$ROOT/scripts/audit_to_lab_downlink_static.sh"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
WITNESS="$ROOT/scripts/telemetry_path_witness.py"
BASELINE_CONTRACT="$ROOT/configs/benign-baseline-contract.json"
DIAGNOSTIC_CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
AUDIT_LOCK="$ROOT/artifacts/to-lab-downlink-static-audit-lock.txt"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
PROJECT="mission-aware-satellite-cyber-recovery"

for file in \
  "$RUNNER" "$HISTORICAL_RUNNER" "$AUDITOR" "$PREPARER" "$WITNESS" \
  "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT" "$AUDIT_LOCK"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

for command in python3 bash docker shasum git; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

python3 -m json.tool "$BASELINE_CONTRACT" >/dev/null
python3 -m json.tool "$DIAGNOSTIC_CONTRACT" >/dev/null
python3 -m py_compile "$PREPARER" "$WITNESS"
python3 "$PREPARER" --self-test
python3 "$WITNESS" --self-test
bash -n "$HISTORICAL_RUNNER"
bash -n "$RUNNER"
bash -n "$AUDITOR"

python3 - "$BASELINE_CONTRACT" "$DIAGNOSTIC_CONTRACT" "$AUDIT_LOCK" "$RUNNER" <<'PY'
import json
import sys
from pathlib import Path

baseline = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
diagnostic = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
audit_lock = Path(sys.argv[3]).read_text(encoding="utf-8")
runner = Path(sys.argv[4]).read_text(encoding="utf-8")

assert baseline["contract_version"] == "0.6.2"
assert baseline["status"] == "PLAINTEXT_RELAY_DOWNLINK_DIAGNOSIS_PENDING"
assert baseline["event_injection_allowed"] is False
assert baseline["gate"]["baseline_run_1_authorized"] is False
assert baseline["gate"]["baseline_run_1_rerun_authorized"] is False
assert baseline["gate"]["baseline_run_2_authorized"] is False

assert diagnostic["contract_version"] == "0.2.0"
assert diagnostic["status"] == "PORT_CORRECTION_STATIC_VALIDATION_PENDING"
assert diagnostic["scientific_outcome_allowed"] is False
assert diagnostic["event_injection_allowed"] is False
assert diagnostic["command_transmission_allowed"] is False
assert diagnostic["baseline_execution_allowed"] is False
assert diagnostic["cryptographic_semantics_claim_allowed"] is False
assert diagnostic["root_cause_finding"]["classification"] == "DIRECT_COMPILED_PORT_MISMATCH"
assert diagnostic["root_cause_finding"]["to_lab_compiled_destination_port"] == 5013
assert diagnostic["root_cause_finding"]["radio_fsw_telemetry_listener_port"] == 5011
assert diagnostic["topology"]["to_radio_witness"] == {
    "mode": "proxy",
    "alias": "active-gs",
    "bind_port": 5013,
    "forward_destination": "radio-sim",
    "forward_port": 5011,
    "byte_preserving": True,
}
assert diagnostic["topology"]["radio_egress_witness"] == {
    "mode": "sink",
    "alias": "cryptolib",
    "bind_port": 8011,
    "forwarding": False,
}
assert diagnostic["evidence_requirements"]["policy_visible_scope_marker_required"] is True
assert diagnostic["evidence_requirements"]["policy_visible_scope_marker_filename"] == "scope.json"
assert diagnostic["evidence_requirements"]["zero_entry_manifest_allowed"] is False
assert diagnostic["gate"]["diagnostic_runtime_authorized"] is False
assert diagnostic["gate"]["diagnostic_runtime_attempts_authorized"] == 0
assert diagnostic["gate"]["baseline_run_1_authorized"] is False
assert diagnostic["gate"]["baseline_run_2_authorized"] is False
assert diagnostic["gate"]["event_injection_authorized"] is False

for token in (
    "to_lab_cfg_tlm_port=5013",
    "radio_fsw_telemetry_listener_port=5011",
    "port_mismatch=5013_to_5011",
    "sample_subscription_present=true",
    "sample_schedule_enabled=true",
    "classification=PASS_DIRECT_CONFIGURATION_MISMATCH_IDENTIFIED",
):
    assert token in audit_lock, token

for token in (
    'assert contract["contract_version"] == "0.2.0"',
    "PORT_CORRECTION_STATIC_VALIDATION_PENDING",
    "PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING",
    "--bind-port 5013",
    "--forward-host radio-sim --forward-port 5011",
    "record to_lab_compiled_destination_port 5013",
    "policy_visible_evidence",
    "zero-entry evidence manifest rejected",
    "start radio-egress-witness cryptolib true",
    "start to-radio-witness active-gs true",
    "DOWNLINK_PORT_CORRECTION_WRAPPER_VERIFICATION_STATUS=PASS",
):
    assert token in runner, token
PY

audit_output="$(bash "$AUDITOR")"
printf '%s\n' "$audit_output"
grep -Fq '#define cfgTLM_PORT        5013' <<< "$audit_output"
grep -Fq 'sample_subscription_present=1' <<< "$audit_output"
grep -Fq 'sample_schedule_enabled=1' <<< "$audit_output"
grep -Fq 'static_sample_telemetry_design=CONFIRMED' <<< "$audit_output"
grep -Fq 'STATIC_TO_LAB_DOWNLINK_AUDIT_STATUS=COMPLETE' <<< "$audit_output"

containers_before="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
networks_before="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$containers_before" == 0 && "$networks_before" == 0 ]] || {
  echo "[ERROR] Existing project-labeled resources found before verification." >&2
  exit 1
}

DOWNLINK_DIAGNOSTIC_VERIFY_ONLY=1 bash "$RUNNER"

for self_test in \
  "scripts/prepare_runtime_radio_config.py" \
  "scripts/telemetry_path_witness.py"; do
  docker run --rm --platform linux/amd64 --network none \
    --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
    --workdir /work/project \
    "$IMAGE" python3 "$self_test" --self-test
done

containers_after="$(docker ps -aq --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
networks_after="$(docker network ls -q --filter "label=research.project=$PROJECT" | wc -l | tr -d ' ')"
[[ "$containers_after" == 0 && "$networks_after" == 0 ]] || {
  echo "[ERROR] Verification left project-labeled resources behind." >&2
  exit 1
}

echo "DOWNLINK_PORT_CORRECTION_STATIC_VERIFICATION_STATUS=PASS"
