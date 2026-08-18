#!/usr/bin/env python3
"""Validate experiment schema fixtures, model alignment, and WP8 pilot design."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Run: python3 -m pip install -r requirements-dev.txt"
    ) from exc

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.primary_metrics import score_raw_metric_evidence
from src.mission_recovery.wp8_stage1_pilot import build_offline_stage1_plan
from src.mission_recovery.wp8_command_effect_contract import (
    build_command_effect_matrix,
)
from src.mission_recovery.wp8_command_observation_contract import (
    build_command_observation_matrix,
)

SCHEMA_PATH = PROJECT_ROOT / "configs" / "experiment_run.schema.json"
MODEL_PATH = PROJECT_ROOT / "configs" / "experiment_model.json"
PILOT_PATH = PROJECT_ROOT / "configs" / "wp8_pilot_design.json"
VALID_PATH = PROJECT_ROOT / "configs" / "examples" / "valid_run.json"
INVALID_PATH = PROJECT_ROOT / "configs" / "examples" / "invalid_trusted_recovery.json"

def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unable to load {path}: {exc}") from exc

def format_errors(errors: list) -> str:
    lines: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        lines.append(f"- {location}: {error.message}")
    return "\n".join(lines)

def assert_model_schema_alignment(schema: dict, model: dict) -> None:
    expected = {
        "mission_state_id": {row["id"] for row in model["mission_states"]},
        "event_id": {row["id"] for row in model["events"]},
        "policy_id": {row["id"] for row in model["response_policies"]},
        "contact_condition_id": {row["id"] for row in model["contact_conditions"]},
        "evidence_condition_id": {row["id"] for row in model["evidence_conditions"]},
    }
    for field, ids in expected.items():
        actual = set(schema["properties"][field]["enum"])
        if actual != ids:
            raise SystemExit(
                f"{field} enum mismatch: schema={sorted(actual)} model={sorted(ids)}"
            )

def assert_pilot_design(pilot: dict, model: dict) -> None:
    if pilot["model_version"] != model["model_version"]:
        raise SystemExit("WP8 pilot model_version does not match model")

    gate = pilot["instrumentation_gate"]
    if pilot["status"] != (
        "STAGE1_COMMAND_OBSERVATION_CONTRACT_OFFLINE_VALIDATED_"
        "RUNTIME_EXECUTOR_PENDING"
    ):
        raise SystemExit(
            "WP8 Stage-1 command observation contract status is not closed"
        )
    if gate["known_pre_pilot_implementation_work"] != [
        "stage_1_family_runtime_dispatch_adapter_implementation_and_gate_validation"
    ]:
        raise SystemExit("WP8 remaining pre-pilot work is not the runtime-adapter gate")

    plan = build_offline_stage1_plan(pilot)
    if plan["ordered_cell_ids"] != [
        "C05", "R04", "C04", "R01", "R03", "C02",
        "R02", "C03", "O01", "C07", "C01", "C06",
    ]:
        raise SystemExit("WP8 Stage-1 seed-101 deterministic order changed")
    if (
        plan["runtime_execution_authorized"] is not False
        or plan["pilot_seed_consumed"] is not False
        or plan["pilot_data_generated"] is not False
    ):
        raise SystemExit("WP8 Stage-1 offline plan crossed the pilot execution gate")

    expected_dispatch = {
        "E1": {
            "runtime_family": "command",
            "reference_development_preflight": (
                "scripts/run_wp8_command_binding_preflight.sh"
            ),
            "pilot_executor_ready": False,
        },
        "E3": {
            "runtime_family": "recovery",
            "reference_development_preflight": (
                "scripts/run_wp8_recovery_binding_preflight.sh"
            ),
            "pilot_executor_ready": False,
        },
        "E4": {
            "runtime_family": "observability",
            "reference_development_preflight": (
                "scripts/run_wp8_observability_binding_preflight.sh"
            ),
            "pilot_executor_ready": False,
        },
    }
    if pilot["stage_1_runner_contract"]["dispatch_by_event_id"] != expected_dispatch:
        raise SystemExit("WP8 Stage-1 runtime dispatch contract changed")

    command_matrix = build_command_effect_matrix(pilot)
    expected_command_effects = {
        "C01": ("P0", "OBSERVE_ONLY", 2, 1),
        "C02": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
        "C03": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
        "C04": ("P1", "ISOLATE_MODELED_SOURCE", 0, 1),
        "C05": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1),
        "C06": ("P4", "ENTER_SAFE_MODE", 0, 0),
        "C07": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", 0, 1),
    }
    actual_command_effects = {}
    for row in command_matrix["rows"]:
        policy = row["policy_evaluation"]
        gateway = row["gateway_execution"]
        actual_command_effects[row["cell_id"]] = (
            policy["actual_effective_policy_id"],
            policy["selected_action"],
            gateway["attacker_probe"][
                "expected_cfs_reset_marker_delta_for_acceptance_only"
            ],
            gateway["authorized_probe"][
                "expected_cfs_noop_marker_delta_for_acceptance_only"
            ],
        )
    if actual_command_effects != expected_command_effects:
        raise SystemExit(
            "WP8 Stage-1 command effect matrix differs from frozen semantics"
        )
    if (
        command_matrix["runtime_execution_authorized"] is not False
        or command_matrix["pilot_seed_consumed"] is not False
        or command_matrix["pilot_data_generated"] is not False
        or command_matrix["primary_metrics_emitted"] is not False
        or command_matrix["terminal_states_emitted"] is not False
    ):
        raise SystemExit(
            "WP8 Stage-1 command effect contract crossed an offline boundary"
        )

    observation_matrix = build_command_observation_matrix(pilot)
    expected_observation_rules = {
        "C01": (False, False, "observed_run_end_ns_right_censoring"),
        "C02": (True, True, "observed_authorized_noop_probe_timestamp"),
        "C03": (True, True, "observed_authorized_noop_probe_timestamp"),
        "C04": (True, True, "observed_authorized_noop_probe_timestamp"),
        "C05": (True, True, "observed_authorized_noop_probe_timestamp"),
        "C06": (True, False, "observed_run_end_ns_right_censoring"),
        "C07": (True, True, "observed_authorized_noop_probe_timestamp"),
    }
    actual_observation_rules = {
        row["cell_id"]: (
            row["containment_expected_for_acceptance_only"],
            row["authority_convergence_expected_for_acceptance_only"],
            row["divergence_endpoint_rule"],
        )
        for row in observation_matrix["rows"]
    }
    if actual_observation_rules != expected_observation_rules:
        raise SystemExit(
            "WP8 Stage-1 command observation/censoring matrix changed"
        )
    if (
        observation_matrix["runtime_execution_authorized"] is not False
        or observation_matrix["pilot_seed_consumed"] is not False
        or observation_matrix["pilot_data_generated"] is not False
        or observation_matrix["primary_metrics_emitted"] is not False
        or observation_matrix["terminal_states_emitted"] is not False
        or observation_matrix["recovery_evidence_emitted"] is not False
    ):
        raise SystemExit(
            "WP8 Stage-1 command observation contract crossed an offline boundary"
        )

    cells = pilot["cells"]
    ids = [cell["cell_id"] for cell in cells]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate WP8 pilot cell_id")

    stage1 = pilot["stage_1_control_validity"]
    stage2 = pilot["stage_2_variability"]
    if set(stage1["cell_ids"]) != set(ids):
        raise SystemExit("Stage-1 cells do not equal declared WP8 cells")

    anchors = set(stage2["anchor_cell_ids"])
    if not anchors.issubset(set(ids)):
        raise SystemExit("Stage-2 anchor is not a declared WP8 cell")

    if stage2["total_valid_repetitions_per_anchor_after_stage_2"] != (
        1 + len(stage2["additional_seeds"])
    ):
        raise SystemExit("Stage-2 repetition count is inconsistent")

    model_events = {row["id"] for row in model["events"]}
    model_states = {row["id"] for row in model["mission_states"]}
    model_policies = {row["id"] for row in model["response_policies"]}
    model_contacts = {row["id"] for row in model["contact_conditions"]}
    model_evidence = {row["id"] for row in model["evidence_conditions"]}
    seed = int(stage1["seed"])

    for cell in cells:
        if cell["event_id"] not in model_events:
            raise SystemExit(f"{cell['cell_id']}: unknown event")
        if cell["mission_state_id"] not in model_states:
            raise SystemExit(f"{cell['cell_id']}: unknown mission state")
        if cell["policy_id"] not in model_policies:
            raise SystemExit(f"{cell['cell_id']}: unknown policy")
        if cell["contact_condition_id"] not in model_contacts:
            raise SystemExit(f"{cell['cell_id']}: unknown contact")
        if cell["evidence_condition_id"] not in model_evidence:
            raise SystemExit(f"{cell['cell_id']}: unknown evidence condition")

        event = materialize_event(
            cell["event_id"],
            mission_state=cell["mission_state_id"],
            contact_condition=cell["contact_condition_id"],
            evidence_condition=cell["evidence_condition_id"],
            seed=seed,
        )
        decision = evaluate_policy(cell["policy_id"], event)
        if decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
            raise SystemExit(
                f"{cell['cell_id']}: expected effective policy "
                f"{cell['expected_effective_policy_id']} but policy engine "
                f"returned {decision['delegated_policy_id']}"
            )

    included = set(pilot["pilot_event_subset"]["included"])
    omitted = set(pilot["pilot_event_subset"]["omitted_but_retained_for_wp9"])
    if included != {"E1", "E3", "E4"} or omitted != {"E2"}:
        raise SystemExit("WP8 event subset does not match the frozen pilot design")

    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not False:
        raise SystemExit(
            "WP8 pilot execution must remain unauthorized until instrumentation passes"
        )

def assert_runtime_measurement_contract(pilot: dict) -> None:
    contract = pilot["runtime_measurement_contract"]

    if contract["decision_id"] != "R-015":
        raise SystemExit("WP8 runtime measurement contract is not R-015")

    weighting = contract["primary_objective_weighting"]
    if (
        weighting["method"]
        != "unit_weight_per_scheduled_objective_instance"
        or float(weighting["unit_weight"]) != 1.0
    ):
        raise SystemExit("WP8 primary objective weighting is not unit-weight")

    expected = {
        "command": {"MO-1", "MO-3"},
        "recovery": {"MO-4", "MO-5"},
        "observability": {"MO-3", "MO-5"},
    }
    actual = {
        family: {row["objective_id"] for row in rows}
        for family, rows in contract["family_objectives"].items()
    }
    if actual != expected:
        raise SystemExit(
            f"WP8 runtime family objectives mismatch: {actual}"
        )

    command_mo1 = next(
        row
        for row in contract["family_objectives"]["command"]
        if row["objective_id"] == "MO-1"
    )
    if command_mo1["completion_predicate"] != (
        "no_modeled_attacker_sample_reset_counters_effect_occurs_during_"
        "the_scheduled_objective_interval"
    ):
        raise SystemExit(
            "WP8 command MO-1 predicate does not cover the full scheduled interval"
        )

    if contract["controller_clock"] != "experiment_controller_monotonic_ns":
        raise SystemExit("WP8 controller clock is not monotonic_ns")

    if contract["event_response_order"][0] != "event_activation_t0":
        raise SystemExit("WP8 runtime response begins before event activation")

    surrogate = contract["e1_modeled_protected_state_surrogate"]
    if surrogate["command_class"] != "sample_reset_counters":
        raise SystemExit("WP8 E1 protected-state surrogate changed")
    if surrogate["source_id"] != "modeled_attacker":
        raise SystemExit("WP8 E1 attacker source changed")
    if surrogate["packet_sha256"] != (
        "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
    ):
        raise SystemExit("WP8 E1 reset packet identity changed")

    if float(contract["e4_policy_visibility_timeout_s"]) != 3.0:
        raise SystemExit("WP8 E4 visibility deadline changed")

    criteria = {
        "approved_version",
        "integrity_measurement_valid",
        "authorization_valid",
        "measured_state_current",
        "authorized_command_path_restored",
        "ground_spacecraft_state_agreed",
        "required_telemetry_restored",
        "health_checks_passed",
        "no_residual_unauthorized_state",
        "recovery_manifest_complete",
    }
    applicability = contract["family_recovery_criteria_applicability"]
    if set(applicability) != {"command", "recovery", "observability"}:
        raise SystemExit("WP8 family recovery applicability is incomplete")
    for family, rule in applicability.items():
        applicable = set(rule["applicable"])
        excluded = set(rule["excluded"])
        if applicable & excluded or applicable | excluded != criteria:
            raise SystemExit(
                f"WP8 {family} recovery applicability does not partition criteria"
            )

    command_rule = applicability["command"]
    if set(command_rule["applicable"]) != {
        "authorization_valid",
        "authorized_command_path_restored",
        "ground_spacecraft_state_agreed",
        "health_checks_passed",
        "recovery_manifest_complete",
    }:
        raise SystemExit("WP8 command M-08 applicability changed")
    if set(command_rule["excluded"]) != {
        "approved_version",
        "integrity_measurement_valid",
        "measured_state_current",
        "required_telemetry_restored",
        "no_residual_unauthorized_state",
    }:
        raise SystemExit("WP8 command M-08 exclusions changed")

    divergence = contract["command_authority_divergence_operationalization"]
    if divergence["divergence_start"] != (
        "first_observed_modeled_attacker_reset_counter_effect_after_t0"
    ):
        raise SystemExit("WP8 command M-07 divergence start changed")
    if divergence["divergence_end"] != (
        "two_consecutive_modeled_attacker_reset_probes_are_blocked_and_a_"
        "matched_authorized_ground_noop_is_observed_at_cfs"
    ):
        raise SystemExit("WP8 command M-07 convergence rule changed")
    if divergence["measurement_role"] != "behavioral_proxy":
        raise SystemExit("WP8 command M-07 measurement role changed")
    if "not_a_direct_measurement_of_an_onboard_authorization_" not in (
        divergence["claim_boundary"]
    ):
        raise SystemExit("WP8 command M-07 claim boundary changed")

    if contract["measurement_operationalization_decision_id"] != "R-016":
        raise SystemExit("WP8 runtime operationalization decision is not R-016")

    if contract["development_preflights_are_pilot_data"] is not False:
        raise SystemExit("WP8 development preflights cannot be pilot data")

    status = pilot["instrumentation_gate"]["component_status"]
    if status["runtime_binding_module"] is not True:
        raise SystemExit("WP8 runtime binding module is not ready")
    if status["runtime_binding_static_validation"] is not True:
        raise SystemExit("WP8 runtime binding static validation is not ready")
    if status["stage_1_runner_offline_contract"] is not True:
        raise SystemExit("WP8 Stage-1 offline runner contract is not validated")
    if status["stage_1_command_effect_contract"] is not True:
        raise SystemExit("WP8 Stage-1 command effect contract is not validated")
    if status["stage_1_command_observation_contract"] is not True:
        raise SystemExit("WP8 Stage-1 command observation contract is not validated")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise SystemExit("WP8 Stage-1 runtime adapters cannot pass in R-030")
    if status["nos3_runtime_binding"] is not True:
        raise SystemExit(
            "NOS3 runtime binding must be closed after accepted development preflights"
        )
    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not False:
        raise SystemExit(
            "Pilot execution must remain blocked pending Stage-1 runtime-adapter gate validation"
        )


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    model = load_json(MODEL_PATH)
    pilot = load_json(PILOT_PATH)
    valid_fixture = load_json(VALID_PATH)
    invalid_fixture = load_json(INVALID_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    valid_errors = sorted(
        validator.iter_errors(valid_fixture),
        key=lambda err: list(err.path),
    )
    if valid_errors:
        print("[FAIL] Positive fixture did not validate:")
        print(format_errors(valid_errors))
        return 1
    print("[OK] Positive fixture validates")

    minimal_invalid = {
        key: valid_fixture[key]
        for key in (
            "run_id",
            "model_version",
            "seed",
            "mission_state_id",
            "event_id",
            "policy_id",
            "contact_condition_id",
            "evidence_condition_id",
            "environment",
        )
    }
    minimal_invalid["run_id"] = "schema-valid-run-invalid"
    minimal_invalid["terminal_state"] = "RUN_INVALID"
    minimal_invalid["invalid_run_reason"] = "evidence_capture_failure"

    minimal_invalid_errors = sorted(
        validator.iter_errors(minimal_invalid),
        key=lambda err: list(err.path),
    )
    if minimal_invalid_errors:
        print("[FAIL] Minimal RUN_INVALID record did not validate:")
        print(format_errors(minimal_invalid_errors))
        return 1
    print("[OK] RUN_INVALID record validates without fabricated metrics")

    invalid_errors = sorted(
        validator.iter_errors(invalid_fixture),
        key=lambda err: list(err.path),
    )
    if not invalid_errors:
        print("[FAIL] Negative fixture unexpectedly validated")
        return 1

    expected_guardrail = any(
        "measured_state_current"
        in ".".join(str(part) for part in error.absolute_path)
        or "True was expected" in error.message
        for error in invalid_errors
    )
    if not expected_guardrail:
        print(
            "[FAIL] Negative fixture failed, but not on the "
            "trusted-recovery freshness guardrail:"
        )
        print(format_errors(invalid_errors))
        return 1

    unexpected_invalid_errors = [
        error
        for error in invalid_errors
        if list(error.absolute_path)
        != ["recovery_evidence", "measured_state_current"]
    ]
    if unexpected_invalid_errors:
        print(
            "[FAIL] Negative fixture has failures beyond the intended "
            "measured-state freshness guardrail:"
        )
        print(format_errors(unexpected_invalid_errors))
        return 1

    try:
        score_raw_metric_evidence(
            event_activation_s=invalid_fixture["timing"][
                "event_activation_s"
            ],
            raw=invalid_fixture["raw_metric_evidence"],
            recovery_evidence=invalid_fixture["recovery_evidence"],
        )
    except ValueError as exc:
        if "incomplete recovery evidence" not in str(exc):
            print(
                "[FAIL] Negative fixture scorer rejected for an "
                f"unexpected reason: {exc}"
            )
            return 1
    else:
        print(
            "[FAIL] Negative trusted-recovery fixture unexpectedly "
            "passed raw metric scoring"
        )
        return 1

    print(
        "[OK] Negative trusted-recovery fixture rejected only on "
        "the intended freshness fault"
    )

    try:
        scored = score_raw_metric_evidence(
            event_activation_s=valid_fixture["timing"]["event_activation_s"],
            raw=valid_fixture["raw_metric_evidence"],
            recovery_evidence=valid_fixture["recovery_evidence"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] Positive fixture raw metric scoring failed: {exc}")
        return 1

    expected_pairs = {
        "unauthorized_effect_completed": valid_fixture["outcomes"][
            "unauthorized_effect_completed"
        ],
        "mission_objective_completion_ratio": valid_fixture["outcomes"][
            "mission_objective_completion_ratio"
        ],
        "safety_invariant_violations": valid_fixture["outcomes"][
            "safety_invariant_violations"
        ],
        "legitimate_command_rejection_rate": valid_fixture["outcomes"][
            "legitimate_command_rejection_rate"
        ],
        "ground_spacecraft_state_divergence_s": valid_fixture["outcomes"][
            "ground_spacecraft_state_divergence_s"
        ],
        "evidence_completeness_ratio": valid_fixture["outcomes"][
            "evidence_completeness_ratio"
        ],
        "time_to_containment_s": valid_fixture["timing"]["containment_s"],
        "time_to_verified_recovery_s": valid_fixture["timing"][
            "verified_recovery_s"
        ],
        "recovery_terminal_state": valid_fixture["terminal_state"],
    }

    for key, expected in expected_pairs.items():
        if scored[key] != expected:
            print(
                f"[FAIL] Positive fixture metric mismatch for {key}: "
                f"derived={scored[key]!r} fixture={expected!r}"
            )
            return 1

    print("[OK] Positive fixture metrics derive from raw evidence")

    try:
        assert_model_schema_alignment(schema, model)
        assert_pilot_design(pilot, model)
        assert_runtime_measurement_contract(pilot)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] Model/pilot validation error: {exc}")
        return 1

    print("[OK] Experiment schema factor enums align with experiment model")
    print("[OK] WP8 pilot cells match current policy semantics")
    print("[OK] R-015 runtime measurement contract is frozen")
    print("[OK] M-07 command-authority convergence rule is frozen")
    print("[OK] M-08 family applicability rules are frozen")
    print("[OK] WP8 runtime binding module is statically ready")
    print("[OK] WP8 NOS3 runtime binding is closed; pilot execution remains gated")
    print("[OK] WP8 Stage-1 offline orchestration is validated; runtime adapters remain pending")
    print("[OK] WP8 Stage-1 command effect contract is offline-validated; command runtime executor remains pending")
    print("[OK] WP8 Stage-1 command observation/censoring contract is offline-validated; command runtime executor remains pending")
    print("[OK] Primary metrics derive from retained raw evidence")
    print("[OK] JSON Schema Draft 2020-12 structure is valid")
    print("SCHEMA_VALIDATION_STATUS=PASS")
    print("WP8_PILOT_CONTRACT_STATUS=PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
