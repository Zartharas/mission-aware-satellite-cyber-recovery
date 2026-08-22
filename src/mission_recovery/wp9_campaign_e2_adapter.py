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
from .wp9_campaign_trial_controller import build_trial_plan, validate_static_controller
from .wp9_static_contracts import (
    build_e2_replay_effect_contract,
    evaluate_wp9_policy,
    load_campaign_design,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-056"
SUPPORTED_CELLS = ("A19", "A20", "A21")
COMMON_HORIZON = ROOT / "configs" / "wp9_precampaign_non_e3_horizon_freeze.json"
TOOLCHAIN = ROOT / "configs" / "toolchain-lock.json"
SCHEMA = ROOT / "configs" / "experiment_run.schema.json"


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
        raise ValueError(f"E2 measurement field must be integer: {key}")
    return value


def _as_bool(measurement: dict[str, Any], key: str) -> bool:
    value = measurement.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"E2 measurement field must be boolean: {key}")
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


def validate_static_adapter() -> dict[str, Any]:
    controller = validate_static_controller()
    horizon = _load(COMMON_HORIZON)
    design = load_campaign_design()
    cells = {row["cell_id"]: row for row in design["cells"]}

    _require(controller["decision_id"] == "R-054", "R-056 requires R-054 controller")
    _require(
        controller["final_campaign_execution_authorized"] is False,
        "R-056 static adapter cannot begin after campaign authorization",
    )
    _require(horizon["decision_id"] == "R-055", "R-056 requires R-055 horizon freeze")
    frozen = horizon["frozen_horizons"]
    _require(
        frozen["common_post_event_analysis_horizon_s"] == 30,
        "R-055 common horizon changed",
    )
    _require(
        frozen["E2_post_event_analysis_horizon_s"] == 30,
        "R-055 E2 horizon changed",
    )
    _require(
        frozen["runner_wall_clock_or_nominal_duration_used_as_metric_input"] is False,
        "runner duration cannot become an E2 metric input",
    )

    expected = {
        "A19": ("P0", "P0"),
        "A20": ("P1", "P1"),
        "A21": ("P7", "P1"),
    }
    for cell_id, (requested, effective) in expected.items():
        cell = cells[cell_id]
        _require(cell["event_id"] == "E2", f"{cell_id}: event is not E2")
        _require(cell["policy_id"] == requested, f"{cell_id}: requested policy changed")
        _require(
            cell["expected_effective_policy_id"] == effective,
            f"{cell_id}: effective policy contract changed",
        )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R056_E2_CAMPAIGN_OBSERVATION_ADAPTER_STATIC_READY",
        "supported_cells": list(SUPPORTED_CELLS),
        "post_event_analysis_horizon_s": 30,
        "post_response_authorized_noop_required": True,
        "expected_replay_effect_used_as_metric_input": False,
        "unexpected_scientific_outcome_retained": True,
        "campaign_runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def _validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_adapter()
    _require(plan.get("decision_id") == "R-054", "E2 adapter requires R-054 trial plan")
    cell_id = plan.get("cell_id")
    _require(cell_id in SUPPORTED_CELLS, "E2 adapter supports A19-A21 only")
    _require(plan.get("runtime_family") == "replay", "E2 runtime family changed")
    _require(
        plan.get("runtime_variant") == "e2_replay_effect",
        "E2 runtime variant changed",
    )
    factor = plan.get("factor_context", {})
    _require(factor.get("event_id") == "E2", "E2 plan event changed")
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
        "E2",
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


def _expected_forwarding(action: str) -> tuple[bool, bool]:
    if action == "OBSERVE_ONLY":
        return True, True
    if action in {"ISOLATE_MODELED_SOURCE", "RESTRICT_HIGH_RISK_COMMANDS"}:
        return False, True
    if action == "ENTER_SAFE_MODE":
        return False, False
    raise ValueError(f"unsupported E2 gateway action: {action}")


