from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from study7e.src.aerc_design import (
    BASE_FEATURES,
    EXTENDED_FEATURES,
    PRIVILEGED_FIELDS,
    build_scenario_manifest,
    objective_action,
)

ROOT = Path(__file__).resolve().parents[2]
PLAN = json.loads((ROOT / "study7e/configs/production_training_run_plan_001.json").read_text())
FREEZE = json.loads((ROOT / "study7e/FREEZE_MANIFEST_001.json").read_text())
LEARNER = json.loads((ROOT / "study7e/configs/frozen_learner_protocol_001.json").read_text())
STATE = json.loads((ROOT / "study7e/TRAINING_PLAN_STATE.json").read_text())


class ProductionTrainingRunPlanTests(unittest.TestCase):
    def test_plan_is_bound_to_frozen_protocol_but_training_is_not_authorized(self) -> None:
        self.assertEqual(PLAN["freeze_id"], "S7E-AERC-FREEZE-001")
        self.assertTrue(all(FREEZE["frozen_components"].values()))
        self.assertTrue(PLAN["authorization"]["plan_preparation_approved"])
        self.assertFalse(PLAN["authorization"]["production_training_authorized"])
        self.assertFalse(PLAN["authorization"]["production_model_freeze_authorized"])
        self.assertFalse(PLAN["authorization"]["canonical_execution_authorized"])
        self.assertFalse(STATE["production_models_trained"])
        self.assertFalse(STATE["production_models_frozen"])
        self.assertFalse(STATE["held_out_evaluation_executed"])
        self.assertFalse(STATE["canonical_execution_authorized"])
        self.assertFalse((ROOT / "study7e/configs/production_training_authorization_001.json").exists())

    def test_training_partition_and_label_distribution_are_exact(self) -> None:
        scenarios = [s for s in build_scenario_manifest() if s.block in {"TR0", "TR1"}]
        counts = Counter(s.block for s in scenarios)
        targets = Counter(objective_action(s) for s in scenarios)
        self.assertEqual(counts, {"TR0": 12, "TR1": 72})
        self.assertEqual(len(scenarios), 84)
        self.assertEqual(targets, {"HOLD": 66, "ENTER_RECOVERY_GATE": 18})
        self.assertEqual(PLAN["training_partition"]["counts"], {"TR0": 12, "TR1": 72, "TOTAL": 84})
        self.assertEqual(PLAN["training_partition"]["expected_target_distribution"], dict(targets))

    def test_evaluation_blocks_are_excluded_from_training(self) -> None:
        self.assertEqual(PLAN["training_partition"]["allowed_blocks"], ["TR0", "TR1"])
        self.assertEqual(PLAN["training_partition"]["prohibited_blocks"], ["E1", "E2", "C0"])
        self.assertFalse(PLAN["snapshot_materialization"]["evaluation_block_capture_for_training"])
        self.assertTrue(PLAN["prohibited_during_plan_qualification"]["E1_E2_C0_access_for_training"])

    def test_feature_orders_match_frozen_design(self) -> None:
        self.assertEqual(tuple(PLAN["learners"]["L0_BASE"]["feature_order"]), BASE_FEATURES)
        self.assertEqual(tuple(PLAN["learners"]["L1_CORROBORATED"]["feature_order"]), EXTENDED_FEATURES)
        self.assertEqual(PLAN["learners"]["L0_BASE"]["records"], 84)
        self.assertEqual(PLAN["learners"]["L1_CORROBORATED"]["records"], 84)
        for feature in PRIVILEGED_FIELDS:
            self.assertNotIn(feature, PLAN["learners"]["L0_BASE"]["feature_order"])
            self.assertNotIn(feature, PLAN["learners"]["L1_CORROBORATED"]["feature_order"])

    def test_hyperparameters_and_runtime_match_frozen_learner_protocol(self) -> None:
        self.assertEqual(PLAN["runtime"]["python"], LEARNER["python_version"])
        self.assertEqual(PLAN["runtime"]["scikit_learn"], LEARNER["library_version"])
        self.assertEqual(PLAN["runtime"]["algorithm"], LEARNER["algorithm"])
        self.assertEqual(PLAN["runtime"]["hyperparameters"], LEARNER["hyperparameters"])
        self.assertEqual(PLAN["training_partition"]["allowed_blocks"], LEARNER["training_blocks"])
        self.assertEqual(PLAN["training_partition"]["prohibited_blocks"], LEARNER["prohibited_training_blocks"])

    def test_dataset_hash_and_dependency_inventory_are_prefit_gates(self) -> None:
        dataset = PLAN["dataset_canonicalization"]
        deps = PLAN["runtime"]["dependency_provenance"]
        self.assertEqual(dataset["required_pre_fit_hash"], "SHA-256 over exact dataset bytes")
        self.assertTrue(dataset["fit_must_abort_if_hash_not_bound_in_training_provenance"])
        self.assertTrue(deps["require_isolated_environment"])
        self.assertTrue(deps["require_dependency_inventory_before_fit"])
        self.assertTrue(deps["require_inventory_sha256"])
        self.assertFalse(deps["exact_transitive_versions_pre_frozen"])

    def test_no_model_artifact_or_training_authorization_exists(self) -> None:
        forbidden_suffixes = {".pkl", ".pickle", ".joblib", ".onnx"}
        model_files = [p for p in (ROOT / "study7e").rglob("*") if p.is_file() and p.suffix.lower() in forbidden_suffixes]
        self.assertEqual(model_files, [])
        self.assertTrue(PLAN["prohibited_during_plan_qualification"]["model_fit"])
        self.assertTrue(PLAN["prohibited_during_plan_qualification"]["model_serialization"])
        self.assertTrue(PLAN["prohibited_during_plan_qualification"]["held_out_evaluation"])

    def test_future_training_sequence_stops_before_held_out_evaluation(self) -> None:
        sequence = PLAN["future_authorized_training_sequence"]
        self.assertIn("fit one primary L0 and one primary L1 estimator with frozen hyperparameters", sequence)
        self.assertIn("perform one deterministic audit refit per learner from the identical bound dataset bytes", sequence)
        self.assertEqual(sequence[-1], "stop before held-out evaluation and request separate model-freeze authorization")
        self.assertTrue(PLAN["model_identity_plan"]["primary_audit_semantic_hash_equality_required"])
        self.assertTrue(PLAN["model_identity_plan"]["no_model_artifact_is_authoritative_until_separate_model_freeze"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
