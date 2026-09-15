from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import REQUIRED_VARIABLES, load_frozen_contracts
from study9_semantic.state_groups import collapse_native_states
from study9_semantic.state_projection import build_projection_plan, project_native_row


class StateGroupTests(unittest.TestCase):
    def test_identical_partial_states_collapse_with_exact_multiplicity(self):
        partial = PartialObservation.build(known={}, unresolved=REQUIRED_VARIABLES)
        groups = collapse_native_states(
            "CUCD_ID_V3",
            [partial, partial, partial],
            expected_row_count=3,
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].multiplicity, 3)
        self.assertEqual(sum(group.multiplicity for group in groups), 3)

    def test_unsw_prospective_ambiguity_collapses_to_one_unresolved_group(self):
        contracts = load_frozen_contracts(ROOT)
        plan = build_projection_plan("UNSW_IOTSAT_2026", contracts)
        rows = [
            {"Position_Anomaly": "0", "Attack_Flag": "0", "Satellite_ID": "A"},
            {"Position_Anomaly": "0", "Attack_Flag": "1", "Satellite_ID": "Z"},
            {"Position_Anomaly": "1", "Attack_Flag": "0", "Satellite_ID": "A"},
        ]
        partials = [project_native_row(plan, row) for row in rows]
        groups = collapse_native_states(
            "UNSW_IOTSAT_2026",
            partials,
            expected_row_count=3,
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].multiplicity, 3)
        self.assertEqual(dict(groups[0].known), {})
        self.assertEqual(groups[0].unresolved, REQUIRED_VARIABLES)

    def test_group_order_is_stable_false_before_true_for_synthetic_known_boolean(self):
        unresolved = tuple(name for name in REQUIRED_VARIABLES if name != "security_signal")
        true_partial = PartialObservation.build(
            known={"security_signal": True}, unresolved=unresolved
        )
        false_partial = PartialObservation.build(
            known={"security_signal": False}, unresolved=unresolved
        )
        groups = collapse_native_states(
            "UNSW_IOTSAT_2026",
            [true_partial, false_partial],
            expected_row_count=2,
        )
        self.assertEqual([dict(group.known)["security_signal"] for group in groups], [False, True])

    def test_multiplicity_conservation_fails_closed(self):
        partial = PartialObservation.build(known={}, unresolved=REQUIRED_VARIABLES)
        with self.assertRaises(ValueError):
            collapse_native_states(
                "AEGISSAT_2025",
                [partial, partial],
                expected_row_count=3,
            )

    def test_unknown_dataset_is_rejected(self):
        partial = PartialObservation.build(known={}, unresolved=REQUIRED_VARIABLES)
        with self.assertRaises(ValueError):
            collapse_native_states("NOT_A_DATASET", [partial], expected_row_count=1)


if __name__ == "__main__":
    unittest.main()
