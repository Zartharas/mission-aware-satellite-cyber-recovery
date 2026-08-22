from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from src.mission_recovery.wp9_campaign_e1_adapter import (
    build_static_fixture_bundle,
    execution_preflight,
    validate_static_adapter,
)
from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "configs" / "experiment_run.schema.json"


class WP9CampaignE1AdapterTests(unittest.TestCase):
    def _plan(self, cell_id: str) -> dict:
        return build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"wp9-r060-{cell_id.lower()}-s10001-static",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        plan: dict,
        attacker_delta: int | None = None,
        noop_delta: int | None = None,
    ) -> dict:
        effective = plan["expected_effective_policy_id_for_acceptance_only"]
        action = {
            "P1": "ISOLATE_MODELED_SOURCE",
            "P2": "RESTRICT_HIGH_RISK_COMMANDS",
            "P4": "ENTER_SAFE_MODE",
        }[effective]
        attacker_forwarded_count = 0
        authorized_forwarded = action != "ENTER_SAFE_MODE"
        if attacker_delta is None:
            attacker_delta = attacker_forwarded_count
        if noop_delta is None:
            noop_delta = 1 if authorized_forwarded else 0
        return {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-22T23:30:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "policy_selection_ns": 2_100_000_000,
            "policy_enforcement_ns": 2_200_000_000,
            "event_success_observed_ns": 2_500_000_000,
            "second_attacker_probe_observed_ns": 3_000_000_000,
            "authorized_noop_probe_observed_ns": 4_000_000_000,
            "observation_complete_ns": 32_100_000_000,
            "event_activation_reset_marker_delta": 1,
            "post_enforcement_attacker_probe_count": 2,
            "post_enforcement_attacker_reset_marker_delta": attacker_delta,
            "legitimate_commands_attempted": 1,
            "authorized_noop_marker_delta": noop_delta,
            "gateway_decision_count": 3,
            "attacker_gateway_action": action,
            "authorized_noop_gateway_action": action,
            "attacker_gateway_forwarded_count": attacker_forwarded_count,
            "authorized_noop_gateway_forwarded": authorized_forwarded,
            "runtime_health_passed": True,
            "policy_selection_not_gated_on_event_success": True,
        }

    def _bundle(self, cell_id: str, **overrides: int) -> dict:
        plan = self._plan(cell_id)
        measurement = self._measurement(plan=plan, **overrides)
        return build_static_fixture_bundle(
            plan=plan,
            measurement=measurement,
            host_architecture="static-test",
            evidence_prefix=f"static-fixture/wp9/e1/{cell_id.lower()}",
        )

    def test_static_adapter_is_a01_a09_only_and_never_authorizes(self) -> None:
        result = validate_static_adapter()
        self.assertEqual(result["decision_id"], "R-060")
        self.assertEqual(result["supported_cells"], [f"A{i:02d}" for i in range(1, 10)])
        self.assertEqual(result["post_event_analysis_horizon_s"], 30)
        self.assertEqual(result["matched_attacker_probe_count"], 2)
        self.assertTrue(result["post_response_authorized_noop_required"])
        self.assertFalse(result["expected_effects_used_as_metric_inputs"])
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["ground_truth_policy_oracle_allowed"])
        self.assertFalse(result["native_spacecraft_safe_mode_claim"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_all_nine_cells_bind_requested_and_effective_policy_without_oracle(self) -> None:
        expected = {
            "A01": ("P1", "P1", "ISOLATE_MODELED_SOURCE"),
            "A02": ("P7", "P1", "ISOLATE_MODELED_SOURCE"),
            "A03": ("P1", "P1", "ISOLATE_MODELED_SOURCE"),
            "A04": ("P7", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "A05": ("P1", "P1", "ISOLATE_MODELED_SOURCE"),
            "A06": ("P7", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "A07": ("P2", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "A08": ("P2", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
            "A09": ("P7", "P4", "ENTER_SAFE_MODE"),
        }
        for cell_id, (requested, effective, action) in expected.items():
            provenance = self._bundle(cell_id)["binding_provenance"]
            metadata = provenance["execution_metadata"]
            self.assertEqual(metadata["requested_policy_id"], requested)
            self.assertEqual(metadata["effective_policy_id"], effective)
            self.assertEqual(metadata["selected_action"], action)
            self.assertFalse(metadata["oracle_ground_truth_read"])

    def test_representative_p1_p2_p4_fixtures_are_schema_valid(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for cell_id in ("A01", "A04", "A09"):
            record = self._bundle(cell_id)["run_record"]
            self.assertEqual(list(validator.iter_errors(record)), [])

    def test_p1_and_p2_expected_routes_contain_attacker_and_preserve_service(self) -> None:
        for cell_id in ("A01", "A04", "A07", "A08"):
            bundle = self._bundle(cell_id)
            record = bundle["run_record"]
            provenance = bundle["binding_provenance"]
            self.assertTrue(provenance["observed_discriminators"]["containment_observed"])
            self.assertTrue(provenance["observed_discriminators"]["authority_convergence_observed"])
            self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 0.0)
            self.assertIsNotNone(record["timing"]["containment_s"])
            self.assertEqual(record["terminal_state"], "OPERATIONAL_BUT_UNVERIFIED")
            self.assertTrue(
                provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"]
            )

    def test_a09_p7_to_p4_blocks_attacker_and_authorized_noop_without_native_safe_mode_claim(self) -> None:
        bundle = self._bundle("A09")
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertEqual(provenance["execution_metadata"]["requested_policy_id"], "P7")
        self.assertEqual(provenance["execution_metadata"]["effective_policy_id"], "P4")
        self.assertEqual(provenance["execution_metadata"]["selected_action"], "ENTER_SAFE_MODE")
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 1.0)
        self.assertEqual(record["terminal_state"], "CONTAINED_NOT_RECOVERED")
        self.assertFalse(provenance["claim_boundaries"]["native_spacecraft_safe_mode_claim"])

    def test_unexpected_attacker_effect_is_retained_not_rejected(self) -> None:
        bundle = self._bundle("A01", attacker_delta=1)
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertFalse(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"])
        self.assertFalse(provenance["predeclared_expectation"]["expectation_used_as_metric_input"])
        self.assertFalse(
            provenance["predeclared_expectation"]["expectation_used_to_reject_scientific_outcome"]
        )
        self.assertTrue(provenance["scientific_validity"]["unexpected_scientific_outcome_retained"])
        self.assertTrue(provenance["scientific_validity"]["scientific_observation_retained"])
        self.assertEqual(record["terminal_state"], "RECOVERY_FAILED")

    def test_unexpected_legitimate_service_loss_is_retained_not_rejected(self) -> None:
        bundle = self._bundle("A04", noop_delta=0)
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertFalse(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"])
        self.assertTrue(provenance["scientific_validity"]["unexpected_scientific_outcome_retained"])
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 1.0)
        self.assertEqual(record["terminal_state"], "CONTAINED_NOT_RECOVERED")

    def test_event_activation_failure_is_invalid_not_scientific_outcome(self) -> None:
        plan = self._plan("A01")
        measurement = self._measurement(plan=plan)
        measurement["event_activation_reset_marker_delta"] = 0
        with self.assertRaisesRegex(ValueError, "event activation effect"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_gateway_treatment_fidelity_failure_is_rejected(self) -> None:
        plan = self._plan("A01")
        measurement = self._measurement(plan=plan)
        measurement["attacker_gateway_forwarded_count"] = 2
        with self.assertRaisesRegex(ValueError, "attacker forwarding differs"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_two_matched_attacker_probes_and_one_authorized_noop_are_required(self) -> None:
        plan = self._plan("A01")
        measurement = self._measurement(plan=plan)
        measurement["post_enforcement_attacker_probe_count"] = 1
        with self.assertRaisesRegex(ValueError, "two matched attacker probes"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

        measurement = self._measurement(plan=plan)
        measurement["legitimate_commands_attempted"] = 0
        with self.assertRaisesRegex(ValueError, "one post-response authorized NOOP"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_policy_selection_cannot_be_ground_truth_gated(self) -> None:
        plan = self._plan("A04")
        measurement = self._measurement(plan=plan)
        measurement["policy_selection_not_gated_on_event_success"] = False
        with self.assertRaisesRegex(ValueError, "gated on ground-truth event success"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_full_thirty_second_analysis_window_is_required(self) -> None:
        plan = self._plan("A01")
        measurement = self._measurement(plan=plan)
        measurement["observation_complete_ns"] = 31_999_999_999
        with self.assertRaisesRegex(ValueError, "30-second analysis horizon"):
            build_static_fixture_bundle(
                plan=plan,
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_static_fixture_never_executes_runtime_or_consumes_campaign_seed(self) -> None:
        provenance = self._bundle("A09")["binding_provenance"]
        self.assertTrue(provenance["static_fixture_only"])
        self.assertFalse(provenance["runtime_execution_performed"])
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