def _validate_measurement(
    *,
    plan: dict[str, Any],
    decision: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, int | bool | None]:
    _require(measurement.get("schema") == 1, "E2 measurement schema changed")
    _require(measurement.get("run_id") == plan["run_id"], "measurement run_id mismatch")

    setup_delta = _as_int(measurement, "setup_reset_marker_delta")
    intervening_delta = _as_int(measurement, "intervening_authorized_noop_marker_delta")
    replay_delta = _as_int(measurement, "post_replay_reset_marker_delta")
    legitimate_attempted = _as_int(measurement, "post_response_authorized_noop_attempted")
    legitimate_delta = _as_int(measurement, "post_response_authorized_noop_marker_delta")
    decision_count = _as_int(measurement, "gateway_decision_count")

    _require(setup_delta == 1, "authorized E2 setup reset did not complete exactly once")
    _require(
        intervening_delta == 1,
        "intervening authorized NOOP did not complete exactly once",
    )
    _require(replay_delta in {0, 1}, "post-replay reset delta must be 0 or 1")
    _require(legitimate_attempted == 1, "E2 campaign requires one post-response NOOP")
    _require(legitimate_delta in {0, 1}, "post-response NOOP delta must be 0 or 1")
    _require(decision_count == 2, "E2 campaign requires replay plus authorized-NOOP decisions")
    _require(
        _as_bool(measurement, "replayed_packet_byte_identical") is True,
        "E2 replay packet is not byte-identical to setup",
    )
    _require(
        _as_bool(measurement, "runtime_health_passed") is True,
        "runtime health failure makes the attempt invalid",
    )

    selected_action = decision["selected_action"]
    _require(
        measurement.get("replay_gateway_action") == selected_action,
        "replay gateway action differs from runtime policy",
    )
    _require(
        measurement.get("authorized_noop_gateway_action") == selected_action,
        "authorized-NOOP gateway action differs from runtime policy",
    )
    replay_forwarded = _as_bool(measurement, "replay_gateway_forwarded")
    noop_forwarded = _as_bool(measurement, "authorized_noop_gateway_forwarded")
    expected_replay_forwarded, expected_noop_forwarded = _expected_forwarding(selected_action)
    _require(
        replay_forwarded == expected_replay_forwarded,
        "gateway replay forwarding differs from frozen treatment semantics",
    )
    _require(
        noop_forwarded == expected_noop_forwarded,
        "gateway authorized-NOOP forwarding differs from frozen treatment semantics",
    )

    run_start_ns = _as_int(measurement, "run_start_ns")
    event_activation_ns = _as_int(measurement, "event_activation_ns")
    enforcement_ns = _as_int(measurement, "policy_enforcement_ns")
    replay_decision_ns = _as_int(measurement, "replay_gateway_decision_ns")
    authorized_noop_ns = _as_int(measurement, "authorized_noop_probe_observed_ns")
    observation_complete_ns = _as_int(measurement, "observation_complete_ns")
    effect_ns_raw = measurement.get("replay_effect_observed_ns")
    effect_ns: int | None
    if replay_delta == 1:
        _require(
            isinstance(effect_ns_raw, int) and not isinstance(effect_ns_raw, bool),
            "observed replay effect requires replay_effect_observed_ns",
        )
        effect_ns = int(effect_ns_raw)
    else:
        _require(effect_ns_raw is None, "zero replay effect cannot have effect timestamp")
        effect_ns = None

    _require(run_start_ns >= 0, "run_start_ns must be non-negative")
    _require(
        run_start_ns <= event_activation_ns <= enforcement_ns <= replay_decision_ns,
        "E2 response timestamps are out of order",
    )
    _require(
        replay_decision_ns <= authorized_noop_ns,
        "authorized NOOP observation precedes replay decision",
    )
    if effect_ns is not None:
        _require(
            event_activation_ns <= effect_ns <= authorized_noop_ns,
            "replay effect timestamp is outside response observation",
        )

    analysis_end_ns = event_activation_ns + 30_000_000_000
    _require(
        observation_complete_ns >= analysis_end_ns,
        "E2 observation did not cover frozen 30-second analysis horizon",
    )
    _require(
        authorized_noop_ns <= analysis_end_ns,
        "post-response authorized NOOP occurred after analysis horizon",
    )
    if effect_ns is not None:
        _require(effect_ns <= analysis_end_ns, "replay effect occurred after analysis horizon")

    return {
        "setup_delta": setup_delta,
        "intervening_delta": intervening_delta,
        "replay_delta": replay_delta,
        "legitimate_attempted": legitimate_attempted,
        "legitimate_delta": legitimate_delta,
        "run_start_ns": run_start_ns,
        "event_activation_ns": event_activation_ns,
        "enforcement_ns": enforcement_ns,
        "replay_decision_ns": replay_decision_ns,
        "authorized_noop_ns": authorized_noop_ns,
        "effect_ns": effect_ns,
        "analysis_end_ns": analysis_end_ns,
        "replay_forwarded": replay_forwarded,
        "noop_forwarded": noop_forwarded,
    }


def _seconds(ns: int, origin_ns: int) -> float:
    return (int(ns) - int(origin_ns)) / 1_000_000_000.0


