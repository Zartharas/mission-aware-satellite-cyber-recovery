from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp8_runtime_binding import (
    bind_invalid_runtime_observation,
    bind_runtime_observation,
    environment_from_toolchain_lock,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)
SCHEMA = json.loads(
    (ROOT / "configs" / "experiment_run.schema.json").read_text(
        encoding="utf-8"
    )
)
TOOLCHAIN = json.loads(
    (ROOT / "configs" / "toolchain-lock.json").read_text(
        encoding="utf-8"
    )
)
VALIDATOR = Draft202012Validator(
    SCHEMA,
    format_checker=FormatChecker(),
)


def factor_context(
    *,
    family: str,
) -> dict:
    if family == "command":
        return {
            "run_id": "wp8-binding-command-test",
            "model_version": "0.3.0",
            "seed": 101,
            "mission_state_id": "M0",
            "event_id": "E1",
            "policy_id": "P1",
            "contact_condition_id": "C0",
            "evidence_condition_id": "T0",
        }
    if family == "recovery":
        return {
            "run_id": "wp8-binding-recovery-test",
            "model_version": "0.3.0",
            "seed": 101,
            "mission_state_id": "M4",
            "event_id": "E3",
            "policy_id": "P5",
            "contact_condition_id": "C0",
            "evidence_condition_id": "T0",
        }
    return {
        "run_id": "wp8-binding-observability-test",
        "model_version": "0.3.0",
        "seed": 101,
        "mission_state_id": "M2",
        "event_id": "E4",
        "policy_id": "P7",
        "contact_condition_id": "C0",
        "evidence_condition_id": "T0",
    }


def environment() -> dict:
    return environment_from_toolchain_lock(
        TOOLCHAIN,
        snapshot_id="wp8-binding-unit-test",
        host_architecture="x86_64",
    )


def clock(
    *,
    containment: bool,
    recovery: bool,
) -> dict:
    return {
        "run_start_utc": "2026-08-15T20:00:00Z",
        "run_end_utc": "2026-08-15T20:00:10Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": 2_000_000_000,
        "containment_ns": 4_000_000_000 if containment else None,
        "trusted_recovery_ns": 7_000_000_000 if recovery else None,
        "run_end_ns": 11_000_000_000,
    }


def recovery_partition(
    applicable: dict[str, bool],
) -> tuple[dict, list[str]]:
    rows = {
        key: {
            "available_current": value,
            "evidence_ref": f"unit:{key}",
        }
        for key, value in applicable.items()
    }
    excluded = [
        key
        for key in RECOVERY_CRITERIA
        if key not in applicable
    ]
    return rows, excluded


def base_observation(
    *,
    family: str,
    containment: bool,
    recovery: bool,
) -> dict:
    if family == "command":
        objectives = {
            "MO-1": {
                "completed": True,
                "evidence_ref": "unit:attacker-reset-marker",
            },
            "MO-3": {
                "completed": True,
                "evidence_ref": "unit:authorized-noop-marker",
            },
        }
        applicable = {
            "authorization_valid": True,
            "authorized_command_path_restored": True,
            "ground_spacecraft_state_agreed": True,
            "health_checks_passed": True,
            "recovery_manifest_complete": True,
        }
    elif family == "recovery":
        objectives = {
            "MO-4": {
                "completed": True,
                "evidence_ref": "unit:terminal-verification",
            },
            "MO-5": {
                "completed": True,
                "evidence_ref": "unit:recovery-evidence-set",
            },
        }
        applicable = {
            key: True
            for key in RECOVERY_CRITERIA
        }
    else:
        objectives = {
            "MO-3": {
                "completed": False,
                "evidence_ref": "unit:policy-visible-timeout",
            },
            "MO-5": {
                "completed": True,
                "evidence_ref": "unit:immutable-truth",
            },
        }
        applicable = {
            "required_telemetry_restored": False,
            "health_checks_passed": True,
            "recovery_manifest_complete": True,
        }

    rows, excluded = recovery_partition(applicable)

    return {
        "family": family,
        "clock": clock(
            containment=containment,
            recovery=recovery,
        ),
        "event_success": {
            "predicate": family in {"recovery", "observability"},
            "observed_ns": (
                2_500_000_000
                if family in {"recovery", "observability"}
                else None
            ),
            "evidence_ref": f"unit:{family}:event-success",
        },
        "objective_results": objectives,
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": 2 if family == "command" else 0,
            "rejected": 0,
            "evidence_ref": f"unit:{family}:legitimate-commands",
        },
        "ground_spacecraft_divergence_intervals": [],
        "recovery_observations": rows,
        "recovery_checklist_excluded": excluded,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": recovery,
            "operational_restored": not recovery,
            "recovery_failed": False,
            "contained": containment,
        },
        "containment_evidence_ref": (
            f"unit:{family}:containment"
            if containment
            else None
        ),
        "trusted_recovery_evidence_ref": (
            "unit:recovery:trusted"
            if recovery
            else None
        ),
        "terminal_state_evidence_refs": [
            f"unit:{family}:terminal"
        ],
        "source_observation_refs": [
            f"unit:{family}:source"
        ],
        "development_preflight": True,
    }


