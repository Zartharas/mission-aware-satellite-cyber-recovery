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
from src.mission_recovery.wp8_command_runtime_executor import (
    STATIC_DEVELOPMENT_SEED,
    build_static_development_matrix,
    reserved_pilot_seeds,
)
from src.mission_recovery.wp8_recovery_effect_contract import (
    build_recovery_effect_matrix,
)
from src.mission_recovery.wp8_recovery_observation_contract import (
    build_recovery_observation_matrix,
)
from src.mission_recovery.wp8_recovery_runtime_executor import (
    DEVELOPMENT_VALIDATION_CELLS,
    validate_recovery_runtime_executor_contract,
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
        "STAGE1_PILOT_MODE_MATERIALIZATION_STATIC_"
        "VALIDATED_RUNTIME_WIRING_PENDING"
    ):
        raise SystemExit(
            "WP8 generic O01 observability executor static gate is not closed"
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
            "development_executor": (
                "scripts/run_wp8_command_stage1_development.sh"
            ),
        },
        "E3": {
            "runtime_family": "recovery",
            "reference_development_preflight": (
                "scripts/run_wp8_recovery_binding_preflight.sh"
            ),
            "pilot_executor_ready": False,
            "development_executor": (
                "scripts/run_wp8_recovery_stage1_development.sh"
            ),
        },
        "E4": {
            "runtime_family": "observability",
            "reference_development_preflight": (
                "scripts/run_wp8_observability_binding_preflight.sh"
            ),
            "pilot_executor_ready": False,
            "development_executor": (
                "scripts/run_wp8_observability_stage1_development.sh"
            ),
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

    executor_matrix = build_static_development_matrix(
        pilot,
        development_seed=STATIC_DEVELOPMENT_SEED,
    )
    expected_executor = {
        "C01": ("P0", "OBSERVE_ONLY"),
        "C02": ("P1", "ISOLATE_MODELED_SOURCE"),
        "C03": ("P1", "ISOLATE_MODELED_SOURCE"),
        "C04": ("P1", "ISOLATE_MODELED_SOURCE"),
        "C05": ("P2", "RESTRICT_HIGH_RISK_COMMANDS"),
        "C06": ("P4", "ENTER_SAFE_MODE"),
        "C07": ("P2", "RESTRICT_HIGH_RISK_COMMANDS"),
    }
    actual_executor = {
        row["cell_id"]: (
            row["actual_effective_policy_id"],
            row["selected_action"],
        )
        for row in executor_matrix["rows"]
    }
    if actual_executor != expected_executor:
        raise SystemExit(
            "WP8 command development executor policy matrix changed"
        )
    if reserved_pilot_seeds(pilot) != {101, 202, 303, 404, 505}:
        raise SystemExit("WP8 reserved pilot seed set changed")
    if STATIC_DEVELOPMENT_SEED in reserved_pilot_seeds(pilot):
        raise SystemExit("WP8 R-032 static development seed collides with pilot")
    if (
        executor_matrix["runtime_execution_performed"] is not False
        or executor_matrix["pilot_seed_consumed"] is not False
        or executor_matrix["pilot_data_generated"] is not False
    ):
        raise SystemExit(
            "WP8 command executor static validation crossed runtime boundary"
        )

    recovery_matrix = build_recovery_effect_matrix(pilot)
    expected_recovery_effects = {
        "R01": ("P0", "OBSERVE_ONLY", "observe_only", False),
        "R02": ("P5", "REQUEST_VERIFIED_ROLLBACK", "rollback_request", True),
        "R03": ("P5", "REQUEST_VERIFIED_ROLLBACK", "rollback_request", True),
        "R04": ("P2", "RESTRICT_HIGH_RISK_COMMANDS", "command_gateway", False),
    }
    actual_recovery_effects = {
        row["cell_id"]: (
            row["policy_evaluation"]["actual_effective_policy_id"],
            row["policy_evaluation"]["selected_action"],
            row["effect_dispatch"]["effect_family"],
            row["effect_dispatch"]["containment_expected_for_acceptance_only"],
        )
        for row in recovery_matrix["rows"]
    }
    if actual_recovery_effects != expected_recovery_effects:
        raise SystemExit(
            "WP8 Stage-1 recovery effect matrix differs from R-034 semantics"
        )
    r04 = next(
        row
        for row in recovery_matrix["rows"]
        if row["cell_id"] == "R04"
    )
    if (
        r04["command_gateway_contract"]["attacker_probe"][
            "expected_cfs_reset_marker_delta_for_acceptance_only"
        ]
        != 0
        or r04["command_gateway_contract"]["authorized_probe"][
            "expected_cfs_noop_marker_delta_for_acceptance_only"
        ]
        != 1
    ):
        raise SystemExit(
            "WP8 R04 P2 command-gateway effect semantics changed"
        )
    if (
        recovery_matrix["runtime_execution_authorized"] is not False
        or recovery_matrix["pilot_seed_consumed"] is not False
        or recovery_matrix["pilot_data_generated"] is not False
        or recovery_matrix["primary_metrics_emitted"] is not False
        or recovery_matrix["terminal_states_emitted"] is not False
        or recovery_matrix["trusted_recovery_evidence_emitted"] is not False
    ):
        raise SystemExit(
            "WP8 Stage-1 recovery effect contract crossed an offline boundary"
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
    semantics = contract["recovery_evidence_semantics"]
    if semantics["decision_id"] != "R-035":
        raise SystemExit("WP8 recovery evidence semantics are not R-035")
    if semantics["raw_checklist_dimensions"] != [
        "available_current", "criterion_satisfied", "evidence_ref"
    ]:
        raise SystemExit("WP8 recovery evidence checklist dimensions changed")
    if semantics["evidence_completeness_numerator"] != (
        "count_available_current_true_applicable_evidence_elements"
    ):
        raise SystemExit("WP8 M-08 numerator semantics changed")
    if semantics["trusted_recovery_requires"] != [
        "all_applicable_evidence_available_current",
        "all_applicable_criteria_satisfied",
    ]:
        raise SystemExit("WP8 trusted-recovery evidence semantics changed")
    if not semantics["pilot_data_requires_explicit_criterion_satisfied"]:
        raise SystemExit("WP8 pilot recovery criterion truth is not explicit")
    if semantics["retained_pre_r035_run_records_rewritten"] is not False:
        raise SystemExit("WP8 retained pre-R-035 records cannot be rewritten")

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
    if (
        status["stage_1_command_observation_temporal_order_corrected"]
        is not True
    ):
        raise SystemExit(
            "WP8 Stage-1 command observation temporal-order correction "
            "is not validated"
        )
    temporal = pilot["stage_1_runner_contract"]["command_observation_contract"]
    if temporal["event_success_policy_enforcement_order_required"] is not False:
        raise SystemExit(
            "WP8 command event-success observation cannot gate policy enforcement"
        )
    if temporal["temporal_order_rule"] != (
        "event_activation_precedes_policy_enforcement_and_event_success_"
        "observation_independently;both_precede_post_enforcement_probe"
    ):
        raise SystemExit("WP8 command temporal partial-order rule changed")
    if status["stage_1_command_runtime_executor_static"] is not True:
        raise SystemExit(
            "WP8 Stage-1 command runtime executor is not statically validated"
        )
    if (
        status["stage_1_command_runtime_executor_runtime_validated"]
        is not True
    ):
        raise SystemExit(
            "WP8 command runtime executor runtime validation is not closed"
        )

    runtime_validation = pilot["stage_1_runner_contract"][
        "command_runtime_executor_contract"
    ]["runtime_validation"]
    if runtime_validation["decision_id"] != "R-033":
        raise SystemExit("WP8 command runtime validation is not R-033")
    if runtime_validation["validation_status"] != "PASS":
        raise SystemExit("WP8 command runtime validation status changed")
    if runtime_validation["generic_executor_cells_executed"] != [
        "C01", "C05", "C06"
    ]:
        raise SystemExit("WP8 R-033 retained runtime cell set changed")
    if runtime_validation["generic_executor_cells_not_executed"] != [
        "C02", "C03", "C04", "C07"
    ]:
        raise SystemExit("WP8 R-033 nonexecuted cell boundary changed")
    if runtime_validation["generic_executor_gateway_actions_observed"] != [
        "OBSERVE_ONLY",
        "RESTRICT_HIGH_RISK_COMMANDS",
        "ENTER_SAFE_MODE",
    ]:
        raise SystemExit("WP8 R-033 gateway branch evidence changed")
    if any(
        row["pilot_data"] is not False
        for row in runtime_validation["retained_development_runs"]
    ):
        raise SystemExit("WP8 R-033 runtime evidence cannot be pilot data")
    if status["stage_1_recovery_effect_contract"] is not True:
        raise SystemExit(
            "WP8 R-034 recovery effect contract is not closed"
        )
    if status["recovery_evidence_semantics_separated"] is not True:
        raise SystemExit("WP8 R-035 recovery evidence semantics are not separated")
    if status["stage_1_recovery_observation_contract"] is not True:
        raise SystemExit(
            "WP8 R-036 recovery observation/censoring contract is not closed"
        )
    recovery_observation = pilot["stage_1_runner_contract"][
        "recovery_observation_contract"
    ]
    if recovery_observation["decision_id"] != "R-036":
        raise SystemExit("WP8 recovery observation contract is not R-036")
    if recovery_observation["r04_command_mitigation_rule"] != (
        "observed_P2_command_gateway_mitigation_is_recorded_separately_"
        "and_never_counts_as_E3_update_containment"
    ):
        raise SystemExit("WP8 R04 mitigation/containment boundary changed")
    if recovery_observation["t1_policy_visibility_rule"] != (
        "policy_time_omission_does_not_automatically_imply_"
        "classification_time_M08_loss"
    ):
        raise SystemExit("WP8 R-036 T1 evidence boundary changed")
    if recovery_observation["criterion_count"] != 10:
        raise SystemExit("WP8 R-036 recovery criterion count changed")
    matrix = build_recovery_observation_matrix(pilot)
    if matrix["cell_ids"] != ["R01", "R02", "R03", "R04"]:
        raise SystemExit("WP8 R-036 recovery cell order changed")
    if (
        matrix["runtime_execution_authorized"] is not False
        or matrix["pilot_seed_consumed"] is not False
        or matrix["pilot_data_generated"] is not False
        or matrix["primary_metrics_emitted"] is not False
        or matrix["terminal_states_emitted"] is not False
    ):
        raise SystemExit("WP8 R-036 crossed offline observation boundary")
    if status["stage_1_recovery_runtime_executor_static"] is not True:
        raise SystemExit(
            "WP8 R-037 recovery runtime executor static gate is not closed"
        )
    if (
        status["stage_1_recovery_runtime_executor_runtime_validated"]
        is not True
    ):
        raise SystemExit(
            "WP8 R-037 recovery runtime validation is not closed"
        )
    if pilot["status"] != (
        "STAGE1_PILOT_MODE_MATERIALIZATION_STATIC_"
        "VALIDATED_RUNTIME_WIRING_PENDING"
    ):
        raise SystemExit(
            "WP8 generic O01 observability runtime validation "
            "is not the next pending family gate"
        )
    try:
        validate_recovery_runtime_executor_contract(pilot)
    except ValueError as exc:
        raise SystemExit(
            f"WP8 R-037 recovery runtime executor contract invalid: {exc}"
        ) from exc
    if DEVELOPMENT_VALIDATION_CELLS != ("R01", "R02", "R04"):
        raise SystemExit(
            "WP8 R-037 recovery discriminator set changed"
        )
    observability = pilot["stage_1_runner_contract"][
        "observability_runtime_executor_contract"
    ]
    if observability["implementation_id"] != "WP8-O01-GENERIC-V1":
        raise SystemExit(
            "WP8 generic O01 observability executor identity changed"
        )
    if observability["development_runner"] != (
        "scripts/run_wp8_observability_stage1_development.sh"
    ):
        raise SystemExit(
            "WP8 generic O01 development runner changed"
        )
    if observability["supported_cell_ids"] != ["O01"]:
        raise SystemExit(
            "WP8 generic observability executor cell set changed"
        )
    if observability["factor_source"] != "wp8_pilot_design.cells":
        raise SystemExit(
            "WP8 generic O01 factors must come from pilot config"
        )
    if observability["development_seed_parameterized"] is not True:
        raise SystemExit(
            "WP8 generic O01 development seed is not parameterized"
        )
    if observability["pilot_seed_collision_rejected"] is not True:
        raise SystemExit(
            "WP8 generic O01 executor must reject frozen pilot seeds"
        )
    if observability["accepted_mechanism_reference_run"] != (
        "results/wp8/runtime-binding/observability/"
        "20260817T042131Z-wp8-observability-binding-dev"
    ):
        raise SystemExit(
            "WP8 accepted O01 mechanism reference changed"
        )
    if float(observability["frozen_visibility_deadline_s"]) != 3.0:
        raise SystemExit(
            "WP8 generic O01 visibility deadline changed"
        )
    if observability["static_validation_complete"] is not True:
        raise SystemExit(
            "WP8 generic O01 static gate is not closed"
        )
    if observability["runtime_validation_complete"] is not True:
        raise SystemExit(
            "WP8 generic O01 runtime validation is not closed"
        )

    runtime_validation = observability.get("runtime_validation")
    if not isinstance(runtime_validation, dict):
        raise SystemExit(
            "WP8 generic O01 retained runtime validation is missing"
        )

    if runtime_validation["validation_status"] != "PASS":
        raise SystemExit(
            "WP8 generic O01 retained validation status changed"
        )

    if runtime_validation["validated_against_repo_commit"] != (
        "78cef883be2225256577cb17925c8df20364378c"
    ):
        raise SystemExit(
            "WP8 generic O01 validation baseline changed"
        )

    if runtime_validation["cell_id"] != "O01":
        raise SystemExit(
            "WP8 generic O01 retained cell changed"
        )

    if runtime_validation["development_seed"] != 9701:
        raise SystemExit(
            "WP8 generic O01 retained development seed changed"
        )

    if runtime_validation["requested_policy_id"] != "P7":
        raise SystemExit(
            "WP8 generic O01 requested policy changed"
        )

    if runtime_validation["actual_effective_policy_id"] != "P4":
        raise SystemExit(
            "WP8 generic O01 effective policy changed"
        )

    if (
        runtime_validation["policy_oracle_ground_truth_read"]
        is not False
    ):
        raise SystemExit(
            "WP8 generic O01 cannot use oracle ground truth"
        )

    if runtime_validation["event_success_observed"] is not True:
        raise SystemExit(
            "WP8 generic O01 event success evidence changed"
        )

    if (
        runtime_validation["observability_containment_observed"]
        is not False
    ):
        raise SystemExit(
            "WP8 generic O01 cannot fabricate containment"
        )

    if (
        runtime_validation["trusted_recovery_observed"]
        is not False
    ):
        raise SystemExit(
            "WP8 generic O01 cannot fabricate trusted recovery"
        )

    if (
        runtime_validation["terminal_state_spacecraft_failure_claim"]
        is not False
    ):
        raise SystemExit(
            "WP8 generic O01 terminal claim boundary changed"
        )

    if runtime_validation["runtime_binding_performed"] is not True:
        raise SystemExit(
            "WP8 generic O01 runtime binding evidence missing"
        )

    if (
        runtime_validation[
            "schema_valid_scored_run_record_emitted"
        ]
        is not True
    ):
        raise SystemExit(
            "WP8 generic O01 scored run-record evidence missing"
        )

    if runtime_validation["development_preflight"] is not True:
        raise SystemExit(
            "WP8 generic O01 must remain development evidence"
        )

    if runtime_validation["pilot_data"] is not False:
        raise SystemExit(
            "WP8 generic O01 cannot become pilot data"
        )

    if runtime_validation["pilot_seed_consumed"] is not False:
        raise SystemExit(
            "WP8 generic O01 cannot consume pilot seed"
        )

    for key in (
        "runner_sha256",
        "factor_context_sha256",
        "policy_decision_sha256",
        "event_success_sha256",
        "post_enforcement_effect_sha256",
        "observability_manifest_sha256",
        "run_record_sha256",
        "binding_provenance_sha256",
    ):
        value = runtime_validation[key]

        if not isinstance(value, str) or len(value) != 64:
            raise SystemExit(
                f"WP8 generic O01 invalid retained hash: {key}"
            )

        try:
            int(value, 16)
        except ValueError as exc:
            raise SystemExit(
                f"WP8 generic O01 nonhex retained hash: {key}"
            ) from exc
    if observability["pilot_executor_ready"] is not False:
        raise SystemExit(
            "WP8 generic O01 cannot authorize pilot execution"
        )
    if status["stage_1_observability_runtime_executor_static"] is not True:
        raise SystemExit(
            "WP8 generic O01 static component gate is not closed"
        )
    if (
        status["stage_1_observability_runtime_executor_runtime_validated"]
        is not True
    ):
        raise SystemExit(
            "WP8 generic O01 runtime validation component gate "
            "is not closed"
        )
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise SystemExit(
            "WP8 Stage-1 runtime adapters cannot pass before O01 validation"
        )
    try:
        from src.mission_recovery.wp8_stage1_family_dispatch import build_offline_family_dispatch_matrix, validate_family_dispatch_contract
        validate_family_dispatch_contract(pilot)
        r038_matrix = build_offline_family_dispatch_matrix(pilot)
    except (ImportError, ValueError) as exc:
        raise SystemExit(f"WP8 R-038 Stage-1 family dispatch adapter invalid: {exc}") from exc
    if r038_matrix["ordered_cell_ids"] != ["C05","R04","C04","R01","R03","C02","R02","C03","O01","C07","C01","C06"]:
        raise SystemExit("WP8 R-038 Stage-1 dispatch order changed")
    if r038_matrix["family_counts"] != {"command":7,"recovery":4,"observability":1}:
        raise SystemExit("WP8 R-038 Stage-1 family counts changed")
    if r038_matrix["runtime_execution_performed"] or r038_matrix["pilot_seed_consumed"] or r038_matrix["pilot_data_generated"]:
        raise SystemExit("WP8 R-038 crossed offline dispatch boundary")

    try:
        from src.mission_recovery.wp8_stage1_family_dispatch import (
            build_offline_pilot_mode_matrix,
            validate_pilot_mode_materialization_contract,
        )
        validate_pilot_mode_materialization_contract(pilot)
        r039_matrix = build_offline_pilot_mode_matrix(pilot)
    except (ImportError, ValueError) as exc:
        raise SystemExit(
            f"WP8 R-039 pilot-mode materialization invalid: {exc}"
        ) from exc

    if r039_matrix["runtime_path_counts"] != {
        "command_generic": 7,
        "recovery_generic": 2,
        "recovery_full_trusted": 2,
        "observability_generic": 1,
    }:
        raise SystemExit(
            "WP8 R-039 runtime-path counts changed"
        )

    if (
        r039_matrix["runtime_execution_performed"]
        or r039_matrix["pilot_seed_consumed"]
        or r039_matrix["pilot_data_generated"]
    ):
        raise SystemExit(
            "WP8 R-039 crossed the offline pilot boundary"
        )

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
    recovery_item = schema["properties"]["raw_metric_evidence"]["properties"][
        "recovery_checklist"
    ]["items"]
    if "criterion_satisfied" not in recovery_item["properties"]:
        raise SystemExit("R-035 criterion_satisfied schema dimension is missing")
    if "criterion_satisfied" in recovery_item["required"]:
        raise SystemExit(
            "R-035 schema cannot invalidate retained pre-R-035 run records"
        )
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
    print("[OK] WP8 Stage-1 command effect contract remains frozen under R-029")
    print("[OK] WP8 Stage-1 command observation/censoring contract remains frozen under R-030/R-031")
    print("[OK] WP8 command event-success observation is temporally independent of policy enforcement after activation")
    print("[OK] WP8 command runtime executor development mechanisms are R-033 validated; C02/C03/C04/C07 remain unexecuted by the generic development runner and no pilot cell is claimed")
    print("[OK] WP8 Stage-1 recovery effect contract remains frozen under R-034; R01/R04 remain non-rollback cases")
    print("[OK] R-035 separates recovery criterion satisfaction from evidence availability/currentness; pilot data requires the explicit dimension and retained development records are not rewritten")
    print("[OK] R-036 freezes E3 recovery observation/censoring semantics; R04 command mitigation is not update containment and final scoring/classification remains deferred")
    print("[OK] R-037 generic recovery executor is runtime-validated by retained R01/R02/R04 development discriminators; R03 remains intentionally unexecuted until pilot and pilot execution remains blocked")
    print("[OK] Generic O01 observability executor is runtime-validated by retained seed-9701 development evidence; pilot execution remains blocked pending the family-dispatch gate")
    print("[OK] R-038 Stage-1 family dispatch adapter interface and frozen 12-cell routing matrix are statically validated offline; pilot-mode family materialization remains blocked")
    print("[OK] R-039 pilot-mode runtime paths are frozen offline: command=7, recovery-generic=2, recovery-full-trusted=2, observability=1; runtime wiring and seed 101 remain blocked")
    print("[OK] Primary metrics derive from retained raw evidence")
    print("[OK] JSON Schema Draft 2020-12 structure is valid")
    print("SCHEMA_VALIDATION_STATUS=PASS")
    print("WP8_PILOT_CONTRACT_STATUS=PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
