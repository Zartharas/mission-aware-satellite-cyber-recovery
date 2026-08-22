from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from src.mission_recovery.wp9_campaign_e2_adapter import (
    SCHEMA,
    build_static_fixture_bundle,
    execution_preflight,
    validate_static_adapter,
)
from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan


class WP9CampaignE2AdapterTests(unittest.TestCase):
    def _plan(self, cell_id: str) -> dict:
        return build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"wp9-r056-{cell_id.lower()}-s10001-static",
            repo_commit="a" * 40,
        )

    def _measurement(
        self,
        *,
        cell_id: str,
        replay_delta: int | None = None,
        noop_delta: int = 1,
    ) -> dict:
        actions = {
            "A19": ("OBSERVE_ONLY", True, 1),
            "A20": ("ISOLATE_MODELED_SOURCE", False, 0),
            "A21": ("ISOLATE_MODELED_SOURCE", False, 0),
        }
        action, replay_forwarded, expected_delta = actions[cell_id]
        actual_delta = expected_delta if replay_delta is None else replay_delta
        return {
            "schema": 1,
            "run_id": f"wp9-r056-{cell_id.lower()}-s10001-static",
            "run_start_utc": "2026-08-22T18:00:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "policy_enforcement_ns": 2_100_000_000,
            "replay_gateway_decision_ns": 2_200_000_000,
            "replay_effect_observed_ns": (
                2_300_000_000 if actual_delta == 1 else None
            ),
            "authorized_noop_probe_observed_ns": 2_400_000_000,
            "observation_complete_ns": 32_100_000_000,
            "setup_reset_marker_delta": 1,
            "intervening_authorized_noop_marker_delta": 1,
            "post_replay_reset_marker_delta": actual_delta,
            "post_response_authorized_noop_attempted": 1,
            "post_response_authorized_noop_marker_delta": noop_delta,
            "gateway_decision_count": 2,
            "replayed_packet_byte_identical": True,
            "runtime_health_passed": True,
            "replay_gateway_action": action,
            "replay_gateway_forwarded": replay_forwarded,
            "authorized_noop_gateway_action": action,
            "authorized_noop_gateway_forwarded": True,
        }

    def _bundle(
        self,
        cell_id: str,
        *,
        replay_delta: int | None = None,
        noop_delta: int = 1,
    ) -> dict:
        return build_static_fixture_bundle(
            plan=self._plan(cell_id),
            measurement=self._measurement(
                cell_id=cell_id,
                replay_delta=replay_delta,
                noop_delta=noop_delta,
            ),
            host_architecture="static-test",
        )

    def test_static_adapter_is_a19_a21_only_and_never_authorizes(self) -> None:
        result = validate_static_adapter()
        self.assertEqual(result["decision_id"], "R-056")
        self.assertEqual(result["supported_cells"], ["A19", "A20", "A21"])
        self.assertEqual(result["post_event_analysis_horizon_s"], 30)
        self.assertTrue(result["post_response_authorized_noop_required"])
        self.assertFalse(result["expected_replay_effect_used_as_metric_input"])
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["campaign_runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_expected_a19_observation_binds_schema_valid_run_record(self) -> None:
        bundle = self._bundle("A19")
        record = bundle["run_record"]
        schema = json.loads(Path(SCHEMA).read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            ).iter_errors(record),
            key=lambda error: list(error.absolute_path),
        )
        self.assertEqual(errors, [])
        self.assertEqual(record["event_id"], "E2")
        self.assertEqual(record["policy_id"], "P0")
        self.assertEqual(record["seed"], 10001)
        self.assertTrue(record["outcomes"]["unauthorized_effect_completed"])
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 0.0)
        self.assertEqual(record["raw_metric_evidence"]["run_end_s"], 31.0)
        self.assertEqual(record["terminal_state"], "RECOVERY_FAILED")

    def test_a20_uses_command_path_objectives_and_legitimate_noop_metric(self) -> None:
        bundle = self._bundle("A20")
        record = bundle["run_record"]
        objectives = record["raw_metric_evidence"]["objective_instances"]
        self.assertEqual(
            [row["objective_instance_id"] for row in objectives],
            ["replay-MO-1-response-interval", "replay-MO-3-response-interval"],
        )
        self.assertTrue(all(row["completed"] for row in objectives))
        self.assertEqual(record["outcomes"]["mission_objective_completion_ratio"], 1.0)
        self.assertEqual(record["outcomes"]["legitimate_command_rejection_rate"], 0.0)
        self.assertTrue(record["raw_metric_evidence"]["containment"]["predicate"])
        self.assertEqual(record["terminal_state"], "OPERATIONAL_BUT_UNVERIFIED")

    def test_a21_retains_requested_p7_and_records_actual_p1_without_oracle(self) -> None:
        bundle = self._bundle("A21")
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        self.assertEqual(record["policy_id"], "P7")
        metadata = provenance["execution_metadata"]
        self.assertEqual(metadata["requested_policy_id"], "P7")
        self.assertEqual(metadata["effective_policy_id"], "P1")
        self.assertEqual(metadata["selected_action"], "ISOLATE_MODELED_SOURCE")
        self.assertFalse(metadata["oracle_ground_truth_read"])

    def test_unexpected_replay_outcome_is_retained_not_rejected(self) -> None:
        bundle = self._bundle("A19", replay_delta=0)
        record = bundle["run_record"]
        provenance = bundle["binding_provenance"]
        expectation = provenance["predeclared_expectation"]
        validity = provenance["scientific_validity"]
        self.assertFalse(record["outcomes"]["unauthorized_effect_completed"])
        self.assertFalse(expectation["outcome_matches_predeclared_expectation"])
        self.assertFalse(expectation["expectation_used_as_metric_input"])
        self.assertFalse(expectation["expectation_used_to_reject_scientific_outcome"])
        self.assertTrue(validity["unexpected_scientific_outcome_retained"])
        self.assertTrue(validity["scientific_observation_retained"])
        self.assertIsNone(record["invalid_run_reason"])

    def test_post_response_noop_is_required_for_m06(self) -> None:
        measurement = self._measurement(cell_id="A20")
        measurement["post_response_authorized_noop_attempted"] = 0
        with self.assertRaisesRegex(ValueError, "one post-response NOOP"):
            build_static_fixture_bundle(
                plan=self._plan("A20"),
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_treatment_fidelity_failure_is_invalid_not_scientific_outcome(self) -> None:
        measurement = self._measurement(cell_id="A20")
        measurement["replay_gateway_forwarded"] = True
        with self.assertRaisesRegex(ValueError, "treatment semantics"):
            build_static_fixture_bundle(
                plan=self._plan("A20"),
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_full_thirty_second_analysis_window_is_required(self) -> None:
        measurement = self._measurement(cell_id="A19")
        measurement["observation_complete_ns"] = 31_999_999_999
        with self.assertRaisesRegex(ValueError, "30-second analysis horizon"):
            build_static_fixture_bundle(
                plan=self._plan("A19"),
                measurement=measurement,
                host_architecture="static-test",
            )

    def test_static_fixture_never_consumes_campaign_seed_or_becomes_data(self) -> None:
        provenance = self._bundle("A20")["binding_provenance"]
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