class WP8RuntimeBindingTests(unittest.TestCase):
    def test_environment_uses_pinned_runtime_identities(self) -> None:
        env = environment()
        self.assertEqual(
            env["simulator_commit"],
            "5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
        )
        self.assertEqual(
            env["flight_software_commit"],
            "87e273743f3d07ed9216462b461e9f398ff96c87",
        )
        self.assertEqual(
            env["container_or_vm_digest"],
            "sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2",
        )

    def test_command_binding_is_schema_valid(self) -> None:
        result = bind_runtime_observation(
            contract=PILOT["runtime_measurement_contract"],
            factor_context=factor_context(family="command"),
            environment=environment(),
            observation=base_observation(
                family="command",
                containment=True,
                recovery=False,
            ),
            notes="development unit test",
        )
        record = result["run_record"]
        self.assertEqual(
            record["outcomes"]["mission_objective_completion_ratio"],
            1.0,
        )
        self.assertEqual(record["timing"]["containment_s"], 2.0)
        self.assertFalse(
            result["binding_provenance"]["pilot_data"]
        )
        self.assertEqual(list(VALIDATOR.iter_errors(record)), [])

    def test_command_event_effect_reduces_mission_completion(self) -> None:
        observation = base_observation(
            family="command",
            containment=True,
            recovery=False,
        )
        observation["event_success"] = {
            "predicate": True,
            "observed_ns": 2_500_000_000,
            "evidence_ref": "unit:command:event-success",
        }
        observation["objective_results"]["MO-1"]["completed"] = False

        result = bind_runtime_observation(
            contract=PILOT["runtime_measurement_contract"],
            factor_context=factor_context(family="command"),
            environment=environment(),
            observation=observation,
        )

        record = result["run_record"]
        self.assertTrue(
            record["outcomes"]["unauthorized_effect_completed"]
        )
        self.assertEqual(
            record["outcomes"]["mission_objective_completion_ratio"],
            0.5,
        )
        self.assertEqual(list(VALIDATOR.iter_errors(record)), [])

    def test_recovery_binding_is_schema_valid_trusted_state(self) -> None:
        result = bind_runtime_observation(
            contract=PILOT["runtime_measurement_contract"],
            factor_context=factor_context(family="recovery"),
            environment=environment(),
            observation=base_observation(
                family="recovery",
                containment=True,
                recovery=True,
            ),
        )
        record = result["run_record"]
        self.assertEqual(
            record["terminal_state"],
            "TRUSTED_RECOVERY_CONFIRMED",
        )
        self.assertEqual(record["timing"]["verified_recovery_s"], 5.0)
        self.assertEqual(list(VALIDATOR.iter_errors(record)), [])

    def test_observability_binding_retains_event_success(self) -> None:
        result = bind_runtime_observation(
            contract=PILOT["runtime_measurement_contract"],
            factor_context=factor_context(family="observability"),
            environment=environment(),
            observation=base_observation(
                family="observability",
                containment=False,
                recovery=False,
            ),
        )
        record = result["run_record"]
        self.assertTrue(
            record["outcomes"]["unauthorized_effect_completed"]
        )
        self.assertEqual(
            record["outcomes"]["mission_objective_completion_ratio"],
            0.5,
        )
        self.assertIsNone(record["timing"]["containment_s"])
        self.assertEqual(list(VALIDATOR.iter_errors(record)), [])

    def test_runtime_applicability_must_match_frozen_family_rule(self) -> None:
        observation = base_observation(
            family="command",
            containment=True,
            recovery=False,
        )
        observation["recovery_observations"][
            "required_telemetry_restored"
        ] = {
            "available_current": True,
            "evidence_ref": "unit:unexpected-telemetry-applicability",
        }
        observation["recovery_checklist_excluded"].remove(
            "required_telemetry_restored"
        )

        with self.assertRaisesRegex(
            ValueError,
            "frozen family rule",
        ):
            bind_runtime_observation(
                contract=PILOT["runtime_measurement_contract"],
                factor_context=factor_context(family="command"),
                environment=environment(),
                observation=observation,
            )

    def test_missing_frozen_objective_result_is_rejected(self) -> None:
        observation = base_observation(
            family="command",
            containment=True,
            recovery=False,
        )
        del observation["objective_results"]["MO-3"]

        with self.assertRaisesRegex(
            ValueError,
            "frozen family schedule",
        ):
            bind_runtime_observation(
                contract=PILOT["runtime_measurement_contract"],
                factor_context=factor_context(family="command"),
                environment=environment(),
                observation=observation,
            )

    def test_containment_before_event_activation_is_rejected(self) -> None:
        observation = base_observation(
            family="command",
            containment=True,
            recovery=False,
        )
        observation["clock"]["containment_ns"] = 1_500_000_000

        with self.assertRaisesRegex(
            ValueError,
            "before event activation",
        ):
            bind_runtime_observation(
                contract=PILOT["runtime_measurement_contract"],
                factor_context=factor_context(family="command"),
                environment=environment(),
                observation=observation,
            )

    def test_minimal_invalid_binding_has_no_primary_metrics(self) -> None:
        result = bind_invalid_runtime_observation(
            factor_context=factor_context(family="command"),
            environment=environment(),
            invalid_run_reason="runtime_evidence_capture_failure",
            source_observation_refs=["unit:failure-log"],
        )
        record = result["run_record"]
        self.assertEqual(record["terminal_state"], "RUN_INVALID")
        self.assertNotIn("outcomes", record)
        self.assertNotIn("timing", record)
        self.assertFalse(
            result["binding_provenance"]["fabricated_primary_metrics"]
        )
        self.assertEqual(list(VALIDATOR.iter_errors(record)), [])


if __name__ == "__main__":
    unittest.main()
