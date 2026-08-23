from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .events import materialize_event
from .primary_metrics import RECOVERY_CRITERIA, build_run_record
from .wp8_runtime_binding import environment_from_toolchain_lock
from .wp9_campaign_trial_controller import validate_static_controller
from .wp9_static_contracts import (
    evaluate_wp9_policy,
    load_campaign_design,
    runtime_route_for_cell,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-062"
SUPPORTED_CELLS = tuple(f"A{i:02d}" for i in range(10, 19))
TIMING_FREEZE = ROOT / "configs" / "wp9_precampaign_timing_freeze.json"
TOOLCHAIN = ROOT / "configs" / "toolchain-lock.json"
APPROVED_SHA256 = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
TAMPERED_SHA256 = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"

EXPECTED_BINDINGS = {
    "A10": ("P2", "P2", "e3_command_gateway"),
    "A11": ("P7", "P5", "e3_trusted_recovery"),
    "A12": ("P2", "P2", "e3_command_gateway"),
    "A13": ("P7", "P2", "e3_command_gateway"),
    "A14": ("P5", "P5", "e3_trusted_recovery"),
    "A15": ("P5", "P5", "e3_trusted_recovery_reduced_evidence"),
    "A16": ("P6", "P6", "e3_ground_authorized_recovery"),
    "A17": ("P6", "P6", "e3_ground_authorized_recovery"),
    "A18": ("P7", "P5", "e3_trusted_recovery_contact_delay"),
}

EXPECTED_ACTION_BY_EFFECTIVE = {
    "P2": "RESTRICT_HIGH_RISK_COMMANDS",
    "P5": "REQUEST_VERIFIED_ROLLBACK",
    "P6": "WAIT_FOR_GROUND_AUTHORIZATION",
}


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _as_int(measurement: dict[str, Any], key: str) -> int:
    value = measurement.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"E3 measurement field must be integer: {key}")
    return value


