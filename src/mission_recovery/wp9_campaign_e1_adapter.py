from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policy_gateway import build_command_envelope, decide_forward
from .primary_metrics import RECOVERY_CRITERIA, build_run_record
from .wp8_runtime_binding import environment_from_toolchain_lock
from .wp9_campaign_trial_controller import validate_static_controller
from .wp9_static_contracts import evaluate_wp9_policy, load_campaign_design

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-060"
SUPPORTED_CELLS = tuple(f"A{i:02d}" for i in range(1, 10))
COMMON_HORIZON = ROOT / "configs" / "wp9_precampaign_non_e3_horizon_freeze.json"
TOOLCHAIN = ROOT / "configs" / "toolchain-lock.json"

MODELED_ATTACKER_SOURCE = "modeled_attacker"
AUTHORIZED_GROUND_SOURCE = "authorized_ground"
ATTACKER_COMMAND_CLASS = "sample_reset_counters"
AUTHORIZED_COMMAND_CLASS = "sample_noop"
MATCHED_ATTACKER_PROBE_COUNT = 2
AUTHORIZED_NOOP_ATTEMPT_COUNT = 1

EXPECTED_POLICY_BINDINGS = {
    "A01": ("P1", "P1"),
    "A02": ("P7", "P1"),
    "A03": ("P1", "P1"),
    "A04": ("P7", "P2"),
    "A05": ("P1", "P1"),
    "A06": ("P7", "P2"),
    "A07": ("P2", "P2"),
    "A08": ("P2", "P2"),
    "A09": ("P7", "P4"),
}


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _as_int(measurement: dict[str, Any], key: str) -> int:
    value = measurement.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"E1 measurement field must be integer: {key}")
    return value


def _as_bool(measurement: dict[str, Any], key: str) -> bool:
    value = measurement.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"E1 measurement field must be boolean: {key}")
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
    horizon = _load(COMMON_HORIZON)
    cells = {row["cell_id"]: row for row in load_campaign_design()["cells"]}

    _require(controller["decision_id"] == "R-054", "R-060 requires R-054 controller")
    _require(
        controller["final_campaign_execution_authorized"] is False,
        "R-060 static adapter cannot begin after campaign authorization",
    )
    _require(horizon["decision_id"] == "R-055", "R-060 requires R-055 horizon freeze")
    frozen = horizon["frozen_horizons"]
    _require(frozen["common_post_event_analysis_horizon_s"] == 30, "common horizon changed")
    _require(frozen["E1_post_event_analysis_horizon_s"] == 30, "E1 horizon changed")
    _require(
        frozen["runner_wall_clock_or_nominal_duration_used_as_metric_input"] is False,
        "runner duration cannot become an E1 metric input",
    )

    for cell_id, (requested, effective) in EXPECTED_POLICY_BINDINGS.items():
        cell = cells[cell_id]
        _require(cell["event_id"] == "E1", f"{cell_id}: event is not E1")
        _require(cell["policy_id"] == requested, f"{cell_id}: requested policy changed")
        _require(
            cell["expected_effective_policy_id"] == effective,
            f"{cell_id}: effective policy contract changed",
        )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R060_E1_CAMPAIGN_OBSERVATION_ADAPTER_STATIC_READY",
        "supported_cells": list(SUPPORTED_CELLS),
        "post_event_analysis_horizon_s": 30,
        "matched_attacker_probe_count": MATCHED_ATTACKER_PROBE_COUNT,
        "post_response_authorized_noop_required": True,
        "expected_effects_used_as_metric_inputs": False,
        "unexpected_scientific_outcome_retained": True,
        "ground_truth_policy_oracle_allowed": False,
        "native_spacecraft_safe_mode_claim": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def _validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_adapter()
    _require(plan.get("decision_id") == "R-054", "E1 adapter requires R-054 trial plan")
    cell_id = plan.get("cell_id")
    _require(cell_id in SUPPORTED_CELLS, "E1 adapter supports A01-A09 only")
    _require(plan.get("runtime_family") == "command", "E1 runtime family changed")
    _require(plan.get("runtime_variant") == "e1_command_gateway", "E1 runtime variant changed")
    factor = plan.get("factor_context", {})
    _require(factor.get("event_id") == "E1", "E1 plan event changed")
    _require(int(factor.get("seed")) == int(plan.get("campaign_seed")), "seed binding changed")
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
        "E1",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(decision["oracle_ground_truth_read"] is False, "policy read immutable ground truth")
    _require(
        decision["delegated_policy_id"]
        == plan["expected_effective_policy_id_for_acceptance_only"],
        "actual policy treatment differs from frozen campaign design",
    )
    return event, decision


