from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.mission_recovery.wp8_command_observation_contract import (
    build_command_observation_matrix,
    derive_command_runtime_observation,
    require_command_observation_acceptance,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(encoding="utf-8")
)

EXPECTED = {
    "C01": (False, False, True, "observed_run_end_ns_right_censoring"),
    "C02": (True, True, True, "observed_authorized_noop_probe_timestamp"),
    "C03": (True, True, True, "observed_authorized_noop_probe_timestamp"),
    "C04": (True, True, True, "observed_authorized_noop_probe_timestamp"),
    "C05": (True, True, True, "observed_authorized_noop_probe_timestamp"),
    "C06": (True, False, False, "observed_run_end_ns_right_censoring"),
    "C07": (True, True, True, "observed_authorized_noop_probe_timestamp"),
}


def observation_for(cell_id: str) -> dict:
    containment, convergence, noop_observed, _ = EXPECTED[cell_id]

    actions = {
        "C01": ("P0", "OBSERVE_ONLY", 2),
        "C02": ("P1", "ISOLATE_MODELED_SOURCE", 0),
        "C03": ("P1", "ISOLATE_MODELED_SOURCE", 0),
        "C04": ("P1", "ISOLATE_MODELED_SOURCE", 0),
        "C05": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0),
        "C06": ("P4", "ENTER_SAFE_MODE", 0),
        "C07": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0),
    }
    effective, action, attacker_delta = actions[cell_id]

    return {
        "actual_effective_policy_id": effective,
        "selected_action": action,
        "event_activation_reset_marker_delta": 1,
        "post_enforcement_attacker_probe_count": 2,
        "post_enforcement_attacker_reset_marker_delta": attacker_delta,
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": 1 if noop_observed else 0,
        "event_activation_ns": 1_000_000_000,
        "event_success_ns": 2_000_000_000,
        "policy_enforcement_ns": 3_000_000_000,
        "second_attacker_probe_observed_ns": 4_000_000_000,
        "authorized_noop_probe_observed_ns": 5_000_000_000,
        "run_end_ns": 9_000_000_000,
    }


