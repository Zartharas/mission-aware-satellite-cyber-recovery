from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.canonical_engine import analysis_to_record, analyze_native_state_groups
from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import PRIMARY_POLICY_VALUES, REQUIRED_VARIABLES
from study9_semantic.state_groups import collapse_native_states


class CanonicalEngineTests(unittest.TestCase):
    def _synthetic_groups(self):
        unresolved = ("security_signal", "authorization_available")
        qualified_known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        partial = PartialObservation.build(known=qualified_known, unresolved=unresolved)
        complete = PartialObservation.build(
            known={
                "signature_valid": True,
                "source_trusted": True,
                "fresh": True,
                "epoch_valid": True,
                "contradictory": False,
                "minimum_evidence_complete": True,
                "security_signal": False,
                "authorization_available": True,
            },
            unresolved=(),
        )
        return collapse_native_states(
            "UNSW_IOTSAT_2026",
            [partial] * 7 + [complete] * 3,
            expected_row_count=10,
        )

    def test_weighted_unique_action_fractions_are_exact_per_policy(self):
        analysis = analyze_native_state_groups("UNSW_IOTSAT_2026", self._synthetic_groups())
        self.assertEqual(tuple(row.policy for row in analysis.policy_strata), PRIMARY_POLICY_VALUES)
        fractions = {
            row.policy: (row.unique_action_numerator, row.unique_action_denominator)
            for row in analysis.policy_strata
        }
        self.assertEqual(fractions["S2_B0_FAIL_CLOSED"], (10, 10))
        self.assertEqual(fractions["S2_B1_FAIL_OPERATIONAL"], (3, 10))
        self.assertEqual(fractions["S2_B2_RISK_THRESHOLD"], (3, 10))
        self.assertEqual(fractions["S2_S1_EVIDENCE_AWARE"], (3, 10))

    def test_guaranteed_sidecar_semantics_are_policy_stratified(self):
        analysis = analyze_native_state_groups("UNSW_IOTSAT_2026", self._synthetic_groups())
        by_policy = {row.policy: row for row in analysis.policy_strata}
        first_group = {policy: row.group_results[0] for policy, row in by_policy.items()}
        self.assertEqual(first_group["S2_B0_FAIL_CLOSED"].guaranteed_sidecar_cardinality, 0)
        self.assertEqual(
            first_group["S2_B1_FAIL_OPERATIONAL"].guaranteed_sidecar_sets,
            (("security_signal",),),
        )
        self.assertEqual(
            first_group["S2_B2_RISK_THRESHOLD"].guaranteed_sidecar_sets,
            (("security_signal",),),
        )
        self.assertEqual(
            first_group["S2_S1_EVIDENCE_AWARE"].guaranteed_sidecar_sets,
            (("security_signal", "authorization_available"),),
        )

    def test_analysis_record_preserves_integer_fraction_representation(self):
        record = analysis_to_record(
            analyze_native_state_groups("UNSW_IOTSAT_2026", self._synthetic_groups())
        )
        for stratum in record["policy_strata"]:
            fraction = stratum["unique_action_fraction"]
            self.assertIs(type(fraction["numerator"]), int)
            self.assertIs(type(fraction["denominator"]), int)
            self.assertEqual(fraction["denominator"], 10)

    def test_cross_dataset_group_is_rejected(self):
        groups = self._synthetic_groups()
        with self.assertRaises(ValueError):
            analyze_native_state_groups("CUCD_ID_V3", groups)


if __name__ == "__main__":
    unittest.main()