def _expected_gateway_treatment(action: str) -> tuple[int, bool]:
    attacker = build_command_envelope(MODELED_ATTACKER_SOURCE, ATTACKER_COMMAND_CLASS)
    authorized = build_command_envelope(AUTHORIZED_GROUND_SOURCE, AUTHORIZED_COMMAND_CLASS)
    attacker_forwarded = decide_forward(action, attacker)
    authorized_forwarded = decide_forward(action, authorized)
    return (
        MATCHED_ATTACKER_PROBE_COUNT if attacker_forwarded else 0,
        bool(authorized_forwarded),
    )


def _validate_measurement(
    *,
    plan: dict[str, Any],
    decision: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, int | bool]:
    _require(measurement.get("schema") == 1, "E1 measurement schema changed")
    _require(measurement.get("run_id") == plan["run_id"], "measurement run_id mismatch")

    event_delta = _as_int(measurement, "event_activation_reset_marker_delta")
    attacker_count = _as_int(measurement, "post_enforcement_attacker_probe_count")
    attacker_delta = _as_int(measurement, "post_enforcement_attacker_reset_marker_delta")
    legitimate_attempted = _as_int(measurement, "legitimate_commands_attempted")
    legitimate_delta = _as_int(measurement, "authorized_noop_marker_delta")
    gateway_count = _as_int(measurement, "gateway_decision_count")
    attacker_forwarded_count = _as_int(measurement, "attacker_gateway_forwarded_count")
    authorized_forwarded = _as_bool(measurement, "authorized_noop_gateway_forwarded")

    _require(event_delta == 1, "E1 event activation effect not observed exactly once")
    _require(
        attacker_count == MATCHED_ATTACKER_PROBE_COUNT,
        "E1 containment requires exactly two matched attacker probes",
    )
    _require(0 <= attacker_delta <= attacker_count, "attacker reset marker delta outside probe bounds")
    _require(
        legitimate_attempted == AUTHORIZED_NOOP_ATTEMPT_COUNT,
        "E1 requires one post-response authorized NOOP",
    )
    _require(0 <= legitimate_delta <= legitimate_attempted, "authorized NOOP marker delta outside attempt bounds")
    _require(gateway_count == 3, "E1 requires exactly three post-enforcement gateway decisions")
    _require(
        _as_bool(measurement, "runtime_health_passed") is True,
        "runtime health failure invalidates attempt",
    )
    _require(
        _as_bool(measurement, "policy_selection_not_gated_on_event_success") is True,
        "E1 policy selection became gated on ground-truth event success",
    )

    selected_action = decision["selected_action"]
    _require(
        measurement.get("attacker_gateway_action") == selected_action,
        "attacker gateway action differs from runtime policy",
    )
    _require(
        measurement.get("authorized_noop_gateway_action") == selected_action,
        "authorized-NOOP gateway action differs from runtime policy",
    )
    expected_attacker_forwarded_count, expected_authorized_forwarded = _expected_gateway_treatment(
        selected_action
    )
    _require(
        attacker_forwarded_count == expected_attacker_forwarded_count,
        "gateway attacker forwarding differs from frozen treatment semantics",
    )
    _require(
        authorized_forwarded == expected_authorized_forwarded,
        "gateway authorized-NOOP forwarding differs from frozen treatment semantics",
    )

    run_start_ns = _as_int(measurement, "run_start_ns")
    event_activation_ns = _as_int(measurement, "event_activation_ns")
    event_success_ns = _as_int(measurement, "event_success_observed_ns")
    policy_selection_ns = _as_int(measurement, "policy_selection_ns")
    enforcement_ns = _as_int(measurement, "policy_enforcement_ns")
    second_attacker_ns = _as_int(measurement, "second_attacker_probe_observed_ns")
    authorized_noop_ns = _as_int(measurement, "authorized_noop_probe_observed_ns")
    observation_complete_ns = _as_int(measurement, "observation_complete_ns")

    _require(run_start_ns >= 0, "run_start_ns must be non-negative")
    _require(
        run_start_ns <= event_activation_ns <= policy_selection_ns <= enforcement_ns,
        "E1 response timestamps are out of order",
    )
    _require(
        event_activation_ns <= event_success_ns <= second_attacker_ns,
        "E1 event-success timestamp is out of bounds",
    )
    _require(
        enforcement_ns <= second_attacker_ns <= authorized_noop_ns,
        "E1 post-enforcement probe timestamps are out of order",
    )

    analysis_end_ns = event_activation_ns + 30_000_000_000
    _require(
        observation_complete_ns >= analysis_end_ns,
        "E1 observation did not cover frozen 30-second analysis horizon",
    )
    _require(second_attacker_ns <= analysis_end_ns, "attacker probes occurred after analysis horizon")
    _require(authorized_noop_ns <= analysis_end_ns, "authorized NOOP occurred after analysis horizon")
    _require(event_success_ns <= analysis_end_ns, "E1 event success occurred after analysis horizon")

    return {
        "event_delta": event_delta,
        "attacker_count": attacker_count,
        "attacker_delta": attacker_delta,
        "legitimate_attempted": legitimate_attempted,
        "legitimate_delta": legitimate_delta,
        "attacker_forwarded_count": attacker_forwarded_count,
        "authorized_forwarded": authorized_forwarded,
        "run_start_ns": run_start_ns,
        "event_activation_ns": event_activation_ns,
        "event_success_ns": event_success_ns,
        "policy_selection_ns": policy_selection_ns,
        "enforcement_ns": enforcement_ns,
        "second_attacker_ns": second_attacker_ns,
        "authorized_noop_ns": authorized_noop_ns,
        "analysis_end_ns": analysis_end_ns,
    }