class WP8CommandObservationContractTests(unittest.TestCase):
    def test_matrix_covers_c01_through_c07(self) -> None:
        matrix = build_command_observation_matrix(PILOT)
        self.assertEqual(
            matrix["cell_ids"],
            ["C01", "C02", "C03", "C04", "C05", "C06", "C07"],
        )

    def test_expected_containment_convergence_and_censoring_matrix(self) -> None:
        matrix = build_command_observation_matrix(PILOT)
        for row in matrix["rows"]:
            expected = EXPECTED[row["cell_id"]]
            self.assertEqual(
                row["containment_expected_for_acceptance_only"],
                expected[0],
            )
            self.assertEqual(
                row["authority_convergence_expected_for_acceptance_only"],
                expected[1],
            )
            self.assertEqual(row["divergence_endpoint_rule"], expected[3])

    def test_c01_containment_is_null_and_right_censored(self) -> None:
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C01",
            observation=observation_for("C01"),
        )
        self.assertFalse(row["containment"]["predicate"])
        self.assertIsNone(row["containment"]["observed_ns"])
        self.assertTrue(row["containment"]["right_censored_at_run_end"])
        self.assertFalse(row["authority_convergence"]["predicate"])
        self.assertEqual(
            row["ground_spacecraft_divergence_interval"]["end_ns"],
            9_000_000_000,
        )
        self.assertTrue(
            row["ground_spacecraft_divergence_interval"][
                "right_censored_at_run_end"
            ]
        )

    def test_c06_contained_but_authority_convergence_is_right_censored(self) -> None:
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C06",
            observation=observation_for("C06"),
        )
        self.assertTrue(row["containment"]["predicate"])
        self.assertEqual(row["containment"]["observed_ns"], 4_000_000_000)
        self.assertFalse(row["authority_convergence"]["predicate"])
        self.assertIsNone(row["authority_convergence"]["observed_ns"])
        self.assertTrue(
            row["authority_convergence"]["right_censored_at_run_end"]
        )
        self.assertEqual(
            row["ground_spacecraft_divergence_interval"]["end_ns"],
            9_000_000_000,
        )

    def test_p1_and_p2_cells_close_divergence_on_observed_noop(self) -> None:
        for cell_id in ("C02", "C03", "C04", "C05", "C07"):
            row = derive_command_runtime_observation(
                pilot=PILOT,
                cell_id=cell_id,
                observation=observation_for(cell_id),
            )
            self.assertTrue(row["authority_convergence"]["predicate"])
            self.assertEqual(
                row["authority_convergence"]["observed_ns"],
                5_000_000_000,
            )
            self.assertFalse(
                row["ground_spacecraft_divergence_interval"][
                    "right_censored_at_run_end"
                ]
            )
            self.assertEqual(
                row["ground_spacecraft_divergence_interval"]["end_ns"],
                5_000_000_000,
            )

    def test_mo1_is_observation_derived_and_false_for_valid_e1_activation(self) -> None:
        for cell_id in EXPECTED:
            row = derive_command_runtime_observation(
                pilot=PILOT,
                cell_id=cell_id,
                observation=observation_for(cell_id),
            )
            self.assertFalse(row["objective_results"]["MO-1"]["completed"])

    def test_mo3_comes_from_observed_authorized_noop_marker(self) -> None:
        for cell_id in EXPECTED:
            row = derive_command_runtime_observation(
                pilot=PILOT,
                cell_id=cell_id,
                observation=observation_for(cell_id),
            )
            self.assertEqual(
                row["objective_results"]["MO-3"]["completed"],
                EXPECTED[cell_id][2],
            )

    def test_c06_legitimate_command_rejection_count_is_observed_one(self) -> None:
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C06",
            observation=observation_for("C06"),
        )
        self.assertEqual(row["legitimate_commands"]["attempted"], 1)
        self.assertEqual(row["legitimate_commands"]["rejected"], 1)

    def test_c01_legitimate_command_rejection_count_is_zero(self) -> None:
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C01",
            observation=observation_for("C01"),
        )
        self.assertEqual(row["legitimate_commands"]["attempted"], 1)
        self.assertEqual(row["legitimate_commands"]["rejected"], 0)

    def test_observed_run_end_not_expected_value_closes_nonconvergence(self) -> None:
        obs = observation_for("C06")
        obs["run_end_ns"] = 12_345_678_901
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C06",
            observation=obs,
        )
        self.assertEqual(
            row["ground_spacecraft_divergence_interval"]["end_ns"],
            12_345_678_901,
        )

    def test_observed_probe_timestamp_not_expected_value_sets_containment(self) -> None:
        obs = observation_for("C05")
        obs["second_attacker_probe_observed_ns"] = 4_321_000_000
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C05",
            observation=obs,
        )
        self.assertEqual(row["containment"]["observed_ns"], 4_321_000_000)

    def test_wrong_timestamp_order_is_rejected(self) -> None:
        obs = observation_for("C02")
        obs["second_attacker_probe_observed_ns"] = 6_000_000_000
        with self.assertRaisesRegex(ValueError, "out of order"):
            derive_command_runtime_observation(
                pilot=PILOT,
                cell_id="C02",
                observation=obs,
            )

    def test_event_success_after_enforcement_is_valid_nonoracle_order(self) -> None:
        obs = observation_for("C02")
        obs["policy_enforcement_ns"] = 2_000_000_000
        obs["event_success_ns"] = 3_000_000_000
        obs["second_attacker_probe_observed_ns"] = 4_000_000_000

        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C02",
            observation=obs,
        )

        self.assertTrue(row["event_success"]["predicate"])
        self.assertEqual(
            row["event_success"]["observed_ns"],
            3_000_000_000,
        )

    def test_event_success_before_activation_is_rejected(self) -> None:
        obs = observation_for("C02")
        obs["event_activation_ns"] = 2_500_000_000
        obs["event_success_ns"] = 2_000_000_000

        with self.assertRaisesRegex(ValueError, "out of order"):
            derive_command_runtime_observation(
                pilot=PILOT,
                cell_id="C02",
                observation=obs,
            )

    def test_wrong_effect_semantics_fail_acceptance_without_substitution(self) -> None:
        obs = observation_for("C02")
        obs["post_enforcement_attacker_reset_marker_delta"] = 2
        row = derive_command_runtime_observation(
            pilot=PILOT,
            cell_id="C02",
            observation=obs,
        )
        self.assertFalse(
            row["effect_acceptance"]["effect_semantics_met"]
        )
        with self.assertRaisesRegex(ValueError, "effects differ"):
            require_command_observation_acceptance(row)

    def test_expected_observations_pass_acceptance_for_all_cells(self) -> None:
        for cell_id in EXPECTED:
            row = derive_command_runtime_observation(
                pilot=PILOT,
                cell_id=cell_id,
                observation=observation_for(cell_id),
            )
            require_command_observation_acceptance(row)

    def test_contract_emits_no_primary_terminal_or_recovery_evidence(self) -> None:
        matrix = build_command_observation_matrix(PILOT)
        self.assertFalse(matrix["primary_metrics_emitted"])
        self.assertFalse(matrix["terminal_states_emitted"])
        self.assertFalse(matrix["recovery_evidence_emitted"])
        for cell_id in EXPECTED:
            row = derive_command_runtime_observation(
                pilot=PILOT,
                cell_id=cell_id,
                observation=observation_for(cell_id),
            )
            self.assertFalse(row["primary_metrics_emitted"])
            self.assertFalse(row["terminal_state_emitted"])
            self.assertFalse(row["recovery_evidence_emitted"])
            self.assertFalse(
                row["expected_values_used_as_raw_metric_inputs"]
            )

    def test_r030_is_offline_and_pilot_gate_remains_closed(self) -> None:
        matrix = build_command_observation_matrix(PILOT)
        self.assertFalse(matrix["runtime_execution_authorized"])
        self.assertFalse(matrix["pilot_seed_consumed"])
        self.assertFalse(matrix["pilot_data_generated"])
        gate = PILOT["instrumentation_gate"]
        self.assertFalse(gate["pilot_execution_authorized"])
        self.assertTrue(
            gate["component_status"]["stage_1_command_observation_contract"]
        )
        self.assertFalse(
            gate["component_status"]["stage_1_family_runtime_dispatch_adapters"]
        )


if __name__ == "__main__":
    unittest.main()
