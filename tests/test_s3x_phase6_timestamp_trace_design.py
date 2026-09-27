from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXTRACTOR = load_module(
    "s3x_phase6_extractor",
    "study3x/validation/extract_p99_x10_timestamp_intervals.py",
)
VALIDATOR = load_module(
    "s3x_phase6_validator",
    "study3x/validation/validate_p99_x10_timestamp_intervals.py",
)


class Phase6TimestampTraceDesignTests(unittest.TestCase):
    def test_quantile_linear_matches_independent_validator(self):
        values = [1.0, 2.0, 3.0, 4.0]
        expected = 3.97
        self.assertAlmostEqual(EXTRACTOR.quantile_linear(values, 0.99), expected)
        self.assertAlmostEqual(
            VALIDATOR.independent_quantile_linear(values, 0.99),
            expected,
        )

    def test_strict_greater_than_boundary(self):
        p99 = 4.0
        self.assertFalse(EXTRACTOR.eligible_delta(40.0, p99))
        self.assertTrue(EXTRACTOR.eligible_delta(40.000000001, p99))

    def test_interval_id_is_full_stable_sha256(self):
        args = (
            "ESA-Mission1",
            "channel_2.zip",
            "a" * 64,
            1000000000,
            2000000000,
        )
        first = EXTRACTOR.interval_id(*args)
        second = EXTRACTOR.interval_id(*args)
        independent = VALIDATOR.independent_interval_id(*args)
        self.assertEqual(first, second)
        self.assertEqual(first, independent)
        self.assertTrue(first.startswith("S3X-INT-"))
        self.assertEqual(len(first), len("S3X-INT-") + 64)

    def test_output_sort_uses_numeric_channel_order(self):
        rows = [
            {
                "mission": "ESA-Mission1",
                "channel_file": "channel_10.zip",
                "preceding_timestamp_ns": 1,
                "following_timestamp_ns": 2,
                "interval_id": "b",
            },
            {
                "mission": "ESA-Mission1",
                "channel_file": "channel_2.zip",
                "preceding_timestamp_ns": 1,
                "following_timestamp_ns": 2,
                "interval_id": "a",
            },
        ]
        ordered = sorted(rows, key=EXTRACTOR.row_sort_key)
        self.assertEqual(ordered[0]["channel_file"], "channel_2.zip")
        self.assertEqual(ordered[1]["channel_file"], "channel_10.zip")

    def test_phase5b_projection_serialization_is_shared(self):
        extractor_rows = [
            {
                "mission": "ESA-Mission1",
                "channel_file": "channel_10.zip",
                "channel_sha256": "b" * 64,
                "positive_delta_count": 20,
                "cadence_p99_seconds": 18.0,
                "threshold_seconds": 180.0,
                "interval_count": 2,
            },
            {
                "mission": "ESA-Mission1",
                "channel_file": "channel_2.zip",
                "channel_sha256": "a" * 64,
                "positive_delta_count": 10,
                "cadence_p99_seconds": 30.0,
                "threshold_seconds": 300.0,
                "interval_count": 1,
            },
        ]
        validator_rows = [
            {
                "mission": row["mission"],
                "channel_file": row["channel_file"],
                "channel_sha256": row["channel_sha256"],
                "positive_delta_count": row["positive_delta_count"],
                "cadence_p99_seconds": row["cadence_p99_seconds"],
                "threshold_seconds": row["threshold_seconds"],
                "exceedance_count": row["interval_count"],
            }
            for row in extractor_rows
        ]
        self.assertEqual(
            EXTRACTOR.channel_projection_sha256(extractor_rows),
            VALIDATOR.projection_sha256(validator_rows),
        )

    def test_design_protocol_keeps_runtime_closed(self):
        protocol = json.loads(
            (
                ROOT
                / "study3x/config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            protocol["protocol_id"],
            "S3X-PHASE6-TIMESTAMP-TRACE-EXTRACTION-PROTOCOL-001",
        )
        self.assertFalse(
            protocol["authorization_model"]["timestamp_level_extraction_authorized"]
        )
        self.assertTrue(
            protocol["authorization_model"][
                "runtime_requires_separate_versioned_authorization_record"
            ]
        )
        self.assertFalse(protocol["gates"]["trace_population_frozen"])
        self.assertFalse(protocol["gates"]["recovery_policy_execution_performed"])
        self.assertFalse(protocol["gates"]["scientific_results_generated"])

    def test_no_runtime_authorization_record_is_committed_in_phase6a(self):
        records = list(
            (ROOT / "study3x/config").glob(
                "S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_*.json"
            )
        )
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
