from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "study7" / "src"))

from learned_selector_model import (
    evaluation_rows,
    train_visible_only,
    train_with_corroboration,
)


class Study7LearnedSelectorTests(unittest.TestCase):
    def test_learned_weights_are_deterministic(self) -> None:
        l0 = train_visible_only()
        l1 = train_with_corroboration()
        self.assertEqual((l0.quality_weight, l0.authorization_weight, l0.security_weight, l0.threshold), (2, 1, -1, 12))
        self.assertEqual((l1.quality_weight, l1.authorization_weight, l1.corroboration_weight, l1.security_weight, l1.threshold), (2, 0, 1, -1, 12))
        self.assertEqual(l0.training_errors, 0)
        self.assertEqual(l1.training_errors, 0)

    def test_exact_population(self) -> None:
        rows = evaluation_rows()
        self.assertEqual(len(rows), 1033)
        self.assertEqual(sum(r["block"] == "A_VISIBLE_LATTICE" for r in rows), 512)
        self.assertEqual(sum(r["block"] == "B_CORROBORATION_LATTICE" for r in rows), 512)
        self.assertEqual(sum(r["block"] == "C_HIDDEN_TRUTH_COLLISION" for r in rows), 9)

    def test_visible_only_generalization_is_exact_on_visible_lattice(self) -> None:
        rows = [r for r in evaluation_rows() if r["block"] == "A_VISIBLE_LATTICE"]
        self.assertEqual(sum(int(r["objective_decision_error"]) for r in rows), 0)

    def test_corroboration_lattice_has_symmetric_boundary_cost(self) -> None:
        rows = [r for r in evaluation_rows() if r["block"] == "B_CORROBORATION_LATTICE"]
        self.assertEqual(sum(int(r["objective_decision_error"]) for r in rows), 2)
        self.assertEqual(sum(int(r["unsafe_proceed"]) for r in rows), 1)
        self.assertEqual(sum(int(r["false_conservative_hold"]) for r in rows), 1)

    def test_visible_only_models_cannot_resolve_v5_collision(self) -> None:
        rows = [r for r in evaluation_rows() if r["block"] == "C_HIDDEN_TRUTH_COLLISION"]
        for policy in ("D0_S1_VISIBLE_ONLY", "L0_ERM_VISIBLE_ONLY"):
            v5 = [r for r in rows if r["scenario"] == "V5_INDEPENDENT_DISAGREEMENT" and r["policy"] == policy][0]
            self.assertEqual(v5["decision_proceed"], 1)
            self.assertEqual(v5["unsafe_proceed"], 1)

    def test_independent_corroboration_resolves_only_independent_v5_case(self) -> None:
        rows = [r for r in evaluation_rows() if r["block"] == "C_HIDDEN_TRUTH_COLLISION" and r["policy"] == "L1_ERM_WITH_INDEPENDENT_CORROBORATION"]
        by = {r["scenario"]: r for r in rows}
        self.assertEqual(by["SAFE_CORROBORATED"]["decision_proceed"], 1)
        self.assertEqual(by["V5_INDEPENDENT_DISAGREEMENT"]["decision_proceed"], 0)
        self.assertEqual(by["V5_INDEPENDENT_DISAGREEMENT"]["unsafe_proceed"], 0)
        self.assertEqual(by["V5_CORRELATED_FALSE_CORROBORATION"]["decision_proceed"], 1)
        self.assertEqual(by["V5_CORRELATED_FALSE_CORROBORATION"]["unsafe_proceed"], 1)

    def test_hidden_truth_not_present_in_policy_feature_vector(self) -> None:
        l0 = train_visible_only()
        l1 = train_with_corroboration()
        self.assertEqual(l0.predict((1, 1, 1, 1, 1, 1, 1, 1)), 1)
        self.assertEqual(l1.predict((1, 1, 1, 1, 1, 1, 1, 1, 0)), 0)


if __name__ == "__main__":
    unittest.main()
