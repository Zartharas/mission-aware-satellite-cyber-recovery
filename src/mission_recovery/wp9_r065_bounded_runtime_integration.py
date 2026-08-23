from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .events import materialize_event
from .wp9_campaign_e1_runtime_adapter import (
    DEVELOPMENT_CASES as R061_DEVELOPMENT_CASES,
)
from .wp9_campaign_e2_runtime_adapter import (
    DEVELOPMENT_CASES as R057_DEVELOPMENT_CASES,
)
from .wp9_campaign_e3_runtime_adapter import (
    DEVELOPMENT_CASES as R063_DEVELOPMENT_CASES,
)
from .wp9_campaign_e4_runtime_adapter import (
    DEVELOPMENT_CASES as R059_DEVELOPMENT_CASES,
)
from .wp9_final_campaign_bridge import (
    ROUTE_CONTRACTS,
    validate_static_bridge as validate_r064_static_bridge,
)
from .wp9_static_contracts import (
    evaluate_wp9_policy,
    load_campaign_design,
    runtime_route_for_cell,
)

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-065"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

SEED_PLAN = ROOT / "configs" / "wp9_campaign_seed_plan.json"
TIMING_FREEZE = ROOT / "configs" / "wp9_precampaign_timing_freeze.json"
COMMON_HORIZON_FREEZE = (
    ROOT / "configs" / "wp9_precampaign_non_e3_horizon_freeze.json"
)

AUTHORIZATION_REQUEST_CLASSIFICATION = (
    "WP9_R065_BOUNDED_RUNTIME_INTEGRATION_AUTHORIZATION_REQUEST"
)
AUTHORIZATION_CLASSIFICATION = (
    "WP9_R065_BOUNDED_RUNTIME_INTEGRATION_AUTHORIZATION"
)

INTEGRATION_CASES: dict[str, dict[str, Any]] = {
    "Z01": {"cell_id": "A06", "development_seed": 9941},
    "Z02": {"cell_id": "A21", "development_seed": 9942},
    "Z03": {"cell_id": "A24", "development_seed": 9943},
    "Z04": {"cell_id": "A13", "development_seed": 9944},
    "Z05": {"cell_id": "A11", "development_seed": 9945},
    "Z06": {"cell_id": "A15", "development_seed": 9946},
    "Z07": {"cell_id": "A16", "development_seed": 9947},
    "Z08": {"cell_id": "A17", "development_seed": 9948},
    "Z09": {"cell_id": "A18", "development_seed": 9949},
}

EXPECTED_CASE_BINDINGS: dict[str, tuple[str, int, str, str]] = {
    "Z01": ("A06", 9941, "E1", "e1_command_gateway"),
    "Z02": ("A21", 9942, "E2", "e2_replay_effect"),
    "Z03": ("A24", 9943, "E4", "e4_observability"),
    "Z04": ("A13", 9944, "E3", "e3_command_gateway"),
    "Z05": ("A11", 9945, "E3", "e3_trusted_recovery"),
    "Z06": (
        "A15",
        9946,
        "E3",
        "e3_trusted_recovery_reduced_evidence",
    ),
    "Z07": ("A16", 9947, "E3", "e3_ground_authorized_recovery"),
    "Z08": ("A17", 9948, "E3", "e3_ground_authorized_recovery"),
    "Z09": (
        "A18",
        9949,
        "E3",
        "e3_trusted_recovery_contact_delay",
    ),
}

EXPECTED_INTEGRATION_SIGNATURES = {
    "e1_command_gateway",
    "e2_replay_effect",
    "e4_observability",
    "e3_command_gateway",
    "e3_trusted_recovery",
    "e3_trusted_recovery_reduced_evidence",
    "e3_ground_authorized_recovery:C0",
    "e3_ground_authorized_recovery:C1",
    "e3_trusted_recovery_contact_delay",
}


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


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


def _cells() -> dict[str, dict[str, Any]]:
    return {
        row["cell_id"]: row
        for row in load_campaign_design()["cells"]
    }


def _event_for_cell(cell_id: str) -> str:
    matches = [
        event_id
        for event_id, contract in ROUTE_CONTRACTS.items()
        if cell_id in contract["cells"]
    ]
    _require(len(matches) == 1, f"R-065 cell route is not unique: {cell_id}")
    return matches[0]


def integration_case(case_id: str) -> dict[str, Any]:
    if case_id not in INTEGRATION_CASES:
        raise ValueError("R-065 supports Z01-Z09 only")
    return copy.deepcopy(INTEGRATION_CASES[case_id])


