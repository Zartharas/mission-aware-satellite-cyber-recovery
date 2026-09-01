import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from study2_security.evidence import (
    EvidenceClaim,
    SignedEvidence,
    sign_claim,
    verify_bundle,
)


class EvidenceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.key_a = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
        self.key_b = Ed25519PrivateKey.from_private_bytes(bytes(range(33, 65)))
        self.public = {
            "sensor-a": self.key_a.public_key(),
            "sensor-b": self.key_b.public_key(),
        }

    def claim(self, source, key, value, sequence=1, issued=10.0, valid=20.0):
        return EvidenceClaim(
            source_id=source,
            subject_id="sat-1",
            key=key,
            value=value,
            epoch=1,
            sequence=sequence,
            issued_at_s=issued,
            valid_for_s=valid,
            provenance="synthetic-study2-fixture",
        )

    def test_current_signed_evidence_is_accepted(self):
        signed = sign_claim(self.claim("sensor-a", "integrity", True), self.key_a)
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a", "sensor-b"},
            now_s=15.0,
        )
        self.assertEqual(len(result.accepted), 1)
        self.assertFalse(result.contradictions)

    def test_tampering_after_signature_is_rejected(self):
        signed = sign_claim(self.claim("sensor-a", "integrity", True), self.key_a)
        tampered = SignedEvidence(
            claim=self.claim("sensor-a", "integrity", False),
            signature_b64=signed.signature_b64,
        )
        result = verify_bundle(
            [tampered],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertIn("invalid_signature", result.rejected[0].reasons)

    def test_stale_evidence_is_not_decision_eligible(self):
        signed = sign_claim(
            self.claim("sensor-a", "integrity", True, valid=2.0), self.key_a
        )
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
        )
        self.assertIn("stale_or_future_evidence", result.rejected[0].reasons)

    def test_replayed_sequence_is_rejected(self):
        signed = sign_claim(
            self.claim("sensor-a", "integrity", True, sequence=4), self.key_a
        )
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
            minimum_sequence_by_source_epoch={("sensor-a", 1): 4},
        )
        self.assertIn(
            "replayed_or_rolled_back_sequence", result.rejected[0].reasons
        )

    def test_valid_signature_from_untrusted_source_is_not_accepted(self):
        signed = sign_claim(self.claim("sensor-b", "integrity", True), self.key_b)
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
        )
        self.assertIn("untrusted_source", result.rejected[0].reasons)

    def test_conflicting_trusted_sources_create_contradiction(self):
        first = sign_claim(self.claim("sensor-a", "approved", True), self.key_a)
        second = sign_claim(self.claim("sensor-b", "approved", False), self.key_b)
        result = verify_bundle(
            [first, second],
            public_keys=self.public,
            trusted_sources={"sensor-a", "sensor-b"},
            now_s=15.0,
        )
        self.assertEqual(
            result.contradiction_keys(subject_id="sat-1"), ("approved",)
        )
        self.assertEqual(result.current_values(subject_id="sat-1"), {})

    def test_duplicate_sequence_in_same_source_bundle_is_rejected(self):
        first = sign_claim(
            self.claim("sensor-a", "integrity", True, sequence=9), self.key_a
        )
        second = sign_claim(
            self.claim("sensor-a", "approved", True, sequence=9), self.key_a
        )
        result = verify_bundle(
            [first, second],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertTrue(
            all(
                "duplicate_sequence_in_bundle" in row.reasons
                for row in result.rejected
            )
        )

    def test_wrong_recovery_epoch_is_rejected(self):
        signed = sign_claim(
            self.claim("sensor-a", "integrity", True, sequence=5), self.key_a
        )
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
            expected_epoch_by_subject={"sat-1": 2},
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertIn("wrong_evidence_epoch", result.rejected[0].reasons)

    def test_malformed_signature_encoding_is_rejected(self):
        signed = SignedEvidence(
            claim=self.claim("sensor-a", "integrity", True),
            signature_b64="%%%not-base64%%%",
        )
        result = verify_bundle(
            [signed],
            public_keys=self.public,
            trusted_sources={"sensor-a"},
            now_s=15.0,
        )
        self.assertIn("invalid_signature", result.rejected[0].reasons)


if __name__ == "__main__":
    unittest.main()
