from __future__ import annotations

import unittest

from study6.src.artifact_trust_model import GATES, SIGNALS, adversarial_rows, baseline_states, benign_unavailability_rows, qualify


class Study6ArtifactTrustTests(unittest.TestCase):
    def setUp(self) -> None:
        self.states = {state.state_id: state for state in baseline_states()}

    def test_exact_population(self) -> None:
        self.assertEqual(len(adversarial_rows()), 36)
        self.assertEqual(len(benign_unavailability_rows()), 384)
        self.assertEqual(len(GATES), 6)
        self.assertEqual(len(SIGNALS), 6)

    def test_clean_approved_qualifies_every_gate(self) -> None:
        clean = self.states["CLEAN_APPROVED"]
        for gate_id in GATES:
            self.assertTrue(qualify(clean, gate_id), gate_id)

    def test_signature_only_rejects_post_release_tamper_but_accepts_validly_signed_bad_states(self) -> None:
        self.assertFalse(qualify(self.states["POST_RELEASE_TAMPER"], "G0_SIGNATURE_ONLY"))
        for state_id in ("TRUSTED_SIGNER_COMPROMISE", "TRUSTED_BUILDER_COMPROMISE", "SOURCE_REVIEW_BYPASS", "APPROVED_BAD_SOURCE"):
            self.assertTrue(qualify(self.states[state_id], "G0_SIGNATURE_ONLY"), state_id)

    def test_reproduced_build_detects_builder_compromise_but_not_bad_source(self) -> None:
        self.assertFalse(qualify(self.states["TRUSTED_BUILDER_COMPROMISE"], "G3_PROVENANCE_REPRODUCED_BUILD"))
        self.assertTrue(qualify(self.states["APPROVED_BAD_SOURCE"], "G3_PROVENANCE_REPRODUCED_BUILD"))

    def test_source_review_detects_review_bypass_but_not_bad_source(self) -> None:
        self.assertFalse(qualify(self.states["SOURCE_REVIEW_BYPASS"], "G4_PROVENANCE_SOURCE_REVIEW"))
        self.assertTrue(qualify(self.states["APPROVED_BAD_SOURCE"], "G4_PROVENANCE_SOURCE_REVIEW"))

    def test_composite_still_accepts_fully_approved_bad_source(self) -> None:
        bad = self.states["APPROVED_BAD_SOURCE"]
        self.assertTrue(qualify(bad, "G5_COMPOSITE"))
        self.assertFalse(bad.objective_baseline_correct)

    def test_objective_correctness_is_not_a_gate_signal(self) -> None:
        for required in GATES.values():
            self.assertNotIn("objective_baseline_correct", required)

    def test_benign_unavailability_has_one_row_per_subset_gate(self) -> None:
        rows = benign_unavailability_rows()
        keys = {(row["missing_signals"], row["gate_id"]) for row in rows}
        self.assertEqual(len(keys), 384)


if __name__ == "__main__":
    unittest.main()