def _integration_signature(
    *,
    runtime_variant: str,
    contact_condition_id: str,
) -> str:
    if runtime_variant == "e3_ground_authorized_recovery":
        return f"{runtime_variant}:{contact_condition_id}"
    return runtime_variant


def _prior_validated_cells() -> set[str]:
    cases = (
        list(R061_DEVELOPMENT_CASES.values())
        + list(R057_DEVELOPMENT_CASES.values())
        + list(R059_DEVELOPMENT_CASES.values())
        + list(R063_DEVELOPMENT_CASES.values())
    )
    return {str(row["cell_id"]) for row in cases}


def _prior_route_validation_seeds() -> set[int]:
    cases = (
        list(R061_DEVELOPMENT_CASES.values())
        + list(R057_DEVELOPMENT_CASES.values())
        + list(R059_DEVELOPMENT_CASES.values())
        + list(R063_DEVELOPMENT_CASES.values())
    )
    return {int(row["development_seed"]) for row in cases}


def validate_static_integration() -> dict[str, Any]:
    r064 = validate_r064_static_bridge()
    _require(r064["decision_id"] == "R-064", "R-065 requires R-064")
    _require(
        r064["production_runtime_executor_bound"] is False,
        "R-065 static preparation must precede production executor binding",
    )
    _require(
        r064["bounded_non_campaign_seed_runtime_validation_required"] is True,
        "R-065 is no longer required by R-064",
    )
    _require(
        r064["final_campaign_execution_authorized"] is False,
        "R-065 cannot begin after final campaign authorization",
    )

    _require(
        set(INTEGRATION_CASES) == {f"Z{i:02d}" for i in range(1, 10)},
        "R-065 case IDs changed",
    )
    _require(
        len(INTEGRATION_CASES) == 9,
        "R-065 minimal integration case count changed",
    )

    integration_seeds = {
        int(row["development_seed"])
        for row in INTEGRATION_CASES.values()
    }
    _require(
        integration_seeds == set(range(9941, 9950)),
        "R-065 development seeds changed",
    )

    seed_plan = _load(SEED_PLAN)
    selection = seed_plan["seed_selection"]
    reserved_sets = {
        "campaign": set(selection["campaign_seed_ids"]),
        "pilot": set(selection["pilot_seed_ids"]),
        "WP9-B2": set(selection["development_seed_ids"]),
        "prior route validation": _prior_route_validation_seeds(),
    }
    for label, reserved in reserved_sets.items():
        _require(
            integration_seeds.isdisjoint(reserved),
            f"R-065 development seed collides with {label} seed",
        )

    cells = _cells()
    prior_cells = _prior_validated_cells()
    observed_variants: set[str] = set()
    observed_signatures: set[str] = set()
    observed_events: set[str] = set()

    for case_id, expected in EXPECTED_CASE_BINDINGS.items():
        cell_id, seed, event_id, variant = expected
        case = INTEGRATION_CASES[case_id]
        _require(case["cell_id"] == cell_id, f"{case_id}: cell binding changed")
        _require(
            int(case["development_seed"]) == seed,
            f"{case_id}: development seed changed",
        )
        _require(
            cell_id in prior_cells,
            f"{case_id}: selected cell lacks prior bounded runtime validation",
        )

        cell = cells[cell_id]
        route = runtime_route_for_cell(cell_id)
        _require(cell["event_id"] == event_id, f"{case_id}: event binding changed")
        _require(_event_for_cell(cell_id) == event_id, f"{case_id}: R-064 route changed")
        _require(route["runtime_variant"] == variant, f"{case_id}: runtime variant changed")
        _require(
            route["runtime_family"] == ROUTE_CONTRACTS[event_id]["runtime_family"],
            f"{case_id}: runtime family changed",
        )

        signature = _integration_signature(
            runtime_variant=variant,
            contact_condition_id=cell["contact_condition_id"],
        )
        observed_variants.add(variant)
        observed_signatures.add(signature)
        observed_events.add(event_id)

    _require(len(observed_variants) == 8, "R-065 must cover all eight runtime variants")
    _require(
        observed_signatures == EXPECTED_INTEGRATION_SIGNATURES,
        "R-065 integration signatures changed",
    )
    _require(observed_events == {"E1", "E2", "E3", "E4"}, "R-065 family coverage changed")

    timing = _load(TIMING_FREEZE)["frozen_timing"]
    common = _load(COMMON_HORIZON_FREEZE)["frozen_horizons"]
    _require(
        timing["c1_semantics"]["modeled_contact_window_s"] == 10,
        "R-065 C1 contact window changed",
    )
    _require(
        common["common_post_event_analysis_horizon_s"] == 30,
        "R-065 common analysis horizon changed",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R065_BOUNDED_RUNTIME_INTEGRATION_STATIC_READY",
        "integration_cases": copy.deepcopy(INTEGRATION_CASES),
        "integration_case_count": 9,
        "runtime_variant_count": len(observed_variants),
        "integration_signature_count": len(observed_signatures),
        "event_family_count": len(observed_events),
        "minimal_representative_set": True,
        "selection_rule": (
            "one previously runtime-validated cell per frozen runtime variant, "
            "plus separate C0/C1 cases for the materially distinct P6 authorization branch"
        ),
        "selected_cells_previously_runtime_validated": True,
        "development_seed_range": "9941-9949",
        "development_seeds_disjoint_from_all_reserved_sets": True,
        "r064_static_bridge_required": True,
        "common_post_event_analysis_horizon_s": 30,
        "modeled_c1_contact_window_s": 10,
        "one_case_per_invocation": True,
        "development_evidence_root": "results/wp9/development/r065/integration",
        "production_runtime_executor_bound": False,
        "development_runtime_execution_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def build_integration_plan(
    *,
    case_id: str,
    run_id: str,
    repo_commit: str,
) -> dict[str, Any]:
    validate_static_integration()
    case = integration_case(case_id)
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("R-065 run_id contains unsupported characters")
    if COMMIT_PATTERN.fullmatch(repo_commit) is None:
        raise ValueError("R-065 repo_commit must be lowercase 40-hex")

    cell = _cells()[case["cell_id"]]
    seed = int(case["development_seed"])
    event_id = str(cell["event_id"])
    route = runtime_route_for_cell(cell["cell_id"])
    event = materialize_event(
        event_id,
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)

    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-065 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"] == cell["expected_effective_policy_id"],
        "R-065 development treatment differs from frozen campaign design",
    )

    timing = _load(TIMING_FREEZE)["frozen_timing"]
    common = _load(COMMON_HORIZON_FREEZE)["frozen_horizons"]
    contact_id = str(cell["contact_condition_id"])
    c1_window = (
        int(timing["c1_semantics"]["modeled_contact_window_s"])
        if contact_id == "C1"
        else None
    )
    p6_release = (
        c1_window
        if cell["policy_id"] == "P6" and contact_id == "C1"
        else (0 if cell["policy_id"] == "P6" else None)
    )
    signature = _integration_signature(
        runtime_variant=route["runtime_variant"],
        contact_condition_id=contact_id,
    )
    route_contract = ROUTE_CONTRACTS[event_id]

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R065_BOUNDED_RUNTIME_INTEGRATION_PLAN",
        "case_id": case_id,
        "run_id": run_id,
        "repo_commit": repo_commit,
        "cell_id": cell["cell_id"],
        "development_seed": seed,
        "development_seed_role": "bounded_integration_only_not_campaign_seed",
        "event_id": event_id,
        "mission_state_id": cell["mission_state_id"],
        "contact_condition_id": contact_id,
        "evidence_condition_id": cell["evidence_condition_id"],
        "requested_policy_id": cell["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "expected_effective_policy_id_for_acceptance_only": cell[
            "expected_effective_policy_id"
        ],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": False,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": event_id,
            "policy_id": cell["policy_id"],
            "contact_condition_id": contact_id,
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance": event,
        "runtime_family": route["runtime_family"],
        "runtime_variant": route["runtime_variant"],
        "integration_signature": signature,
        "campaign_observation_adapter_decision_id": route_contract[
            "campaign_observation_adapter_decision_id"
        ],
        "prior_runtime_validation_decision_id": route_contract[
            "development_runtime_validation_decision_id"
        ],
        "common_post_event_analysis_horizon_s": int(
            common["common_post_event_analysis_horizon_s"]
        ),
        "modeled_c1_contact_window_s": c1_window,
        "p6_authorization_release_after_event_s": p6_release,
        "ground_authorization_wait_required": bool(cell["policy_id"] == "P6"),
        "expected_values_role": "post_observation_acceptance_only_not_metric_inputs",
        "development_evidence_directory": (
            f"results/wp9/development/r065/integration/{run_id}"
        ),
        "development_validation_only": True,
        "development_runtime_execution_authorized": False,
        "production_runtime_executor_bound": False,
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "claim_boundaries": {
            "controlled_nos3_software_in_loop_only": True,
            "real_spacecraft_claim": False,
            "real_ground_contact_claim": False,
            "real_human_operator_claim": False,
            "operational_firmware_activation_claim": False,
            "rf_interference_claim": False,
        },
    }


