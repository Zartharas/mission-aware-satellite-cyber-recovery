import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hypothesis import given, settings, strategies as st

from study2_security.evidence import EvidenceClaim, EvidenceCondition, sign_claim
from study2_security.protocol import AdversaryBudget, AdversaryClass, ContactRegime, ScenarioIdentity
from study2_security.treatments import apply_treatment


KEY_A = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
KEY_B = Ed25519PrivateKey.from_private_bytes(bytes(range(33, 65)))
KEYS = {"source-a": KEY_A, "source-b": KEY_B}


class ProtocolPropertyTests(unittest.TestCase):
    @settings(max_examples=96, derandomize=True, deadline=None)
    @given(
        condition=st.sampled_from(list(EvidenceCondition)),
        seed=st.integers(min_value=1, max_value=10_000_000),
    )
    def test_treatments_preserve_immutable_scenario_identity(self, condition, seed):
        adversary = AdversaryClass.A1 if condition in {EvidenceCondition.MANIPULATED, EvidenceCondition.PARTIAL_COMPROMISE} else AdversaryClass.A0
        scenario = ScenarioIdentity("S2-AEATR-001", "SC-PROP", seed, f"T-{condition.value}", condition, adversary, ContactRegime.K0, "GT", "PROV", "ANALYSIS")
        claim = EvidenceClaim("source-a", "sat-1", "authorization_valid", True, 3, 10, 100.0, 30.0, "fixture")
        evidence = (sign_claim(claim, KEY_A),)
        budget = AdversaryBudget(adversary, ("source-a",) if adversary is AdversaryClass.A1 else ())
        kwargs = {}
        if condition is not EvidenceCondition.CURRENT:
            kwargs.update(target_source="source-a", target_key="authorization_valid")
        if condition is EvidenceCondition.CONTRADICTORY:
            kwargs["alternate_source"] = "source-b"
        result = apply_treatment(scenario, evidence, budget=budget, private_keys=KEYS, now_s=110.0, **kwargs)
        self.assertEqual(result.scenario, scenario)
        self.assertEqual(result.scenario.seed, seed)
        self.assertEqual(result.scenario.ground_truth_token, "GT")
        self.assertEqual(result.scenario.provenance_token, "PROV")
        self.assertEqual(result.scenario.analysis_control_token, "ANALYSIS")

    @settings(max_examples=64, derandomize=True, deadline=None)
    @given(sequence=st.integers(min_value=1, max_value=1_000_000))
    def test_v5_does_not_mutate_uncompromised_source(self, sequence):
        scenario = ScenarioIdentity("S2-AEATR-001", "SC-V5", sequence, "T-V5", EvidenceCondition.PARTIAL_COMPROMISE, AdversaryClass.A1, ContactRegime.K0, "GT", "PROV", "ANALYSIS")
        a = sign_claim(EvidenceClaim("source-a", "sat-1", "authorization_valid", True, 3, sequence, 100.0, 30.0, "a"), KEY_A)
        b = sign_claim(EvidenceClaim("source-b", "sat-1", "integrity_measurement_valid", True, 3, sequence, 100.0, 30.0, "b"), KEY_B)
        result = apply_treatment(scenario, (a, b), budget=AdversaryBudget(AdversaryClass.A1, ("source-a",)), private_keys=KEYS, target_source="source-a", target_key="authorization_valid")
        self.assertEqual(result.evidence[1], b)


if __name__ == "__main__":
    unittest.main()