def _as_bool(measurement: dict[str, Any], key: str) -> bool:
    value = measurement.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"E3 measurement field must be boolean: {key}")
    return value


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("run_start_utc is required")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("run_start_utc must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _seconds(ns: int, origin_ns: int) -> float:
    return (int(ns) - int(origin_ns)) / 1_000_000_000.0


def validate_static_adapter() -> dict[str, Any]:
    controller = validate_static_controller()
    timing = _load(TIMING_FREEZE)
    cells = {row["cell_id"]: row for row in load_campaign_design()["cells"]}
    _require(controller["decision_id"] == "R-054", "R-062 requires R-054 controller")
    _require(controller["final_campaign_execution_authorized"] is False, "R-062 cannot follow campaign authorization")
    _require(timing["decision_id"] == "R-052", "R-062 requires R-052 timing freeze")
    frozen = timing["frozen_timing"]
    _require(frozen["e3_common_post_event_analysis_horizon_s"] == 30, "E3 horizon changed")
    _require(frozen["c1_semantics"]["modeled_contact_window_s"] == 10, "E3 C1 window changed")
    _require(frozen["early_absorbing_trusted_recovery_allowed"] is True, "early recovery rule changed")
    _require(frozen["unrecovered_e3_run_right_censored_at_horizon"] is True, "E3 censoring rule changed")
    for cell_id, (requested, effective, _) in EXPECTED_BINDINGS.items():
        cell = cells[cell_id]
        _require(cell["event_id"] == "E3", f"{cell_id}: event changed")
        _require(cell["mission_state_id"] == "M4", f"{cell_id}: mission state changed")
        _require(cell["policy_id"] == requested, f"{cell_id}: requested policy changed")
        _require(cell["expected_effective_policy_id"] == effective, f"{cell_id}: effective policy changed")
        route = runtime_route_for_cell(cell_id)
        _require(route["runtime_family"] == "recovery", f"{cell_id}: runtime family changed")
        _require(route["runtime_variant"] == EXPECTED_BINDINGS[cell_id][2], f"{cell_id}: runtime variant changed")
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R062_E3_CAMPAIGN_OBSERVATION_ADAPTER_STATIC_READY",
        "supported_cells": list(SUPPORTED_CELLS),
        "post_event_analysis_horizon_s": 30,
        "modeled_c1_contact_window_s": 10,
        "runtime_variants": sorted({row[2] for row in EXPECTED_BINDINGS.values()}),
        "expected_effects_used_as_metric_inputs": False,
        "unexpected_scientific_outcome_retained": True,
        "ground_truth_policy_oracle_allowed": False,
        "p2_command_mitigation_counts_as_update_containment": False,
        "t1_policy_omission_implies_recovery_failure": False,
        "real_ground_contact_required": False,
        "real_human_operator_required": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def _validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_adapter()
    _require(plan.get("decision_id") == "R-054", "E3 adapter requires R-054 trial plan")
    cell_id = plan.get("cell_id")
    _require(cell_id in SUPPORTED_CELLS, "E3 adapter supports A10-A18 only")
    _require(plan.get("runtime_family") == "recovery", "E3 runtime family changed")
    _, _, expected_variant = EXPECTED_BINDINGS[cell_id]
    _require(plan.get("runtime_variant") == expected_variant, f"{cell_id}: runtime variant changed")
    factor = plan.get("factor_context", {})
    _require(factor.get("event_id") == "E3", "E3 plan event changed")
    _require(int(factor.get("seed")) == int(plan.get("campaign_seed")), "seed binding changed")
    timing = plan.get("timing_contract", {})
    _require(timing.get("e3_post_event_analysis_horizon_s") == 30, "E3 plan horizon changed")
    if factor.get("contact_condition_id") == "C1":
        _require(timing.get("modeled_c1_contact_window_s") == 10, "C1 plan window changed")
    else:
        _require(timing.get("modeled_c1_contact_window_s") is None, "C0 unexpectedly has C1 window")
    if factor.get("policy_id") == "P6":
        expected_release = 10 if factor.get("contact_condition_id") == "C1" else 0
        _require(timing.get("p6_ground_authorization_release_after_event_s") == expected_release, "P6 release timing changed")
    else:
        _require(timing.get("p6_ground_authorization_release_after_event_s") is None, "non-P6 waits for P6 authorization")
    boundary = plan.get("execution_boundary", {})
    for key in (
        "automatic_retry_allowed",
        "automatic_next_case_allowed",
        "campaign_seed_consumed",
        "campaign_data_generated",
        "runtime_execution_performed",
        "final_campaign_execution_authorized",
    ):
        _require(boundary.get(key) is False, f"R-054 boundary changed: {key}")
    return factor


def _runtime_policy(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    factor = _validate_plan(plan)
    event = materialize_event(
        "E3",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(decision["oracle_ground_truth_read"] is False, "policy read immutable ground truth")
    _require(decision["delegated_policy_id"] == plan["expected_effective_policy_id_for_acceptance_only"], "actual policy differs from frozen design")
    _require(decision["selected_action"] == EXPECTED_ACTION_BY_EFFECTIVE[decision["delegated_policy_id"]], "actual action differs from frozen E3 treatment")
    return event, decision


def _validate_common(plan: dict[str, Any], measurement: dict[str, Any]) -> dict[str, int]:
    _require(measurement.get("schema") == 1, "E3 measurement schema changed")
    _require(measurement.get("run_id") == plan["run_id"], "measurement run_id mismatch")
    _require(_as_bool(measurement, "event_activation_observed") is True, "E3 event activation was not observed")
    _require(measurement.get("event_slot_sha256") == TAMPERED_SHA256, "E3 activation slot identity changed")
    _require(_as_bool(measurement, "runtime_health_passed") is True, "runtime health failure invalidates attempt")
    _require(_as_bool(measurement, "policy_selection_not_gated_on_event_success") is True, "E3 policy selection became ground-truth gated")
    run_start_ns = _as_int(measurement, "run_start_ns")
    activation_ns = _as_int(measurement, "event_activation_ns")
    success_ns = _as_int(measurement, "event_success_observed_ns")
    selection_ns = _as_int(measurement, "policy_selection_ns")
    enforcement_ns = _as_int(measurement, "policy_enforcement_ns")
    response_boundary_ns = _as_int(measurement, "response_boundary_ns")
    complete_ns = _as_int(measurement, "observation_complete_ns")
    _require(run_start_ns >= 0, "run_start_ns must be non-negative")
    _require(run_start_ns <= activation_ns <= selection_ns <= enforcement_ns <= response_boundary_ns, "E3 response timestamps out of order")
    _require(activation_ns <= success_ns <= enforcement_ns, "E3 event success must be observed by policy-enforcement boundary")
    analysis_end_ns = activation_ns + 30_000_000_000
    _require(success_ns <= analysis_end_ns, "E3 event success after analysis horizon")
    return {
        "run_start_ns": run_start_ns,
        "activation_ns": activation_ns,
        "success_ns": success_ns,
        "selection_ns": selection_ns,
        "enforcement_ns": enforcement_ns,
        "response_boundary_ns": response_boundary_ns,
        "complete_ns": complete_ns,
        "analysis_end_ns": analysis_end_ns,
    }


def _p2_observation(decision: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    _require(decision["selected_action"] == "RESTRICT_HIGH_RISK_COMMANDS", "P2 E3 action changed")
    _require(measurement.get("post_response_slot_sha256") == TAMPERED_SHA256, "P2 replaced tampered update slot")
    _require(_as_bool(measurement, "update_containment_observed") is False, "P2 mitigation cannot count as update containment")
    _require(_as_int(measurement, "matched_attacker_probe_count") == 2, "P2 requires two matched attacker probes")
    _require(_as_int(measurement, "gateway_decision_count") == 3, "P2 requires three gateway decisions")
    _require(_as_int(measurement, "attacker_gateway_forwarded_count") == 0, "P2 attacker treatment fidelity failed")
    _require(_as_bool(measurement, "authorized_noop_gateway_forwarded") is True, "P2 authorized NOOP treatment fidelity failed")
    _require(measurement.get("gateway_action") == "RESTRICT_HIGH_RISK_COMMANDS", "P2 gateway action changed")
    attacker_delta = _as_int(measurement, "observed_post_enforcement_attacker_reset_marker_delta")
    noop_attempted = _as_int(measurement, "authorized_noop_attempted")
    noop_delta = _as_int(measurement, "authorized_noop_marker_delta")
    _require(0 <= attacker_delta <= 2, "P2 attacker effect delta outside bounds")
    _require(noop_attempted == 1, "E3 requires one authorized NOOP")
    _require(0 <= noop_delta <= 1, "authorized NOOP delta outside bounds")
    _require(_as_bool(measurement, "ground_authorization_waited") is False, "P2 unexpectedly waited for ground authorization")
    return {
        "containment": False,
        "containment_ns": None,
        "attacker_delta": attacker_delta,
        "noop_attempted": noop_attempted,
        "noop_delta": noop_delta,
        "trusted": False,
        "trusted_ns": None,
        "ground_waited": False,
    }


def _criteria(measurement: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, bool | None]]:
    source = measurement.get("recovery_criteria")
    _require(isinstance(source, dict), "E3 recovery criteria required")
    _require(set(source) == set(RECOVERY_CRITERIA), "E3 recovery criteria must contain exactly ten criteria")
    checklist = []
    evidence: dict[str, bool | None] = {criterion: None for criterion in RECOVERY_CRITERIA}
    for criterion in RECOVERY_CRITERIA:
        row = source[criterion]
        _require(isinstance(row, dict), f"invalid criterion: {criterion}")
        available = row.get("available_current")
        satisfied = row.get("criterion_satisfied")
        ref = row.get("evidence_ref")
        _require(isinstance(available, bool), f"criterion availability invalid: {criterion}")
        _require(isinstance(satisfied, bool), f"criterion result invalid: {criterion}")
        _require(bool(ref), f"criterion evidence ref missing: {criterion}")
        if satisfied:
            _require(available, f"satisfied criterion not current: {criterion}")
        checklist.append({"criterion_id": criterion, "available_current": available, "criterion_satisfied": satisfied, "evidence_ref": ref})
        evidence[criterion] = satisfied
    return checklist, evidence


def _recovery_observation(
    plan: dict[str, Any],
    event: dict[str, Any],
    decision: dict[str, Any],
    common: dict[str, int],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    effective = decision["delegated_policy_id"]
    _require(effective in {"P5", "P6"}, "recovery observation requires P5/P6")
    _require(_as_bool(measurement, "rollback_request_validated") is True, "rollback request validation failed")
    _require(_as_bool(measurement, "approved_replacement_source_verified") is True, "replacement verification failed")
    _require(measurement.get("post_response_slot_sha256") == APPROVED_SHA256, "approved replacement not in activation slot")
    _require(_as_bool(measurement, "temporary_recovery_state_absent") is True, "temporary recovery residue remains")
    rollback_ns = _as_int(measurement, "rollback_complete_ns")
    _require(common["enforcement_ns"] <= rollback_ns <= common["analysis_end_ns"], "rollback timestamp outside horizon")
    noop_attempted = _as_int(measurement, "authorized_noop_attempted")
    noop_delta = _as_int(measurement, "authorized_noop_marker_delta")
    _require(noop_attempted == 1, "E3 requires one authorized NOOP")
    _require(0 <= noop_delta <= 1, "authorized NOOP delta outside bounds")

    if effective == "P6":
        _require(_as_bool(measurement, "ground_authorization_waited") is True, "P6 must wait for modeled authorization")
        _require(measurement.get("ground_authorization_source") == "synthetic_ground_authorization_schedule", "P6 authorization source changed")
        _require(_as_bool(measurement, "ground_authorization_current") is True, "P6 authorization not current")
        auth_ns = _as_int(measurement, "authorization_observed_ns")
        handoff_ns = _as_int(measurement, "handoff_ns")
        _require(common["response_boundary_ns"] <= auth_ns <= handoff_ns <= rollback_ns, "P6 authorization/handoff ordering invalid")
        contact = plan["factor_context"]["contact_condition_id"]
        if contact == "C0":
            _require(_as_bool(measurement, "authorization_available_at_response_boundary") is True, "P6/C0 authorization not available at boundary")
            _require(_as_int(measurement, "missed_contact_windows_observed") == 0, "P6/C0 missed-window count changed")
        else:
            _require(_as_bool(measurement, "authorization_available_at_response_boundary") is False, "P6/C1 authorization available too early")
            _require(_as_int(measurement, "missed_contact_windows_observed") == 1, "P6/C1 requires one missed window")
            _require(auth_ns - common["response_boundary_ns"] >= 10_000_000_000, "P6/C1 authorization released before frozen 10-second window")
        _require(measurement.get("post_authorization_delegate") == "P5", "P6 handoff delegate changed")
        _require(measurement.get("post_authorization_action") == "REQUEST_VERIFIED_ROLLBACK", "P6 handoff action changed")
        ground_waited = True
    else:
        _require(_as_bool(measurement, "ground_authorization_waited") is False, "autonomous P5 unexpectedly waited for ground authorization")
        ground_waited = False

    if plan["cell_id"] == "A18":
        _require(ground_waited is False, "A18 autonomous P7-to-P5 cannot wait for ground authorization")
        _require(common["selection_ns"] - common["activation_ns"] < 10_000_000_000, "A18 policy selection incorrectly delayed by C1")

    checklist, evidence = _criteria(measurement)
    trusted = _as_bool(measurement, "trusted_recovery_confirmed")
    trusted_ns = None
    all_current = all(row["available_current"] for row in checklist)
    all_satisfied = all(row["criterion_satisfied"] for row in checklist)
    if trusted:
        _require(all_current and all_satisfied, "trusted recovery requires all ten current satisfied criteria")
        trusted_ns = _as_int(measurement, "trusted_recovery_observed_ns")
        _require(rollback_ns <= trusted_ns <= common["analysis_end_ns"], "trusted recovery timestamp outside horizon")
        _require(common["complete_ns"] >= trusted_ns, "trusted terminal classification not fully observed")
    else:
        _require(not (all_current and all_satisfied), "complete satisfied recovery evidence requires trusted recovery")
        _require(common["complete_ns"] >= common["analysis_end_ns"], "unrecovered E3 run did not cover 30-second horizon")

    if plan["cell_id"] == "A15":
        _require(event["evidence_condition"] == "T1", "A15 evidence condition changed")
        _require("approved_version" in event["policy_evidence_omitted"], "A15 must omit approved_version at policy time")

    return {
        "containment": True,
        "containment_ns": rollback_ns,
        "attacker_delta": None,
        "noop_attempted": noop_attempted,
        "noop_delta": noop_delta,
        "trusted": trusted,
        "trusted_ns": trusted_ns,
        "ground_waited": ground_waited,
        "checklist": checklist,
        "recovery_evidence": evidence,
    }


def _p2_criteria(noop_delta: int, evidence_prefix: str) -> tuple[list[dict[str, Any]], dict[str, bool | None]]:
    satisfied = {
        "authorization_valid": True,
        "authorized_command_path_restored": noop_delta == 1,
        "health_checks_passed": True,
    }
    checklist = []
    evidence: dict[str, bool | None] = {}
    for criterion in RECOVERY_CRITERIA:
        value = bool(satisfied.get(criterion, False))
        checklist.append({
            "criterion_id": criterion,
            "available_current": True,
            "criterion_satisfied": value,
            "evidence_ref": f"{evidence_prefix}/classification/{criterion}.json",
        })
        evidence[criterion] = value
    return checklist, evidence


def build_static_fixture_bundle(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
    host_architecture: str,
    evidence_prefix: str = "static-fixture/wp9/e3",
) -> dict[str, Any]:
    factor = _validate_plan(plan)
    event, decision = _runtime_policy(plan)
    common = _validate_common(plan, measurement)
    effective = decision["delegated_policy_id"]

    if effective == "P2":
        observed = _p2_observation(decision, measurement)
        checklist, recovery_evidence = _p2_criteria(int(observed["noop_delta"]), evidence_prefix)
        _require(common["complete_ns"] >= common["analysis_end_ns"], "unrecovered P2 E3 run did not cover 30-second horizon")
    else:
        observed = _recovery_observation(plan, event, decision, common, measurement)
        checklist = observed["checklist"]
        recovery_evidence = observed["recovery_evidence"]

    run_start_ns = common["run_start_ns"]
    activation_s = _seconds(common["activation_ns"], run_start_ns)
    success_s = _seconds(common["success_ns"], run_start_ns)
    analysis_end_s = _seconds(common["analysis_end_ns"], run_start_ns)
    containment = bool(observed["containment"])
    containment_s = _seconds(int(observed["containment_ns"]), run_start_ns) if observed["containment_ns"] is not None else None
    trusted = bool(observed["trusted"])
    trusted_s = _seconds(int(observed["trusted_ns"]), run_start_ns) if observed["trusted_ns"] is not None else None
    run_end_s = trusted_s if trusted else analysis_end_s
    _require(run_end_s is not None, "E3 run end unresolved")
    noop_delta = int(observed["noop_delta"])
    authorized_path = noop_delta == 1

    raw = {
        "event_success": {"predicate": True, "timestamp_s": success_s},
        "containment": {"predicate": containment, "timestamp_s": containment_s},
        "trusted_recovery": {"predicate": trusted, "timestamp_s": trusted_s},
        "objective_instances": [
            {
                "objective_instance_id": "recovery-MO-4-update-state",
                "weight": 1.0,
                "scheduled_start_s": activation_s,
                "scheduled_end_s": run_end_s,
                "completion_predicate": "approved_replacement_occupies_activation_slot",
                "completion_evidence_ref": f"{evidence_prefix}/runtime-observation/e3-recovery-measurement.json",
                "completed": containment,
            },
            {
                "objective_instance_id": "recovery-MO-3-authorized-command-path",
                "weight": 1.0,
                "scheduled_start_s": activation_s,
                "scheduled_end_s": run_end_s,
                "completion_predicate": "authorized_ground_noop_observed",
                "completion_evidence_ref": f"{evidence_prefix}/runtime-observation/authorized-noop.json",
                "completed": authorized_path,
            },
        ],
        "invariant_violation_intervals": [],
        "legitimate_commands": {"attempted": int(observed["noop_attempted"]), "rejected": int(observed["noop_attempted"]) - noop_delta},
        "ground_spacecraft_divergence_intervals": [{
            "state_key": "approved_version",
            "start_s": success_s,
            "end_s": containment_s if containment_s is not None else analysis_end_s,
        }],
        "recovery_checklist": checklist,
        "recovery_checklist_excluded": [],
        "run_end_s": run_end_s,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": trusted,
            "operational_restored": containment and authorized_path and not trusted,
            "recovery_failed": not containment,
            "contained": containment,
        },
    }

    if effective == "P6":
        raw["ground_authorization"] = {
            "required": True,
            "source": measurement["ground_authorization_source"],
            "available_at_response_boundary": measurement[
                "authorization_available_at_response_boundary"
            ],
            "available_timestamp_s": _seconds(
                _as_int(measurement, "authorization_observed_ns"),
                run_start_ns,
            ),
            "missed_contact_windows": _as_int(
                measurement, "missed_contact_windows_observed"
            ),
            "authorization_current": measurement["ground_authorization_current"],
            "evidence_ref": (
                f"{evidence_prefix}/runtime-observation/"
                "synthetic-ground-authorization.json"
            ),
        }

    start_utc = _parse_utc(measurement["run_start_utc"])
    run_end_utc = start_utc + timedelta(seconds=run_end_s)
    environment = environment_from_toolchain_lock(
        _load(TOOLCHAIN),
        snapshot_id=f"repo-{plan['repo_commit']}",
        host_architecture=host_architecture,
    )
    run_record = build_run_record(
        run_id=plan["run_id"],
        model_version=factor["model_version"],
        seed=int(factor["seed"]),
        mission_state_id=factor["mission_state_id"],
        event_id="E3",
        policy_id=factor["policy_id"],
        contact_condition_id=factor["contact_condition_id"],
        evidence_condition_id=factor["evidence_condition_id"],
        environment=environment,
        run_start_utc=_format_utc(start_utc),
        event_activation_s=activation_s,
        run_end_utc=_format_utc(run_end_utc),
        raw_metric_evidence=raw,
        recovery_evidence=recovery_evidence,
        notes="R-062 static E3 campaign-binding fixture; controlled NOS3 staged-update surrogate only; no campaign runtime or data.",
    )

    expected_containment = effective in {"P5", "P6"}
    expected_noop_delta = 1
    expected_trusted = None
    outcome_matches = containment == expected_containment and noop_delta == expected_noop_delta
    p2_attacker_delta = observed.get("attacker_delta")

    provenance = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R062_E3_STATIC_BINDING_FIXTURE",
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "runtime_family": "recovery",
        "runtime_variant": plan["runtime_variant"],
        "factor_context": deepcopy(factor),
        "event_instance": event,
        "execution_metadata": {
            "requested_policy_id": factor["policy_id"],
            "effective_policy_id": effective,
            "selected_action": decision["selected_action"],
            "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        },
        "timing_binding": {
            "post_event_analysis_horizon_s": 30,
            "modeled_c1_contact_window_s": 10 if factor["contact_condition_id"] == "C1" else None,
            "early_absorbing_trusted_recovery": trusted,
            "right_censored_at_30s": not trusted,
            "runner_duration_used_as_metric_input": False,
        },
        "observed_discriminators": {
            "event_activation_observed": True,
            "update_containment_observed": containment,
            "command_path_mitigation_observed": effective == "P2" and p2_attacker_delta == 0,
            "p2_command_mitigation_counts_as_update_containment": False,
            "authorized_noop_marker_delta": noop_delta,
            "trusted_recovery_observed": trusted,
            "ground_authorization_waited": bool(observed["ground_waited"]),
        },
        "predeclared_expectation": {
            "expected_update_containment_for_acceptance_only": expected_containment,
            "expected_authorized_noop_marker_delta_for_acceptance_only": expected_noop_delta,
            "expected_trusted_recovery_for_acceptance_only": expected_trusted,
            "outcome_matches_predeclared_expectation": outcome_matches,
            "expectation_used_as_metric_input": False,
            "expectation_used_to_reject_scientific_outcome": False,
        },
        "evidence_semantics": {
            "policy_time_approved_version_omitted": "approved_version" in event.get("policy_evidence_omitted", []),
            "policy_time_omission_implies_classification_time_loss": False,
            "classification_time_recovery_evidence_source": "retained_runtime_observation",
            "trusted_recovery_requires_all_ten_current_satisfied_criteria": True,
        },
        "scientific_validity": {
            "event_treatment_fidelity_valid": True,
            "response_treatment_fidelity_valid": True,
            "raw_metric_inputs_complete": True,
            "policy_selection_not_gated_on_event_success": True,
            "unexpected_scientific_outcome_retained": not outcome_matches,
            "scientific_observation_retained": True,
        },
        "claim_boundaries": {
            "ground_truth_used_as_policy_oracle": False,
            "trusted_recovery_scope": "controlled_staged_synthetic_update_state_only",
            "operational_firmware_activation_claim": False,
            "native_spacecraft_safe_mode_claim": False,
            "real_spacecraft_claim": False,
            "real_ground_contact_claim": False,
            "real_human_operator_claim": False,
            "rf_interference_claim": False,
        },
        "static_fixture_only": True,
        "runtime_execution_performed": False,
        "campaign_runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
    }
    return {"schema": 1, "decision_id": DECISION_ID, "run_record": run_record, "binding_provenance": provenance}


def execution_preflight() -> None:
    raise PermissionError(
        "R-062 is static observation-binding only; E3 campaign runtime remains blocked until a campaign-safe runtime adapter and separate explicit authorization exist"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")
    fixture = sub.add_parser("bind-static-fixture")
    fixture.add_argument("--plan-json", type=Path, required=True)
    fixture.add_argument("--measurement-json", type=Path, required=True)
    fixture.add_argument("--host-architecture", required=True)
    fixture.add_argument("--evidence-prefix", default="static-fixture/wp9/e3")
    fixture.add_argument("--output-json", type=Path, required=True)
    sub.add_parser("execute-trial")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_adapter()
        print("WP9_R062_E3_CAMPAIGN_OBSERVATION_ADAPTER_STATIC=PASS")
        for key in (
            "supported_cells", "post_event_analysis_horizon_s", "modeled_c1_contact_window_s",
            "runtime_variants", "expected_effects_used_as_metric_inputs",
            "unexpected_scientific_outcome_retained", "ground_truth_policy_oracle_allowed",
            "p2_command_mitigation_counts_as_update_containment", "t1_policy_omission_implies_recovery_failure",
            "real_ground_contact_required", "real_human_operator_required", "runtime_execution_performed",
            "campaign_seed_consumed", "campaign_data_generated", "final_campaign_execution_authorized",
        ):
            value = result[key]
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, list):
                value = ",".join(value)
            print(f"{key}={value}")
        return 0

    if args.command == "bind-static-fixture":
        bundle = build_static_fixture_bundle(
            plan=_load(args.plan_json), measurement=_load(args.measurement_json),
            host_architecture=args.host_architecture, evidence_prefix=args.evidence_prefix,
        )
        _write(args.output_json, bundle)
        provenance = bundle["binding_provenance"]
        print("WP9_R062_E3_STATIC_FIXTURE_BINDING=PASS")
        print("cell_id=" + provenance["cell_id"])
        print("campaign_seed=" + str(provenance["campaign_seed"]))
        print("outcome_matches_predeclared_expectation=" + str(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"]).lower())
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