def _validate_plan(plan: dict[str, Any]) -> None:
    _require(plan.get("decision_id") == DECISION_ID, "not an R-065 plan")
    _require(
        plan.get("classification") == "WP9_R065_BOUNDED_RUNTIME_INTEGRATION_PLAN",
        "not an R-065 bounded integration plan",
    )
    case = integration_case(str(plan.get("case_id")))
    _require(plan.get("cell_id") == case["cell_id"], "R-065 plan cell mismatch")
    _require(
        int(plan.get("development_seed")) == int(case["development_seed"]),
        "R-065 plan development seed mismatch",
    )
    _require("campaign_seed" not in plan, "R-065 plan cannot contain a campaign seed")
    _require(
        plan.get("development_validation_only") is True,
        "R-065 plan must remain development-only",
    )
    _require(
        plan.get("development_runtime_execution_authorized") is False,
        "R-065 plan cannot self-authorize runtime",
    )
    _require(
        plan.get("final_campaign_execution_authorized") is False,
        "R-065 plan cannot authorize final campaign",
    )
    _require(
        plan.get("campaign_seed_consumed") is False,
        "R-065 plan consumed campaign seed",
    )
    _require(
        plan.get("campaign_data_generated") is False,
        "R-065 plan generated campaign data",
    )


def build_authorization_request(plan: dict[str, Any]) -> dict[str, Any]:
    validate_static_integration()
    _validate_plan(plan)
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": AUTHORIZATION_REQUEST_CLASSIFICATION,
        "authorization_scope": "single_development_integration_case",
        "case_id": plan["case_id"],
        "run_id": plan["run_id"],
        "authorized_repo_sha": plan["repo_commit"],
        "cell_id": plan["cell_id"],
        "development_seed": int(plan["development_seed"]),
        "plan_sha256": _canonical_sha256(plan),
        "route_binding": {
            "event_id": plan["event_id"],
            "runtime_family": plan["runtime_family"],
            "runtime_variant": plan["runtime_variant"],
            "integration_signature": plan["integration_signature"],
            "campaign_observation_adapter_decision_id": plan[
                "campaign_observation_adapter_decision_id"
            ],
            "prior_runtime_validation_decision_id": plan[
                "prior_runtime_validation_decision_id"
            ],
        },
        "development_runtime_authorized": False,
        "campaign_runtime_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def validate_runtime_authorization(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    current_repo_sha: str,
) -> dict[str, Any]:
    _validate_plan(plan)
    _require(
        authorization.get("decision_id") == DECISION_ID,
        "R-065 authorization decision changed",
    )
    _require(
        authorization.get("classification") == AUTHORIZATION_CLASSIFICATION,
        "R-065 authorization classification changed",
    )
    _require(
        authorization.get("authorization_scope")
        == "single_development_integration_case",
        "R-065 authorization scope changed",
    )
    if authorization.get("development_runtime_authorized") is not True:
        raise PermissionError("R-065 development runtime authorization was not granted")
    if authorization.get("campaign_runtime_authorized") is not False:
        raise PermissionError("R-065 authorization cannot authorize campaign runtime")
    _require(
        authorization.get("automatic_retry_allowed") is False,
        "R-065 authorization cannot allow automatic retry",
    )
    _require(
        authorization.get("automatic_next_case_allowed") is False,
        "R-065 authorization cannot allow automatic next case",
    )
    _require(
        authorization.get("case_id") == plan["case_id"],
        "R-065 authorization case mismatch",
    )
    _require(
        authorization.get("run_id") == plan["run_id"],
        "R-065 authorization run_id mismatch",
    )
    _require(
        authorization.get("cell_id") == plan["cell_id"],
        "R-065 authorization cell mismatch",
    )
    _require(
        int(authorization.get("development_seed")) == int(plan["development_seed"]),
        "R-065 authorization development seed mismatch",
    )
    _require(
        authorization.get("authorized_repo_sha") == plan["repo_commit"],
        "R-065 authorization repository SHA differs from plan",
    )
    _require(
        authorization.get("authorized_repo_sha") == current_repo_sha,
        "R-065 authorization repository SHA differs from current repository",
    )
    _require(
        authorization.get("plan_sha256") == _canonical_sha256(plan),
        "R-065 authorization plan SHA mismatch",
    )
    _require(
        authorization.get("route_binding")
        == build_authorization_request(plan)["route_binding"],
        "R-065 authorization route binding changed",
    )
    _require(
        authorization.get("campaign_seed_consumed") is False,
        "R-065 authorization consumed campaign seed",
    )
    _require(
        authorization.get("campaign_data_generated") is False,
        "R-065 authorization generated campaign data",
    )
    _require(
        authorization.get("final_campaign_execution_authorized") is False,
        "R-065 authorization cannot authorize final campaign",
    )
    return copy.deepcopy(authorization)


