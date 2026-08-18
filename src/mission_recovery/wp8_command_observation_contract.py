from __future__ import annotations

from typing import Any

from .wp8_command_effect_contract import (
    COMMAND_CELL_IDS,
    MATCHED_ATTACKER_PROBE_COUNT,
    AUTHORIZED_NOOP_ATTEMPT_COUNT,
    build_command_cell_effect_contract,
    derive_observed_command_effect,
    require_command_effect_acceptance,
)

DECISION_ID = "R-030"


def validate_command_observation_contract_config(
    pilot: dict[str, Any],
) -> None:
    runner = pilot["stage_1_runner_contract"]
    contract = runner["command_observation_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    if contract["decision_id"] != DECISION_ID:
        raise ValueError("Stage-1 command observation contract is not R-030")
    if contract["event_success_source"] != (
        "observed_event_activation_cfs_reset_marker_delta"
    ):
        raise ValueError("command event-success source changed")
    if contract["containment_timestamp_rule"] != (
        "second_matched_attacker_probe_observation_when_both_probes_blocked"
    ):
        raise ValueError("command containment timestamp rule changed")
    if contract["containment_censoring_rule"] != (
        "null_when_two_matched_attacker_probes_are_not_both_blocked"
    ):
        raise ValueError("command containment censoring rule changed")
    if contract["authority_convergence_rule"] != (
        "two_matched_attacker_probes_blocked_and_authorized_noop_observed_at_cfs"
    ):
        raise ValueError("command authority convergence rule changed")
    if contract["divergence_nonconvergence_endpoint"] != (
        "observed_run_end_ns_right_censoring"
    ):
        raise ValueError("command divergence censoring rule changed")
    if contract["mo1_completion_source"] != (
        "observed_modeled_attacker_reset_effect_over_scheduled_interval"
    ):
        raise ValueError("command MO-1 source changed")
    if contract["mo3_completion_source"] != (
        "observed_authorized_ground_noop_cfs_marker_delta"
    ):
        raise ValueError("command MO-3 source changed")
    if contract["expected_values_role"] != (
        "post_observation_acceptance_only_not_raw_metric_substitution"
    ):
        raise ValueError("expected values cannot substitute raw observations")
    if contract["emits_primary_metrics"] is not False:
        raise ValueError("R-030 cannot emit primary metrics")
    if contract["emits_terminal_state"] is not False:
        raise ValueError("R-030 cannot emit terminal state")
    if contract["emits_recovery_evidence"] is not False:
        raise ValueError("R-030 cannot emit recovery evidence")
    if contract["offline_validation_executes_runtime"] is not False:
        raise ValueError("R-030 offline validation cannot execute runtime")
    if contract["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError("R-030 offline validation cannot consume pilot seed")

    if status["stage_1_command_effect_contract"] is not True:
        raise ValueError("R-029 command effect contract must remain closed")
    if status["stage_1_command_observation_contract"] is not True:
        raise ValueError("R-030 command observation contract is not closed")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("runtime dispatch adapters cannot pass in R-030")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("pilot execution must remain blocked in R-030")


def build_command_observation_plan(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    validate_command_observation_contract_config(pilot)

    effect = build_command_cell_effect_contract(pilot, cell_id)
    gateway = effect["gateway_execution"]

    expected_attacker_delta = gateway["attacker_probe"][
        "expected_cfs_reset_marker_delta_for_acceptance_only"
    ]
    expected_noop_delta = gateway["authorized_probe"][
        "expected_cfs_noop_marker_delta_for_acceptance_only"
    ]

    containment_expected = expected_attacker_delta == 0
    convergence_expected = (
        containment_expected and expected_noop_delta == 1
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "seed": effect["seed"],
        "expected_effective_policy_id_for_acceptance_only": (
            effect["policy_evaluation"]["actual_effective_policy_id"]
        ),
        "selected_action_for_acceptance_only": (
            effect["policy_evaluation"]["selected_action"]
        ),
        "containment_expected_for_acceptance_only": containment_expected,
        "authority_convergence_expected_for_acceptance_only": (
            convergence_expected
        ),
        "divergence_endpoint_rule": (
            "observed_authorized_noop_probe_timestamp"
            if convergence_expected
            else "observed_run_end_ns_right_censoring"
        ),
        "mo1_completion_rule": (
            "false_when_observed_e1_activation_reset_effect_occurs"
        ),
        "mo3_completion_rule": (
            "true_only_when_observed_authorized_noop_marker_delta_is_one"
        ),
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "recovery_evidence_emitted": False,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
    }


def build_command_observation_matrix(
    pilot: dict[str, Any],
) -> dict[str, Any]:
    validate_command_observation_contract_config(pilot)
    rows = [
        build_command_observation_plan(pilot, cell_id)
        for cell_id in COMMAND_CELL_IDS
    ]
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_STAGE1_COMMAND_OBSERVATION_CONTRACT_OFFLINE",
        "cell_ids": list(COMMAND_CELL_IDS),
        "rows": rows,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
        "primary_metrics_emitted": False,
        "terminal_states_emitted": False,
        "recovery_evidence_emitted": False,
    }


def derive_command_runtime_observation(
    *,
    pilot: dict[str, Any],
    cell_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    validate_command_observation_contract_config(pilot)

    required = {
        "actual_effective_policy_id",
        "selected_action",
        "event_activation_reset_marker_delta",
        "post_enforcement_attacker_probe_count",
        "post_enforcement_attacker_reset_marker_delta",
        "legitimate_commands_attempted",
        "authorized_noop_marker_delta",
        "event_success_ns",
        "policy_enforcement_ns",
        "second_attacker_probe_observed_ns",
        "authorized_noop_probe_observed_ns",
        "run_end_ns",
    }
    missing = sorted(required - set(observation))
    if missing:
        raise ValueError(
            f"command runtime observation missing fields: {missing}"
        )

    effect = derive_observed_command_effect(
        pilot=pilot,
        cell_id=cell_id,
        observation=observation,
    )

    event_success_ns = int(observation["event_success_ns"])
    enforcement_ns = int(observation["policy_enforcement_ns"])
    second_probe_ns = int(observation["second_attacker_probe_observed_ns"])
    authorized_probe_ns = int(
        observation["authorized_noop_probe_observed_ns"]
    )
    run_end_ns = int(observation["run_end_ns"])

    if min(
        event_success_ns,
        enforcement_ns,
        second_probe_ns,
        authorized_probe_ns,
        run_end_ns,
    ) < 0:
        raise ValueError("command observation timestamps must be non-negative")

    if not (
        event_success_ns
        <= enforcement_ns
        <= second_probe_ns
        <= authorized_probe_ns
        <= run_end_ns
    ):
        raise ValueError("command observation timestamps are out of order")

    containment = bool(effect["containment_predicate_observed"])
    authorized_observed = (
        int(observation["authorized_noop_marker_delta"]) == 1
    )
    authority_convergence = containment and authorized_observed

    containment_ns = second_probe_ns if containment else None
    convergence_ns = authorized_probe_ns if authority_convergence else None

    divergence_end_ns = (
        convergence_ns if convergence_ns is not None else run_end_ns
    )
    divergence_right_censored = convergence_ns is None

    event_success = bool(effect["event_success_observed"])
    if not event_success:
        event_success_timestamp_ns = None
        divergence_interval = None
    else:
        event_success_timestamp_ns = event_success_ns
        divergence_interval = {
            "state_key": "command_authority",
            "start_ns": event_success_ns,
            "end_ns": divergence_end_ns,
            "right_censored_at_run_end": divergence_right_censored,
        }

    mo1_completed = not event_success
    mo3_completed = authorized_observed

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "event_success": {
            "predicate": event_success,
            "observed_ns": event_success_timestamp_ns,
        },
        "containment": {
            "predicate": containment,
            "observed_ns": containment_ns,
            "right_censored_at_run_end": not containment,
        },
        "authority_convergence": {
            "predicate": authority_convergence,
            "observed_ns": convergence_ns,
            "right_censored_at_run_end": divergence_right_censored,
        },
        "objective_results": {
            "MO-1": {
                "completed": mo1_completed,
                "source": (
                    "observed_e1_activation_reset_effect_over_"
                    "scheduled_interval"
                ),
            },
            "MO-3": {
                "completed": mo3_completed,
                "source": "observed_authorized_ground_noop_cfs_marker_delta",
            },
        },
        "legitimate_commands": {
            "attempted": int(effect["legitimate_commands_attempted"]),
            "rejected": int(effect["legitimate_commands_rejected"]),
        },
        "ground_spacecraft_divergence_interval": divergence_interval,
        "effect_acceptance": {
            "policy_semantics_met": effect["policy_semantics_met"],
            "effect_semantics_met": effect["effect_semantics_met"],
            "stage1_expected_effect_semantics_met": (
                effect["stage1_expected_effect_semantics_met"]
            ),
        },
        "expected_values_used_as_raw_metric_inputs": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "recovery_evidence_emitted": False,
    }


def require_command_observation_acceptance(
    derived: dict[str, Any],
) -> None:
    pseudo_effect = {
        "event_success_observed": derived["event_success"]["predicate"],
        "policy_semantics_met": derived["effect_acceptance"][
            "policy_semantics_met"
        ],
        "effect_semantics_met": derived["effect_acceptance"][
            "effect_semantics_met"
        ],
        "stage1_expected_effect_semantics_met": derived[
            "effect_acceptance"
        ]["stage1_expected_effect_semantics_met"],
    }
    require_command_effect_acceptance(pseudo_effect)

    if derived["ground_spacecraft_divergence_interval"] is None:
        raise ValueError("valid E1 command run requires divergence observation")

    convergence = derived["authority_convergence"]
    interval = derived["ground_spacecraft_divergence_interval"]

    if convergence["predicate"]:
        if convergence["observed_ns"] is None:
            raise ValueError("observed command convergence lacks timestamp")
        if interval["right_censored_at_run_end"]:
            raise ValueError("observed convergence cannot be right-censored")
        if interval["end_ns"] != convergence["observed_ns"]:
            raise ValueError("divergence end differs from observed convergence")
    else:
        if convergence["observed_ns"] is not None:
            raise ValueError("non-convergence cannot have convergence timestamp")
        if not interval["right_censored_at_run_end"]:
            raise ValueError("non-convergence must be right-censored at run end")
