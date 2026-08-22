from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class WP9PrecampaignTimingFreezeTests(unittest.TestCase):
    def test_r052_freezes_only_reviewed_modeled_timing_without_campaign_authorization(self) -> None:
        r052 = load("configs/wp9_precampaign_timing_freeze.json")
        r051 = load("configs/wp9c_repetition_freeze.json")
        r047 = load("configs/wp9b2_p6_runtime_gate.json")
        campaign = load("configs/wp9_campaign_design.json")

        self.assertEqual(r052["decision_id"], "R-052")
        self.assertEqual(
            r052["reviewed_timing_result"]["review_artifact_sha256"],
            "33b9ded122d3d0da9894622ad12713d5757064ed77e5c1dcce54274bea80efbe",
        )
        self.assertTrue(
            r052["reviewed_timing_result"]["review_result_reviewed"]
        )
        self.assertFalse(
            r052["reviewed_timing_result"]["development_2s_surrogate_reused"]
        )
        self.assertFalse(
            r052["reviewed_timing_result"]["pilot_run_end_used_as_common_horizon"]
        )

        timing = r052["frozen_timing"]
        self.assertEqual(timing["c1_semantics"]["modeled_contact_window_s"], 10)
        self.assertEqual(
            timing["c1_semantics"]["authorization_available_after_event_response_boundary_s"],
            10,
        )
        self.assertEqual(timing["e3_common_post_event_analysis_horizon_s"], 30)
        self.assertEqual(timing["post_c1_observation_allowance_s"], 20)
        self.assertTrue(timing["early_absorbing_trusted_recovery_allowed"])
        self.assertTrue(timing["unrecovered_e3_run_right_censored_at_horizon"])

        max_recovery = r052["reviewed_timing_result"]["max_verified_recovery_s"]
        self.assertGreaterEqual(
            timing["post_c1_observation_allowance_s"],
            2.0 * max_recovery,
        )
        self.assertEqual(
            timing["e3_common_post_event_analysis_horizon_s"],
            3 * timing["c1_semantics"]["modeled_contact_window_s"],
        )

        e3_cells = [
            row["cell_id"]
            for row in campaign["cells"]
            if row["event_id"] == "E3"
        ]
        self.assertEqual(timing["e3_campaign_cell_ids"], e3_cells)
        self.assertEqual(
            e3_cells,
            ["A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18"],
        )

        development_window = r047["development_contact_window"]
        self.assertEqual(development_window["seconds"], 2)
        self.assertFalse(development_window["final_campaign_parameter"])
        self.assertFalse(development_window["final_campaign_duration_frozen"])

        self.assertTrue(r051["scientific_boundary"]["repetition_count_frozen"])
        self.assertEqual(
            r051["reviewed_result"]["selected_valid_repetitions_per_cell"],
            30,
        )
        self.assertEqual(
            r051["reviewed_result"]["selected_total_valid_executions"],
            720,
        )

        readiness = r052["campaign_readiness_effect"]
        self.assertTrue(readiness["final_c1_contact_window_duration_frozen"])
        self.assertTrue(readiness["e3_analysis_horizon_frozen"])
        self.assertTrue(readiness["timing_blocker_closed"])
        self.assertEqual(readiness["valid_repetitions_per_cell"], 30)
        self.assertEqual(readiness["planned_total_valid_executions"], 720)
        self.assertFalse(readiness["campaign_runtime_execution_performed"])
        self.assertFalse(readiness["campaign_seed_consumed"])
        self.assertFalse(readiness["campaign_data_generated"])
        self.assertFalse(readiness["final_campaign_execution_authorized"])

        boundary = r052["scientific_boundary"]
        self.assertFalse(boundary["campaign_runtime_execution_performed"])
        self.assertFalse(boundary["campaign_seed_consumed"])
        self.assertFalse(boundary["campaign_data_generated"])
        self.assertFalse(boundary["final_campaign_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
