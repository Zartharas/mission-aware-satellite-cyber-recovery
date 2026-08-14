import unittest

from src.mission_recovery.events import load_catalog, materialize_event


class EventLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def test_exact_event_set(self):
        self.assertEqual(
            [event["id"] for event in self.catalog["events"]],
            ["E1", "E2", "E3", "E4"],
        )

    def test_all_events_have_external_threat_mapping(self):
        for event in self.catalog["events"]:
            self.assertTrue(event["sparta"])

    def test_materialization_is_deterministic(self):
        a = materialize_event(
            "E2",
            mission_state="M2",
            contact_condition="C1",
            evidence_condition="T1",
            seed=7,
        )
        b = materialize_event(
            "E2",
            mission_state="M2",
            contact_condition="C1",
            evidence_condition="T1",
            seed=7,
        )
        self.assertEqual(a, b)

    def test_seed_is_part_of_instance_identity(self):
        a = materialize_event(
            "E1",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        b = materialize_event(
            "E1",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=2,
        )
        self.assertNotEqual(a["instance_sha256"], b["instance_sha256"])

    def test_reduced_evidence_never_changes_ground_truth(self):
        for event in ("E1", "E2", "E3", "E4"):
            full = materialize_event(
                event,
                mission_state="M4",
                contact_condition="C1",
                evidence_condition="T0",
                seed=11,
            )
            reduced = materialize_event(
                event,
                mission_state="M4",
                contact_condition="C1",
                evidence_condition="T1",
                seed=11,
            )
            self.assertEqual(full["ground_truth"], reduced["ground_truth"])
            self.assertLess(
                len(reduced["policy_visible_evidence"]),
                len(full["policy_visible_evidence"]),
            )

    def test_no_event_materializer_performs_real_world_action(self):
        for event in ("E1", "E2", "E3", "E4"):
            instance = materialize_event(
                event,
                mission_state="M0",
                contact_condition="C0",
                evidence_condition="T0",
                seed=3,
            )
            self.assertEqual(instance["execution_mode"], "synthetic_model_only")
            self.assertTrue(instance["prohibited_actions"])

    def test_contact_delay_is_condition_not_event(self):
        event_ids = {event["id"] for event in self.catalog["events"]}
        self.assertNotIn("C0", event_ids)
        self.assertNotIn("C1", event_ids)

    def test_invalid_factor_is_rejected(self):
        with self.assertRaises(ValueError):
            materialize_event(
                "E1",
                mission_state="M9",
                contact_condition="C0",
                evidence_condition="T0",
                seed=1,
            )


if __name__ == "__main__":
    unittest.main()
