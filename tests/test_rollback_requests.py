import copy
import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
)
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)


class RollbackRequestTests(unittest.TestCase):
    def setUp(self):
        self.event = materialize_event(
            "E3",
            mission_state="M4",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        self.manifest = build_manifest()
        self.tampered_verification = verify_candidate(
            build_tampered_update(),
            self.manifest,
        )
        self.approved_verification = verify_candidate(
            build_approved_update(),
            self.manifest,
        )
        self.p5 = evaluate_policy("P5", self.event)

    def test_p5_builds_evidence_bound_request(self):
        request = build_verified_rollback_request(
            event_instance=self.event,
            policy_decision=self.p5,
            manifest=self.manifest,
            candidate_verification=self.tampered_verification,
        )

        self.assertEqual(request["action"], "REQUEST_VERIFIED_ROLLBACK")
        self.assertEqual(
            request["approved_target_sha256"],
            "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697",
        )
        self.assertEqual(
            request["rejected_candidate_sha256"],
            "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d",
        )
        self.assertIn("sha256_mismatch", request["rejection_reasons"])
        self.assertFalse(request["rollback_staging_performed"])
        self.assertFalse(request["rollback_activation_performed"])
        self.assertFalse(request["recovery_execution_performed"])
        self.assertFalse(request["trusted_recovery_verified"])
        self.assertFalse(request["oracle_ground_truth_read"])

    def test_request_is_deterministic(self):
        first = build_verified_rollback_request(
            event_instance=self.event,
            policy_decision=self.p5,
            manifest=self.manifest,
            candidate_verification=self.tampered_verification,
        )
        second = build_verified_rollback_request(
            event_instance=self.event,
            policy_decision=self.p5,
            manifest=self.manifest,
            candidate_verification=self.tampered_verification,
        )
        self.assertEqual(first, second)

    def test_request_does_not_depend_on_ground_truth(self):
        changed = copy.deepcopy(self.event)
        for key, value in list(changed["ground_truth"].items()):
            if isinstance(value, bool):
                changed["ground_truth"][key] = not value

        original = build_verified_rollback_request(
            event_instance=self.event,
            policy_decision=self.p5,
            manifest=self.manifest,
            candidate_verification=self.tampered_verification,
        )
        mutated = build_verified_rollback_request(
            event_instance=changed,
            policy_decision=self.p5,
            manifest=self.manifest,
            candidate_verification=self.tampered_verification,
        )
        self.assertEqual(original, mutated)

    def test_p0_cannot_create_rollback_request(self):
        with self.assertRaises(ValueError):
            build_verified_rollback_request(
                event_instance=self.event,
                policy_decision=evaluate_policy("P0", self.event),
                manifest=self.manifest,
                candidate_verification=self.tampered_verification,
            )

    def test_approved_candidate_cannot_trigger_request(self):
        with self.assertRaises(ValueError):
            build_verified_rollback_request(
                event_instance=self.event,
                policy_decision=self.p5,
                manifest=self.manifest,
                candidate_verification=self.approved_verification,
            )

    def test_missing_rollback_availability_rejected(self):
        changed = copy.deepcopy(self.event)
        changed["policy_visible_evidence"]["rollback_available"] = False

        with self.assertRaises(ValueError):
            build_verified_rollback_request(
                event_instance=changed,
                policy_decision=self.p5,
                manifest=self.manifest,
                candidate_verification=self.tampered_verification,
            )


if __name__ == "__main__":
    unittest.main()