def build_executor_descriptor(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    current_repo_sha: str,
) -> dict[str, Any]:
    validate_runtime_authorization(
        plan=plan,
        authorization=authorization,
        current_repo_sha=current_repo_sha,
    )
    evidence_directory = str(plan["development_evidence_directory"])
    _require(
        evidence_directory.startswith("results/wp9/development/r065/integration/"),
        "R-065 evidence directory escaped development namespace",
    )
    _require(
        "results/wp9/campaign" not in evidence_directory,
        "R-065 evidence directory entered campaign namespace",
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R065_BOUNDED_RUNTIME_EXECUTOR_DESCRIPTOR",
        "case_id": plan["case_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "cell_id": plan["cell_id"],
        "development_seed": int(plan["development_seed"]),
        "event_id": plan["event_id"],
        "runtime_family": plan["runtime_family"],
        "runtime_variant": plan["runtime_variant"],
        "integration_signature": plan["integration_signature"],
        "evidence_directory": evidence_directory,
        "common_post_event_analysis_horizon_s": int(
            plan["common_post_event_analysis_horizon_s"]
        ),
        "modeled_c1_contact_window_s": plan["modeled_c1_contact_window_s"],
        "p6_authorization_release_after_event_s": plan[
            "p6_authorization_release_after_event_s"
        ],
        "ground_authorization_wait_required": plan[
            "ground_authorization_wait_required"
        ],
        "one_case_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def execution_preflight(*, descriptor: dict[str, Any]) -> None:
    _require(
        descriptor.get("decision_id") == DECISION_ID,
        "not an R-065 executor descriptor",
    )
    raise PermissionError(
        "R-065 bounded runtime execution remains blocked: a separate runtime authorization "
        "and production integration executor implementation are required"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    plan_parser = sub.add_parser("plan-case")
    plan_parser.add_argument("--case-id", required=True)
    plan_parser.add_argument("--run-id", required=True)
    plan_parser.add_argument("--repo-commit", required=True)
    plan_parser.add_argument("--output-json", type=Path, required=True)

    auth_parser = sub.add_parser("authorization-request")
    auth_parser.add_argument("--plan-json", type=Path, required=True)
    auth_parser.add_argument("--output-json", type=Path, required=True)

    execute_parser = sub.add_parser("execute-case")
    execute_parser.add_argument("--descriptor-json", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.command == "validate-static":
        result = validate_static_integration()
        print("WP9_R065_BOUNDED_RUNTIME_INTEGRATION_STATIC=PASS")
        for key in (
            "integration_case_count",
            "runtime_variant_count",
            "integration_signature_count",
            "event_family_count",
            "minimal_representative_set",
            "selected_cells_previously_runtime_validated",
            "development_seed_range",
            "development_seeds_disjoint_from_all_reserved_sets",
            "common_post_event_analysis_horizon_s",
            "modeled_c1_contact_window_s",
            "one_case_per_invocation",
            "production_runtime_executor_bound",
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

    if args.command == "plan-case":
        plan = build_integration_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write(args.output_json, plan)
        print("WP9_R065_BOUNDED_RUNTIME_INTEGRATION_PLAN=PASS")
        print(f"case_id={plan['case_id']}")
        print(f"cell_id={plan['cell_id']}")
        print(f"development_seed={plan['development_seed']}")
        print(f"runtime_variant={plan['runtime_variant']}")
        print(f"integration_signature={plan['integration_signature']}")
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("final_campaign_execution_authorized=false")
        return 0

    if args.command == "authorization-request":
        plan = _load(args.plan_json)
        request = build_authorization_request(plan)
        _write(args.output_json, request)
        print("WP9_R065_AUTHORIZATION_REQUEST=PASS")
        print(f"case_id={request['case_id']}")
        print(f"development_seed={request['development_seed']}")
        print("development_runtime_authorized=false")
        print("campaign_runtime_authorized=false")
        print("automatic_retry_allowed=false")
        print("automatic_next_case_allowed=false")
        return 0

    descriptor = _load(args.descriptor_json)
    execution_preflight(descriptor=descriptor)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
