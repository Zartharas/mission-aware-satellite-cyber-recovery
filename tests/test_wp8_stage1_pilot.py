from __future__ import annotations

import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from src.mission_recovery.wp8_stage1_pilot import (
    allocate_run_id,
    bind_stage1_runtime_observation,
    build_offline_stage1_plan,
    deterministic_stage1_cell_ids,
    dispatch_for_cell,
    new_stage1_ledger,
    record_attempt,
    stage1_progress,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(encoding="utf-8")
)
TOOLCHAIN = json.loads(
    (ROOT / "configs" / "toolchain-lock.json").read_text(encoding="utf-8")
)
SCHEMA = json.loads(
    (ROOT / "configs" / "experiment_run.schema.json").read_text(encoding="utf-8")
)


def command_observation_bundle(*, run_id: str) -> dict:
    return {
        "factor_context": {
            "run_id": run_id,
            "model_version": "0.3.0",
            "seed": 101,
            "mission_state_id": "M0",
            "event_id": "E1",
            "policy_id": "P1",
            "contact_condition_id": "C0",
            "evidence_condition_id": "T0",
        },
        "execution_metadata": {
            "effective_policy_id": "P1",
        },
        "runtime_observation": {
            "family": "command",
            "clock": {
                "run_start_utc": "2026-08-17T20:00:00Z",
                "run_end_utc": "2026-08-17T20:00:10Z",
                "run_start_ns": 1_000_000_000,
                "event_activation_ns": 2_000_000_000,
                "containment_ns": 4_000_000_000,
                "trusted_recovery_ns": None,
                "run_end_ns": 11_000_000_000,
            },
            "event_success": {
                "predicate": True,
                "observed_ns": 2_500_000_000,
                "evidence_ref": "unit:stage1:event-success",
            },
            "objective_results": {
                "MO-1": {
                    "completed": False,
                    "evidence_ref": "unit:stage1:unauthorized-effect",
                },
                "MO-3": {
                    "completed": True,
                    "evidence_ref": "unit:stage1:authorized-noop",
                },
            },
            "invariant_violation_intervals": [],
            "legitimate_commands": {
                "attempted": 2,
                "rejected": 0,
                "evidence_ref": "unit:stage1:legitimate-commands",
            },
            "ground_spacecraft_divergence_intervals": [],
            "recovery_observations": {
                "authorization_valid": {
                    "available_current": True,
                    "criterion_satisfied": True,
                    "evidence_ref": "unit:stage1:authorization",
                },
                "authorized_command_path_restored": {
                    "available_current": True,
                    "criterion_satisfied": True,
                    "evidence_ref": "unit:stage1:authorized-path",
                },
                "ground_spacecraft_state_agreed": {
                    "available_current": True,
                    "criterion_satisfied": True,
                    "evidence_ref": "unit:stage1:agreement",
                },
                "health_checks_passed": {
                    "available_current": True,
                    "criterion_satisfied": True,
                    "evidence_ref": "unit:stage1:health",
                },
                "recovery_manifest_complete": {
                    "available_current": True,
                    "criterion_satisfied": False,
                    "evidence_ref": "unit:stage1:manifest",
                },
            },
            "recovery_checklist_excluded": [
                "approved_version",
                "integrity_measurement_valid",
                "measured_state_current",
                "required_telemetry_restored",
                "no_residual_unauthorized_state",
            ],
            "terminal_state_predicates": {
                "run_invalid": False,
                "mission_loss": False,
                "trusted_recovery_confirmed": False,
                "operational_restored": True,
                "recovery_failed": False,
                "contained": True,
            },
            "containment_evidence_ref": "unit:stage1:containment",
            "trusted_recovery_evidence_ref": None,
            "terminal_state_evidence_refs": ["unit:stage1:terminal"],
            "source_observation_refs": ["unit:stage1:source"],
            "development_preflight": False,
            "pilot_data": True,
        },
        "notes": "offline Stage-1 runner contract fixture only",
    }


