from __future__ import annotations

import argparse
import copy
import json
from functools import lru_cache
from typing import Any, Callable

from .wp9_r065_bounded_runtime_integration import (
    EXPECTED_INTEGRATION_SIGNATURES,
    INTEGRATION_CASES,
    build_executor_descriptor,
    build_integration_plan,
    validate_static_integration,
)

DECISION_ID = "R-065"
STATIC_CLASSIFICATION = "WP9_R065_PRODUCTION_INTEGRATION_EXECUTOR_STATIC_READY"
REQUEST_CLASSIFICATION = "WP9_R065_PRODUCTION_INTEGRATION_EXECUTION_REQUEST"
RETURN_CLASSIFICATION = "WP9_R065_PRODUCTION_INTEGRATION_EXECUTOR_RETURN"

Driver = Callable[[dict[str, Any]], dict[str, Any]]

MECHANISM_BINDINGS: dict[str, dict[str, str]] = {
    "e1_command_gateway": {
        "event_id": "E1",
        "runtime_family": "command",
        "runtime_variant": "e1_command_gateway",
        "campaign_observation_adapter_decision_id": "R-060",
        "prior_runtime_validation_decision_id": "R-061",
    },
    "e2_replay_effect": {
        "event_id": "E2",
        "runtime_family": "replay",
        "runtime_variant": "e2_replay_effect",
        "campaign_observation_adapter_decision_id": "R-056",
        "prior_runtime_validation_decision_id": "R-057",
    },
    "e4_observability": {
        "event_id": "E4",
        "runtime_family": "observability",
        "runtime_variant": "e4_observability",
        "campaign_observation_adapter_decision_id": "R-058",
        "prior_runtime_validation_decision_id": "R-059",
    },
    "e3_command_gateway": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_command_gateway",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
    "e3_trusted_recovery": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
    "e3_trusted_recovery_reduced_evidence": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery_reduced_evidence",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
    "e3_ground_authorized_recovery:C0": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_ground_authorized_recovery",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
    "e3_ground_authorized_recovery:C1": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_ground_authorized_recovery",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
    "e3_trusted_recovery_contact_delay": {
        "event_id": "E3",
        "runtime_family": "recovery",
        "runtime_variant": "e3_trusted_recovery_contact_delay",
        "campaign_observation_adapter_decision_id": "R-062",
        "prior_runtime_validation_decision_id": "R-063",
    },
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _binding_for_signature(signature: str) -> dict[str, str]:
    try:
        return copy.deepcopy(MECHANISM_BINDINGS[signature])
    except KeyError as exc:
        raise ValueError(
            f"R-065 production executor has no mechanism binding: {signature}"
        ) from exc


@lru_cache(maxsize=1)
def _validated_static_executor() -> dict[str, Any]:
    base = validate_static_integration()
    _require(base["decision_id"] == DECISION_ID, "R-065 base preparation changed")
    _require(
        base["production_runtime_executor_bound"] is False,
        "R-065 production executor preparation boundary changed",
    )
    _require(
        base["runtime_execution_performed"] is False,
        "R-065 static executor validation cannot follow runtime execution",
    )
    _require(
        set(MECHANISM_BINDINGS) == EXPECTED_INTEGRATION_SIGNATURES,
        "R-065 production executor signature coverage changed",
    )

    observed_cases: set[str] = set()
    observed_signatures: set[str] = set()
    observed_events: set[str] = set()
    observed_variants: set[str] = set()

    for case_id in sorted(INTEGRATION_CASES):
        plan = build_integration_plan(
            case_id=case_id,
            run_id=f"r065-static-{case_id.lower()}",
            repo_commit="a" * 40,
        )
        binding = _binding_for_signature(plan["integration_signature"])
        _require(
            binding["event_id"] == plan["event_id"],
            f"{case_id}: event binding changed",
        )
        _require(
            binding["runtime_family"] == plan["runtime_family"],
            f"{case_id}: runtime family binding changed",
        )
        _require(
            binding["runtime_variant"] == plan["runtime_variant"],
            f"{case_id}: runtime variant binding changed",
        )
        _require(
            binding["campaign_observation_adapter_decision_id"]
            == plan["campaign_observation_adapter_decision_id"],
            f"{case_id}: observation adapter binding changed",
        )
        _require(
            binding["prior_runtime_validation_decision_id"]
            == plan["prior_runtime_validation_decision_id"],
            f"{case_id}: prior runtime validation binding changed",
        )
        observed_cases.add(case_id)
        observed_signatures.add(plan["integration_signature"])
        observed_events.add(plan["event_id"])
        observed_variants.add(plan["runtime_variant"])

    _require(observed_cases == set(INTEGRATION_CASES), "R-065 case coverage changed")
    _require(
        observed_signatures == EXPECTED_INTEGRATION_SIGNATURES,
        "R-065 signature coverage changed",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": STATIC_CLASSIFICATION,
        "integration_case_count": len(observed_cases),
        "runtime_variant_count": len(observed_variants),
        "integration_signature_count": len(observed_signatures),
        "event_family_count": len(observed_events),
        "production_integration_executor_bound": True,
        "mechanism_binding_count": len(MECHANISM_BINDINGS),
        "mechanism_driver_interface": "single_injected_callable_per_invocation",
        "one_case_per_invocation": True,
        "driver_invocation_limit": 1,
        "unexpected_scientific_outcome_retained": True,
        "treatment_fidelity_failure_retained": True,
        "development_runtime_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def validate_static_executor() -> dict[str, Any]:
    return copy.deepcopy(_validated_static_executor())


def build_execution_request(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    current_repo_sha: str,
) -> dict[str, Any]:
    validate_static_executor()
    descriptor = build_executor_descriptor(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    binding = _binding_for_signature(str(descriptor["integration_signature"]))

    _require(
        binding["event_id"] == descriptor["event_id"],
        "R-065 descriptor event mismatch",
    )
    _require(
        binding["runtime_family"] == descriptor["runtime_family"],
        "R-065 descriptor runtime family mismatch",
    )
    _require(
        binding["runtime_variant"] == descriptor["runtime_variant"],
        "R-065 descriptor runtime variant mismatch",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": REQUEST_CLASSIFICATION,
        "case_id": descriptor["case_id"],
        "run_id": descriptor["run_id"],
        "repo_commit": descriptor["repo_commit"],
        "cell_id": descriptor["cell_id"],
        "development_seed": int(descriptor["development_seed"]),
        "event_id": descriptor["event_id"],
        "runtime_family": descriptor["runtime_family"],
        "runtime_variant": descriptor["runtime_variant"],
        "integration_signature": descriptor["integration_signature"],
        "mechanism_binding": binding,
        "factor_context": copy.deepcopy(plan["factor_context"]),
        "event_instance": copy.deepcopy(plan["event_instance"]),
        "requested_policy_id": plan["requested_policy_id"],
        "actual_effective_policy_id": plan["actual_effective_policy_id"],
        "selected_action": plan["selected_action"],
        "expected_values_role": plan["expected_values_role"],
        "common_post_event_analysis_horizon_s": descriptor[
            "common_post_event_analysis_horizon_s"
        ],
        "modeled_c1_contact_window_s": descriptor[
            "modeled_c1_contact_window_s"
        ],
        "p6_authorization_release_after_event_s": descriptor[
            "p6_authorization_release_after_event_s"
        ],
        "ground_authorization_wait_required": descriptor[
            "ground_authorization_wait_required"
        ],
        "evidence_directory": descriptor["evidence_directory"],
        "claim_boundaries": copy.deepcopy(plan["claim_boundaries"]),
        "development_validation_only": True,
        "single_case_runtime_authorization_validated": True,
        "one_case_per_invocation": True,
        "driver_invocation_limit": 1,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def validate_execution_request(request: dict[str, Any]) -> dict[str, Any]:
    _require(
        request.get("decision_id") == DECISION_ID,
        "not an R-065 execution request",
    )
    _require(
        request.get("classification") == REQUEST_CLASSIFICATION,
        "R-065 request classification changed",
    )
    case_id = str(request.get("case_id"))
    _require(case_id in INTEGRATION_CASES, "R-065 request case changed")
    expected = INTEGRATION_CASES[case_id]
    _require(
        request.get("cell_id") == expected["cell_id"],
        "R-065 request cell mismatch",
    )
    _require(
        int(request.get("development_seed")) == int(expected["development_seed"]),
        "R-065 request development seed mismatch",
    )
    signature = str(request.get("integration_signature"))
    binding = _binding_for_signature(signature)
    _require(
        request.get("mechanism_binding") == binding,
        "R-065 mechanism binding mismatch",
    )
    _require(
        request.get("event_id") == binding["event_id"],
        "R-065 request event mismatch",
    )
    _require(
        request.get("runtime_family") == binding["runtime_family"],
        "R-065 request runtime family mismatch",
    )
    _require(
        request.get("runtime_variant") == binding["runtime_variant"],
        "R-065 request runtime variant mismatch",
    )
    evidence = str(request.get("evidence_directory", ""))
    _require(
        evidence.startswith("results/wp9/development/r065/integration/"),
        "R-065 production request escaped development evidence namespace",
    )
    _require(
        "results/wp9/campaign" not in evidence,
        "R-065 production request entered campaign namespace",
    )
    _require(
        request.get("development_validation_only") is True,
        "R-065 request is not development-only",
    )
    _require(
        request.get("single_case_runtime_authorization_validated") is True,
        "R-065 request lacks exact single-case authorization",
    )
    _require(
        request.get("one_case_per_invocation") is True,
        "R-065 request invocation boundary changed",
    )
    _require(
        request.get("driver_invocation_limit") == 1,
        "R-065 driver invocation limit changed",
    )
    _require(
        request.get("automatic_retry_allowed") is False,
        "R-065 request allows automatic retry",
    )
    _require(
        request.get("automatic_next_case_allowed") is False,
        "R-065 request allows automatic next case",
    )
    _require(
        request.get("campaign_seed_consumed") is False,
        "R-065 request consumed campaign seed",
    )
    _require(
        request.get("campaign_data_generated") is False,
        "R-065 request generated campaign data",
    )
    _require(
        request.get("final_campaign_execution_authorized") is False,
        "R-065 request authorizes final campaign",
    )
    return copy.deepcopy(request)


def _validate_driver_result(
    *,
    request: dict[str, Any],
    result: dict[str, Any],
) -> None:
    for key in (
        "case_id",
        "run_id",
        "cell_id",
        "event_id",
        "runtime_variant",
    ):
        _require(
            result.get(key) == request[key],
            f"R-065 driver result {key} mismatch",
        )
    _require(
        int(result.get("development_seed")) == int(request["development_seed"]),
        "R-065 driver result development seed mismatch",
    )
    _require(
        result.get("campaign_seed_consumed") is False,
        "R-065 driver result consumed campaign seed",
    )
    _require(
        result.get("campaign_data_generated") is False,
        "R-065 driver result generated campaign data",
    )
    _require(
        result.get("final_campaign_execution_authorized") is False,
        "R-065 driver result authorized final campaign",
    )
    _require(
        result.get("automatic_retry_performed") is False,
        "R-065 driver performed automatic retry",
    )
    _require(
        result.get("automatic_next_case_performed") is False,
        "R-065 driver performed automatic next case",
    )


def execute_request(
    *,
    request: dict[str, Any],
    driver: Driver,
) -> dict[str, Any]:
    validated = validate_execution_request(request)
    result = driver(copy.deepcopy(validated))
    _require(isinstance(result, dict), "R-065 driver result must be an object")
    _validate_driver_result(request=validated, result=result)

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": RETURN_CLASSIFICATION,
        "case_id": validated["case_id"],
        "run_id": validated["run_id"],
        "cell_id": validated["cell_id"],
        "development_seed": int(validated["development_seed"]),
        "integration_signature": validated["integration_signature"],
        "driver_invocation_count": 1,
        "driver_result": copy.deepcopy(result),
        "unexpected_scientific_outcome_retained": True,
        "treatment_fidelity_failure_retained": True,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "runtime_execution_performed": bool(
            result.get("runtime_execution_performed", False)
        ),
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")
    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_executor()
        print("WP9_R065_PRODUCTION_INTEGRATION_EXECUTOR_STATIC=PASS")
        for key in (
            "integration_case_count",
            "runtime_variant_count",
            "integration_signature_count",
            "event_family_count",
            "production_integration_executor_bound",
            "mechanism_binding_count",
            "one_case_per_invocation",
            "driver_invocation_limit",
            "unexpected_scientific_outcome_retained",
            "treatment_fidelity_failure_retained",
            "development_runtime_execution_authorized",
            "automatic_retry_allowed",
            "automatic_next_case_allowed",
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            value = result[key]
            if isinstance(value, bool):
                value = str(value).lower()
            print(f"{key}={value}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
