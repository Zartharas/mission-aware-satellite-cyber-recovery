import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from study2_security.evidence import EvidenceClaim, EvidenceCondition, sign_claim, verify_bundle
from study2_security.protocol import AdversaryBudget, AdversaryClass, ContactRegime, ScenarioIdentity
from study2_security.treatments import apply_treatment


class TreatmentTests(unittest.TestCase):
    def setUp(self):
        self.keys = {
            "source-a": Ed25519PrivateKey.generate(),
            "source-b": Ed25519PrivateKey.generate(),
        }
        claim = EvidenceClaim(
            "source-a",
            "sat-1",
            "authorization_valid",
            True,
            7,
            5,
            990.0,
            20.0,
            "fixture",
        )
        self.bundle = (sign_claim(claim, self.keys["source-a"]),)

    def scenario(
        self,
        condition,
        adversary=AdversaryClass.A0,
        contact=ContactRegime.K0,
    ):
        return ScenarioIdentity(
            "S2",
            "SC-001",
            900001,
            f"T-{condition.value}",
            condition,
            adversary,
            contact,
            "gt-fixed",
            "prov-fixed",
            "analysis-fixed",
        )

    def test_v0_is_identity_preserving(self):
        s = self.scenario(EvidenceCondition.CURRENT)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A0),
            private_keys=self.keys,
        )
        self.assertEqual(result.scenario, s)
        self.assertEqual(result.evidence, self.bundle)

    def test_v1_omits_claim_without_mutating_identity(self):
        s = self.scenario(EvidenceCondition.OMITTED)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A0),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
        )
        self.assertEqual(result.evidence, ())
        self.assertEqual(result.scenario.ground_truth_token, "gt-fixed")
        self.assertEqual(result.scenario.seed, 900001)

    def test_budget_class_must_match_frozen_scenario_identity(self):
        s = self.scenario(EvidenceCondition.PARTIAL_COMPROMISE, AdversaryClass.A1)
        with self.assertRaisesRegex(ValueError, "must match frozen scenario"):
            apply_treatment(
                s,
                self.bundle,
                budget=AdversaryBudget(
                    AdversaryClass.A3,
                    ("source-a", "source-b"),
                ),
                private_keys=self.keys,
                target_source="source-a",
                target_key="authorization_valid",
            )

    def test_v2_stale_is_signed_but_not_accepted(self):
        s = self.scenario(EvidenceCondition.STALE_OR_REPLAYED)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A0),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
            now_s=1000.0,
        )
        checked = verify_bundle(
            result.evidence,
            public_keys={k: v.public_key() for k, v in self.keys.items()},
            trusted_sources={"source-a"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertFalse(checked.verifications[0].accepted)
        self.assertIn("stale_or_future_evidence", checked.verifications[0].reasons)

    def test_v2_stale_rejects_clock_that_cannot_represent_expiry(self):
        s = self.scenario(EvidenceCondition.STALE_OR_REPLAYED)
        with self.assertRaisesRegex(ValueError, "beyond the claim validity duration"):
            apply_treatment(
                s,
                self.bundle,
                budget=AdversaryBudget(AdversaryClass.A0),
                private_keys=self.keys,
                target_source="source-a",
                target_key="authorization_valid",
                now_s=10.0,
            )

    def test_v3_creates_accepted_contradiction(self):
        s = self.scenario(EvidenceCondition.CONTRADICTORY)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A0),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
            alternate_source="source-b",
        )
        checked = verify_bundle(
            result.evidence,
            public_keys={k: v.public_key() for k, v in self.keys.items()},
            trusted_sources={"source-a", "source-b"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertEqual(len(checked.contradictions), 1)
        self.assertNotIn(
            "authorization_valid",
            checked.current_values(subject_id="sat-1"),
        )

    def test_v3_sequence_is_above_alternate_source_epoch_maximum(self):
        existing = EvidenceClaim(
            "source-b",
            "sat-1",
            "health_checks_passed",
            True,
            7,
            6,
            990.0,
            20.0,
            "fixture-b",
        )
        bundle = (*self.bundle, sign_claim(existing, self.keys["source-b"]))
        s = self.scenario(EvidenceCondition.CONTRADICTORY)
        result = apply_treatment(
            s,
            bundle,
            budget=AdversaryBudget(AdversaryClass.A0),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
            alternate_source="source-b",
        )
        conflict = result.evidence[-1]
        self.assertEqual(conflict.claim.source_id, "source-b")
        self.assertEqual(conflict.claim.sequence, 7)
        checked = verify_bundle(
            result.evidence,
            public_keys={k: v.public_key() for k, v in self.keys.items()},
            trusted_sources={"source-a", "source-b"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertNotIn(
            "duplicate_sequence_in_bundle",
            conflict_verification.reasons
            if (conflict_verification := checked.verifications[-1])
            else (),
        )
        self.assertEqual(len(checked.contradictions), 1)

    def test_v4_tamper_breaks_signature(self):
        s = self.scenario(EvidenceCondition.MANIPULATED, AdversaryClass.A1)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A1, ("source-a",)),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
        )
        checked = verify_bundle(
            result.evidence,
            public_keys={"source-a": self.keys["source-a"].public_key()},
            trusted_sources={"source-a"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertFalse(checked.verifications[0].signature_valid)

    def test_v5_valid_signature_does_not_imply_correctness(self):
        s = self.scenario(EvidenceCondition.PARTIAL_COMPROMISE, AdversaryClass.A1)
        result = apply_treatment(
            s,
            self.bundle,
            budget=AdversaryBudget(AdversaryClass.A1, ("source-a",)),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
        )
        checked = verify_bundle(
            result.evidence,
            public_keys={"source-a": self.keys["source-a"].public_key()},
            trusted_sources={"source-a"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertTrue(checked.verifications[0].signature_valid)
        self.assertFalse(
            checked.current_values(subject_id="sat-1")["authorization_valid"]
        )

    def test_v5_sequence_is_above_compromised_source_epoch_maximum(self):
        existing = EvidenceClaim(
            "source-a",
            "sat-1",
            "health_checks_passed",
            True,
            7,
            6,
            990.0,
            20.0,
            "fixture-a2",
        )
        bundle = (*self.bundle, sign_claim(existing, self.keys["source-a"]))
        s = self.scenario(EvidenceCondition.PARTIAL_COMPROMISE, AdversaryClass.A1)
        result = apply_treatment(
            s,
            bundle,
            budget=AdversaryBudget(AdversaryClass.A1, ("source-a",)),
            private_keys=self.keys,
            target_source="source-a",
            target_key="authorization_valid",
        )
        forged = result.evidence[0]
        self.assertEqual(forged.claim.sequence, 7)
        checked = verify_bundle(
            result.evidence,
            public_keys={"source-a": self.keys["source-a"].public_key()},
            trusted_sources={"source-a"},
            now_s=1000.0,
            expected_epoch_by_subject={"sat-1": 7},
        )
        self.assertNotIn(
            "duplicate_sequence_in_bundle",
            checked.verifications[0].reasons,
        )


if __name__ == "__main__":
    unittest.main()
