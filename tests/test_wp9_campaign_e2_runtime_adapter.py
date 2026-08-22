from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.wp9_campaign_e2_runtime_adapter import (
    DEVELOPMENT_CASES,
    build_development_plan,
    campaign_execution_preflight,
    construct_authorized_campaign_plan,
    finalize_development_observation,
    validate_static_runtime_adapter,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9_r057_e2_route_validation.sh"


class WP9CampaignE2RuntimeAdapterTests(unittest.TestCase):
    def _plan(self, case_id: str) -> dict:
        row = DEVELOPMENT_CASES[case_id]
        return build_development_plan(
            case_id=case_id,
            run_id=f"wp9-r057-{case_id.lower()}-s{row['development_seed']}-test",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        plan: dict,
        replay_delta: int | None = None,
    ) -> dict:
        action = plan["runtime_policy_decision"]["selected_action"]
        expected = 1 if plan["cell_id"] == "A19" else 0
        actual = expected if replay_delta is None else replay_delta
        replay_forwarded = action == "OBSERVE_ONLY"
        return {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-22T18:00:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "policy_enforcement_ns": 2_100_000_000,
            "replay_gateway_decision_ns": 2_200_000_000,
            "replay_effect_observed_ns": (
                2_300_000_000 if actual == 1 else None
            ),
            "authorized_noop_probe_observed_ns": 2_400_000_000,
            "observation_complete_ns": 32_100_000_000,
            "setup_reset_marker_delta": 1,
            "intervening_authorized_noop_marker_delta": 1,
            "post_replay_reset_marker_delta": actual,
            "post_response_authorized_noop_attempted": 1,
            "post_response_authorized_noop_marker_delta": 1,
            "gateway_decision_count": 2,
            "replayed_packet_byte_identical": True,
            "runtime_health_passed": True,
            "replay_gateway_action": action,
            "replay_gateway_forwarded": replay_forwarded,
            "authorized_noop_gateway_action": action,
            "authorized_noop_gateway_forwarded": True,
        }

    def test_static_adapter_reserves_only_noncampaign_validation_seeds(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(result["decision_id"], "R-057")
        self.assertEqual(
            result["development_cases"],
            {
                "V01": {"cell_id": "A19", "development_seed": 9901},
                "V02": {"cell_id": "A20", "development_seed": 9902},
                "V03": {"cell_id": "A21", "development_seed": 9903},
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

    def test_development_plans_cover_requested_and_effective_policy_paths(self) -> None:
        expected = {
            "V01": ("A19", 9901, "P0", "P0", "OBSERVE_ONLY"),
            "V02": ("A20", 9902, "P1", "P1", "ISOLATE_MODELED_SOURCE"),
            "V03": ("A21", 9903, "P7", "P1", "ISOLATE_MODELED_SOURCE"),
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
            self.assertFalse(plan["runtime_policy_decision"]["oracle_ground_truth_read"])

    def test_expected_route_validation_observation_passes(self) -> None:
        for case_id in ("V01", "V02", "V03"):
            plan = self._plan(case_id)
            summary = finalize_development_observation(
                plan=plan,
                measurement=self._measurement(plan=plan),
            )
            self.assertEqual(summary["acceptance_status"], "PASS")
            self.assertTrue(summary["treatment_fidelity_valid"])
            self.assertTrue(summary["raw_metric_inputs_complete"])
            self.assertTrue(summary["outcome_matches_predeclared_expectation"])
            self.assertFalse(summary["campaign_seed_consumed"])
            self.assertFalse(summary["campaign_data_generated"])

    def test_unexpected_outcome_does_not_invalidate_development_route_contract(self) -> None:
        plan = self._plan("V01")
        summary = finalize_development_observation(
            plan=plan,
            measurement=self._measurement(plan=plan, replay_delta=0),
        )
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertFalse(summary["outcome_matches_predeclared_expectation"])
        self.assertTrue(
            summary["unexpected_scientific_outcome_would_be_retained_in_campaign"]
        )

    def test_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("V02")
        measurement = self._measurement(plan=plan)
        measurement["replay_gateway_forwarded"] = True
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            finalize_development_observation(
                plan=plan,
                measurement=measurement,
            )

    def test_campaign_plan_is_constructed_from_r054_not_accepted_externally(self) -> None:
        plan = construct_authorized_campaign_plan(
            campaign_seed=10001,
            cell_id="A19",
            run_id="wp9-r057-a19-s10001-plan-only",
            repo_commit="b" * 40,
        )
        self.assertEqual(plan["decision_id"], "R-054")
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["cell_id"], "A19")
        self.assertFalse(plan["execution_boundary"]["campaign_seed_consumed"])
        self.assertFalse(plan["execution_boundary"]["final_campaign_execution_authorized"])

    def test_campaign_execution_remains_blocked(self) -> None:
        with self.assertRaisesRegex(PermissionError, "campaign execution remains blocked"):
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
        self.assertIn("results/wp9/development/r057/e2", text)
        self.assertNotIn("results/wp9/campaign", text)
        self.assertIn('V01) CELL_ID="A19"; SEED="9901"', text)
        self.assertIn('V02) CELL_ID="A20"; SEED="9902"', text)
        self.assertIn('V03) CELL_ID="A21"; SEED="9903"', text)
        self.assertIn("DURATION_SECONDS=90", text)
        self.assertIn("automatic_retry_allowed=false", text)
        self.assertIn("automatic_next_case_allowed=false", text)
        self.assertNotIn("mapfile", text)
        self.assertNotIn("readarray", text)
        self.assertNotIn("declare -A", text)

    def test_runner_requires_full_thirty_second_post_event_horizon(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("origin+30_000_000_000", text)
        self.assertIn("POST_RESPONSE_AUTHORIZED_NOOP", text)
        self.assertIn("gateway_decision_count", text)
        self.assertIn("runtime_health_passed", text)


if __name__ == "__main__":
    unittest.main()
