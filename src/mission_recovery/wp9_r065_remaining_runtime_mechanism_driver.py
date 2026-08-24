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
from .wp9_campaign_e2_adapter import _validate_measurement as _validate_e2_measurement
from .wp9_campaign_e3_adapter import (
    _p2_observation,
    _recovery_observation,
    _validate_common as _validate_e3_common,
)
from .wp9_campaign_e4_adapter import _validate_measurement as _validate_e4_measurement
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
STATIC_CLASSIFICATION = "WP9_R065_REMAINING_RUNTIME_MECHANISMS_STATIC_READY"
DRIVER_RESULT_CLASSIFICATION = "WP9_R065_REMAINING_MECHANISM_DRIVER_RESULT"
INTEGRATION_RETURN_CLASSIFICATION = "WP9_R065_REMAINING_INTEGRATION_RETURN"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

CONCRETE_CASES = {f"Z{i:02d}" for i in range(2, 10)}
CASE_BINDINGS: dict[str, dict[str, Any]] = {
    "Z02": {
        "cell_id": "A21",
        "development_seed": 9942,
        "event_id": "E2",
        "runtime_family": "replay",
        "runtime_variant": "e2_replay_effect",
        "integration_signature": "e2_replay_effect",
        "harness": "run_wp9_r065_e2_mechanism.sh",
        "basis_decision": "R-057",
    },
    "Z03": {
        "cell_id": "A24",
        "development_seed": 9943,
        "event_id": "E4",
        "runtime_family": "observability",
        "runtime_variant": "e4_observability",
        "integration_signature": "e4_observability",
        "harness": "run_wp9_r065_e4_mechanism.sh",
        "basis_decision": "R-059",
    },
    "Z04": {
        "cell_id": "A13",
        "development_seed": 9944,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_command_gateway",
        "integration_signature": "e3_command_gateway",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
    "Z05": {
        "cell_id": "A11",
        "development_seed": 9945,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery",
        "integration_signature": "e3_trusted_recovery",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
    "Z06": {
        "cell_id": "A15",
        "development_seed": 9946,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery_reduced_evidence",
        "integration_signature": "e3_trusted_recovery_reduced_evidence",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
    "Z07": {
        "cell_id": "A16",
        "development_seed": 9947,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_ground_authorized_recovery",
        "integration_signature": "e3_ground_authorized_recovery:C0",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
    "Z08": {
        "cell_id": "A17",
        "development_seed": 9948,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_ground_authorized_recovery",
        "integration_signature": "e3_ground_authorized_recovery:C1",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
    "Z09": {
        "cell_id": "A18",
        "development_seed": 9949,
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery_contact_delay",
        "integration_signature": "e3_trusted_recovery_contact_delay",
        "harness": "run_wp9_r065_e3_mechanism.sh",
        "basis_decision": "R-063",
    },
}

BASIS_SCRIPTS = {
    "R-057": ROOT / "scripts" / "run_wp9_r057_e2_route_validation.sh",
    "R-059": ROOT / "scripts" / "run_wp9_r059_e4_route_validation.sh",
    "R-063": ROOT / "scripts" / "run_wp9_r063_e3_route_validation.sh",
}
BASIS_SCRIPT_BLOBS = {
    "R-057": "4530cde131dd5a27454411d9e39f99e36c58b211",
    "R-059": "c51e254e1d00f6b59dbd33f6130eda8ff506bae1",
    "R-063": "76193d768ee48bfc5748f5fc6c12675d8057456e",
}
FAMILY_HARNESSES = {
    "replay": ROOT / "scripts" / "run_wp9_r065_e2_mechanism.sh",
    "observability": ROOT / "scripts" / "run_wp9_r065_e4_mechanism.sh",
    "recovery": ROOT / "scripts" / "run_wp9_r065_e3_mechanism.sh",
}


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
    target.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_replace(path: Path | str, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _binding(case_id: str) -> dict[str, Any]:
    if case_id not in CASE_BINDINGS:
        raise PermissionError("R-065 remaining mechanism driver supports Z02-Z09 only")
    return copy.deepcopy(CASE_BINDINGS[case_id])


def _validate_request(request: dict[str, Any]) -> dict[str, Any]:
    validated = validate_execution_request(request)
    case_id = str(validated["case_id"])
    binding = _binding(case_id)
    _require(validated["cell_id"] == binding["cell_id"], f"{case_id} cell binding changed")
    _require(
        int(validated["development_seed"]) == int(binding["development_seed"]),
        f"{case_id} development seed changed",
    )
    for key in ("event_id", "runtime_family", "runtime_variant", "integration_signature"):
        _require(validated[key] == binding[key], f"{case_id} {key} changed")
    _require(validated["development_validation_only"] is True, "R-065 request escaped development validation")
    _require(validated["single_case_runtime_authorization_validated"] is True, "R-065 request lacks exact single-case authorization")
    _require(validated["one_case_per_invocation"] is True, "R-065 request invocation boundary changed")
    _require(validated["driver_invocation_limit"] == 1, "R-065 driver invocation limit changed")
    _require(validated["automatic_retry_allowed"] is False, "R-065 request permits automatic retry")
    _require(validated["automatic_next_case_allowed"] is False, "R-065 request permits automatic next case")
    return validated


def _runtime_decision(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validated = _validate_request(request)
    factor = validated["factor_context"]
    event = materialize_event(
        validated["event_id"],
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    _require(event == validated["event_instance"], "R-065 retained event instance changed")
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(decision["oracle_ground_truth_read"] is False, "R-065 policy read immutable ground truth")
    _require(
        decision["delegated_policy_id"] == validated["actual_effective_policy_id"],
        "R-065 runtime effective policy differs from authorized request",
    )
    _require(
        decision["selected_action"] == validated["selected_action"],
        "R-065 selected action differs from authorized request",
    )
    return event, decision


def validate_static_remaining_mechanisms() -> dict[str, Any]:
    upstream = validate_static_executor()
    _require(upstream["decision_id"] == DECISION_ID, "R-065 executor decision changed")
    _require(upstream["production_integration_executor_bound"] is True, "R-065 production integration executor is not bound")
    _require(upstream["development_runtime_execution_authorized"] is False, "static validation inherited runtime authorization")
    _require(upstream["runtime_execution_performed"] is False, "static validation followed hidden runtime")

    _require(set(CASE_BINDINGS) == CONCRETE_CASES, "R-065 remaining case set changed")
    _require(len(FAMILY_HARNESSES) == 3, "R-065 remaining mechanisms require exactly three family harnesses")

    for decision_id, path in BASIS_SCRIPTS.items():
        _require(path.is_file(), f"{decision_id} basis harness missing")
        _require(
            _git_blob_sha(path) == BASIS_SCRIPT_BLOBS[decision_id],
            f"{decision_id} validated basis harness blob changed",
        )

    for family, path in FAMILY_HARNESSES.items():
        _require(path.is_file(), f"R-065 {family} family harness missing")
        source = path.read_text(encoding="utf-8")
        for marker in (
            "results/wp9/development/r065/integration",
            "automatic_retry_allowed=false",
            "automatic_next_case_allowed=false",
            "campaign_seed_consumed=false",
            "campaign_data_generated=false",
        ):
            _require(marker in source, f"R-065 {family} harness marker missing: {marker}")
        _require("results/wp9/campaign" not in source, f"R-065 {family} harness references campaign evidence")

    for case_id, binding in CASE_BINDINGS.items():
        frozen = INTEGRATION_CASES[case_id]
        _require(frozen["cell_id"] == binding["cell_id"], f"{case_id} frozen cell changed")
        _require(
            int(frozen["development_seed"]) == int(binding["development_seed"]),
            f"{case_id} frozen development seed changed",
        )
        plan = build_integration_plan(
            case_id=case_id,
            run_id=f"r065-{case_id.lower()}-static",
            repo_commit="a" * 40,
        )
        for key in ("event_id", "runtime_family", "runtime_variant", "integration_signature"):
            _require(plan[key] == binding[key], f"{case_id} frozen {key} changed")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": STATIC_CLASSIFICATION,
        "concrete_case_count": 8,
        "concrete_cases": sorted(CONCRETE_CASES),
        "development_seeds": [CASE_BINDINGS[c]["development_seed"] for c in sorted(CONCRETE_CASES)],
        "family_harness_count": 3,
        "basis_script_blobs": copy.deepcopy(BASIS_SCRIPT_BLOBS),
        "measurement_contracts": {
            "Z02": "R-056_E2_raw_measurement_validator",
            "Z03": "R-058_E4_raw_measurement_validator",
            "Z04-Z09": "R-062_E3_raw_measurement_validators",
        },
        "one_case_per_invocation": True,
        "mechanism_subprocess_invocation_limit": 1,
        "unexpected_scientific_outcome_retained": True,
        "treatment_fidelity_failure_retained": True,
        "development_runtime_execution_authorized": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "final_campaign_execution_authorized": False,
    }


def build_authorized_request(
    *,
    case_id: str,
    run_id: str,
    current_repo_sha: str,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    validate_static_remaining_mechanisms()
    binding = _binding(case_id)
    env = os.environ if environ is None else environ
    if env.get("WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED") != "1":
        raise PermissionError("R-065 development runtime authorization is not granted")
    if env.get("WP9_R065_AUTHORIZED_CASE") != case_id:
        raise PermissionError(f"R-065 runtime authorization is not for {case_id}")
    if env.get("WP9_R065_AUTHORIZED_SEED") != str(binding["development_seed"]):
        raise PermissionError(f"R-065 runtime authorization is not for seed {binding['development_seed']}")
    if COMMIT_PATTERN.fullmatch(current_repo_sha) is None:
        raise ValueError("R-065 current repository SHA must be lowercase 40-hex")
    if env.get("WP9_R065_AUTHORIZED_REPO_SHA") != current_repo_sha:
        raise ValueError("R-065 authorization SHA does not match current repository SHA")
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("R-065 run_id contains unsupported characters")

    plan = build_integration_plan(case_id=case_id, run_id=run_id, repo_commit=current_repo_sha)
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = True
    request = build_execution_request(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    return _validate_request(request)


def build_mechanism_invocation(
    *,
    request: dict[str, Any],
    root: Path = ROOT,
) -> dict[str, Any]:
    validated = _validate_request(request)
    binding = _binding(validated["case_id"])
    evidence = root / validated["evidence_directory"]
    expected_root = root / "results/wp9/development/r065/integration"
    _require(str(evidence).startswith(str(expected_root)), "R-065 evidence escaped development namespace")
    request_json = evidence / "immutable-ground" / "r065-execution-request.json"
    result_json = evidence / "runtime-observation" / f"{validated['case_id'].lower()}-driver-result.json"
    harness = root / "scripts" / binding["harness"]
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


def _base_result(
    request: dict[str, Any],
    decision: dict[str, Any],
    *,
    outcome_matches: bool,
) -> dict[str, Any]:
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": DRIVER_RESULT_CLASSIFICATION,
        "case_id": request["case_id"],
        "run_id": request["run_id"],
        "repo_commit": request["repo_commit"],
        "cell_id": request["cell_id"],
        "development_seed": int(request["development_seed"]),
        "development_seed_consumed": True,
        "event_id": request["event_id"],
        "runtime_family": request["runtime_family"],
        "runtime_variant": request["runtime_variant"],
        "integration_signature": request["integration_signature"],
        "requested_policy_id": request["factor_context"]["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": False,
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


def finalize_case_measurement(
    *,
    request: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validated = _validate_request(request)
    event, decision = _runtime_decision(validated)
    case_id = validated["case_id"]

    if case_id == "Z02":
        observed = _validate_e2_measurement(
            plan=validated,
            decision=decision,
            measurement=measurement,
        )
        replay_delta = int(observed["replay_delta"])
        expected_delta = 0
        outcome_matches = replay_delta == expected_delta
        result = _base_result(validated, decision, outcome_matches=outcome_matches)
        result.update({
            "setup_reset_marker_delta": int(observed["setup_delta"]),
            "intervening_authorized_noop_marker_delta": int(observed["intervening_delta"]),
            "post_replay_reset_marker_delta": replay_delta,
            "post_response_authorized_noop_marker_delta": int(observed["legitimate_delta"]),
            "replay_gateway_forwarded": bool(observed["replay_forwarded"]),
            "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
            "expected_replay_reset_marker_delta_for_acceptance_only": expected_delta,
            "post_event_analysis_horizon_s": 30,
        })
        return result

    if case_id == "Z03":
        observed = _validate_e4_measurement(
            plan=validated,
            decision=decision,
            measurement=measurement,
        )
        post_visible = int(observed["post_visible_delta"])
        legitimate_delta = int(observed["legitimate_delta"])
        expected_visible = 0
        expected_legitimate = 1 if decision["selected_action"] == "OBSERVE_ONLY" else 0
        outcome_matches = post_visible == expected_visible and legitimate_delta == expected_legitimate
        result = _base_result(validated, decision, outcome_matches=outcome_matches)
        result.update({
            "event_truth_high_value_delta": int(observed["event_truth_delta"]),
            "event_policy_visible_high_value_delta": int(observed["event_visible_delta"]),
            "post_response_truth_high_value_delta": int(observed["post_truth_delta"]),
            "post_response_policy_visible_high_value_delta": post_visible,
            "post_response_authorized_noop_marker_delta": legitimate_delta,
            "authorized_noop_gateway_forwarded": bool(observed["noop_forwarded"]),
            "expected_post_response_policy_visible_delta_for_acceptance_only": expected_visible,
            "expected_authorized_noop_marker_delta_for_acceptance_only": expected_legitimate,
            "post_event_analysis_horizon_s": 30,
            "native_spacecraft_safe_mode_claim": False,
        })
        return result

    common = _validate_e3_common(validated, measurement)
    effective = decision["delegated_policy_id"]
    if effective == "P2":
        observed = _p2_observation(decision, measurement)
        _require(
            common["complete_ns"] >= common["analysis_end_ns"],
            "R-065 unrecovered E3/P2 run did not cover 30-second horizon",
        )
    else:
        observed = _recovery_observation(
            validated,
            event,
            decision,
            common,
            measurement,
        )
    containment = bool(observed["containment"])
    noop_delta = int(observed["noop_delta"])
    expected_containment = effective in {"P5", "P6"}
    expected_noop_delta = 1
    outcome_matches = containment == expected_containment and noop_delta == expected_noop_delta
    result = _base_result(validated, decision, outcome_matches=outcome_matches)
    result.update({
        "event_activation_observed": True,
        "update_containment_observed": containment,
        "p2_command_mitigation_counts_as_update_containment": False,
        "post_response_authorized_noop_marker_delta": noop_delta,
        "trusted_recovery_confirmed": bool(observed["trusted"]),
        "ground_authorization_waited": bool(observed["ground_waited"]),
        "post_event_analysis_horizon_s": 30,
        "modeled_c1_contact_window_s": (
            10 if validated["factor_context"]["contact_condition_id"] == "C1" else None
        ),
        "expected_update_containment_for_acceptance_only": expected_containment,
        "expected_authorized_noop_marker_delta_for_acceptance_only": expected_noop_delta,
        "policy_selection_not_gated_on_event_success": True,
        "runner_duration_used_as_metric_input": False,
    })
    if effective == "P2":
        result.update({
            "matched_attacker_probe_count": int(measurement["matched_attacker_probe_count"]),
            "attacker_gateway_forwarded_count": int(measurement["attacker_gateway_forwarded_count"]),
            "authorized_noop_gateway_forwarded": bool(measurement["authorized_noop_gateway_forwarded"]),
            "observed_post_enforcement_attacker_reset_marker_delta": int(
                measurement["observed_post_enforcement_attacker_reset_marker_delta"]
            ),
        })
    if effective == "P6":
        result.update({
            "authorization_available_at_response_boundary": bool(
                measurement["authorization_available_at_response_boundary"]
            ),
            "missed_contact_windows_observed": int(measurement["missed_contact_windows_observed"]),
            "ground_authorization_source": measurement["ground_authorization_source"],
            "post_authorization_delegate": measurement["post_authorization_delegate"],
        })
    return result


def _concrete_driver(request: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    invocation = build_mechanism_invocation(request=request, root=root)
    _write_new(invocation["request_json"], _validate_request(request))
    completed = subprocess.run(invocation["command"], cwd=root, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"R-065 {request['case_id']} concrete mechanism failed with rc={completed.returncode}; "
            "no retry or next case was attempted"
        )
    if not invocation["result_json"].is_file():
        raise RuntimeError(f"R-065 {request['case_id']} mechanism completed without driver result")
    return _load(invocation["result_json"])


def execute_case(
    *,
    case_id: str,
    run_id: str,
    current_repo_sha: str,
    environ: Mapping[str, str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    request = build_authorized_request(
        case_id=case_id,
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

    finalize = sub.add_parser("finalize-case")
    finalize.add_argument("--request-json", type=Path, required=True)
    finalize.add_argument("--measurement-json", type=Path, required=True)
    finalize.add_argument("--output-json", type=Path, required=True)

    execute = sub.add_parser("execute-case")
    execute.add_argument("--case-id", choices=sorted(CONCRETE_CASES), required=True)
    execute.add_argument("--run-id", required=True)
    execute.add_argument("--repo-commit", required=True)

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_remaining_mechanisms()
        print("WP9_R065_REMAINING_RUNTIME_MECHANISMS_STATIC=PASS")
        print("concrete_case_count=" + str(result["concrete_case_count"]))
        print("concrete_cases=" + ",".join(result["concrete_cases"]))
        print("development_seeds=" + ",".join(str(x) for x in result["development_seeds"]))
        print("family_harness_count=" + str(result["family_harness_count"]))
        print("one_case_per_invocation=true")
        print("mechanism_subprocess_invocation_limit=1")
        print("development_runtime_execution_authorized=false")
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        print("final_campaign_execution_authorized=false")
        return 0

    if args.command == "validate-request":
        request = _validate_request(_load(args.request_json))
        print("WP9_R065_REMAINING_EXECUTION_REQUEST=PASS")
        print("case_id=" + request["case_id"])
        print("cell_id=" + request["cell_id"])
        print("development_seed=" + str(request["development_seed"]))
        print("repo_commit=" + request["repo_commit"])
        return 0

    if args.command == "finalize-case":
        result = finalize_case_measurement(
            request=_load(args.request_json),
            measurement=_load(args.measurement_json),
        )
        _write_replace(args.output_json, result)
        print("WP9_R065_REMAINING_MECHANISM_OBSERVATION=PASS")
        print("case_id=" + result["case_id"])
        print("treatment_fidelity_valid=true")
        print(
            "outcome_matches_predeclared_expectation="
            + str(result["outcome_matches_predeclared_expectation"]).lower()
        )
        print("automatic_retry_performed=false")
        print("automatic_next_case_performed=false")
        return 0

    result = execute_case(
        case_id=args.case_id,
        run_id=args.run_id,
        current_repo_sha=args.repo_commit,
    )
    print("WP9_R065_BOUNDED_RUNTIME_INTEGRATION=PASS")
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
