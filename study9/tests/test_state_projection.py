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

    def test_cucd_and_aegissat_leave_all_eight_variables_unresolved(self):
        for dataset_id, row in (
            ("CUCD_ID_V3", {"Label": "4", "SequenceCount": "7"}),
            (
                "AEGISSAT_2025",
                {"attacks.cpuhightarget.target": "OBC", "command": "PING"},
            ),
        ):
            plan = build_projection_plan(dataset_id, self.contracts)
            partial = project_native_row(plan, row)
            self.assertEqual(partial.known, ())
            self.assertEqual(partial.unresolved, REQUIRED_VARIABLES)

    def test_unsw_position_anomaly_is_the_only_known_primary_state(self):
        plan = build_projection_plan("UNSW_IOTSAT_2026", self.contracts)
        false_row = {
            "Position_Anomaly": "0",
            "Attack_Flag": "1",
            "Attack_Type": "spoofing",
            "RF_CRC_Errors": "99",
        }
        true_row = {**false_row, "Position_Anomaly": "1", "Attack_Flag": "0"}
        false_partial = project_native_row(plan, false_row)
        true_partial = project_native_row(plan, true_row)
        self.assertEqual(false_partial.known_dict(), {"security_signal": False})
        self.assertEqual(true_partial.known_dict(), {"security_signal": True})
        self.assertNotIn("security_signal", false_partial.unresolved)
        self.assertEqual(len(false_partial.unresolved), 7)

    def test_labels_and_ambiguous_fields_cannot_change_projection(self):
        plan = build_projection_plan("UNSW_IOTSAT_2026", self.contracts)
        first = project_native_row(
            plan,
            {
                "Position_Anomaly": "1",
                "Attack_Flag": "0",
                "Attack_Type": "none",
                "Satellite_ID": "SAT-A",
                "Timestamp": "1",
            },
        )
        second = project_native_row(
            plan,
            {
                "Position_Anomaly": "1",
                "Attack_Flag": "1",
                "Attack_Type": "attack",
                "Satellite_ID": "SAT-Z",
                "Timestamp": "999999",
            },
        )
        self.assertEqual(first, second)

    def test_unsw_missing_direct_field_fails_closed(self):
        plan = build_projection_plan("UNSW_IOTSAT_2026", self.contracts)
        with self.assertRaises(StateProjectionError):
            project_native_row(plan, {"Attack_Flag": "1"})

    def test_binary_numeric_normalization_is_strict(self):
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
