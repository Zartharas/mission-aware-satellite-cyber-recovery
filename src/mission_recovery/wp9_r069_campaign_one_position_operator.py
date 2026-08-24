from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .wp9_campaign_trial_controller import build_trial_plan
from .wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
    validate_trial_authorization,
)
from .wp9_r064_attempt_history import (
    next_required_trial_from_attempt_history,
    validate_attempt_history,
    validate_static_attempt_guard,
)
from .wp9_r066_final_campaign_runtime_binding import (
    build_campaign_runtime_request,
    validate_static_campaign_runtime_binding,
)
from .wp9_r066_campaign_runtime_executor import validate_static_executor
from .wp9_r068_campaign_continuity import validate_campaign_continuity

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-069"
CAMPAIGN_ROOT = ROOT / "results" / "wp9" / "campaign"
ATTEMPT_HISTORY = CAMPAIGN_ROOT / "attempt-history.json"


class OperatorError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OperatorError(message)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_attempt_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    _require(not path.is_symlink(), "R-069 attempt-history path must not be a symlink")
    value = _load_json(path)
    _require(isinstance(value, list), "R-069 attempt history must be a JSON array")
    return value


def _git_is_ancestor(old: str, new: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", old, new],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _retained_result_path(
    *, campaign_root: Path, attempt: dict[str, Any]
) -> Path:
    seed = int(attempt["campaign_seed"])
    cell = str(attempt["cell_id"])
    run_id = str(attempt["run_id"])
    run_dir = campaign_root / f"seed-{seed}" / cell / run_id
    name = (
        "campaign-trial-result.json"
        if attempt["attempt_status"] == "VALID"
        else "campaign-trial-invalid.json"
    )
    return run_dir / name


def load_retained_results(
    *, attempt_history: list[dict[str, Any]], campaign_root: Path
) -> dict[str, dict[str, Any]]:
    retained: dict[str, dict[str, Any]] = {}
    for attempt in attempt_history:
        run_id = str(attempt["run_id"])
        path = _retained_result_path(campaign_root=campaign_root, attempt=attempt)
        _require(path.is_file() and not path.is_symlink(), f"R-069 retained result missing: {path}")
        value = _load_json(path)
        _require(isinstance(value, dict), f"R-069 retained result is not an object: {path}")
        retained[run_id] = value
    return retained


