from __future__ import annotations

import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, FormatChecker

from src.mission_recovery.wp9_campaign_e4_adapter import (
    build_static_fixture_bundle,
    execution_preflight,
    validate_static_adapter,
)
from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "configs" / "experiment_run.schema.json"


class WP9CampaignE4AdapterTests(unittest.TestCase):
    def _plan(self, cell_id: str) -> dict:
        return build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"wp9-r058-{cell_id.lower()}-s10001-static",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        plan: dict,
        post_visible_delta: int = 0,
        noop_delta: int | None = None,
    ) -> dict:
        requested = plan["factor_context"]["policy_id"]
        safe_mode = requested in {"P4", "P7"}
        if noop_delta is None:
            noop_delta = 0 if safe_mode else 1
        action = "ENTER_SAFE_MODE" if safe_mode else "OBSERVE_ONLY"
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
            "post_response_policy_visible_high_value_delta": post_visible_delta,
            "post_response_authorized_noop_attempted": 1,
            "post_response_authorized_noop_marker_delta": noop_delta,
            "gateway_decision_count": 1,
            "immutable_truth_separate": True,
            "runtime_health_passed": True,
            "authorized_noop_gateway_action": action,
            "authorized_noop_gateway_forwarded": not safe_mode,
        }

    def _bundle(self, cell_id: str, **measurement_overrides: int) -> dict:
        plan = self._plan(cell_id)
        measurement = self._measurement(plan=plan, **measurement_overrides)
        return build_static_fixture_bundle(
            plan=plan,
            measurement=measurement,
            host_architecture="static-test",
            evidence_prefix=f"static-fixture/wp9/e4/{cell_id.lower()}",
        )

    def test_static_adapter_is_a22_a24_only_and_never_authorizes(self) -> None:
        result = validate_static_adapter()
        self.assertEqual(result["decision_id"], "R-058")
        self.assertEqual(result["supported_cells"], ["A22", "A23", "A24"])
        self.assertEqual(result["post_event_analysis_horizon_s"], 30)
        self.assertTrue(result["event_activation_requires_truth_visible_separation"])
        self.assertTrue(result["post_response_authorized_noop_required"])
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["trusted_recovery_fabricated_by_observability_route"])
        self.assertFalse(result["native_spacecraft_safe_mode_claim"])
        self.assertFalse(result["campaign_runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_a22_expected_observation_is_schema_valid_and_preserves_service(self) -> None:
        bundle = self._bundle("A22")
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
        self.assertEqual(errors, [])
        self.assertEqual(record["policy_id"], "P0")
        self.assertTrue(record["outcomes"]["unauthorized_effect_completed"])
        self.assertEqual(record["outcomes"]["mission_objective_completion_ratio"], 0.5)
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 0.0)
        self.assertIsNone(record["timing"]["containment_s"])
        self.assertIsNone(record["timing"]["verified_recovery_s"])
        self.assertEqual(record["terminal_state"], "RECOVERY_FAILED")
        self.assertTrue(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"])

    def test_a23_fixed_p4_blocks_authorized_noop_without_native_safe_mode_claim(self) -> None:
        bundle = self._bundle("A23")
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertEqual(provenance["execution_metadata"]["requested_policy_id"], "P4")
        self.assertEqual(provenance["execution_metadata"]["effective_policy_id"], "P4")
        self.assertEqual(provenance["execution_metadata"]["selected_action"], "ENTER_SAFE_MODE")
        self.assertFalse(provenance["observed_discriminators"]["authorized_noop_gateway_forwarded"])
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 1.0)
        self.assertFalse(provenance["claim_boundaries"]["native_spacecraft_safe_mode_claim"])
        self.assertFalse(provenance["claim_boundaries"]["p4_telemetry_restoration_attribution_claim"])

    def test_a24_retains_requested_p7_and_actual_p4_without_oracle(self) -> None:
        bundle = self._bundle("A24")
        provenance = bundle["binding_provenance"]
        metadata = provenance["execution_metadata"]
        self.assertEqual(metadata["requested_policy_id"], "P7")
        self.assertEqual(metadata["effective_policy_id"], "P4")
        self.assertEqual(metadata["selected_action"], "ENTER_SAFE_MODE")
        self.assertFalse(metadata["oracle_ground_truth_read"])
        self.assertFalse(provenance["claim_boundaries"]["ground_truth_used_as_policy_oracle"])

    def test_unexpected_a22_legitimate_service_loss_is_retained_not_rejected(self) -> None:
        bundle = self._bundle("A22", noop_delta=0)
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 1.0)
        self.assertFalse(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"])
        self.assertFalse(provenance["predeclared_expectation"]["expectation_used_as_metric_input"])
        self.assertFalse(provenance["predeclared_expectation"]["expectation_used_to_reject_scientific_outcome"])
        self.assertTrue(provenance["scientific_validity"]["unexpected_scientific_outcome_retained"])
        self.assertTrue(provenance["scientific_validity"]["scientific_observation_retained"])

    def test_unexpected_telemetry_restoration_is_retained_without_trusted_recovery(self) -> None:
        bundle = self._bundle("A23", post_visible_delta=1)
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertEqual(record["outcomes"]["mission_objective_completion_ratio"], 1.0)
        self.assertIsNotNone(record["timing"]["containment_s"])
        self.assertIsNone(record["timing"]["verified_recovery_s"])
        self.assertEqual(record["terminal_state"], "CONTAINED_NOT_RECOVERED")
        self.assertTrue(provenance["observed_discriminators"]["telemetry_restored_observed"])
        self.assertTrue(provenance["scientific_validity"]["unexpected_scientific_outcome_retained"])
        self.assertFalse(provenance["claim_boundaries"]["p4_telemetry_restoration_attribution_claim"])

    def test_event_treatment_fidelity_failure_is_invalid_not_scientific_outcome(self) -> None:
        plan = self._plan("A22")
        measurement = self._measurement(plan=plan)
        measurement["event_policy_visible_high_value_delta"] = 1
        with self.assertRaisesRegex(ValueError, "treatment did not activate"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_gateway_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("A23")
        measurement = self._measurement(plan=plan)
        measurement["authorized_noop_gateway_forwarded"] = True
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_full_thirty_second_analysis_window_is_required(self) -> None:
        plan = self._plan("A22")
        measurement = self._measurement(plan=plan)
        measurement["observation_complete_ns"] = 31_999_999_999
        with self.assertRaisesRegex(ValueError, "30-second analysis horizon"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_post_response_authorized_noop_is_required_for_all_e4_cells(self) -> None:
        for cell_id in ("A22", "A23", "A24"):
            plan = self._plan(cell_id)
            measurement = self._measurement(plan=plan)
            measurement["post_response_authorized_noop_attempted"] = 0
            with self.assertRaisesRegex(ValueError, "requires one post-response authorized NOOP"):
                build_static_fixture_bundle(
                    plan=plan,
                    measurement=measurement,
                    host_architecture="static-test",
                )

    def test_static_fixture_never_consumes_campaign_seed_or_becomes_campaign_data(self) -> None:
        bundle = self._bundle("A24")
        provenance = bundle["binding_provenance"]
        self.assertTrue(provenance["static_fixture_only"])
        self.assertFalse(provenance["campaign_runtime_execution_performed"])
        self.assertFalse(provenance["campaign_seed_consumed"])
        self.assertFalse(provenance["campaign_data_generated"])
        self.assertFalse(provenance["final_campaign_execution_authorized"])
        self.assertFalse(provenance["automatic_retry_allowed"])
        self.assertFalse(provenance["automatic_next_case_allowed"])

    def test_execution_entry_point_remains_blocked(self) -> None:
        with self.assertRaisesRegex(PermissionError, "campaign runtime remains blocked"):
            execution_preflight()


if __name__ == "__main__":
    unittest.main()
