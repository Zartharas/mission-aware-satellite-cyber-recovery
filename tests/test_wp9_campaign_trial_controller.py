from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.mission_recovery.wp9_campaign_trial_controller import (
    build_trial_plan,
    execution_preflight,
    validate_static_controller,
)


class WP9CampaignTrialControllerTests(unittest.TestCase):
    def test_static_controller_binds_frozen_design_without_execution(self):
        result = validate_static_controller()
        self.assertEqual(result["decision_id"], "R-054")
        self.assertEqual(result["campaign_cell_count"], 24)
        self.assertEqual(result["campaign_seed_block_count"], 30)
        self.assertEqual(result["valid_repetitions_per_cell"], 30)
        self.assertEqual(result["planned_valid_executions"], 720)
        self.assertEqual(result["c1_contact_window_s"], 10)
        self.assertEqual(result["e3_post_event_analysis_horizon_s"], 30)
        self.assertFalse(result["campaign_safe_route_adapters_ready"])
        self.assertFalse(result["authorization_contract_present"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_first_frozen_block_plan_preserves_order_and_route(self):
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id="A19",
            run_id="wp9-campaign-a19-s10001-attempt1",
            repo_commit="a" * 40,
        )
        self.assertEqual(plan["block_index"], 1)
        self.assertEqual(plan["cell_order_index"], 1)
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["cell_id"], "A19")
        self.assertEqual(plan["runtime_family"], "replay")
        self.assertEqual(plan["runtime_variant"], "e2_replay_effect")
        self.assertIsNone(plan["timing_contract"]["e3_post_event_analysis_horizon_s"])
        self.assertFalse(plan["execution_boundary"]["automatic_retry_allowed"])
        self.assertFalse(plan["execution_boundary"]["automatic_next_case_allowed"])
        self.assertFalse(plan["execution_boundary"]["campaign_seed_consumed"])

    def test_p6_c1_plan_uses_final_timing_not_development_surrogate(self):
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id="A17",
            run_id="wp9-campaign-a17-s10001-attempt1",
            repo_commit="b" * 40,
        )
        timing = plan["timing_contract"]
        self.assertEqual(plan["factor_context"]["policy_id"], "P6")
        self.assertEqual(plan["factor_context"]["contact_condition_id"], "C1")
        self.assertEqual(timing["modeled_c1_contact_window_s"], 10)
        self.assertEqual(timing["p6_ground_authorization_release_after_event_s"], 10)
        self.assertEqual(timing["e3_post_event_analysis_horizon_s"], 30)
        self.assertTrue(timing["unrecovered_e3_right_censored_at_horizon"])

    def test_autonomous_c1_plan_does_not_invent_ground_authorization_wait(self):
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id="A18",
            run_id="wp9-campaign-a18-s10001-attempt1",
            repo_commit="c" * 40,
        )
        timing = plan["timing_contract"]
        self.assertEqual(plan["factor_context"]["policy_id"], "P7")
        self.assertEqual(timing["modeled_c1_contact_window_s"], 10)
        self.assertIsNone(timing["p6_ground_authorization_release_after_event_s"])
        self.assertEqual(timing["e3_post_event_analysis_horizon_s"], 30)

    def test_unknown_seed_is_rejected_before_consumption(self):
        with self.assertRaisesRegex(ValueError, "not in frozen R-053"):
            build_trial_plan(
                campaign_seed=9999,
                cell_id="A01",
                run_id="wp9-invalid-seed",
                repo_commit="d" * 40,
            )

    def test_unknown_cell_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not in frozen A01-A24"):
            build_trial_plan(
                campaign_seed=10001,
                cell_id="A25",
                run_id="wp9-invalid-cell",
                repo_commit="e" * 40,
            )

    def test_run_identity_inputs_are_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "run_id"):
            build_trial_plan(
                campaign_seed=10001,
                cell_id="A19",
                run_id="bad run id",
                repo_commit="f" * 40,
            )
        with self.assertRaisesRegex(ValueError, "repo_commit"):
            build_trial_plan(
                campaign_seed=10001,
                cell_id="A19",
                run_id="good-run-id",
                repo_commit="not-a-commit",
            )

    def test_execution_entry_point_is_unconditionally_blocked_at_r054(self):
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id="A19",
            run_id="wp9-r054-execution-block",
            repo_commit="1" * 40,
        )
        with self.assertRaisesRegex(PermissionError, "separate explicit authorization"):
            execution_preflight(plan=plan)


if __name__ == "__main__":
    unittest.main()
