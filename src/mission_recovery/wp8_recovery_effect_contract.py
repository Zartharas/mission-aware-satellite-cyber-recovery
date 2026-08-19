from __future__ import annotations

from copy import deepcopy
from typing import Any

from .events import materialize_event
from .p7_effect_dispatch import build_p7_effect_plan
from .policies import evaluate_policy
from .policy_gateway import build_command_envelope, decide_forward
from .rollback_requests import build_verified_rollback_request
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)

DECISION_ID = "R-034"
RECOVERY_EVENT_ID = "E3"
RECOVERY_CELL_IDS = ("R01", "R02", "R03", "R04")

MODELED_ATTACKER_SOURCE = "modeled_attacker"
AUTHORIZED_GROUND_SOURCE = "authorized_ground"
ATTACKER_COMMAND_CLASS = "sample_reset_counters"
AUTHORIZED_COMMAND_CLASS = "sample_noop"
MATCHED_ATTACKER_PROBE_COUNT = 2
AUTHORIZED_NOOP_ATTEMPT_COUNT = 1

EFFECT_FAMILY_BY_EFFECTIVE_POLICY = {
    "P0": "observe_only",
    "P2": "command_gateway",
    "P5": "rollback_request",
}


def _cells_by_id(pilot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cells = pilot["cells"]
    by_id = {row["cell_id"]: row for row in cells}
    if len(by_id) != len(cells):
        raise ValueError("duplicate WP8 pilot cell_id")
    return by_id


def recovery_cells(pilot: dict[str, Any]) -> list[dict[str, Any]]:
    cells = _cells_by_id(pilot)
    stage1_ids = list(pilot["stage_1_control_validity"]["cell_ids"])

    result = [
        deepcopy(cells[cell_id])
        for cell_id in stage1_ids
        if cells[cell_id]["event_id"] == RECOVERY_EVENT_ID
        and cells[cell_id]["family"].startswith("recovery_")
    ]

    ids = tuple(row["cell_id"] for row in result)
    if ids != RECOVERY_CELL_IDS:
        raise ValueError(
            "Stage-1 recovery cells differ from frozen R01-R04 declaration"
        )
    return result


def _artifacts() -> dict[str, Any]:
    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    verification = verify_candidate(tampered, manifest)

    approved_sha = sha256_hex(approved)
    tampered_sha = sha256_hex(tampered)

    if approved_sha != manifest["approved_sha256"]:
        raise ValueError("approved recovery artifact identity changed")
    if approved_sha != (
        "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
    ):
        raise ValueError("approved recovery artifact SHA changed")
    if tampered_sha != (
        "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"
    ):
        raise ValueError("tampered recovery artifact SHA changed")
    if verification["accepted"] is not False:
        raise ValueError("tampered candidate unexpectedly accepted")
    if "sha256_mismatch" not in verification["reasons"]:
        raise ValueError("tampered candidate rejection reason changed")

    return {
        "approved": approved,
        "tampered": tampered,
        "manifest": manifest,
        "tampered_verification": verification,
        "approved_sha256": approved_sha,
        "tampered_sha256": tampered_sha,
    }


def validate_recovery_effect_contract_config(
    pilot: dict[str, Any],
) -> None:
    runner = pilot["stage_1_runner_contract"]
    contract = runner["recovery_effect_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    if contract["decision_id"] != DECISION_ID:
        raise ValueError("Stage-1 recovery effect contract is not R-034")
    if contract["factor_source"] != "wp8_pilot_design.cells":
        raise ValueError("recovery factors must come from WP8 pilot cells")
    if contract["policy_evaluation_source"] != (
        "src.mission_recovery.policies.evaluate_policy"
    ):
        raise ValueError("recovery policy evaluation source changed")
    if contract["p7_effect_dispatch_source"] != (
        "src.mission_recovery.p7_effect_dispatch.build_p7_effect_plan"
    ):
        raise ValueError("recovery P7 effect dispatch source changed")
    if contract["event_success_source"] != (
        "observed_retained_tampered_sha256_in_modeled_activation_slot_after_t0"
    ):
        raise ValueError("recovery event-success source changed")
    if contract["effect_family_by_effective_policy"] != (
        EFFECT_FAMILY_BY_EFFECTIVE_POLICY
    ):
        raise ValueError("recovery effect-family mapping changed")
    if contract["rollback_containment_source"] != (
        "approved_sha256_occupies_modeled_activation_slot_and_rejected_sha256_"
        "is_absent_and_temporary_recovery_state_is_absent"
    ):
        raise ValueError("recovery rollback containment source changed")
    if contract["nonrollback_update_slot_rule"] != (
        "P0_and_P2_do_not_replace_the_tampered_modeled_activation_slot"
    ):
        raise ValueError("recovery non-rollback slot rule changed")
    if contract["p2_command_gateway_probe_rule"] != (
        "two_modeled_attacker_reset_probes_blocked_and_one_authorized_noop_forwarded"
    ):
        raise ValueError("recovery P2 command-gateway probe rule changed")
    if contract["expected_effect_values_role"] != (
        "post_observation_acceptance_only_not_raw_metric_substitution"
    ):
        raise ValueError(
            "recovery expected effects cannot substitute observations"
        )
    if (
        contract[
            "recovery_criteria_evaluation_deferred_to_observation_contract"
        ]
        is not True
    ):
        raise ValueError(
            "R-034 must defer recovery criteria to observation contract"
        )
    if contract["emits_primary_metrics"] is not False:
        raise ValueError("R-034 cannot emit primary metrics")
    if contract["emits_terminal_state"] is not False:
        raise ValueError("R-034 cannot emit terminal state")
    if contract["emits_trusted_recovery_evidence"] is not False:
        raise ValueError("R-034 cannot emit trusted-recovery evidence")
    if contract["offline_validation_executes_runtime"] is not False:
        raise ValueError("R-034 offline validation cannot execute runtime")
    if contract["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError(
            "R-034 offline validation cannot consume pilot seed"
        )

    if (
        status["stage_1_command_runtime_executor_runtime_validated"]
        is not True
    ):
        raise ValueError(
            "R-033 command runtime validation must remain closed"
        )
    if status["stage_1_recovery_effect_contract"] is not True:
        raise ValueError(
            "R-034 recovery effect contract status is not closed"
        )
    if not isinstance(
        status["stage_1_recovery_observation_contract"],
        bool,
    ):
        raise ValueError(
            "recovery observation contract gate must remain boolean"
        )
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError(
            "runtime dispatch adapters cannot pass in R-034"
        )
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("pilot execution must remain blocked in R-034")

    recovery_cells(pilot)
    _artifacts()


def _recovery_cell(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    cells = {row["cell_id"]: row for row in recovery_cells(pilot)}
    if cell_id not in cells:
        raise ValueError(
            f"not a frozen Stage-1 recovery cell: {cell_id}"
        )
    return deepcopy(cells[cell_id])


def build_recovery_cell_effect_contract(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    validate_recovery_effect_contract_config(pilot)

    cell = _recovery_cell(pilot, cell_id)
    seed = int(pilot["stage_1_control_validity"]["seed"])
    artifacts = _artifacts()

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
    if actual_effective not in EFFECT_FAMILY_BY_EFFECTIVE_POLICY:
        raise ValueError(
            f"{cell_id}: unsupported recovery effective policy "
            f"{actual_effective}"
        )

    effect_family = EFFECT_FAMILY_BY_EFFECTIVE_POLICY[actual_effective]
    selected_action = decision["selected_action"]

    p7_plan = None
    if cell["policy_id"] == "P7":
        p7_plan = build_p7_effect_plan(decision)
        if p7_plan["effect_family"] != effect_family:
            raise ValueError(
                f"{cell_id}: P7 effect-family dispatch changed"
            )
        if p7_plan["oracle_ground_truth_read"] is not False:
            raise ValueError(
                f"{cell_id}: P7 effect dispatch crossed oracle boundary"
            )

    rollback_expected = effect_family == "rollback_request"
    command_gateway_required = effect_family == "command_gateway"
    containment_expected = rollback_expected

    rollback_request = None
    if rollback_expected:
        rollback_request = build_verified_rollback_request(
            event_instance=event,
            policy_decision=decision,
            manifest=artifacts["manifest"],
            candidate_verification=artifacts["tampered_verification"],
        )
        if rollback_request["request_ready"] is not True:
            raise ValueError(
                f"{cell_id}: rollback request is not ready"
            )
        if (
            rollback_request["recovery_execution_performed"]
            is not False
        ):
            raise ValueError(
                f"{cell_id}: offline rollback request executed recovery"
            )

    gateway_contract = {
        "required": False,
        "action": None,
        "attacker_probe": None,
        "authorized_probe": None,
    }
    if command_gateway_required:
        attacker = build_command_envelope(
            MODELED_ATTACKER_SOURCE,
            ATTACKER_COMMAND_CLASS,
        )
        authorized = build_command_envelope(
            AUTHORIZED_GROUND_SOURCE,
            AUTHORIZED_COMMAND_CLASS,
        )
        attacker_forwarded = decide_forward(
            selected_action,
            attacker,
        )
        authorized_forwarded = decide_forward(
            selected_action,
            authorized,
        )

        gateway_contract = {
            "required": True,
            "action": selected_action,
            "attacker_probe": {
                "source_id": MODELED_ATTACKER_SOURCE,
                "command_class": ATTACKER_COMMAND_CLASS,
                "probe_count": MATCHED_ATTACKER_PROBE_COUNT,
                "expected_gateway_forwarded_for_acceptance_only": (
                    attacker_forwarded
                ),
                "expected_cfs_reset_marker_delta_for_acceptance_only": (
                    MATCHED_ATTACKER_PROBE_COUNT
                    if attacker_forwarded
                    else 0
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
                    AUTHORIZED_NOOP_ATTEMPT_COUNT
                    if authorized_forwarded
                    else 0
                ),
            },
        }

    expected_post_slot = (
        artifacts["approved_sha256"]
        if containment_expected
        else artifacts["tampered_sha256"]
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
            "contact_condition_id": cell[
                "contact_condition_id"
            ],
            "evidence_condition_id": cell[
                "evidence_condition_id"
            ],
        },
        "event_instance_sha256": event["instance_sha256"],
        "event_artifacts": {
            "approved_sha256": artifacts["approved_sha256"],
            "tampered_sha256": artifacts["tampered_sha256"],
            "tampered_candidate_verification_accepted": False,
            "tampered_candidate_rejection_reasons": list(
                artifacts["tampered_verification"]["reasons"]
            ),
        },
        "policy_evaluation": {
            "requested_policy_id": cell["policy_id"],
            "actual_effective_policy_id": actual_effective,
            "expected_effective_policy_id_for_acceptance_only": (
                cell["expected_effective_policy_id"]
            ),
            "selected_action": selected_action,
            "decision_sha256": decision["decision_sha256"],
            "decision_basis": decision["decision_basis"],
            "evidence_insufficient": decision[
                "evidence_insufficient"
            ],
            "oracle_ground_truth_read": decision[
                "oracle_ground_truth_read"
            ],
        },
        "effect_dispatch": {
            "effect_family": effect_family,
            "rollback_request_expected_for_acceptance_only": (
                rollback_expected
            ),
            "command_gateway_probe_required_for_acceptance_only": (
                command_gateway_required
            ),
            "update_slot_mutation_expected_for_acceptance_only": (
                containment_expected
            ),
            "expected_post_response_slot_sha256_for_acceptance_only": (
                expected_post_slot
            ),
            "containment_expected_for_acceptance_only": (
                containment_expected
            ),
            "trusted_recovery_verification_required": (
                rollback_expected
            ),
            "trusted_recovery_verification_deferred_to_r035": True,
        },
        "p7_effect_plan": p7_plan,
        "rollback_request_contract": {
            "expected": rollback_expected,
            "request_ready_for_acceptance_only": (
                rollback_request["request_ready"]
                if rollback_request
                else False
            ),
            "request_sha256_for_acceptance_only": (
                rollback_request["request_sha256"]
                if rollback_request
                else None
            ),
            "rollback_staging_performed_offline": False,
            "rollback_activation_performed_offline": False,
            "recovery_execution_performed_offline": False,
        },
        "command_gateway_contract": gateway_contract,
        "observation_contract": {
            "event_success_source": (
                "observed_retained_tampered_sha256_in_modeled_"
                "activation_slot_after_t0"
            ),
            "rollback_containment_source": (
                "approved_sha256_occupies_modeled_activation_slot_"
                "and_rejected_sha256_is_absent_and_temporary_"
                "recovery_state_is_absent"
            ),
            "nonrollback_slot_source": (
                "observed_tampered_sha256_remains_in_modeled_"
                "activation_slot"
            ),
            "p2_gateway_source": (
                "observed_gateway_decisions_and_cfs_marker_deltas"
            ),
            "expected_values_role": (
                "post_observation_acceptance_only_not_raw_"
                "metric_substitution"
            ),
            "recovery_criteria_evaluation_deferred_to_r035": True,
            "primary_metrics_emitted": False,
            "terminal_state_emitted": False,
            "trusted_recovery_evidence_emitted": False,
        },
        "offline_only": True,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "trusted_recovery_evidence_emitted": False,
    }


def build_recovery_effect_matrix(
    pilot: dict[str, Any],
) -> dict[str, Any]:
    validate_recovery_effect_contract_config(pilot)
    rows = [
        build_recovery_cell_effect_contract(pilot, cell_id)
        for cell_id in RECOVERY_CELL_IDS
    ]
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": (
            "WP8_STAGE1_RECOVERY_EFFECT_CONTRACT_OFFLINE"
        ),
        "seed": int(
            pilot["stage_1_control_validity"]["seed"]
        ),
        "cell_ids": list(RECOVERY_CELL_IDS),
        "rows": rows,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
        "primary_metrics_emitted": False,
        "terminal_states_emitted": False,
        "trusted_recovery_evidence_emitted": False,
    }


def derive_observed_recovery_effect(
    *,
    pilot: dict[str, Any],
    cell_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    contract = build_recovery_cell_effect_contract(
        pilot,
        cell_id,
    )

    required = {
        "actual_effective_policy_id",
        "selected_action",
        "event_slot_sha256",
        "post_response_slot_sha256",
        "rejected_sha256_absent",
        "temporary_recovery_state_absent",
        "rollback_request_emitted",
        "rollback_request_validated",
        "replacement_source_verified",
    }
    missing = sorted(required - set(observation))
    if missing:
        raise ValueError(
            f"recovery effect observation missing fields: {missing}"
        )

    event_artifacts = contract["event_artifacts"]
    policy = contract["policy_evaluation"]
    dispatch = contract["effect_dispatch"]
    effect_family = dispatch["effect_family"]

    event_success = (
        observation["event_slot_sha256"]
        == event_artifacts["tampered_sha256"]
    )

    containment = (
        observation["post_response_slot_sha256"]
        == event_artifacts["approved_sha256"]
        and observation["rejected_sha256_absent"] is True
        and observation["temporary_recovery_state_absent"] is True
    )

    policy_semantics_met = (
        observation["actual_effective_policy_id"]
        == policy["actual_effective_policy_id"]
        and observation["selected_action"]
        == policy["selected_action"]
    )

    gateway_observation = observation.get(
        "command_gateway_observation"
    )

    if effect_family == "observe_only":
        effect_semantics_met = (
            event_success
            and observation["rollback_request_emitted"] is False
            and observation["rollback_request_validated"] is False
            and observation["replacement_source_verified"] is False
            and observation["post_response_slot_sha256"]
            == event_artifacts["tampered_sha256"]
            and observation["rejected_sha256_absent"] is False
            and observation[
                "temporary_recovery_state_absent"
            ]
            is True
            and gateway_observation is None
            and containment is False
        )
    elif effect_family == "rollback_request":
        effect_semantics_met = (
            event_success
            and observation["rollback_request_emitted"] is True
            and observation["rollback_request_validated"] is True
            and observation["replacement_source_verified"] is True
            and gateway_observation is None
            and containment is True
        )
    elif effect_family == "command_gateway":
        if not isinstance(gateway_observation, dict):
            gateway_semantics_met = False
        else:
            gateway_semantics_met = (
                int(
                    gateway_observation.get(
                        "matched_attacker_probe_count",
                        -1,
                    )
                )
                == MATCHED_ATTACKER_PROBE_COUNT
                and int(
                    gateway_observation.get(
                        "attacker_reset_marker_delta",
                        -1,
                    )
                )
                == 0
                and int(
                    gateway_observation.get(
                        "authorized_noop_attempt_count",
                        -1,
                    )
                )
                == AUTHORIZED_NOOP_ATTEMPT_COUNT
                and int(
                    gateway_observation.get(
                        "authorized_noop_marker_delta",
                        -1,
                    )
                )
                == AUTHORIZED_NOOP_ATTEMPT_COUNT
            )
        effect_semantics_met = (
            event_success
            and observation["rollback_request_emitted"] is False
            and observation["rollback_request_validated"] is False
            and observation["replacement_source_verified"] is False
            and observation["post_response_slot_sha256"]
            == event_artifacts["tampered_sha256"]
            and observation["rejected_sha256_absent"] is False
            and observation[
                "temporary_recovery_state_absent"
            ]
            is True
            and gateway_semantics_met
            and containment is False
        )
    else:
        raise ValueError(
            f"unsupported recovery effect family: {effect_family}"
        )

    expected_containment = bool(
        dispatch["containment_expected_for_acceptance_only"]
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "event_success_observed": event_success,
        "containment_predicate_observed": containment,
        "containment_expected_for_acceptance_only": (
            expected_containment
        ),
        "non_recovery_behavior_expected": (
            not expected_containment
        ),
        "non_recovery_behavior_observed": (
            not containment and effect_semantics_met
        ),
        "trusted_recovery_verification_permitted": (
            effect_family == "rollback_request"
            and containment
        ),
        "effect_family": effect_family,
        "actual_effective_policy_id": observation[
            "actual_effective_policy_id"
        ],
        "selected_action": observation["selected_action"],
        "policy_semantics_met": policy_semantics_met,
        "effect_semantics_met": effect_semantics_met,
        "stage1_expected_effect_semantics_met": (
            policy_semantics_met
            and effect_semantics_met
            and containment == expected_containment
        ),
        "recovery_criteria_evaluated": False,
        "expected_values_used_as_raw_metric_inputs": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "trusted_recovery_evidence_emitted": False,
    }


def require_recovery_effect_acceptance(
    derived: dict[str, Any],
) -> None:
    if derived["event_success_observed"] is not True:
        raise ValueError("E3 activation effect was not observed")
    if derived["policy_semantics_met"] is not True:
        raise ValueError(
            "observed recovery policy semantics differ from frozen cell"
        )
    if derived["effect_semantics_met"] is not True:
        raise ValueError(
            "observed recovery effects differ from frozen cell semantics"
        )
    if derived["containment_predicate_observed"] != (
        derived["containment_expected_for_acceptance_only"]
    ):
        raise ValueError(
            "observed recovery containment differs from frozen cell"
        )
    if derived["stage1_expected_effect_semantics_met"] is not True:
        raise ValueError(
            "Stage-1 recovery effect acceptance failed"
        )