def build_static_fixture_bundle(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
    host_architecture: str,
    evidence_prefix: str = "static-fixture/wp9/e1",
) -> dict[str, Any]:
    factor = _validate_plan(plan)
    event, decision = _runtime_policy(plan)
    observed = _validate_measurement(plan=plan, decision=decision, measurement=measurement)

    run_start_ns = int(observed["run_start_ns"])
    event_activation_ns = int(observed["event_activation_ns"])
    event_success_ns = int(observed["event_success_ns"])
    second_attacker_ns = int(observed["second_attacker_ns"])
    authorized_noop_ns = int(observed["authorized_noop_ns"])
    analysis_end_ns = int(observed["analysis_end_ns"])

    event_activation_s = _seconds(event_activation_ns, run_start_ns)
    event_success_s = _seconds(event_success_ns, run_start_ns)
    second_attacker_s = _seconds(second_attacker_ns, run_start_ns)
    authorized_noop_s = _seconds(authorized_noop_ns, run_start_ns)
    analysis_end_s = _seconds(analysis_end_ns, run_start_ns)

    event_success = int(observed["event_delta"]) == 1
    containment = int(observed["attacker_delta"]) == 0
    containment_s = second_attacker_s if containment else None
    authorized_observed = int(observed["legitimate_delta"]) == 1
    authority_convergence = containment and authorized_observed
    divergence_end_s = authorized_noop_s if authority_convergence else analysis_end_s

    event_ref = f"{evidence_prefix}/immutable-ground/event-instance.json"
    gateway_ref = f"{evidence_prefix}/immutable-ground/gateway-decisions.jsonl"
    noop_ref = f"{evidence_prefix}/immutable-ground/authorized-noop-probe.json"
    derived_ref = f"{evidence_prefix}/immutable-ground/e1-campaign-derived.json"
    runtime_ref = f"artifacts/runtime/{plan['run_id']}/runtime-manifest.txt"
    class_ref = f"{evidence_prefix}/immutable-ground/e1-classification-evidence.json"

    authorization_ok = decision["oracle_ground_truth_read"] is False
    operational = containment and authority_convergence and authorization_ok

    checklist = [
        {
            "criterion_id": "authorization_valid",
            "available_current": True,
            "criterion_satisfied": authorization_ok,
            "evidence_ref": gateway_ref,
        },
        {
            "criterion_id": "authorized_command_path_restored",
            "available_current": True,
            "criterion_satisfied": authorized_observed,
            "evidence_ref": noop_ref,
        },
        {
            "criterion_id": "ground_spacecraft_state_agreed",
            "available_current": True,
            "criterion_satisfied": authority_convergence,
            "evidence_ref": derived_ref,
        },
        {
            "criterion_id": "health_checks_passed",
            "available_current": True,
            "criterion_satisfied": True,
            "evidence_ref": runtime_ref,
        },
        {
            "criterion_id": "recovery_manifest_complete",
            "available_current": True,
            "criterion_satisfied": False,
            "evidence_ref": class_ref,
        },
    ]
    excluded = [
        "approved_version",
        "integrity_measurement_valid",
        "measured_state_current",
        "required_telemetry_restored",
        "no_residual_unauthorized_state",
    ]
    _require(
        {row["criterion_id"] for row in checklist} | set(excluded) == set(RECOVERY_CRITERIA),
        "E1 command-family recovery partition changed",
    )

    divergence = []
    if event_success:
        divergence.append(
            {
                "state_key": "command_authority",
                "start_s": event_success_s,
                "end_s": divergence_end_s,
            }
        )

    raw = {
        "event_success": {"predicate": event_success, "timestamp_s": event_success_s},
        "containment": {"predicate": containment, "timestamp_s": containment_s},
        "trusted_recovery": {"predicate": False, "timestamp_s": None},
        "objective_instances": [
            {
                "objective_instance_id": "command-MO-1-response-interval",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": "no_observed_unauthorized_e1_effect",
                "completion_evidence_ref": event_ref,
                "completed": not event_success,
            },
            {
                "objective_instance_id": "command-MO-3-response-interval",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": "observed_authorized_ground_noop_cfs_marker_delta",
                "completion_evidence_ref": noop_ref,
                "completed": authorized_observed,
            },
        ],
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": int(observed["legitimate_attempted"]),
            "rejected": int(observed["legitimate_attempted"]) - int(observed["legitimate_delta"]),
        },
        "ground_spacecraft_divergence_intervals": divergence,
        "recovery_checklist": checklist,
        "recovery_checklist_excluded": excluded,
        "run_end_s": analysis_end_s,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": False,
            "operational_restored": operational,
            "recovery_failed": not containment,
            "contained": containment,
        },
    }

    recovery_evidence = {criterion: None for criterion in RECOVERY_CRITERIA}
    for row in checklist:
        recovery_evidence[row["criterion_id"]] = bool(row["criterion_satisfied"])

    start_utc = _parse_utc(measurement["run_start_utc"])
    analysis_end_utc = start_utc + timedelta(seconds=analysis_end_s)
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
        event_id="E1",
        policy_id=factor["policy_id"],
        contact_condition_id=factor["contact_condition_id"],
        evidence_condition_id=factor["evidence_condition_id"],
        environment=environment,
        run_start_utc=_format_utc(start_utc),
        event_activation_s=event_activation_s,
        run_end_utc=_format_utc(analysis_end_utc),
        raw_metric_evidence=raw,
        recovery_evidence=recovery_evidence,
        notes=(
            "R-060 static E1 campaign-binding fixture; controlled NOS3 SAMPLE-command "
            "surrogate semantics only; no campaign runtime or campaign data."
        ),
    )

    expected_attacker_delta, expected_authorized_forwarded = _expected_gateway_treatment(
        decision["selected_action"]
    )
    expected_authorized_delta = 1 if expected_authorized_forwarded else 0
    outcome_matches = (
        int(observed["attacker_delta"]) == expected_attacker_delta
        and int(observed["legitimate_delta"]) == expected_authorized_delta
    )

    provenance = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R060_E1_STATIC_BINDING_FIXTURE",
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "runtime_family": "command",
        "runtime_variant": "e1_command_gateway",
        "factor_context": deepcopy(factor),
        "event_instance": event,
        "execution_metadata": {
            "requested_policy_id": factor["policy_id"],
            "effective_policy_id": decision["delegated_policy_id"],
            "selected_action": decision["selected_action"],
            "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        },
        "observed_discriminators": {
            "event_activation_reset_marker_delta": int(observed["event_delta"]),
            "post_enforcement_attacker_probe_count": int(observed["attacker_count"]),
            "post_enforcement_attacker_reset_marker_delta": int(observed["attacker_delta"]),
            "legitimate_commands_attempted": int(observed["legitimate_attempted"]),
            "authorized_noop_marker_delta": int(observed["legitimate_delta"]),
            "attacker_gateway_forwarded_count": int(observed["attacker_forwarded_count"]),
            "authorized_noop_gateway_forwarded": bool(observed["authorized_forwarded"]),
            "containment_observed": containment,
            "authority_convergence_observed": authority_convergence,
        },
        "predeclared_expectation": {
            "expected_post_enforcement_attacker_reset_marker_delta_for_acceptance_only": expected_attacker_delta,
            "expected_authorized_noop_marker_delta_for_acceptance_only": expected_authorized_delta,
            "outcome_matches_predeclared_expectation": outcome_matches,
            "expectation_used_as_metric_input": False,
            "expectation_used_to_reject_scientific_outcome": False,
        },
        "scientific_validity": {
            "event_treatment_fidelity_valid": True,
            "gateway_treatment_fidelity_valid": True,
            "raw_metric_inputs_complete": True,
            "policy_selection_not_gated_on_event_success": True,
            "unexpected_scientific_outcome_retained": not outcome_matches,
            "scientific_observation_retained": True,
        },
        "claim_boundaries": {
            "ground_truth_used_as_policy_oracle": False,
            "native_spacecraft_safe_mode_claim": False,
            "trusted_recovery_claim": False,
            "real_spacecraft_claim": False,
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
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "run_record": run_record,
        "binding_provenance": provenance,
    }


def execution_preflight() -> None:
    raise PermissionError(
        "R-060 is static observation-binding only; E1 campaign runtime remains blocked "
        "until a campaign-safe runtime adapter and separate explicit authorization exist"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    fixture = sub.add_parser("bind-static-fixture")
    fixture.add_argument("--plan-json", type=Path, required=True)
    fixture.add_argument("--measurement-json", type=Path, required=True)
    fixture.add_argument("--host-architecture", required=True)
    fixture.add_argument("--evidence-prefix", default="static-fixture/wp9/e1")
    fixture.add_argument("--output-json", type=Path, required=True)

    sub.add_parser("execute-trial")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_adapter()
        print("WP9_R060_E1_CAMPAIGN_OBSERVATION_ADAPTER_STATIC=PASS")
        for key in (
            "supported_cells",
            "post_event_analysis_horizon_s",
            "matched_attacker_probe_count",
            "post_response_authorized_noop_required",
            "expected_effects_used_as_metric_inputs",
            "unexpected_scientific_outcome_retained",
            "ground_truth_policy_oracle_allowed",
            "native_spacecraft_safe_mode_claim",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
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
            plan=_load(args.plan_json),
            measurement=_load(args.measurement_json),
            host_architecture=args.host_architecture,
            evidence_prefix=args.evidence_prefix,
        )
        _write(args.output_json, bundle)
        provenance = bundle["binding_provenance"]
        print("WP9_R060_E1_STATIC_FIXTURE_BINDING=PASS")
        print("cell_id=" + provenance["cell_id"])
        print("campaign_seed=" + str(provenance["campaign_seed"]))
        print(
            "outcome_matches_predeclared_expectation="
            + str(
                provenance["predeclared_expectation"][
                    "outcome_matches_predeclared_expectation"
                ]
            ).lower()
        )
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
