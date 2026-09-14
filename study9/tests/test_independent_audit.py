from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import unittest

from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import REQUIRED_VARIABLES
from study9_semantic.independent_audit import (
    audit_guaranteed_minimal_sidecar_sets,
    audit_minimal_sidecar_sets,
    audit_reachable_actions,
)
from study9_semantic.selector_adapter import selector_types
from study9_semantic.sidecar import (
    guaranteed_minimal_sidecar_sets,
    minimal_sidecar_sets,
    reachable_actions,
)


class IndependentAuditTests(unittest.TestCase):
    def test_independent_completion_path_matches_canonical_on_synthetic_fixtures(self):
        Study2Policy, _, _ = selector_types()
        fixtures = [
            ("security_signal",),
            ("fresh", "security_signal"),
            ("source_trusted", "contradictory", "authorization_available"),
        ]
        for unresolved in fixtures:
            known = {
                name: (False if name == "contradictory" else True)
                for name in REQUIRED_VARIABLES
                if name not in unresolved
            }
            partial = PartialObservation.build(known=known, unresolved=unresolved)
            for policy in Study2Policy:
                self.assertEqual(
                    reachable_actions(policy, partial),
                    audit_reachable_actions(policy, known=known, unresolved=tuple(unresolved)),
                )

    def test_independent_minimal_sidecar_matches_canonical(self):
        Study2Policy, _, _ = selector_types()
        unresolved = ("security_signal", "authorization_available")
        known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        actual = {"security_signal": False, "authorization_available": True}
        partial = PartialObservation.build(known=known, unresolved=unresolved)
        self.assertEqual(
            minimal_sidecar_sets(Study2Policy.EVIDENCE_AWARE, partial, actual),
            audit_minimal_sidecar_sets(
                Study2Policy.EVIDENCE_AWARE,
                known=known,
                unresolved=unresolved,
                actual_unresolved_values=actual,
            ),
        )

    def test_independent_guaranteed_sidecar_matches_canonical(self):
        Study2Policy, _, _ = selector_types()
        fixtures = [
            ("security_signal", "authorization_available"),
            ("fresh", "security_signal", "authorization_available"),
            ("signature_valid", "source_trusted", "fresh"),
        ]
        for unresolved in fixtures:
            known = {
                name: (False if name == "contradictory" else True)
                for name in REQUIRED_VARIABLES
                if name not in unresolved
            }
            partial = PartialObservation.build(known=known, unresolved=unresolved)
            for policy in Study2Policy:
                self.assertEqual(
                    guaranteed_minimal_sidecar_sets(policy, partial),
                    audit_guaranteed_minimal_sidecar_sets(
                        policy,
                        known=known,
                        unresolved=tuple(unresolved),
                    ),
                )


if __name__ == "__main__":
    unittest.main()
