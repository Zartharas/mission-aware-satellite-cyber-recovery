from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .events import materialize_event
from .wp9_campaign_e1_adapter import (
    _expected_gateway_treatment,
    _validate_measurement,
)
from .wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    INTEGRATION_CASES,
    build_authorization_request,
    build_integration_plan,
)
from .wp9_r065_production_integration_executor import (
    build_execution_request,
    execute_request,
    validate_execution_request,
    validate_static_executor,
)
from .wp9_static_contracts import evaluate_wp9_policy

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-065"
STATIC_CLASSIFICATION = "WP9_R065_CONCRETE_RUNTIME_MECHANISM_DRIVER_STATIC_READY"
DRIVER_RESULT_CLASSIFICATION = "WP9_R065_Z01_E1_MECHANISM_DRIVER_RESULT"
INTEGRATION_RETURN_CLASSIFICATION = "WP9_R065_Z01_INTEGRATION_RETURN"

CONCRETE_CASES = {"Z01"}
REMAINING_CASES = tuple(f"Z{i:02d}" for i in range(2, 10))
Z01_CELL_ID = "A06"
Z01_DEVELOPMENT_SEED = 9941
Z01_RUNTIME_VARIANT = "e1_command_gateway"
Z01_RUNTIME_FAMILY = "command"
PINNED_NOS3_IMAGE = (
    "ivvitc/nos3-64@sha256:"
    "06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
)

BASIS_R061_E1_SCRIPT = ROOT / "scripts" / "run_wp9_r061_e1_route_validation.sh"
BASIS_R061_E1_GIT_BLOB_SHA = "5a4596cfbe5941dbaeb833c802d68258343e7f9a"
Z01_MECHANISM_SCRIPT = ROOT / "scripts" / "run_wp9_r065_z01_e1_mechanism.sh"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_new(path: Path | str, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"R-065 refuses to overwrite retained evidence: {target}")
    target.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_replace(path: Path | str, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_z01_request(request: dict[str, Any]) -> dict[str, Any]:
    validated = validate_execution_request(request)
    if validated["case_id"] != "Z01":
        raise PermissionError(
            "R-065 concrete runtime mechanism driver supports Z01 only; "
            "Z02-Z09 remain fail-closed"
        )
    _require(validated["cell_id"] == Z01_CELL_ID, "Z01 cell binding changed")
    _require(
        int(validated["development_seed"]) == Z01_DEVELOPMENT_SEED,
        "Z01 development seed changed",
    )
    _require(validated["event_id"] == "E1", "Z01 event binding changed")
    _require(
        validated["runtime_family"] == Z01_RUNTIME_FAMILY,
        "Z01 runtime family changed",
    )
    _require(
        validated["runtime_variant"] == Z01_RUNTIME_VARIANT,
        "Z01 runtime variant changed",
    )
    _require(
        validated["integration_signature"] == Z01_RUNTIME_VARIANT,
        "Z01 integration signature changed",
    )
    _require(
        validated["development_validation_only"] is True,
        "Z01 request escaped development validation",
    )
    _require(
        validated["single_case_runtime_authorization_validated"] is True,
        "Z01 request lacks single-case authorization",
    )
    _require(
        validated["automatic_retry_allowed"] is False,
        "Z01 request permits automatic retry",
    )
    _require(
        validated["automatic_next_case_allowed"] is False,
        "Z01 request permits automatic next case",
    )
    return validated


def validate_static_mechanism_driver() -> dict[str, Any]:
    upstream = validate_static_executor()
    _require(upstream["decision_id"] == DECISION_ID, "R-065 executor decision changed")
    _require(
        upstream["production_integration_executor_bound"] is True,
        "R-065 production integration executor is not bound",
    )
    _require(
        upstream["development_runtime_execution_authorized"] is False,
        "static concrete-driver validation cannot inherit runtime authorization",
    )
    _require(
        upstream["runtime_execution_performed"] is False,
        "static concrete-driver validation cannot follow runtime execution",
    )

    z01 = INTEGRATION_CASES["Z01"]
    _require(z01 == {"cell_id": Z01_CELL_ID, "development_seed": Z01_DEVELOPMENT_SEED}, "Z01 binding changed")
    _require(BASIS_R061_E1_SCRIPT.is_file(), "validated R-061 E1 harness is missing")
    _require(
        _git_blob_sha(BASIS_R061_E1_SCRIPT) == BASIS_R061_E1_GIT_BLOB_SHA,
        "validated R-061 E1 harness blob changed",
    )
    _require(Z01_MECHANISM_SCRIPT.is_file(), "R-065 Z01 mechanism harness is missing")

    source = Z01_MECHANISM_SCRIPT.read_text(encoding="utf-8")
    required_markers = (
        'CASE_ID="Z01"',
        'CELL_ID="A06"',
        'SEED="9941"',
        f'IMAGE="{PINNED_NOS3_IMAGE}"',
        "src.mission_recovery.nos3_e1_adapter",
        "modeled_attacker sample_reset_counters",
        "authorized_ground sample_noop",
        "EVENT_ACTIVATION_NS + 30 * 1000000000",
        "results/wp9/development/r065/integration",
        "automatic_retry_allowed=false",
        "automatic_next_case_allowed=false",
        "campaign_seed_consumed=false",
        "campaign_data_generated=false",
    )
    for marker in required_markers:
        _require(marker in source, f"R-065 Z01 harness marker missing: {marker}")
    _require("results/wp9/campaign" not in source, "Z01 harness references campaign evidence")
    _require('SEED="9924"' not in source, "Z01 harness retained R-061 seed 9924")
    _require("X04" not in source, "Z01 harness retained R-061 case identity")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": STATIC_CLASSIFICATION,
        "concrete_case_count": 1,
        "concrete_cases": ["Z01"],
        "remaining_cases": list(REMAINING_CASES),
        "cell_id": Z01_CELL_ID,
        "development_seed": Z01_DEVELOPMENT_SEED,
        "runtime_family": Z01_RUNTIME_FAMILY,
        "runtime_variant": Z01_RUNTIME_VARIANT,
        "basis_runtime_validation_decision_id": "R-061",
        "basis_r061_e1_git_blob_sha": BASIS_R061_E1_GIT_BLOB_SHA,
        "pinned_nos3_image": PINNED_NOS3_IMAGE,
        "one_case_per_invocation": True,
        "mechanism_subprocess_invocation_limit": 1,
        "unexpected_scientific_outcome_retained": True,
        "treatment_fidelity_failure_retained": True,
        "development_runtime_execution_authorized": False,
        "runtime_execution_performed": False,
        "development_seed_consumed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "final_campaign_execution_authorized": False,
    }


