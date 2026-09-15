from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import unittest

from study9_semantic.completions import PartialObservation, enumerate_admissible_states, reveal_values
from study9_semantic.contracts import REQUIRED_VARIABLES


class CompletionTests(unittest.TestCase):
    def test_two_unresolved_variables_produce_four_states(self):
        unresolved = ("security_signal", "authorization_available")
        known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        partial = PartialObservation.build(known=known, unresolved=unresolved)
        states = enumerate_admissible_states(partial)
        self.assertEqual(len(states), 4)
        self.assertEqual(
            {(row["security_signal"], row["authorization_available"]) for row in states},
            {(False, False), (False, True), (True, False), (True, True)},
        )

    def test_reveal_removes_exact_variable(self):
        unresolved = ("security_signal", "authorization_available")
        known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        partial = PartialObservation.build(known=known, unresolved=unresolved)
        reduced = reveal_values(partial, {"security_signal": False})
        self.assertEqual(reduced.unresolved, ("authorization_available",))
        self.assertFalse(reduced.known_dict()["security_signal"])

    def test_partial_must_partition_all_eight_variables(self):
        with self.assertRaises(ValueError):
            PartialObservation.build(known={"signature_valid": True}, unresolved=())


if __name__ == "__main__":
    unittest.main()
