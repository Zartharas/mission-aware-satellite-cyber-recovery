from __future__ import annotations

from copy import deepcopy
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy
from .policy_gateway import build_command_envelope, decide_forward

DECISION_ID = "R-029"
COMMAND_EVENT_ID = "E1"
COMMAND_CELL_IDS = (
    "C01",
    "C02",
    "C03",
    "C04",
    "C05",
    "C06",
    "C07",
)

MODELED_ATTACKER_SOURCE = "modeled_attacker"
AUTHORIZED_GROUND_SOURCE = "authorized_ground"
ATTACKER_COMMAND_CLASS = "sample_reset_counters"
AUTHORIZED_COMMAND_CLASS = "sample_noop"

MATCHED_ATTACKER_PROBE_COUNT = 2
AUTHORIZED_NOOP_ATTEMPT_COUNT = 1


def _cells_by_id(pilot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cells = pilot["cells"]
    by_id = {row["cell_id"]: row for row in cells}
    if len(by_id) != len(cells):
        raise ValueError("duplicate WP8 pilot cell_id")
    return by_id


def command_cells(pilot: dict[str, Any]) -> list[dict[str, Any]]:
    cells = _cells_by_id(pilot)
    stage1_ids = list(pilot["stage_1_control_validity"]["cell_ids"])

    result = [
        deepcopy(cells[cell_id])
        for cell_id in stage1_ids
        if cells[cell_id]["event_id"] == COMMAND_EVENT_ID
        and cells[cell_id]["family"].startswith("command_")
    ]

    ids = tuple(row["cell_id"] for row in result)
    if ids != COMMAND_CELL_IDS:
        raise ValueError(
            "Stage-1 command cells differ from frozen C01-C07 declaration"
        )

    return result


def validate_command_effect_contract_config(
    pilot: dict[str, Any],
) -> None:
    runner = pilot["stage_1_runner_contract"]
    contract = runner["command_effect_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    if contract["decision_id"] != DECISION_ID:
        raise ValueError("Stage-1 command effect contract is not R-029")
    if contract["factor_source"] != "wp8_pilot_design.cells":
        raise ValueError("command factors must come from WP8 pilot cells")
    if contract["policy_evaluation_source"] != (
        "src.mission_recovery.policies.evaluate_policy"
    ):
        raise ValueError("command policy evaluation source changed")
    if contract["gateway_action_source"] != (
        "evaluated_policy_decision.selected_action"
    ):
        raise ValueError("command gateway action source changed")
    if int(contract["matched_attacker_probe_count"]) != (
        MATCHED_ATTACKER_PROBE_COUNT
    ):
        raise ValueError("command containment probe count changed")
    if contract["containment_observation_source"] != (
        "observed_post_enforcement_cfs_reset_marker_delta"
    ):
        raise ValueError("command containment observation source changed")
    if contract["legitimate_service_observation_source"] != (
        "observed_authorized_ground_cfs_noop_marker_delta"
    ):
        raise ValueError("command legitimate-service observation source changed")
    if contract["expected_effect_values_role"] != (
        "post_observation_acceptance_only_not_metric_inputs"
    ):
        raise ValueError("expected command effects cannot become metric inputs")
    if contract["terminal_state_source"] != (
        "existing_runtime_binding_and_primary_metric_scorer"
    ):
        raise ValueError("command contract cannot emit terminal state")
    if contract["primary_metric_source"] != (
        "existing_runtime_binding_and_primary_metric_scorer"
    ):
        raise ValueError("command contract cannot emit primary metrics")
    if contract["offline_validation_executes_runtime"] is not False:
        raise ValueError("R-029 offline validation cannot execute runtime")
    if contract["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError("R-029 offline validation cannot consume pilot seed")

    if status["stage_1_command_effect_contract"] is not True:
        raise ValueError("Stage-1 command effect contract status is not closed")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("Stage-1 runtime dispatch adapters cannot pass in R-029")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("pilot execution must remain blocked in R-029")

    command_cells(pilot)


def _command_cell(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    matches = {
        row["cell_id"]: row
        for row in command_cells(pilot)
    }
    if cell_id not in matches:
        raise ValueError(f"not a frozen Stage-1 command cell: {cell_id}")
    return deepcopy(matches[cell_id])


def build_command_cell_effect_contract(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    validate_command_effect_contract_config(pilot)

    cell = _command_cell(pilot, cell_id)
    seed = int(pilot["stage_1_control_validity"]["seed"])

    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )

    decision = evaluate_policy(cell["policy_id"], event)
    actual_effective = decision["delegated_policy_id"]

    if actual_effective != cell["expected_effective_policy_id"]:
        raise ValueError(
            f"{cell_id}: policy engine returned {actual_effective}, "
            f"frozen pilot expected {cell['expected_effective_policy_id']}"
        )

    selected_action = decision["selected_action"]

    attacker_envelope = build_command_envelope(
        MODELED_ATTACKER_SOURCE,
        ATTACKER_COMMAND_CLASS,
    )
    authorized_envelope = build_command_envelope(
        AUTHORIZED_GROUND_SOURCE,
        AUTHORIZED_COMMAND_CLASS,
    )

    attacker_forwarded = decide_forward(
        selected_action,
        attacker_envelope,
    )
    authorized_forwarded = decide_forward(
        selected_action,
        authorized_envelope,
    )

    expected_attacker_delta = (
        MATCHED_ATTACKER_PROBE_COUNT
        if attacker_forwarded
        else 0
    )
    expected_authorized_delta = (
        AUTHORIZED_NOOP_ATTEMPT_COUNT
        if authorized_forwarded
        else 0
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "seed": seed,
        "factor_source": "wp8_pilot_design.cells",
        "factor_context_without_run_id": {
            "model_version": pilot["model_version"],
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": cell["event_id"],
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance_sha256": event["instance_sha256"],
        "policy_evaluation": {
            "requested_policy_id": cell["policy_id"],
            "actual_effective_policy_id": actual_effective,
            "expected_effective_policy_id_for_acceptance_only": (
                cell["expected_effective_policy_id"]
            ),
            "selected_action": selected_action,
            "decision_sha256": decision["decision_sha256"],
            "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        },
        "gateway_execution": {
            "action_source": (
                "evaluated_policy_decision.selected_action"
            ),
            "action": selected_action,
            "attacker_probe": {
                "source_id": MODELED_ATTACKER_SOURCE,
                "command_class": ATTACKER_COMMAND_CLASS,
                "probe_count": MATCHED_ATTACKER_PROBE_COUNT,
                "expected_gateway_forwarded_for_acceptance_only": (
                    attacker_forwarded
                ),
                "expected_cfs_reset_marker_delta_for_acceptance_only": (
                    expected_attacker_delta
                ),
            },
            "authorized_probe": {
                "source_id": AUTHORIZED_GROUND_SOURCE,
                "command_class": AUTHORIZED_COMMAND_CLASS,
                "attempt_count": AUTHORIZED_NOOP_ATTEMPT_COUNT,
                "expected_gateway_forwarded_for_acceptance_only": (
                    authorized_forwarded
                ),
                "expected_cfs_noop_marker_delta_for_acceptance_only": (
                    expected_authorized_delta
                ),
            },
        },
        "observation_contract": {
            "event_success_source": (
                "observed_event_activation_cfs_reset_marker_delta"
            ),
            "containment_source": (
                "observed_post_enforcement_cfs_reset_marker_delta"
            ),
            "legitimate_rejection_source": (
                "observed_authorized_ground_cfs_noop_marker_delta"
            ),
            "expected_values_role": (
                "post_observation_acceptance_only_not_metric_inputs"
            ),
            "primary_metrics_emitted": False,
            "terminal_state_emitted": False,
        },
        "offline_only": True,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
    }


def build_command_effect_matrix(
    pilot: dict[str, Any],
) -> dict[str, Any]:
    validate_command_effect_contract_config(pilot)
    rows = [
        build_command_cell_effect_contract(
            pilot,
            cell["cell_id"],
        )
        for cell in command_cells(pilot)
    ]
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_STAGE1_COMMAND_EFFECT_CONTRACT_OFFLINE",
        "seed": int(pilot["stage_1_control_validity"]["seed"]),
        "cell_ids": [row["cell_id"] for row in rows],
        "rows": rows,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
        "primary_metrics_emitted": False,
        "terminal_states_emitted": False,
    }


def derive_observed_command_effect(
    *,
    pilot: dict[str, Any],
    cell_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    contract = build_command_cell_effect_contract(
        pilot,
        cell_id,
    )

    required = {
        "actual_effective_policy_id",
        "selected_action",
        "event_activation_reset_marker_delta",
        "post_enforcement_attacker_probe_count",
        "post_enforcement_attacker_reset_marker_delta",
        "legitimate_commands_attempted",
        "authorized_noop_marker_delta",
    }
    missing = sorted(required - set(observation))
    if missing:
        raise ValueError(
            f"command effect observation missing fields: {missing}"
        )

    event_delta = int(
        observation["event_activation_reset_marker_delta"]
    )
    attacker_count = int(
        observation["post_enforcement_attacker_probe_count"]
    )
    attacker_delta = int(
        observation["post_enforcement_attacker_reset_marker_delta"]
    )
    attempted = int(observation["legitimate_commands_attempted"])
    authorized_delta = int(
        observation["authorized_noop_marker_delta"]
    )

    if event_delta < 0:
        raise ValueError("event activation reset marker delta cannot be negative")
    if attacker_count != MATCHED_ATTACKER_PROBE_COUNT:
        raise ValueError(
            "command containment requires exactly two matched attacker probes"
        )
    if attacker_delta < 0 or attacker_delta > attacker_count:
        raise ValueError("attacker reset marker delta outside probe bounds")
    if attempted != AUTHORIZED_NOOP_ATTEMPT_COUNT:
        raise ValueError(
            "command legitimate-service probe requires one authorized NOOP"
        )
    if authorized_delta < 0 or authorized_delta > attempted:
        raise ValueError("authorized NOOP marker delta outside attempt bounds")

    event_success_observed = event_delta == 1
    containment_observed = (
        attacker_count == MATCHED_ATTACKER_PROBE_COUNT
        and attacker_delta == 0
    )
    legitimate_commands_rejected = attempted - authorized_delta

    policy = contract["policy_evaluation"]
    gateway = contract["gateway_execution"]

    policy_semantics_met = (
        observation["actual_effective_policy_id"]
        == policy["actual_effective_policy_id"]
        and observation["selected_action"]
        == policy["selected_action"]
    )

    expected_attacker_delta = gateway["attacker_probe"][
        "expected_cfs_reset_marker_delta_for_acceptance_only"
    ]
    expected_authorized_delta = gateway["authorized_probe"][
        "expected_cfs_noop_marker_delta_for_acceptance_only"
    ]

    effect_semantics_met = (
        event_success_observed
        and attacker_delta == expected_attacker_delta
        and authorized_delta == expected_authorized_delta
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "event_success_observed": event_success_observed,
        "containment_predicate_observed": containment_observed,
        "legitimate_commands_attempted": attempted,
        "legitimate_commands_rejected": legitimate_commands_rejected,
        "observed_post_enforcement_attacker_reset_marker_delta": (
            attacker_delta
        ),
        "observed_authorized_noop_marker_delta": authorized_delta,
        "actual_effective_policy_id": observation[
            "actual_effective_policy_id"
        ],
        "selected_action": observation["selected_action"],
        "policy_semantics_met": policy_semantics_met,
        "effect_semantics_met": effect_semantics_met,
        "stage1_expected_effect_semantics_met": (
            policy_semantics_met and effect_semantics_met
        ),
        "expected_values_used_as_metric_inputs": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
    }


def require_command_effect_acceptance(
    derived: dict[str, Any],
) -> None:
    if derived["event_success_observed"] is not True:
        raise ValueError("E1 activation effect was not observed")
    if derived["policy_semantics_met"] is not True:
        raise ValueError("observed command policy semantics differ from frozen cell")
    if derived["effect_semantics_met"] is not True:
        raise ValueError("observed command effects differ from frozen cell semantics")
    if derived["stage1_expected_effect_semantics_met"] is not True:
        raise ValueError("Stage-1 command effect acceptance failed")
