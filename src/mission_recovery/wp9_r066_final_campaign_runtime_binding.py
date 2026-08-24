from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from .events import materialize_event
from .wp9_campaign_e1_adapter import (
    _expected_gateway_treatment as e1_expected_gateway_treatment,
    build_static_fixture_bundle as build_e1_bundle,
)
from .wp9_campaign_e1_runtime_adapter import (
    build_development_plan as build_e1_development_plan,
)
from .wp9_campaign_e2_adapter import build_static_fixture_bundle as build_e2_bundle
from .wp9_campaign_e2_runtime_adapter import (
    build_development_plan as build_e2_development_plan,
)
from .wp9_campaign_e3_adapter import build_static_fixture_bundle as build_e3_bundle
from .wp9_campaign_e3_runtime_adapter import (
    build_development_plan as build_e3_development_plan,
)
from .wp9_campaign_e4_adapter import build_static_fixture_bundle as build_e4_bundle
from .wp9_campaign_e4_runtime_adapter import (
    build_development_plan as build_e4_development_plan,
)
from .wp9_final_campaign_bridge import route_trial_plan, validate_static_bridge
from .wp9_r064_attempt_history import (
    build_attempt_guarded_execution_descriptor,
    validate_static_attempt_guard,
)
from .wp9_static_contracts import evaluate_wp9_policy

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-066"
STATIC_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_RUNTIME_BINDING_STATIC_READY"
REQUEST_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_RUNTIME_REQUEST"
RETURN_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_RUNTIME_RETURN"
VALID_RESULT_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT"
INVALID_RESULT_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_INVALID_ATTEMPT"

_SOURCE_HARNESSES: dict[str, dict[str, Any]] = {
    "E1": {
        "path": "scripts/run_wp9_r061_e1_route_validation.sh",
        "blob_sha": "5a4596cfbe5941dbaeb833c802d68258343e7f9a",
        "source_decision_id": "R-061",
        "runtime_adapter_module": "src.mission_recovery.wp9_campaign_e1_runtime_adapter",
        "development_evidence_prefix": "results/wp9/development/r061/e1",
        "supported_cases": ("X01", "X02", "X03", "X04", "X05"),
        "authorization_env": {
            "enabled": "WP9_R061_DEVELOPMENT_RUNTIME_AUTHORIZED",
            "case": "WP9_R061_AUTHORIZED_CASE",
            "sha": "WP9_R061_AUTHORIZED_REPO_SHA",
        },
    },
    "E2": {
        "path": "scripts/run_wp9_r057_e2_route_validation.sh",
        "blob_sha": "4530cde131dd5a27454411d9e39f99e36c58b211",
        "source_decision_id": "R-057",
        "runtime_adapter_module": "src.mission_recovery.wp9_campaign_e2_runtime_adapter",
        "development_evidence_prefix": "results/wp9/development/r057/e2",
        "supported_cases": ("V01", "V02", "V03"),
        "authorization_env": None,
    },
    "E3": {
        "path": "scripts/run_wp9_r063_e3_route_validation.sh",
        "blob_sha": "76193d768ee48bfc5748f5fc6c12675d8057456e",
        "source_decision_id": "R-063",
        "runtime_adapter_module": "src.mission_recovery.wp9_campaign_e3_runtime_adapter",
        "development_evidence_prefix": "results/wp9/development/r063/e3",
        "supported_cases": ("Y01", "Y02", "Y03", "Y04", "Y05", "Y06"),
        "authorization_env": {
            "enabled": "WP9_R063_DEVELOPMENT_RUNTIME_AUTHORIZED",
            "case": "WP9_R063_AUTHORIZED_CASE",
            "sha": "WP9_R063_AUTHORIZED_REPO_SHA",
        },
    },
    "E4": {
        "path": "scripts/run_wp9_r059_e4_route_validation.sh",
        "blob_sha": "c51e254e1d00f6b59dbd33f6130eda8ff506bae1",
        "source_decision_id": "R-059",
        "runtime_adapter_module": "src.mission_recovery.wp9_campaign_e4_runtime_adapter",
        "development_evidence_prefix": "results/wp9/development/r059/e4",
        "supported_cases": ("W01", "W02", "W03"),
        "authorization_env": None,
    },
}

