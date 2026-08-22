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
from .wp9_static_contracts import evaluate_wp9_policy, load_campaign_design

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-058"
SUPPORTED_CELLS = ("A22", "A23", "A24")
COMMON_HORIZON = ROOT / "configs" / "wp9_precampaign_non_e3_horizon_freeze.json"
TOOLCHAIN = ROOT / "configs" / "toolchain-lock.json"


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
        raise ValueError(f"E4 measurement field must be integer: {key}")
    return value


def _as_bool(measurement: dict[str, Any], key: str) -> bool:
    value = measurement.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"E4 measurement field must be boolean: {key}")
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

    _require(controller["decision_id"] == "R-054", "R-058 requires R-054 controller")
    _require(
        controller["final_campaign_execution_authorized"] is False,
        "R-058 static adapter cannot begin after campaign authorization",
    )
    _require(horizon["decision_id"] == "R-055", "R-058 requires R-055 horizon freeze")
    frozen = horizon["frozen_horizons"]
    _require(frozen["common_post_event_analysis_horizon_s"] == 30, "common horizon changed")
    _require(frozen["E4_post_event_analysis_horizon_s"] == 30, "E4 horizon changed")
    _require(
        frozen["runner_wall_clock_or_nominal_duration_used_as_metric_input"] is False,
        "runner duration cannot become an E4 metric input",
    )

    expected = {
        "A22": ("P0", "P0"),
        "A23": ("P4", "P4"),
        "A24": ("P7", "P4"),
    }
    for cell_id, (requested, effective) in expected.items():
        cell = cells[cell_id]
        _require(cell["event_id"] == "E4", f"{cell_id}: event is not E4")
        _require(cell["policy_id"] == requested, f"{cell_id}: requested policy changed")
        _require(
            cell["expected_effective_policy_id"] == effective,
            f"{cell_id}: effective policy contract changed",
        )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R058_E4_CAMPAIGN_OBSERVATION_ADAPTER_STATIC_READY",
        "supported_cells": list(SUPPORTED_CELLS),
        "post_event_analysis_horizon_s": 30,
        "event_activation_requires_truth_visible_separation": True,
        "post_response_authorized_noop_required": True,
        "unexpected_scientific_outcome_retained": True,
        "trusted_recovery_fabricated_by_observability_route": False,
        "native_spacecraft_safe_mode_claim": False,
        "campaign_runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def _validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_adapter()
    _require(plan.get("decision_id") == "R-054", "E4 adapter requires R-054 trial plan")
    cell_id = plan.get("cell_id")
    _require(cell_id in SUPPORTED_CELLS, "E4 adapter supports A22-A24 only")
    _require(plan.get("runtime_family") == "observability", "E4 runtime family changed")
    _require(plan.get("runtime_variant") == "e4_observability", "E4 runtime variant changed")
    factor = plan.get("factor_context", {})
    _require(factor.get("event_id") == "E4", "E4 plan event changed")
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
        "E4",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    _require(
        event["ground_truth"]["telemetry_truth_available"] is True,
        "E4 immutable telemetry truth changed",
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(decision["oracle_ground_truth_read"] is False, "policy read immutable ground truth")
    _require(
        decision["delegated_policy_id"]
        == plan["expected_effective_policy_id_for_acceptance_only"],
        "actual policy treatment differs from frozen campaign design",
    )
    return event, decision


def _expected_noop_forwarding(action: str) -> bool:
    if action == "OBSERVE_ONLY":
        return True
    if action == "ENTER_SAFE_MODE":
        return False
    raise ValueError(f"unsupported E4 gateway action: {action}")


def _validate_measurement(
    *,
    plan: dict[str, Any],
    decision: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, int | bool]:
    _require(measurement.get("schema") == 1, "E4 measurement schema changed")
    _require(measurement.get("run_id") == plan["run_id"], "measurement run_id mismatch")

    event_truth = _as_int(measurement, "event_truth_high_value_delta")
    event_visible = _as_int(measurement, "event_policy_visible_high_value_delta")
    post_truth = _as_int(measurement, "post_response_truth_high_value_delta")
    post_visible = _as_int(measurement, "post_response_policy_visible_high_value_delta")
    legitimate_attempted = _as_int(measurement, "post_response_authorized_noop_attempted")
    legitimate_delta = _as_int(measurement, "post_response_authorized_noop_marker_delta")
    gateway_count = _as_int(measurement, "gateway_decision_count")

    # Event activation is treatment fidelity, not an outcome expectation.
    _require(event_truth == 1, "E4 immutable-truth event sample not observed exactly once")
    _require(event_visible == 0, "E4 degraded policy-visible treatment did not activate")
    _require(post_truth == 1, "E4 post-response immutable-truth probe not observed exactly once")
    _require(post_visible in {0, 1}, "E4 post-response visible delta must be 0 or 1")
    _require(legitimate_attempted == 1, "E4 campaign requires one post-response authorized NOOP")
    _require(legitimate_delta in {0, 1}, "post-response NOOP delta must be 0 or 1")
    _require(gateway_count == 1, "E4 campaign requires exactly one authorized-NOOP decision")
    _require(_as_bool(measurement, "immutable_truth_separate") is True, "truth/evidence separation failed")
    _require(_as_bool(measurement, "runtime_health_passed") is True, "runtime health failure invalidates attempt")

    selected_action = decision["selected_action"]
    _require(
        measurement.get("authorized_noop_gateway_action") == selected_action,
        "authorized-NOOP gateway action differs from runtime policy",
    )
    noop_forwarded = _as_bool(measurement, "authorized_noop_gateway_forwarded")
    _require(
        noop_forwarded == _expected_noop_forwarding(selected_action),
        "gateway authorized-NOOP forwarding differs from frozen treatment semantics",
    )

    run_start_ns = _as_int(measurement, "run_start_ns")
    event_activation_ns = _as_int(measurement, "event_activation_ns")
    event_success_ns = _as_int(measurement, "event_success_observed_ns")
    policy_selection_ns = _as_int(measurement, "policy_selection_ns")
    enforcement_ns = _as_int(measurement, "policy_enforcement_ns")
    post_probe_ns = _as_int(measurement, "post_response_probe_observed_ns")
    authorized_noop_ns = _as_int(measurement, "authorized_noop_probe_observed_ns")
    observation_complete_ns = _as_int(measurement, "observation_complete_ns")

    _require(run_start_ns >= 0, "run_start_ns must be non-negative")
    _require(
        run_start_ns <= event_activation_ns <= policy_selection_ns <= enforcement_ns,
        "E4 response timestamps are out of order",
    )
    _require(
        event_activation_ns <= event_success_ns <= post_probe_ns,
        "E4 event-success timestamp is out of bounds",
    )
    _require(enforcement_ns <= post_probe_ns, "E4 post-response probe precedes enforcement")
    _require(post_probe_ns <= authorized_noop_ns, "authorized NOOP precedes post-response telemetry probe")

    analysis_end_ns = event_activation_ns + 30_000_000_000
    _require(
        observation_complete_ns >= analysis_end_ns,
        "E4 observation did not cover frozen 30-second analysis horizon",
    )
    _require(post_probe_ns <= analysis_end_ns, "post-response telemetry probe occurred after horizon")
    _require(authorized_noop_ns <= analysis_end_ns, "authorized NOOP occurred after analysis horizon")

    return {
        "event_truth_delta": event_truth,
        "event_visible_delta": event_visible,
        "post_truth_delta": post_truth,
        "post_visible_delta": post_visible,
        "legitimate_attempted": legitimate_attempted,
        "legitimate_delta": legitimate_delta,
        "noop_forwarded": noop_forwarded,
        "run_start_ns": run_start_ns,
        "event_activation_ns": event_activation_ns,
        "event_success_ns": event_success_ns,
        "policy_selection_ns": policy_selection_ns,
        "enforcement_ns": enforcement_ns,
        "post_probe_ns": post_probe_ns,
        "authorized_noop_ns": authorized_noop_ns,
        "analysis_end_ns": analysis_end_ns,
    }


def build_static_fixture_bundle(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
    host_architecture: str,
    evidence_prefix: str = "static-fixture/wp9/e4",
) -> dict[str, Any]:
    factor = _validate_plan(plan)
    event, decision = _runtime_policy(plan)
    observed = _validate_measurement(plan=plan, decision=decision, measurement=measurement)

    run_start_ns = int(observed["run_start_ns"])
    event_activation_ns = int(observed["event_activation_ns"])
    event_success_ns = int(observed["event_success_ns"])
    post_probe_ns = int(observed["post_probe_ns"])
    analysis_end_ns = int(observed["analysis_end_ns"])

    event_activation_s = _seconds(event_activation_ns, run_start_ns)
    event_success_s = _seconds(event_success_ns, run_start_ns)
    post_probe_s = _seconds(post_probe_ns, run_start_ns)
    analysis_end_s = _seconds(analysis_end_ns, run_start_ns)

    telemetry_restored = int(observed["post_visible_delta"]) == 1
    authorized_observed = int(observed["legitimate_delta"]) == 1
    containment_s = post_probe_s if telemetry_restored else None

    truth_ref = f"{evidence_prefix}/immutable-ground/telemetry-truth.jsonl"
    visible_ref = f"{evidence_prefix}/runtime-observation/policy-visible.jsonl"
    gateway_ref = f"{evidence_prefix}/immutable-ground/gateway-decisions.jsonl"
    noop_ref = f"{evidence_prefix}/immutable-ground/post-response-authorized-noop.json"
    health_ref = f"artifacts/runtime/{plan['run_id']}/runtime-manifest.txt"
    classification_ref = f"{evidence_prefix}/immutable-ground/e4-classification-evidence.json"

    checklist = [
        {
            "criterion_id": "required_telemetry_restored",
            "available_current": telemetry_restored,
            "criterion_satisfied": telemetry_restored,
            "evidence_ref": visible_ref,
        },
        {
            "criterion_id": "health_checks_passed",
            "available_current": True,
            "criterion_satisfied": True,
            "evidence_ref": health_ref,
        },
        {
            "criterion_id": "recovery_manifest_complete",
            "available_current": True,
            "criterion_satisfied": False,
            "evidence_ref": classification_ref,
        },
    ]
    excluded = [
        "approved_version",
        "integrity_measurement_valid",
        "authorization_valid",
        "measured_state_current",
        "authorized_command_path_restored",
        "ground_spacecraft_state_agreed",
        "no_residual_unauthorized_state",
    ]
    _require(
        {row["criterion_id"] for row in checklist} | set(excluded)
        == set(RECOVERY_CRITERIA),
        "E4 recovery partition changed",
    )

    operational = telemetry_restored and authorized_observed
    raw = {
        "event_success": {"predicate": True, "timestamp_s": event_success_s},
        "containment": {"predicate": telemetry_restored, "timestamp_s": containment_s},
        "trusted_recovery": {"predicate": False, "timestamp_s": None},
        "objective_instances": [
            {
                "objective_instance_id": "observability-MO-3-response-interval",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": "required_high_value_telemetry_policy_visible_after_response",
                "completion_evidence_ref": visible_ref,
                "completed": telemetry_restored,
            },
            {
                "objective_instance_id": "observability-MO-5-evidence-integrity",
                "weight": 1.0,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": analysis_end_s,
                "completion_predicate": "immutable_truth_separate_and_runtime_health_passed",
                "completion_evidence_ref": truth_ref,
                "completed": True,
            },
        ],
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": int(observed["legitimate_attempted"]),
            "rejected": int(observed["legitimate_attempted"]) - int(observed["legitimate_delta"]),
        },
        "ground_spacecraft_divergence_intervals": [],
        "recovery_checklist": checklist,
        "recovery_checklist_excluded": excluded,
        "run_end_s": analysis_end_s,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": False,
            "operational_restored": operational,
            "recovery_failed": not telemetry_restored,
            "contained": telemetry_restored,
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
        event_id="E4",
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
            "R-058 static E4 campaign-binding fixture; controlled NOS3 telemetry-visibility "
            "surrogate only; no RF interference, native spacecraft safe-mode, or campaign data."
        ),
    )

    expected_noop_delta = 1 if decision["selected_action"] == "OBSERVE_ONLY" else 0
    expected_post_visible_delta = 0
    outcome_matches = (
        int(observed["post_visible_delta"]) == expected_post_visible_delta
        and int(observed["legitimate_delta"]) == expected_noop_delta
    )

    provenance = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R058_E4_STATIC_BINDING_FIXTURE",
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "runtime_family": "observability",
        "runtime_variant": "e4_observability",
        "factor_context": deepcopy(factor),
        "event_instance": event,
        "execution_metadata": {
            "requested_policy_id": factor["policy_id"],
            "effective_policy_id": decision["delegated_policy_id"],
            "selected_action": decision["selected_action"],
            "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        },
        "observed_discriminators": {
            "event_truth_high_value_delta": int(observed["event_truth_delta"]),
            "event_policy_visible_high_value_delta": int(observed["event_visible_delta"]),
            "post_response_truth_high_value_delta": int(observed["post_truth_delta"]),
            "post_response_policy_visible_high_value_delta": int(observed["post_visible_delta"]),
            "post_response_authorized_noop_marker_delta": int(observed["legitimate_delta"]),
            "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
            "telemetry_restored_observed": telemetry_restored,
        },
        "predeclared_expectation": {
            "expected_post_response_policy_visible_high_value_delta_for_acceptance_only": expected_post_visible_delta,
            "expected_post_response_authorized_noop_marker_delta_for_acceptance_only": expected_noop_delta,
            "outcome_matches_predeclared_expectation": outcome_matches,
            "expectation_used_as_metric_input": False,
            "expectation_used_to_reject_scientific_outcome": False,
        },
        "scientific_validity": {
            "event_treatment_fidelity_valid": True,
            "gateway_treatment_fidelity_valid": True,
            "raw_metric_inputs_complete": True,
            "unexpected_scientific_outcome_retained": not outcome_matches,
            "scientific_observation_retained": True,
        },
        "claim_boundaries": {
            "immutable_ground_truth_separate": True,
            "ground_truth_used_as_policy_oracle": False,
            "native_spacecraft_safe_mode_claim": False,
            "p4_telemetry_restoration_attribution_claim": False,
            "spacecraft_failure_claim": False,
            "rf_interference_claim": False,
        },
        "static_fixture_only": True,
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
        "R-058 is static observation-binding only; E4 campaign runtime remains blocked "
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
    fixture.add_argument("--evidence-prefix", default="static-fixture/wp9/e4")
    fixture.add_argument("--output-json", type=Path, required=True)

    sub.add_parser("execute-trial")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_adapter()
        print("WP9_R058_E4_CAMPAIGN_OBSERVATION_ADAPTER_STATIC=PASS")
        for key in (
            "supported_cells",
            "post_event_analysis_horizon_s",
            "event_activation_requires_truth_visible_separation",
            "post_response_authorized_noop_required",
            "unexpected_scientific_outcome_retained",
            "trusted_recovery_fabricated_by_observability_route",
            "native_spacecraft_safe_mode_claim",
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
        print("WP9_R058_E4_STATIC_FIXTURE_BINDING=PASS")
        print("cell_id=" + provenance["cell_id"])
        print("campaign_seed=" + str(provenance["campaign_seed"]))
        print(
            "outcome_matches_predeclared_expectation="
            + str(provenance["predeclared_expectation"]["outcome_matches_predeclared_expectation"]).lower()
        )
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
