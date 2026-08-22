from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .wp9_static_contracts import build_static_matrix, campaign_cells

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-054"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

CAMPAIGN_DESIGN = ROOT / "configs" / "wp9_campaign_design.json"
REPETITION_FREEZE = ROOT / "configs" / "wp9c_repetition_freeze.json"
TIMING_FREEZE = ROOT / "configs" / "wp9_precampaign_timing_freeze.json"
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _seed_blocks(seed_plan: dict[str, Any]) -> dict[int, dict[str, Any]]:
    blocks = {int(row["campaign_seed"]): row for row in seed_plan["blocks"]}
    if len(blocks) != 30:
        raise ValueError("R-054 requires exactly 30 frozen campaign seed blocks")
    return blocks


def validate_static_controller() -> dict[str, Any]:
    design = _load(CAMPAIGN_DESIGN)
    repetition = _load(REPETITION_FREEZE)
    timing = _load(TIMING_FREEZE)
    seed_plan = _load(SEED_PLAN)
    cells = campaign_cells(design)
    matrix = build_static_matrix(design)
    matrix_by_cell = {row["cell_id"]: row for row in matrix["rows"]}

    _require(design["decision_id"] == "R-044", "campaign design decision changed")
    _require(len(cells) == 24, "campaign cell count changed")
    _require(
        repetition["reviewed_result"]["selected_valid_repetitions_per_cell"] == 30,
        "R-051 repetition freeze changed",
    )
    _require(
        repetition["reviewed_result"]["selected_total_valid_executions"] == 720,
        "R-051 total valid execution count changed",
    )

    frozen_timing = timing["frozen_timing"]
    _require(
        frozen_timing["c1_semantics"]["modeled_contact_window_s"] == 10,
        "R-052 C1 contact window changed",
    )
    _require(
        frozen_timing["e3_common_post_event_analysis_horizon_s"] == 30,
        "R-052 E3 analysis horizon changed",
    )
    _require(
        timing["campaign_readiness_effect"]["final_campaign_execution_authorized"]
        is False,
        "R-052 cannot authorize campaign execution",
    )

    blocking = seed_plan["blocking_contract"]
    _require(blocking["valid_repetitions_per_cell"] == 30, "R-053 repetition count changed")
    _require(blocking["frozen_cell_count"] == 24, "R-053 cell count changed")
    _require(blocking["planned_valid_executions"] == 720, "R-053 total changed")
    _require(blocking["same_seed_runs_all_frozen_cells"] is True, "seed blocking changed")
    _require(blocking["randomize_cell_order_within_seed_block"] is True, "order rule changed")
    _require(blocking["clean_snapshot_before_each_trial"] is True, "snapshot rule changed")

    seeds = seed_plan["seed_selection"]["campaign_seed_ids"]
    _require(seeds == list(range(10001, 10031)), "campaign seed IDs changed")
    _require(seed_plan["seed_selection"]["seed_ids_consumed"] is False, "seed plan already consumed")

    attempt = seed_plan["attempt_semantics"]
    _require(attempt["invalid_attempt_counts_toward_720"] is False, "invalid-run counting changed")
    _require(attempt["invalid_attempt_reuses_same_campaign_seed"] is True, "invalid seed rule changed")
    _require(attempt["invalid_attempt_reuses_same_cell_id"] is True, "invalid cell rule changed")
    _require(attempt["invalid_attempt_requires_new_run_id"] is True, "invalid run-id rule changed")
    _require(attempt["automatic_retry_allowed"] is False, "automatic retry became allowed")
    _require(attempt["automatic_next_case_allowed"] is False, "automatic next case became allowed")

    boundary = seed_plan["scientific_boundary"]
    _require(boundary["campaign_seed_plan_frozen"] is True, "seed plan not frozen")
    _require(boundary["campaign_seed_consumed"] is False, "campaign seed already consumed")
    _require(boundary["campaign_data_generated"] is False, "campaign data already generated")
    _require(boundary["campaign_runtime_execution_performed"] is False, "campaign runtime already performed")
    _require(boundary["final_campaign_execution_authorized"] is False, "campaign unexpectedly authorized")

    blocks = _seed_blocks(seed_plan)
    expected_cells = set(cells)
    for seed in seeds:
        block = blocks[seed]
        _require(len(block["cell_order"]) == 24, f"seed {seed}: cell-order length changed")
        _require(set(block["cell_order"]) == expected_cells, f"seed {seed}: cell-order membership changed")

    _require(set(matrix_by_cell) == expected_cells, "R-045/B3 routing does not cover A01-A24")
    for cell_id, row in matrix_by_cell.items():
        _require(row["runtime_execution_performed"] is False, f"{cell_id}: static matrix executed runtime")
        _require(row["campaign_seed_consumed"] is False, f"{cell_id}: static matrix consumed campaign seed")
        _require(row["campaign_data"] is False, f"{cell_id}: static matrix generated campaign data")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R054_SINGLE_TRIAL_CONTROLLER_STATIC_READY",
        "campaign_cell_count": 24,
        "campaign_seed_block_count": 30,
        "valid_repetitions_per_cell": 30,
        "planned_valid_executions": 720,
        "c1_contact_window_s": 10,
        "e3_post_event_analysis_horizon_s": 30,
        "route_variants": sorted({row["runtime_variant"] for row in matrix["rows"]}),
        "campaign_safe_route_adapters_ready": False,
        "authorization_contract_present": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def build_trial_plan(
    *,
    campaign_seed: int,
    cell_id: str,
    run_id: str,
    repo_commit: str,
) -> dict[str, Any]:
    validate_static_controller()
    design = _load(CAMPAIGN_DESIGN)
    timing = _load(TIMING_FREEZE)["frozen_timing"]
    seed_plan = _load(SEED_PLAN)
    blocks = _seed_blocks(seed_plan)
    cells = campaign_cells(design)
    matrix = {row["cell_id"]: row for row in build_static_matrix(design)["rows"]}

    seed = int(campaign_seed)
    if seed not in blocks:
        raise ValueError("campaign seed is not in frozen R-053 seed plan")
    if cell_id not in cells:
        raise ValueError("cell_id is not in frozen A01-A24 campaign design")
    if not run_id or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("run_id must contain only A-Z a-z 0-9 _ . -")
    if COMMIT_PATTERN.fullmatch(repo_commit) is None:
        raise ValueError("repo_commit must be a lowercase 40-hex commit SHA")

    block = blocks[seed]
    order = block["cell_order"]
    order_index = order.index(cell_id) + 1
    cell = cells[cell_id]
    route = matrix[cell_id]

    event_id = cell["event_id"]
    contact_id = cell["contact_condition_id"]
    policy_id = cell["policy_id"]
    e3_horizon = timing["e3_common_post_event_analysis_horizon_s"] if event_id == "E3" else None
    c1_window = timing["c1_semantics"]["modeled_contact_window_s"] if contact_id == "C1" else None
    ground_authorization_release = c1_window if (policy_id == "P6" and contact_id == "C1") else (0 if policy_id == "P6" else None)

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R054_FINAL_CAMPAIGN_SINGLE_TRIAL_PLAN",
        "run_id": run_id,
        "repo_commit": repo_commit,
        "block_index": int(block["block_index"]),
        "campaign_seed": seed,
        "cell_order_index": order_index,
        "cell_id": cell_id,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": event_id,
            "policy_id": policy_id,
            "contact_condition_id": contact_id,
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "expected_effective_policy_id_for_acceptance_only": cell["expected_effective_policy_id"],
        "runtime_family": route["runtime_family"],
        "runtime_variant": route["runtime_variant"],
        "timing_contract": {
            "analysis_time_origin": timing["analysis_time_origin"],
            "e3_post_event_analysis_horizon_s": e3_horizon,
            "modeled_c1_contact_window_s": c1_window,
            "p6_ground_authorization_release_after_event_s": ground_authorization_release,
            "early_absorbing_trusted_recovery_allowed": bool(event_id == "E3" and timing["early_absorbing_trusted_recovery_allowed"]),
            "unrecovered_e3_right_censored_at_horizon": bool(event_id == "E3" and timing["unrecovered_e3_run_right_censored_at_horizon"]),
        },
        "execution_boundary": {
            "clean_snapshot_required_before_trial": True,
            "campaign_safe_route_adapter_required": True,
            "explicit_authorization_contract_required": True,
            "automatic_retry_allowed": False,
            "automatic_next_case_allowed": False,
            "invalid_attempt_reuses_same_seed": True,
            "invalid_attempt_reuses_same_cell_id": True,
            "invalid_attempt_requires_new_run_id": True,
            "campaign_seed_consumed": False,
            "campaign_data_generated": False,
            "runtime_execution_performed": False,
            "final_campaign_execution_authorized": False,
        },
        "expected_values_role": "post_observation_acceptance_only_not_metric_inputs",
        "ground_truth_policy_oracle_allowed": False,
    }