_SOURCE_CASE_IDENTITIES: dict[str, tuple[str, int]] = {
    "X01": ("A05", 9921),
    "X02": ("A08", 9922),
    "X03": ("A02", 9923),
    "X04": ("A06", 9924),
    "X05": ("A09", 9925),
    "V01": ("A19", 9901),
    "V02": ("A20", 9902),
    "V03": ("A21", 9903),
    "Y01": ("A13", 9931),
    "Y02": ("A11", 9932),
    "Y03": ("A15", 9933),
    "Y04": ("A16", 9934),
    "Y05": ("A17", 9935),
    "Y06": ("A18", 9936),
    "W01": ("A22", 9911),
    "W02": ("A23", 9912),
    "W03": ("A24", 9913),
}

_CELL_SOURCE_CASE = {
    "A01": "X01",
    "A02": "X03",
    "A03": "X01",
    "A04": "X04",
    "A05": "X01",
    "A06": "X04",
    "A07": "X02",
    "A08": "X02",
    "A09": "X05",
    "A10": "Y01",
    "A11": "Y02",
    "A12": "Y01",
    "A13": "Y01",
    "A14": "Y02",
    "A15": "Y03",
    "A16": "Y04",
    "A17": "Y05",
    "A18": "Y06",
    "A19": "V01",
    "A20": "V02",
    "A21": "V03",
    "A22": "W01",
    "A23": "W02",
    "A24": "W03",
}


def _event_for_cell(cell_id: str) -> str:
    number = int(cell_id[1:])
    if 1 <= number <= 9:
        return "E1"
    if 10 <= number <= 18:
        return "E3"
    if 19 <= number <= 21:
        return "E2"
    if 22 <= number <= 24:
        return "E4"
    raise ValueError(f"unsupported R-066 campaign cell: {cell_id}")


def _make_binding(cell_id: str) -> dict[str, Any]:
    event_id = _event_for_cell(cell_id)
    source = _SOURCE_HARNESSES[event_id]
    source_case = _CELL_SOURCE_CASE[cell_id]
    source_cell, source_seed = _SOURCE_CASE_IDENTITIES[source_case]
    return {
        "event_id": event_id,
        "source_case": source_case,
        "source_cell": source_cell,
        "source_development_seed": source_seed,
        "source_path": source["path"],
        "source_blob_sha": source["blob_sha"],
        "source_decision_id": source["source_decision_id"],
        "source_supported_cases": source["supported_cases"],
        "runtime_adapter_module": source["runtime_adapter_module"],
        "development_evidence_prefix": source["development_evidence_prefix"],
    }


CELL_HARNESS_BINDINGS: dict[str, dict[str, Any]] = {
    cell_id: _make_binding(cell_id)
    for cell_id in (f"A{i:02d}" for i in range(1, 25))
}

_PLAN_BUILDERS: dict[str, Callable[..., dict[str, Any]]] = {
    "E1": build_e1_development_plan,
    "E2": build_e2_development_plan,
    "E3": build_e3_development_plan,
    "E4": build_e4_development_plan,
}

_BUNDLE_BUILDERS: dict[str, Callable[..., dict[str, Any]]] = {
    "E1": build_e1_bundle,
    "E2": build_e2_bundle,
    "E3": build_e3_bundle,
    "E4": build_e4_bundle,
}


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


def source_harness_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("utf-8") + data,
        usedforsecurity=False,
    ).hexdigest()


def _source_plan(binding: dict[str, Any], *, run_id: str, repo_commit: str) -> dict[str, Any]:
    return _PLAN_BUILDERS[binding["event_id"]](
        case_id=binding["source_case"],
        run_id=run_id,
        repo_commit=repo_commit,
    )


def _source_selected_action(source_plan: dict[str, Any]) -> str:
    if isinstance(source_plan.get("runtime_policy_decision"), dict):
        return str(source_plan["runtime_policy_decision"]["selected_action"])
    return str(source_plan["expected_selected_action_for_acceptance_only"])


