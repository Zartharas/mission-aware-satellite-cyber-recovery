import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from study2_security.ambiguity import matched_pair, policy_visible_fingerprint
from study2_security.evidence import EvidenceClaim, sign_claim
from study2_security.protocol import CauseClass


class AmbiguityTests(unittest.TestCase):
    def test_hidden_cause_is_not_in_policy_visible_fingerprint(self):
        key = Ed25519PrivateKey.generate()
        evidence = (sign_claim(EvidenceClaim("source-a", "sat-1", "telemetry_restored", True, 1, 1, 10.0, 30.0, "fixture"), key),)
        benign, adversarial = matched_pair("AMB-TELEMETRY-LOSS", evidence)
        self.assertEqual(benign.cause, CauseClass.BENIGN)
        self.assertEqual(adversarial.cause, CauseClass.ADVERSARIAL)
        self.assertNotEqual(benign.hidden_cause_token, adversarial.hidden_cause_token)
        self.assertEqual(policy_visible_fingerprint(benign), policy_visible_fingerprint(adversarial))


if __name__ == "__main__":
    unittest.main()