def build_z01_authorized_request(
    *,
    run_id: str,
    current_repo_sha: str,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    validate_static_mechanism_driver()
    env = os.environ if environ is None else environ
    if env.get("WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED") != "1":
        raise PermissionError("R-065 Z01 development runtime authorization is not granted")
    if env.get("WP9_R065_AUTHORIZED_CASE") != "Z01":
        raise PermissionError("R-065 runtime authorization is not for Z01")
    if env.get("WP9_R065_AUTHORIZED_SEED") != str(Z01_DEVELOPMENT_SEED):
        raise PermissionError("R-065 runtime authorization is not for seed 9941")
    if COMMIT_PATTERN.fullmatch(current_repo_sha) is None:
        raise ValueError("R-065 current repository SHA must be lowercase 40-hex")
    if env.get("WP9_R065_AUTHORIZED_REPO_SHA") != current_repo_sha:
        raise ValueError("R-065 authorization SHA does not match current repository SHA")
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("R-065 Z01 run_id contains unsupported characters")

    plan = build_integration_plan(
        case_id="Z01",
        run_id=run_id,
        repo_commit=current_repo_sha,
    )
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = True
    request = build_execution_request(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    return _validate_z01_request(request)


def build_mechanism_invocation(
    *,
    request: dict[str, Any],
    root: Path = ROOT,
) -> dict[str, Any]:
    validated = _validate_z01_request(request)
    evidence = root / validated["evidence_directory"]
    _require(
        str(evidence).startswith(str(root / "results/wp9/development/r065/integration")),
        "Z01 evidence escaped R-065 development namespace",
    )
    request_json = evidence / "immutable-ground" / "r065-execution-request.json"
    result_json = evidence / "runtime-observation" / "z01-driver-result.json"
    harness = root / "scripts" / "run_wp9_r065_z01_e1_mechanism.sh"
    return {
        "command": [
            "bash",
            str(harness),
            "--request-json",
            str(request_json),
            "--output-json",
            str(result_json),
        ],
        "request_json": request_json,
        "result_json": result_json,
        "evidence_directory": evidence,
        "subprocess_invocation_limit": 1,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def finalize_z01_measurement(
    *,
    request: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validated = _validate_z01_request(request)
    factor = validated["factor_context"]
    event = materialize_event(
        "E1",
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    _require(event == validated["event_instance"], "Z01 retained event instance changed")
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(decision["oracle_ground_truth_read"] is False, "Z01 policy read immutable ground truth")
    _require(
        decision["delegated_policy_id"] == validated["actual_effective_policy_id"],
        "Z01 runtime effective policy differs from authorized request",
    )
    _require(
        decision["selected_action"] == validated["selected_action"],
        "Z01 selected action differs from authorized request",
    )

    observed = _validate_measurement(
        plan=validated,
        decision=decision,
        measurement=measurement,
    )
    attacker_delta = int(observed["attacker_delta"])
    legitimate_delta = int(observed["legitimate_delta"])
    expected_attacker_forwarded, expected_authorized_forwarded = (
        _expected_gateway_treatment(decision["selected_action"])
    )
    _require(expected_attacker_forwarded == 0, "Z01 treatment must block matched attacker probes")
    expected_legitimate_delta = 1 if expected_authorized_forwarded else 0
    outcome_matches = attacker_delta == 0 and legitimate_delta == expected_legitimate_delta

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": DRIVER_RESULT_CLASSIFICATION,
        "case_id": validated["case_id"],
        "run_id": validated["run_id"],
        "repo_commit": validated["repo_commit"],
        "cell_id": validated["cell_id"],
        "development_seed": int(validated["development_seed"]),
        "development_seed_consumed": True,
        "event_id": validated["event_id"],
        "runtime_family": validated["runtime_family"],
        "runtime_variant": validated["runtime_variant"],
        "integration_signature": validated["integration_signature"],
        "requested_policy_id": factor["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": False,
        "event_activation_reset_marker_delta": int(observed["event_delta"]),
        "post_enforcement_attacker_probe_count": int(observed["attacker_count"]),
        "post_enforcement_attacker_reset_marker_delta": attacker_delta,
        "post_response_authorized_noop_marker_delta": legitimate_delta,
        "attacker_gateway_forwarded_count": int(observed["attacker_forwarded_count"]),
        "authorized_noop_gateway_forwarded": bool(observed["authorized_forwarded"]),
        "outcome_matches_predeclared_expectation": outcome_matches,
        "unexpected_scientific_outcome_retained": not outcome_matches,
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "runtime_execution_performed": True,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
    }


def _concrete_driver(request: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    invocation = build_mechanism_invocation(request=request, root=root)
    _write_new(invocation["request_json"], _validate_z01_request(request))
    completed = subprocess.run(
        invocation["command"],
        cwd=root,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"R-065 Z01 concrete mechanism failed with rc={completed.returncode}; "
            "no retry or next case was attempted"
        )
    result_path = invocation["result_json"]
    if not result_path.is_file():
        raise RuntimeError("R-065 Z01 mechanism completed without driver result")
    return _load(result_path)


def execute_z01(
    *,
    run_id: str,
    current_repo_sha: str,
    environ: Mapping[str, str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    request = build_z01_authorized_request(
        run_id=run_id,
        current_repo_sha=current_repo_sha,
        environ=environ,
    )
    result = execute_request(
        request=request,
        driver=lambda value: _concrete_driver(value, root=root),
    )
    result["classification"] = INTEGRATION_RETURN_CLASSIFICATION
    evidence = root / request["evidence_directory"]
    _write_new(evidence / "integration-return.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    validate_request = sub.add_parser("validate-request")
    validate_request.add_argument("--request-json", type=Path, required=True)

    finalize = sub.add_parser("finalize-z01")
    finalize.add_argument("--request-json", type=Path, required=True)
    finalize.add_argument("--measurement-json", type=Path, required=True)
    finalize.add_argument("--output-json", type=Path, required=True)

    execute = sub.add_parser("execute-z01")
    execute.add_argument("--run-id", required=True)
    execute.add_argument("--repo-commit", required=True)

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_mechanism_driver()
        print("WP9_R065_CONCRETE_RUNTIME_MECHANISM_DRIVER_STATIC=PASS")
        for key in (
            "concrete_case_count",
            "cell_id",
            "development_seed",
            "runtime_family",
            "runtime_variant",
            "basis_runtime_validation_decision_id",
            "basis_r061_e1_git_blob_sha",
            "one_case_per_invocation",
            "mechanism_subprocess_invocation_limit",
            "development_runtime_execution_authorized",
            "runtime_execution_performed",
            "development_seed_consumed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "final_campaign_execution_authorized",
        ):
            value = result[key]
            if isinstance(value, bool):
                value = str(value).lower()
            print(f"{key}={value}")
        print("concrete_cases=" + ",".join(result["concrete_cases"]))
        print("remaining_cases=" + ",".join(result["remaining_cases"]))
        return 0

    if args.command == "validate-request":
        request = _validate_z01_request(_load(args.request_json))
        print("WP9_R065_Z01_EXECUTION_REQUEST=PASS")
        print("case_id=" + request["case_id"])
        print("cell_id=" + request["cell_id"])
        print("development_seed=" + str(request["development_seed"]))
        print("repo_commit=" + request["repo_commit"])
        return 0

    if args.command == "finalize-z01":
        result = finalize_z01_measurement(
            request=_load(args.request_json),
            measurement=_load(args.measurement_json),
        )
        _write_replace(args.output_json, result)
        print("WP9_R065_Z01_MECHANISM_OBSERVATION=PASS")
        print("treatment_fidelity_valid=true")
        print(
            "outcome_matches_predeclared_expectation="
            + str(result["outcome_matches_predeclared_expectation"]).lower()
        )
        print("automatic_retry_performed=false")
        print("automatic_next_case_performed=false")
        return 0

    result = execute_z01(
        run_id=args.run_id,
        current_repo_sha=args.repo_commit,
    )
    print("WP9_R065_Z01_BOUNDED_RUNTIME_INTEGRATION=PASS")
    print("case_id=" + result["case_id"])
    print("cell_id=" + result["cell_id"])
    print("development_seed=" + str(result["development_seed"]))
    print("driver_invocation_count=" + str(result["driver_invocation_count"]))
    print("automatic_retry_performed=false")
    print("automatic_next_case_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    print("final_campaign_execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