def build_static_fixture_bundle(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
    host_architecture: str,
    evidence_prefix: str = "static-fixture/wp9/e2",
) -> dict[str, Any]:
    factor = _validate_plan(plan)
    event, decision = _runtime_policy(plan)
    observed = _validate_measurement(plan=plan, decision=decision, measurement=measurement)

    run_start_ns = int(observed["run_start_ns"])
    event_activation_ns = int(observed["event_activation_ns"])
    replay_decision_ns = int(observed["replay_decision_ns"])
    authorized_noop_ns = int(observed["authorized_noop_ns"])
    analysis_end_ns = int(observed["analysis_end_ns"])
    effect_ns = observed["effect_ns"]

    run_start_s = 0.0
    event_activation_s = _seconds(event_activation_ns, run_start_ns)
    analysis_end_s = _seconds(analysis_end_ns, run_start_ns)
    containment = not bool(observed["replay_forwarded"])
    containment_ns = replay_decision_ns if containment else None
    containment_s = None if containment_ns is None else _seconds(containment_ns, run_start_ns)
    event_success = int(observed["replay_delta"]) == 1
    event_success_s = None if effect_ns is None else _seconds(int(effect_ns), run_start_ns)
    authorized_observed = int(observed["legitimate_delta"]) == 1
    authority_convergence = containment and authorized_observed

    divergence: list[dict[str, Any]] = []
    if event_success:
        divergence.append(
            {
                "state_key": "command_authority",
                "start_s": float(event_success_s),
                "end_s": analysis_end_s,
            }
        )

    derived_ref = f"{evidence_prefix}/immutable-ground/e2-campaign-derived.json"
    gateway_ref = f"{evidence_prefix}/immutable-ground/gateway-decisions.jsonl"
    setup_ref = f"{evidence_prefix}/immutable-ground/setup-reset.json"
    replay_ref = f"{evidence_prefix}/immutable-ground/replay-send.json"
    noop_ref = f"{evidence_prefix}/immutable-ground/post-response-authorized-noop.json"
    runtime_ref = f"artifacts/runtime/{plan['run_id']}/runtime-manifest.txt"
    class_ref = f"{evidence_prefix}/immutable-ground/e2-classification-evidence.json"

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
        {row["criterion_id"] for row in checklist} | set(excluded)
        == set(RECOVERY_CRITERIA),
        "E2 command-family recovery partition changed",
    )

    raw = {
        "event_success": {
            "predicate": event_success,
            "timestamp_s": event_success_s,
        },
        "containment": {
            "predicate": containment,
            "timestamp_s": containment_s,
        },
        "trusted_recovery": {
            "predicate": False,
            "timestamp_s": None,
        },
        "objective_instances": [
            {
                "objective_instance_id": "replay-MO-1-response-interval",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": (
                    "observed_modeled_attacker_reset_effect_over_scheduled_interval"
                ),
                "completion_evidence_ref": replay_ref,
                "completed": not event_success,
            },
            {
                "objective_instance_id": "replay-MO-3-response-interval",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": (
                    "observed_authorized_ground_noop_cfs_marker_delta"
                ),
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
    analysis_end_utc = start_utc + timedelta(seconds=analysis_end_s - run_start_s)
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
        event_id="E2",
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
            "R-056 static E2 campaign-binding fixture; controlled NOS3 SAMPLE-state "
            "surrogate only; not campaign data."
        ),
    )

    contract = build_e2_replay_effect_contract(plan["cell_id"], design=load_campaign_design())
    expected_delta = int(
        contract["m01_effect_observation"]["expected_delta_for_acceptance_only"]
    )
    outcome_matches = int(observed["replay_delta"]) == expected_delta

    provenance = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R056_E2_STATIC_BINDING_FIXTURE",
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "runtime_family": "replay",
        "runtime_variant": "e2_replay_effect",
        "factor_context": deepcopy(factor),
        "event_instance": event,
        "execution_metadata": {
            "requested_policy_id": factor["policy_id"],
            "effective_policy_id": decision["delegated_policy_id"],
            "selected_action": decision["selected_action"],
            "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        },
        "observed_discriminators": {
            "setup_reset_marker_delta": int(observed["setup_delta"]),
            "intervening_authorized_noop_marker_delta": int(observed["intervening_delta"]),
            "post_replay_reset_marker_delta": int(observed["replay_delta"]),
            "post_response_authorized_noop_marker_delta": int(observed["legitimate_delta"]),
            "replay_gateway_forwarded": bool(observed["replay_forwarded"]),
            "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
        },
        "predeclared_expectation": {
            "expected_replay_reset_marker_delta_for_acceptance_only": expected_delta,
            "outcome_matches_predeclared_expectation": outcome_matches,
            "expectation_used_as_metric_input": False,
            "expectation_used_to_reject_scientific_outcome": False,
        },
        "scientific_validity": {
            "treatment_fidelity_valid": True,
            "raw_metric_inputs_complete": True,
            "unexpected_scientific_outcome_retained": not outcome_matches,
            "scientific_observation_retained": True,
        },
        "static_fixture_only": True,
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
        "R-056 is static observation-binding only; E2 campaign runtime remains blocked "
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
    fixture.add_argument("--evidence-prefix", default="static-fixture/wp9/e2")
    fixture.add_argument("--output-json", type=Path, required=True)

    sub.add_parser("execute-trial")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_adapter()
        print("WP9_R056_E2_CAMPAIGN_OBSERVATION_ADAPTER_STATIC=PASS")
        for key in (
            "supported_cells",
            "post_event_analysis_horizon_s",
            "post_response_authorized_noop_required",
            "expected_replay_effect_used_as_metric_input",
            "unexpected_scientific_outcome_retained",
            "campaign_runtime_execution_performed",
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
        print("WP9_R056_E2_STATIC_FIXTURE_BINDING=PASS")
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
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
