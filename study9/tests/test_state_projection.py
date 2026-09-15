from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.contracts import REQUIRED_VARIABLES, load_frozen_contracts
from study9_semantic.state_projection import (
    StateProjectionError,
    build_projection_plan,
    normalize_binary_numeric,
    project_native_row,
)


class StateProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = load_frozen_contracts(ROOT)

    def test_all_three_datasets_leave_all_eight_variables_unresolved(self):
        fixtures = (
            ("CUCD_ID_V3", {"Label": "4", "SequenceCount": "7"}),
            (
                "AEGISSAT_2025",
                {"attacks.cpuhightarget.target": "OBC", "command": "PING"},
            ),
            (
                "UNSW_IOTSAT_2026",
                {
                    "Position_Anomaly": "-29.16",
                    "Attack_Flag": "1",
                    "Speed_ms": "-21.53",
                },
            ),
        )
        for dataset_id, row in fixtures:
            plan = build_projection_plan(dataset_id, self.contracts)
            partial = project_native_row(plan, row)
            self.assertEqual(partial.known, ())
            self.assertEqual(partial.unresolved, REQUIRED_VARIABLES)

    def test_unsw_position_anomaly_labels_and_neighboring_fields_cannot_change_projection(self):
        plan = build_projection_plan("UNSW_IOTSAT_2026", self.contracts)
        rows = (
            {
                "Position_Anomaly": "0",
                "Attack_Flag": "0",
                "Attack_Type": "none",
                "Speed_ms": "0",
            },
            {
                "Position_Anomaly": "1",
                "Attack_Flag": "1",
                "Attack_Type": "spoofing",
                "Speed_ms": "15000",
            },
            {
                "Position_Anomaly": "-29.16",
                "Attack_Flag": "1",
                "Distance_From_Origin": "25.0",
                "Vertical_Category": "66.76",
            },
            {},
        )
        projected = tuple(project_native_row(plan, row) for row in rows)
        self.assertTrue(all(item == projected[0] for item in projected))
        self.assertEqual(projected[0].known, ())
        self.assertEqual(projected[0].unresolved, REQUIRED_VARIABLES)

    def test_unsw_no_direct_field_is_required_after_domain_deviation(self):
        plan = build_projection_plan("UNSW_IOTSAT_2026", self.contracts)
        partial = project_native_row(plan, {"Attack_Flag": "1"})
        self.assertEqual(partial.known, ())
        self.assertEqual(partial.unresolved, REQUIRED_VARIABLES)

    def test_binary_numeric_normalization_remains_strict_utility(self):
        self.assertFalse(normalize_binary_numeric("0"))
        self.assertFalse(normalize_binary_numeric("0.0"))
        self.assertTrue(normalize_binary_numeric("1"))
        self.assertTrue(normalize_binary_numeric("1.000"))
        for bad in ("", "true", "2", "-1", "NaN", "Infinity", True):
            with self.subTest(value=bad):
                with self.assertRaises(StateProjectionError):
                    normalize_binary_numeric(bad)


if __name__ == "__main__":
    unittest.main()