def _materialized_policy(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    route_trial_plan(plan)
    factor = plan["factor_context"]
    event = materialize_event(
        factor["event_id"],
        mission_state=factor["mission_state_id"],
        contact_condition=factor["contact_condition_id"],
        evidence_condition=factor["evidence_condition_id"],
        seed=int(factor["seed"]),
    )
    decision = evaluate_wp9_policy(factor["policy_id"], event)
    _require(
        decision["oracle_ground_truth_read"] is False,
        "R-066 policy selection cannot read immutable ground truth",
    )
    _require(
        decision["delegated_policy_id"]
        == plan["expected_effective_policy_id_for_acceptance_only"],
        "R-066 campaign treatment differs from frozen design",
    )
    return event, decision


def build_compatibility_plan(*, plan: dict[str, Any]) -> dict[str, Any]:
    cell_id = str(plan.get("cell_id"))
    _require(cell_id in CELL_HARNESS_BINDINGS, "R-066 cell binding is missing")
    binding = CELL_HARNESS_BINDINGS[cell_id]
    route = route_trial_plan(plan)
    _require(
        route["event_id"] == binding["event_id"],
        "R-066 campaign/source event binding mismatch",
    )

    template = _source_plan(
        binding,
        run_id=str(plan["run_id"]),
        repo_commit=str(plan["repo_commit"]),
    )
    event, decision = _materialized_policy(plan)
    campaign_seed = int(plan["campaign_seed"])
    factor = copy.deepcopy(plan["factor_context"])

    template["cell_id"] = cell_id
    template["development_seed"] = campaign_seed
    template["campaign_seed"] = campaign_seed
    template["factor_context"] = factor
    template["event_instance"] = copy.deepcopy(event)
    template["runtime_policy_decision"] = copy.deepcopy(decision)
    template["expected_effective_policy_id_for_acceptance_only"] = plan[
        "expected_effective_policy_id_for_acceptance_only"
    ]
    template["runtime_family"] = plan["runtime_family"]
    template["runtime_variant"] = plan["runtime_variant"]
    template["campaign_runtime_compatibility_plan"] = True
    template["campaign_source_harness_decision_id"] = binding[
        "source_decision_id"
    ]
    template["campaign_source_harness_case"] = binding["source_case"]
    template["development_validation_only"] = False
    template["development_runtime_execution_authorized"] = False
    template["campaign_seed_consumed"] = False
    template["campaign_data_generated"] = False
    template["final_campaign_execution_authorized"] = False
    template["automatic_retry_allowed"] = False
    template["automatic_next_case_allowed"] = False

    if binding["event_id"] == "E1":
        attacker_forwarded_count, authorized_forwarded = (
            e1_expected_gateway_treatment(decision["selected_action"])
        )
        template["acceptance_only_expected_gateway_treatment"] = {
            "attacker_gateway_forwarded_count": attacker_forwarded_count,
            "authorized_noop_gateway_forwarded": authorized_forwarded,
        }
        template["acceptance_only_expected_effects"] = {
            "post_enforcement_attacker_reset_marker_delta": (
                attacker_forwarded_count
            ),
            "authorized_noop_marker_delta": 1 if authorized_forwarded else 0,
        }

    if binding["event_id"] == "E3":
        timing = plan["timing_contract"]
        template["expected_selected_action_for_acceptance_only"] = decision[
            "selected_action"
        ]
        template["timing_contract"] = {
            "post_event_analysis_horizon_s": timing[
                "e3_post_event_analysis_horizon_s"
            ],
            "modeled_c1_contact_window_s": timing[
                "modeled_c1_contact_window_s"
            ],
            "p6_ground_authorization_release_after_response_boundary_s": timing[
                "p6_ground_authorization_release_after_event_s"
            ],
            "early_absorbing_trusted_recovery_allowed": timing[
                "early_absorbing_trusted_recovery_allowed"
            ],
            "unrecovered_run_right_censored_at_horizon": timing[
                "unrecovered_e3_right_censored_at_horizon"
            ],
            "runner_duration_used_as_metric_input": False,
        }
        treatment = copy.deepcopy(template.get("treatment_contract", {}))
        treatment["p6_post_authorization_delegate"] = (
            "P5" if factor["policy_id"] == "P6" else None
        )
        treatment["a18_ground_authorization_waited"] = (
            False if cell_id == "A18" else None
        )
        template["treatment_contract"] = treatment
        template["acceptance_only_expected_effects"] = {
            "update_containment_observed": decision["delegated_policy_id"]
            in {"P5", "P6"},
            "authorized_noop_marker_delta": 1,
            "trusted_recovery_confirmed": None,
        }

    _require(
        int(template["factor_context"]["seed"]) == campaign_seed,
        "R-066 compatibility plan fell back to a development seed",
    )
    _require(
        template["cell_id"] == cell_id,
        "R-066 compatibility plan fell back to a development cell",
    )
    return template


def derive_harness_text(*, request: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    binding = request["source_harness"]
    path = ROOT / binding["source_path"]
    observed_blob = source_harness_blob_sha(path)
    _require(
        observed_blob == binding["source_blob_sha"],
        "R-066 source harness blob identity changed",
    )
    text = path.read_text(encoding="utf-8")

    root_line = 'ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"'
    _require(text.count(root_line) == 1, "R-066 source harness ROOT marker changed")
    text = text.replace(root_line, 'ROOT="${WP9_R066_REPO_ROOT:?}"', 1)

    source_case = binding["source_case"]
    source_cell = binding["source_cell"]
    source_seed = int(binding["source_development_seed"])
    old_case_line = (
        f'{source_case}) CELL_ID="{source_cell}"; SEED="{source_seed}" ;;'
    )
    new_case_line = (
        f'{source_case}) CELL_ID="{request["cell_id"]}"; '
        f'SEED="{int(request["campaign_seed"])}" ;;'
    )
    _require(
        text.count(old_case_line) == 1,
        "R-066 source harness case mapping marker changed",
    )
    text = text.replace(old_case_line, new_case_line, 1)
    return text, {
        "source_blob_sha": observed_blob,
        "root_line_replacement_count": 1,
        "case_mapping_replacement_count": 1,
        "source_case": source_case,
        "source_cell": source_cell,
        "source_development_seed": source_seed,
        "campaign_cell": request["cell_id"],
        "campaign_seed": int(request["campaign_seed"]),
    }


def validate_static_campaign_runtime_binding() -> dict[str, Any]:
    bridge = validate_static_bridge()
    guard = validate_static_attempt_guard()
    _require(bridge["decision_id"] == "R-064", "R-066 requires R-064 bridge")
    _require(guard["decision_id"] == "R-064", "R-066 requires R-064 attempt guard")
    _require(
        guard["attempt_history_required_for_campaign_execution"] is True,
        "R-066 attempt history gate disappeared",
    )
    _require(
        set(CELL_HARNESS_BINDINGS) == {f"A{i:02d}" for i in range(1, 25)},
        "R-066 must bind A01-A24 exactly",
    )

    variants: set[str] = set()
    source_paths: set[str] = set()
    for cell_id, binding in CELL_HARNESS_BINDINGS.items():
        source_path = ROOT / binding["source_path"]
        _require(source_path.is_file(), f"R-066 source harness missing: {source_path}")
        _require(
            source_harness_blob_sha(source_path) == binding["source_blob_sha"],
            f"R-066 source harness blob changed: {binding['source_path']}",
        )
        _require(
            binding["source_case"] in binding["source_supported_cases"],
            f"R-066 unsupported source case: {cell_id}",
        )
        plan = __import__(
            "src.mission_recovery.wp9_campaign_trial_controller",
            fromlist=["build_trial_plan"],
        ).build_trial_plan(
            campaign_seed=10001,
            cell_id=cell_id,
            run_id=f"r066-static-{cell_id.lower()}",
            repo_commit="a" * 40,
        )
        compat = build_compatibility_plan(plan=plan)
        source_plan = _source_plan(
            binding,
            run_id=f"r066-source-{cell_id.lower()}",
            repo_commit="a" * 40,
        )
        _require(
            compat["runtime_policy_decision"]["selected_action"]
            == _source_selected_action(source_plan),
            f"R-066 source alias treatment differs: {cell_id}",
        )
        _require(
            compat["runtime_variant"] == plan["runtime_variant"],
            f"R-066 runtime variant changed: {cell_id}",
        )
        _require(
            int(compat["factor_context"]["seed"]) == 10001,
            f"R-066 campaign seed passthrough failed: {cell_id}",
        )
        source_paths.add(binding["source_path"])
        variants.add(plan["runtime_variant"])

    _require(len(source_paths) == 4, "R-066 must use four family harnesses")
    _require(len(variants) == 8, "R-066 runtime variant coverage changed")
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": STATIC_CLASSIFICATION,
        "campaign_cell_count": 24,
        "source_harness_count": len(source_paths),
        "runtime_variant_count": len(variants),
        "production_runtime_executor_bound": True,
        "source_harness_blob_identity_enforced": True,
        "source_alias_treatment_equivalence_validated": True,
        "campaign_seed_passthrough_enforced": True,
        "campaign_evidence_namespace_enforced": True,
        "attempt_history_guard_required": True,
        "deterministic_plumbing_only_harness_derivation": True,
        "one_trial_per_invocation": True,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_runtime_authorized": False,
        "campaign_wide_execution_authorized": False,
    }


def build_campaign_runtime_request(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    attempt_history: list[dict[str, Any]],
    current_repo_sha: str,
) -> dict[str, Any]:
    validate_static_campaign_runtime_binding()
    descriptor = build_attempt_guarded_execution_descriptor(
        plan=plan,
        authorization=authorization,
        attempt_history=attempt_history,
        current_repo_sha=current_repo_sha,
    )
    cell_id = str(plan["cell_id"])
    binding = copy.deepcopy(CELL_HARNESS_BINDINGS[cell_id])
    evidence = str(descriptor["evidence_directory"])
    expected_prefix = (
        f"results/wp9/campaign/seed-{int(plan['campaign_seed'])}/{cell_id}/"
    )
    _require(
        evidence.startswith(expected_prefix),
        "R-066 evidence directory escaped exact campaign seed/cell namespace",
    )
    _require(
        "results/wp9/development" not in evidence,
        "R-066 campaign request entered development evidence namespace",
    )
    _require(
        source_harness_blob_sha(ROOT / binding["source_path"])
        == binding["source_blob_sha"],
        "R-066 source harness identity changed before request",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": REQUEST_CLASSIFICATION,
        "global_order_index": int(descriptor["global_order_index"]),
        "block_index": int(descriptor["block_index"]),
        "campaign_seed": int(descriptor["campaign_seed"]),
        "cell_order_index": int(descriptor["cell_order_index"]),
        "cell_id": cell_id,
        "run_id": descriptor["run_id"],
        "repo_commit": descriptor["repo_commit"],
        "plan": copy.deepcopy(plan),
        "plan_sha256": descriptor["plan_sha256"],
        "route_binding": copy.deepcopy(descriptor["route_binding"]),
        "source_harness": binding,
        "source_harness_blob_identity_validated": True,
        "attempt_history_validated": bool(descriptor["attempt_history_validated"]),
        "prior_attempt_count": int(descriptor["prior_attempt_count"]),
        "prior_valid_position_count": int(descriptor["prior_valid_position_count"]),
        "prior_invalid_attempt_count": int(descriptor["prior_invalid_attempt_count"]),
        "evidence_directory": evidence,
        "clean_snapshot_required_before_trial": True,
        "one_trial_per_invocation": True,
        "source_harness_invocation_limit": 1,
        "automatic_retry_allowed": False,
        "automatic_next_case_allowed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "campaign_runtime_authorized": False,
        "campaign_wide_execution_authorized": False,
    }


def _validate_request(request: dict[str, Any]) -> dict[str, Any]:
    _require(request.get("decision_id") == DECISION_ID, "not an R-066 request")
    _require(
        request.get("classification") == REQUEST_CLASSIFICATION,
        "R-066 request classification changed",
    )
    cell_id = str(request.get("cell_id"))
    _require(cell_id in CELL_HARNESS_BINDINGS, "R-066 request cell changed")
    _require(
        request.get("source_harness") == CELL_HARNESS_BINDINGS[cell_id],
        "R-066 request source harness binding changed",
    )
    _require(
        request.get("attempt_history_validated") is True,
        "R-066 request lacks validated attempt history",
    )
    _require(
        request.get("source_harness_blob_identity_validated") is True,
        "R-066 request lacks source harness identity validation",
    )
    _require(
        request.get("automatic_retry_allowed") is False,
        "R-066 request allows automatic retry",
    )
    _require(
        request.get("automatic_next_case_allowed") is False,
        "R-066 request allows automatic next case",
    )
    _require(
        request.get("campaign_seed_consumed") is False,
        "R-066 request already consumed campaign seed",
    )
    _require(
        request.get("campaign_data_generated") is False,
        "R-066 request already generated campaign data",
    )
    evidence = str(request.get("evidence_directory", ""))
    expected = (
        f"results/wp9/campaign/seed-{int(request['campaign_seed'])}/"
        f"{cell_id}/{request['run_id']}"
    )
    _require(evidence == expected, "R-066 exact campaign evidence path changed")
    return copy.deepcopy(request)


def _validate_authorization_environment(
    request: dict[str, Any],
    env: Mapping[str, str],
) -> None:
    if env.get("WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED") != "1":
        raise PermissionError(
            "R-066 campaign runtime authorization is not active"
        )
    expected = {
        "WP9_R066_AUTHORIZED_RUN_ID": str(request["run_id"]),
        "WP9_R066_AUTHORIZED_SEED": str(int(request["campaign_seed"])),
        "WP9_R066_AUTHORIZED_CELL": str(request["cell_id"]),
        "WP9_R066_AUTHORIZED_REPO_SHA": str(request["repo_commit"]),
    }
    for key, value in expected.items():
        _require(env.get(key) == value, f"R-066 authorization mismatch: {key}")


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
    exec "$REAL" -m src.mission_recovery.wp9_r066_final_campaign_runtime_binding \
      shim-plan --family "$FAMILY" --output-json "$OUT"
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
    exec "$REAL" -m src.mission_recovery.wp9_r066_final_campaign_runtime_binding \
      shim-finalize --family "$FAMILY" --measurement-json "$MEASUREMENT" \
      --output-json "$OUT"
  fi
fi
exec "$REAL" "$@"
'''


def _shim_plan(*, family: str, output_json: Path) -> None:
    plan_path = os.environ.get("WP9_R066_CAMPAIGN_PLAN_JSON")
    evidence_dir = os.environ.get("WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY")
    _require(bool(plan_path), "R-066 shim campaign plan path missing")
    _require(bool(evidence_dir), "R-066 shim campaign evidence path missing")
    plan = _load(Path(str(plan_path)))
    _require(
        plan["factor_context"]["event_id"] == family,
        "R-066 shim family/plan event mismatch",
    )
    compat = build_compatibility_plan(plan=plan)
    _write(output_json, compat)
    marker = Path(str(evidence_dir)) / "immutable-ground" / "campaign-seed-consumption.json"
    _write(
        marker,
        {
            "schema": 1,
            "decision_id": DECISION_ID,
            "classification": "WP9_R066_CAMPAIGN_SEED_MATERIALIZED",
            "run_id": plan["run_id"],
            "campaign_seed": int(plan["campaign_seed"]),
            "cell_id": plan["cell_id"],
            "event_id": family,
            "materialized_monotonic_ns": time.monotonic_ns(),
            "campaign_seed_consumed": True,
            "automatic_retry_performed": False,
            "automatic_next_case_performed": False,
        },
    )


def _runtime_bundle(
    *,
    plan: dict[str, Any],
    measurement: dict[str, Any],
    evidence_prefix: str,
) -> dict[str, Any]:
    family = str(plan["factor_context"]["event_id"])
    builder = _BUNDLE_BUILDERS[family]
    bundle = builder(
        plan=plan,
        measurement=measurement,
        host_architecture=platform.machine(),
        evidence_prefix=evidence_prefix,
    )
    run_record = copy.deepcopy(bundle["run_record"])
    run_record["notes"] = (
        "R-066 final-campaign single-trial runtime observation in controlled "
        "NOS3 software-in-the-loop; no real spacecraft, RF interference, real "
        "ground-contact timing, or real human-operator timing claim."
    )
    provenance = copy.deepcopy(bundle["binding_provenance"])
    original_decision = provenance.get("decision_id")
    provenance["source_campaign_observation_adapter_decision_id"] = original_decision
    provenance["decision_id"] = DECISION_ID
    provenance["classification"] = "WP9_R066_FINAL_CAMPAIGN_RUNTIME_PROVENANCE"
    provenance["static_fixture_only"] = False
    provenance["runtime_execution_performed"] = True
    provenance["campaign_runtime_execution_performed"] = True
    provenance["campaign_seed_consumed"] = True
    provenance["campaign_data_generated"] = True
    provenance["single_trial_runtime_authorization_validated"] = True
    provenance["campaign_wide_execution_authorized"] = False
    provenance["automatic_retry_allowed"] = False
    provenance["automatic_next_case_allowed"] = False

    expectation = provenance.get("predeclared_expectation", {})
    outcome_matches = expectation.get("outcome_matches_predeclared_expectation")
    scientific = provenance.get("scientific_validity", {})
    unexpected_retained = scientific.get(
        "unexpected_scientific_outcome_retained",
        (not outcome_matches) if isinstance(outcome_matches, bool) else False,
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": VALID_RESULT_CLASSIFICATION,
        "run_id": plan["run_id"],
        "campaign_seed": int(plan["campaign_seed"]),
        "cell_id": plan["cell_id"],
        "event_id": family,
        "runtime_family": plan["runtime_family"],
        "runtime_variant": plan["runtime_variant"],
        "attempt_status": "VALID",
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "outcome_matches_predeclared_expectation": outcome_matches,
        "unexpected_scientific_outcome_retained": bool(unexpected_retained),
        "run_record": run_record,
        "binding_provenance": provenance,
        "runtime_execution_performed": True,
        "campaign_seed_consumed": True,
        "campaign_data_generated": True,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "campaign_wide_execution_authorized": False,
    }


def _shim_finalize(*, family: str, measurement_json: Path, output_json: Path) -> None:
    plan_path = os.environ.get("WP9_R066_CAMPAIGN_PLAN_JSON")
    evidence_dir = os.environ.get("WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY")
    evidence_prefix = os.environ.get("WP9_R066_CAMPAIGN_EVIDENCE_PREFIX")
    _require(bool(plan_path), "R-066 shim campaign plan path missing")
    _require(bool(evidence_dir), "R-066 shim campaign evidence path missing")
    _require(bool(evidence_prefix), "R-066 shim evidence prefix missing")
    plan = _load(Path(str(plan_path)))
    _require(
        plan["factor_context"]["event_id"] == family,
        "R-066 finalizer family/plan mismatch",
    )
    result = _runtime_bundle(
        plan=plan,
        measurement=_load(measurement_json),
        evidence_prefix=str(evidence_prefix),
    )
    _write(output_json, result)
    _write(Path(str(evidence_dir)) / "campaign-trial-result.json", result)


def run_source_harness(request: dict[str, Any]) -> dict[str, Any]:
    validated = _validate_request(request)
    repo_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _require(repo_sha == validated["repo_commit"], "R-066 runtime repository SHA changed")
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _require(status == "", "R-066 runtime requires a clean worktree")

    source = validated["source_harness"]
    source_path = ROOT / source["source_path"]
    _require(
        source_harness_blob_sha(source_path) == source["source_blob_sha"],
        "R-066 source harness blob changed at runtime",
    )

    evidence = ROOT / validated["evidence_directory"]
    evidence.mkdir(parents=True, exist_ok=True)
    ground = evidence / "immutable-ground"
    ground.mkdir(parents=True, exist_ok=True)
    plan_path = ground / "campaign-plan.json"
    request_path = ground / "r066-runtime-request.json"
    _write(plan_path, validated["plan"])
    _write(request_path, validated)

    dev_link = (
        ROOT
        / source["development_evidence_prefix"]
        / str(validated["run_id"])
    )
    dev_link.parent.mkdir(parents=True, exist_ok=True)
    _require(
        not dev_link.exists() and not dev_link.is_symlink(),
        "R-066 compatibility evidence alias already exists",
    )

    derived_text, derivation = derive_harness_text(request=validated)
    derivation_path = ground / "source-harness-derivation.json"
    _write(derivation_path, derivation)

    result: dict[str, Any]
    with tempfile.TemporaryDirectory(prefix="wp9-r066-") as tmp:
        tmp_path = Path(tmp)
        derived_script = tmp_path / "derived-source-harness.sh"
        derived_script.write_text(derived_text, encoding="utf-8")
        derived_script.chmod(
            derived_script.stat().st_mode | stat.S_IXUSR
        )
        shim_dir = tmp_path / "shim"
        shim_dir.mkdir()
        python_shim = shim_dir / "python3"
        python_shim.write_text(_shim_text(), encoding="utf-8")
        python_shim.chmod(python_shim.stat().st_mode | stat.S_IXUSR)

        os.symlink(evidence.resolve(), dev_link, target_is_directory=True)
        env = os.environ.copy()
        env.update(
            {
                "RUN_ID": str(validated["run_id"]),
                "WP9_R066_REPO_ROOT": str(ROOT),
                "WP9_R066_REAL_PYTHON3": sys.executable,
                "WP9_R066_CAMPAIGN_PLAN_JSON": str(plan_path.resolve()),
                "WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY": str(evidence.resolve()),
                "WP9_R066_CAMPAIGN_EVIDENCE_PREFIX": validated[
                    "evidence_directory"
                ],
                "PATH": str(shim_dir) + os.pathsep + env.get("PATH", ""),
            }
        )
        source_env = _SOURCE_HARNESSES[source["event_id"]]["authorization_env"]
        if source_env:
            env[source_env["enabled"]] = "1"
            env[source_env["case"]] = source["source_case"]
            env[source_env["sha"]] = validated["repo_commit"]

        try:
            completed = subprocess.run(
                ["/bin/bash", str(derived_script), source["source_case"]],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            if dev_link.is_symlink():
                dev_link.unlink()

    (evidence / "source-harness.stdout.log").write_text(
        completed.stdout,
        encoding="utf-8",
    )
    (evidence / "source-harness.stderr.log").write_text(
        completed.stderr,
        encoding="utf-8",
    )
    seed_marker = ground / "campaign-seed-consumption.json"
    seed_consumed = seed_marker.is_file()

    canonical = evidence / "campaign-trial-result.json"
    if completed.returncode == 0:
        _require(seed_consumed, "R-066 successful runtime did not consume campaign seed")
        _require(canonical.is_file(), "R-066 successful runtime lacks canonical result")
        result = _load(canonical)
        _require(result.get("attempt_status") == "VALID", "R-066 result is not valid")
        result["source_harness_return_code"] = 0
        result["source_harness_invocation_count"] = 1
        _write(canonical, result)
        return result

    source_invalid = evidence / "development-run-invalid.json"
    retained_source_invalid = evidence / "source-harness-invalid.json"
    if source_invalid.exists():
        if retained_source_invalid.exists():
            retained_source_invalid.unlink()
        source_invalid.rename(retained_source_invalid)
    runtime_observation = evidence / "runtime-observation"
    data_generated = bool(
        seed_consumed
        and runtime_observation.exists()
        and any(runtime_observation.iterdir())
    )
    result = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": INVALID_RESULT_CLASSIFICATION,
        "run_id": validated["run_id"],
        "campaign_seed": int(validated["campaign_seed"]),
        "cell_id": validated["cell_id"],
        "attempt_status": "INVALID",
        "source_harness_return_code": int(completed.returncode),
        "source_harness_invocation_count": 1,
        "invalid_attempt_retained": True,
        "campaign_seed_consumed": seed_consumed,
        "campaign_data_generated": data_generated,
        "runtime_execution_performed": seed_consumed,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "campaign_wide_execution_authorized": False,
    }
    _write(evidence / "campaign-trial-invalid.json", result)
    return result


def execute_campaign_runtime_request(
    *,
    request: dict[str, Any],
    runner: Callable[[dict[str, Any]], dict[str, Any]] = run_source_harness,
    authorization_environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    validated = _validate_request(request)
    env = os.environ if authorization_environment is None else authorization_environment
    _validate_authorization_environment(validated, env)
    result = runner(copy.deepcopy(validated))
    _require(isinstance(result, dict), "R-066 runner result must be an object")
    for key in ("run_id", "cell_id"):
        _require(result.get(key) == validated[key], f"R-066 runner {key} mismatch")
    _require(
        int(result.get("campaign_seed")) == int(validated["campaign_seed"]),
        "R-066 runner campaign seed mismatch",
    )
    _require(
        result.get("automatic_retry_performed") is False,
        "R-066 runner performed automatic retry",
    )
    _require(
        result.get("automatic_next_case_performed") is False,
        "R-066 runner performed automatic next case",
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": RETURN_CLASSIFICATION,
        "run_id": validated["run_id"],
        "campaign_seed": int(validated["campaign_seed"]),
        "cell_id": validated["cell_id"],
        "source_harness_invocation_count": 1,
        "attempt_status": result.get("attempt_status"),
        "runner_result": copy.deepcopy(result),
        "runtime_execution_performed": bool(
            result.get("runtime_execution_performed", False)
        ),
        "campaign_seed_consumed": bool(
            result.get("campaign_seed_consumed", False)
        ),
        "campaign_data_generated": bool(
            result.get("campaign_data_generated", False)
        ),
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "campaign_wide_execution_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-static")

    shim_plan = sub.add_parser("shim-plan")
    shim_plan.add_argument("--family", required=True, choices=("E1", "E2", "E3", "E4"))
    shim_plan.add_argument("--output-json", type=Path, required=True)

    shim_finalize = sub.add_parser("shim-finalize")
    shim_finalize.add_argument("--family", required=True, choices=("E1", "E2", "E3", "E4"))
    shim_finalize.add_argument("--measurement-json", type=Path, required=True)
    shim_finalize.add_argument("--output-json", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "validate-static":
        result = validate_static_campaign_runtime_binding()
        print("WP9_R066_FINAL_CAMPAIGN_RUNTIME_BINDING_STATIC=PASS")
        for key in (
            "campaign_cell_count",
            "source_harness_count",
            "runtime_variant_count",
            "production_runtime_executor_bound",
            "source_harness_blob_identity_enforced",
            "source_alias_treatment_equivalence_validated",
            "campaign_seed_passthrough_enforced",
            "campaign_evidence_namespace_enforced",
            "attempt_history_guard_required",
            "deterministic_plumbing_only_harness_derivation",
            "one_trial_per_invocation",
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
    if args.command == "shim-plan":
        _shim_plan(family=args.family, output_json=args.output_json)
        return 0
    _shim_finalize(
        family=args.family,
        measurement_json=args.measurement_json,
        output_json=args.output_json,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
