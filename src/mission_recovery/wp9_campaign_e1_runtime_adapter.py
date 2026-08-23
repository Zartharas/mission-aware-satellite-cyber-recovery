from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .wp9_campaign_e1_adapter import (
    SUPPORTED_CELLS,
    _expected_gateway_treatment,
    _validate_measurement,
    validate_static_adapter,
)
from .wp9_campaign_e2_runtime_adapter import (
    DEVELOPMENT_CASES as R057_DEVELOPMENT_CASES,
)
from .wp9_campaign_e4_runtime_adapter import (
    DEVELOPMENT_CASES as R059_DEVELOPMENT_CASES,
)
from .wp9_campaign_trial_controller import build_trial_plan
from .wp9_static_contracts import evaluate_wp9_policy, load_campaign_design

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-061"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"

DEVELOPMENT_CASES: dict[str, dict[str, Any]] = {
    "X01": {"cell_id": "A05", "development_seed": 9921},
    "X02": {"cell_id": "A08", "development_seed": 9922},
    "X03": {"cell_id": "A02", "development_seed": 9923},
    "X04": {"cell_id": "A06", "development_seed": 9924},
    "X05": {"cell_id": "A09", "development_seed": 9925},
}

EXPECTED_PATHS = {
    ("P1", "P1"),
    ("P2", "P2"),
    ("P7", "P1"),
    ("P7", "P2"),
    ("P7", "P4"),
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
        raise ValueError("R-061 E1 route validation supports X01-X05 only")
    return deepcopy(DEVELOPMENT_CASES[case_id])


def _cells() -> dict[str, dict[str, Any]]:
    return {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }


def validate_static_runtime_adapter() -> dict[str, Any]:
    r060 = validate_static_adapter()
    seed_plan = _load(SEED_PLAN)
    campaign_seeds = set(seed_plan["seed_selection"]["campaign_seed_ids"])
    pilot_seeds = set(seed_plan["seed_selection"]["pilot_seed_ids"])
    b2_seeds = set(seed_plan["seed_selection"]["development_seed_ids"])
    r057_seeds = {
        int(row["development_seed"])
        for row in R057_DEVELOPMENT_CASES.values()
    }
    r059_seeds = {
        int(row["development_seed"])
        for row in R059_DEVELOPMENT_CASES.values()
    }
    route_validation_seeds = {
        int(row["development_seed"])
        for row in DEVELOPMENT_CASES.values()
    }
    cells = _cells()
    selected = [
        cells[row["cell_id"]]
        for row in DEVELOPMENT_CASES.values()
    ]

    _require(r060["decision_id"] == "R-060", "R-061 requires R-060")
    _require(
        r060["final_campaign_execution_authorized"] is False,
        "R-061 cannot begin after final campaign authorization",
    )
    _require(
        set(row["cell_id"] for row in DEVELOPMENT_CASES.values())
        <= set(SUPPORTED_CELLS),
        "R-061 contains a cell outside A01-A09",
    )
    _require(
        len(DEVELOPMENT_CASES) == len(EXPECTED_PATHS),
        "R-061 development set is not minimal for declared path coverage",
    )
    _require(
        route_validation_seeds == {9921, 9922, 9923, 9924, 9925},
        "R-061 route-validation seeds changed",
    )

    for reserved, label in (
        (campaign_seeds, "campaign"),
        (pilot_seeds, "pilot"),
        (b2_seeds, "WP9-B2"),
        (r057_seeds, "R-057"),
        (r059_seeds, "R-059"),
    ):
        _require(
            route_validation_seeds.isdisjoint(reserved),
            f"R-061 route-validation seed collides with {label} seed",
        )

    for cell in selected:
        _require(cell["event_id"] == "E1", "R-061 case is not E1")

    actual_paths = {
        (cell["policy_id"], cell["expected_effective_policy_id"])
        for cell in selected
    }
    _require(
        actual_paths == EXPECTED_PATHS,
        "R-061 development set does not cover every distinct E1 policy path exactly",
    )
    _require(
        {cell["mission_state_id"] for cell in selected}
        == {"M0", "M2", "M4"},
        "R-061 development set does not span all E1 mission states",
    )
    _require(
        {cell["evidence_condition_id"] for cell in selected}
        == {"T0", "T1"},
        "R-061 development set does not span both E1 evidence conditions",
    )
    _require(
        {cell["contact_condition_id"] for cell in selected} == {"C0"},
        "R-061 E1 contact condition changed",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R061_E1_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC_READY",
        "development_cases": deepcopy(DEVELOPMENT_CASES),
        "development_validation_only": True,
        "minimal_distinct_policy_path_set": True,
        "covered_requested_effective_paths": [
            ["P1", "P1"],
            ["P2", "P2"],
            ["P7", "P1"],
            ["P7", "P2"],
            ["P7", "P4"],
        ],
        "covered_mission_states": ["M0", "M2", "M4"],
        "covered_evidence_conditions": ["T0", "T1"],
        "post_event_analysis_horizon_s": 30,
        "matched_attacker_probe_count": 2,
        "post_response_authorized_noop_required": True,
        "unexpected_scientific_outcome_retained": True,
        "ground_truth_policy_oracle_allowed": False,
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "development_runtime_execution_authorized": False,
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
        raise ValueError("R-061 run_id contains unsupported characters")
    if COMMIT_PATTERN.fullmatch(repo_commit) is None:
        raise ValueError("R-061 repo_commit must be lowercase 40-hex")

    cell = _cells()[case["cell_id"]]
    seed = int(case["development_seed"])
    event = materialize_event(
        "E1",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-061 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == cell["expected_effective_policy_id"],
        "R-061 runtime policy treatment differs from frozen campaign design",
    )

    attacker_forwarded_count, authorized_forwarded = (
        _expected_gateway_treatment(decision["selected_action"])
    )
    _require(
        attacker_forwarded_count == 0,
        "R-061 selected development path must block matched attacker reset probes",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R061_E1_ROUTE_VALIDATION_PLAN",
        "case_id": case_id,
        "run_id": run_id,
        "repo_commit": repo_commit,
        "cell_id": case["cell_id"],
        "development_seed": seed,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": "E1",
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "expected_effective_policy_id_for_acceptance_only": (
            cell["expected_effective_policy_id"]
        ),
        "event_instance": event,
        "runtime_policy_decision": decision,
        "runtime_family": "command",
        "runtime_variant": "e1_command_gateway",
        "post_event_analysis_horizon_s": 30,
        "matched_attacker_probe_count": 2,
        "post_response_authorized_noop_required": True,
        "policy_selection_not_gated_on_event_success_required": True,
        "acceptance_only_expected_gateway_treatment": {
            "attacker_gateway_forwarded_count": attacker_forwarded_count,
            "authorized_noop_gateway_forwarded": authorized_forwarded,
        },
        "acceptance_only_expected_effects": {
            "post_enforcement_attacker_reset_marker_delta": 0,
            "authorized_noop_marker_delta": 1 if authorized_forwarded else 0,
        },
        "development_validation_only": True,
        "development_runtime_execution_authorized": False,
        "ground_truth_policy_oracle_allowed": False,
        "native_spacecraft_safe_mode_claim": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
    }


def _validated_plan_policy(plan: dict[str, Any]) -> dict[str, Any]:
    _require(plan.get("decision_id") == DECISION_ID, "not an R-061 plan")
    _require(
        plan.get("classification") == "WP9_R061_E1_ROUTE_VALIDATION_PLAN",
        "not an R-061 development-validation plan",
    )
    case = development_case(str(plan.get("case_id")))
    _require(plan.get("cell_id") == case["cell_id"], "R-061 plan cell mismatch")
    _require(
        int(plan.get("development_seed")) == int(case["development_seed"]),
        "R-061 development seed mismatch",
    )
    _require(
        plan.get("runtime_family") == "command",
        "R-061 runtime family changed",
    )
    _require(
        plan.get("runtime_variant") == "e1_command_gateway",
        "R-061 runtime variant changed",
    )
    _require(
        plan.get("development_runtime_execution_authorized") is False,
        "R-061 static plan cannot self-authorize development runtime",
    )
    _require(
        plan.get("final_campaign_execution_authorized") is False,
        "R-061 development plan cannot authorize final campaign",
    )

    cell = _cells()[case["cell_id"]]
    factor = plan.get("factor_context", {})
    _require(factor.get("event_id") == "E1", "R-061 plan event changed")
    _require(
        int(factor.get("seed")) == int(case["development_seed"]),
        "R-061 factor seed mismatch",
    )
    _require(
        factor.get("policy_id") == cell["policy_id"],
        "R-061 factor requested policy changed",
    )

    event = materialize_event(
        "E1",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=int(case["development_seed"]),
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-061 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == cell["expected_effective_policy_id"],
        "R-061 actual effective policy changed",
    )

    retained = plan.get("runtime_policy_decision", {})
    _require(
        retained.get("delegated_policy_id") == decision["delegated_policy_id"],
        "R-061 retained effective policy differs from recomputed policy",
    )
    _require(
        retained.get("selected_action") == decision["selected_action"],
        "R-061 retained selected action differs from recomputed policy",
    )
    _require(
        retained.get("oracle_ground_truth_read") is False,
        "R-061 retained policy decision read immutable ground truth",
    )
    return decision


def finalize_development_observation(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validate_static_runtime_adapter()
    decision = _validated_plan_policy(plan)
    observed = _validate_measurement(
        plan=plan,
        decision=decision,
        measurement=measurement,
    )

    attacker_delta = int(observed["attacker_delta"])
    legitimate_delta = int(observed["legitimate_delta"])
    expected_attacker_delta = 0
    expected_legitimate_delta = (
        1 if bool(observed["authorized_forwarded"]) else 0
    )
    outcome_matches = (
        attacker_delta == expected_attacker_delta
        and legitimate_delta == expected_legitimate_delta
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R061_E1_ROUTE_VALIDATION_PASS",
        "case_id": plan["case_id"],
        "cell_id": plan["cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": int(plan["development_seed"]),
        "requested_policy_id": plan["factor_context"]["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        "event_activation_reset_marker_delta": int(observed["event_delta"]),
        "post_enforcement_attacker_probe_count": int(observed["attacker_count"]),
        "post_enforcement_attacker_reset_marker_delta": attacker_delta,
        "post_response_authorized_noop_attempted": int(
            observed["legitimate_attempted"]
        ),
        "post_response_authorized_noop_marker_delta": legitimate_delta,
        "attacker_gateway_forwarded_count": int(
            observed["attacker_forwarded_count"]
        ),
        "authorized_noop_gateway_forwarded": bool(
            observed["authorized_forwarded"]
        ),
        "expected_attacker_reset_marker_delta_for_acceptance_only": (
            expected_attacker_delta
        ),
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
        "policy_selection_not_gated_on_event_success": True,
        "ground_truth_policy_oracle_allowed": False,
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
        raise ValueError("R-061 campaign plan supports A01-A09 only")
    return build_trial_plan(
        campaign_seed=campaign_seed,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=repo_commit,
    )


def development_execution_preflight() -> None:
    raise PermissionError(
        "R-061 development runtime remains blocked until the exact-SHA "
        "static/TDD gate passes and a separate explicit bounded runtime "
        "authorization is recorded"
    )


def campaign_execution_preflight() -> None:
    raise PermissionError(
        "R-061 campaign execution remains blocked: bounded E1 development "
        "route validation must close and a separate explicit final-campaign "
        "authorization contract is required"
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

    sub.add_parser("execute-development")
    sub.add_parser("execute-campaign")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        validate_static_runtime_adapter()
        print("WP9_R061_E1_SINGLE_TRIAL_ROUTE_ADAPTER_STATIC=PASS")
        print("development_cases=X01,X02,X03,X04,X05")
        print("supported_cells=A05,A08,A02,A06,A09")
        print("development_seeds=9921,9922,9923,9924,9925")
        print("distinct_requested_effective_paths=5")
        print("covered_mission_states=M0,M2,M4")
        print("covered_evidence_conditions=T0,T1")
        print("post_event_analysis_horizon_s=30")
        print("matched_attacker_probe_count=2")
        print("post_response_authorized_noop_required=true")
        print("unexpected_scientific_outcome_retained=true")
        print("one_case_per_invocation=true")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("development_runtime_execution_authorized=false")
        print("external_campaign_plan_accepted=false")
        print("ground_truth_policy_oracle_allowed=false")
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
        print("WP9_R061_E1_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + plan["case_id"])
        print("cell_id=" + plan["cell_id"])
        print("development_seed=" + str(plan["development_seed"]))
        print(
            "selected_action="
            + plan["runtime_policy_decision"]["selected_action"]
        )
        print("development_runtime_execution_authorized=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    if args.command == "finalize-development":
        summary = finalize_development_observation(
            plan=_load(args.plan_json),
            measurement=_load(args.measurement_json),
        )
        _write(args.output_json, summary)
        print("WP9_R061_E1_ROUTE_VALIDATION_OBSERVATION=PASS")
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

    if args.command == "execute-development":
        development_execution_preflight()
    campaign_execution_preflight()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
