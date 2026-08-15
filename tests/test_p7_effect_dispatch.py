import copy
import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.p7_effect_dispatch import build_p7_effect_plan
from src.mission_recovery.policies import evaluate_policy


CASES = {
    "A": ("E1", "M0", "C0", "T0", "P1", "ISOLATE_MODELED_SOURCE"),
    "B": ("E1", "M0", "C1", "T0", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
    "C": ("E1", "M2", "C0", "T0", "P2", "RESTRICT_HIGH_RISK_COMMANDS"),
    "D": ("E1", "M2", "C0", "T1", "P4", "ENTER_SAFE_MODE"),
    "E": ("E3", "M4", "C0", "T0", "P5", "REQUEST_VERIFIED_ROLLBACK"),
}


class P7EffectDispatchTests(unittest.TestCase):
    def _decision(self, spec):
        event_id, state, contact, evidence, _, _ = spec
        event = materialize_event(
            event_id,
            mission_state=state,
            contact_condition=contact,
            evidence_condition=evidence,
            seed=1,
        )
        return event, evaluate_policy("P7", event)

    def test_runtime_case_delegates(self):
        for case_id, spec in CASES.items():
            with self.subTest(case_id=case_id):
                event, decision = self._decision(spec)
                expected_delegate = spec[4]
                expected_action = spec[5]

                self.assertEqual(
                    decision["delegated_policy_id"],
                    expected_delegate,
                )
                self.assertEqual(
                    decision["selected_action"],
                    expected_action,
                )
                self.assertFalse(decision["oracle_ground_truth_read"])

                plan = build_p7_effect_plan(decision)
                self.assertEqual(plan["delegated_policy_id"], expected_delegate)
                self.assertEqual(plan["selected_action"], expected_action)

                expected_family = (
                    "rollback_request"
                    if expected_delegate == "P5"
                    else "command_gateway"
                )
                self.assertEqual(plan["effect_family"], expected_family)

    def test_ground_truth_mutation_does_not_change_p7_decision(self):
        for case_id, spec in CASES.items():
            with self.subTest(case_id=case_id):
                event, original = self._decision(spec)
                changed = copy.deepcopy(event)
                for key, value in list(changed["ground_truth"].items()):
                    if isinstance(value, bool):
                        changed["ground_truth"][key] = not value
                mutated = evaluate_policy("P7", changed)
                self.assertEqual(original, mutated)

    def test_contact_only_contrast(self):
        _, left = self._decision(CASES["A"])
        _, right = self._decision(CASES["B"])
        self.assertEqual(left["delegated_policy_id"], "P1")
        self.assertEqual(right["delegated_policy_id"], "P2")

    def test_mission_state_only_contrast(self):
        _, left = self._decision(CASES["A"])
        _, right = self._decision(CASES["C"])
        self.assertEqual(left["delegated_policy_id"], "P1")
        self.assertEqual(right["delegated_policy_id"], "P2")

    def test_evidence_only_contrast(self):
        _, left = self._decision(CASES["C"])
        _, right = self._decision(CASES["D"])
        self.assertEqual(left["delegated_policy_id"], "P2")
        self.assertEqual(right["delegated_policy_id"], "P4")
        self.assertFalse(left["evidence_insufficient"])
        self.assertTrue(right["evidence_insufficient"])

    def test_non_p7_decision_rejected(self):
        event = materialize_event(
            "E1",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        with self.assertRaises(ValueError):
            build_p7_effect_plan(evaluate_policy("P1", event))


if __name__ == "__main__":
    unittest.main()
