from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import unittest
from unittest.mock import patch

from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import REQUIRED_VARIABLES
from study9_semantic.selector_adapter import selector_types
from study9_semantic.sidecar import (
    action_set_cardinality,
    guaranteed_minimal_sidecar_sets,
    minimal_sidecar_sets,
    reachable_actions,
)


class SidecarTests(unittest.TestCase):
    def _qualified_partial(self):
        unresolved = ("security_signal", "authorization_available")
        known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        return PartialObservation.build(known=known, unresolved=unresolved)

    def test_evidence_aware_action_set_is_ambiguous_before_revelation(self):
        Study2Policy, _, _ = selector_types()
        partial = self._qualified_partial()
        actions = reachable_actions(Study2Policy.EVIDENCE_AWARE, partial)
        self.assertEqual(
            actions,
            frozenset({"PROCEED_TO_RECOVERY_GATE", "RESTRICT_AND_REQUEST_AUTHORIZATION"}),
        )
        self.assertEqual(action_set_cardinality(Study2Policy.EVIDENCE_AWARE, partial), 2)

    def test_minimal_sidecar_retains_tied_singletons(self):
        Study2Policy, _, _ = selector_types()
        partial = self._qualified_partial()
        winners = minimal_sidecar_sets(
            Study2Policy.EVIDENCE_AWARE,
            partial,
            {"security_signal": False, "authorization_available": True},
        )
        self.assertEqual(
            winners,
            (("security_signal",), ("authorization_available",)),
        )

    def test_guaranteed_sidecar_requires_both_for_every_possible_assignment(self):
        Study2Policy, _, _ = selector_types()
        partial = self._qualified_partial()
        self.assertEqual(
            guaranteed_minimal_sidecar_sets(Study2Policy.EVIDENCE_AWARE, partial),
            (("security_signal", "authorization_available"),),
        )

    def test_guaranteed_sidecar_is_stricter_than_assignment_conditioned_helper(self):
        Study2Policy, _, _ = selector_types()
        partial = self._qualified_partial()
        assignment_conditioned = minimal_sidecar_sets(
            Study2Policy.EVIDENCE_AWARE,
            partial,
            {"security_signal": False, "authorization_available": True},
        )
        guaranteed = guaranteed_minimal_sidecar_sets(Study2Policy.EVIDENCE_AWARE, partial)
        self.assertEqual(
            assignment_conditioned,
            (("security_signal",), ("authorization_available",)),
        )
        self.assertEqual(
            guaranteed,
            (("security_signal", "authorization_available"),),
        )

    def test_guaranteed_sidecar_can_be_empty_when_action_is_already_unique(self):
        Study2Policy, _, _ = selector_types()
        unresolved = ("authorization_available",)
        known = {
            name: (False if name in ("contradictory", "security_signal") else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        partial = PartialObservation.build(known=known, unresolved=unresolved)
        self.assertEqual(
            guaranteed_minimal_sidecar_sets(Study2Policy.EVIDENCE_AWARE, partial),
            ((),),
        )

    def test_guaranteed_sidecar_retains_all_minimum_cardinality_ties(self):
        Study2Policy, _, _ = selector_types()
        partial = self._qualified_partial()

        def fake_cardinality(_policy, candidate):
            return 2 if len(candidate.unresolved) == 2 else 1

        with patch(
            "study9_semantic.sidecar.action_set_cardinality",
            side_effect=fake_cardinality,
        ):
            self.assertEqual(
                guaranteed_minimal_sidecar_sets(Study2Policy.EVIDENCE_AWARE, partial),
                (("security_signal",), ("authorization_available",)),
            )


if __name__ == "__main__":
    unittest.main()
