from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "study3x"
    / "validation"
    / "validate_p99_x10_prefreeze.py"
)
SPEC = importlib.util.spec_from_file_location("s3x_p99_x10_prefreeze", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
s3x = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s3x)


def row(
    mission: str,
    channel: str,
    p99: str,
    threshold: str,
    count: int,
    minimum: str,
    cadence_max: str,
) -> dict[str, str]:
    return {
        "mission": mission,
        "channel_file": channel,
        "channel_sha256": "a" * 64,
        "positive_delta_count": "100",
        "cadence_p99_seconds": p99,
        "threshold_seconds": threshold,
        "candidate_rule": "P99_X10",
        "exceedance_count": str(count),
        "exceedance_fraction": "0.01" if count else "0.0",
        "exceedance_min_seconds": minimum,
        "exceedance_median_seconds": minimum,
        "exceedance_p95_seconds": minimum,
        "exceedance_p99_seconds": minimum,
        "exceedance_max_seconds": minimum,
        "cadence_max_seconds": cadence_max,
    }


class S3XP99X10PreFreezeTests(unittest.TestCase):
    def test_candidate_constants_are_prefreeze_only(self) -> None:
        self.assertEqual(s3x.CANDIDATE_RULE, "P99_X10")
        self.assertEqual(s3x.EXPECTED_CHANNELS, 176)
        self.assertEqual(s3x.EXPECTED_TOTAL_EXCEEDANCES, 1919)
        self.assertEqual(s3x.EXPECTED_CHANNELS_WITH_EXCEEDANCES, 171)
        self.assertEqual(len(s3x.EXPECTED_ZERO_CHANNELS), 5)

    def test_canonical_projection_is_order_independent(self) -> None:
        a = row("ESA-Mission1", "channel_2.zip", "3", "30", 1, "31", "100")
        b = row("ESA-Mission1", "channel_1.zip", "3", "30", 1, "32", "100")
        self.assertEqual(
            s3x.canonical_projection([a, b]),
            s3x.canonical_projection([b, a]),
        )

    def test_valid_candidate_rows_pass_strict_semantics(self) -> None:
        nonzero = row(
            "ESA-Mission1",
            "channel_1.zip",
            "3",
            "30",
            1,
            "30.000000001",
            "100",
        )
        zero = row(
            "ESA-Mission2",
            "channel_2.zip",
            "90",
            "900",
            0,
            "",
            "899",
        )
        for key in (
            "exceedance_median_seconds",
            "exceedance_p95_seconds",
            "exceedance_p99_seconds",
            "exceedance_max_seconds",
        ):
            zero[key] = ""

        projection = s3x.projection_sha256([nonzero, zero])
        with (
            mock.patch.object(s3x, "EXPECTED_CHANNELS", 2),
            mock.patch.object(s3x, "EXPECTED_SENSITIVITY_ROWS", 2),
            mock.patch.object(s3x, "EXPECTED_TOTAL_EXCEEDANCES", 1),
            mock.patch.object(s3x, "EXPECTED_CHANNELS_WITH_EXCEEDANCES", 1),
            mock.patch.object(
                s3x,
                "EXPECTED_ZERO_CHANNELS",
                {("ESA-Mission2", "channel_2.zip")},
            ),
            mock.patch.object(s3x, "EXPECTED_PROJECTION_SHA256", projection),
        ):
            result = s3x.validate_candidate_rows([zero, nonzero])

        self.assertEqual(result["channels"], 2)
        self.assertEqual(result["total_exceedance_count"], 1)
        self.assertEqual(result["channels_with_zero_exceedances"], 1)

    def test_equal_to_threshold_is_rejected_as_non_strict(self) -> None:
        bad = row(
            "ESA-Mission1",
            "channel_1.zip",
            "3",
            "30",
            1,
            "30",
            "100",
        )
        projection = s3x.projection_sha256([bad])
        with (
            mock.patch.object(s3x, "EXPECTED_CHANNELS", 1),
            mock.patch.object(s3x, "EXPECTED_SENSITIVITY_ROWS", 1),
            mock.patch.object(s3x, "EXPECTED_TOTAL_EXCEEDANCES", 1),
            mock.patch.object(s3x, "EXPECTED_CHANNELS_WITH_EXCEEDANCES", 1),
            mock.patch.object(s3x, "EXPECTED_ZERO_CHANNELS", set()),
            mock.patch.object(s3x, "EXPECTED_PROJECTION_SHA256", projection),
        ):
            with self.assertRaises(SystemExit):
                s3x.validate_candidate_rows([bad])

    def test_threshold_formula_drift_is_rejected(self) -> None:
        bad = row(
            "ESA-Mission1",
            "channel_1.zip",
            "3",
            "31",
            1,
            "32",
            "100",
        )
        projection = s3x.projection_sha256([bad])
        with (
            mock.patch.object(s3x, "EXPECTED_CHANNELS", 1),
            mock.patch.object(s3x, "EXPECTED_SENSITIVITY_ROWS", 1),
            mock.patch.object(s3x, "EXPECTED_TOTAL_EXCEEDANCES", 1),
            mock.patch.object(s3x, "EXPECTED_CHANNELS_WITH_EXCEEDANCES", 1),
            mock.patch.object(s3x, "EXPECTED_ZERO_CHANNELS", set()),
            mock.patch.object(s3x, "EXPECTED_PROJECTION_SHA256", projection),
        ):
            with self.assertRaises(SystemExit):
                s3x.validate_candidate_rows([bad])


if __name__ == "__main__":
    unittest.main()
