from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .wp9_campaign_e2_adapter import (
    SUPPORTED_CELLS,
    _validate_measurement,
    validate_static_adapter,
)
from .wp9_campaign_trial_controller import build_trial_plan
from .wp9_static_contracts import evaluate_wp9_policy, load_campaign_design

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-057"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"

DEVELOPMENT_CASES: dict[str, dict[str, Any]] = {
    "V01": {"cell_id": "A19", "development_seed": 9901},
    "V02": {"cell_id": "A20", "development_seed": 9902},
    "V03": {"cell_id": "A21", "development_seed": 9903},
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
        raise ValueError("R-057 E2 route validation supports V01-V03 only")
    return deepcopy(DEVELOPMENT_CASES[case_id])


def validate_static_runtime_adapter() -> dict[str, Any]:
    r056 = validate_static_adapter()
    seed_plan = _load(SEED_PLAN)
    campaign_seeds = set(seed_plan["seed_selection"]["campaign_seed_ids"])
    pilot_seeds = set(seed_plan["seed_selection"]["pilot_seed_ids"])
    b2_seeds = set(seed_plan["seed_selection"]["development_seed_ids"])
    route_validation_seeds = {
        int(row["development_seed"])
        for row in DEVELOPMENT_CASES.values()
    }
    cells = {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }

    _require(r056["decision_id"] == "R-056", "R-057 requires R-056")
    _require(
        set(row["cell_id"] for row in DEVELOPMENT_CASES.values())
        == set(SUPPORTED_CELLS),
        "R-057 development cases do not cover A19-A21 exactly",
    )
    _require(
        route_validation_seeds == {9901, 9902, 9903},
        "R-057 route-validation seeds changed",
    )
    _require(
        route_validation_seeds.isdisjoint(campaign_seeds),
        "R-057 route-validation seed collides with campaign seed",
    )
    _require(
        route_validation_seeds.isdisjoint(pilot_seeds),
        "R-057 route-validation seed collides with pilot seed",
    )
    _require(
        route_validation_seeds.isdisjoint(b2_seeds),
        "R-057 route-validation seed collides with WP9-B2 seed",
    )
    for row in DEVELOPMENT_CASES.values():
        cell = cells[row["cell_id"]]
        _require(cell["event_id"] == "E2", "R-057 case is not E2")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R057_E2_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC_READY",
        "development_cases": deepcopy(DEVELOPMENT_CASES),
        "development_validation_only": True,
        "post_event_analysis_horizon_s": 30,
        "post_response_authorized_noop_required": True,
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_plan_constructed_internally_when_authorized": True,
        "external_campaign_plan_accepted": False,
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
        raise ValueError("R-057 run_id contains unsupported characters")
    if COMMIT_PATTERN.fullmatch(repo_commit) is None:
        raise ValueError("R-057 repo_commit must be lowercase 40-hex")

    cells = {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }
    cell = cells[case["cell_id"]]
    seed = int(case["development_seed"])
    event = materialize_event(
        "E2",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-057 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == cell["expected_effective_policy_id"],
        "R-057 runtime policy treatment differs from frozen campaign design",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R057_E2_ROUTE_VALIDATION_PLAN",
        "case_id": case_id,
        "run_id": run_id,
        "repo_commit": repo_commit,
        "cell_id": case["cell_id"],
        "development_seed": seed,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": "E2",
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "expected_effective_policy_id_for_acceptance_only": (
            cell["expected_effective_policy_id"]
        ),
        "event_instance": event,
        "runtime_policy_decision": decision,
        "runtime_family": "replay",
        "runtime_variant": "e2_replay_effect",
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
    _require(plan.get("decision_id") == DECISION_ID, "not an R-057 plan")
    _require(
        plan.get("classification") == "WP9_R057_E2_ROUTE_VALIDATION_PLAN",
        "not an R-057 development-validation plan",
    )
    case = development_case(str(plan.get("case_id")))
    _require(plan.get("cell_id") == case["cell_id"], "R-057 plan cell mismatch")
    _require(
        int(plan.get("development_seed")) == int(case["development_seed"]),
        "R-057 development seed mismatch",
    )
    decision = plan["runtime_policy_decision"]
    observed = _validate_measurement(
        plan=plan,
        decision=decision,
        measurement=measurement,
    )

    replay_delta = int(observed["replay_delta"])
    expected_delta = 1 if plan["cell_id"] == "A19" else 0
    outcome_matches = replay_delta == expected_delta

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R057_E2_ROUTE_VALIDATION_PASS",
        "case_id": plan["case_id"],
        "cell_id": plan["cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": int(plan["development_seed"]),
        "requested_policy_id": plan["factor_context"]["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        "setup_reset_marker_delta": int(observed["setup_delta"]),
        "intervening_authorized_noop_marker_delta": int(observed["intervening_delta"]),
        "post_replay_reset_marker_delta": replay_delta,
        "post_response_authorized_noop_marker_delta": int(observed["legitimate_delta"]),
        "replay_gateway_forwarded": bool(observed["replay_forwarded"]),
        "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
        "expected_replay_reset_marker_delta_for_acceptance_only": expected_delta,
        "outcome_matches_predeclared_expectation": outcome_matches,
        "unexpected_scientific_outcome_would_be_retained_in_campaign": (
            not outcome_matches
        ),
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "post_event_analysis_horizon_s": 30,
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
    """Construct, never accept, an R-054 campaign plan.

    This function is safe to call before authorization because plan materialization
    does not execute runtime or consume the seed. Runtime execution remains blocked.
    """
    if cell_id not in SUPPORTED_CELLS:
        raise ValueError("R-057 campaign plan supports A19-A21 only")
    return build_trial_plan(
        campaign_seed=campaign_seed,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=repo_commit,
    )


def campaign_execution_preflight() -> None:
    raise PermissionError(
        "R-057 campaign execution remains blocked: development route validation "
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
        result = validate_static_runtime_adapter()
        print("WP9_R057_E2_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC=PASS")
        print("development_cases=V01,V02,V03")
        print("supported_cells=A19,A20,A21")
        print("development_seeds=9901,9902,9903")
        print("post_event_analysis_horizon_s=30")
        print("one_case_per_invocation=true")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("external_campaign_plan_accepted=false")
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
        print("WP9_R057_E2_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + plan["case_id"])
        print("cell_id=" + plan["cell_id"])
        print("development_seed=" + str(plan["development_seed"]))
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    if args.command == "finalize-development":
        summary = finalize_development_observation(
            plan=_load(args.plan_json),
            measurement=_load(args.measurement_json),
        )
        _write(args.output_json, summary)
        print("WP9_R057_E2_ROUTE_VALIDATION_OBSERVATION=PASS")
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
