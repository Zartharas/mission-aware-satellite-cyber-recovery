from __future__ import annotations

import unittest

from src.mission_recovery.wp9_campaign_e1_runtime_adapter import (
    DEVELOPMENT_CASES,
    build_development_plan,
    campaign_execution_preflight,
    construct_authorized_campaign_plan,
    development_execution_preflight,
    finalize_development_observation,
    validate_static_runtime_adapter,
)


class WP9CampaignE1RuntimeAdapterTests(unittest.TestCase):
    def _plan(self, case_id: str) -> dict:
        row = DEVELOPMENT_CASES[case_id]
        return build_development_plan(
            case_id=case_id,
            run_id=f"wp9-r061-{case_id.lower()}-s{row['development_seed']}-test",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        plan: dict,
        attacker_delta: int | None = None,
        legitimate_delta: int | None = None,
    ) -> dict:
        action = plan["runtime_policy_decision"]["selected_action"]
        authorized_forwarded = action != "ENTER_SAFE_MODE"
        actual_attacker = 0 if attacker_delta is None else attacker_delta
        actual_legitimate = (
            (1 if authorized_forwarded else 0)
            if legitimate_delta is None
            else legitimate_delta
        )
        return {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-22T19:00:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "policy_selection_ns": 2_100_000_000,
            "policy_enforcement_ns": 2_200_000_000,
            "event_success_observed_ns": 2_300_000_000,
            "second_attacker_probe_observed_ns": 4_000_000_000,
            "authorized_noop_probe_observed_ns": 5_000_000_000,
            "observation_complete_ns": 32_100_000_000,
            "event_activation_reset_marker_delta": 1,
            "post_enforcement_attacker_probe_count": 2,
            "post_enforcement_attacker_reset_marker_delta": actual_attacker,
            "legitimate_commands_attempted": 1,
            "authorized_noop_marker_delta": actual_legitimate,
            "gateway_decision_count": 3,
            "attacker_gateway_forwarded_count": 0,
            "authorized_noop_gateway_forwarded": authorized_forwarded,
            "runtime_health_passed": True,
            "policy_selection_not_gated_on_event_success": True,
            "attacker_gateway_action": action,
            "authorized_noop_gateway_action": action,
        }

    def test_static_adapter_reserves_minimal_noncampaign_validation_set(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(result["decision_id"], "R-061")
        self.assertEqual(
            result["development_cases"],
            {
                "X01": {"cell_id": "A05", "development_seed": 9921},
                "X02": {"cell_id": "A08", "development_seed": 9922},
                "X03": {"cell_id": "A02", "development_seed": 9923},
                "X04": {"cell_id": "A06", "development_seed": 9924},
                "X05": {"cell_id": "A09", "development_seed": 9925},
            },
        )
        self.assertTrue(result["minimal_distinct_policy_path_set"])
        self.assertTrue(result["development_validation_only"])
        self.assertTrue(result["one_case_per_invocation"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["development_runtime_execution_authorized"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_development_set_covers_all_distinct_paths_and_factor_span(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(
            result["covered_requested_effective_paths"],
            [
                ["P1", "P1"],
                ["P2", "P2"],
                ["P7", "P1"],
                ["P7", "P2"],
                ["P7", "P4"],
            ],
        )
        self.assertEqual(result["covered_mission_states"], ["M0", "M2", "M4"])
        self.assertEqual(result["covered_evidence_conditions"], ["T0", "T1"])

    def test_development_plans_cover_fixed_and_adaptive_e1_paths(self) -> None:
        expected = {
            "X01": ("A05", 9921, "P1", "P1", "ISOLATE_MODELED_SOURCE"),
            "X02": ("A08", 9922, "P2", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "X03": ("A02", 9923, "P7", "P1", "ISOLATE_MODELED_SOURCE"),
            "X04": ("A06", 9924, "P7", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "X05": ("A09", 9925, "P7", "P4", "ENTER_SAFE_MODE"),
        }
        for case_id, values in expected.items():
            plan = self._plan(case_id)
            self.assertEqual(plan["cell_id"], values[0])
            self.assertEqual(plan["development_seed"], values[1])
            self.assertEqual(plan["factor_context"]["policy_id"], values[2])
            self.assertEqual(
                plan["runtime_policy_decision"]["delegated_policy_id"],
                values[3],
            )
            self.assertEqual(
                plan["runtime_policy_decision"]["selected_action"],
                values[4],
            )
            self.assertFalse(
                plan["runtime_policy_decision"]["oracle_ground_truth_read"]
            )
            self.assertFalse(plan["development_runtime_execution_authorized"])
            self.assertFalse(plan["campaign_seed_consumed"])

    def test_expected_route_validation_observations_pass(self) -> None:
        for case_id in ("X01", "X02", "X03", "X04", "X05"):
            plan = self._plan(case_id)
            summary = finalize_development_observation(
                plan=plan,
                measurement=self._measurement(plan=plan),
            )
            self.assertEqual(summary["acceptance_status"], "PASS")
            self.assertTrue(summary["treatment_fidelity_valid"])
            self.assertTrue(summary["raw_metric_inputs_complete"])
            self.assertTrue(summary["outcome_matches_predeclared_expectation"])
            self.assertFalse(summary["oracle_ground_truth_read"])
            self.assertFalse(summary["campaign_seed_consumed"])
            self.assertFalse(summary["campaign_data_generated"])

    def test_unexpected_attacker_effect_is_retained_as_science(self) -> None:
        plan = self._plan("X01")
        summary = finalize_development_observation(
            plan=plan,
            measurement=self._measurement(plan=plan, attacker_delta=1),
        )
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertEqual(summary["attacker_gateway_forwarded_count"], 0)
        self.assertEqual(summary["post_enforcement_attacker_reset_marker_delta"], 1)
        self.assertFalse(summary["outcome_matches_predeclared_expectation"])
        self.assertTrue(
            summary["unexpected_scientific_outcome_would_be_retained_in_campaign"]
        )

    def test_unexpected_legitimate_service_loss_is_retained_as_science(self) -> None:
        plan = self._plan("X02")
        summary = finalize_development_observation(
            plan=plan,
            measurement=self._measurement(plan=plan, legitimate_delta=0),
        )
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertTrue(summary["authorized_noop_gateway_forwarded"])
        self.assertEqual(summary["post_response_authorized_noop_marker_delta"], 0)
        self.assertFalse(summary["outcome_matches_predeclared_expectation"])
        self.assertTrue(
            summary["unexpected_scientific_outcome_would_be_retained_in_campaign"]
        )

    def test_event_activation_failure_is_invalid(self) -> None:
        plan = self._plan("X03")
        measurement = self._measurement(plan=plan)
        measurement["event_activation_reset_marker_delta"] = 0
        with self.assertRaisesRegex(ValueError, "activation effect"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_gateway_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("X04")
        measurement = self._measurement(plan=plan)
        measurement["attacker_gateway_forwarded_count"] = 2
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_probe_sequence_requires_two_attackers_and_one_authorized_noop(self) -> None:
        plan = self._plan("X01")
        measurement = self._measurement(plan=plan)
        measurement["post_enforcement_attacker_probe_count"] = 1
        with self.assertRaisesRegex(ValueError, "exactly two"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

        measurement = self._measurement(plan=plan)
        measurement["legitimate_commands_attempted"] = 0
        with self.assertRaisesRegex(ValueError, "one post-response authorized NOOP"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_policy_selection_cannot_be_ground_truth_gated(self) -> None:
        plan = self._plan("X05")
        measurement = self._measurement(plan=plan)
        measurement["policy_selection_not_gated_on_event_success"] = False
        with self.assertRaisesRegex(ValueError, "gated on ground-truth"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_full_thirty_second_analysis_horizon_is_required(self) -> None:
        plan = self._plan("X02")
        measurement = self._measurement(plan=plan)
        measurement["observation_complete_ns"] = 31_900_000_000
        with self.assertRaisesRegex(ValueError, "30-second analysis horizon"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_campaign_plan_is_constructed_but_all_execution_remains_blocked(self) -> None:
        plan = construct_authorized_campaign_plan(
            campaign_seed=10001,
            cell_id="A09",
            run_id="wp9-r061-a09-s10001-plan-only",
            repo_commit="b" * 40,
        )
        self.assertEqual(plan["decision_id"], "R-054")
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["cell_id"], "A09")
        self.assertEqual(plan["runtime_variant"], "e1_command_gateway")
        self.assertFalse(plan["execution_boundary"]["campaign_seed_consumed"])
        self.assertFalse(
            plan["execution_boundary"]["final_campaign_execution_authorized"]
        )

        with self.assertRaisesRegex(
            PermissionError,
            "development runtime remains blocked",
        ):
            development_execution_preflight()

        with self.assertRaisesRegex(
            PermissionError,
            "campaign execution remains blocked",
        ):
            campaign_execution_preflight()


if __name__ == "__main__":
    unittest.main()
