from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.mission_recovery.wp8_command_runtime_executor import (
    STATIC_DEVELOPMENT_SEED,
    build_development_execution_plan,
    build_static_development_matrix,
    finalize_raw_observation,
    reserved_pilot_seeds,
    select_runtime_policy,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(encoding="utf-8")
)
RUNNER = (
    ROOT / "scripts" / "run_wp8_command_stage1_development.sh"
).read_text(encoding="utf-8")

EXPECTED = {
    "C01": ("P0", "OBSERVE_ONLY", 2, 1, True, True, True),
    "C02": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1, False, False, True),
    "C03": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1, False, False, True),
    "C04": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1, False, False, True),
    "C05": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1, False, False, True),
    "C06": ("P4", "ENTER_SAFE_MODE", 0, 0, False, False, False),
    "C07": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1, False, False, True),
}


def plan(cell_id: str, seed: int = STATIC_DEVELOPMENT_SEED):
    return build_development_execution_plan(
        PILOT,
        cell_id=cell_id,
        development_seed=seed,
        run_id=f"unit-r032-{cell_id.lower()}-s{seed}",
    )


def gateway_rows(cell_id: str):
    effective, action, _, _, attacker_forwarded, _, noop_forwarded = EXPECTED[
        cell_id
    ]
    return [
        {
            "action": action,
            "source_id": "modeled_attacker",
            "command_class": "sample_reset_counters",
            "forwarded": attacker_forwarded,
        },
        {
            "action": action,
            "source_id": "modeled_attacker",
            "command_class": "sample_reset_counters",
            "forwarded": attacker_forwarded,
        },
        {
            "action": action,
            "source_id": "authorized_ground",
            "command_class": "sample_noop",
            "forwarded": noop_forwarded,
        },
    ]


def measurement_for(cell_id: str, run_id: str):
    _, _, attacker_delta, noop_delta, _, _, _ = EXPECTED[cell_id]
    return {
        "schema": 1,
        "run_id": run_id,
        "counts": {
            "reset_before_event": 10,
            "reset_after_event": 11,
            "reset_before_attacker": 11,
            "reset_after_attacker": 11 + attacker_delta,
            "noop_before": 3,
            "noop_after": 3 + noop_delta,
        },
        "timestamps_ns": {
            "event_activation_ns": 1_000_000_000,
            "event_success_ns": 3_000_000_000,
            "policy_enforcement_ns": 2_000_000_000,
            "second_attacker_probe_observed_ns": 4_000_000_000,
            "authorized_noop_probe_observed_ns": 5_000_000_000,
            "run_end_ns": 9_000_000_000,
        },
        "development_preflight": True,
        "pilot_data": False,
        "pilot_seed_consumed": False,
    }