def add_valid_attempt(pilot: dict, ledger: dict, cell_id: str, index: int) -> None:
    record_attempt(
        pilot=pilot,
        ledger=ledger,
        cell_id=cell_id,
        run_id=f"unit-stage1-valid-{index:02d}",
        status="VALID",
        retained_evidence_ref=f"unit:evidence:{cell_id}:{index}",
        schema_valid=True,
        raw_metric_inputs_complete=True,
        expected_policy_semantics_met=True,
    )


class WP8Stage1PilotTests(unittest.TestCase):
    def test_plan_reads_cells_from_pilot_config(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"][
            "pilot_execution_authorized"
        ] = False
        pilot["cells"][0]["primary_role"] = "unit_mutated_role"
        plan = build_offline_stage1_plan(pilot)
        planned = {
            row["cell"]["cell_id"]: row["cell"]
            for row in plan["planned_cells"]
        }
        self.assertEqual(planned["C01"]["primary_role"], "unit_mutated_role")
        self.assertEqual(set(planned), set(pilot["stage_1_control_validity"]["cell_ids"]))

    def test_seed101_order_is_frozen_sha256_rank(self) -> None:
        self.assertEqual(
            deterministic_stage1_cell_ids(PILOT),
            [
                "C05",
                "R04",
                "C04",
                "R01",
                "R03",
                "C02",
                "R02",
                "C03",
                "O01",
                "C07",
                "C01",
                "C06",
            ],
        )

    def test_offline_plan_does_not_consume_seed_or_generate_pilot_data(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = False
        plan = build_offline_stage1_plan(pilot)
        self.assertFalse(plan["runtime_execution_authorized"])
        self.assertFalse(plan["pilot_seed_consumed"])
        self.assertFalse(plan["pilot_data_generated"])
        self.assertEqual(plan["seed"], 101)

    def test_dispatch_maps_all_declared_cells_to_runtime_family(self) -> None:
        counts = {"command": 0, "recovery": 0, "observability": 0}
        for cell in PILOT["cells"]:
            dispatch = dispatch_for_cell(PILOT, cell)
            counts[dispatch["runtime_family"]] += 1
            self.assertTrue(dispatch["pilot_executor_ready"])
        self.assertEqual(counts, {"command": 7, "recovery": 4, "observability": 1})

    def test_run_id_allocator_produces_unique_attempt_ids(self) -> None:
        now = datetime(2026, 8, 17, 20, 0, 0, tzinfo=timezone.utc)
        one = allocate_run_id(
            cell_id="C02",
            seed=101,
            now=now,
            token_factory=lambda: "a1",
        )
        two = allocate_run_id(
            cell_id="C02",
            seed=101,
            now=now,
            token_factory=lambda: "b2",
        )
        self.assertNotEqual(one, two)
        self.assertIn("wp8-stage1-c02-s101", one)
        self.assertIn("wp8-stage1-c02-s101", two)

    def test_duplicate_run_id_is_rejected(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        add_valid_attempt(PILOT, ledger, "C01", 1)
        with self.assertRaisesRegex(ValueError, "duplicate Stage-1 run_id"):
            record_attempt(
                pilot=PILOT,
                ledger=ledger,
                cell_id="C02",
                run_id="unit-stage1-valid-01",
                status="VALID",
                retained_evidence_ref="unit:evidence:C02",
                schema_valid=True,
                raw_metric_inputs_complete=True,
                expected_policy_semantics_met=True,
            )

    def test_invalid_attempt_is_retained_and_replacement_keeps_seed(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        record_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="C01",
            run_id="unit-invalid-c01",
            status="RUN_INVALID",
            retained_evidence_ref="unit:evidence:invalid-c01",
            invalid_class="non_infrastructure",
            invalid_cause="measurement_fixture_failure",
        )
        add_valid_attempt(PILOT, ledger, "C01", 2)
        self.assertEqual(len(ledger["attempts"]), 2)
        self.assertEqual(ledger["attempts"][0]["status"], "RUN_INVALID")
        self.assertEqual(ledger["attempts"][0]["seed"], 101)
        self.assertEqual(ledger["attempts"][1]["seed"], 101)
        progress = stage1_progress(PILOT, ledger)
        self.assertEqual(progress["replacement_attempt_seed"], 101)
        self.assertEqual(progress["valid_cell_count"], 1)

    def test_stage2_is_blocked_until_every_stage1_cell_is_valid(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        ids = PILOT["stage_1_control_validity"]["cell_ids"]
        for index, cell_id in enumerate(ids[:-1], start=1):
            add_valid_attempt(PILOT, ledger, cell_id, index)
        progress = stage1_progress(PILOT, ledger)
        self.assertFalse(progress["stage_1_all_cells_valid"])
        self.assertFalse(progress["stage_2_progression_gate_passed"])
        self.assertEqual(progress["missing_valid_cells"], [ids[-1]])

    def test_stage2_gate_passes_only_after_all_stage1_cells_are_valid(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        ids = PILOT["stage_1_control_validity"]["cell_ids"]
        for index, cell_id in enumerate(ids, start=1):
            add_valid_attempt(PILOT, ledger, cell_id, index)
        progress = stage1_progress(PILOT, ledger)
        self.assertTrue(progress["stage_1_all_cells_valid"])
        self.assertTrue(progress["stage_2_progression_gate_passed"])
        self.assertEqual(progress["missing_valid_cells"], [])

    def test_infrastructure_fraction_uses_declared_cell_denominator(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        record_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="C01",
            run_id="unit-infra-1",
            status="RUN_INVALID",
            retained_evidence_ref="unit:evidence:infra-1",
            invalid_class="infrastructure",
            invalid_cause="infra_cause_one",
        )
        one = stage1_progress(PILOT, ledger)
        self.assertAlmostEqual(one["infrastructure_invalid_fraction"], 1 / 12)
        self.assertFalse(one["pilot_halt_required"])

        record_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="C02",
            run_id="unit-infra-2",
            status="RUN_INVALID",
            retained_evidence_ref="unit:evidence:infra-2",
            invalid_class="infrastructure",
            invalid_cause="infra_cause_two",
        )
        two = stage1_progress(PILOT, ledger)
        self.assertAlmostEqual(two["infrastructure_invalid_fraction"], 2 / 12)
        self.assertTrue(two["pilot_halt_required"])

    def test_repeated_same_infrastructure_cause_halts_progression(self) -> None:
        ledger = new_stage1_ledger(PILOT)
        for index, cell_id in enumerate(["C01", "C02"], start=1):
            record_attempt(
                pilot=PILOT,
                ledger=ledger,
                cell_id=cell_id,
                run_id=f"unit-repeat-infra-{index}",
                status="RUN_INVALID",
                retained_evidence_ref=f"unit:evidence:repeat-{index}",
                invalid_class="infrastructure",
                invalid_cause="same_startup_failure",
            )
        progress = stage1_progress(PILOT, ledger)
        self.assertEqual(
            progress["repeated_infrastructure_causes"],
            ["same_startup_failure"],
        )
        self.assertTrue(progress["pilot_halt_required"])
        self.assertFalse(progress["stage_2_progression_gate_passed"])

    def test_explicit_false_gate_refuses_pilot_binding(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = False
        run_id = "unit-stage1-c02-blocked"
        with self.assertRaisesRegex(PermissionError, "not authorized"):
            bind_stage1_runtime_observation(
                pilot=pilot,
                toolchain=TOOLCHAIN,
                schema=SCHEMA,
                cell_id="C02",
                run_id=run_id,
                observation_bundle=command_observation_bundle(run_id=run_id),
                snapshot_id="unit-stage1",
                host_architecture="x86_64",
            )

    def test_authorized_fixture_binds_observation_and_scores_without_expected_substitution(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = True
        run_id = "unit-stage1-c02-authorized"
        result = bind_stage1_runtime_observation(
            pilot=pilot,
            toolchain=TOOLCHAIN,
            schema=SCHEMA,
            cell_id="C02",
            run_id=run_id,
            observation_bundle=command_observation_bundle(run_id=run_id),
            snapshot_id="unit-stage1",
            host_architecture="x86_64",
        )
        record = result["run_record"]
        self.assertTrue(record["outcomes"]["unauthorized_effect_completed"])
        self.assertEqual(record["outcomes"]["mission_objective_completion_ratio"], 0.5)
        self.assertEqual(record["timing"]["containment_s"], 2.0)
        self.assertTrue(result["binding_provenance"]["pilot_data"])
        self.assertFalse(result["binding_provenance"]["development_preflight"])
        self.assertTrue(result["stage1_acceptance"]["schema_valid"])
        self.assertEqual(record["outcomes"]["evidence_completeness_ratio"], 1.0)
        self.assertFalse(record["recovery_evidence"]["recovery_manifest_complete"])

    def test_pilot_observation_requires_explicit_criterion_satisfied(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = True
        run_id = "unit-stage1-missing-criterion-satisfaction"
        bundle = command_observation_bundle(run_id=run_id)
        del bundle["runtime_observation"]["recovery_observations"][
            "recovery_manifest_complete"
        ]["criterion_satisfied"]
        with self.assertRaisesRegex(ValueError, "explicit criterion_satisfied"):
            bind_stage1_runtime_observation(
                pilot=pilot,
                toolchain=TOOLCHAIN,
                schema=SCHEMA,
                cell_id="C02",
                run_id=run_id,
                observation_bundle=bundle,
                snapshot_id="unit-stage1",
                host_architecture="x86_64",
            )

    def test_missing_actual_effective_policy_is_rejected(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = True
        run_id = "unit-stage1-missing-policy"
        bundle = command_observation_bundle(run_id=run_id)
        del bundle["execution_metadata"]["effective_policy_id"]
        with self.assertRaisesRegex(ValueError, "actual effective policy"):
            bind_stage1_runtime_observation(
                pilot=pilot,
                toolchain=TOOLCHAIN,
                schema=SCHEMA,
                cell_id="C02",
                run_id=run_id,
                observation_bundle=bundle,
                snapshot_id="unit-stage1",
            )

    def test_wrong_actual_effective_policy_is_rejected_not_substituted(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = True
        run_id = "unit-stage1-wrong-policy"
        bundle = command_observation_bundle(run_id=run_id)
        bundle["execution_metadata"]["effective_policy_id"] = "P2"
        with self.assertRaisesRegex(ValueError, "differs from frozen cell semantics"):
            bind_stage1_runtime_observation(
                pilot=pilot,
                toolchain=TOOLCHAIN,
                schema=SCHEMA,
                cell_id="C02",
                run_id=run_id,
                observation_bundle=bundle,
                snapshot_id="unit-stage1",
            )

    def test_pilot_observation_requires_explicit_pilot_data_marker(self) -> None:
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"]["pilot_execution_authorized"] = True
        run_id = "unit-stage1-missing-pilot-marker"
        bundle = command_observation_bundle(run_id=run_id)
        del bundle["runtime_observation"]["pilot_data"]
        with self.assertRaisesRegex(ValueError, "pilot_data=true"):
            bind_stage1_runtime_observation(
                pilot=pilot,
                toolchain=TOOLCHAIN,
                schema=SCHEMA,
                cell_id="C02",
                run_id=run_id,
                observation_bundle=bundle,
                snapshot_id="unit-stage1",
            )


if __name__ == "__main__":
    unittest.main()
