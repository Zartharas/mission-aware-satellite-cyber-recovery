from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import unittest
from unittest.mock import patch

from study9_semantic.canonical_engine import analysis_to_record, analyze_native_state_groups
from study9_semantic.canonical_runner import _mapping_and_coverage
from study9_semantic.completions import PartialObservation
from study9_semantic.contracts import REQUIRED_VARIABLES, load_frozen_contracts
from study9_semantic.independent_audit import (
    audit_analyze_native_state_groups,
    audit_collapse_native_states,
    audit_guaranteed_minimal_sidecar_sets,
    audit_mapping_and_coverage,
    audit_minimal_sidecar_sets,
    audit_project_native_row,
    audit_reachable_actions,
)
from study9_semantic.selector_adapter import selector_types
from study9_semantic.sidecar import (
    guaranteed_minimal_sidecar_sets,
    minimal_sidecar_sets,
    reachable_actions,
)
from study9_semantic.state_groups import collapse_native_states
from study9_semantic.state_projection import build_projection_plan, project_native_row


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

    def _finite_population(self):
        unresolved = ("security_signal", "authorization_available")
        qualified_known = {
            name: (False if name == "contradictory" else True)
            for name in REQUIRED_VARIABLES
            if name not in unresolved
        }
        ambiguous = PartialObservation.build(known=qualified_known, unresolved=unresolved)
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
        return [ambiguous] * 5 + [complete] * 2

    def test_independent_grouping_matches_canonical_exact_multiplicities(self):
        partials = self._finite_population()
        canonical = collapse_native_states(
            "UNSW_IOTSAT_2026", partials, expected_row_count=7
        )
        audit = audit_collapse_native_states(
            "UNSW_IOTSAT_2026", partials, expected_row_count=7
        )
        canonical_signature = tuple(
            (group.dataset_id, group.known, group.unresolved, group.multiplicity)
            for group in canonical
        )
        audit_signature = tuple(
            (
                row["dataset_id"],
                row["known"],
                row["unresolved"],
                row["multiplicity"],
            )
            for row in audit
        )
        self.assertEqual(canonical_signature, audit_signature)

    def test_independent_policy_endpoint_summary_matches_canonical(self):
        partials = self._finite_population()
        canonical_groups = collapse_native_states(
            "UNSW_IOTSAT_2026", partials, expected_row_count=7
        )
        audit_groups = audit_collapse_native_states(
            "UNSW_IOTSAT_2026", partials, expected_row_count=7
        )
        canonical = analysis_to_record(
            analyze_native_state_groups("UNSW_IOTSAT_2026", canonical_groups)
        )
        audit = audit_analyze_native_state_groups("UNSW_IOTSAT_2026", audit_groups)
        self.assertEqual(canonical["policy_strata"], audit["policy_strata"])

    def test_independent_raw_row_projection_matches_canonical_frozen_rule(self):
        contracts = load_frozen_contracts(ROOT)
        plan = build_projection_plan("UNSW_IOTSAT_2026", contracts)
        for value, expected in (("0", False), ("1", True), ("0.0", False), ("1.000", True)):
            row = {"Position_Anomaly": value, "Attack_Flag": "1"}
            canonical = project_native_row(plan, row)
            audit = audit_project_native_row("UNSW_IOTSAT_2026", row, contracts)
            self.assertEqual(canonical, audit)
            self.assertEqual(audit.known_dict()["security_signal"], expected)

    def test_corrupted_canonical_projector_is_detectably_independent(self):
        contracts = load_frozen_contracts(ROOT)
        plan = build_projection_plan("UNSW_IOTSAT_2026", contracts)
        row = {"Position_Anomaly": "0", "Attack_Flag": "1"}
        audit = audit_project_native_row("UNSW_IOTSAT_2026", row, contracts)
        with patch("study9_semantic.state_projection.normalize_binary_numeric", return_value=True):
            corrupted = project_native_row(plan, row)
        self.assertNotEqual(corrupted, audit)
        self.assertTrue(corrupted.known_dict()["security_signal"])
        self.assertFalse(audit.known_dict()["security_signal"])

    def test_independent_policy_independent_mapping_and_coverage_matches_canonical(self):
        contracts = load_frozen_contracts(ROOT)
        canonical_mapping, canonical_coverage = _mapping_and_coverage(contracts)
        audit_mapping, audit_coverage = audit_mapping_and_coverage(contracts)
        self.assertEqual(canonical_mapping, audit_mapping)
        self.assertEqual(canonical_coverage, audit_coverage)
        by_id = {row["dataset_id"]: row for row in audit_coverage["per_dataset"]}
        self.assertEqual(by_id["CUCD_ID_V3"]["operational_direct_coverage"], {"numerator": 0, "denominator": 8})
        self.assertEqual(by_id["AEGISSAT_2025"]["operational_direct_coverage"], {"numerator": 0, "denominator": 8})
        self.assertEqual(by_id["UNSW_IOTSAT_2026"]["operational_direct_coverage"], {"numerator": 1, "denominator": 8})


if __name__ == "__main__":
    unittest.main()
