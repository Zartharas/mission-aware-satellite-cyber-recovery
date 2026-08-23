from __future__ import annotations

import unittest

from jsonschema import Draft202012Validator, FormatChecker

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp9_campaign_e3_adapter import (
    APPROVED_SHA256,
    TAMPERED_SHA256,
    build_static_fixture_bundle,
    execution_preflight,
    validate_static_adapter,
)
from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_static_contracts import build_wp9_run_schema


class WP9CampaignE3AdapterTests(unittest.TestCase):
    def _plan(self, cell_id: str) -> dict:
        return build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"wp9-r062-{cell_id.lower()}-s10001-static",
            repo_commit="b" * 40,
        )

    def _criteria(self, *, all_satisfied: bool = True) -> dict:
        result = {}
        for criterion in RECOVERY_CRITERIA:
            satisfied = all_satisfied
            result[criterion] = {
                "available_current": True,
                "criterion_satisfied": satisfied,
                "evidence_ref": f"static/e3/{criterion}.json",
            }
        return result

    def _measurement(
        self,
        *,
        plan: dict,
        trusted: bool | None = None,
        noop_delta: int = 1,
    ) -> dict:
        effective = plan["expected_effective_policy_id_for_acceptance_only"]
        base = {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-23T03:30:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "event_success_observed_ns": 2_150_000_000,
            "policy_selection_ns": 2_100_000_000,
            "policy_enforcement_ns": 2_200_000_000,
            "response_boundary_ns": 2_200_000_000,
            "observation_complete_ns": 32_100_000_000,
            "event_activation_observed": True,
            "event_slot_sha256": TAMPERED_SHA256,
            "runtime_health_passed": True,
            "policy_selection_not_gated_on_event_success": True,
            "authorized_noop_attempted": 1,
            "authorized_noop_marker_delta": noop_delta,
        }
        if effective == "P2":
            base.update(
                {
                    "post_response_slot_sha256": TAMPERED_SHA256,
                    "update_containment_observed": False,
                    "matched_attacker_probe_count": 2,
                    "gateway_decision_count": 3,
                    "attacker_gateway_forwarded_count": 0,
                    "authorized_noop_gateway_forwarded": True,
                    "gateway_action": "RESTRICT_HIGH_RISK_COMMANDS",
                    "observed_post_enforcement_attacker_reset_marker_delta": 0,
                    "ground_authorization_waited": False,
                }
            )
            return base

        if trusted is None:
            trusted = True
        criteria = self._criteria(all_satisfied=True)
        if not trusted:
            criteria["recovery_manifest_complete"]["criterion_satisfied"] = False
        if noop_delta == 0:
            criteria["authorized_command_path_restored"]["criterion_satisfied"] = False
        base.update(
            {
                "post_response_slot_sha256": APPROVED_SHA256,
                "rollback_request_validated": True,
                "approved_replacement_source_verified": True,
                "temporary_recovery_state_absent": True,
                "rollback_complete_ns": 5_000_000_000,
                "trusted_recovery_confirmed": trusted,
                "recovery_criteria": criteria,
                "ground_authorization_waited": effective == "P6",
            }
        )
        if trusted:
            base["trusted_recovery_observed_ns"] = 6_000_000_000
            base["observation_complete_ns"] = 6_100_000_000
        if effective == "P6":
            contact = plan["factor_context"]["contact_condition_id"]
            if contact == "C0":
                auth_ns = 2_300_000_000
                base["rollback_complete_ns"] = 5_000_000_000
                if trusted:
                    base["trusted_recovery_observed_ns"] = 6_000_000_000
                    base["observation_complete_ns"] = 6_100_000_000
                available = True
                missed = 0
            else:
                auth_ns = 12_200_000_000
                base["rollback_complete_ns"] = 15_000_000_000
                if trusted:
                    base["trusted_recovery_observed_ns"] = 16_000_000_000
                    base["observation_complete_ns"] = 16_100_000_000
                available = False
                missed = 1
            base.update(
                {
                    "ground_authorization_source": "synthetic_ground_authorization_schedule",
                    "ground_authorization_current": True,
                    "authorization_observed_ns": auth_ns,
                    "handoff_ns": auth_ns + 100_000_000,
                    "authorization_available_at_response_boundary": available,
                    "missed_contact_windows_observed": missed,
                    "post_authorization_delegate": "P5",
                    "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
                }
            )
        return base

    def _bundle(self, cell_id: str, *, trusted: bool | None = None, noop_delta: int = 1) -> dict:
        plan = self._plan(cell_id)
        return build_static_fixture_bundle(
            plan=plan,
            measurement=self._measurement(plan=plan, trusted=trusted, noop_delta=noop_delta),
            host_architecture="static-test",
            evidence_prefix=f"static-fixture/wp9/e3/{cell_id.lower()}",
        )

    def test_static_adapter_covers_a10_a18_and_never_authorizes(self) -> None:
        result = validate_static_adapter()
        self.assertEqual(result["decision_id"], "R-062")
        self.assertEqual(result["supported_cells"], [f"A{i:02d}" for i in range(10, 19)])
        self.assertEqual(result["post_event_analysis_horizon_s"], 30)
        self.assertEqual(result["modeled_c1_contact_window_s"], 10)
        self.assertEqual(len(result["runtime_variants"]), 5)
        self.assertFalse(result["p2_command_mitigation_counts_as_update_containment"])
        self.assertFalse(result["t1_policy_omission_implies_recovery_failure"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_all_nine_cells_bind_frozen_policy_route_and_no_oracle(self) -> None:
        expected = {
            "A10": ("P2", "P2", "RESTRICT_HIGH_RISK_COMMANDS", "e3_command_gateway"),
            "A11": ("P7", "P5", "REQUEST_VERIFIED_ROLLBACK", "e3_trusted_recovery"),
            "A12": ("P2", "P2", "RESTRICT_HIGH_RISK_COMMANDS", "e3_command_gateway"),
            "A13": ("P7", "P2", "RESTRICT_HIGH_RISK_COMMANDS", "e3_command_gateway"),
            "A14": ("P5", "P5", "REQUEST_VERIFIED_ROLLBACK", "e3_trusted_recovery"),
            "A15": ("P5", "P5", "REQUEST_VERIFIED_ROLLBACK", "e3_trusted_recovery_reduced_evidence"),
            "A16": ("P6", "P6", "WAIT_FOR_GROUND_AUTHORIZATION", "e3_ground_authorized_recovery"),
            "A17": ("P6", "P6", "WAIT_FOR_GROUND_AUTHORIZATION", "e3_ground_authorized_recovery"),
            "A18": ("P7", "P5", "REQUEST_VERIFIED_ROLLBACK", "e3_trusted_recovery_contact_delay"),
        }
        for cell_id, values in expected.items():
            provenance = self._bundle(cell_id)["binding_provenance"]
            metadata = provenance["execution_metadata"]
            self.assertEqual(
                (metadata["requested_policy_id"], metadata["effective_policy_id"], metadata["selected_action"], provenance["runtime_variant"]),
                values,
            )
            self.assertFalse(metadata["oracle_ground_truth_read"])

    def test_representative_p2_p5_p6_records_are_wp9_schema_valid(self) -> None:
        validator = Draft202012Validator(build_wp9_run_schema(), format_checker=FormatChecker())
        for cell_id in ("A10", "A11", "A16", "A17"):
            self.assertEqual(list(validator.iter_errors(self._bundle(cell_id)["run_record"])), [])

    def test_p2_command_mitigation_never_becomes_update_containment(self) -> None:
        for cell_id in ("A10", "A12", "A13"):
            bundle = self._bundle(cell_id)
            p = bundle["binding_provenance"]
            record = bundle["run_record"]
            self.assertTrue(p["observed_discriminators"]["command_path_mitigation_observed"])
            self.assertFalse(p["observed_discriminators"]["update_containment_observed"])
            self.assertFalse(p["observed_discriminators"]["p2_command_mitigation_counts_as_update_containment"])
            self.assertIsNone(record["timing"]["containment_s"])
            self.assertEqual(record["terminal_state"], "RECOVERY_FAILED")
            self.assertTrue(p["timing_binding"]["right_censored_at_30s"])

    def test_a13_is_adaptive_p7_to_p2_without_oracle(self) -> None:
        metadata = self._bundle("A13")["binding_provenance"]["execution_metadata"]
        self.assertEqual(metadata["requested_policy_id"], "P7")
        self.assertEqual(metadata["effective_policy_id"], "P2")
        self.assertEqual(metadata["selected_action"], "RESTRICT_HIGH_RISK_COMMANDS")
        self.assertFalse(metadata["oracle_ground_truth_read"])

    def test_full_evidence_p5_paths_can_end_in_early_trusted_recovery(self) -> None:
        for cell_id in ("A11", "A14"):
            bundle = self._bundle(cell_id)
            p = bundle["binding_provenance"]
            record = bundle["run_record"]
            self.assertTrue(p["observed_discriminators"]["update_containment_observed"])
            self.assertTrue(p["observed_discriminators"]["trusted_recovery_observed"])
            self.assertTrue(p["timing_binding"]["early_absorbing_trusted_recovery"])
            self.assertFalse(p["timing_binding"]["right_censored_at_30s"])
            self.assertEqual(record["terminal_state"], "TRUSTED_RECOVERY_CONFIRMED")

    def test_a15_t1_policy_omission_does_not_force_recovery_failure(self) -> None:
        bundle = self._bundle("A15", trusted=True)
        p = bundle["binding_provenance"]
        self.assertTrue(p["evidence_semantics"]["policy_time_approved_version_omitted"])
        self.assertFalse(p["evidence_semantics"]["policy_time_omission_implies_classification_time_loss"])
        self.assertTrue(p["observed_discriminators"]["trusted_recovery_observed"])
        self.assertEqual(bundle["run_record"]["terminal_state"], "TRUSTED_RECOVERY_CONFIRMED")

    def test_a15_nonconfirmation_is_valid_right_censored_not_a_t1_causal_claim(self) -> None:
        bundle = self._bundle("A15", trusted=False)
        p = bundle["binding_provenance"]
        self.assertFalse(p["observed_discriminators"]["trusted_recovery_observed"])
        self.assertTrue(p["timing_binding"]["right_censored_at_30s"])
        self.assertFalse(p["evidence_semantics"]["policy_time_omission_implies_classification_time_loss"])
        self.assertEqual(bundle["run_record"]["terminal_state"], "OPERATIONAL_BUT_UNVERIFIED")

    def test_p6_c0_and_c1_bind_campaign_contact_semantics(self) -> None:
        a16 = self._bundle("A16")["binding_provenance"]
        a17 = self._bundle("A17")["binding_provenance"]
        self.assertTrue(a16["observed_discriminators"]["ground_authorization_waited"])
        self.assertTrue(a17["observed_discriminators"]["ground_authorization_waited"])
        self.assertIsNone(a16["timing_binding"]["modeled_c1_contact_window_s"])
        self.assertEqual(a17["timing_binding"]["modeled_c1_contact_window_s"], 10)
        self.assertEqual(a16["execution_metadata"]["effective_policy_id"], "P6")
        self.assertEqual(a17["execution_metadata"]["effective_policy_id"], "P6")

    def test_p6_c1_authorization_before_ten_seconds_is_rejected(self) -> None:
        plan = self._plan("A17")
        measurement = self._measurement(plan=plan)
        measurement["authorization_observed_ns"] = 12_199_999_999
        measurement["handoff_ns"] = 12_300_000_000
        with self.assertRaisesRegex(ValueError, "before frozen 10-second window"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

    def test_a18_c1_is_autonomous_p7_to_p5_not_ground_waiting(self) -> None:
        bundle = self._bundle("A18")
        p = bundle["binding_provenance"]
        self.assertEqual(p["execution_metadata"]["requested_policy_id"], "P7")
        self.assertEqual(p["execution_metadata"]["effective_policy_id"], "P5")
        self.assertFalse(p["observed_discriminators"]["ground_authorization_waited"])
        self.assertEqual(p["timing_binding"]["modeled_c1_contact_window_s"], 10)

        plan = self._plan("A18")
        measurement = self._measurement(plan=plan)
        measurement["ground_authorization_waited"] = True
        with self.assertRaisesRegex(ValueError, "autonomous P5"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

    def test_event_activation_and_response_treatment_fidelity_fail_closed(self) -> None:
        plan = self._plan("A11")
        measurement = self._measurement(plan=plan)
        measurement["event_slot_sha256"] = APPROVED_SHA256
        with self.assertRaisesRegex(ValueError, "activation slot identity"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

        measurement = self._measurement(plan=plan)
        measurement["post_response_slot_sha256"] = TAMPERED_SHA256
        with self.assertRaisesRegex(ValueError, "approved replacement"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

    def test_policy_selection_cannot_be_ground_truth_gated(self) -> None:
        plan = self._plan("A13")
        measurement = self._measurement(plan=plan)
        measurement["policy_selection_not_gated_on_event_success"] = False
        with self.assertRaisesRegex(ValueError, "ground-truth gated"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

    def test_unrecovered_e3_requires_full_thirty_second_horizon(self) -> None:
        plan = self._plan("A15")
        measurement = self._measurement(plan=plan, trusted=False)
        measurement["observation_complete_ns"] = 31_999_999_999
        with self.assertRaisesRegex(ValueError, "30-second horizon"):
            build_static_fixture_bundle(plan=plan, measurement=measurement, host_architecture="static-test")

    def test_unexpected_legitimate_service_loss_is_retained_not_rejected(self) -> None:
        bundle = self._bundle("A11", trusted=False, noop_delta=0)
        p = bundle["binding_provenance"]
        self.assertFalse(p["predeclared_expectation"]["outcome_matches_predeclared_expectation"])
        self.assertFalse(p["predeclared_expectation"]["expectation_used_as_metric_input"])
        self.assertFalse(p["predeclared_expectation"]["expectation_used_to_reject_scientific_outcome"])
        self.assertTrue(p["scientific_validity"]["unexpected_scientific_outcome_retained"])
        self.assertTrue(p["scientific_validity"]["scientific_observation_retained"])
        self.assertEqual(bundle["run_record"]["terminal_state"], "CONTAINED_NOT_RECOVERED")

    def test_static_fixture_never_executes_runtime_or_consumes_campaign_seed(self) -> None:
        p = self._bundle("A17")["binding_provenance"]
        self.assertTrue(p["static_fixture_only"])
        self.assertFalse(p["runtime_execution_performed"])
        self.assertFalse(p["campaign_runtime_execution_performed"])
        self.assertFalse(p["campaign_seed_consumed"])
        self.assertFalse(p["campaign_data_generated"])
        self.assertFalse(p["final_campaign_execution_authorized"])
        self.assertFalse(p["automatic_retry_allowed"])
        self.assertFalse(p["automatic_next_case_allowed"])

    def test_execution_entry_point_remains_blocked(self) -> None:
        with self.assertRaisesRegex(PermissionError, "campaign runtime remains blocked"):
            execution_preflight()


if __name__ == "__main__":
    unittest.main()
