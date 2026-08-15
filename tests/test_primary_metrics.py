from __future__ import annotations

import unittest

from src.mission_recovery.primary_metrics import (
    RECOVERY_CRITERIA,
    build_invalid_run_record,
    build_run_record,
    classify_terminal_state,
    score_raw_metric_evidence,
)


def recovery_evidence_all(value: bool = True) -> dict[str, bool]:
    return {key: value for key in RECOVERY_CRITERIA}


def valid_raw() -> dict:
    return {
        "event_success": {
            "predicate": False,
            "timestamp_s": None,
        },
        "containment": {
            "predicate": True,
            "timestamp_s": 12.5,
        },
        "trusted_recovery": {
            "predicate": True,
            "timestamp_s": 35.0,
        },
        "objective_instances": [
            {
                "objective_instance_id": "MO-1-A",
                "weight": 3.0,
                "scheduled_start_s": 10.0,
                "scheduled_end_s": 60.0,
                "completion_predicate": "mo1_complete",
                "completion_evidence_ref": "fixture:mo1",
                "completed": True,
            },
            {
                "objective_instance_id": "MO-3-A",
                "weight": 1.0,
                "scheduled_start_s": 10.0,
                "scheduled_end_s": 60.0,
                "completion_predicate": "mo3_complete",
                "completion_evidence_ref": "fixture:mo3",
                "completed": False,
            },
        ],
        "invariant_violation_intervals": [
            {
                "invariant_id": "SI-2",
                "start_s": 4.0,
                "end_s": 5.0,
                "ground_truth_evidence_ref": "fixture:si2-a",
            },
            {
                "invariant_id": "SI-2",
                "start_s": 8.0,
                "end_s": 9.0,
                "ground_truth_evidence_ref": "fixture:si2-b",
            },
        ],
        "legitimate_commands": {
            "attempted": 4,
            "rejected": 1,
        },
        "ground_spacecraft_divergence_intervals": [
            {
                "state_key": "command_authority",
                "start_s": 1.0,
                "end_s": 5.0,
            },
            {
                "state_key": "approved_version",
                "start_s": 4.0,
                "end_s": 8.0,
            },
            {
                "state_key": "recovery_status",
                "start_s": 10.0,
                "end_s": 12.0,
            },
        ],
        "recovery_checklist": [
            {
                "criterion_id": key,
                "available_current": True,
                "evidence_ref": f"fixture:{key}",
            }
            for key in RECOVERY_CRITERIA
        ],
        "recovery_checklist_excluded": [],
        "run_end_s": 60.0,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": True,
            "operational_restored": True,
            "recovery_failed": False,
            "contained": True,
        },
    }


