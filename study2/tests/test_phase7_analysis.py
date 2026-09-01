from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "analysis" / "analyze_phase7.py"
SPEC = importlib.util.spec_from_file_location("study2_phase7_analysis", SCRIPT)
analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(analysis)


class Phase7AnalysisTests(unittest.TestCase):
    def test_expected_positions_are_exact_and_unique(self):
        positions = analysis.expected_positions()
        self.assertEqual(len(positions), 3872)
        self.assertEqual(len(set(positions)), 3872)
        self.assertEqual(positions[0], ("A01", 2100001, "S2-AEATR-001:A01:2100001"))
        self.assertEqual(positions[-1], ("E09", 2500032, "S2-AEATR-001:E09:2500032"))

    def test_wilson_bounds_and_center_behavior(self):
        lo, hi = analysis.wilson_interval(0, 96)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = analysis.wilson_interval(48, 96)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_exact_mcnemar_known_value(self):
        first = [1, 1, 1, 1, 1]
        reference = [0, 0, 0, 0, 0]
        self.assertAlmostEqual(analysis.exact_mcnemar_p(first, reference), 0.0625)

    def test_holm_step_down(self):
        adjusted = analysis.holm_adjust([0.01, 0.04, 0.03])
        self.assertEqual([round(v, 8) for v in adjusted], [0.03, 0.06, 0.06])

    def test_recovery_restricted_time_enforces_censor_contract(self):
        event = {
            "evidence_qualified_trusted_recovery": True,
            "time_to_recovery_right_censored": False,
            "time_to_evidence_qualified_trusted_recovery_s": 25.0,
        }
        self.assertEqual(analysis.recovery_restricted_time(event), 25.0)
        censored = {
            "evidence_qualified_trusted_recovery": False,
            "time_to_recovery_right_censored": True,
            "time_to_evidence_qualified_trusted_recovery_s": None,
        }
        self.assertEqual(analysis.recovery_restricted_time(censored), 240.0)
        inconsistent = {
            "evidence_qualified_trusted_recovery": False,
            "time_to_recovery_right_censored": False,
            "time_to_evidence_qualified_trusted_recovery_s": None,
        }
        with self.assertRaises(ValueError):
            analysis.recovery_restricted_time(inconsistent)

    def test_containment_null_is_right_censored_at_frozen_horizon(self):
        self.assertEqual(analysis.containment_restricted_time({"time_to_containment_s": None}), 240.0)
        self.assertEqual(analysis.containment_restricted_time({"time_to_containment_s": 10.0}), 10.0)
        with self.assertRaises(ValueError):
            analysis.containment_restricted_time({"time_to_containment_s": 241.0})

    def test_mean_ci_uses_sample_standard_deviation(self):
        mean, sd, lo, hi = analysis.mean_ci([1.0, 2.0, 3.0])
        self.assertEqual(mean, 2.0)
        self.assertAlmostEqual(sd, 1.0)
        self.assertLess(lo, mean)
        self.assertGreater(hi, mean)

    def test_normal_p_zero_variance_rules(self):
        self.assertEqual(analysis.normal_two_sided_p([0.0, 0.0]), 1.0)
        self.assertEqual(analysis.normal_two_sided_p([1.0, 1.0]), 0.0)

    def test_k0_k3_slope(self):
        self.assertAlmostEqual(analysis._trend_slope([0.0, 1.0, 2.0, 3.0]), 1.0)
        self.assertAlmostEqual(analysis._trend_slope([3.0, 2.0, 1.0, 0.0]), -1.0)


if __name__ == "__main__":
    unittest.main()
