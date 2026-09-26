from __future__ import annotations

import unittest

from study6x.src.invariant_oracle import adjudicate, expected_cases


class InvariantOracleTests(unittest.TestCase):
    def test_frozen_truth_table(self) -> None:
        expected = {
            ("GT", -1, 0): False,
            ("GT", 0, 0): False,
            ("GT", 1, 0): True,
            ("GE", -1, 0): False,
            ("GE", 0, 0): True,
            ("GE", 1, 0): True,
        }
        self.assertEqual(expected_cases(), expected)
        for key, value in expected.items():
            self.assertIs(adjudicate(*key), value)

    def test_unfrozen_case_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            adjudicate("GT", 2, 0)

    def test_operator_drift_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            adjudicate("LT", -1, 0)


if __name__ == "__main__":
    unittest.main()
