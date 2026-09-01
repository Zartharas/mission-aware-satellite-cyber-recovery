import unittest

from study2_security.evidence import EvidenceCondition
from study2_security.protocol import AdversaryBudget, AdversaryClass, ContactRegime, validate_treatment_budget


class ProtocolTests(unittest.TestCase):
    def test_a0_has_no_compromised_source(self):
        AdversaryBudget(AdversaryClass.A0).validate(contact_regime=ContactRegime.K0)

    def test_a2_requires_contact_unavailability(self):
        with self.assertRaises(ValueError):
            AdversaryBudget(AdversaryClass.A2, ("source-a",)).validate(contact_regime=ContactRegime.K0)

    def test_a3_retains_independent_trust_anchor(self):
        with self.assertRaises(ValueError):
            AdversaryBudget(AdversaryClass.A3, ("source-a", "verifier-root")).validate(contact_regime=ContactRegime.K2)

    def test_v4_requires_nonzero_adversary_budget(self):
        with self.assertRaises(ValueError):
            validate_treatment_budget(EvidenceCondition.MANIPULATED, AdversaryBudget(AdversaryClass.A0), contact_regime=ContactRegime.K0)

    def test_budget_cannot_read_ground_truth(self):
        with self.assertRaises(ValueError):
            AdversaryBudget(AdversaryClass.A1, ("source-a",), may_read_ground_truth=True).validate(contact_regime=ContactRegime.K0)


if __name__ == "__main__":
    unittest.main()