def audit_unledgered_campaign_artifacts(
    *, attempt_history: list[dict[str, Any]], campaign_root: Path
) -> dict[str, Any]:
    if not campaign_root.exists():
        return {
            "unledgered_pre_runtime_artifact_count": 0,
            "unledgered_pre_runtime_run_ids": [],
            "unledgered_scientific_artifact_detected": False,
        }
    _require(not campaign_root.is_symlink(), "R-069 campaign root must not be a symlink")
    ledger_ids = {str(row["run_id"]) for row in attempt_history}
    allowed = {
        "immutable-ground/campaign-plan.json",
        "immutable-ground/r066-runtime-request.json",
        "immutable-ground/source-harness-derivation.json",
    }
    pre_runtime_ids: list[str] = []
    for run_dir in sorted(campaign_root.glob("seed-*/*/*")):
        if not run_dir.is_dir() or run_dir.is_symlink():
            continue
        run_id = run_dir.name
        if run_id in ledger_ids:
            continue
        relative_files = {
            str(path.relative_to(run_dir))
            for path in run_dir.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        unexpected = sorted(relative_files - allowed)
        _require(
            not unexpected,
            "R-069 unledgered campaign artifact contains runtime/scientific evidence: "
            + run_id
            + " -> "
            + ",".join(unexpected),
        )
        seed_marker = run_dir / "immutable-ground" / "campaign-seed-consumption.json"
        _require(
            not seed_marker.exists() and not seed_marker.is_symlink(),
            "R-069 unledgered campaign artifact contains a seed-commit marker: " + run_id,
        )
        runtime_observation = run_dir / "runtime-observation"
        _require(
            not runtime_observation.exists(),
            "R-069 unledgered campaign artifact contains runtime observation: " + run_id,
        )
        pre_runtime_ids.append(run_id)
    return {
        "unledgered_pre_runtime_artifact_count": len(pre_runtime_ids),
        "unledgered_pre_runtime_run_ids": pre_runtime_ids,
        "unledgered_scientific_artifact_detected": False,
    }


def _grant_exact_single_trial_authorization(
    *, plan: dict[str, Any], current_repo_sha: str
) -> dict[str, Any]:
    authorization = build_authorization_request(plan)
    authorization = copy.deepcopy(authorization)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["single_trial_runtime_authorized"] = True
    validate_trial_authorization(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    _require(
        authorization["campaign_wide_execution_authorized"] is False,
        "R-069 cannot grant campaign-wide execution",
    )
    _require(
        authorization["automatic_retry_allowed"] is False,
        "R-069 authorization cannot allow automatic retry",
    )
    _require(
        authorization["automatic_next_case_allowed"] is False,
        "R-069 authorization cannot allow automatic next case",
    )
    return authorization


def inspect_runtime_request(request: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(request, dict), "R-069 runtime request must be an object")
    plan = request.get("plan")
    route = request.get("route_binding")
    source = request.get("source_harness")
    _require(isinstance(plan, dict), "R-069 runtime request lacks embedded trial plan")
    _require(isinstance(route, dict), "R-069 runtime request lacks route binding")
    _require(isinstance(source, dict), "R-069 runtime request lacks source harness binding")
    factor = plan.get("factor_context")
    _require(isinstance(factor, dict), "R-069 embedded plan lacks factor context")

    _require(request.get("cell_id") == plan.get("cell_id"), "R-069 request/plan cell mismatch")
    _require(int(request.get("campaign_seed")) == int(plan.get("campaign_seed")), "R-069 request/plan seed mismatch")
    _require(request.get("run_id") == plan.get("run_id"), "R-069 request/plan run_id mismatch")
    _require(request.get("repo_commit") == plan.get("repo_commit"), "R-069 request/plan repository mismatch")
    _require(plan.get("runtime_family") == route.get("runtime_family"), "R-069 plan/route runtime family mismatch")
    _require(plan.get("runtime_variant") == route.get("runtime_variant"), "R-069 plan/route runtime variant mismatch")
    _require(factor.get("event_id") == route.get("event_id"), "R-069 plan/route event mismatch")
    _require(source.get("event_id") == factor.get("event_id"), "R-069 source/plan event mismatch")
    _require(request.get("source_harness_blob_identity_validated") is True, "R-069 source harness identity was not validated")
    _require(request.get("attempt_history_validated") is True, "R-069 attempt history was not validated")
    _require(request.get("one_trial_per_invocation") is True, "R-069 request does not enforce one trial")
    _require(int(request.get("source_harness_invocation_limit", 0)) == 1, "R-069 source harness invocation limit changed")
    _require(request.get("automatic_retry_allowed") is False, "R-069 request allows automatic retry")
    _require(request.get("automatic_next_case_allowed") is False, "R-069 request allows automatic next case")
    _require(request.get("runtime_execution_performed") is False, "R-069 request already executed runtime")
    _require(request.get("campaign_seed_consumed") is False, "R-069 request already consumed campaign seed")
    _require(request.get("campaign_data_generated") is False, "R-069 request already generated campaign data")
    _require(request.get("campaign_wide_execution_authorized") is False, "R-069 request allows campaign-wide execution")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R069_SCHEMA_AWARE_RUNTIME_REQUEST_VALID",
        "global_order_index": int(request["global_order_index"]),
        "campaign_seed": int(request["campaign_seed"]),
        "cell_order_index": int(request["cell_order_index"]),
        "cell_id": str(request["cell_id"]),
        "run_id": str(request["run_id"]),
        "repo_commit": str(request["repo_commit"]),
        "event_id": str(factor["event_id"]),
        "runtime_family": str(plan["runtime_family"]),
        "runtime_variant": str(plan["runtime_variant"]),
        "requested_policy_id": str(factor["policy_id"]),
        "expected_effective_policy_id_for_acceptance_only": plan.get(
            "expected_effective_policy_id_for_acceptance_only"
        ),
        "source_case": str(source["source_case"]),
        "source_cell": str(source["source_cell"]),
        "source_blob_sha": str(source["source_blob_sha"]),
        "prior_attempt_count": int(request["prior_attempt_count"]),
        "prior_valid_position_count": int(request["prior_valid_position_count"]),
        "prior_invalid_attempt_count": int(request["prior_invalid_attempt_count"]),
        "request_schema_validated": True,
        "one_trial_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_wide_execution_authorized": False,
    }


def prepare_next_attempt(
    *,
    attempt_history: list[dict[str, Any]],
    retained_results: dict[str, dict[str, Any]],
    current_repo_sha: str,
    run_id: str,
    is_ancestor: Callable[[str, str], bool],
) -> dict[str, Any]:
    continuity = validate_campaign_continuity(
        attempt_history=attempt_history,
        retained_results=retained_results,
        current_repo_sha=current_repo_sha,
        is_ancestor=is_ancestor,
    )
    next_trial = next_required_trial_from_attempt_history(attempt_history)
    _require(next_trial is not None, "R-069 frozen campaign is already complete")
    _require(
        int(next_trial["global_order_index"])
        == int(continuity["next_required_global_order_index"]),
        "R-069 continuity/attempt-guard global position mismatch",
    )
    _require(
        int(next_trial["campaign_seed"])
        == int(continuity["next_required_campaign_seed"])
        and int(next_trial["cell_order_index"])
        == int(continuity["next_required_cell_order_index"])
        and str(next_trial["cell_id"]) == str(continuity["next_required_cell_id"]),
        "R-069 continuity/attempt-guard next trial mismatch",
    )

    plan = build_trial_plan(
        campaign_seed=int(next_trial["campaign_seed"]),
        cell_id=str(next_trial["cell_id"]),
        run_id=run_id,
        repo_commit=current_repo_sha,
    )
    authorization = _grant_exact_single_trial_authorization(
        plan=plan,
        current_repo_sha=current_repo_sha,
    )
    request = build_campaign_runtime_request(
        plan=plan,
        authorization=authorization,
        attempt_history=attempt_history,
        current_repo_sha=current_repo_sha,
    )
    summary = inspect_runtime_request(request)
    _require(
        summary["global_order_index"] == int(next_trial["global_order_index"]),
        "R-069 request global position differs from frozen next trial",
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R069_NEXT_SINGLE_TRIAL_PREPARED",
        "continuity": copy.deepcopy(continuity),
        "next_trial": copy.deepcopy(next_trial),
        "plan": plan,
        "authorization": authorization,
        "request": request,
        "request_summary": summary,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_wide_execution_authorized": False,
    }


def _validate_executor_result_for_append(
    *, history: list[dict[str, Any]], executor_result: dict[str, Any], cell_order_index: int
) -> dict[str, Any]:
    next_trial = next_required_trial_from_attempt_history(history)
    _require(next_trial is not None, "R-069 cannot append after campaign completion")
    _require(int(cell_order_index) == int(next_trial["cell_order_index"]), "R-069 append cell-order index differs from next frozen trial")
    _require(executor_result.get("attempt_status") in {"VALID", "INVALID"}, "R-069 executor attempt_status must be VALID or INVALID")
    _require(int(executor_result.get("campaign_seed")) == int(next_trial["campaign_seed"]), "R-069 executor seed differs from next frozen trial")
    _require(str(executor_result.get("cell_id")) == str(next_trial["cell_id"]), "R-069 executor cell differs from next frozen trial")
    _require(int(executor_result.get("source_harness_invocation_count", 0)) == 1, "R-069 executor did not invoke exactly one source harness")
    _require(executor_result.get("automatic_retry_performed") is False, "R-069 executor performed automatic retry")
    _require(executor_result.get("automatic_next_case_performed") is False, "R-069 executor performed automatic next case")
    _require(executor_result.get("campaign_wide_execution_authorized") is False, "R-069 executor reports campaign-wide authorization")
    runner = executor_result.get("runner_result")
    _require(isinstance(runner, dict), "R-069 executor lacks runner result")
    _require(runner.get("attempt_status") == executor_result.get("attempt_status"), "R-069 executor/runner attempt status mismatch")
    if executor_result["attempt_status"] == "VALID":
        _require(executor_result.get("runtime_execution_performed") is True, "R-069 VALID attempt lacks runtime execution")
        _require(executor_result.get("campaign_seed_consumed") is True, "R-069 VALID attempt did not consume seed")
        _require(executor_result.get("campaign_data_generated") is True, "R-069 VALID attempt did not generate campaign data")
        _require(runner.get("treatment_fidelity_valid") is True, "R-069 VALID attempt lacks treatment fidelity")
        _require(runner.get("raw_metric_inputs_complete") is True, "R-069 VALID attempt lacks raw metrics")
    else:
        _require(runner.get("invalid_attempt_retained") is True, "R-069 INVALID attempt was not retained")
    return copy.deepcopy(next_trial)


def _atomic_write_json(path: Path, value: Any) -> None:
    _require(not path.is_symlink(), "R-069 refuses to replace a symlinked attempt-history file")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
        try:
            dir_fd = os.open(path.parent, os.O_DIRECTORY)
        except (AttributeError, OSError):
            dir_fd = None
        if dir_fd is not None:
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def append_attempt_result_atomic(
    *,
    attempt_history_path: Path,
    executor_result: dict[str, Any],
    cell_order_index: int,
    expected_prior_attempt_count: int | None = None,
) -> dict[str, Any]:
    history = _load_attempt_history(attempt_history_path)
    if expected_prior_attempt_count is not None:
        _require(
            len(history) == int(expected_prior_attempt_count),
            "R-069 attempt history changed between preparation and append",
        )
    next_trial = _validate_executor_result_for_append(
        history=history,
        executor_result=executor_result,
        cell_order_index=cell_order_index,
    )
    entry = {
        "campaign_seed": int(executor_result["campaign_seed"]),
        "cell_order_index": int(next_trial["cell_order_index"]),
        "cell_id": str(executor_result["cell_id"]),
        "run_id": str(executor_result["run_id"]),
        "attempt_status": str(executor_result["attempt_status"]),
    }
    candidate = history + [entry]
    state = validate_attempt_history(candidate)
    _atomic_write_json(attempt_history_path, candidate)
    next_required = next_required_trial_from_attempt_history(candidate)
    result: dict[str, Any] = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R069_ATTEMPT_HISTORY_APPEND_VALID",
        "attempt_count": int(state["attempt_count"]),
        "valid_position_count": int(state["valid_position_count"]),
        "invalid_attempt_count": int(state["invalid_attempt_count"]),
        "campaign_complete": bool(state["campaign_complete"]),
        "appended_run_id": entry["run_id"],
        "appended_attempt_status": entry["attempt_status"],
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
    }
    if next_required is None:
        result["next_required_trial"] = None
    else:
        result.update(
            {
                "next_required_global_order_index": int(next_required["global_order_index"]),
                "next_required_campaign_seed": int(next_required["campaign_seed"]),
                "next_required_cell_order_index": int(next_required["cell_order_index"]),
                "next_required_cell_id": str(next_required["cell_id"]),
            }
        )
    return result


