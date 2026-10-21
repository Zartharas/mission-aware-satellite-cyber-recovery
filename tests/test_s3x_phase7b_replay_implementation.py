from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest

from study3x.audit.reference_replay import evaluate_reference
from study3x.src.recovery_replay import (
    EVIDENCE_STATES,
    POLICIES,
    TIMING_ARMS,
    evaluate_case,
    evaluate_interval,
    parse_interval_row,
    verify_frozen_interval_artifact,
)


def synthetic_interval(
    *,
    interval_id: str = "S3X-SYNTH-001",
    delta: str = "25",
    cadence: str = "2",
    threshold: str = "20",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "experiment_id": "S3X-ETA-001",
        "source_freeze_id": "S3X-ESA-V2-SOURCE-FREEZE-001",
        "source_freeze_sha256": "synthetic-not-used",
        "gap_rule_freeze_id": "S3X-P99X10-GAP-RULE-FREEZE-001",
        "gap_rule": "P99_X10",
        "mission": "SYNTHETIC-MISSION",
        "channel_file": "synthetic_channel.zip",
        "channel_sha256": "synthetic-not-used",
        "preceding_timestamp_ns": 0,
        "following_timestamp_ns": 25_000_000_000,
        "preceding_timestamp": "SYNTHETIC-T0",
        "following_timestamp": "SYNTHETIC-T1",
        "delta_nanoseconds": 25_000_000_000,
        "delta_seconds": delta,
        "cadence_p99_seconds": cadence,
        "threshold_seconds": threshold,
        "comparison_operator": ">",
        "diagnostic_label": "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC",
        "interval_id": interval_id,
    }


PARITY_FIELDS = (
    "interval_id",
    "policy",
    "evidence_state",
    "timing_arm",
    "normalized_hiatus_units",
    "cache_origin_unsafe_qualified_exposure_cadence_units",
    "protective_hiatus_duration_cadence_units",
    "first_refresh_time_cadence_units",
    "first_refresh_action",
    "first_refresh_gate_qualified",
    "first_refresh_unsafe_permissive",
    "first_refresh_unsafe_qualified",
    "first_refresh_unsafe_qualification_origin",
    "v5_first_refresh_qualification_delay_cadence_units",
)


