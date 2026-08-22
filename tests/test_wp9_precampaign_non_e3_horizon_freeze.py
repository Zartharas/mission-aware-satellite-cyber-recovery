from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "configs" / "wp9_precampaign_non_e3_horizon_freeze.json"
DESIGN = ROOT / "configs" / "wp9_campaign_design.json"
E3_TIMING = ROOT / "configs" / "wp9_precampaign_timing_freeze.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class WP9PrecampaignNonE3HorizonFreezeTests(unittest.TestCase):
    def test_r055_freezes_common_horizon_without_authorizing_runtime(self) -> None:
        freeze = load(FREEZE)
        design = load(DESIGN)
        timing = load(E3_TIMING)

        self.assertEqual(freeze["decision_id"], "R-055")
        self.assertEqual(
            freeze["status"],
            "WP9_COMMON_POST_EVENT_ANALYSIS_HORIZON_FROZEN_EXECUTION_UNAUTHORIZED",
        )

        p5 = design["analysis_contracts"]["P5_tradeoff"]
        self.assertIn("time_to_verified_recovery_s", p5["primary_endpoints"])

        cells = {row["cell_id"]: row for row in design["cells"]}
        grouped = {
            cell_id
            for group in p5["condition_groups"].values()
            for cell_id in group
        }
        self.assertEqual(grouped, set(cells))
        self.assertEqual(
            {cells[cell_id]["event_id"] for cell_id in grouped},
            {"E1", "E2", "E3", "E4"},
        )

        e3_horizon = timing["frozen_timing"][
            "e3_common_post_event_analysis_horizon_s"
        ]
        self.assertEqual(e3_horizon, 30)

        horizons = freeze["frozen_horizons"]
        self.assertEqual(horizons["analysis_time_origin"], "event_activation_t0")
        self.assertEqual(horizons["common_post_event_analysis_horizon_s"], 30)
        for event_id in ("E1", "E2", "E3", "E4"):
            self.assertEqual(
                horizons[f"{event_id}_post_event_analysis_horizon_s"],
                30,
            )
        self.assertTrue(horizons["unobserved_containment_right_censored_at_horizon"])
        self.assertTrue(
            horizons["unobserved_trusted_recovery_right_censored_at_horizon"]
        )
        self.assertTrue(
            horizons[
                "early_terminal_allowed_only_after_required_raw_metric_inputs_complete"
            ]
        )
        self.assertFalse(
            horizons["runner_wall_clock_or_nominal_duration_used_as_metric_input"]
        )

        rationale = freeze["scientific_rationale"]
        self.assertTrue(rationale["right_censoring_preserved_by_r044"])
        self.assertTrue(rationale["p5_tradeoff_includes_time_to_verified_recovery_s"])
        self.assertTrue(rationale["p5_tradeoff_spans_e1_e2_e3_e4_condition_groups"])
        self.assertTrue(rationale["common_horizon_avoids_route_dependent_censoring"])
        self.assertFalse(
            rationale["pilot_or_development_outcomes_used_to_select_horizon"]
        )

        for rel in (
            "scripts/run_wp8_command_stage1_development.sh",
            "scripts/run_wp9b2_e2_development.sh",
            "scripts/run_wp9b2_e4_fixed_development.sh",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("DURATION_SECONDS=60", text)

        envelope = freeze["runtime_envelope_requirements"]
        self.assertTrue(
            envelope[
                "runtime_must_remain_available_through_analysis_horizon_when_no_earlier_valid_absorbing_terminal"
            ]
        )
        self.assertTrue(
            envelope["route_adapter_must_fail_run_invalid_if_runtime_ends_before_required_horizon"]
        )
        self.assertTrue(
            envelope["runtime_envelope_duration_is_operational_not_an_analysis_metric"]
        )

        ready = freeze["campaign_readiness_effect"]
        self.assertTrue(ready["all_event_post_event_analysis_horizons_frozen"])
        self.assertFalse(ready["campaign_safe_route_adapters_ready"])
        self.assertFalse(ready["campaign_runtime_execution_performed"])
        self.assertFalse(ready["campaign_seed_consumed"])
        self.assertFalse(ready["campaign_data_generated"])
        self.assertFalse(ready["final_campaign_execution_authorized"])

        boundary = freeze["scientific_boundary"]
        self.assertFalse(boundary["expected_values_used_as_metric_inputs"])
        self.assertFalse(boundary["ground_truth_policy_oracle_allowed"])
        self.assertFalse(boundary["wp8_pilot_data_mutated"])
        self.assertFalse(boundary["development_runtime_reclassified_as_campaign_data"])
        self.assertFalse(boundary["campaign_runtime_execution_performed"])
        self.assertFalse(boundary["campaign_seed_consumed"])
        self.assertFalse(boundary["campaign_data_generated"])
        self.assertFalse(boundary["final_campaign_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
