import unittest

from study2_security.selectors import ObservationSummary, Study2Action, Study2Policy, select_action


class SelectorTests(unittest.TestCase):
    def qualified(self, **changes):
        values = dict(signature_valid=True, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=True, security_signal=True, authorization_available=False)
        values.update(changes)
        return ObservationSummary(**values)

    def test_evidence_aware_fails_closed_on_stale(self):
        self.assertEqual(select_action(Study2Policy.EVIDENCE_AWARE, self.qualified(fresh=False)), Study2Action.HOLD_AND_REQUIRE_EVIDENCE)

    def test_no_freshness_ablation_is_deliberately_weaker(self):
        self.assertNotEqual(select_action(Study2Policy.EVIDENCE_AWARE, self.qualified(fresh=False)), select_action(Study2Policy.NO_FRESHNESS, self.qualified(fresh=False)))

    def test_no_contradiction_ablation_is_deliberately_weaker(self):
        self.assertNotEqual(select_action(Study2Policy.EVIDENCE_AWARE, self.qualified(contradictory=True)), select_action(Study2Policy.NO_CONTRADICTION, self.qualified(contradictory=True)))

    def test_fail_operational_preserves_operation_when_evidence_unqualified(self):
        self.assertEqual(select_action(Study2Policy.FAIL_OPERATIONAL, self.qualified(signature_valid=False)), Study2Action.PRESERVE_LIMITED_OPERATION)


if __name__ == "__main__":
    unittest.main()
