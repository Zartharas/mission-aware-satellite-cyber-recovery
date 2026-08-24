from __future__ import annotations

import unittest

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp9_campaign_e3_adapter import APPROVED_SHA256, TAMPERED_SHA256
from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import _runtime_bundle

REPO_SHA = "c" * 40


def _plan(cell_id: str, run_id: str) -> dict:
    return build_trial_plan(
        campaign_seed=10001,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=REPO_SHA,
    )


def _e1_measurement(plan: dict) -> dict:
    effective = plan["expected_effective_policy_id_for_acceptance_only"]
    action = {
        "P1": "ISOLATE_MODELED_SOURCE",
        "P2": "RESTRICT_HIGH_RISK_COMMANDS",
        "P4": "ENTER_SAFE_MODE",
    }[effective]
    authorized_forwarded = action != "ENTER_SAFE_MODE"
    return {
        "schema": 1,
        "run_id": plan["run_id"],
        "run_start_utc": "2026-08-24T03:00:00Z",
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
        "post_enforcement_attacker_reset_marker_delta": 0,
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": 1 if authorized_forwarded else 0,
        "gateway_decision_count": 3,
        "attacker_gateway_action": action,
        "authorized_noop_gateway_action": action,
        "attacker_gateway_forwarded_count": 0,
        "authorized_noop_gateway_forwarded": authorized_forwarded,
        "runtime_health_passed": True,
        "policy_selection_not_gated_on_event_success": True,
    }


def _e2_measurement(plan: dict, *, replay_delta: int = 0) -> dict:
    return {
        "schema": 1,
        "run_id": plan["run_id"],
        "run_start_utc": "2026-08-24T03:00:00Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": 2_000_000_000,
        "policy_enforcement_ns": 2_100_000_000,
        "replay_gateway_decision_ns": 2_200_000_000,
        "replay_effect_observed_ns": 2_300_000_000 if replay_delta else None,
        "authorized_noop_probe_observed_ns": 2_400_000_000,
        "observation_complete_ns": 32_100_000_000,
        "setup_reset_marker_delta": 1,
        "intervening_authorized_noop_marker_delta": 1,
        "post_replay_reset_marker_delta": replay_delta,
        "post_response_authorized_noop_attempted": 1,
        "post_response_authorized_noop_marker_delta": 1,
        "gateway_decision_count": 2,
        "replayed_packet_byte_identical": True,
        "runtime_health_passed": True,
        "replay_gateway_action": "ISOLATE_MODELED_SOURCE",
        "replay_gateway_forwarded": False,
        "authorized_noop_gateway_action": "ISOLATE_MODELED_SOURCE",
        "authorized_noop_gateway_forwarded": True,
    }


def _criteria() -> dict:
    return {
        criterion: {
            "available_current": True,
            "criterion_satisfied": True,
            "evidence_ref": f"static/r066/{criterion}.json",
        }
        for criterion in RECOVERY_CRITERIA
    }


def _e3_measurement(plan: dict) -> dict:
    return {
        "schema": 1,
        "run_id": plan["run_id"],
        "run_start_utc": "2026-08-24T03:00:00Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": 2_000_000_000,
        "event_success_observed_ns": 2_150_000_000,
        "policy_selection_ns": 2_100_000_000,
        "policy_enforcement_ns": 2_200_000_000,
        "response_boundary_ns": 2_200_000_000,
        "observation_complete_ns": 16_100_000_000,
        "event_activation_observed": True,
        "event_slot_sha256": TAMPERED_SHA256,
        "post_response_slot_sha256": APPROVED_SHA256,
        "runtime_health_passed": True,
        "policy_selection_not_gated_on_event_success": True,
        "authorized_noop_attempted": 1,
        "authorized_noop_marker_delta": 1,
        "rollback_request_validated": True,
        "approved_replacement_source_verified": True,
        "temporary_recovery_state_absent": True,
        "rollback_complete_ns": 15_000_000_000,
        "trusted_recovery_confirmed": True,
        "trusted_recovery_observed_ns": 16_000_000_000,
        "recovery_criteria": _criteria(),
        "ground_authorization_waited": True,
        "ground_authorization_source": "synthetic_ground_authorization_schedule",
        "ground_authorization_current": True,
        "authorization_observed_ns": 12_200_000_000,
        "handoff_ns": 12_300_000_000,
        "authorization_available_at_response_boundary": False,
        "missed_contact_windows_observed": 1,
        "post_authorization_delegate": "P5",
        "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
    }


