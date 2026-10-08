#!/usr/bin/env python3
"""P2X v2f nominal-runtime candidate: static gate ONLY; no executable runtime."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x/phase_a/V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
BUILD_GATE = ROOT / "paper2x/phase_a/V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json"
MANIFEST_SHA = "cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee"
EVIDENCE = "p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1"
MANIFEST_REL = "artifacts/runtime/" + EVIDENCE + "/p2x-v2f-build-manifest.json"
PRIMARY_REL = "artifacts/runtime/" + EVIDENCE + "/primary/source"
REPEAT_REL = "artifacts/runtime/" + EVIDENCE + "/repeat/source"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SystemExit("P2X_V2F_NOMINAL_DESIGN_HOLD=" + reason)


def static_check() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    build = json.loads(BUILD_GATE.read_text(encoding="utf-8"))
    scope = gate["authorization_scope"]
    plan = gate["nominal_launcher_candidate"]
    require(gate["decision"] == "V2F_MANIFEST_SHA256_BOUND__RUNTIME_NOT_AUTHORIZED",
            "parent_runtime_gate_not_closed")
    require(gate["execution_authorized"] is False and
            scope["nominal_runtime_execution"] is False and
            scope["benign_internal_cfs_noop"] is False and
            scope["cosmos"] is False and
            scope["faults"] is False and
            scope["scientific_observations"] is False and
            scope["final_environment_acceptance"] is False and
            scope["merge_pr215"] is False, "execution_scope_not_closed")
    require(gate["parent_v2f_manifest_sha256"] == MANIFEST_SHA and
            gate["parent_v2f_manifest_relative_path"] == MANIFEST_REL and
            gate["parent_v2f_evidence_id"] == EVIDENCE and
            gate["parent_v2f_manifest_sha256_status"] ==
            "VERIFIED_READ_ONLY_HOST_READBACK", "manifest_binding_drift")
    require(build["decision"] ==
            "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED" and
            build["execution_authorized"] is False and
            build["third_attempt_raw_artifact_identity"] == "9_OF_9",
            "parent_build_not_closed_pass")
    require(gate["nominal_launcher_design_status"] ==
            "STATIC_CANDIDATE_PREPARED__NOT_EXECUTABLE" and
            plan["candidate_mode"] == "STATIC_INSPECT_AND_SELF_TEST_ONLY" and
            plan["runtime_execution_entrypoint"] ==
            "UNIMPLEMENTED_AND_HARD_DENIED", "candidate_execution_enabled")
    require(plan["parent_manifest_sha256"] == MANIFEST_SHA and
            plan["parent_manifest_relative_path"] == MANIFEST_REL and
            plan["evidence_id"] == EVIDENCE and
            plan["candidate_primary_source_relative_path"] == PRIMARY_REL and
            plan["candidate_repeat_source_relative_path"] == REPEAT_REL and
            plan["source_population"] == "primary", "candidate_source_drift")
    require(plan["legacy_canonical_nos3_mount_forbidden"] is True and
            plan["direct_preserved_build_evidence_runtime_mount_forbidden"] is True and
            plan["require_separately_materialized_fresh_runtime_workspace"] is True and
            plan["runtime_workspace_materialization_implemented"] is False and
            plan["runtime_workspace_independent_validation_implemented"] is False and
            plan["runtime_launcher_v2f_binding_implemented"] is False and
            plan["preflight_legacy_v2_adapter_validated"] is False and
            plan["runtime_authorized"] is False, "materialization_or_runtime_open")
    require(plan["image"] == IMAGE and
            plan["prospective_network"] == "INTERNAL_ONLY_NO_HOST_PORTS",
            "runtime_image_or_network_contract_drift")
    print("P2X_V2F_NOMINAL_CANDIDATE_STATIC=PASS")
    print("P2X_V2F_MANIFEST_SHA256_BOUND=" + MANIFEST_SHA)
    print("P2X_V2F_RUNTIME_WORKSPACE=NOT_MATERIALIZED")
    print("P2X_V2F_LEGACY_V2_RUNNER=BLOCKED")
    print("P2X_V2F_RUNTIME_EXECUTION=NOT_AUTHORIZED")
    print("P2X_V2F_COSMOS=NOT_AUTHORIZED")
    print("P2X_V2F_FAULTS=NOT_AUTHORIZED")
    print("P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO")


def main() -> None:
    mode = sys.argv[1:]
    if mode == ["--run"]:
        raise SystemExit(
            "P2X_V2F_NOMINAL_RUNTIME_HOLD=not_implemented__separate_authorization_required"
        )
    require(mode in (["--inspect"], ["--self-test"]),
            "usage:--inspect_or_--self-test__runtime_denied")
    static_check()


if __name__ == "__main__":
    main()