def validate_static_operator() -> dict[str, Any]:
    guard = validate_static_attempt_guard()
    binder = validate_static_campaign_runtime_binding()
    executor = validate_static_executor()
    _require(guard["one_trial_per_invocation"] is True, "R-069 requires R-064 one-trial guard")
    _require(binder["production_runtime_executor_bound"] is True, "R-069 requires R-066 production binder")
    _require(executor["production_runtime_executor_bound"] is True, "R-069 requires R-066 production executor")

    fake_sha = "a" * 40
    plan = build_trial_plan(
        campaign_seed=10001,
        cell_id="A19",
        run_id="wp9-r069-static-a19",
        repo_commit=fake_sha,
    )
    authorization = _grant_exact_single_trial_authorization(
        plan=plan,
        current_repo_sha=fake_sha,
    )
    request = build_campaign_runtime_request(
        plan=plan,
        authorization=authorization,
        attempt_history=[],
        current_repo_sha=fake_sha,
    )
    summary = inspect_runtime_request(request)
    _require(summary["runtime_family"] == "replay", "R-069 nested runtime-family inspection changed")
    _require(summary["runtime_variant"] == "e2_replay_effect", "R-069 nested runtime-variant inspection changed")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R069_ONE_POSITION_OPERATOR_STATIC_READY",
        "schema_aware_request_inspection": True,
        "runtime_family_read_from_embedded_plan": True,
        "r068_continuity_required": True,
        "unledgered_campaign_artifact_audit_required": True,
        "atomic_attempt_history_append": True,
        "one_trial_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_wide_execution_authorized": False,
    }


