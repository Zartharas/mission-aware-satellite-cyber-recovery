from __future__ import annotations

import json
from pathlib import Path
import unittest

from study3x.audit.reference_replay_v2 import evaluate_reference
from study3x.src import recovery_replay as V1
from study3x.src import recovery_replay_v2 as V2

ROOT = Path(__file__).resolve().parents[1]


def row(
    *,
    delta: str = "0.8",
    cadence: str = "0.07",
    threshold: str = "0.7000000000000001",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "experiment_id": "S3X-ETA-001",
        "source_freeze_id": "S3X-ESA-V2-SOURCE-FREEZE-001",
        "source_freeze_sha256": "synthetic",
        "gap_rule_freeze_id": "S3X-P99X10-GAP-RULE-FREEZE-001",
        "gap_rule": "P99_X10",
        "mission": "SYNTHETIC-MISSION",
        "channel_file": "synthetic_channel.zip",
        "channel_sha256": "synthetic",
        "preceding_timestamp_ns": 0,
        "following_timestamp_ns": 800000000,
        "preceding_timestamp": "SYNTHETIC-T0",
        "following_timestamp": "SYNTHETIC-T1",
        "delta_nanoseconds": 800000000,
        "delta_seconds": delta,
        "cadence_p99_seconds": cadence,
        "threshold_seconds": threshold,
        "comparison_operator": ">",
        "diagnostic_label": "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC",
        "interval_id": "S3X-SYNTH-FLOAT-CONTRACT",
    }


class Phase7DFloatContractCorrectionTests(unittest.TestCase):
    def test_regression_v1_decimal_exact_check_rejects_phase6_float_serialization(self):
        fixture = row()
        self.assertEqual(float(fixture["threshold_seconds"]), float(fixture["cadence_p99_seconds"]) * 10.0)
        with self.assertRaisesRegex(
            ValueError,
            "threshold relationship is inconsistent",
        ):
            V1.parse_interval_row(fixture)

    def test_v2_accepts_original_phase6_float_contract_without_tolerance(self):
        fixture = row()
        parsed = V2.parse_interval_row(fixture)
        self.assertEqual(parsed.normalized_hiatus.numerator, 80)
        self.assertEqual(parsed.normalized_hiatus.denominator, 7)

    def test_v2_rejects_decimal_neat_but_float_incorrect_threshold(self):
        fixture = row(threshold="0.7")
        self.assertNotEqual(
            float(fixture["threshold_seconds"]),
            float(fixture["cadence_p99_seconds"]) * 10.0,
        )
        with self.assertRaisesRegex(ValueError, "threshold float relationship"):
            V2.parse_interval_row(fixture)

    def test_v2_preserves_strict_greater_than_membership(self):
        fixture = row(delta="0.7000000000000001")
        with self.assertRaisesRegex(ValueError, "not a member"):
            V2.parse_interval_row(fixture)

    def test_v2_primary_reference_parity_on_float_serialization_edge(self):
        fixture = row()
        primary = V2.evaluate_case(
            fixture,
            policy="S2_S1_EVIDENCE_AWARE",
            evidence_state="V5",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
        reference = evaluate_reference(
            fixture,
            policy="S2_S1_EVIDENCE_AWARE",
            evidence_state="V5",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
        self.assertEqual(primary.normalized_hiatus_units, reference["normalized_hiatus_units"])
        self.assertEqual(primary.first_refresh_action, reference["first_refresh_action"])
        self.assertEqual(primary.first_refresh_gate_qualified, reference["first_refresh_gate_qualified"])
        self.assertEqual(primary.first_refresh_unsafe_qualified, reference["first_refresh_unsafe_qualified"])
        self.assertEqual(
            primary.v5_first_refresh_qualification_delay_cadence_units,
            reference["v5_first_refresh_qualification_delay_cadence_units"],
        )

    def test_corrected_authorization_is_not_effective_on_feature_branch(self):
        auth = json.loads(
            (ROOT / "study3x/config/S3X_PHASE7_RUNTIME_AUTH_002.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(auth["authorization_id"], "S3X-PHASE7-RUNTIME-AUTH-002")
        self.assertEqual(auth["status"], "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE")
        self.assertFalse(auth["result_freeze_boundary"]["result_freeze_authorized_now"])
        self.assertFalse(auth["result_freeze_boundary"]["manuscript_claim_use_authorized_now"])
        self.assertTrue(
            auth["effectivity"][
                "actual_corrected_runtime_execution_requires_explicit_post_merge_author_instruction"
            ]
        )


if __name__ == "__main__":
    unittest.main()
