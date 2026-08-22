from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .wp9_campaign_e4_adapter import (
    SUPPORTED_CELLS,
    _validate_measurement,
    validate_static_adapter,
)
from .wp9_campaign_e2_runtime_adapter import DEVELOPMENT_CASES as R057_DEVELOPMENT_CASES
from .wp9_campaign_trial_controller import build_trial_plan
from .wp9_static_contracts import evaluate_wp9_policy, load_campaign_design

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-059"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"

DEVELOPMENT_CASES: dict[str, dict[str, Any]] = {
    "W01": {"cell_id": "A22", "development_seed": 9911},
    "W02": {"cell_id": "A23", "development_seed": 9912},
    "W03": {"cell_id": "A24", "development_seed": 9913},
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


def development_case(case_id: str) -> dict[str, Any]:
    if case_id not in DEVELOPMENT_CASES:
        raise ValueError("R-059 E4 route validation supports W01-W03 only")
    return deepcopy(DEVELOPMENT_CASES[case_id])


def validate_static_runtime_adapter() -> dict[str, Any]:
    r058 = validate_static_adapter()
    seed_plan = _load(SEED_PLAN)
    campaign_seeds = set(seed_plan["seed_selection"]["campaign_seed_ids"])
    pilot_seeds = set(seed_plan["seed_selection"]["pilot_seed_ids"])
    b2_seeds = set(seed_plan["seed_selection"]["development_seed_ids"])
    r057_seeds = {
        int(row["development_seed"])
        for row in R057_DEVELOPMENT_CASES.values()
    }
    route_validation_seeds = {
        int(row["development_seed"])
        for row in DEVELOPMENT_CASES.values()
    }
    cells = {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }

    _require(r058["decision_id"] == "R-058", "R-059 requires R-058")
    _require(
        set(row["cell_id"] for row in DEVELOPMENT_CASES.values())
        == set(SUPPORTED_CELLS),
        "R-059 development cases do not cover A22-A24 exactly",
    )
    _require(
        route_validation_seeds == {9911, 9912, 9913},
        "R-059 route-validation seeds changed",
    )
    for reserved, label in (
        (campaign_seeds, "campaign"),
        (pilot_seeds, "pilot"),
        (b2_seeds, "WP9-B2"),
        (r057_seeds, "R-057"),
    ):
        _require(
            route_validation_seeds.isdisjoint(reserved),
            f"R-059 route-validation seed collides with {label} seed",
        )

    for row in DEVELOPMENT_CASES.values():
        cell = cells[row["cell_id"]]
        _require(cell["event_id"] == "E4", "R-059 case is not E4")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R059_E4_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC_READY",
        "development_cases": deepcopy(DEVELOPMENT_CASES),
        "development_validation_only": True,
        "post_event_analysis_horizon_s": 30,
        "event_activation_requires_truth_visible_separation": True,
        "post_response_authorized_noop_required": True,
        "unexpected_scientific_outcome_retained": True,
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_plan_constructed_internally_when_authorized": True,
        "external_campaign_plan_accepted": False,
        "native_spacecraft_safe_mode_claim": False,
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
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("R-059 run_id contains unsupported characters")
    if COMMIT_PATTERN.fullmatch(repo_commit) is None:
        raise ValueError("R-059 repo_commit must be lowercase 40-hex")

    cells = {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }
    cell = cells[case["cell_id"]]
    seed = int(case["development_seed"])
    event = materialize_event(
        "E4",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    _require(
        event["ground_truth"]["telemetry_truth_available"] is True,
        "R-059 immutable telemetry truth changed",
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-059 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == cell["expected_effective_policy_id"],
        "R-059 runtime policy treatment differs from frozen campaign design",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R059_E4_ROUTE_VALIDATION_PLAN",
        "case_id": case_id,
        "run_id": run_id,
        "repo_commit": repo_commit,
        "cell_id": case["cell_id"],
        "development_seed": seed,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": "E4",
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "expected_effective_policy_id_for_acceptance_only": (
            cell["expected_effective_policy_id"]
        ),
        "event_instance": event,
        "runtime_policy_decision": decision,
        "runtime_family": "observability",
        "runtime_variant": "e4_observability",
        "post_event_analysis_horizon_s": 30,
        "development_validation_only": True,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
    }


def finalize_development_observation(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validate_static_runtime_adapter()
    _require(plan.get("decision_id") == DECISION_ID, "not an R-059 plan")
    _require(
        plan.get("classification") == "WP9_R059_E4_ROUTE_VALIDATION_PLAN",
        "not an R-059 development-validation plan",
    )
    case = development_case(str(plan.get("case_id")))
    _require(plan.get("cell_id") == case["cell_id"], "R-059 plan cell mismatch")
    _require(
        int(plan.get("development_seed")) == int(case["development_seed"]),
        "R-059 development seed mismatch",
    )

    decision = plan["runtime_policy_decision"]
    observed = _validate_measurement(
        plan=plan,
        decision=decision,
        measurement=measurement,
    )

    post_visible = int(observed["post_visible_delta"])
    legitimate_delta = int(observed["legitimate_delta"])
    expected_post_visible = 0
    expected_legitimate_delta = (
        1 if decision["selected_action"] == "OBSERVE_ONLY" else 0
    )
    outcome_matches = (
        post_visible == expected_post_visible
        and legitimate_delta == expected_legitimate_delta
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R059_E4_ROUTE_VALIDATION_PASS",
        "case_id": plan["case_id"],
        "cell_id": plan["cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": int(plan["development_seed"]),
        "requested_policy_id": plan["factor_context"]["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        "event_truth_high_value_delta": int(observed["event_truth_delta"]),
        "event_policy_visible_high_value_delta": int(observed["event_visible_delta"]),
        "post_response_truth_high_value_delta": int(observed["post_truth_delta"]),
        "post_response_policy_visible_high_value_delta": post_visible,
        "telemetry_restored_observed": post_visible == 1,
        "post_response_authorized_noop_marker_delta": legitimate_delta,
        "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
        "expected_post_response_policy_visible_delta_for_acceptance_only": 0,
        "expected_authorized_noop_marker_delta_for_acceptance_only": (
            expected_legitimate_delta
        ),
        "outcome_matches_predeclared_expectation": outcome_matches,
        "unexpected_scientific_outcome_would_be_retained_in_campaign": (
            not outcome_matches
        ),
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "post_event_analysis_horizon_s": 30,
        "trusted_recovery_fabricated": False,
        "native_spacecraft_safe_mode_claim": False,
        "development_validation_only": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "acceptance_status": "PASS",
    }


def construct_authorized_campaign_plan(
    *,
    campaign_seed: int,
    cell_id: str,
    run_id: str,
    repo_commit: str,
) -> dict[str, Any]:
    if cell_id not in SUPPORTED_CELLS:
        raise ValueError("R-059 campaign plan supports A22-A24 only")
    return build_trial_plan(
        campaign_seed=campaign_seed,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=repo_commit,
    )


def campaign_execution_preflight() -> None:
    raise PermissionError(
        "R-059 campaign execution remains blocked: development route validation "
        "must pass and a separate explicit final-campaign authorization contract "
        "is required"
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

    fin = sub.add_parser("finalize-development")
    fin.add_argument("--plan-json", type=Path, required=True)
    fin.add_argument("--measurement-json", type=Path, required=True)
    fin.add_argument("--output-json", type=Path, required=True)

    sub.add_parser("execute-campaign")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        validate_static_runtime_adapter()
        print("WP9_R059_E4_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC=PASS")
        print("development_cases=W01,W02,W03")
        print("supported_cells=A22,A23,A24")
        print("development_seeds=9911,9912,9913")
        print("post_event_analysis_horizon_s=30")
        print("one_case_per_invocation=true")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("external_campaign_plan_accepted=false")
        print("native_spacecraft_safe_mode_claim=false")
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
        print("WP9_R059_E4_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + plan["case_id"])
        print("cell_id=" + plan["cell_id"])
        print("development_seed=" + str(plan["development_seed"]))
        print("selected_action=" + plan["runtime_policy_decision"]["selected_action"])
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    if args.command == "finalize-development":
        summary = finalize_development_observation(
            plan=_load(args.plan_json),
            measurement=_load(args.measurement_json),
        )
        _write(args.output_json, summary)
        print("WP9_R059_E4_ROUTE_VALIDATION_OBSERVATION=PASS")
        print("case_id=" + summary["case_id"])
        print("cell_id=" + summary["cell_id"])
        print("development_seed=" + str(summary["development_seed"]))
        print(
            "outcome_matches_predeclared_expectation="
            + str(summary["outcome_matches_predeclared_expectation"]).lower()
        )
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    campaign_execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
