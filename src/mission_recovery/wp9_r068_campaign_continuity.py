from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from .wp9_r064_attempt_history import (
    next_required_trial_from_attempt_history,
    validate_attempt_history,
)

DECISION_ID = "R-068"
VALID_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _require_sha(value: Any, *, label: str) -> str:
    text = str(value)
    _require(
        SHA_RE.fullmatch(text) is not None,
        f"R-068 {label} must be a lowercase 40-hex Git SHA",
    )
    return text


def _snapshot_repo_sha(result: dict[str, Any]) -> str | None:
    run_record = result.get("run_record")
    if not isinstance(run_record, dict):
        return None
    environment = run_record.get("environment")
    if not isinstance(environment, dict):
        return None
    snapshot = environment.get("snapshot_id")
    if not isinstance(snapshot, str) or not snapshot.startswith("repo-"):
        return None
    return _require_sha(snapshot[5:], label="retained execution snapshot")


def _validate_identity(
    *, attempt: dict[str, Any], result: dict[str, Any]
) -> None:
    _require(
        result.get("run_id") == attempt.get("run_id")
        and int(result.get("campaign_seed")) == int(attempt.get("campaign_seed"))
        and result.get("cell_id") == attempt.get("cell_id")
        and result.get("attempt_status") == attempt.get("attempt_status"),
        "R-068 retained result identity differs from attempt ledger",
    )


def _validate_valid_result(result: dict[str, Any]) -> None:
    _require(
        result.get("classification") == VALID_CLASSIFICATION
        and result.get("runtime_execution_performed") is True
        and result.get("campaign_seed_consumed") is True
        and result.get("campaign_data_generated") is True
        and int(result.get("source_harness_invocation_count", 0)) == 1
        and result.get("automatic_retry_performed") is False
        and result.get("automatic_next_case_performed") is False
        and result.get("treatment_fidelity_valid") is True
        and result.get("raw_metric_inputs_complete") is True,
        "R-068 VALID retained result is scientifically or operationally incomplete",
    )


def validate_campaign_continuity(
    *,
    attempt_history: list[dict[str, Any]],
    retained_results: dict[str, dict[str, Any]],
    current_repo_sha: str,
    is_ancestor: Callable[[str, str], bool],
) -> dict[str, Any]:
    current_sha = _require_sha(current_repo_sha, label="current repository")
    state = validate_attempt_history(attempt_history)

    _require(
        len(retained_results) == len(attempt_history),
        "R-068 retained-result count differs from attempt ledger",
    )

    execution_shas: list[str] = []
    for attempt in attempt_history:
        run_id = str(attempt.get("run_id"))
        _require(
            run_id in retained_results,
            "R-068 retained campaign result is missing for ledger run_id",
        )
        result = retained_results[run_id]
        _validate_identity(attempt=attempt, result=result)

        if attempt.get("attempt_status") == "VALID":
            _validate_valid_result(result)

        historical_sha = _snapshot_repo_sha(result)
        if historical_sha is not None:
            _require(
                is_ancestor(historical_sha, current_sha),
                "R-068 retained execution baseline is not an ancestor of current baseline",
            )
            execution_shas.append(historical_sha)

    next_trial = next_required_trial_from_attempt_history(attempt_history)
    result: dict[str, Any] = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R068_CAMPAIGN_CONTINUITY_VALID",
        "attempt_count": int(state["attempt_count"]),
        "valid_position_count": int(state["valid_position_count"]),
        "invalid_attempt_count": int(state["invalid_attempt_count"]),
        "campaign_complete": bool(state["campaign_complete"]),
        "retained_execution_repo_shas": execution_shas,
        "historical_baseline_count": len(set(execution_shas)),
        "current_repo_sha": current_sha,
        "baseline_transition_valid": True,
        "historical_execution_sha_may_differ_from_current_sha": True,
        "attempt_history_validated": True,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
    }
    if next_trial is None:
        result["next_required_trial"] = None
    else:
        result.update(
            {
                "next_required_global_order_index": int(
                    next_trial["global_order_index"]
                ),
                "next_required_campaign_seed": int(next_trial["campaign_seed"]),
                "next_required_cell_order_index": int(
                    next_trial["cell_order_index"]
                ),
                "next_required_cell_id": str(next_trial["cell_id"]),
            }
        )
    return result


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_is_ancestor(old: str, new: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", old, new],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _load_retained_results(
    *, attempt_history: list[dict[str, Any]], campaign_root: Path
) -> dict[str, dict[str, Any]]:
    retained: dict[str, dict[str, Any]] = {}
    for attempt in attempt_history:
        seed = int(attempt["campaign_seed"])
        cell = str(attempt["cell_id"])
        run_id = str(attempt["run_id"])
        run_dir = campaign_root / f"seed-{seed}" / cell / run_id
        if attempt["attempt_status"] == "VALID":
            path = run_dir / "campaign-trial-result.json"
        else:
            path = run_dir / "campaign-trial-invalid.json"
        _require(path.is_file(), f"R-068 retained result file missing: {path}")
        retained[run_id] = _load_json(path)
    return retained


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-history-json", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--current-repo-sha", required=True)
    args = parser.parse_args(argv)

    history = _load_json(args.attempt_history_json)
    _require(isinstance(history, list), "R-068 attempt history must be a JSON array")
    retained = _load_retained_results(
        attempt_history=history,
        campaign_root=args.campaign_root,
    )
    result = validate_campaign_continuity(
        attempt_history=history,
        retained_results=retained,
        current_repo_sha=args.current_repo_sha,
        is_ancestor=_git_is_ancestor,
    )

    print("WP9_R068_CAMPAIGN_CONTINUITY=PASS")
    for key in (
        "attempt_count",
        "valid_position_count",
        "invalid_attempt_count",
        "historical_baseline_count",
        "current_repo_sha",
        "baseline_transition_valid",
        "historical_execution_sha_may_differ_from_current_sha",
        "attempt_history_validated",
        "next_required_global_order_index",
        "next_required_campaign_seed",
        "next_required_cell_order_index",
        "next_required_cell_id",
        "runtime_execution_performed",
        "campaign_seed_consumed",
        "campaign_data_generated",
        "automatic_retry_performed",
        "automatic_next_case_performed",
    ):
        if key not in result:
            continue
        value = result[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    for sha in result["retained_execution_repo_shas"]:
        print(f"retained_execution_repo_sha={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
