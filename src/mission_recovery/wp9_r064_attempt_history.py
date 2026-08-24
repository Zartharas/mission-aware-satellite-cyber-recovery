from __future__ import annotations

import argparse
import copy
import re
from typing import Any

from .wp9_final_campaign_bridge import (
    build_execution_descriptor,
    frozen_campaign_sequence,
    validate_static_bridge,
)

DECISION_ID = "R-064"
STATIC_CLASSIFICATION = "WP9_R064_ATTEMPT_HISTORY_GUARD_STATIC_READY"
ATTEMPT_STATUS_VALID = "VALID"
ATTEMPT_STATUS_INVALID = "INVALID"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _position_identity(row: dict[str, Any]) -> tuple[int, int, str]:
    try:
        return (
            int(row["campaign_seed"]),
            int(row["cell_order_index"]),
            str(row["cell_id"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("R-064 attempt position identity is incomplete") from exc


def _run_id(row: dict[str, Any]) -> str:
    value = row.get("run_id")
    _require(
        isinstance(value, str) and RUN_ID_PATTERN.fullmatch(value) is not None,
        "R-064 attempt run_id must use only A-Z a-z 0-9 _ . -",
    )
    return value


def validate_attempt_history(
    attempt_history: list[dict[str, Any]],
) -> dict[str, Any]:
    sequence = frozen_campaign_sequence()
    attempts = list(attempt_history)
    seen_run_ids: set[str] = set()
    valid_count = 0
    invalid_count = 0

    for attempt_index, attempt in enumerate(attempts, start=1):
        _require(
            valid_count < len(sequence),
            "R-064 attempt history continues after frozen campaign completion",
        )
        expected = sequence[valid_count]
        _require(
            _position_identity(attempt) == _position_identity(expected),
            "R-064 attempt must target the exact next frozen trial",
        )

        run_id = _run_id(attempt)
        _require(
            run_id not in seen_run_ids,
            "R-064 attempt run_id must be globally unique",
        )
        seen_run_ids.add(run_id)

        status = attempt.get("attempt_status")
        _require(
            status in {ATTEMPT_STATUS_VALID, ATTEMPT_STATUS_INVALID},
            "R-064 attempt_status must be VALID or INVALID",
        )

        if status == ATTEMPT_STATUS_VALID:
            valid_count += 1
        else:
            invalid_count += 1

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R064_ATTEMPT_HISTORY_VALID",
        "attempt_count": len(attempts),
        "valid_position_count": valid_count,
        "invalid_attempt_count": invalid_count,
        "campaign_complete": valid_count == len(sequence),
        "run_id_uniqueness_enforced": True,
        "invalid_attempt_retains_current_position": True,
        "duplicate_valid_position_prevented": True,
        "hidden_rerun_prevented": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def next_required_trial_from_attempt_history(
    attempt_history: list[dict[str, Any]],
) -> dict[str, Any] | None:
    state = validate_attempt_history(attempt_history)
    if state["campaign_complete"]:
        return None
    return copy.deepcopy(
        frozen_campaign_sequence()[int(state["valid_position_count"])]
    )


def build_attempt_guarded_execution_descriptor(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    attempt_history: list[dict[str, Any]],
    current_repo_sha: str,
) -> dict[str, Any]:
    state = validate_attempt_history(attempt_history)
    next_trial = next_required_trial_from_attempt_history(attempt_history)
    _require(next_trial is not None, "R-064 frozen campaign is already complete")

    _require(
        plan.get("run_id") not in {
            _run_id(row) for row in attempt_history
        },
        "R-064 new attempt run_id must not reuse retained run_id",
    )
    _require(
        _position_identity(plan) == _position_identity(next_trial),
        "R-064 requested plan is not the next frozen trial",
    )

    completed_valid_positions = frozen_campaign_sequence()[
        : int(state["valid_position_count"])
    ]
    descriptor = build_execution_descriptor(
        plan=plan,
        authorization=authorization,
        completed_valid_positions=completed_valid_positions,
        current_repo_sha=current_repo_sha,
    )
    result = copy.deepcopy(descriptor)
    result.update(
        {
            "attempt_history_validated": True,
            "prior_attempt_count": int(state["attempt_count"]),
            "prior_valid_position_count": int(state["valid_position_count"]),
            "prior_invalid_attempt_count": int(state["invalid_attempt_count"]),
            "run_id_uniqueness_enforced": True,
            "invalid_attempt_retains_current_position": True,
            "duplicate_valid_position_prevented": True,
            "hidden_rerun_prevented": True,
        }
    )
    return result


def validate_static_attempt_guard() -> dict[str, Any]:
    bridge = validate_static_bridge()
    _require(bridge["decision_id"] == DECISION_ID, "R-064 bridge decision changed")
    _require(
        bridge["final_campaign_execution_authorized"] is False,
        "R-064 attempt guard cannot follow final campaign authorization",
    )

    empty_state = validate_attempt_history([])
    first = next_required_trial_from_attempt_history([])
    _require(first is not None, "R-064 first frozen position is missing")
    _require(
        int(first["global_order_index"]) == 1
        and int(first["campaign_seed"]) == 10001
        and first["cell_id"] == "A19",
        "R-064 first frozen position changed",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": STATIC_CLASSIFICATION,
        "attempt_history_required_for_campaign_execution": True,
        "run_id_uniqueness_enforced": True,
        "invalid_attempt_retains_same_seed_cell": True,
        "invalid_attempt_requires_new_run_id": True,
        "duplicate_valid_position_prevented": True,
        "hidden_rerun_prevented": True,
        "one_trial_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "empty_history_valid_position_count": empty_state["valid_position_count"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_attempt_guard()
        print("WP9_R064_ATTEMPT_HISTORY_GUARD_STATIC=PASS")
        for key in (
            "attempt_history_required_for_campaign_execution",
            "run_id_uniqueness_enforced",
            "invalid_attempt_retains_same_seed_cell",
            "invalid_attempt_requires_new_run_id",
            "duplicate_valid_position_prevented",
            "hidden_rerun_prevented",
            "one_trial_per_invocation",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            value = result[key]
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
