from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class WP9CRepetitionFreezeTests(unittest.TestCase):
    def test_r051_freezes_only_the_reviewed_smallest_passing_candidate(self) -> None:
        freeze = load(ROOT / "configs/wp9c_repetition_freeze.json")
        method = load(ROOT / "configs/wp9c_repetition_selection.json")
        campaign = load(ROOT / "configs/wp9_campaign_design.json")

        self.assertEqual(freeze["decision_id"], "R-051")
        self.assertEqual(
            method["candidate_valid_repetitions_per_cell"],
            campaign["repetition_selection"]["candidate_valid_repetitions_per_cell"],
        )
        self.assertEqual(freeze["reviewed_result"]["selected_valid_repetitions_per_cell"], 30)
        self.assertEqual(freeze["reviewed_result"]["selected_total_valid_executions"], 720)
        self.assertEqual(
            freeze["reviewed_result"]["selected_valid_repetitions_per_cell"],
            max(method["candidate_valid_repetitions_per_cell"]),
        )
        self.assertFalse(freeze["candidate_review"]["24"]["overall_pass"])
        self.assertTrue(freeze["candidate_review"]["30"]["overall_pass"])
        self.assertLess(
            freeze["candidate_review"]["24"]["minimum_model_stability_rate"],
            method["precision_targets"]["model_fit_convergence_rate"],
        )
        self.assertGreaterEqual(
            freeze["candidate_review"]["30"]["minimum_model_stability_rate"],
            method["precision_targets"]["model_fit_convergence_rate"],
        )
        self.assertEqual(
            freeze["basis"]["local_selection_result_sha256"],
            "027a83947537ddcaa9b6700cb543e4749b079502dcedc2290d86e9ea75b1bbb1",
        )
        self.assertTrue(freeze["scientific_boundary"]["repetition_count_frozen"])
        for key in (
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            self.assertFalse(freeze["scientific_boundary"][key], key)
        blockers = freeze["remaining_precampaign_blockers"]
        self.assertFalse(blockers["final_c1_contact_window_duration_frozen"])
        self.assertFalse(blockers["campaign_seed_schedule_frozen"])
        self.assertFalse(blockers["final_campaign_runner_validated"])
        self.assertFalse(blockers["explicit_final_campaign_execution_authorization"])


if __name__ == "__main__":
    unittest.main()
