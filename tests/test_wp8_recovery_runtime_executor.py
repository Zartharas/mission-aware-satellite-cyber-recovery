import json
import unittest
from pathlib import Path

from src.mission_recovery.wp8_recovery_effect_contract import (
    build_recovery_cell_effect_contract,
)
from src.mission_recovery.wp8_recovery_runtime_executor import (
    DEVELOPMENT_VALIDATION_CELLS,
    build_development_execution_plan,
    build_development_observation,
    prepare_verified_rollback,
    reserved_pilot_seeds,
    select_runtime_policy,
    validate_recovery_runtime_executor_contract,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs/wp8_pilot_design.json").read_text(encoding="utf-8")
)


def measurement(cell_id: str) -> dict:
    effect = build_recovery_cell_effect_contract(PILOT, cell_id)
    family = effect["effect_dispatch"]["effect_family"]
    artifacts = effect["event_artifacts"]
    contained = family == "rollback_request"
    row = {
        "event_slot_sha256": artifacts["tampered_sha256"],
        "post_response_slot_sha256": (
            artifacts["approved_sha256"] if contained else artifacts["tampered_sha256"]
        ),
        "rejected_sha256_absent": contained,
        "temporary_recovery_state_absent": True,
        "rollback_request_emitted": contained,
        "rollback_request_validated": contained,
        "replacement_source_verified": contained,
        "event_activation_ns": 100,
        "event_success_ns": 105,
        "policy_selection_ns": 110,
        "policy_enforcement_ns": 120,
        "post_response_slot_observed_ns": 130,
        "authorized_noop_probe_observed_ns": 140,
        "criteria_classification_ns": 150,
        "run_end_ns": 160,
        "authorized_noop_marker_delta": 1,
    }
    if family == "command_gateway":
        row.update({
            "matched_attacker_probe_count": 2,
            "attacker_reset_marker_delta": 0,
            "command_gateway_probe_observed_ns": 135,
        })
    return row


