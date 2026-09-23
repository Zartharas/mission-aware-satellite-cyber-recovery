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

    required_precanonical_files = (
        ROOT / "study7e/audit/independent_design_audit.py",
        ROOT / "study7e/validation/check_fsw_truth_leakage.py",
        ROOT / "study7e/fsw/aerc_bus_probe/CMakeLists.txt",
        ROOT / "study7e/fsw/aerc_bus_probe/fsw/inc/aerc_bus_probe.h",
        ROOT / "study7e/fsw/aerc_bus_probe/fsw/src/aerc_bus_probe.c",
        ROOT / "study7e/fsw/aerc_sbn_probe/fsw/src/aerc_sbn_probe.c",
        ROOT / "study7e/fsw/aerc_hs_probe/fsw/src/aerc_hs_probe.c",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_CFS_PRESELECTION_SEAMS_CHECKPOINT_2026-09-23.md",
        ROOT / "publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_SELECTION_DECISION_2026-09-23.md",
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
    print("candidate_stack_selected=true")\n    print("candidate_stack=standalone_cFS_v7.0.1")\n    print("canonical_environment_frozen=false")
    print("production_model_training_performed=false")
    print("production_model_freeze_performed=false")
    print("canonical_execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
