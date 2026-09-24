from __future__ import annotations

import unittest

from study7e.models.training_contracts import (
    LearnerCandidateSpec,
    TrainingRecord,
    make_training_record,
    validate_training_partition,
)
from study7e.src.aerc_design import BASE_FEATURES, EXTENDED_FEATURES


class TrainingBoundaryTests(unittest.TestCase):
    def _snapshot(self) -> dict[str, int]:
        return {feature: 1 for feature in EXTENDED_FEATURES}

    def test_evaluation_blocks_are_rejected(self) -> None:
        for block in ("E1", "E2", "C0"):
            with self.assertRaises(ValueError):
                make_training_record(
                    policy_id="L0_BASE",
                    scenario_id=f"{block}-001",
                    block=block,
                    snapshot=self._snapshot(),
                    target="HOLD",
                )

    def test_privileged_fields_are_rejected(self) -> None:
        snapshot = self._snapshot()
        snapshot["true_authorization"] = 1
        with self.assertRaises(ValueError):
            make_training_record(
                policy_id="L1_CORROBORATED",
                scenario_id="TR1-001",
                block="TR1",
                snapshot=snapshot,
                target="ENTER_RECOVERY_GATE",
            )

    def test_policy_feature_orders_are_exact(self) -> None:
        snapshot = self._snapshot()
        l0 = make_training_record(
            policy_id="L0_BASE",
            scenario_id="TR1-001",
            block="TR1",
            snapshot=snapshot,
            target="ENTER_RECOVERY_GATE",
        )
        l1 = make_training_record(
            policy_id="L1_CORROBORATED",
            scenario_id="TR1-002",
            block="TR1",
            snapshot=snapshot,
            target="ENTER_RECOVERY_GATE",
        )
        self.assertEqual(len(l0.features), len(BASE_FEATURES))
        self.assertEqual(len(l1.features), len(EXTENDED_FEATURES))

    def test_candidate_spec_must_not_be_frozen(self) -> None:
        good = LearnerCandidateSpec(
            policy_id="L0_BASE",
            algorithm="DecisionTreeClassifier",
            feature_order=BASE_FEATURES,
            library="scikit-learn",
            library_version=None,
            hyperparameters={},
            frozen=False,
        )
        good.validate_precanonical()

        bad = LearnerCandidateSpec(
            policy_id="L0_BASE",
            algorithm="DecisionTreeClassifier",
            feature_order=BASE_FEATURES,
            library="scikit-learn",
            library_version="candidate",
            hyperparameters={},
            frozen=True,
        )
        with self.assertRaises(ValueError):
            bad.validate_precanonical()

    def test_exact_training_partition(self) -> None:
        rows: list[TrainingRecord] = []
        for i in range(1, 13):
            rows.append(TrainingRecord(f"TR0-{i:03d}", "TR0", (0,) * len(BASE_FEATURES), "HOLD"))
        for i in range(1, 73):
            rows.append(TrainingRecord(f"TR1-{i:03d}", "TR1", (0,) * len(BASE_FEATURES), "HOLD"))
        self.assertEqual(
            validate_training_partition(rows),
            {"TR0": 12, "TR1": 72, "TOTAL": 84},
        )

    def test_duplicate_training_scenario_is_rejected(self) -> None:
        row = TrainingRecord("TR0-001", "TR0", (0,) * len(BASE_FEATURES), "HOLD")
        with self.assertRaises(ValueError):
            validate_training_partition([row, row])


if __name__ == "__main__":
    unittest.main()