class RecoveryRuntimeExecutorTests(unittest.TestCase):
    def test_contract_is_static_and_pilot_blocked(self) -> None:
        validate_recovery_runtime_executor_contract(PILOT)
        contract = PILOT["stage_1_runner_contract"]["recovery_runtime_executor_contract"]
        self.assertTrue(contract["development_only"])
        self.assertFalse(contract["pilot_executor_ready"])
        self.assertFalse(PILOT["instrumentation_gate"]["pilot_execution_authorized"])

    def test_discriminator_cells_are_minimal_three(self) -> None:
        self.assertEqual(DEVELOPMENT_VALIDATION_CELLS, ("R01", "R02", "R04"))

    def test_reserved_pilot_seeds_rejected(self) -> None:
        self.assertEqual(reserved_pilot_seeds(PILOT), {101, 202, 303, 404, 505})
        for seed in reserved_pilot_seeds(PILOT):
            with self.assertRaisesRegex(ValueError, "collides with frozen pilot seed"):
                build_development_execution_plan(
                    PILOT,
                    cell_id="R01",
                    development_seed=seed,
                    run_id=f"bad-{seed}",
                    repo_commit="unit",
                )

    def test_plan_supports_all_recovery_cells(self) -> None:
        expected = {
            "R01": ("P0", "observe_only"),
            "R02": ("P5", "rollback_request"),
            "R03": ("P7", "rollback_request"),
            "R04": ("P7", "command_gateway"),
        }
        for index, (cell, values) in enumerate(expected.items(), start=1):
            plan = build_development_execution_plan(
                PILOT,
                cell_id=cell,
                development_seed=9500 + index,
                run_id=f"unit-{cell}",
                repo_commit="unit",
            )
            self.assertEqual(plan["factor_context"]["policy_id"], values[0])
            self.assertEqual(plan["effect_family_for_acceptance_only"], values[1])
            self.assertFalse(plan["pilot_data"])
            self.assertFalse(plan["pilot_seed_consumed"])

    def test_policy_selection_is_non_oracle(self) -> None:
        for cell, seed in (("R01", 9511), ("R02", 9512), ("R03", 9513), ("R04", 9514)):
            plan = build_development_execution_plan(
                PILOT,
                cell_id=cell,
                development_seed=seed,
                run_id=f"policy-{cell}",
                repo_commit="unit",
            )
            decision = select_runtime_policy(
                PILOT,
                cell_id=cell,
                event=plan["event_instance"],
            )
            self.assertFalse(decision["oracle_ground_truth_read"])

    def test_verified_rollback_material_is_valid(self) -> None:
        plan = build_development_execution_plan(
            PILOT,
            cell_id="R02",
            development_seed=9520,
            run_id="rollback-r02",
            repo_commit="unit",
        )
        policy = select_runtime_policy(PILOT, cell_id="R02", event=plan["event_instance"])
        result = prepare_verified_rollback(
            event=plan["event_instance"],
            policy_decision=policy,
        )
        self.assertTrue(result["rollback_request_validated"])
        self.assertEqual(
            result["rollback_request_validation"]["reasons"],
            [],
        )
        self.assertTrue(
            result["rollback_request_validation"]["accepted"]
        )
        self.assertTrue(result["replacement_source_verified"])
        self.assertEqual(
            result["replacement_source_verification"]["reasons"],
            [],
        )
        self.assertTrue(
            result["replacement_source_verification"]["accepted"]
        )
        self.assertFalse(result["recovery_execution_performed"])

    def test_r01_runtime_observation_is_uncontained(self) -> None:
        plan = build_development_execution_plan(
            PILOT, cell_id="R01", development_seed=9531,
            run_id="r01", repo_commit="unit",
        )
        policy = select_runtime_policy(PILOT, cell_id="R01", event=plan["event_instance"])
        result = build_development_observation(
            PILOT, cell_id="R01", policy_decision=policy,
            measurement=measurement("R01"), evidence_prefix="results/unit/r01",
        )
        self.assertFalse(result["derived_observation"]["containment"]["predicate"])

    def test_r02_runtime_observation_proves_containment_not_duplicate_trust(self) -> None:
        plan = build_development_execution_plan(
            PILOT, cell_id="R02", development_seed=9532,
            run_id="r02", repo_commit="unit",
        )
        policy = select_runtime_policy(PILOT, cell_id="R02", event=plan["event_instance"])
        result = build_development_observation(
            PILOT, cell_id="R02", policy_decision=policy,
            measurement=measurement("R02"), evidence_prefix="results/unit/r02",
        )
        derived = result["derived_observation"]
        self.assertTrue(derived["containment"]["predicate"])
        self.assertFalse(derived["trusted_recovery"]["predicate"])
        self.assertFalse(result["development_evidence_scope"]["trusted_recovery_runtime_claimed"])

    def test_r04_runtime_observation_separates_mitigation(self) -> None:
        plan = build_development_execution_plan(
            PILOT, cell_id="R04", development_seed=9534,
            run_id="r04", repo_commit="unit",
        )
        policy = select_runtime_policy(PILOT, cell_id="R04", event=plan["event_instance"])
        result = build_development_observation(
            PILOT, cell_id="R04", policy_decision=policy,
            measurement=measurement("R04"), evidence_prefix="results/unit/r04",
        )
        derived = result["derived_observation"]
        self.assertTrue(derived["command_path_mitigation"]["predicate"])
        self.assertFalse(derived["containment"]["predicate"])

    def test_unmeasured_development_criteria_are_not_imputed(self) -> None:
        plan = build_development_execution_plan(
            PILOT, cell_id="R02", development_seed=9542,
            run_id="scope-r02", repo_commit="unit",
        )
        policy = select_runtime_policy(PILOT, cell_id="R02", event=plan["event_instance"])
        result = build_development_observation(
            PILOT, cell_id="R02", policy_decision=policy,
            measurement=measurement("R02"), evidence_prefix="results/unit/r02",
        )
        rows = result["raw_observation"]["recovery_criteria"]
        for key in (
            "required_telemetry_restored",
            "health_checks_passed",
            "recovery_manifest_complete",
        ):
            self.assertFalse(rows[key]["available_current"])
            self.assertFalse(rows[key]["criterion_satisfied"])


    def test_runner_requires_observer_ready_before_t0(self) -> None:
        runner = (
            ROOT
            / "scripts"
            / "run_wp8_recovery_stage1_development.sh"
        )
        text = runner.read_text(encoding="utf-8")

        self.assertIn(
            "WP8_EVENT_SLOT_WATCHER_READY",
            text,
        )
        self.assertIn(
            "event_success_observer_ready_before_t0=true",
            text,
        )

        ready = text.index(
            'echo "event_success_observer_ready_before_t0=true"'
        )
        activation = text.index(
            'PHASE="EVENT_ACTIVATION"'
        )

        self.assertLess(ready, activation)


if __name__ == "__main__":
    unittest.main()