def _generate_run_id(*, global_order_index: int, campaign_seed: int, cell_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retry = "-retry" if global_order_index > 0 else ""
    return (
        f"{stamp}-wp9-r069-p{global_order_index:04d}{retry}-"
        f"s{campaign_seed}-{cell_id.lower()}-{uuid.uuid4().hex}"
    )


def _prepare_from_files(
    *,
    attempt_history_path: Path,
    campaign_root: Path,
    current_repo_sha: str,
    run_id: str | None,
) -> dict[str, Any]:
    history = _load_attempt_history(attempt_history_path)
    audit = audit_unledgered_campaign_artifacts(
        attempt_history=history,
        campaign_root=campaign_root,
    )
    retained = load_retained_results(
        attempt_history=history,
        campaign_root=campaign_root,
    )
    next_trial = next_required_trial_from_attempt_history(history)
    _require(next_trial is not None, "R-069 frozen campaign is already complete")
    actual_run_id = run_id or _generate_run_id(
        global_order_index=int(next_trial["global_order_index"]),
        campaign_seed=int(next_trial["campaign_seed"]),
        cell_id=str(next_trial["cell_id"]),
    )
    prepared = prepare_next_attempt(
        attempt_history=history,
        retained_results=retained,
        current_repo_sha=current_repo_sha,
        run_id=actual_run_id,
        is_ancestor=_git_is_ancestor,
    )
    prepared["artifact_audit"] = audit
    return prepared


def _write_prepared(output_dir: Path, prepared: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, key in (
        ("plan.json", "plan"),
        ("authorization.json", "authorization"),
        ("request.json", "request"),
        ("request-summary.json", "request_summary"),
        ("continuity.json", "continuity"),
        ("artifact-audit.json", "artifact_audit"),
    ):
        path = output_dir / name
        path.write_text(json.dumps(prepared[key], sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    prepare = sub.add_parser("prepare-next")
    prepare.add_argument("--attempt-history-json", type=Path, default=ATTEMPT_HISTORY)
    prepare.add_argument("--campaign-root", type=Path, default=CAMPAIGN_ROOT)
    prepare.add_argument("--current-repo-sha", required=True)
    prepare.add_argument("--run-id")
    prepare.add_argument("--output-dir", type=Path, required=True)

    append = sub.add_parser("append-result")
    append.add_argument("--attempt-history-json", type=Path, default=ATTEMPT_HISTORY)
    append.add_argument("--request-json", type=Path, required=True)
    append.add_argument("--executor-result-json", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_operator()
        print("WP9_R069_ONE_POSITION_OPERATOR_STATIC=PASS")
        for key in (
            "schema_aware_request_inspection",
            "runtime_family_read_from_embedded_plan",
            "r068_continuity_required",
            "unledgered_campaign_artifact_audit_required",
            "atomic_attempt_history_append",
            "one_trial_per_invocation",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "campaign_wide_execution_authorized",
        ):
            value = result[key]
            if isinstance(value, bool):
                value = str(value).lower()
            print(f"{key}={value}")
        return 0

    if args.command == "prepare-next":
        prepared = _prepare_from_files(
            attempt_history_path=args.attempt_history_json,
            campaign_root=args.campaign_root,
            current_repo_sha=args.current_repo_sha,
            run_id=args.run_id,
        )
        _write_prepared(args.output_dir, prepared)
        summary = prepared["request_summary"]
        audit = prepared["artifact_audit"]
        print("WP9_R069_NEXT_SINGLE_TRIAL_PREPARED=PASS")
        for key in (
            "global_order_index",
            "campaign_seed",
            "cell_order_index",
            "cell_id",
            "run_id",
            "repo_commit",
            "event_id",
            "runtime_family",
            "runtime_variant",
            "requested_policy_id",
            "expected_effective_policy_id_for_acceptance_only",
            "source_case",
            "source_cell",
            "prior_attempt_count",
            "prior_valid_position_count",
            "prior_invalid_attempt_count",
        ):
            print(f"{key}={summary[key]}")
        print(
            "unledgered_pre_runtime_artifact_count="
            + str(audit["unledgered_pre_runtime_artifact_count"])
        )
        for run in audit["unledgered_pre_runtime_run_ids"]:
            print("unledgered_pre_runtime_run_id=" + run)
        print("request_schema_validated=true")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        return 0

    request = _load_json(args.request_json)
    executor_result = _load_json(args.executor_result_json)
    summary = inspect_runtime_request(request)
    _require(
        executor_result.get("run_id") == summary["run_id"],
        "R-069 executor result run_id differs from prepared request",
    )
    state = append_attempt_result_atomic(
        attempt_history_path=args.attempt_history_json,
        executor_result=executor_result,
        cell_order_index=int(summary["cell_order_index"]),
        expected_prior_attempt_count=int(summary["prior_attempt_count"]),
    )
    print("WP9_R069_ATTEMPT_HISTORY_APPEND=PASS")
    for key in (
        "attempt_count",
        "valid_position_count",
        "invalid_attempt_count",
        "campaign_complete",
        "appended_run_id",
        "appended_attempt_status",
        "next_required_global_order_index",
        "next_required_campaign_seed",
        "next_required_cell_order_index",
        "next_required_cell_id",
    ):
        if key not in state:
            continue
        value = state[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    print("automatic_retry_performed=false")
    print("automatic_next_case_performed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