def _e4_measurement(plan: dict) -> dict:
    return {
        "schema": 1,
        "run_id": plan["run_id"],
        "run_start_utc": "2026-08-24T03:00:00Z",
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
        "post_response_policy_visible_high_value_delta": 0,
        "post_response_authorized_noop_attempted": 1,
        "post_response_authorized_noop_marker_delta": 0,
        "gateway_decision_count": 1,
        "immutable_truth_separate": True,
        "runtime_health_passed": True,
        "authorized_noop_gateway_action": "ENTER_SAFE_MODE",
        "authorized_noop_gateway_forwarded": False,
    }


class WP9R066RuntimeBundleIntegrationTests(unittest.TestCase):
    def test_representative_raw_measurements_bind_through_all_four_campaign_families(self) -> None:
        cases = (
            ("A06", "E1", _e1_measurement, "R-060"),
            ("A21", "E2", _e2_measurement, "R-056"),
            ("A17", "E3", _e3_measurement, "R-062"),
            ("A24", "E4", _e4_measurement, "R-058"),
        )
        for cell_id, event_id, factory, source_decision in cases:
            with self.subTest(cell_id=cell_id):
                plan = _plan(cell_id, f"r066-bundle-{cell_id.lower()}")
                result = _runtime_bundle(
                    plan=plan,
                    measurement=factory(plan),
                    evidence_prefix=(
                        f"results/wp9/campaign/seed-10001/{cell_id}/fixture"
                    ),
                )
                self.assertEqual(result["decision_id"], "R-066")
                self.assertEqual(result["attempt_status"], "VALID")
                self.assertEqual(result["campaign_seed"], 10001)
                self.assertEqual(result["cell_id"], cell_id)
                self.assertEqual(result["event_id"], event_id)
                self.assertTrue(result["treatment_fidelity_valid"])
                self.assertTrue(result["raw_metric_inputs_complete"])
                self.assertTrue(result["runtime_execution_performed"])
                self.assertTrue(result["campaign_seed_consumed"])
                self.assertTrue(result["campaign_data_generated"])
                self.assertFalse(result["automatic_retry_performed"])
                self.assertFalse(result["automatic_next_case_performed"])
                self.assertFalse(result["campaign_wide_execution_authorized"])
                provenance = result["binding_provenance"]
                self.assertEqual(
                    provenance["source_campaign_observation_adapter_decision_id"],
                    source_decision,
                )
                self.assertFalse(
                    provenance["execution_metadata"]["oracle_ground_truth_read"]
                )
                self.assertEqual(result["run_record"]["seed"], 10001)

    def test_unexpected_treatment_valid_scientific_effect_remains_valid_data(self) -> None:
        plan = _plan("A21", "r066-bundle-unexpected")
        measurement = _e2_measurement(plan, replay_delta=1)
        result = _runtime_bundle(
            plan=plan,
            measurement=measurement,
            evidence_prefix="results/wp9/campaign/seed-10001/A21/fixture",
        )
        self.assertEqual(result["attempt_status"], "VALID")
        self.assertFalse(result["outcome_matches_predeclared_expectation"])
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertTrue(result["treatment_fidelity_valid"])
        self.assertTrue(
            result["binding_provenance"]["scientific_validity"][
                "scientific_observation_retained"
            ]
        )

    def test_treatment_fidelity_failure_is_rejected_not_reclassified_as_science(self) -> None:
        plan = _plan("A21", "r066-bundle-treatment-invalid")
        measurement = _e2_measurement(plan, replay_delta=0)
        measurement["replay_gateway_forwarded"] = True
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            _runtime_bundle(
                plan=plan,
                measurement=measurement,
                evidence_prefix="results/wp9/campaign/seed-10001/A21/fixture",
            )


if __name__ == "__main__":
    unittest.main()
