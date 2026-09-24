from __future__ import annotations

import json
from pathlib import Path

from study7e.src.aerc_design import (
    BASE_FEATURES,
    EXTENDED_FEATURES,
    build_scenario_manifest,
    manifest_counts,
)

ROOT = Path(__file__).resolve().parents[2]
PLAN = json.loads((ROOT / "study7e/configs/held_out_evaluation_plan_001.json").read_text())
FREEZE = json.loads((ROOT / "study7e/MODEL_FREEZE_MANIFEST_001.json").read_text())
STATE = json.loads((ROOT / "study7e/HELD_OUT_EVALUATION_PLAN_STATE.json").read_text())


def test_plan_is_review_only_and_inference_is_closed():
    assert PLAN["state"] == "PLAN_REVIEWED__QUALIFICATION_PENDING__HELD_OUT_INFERENCE_NOT_AUTHORIZED"
    assert PLAN["authorization"]["plan_preparation_and_review_authorized"] is True
    assert PLAN["authorization"]["held_out_inference_authorized"] is False
    assert PLAN["authorization"]["canonical_scientific_execution_authorized"] is False
    assert STATE["held_out_inference_authorized"] is False
    assert STATE["held_out_evaluation_executed"] is False


def test_model_freeze_is_active_but_downstream_gates_are_closed():
    assert FREEZE["safety"]["production_models_frozen"] is True
    assert FREEZE["safety"]["held_out_evaluation_authorized"] is False
    assert FREEZE["safety"]["held_out_evaluation_executed"] is False
    assert FREEZE["safety"]["canonical_execution_authorized"] is False
    assert FREEZE["safety"]["pr_merge_authorized"] is False


def test_held_out_population_is_exactly_196_and_training_is_excluded():
    rows = build_scenario_manifest()
    counts = manifest_counts(rows)
    assert counts["E1"] == 84
    assert counts["E2"] == 104
    assert counts["C0"] == 8
    assert counts["CANONICAL_EVAL_SCENARIOS"] == 196
    assert counts["CANONICAL_EVAL_POLICY_DECISIONS"] == 784
    held = [row for row in rows if row.block in {"E1", "E2", "C0"}]
    assert len(held) == 196
    assert not any(row.block in {"TR0", "TR1"} for row in held)


def test_block_factorization_matches_frozen_design():
    rows = build_scenario_manifest()
    by = {b: [r for r in rows if r.block == b] for b in ("E1", "E2", "C0")}
    assert {r.topology for r in by["E1"]} == {
        "T0_SHARED_ALL", "T1_SEPARATE_SOURCE_EXEC", "T2_SEPARATE_SOURCE_KEY_EXEC"
    }
    assert {r.fault_profile for r in by["E1"]} == {"F6","F7","F8","F9","F10","F11","F12"}
    assert {r.security_signal for r in by["E1"]} == {1}
    assert {r.topology for r in by["E2"]} == {
        "T3_SEPARATE_THROUGH_TRANSPORT", "T4_SEPARATE_ALL"
    }
    assert {r.fault_profile for r in by["E2"]} == {f"F{i}" for i in range(13)}
    assert {r.security_signal for r in by["E2"]} == {1}
    assert {r.topology for r in by["C0"]} == {
        "T3_SEPARATE_THROUGH_TRANSPORT", "T4_SEPARATE_ALL"
    }
    assert {r.fault_profile for r in by["C0"]} == {"F0"}
    assert {r.security_signal for r in by["C0"]} == {0}


def test_policy_orders_and_frozen_feature_widths_are_exact():
    assert PLAN["held_out_population"]["policy_order"] == [
        "D0_BASE", "L0_BASE", "D1_CORROBORATED", "L1_CORROBORATED"
    ]
    assert len(BASE_FEATURES) == 9
    assert len(EXTENDED_FEATURES) == 16
    assert FREEZE["authoritative_semantic_identity"]["L0_BASE"]["features"] == 9
    assert FREEZE["authoritative_semantic_identity"]["L1_CORROBORATED"]["features"] == 16


def test_primary_endpoints_preserve_protocol_definitions():
    p = PLAN["primary_endpoints"]
    joined = json.dumps(p, sort_keys=True)
    for token in (
        "objective_decision_error",
        "unsafe_proceed",
        "false_conservative_hold",
        "D0_BASE versus L0_BASE",
        "D1_CORROBORATED versus L1_CORROBORATED",
        "F10",
        "F11",
    ):
        assert token in joined
    assert PLAN["analysis_rules"]["significance_testing"] is False
    assert PLAN["analysis_rules"]["global_policy_ranking"] is False
    assert PLAN["analysis_rules"]["aggregate_requires_topology_and_fault_stratification"] is True


def test_complete_population_release_requires_zero_invalid_scenarios():
    rule = PLAN["validity_rule"]
    assert rule["final_analysis_release_requires_invalid_scenarios"] == 0
    assert rule["no_hidden_retry"] if "no_hidden_retry" in rule else PLAN["execution_design"]["no_hidden_retry"]
    assert "do not compute/release final complete-population aggregate results" in rule["if_any_invalid"]


def test_independent_audit_does_not_require_joblib_deserialization():
    audit = PLAN["execution_design"]["independent_audit_engine"]
    assert "semantic-tree interpreter" in audit["learned_policies"]
    assert "do not deserialize joblib" in audit["learned_policies"]
    assert PLAN["inference_preflight"]["no_deserialization_during_plan_qualification"] is True


def test_no_inference_authorization_or_executable_workflow_exists():
    assert not (ROOT / "study7e/HELD_OUT_EVALUATION_AUTHORIZATION.json").exists()
    assert not (ROOT / ".github/workflows/study7e-held-out-evaluation.yml").exists()
    assert not (ROOT / "study7e/CANONICAL_EXECUTION_AUTHORIZATION.json").exists()
    assert not (ROOT / ".github/workflows/study7e-canonical-execution.yml").exists()
