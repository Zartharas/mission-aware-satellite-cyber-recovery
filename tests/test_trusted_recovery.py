import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
)
from src.mission_recovery.trusted_recovery import (
    validate_rollback_request,
    verify_replacement_source,
    verify_terminal_recovery,
)
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)


class TrustedRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = build_manifest()
        self.approved = build_approved_update()
        self.tampered = build_tampered_update()

        event = materialize_event(
            "E3",
            mission_state="M4",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        decision = evaluate_policy("P5", event)
        verification = verify_candidate(self.tampered, self.manifest)
        self.request = build_verified_rollback_request(
            event_instance=event,
            policy_decision=decision,
            manifest=self.manifest,
            candidate_verification=verification,
        )

    def test_request_validates_against_rejected_candidate(self):
        result = validate_rollback_request(
            request=self.request,
            manifest=self.manifest,
            pre_recovery_candidate_sha256=(
                "ff96d61205cc2c49b6d7d73fc36b9544"
                "c0deea79d7a9304cc1fb9f1f8986053d"
            ),
        )
        self.assertTrue(result["accepted"])
        self.assertEqual(result["reasons"], [])

    def test_wrong_rejected_candidate_binding_fails(self):
        result = validate_rollback_request(
            request=self.request,
            manifest=self.manifest,
            pre_recovery_candidate_sha256="0" * 64,
        )
        self.assertFalse(result["accepted"])
        self.assertIn("rejected_candidate_mismatch", result["reasons"])

    def test_approved_replacement_source_is_valid(self):
        result = verify_replacement_source(self.approved, self.manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["reasons"], [])

    def test_tampered_replacement_source_is_rejected(self):
        result = verify_replacement_source(self.tampered, self.manifest)
        self.assertFalse(result["accepted"])
        self.assertIn("sha256_mismatch", result["reasons"])

    def test_approved_terminal_state_is_trusted(self):
        result = verify_terminal_recovery(
            terminal_candidate=self.approved,
            manifest=self.manifest,
            rejected_candidate_sha256=(
                "ff96d61205cc2c49b6d7d73fc36b9544"
                "c0deea79d7a9304cc1fb9f1f8986053d"
            ),
        )
        self.assertTrue(result["trusted_recovery_verified"])
        self.assertTrue(result["terminal_matches_approved"])
        self.assertTrue(result["terminal_differs_from_rejected"])
        self.assertEqual(result["reasons"], [])

    def test_tampered_terminal_state_is_not_trusted(self):
        result = verify_terminal_recovery(
            terminal_candidate=self.tampered,
            manifest=self.manifest,
            rejected_candidate_sha256=(
                "ff96d61205cc2c49b6d7d73fc36b9544"
                "c0deea79d7a9304cc1fb9f1f8986053d"
            ),
        )
        self.assertFalse(result["trusted_recovery_verified"])
        self.assertFalse(result["terminal_matches_approved"])
        self.assertFalse(result["terminal_differs_from_rejected"])
        self.assertIn("sha256_mismatch", result["reasons"])
        self.assertIn(
            "terminal_still_rejected_candidate",
            result["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
