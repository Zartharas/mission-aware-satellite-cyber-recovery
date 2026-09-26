from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "study3x"
    / "validation"
    / "analyze_cadence_gap_sensitivity.py"
)
SPEC = importlib.util.spec_from_file_location("s3x_gap_sensitivity", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
s3x = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s3x)


class S3XGapSensitivityTests(unittest.TestCase):
    def test_quantile_linear_matches_expected_interpolation(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0]
        self.assertAlmostEqual(s3x.quantile_linear(values, 0.5), 2.5)
        self.assertAlmostEqual(s3x.quantile_linear(values, 0.95), 3.85)

    def test_candidate_thresholds_are_diagnostic_formulas(self) -> None:
        values = [1.0] * 99 + [10.0]
        thresholds = s3x.candidate_thresholds(values)
        p99 = s3x.quantile_linear(values, 0.99)
        median = s3x.quantile_linear(values, 0.5)

        self.assertEqual(set(thresholds), {row[0] for row in s3x.RULES})
        self.assertAlmostEqual(thresholds["P99_X1"], p99)
        self.assertAlmostEqual(thresholds["P99_X10"], p99 * 10.0)
        self.assertAlmostEqual(
            thresholds["MAX_P99_MEDIAN_X5"],
            max(p99, median * 5.0),
        )

    def test_rule_uses_strict_greater_than(self) -> None:
        result = s3x.evaluate_rule([1.0, 2.0, 3.0, 4.0], 3.0)
        self.assertEqual(result["exceedance_count"], 1)
        self.assertEqual(result["min_seconds"], 4.0)
        self.assertEqual(result["sum_interval_seconds"], 4.0)
        self.assertEqual(result["sum_excess_above_threshold_seconds"], 1.0)

    def test_top_delta_frequencies_are_stable(self) -> None:
        result = s3x.top_delta_frequencies(
            [3.0, 1.0, 3.0, 2.0, 2.0, 3.0, 1.0],
            top_n=3,
        )
        self.assertEqual(result, [(3.0, 3), (1.0, 2), (2.0, 2)])

    def test_aggregate_rule_counts_zero_and_nonzero_channels(self) -> None:
        rows = [
            {
                "positive_delta_count": 100,
                "exceedance_count": 0,
                "exceedance_fraction": 0.0,
                "sum_interval_seconds": 0.0,
                "sum_excess_above_threshold_seconds": 0.0,
            },
            {
                "positive_delta_count": 100,
                "exceedance_count": 2,
                "exceedance_fraction": 0.02,
                "sum_interval_seconds": 25.0,
                "sum_excess_above_threshold_seconds": 5.0,
            },
        ]
        result = s3x.aggregate_rule(rows)
        self.assertEqual(result["channels"], 2)
        self.assertEqual(result["channels_with_zero_exceedances"], 1)
        self.assertEqual(result["channels_with_exceedances"], 1)
        self.assertEqual(result["total_exceedance_count"], 2)
        self.assertAlmostEqual(result["pooled_exceedance_fraction"], 0.01)
        self.assertEqual(result["channels_over_1pct_exceedance_fraction"], 1)
        self.assertEqual(result["channels_over_5pct_exceedance_fraction"], 0)


if __name__ == "__main__":
    unittest.main()
