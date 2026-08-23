from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)
from .wp9_campaign_e1_runtime_adapter import (
    DEVELOPMENT_CASES as R061_DEVELOPMENT_CASES,
)
from .wp9_campaign_e2_runtime_adapter import (
    DEVELOPMENT_CASES as R057_DEVELOPMENT_CASES,
)
from .wp9_campaign_e3_adapter import (
    APPROVED_SHA256,
    TAMPERED_SHA256,
    _p2_observation,
    _recovery_observation,
    _validate_common,
    validate_static_adapter as validate_r062_static_adapter,
)
from .wp9_campaign_e4_runtime_adapter import (
    DEVELOPMENT_CASES as R059_DEVELOPMENT_CASES,
)
from .wp9_static_contracts import (
    evaluate_wp9_policy,
    load_campaign_design,
    runtime_route_for_cell,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-063"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"

DEVELOPMENT_CASES: dict[str, dict[str, Any]] = {
    "Y01": {"cell_id": "A13", "development_seed": 9931},
    "Y02": {"cell_id": "A11", "development_seed": 9932},
    "Y03": {"cell_id": "A15", "development_seed": 9933},
    "Y04": {"cell_id": "A16", "development_seed": 9934},
    "Y05": {"cell_id": "A17", "development_seed": 9935},
    "Y06": {"cell_id": "A18", "development_seed": 9936},
}

EXPECTED_CASE_BINDINGS = {
    "Y01": ("A13", "P7", "P2", "C0", "T1", "e3_command_gateway"),
    "Y02": ("A11", "P7", "P5", "C0", "T0", "e3_trusted_recovery"),
    "Y03": (
        "A15",
        "P5",
        "P5",
        "C0",
        "T1",
        "e3_trusted_recovery_reduced_evidence",
    ),
    "Y04": (
        "A16",
        "P6",
        "P6",
        "C0",
        "T0",
        "e3_ground_authorized_recovery",
    ),
    "Y05": (
        "A17",
        "P6",
        "P6",
        "C1",
        "T0",
        "e3_ground_authorized_recovery",
    ),
    "Y06": (
        "A18",
        "P7",
        "P5",
        "C1",
        "T0",
        "e3_trusted_recovery_contact_delay",
    ),
}

OMITTED_RUNTIME_DUPLICATES = {
    "A10": "Y01",
    "A12": "Y01",
    "A14": "Y02",
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


def _cells() -> dict[str, dict[str, Any]]:
    return {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }


def development_case(case_id: str) -> dict[str, Any]:
    if case_id not in DEVELOPMENT_CASES:
        raise ValueError("R-063 E3 route validation supports Y01-Y06 only")
    return deepcopy(DEVELOPMENT_CASES[case_id])


def _seed_set(cases: dict[str, dict[str, Any]]) -> set[int]:
    return {
        int(row["development_seed"])
        for row in cases.values()
    }


def validate_static_runtime_adapter() -> dict[str, Any]:
    r062 = validate_r062_static_adapter()
    seed_plan = _load(SEED_PLAN)
    campaign_seeds = set(
        seed_plan["seed_selection"]["campaign_seed_ids"]
    )
    pilot_seeds = set(
        seed_plan["seed_selection"]["pilot_seed_ids"]
    )
    b2_seeds = set(
        seed_plan["seed_selection"]["development_seed_ids"]
    )
    prior_sets = {
        "campaign": campaign_seeds,
        "pilot": pilot_seeds,
        "WP9-B2": b2_seeds,
        "R-057": _seed_set(R057_DEVELOPMENT_CASES),
        "R-059": _seed_set(R059_DEVELOPMENT_CASES),
        "R-061": _seed_set(R061_DEVELOPMENT_CASES),
    }
    route_seeds = _seed_set(DEVELOPMENT_CASES)
    cells = _cells()

    _require(
        r062["decision_id"] == "R-062",
        "R-063 requires R-062",
    )
    _require(
        r062["runtime_execution_performed"] is False,
        "R-063 static gate cannot follow hidden R-062 runtime",
    )
    _require(
        r062["final_campaign_execution_authorized"] is False,
        "R-063 cannot begin after final campaign authorization",
    )
    _require(
        route_seeds == {9931, 9932, 9933, 9934, 9935, 9936},
        "R-063 development seeds changed",
    )
    _require(
        len(route_seeds) == len(DEVELOPMENT_CASES) == 6,
        "R-063 development seeds must be unique",
    )
    for label, reserved in prior_sets.items():
        _require(
            route_seeds.isdisjoint(reserved),
            f"R-063 development seed collides with {label} seed",
        )

    observed_variants: set[str] = set()
    for case_id, expected in EXPECTED_CASE_BINDINGS.items():
        (
            cell_id,
            requested,
            effective,
            contact,
            evidence,
            variant,
        ) = expected
        case = DEVELOPMENT_CASES[case_id]
        _require(
            case["cell_id"] == cell_id,
            f"{case_id}: cell mapping changed",
        )
        cell = cells[cell_id]
        route = runtime_route_for_cell(cell_id)
        _require(cell["event_id"] == "E3", f"{case_id}: event changed")
        _require(cell["mission_state_id"] == "M4", f"{case_id}: mission state changed")
        _require(cell["policy_id"] == requested, f"{case_id}: requested policy changed")
        _require(
            cell["expected_effective_policy_id"] == effective,
            f"{case_id}: effective policy changed",
        )
        _require(
            cell["contact_condition_id"] == contact,
            f"{case_id}: contact condition changed",
        )
        _require(
            cell["evidence_condition_id"] == evidence,
            f"{case_id}: evidence condition changed",
        )
        _require(
            route["runtime_family"] == "recovery",
            f"{case_id}: runtime family changed",
        )
        _require(
            route["runtime_variant"] == variant,
            f"{case_id}: runtime variant changed",
        )
        observed_variants.add(variant)

    _require(
        observed_variants
        == {
            "e3_command_gateway",
            "e3_trusted_recovery",
            "e3_trusted_recovery_reduced_evidence",
            "e3_ground_authorized_recovery",
            "e3_trusted_recovery_contact_delay",
        },
        "R-063 no longer covers all distinct E3 runtime variants",
    )

    _require(
        cells["A10"]["expected_effective_policy_id"] == "P2"
        and cells["A12"]["expected_effective_policy_id"] == "P2"
        and runtime_route_for_cell("A10")["runtime_variant"]
        == "e3_command_gateway"
        and runtime_route_for_cell("A12")["runtime_variant"]
        == "e3_command_gateway",
        "R-063 A10/A12 omission rationale changed",
    )
    _require(
        cells["A14"]["expected_effective_policy_id"] == "P5"
        and runtime_route_for_cell("A14")["runtime_variant"]
        == "e3_trusted_recovery",
        "R-063 A14 omission rationale changed",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R063_E3_BOUNDED_ROUTE_HARNESS_STATIC_READY",
        "development_cases": deepcopy(DEVELOPMENT_CASES),
        "case_bindings": {
            key: list(value)
            for key, value in EXPECTED_CASE_BINDINGS.items()
        },
        "omitted_runtime_duplicates": deepcopy(OMITTED_RUNTIME_DUPLICATES),
        "minimal_representative_case_count": 6,
        "covered_runtime_variants": sorted(observed_variants),
        "covered_requested_effective_paths": [
            ["P7", "P2"],
            ["P7", "P5"],
            ["P5", "P5"],
            ["P6", "P6"],
        ],
        "covered_contact_conditions": ["C0", "C1"],
        "covered_evidence_conditions": ["T0", "T1"],
        "modeled_c1_contact_window_s": 10,
        "post_event_analysis_horizon_s": 30,
        "p2_command_mitigation_counts_as_update_containment": False,
        "p6_post_authorization_delegate": "P5",
        "a18_ground_authorization_waited": False,
        "unexpected_scientific_outcome_retained": True,
        "ground_truth_policy_oracle_allowed": False,
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "development_runtime_execution_authorized": False,
        "campaign_runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def build_development_plan(
    *,
    case_id: str,
    run_id: str,
    repo_commit: str,
) -> dict[str, Any]:
    validate_static_runtime_adapter()
    case = development_case(case_id)
    _require(
        RUN_ID_PATTERN.fullmatch(run_id) is not None,
        "R-063 run_id contains unsupported characters",
    )
    _require(
        COMMIT_PATTERN.fullmatch(repo_commit) is not None,
        "R-063 repo_commit must be lowercase 40-hex",
    )

    cell = _cells()[case["cell_id"]]
    seed = int(case["development_seed"])
    event = materialize_event(
        "E3",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    route = runtime_route_for_cell(cell["cell_id"])

    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-063 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == cell["expected_effective_policy_id"],
        "R-063 runtime policy differs from frozen E3 design",
    )

    contact = cell["contact_condition_id"]
    p6_release = None
    if cell["policy_id"] == "P6":
        p6_release = 10 if contact == "C1" else 0

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R063_E3_ROUTE_VALIDATION_PLAN",
        "case_id": case_id,
        "run_id": run_id,
        "repo_commit": repo_commit,
        "cell_id": cell["cell_id"],
        "development_seed": seed,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": "E3",
            "policy_id": cell["policy_id"],
            "contact_condition_id": contact,
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance": event,
        "expected_effective_policy_id_for_acceptance_only": (
            cell["expected_effective_policy_id"]
        ),
        "expected_selected_action_for_acceptance_only": (
            decision["selected_action"]
        ),
        "runtime_family": "recovery",
        "runtime_variant": route["runtime_variant"],
        "timing_contract": {
            "post_event_analysis_horizon_s": 30,
            "modeled_c1_contact_window_s": (
                10 if contact == "C1" else None
            ),
            "p6_ground_authorization_release_after_response_boundary_s": (
                p6_release
            ),
            "early_absorbing_trusted_recovery_allowed": True,
            "unrecovered_run_right_censored_at_horizon": True,
            "runner_duration_used_as_metric_input": False,
        },
        "treatment_contract": {
            "event_slot_sha256": TAMPERED_SHA256,
            "approved_replacement_sha256": APPROVED_SHA256,
            "p2_command_mitigation_counts_as_update_containment": False,
            "policy_selection_not_gated_on_event_success_required": True,
            "post_response_authorized_noop_required": True,
            "p6_post_authorization_delegate": (
                "P5" if cell["policy_id"] == "P6" else None
            ),
            "a18_ground_authorization_waited": (
                False if cell["cell_id"] == "A18" else None
            ),
        },
        "acceptance_only_expected_effects": {
            "update_containment_observed": (
                decision["delegated_policy_id"] in {"P5", "P6"}
            ),
            "authorized_noop_marker_delta": 1,
            "trusted_recovery_confirmed": None,
        },
        "development_validation_only": True,
        "development_runtime_execution_authorized": False,
        "ground_truth_policy_oracle_allowed": False,
        "real_ground_contact_required": False,
        "real_human_operator_required": False,
        "operational_firmware_activation_claim": False,
        "real_spacecraft_claim": False,
        "rf_interference_claim": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
    }


def select_runtime_policy(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_runtime_adapter()
    _require(
        plan.get("decision_id") == DECISION_ID,
        "not an R-063 development plan",
    )
    case = development_case(str(plan.get("case_id")))
    _require(
        plan.get("cell_id") == case["cell_id"],
        "R-063 plan cell mismatch",
    )
    _require(
        int(plan.get("development_seed")) == int(case["development_seed"]),
        "R-063 development seed mismatch",
    )
    factor = plan.get("factor_context", {})
    event = materialize_event(
        "E3",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-063 runtime policy cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == plan["expected_effective_policy_id_for_acceptance_only"],
        "R-063 runtime effective policy changed",
    )
    _require(
        decision["selected_action"]
        == plan["expected_selected_action_for_acceptance_only"],
        "R-063 runtime action changed",
    )
    result = deepcopy(decision)
    result.update(
        {
            "schema": 1,
            "decision_id": DECISION_ID,
            "classification": "WP9_R063_E3_RUNTIME_POLICY_DECISION",
            "case_id": plan["case_id"],
            "cell_id": plan["cell_id"],
            "development_seed": int(plan["development_seed"]),
            "development_validation_only": True,
            "campaign_seed_consumed": False,
            "campaign_data_generated": False,
        }
    )
    return result


def build_p5_handoff(
    *,
    plan: dict[str, Any],
    runtime_policy: dict[str, Any],
) -> dict[str, Any]:
    _require(
        runtime_policy.get("delegated_policy_id") == "P6",
        "R-063 P5 handoff is only valid after P6",
    )
    factor = plan["factor_context"]
    event = materialize_event(
        "E3",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy("P5", event)
    _require(
        decision["delegated_policy_id"] == "P5",
        "R-063 P6 handoff did not delegate to P5",
    )
    _require(
        decision["selected_action"] == "REQUEST_VERIFIED_ROLLBACK",
        "R-063 P6 handoff action changed",
    )
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-063 P6 handoff read immutable ground truth",
    )
    result = deepcopy(decision)
    result.update(
        {
            "schema": 1,
            "decision_id": DECISION_ID,
            "classification": "WP9_R063_P6_TO_P5_HANDOFF",
            "case_id": plan["case_id"],
            "cell_id": plan["cell_id"],
            "development_seed": int(plan["development_seed"]),
            "ground_authorization_source": (
                "synthetic_ground_authorization_schedule"
            ),
            "real_ground_contact": False,
            "real_human_operator": False,
        }
    )
    return result


def materialize_runtime_artifacts(
    *,
    plan: dict[str, Any],
) -> dict[str, Any]:
    _require(
        plan.get("decision_id") == DECISION_ID,
        "not an R-063 development plan",
    )
    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    tampered_verification = verify_candidate(tampered, manifest)
    _require(
        sha256_hex(approved) == APPROVED_SHA256,
        "approved update identity changed",
    )
    _require(
        sha256_hex(tampered) == TAMPERED_SHA256,
        "tampered update identity changed",
    )
    _require(
        tampered_verification["accepted"] is False,
        "tampered E3 update unexpectedly accepted",
    )
    return {
        "event_instance": deepcopy(plan["event_instance"]),
        "approved_update": approved,
        "tampered_update": tampered,
        "approved_manifest": manifest,
        "tampered_verification": tampered_verification,
    }


def _validated_policy(
    *,
    plan: dict[str, Any],
    runtime_policy: dict[str, Any],
) -> dict[str, Any]:
    recomputed = select_runtime_policy(plan)
    for key in (
        "delegated_policy_id",
        "selected_action",
        "oracle_ground_truth_read",
    ):
        _require(
            runtime_policy.get(key) == recomputed.get(key),
            f"R-063 retained runtime policy differs: {key}",
        )
    return recomputed


def finalize_development_observation(
    *,
    plan: dict[str, Any],
    runtime_policy: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validate_static_runtime_adapter()
    decision = _validated_policy(
        plan=plan,
        runtime_policy=runtime_policy,
    )
    common = _validate_common(plan, measurement)
    effective = decision["delegated_policy_id"]

    if effective == "P2":
        observed = _p2_observation(decision, measurement)
        _require(
            common["complete_ns"] >= common["analysis_end_ns"],
            "R-063 unrecovered P2 run did not cover 30-second horizon",
        )
    else:
        observed = _recovery_observation(
            plan,
            plan["event_instance"],
            decision,
            common,
            measurement,
        )

    containment = bool(observed["containment"])
    noop_delta = int(observed["noop_delta"])
    expected_containment = effective in {"P5", "P6"}
    expected_noop_delta = 1
    outcome_matches = (
        containment == expected_containment
        and noop_delta == expected_noop_delta
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R063_E3_ROUTE_VALIDATION_PASS",
        "acceptance_status": "PASS",
        "case_id": plan["case_id"],
        "cell_id": plan["cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": int(plan["development_seed"]),
        "requested_policy_id": plan["factor_context"]["policy_id"],
        "actual_effective_policy_id": effective,
        "selected_action": decision["selected_action"],
        "runtime_variant": plan["runtime_variant"],
        "oracle_ground_truth_read": False,
        "event_activation_observed": True,
        "update_containment_observed": containment,
        "p2_command_mitigation_counts_as_update_containment": False,
        "post_response_authorized_noop_marker_delta": noop_delta,
        "trusted_recovery_confirmed": bool(observed["trusted"]),
        "ground_authorization_waited": bool(observed["ground_waited"]),
        "post_event_analysis_horizon_s": 30,
        "modeled_c1_contact_window_s": (
            10
            if plan["factor_context"]["contact_condition_id"] == "C1"
            else None
        ),
        "expected_update_containment_for_acceptance_only": (
            expected_containment
        ),
        "expected_authorized_noop_marker_delta_for_acceptance_only": (
            expected_noop_delta
        ),
        "outcome_matches_predeclared_expectation": outcome_matches,
        "unexpected_scientific_outcome_would_be_retained_in_campaign": (
            not outcome_matches
        ),
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "policy_selection_not_gated_on_event_success": True,
        "runner_duration_used_as_metric_input": False,
        "development_validation_only": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "claim_boundaries": {
            "trusted_recovery_scope": (
                "controlled_staged_synthetic_update_state_only"
            ),
            "operational_firmware_activation_claim": False,
            "real_spacecraft_claim": False,
            "real_ground_contact_claim": False,
            "real_human_operator_claim": False,
            "rf_interference_claim": False,
        },
    }


def development_execution_preflight() -> None:
    raise PermissionError(
        "R-063 development runtime remains blocked until the exact-SHA "
        "static/TDD harness gate passes and a separate explicit per-case "
        "authorization is recorded"
    )


def campaign_execution_preflight() -> None:
    raise PermissionError(
        "R-063 final campaign execution remains blocked; bounded E3 "
        "development validation must close and a separate final-campaign "
        "authorization is required"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate-static")

    plan_parser = sub.add_parser("plan-development")
    plan_parser.add_argument("--case-id", required=True)
    plan_parser.add_argument("--run-id", required=True)
    plan_parser.add_argument("--repo-commit", required=True)
    plan_parser.add_argument("--output-json", type=Path, required=True)

    policy_parser = sub.add_parser("select-policy")
    policy_parser.add_argument("--plan-json", type=Path, required=True)
    policy_parser.add_argument("--output-json", type=Path, required=True)

    handoff = sub.add_parser("build-p5-handoff")
    handoff.add_argument("--plan-json", type=Path, required=True)
    handoff.add_argument("--policy-json", type=Path, required=True)
    handoff.add_argument("--output-json", type=Path, required=True)

    materialize = sub.add_parser("materialize-artifacts")
    materialize.add_argument("--plan-json", type=Path, required=True)
    materialize.add_argument("--event-json", type=Path, required=True)
    materialize.add_argument("--approved", type=Path, required=True)
    materialize.add_argument("--tampered", type=Path, required=True)
    materialize.add_argument("--manifest-json", type=Path, required=True)
    materialize.add_argument(
        "--tampered-verification-json",
        type=Path,
        required=True,
    )

    finalize = sub.add_parser("finalize-development")
    finalize.add_argument("--plan-json", type=Path, required=True)
    finalize.add_argument("--policy-json", type=Path, required=True)
    finalize.add_argument("--measurement-json", type=Path, required=True)
    finalize.add_argument("--output-json", type=Path, required=True)

    sub.add_parser("execute-development")
    sub.add_parser("execute-campaign")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_runtime_adapter()
        print("WP9_R063_E3_BOUNDED_ROUTE_HARNESS_STATIC=PASS")
        print("development_cases=Y01,Y02,Y03,Y04,Y05,Y06")
        print("supported_cells=A13,A11,A15,A16,A17,A18")
        print("development_seeds=9931,9932,9933,9934,9935,9936")
        print("minimal_representative_case_count=6")
        print("covered_runtime_variants=5")
        print("covered_contact_conditions=C0,C1")
        print("covered_evidence_conditions=T0,T1")
        print("modeled_c1_contact_window_s=10")
        print("post_event_analysis_horizon_s=30")
        print("one_case_per_invocation=true")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("development_runtime_execution_authorized=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    if args.command == "plan-development":
        plan = build_development_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write(args.output_json, plan)
        print("WP9_R063_E3_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + plan["case_id"])
        print("cell_id=" + plan["cell_id"])
        print("development_seed=" + str(plan["development_seed"]))
        print(
            "requested_policy_id="
            + plan["factor_context"]["policy_id"]
        )
        print(
            "expected_effective_policy_id="
            + plan["expected_effective_policy_id_for_acceptance_only"]
        )
        print("runtime_variant=" + plan["runtime_variant"])
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    if args.command == "select-policy":
        result = select_runtime_policy(_load(args.plan_json))
        _write(args.output_json, result)
        print("WP9_R063_E3_RUNTIME_POLICY_SELECTION=PASS")
        print("actual_effective_policy_id=" + result["delegated_policy_id"])
        print("selected_action=" + result["selected_action"])
        print("oracle_ground_truth_read=false")
        return 0

    if args.command == "build-p5-handoff":
        result = build_p5_handoff(
            plan=_load(args.plan_json),
            runtime_policy=_load(args.policy_json),
        )
        _write(args.output_json, result)
        print("WP9_R063_P6_TO_P5_HANDOFF=PASS")
        print("delegated_policy_id=P5")
        print("selected_action=REQUEST_VERIFIED_ROLLBACK")
        print("real_ground_contact=false")
        print("real_human_operator=false")
        return 0

    if args.command == "materialize-artifacts":
        bundle = materialize_runtime_artifacts(
            plan=_load(args.plan_json)
        )
        _write(args.event_json, bundle["event_instance"])
        args.approved.write_bytes(bundle["approved_update"])
        args.tampered.write_bytes(bundle["tampered_update"])
        _write(args.manifest_json, bundle["approved_manifest"])
        _write(
            args.tampered_verification_json,
            bundle["tampered_verification"],
        )
        print("WP9_R063_E3_RUNTIME_ARTIFACTS=PASS")
        print("approved_sha256=" + APPROVED_SHA256)
        print("tampered_sha256=" + TAMPERED_SHA256)
        return 0

    if args.command == "finalize-development":
        summary = finalize_development_observation(
            plan=_load(args.plan_json),
            runtime_policy=_load(args.policy_json),
            measurement=_load(args.measurement_json),
        )
        _write(args.output_json, summary)
        print("WP9_R063_E3_ROUTE_VALIDATION_BINDING=PASS")
        print("case_id=" + summary["case_id"])
        print("cell_id=" + summary["cell_id"])
        print(
            "outcome_matches_predeclared_expectation="
            + str(
                summary[
                    "outcome_matches_predeclared_expectation"
                ]
            ).lower()
        )
        print(
            "unexpected_scientific_outcome_retained="
            + str(
                summary[
                    "unexpected_scientific_outcome_would_be_retained_in_campaign"
                ]
            ).lower()
        )
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    if args.command == "execute-development":
        development_execution_preflight()
    campaign_execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