class PrimaryMetricTests(unittest.TestCase):
    def test_scores_raw_evidence_without_expected_substitution(self) -> None:
        result = score_raw_metric_evidence(
            event_activation_s=10.0,
            raw=valid_raw(),
            recovery_evidence=recovery_evidence_all(),
        )

        self.assertFalse(result["unauthorized_effect_completed"])
        self.assertEqual(
            result["mission_objective_completion_ratio"],
            0.75,
        )
        self.assertEqual(result["safety_invariant_violations"], ["SI-2"])
        self.assertEqual(result["safety_invariant_violation_count"], 1)
        self.assertEqual(
            result["legitimate_command_rejection_rate"],
            0.25,
        )
        self.assertEqual(
            result["ground_spacecraft_state_divergence_s"],
            9.0,
        )
        self.assertEqual(result["evidence_completeness_ratio"], 1.0)
        self.assertEqual(result["time_to_containment_s"], 2.5)
        self.assertEqual(result["time_to_verified_recovery_s"], 25.0)
        self.assertEqual(result["run_end_censoring_s"], 50.0)
        self.assertEqual(
            result["recovery_terminal_state"],
            "TRUSTED_RECOVERY_CONFIRMED",
        )

    def test_zero_legitimate_command_denominator_is_null(self) -> None:
        raw = valid_raw()
        raw["legitimate_commands"] = {
            "attempted": 0,
            "rejected": 0,
        }

        result = score_raw_metric_evidence(
            event_activation_s=10.0,
            raw=raw,
            recovery_evidence=recovery_evidence_all(),
        )
        self.assertIsNone(
            result["legitimate_command_rejection_rate"]
        )

    def test_overlapping_divergence_intervals_count_once(self) -> None:
        result = score_raw_metric_evidence(
            event_activation_s=10.0,
            raw=valid_raw(),
            recovery_evidence=recovery_evidence_all(),
        )
        self.assertEqual(
            result["ground_spacecraft_state_divergence_s"],
            9.0,
        )

    def test_terminal_precedence_is_deterministic(self) -> None:
        predicates = valid_raw()["terminal_state_predicates"]
        predicates["mission_loss"] = True
        self.assertEqual(
            classify_terminal_state(predicates),
            "MISSION_LOSS",
        )

        predicates["run_invalid"] = True
        self.assertEqual(
            classify_terminal_state(predicates),
            "RUN_INVALID",
        )

    def test_rejects_impossible_command_counts(self) -> None:
        raw = valid_raw()
        raw["legitimate_commands"] = {
            "attempted": 1,
            "rejected": 2,
        }

        with self.assertRaisesRegex(
            ValueError,
            "invalid legitimate-command counts",
        ):
            score_raw_metric_evidence(
                event_activation_s=10.0,
                raw=raw,
                recovery_evidence=recovery_evidence_all(),
            )

    def test_rejects_timestamp_when_predicate_false(self) -> None:
        raw = valid_raw()
        raw["event_success"] = {
            "predicate": False,
            "timestamp_s": 2.0,
        }

        with self.assertRaisesRegex(
            ValueError,
            "event_success predicate false with timestamp",
        ):
            score_raw_metric_evidence(
                event_activation_s=10.0,
                raw=raw,
                recovery_evidence=recovery_evidence_all(),
            )

    def test_rejects_timestamp_before_event_activation(self) -> None:
        raw = valid_raw()
        raw["containment"] = {
            "predicate": True,
            "timestamp_s": 9.9,
        }

        with self.assertRaisesRegex(
            ValueError,
            "before event activation",
        ):
            score_raw_metric_evidence(
                event_activation_s=10.0,
                raw=raw,
                recovery_evidence=recovery_evidence_all(),
            )

    def test_rejects_false_trusted_recovery(self) -> None:
        raw = valid_raw()
        evidence = recovery_evidence_all()
        evidence["measured_state_current"] = False
        for row in raw["recovery_checklist"]:
            if row["criterion_id"] == "measured_state_current":
                row["available_current"] = False

        with self.assertRaisesRegex(
            ValueError,
            "incomplete recovery evidence",
        ):
            score_raw_metric_evidence(
                event_activation_s=10.0,
                raw=raw,
                recovery_evidence=evidence,
            )

    def test_applicable_recovery_evidence_excludes_n_a(self) -> None:
        raw = valid_raw()
        evidence = recovery_evidence_all()
        excluded = "required_telemetry_restored"
        evidence[excluded] = None
        raw["recovery_checklist"] = [
            row
            for row in raw["recovery_checklist"]
            if row["criterion_id"] != excluded
        ]
        raw["recovery_checklist_excluded"] = [excluded]
        raw["trusted_recovery"] = {"predicate": False, "timestamp_s": None}
        raw["terminal_state_predicates"]["trusted_recovery_confirmed"] = False
        raw["terminal_state_predicates"]["operational_restored"] = True

        result = score_raw_metric_evidence(
            event_activation_s=10.0,
            raw=raw,
            recovery_evidence=evidence,
        )
        self.assertEqual(result["evidence_completeness_ratio"], 1.0)
        self.assertEqual(
            result["recovery_terminal_state"],
            "OPERATIONAL_BUT_UNVERIFIED",
        )

    def test_build_invalid_run_record_needs_no_fabricated_metrics(self) -> None:
        record = build_invalid_run_record(
            run_id="wp8-invalid-001",
            model_version="0.3.0",
            seed=101,
            mission_state_id="M0",
            event_id="E1",
            policy_id="P0",
            contact_condition_id="C0",
            evidence_condition_id="T0",
            environment={
                "host_architecture": "x86_64",
                "simulator": "NOS3",
                "simulator_commit": "5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
                "flight_software": "cFS via NOS3 submodule",
                "flight_software_commit": "sample-cfs-commit",
                "snapshot_id": "invalid-fixture",
                "container_or_vm_digest": None,
            },
            invalid_run_reason="evidence_capture_failure",
        )
        self.assertEqual(record["terminal_state"], "RUN_INVALID")
        self.assertNotIn("outcomes", record)
        self.assertNotIn("raw_metric_evidence", record)

    def test_build_run_record_uses_derived_metrics(self) -> None:
        record = build_run_record(
            run_id="wp8-test-001",
            model_version="0.3.0",
            seed=101,
            mission_state_id="M4",
            event_id="E3",
            policy_id="P5",
            contact_condition_id="C0",
            evidence_condition_id="T0",
            environment={
                "host_architecture": "x86_64",
                "simulator": "NOS3",
                "simulator_commit": "5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
                "flight_software": "cFS via NOS3 submodule",
                "flight_software_commit": "sample-cfs-commit",
                "snapshot_id": "sample-clean-baseline-v1",
                "container_or_vm_digest": "sha256:sample",
            },
            run_start_utc="2026-08-15T20:00:00Z",
            event_activation_s=10.0,
            run_end_utc="2026-08-15T20:02:00Z",
            raw_metric_evidence=valid_raw(),
            recovery_evidence=recovery_evidence_all(),
            notes="unit-test fixture only",
        )

        self.assertEqual(record["timing"]["containment_s"], 2.5)
        self.assertEqual(record["timing"]["verified_recovery_s"], 25.0)
        self.assertEqual(
            record["outcomes"]["mission_objective_completion_ratio"],
            0.75,
        )
        self.assertEqual(
            record["terminal_state"],
            "TRUSTED_RECOVERY_CONFIRMED",
        )
        self.assertIn("raw_metric_evidence", record)


if __name__ == "__main__":
    unittest.main()
