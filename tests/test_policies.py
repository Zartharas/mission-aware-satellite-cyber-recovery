import copy
import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import (
    assess_minimum_evidence,
    evaluate_policy,
)


class PolicySemanticsTests(unittest.TestCase):
    def event(
        self,
        event_id,
        *,
        mission_state="M0",
        contact="C0",
        evidence="T0",
    ):
        return materialize_event(
            event_id,
            mission_state=mission_state,
            contact_condition=contact,
            evidence_condition=evidence,
            seed=1,
        )

    def test_fixed_policy_actions(self):
        event = self.event("E1")
        expected = {
            "P0": "OBSERVE_ONLY",
            "P1": "ISOLATE_MODELED_SOURCE",
            "P2": "RESTRICT_HIGH_RISK_COMMANDS",
            "P4": "ENTER_SAFE_MODE",
            "P5": "REQUEST_VERIFIED_ROLLBACK",
        }

        for policy_id, action in expected.items():
            with self.subTest(policy_id=policy_id):
                result = evaluate_policy(policy_id, event)
                self.assertEqual(result["delegated_policy_id"], policy_id)
                self.assertEqual(result["selected_action"], action)
                self.assertFalse(result["oracle_ground_truth_read"])

    def test_p5_defers_trusted_recovery_to_wp7(self):
        result = evaluate_policy("P5", self.event("E3", mission_state="M4"))
        self.assertTrue(
            result["trusted_recovery_verification_deferred_to_wp7"]
        )

    def test_p7_e1_nominal_immediate_isolates_source(self):
        result = evaluate_policy("P7", self.event("E1"))
        self.assertEqual(result["delegated_policy_id"], "P1")
        self.assertFalse(result["evidence_insufficient"])

    def test_p7_contact_delay_changes_e1_action(self):
        immediate = evaluate_policy("P7", self.event("E1", contact="C0"))
        delayed = evaluate_policy("P7", self.event("E1", contact="C1"))
        self.assertEqual(immediate["delegated_policy_id"], "P1")
        self.assertEqual(delayed["delegated_policy_id"], "P2")

    def test_p7_reduced_e1_evidence_is_conservative(self):
        event = self.event("E1", evidence="T1")
        assessment = assess_minimum_evidence(event)
        result = evaluate_policy("P7", event)

        self.assertFalse(assessment["sufficient"])
        self.assertIn(
            "authorization_context_current:missing",
            assessment["failures"],
        )
        self.assertEqual(result["delegated_policy_id"], "P2")
        self.assertTrue(result["evidence_insufficient"])

    def test_p7_full_e3_requests_rollback(self):
        result = evaluate_policy(
            "P7",
            self.event("E3", mission_state="M4", contact="C0"),
        )
        self.assertEqual(result["delegated_policy_id"], "P5")
        self.assertTrue(
            result["trusted_recovery_verification_deferred_to_wp7"]
        )

    def test_p7_reduced_e3_evidence_with_missed_contact_enters_safe_mode(self):
        result = evaluate_policy(
            "P7",
            self.event(
                "E3",
                mission_state="M4",
                contact="C1",
                evidence="T1",
            ),
        )
        self.assertEqual(result["delegated_policy_id"], "P4")
        self.assertTrue(result["evidence_insufficient"])

    def test_p7_e4_detects_event_intrinsic_evidence_insufficiency(self):
        nominal = evaluate_policy(
            "P7",
            self.event("E4", mission_state="M0", evidence="T0"),
        )
        low_power = evaluate_policy(
            "P7",
            self.event("E4", mission_state="M2", evidence="T0"),
        )

        self.assertTrue(nominal["evidence_insufficient"])
        self.assertEqual(nominal["delegated_policy_id"], "P2")
        self.assertEqual(low_power["delegated_policy_id"], "P4")

    def test_p7_does_not_read_immutable_ground_truth(self):
        original = self.event("E1", mission_state="M0", contact="C0")
        mutated = copy.deepcopy(original)

        for key, value in list(mutated["ground_truth"].items()):
            if isinstance(value, bool):
                mutated["ground_truth"][key] = not value

        before = evaluate_policy("P7", original)
        after = evaluate_policy("P7", mutated)

        self.assertEqual(before, after)
        self.assertFalse(before["oracle_ground_truth_read"])

    def test_decision_hash_is_deterministic(self):
        event = self.event("E3", mission_state="M4")
        first = evaluate_policy("P7", event)
        second = evaluate_policy("P7", event)
        self.assertEqual(first["decision_sha256"], second["decision_sha256"])

    def test_p7_full_factor_matrix_is_defined(self):
        for event_id in ("E1", "E2", "E3", "E4"):
            for state in ("M0", "M2", "M4"):
                for contact in ("C0", "C1"):
                    for evidence in ("T0", "T1"):
                        with self.subTest(
                            event=event_id,
                            state=state,
                            contact=contact,
                            evidence=evidence,
                        ):
                            result = evaluate_policy(
                                "P7",
                                self.event(
                                    event_id,
                                    mission_state=state,
                                    contact=contact,
                                    evidence=evidence,
                                ),
                            )
                            self.assertIn(
                                result["delegated_policy_id"],
                                {"P1", "P2", "P4", "P5"},
                            )
                            self.assertFalse(
                                result["oracle_ground_truth_read"]
                            )


if __name__ == "__main__":
    unittest.main()
