from __future__ import annotations

import json
import unittest
from pathlib import Path

from study7e.src.aerc_design import BASE_FEATURES, EXTENDED_FEATURES, build_scenario_manifest
from study7e.tools.run_production_training_001 import datasets, registries, snapshot, training_rows

ROOT = Path(__file__).resolve().parents[2]
AUTH = json.loads((ROOT / "study7e/configs/production_training_authorization_001.json").read_text())
PLAN = json.loads((ROOT / "study7e/configs/production_training_run_plan_001.json").read_text())
FREEZE = json.loads((ROOT / "study7e/FREEZE_MANIFEST_001.json").read_text())
LEARNER = json.loads((ROOT / "study7e/configs/frozen_learner_protocol_001.json").read_text())


class ProductionTrainingExecutionContractTests(unittest.TestCase):
    def test_authorization_scope_is_exact(self) -> None:
        self.assertEqual(AUTH["experiment_id"], "S7E-AERC-001")
        self.assertEqual(AUTH["freeze_id"], "S7E-AERC-FREEZE-001")
        self.assertEqual(AUTH["plan_id"], "S7E-AERC-TRAINPLAN-001")
        self.assertEqual(AUTH["authorization_id"], "S7E-AERC-TRAIN-AUTH-001")
        self.assertEqual(AUTH["state"], "AUTHORIZED_FOR_DETERMINISTIC_PRODUCTION_TRAINING_ONLY")
        self.assertTrue(all(AUTH["authorized"].values()))
        self.assertTrue(all(AUTH["not_authorized"].values()))

    def test_plan_and_frozen_learner_identity_remain_exact(self) -> None:
        self.assertEqual(PLAN["freeze_id"], AUTH["freeze_id"])
        self.assertEqual(FREEZE["freeze_id"], AUTH["freeze_id"])
        self.assertEqual(LEARNER["freeze_id"], AUTH["freeze_id"])
        self.assertEqual(LEARNER["training_blocks"], ["TR0", "TR1"])
        self.assertEqual(LEARNER["prohibited_training_blocks"], ["E1", "E2", "C0"])
        self.assertEqual(LEARNER["hyperparameters"]["random_state"], 2571582253)

    def test_training_rows_are_exact_and_held_out_rows_are_absent(self) -> None:
        rows = training_rows()
        self.assertEqual(len(rows), 84)
        self.assertEqual(sum(r.block == "TR0" for r in rows), 12)
        self.assertEqual(sum(r.block == "TR1" for r in rows), 72)
        self.assertTrue(all(r.block in {"TR0", "TR1"} for r in rows))
        self.assertEqual(rows[0].scenario_id, "TR0-001")
        self.assertEqual(rows[11].scenario_id, "TR0-012")
        self.assertEqual(rows[12].scenario_id, "TR1-001")
        self.assertEqual(rows[-1].scenario_id, "TR1-072")

    def test_opaque_training_ids_match_frozen_examples(self) -> None:
        regs = registries()
        self.assertEqual(regs["scenario"]["TR0-001"], 0xAF8B82F8)
        self.assertEqual(regs["scenario"]["TR1-001"], 0x408AB824)
        self.assertEqual(regs["source"]["primary:source"], 0x0B094571)
        self.assertEqual(regs["key"]["primary:key"], 0xC9B0FE66)
        self.assertEqual(regs["authority"]["primary:authority"], 0x53B10C72)

    def test_dataset_contract_and_label_distribution_are_exact(self) -> None:
        l0, l1 = datasets()
        self.assertEqual(len(l0), 84)
        self.assertEqual(len(l1), 84)
        self.assertTrue(all(len(row["features"]) == len(BASE_FEATURES) for row in l0))
        self.assertTrue(all(len(row["features"]) == len(EXTENDED_FEATURES) for row in l1))
        self.assertEqual([row["scenario_id"] for row in l0], [row["scenario_id"] for row in l1])
        self.assertEqual([row["target"] for row in l0], [row["target"] for row in l1])
        labels: dict[str, int] = {}
        for row in l0:
            labels[row["target"]] = labels.get(row["target"], 0) + 1
            self.assertNotIn(row["block"], {"E1", "E2", "C0"})
        self.assertEqual(labels, {"HOLD": 66, "ENTER_RECOVERY_GATE": 18})

    def test_f5_uses_frozen_evaluation_tick_without_mutating_other_path(self) -> None:
        scenario = next(r for r in build_scenario_manifest() if r.block == "TR1" and r.fault_profile == "F5" and r.topology == "T0_SHARED_ALL" and r.true_authorization == 1 and r.true_health_ready == 1)
        snap = snapshot(scenario, registries(), FREEZE["frozen_execution_parameters"])
        self.assertEqual(snap["primary_fresh"], 0)
        self.assertEqual(snap["corr_fresh"], 1)
        self.assertEqual(snap["primary_signature_valid"], 1)
        self.assertEqual(snap["corr_signature_valid"], 1)

    def test_shared_domain_fault_propagation_is_reflected_in_features(self) -> None:
        scenario = next(r for r in build_scenario_manifest() if r.block == "TR1" and r.fault_profile == "F3" and r.topology == "T0_SHARED_ALL" and r.true_authorization == 1 and r.true_health_ready == 1)
        snap = snapshot(scenario, registries(), FREEZE["frozen_execution_parameters"])
        self.assertEqual(snap["primary_authorization"], 0)
        self.assertEqual(snap["corr_authorization"], 0)
        self.assertEqual(snap["primary_signature_valid"], 1)
        self.assertEqual(snap["corr_signature_valid"], 1)

    def test_training_runner_contains_no_held_out_prediction_or_metrics_path(self) -> None:
        text = (ROOT / "study7e/tools/run_production_training_001.py").read_text()
        self.assertNotIn(".predict(", text)
        self.assertNotIn(".score(", text)
        self.assertNotIn("accuracy_score", text)
        self.assertNotIn("classification_report", text)
        self.assertIn("held_out_evaluation_executed=false", text)
        self.assertIn("production_models_frozen=false", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
