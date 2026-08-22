from __future__ import annotations

import itertools
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "wp9_campaign_design.json"


class WP9CampaignDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.cells = {row["cell_id"]: row for row in cls.data["cells"]}

    def test_scientific_boundary_blocks_campaign_execution(self) -> None:
        boundary = self.data["scientific_boundary"]
        self.assertTrue(boundary["wp9a_matrix_frozen"])
        self.assertTrue(boundary["endpoint_model_rules_frozen"])
        self.assertFalse(boundary["repetition_count_frozen"])
        self.assertFalse(boundary["runtime_support_complete"])
        self.assertFalse(boundary["campaign_execution_authorized"])

    def test_exact_24_unique_cells(self) -> None:
        self.assertEqual(self.data["design_strategy"]["final_cell_count"], 24)
        self.assertEqual(len(self.cells), 24)
        tuples = {
            (
                row["event_id"],
                row["mission_state_id"],
                row["contact_condition_id"],
                row["evidence_condition_id"],
                row["policy_id"],
            )
            for row in self.cells.values()
        }
        self.assertEqual(len(tuples), 24)

    def _assert_complete_factorial(
        self,
        cell_ids: list[str],
        factors: list[str],
    ) -> None:
        rows = [self.cells[cell_id] for cell_id in cell_ids]
        actual = {
            tuple(row[factor] for factor in factors)
            for row in rows
        }
        levels = [
            sorted({row[factor] for row in rows})
            for factor in factors
        ]
        expected = set(itertools.product(*levels))
        self.assertEqual(actual, expected)

    def test_p1_factorial_complete(self) -> None:
        self._assert_complete_factorial(
            self.data["analysis_contracts"]["P1_mission_state_dependence"]["cell_ids"],
            ["policy_id", "mission_state_id"],
        )

    def test_p2_factorial_complete(self) -> None:
        self._assert_complete_factorial(
            self.data["analysis_contracts"]["P2_contact_delay"]["cell_ids"],
            ["policy_id", "contact_condition_id"],
        )

    def test_p3_factorial_complete(self) -> None:
        self._assert_complete_factorial(
            self.data["analysis_contracts"]["P3_trusted_recovery_evidence"]["cell_ids"],
            ["policy_id", "evidence_condition_id"],
        )

    def test_p4_factorial_complete(self) -> None:
        self._assert_complete_factorial(
            self.data["analysis_contracts"]["P4_degraded_evidence"]["cell_ids"],
            ["event_id", "policy_id", "evidence_condition_id"],
        )

    def test_p6_is_explicit_unresolved_runtime_extension(self) -> None:
        p6 = self.data["required_policy_extension"]
        self.assertEqual(p6["policy_id"], "P6")
        self.assertFalse(p6["existing_experiment_model_support"])
        self.assertFalse(p6["existing_run_schema_support"])
        self.assertFalse(p6["existing_runtime_support"])
        self.assertTrue(p6["wp9b_validation_required"])
        self.assertTrue(p6["campaign_execution_blocked_until_validated"])
        p6_cells = {
            cell_id
            for cell_id, row in self.cells.items()
            if row["policy_id"] == "P6"
        }
        self.assertEqual(p6_cells, {"A16", "A17"})

    def test_p7_expected_delegates_are_frozen(self) -> None:
        expected = {
            "A02": "P1",
            "A04": "P2",
            "A06": "P2",
            "A09": "P4",
            "A11": "P5",
            "A13": "P2",
            "A18": "P5",
            "A21": "P1",
            "A24": "P4",
        }
        actual = {
            cell_id: row["expected_effective_policy_id"]
            for cell_id, row in self.cells.items()
            if row["policy_id"] == "P7"
        }
        self.assertEqual(actual, expected)

    def test_e2_and_e4_have_sentinel_and_matched_comparators(self) -> None:
        self.assertEqual(
            self.data["event_generalization"]["E2_replay"]["cell_ids"],
            ["A19", "A20", "A21"],
        )
        self.assertEqual(
            self.data["event_generalization"]["E4_observability"]["cell_ids"],
            ["A22", "A23", "A24"],
        )
        self.assertEqual(self.cells["A19"]["policy_id"], "P0")
        self.assertEqual(self.cells["A22"]["policy_id"], "P0")

    def test_candidate_totals_match_24_cell_matrix(self) -> None:
        candidates = self.data["repetition_selection"][
            "candidate_valid_repetitions_per_cell"
        ]
        totals = self.data["repetition_selection"][
            "candidate_total_valid_executions"
        ]
        for n in candidates:
            self.assertEqual(totals[str(n)], 24 * n)

    def test_wp9b_is_development_only_and_consumes_no_campaign_seed(self) -> None:
        gate = self.data["wp9b_runtime_gate"]
        self.assertTrue(gate["development_only"])
        self.assertFalse(gate["final_campaign_seed_consumption"])
        self.assertFalse(gate["final_campaign_data_generation"])


if __name__ == "__main__":
    unittest.main()
