from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from src.mission_recovery.wp8_command_effect_contract import (
    build_command_cell_effect_contract,
    build_command_effect_matrix,
    command_cells,
    derive_observed_command_effect,
    require_command_effect_acceptance,
)
from src.mission_recovery.policy_gateway import SUPPORTED_ACTIONS

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)

EXPECTED = {
    "C01": ("P0", "OBSERVE_ONLY", 2, 1),
    "C02": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
    "C03": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
    "C04": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
    "C05": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1),
    "C06": ("P4", "ENTER_SAFE_MODE", 0, 0),
    "C07": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1),
}


def expected_observation(cell_id: str) -> dict:
    effective, action, attacker_delta, noop_delta = EXPECTED[cell_id]
    return {
        "actual_effective_policy_id": effective,
        "selected_action": action,
        "event_activation_reset_marker_delta": 1,
        "post_enforcement_attacker_probe_count": 2,
        "post_enforcement_attacker_reset_marker_delta": attacker_delta,
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": noop_delta,
    }


class WP8CommandEffectContractTests(unittest.TestCase):
    def test_command_cells_are_exactly_c01_through_c07(self) -> None:
        self.assertEqual(
            [row["cell_id"] for row in command_cells(PILOT)],
            ["C01", "C02", "C03", "C04", "C05", "C06", "C07"],
        )

    def test_factor_context_is_read_from_pilot_cells(self) -> None:
        pilot = deepcopy(PILOT)
        c04 = next(row for row in pilot["cells"] if row["cell_id"] == "C04")
        c04["contact_condition_id"] = "C1"

        row = build_command_cell_effect_contract(pilot, "C04")
        self.assertEqual(
            row["factor_context_without_run_id"]["contact_condition_id"],
            "C1",
        )

    def test_policy_engine_outputs_frozen_effective_policy_matrix(self) -> None:
        matrix = build_command_effect_matrix(PILOT)
        actual = {
            row["cell_id"]: row["policy_evaluation"][
                "actual_effective_policy_id"
            ]
            for row in matrix["rows"]
        }
        self.assertEqual(
            actual,
            {cell_id: values[0] for cell_id, values in EXPECTED.items()},
        )

    def test_selected_action_drives_gateway_contract(self) -> None:
        matrix = build_command_effect_matrix(PILOT)
        for row in matrix["rows"]:
            cell_id = row["cell_id"]
            action = row["policy_evaluation"]["selected_action"]
            self.assertEqual(action, EXPECTED[cell_id][1])
            self.assertEqual(
                row["gateway_execution"]["action"],
                action,
            )
            self.assertEqual(
                row["gateway_execution"]["action_source"],
                "evaluated_policy_decision.selected_action",
            )
            self.assertIn(action, SUPPORTED_ACTIONS)

    def test_expected_probe_effect_matrix(self) -> None:
        matrix = build_command_effect_matrix(PILOT)
        for row in matrix["rows"]:
            cell_id = row["cell_id"]
            gateway = row["gateway_execution"]
            self.assertEqual(
                gateway["attacker_probe"][
                    "expected_cfs_reset_marker_delta_for_acceptance_only"
                ],
                EXPECTED[cell_id][2],
            )
            self.assertEqual(
                gateway["authorized_probe"][
                    "expected_cfs_noop_marker_delta_for_acceptance_only"
                ],
                EXPECTED[cell_id][3],
            )

    def test_c01_no_response_control_allows_attacker_effect(self) -> None:
        row = build_command_cell_effect_contract(PILOT, "C01")
        gateway = row["gateway_execution"]
        self.assertEqual(gateway["action"], "OBSERVE_ONLY")
        self.assertTrue(
            gateway["attacker_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ]
        )
        self.assertEqual(
            gateway["attacker_probe"][
                "expected_cfs_reset_marker_delta_for_acceptance_only"
            ],
            2,
        )
        self.assertEqual(
            gateway["authorized_probe"][
                "expected_cfs_noop_marker_delta_for_acceptance_only"
            ],
            1,
        )

    def test_c06_p4_tradeoff_blocks_attacker_and_authorized_noop(self) -> None:
        row = build_command_cell_effect_contract(PILOT, "C06")
        gateway = row["gateway_execution"]
        self.assertEqual(gateway["action"], "ENTER_SAFE_MODE")
        self.assertFalse(
            gateway["attacker_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ]
        )
        self.assertFalse(
            gateway["authorized_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ]
        )
        self.assertEqual(
            gateway["attacker_probe"][
                "expected_cfs_reset_marker_delta_for_acceptance_only"
            ],
            0,
        )
        self.assertEqual(
            gateway["authorized_probe"][
                "expected_cfs_noop_marker_delta_for_acceptance_only"
            ],
            0,
        )

    def test_observed_attacker_delta_not_expected_value_derives_containment(
        self,
    ) -> None:
        observation = expected_observation("C02")
        observation["post_enforcement_attacker_reset_marker_delta"] = 2

        derived = derive_observed_command_effect(
            pilot=PILOT,
            cell_id="C02",
            observation=observation,
        )

        self.assertFalse(derived["containment_predicate_observed"])
        self.assertFalse(derived["effect_semantics_met"])
        self.assertFalse(derived["stage1_expected_effect_semantics_met"])

    def test_observed_noop_delta_not_expected_value_derives_rejection(
        self,
    ) -> None:
        observation = expected_observation("C06")
        observation["authorized_noop_marker_delta"] = 1

        derived = derive_observed_command_effect(
            pilot=PILOT,
            cell_id="C06",
            observation=observation,
        )

        self.assertEqual(derived["legitimate_commands_rejected"], 0)
        self.assertFalse(derived["effect_semantics_met"])

    def test_partial_attacker_effect_is_noncontainment_and_fails_acceptance(
        self,
    ) -> None:
        observation = expected_observation("C05")
        observation["post_enforcement_attacker_reset_marker_delta"] = 1

        derived = derive_observed_command_effect(
            pilot=PILOT,
            cell_id="C05",
            observation=observation,
        )

        self.assertFalse(derived["containment_predicate_observed"])
        self.assertFalse(derived["effect_semantics_met"])
        with self.assertRaisesRegex(ValueError, "effects differ"):
            require_command_effect_acceptance(derived)

    def test_wrong_actual_effective_policy_is_not_substituted(self) -> None:
        observation = expected_observation("C02")
        observation["actual_effective_policy_id"] = "P2"

        derived = derive_observed_command_effect(
            pilot=PILOT,
            cell_id="C02",
            observation=observation,
        )

        self.assertEqual(derived["actual_effective_policy_id"], "P2")
        self.assertFalse(derived["policy_semantics_met"])
        with self.assertRaisesRegex(ValueError, "policy semantics differ"):
            require_command_effect_acceptance(derived)

    def test_wrong_selected_action_is_not_substituted(self) -> None:
        observation = expected_observation("C02")
        observation["selected_action"] = "OBSERVE_ONLY"

        derived = derive_observed_command_effect(
            pilot=PILOT,
            cell_id="C02",
            observation=observation,
        )

        self.assertEqual(derived["selected_action"], "OBSERVE_ONLY")
        self.assertFalse(derived["policy_semantics_met"])

    def test_expected_observations_pass_all_command_cells(self) -> None:
        for cell_id in EXPECTED:
            derived = derive_observed_command_effect(
                pilot=PILOT,
                cell_id=cell_id,
                observation=expected_observation(cell_id),
            )
            require_command_effect_acceptance(derived)
            self.assertTrue(
                derived["stage1_expected_effect_semantics_met"],
                cell_id,
            )

    def test_contract_does_not_emit_primary_metrics_or_terminal_state(
        self,
    ) -> None:
        matrix = build_command_effect_matrix(PILOT)
        self.assertFalse(matrix["primary_metrics_emitted"])
        self.assertFalse(matrix["terminal_states_emitted"])
        for row in matrix["rows"]:
            self.assertFalse(
                row["observation_contract"]["primary_metrics_emitted"]
            )
            self.assertFalse(
                row["observation_contract"]["terminal_state_emitted"]
            )

    def test_policy_engine_never_reads_ground_truth(self) -> None:
        matrix = build_command_effect_matrix(PILOT)
        for row in matrix["rows"]:
            self.assertFalse(
                row["policy_evaluation"]["oracle_ground_truth_read"]
            )

    def test_r029_is_offline_and_pilot_gate_remains_closed(self) -> None:
        matrix = build_command_effect_matrix(PILOT)
        self.assertFalse(matrix["runtime_execution_authorized"])
        self.assertFalse(matrix["pilot_seed_consumed"])
        self.assertFalse(matrix["pilot_data_generated"])
        self.assertFalse(
            PILOT["instrumentation_gate"]["pilot_execution_authorized"]
        )
        self.assertTrue(
            PILOT["instrumentation_gate"]["component_status"][
                "stage_1_command_effect_contract"
            ]
        )
        self.assertFalse(
            PILOT["instrumentation_gate"]["component_status"][
                "stage_1_family_runtime_dispatch_adapters"
            ]
        )


if __name__ == "__main__":
    unittest.main()
