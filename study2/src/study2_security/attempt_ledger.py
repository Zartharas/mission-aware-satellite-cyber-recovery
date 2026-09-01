from __future__ import annotations

import re
from typing import Any

from .trial_manifest import materialize_trial_manifest


RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
VALID = "VALID"
INVALID = "INVALID"


def _identity(row: dict[str, Any]) -> tuple[str, str, int]:
    try:
        return (str(row["trial_id"]), str(row["cell_id"]), int(row["seed"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("attempt identity is incomplete") from exc


def validate_attempt_ledger(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    positions = materialize_trial_manifest()["positions"]
    seen_run_ids: set[str] = set()
    valid_position_count = 0
    invalid_attempt_count = 0
    for attempt in attempts:
        if valid_position_count >= len(positions):
            raise ValueError("attempt ledger continues after campaign completion")
        expected = positions[valid_position_count]
        if _identity(attempt) != _identity(expected):
            raise ValueError("attempt does not target the exact next frozen trial")
        run_id = attempt.get("run_id")
        if not isinstance(run_id, str) or RUN_ID_PATTERN.fullmatch(run_id) is None:
            raise ValueError("run_id is missing or contains unsupported characters")
        if run_id in seen_run_ids:
            raise ValueError("run_id must be globally unique")
        seen_run_ids.add(run_id)
        status = attempt.get("attempt_status")
        if status not in {VALID, INVALID}:
            raise ValueError("attempt_status must be VALID or INVALID")
        if status == VALID:
            valid_position_count += 1
        else:
            invalid_attempt_count += 1
    return {
        "schema": 1,
        "classification": "STUDY2_ATTEMPT_LEDGER_VALID",
        "attempt_count": len(attempts),
        "valid_position_count": valid_position_count,
        "invalid_attempt_count": invalid_attempt_count,
        "campaign_complete": valid_position_count == len(positions),
        "run_id_uniqueness_enforced": True,
        "invalid_attempt_retains_current_position": True,
        "hidden_rerun_prevented": True,
        "automatic_retry_allowed": False,
        "automatic_next_trial_allowed": False,
    }


def next_required_trial(attempts: list[dict[str, Any]]) -> dict[str, Any] | None:
    state = validate_attempt_ledger(attempts)
    if state["campaign_complete"]:
        return None
    return dict(materialize_trial_manifest()["positions"][int(state["valid_position_count"])])