def execution_preflight(*, plan: dict[str, Any]) -> None:
    if plan.get("decision_id") != DECISION_ID:
        raise ValueError("not an R-054 single-trial plan")
    raise PermissionError(
        "final campaign execution remains blocked: campaign-safe route adapters "
        "and a separate explicit authorization contract are required"
    )


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    plan_parser = sub.add_parser("plan-trial")
    plan_parser.add_argument("--campaign-seed", type=int, required=True)
    plan_parser.add_argument("--cell-id", required=True)
    plan_parser.add_argument("--run-id", required=True)
    plan_parser.add_argument("--repo-commit", required=True)
    plan_parser.add_argument("--output-json", type=Path, required=True)

    execute_parser = sub.add_parser("execute-trial")
    execute_parser.add_argument("--plan-json", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_controller()
        print("WP9_R054_SINGLE_TRIAL_CONTROLLER_STATIC=PASS")
        for key in (
            "campaign_cell_count",
            "campaign_seed_block_count",
            "valid_repetitions_per_cell",
            "planned_valid_executions",
            "c1_contact_window_s",
            "e3_post_event_analysis_horizon_s",
            "campaign_safe_route_adapters_ready",
            "authorization_contract_present",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            print(f"{key}={str(result[key]).lower() if isinstance(result[key], bool) else result[key]}")
        return 0

    if args.command == "plan-trial":
        plan = build_trial_plan(
            campaign_seed=args.campaign_seed,
            cell_id=args.cell_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write_json(args.output_json, plan)
        print("WP9_R054_SINGLE_TRIAL_PLAN=PASS")
        print(f"campaign_seed={plan['campaign_seed']}")
        print(f"cell_id={plan['cell_id']}")
        print(f"cell_order_index={plan['cell_order_index']}")
        print(f"runtime_variant={plan['runtime_variant']}")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("runtime_execution_performed=false")
        print("final_campaign_execution_authorized=false")
        return 0

    plan = _load(args.plan_json)
    execution_preflight(plan=plan)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
