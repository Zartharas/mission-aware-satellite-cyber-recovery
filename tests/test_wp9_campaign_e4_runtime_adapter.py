from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.wp9_campaign_e4_runtime_adapter import (
    DEVELOPMENT_CASES,
    build_development_plan,
    campaign_execution_preflight,
    construct_authorized_campaign_plan,
    finalize_development_observation,
    validate_static_runtime_adapter,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9_r059_e4_route_validation.sh"


class WP9CampaignE4RuntimeAdapterTests(unittest.TestCase):
    def _plan(self, case_id: str) -> dict:
        row = DEVELOPMENT_CASES[case_id]
        return build_development_plan(
            case_id=case_id,
            run_id=f"wp9-r059-{case_id.lower()}-s{row['development_seed']}-test",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        plan: dict,
        post_visible: int = 0,
        legitimate_delta: int | None = None,
    ) -> dict:
        action = plan["runtime_policy_decision"]["selected_action"]
        expected_legitimate = 1 if action == "OBSERVE_ONLY" else 0
        actual_legitimate = (
            expected_legitimate
            if legitimate_delta is None
            else legitimate_delta
        )
        return {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-22T18:00:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "policy_selection_ns": 2_100_000_000,
            "policy_enforcement_ns": 2_200_000_000,
            "event_success_observed_ns": 4_000_000_000,
            "post_response_probe_observed_ns": 5_000_000_000,
            "authorized_noop_probe_observed_ns": 6_000_000_000,
            "observation_complete_ns": 32_100_000_000,
            "event_truth_high_value_delta": 1,
            "event_policy_visible_high_value_delta": 0,
            "post_response_truth_high_value_delta": 1,
            "post_response_policy_visible_high_value_delta": post_visible,
            "post_response_authorized_noop_attempted": 1,
            "post_response_authorized_noop_marker_delta": actual_legitimate,
            "gateway_decision_count": 1,
            "immutable_truth_separate": True,
            "runtime_health_passed": True,
            "authorized_noop_gateway_action": action,
            "authorized_noop_gateway_forwarded": action == "OBSERVE_ONLY",
        }

    def test_static_adapter_reserves_only_new_noncampaign_validation_seeds(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(result["decision_id"], "R-059")
        self.assertEqual(
            result["development_cases"],
            {
                "W01": {"cell_id": "A22", "development_seed": 9911},
                "W02": {"cell_id": "A23", "development_seed": 9912},
                "W03": {"cell_id": "A24", "development_seed": 9913},
            },
        )
        self.assertTrue(result["development_validation_only"])
        self.assertTrue(result["one_case_per_invocation"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertTrue(result["campaign_plan_constructed_internally_when_authorized"])
        self.assertFalse(result["external_campaign_plan_accepted"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_development_plans_cover_fixed_and_adaptive_e4_paths(self) -> None:
        expected = {
            "W01": ("A22", 9911, "P0", "P0", "OBSERVE_ONLY"),
            "W02": ("A23", 9912, "P4", "P4", "ENTER_SAFE_MODE"),
            "W03": ("A24", 9913, "P7", "P4", "ENTER_SAFE_MODE"),
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

    def test_expected_route_validation_observations_pass(self) -> None:
        for case_id in ("W01", "W02", "W03"):
            plan = self._plan(case_id)
            summary = finalize_development_observation(
                plan=plan,
                measurement=self._measurement(plan=plan),
            )
            self.assertEqual(summary["acceptance_status"], "PASS")
            self.assertTrue(summary["treatment_fidelity_valid"])
            self.assertTrue(summary["raw_metric_inputs_complete"])
            self.assertTrue(summary["outcome_matches_predeclared_expectation"])
            self.assertFalse(summary["telemetry_restored_observed"])
            self.assertFalse(summary["trusted_recovery_fabricated"])
            self.assertFalse(summary["native_spacecraft_safe_mode_claim"])

    def test_unexpected_w01_legitimate_service_loss_is_retained(self) -> None:
        plan = self._plan("W01")
        summary = finalize_development_observation(
            plan=plan,
            measurement=self._measurement(
                plan=plan,
                legitimate_delta=0,
            ),
        )
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertFalse(summary["outcome_matches_predeclared_expectation"])
        self.assertTrue(
            summary[
                "unexpected_scientific_outcome_would_be_retained_in_campaign"
            ]
        )
        self.assertTrue(summary["authorized_noop_gateway_forwarded"])
        self.assertEqual(summary["post_response_authorized_noop_marker_delta"], 0)

    def test_unexpected_telemetry_restoration_is_retained_without_recovery_claim(self) -> None:
        plan = self._plan("W02")
        summary = finalize_development_observation(
            plan=plan,
            measurement=self._measurement(
                plan=plan,
                post_visible=1,
            ),
        )
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertTrue(summary["telemetry_restored_observed"])
        self.assertFalse(summary["outcome_matches_predeclared_expectation"])
        self.assertTrue(
            summary[
                "unexpected_scientific_outcome_would_be_retained_in_campaign"
            ]
        )
        self.assertFalse(summary["trusted_recovery_fabricated"])
        self.assertFalse(summary["native_spacecraft_safe_mode_claim"])

    def test_event_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("W01")
        measurement = self._measurement(plan=plan)
        measurement["event_policy_visible_high_value_delta"] = 1
        with self.assertRaisesRegex(ValueError, "degraded policy-visible treatment"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_gateway_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("W02")
        measurement = self._measurement(plan=plan)
        measurement["authorized_noop_gateway_forwarded"] = True
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_campaign_plan_is_constructed_from_r054_not_accepted_externally(self) -> None:
        plan = construct_authorized_campaign_plan(
            campaign_seed=10001,
            cell_id="A24",
            run_id="wp9-r059-a24-s10001-plan-only",
            repo_commit="b" * 40,
        )
        self.assertEqual(plan["decision_id"], "R-054")
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["cell_id"], "A24")
        self.assertEqual(plan["runtime_variant"], "e4_observability")
        self.assertFalse(plan["execution_boundary"]["campaign_seed_consumed"])
        self.assertFalse(
            plan["execution_boundary"]["final_campaign_execution_authorized"]
        )

    def test_campaign_execution_remains_blocked(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "campaign execution remains blocked",
        ):
            campaign_execution_preflight()

    def test_runner_is_bash32_safe_and_development_only(self) -> None:
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("results/wp9/development/r059/e4", text)
        self.assertNotIn("results/wp9/campaign", text)
        self.assertIn('W01) CELL_ID="A22"; SEED="9911"', text)
        self.assertIn('W02) CELL_ID="A23"; SEED="9912"', text)
        self.assertIn('W03) CELL_ID="A24"; SEED="9913"', text)
        self.assertIn("DURATION_SECONDS=90", text)
        self.assertIn("automatic_retry_allowed=false", text)
        self.assertIn("automatic_next_case_allowed=false", text)
        self.assertNotIn("mapfile", text)
        self.assertNotIn("readarray", text)
        self.assertNotIn("declare -A", text)

    def test_runner_separates_operational_capture_from_frozen_horizon(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("OPERATIONAL_VISIBILITY_CAPTURE_SECONDS=3", text)
        self.assertIn("operational_visibility_capture_used_as_analysis_horizon=false", text)
        self.assertIn(
            "ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))",
            text,
        )
        self.assertIn('PHASE="POST_RESPONSE_AUTHORIZED_NOOP"', text)
        self.assertIn("post_event_analysis_horizon_s=30", text)

    def test_runner_releases_auxiliaries_before_nominal_teardown_and_audits_residue(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        auxiliary = text.index('PHASE="AUXILIARY_CLEANUP"')
        nominal = text.index('PHASE="NOMINAL_RUNTIME_COMPLETION"')
        audit = text.index('PHASE="CLEANUP_AUDIT"')
        self.assertLess(auxiliary, nominal)
        self.assertLess(nominal, audit)
        self.assertIn(
            'docker rm -f "$GATEWAY" "$PROXY" "$OBSERVER"',
            text[auxiliary:nominal],
        )
        self.assertIn('docker network rm "$NETWORK"', text[audit:])
        self.assertIn("residual_runtime=none", text[audit:])


if __name__ == "__main__":
    unittest.main()
