from __future__ import annotations
from typing import Any

from .primary_metrics import RECOVERY_CRITERIA
from .wp8_recovery_effect_contract import (
    RECOVERY_CELL_IDS,
    build_recovery_cell_effect_contract,
    derive_observed_recovery_effect,
    require_recovery_effect_acceptance,
)

DECISION_ID = "R-036"
MO4_STATE_CRITERIA = tuple(
    c for c in RECOVERY_CRITERIA
    if c != "recovery_manifest_complete"
)
MO5_EVIDENCE_CRITERION = "recovery_manifest_complete"


def validate_recovery_observation_contract_config(
    pilot: dict[str, Any],
) -> None:
    c = pilot["stage_1_runner_contract"]["recovery_observation_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    required = {
        "decision_id": "R-036",
        "event_success_source":
            "observed_retained_tampered_sha256_in_modeled_activation_slot_after_t0",
        "event_success_observer_revision": "R-019",
        "event_success_must_complete_by": "policy_enforcement_boundary",
        "containment_timestamp_rule":
            "post_response_slot_observation_when_R034_update_containment_is_observed",
        "containment_censoring_rule":
            "null_and_right_censored_at_run_end_when_update_containment_is_not_observed",
        "r04_command_mitigation_rule":
            "observed_P2_command_gateway_mitigation_is_recorded_separately_and_never_counts_as_E3_update_containment",
        "divergence_state_key": "approved_version",
        "divergence_start": "observed_E3_event_success_timestamp",
        "divergence_end_if_contained": "observed_update_containment_timestamp",
        "divergence_end_if_uncontained": "observed_run_end_ns_right_censoring",
        "classification_time_evidence_rule":
            "derive_available_current_from_retained_classification_time_evidence_not_policy_visibility_at_selection",
        "t1_policy_visibility_rule":
            "policy_time_omission_does_not_automatically_imply_classification_time_M08_loss",
        "approved_version_observation_rule":
            "post_response_slot_SHA_is_current_classification_evidence_even_when_approved_version_was_omitted_from_R04_policy_visible_evidence",
        "mo4_completion_rule":
            "all_MO4_state_criteria_are_available_current_and_satisfied",
        "mo5_completion_rule":
            "recovery_manifest_complete_is_available_current_and_satisfied",
        "nonrecovery_mo5_rule":
            "R01_or_R04_nonrecovery_does_not_by_itself_make_MO5_false",
        "trusted_recovery_rule":
            "update_containment_observed_AND_all_ten_criteria_available_current_AND_all_ten_criteria_satisfied",
        "trusted_recovery_timestamp_rule":
            "max_of_update_containment_timestamp_and_all_ten_criterion_observed_ns",
        "trusted_recovery_censoring_rule":
            "null_and_right_censored_at_run_end_when_trusted_recovery_is_not_observed",
        "authorized_noop_probe_rule":
            "one_post_response_authorized_noop_attempt_per_recovery_cell",
        "expected_values_role":
            "post_observation_acceptance_only_not_raw_metric_substitution",
    }
    for k,v in required.items():
        if c[k] != v:
            raise ValueError(f"R-036 contract changed: {k}")
    if c["event_success_observation_can_gate_policy_response"] is not False:
        raise ValueError("R-036 event observer cannot gate policy response")
    if c["criterion_dimensions"] != [
        "available_current","criterion_satisfied","evidence_ref","observed_ns"
    ] or c["criterion_count"] != 10:
        raise ValueError("R-036 criterion observation shape changed")
    if tuple(c["mo4_state_criteria"]) != MO4_STATE_CRITERIA:
        raise ValueError("R-036 MO-4 state criteria changed")
    if c["emits_primary_metrics"] is not False or c["emits_terminal_state"] is not False:
        raise ValueError("R-036 cannot emit metrics or terminal state")
    if c["offline_validation_executes_runtime"] is not False:
        raise ValueError("R-036 cannot execute runtime")
    if c["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError("R-036 cannot consume pilot seed")

    sem=pilot["runtime_measurement_contract"]["recovery_evidence_semantics"]
    if sem["decision_id"]!="R-035":
        raise ValueError("R-036 requires R-035")
    app=pilot["runtime_measurement_contract"][
        "family_recovery_criteria_applicability"
    ]["recovery"]
    if set(app["applicable"])!=set(RECOVERY_CRITERIA) or app["excluded"]!=[]:
        raise ValueError("R-036 requires all ten E3 criteria")
    if status["stage_1_recovery_effect_contract"] is not True:
        raise ValueError("R-036 requires R-034")
    if status["recovery_evidence_semantics_separated"] is not True:
        raise ValueError("R-036 requires R-035 semantics")
    if status["stage_1_recovery_observation_contract"] is not True:
        raise ValueError("R-036 observation gate is not closed")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("R-036 cannot close runtime adapters")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("R-036 cannot authorize pilot execution")


def build_recovery_observation_plan(
    pilot: dict[str, Any], cell_id: str
) -> dict[str, Any]:
    validate_recovery_observation_contract_config(pilot)
    effect=build_recovery_cell_effect_contract(pilot,cell_id)
    family=effect["effect_dispatch"]["effect_family"]
    return {
        "schema":1,"decision_id":DECISION_ID,"cell_id":cell_id,
        "seed":effect["seed"],"effect_family":family,
        "expected_effective_policy_id_for_acceptance_only":
            effect["policy_evaluation"]["actual_effective_policy_id"],
        "update_containment_expected_for_acceptance_only":
            bool(effect["effect_dispatch"]["containment_expected_for_acceptance_only"]),
        "command_path_mitigation_applicable":family=="command_gateway",
        "command_path_mitigation_counts_as_update_containment":False,
        "trusted_recovery_verification_applicable":family=="rollback_request",
        "mo4_state_criteria":list(MO4_STATE_CRITERIA),
        "mo5_evidence_criterion":MO5_EVIDENCE_CRITERION,
        "mo4_expected_value_frozen":False,
        "mo5_expected_value_frozen":False,
        "trusted_recovery_expected_value_frozen":False,
        "event_observer_can_gate_policy_response":False,
        "policy_time_visibility_can_substitute_for_classification_evidence":False,
        "expected_values_used_as_raw_metric_inputs":False,
        "primary_metrics_emitted":False,"terminal_state_emitted":False,
        "runtime_execution_authorized":False,"pilot_seed_consumed":False,
        "pilot_data_generated":False,
    }


def build_recovery_observation_matrix(pilot: dict[str, Any]) -> dict[str, Any]:
    validate_recovery_observation_contract_config(pilot)
    rows=[build_recovery_observation_plan(pilot,c) for c in RECOVERY_CELL_IDS]
    return {
        "schema":1,"decision_id":DECISION_ID,
        "classification":"WP8_STAGE1_RECOVERY_OBSERVATION_CONTRACT_OFFLINE",
        "cell_ids":list(RECOVERY_CELL_IDS),"rows":rows,
        "runtime_execution_authorized":False,"pilot_seed_consumed":False,
        "pilot_data_generated":False,"primary_metrics_emitted":False,
        "terminal_states_emitted":False,
    }


def _criteria(
    observation: dict[str, Any], classification_ns: int, containment: bool
) -> dict[str, dict[str, Any]]:
    supplied=observation["recovery_criteria"]
    if set(supplied)!=set(RECOVERY_CRITERIA):
        raise ValueError("recovery criteria must contain exactly all ten criteria")
    out={}
    for criterion in RECOVERY_CRITERIA:
        row=supplied[criterion]
        need={"available_current","criterion_satisfied","evidence_ref","observed_ns"}
        missing=sorted(need-set(row))
        if missing:
            raise ValueError(f"criterion fields missing {criterion}: {missing}")
        a=row["available_current"]; s=row["criterion_satisfied"]
        if not isinstance(a,bool) or not isinstance(s,bool):
            raise ValueError(f"criterion booleans required: {criterion}")
        if s and not a:
            raise ValueError(
                "criterion_satisfied=true requires available_current=true: "
                + criterion
            )
        ref=row["evidence_ref"]
        if not isinstance(ref,str) or not ref:
            raise ValueError(f"criterion evidence_ref required: {criterion}")
        ns=int(row["observed_ns"])
        if ns<0 or ns>classification_ns:
            raise ValueError(f"criterion timestamp outside classification: {criterion}")
        out[criterion]={
            "available_current":a,"criterion_satisfied":s,
            "evidence_ref":ref,"observed_ns":ns,
        }

    approved=out["approved_version"]
    if approved["available_current"] is not True:
        raise ValueError("post-response slot SHA must provide current approved-version evidence")
    if approved["criterion_satisfied"] != containment:
        raise ValueError("approved-version criterion disagrees with observed update slot")

    manifest=out["recovery_manifest_complete"]
    if manifest["criterion_satisfied"]:
        latest=max(
            row["observed_ns"] for key,row in out.items()
            if key!="recovery_manifest_complete"
        )
        if manifest["observed_ns"]<latest:
            raise ValueError("complete manifest predates retained criterion evidence")
    return out


def derive_recovery_runtime_observation(
    *, pilot: dict[str, Any], cell_id: str, observation: dict[str, Any]
) -> dict[str, Any]:
    validate_recovery_observation_contract_config(pilot)
    need={
        "actual_effective_policy_id","selected_action","event_slot_sha256",
        "post_response_slot_sha256","rejected_sha256_absent",
        "temporary_recovery_state_absent","rollback_request_emitted",
        "rollback_request_validated","replacement_source_verified",
        "event_activation_ns","event_success_ns","policy_selection_ns",
        "policy_enforcement_ns","post_response_slot_observed_ns",
        "authorized_noop_probe_observed_ns","criteria_classification_ns",
        "run_end_ns","authorized_noop_attempt_count",
        "authorized_noop_marker_delta","recovery_criteria",
    }
    missing=sorted(need-set(observation))
    if missing: raise ValueError(f"recovery runtime fields missing: {missing}")

    effect=derive_observed_recovery_effect(
        pilot=pilot,cell_id=cell_id,observation=observation
    )
    require_recovery_effect_acceptance(effect)

    ea=int(observation["event_activation_ns"])
    es=int(observation["event_success_ns"])
    ps=int(observation["policy_selection_ns"])
    pe=int(observation["policy_enforcement_ns"])
    slot=int(observation["post_response_slot_observed_ns"])
    noop=int(observation["authorized_noop_probe_observed_ns"])
    cls=int(observation["criteria_classification_ns"])
    end=int(observation["run_end_ns"])
    if min(ea,es,ps,pe,slot,noop,cls,end)<0:
        raise ValueError("recovery timestamps must be non-negative")
    if not ea<=ps<=pe<=cls<=end:
        raise ValueError("recovery response timestamps are out of order")
    if not ea<=es<=pe:
        raise ValueError("R-019 event-success observer must complete by enforcement")
    if not (pe<=slot<=cls and pe<=noop<=cls):
        raise ValueError("post-response observations outside response boundary")

    family=effect["effect_family"]
    gateway_ns=None
    if family=="command_gateway":
        if "command_gateway_probe_observed_ns" not in observation:
            raise ValueError("R04 command-gateway timestamp required")
        gateway_ns=int(observation["command_gateway_probe_observed_ns"])
        if not pe<=gateway_ns<=cls:
            raise ValueError("R04 gateway timestamp outside response boundary")
        gw=observation.get("command_gateway_observation")
        if not isinstance(gw,dict):
            raise ValueError("R04 gateway observation required")
        if int(observation["authorized_noop_attempt_count"]) != int(
            gw["authorized_noop_attempt_count"]
        ) or int(observation["authorized_noop_marker_delta"]) != int(
            gw["authorized_noop_marker_delta"]
        ):
            raise ValueError("R04 authorized NOOP disagrees with gateway observation")

    attempted=int(observation["authorized_noop_attempt_count"])
    delta=int(observation["authorized_noop_marker_delta"])
    if attempted!=1:
        raise ValueError("R-036 requires one authorized NOOP attempt")
    if delta not in (0,1):
        raise ValueError("authorized NOOP marker delta must be zero or one")

    containment=bool(effect["containment_predicate_observed"])
    containment_ns=slot if containment else None
    criteria=_criteria(observation,cls,containment)

    mo4=all(
        criteria[c]["available_current"] and criteria[c]["criterion_satisfied"]
        for c in MO4_STATE_CRITERIA
    )
    manifest=criteria[MO5_EVIDENCE_CRITERION]
    mo5=manifest["available_current"] and manifest["criterion_satisfied"]
    all_current=all(r["available_current"] for r in criteria.values())
    all_satisfied=all(r["criterion_satisfied"] for r in criteria.values())
    trusted=containment and all_current and all_satisfied
    trusted_ns=(
        max(containment_ns,max(r["observed_ns"] for r in criteria.values()))
        if trusted else None
    )
    divergence_end=containment_ns if containment else end

    mitigation_applicable=family=="command_gateway"
    return {
        "schema":1,"decision_id":DECISION_ID,"cell_id":cell_id,
        "event_success":{"predicate":True,"observed_ns":es},
        "containment":{
            "predicate":containment,"observed_ns":containment_ns,
            "right_censored_at_run_end":not containment,
        },
        "trusted_recovery":{
            "predicate":trusted,"observed_ns":trusted_ns,
            "right_censored_at_run_end":not trusted,
        },
        "command_path_mitigation":{
            "applicable":mitigation_applicable,
            "predicate":effect["effect_semantics_met"] if mitigation_applicable else None,
            "observed_ns":gateway_ns if mitigation_applicable else None,
            "counts_as_e3_update_containment":False,
        },
        "objective_results":{
            "MO-4":{"completed":mo4,"source":
                "all_MO4_state_criteria_available_current_and_satisfied"},
            "MO-5":{"completed":mo5,"source":
                "recovery_manifest_complete_available_current_and_satisfied"},
        },
        "legitimate_commands":{"attempted":attempted,"rejected":attempted-delta},
        "ground_spacecraft_divergence_interval":{
            "state_key":"approved_version","start_ns":es,
            "end_ns":divergence_end,
            "right_censored_at_run_end":not containment,
        },
        "recovery_observations":criteria,
        "classification_time_ns":cls,
        "effect_acceptance":{
            "policy_semantics_met":effect["policy_semantics_met"],
            "effect_semantics_met":effect["effect_semantics_met"],
            "stage1_expected_effect_semantics_met":
                effect["stage1_expected_effect_semantics_met"],
        },
        "policy_time_visibility_used_as_classification_evidence":False,
        "expected_values_used_as_raw_metric_inputs":False,
        "primary_metrics_emitted":False,"terminal_state_emitted":False,
    }


def require_recovery_observation_acceptance(derived: dict[str, Any]) -> None:
    a=derived["effect_acceptance"]
    if not all(a.values()):
        raise ValueError("Stage-1 recovery effect acceptance failed")
    c=derived["containment"]; d=derived["ground_spacecraft_divergence_interval"]
    if c["predicate"]:
        if c["observed_ns"] is None or c["right_censored_at_run_end"]:
            raise ValueError("observed containment censoring invalid")
        if d["right_censored_at_run_end"] or d["end_ns"]!=c["observed_ns"]:
            raise ValueError("contained divergence endpoint invalid")
    else:
        if c["observed_ns"] is not None or not c["right_censored_at_run_end"]:
            raise ValueError("uncontained update censoring invalid")
        if not d["right_censored_at_run_end"]:
            raise ValueError("uncontained divergence must be right-censored")

    t=derived["trusted_recovery"]
    if t["predicate"]:
        if t["observed_ns"] is None or t["right_censored_at_run_end"]:
            raise ValueError("trusted recovery censoring invalid")
        if not c["predicate"]:
            raise ValueError("trusted recovery requires update containment")
    else:
        if t["observed_ns"] is not None or not t["right_censored_at_run_end"]:
            raise ValueError("unobserved trusted recovery must be right-censored")

    m=derived["command_path_mitigation"]
    if derived["cell_id"]=="R04":
        if not m["applicable"] or m["predicate"] is not True:
            raise ValueError("R04 command mitigation not observed")
        if m["counts_as_e3_update_containment"] is not False:
            raise ValueError("R04 mitigation cannot count as E3 containment")
        if c["predicate"] is not False:
            raise ValueError("R04 mitigation cannot replace update containment")
    elif m["applicable"]:
        raise ValueError("command-path mitigation is only applicable to R04")
