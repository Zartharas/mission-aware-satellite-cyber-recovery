#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study7e.src.aerc_design import (
    FAULT_PROFILES,
    TOPOLOGY_SEPARATION,
    build_scenario_manifest,
    manifest_counts,
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def main() -> int:
    protocol = load_json(ROOT / "study7e/PROTOCOL_DRAFT.json")
    state = load_json(ROOT / "study7e/IMPLEMENTATION_STATE.json")
    topologies = load_json(ROOT / "study7e/configs/topologies.json")
    faults = load_json(ROOT / "study7e/configs/fault_profiles.json")
    policy = load_json(ROOT / "study7e/configs/policy_contracts.json")
    env = load_json(ROOT / "study7e/configs/candidate_environment.json")
    learner = load_json(ROOT / "study7e/configs/learner_candidate.json")
    signature_deps = load_json(ROOT / "study7e/configs/signature_dependency_candidates.json")

    require(protocol["experiment_id"] == "S7E-AERC-001", "protocol experiment id drift")
    require("NOT_FROZEN" in protocol["state"], "draft protocol unexpectedly frozen")
    require(protocol["execution_gate"]["canonical_execution_authorized"] is False, "protocol prematurely authorizes execution")
    require(state["canonical_scientific_execution_authorized"] is False, "implementation state prematurely authorizes execution")
    require(state["canonical_results_generated"] is False, "implementation state claims canonical results")
    require(state["production_models_frozen"] is False, "production models prematurely frozen")

    auth = ROOT / "study7e/CANONICAL_EXECUTION_AUTHORIZATION.json"
    require(not auth.exists(), "canonical execution authorization file must not exist in implementation phase")

    canonical_workflow = ROOT / ".github/workflows/study7e-canonical-execution.yml"
    require(not canonical_workflow.exists(), "canonical execution workflow must not exist in implementation phase")

    results_dir = ROOT / "study7e/results"
    if results_dir.exists():
        require(not any(results_dir.rglob("*")), "canonical results directory must be absent or empty")

    model_dir = ROOT / "study7e/models"
    prohibited_model_artifacts = (
        model_dir / "frozen_model_manifest.json",
        model_dir / "L0_BASE.joblib",
        model_dir / "L1_CORROBORATED.joblib",
        model_dir / "L0_BASE.pkl",
        model_dir / "L1_CORROBORATED.pkl",
        model_dir / "L0_BASE.onnx",
        model_dir / "L1_CORROBORATED.onnx",
    )
    require(not any(path.exists() for path in prohibited_model_artifacts), "frozen/serialized production model artifact exists prematurely")

    require(set(topologies["topologies"]) == set(TOPOLOGY_SEPARATION), "topology config/code drift")
    require(set(faults["profiles"]) == set(FAULT_PROFILES), "fault config/code drift")

    counts = manifest_counts(build_scenario_manifest())
    expected = protocol["expected_counts"]
    require(counts["TOTAL"] == expected["total_manifest_scenarios"] == 280, "manifest total drift")
    require(counts["TR1"] == 72, "TR1 count drift")
    require(counts["TR0"] == 12, "TR0 count drift")
    require(counts["TRAINING_SCENARIOS"] == expected["training_scenarios"] == 84, "training count drift")
    require(counts["E1"] == 84, "E1 count drift")
    require(counts["E2"] == 104, "E2 count drift")
    require(counts["C0"] == 8, "C0 count drift")
    require(counts["CANONICAL_EVAL_SCENARIOS"] == expected["canonical_evaluation_scenarios"] == 196, "evaluation count drift")
    require(counts["CANONICAL_EVAL_POLICY_DECISIONS"] == expected["canonical_evaluation_policy_decisions"] == 784, "decision count drift")

    require(len(policy["base_features"]) == 9, "base feature count drift")
    require(len(policy["corroborated_additional_features"]) == 7, "corroborated feature count drift")
    snapshot_contract = policy["cfs_snapshot_contract"]
    require(snapshot_contract["state"] == "PRECANONICAL_IMPLEMENTATION_CONTRACT", "cFS snapshot contract state drift")
    require(snapshot_contract["base_mid"] == "0x0EE5", "base snapshot MID drift")
    require(snapshot_contract["corroborated_mid"] == "0x0EE6", "corroborated snapshot MID drift")
    require(snapshot_contract["decision_mid"] == "0x0EE7", "policy decision MID drift")
    require(snapshot_contract["feature_slots"] == 16, "policy feature-slot count drift")
    require(snapshot_contract["base_feature_count"] == 9, "policy base feature-count drift")
    require(snapshot_contract["corroborated_feature_count"] == 16, "policy corroborated feature-count drift")
    require(snapshot_contract["binary_only"] is True, "policy binary-only guard lost")
    require(snapshot_contract["base_unused_slots_must_be_zero"] is True, "base unused-slot guard lost")
    require(snapshot_contract["reserved_bytes_must_be_zero"] is True, "policy reserved-byte guard lost")
    require(snapshot_contract["learned_policy_runtime_implemented"] is False, "learned policy runtime implemented prematurely")
    require(snapshot_contract["signature_verification_implemented"] is False, "signature verification claimed prematurely")
    require(env["cfs"]["tag_commit"] == "088b2fa828db9ff7e00733f1908e0eeb59f66ce3", "cFS candidate commit drift")
    require(env["nos3"]["tag_commit"] == "5a3bdee6be9a2c67fdf994ae6db56d5c60395302", "NOS3 candidate commit drift")
    require(
        env["state"] == "PRE_FREEZE_IMPLEMENTATION_BASELINE_SELECTED__NOT_CANONICAL_FREEZE",
        "environment selection state drift",
    )
    require(
        env["stack_selection"]["state"] == "PRE_FREEZE_IMPLEMENTATION_BASELINE_SELECTED__NOT_CANONICAL_FREEZE",
        "pre-freeze stack selection state drift",
    )
    require(env["stack_selection"]["selected_candidate"] == "standalone_cFS_v7.0.1", "unexpected implementation baseline")
    require(env["stack_selection"]["author_review_completed"] is True, "stack selection lacks author review")
    require(env["stack_selection"]["canonical_environment_frozen"] is False, "environment frozen prematurely")
    require(protocol["implementation_environment"]["selected_stack"] == "standalone_cFS_v7.0.1", "protocol/environment stack decision drift")
    require(protocol["implementation_environment"]["canonical_environment_frozen"] is False, "protocol environment frozen prematurely")
    require(
        env["stack_selection"]["mixing_standalone_cfs_and_nos3_pinned_fsw_without_compatibility_study"] == "PROHIBITED",
        "candidate stack-mixing prohibition lost",
    )

    require(learner["state"] == "CANDIDATE__NOT_FROZEN__NO_MODEL_ARTIFACTS", "learner candidate state drift")
    require(learner["library"] == "scikit-learn", "learner library drift")
    require(learner["library_version"] is None, "learner library version frozen prematurely")
    require(learner["training_blocks"] == ["TR0", "TR1"], "training-block contract drift")
    require(learner["prohibited_training_blocks"] == ["E1", "E2", "C0"], "evaluation leakage guard drift")
    require(learner["training_scenarios"] == 84, "learner training count drift")
    require(learner["model_training_performed"] is False, "production learner trained prematurely")
    require(learner["production_model_freeze_performed"] is False, "production learner frozen prematurely")

    sigdep = load_json(ROOT / "study7e/configs/signature_dependency_candidates.json")
    require(
        sigdep["state"] == "SELECTED_FOR_PRECANONICAL_CFS_VERIFICATION_INTEGRATION__NOT_FROZEN",
        "signature dependency selection state drift",
    )
    require(sigdep["selected_candidate"] == "monocypher", "unexpected Ed25519 verification dependency")
    require(
        sigdep["candidates"]["monocypher"]["commit"] == "ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f",
        "Monocypher revision drift",
    )
    require(
        sigdep["candidates"]["monocypher"]["version"] == "4.0.3",
        "Monocypher version drift",
    )
    require(
        sigdep["requirements"]["secret_key_in_flight_software"] is False,
        "flight-software secret-key prohibition lost",
    )

    require(
        signature_deps["state"] == "SELECTED_FOR_PRECANONICAL_CFS_VERIFICATION_INTEGRATION__NOT_FROZEN",
        "signature dependency state drift",
    )
    require(signature_deps["algorithm_candidate"] == "Ed25519_RFC8032", "signature algorithm candidate drift")
    require(signature_deps["use_case"] == "verification_only", "signature dependency use-case drift")
    require(signature_deps["requirements"]["secret_key_in_flight_software"] is False, "secret key allowed in flight software")
    require(signature_deps["requirements"]["public_key_bytes"] == 32, "Ed25519 public-key length drift")
    require(signature_deps["requirements"]["signature_bytes"] == 64, "Ed25519 signature length drift")
    require(signature_deps["selected_candidate"] == "monocypher", "signature dependency selection drift")
    require(signature_deps["candidates"]["monocypher"]["commit"] == "ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f", "Monocypher pin drift")
    require(signature_deps["candidates"]["libsodium"]["commit"] == "77e1ce5d6dee871c49ef211222ba18ef0c486bda", "libsodium pin drift")
    require(signature_deps["candidates"]["libsodium"]["official_tarball_sha256"] == "adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349", "libsodium tarball digest drift")
    sigwire = signature_deps["integration_contract"]
    require(sigwire["state"] == "CFS_VERIFICATION_BOUNDARY_RUNTIME_GREEN__NOT_AUTHORIZATION_BOUND", "signature verifier integration state drift")
    require(sigwire["request_mid"] == "0x0EE8", "signature verifier request MID drift")
    require(sigwire["result_mid"] == "0x0EE9", "signature verifier result MID drift")
    require(sigwire["wire_version"] == 1, "signature verifier wire version drift")
    require(sigwire["public_key_bytes"] == 32, "signature verifier public-key size drift")
    require(sigwire["signature_bytes"] == 64, "signature verifier signature size drift")
    require(sigwire["message_capacity_bytes"] == 64, "signature verifier message capacity drift")
    require(sigwire["exact_cfe_packet_size_required"] is True, "signature verifier packet-size guard lost")
    require(sigwire["zero_padding_required"] is True, "signature verifier zero-padding guard lost")
    require(sigwire["secret_key_present"] is False, "secret key added to verifier boundary")
    require(sigwire["signing_runtime_present"] is False, "signing runtime added prematurely")
    require(sigwire["policy_authorization_binding_present"] is False, "verification bound to authorization prematurely")
    require(sigwire["production_public_key_registry_frozen"] is False, "production public-key registry frozen prematurely")
    require(sigwire["canonical_authorization_message_defined"] is False, "canonical authorization bytes defined without review")
    require(sigwire["runtime_evidence"]["valid_signature_results"] == 2, "signature verifier positive-case evidence drift")
    require(sigwire["runtime_evidence"]["crypto_reject_results"] == 3, "signature verifier crypto-rejection evidence drift")
    require(sigwire["runtime_evidence"]["malformed_requests_rejected_without_result"] == 5, "signature verifier malformed-input evidence drift")
    require(sigwire["runtime_evidence"]["final_verification_sequence"] == 5, "signature verifier sequence evidence drift")

    required_precanonical_files = (
        ROOT / "study7e/audit/independent_design_audit.py",
        ROOT / "study7e/validation/check_fsw_truth_leakage.py",
        ROOT / "study7e/fsw/aerc_bus_probe/CMakeLists.txt",
        ROOT / "study7e/fsw/aerc_bus_probe/fsw/inc/aerc_bus_probe.h",
        ROOT / "study7e/fsw/aerc_bus_probe/fsw/src/aerc_bus_probe.c",
        ROOT / "study7e/fsw/aerc_sbn_probe/fsw/src/aerc_sbn_probe.c",
        ROOT / "study7e/fsw/aerc_hs_probe/fsw/src/aerc_hs_probe.c",
        ROOT / "study7e/fsw/aerc_recovery_sink/fsw/src/aerc_recovery_sink.c",
        ROOT / "study7e/fsw/aerc_sink_probe/fsw/src/aerc_sink_probe.c",
        ROOT / "study7e/fsw/aerc_policy/fsw/src/aerc_policy.c",
        ROOT / "study7e/fsw/aerc_policy_probe/fsw/src/aerc_policy_probe.c",
        ROOT / "study7e/fsw/aerc_sigverify/bootstrap_monocypher.sh",
        ROOT / "study7e/fsw/aerc_sigverify/fsw/src/aerc_ed25519_wrapper.c",
        ROOT / "study7e/fsw/aerc_sigverify/fsw/src/aerc_sigverify.c",
        ROOT / "study7e/fsw/aerc_sigverify_probe/fsw/src/aerc_sigverify_probe.c",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_CFS_PRESELECTION_SEAMS_CHECKPOINT_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_SELECTION_DECISION_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_RECOVERY_SINK_CHECKPOINT_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_ED25519_DEPENDENCY_DECISION_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_ED25519_CFS_BOUNDARY_CHECKPOINT_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_POLICY_SNAPSHOT_D0_D1_CHECKPOINT_2026-09-23.md",
        ROOT / ".github/workflows/study7e-cfs-runtime-smoke.yml",
        ROOT / ".github/workflows/study7e-cfs-baseline-feasibility.yml",
        ROOT / ".github/workflows/study7e-ed25519-dependency-feasibility.yml",
        ROOT / "study7e/configs/signature_dependency_candidates.json",
        ROOT / "study7e/feasibility/ed25519/rfc8032_monocypher_test.c",
        ROOT / "study7e/feasibility/ed25519/rfc8032_libsodium_test.c",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_PROTOCOL_REVIEW_R1_2026-09-22.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_PROTOCOL_REVIEW_R2_2026-09-22.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_COMPATIBILITY_DECISION_2026-09-22.md",
    )
    for required in required_precanonical_files:
        require(required.is_file(), f"missing pre-canonical control: {required.relative_to(ROOT)}")

    print("Study 7E pre-canonical implementation validation: PASS")
    print("experiment_id=S7E-AERC-001")
    print("manifest_total=280")
    print("training_scenarios=84")
    print("canonical_evaluation_scenarios=196")
    print("planned_evaluation_decisions=784")
    print("candidate_stack_selected=true")
    print("candidate_stack=standalone_cFS_v7.0.1")
    print("canonical_environment_frozen=false")
    print("production_model_training_performed=false")
    print("production_model_freeze_performed=false")
    print("canonical_execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
