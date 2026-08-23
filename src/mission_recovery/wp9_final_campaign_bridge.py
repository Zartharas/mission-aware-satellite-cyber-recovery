from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from .wp9_campaign_e1_adapter import (
    _validate_plan as _validate_e1_plan,
    validate_static_adapter as validate_e1_observation_adapter,
)
from .wp9_campaign_e1_runtime_adapter import (
    validate_static_runtime_adapter as validate_e1_runtime_adapter,
)
from .wp9_campaign_e2_adapter import (
    _validate_plan as _validate_e2_plan,
    validate_static_adapter as validate_e2_observation_adapter,
)
from .wp9_campaign_e2_runtime_adapter import (
    validate_static_runtime_adapter as validate_e2_runtime_adapter,
)
from .wp9_campaign_e3_adapter import (
    _validate_plan as _validate_e3_plan,
    validate_static_adapter as validate_e3_observation_adapter,
)
from .wp9_campaign_e3_runtime_adapter import (
    validate_static_runtime_adapter as validate_e3_runtime_adapter,
)
from .wp9_campaign_e4_adapter import (
    _validate_plan as _validate_e4_plan,
    validate_static_adapter as validate_e4_observation_adapter,
)
from .wp9_campaign_e4_runtime_adapter import (
    validate_static_runtime_adapter as validate_e4_runtime_adapter,
)
from .wp9_campaign_trial_controller import (
    build_trial_plan,
    validate_static_controller,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-064"
SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"

AUTHORIZATION_REQUEST_CLASSIFICATION = (
    "WP9_R064_FINAL_CAMPAIGN_SINGLE_TRIAL_AUTHORIZATION_REQUEST"
)
AUTHORIZATION_CLASSIFICATION = (
    "WP9_R064_FINAL_CAMPAIGN_SINGLE_TRIAL_AUTHORIZATION"
)

ROUTE_CONTRACTS: dict[str, dict[str, Any]] = {
    "E1": {
        "cells": tuple(f"A{i:02d}" for i in range(1, 10)),
        "runtime_family": "command",
        "campaign_observation_adapter_decision_id": "R-060",
        "development_runtime_validation_decision_id": "R-061",
    },
    "E2": {
        "cells": ("A19", "A20", "A21"),
        "runtime_family": "replay",
        "campaign_observation_adapter_decision_id": "R-056",
        "development_runtime_validation_decision_id": "R-057",
    },
    "E3": {
        "cells": tuple(f"A{i:02d}" for i in range(10, 19)),
        "runtime_family": "recovery",
        "campaign_observation_adapter_decision_id": "R-062",
        "development_runtime_validation_decision_id": "R-063",
    },
    "E4": {
        "cells": ("A22", "A23", "A24"),
        "runtime_family": "observability",
        "campaign_observation_adapter_decision_id": "R-058",
        "development_runtime_validation_decision_id": "R-059",
    },
}

_PLAN_VALIDATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "E1": _validate_e1_plan,
    "E2": _validate_e2_plan,
    "E3": _validate_e3_plan,
    "E4": _validate_e4_plan,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _canonical_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def frozen_campaign_sequence() -> list[dict[str, Any]]:
    seed_plan = _load(SEED_PLAN)
    blocks = sorted(
        seed_plan["blocks"],
        key=lambda row: int(row["block_index"]),
    )
    sequence: list[dict[str, Any]] = []
    global_index = 0

    _require(len(blocks) == 30, "R-064 requires 30 frozen seed blocks")

    for expected_block_index, block in enumerate(blocks, start=1):
        block_index = int(block["block_index"])
        campaign_seed = int(block["campaign_seed"])
        order = list(block["cell_order"])

        _require(
            block_index == expected_block_index,
            "R-064 seed block ordering changed",
        )
        _require(
            campaign_seed == 10000 + expected_block_index,
            "R-064 campaign seed ordering changed",
        )
        _require(
            len(order) == 24 and len(set(order)) == 24,
            "R-064 frozen cell order is not a 24-cell permutation",
        )

        for cell_order_index, cell_id in enumerate(order, start=1):
            global_index += 1
            sequence.append(
                {
                    "global_order_index": global_index,
                    "block_index": block_index,
                    "campaign_seed": campaign_seed,
                    "cell_order_index": cell_order_index,
                    "cell_id": cell_id,
                }
            )

    _require(
        len(sequence) == 720,
        "R-064 frozen campaign sequence must contain 720 valid positions",
    )
    return sequence


def _position_identity(row: dict[str, Any]) -> tuple[int, int, str]:
    try:
        campaign_seed = int(row["campaign_seed"])
        cell_order_index = int(row["cell_order_index"])
        cell_id = str(row["cell_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("completed-valid position identity is incomplete") from exc
    return campaign_seed, cell_order_index, cell_id


def next_required_trial(
    completed_valid_positions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    sequence = frozen_campaign_sequence()
    completed = list(completed_valid_positions)

    _require(
        len(completed) <= len(sequence),
        "completed-valid sequence exceeds frozen campaign length",
    )

    for index, observed in enumerate(completed):
        expected = sequence[index]
        _require(
            _position_identity(observed) == _position_identity(expected),
            "completed-valid positions must be the exact frozen prefix",
        )

    if len(completed) == len(sequence):
        return None
    return copy.deepcopy(sequence[len(completed)])


def _event_for_cell(cell_id: str) -> str:
    matches = [
        event_id
        for event_id, contract in ROUTE_CONTRACTS.items()
        if cell_id in contract["cells"]
    ]
    _require(len(matches) == 1, f"R-064 cell route is not unique: {cell_id}")
    return matches[0]


def route_trial_plan(plan: dict[str, Any]) -> dict[str, Any]:
    _require(plan.get("decision_id") == "R-054", "R-064 requires R-054 trial plan")
    cell_id = str(plan.get("cell_id"))
    event_id = _event_for_cell(cell_id)
    factor = plan.get("factor_context", {})
    contract = ROUTE_CONTRACTS[event_id]

    _require(
        factor.get("event_id") == event_id,
        f"R-064 event/cell route mismatch: {cell_id}",
    )
    _require(
        plan.get("runtime_family") == contract["runtime_family"],
        f"R-064 runtime family changed: {cell_id}",
    )

    _PLAN_VALIDATORS[event_id](plan)

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R064_FINAL_CAMPAIGN_ROUTE_DESCRIPTOR",
        "cell_id": cell_id,
        "event_id": event_id,
        "runtime_family": plan["runtime_family"],
        "runtime_variant": plan["runtime_variant"],
        "campaign_observation_adapter_decision_id": contract[
            "campaign_observation_adapter_decision_id"
        ],
        "development_runtime_validation_decision_id": contract[
            "development_runtime_validation_decision_id"
        ],
        "expected_values_role": plan["expected_values_role"],
        "ground_truth_policy_oracle_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def _validate_adapter_result(
    result: dict[str, Any],
    *,
    decision_id: str,
) -> None:
    _require(
        result.get("decision_id") == decision_id,
        f"R-064 dependency changed: expected {decision_id}",
    )
    _require(
        result.get("final_campaign_execution_authorized") is False,
        f"R-064 dependency {decision_id} unexpectedly authorizes final campaign",
    )
    _require(
        result.get("campaign_seed_consumed") is False,
        f"R-064 dependency {decision_id} consumed campaign seed",
    )
    _require(
        result.get("campaign_data_generated") is False,
        f"R-064 dependency {decision_id} generated campaign data",
    )


def validate_static_bridge() -> dict[str, Any]:
    controller = validate_static_controller()
    _require(controller["decision_id"] == "R-054", "R-064 requires R-054")
    _require(
        controller["final_campaign_execution_authorized"] is False,
        "R-064 static/TDD gate cannot follow final campaign authorization",
    )

    observation_results = {
        "E1": validate_e1_observation_adapter(),
        "E2": validate_e2_observation_adapter(),
        "E3": validate_e3_observation_adapter(),
        "E4": validate_e4_observation_adapter(),
    }
    runtime_results = {
        "E1": validate_e1_runtime_adapter(),
        "E2": validate_e2_runtime_adapter(),
        "E3": validate_e3_runtime_adapter(),
        "E4": validate_e4_runtime_adapter(),
    }

    for event_id, contract in ROUTE_CONTRACTS.items():
        _validate_adapter_result(
            observation_results[event_id],
            decision_id=contract["campaign_observation_adapter_decision_id"],
        )
        _validate_adapter_result(
            runtime_results[event_id],
            decision_id=contract["development_runtime_validation_decision_id"],
        )

    routed_cells: set[str] = set()
    variants: set[str] = set()
    for cell_number in range(1, 25):
        cell_id = f"A{cell_number:02d}"
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"wp9-r064-static-{cell_id.lower()}",
            repo_commit="a" * 40,
        )
        route = route_trial_plan(plan)
        routed_cells.add(route["cell_id"])
        variants.add(route["runtime_variant"])

    _require(
        routed_cells == {f"A{i:02d}" for i in range(1, 25)},
        "R-064 route bridge does not cover A01-A24 exactly",
    )
    _require(
        len(variants) == 8,
        "R-064 runtime variant coverage changed",
    )

    sequence = frozen_campaign_sequence()
    _require(sequence[0]["campaign_seed"] == 10001, "R-064 first seed changed")
    _require(sequence[-1]["campaign_seed"] == 10030, "R-064 last seed changed")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R064_FINAL_CAMPAIGN_BRIDGE_STATIC_READY",
        "campaign_cell_count": 24,
        "campaign_seed_block_count": 30,
        "valid_repetitions_per_cell": 30,
        "planned_valid_executions": 720,
        "campaign_route_family_count": len(ROUTE_CONTRACTS),
        "campaign_runtime_variant_count": len(variants),
        "campaign_observation_adapters_ready": True,
        "validated_runtime_mechanism_evidence_present": True,
        "authorization_contract_present": True,
        "frozen_order_enforced": True,
        "one_trial_per_invocation": True,
        "executor_interface_injected_per_trial": True,
        "production_runtime_executor_bound": False,
        "bounded_non_campaign_seed_runtime_validation_required": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def build_authorization_request(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_bridge()
    route = route_trial_plan(plan)
    boundary = plan.get("execution_boundary", {})

    _require(
        boundary.get("automatic_retry_allowed") is False,
        "R-064 plan automatic retry boundary changed",
    )
    _require(
        boundary.get("automatic_next_case_allowed") is False,
        "R-064 plan automatic next boundary changed",
    )
    _require(
        boundary.get("final_campaign_execution_authorized") is False,
        "R-064 request must originate from unauthorized R-054 plan",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": AUTHORIZATION_REQUEST_CLASSIFICATION,
        "authorization_scope": "single_frozen_trial",
        "run_id": plan["run_id"],
        "authorized_repo_sha": plan["repo_commit"],
        "campaign_seed": int(plan["campaign_seed"]),
        "block_index": int(plan["block_index"]),
        "cell_order_index": int(plan["cell_order_index"]),
        "cell_id": plan["cell_id"],
        "plan_sha256": _canonical_sha256(plan),
        "route_binding": {
            "event_id": route["event_id"],
            "runtime_family": route["runtime_family"],
            "runtime_variant": route["runtime_variant"],
            "campaign_observation_adapter_decision_id": route[
                "campaign_observation_adapter_decision_id"
            ],
            "development_runtime_validation_decision_id": route[
                "development_runtime_validation_decision_id"
            ],
        },
        "single_trial_runtime_authorized": False,
        "campaign_wide_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def validate_trial_authorization(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    current_repo_sha: str,
) -> dict[str, Any]:
    route = route_trial_plan(plan)

    _require(
        authorization.get("decision_id") == DECISION_ID,
        "R-064 authorization decision changed",
    )
    _require(
        authorization.get("classification") == AUTHORIZATION_CLASSIFICATION,
        "R-064 authorization classification changed",
    )
    _require(
        authorization.get("authorization_scope") == "single_frozen_trial",
        "R-064 authorization scope must be one frozen trial",
    )
    if authorization.get("single_trial_runtime_authorized") is not True:
        raise PermissionError("R-064 single-trial runtime authorization was not granted")
    _require(
        authorization.get("campaign_wide_execution_authorized") is False,
        "R-064 campaign-wide authorization is prohibited",
    )
    _require(
        authorization.get("automatic_retry_allowed") is False,
        "R-064 authorization cannot allow automatic retry",
    )
    _require(
        authorization.get("automatic_next_case_allowed") is False,
        "R-064 authorization cannot allow automatic next case",
    )

    _require(
        authorization.get("run_id") == plan["run_id"],
        "R-064 authorization run_id mismatch",
    )
    _require(
        int(authorization.get("campaign_seed")) == int(plan["campaign_seed"]),
        "R-064 authorization campaign seed mismatch",
    )
    _require(
        int(authorization.get("block_index")) == int(plan["block_index"]),
        "R-064 authorization block mismatch",
    )
    _require(
        int(authorization.get("cell_order_index"))
        == int(plan["cell_order_index"]),
        "R-064 authorization order mismatch",
    )
    _require(
        authorization.get("cell_id") == plan["cell_id"],
        "R-064 authorization cell mismatch",
    )
    _require(
        authorization.get("plan_sha256") == _canonical_sha256(plan),
        "R-064 authorization plan identity mismatch",
    )

    _require(
        isinstance(current_repo_sha, str)
        and len(current_repo_sha) == 40
        and all(ch in "0123456789abcdef" for ch in current_repo_sha),
        "R-064 current repository SHA must be lowercase 40-hex",
    )
    _require(
        plan["repo_commit"] == current_repo_sha,
        "R-064 plan repository SHA does not match current repository SHA",
    )
    _require(
        authorization.get("authorized_repo_sha") == current_repo_sha,
        "R-064 authorization repository SHA does not match current repository SHA",
    )

    expected_route_binding = {
        "event_id": route["event_id"],
        "runtime_family": route["runtime_family"],
        "runtime_variant": route["runtime_variant"],
        "campaign_observation_adapter_decision_id": route[
            "campaign_observation_adapter_decision_id"
        ],
        "development_runtime_validation_decision_id": route[
            "development_runtime_validation_decision_id"
        ],
    }
    _require(
        authorization.get("route_binding") == expected_route_binding,
        "R-064 authorization route binding mismatch",
    )

    return copy.deepcopy(authorization)


def build_execution_descriptor(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    completed_valid_positions: list[dict[str, Any]],
    current_repo_sha: str,
) -> dict[str, Any]:
    next_trial = next_required_trial(completed_valid_positions)
    _require(next_trial is not None, "R-064 frozen campaign is already complete")

    _require(
        int(plan["campaign_seed"]) == int(next_trial["campaign_seed"])
        and int(plan["cell_order_index"]) == int(next_trial["cell_order_index"])
        and plan["cell_id"] == next_trial["cell_id"],
        "R-064 requested plan is not the next frozen trial",
    )

    validate_trial_authorization(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    route = route_trial_plan(plan)

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R064_AUTHORIZED_SINGLE_TRIAL_EXECUTION_DESCRIPTOR",
        "global_order_index": int(next_trial["global_order_index"]),
        "block_index": int(plan["block_index"]),
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_order_index": int(plan["cell_order_index"]),
        "cell_id": plan["cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "plan_sha256": _canonical_sha256(plan),
        "route_binding": route,
        "evidence_directory": (
            f"results/wp9/campaign/seed-{int(plan['campaign_seed'])}/"
            f"{plan['cell_id']}/{plan['run_id']}"
        ),
        "single_trial_authorization_validated": True,
        "clean_snapshot_required_before_trial": True,
        "invalid_attempt_reuses_same_seed": True,
        "invalid_attempt_reuses_same_cell_id": True,
        "invalid_attempt_requires_new_run_id": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def run_authorized_trial(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    completed_valid_positions: list[dict[str, Any]],
    current_repo_sha: str,
    executor: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    descriptor = build_execution_descriptor(
        plan=plan,
        authorization=authorization,
        completed_valid_positions=completed_valid_positions,
        current_repo_sha=current_repo_sha,
    )

    result = executor(copy.deepcopy(descriptor))
    _require(isinstance(result, dict), "R-064 executor result must be an object")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R064_SINGLE_TRIAL_EXECUTOR_RETURN",
        "run_id": descriptor["run_id"],
        "campaign_seed": descriptor["campaign_seed"],
        "cell_id": descriptor["cell_id"],
        "executor_invocation_count": 1,
        "executor_result": copy.deepcopy(result),
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "runtime_execution_performed": bool(
            result.get("runtime_execution_performed", False)
        ),
        "campaign_seed_consumed": bool(
            result.get("campaign_seed_consumed", False)
        ),
        "campaign_data_generated": bool(
            result.get("campaign_data_generated", False)
        ),
    }


def _authorization_request_from_args(args: argparse.Namespace) -> dict[str, Any]:
    plan = build_trial_plan(
        campaign_seed=args.campaign_seed,
        cell_id=args.cell_id,
        run_id=args.run_id,
        repo_commit=args.repo_commit,
    )
    return build_authorization_request(plan)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate-static")

    request = sub.add_parser("authorization-request")
    request.add_argument("--campaign-seed", type=int, required=True)
    request.add_argument("--cell-id", required=True)
    request.add_argument("--run-id", required=True)
    request.add_argument("--repo-commit", required=True)

    sub.add_parser("execute-trial")

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_bridge()
        print("WP9_R064_FINAL_CAMPAIGN_BRIDGE_STATIC=PASS")
        for key in (
            "campaign_cell_count",
            "campaign_seed_block_count",
            "valid_repetitions_per_cell",
            "planned_valid_executions",
            "campaign_route_family_count",
            "campaign_runtime_variant_count",
            "campaign_observation_adapters_ready",
            "validated_runtime_mechanism_evidence_present",
            "authorization_contract_present",
            "frozen_order_enforced",
            "one_trial_per_invocation",
            "production_runtime_executor_bound",
            "bounded_non_campaign_seed_runtime_validation_required",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            value = result[key]
            print(
                f"{key}="
                + (str(value).lower() if isinstance(value, bool) else str(value))
            )
        return 0

    if args.command == "authorization-request":
        result = _authorization_request_from_args(args)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0

    raise PermissionError(
        "R-064 static/TDD gate: campaign execution remains blocked; "
        "a bounded non-campaign-seed runtime integration validation and "
        "a separate exact single-trial authorization are required"
    )


if __name__ == "__main__":
    raise SystemExit(main())