class Phase7BReplayImplementationTests(unittest.TestCase):
    def test_synthetic_interval_expands_to_exactly_18_cases(self):
        rows = evaluate_interval(synthetic_interval())
        self.assertEqual(len(rows), 18)
        keys = {(r.policy, r.evidence_state, r.timing_arm) for r in rows}
        self.assertEqual(len(keys), 18)

    def test_exact_rational_normalization(self):
        parsed = parse_interval_row(
            synthetic_interval(delta="31.5", cadence="2.5", threshold="25")
        )
        self.assertEqual(parsed.normalized_hiatus.numerator, 63)
        self.assertEqual(parsed.normalized_hiatus.denominator, 5)

    def test_gap_arm_cache_and_protective_boundaries(self):
        row = synthetic_interval()

        b0 = evaluate_case(
            row,
            policy="S2_B0_FAIL_CLOSED",
            evidence_state="V0",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
        self.assertEqual(
            b0.cache_origin_unsafe_qualified_exposure_cadence_units,
            "1",
        )
        self.assertEqual(
            b0.protective_hiatus_duration_cadence_units,
            "23/2",
        )

        b2 = evaluate_case(
            row,
            policy="S2_B2_RISK_THRESHOLD",
            evidence_state="V0",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
        self.assertEqual(
            b2.cache_origin_unsafe_qualified_exposure_cadence_units,
            "0",
        )
        self.assertEqual(
            b2.protective_hiatus_duration_cadence_units,
            "25/2",
        )

        s1 = evaluate_case(
            row,
            policy="S2_S1_EVIDENCE_AWARE",
            evidence_state="V0",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
        self.assertEqual(
            s1.cache_origin_unsafe_qualified_exposure_cadence_units,
            "0",
        )
        self.assertEqual(
            s1.protective_hiatus_duration_cadence_units,
            "25/2",
        )

    def test_v5_first_refresh_policy_distinction(self):
        row = synthetic_interval()
        for arm, expected_time in (
            ("EMPIRICAL_HIATUS_PROXY", "25/2"),
            ("MATCHED_CONTINUOUS_REFRESH_CONTROL", "0"),
        ):
            b0 = evaluate_case(
                row,
                policy="S2_B0_FAIL_CLOSED",
                evidence_state="V5",
                timing_arm=arm,
            )
            self.assertTrue(b0.first_refresh_gate_qualified)
            self.assertTrue(b0.first_refresh_unsafe_qualified)
            self.assertEqual(
                b0.first_refresh_unsafe_qualification_origin,
                "V5_AFFECTED_RECORD",
            )
            self.assertEqual(
                b0.v5_first_refresh_qualification_delay_cadence_units,
                expected_time,
            )

            s1 = evaluate_case(
                row,
                policy="S2_S1_EVIDENCE_AWARE",
                evidence_state="V5",
                timing_arm=arm,
            )
            self.assertTrue(s1.first_refresh_gate_qualified)
            self.assertEqual(
                s1.v5_first_refresh_qualification_delay_cadence_units,
                expected_time,
            )

            b2 = evaluate_case(
                row,
                policy="S2_B2_RISK_THRESHOLD",
                evidence_state="V5",
                timing_arm=arm,
            )
            self.assertFalse(b2.first_refresh_gate_qualified)
            self.assertFalse(b2.first_refresh_unsafe_qualified)
            self.assertIsNone(
                b2.v5_first_refresh_qualification_delay_cadence_units
            )

    def test_v0_permissive_is_not_gate_qualified(self):
        row = synthetic_interval()
        for policy in ("S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"):
            result = evaluate_case(
                row,
                policy=policy,
                evidence_state="V0",
                timing_arm="MATCHED_CONTINUOUS_REFRESH_CONTROL",
            )
            self.assertEqual(result.first_refresh_action, "PROCEED_TO_RECOVERY_GATE")
            self.assertTrue(result.first_refresh_unsafe_permissive)
            self.assertFalse(result.first_refresh_gate_qualified)
            self.assertFalse(result.first_refresh_unsafe_qualified)

    def test_v4_is_unqualified_at_first_refresh(self):
        row = synthetic_interval()
        expected = {
            "S2_B0_FAIL_CLOSED": "RESTRICT_AND_REQUEST_AUTHORIZATION",
            "S2_B2_RISK_THRESHOLD": "HOLD_AND_REQUIRE_EVIDENCE",
            "S2_S1_EVIDENCE_AWARE": "HOLD_AND_REQUIRE_EVIDENCE",
        }
        for policy, action in expected.items():
            result = evaluate_case(
                row,
                policy=policy,
                evidence_state="V4",
                timing_arm="EMPIRICAL_HIATUS_PROXY",
            )
            self.assertEqual(result.first_refresh_action, action)
            self.assertFalse(result.first_refresh_gate_qualified)
            self.assertFalse(result.first_refresh_unsafe_qualified)

    def test_primary_reference_parity_for_multiple_synthetic_ratios(self):
        fixtures = (
            synthetic_interval(interval_id="S3X-SYNTH-A", delta="25", cadence="2", threshold="20"),
            synthetic_interval(interval_id="S3X-SYNTH-B", delta="31.5", cadence="2.5", threshold="25"),
            synthetic_interval(interval_id="S3X-SYNTH-C", delta="27.5", cadence="2.5", threshold="25"),
        )
        mismatches = []
        for row in fixtures:
            for policy in POLICIES:
                for evidence_state in EVIDENCE_STATES:
                    for timing_arm in TIMING_ARMS:
                        primary = asdict(
                            evaluate_case(
                                row,
                                policy=policy,
                                evidence_state=evidence_state,
                                timing_arm=timing_arm,
                            )
                        )
                        reference = evaluate_reference(
                            row,
                            policy=policy,
                            evidence_state=evidence_state,
                            timing_arm=timing_arm,
                        )
                        for field in PARITY_FIELDS:
                            if primary[field] != reference[field]:
                                mismatches.append(
                                    (
                                        row["interval_id"],
                                        policy,
                                        evidence_state,
                                        timing_arm,
                                        field,
                                        primary[field],
                                        reference[field],
                                    )
                                )
        self.assertEqual(mismatches, [])

    def test_inconsistent_membership_rows_fail_closed(self):
        with self.assertRaises(ValueError):
            parse_interval_row(
                synthetic_interval(delta="20", cadence="2", threshold="20")
            )
        with self.assertRaises(ValueError):
            parse_interval_row(
                synthetic_interval(delta="25", cadence="2", threshold="19")
            )

    def test_wrong_artifact_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not-frozen.csv"
            path.write_bytes(b"synthetic fixture only\n")
            with self.assertRaises(ValueError):
                verify_frozen_interval_artifact(path)


if __name__ == "__main__":
    unittest.main()
