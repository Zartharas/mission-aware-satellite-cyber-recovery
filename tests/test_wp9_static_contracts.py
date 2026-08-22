from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.wp9_static_contracts import (
    build_e2_replay_effect_contract,
    build_p6_authorization_contract,
    build_p6_handoff_contract,
    build_static_matrix,
    build_wp9_run_schema,
    campaign_cells,
    evaluate_wp9_policy,
    load_campaign_design,
    load_static_contract,
    load_wp9_model,
    runtime_route_for_cell,
    validate_wp9_static_contract,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = ROOT / "configs" / "experiment_model.json"
BASE_SCHEMA = ROOT / "configs" / "experiment_run.schema.json"
VALID_FIXTURE = ROOT / "configs" / "examples" / "valid_run.json"


class WP9StaticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.design = load_campaign_design()
        cls.cells = campaign_cells(cls.design)

    def test_wp9_model_is_additive_and_wp8_model_remains_frozen(self) -> None:
        base = json.loads(BASE_MODEL.read_text(encoding="utf-8"))
        wp9 = load_wp9_model()
        self.assertEqual(base["model_version"], "0.3.0")
        self.assertEqual(wp9["base_model_version"], "0.3.0")
        self.assertEqual(wp9["model_version"], "0.4.0")
        base_ids = {row["id"] for row in base["response_policies"]}
        wp9_ids = {row["id"] for row in wp9["response_policies"]}
        self.assertNotIn("P6", base_ids)
        self.assertEqual(wp9_ids - base_ids, {"P6"})
        self.assertFalse(wp9["scientific_boundary"]["wp8_model_mutated"])

    def test_non_p6_policy_semantics_reuse_frozen_wp8_engine(self) -> None:
        for cell_id, cell in self.cells.items():
            if cell["policy_id"] == "P6":
                continue
            event = materialize_event(
                cell["event_id"],
                mission_state=cell["mission_state_id"],
                contact_condition=cell["contact_condition_id"],
                evidence_condition=cell["evidence_condition_id"],
                seed=0,
            )
            with self.subTest(cell_id=cell_id):
                self.assertEqual(
                    evaluate_wp9_policy(cell["policy_id"], event),
                    evaluate_policy(cell["policy_id"], event),
                )

    def test_p6_is_narrow_ground_dependent_static_policy(self) -> None:
        for contact in ("C0", "C1"):
            event = materialize_event(
                "E3",
                mission_state="M4",
                contact_condition=contact,
                evidence_condition="T0",
                seed=0,
            )
            decision = evaluate_wp9_policy("P6", event)
            self.assertEqual(decision["delegated_policy_id"], "P6")
            self.assertEqual(
                decision["selected_action"], "WAIT_FOR_GROUND_AUTHORIZATION"
            )
            self.assertEqual(decision["autonomy_level"], "ground_dependent")
            self.assertTrue(decision["ground_authorization_required"])
            self.assertFalse(decision["oracle_ground_truth_read"])

        invalid = materialize_event(
            "E1",
            mission_state="M4",
            contact_condition="C0",
            evidence_condition="T0",
            seed=0,
        )
        with self.assertRaises(ValueError):
            evaluate_wp9_policy("P6", invalid)

    def test_p6_authorization_schedule_distinguishes_c0_and_c1(self) -> None:
        c0 = build_p6_authorization_contract(
            materialize_event(
                "E3",
                mission_state="M4",
                contact_condition="C0",
                evidence_condition="T0",
                seed=0,
            )
        )
        c1 = build_p6_authorization_contract(
            materialize_event(
                "E3",
                mission_state="M4",
                contact_condition="C1",
                evidence_condition="T0",
                seed=0,
            )
        )
        self.assertTrue(c0["available_at_response_boundary"])
        self.assertEqual(c0["missed_contact_windows_before_authorization"], 0)
        self.assertFalse(c1["available_at_response_boundary"])
        self.assertEqual(c1["missed_contact_windows_before_authorization"], 1)
        self.assertIsNone(c0["runtime_authorization_timestamp_s"])
        self.assertIsNone(c1["runtime_authorization_timestamp_s"])
        self.assertTrue(c0["runtime_observation_required"])
        self.assertTrue(c1["runtime_observation_required"])
        self.assertFalse(c0["expected_contact_condition_used_as_observed_timestamp"])
        self.assertFalse(c1["expected_contact_condition_used_as_observed_timestamp"])

    def test_p6_handoff_requires_observed_authorization_before_p5(self) -> None:
        event = materialize_event(
            "E3",
            mission_state="M4",
            contact_condition="C1",
            evidence_condition="T0",
            seed=0,
        )
        contract = build_p6_handoff_contract(event)
        self.assertEqual(
            contract["handoff_precondition"],
            "runtime_observed_authorization_current",
        )
        self.assertEqual(contract["post_authorization_delegated_policy_id"], "P5")
        self.assertEqual(
            contract["post_authorization_action"],
            "REQUEST_VERIFIED_ROLLBACK",
        )
        self.assertTrue(
            contract["authorization_observation_required_before_handoff"]
        )
        self.assertFalse(contract["runtime_execution_performed"])
        self.assertFalse(contract["campaign_seed_consumed"])

    def test_e2_replay_uses_byte_identical_reset_effect_not_noop_receipt(self) -> None:
        expected = {"A19": 1, "A20": 0, "A21": 0}
        packet_sha = "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
        for cell_id, expected_delta in expected.items():
            contract = build_e2_replay_effect_contract(cell_id)
            with self.subTest(cell_id=cell_id):
                self.assertEqual(contract["setup"]["packet_sha256"], packet_sha)
                self.assertEqual(contract["replay"]["packet_sha256"], packet_sha)
                self.assertTrue(contract["replay"]["byte_identical_to_setup"])
                self.assertTrue(contract["setup"]["excluded_from_m01"])
                self.assertEqual(
                    contract["m01_effect_observation"][
                        "source"
                    ],
                    "observed_post_replay_cfs_reset_marker_delta",
                )
                self.assertEqual(
                    contract["m01_effect_observation"][
                        "expected_delta_for_acceptance_only"
                    ],
                    expected_delta,
                )
                self.assertTrue(
                    contract["m01_effect_observation"][
                        "packet_send_success_is_not_effect_evidence"
                    ]
                )
                self.assertTrue(
                    contract["m01_effect_observation"][
                        "noop_receipt_alone_is_not_effect_evidence"
                    ]
                )
                self.assertFalse(contract["runtime_execution_performed"])

    def test_all_24_cells_materialize_exact_frozen_delegates_without_runtime(self) -> None:
        expected_p7 = {
            "A02": "P1",
            "A04": "P2",
            "A06": "P2",
            "A09": "P4",
            "A11": "P5",
            "A13": "P2",
            "A18": "P5",
            "A21": "P1",
            "A24": "P4",
        }
        matrix = build_static_matrix(self.design)
        self.assertEqual(matrix["cell_ids"], [f"A{i:02d}" for i in range(1, 25)])
        self.assertEqual(len(matrix["rows"]), 24)
        rows = {row["cell_id"]: row for row in matrix["rows"]}
        for cell_id, cell in self.cells.items():
            row = rows[cell_id]
            self.assertEqual(
                row["actual_effective_policy_id"],
                cell["expected_effective_policy_id"],
            )
            self.assertFalse(row["oracle_ground_truth_read"])
            self.assertTrue(row["development_preflight"])
            self.assertFalse(row["campaign_data"])
            self.assertFalse(row["campaign_seed_consumed"])
            self.assertFalse(row["runtime_execution_performed"])
        for cell_id, delegated in expected_p7.items():
            self.assertEqual(rows[cell_id]["actual_effective_policy_id"], delegated)
        self.assertFalse(matrix["runtime_execution_performed"])
        self.assertFalse(matrix["campaign_seed_consumed"])
        self.assertFalse(matrix["campaign_data_generated"])
        self.assertFalse(matrix["campaign_execution_authorized"])

    def test_runtime_routing_covers_exactly_all_24_cells(self) -> None:
        static = load_static_contract()
        self.assertEqual(set(static["runtime_routing"]), set(self.cells))
        families = {
            cell_id: runtime_route_for_cell(cell_id)["runtime_family"]
            for cell_id in self.cells
        }
        self.assertEqual({families[f"A{i:02d}"] for i in range(1, 10)}, {"command"})
        self.assertEqual({families[f"A{i:02d}"] for i in range(10, 19)}, {"recovery"})
        self.assertEqual({families[f"A{i:02d}"] for i in range(19, 22)}, {"replay"})
        self.assertEqual({families[f"A{i:02d}"] for i in range(22, 25)}, {"observability"})

    def test_wp9_schema_overlay_admits_p6_and_requires_observed_authorization(self) -> None:
        base_schema = json.loads(BASE_SCHEMA.read_text(encoding="utf-8"))
        self.assertNotIn("P6", base_schema["properties"]["policy_id"]["enum"])
        schema = build_wp9_run_schema()
        Draft202012Validator.check_schema(schema)
        self.assertIn("P6", schema["properties"]["policy_id"]["enum"])
        validator = Draft202012Validator(schema)

        fixture = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(list(validator.iter_errors(fixture)), [])

        p6 = copy.deepcopy(fixture)
        p6.update(
            {
                "model_version": "0.4.0",
                "mission_state_id": "M4",
                "event_id": "E3",
                "policy_id": "P6",
                "contact_condition_id": "C0",
                "evidence_condition_id": "T0",
            }
        )
        errors = list(validator.iter_errors(p6))
        self.assertTrue(errors)
        self.assertTrue(any("ground_authorization" in error.message for error in errors))

        p6["raw_metric_evidence"]["ground_authorization"] = {
            "required": True,
            "source": "synthetic_ground_authorization_schedule",
            "available_at_response_boundary": True,
            "available_timestamp_s": 30.0,
            "missed_contact_windows": 0,
            "authorization_current": True,
            "evidence_ref": "fixture:synthetic-ground-authorization",
        }
        self.assertEqual(list(validator.iter_errors(p6)), [])

        c1 = copy.deepcopy(p6)
        c1["contact_condition_id"] = "C1"
        self.assertTrue(list(validator.iter_errors(c1)))
        c1["raw_metric_evidence"]["ground_authorization"].update(
            {
                "available_at_response_boundary": False,
                "missed_contact_windows": 1,
                "available_timestamp_s": 90.0,
            }
        )
        self.assertEqual(list(validator.iter_errors(c1)), [])

    def test_r044_design_remains_frozen_and_unmodified_by_r045(self) -> None:
        p6 = self.design["required_policy_extension"]
        self.assertFalse(p6["existing_experiment_model_support"])
        self.assertFalse(p6["existing_run_schema_support"])
        self.assertFalse(p6["existing_runtime_support"])
        self.assertFalse(self.design["scientific_boundary"]["runtime_support_complete"])
        self.assertFalse(
            self.design["scientific_boundary"]["campaign_execution_authorized"]
        )

    def test_r045_static_boundary_blocks_wp9b2_and_campaign(self) -> None:
        validate_wp9_static_contract()
        static = load_static_contract()
        boundary = static["scientific_boundary"]
        self.assertTrue(boundary["wp9b1_static_implementation_complete"])
        self.assertFalse(boundary["wp9b2_runtime_validation_complete"])
        self.assertFalse(boundary["runtime_execution_performed"])
        self.assertFalse(boundary["development_runtime_data_generated"])
        self.assertFalse(boundary["campaign_seed_consumed"])
        self.assertFalse(boundary["campaign_data_generated"])
        self.assertFalse(boundary["repetition_count_frozen"])
        self.assertFalse(boundary["campaign_execution_authorized"])
        self.assertFalse(boundary["wp8_code_or_pilot_design_mutated"])


if __name__ == "__main__":
    unittest.main()