class WP8CommandRuntimeExecutorTests(unittest.TestCase):
    def test_reserved_pilot_seeds_cover_stage1_and_stage2(self) -> None:
        self.assertEqual(
            reserved_pilot_seeds(PILOT),
            {101, 202, 303, 404, 505},
        )

    def test_stage1_seed_is_rejected_for_development(self) -> None:
        with self.assertRaisesRegex(ValueError, "collides"):
            plan("C02", 101)

    def test_stage2_seed_is_rejected_for_development(self) -> None:
        for seed in (202, 303, 404, 505):
            with self.assertRaisesRegex(ValueError, "collides"):
                plan("C02", seed)

    def test_static_development_seed_is_nonpilot(self) -> None:
        self.assertNotIn(
            STATIC_DEVELOPMENT_SEED,
            reserved_pilot_seeds(PILOT),
        )

    def test_plan_covers_exact_cell_factors(self) -> None:
        row = plan("C06")
        factor = row["factor_context"]
        self.assertEqual(factor["mission_state_id"], "M2")
        self.assertEqual(factor["event_id"], "E1")
        self.assertEqual(factor["policy_id"], "P7")
        self.assertEqual(factor["contact_condition_id"], "C0")
        self.assertEqual(factor["evidence_condition_id"], "T1")
        self.assertEqual(factor["seed"], STATIC_DEVELOPMENT_SEED)

    def test_runtime_policy_preview_matrix(self) -> None:
        matrix = build_static_development_matrix(PILOT)
        actual = {
            row["cell_id"]: (
                row["actual_effective_policy_id"],
                row["selected_action"],
            )
            for row in matrix["rows"]
        }
        expected = {
            cell_id: (values[0], values[1])
            for cell_id, values in EXPECTED.items()
        }
        self.assertEqual(actual, expected)

    def test_p7_c03_runtime_selection_delegates_to_p1(self) -> None:
        row = plan("C03")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C03",
            event=row["event_instance"],
        )
        self.assertEqual(decision["delegated_policy_id"], "P1")
        self.assertEqual(decision["selected_action"], "ISOLATE_MODELED_SOURCE")

    def test_p7_c05_runtime_selection_delegates_to_p2(self) -> None:
        row = plan("C05")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C05",
            event=row["event_instance"],
        )
        self.assertEqual(decision["delegated_policy_id"], "P2")
        self.assertEqual(
            decision["selected_action"],
            "RESTRICT_HIGH_RISK_COMMANDS",
        )

    def test_p7_c06_runtime_selection_delegates_to_p4(self) -> None:
        row = plan("C06")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C06",
            event=row["event_instance"],
        )
        self.assertEqual(decision["delegated_policy_id"], "P4")
        self.assertEqual(decision["selected_action"], "ENTER_SAFE_MODE")

    def test_runtime_policy_never_reads_ground_truth(self) -> None:
        for cell_id in EXPECTED:
            row = plan(cell_id)
            decision = select_runtime_policy(
                PILOT,
                cell_id=cell_id,
                event=row["event_instance"],
            )
            self.assertFalse(decision["oracle_ground_truth_read"])

    def test_finalize_expected_observation_all_cells(self) -> None:
        for cell_id in EXPECTED:
            row = plan(cell_id)
            decision = select_runtime_policy(
                PILOT,
                cell_id=cell_id,
                event=row["event_instance"],
            )
            result = finalize_raw_observation(
                PILOT,
                cell_id=cell_id,
                factor=row["factor_context"],
                policy_decision=decision,
                gateway_rows=gateway_rows(cell_id),
                measurement=measurement_for(
                    cell_id,
                    row["factor_context"]["run_id"],
                ),
            )
            self.assertFalse(result["runtime_binding_performed"])
            self.assertFalse(result["primary_metrics_emitted"])
            self.assertFalse(result["terminal_state_emitted"])

    def test_finalize_c01_preserves_noncontainment_censoring(self) -> None:
        row = plan("C01")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C01",
            event=row["event_instance"],
        )
        result = finalize_raw_observation(
            PILOT,
            cell_id="C01",
            factor=row["factor_context"],
            policy_decision=decision,
            gateway_rows=gateway_rows("C01"),
            measurement=measurement_for(
                "C01",
                row["factor_context"]["run_id"],
            ),
        )
        derived = result["derived_command_observation"]
        self.assertFalse(derived["containment"]["predicate"])
        self.assertTrue(
            derived["ground_spacecraft_divergence_interval"][
                "right_censored_at_run_end"
            ]
        )

    def test_finalize_c06_preserves_containment_without_convergence(self) -> None:
        row = plan("C06")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C06",
            event=row["event_instance"],
        )
        result = finalize_raw_observation(
            PILOT,
            cell_id="C06",
            factor=row["factor_context"],
            policy_decision=decision,
            gateway_rows=gateway_rows("C06"),
            measurement=measurement_for(
                "C06",
                row["factor_context"]["run_id"],
            ),
        )
        derived = result["derived_command_observation"]
        self.assertTrue(derived["containment"]["predicate"])
        self.assertFalse(derived["authority_convergence"]["predicate"])

    def test_wrong_gateway_forwarding_is_rejected(self) -> None:
        row = plan("C02")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C02",
            event=row["event_instance"],
        )
        decisions = gateway_rows("C02")
        decisions[0]["forwarded"] = True
        with self.assertRaisesRegex(ValueError, "forwarding differs"):
            finalize_raw_observation(
                PILOT,
                cell_id="C02",
                factor=row["factor_context"],
                policy_decision=decision,
                gateway_rows=decisions,
                measurement=measurement_for(
                    "C02",
                    row["factor_context"]["run_id"],
                ),
            )

    def test_wrong_marker_effect_is_rejected(self) -> None:
        row = plan("C02")
        decision = select_runtime_policy(
            PILOT,
            cell_id="C02",
            event=row["event_instance"],
        )
        measurement = measurement_for(
            "C02",
            row["factor_context"]["run_id"],
        )
        measurement["counts"]["reset_after_attacker"] += 2
        with self.assertRaisesRegex(ValueError, "effects differ"):
            finalize_raw_observation(
                PILOT,
                cell_id="C02",
                factor=row["factor_context"],
                policy_decision=decision,
                gateway_rows=gateway_rows("C02"),
                measurement=measurement,
            )

    def test_runner_preflight_precedes_nominal_runtime(self) -> None:
        plan_index = RUNNER.index('PHASE="DEVELOPMENT_PLAN_PREFLIGHT"')
        nominal_index = RUNNER.index('PHASE="NOMINAL_RUNTIME_LAUNCH"')
        self.assertLess(plan_index, nominal_index)

    def test_runner_runtime_policy_selection_is_post_activation_and_dynamic(self) -> None:
        activation = RUNNER.index('PHASE="EVENT_ACTIVATION"')
        selection = RUNNER.index('PHASE="POLICY_SELECTION"')
        enforcement = RUNNER.index('PHASE="POLICY_ENFORCEMENT"')
        self.assertLess(activation, selection)
        self.assertLess(selection, enforcement)
        self.assertIn('--action "$SELECTED_ACTION"', RUNNER)
        self.assertNotIn("--action ISOLATE_MODELED_SOURCE", RUNNER)

    def test_runner_stops_before_binding_and_marks_nonpilot(self) -> None:
        self.assertNotIn("wp8_runtime_binding", RUNNER)
        self.assertIn("finalize-observation", RUNNER)
        self.assertIn("runtime_binding_performed=false", RUNNER)
        self.assertIn("primary_metrics_emitted=false", RUNNER)
        self.assertIn("terminal_state_emitted=false", RUNNER)
        self.assertIn("development_preflight=true", RUNNER)
        self.assertIn("pilot_data=false", RUNNER)
        self.assertIn("pilot_seed_consumed=false", RUNNER)


if __name__ == "__main__":
    unittest.main()
