from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .wp9_static_contracts import (
    build_e2_replay_effect_contract,
    campaign_cells,
    evaluate_wp9_policy,
    load_campaign_design,
    load_static_contract,
    runtime_route_for_cell,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "configs" / "wp9b2_development_cases.json"
DECISION_ID = "R-046"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
EXPECTED_CASE_IDS = tuple(f"D{i:02d}" for i in range(1, 11))
WP8_PILOT_SEEDS = {101, 202, 303, 404, 505}
E2_CASE_IDS = {"D03", "D04", "D05"}


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_development_cases(path: Path | str = DEFAULT_CASES) -> dict[str, Any]:
    return _load(path)


def case_registry(data: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    data = data or load_development_cases()
    rows = {row["case_id"]: deepcopy(row) for row in data["cases"]}
    if tuple(sorted(rows)) != EXPECTED_CASE_IDS:
        raise ValueError("WP9-B2 cases must be exactly D01-D10")
    if len(rows) != len(data["cases"]):
        raise ValueError("duplicate WP9-B2 case_id")
    return rows


def validate_development_cases(data: dict[str, Any] | None = None) -> None:
    data = data or load_development_cases()
    if data["decision_id"] != DECISION_ID:
        raise ValueError("WP9-B2 case decision is not R-046")
    if data["status"] != (
        "WP9B2_BOUNDED_DEVELOPMENT_CASES_FROZEN_"
        "E2_EXECUTOR_READY_OTHER_FAMILIES_PENDING"
    ):
        raise ValueError("WP9-B2 case status changed")

    boundary = data["scientific_boundary"]
    required_true = ["development_only", "single_case_per_invocation"]
    required_false = [
        "automatic_next_case",
        "final_campaign_seed_consumption",
        "final_campaign_data_generation",
        "repetition_count_frozen",
        "final_campaign_execution_authorized",
        "expected_values_used_as_measurements",
        "ground_truth_policy_oracle_allowed",
    ]
    for key in required_true:
        if boundary[key] is not True:
            raise ValueError(f"WP9-B2 boundary must be true: {key}")
    for key in required_false:
        if boundary[key] is not False:
            raise ValueError(f"WP9-B2 boundary must be false: {key}")

    rows = case_registry(data)
    seeds = [int(rows[case_id]["development_seed"]) for case_id in EXPECTED_CASE_IDS]
    if seeds != list(range(9601, 9611)):
        raise ValueError("WP9-B2 development seeds must remain 9601-9610")
    if set(seeds) & WP8_PILOT_SEEDS:
        raise ValueError("WP9-B2 development seed collides with WP8 pilot")
    if data["development_seed_policy"]["reserved_seeds"] != seeds:
        raise ValueError("WP9-B2 reserved development seed list changed")

    design = load_campaign_design()
    cells = campaign_cells(design)
    static = load_static_contract()

    expected_ready = E2_CASE_IDS
    actual_ready = {case_id for case_id, row in rows.items() if row["executor_ready"]}
    if actual_ready != expected_ready:
        raise ValueError("only D03-D05 may be executor-ready at R-046")

    seen_cells: set[str] = set()
    for case_id in EXPECTED_CASE_IDS:
        row = rows[case_id]
        cell_id = row["campaign_cell_id"]
        if cell_id in seen_cells:
            raise ValueError("WP9-B2 cases must map to unique campaign cells")
        seen_cells.add(cell_id)
        if cell_id not in cells:
            raise ValueError(f"unknown campaign cell for {case_id}")
        route = runtime_route_for_cell(cell_id, static_contract=static)
        if row["runtime_family"] != route["runtime_family"]:
            raise ValueError(f"{case_id}: runtime family differs from R-045")
        if case_id in E2_CASE_IDS and row["runtime_variant"] != "e2_replay_effect":
            raise ValueError(f"{case_id}: E2 runtime variant changed")

    expected_map = {
        "D01": "A16", "D02": "A17",
        "D03": "A19", "D04": "A20", "D05": "A21",
        "D06": "A10", "D07": "A12", "D08": "A15",
        "D09": "A22", "D10": "A23",
    }
    actual_map = {case_id: rows[case_id]["campaign_cell_id"] for case_id in EXPECTED_CASE_IDS}
    if actual_map != expected_map:
        raise ValueError("WP9-B2 bounded case-to-cell mapping changed")

    expected_e2 = {"D03": 1, "D04": 0, "D05": 0}
    for case_id, expected_delta in expected_e2.items():
        contract = build_e2_replay_effect_contract(rows[case_id]["campaign_cell_id"], design=design)
        if contract["m01_effect_observation"]["expected_delta_for_acceptance_only"] != expected_delta:
            raise ValueError(f"{case_id}: frozen E2 acceptance discriminator changed")


def development_case(case_id: str) -> dict[str, Any]:
    validate_development_cases()
    rows = case_registry()
    if case_id not in rows:
        raise ValueError(f"unknown WP9-B2 case: {case_id}")
    return deepcopy(rows[case_id])


def build_case_plan(*, case_id: str, run_id: str, repo_commit: str) -> dict[str, Any]:
    if not run_id or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("development run_id contains unsupported characters")
    if not repo_commit or len(repo_commit) < 7:
        raise ValueError("repo commit identity is missing")

    row = development_case(case_id)
    if row["executor_ready"] is not True:
        raise PermissionError(f"WP9-B2 executor is not ready for {case_id}")

    design = load_campaign_design()
    cell = campaign_cells(design)[row["campaign_cell_id"]]
    seed = int(row["development_seed"])
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    if decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
        raise ValueError("runtime policy delegate differs from frozen WP9 design")
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("WP9-B2 policy cannot read immutable ground truth")

    plan: dict[str, Any] = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_DEVELOPMENT_RUNTIME_PLAN",
        "case_id": case_id,
        "campaign_cell_id": row["campaign_cell_id"],
        "run_id": run_id,
        "repo_commit": repo_commit,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": cell["event_id"],
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance": event,
        "runtime_policy_decision": decision,
        "expected_effective_policy_id_for_acceptance_only": cell[
            "expected_effective_policy_id"
        ],
        "runtime_family": row["runtime_family"],
        "runtime_variant": row["runtime_variant"],
        "required_discriminator": row["required_discriminator"],
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "expected_values_role": "post_observation_acceptance_only_not_metric_inputs",
        "ground_truth_policy_oracle": False,
        "automatic_next_case": False,
    }
    if case_id in E2_CASE_IDS:
        plan["e2_replay_effect_contract"] = build_e2_replay_effect_contract(
            row["campaign_cell_id"], design=design
        )
    return plan


def finalize_e2_observation(
    *,
    plan: dict[str, Any],
    setup: dict[str, Any],
    intervening: dict[str, Any],
    replay: dict[str, Any],
    gateway_decisions: list[dict[str, Any]],
    reset_before_setup: int,
    reset_after_setup: int,
    reset_before_replay: int,
    reset_after_replay: int,
    noop_before: int,
    noop_after: int,
) -> dict[str, Any]:
    case_id = plan["case_id"]
    if case_id not in E2_CASE_IDS:
        raise ValueError("E2 finalization accepts D03-D05 only")
    contract = plan["e2_replay_effect_contract"]
    expected_packet = contract["setup"]["packet_sha256"]

    if plan["factor_context"]["event_id"] != "E2":
        raise ValueError("E2 finalization received a non-E2 plan")
    truth = plan["event_instance"]["ground_truth"]
    if truth.get("replay") is not True or truth.get("command_authorized") is not False:
        raise ValueError("E2 immutable ground truth changed")
    if plan["runtime_policy_decision"]["oracle_ground_truth_read"] is not False:
        raise ValueError("runtime policy used ground truth")

    if setup.get("role") != "previously_accepted_authorized_command_before_treatment":
        raise ValueError("E2 setup role changed")
    if replay.get("role") != "byte_identical_stale_replay_after_treatment":
        raise ValueError("E2 replay role changed")
    if setup.get("packet_sha256") != expected_packet:
        raise ValueError("E2 setup packet identity changed")
    if replay.get("packet_sha256") != expected_packet:
        raise ValueError("E2 replay packet identity changed")
    if setup.get("packet_hex") != replay.get("packet_hex"):
        raise ValueError("E2 replay is not byte-identical to setup")

    setup_delta = int(reset_after_setup) - int(reset_before_setup)
    replay_delta = int(reset_after_replay) - int(reset_before_replay)
    noop_delta = int(noop_after) - int(noop_before)
    if setup_delta != 1:
        raise ValueError("authorized E2 setup reset did not complete exactly once")
    if int(reset_before_replay) != int(reset_after_setup):
        raise ValueError("RESET marker changed between setup and replay baseline")
    if noop_delta != 1:
        raise ValueError("intervening authorized NOOP did not complete exactly once")
    if intervening.get("command_class") != "sample_noop":
        raise ValueError("intervening E2 probe is not the authorized NOOP")

    if len(gateway_decisions) != 1:
        raise ValueError("E2 replay requires exactly one treatment gateway decision")
    decision = gateway_decisions[0]
    if decision.get("source_id") != "modeled_attacker":
        raise ValueError("E2 replay source identity changed")
    if decision.get("command_class") != "sample_reset_counters":
        raise ValueError("E2 replay command class changed")
    if decision.get("packet_sha256") != expected_packet:
        raise ValueError("E2 gateway observed unexpected replay packet")
    if decision.get("action") != plan["runtime_policy_decision"]["selected_action"]:
        raise ValueError("E2 gateway action differs from runtime policy")

    expected_delta = int(
        contract["m01_effect_observation"]["expected_delta_for_acceptance_only"]
    )
    expected_forwarded = bool(
        contract["m01_effect_observation"]["expected_forwarded_for_acceptance_only"]
    )
    if replay_delta != expected_delta:
        raise ValueError(
            f"observed E2 replay effect delta {replay_delta} != acceptance {expected_delta}"
        )
    if bool(decision.get("forwarded")) != expected_forwarded:
        raise ValueError("observed E2 gateway forwarding differs from acceptance contract")

    unauthorized_effect_completed = replay_delta == 1
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E2_DEVELOPMENT_RUNTIME_PASS",
        "case_id": case_id,
        "campaign_cell_id": plan["campaign_cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": plan["factor_context"]["seed"],
        "requested_policy_id": plan["factor_context"]["policy_id"],
        "actual_effective_policy_id": plan["runtime_policy_decision"]["delegated_policy_id"],
        "selected_action": plan["runtime_policy_decision"]["selected_action"],
        "setup_reset_marker_delta": setup_delta,
        "intervening_authorized_noop_delta": noop_delta,
        "post_replay_reset_marker_delta": replay_delta,
        "replay_gateway_forwarded": bool(decision["forwarded"]),
        "replayed_packet_byte_identical": True,
        "unauthorized_effect_completed_observed": unauthorized_effect_completed,
        "m01_observation_source": "observed_post_replay_cfs_reset_marker_delta",
        "setup_marker_excluded_from_m01": True,
        "packet_send_success_used_as_m01": False,
        "noop_receipt_used_as_m01": False,
        "oracle_ground_truth_read": False,
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "final_effect_size_claim": False,
        "campaign_execution_authorized": False,
        "automatic_next_case": False,
        "acceptance_status": "PASS",
    }


def _write(path: str | Path, value: Any) -> None:
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    plan = sub.add_parser("plan")
    plan.add_argument("--case-id", required=True)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--repo-commit", required=True)
    plan.add_argument("--output-plan-json", required=True)
    plan.add_argument("--output-event-json", required=True)
    plan.add_argument("--output-policy-json", required=True)
    plan.add_argument("--output-e2-contract-json")

    fin = sub.add_parser("finalize-e2")
    fin.add_argument("--plan-json", required=True)
    fin.add_argument("--setup-json", required=True)
    fin.add_argument("--intervening-json", required=True)
    fin.add_argument("--replay-json", required=True)
    fin.add_argument("--gateway-decisions-jsonl", required=True)
    fin.add_argument("--reset-before-setup", type=int, required=True)
    fin.add_argument("--reset-after-setup", type=int, required=True)
    fin.add_argument("--reset-before-replay", type=int, required=True)
    fin.add_argument("--reset-after-replay", type=int, required=True)
    fin.add_argument("--noop-before", type=int, required=True)
    fin.add_argument("--noop-after", type=int, required=True)
    fin.add_argument("--output-summary-json", required=True)

    args = parser.parse_args()
    if args.command == "validate":
        validate_development_cases()
        print("WP9B2_DEVELOPMENT_CASES=PASS")
        return 0

    if args.command == "plan":
        value = build_case_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write(args.output_plan_json, value)
        _write(args.output_event_json, value["event_instance"])
        _write(args.output_policy_json, value["runtime_policy_decision"])
        if args.output_e2_contract_json:
            if "e2_replay_effect_contract" not in value:
                raise ValueError("requested E2 contract for non-E2 case")
            _write(args.output_e2_contract_json, value["e2_replay_effect_contract"])
        print("WP9B2_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + value["case_id"])
        print("campaign_cell_id=" + value["campaign_cell_id"])
        print("development_seed=" + str(value["factor_context"]["seed"]))
        print("runtime_family=" + value["runtime_family"])
        print("runtime_variant=" + value["runtime_variant"])
        return 0

    value = finalize_e2_observation(
        plan=_load(args.plan_json),
        setup=_load(args.setup_json),
        intervening=_load(args.intervening_json),
        replay=_load(args.replay_json),
        gateway_decisions=_read_jsonl(args.gateway_decisions_jsonl),
        reset_before_setup=args.reset_before_setup,
        reset_after_setup=args.reset_after_setup,
        reset_before_replay=args.reset_before_replay,
        reset_after_replay=args.reset_after_replay,
        noop_before=args.noop_before,
        noop_after=args.noop_after,
    )
    _write(args.output_summary_json, value)
    print("WP9B2_E2_DEVELOPMENT_ACCEPTANCE=PASS")
    print("case_id=" + value["case_id"])
    print("post_replay_reset_marker_delta=" + str(value["post_replay_reset_marker_delta"]))
    print("unauthorized_effect_completed_observed=" + str(value["unauthorized_effect_completed_observed"]).lower())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
