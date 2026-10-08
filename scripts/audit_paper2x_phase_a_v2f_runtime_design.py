#!/usr/bin/env python3
"""Static, fail-closed audit of the P2X v2f nominal-runtime design gate.

This script does not launch Docker, run the nominal wrapper, create evidence,
or authorize runtime execution.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "paper2x" / "phase_a"
GATE = D / "V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
V2F_GATE = D / "V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json"
NOMINAL = ROOT / "scripts" / "run_paper2x_phase_a_nominal.sh"
PREFLIGHT = ROOT / "scripts" / "run_nominal_runtime_preflight.sh"
READBACK = ROOT / "scripts" / "readback_paper2x_phase_a_v2f_manifest.py"

EXPECTED_MANIFEST_SHA256 = "cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee"
EXPECTED_HEAD = "8f5faef3830646eae065e8210216a2ed4301316c"
EXPECTED_EVIDENCE = "p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1"
EXPECTED_DESCRIPTOR = "08ea45ca09c9a82b5456bea1f93cf325c1a61a8ae4332c5a8dea1b7d4dfbb736"


def hold(reason: str) -> None:
    raise SystemExit("P2X_V2F_RUNTIME_DESIGN_HOLD=" + reason)


def require(ok: bool, reason: str) -> None:
    if not ok:
        hold(reason)


def audit() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    v2f = json.loads(V2F_GATE.read_text(encoding="utf-8"))
    nominal = NOMINAL.read_text(encoding="utf-8")
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    readback = READBACK.read_text(encoding="utf-8")

    require(gate["record_id"] ==
            "P2X-PHASE-A-V2F-NOMINAL-RUNTIME-QUALIFICATION-GATE-2026-10-07",
            "wrong_runtime_gate")
    require(gate["experiment_id"] == "P2X-NOS3-RG-001",
            "wrong_experiment")
    design_only = gate["decision"] == (
        "V2F_RUNTIME_DESIGN_AND_STATIC_VALIDATION_ONLY__EXECUTION_NOT_AUTHORIZED"
    )
    readback_authorized = gate["decision"] == (
        "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_MANIFEST_BINDING"
    )
    manifest_bound = gate["decision"] == (
        "V2F_MANIFEST_SHA256_BOUND__RUNTIME_NOT_AUTHORIZED"
    )
    require(design_only or readback_authorized or manifest_bound,
            "runtime_gate_invalid_state")
    require(gate["execution_authorized"] is False,
            "runtime_execution_authorized")
    require(gate.get("read_only_manifest_binding_authorized", False)
            is readback_authorized,
            "read_only_binding_authorization_state")

    scope = gate["authorization_scope"]
    require(scope["runtime_design"] is True and
            scope["static_validation"] is True and
            scope["read_only_manifest_hash_readback"] is readback_authorized and
            scope["nominal_runtime_execution"] is False and
            scope["benign_internal_cfs_noop"] is False and
            scope["cosmos"] is False and
            scope["faults"] is False and
            scope["scientific_observations"] is False and
            scope["final_environment_acceptance"] is False and
            scope["merge_pr215"] is False,
            "runtime_scope_firewall")

    require(v2f["decision"] ==
            "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
            "parent_v2f_not_closed_pass")
    require(v2f["execution_authorized"] is False and
            v2f["authorization_scope"]["offline_full_build"] is False,
            "parent_build_gate_open")
    require(v2f["third_attempt_result"] == "PASS" and
            v2f["third_attempt_raw_artifact_identity"] == "9_OF_9" and
            v2f["third_attempt_independent_readback"] == "PASS",
            "parent_v2f_pass_not_bound")
    require(v2f["third_attempt_runtime_tested"] is False and
            v2f["third_attempt_cosmos_tested"] is False and
            v2f["third_attempt_fault_campaign_executed"] is False,
            "parent_runtime_scope_changed")

    require(gate["parent_v2f_executed_head"] == EXPECTED_HEAD and
            gate["parent_v2f_evidence_id"] == EXPECTED_EVIDENCE and
            gate["parent_v2f_descriptor_map_sha256"] == EXPECTED_DESCRIPTOR and
            gate["parent_v2f_raw_artifact_identity"] == "9_OF_9" and
            gate["parent_v2f_independent_readback"] == "PASS" and
            gate["parent_v2f_runtime_tested"] is False,
            "runtime_parent_binding_drift")

    require(gate["parent_v2f_manifest_relative_path"] ==
            "artifacts/runtime/" + EXPECTED_EVIDENCE +
            "/p2x-v2f-build-manifest.json",
            "manifest_path_drift")
    expected_hash_status = (
        "VERIFIED_READ_ONLY_HOST_READBACK" if manifest_bound else
        "PENDING_AUTHORIZED_READ_ONLY_HOST_READBACK" if readback_authorized else
        "PENDING_READ_ONLY_HOST_READBACK"
    )
    require(gate["parent_v2f_manifest_sha256_status"] == expected_hash_status and
            gate["parent_v2f_manifest_sha256_required_before_runtime_authorization"]
            is True,
            "manifest_hash_state_drift")
    if manifest_bound:
        require(gate["parent_v2f_manifest_sha256"] == EXPECTED_MANIFEST_SHA256 and
                gate.get("read_only_manifest_binding_completed") is True and
                gate.get("read_only_manifest_binding_result") == "PASS" and
                gate.get("read_only_manifest_binding_evidence_unchanged") is True and
                gate.get("read_only_manifest_binding_independent_verifier_pass") is True and
                gate.get("read_only_manifest_binding_worktree_clean") is True and
                gate.get("read_only_manifest_binding_verified_head") ==
                "e76b51e80a94dc3826fb39d268c681ad6d4c6450",
                "manifest_readback_bound_provenance")
    else:
        require(gate["parent_v2f_manifest_sha256"] is None,
                "manifest_hash_unexpectedly_bound")

    future = gate["required_future_v2f_runtime_binding"]
    require(future["manifest_environment_variable"] == "P2X_V2F_MANIFEST" and
            future["independent_verifier"] ==
            "scripts/verify_paper2x_phase_a_v2f.py" and
            future["require_exact_manifest_sha256"] is True and
            future["require_exact_parent_evidence_id"] is True and
            future["require_exact_parent_executed_head"] is True and
            future["require_raw_identity_9_of_9"] is True and
            future["require_independent_readback_pass"] is True and
            future["legacy_p2x_v2_manifest_binding_forbidden"] is True,
            "future_v2f_runtime_binding_incomplete")

    require("P2X_V2_MANIFEST" in nominal and
            "verify_paper2x_phase_a_v2.py" in nominal and
            "P2X_V2F_MANIFEST" not in nominal,
            "legacy_runner_boundary_changed")
    require("run-ci-noop" in nominal and
            "run_nominal_runtime_preflight.sh" in nominal,
            "nominal_execution_path_not_detected")

    require("docker network create" in preflight and
            "docker run -d" in preflight and
            "NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS" in preflight,
            "preflight_execution_capability_not_detected")

    for token in ("P2X_V2F_MANIFEST_READBACK=PASS",
                  "P2X_V2F_MANIFEST_SHA256=",
                  "verify_paper2x_phase_a_v2f.py",
                  "P2X_V2F_RUNTIME_EXECUTED=NO",
                  "P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO"):
        require(token in readback, "readback_contract_missing:" + token)
    for forbidden in ("docker run", "docker network",
                      "run_nominal_runtime_preflight.sh",
                      "run_paper2x_phase_a_nominal.sh",
                      "cleanup_nominal_runtime.sh",
                      "shell=True", ".write_text(", ".unlink(", ".mkdir("):
        require(forbidden not in readback,
                "readback_not_read_only:" + forbidden)

    require(gate["runtime_execution_result"] == "NOT_RUN" and
            gate["cosmos_result"] == "NOT_RUN" and
            gate["fault_campaign_result"] == "NOT_RUN" and
            gate["scientific_observations_generated"] is False and
            gate["environment_final_acceptance"] is False,
            "false_runtime_result")

    print("P2X_V2F_RUNTIME_DESIGN_GATE=PASS")
    print("P2X_V2F_PARENT_BUILD_9_OF_9=BOUND")
    print("P2X_V2F_MANIFEST_SHA256=" + expected_hash_status)
    print("P2X_V2F_MANIFEST_READBACK_AUTHORIZATION=" +
          ("AUTHORIZED_READ_ONLY_HOST_ONLY" if readback_authorized else "CLOSED"))
    print("P2X_V2F_CURRENT_NOMINAL_RUNNER=LEGACY_V2_BOUND_BLOCKED")
    print("P2X_V2F_NOMINAL_PREFLIGHT=EXECUTION_CAPABLE_BLOCKED")
    print("P2X_V2F_RUNTIME_EXECUTION=NOT_AUTHORIZED")
    print("P2X_V2F_COSMOS=NOT_AUTHORIZED")
    print("P2X_V2F_FAULTS=NOT_AUTHORIZED")
    print("P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()
    audit()


if __name__ == "__main__":
    main()
