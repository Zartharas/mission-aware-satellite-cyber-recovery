import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from study2_security.evidence import EvidenceClaim, sign_claim, verify_bundle
from study2_security.recovery_gate import evaluate_trusted_recovery_gate


class RecoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.key = Ed25519PrivateKey.from_private_bytes(bytes(range(65, 97)))
        self.public = {"verifier": self.key.public_key()}

    def signed(self, key, value=True, sequence=1):
        claim = EvidenceClaim(
            source_id="verifier",
            subject_id="sat-1",
            key=key,
            value=value,
            epoch=2,
            sequence=sequence,
            issued_at_s=100.0,
            valid_for_s=30.0,
            provenance="synthetic-study2-recovery",
        )
        return sign_claim(claim, self.key)

    def attest(self, rows, now=110.0):
        return verify_bundle(
            rows,
            public_keys=self.public,
            trusted_sources={"verifier"},
            now_s=now,
            expected_epoch_by_subject={"sat-1": 2},
        )

    def test_all_applicable_current_evidence_allows_trusted_recovery(self):
        applicable = (
            "approved_version",
            "integrity_measurement_valid",
            "authorization_valid",
            "no_residual_unauthorized_state",
        )
        attestation = self.attest(
            [self.signed(key, sequence=i + 1) for i, key in enumerate(applicable)]
        )
        decision = evaluate_trusted_recovery_gate(
            attestation,
            subject_id="sat-1",
            applicable_criteria=applicable,
            residual_unauthorized_state=False,
        )
        self.assertTrue(decision.trusted_recovery_allowed)

    def test_missing_evidence_fails_closed(self):
        applicable = ("approved_version", "integrity_measurement_valid")
        attestation = self.attest([self.signed("approved_version")])
        decision = evaluate_trusted_recovery_gate(
            attestation,
            subject_id="sat-1",
            applicable_criteria=applicable,
            residual_unauthorized_state=False,
        )
        self.assertFalse(decision.trusted_recovery_allowed)

    def test_residual_unauthorized_state_blocks_trusted_recovery(self):
        applicable = ("approved_version",)
        attestation = self.attest([self.signed("approved_version")])
        decision = evaluate_trusted_recovery_gate(
            attestation,
            subject_id="sat-1",
            applicable_criteria=applicable,
            residual_unauthorized_state=True,
        )
        self.assertFalse(decision.trusted_recovery_allowed)
        self.assertIn("residual_unauthorized_state", decision.reasons)

    def test_false_criterion_blocks_trusted_recovery(self):
        applicable = ("approved_version",)
        attestation = self.attest([self.signed("approved_version", False)])
        decision = evaluate_trusted_recovery_gate(
            attestation,
            subject_id="sat-1",
            applicable_criteria=applicable,
            residual_unauthorized_state=False,
        )
        self.assertFalse(decision.trusted_recovery_allowed)


if __name__ == "__main__":
    unittest.main()
