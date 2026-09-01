from __future__ import annotations

import unittest

from study2_security.context_ablations import select_context_ablation
from study2_security.selectors import ObservationSummary, Study2Action


class ContextAblationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.obs = ObservationSummary(signature_valid=False, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=False, security_signal=True, authorization_available=False)

    def test_no_evidence_ablation_removes_evidence_dependency_only(self) -> None:
        self.assertEqual(select_context_ablation("PI_NO_EVIDENCE", self.obs), Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION)

    def test_no_contact_ablation_does_not_hide_missing_evidence(self) -> None:
        self.assertEqual(select_context_ablation("PI_NO_CONTACT", self.obs), Study2Action.HOLD_AND_REQUIRE_EVIDENCE)

    def test_security_only_is_explicitly_restrictive_on_signal(self) -> None:
        self.assertEqual(select_context_ablation("PI_SECURITY_ONLY", self.obs), Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION)


if __name__ == "__main__":
    unittest.main()
