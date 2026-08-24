from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
from typing import Any

from .events import materialize_event
from . import wp9_r066_final_campaign_runtime_binding as binding
from .wp9_static_contracts import evaluate_wp9_policy

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-066"

_READINESS_MARKER = (
    'echo "nominal_runtime_ready=PASS"\n'
    'echo "nominal_isolation=PASS"\n'
)
_SEED_COMMIT_BLOCK = (
    'echo "nominal_runtime_ready=PASS"\n'
    'echo "nominal_isolation=PASS"\n'
    'PHASE="CAMPAIGN_SEED_COMMIT"\n'
    'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \\\n'
    '  src.mission_recovery.wp9_r066_campaign_runtime_executor \\\n'
    '  mark-seed >/dev/null\n'
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def derive_runtime_harness_text(
    *, request: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    text, derivation = binding.derive_harness_text(request=request)
    _require(
        text.count(_READINESS_MARKER) == 1,
        "R-066 source harness post-readiness marker changed",
    )
    text = text.replace(_READINESS_MARKER, _SEED_COMMIT_BLOCK, 1)
    result = copy.deepcopy(derivation)
    result["post_readiness_seed_commit_insertion_count"] = 1
    result["campaign_seed_commit_after_nominal_runtime_ready"] = True
    result["campaign_seed_commit_after_nominal_isolation"] = True
    result["campaign_seed_commit_before_scientific_runtime_effects"] = True
    return text, result


def _campaign_context() -> tuple[dict[str, Any], Path, str]:
    plan_path = os.environ.get("WP9_R066_CAMPAIGN_PLAN_JSON")
    evidence_dir = os.environ.get("WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY")
    evidence_prefix = os.environ.get("WP9_R066_CAMPAIGN_EVIDENCE_PREFIX")
    _require(bool(plan_path), "R-066 campaign plan environment is missing")
    _require(bool(evidence_dir), "R-066 campaign evidence environment is missing")
    _require(bool(evidence_prefix), "R-066 campaign evidence prefix is missing")
    return (
        _load(Path(str(plan_path))),
        Path(str(evidence_dir)),
        str(evidence_prefix),
    )


def mark_seed_consumed() -> dict[str, Any]:
    plan, evidence, _ = _campaign_context()
    marker = evidence / "immutable-ground" / "campaign-seed-consumption.json"
    _require(
        not marker.exists(),
        "R-066 campaign seed-consumption marker already exists for run",
    )
    record = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R066_CAMPAIGN_SEED_COMMITTED_TO_ATTEMPT",
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "event_id": plan["factor_context"]["event_id"],
        "commit_boundary": "after_nominal_runtime_readiness_and_isolation",
        "campaign_seed_consumed": True,
        "campaign_data_generated": False,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "campaign_wide_execution_authorized": False,
    }
    _write(marker, record)
    return record


def shim_plan(*, family: str, output_json: Path) -> None:
    plan, _, _ = _campaign_context()
    _require(
        plan["factor_context"]["event_id"] == family,
        "R-066 shim family/plan event mismatch",
    )
    compat = binding.build_compatibility_plan(plan=plan)
    _write(output_json, compat)


def shim_select_policy(*, plan_json: Path, output_json: Path) -> None:
    plan = _load(plan_json)
    factor = plan["factor_context"]
    _require(factor["event_id"] == "E3", "R-066 select-policy shim is E3 only")
    event = materialize_event(
        "E3",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-066 E3 runtime policy read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == plan["expected_effective_policy_id_for_acceptance_only"],
        "R-066 E3 runtime policy differs from campaign plan",
    )
    expected_action = plan["expected_selected_action_for_acceptance_only"]
    _require(
        decision["selected_action"] == expected_action,
        "R-066 E3 selected action differs from campaign plan",
    )
    result = copy.deepcopy(decision)
    result.update(
        {
            "schema": 1,
            "decision_id": DECISION_ID,
            "classification": "WP9_R066_E3_RUNTIME_POLICY_DECISION",
            "case_id": plan["case_id"],
            "cell_id": plan["cell_id"],
            "development_seed": int(plan["development_seed"]),
            "campaign_seed": int(plan["campaign_seed"]),
            "campaign_runtime_compatibility_plan": True,
            "development_validation_only": False,
            "campaign_seed_consumed": True,
            "campaign_data_generated": False,
        }
    )
    _write(output_json, result)


def shim_finalize(
    *, family: str, measurement_json: Path, output_json: Path
) -> None:
    plan, evidence, evidence_prefix = _campaign_context()
    _require(
        plan["factor_context"]["event_id"] == family,
        "R-066 finalizer family/plan mismatch",
    )
    seed_marker = evidence / "immutable-ground" / "campaign-seed-consumption.json"
    _require(
        seed_marker.is_file(),
        "R-066 finalization requires post-readiness seed commitment",
    )
    marker = _load(seed_marker)
    _require(
        marker["campaign_seed"] == int(plan["campaign_seed"])
        and marker["cell_id"] == plan["cell_id"],
        "R-066 seed marker identity differs from campaign plan",
    )
    result = binding._runtime_bundle(
        plan=plan,
        measurement=_load(measurement_json),
        evidence_prefix=evidence_prefix,
    )
    _write(output_json, result)
    _write(evidence / "campaign-trial-result.json", result)


def _shim_text() -> str:
    return r'''#!/bin/bash
set -eu
REAL="${WP9_R066_REAL_PYTHON3:?}"
if [ "${1:-}" = "-m" ]; then
  MODULE="${2:-}"
  COMMAND="${3:-}"
  FAMILY=""
  case "$MODULE" in
    src.mission_recovery.wp9_campaign_e1_runtime_adapter) FAMILY="E1" ;;
    src.mission_recovery.wp9_campaign_e2_runtime_adapter) FAMILY="E2" ;;
    src.mission_recovery.wp9_campaign_e3_runtime_adapter) FAMILY="E3" ;;
    src.mission_recovery.wp9_campaign_e4_runtime_adapter) FAMILY="E4" ;;
  esac
  if [ -n "$FAMILY" ] && [ "$COMMAND" = "plan-development" ]; then
    shift 3
    OUT=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --output-json) OUT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [ -n "$OUT" ]
    exec "$REAL" -m src.mission_recovery.wp9_r066_campaign_runtime_executor \
      shim-plan --family "$FAMILY" --output-json "$OUT"
  fi
  if [ "$FAMILY" = "E3" ] && [ "$COMMAND" = "select-policy" ]; then
    shift 3
    PLAN=""
    OUT=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --plan-json) PLAN="$2"; shift 2 ;;
        --output-json) OUT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [ -n "$PLAN" ]
    [ -n "$OUT" ]
    exec "$REAL" -m src.mission_recovery.wp9_r066_campaign_runtime_executor \
      shim-select-policy --plan-json "$PLAN" --output-json "$OUT"
  fi
  if [ -n "$FAMILY" ] && [ "$COMMAND" = "finalize-development" ]; then
    shift 3
    MEASUREMENT=""
    OUT=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --measurement-json) MEASUREMENT="$2"; shift 2 ;;
        --output-json) OUT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [ -n "$MEASUREMENT" ]
    [ -n "$OUT" ]
    exec "$REAL" -m src.mission_recovery.wp9_r066_campaign_runtime_executor \
      shim-finalize --family "$FAMILY" --measurement-json "$MEASUREMENT" \
      --output-json "$OUT"
  fi
fi
exec "$REAL" "$@"
'''


def run_campaign_source_harness(request: dict[str, Any]) -> dict[str, Any]:
    original_derive = binding.derive_harness_text
    original_shim = binding._shim_text
    try:
        binding.derive_harness_text = derive_runtime_harness_text
        binding._shim_text = _shim_text
        return binding.run_source_harness(request)
    finally:
        binding.derive_harness_text = original_derive
        binding._shim_text = original_shim


def execute_request(request: dict[str, Any]) -> dict[str, Any]:
    return binding.execute_campaign_runtime_request(
        request=request,
        runner=run_campaign_source_harness,
        authorization_environment=os.environ,
    )


def validate_static_executor() -> dict[str, Any]:
    base = binding.validate_static_campaign_runtime_binding()
    _require(
        base["production_runtime_executor_bound"] is True,
        "R-066 base production binder is not ready",
    )
    families: set[str] = set()
    for cell_id in sorted(binding.CELL_HARNESS_BINDINGS):
        request = {
            "source_harness": copy.deepcopy(
                binding.CELL_HARNESS_BINDINGS[cell_id]
            ),
            "cell_id": cell_id,
            "campaign_seed": 10001,
        }
        text, derivation = derive_runtime_harness_text(request=request)
        _require(
            derivation["post_readiness_seed_commit_insertion_count"] == 1,
            f"R-066 seed boundary insertion changed: {cell_id}",
        )
        _require(
            text.count("WP9_R066_REPO_ROOT") == 1,
            f"R-066 derived ROOT binding changed: {cell_id}",
        )
        _require(
            "mark-seed" in text,
            f"R-066 derived harness lacks seed boundary: {cell_id}",
        )
        families.add(request["source_harness"]["event_id"])
    _require(families == {"E1", "E2", "E3", "E4"}, "R-066 family coverage changed")
    shim = _shim_text()
    _require("shim-select-policy" in shim, "R-066 E3 policy shim missing")
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R066_CAMPAIGN_RUNTIME_EXECUTOR_STATIC_READY",
        "campaign_cell_count": 24,
        "runtime_family_count": 4,
        "production_runtime_executor_bound": True,
        "source_harness_blob_identity_enforced": True,
        "post_readiness_seed_commit_enforced": True,
        "pre_readiness_failure_can_remain_seed_unconsumed": True,
        "e3_runtime_policy_compatibility_intercepted": True,
        "one_source_harness_invocation_per_trial": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_runtime_authorized": False,
        "campaign_wide_execution_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")
    sub.add_parser("mark-seed")

    plan = sub.add_parser("shim-plan")
    plan.add_argument("--family", required=True, choices=("E1", "E2", "E3", "E4"))
    plan.add_argument("--output-json", type=Path, required=True)

    policy = sub.add_parser("shim-select-policy")
    policy.add_argument("--plan-json", type=Path, required=True)
    policy.add_argument("--output-json", type=Path, required=True)

    finalize = sub.add_parser("shim-finalize")
    finalize.add_argument("--family", required=True, choices=("E1", "E2", "E3", "E4"))
    finalize.add_argument("--measurement-json", type=Path, required=True)
    finalize.add_argument("--output-json", type=Path, required=True)

    execute = sub.add_parser("execute-request")
    execute.add_argument("--request-json", type=Path, required=True)
    execute.add_argument("--output-json", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "validate-static":
        result = validate_static_executor()
        print("WP9_R066_CAMPAIGN_RUNTIME_EXECUTOR_STATIC=PASS")
        for key in (
            "campaign_cell_count",
            "runtime_family_count",
            "production_runtime_executor_bound",
            "source_harness_blob_identity_enforced",
            "post_readiness_seed_commit_enforced",
            "pre_readiness_failure_can_remain_seed_unconsumed",
            "e3_runtime_policy_compatibility_intercepted",
            "one_source_harness_invocation_per_trial",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "campaign_runtime_authorized",
            "campaign_wide_execution_authorized",
        ):
            value = result[key]
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
        return 0
    if args.command == "mark-seed":
        mark_seed_consumed()
        return 0
    if args.command == "shim-plan":
        shim_plan(family=args.family, output_json=args.output_json)
        return 0
    if args.command == "shim-select-policy":
        shim_select_policy(plan_json=args.plan_json, output_json=args.output_json)
        return 0
    if args.command == "shim-finalize":
        shim_finalize(
            family=args.family,
            measurement_json=args.measurement_json,
            output_json=args.output_json,
        )
        return 0
    result = execute_request(_load(args.request_json))
    _write(args.output_json, result)
    print("WP9_R066_FINAL_CAMPAIGN_SINGLE_TRIAL_EXECUTOR_RETURN")
    print("run_id=" + result["run_id"])
    print("campaign_seed=" + str(result["campaign_seed"]))
    print("cell_id=" + result["cell_id"])
    print("attempt_status=" + str(result["attempt_status"]))
    print("source_harness_invocation_count=1")
    print("automatic_retry_performed=false")
    print("automatic_next_case_performed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
