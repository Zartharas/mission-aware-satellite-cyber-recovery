from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

from .wp8_runtime_binding import (
    bind_runtime_observation,
    environment_from_toolchain_lock,
)

ORDERING_METHOD = "sha256_rank_v1"
RUNNER_VERSION = "0.1.0"
STAGE1_KEY = "stage_1_control_validity"


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cells_by_id(pilot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cells = pilot["cells"]
    by_id = {row["cell_id"]: row for row in cells}
    if len(by_id) != len(cells):
        raise ValueError("duplicate Stage-1 pilot cell_id")
    return by_id


def validate_stage1_contract(pilot: dict[str, Any]) -> None:
    stage1 = pilot[STAGE1_KEY]
    contract = pilot["stage_1_runner_contract"]
    gate = pilot["instrumentation_gate"]
    invalid_rule = pilot["invalid_run_rule"]

    if contract["decision_id"] != "R-028":
        raise ValueError("Stage-1 runner contract is not R-028")
    if contract["runner_version"] != RUNNER_VERSION:
        raise ValueError("unexpected Stage-1 runner version")
    if contract["ordering_method"] != ORDERING_METHOD:
        raise ValueError("unexpected Stage-1 ordering method")
    if contract["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError("offline validation cannot consume pilot seed")
    if contract["run_id_policy"] != "utc_microseconds_cell_seed_uuid4":
        raise ValueError("unexpected Stage-1 run-id policy")

    if stage1["randomize_order_within_seed_block"] is not True:
        raise ValueError("Stage-1 order must be randomized within seed block")

    cells = _cells_by_id(pilot)
    declared = list(stage1["cell_ids"])
    if len(declared) != len(set(declared)):
        raise ValueError("duplicate Stage-1 cell declaration")
    if set(declared) != set(cells):
        raise ValueError("Stage-1 cell declarations differ from pilot cells")

    dispatch = contract["dispatch_by_event_id"]
    if set(dispatch) != {"E1", "E3", "E4"}:
        raise ValueError("Stage-1 dispatch must cover E1 E3 and E4 only")
    if {row["runtime_family"] for row in dispatch.values()} != {
        "command",
        "recovery",
        "observability",
    }:
        raise ValueError("Stage-1 dispatch runtime families are incomplete")

    for cell_id in declared:
        cell = cells[cell_id]
        event_id = cell["event_id"]
        if event_id not in dispatch:
            raise ValueError(f"{cell_id}: no Stage-1 dispatch for {event_id}")
        runtime_family = dispatch[event_id]["runtime_family"]
        family_prefix = cell["family"].split("_", 1)[0]
        if family_prefix != runtime_family:
            raise ValueError(
                f"{cell_id}: pilot family and runtime dispatch disagree"
            )

    ledger_contract = contract["attempt_ledger"]
    if ledger_contract["retain_all_attempts"] is not True:
        raise ValueError("Stage-1 ledger must retain all attempts")
    if ledger_contract["duplicate_run_id_rejected"] is not True:
        raise ValueError("Stage-1 ledger must reject duplicate run IDs")
    if ledger_contract["invalid_attempt_keeps_seed"] is not True:
        raise ValueError("invalid Stage-1 attempt must keep seed")
    if ledger_contract["stage_2_requires_all_stage_1_cells_valid"] is not True:
        raise ValueError("Stage 2 must require all Stage-1 cells valid")
    if (
        ledger_contract["infrastructure_invalid_fraction_denominator"]
        != "declared_stage_1_cell_count"
    ):
        raise ValueError("unexpected infrastructure-invalid denominator")
    if int(ledger_contract["same_cause_repeat_threshold"]) != 2:
        raise ValueError("same-cause infrastructure threshold must be 2")

    if invalid_rule["retain_all_invalid_runs"] is not True:
        raise ValueError("invalid-run retention contract changed")
    if invalid_rule["replacement_run_requires_new_run_id"] is not True:
        raise ValueError("replacement run-id contract changed")
    if (
        invalid_rule[
            "same_cause_repeated_infrastructure_failure_blocks_stage_progression"
        ]
        is not True
    ):
        raise ValueError("same-cause infrastructure halt contract changed")
    if float(invalid_rule["maximum_infrastructure_invalid_fraction_before_pilot_halt"]) != 0.1:
        raise ValueError("infrastructure-invalid fraction threshold changed")

    if gate["component_status"]["nos3_runtime_binding"] is not True:
        raise ValueError("NOS3 runtime binding must be closed before Stage-1 work")
    if not isinstance(gate["pilot_execution_authorized"], bool):
        raise ValueError("pilot_execution_authorized must be boolean")


def deterministic_stage1_cell_ids(pilot: dict[str, Any]) -> list[str]:
    validate_stage1_contract(pilot)
    stage1 = pilot[STAGE1_KEY]
    seed = int(stage1["seed"])
    ids = list(stage1["cell_ids"])

    def rank(cell_id: str) -> bytes:
        material = f"WP8-STAGE1|{seed}|{cell_id}".encode("utf-8")
        return hashlib.sha256(material).digest()

    return sorted(ids, key=rank)


def dispatch_for_cell(
    pilot: dict[str, Any],
    cell: dict[str, Any],
) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    dispatch = pilot["stage_1_runner_contract"]["dispatch_by_event_id"]
    result = deepcopy(dispatch[cell["event_id"]])
    result["cell_id"] = cell["cell_id"]
    result["event_id"] = cell["event_id"]
    return result


def build_offline_stage1_plan(pilot: dict[str, Any]) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not False:
        raise ValueError("offline Stage-1 planning requires pilot execution blocked")
    cells = _cells_by_id(pilot)
    stage1 = pilot[STAGE1_KEY]
    order = deterministic_stage1_cell_ids(pilot)

    planned = []
    for position, cell_id in enumerate(order, start=1):
        cell = deepcopy(cells[cell_id])
        planned.append(
            {
                "position": position,
                "cell": cell,
                "dispatch": dispatch_for_cell(pilot, cell),
            }
        )

    return {
        "schema": 1,
        "classification": "WP8_STAGE1_OFFLINE_EXECUTION_PLAN",
        "decision_id": "R-028",
        "runner_version": RUNNER_VERSION,
        "seed": int(stage1["seed"]),
        "ordering_method": ORDERING_METHOD,
        "ordered_cell_ids": order,
        "planned_cells": planned,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
    }


def allocate_run_id(
    *,
    cell_id: str,
    seed: int,
    now: datetime | None = None,
    token_factory: Callable[[], str] | None = None,
) -> str:
    when = now or datetime.now(timezone.utc)
    if when.tzinfo is None:
        raise ValueError("run-id timestamp must be timezone-aware")
    when = when.astimezone(timezone.utc)
    token = (
        token_factory()
        if token_factory is not None
        else uuid.uuid4().hex
    )
    if not token or any(ch not in "0123456789abcdefABCDEF" for ch in token):
        raise ValueError("run-id token must be non-empty hexadecimal")
    stamp = when.strftime("%Y%m%dT%H%M%S.%fZ")
    return (
        f"{stamp}-wp8-stage1-{cell_id.lower()}-s{int(seed)}-"
        f"{token.lower()}"
    )


def new_stage1_ledger(pilot: dict[str, Any]) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    return {
        "schema": 1,
        "decision_id": "R-028",
        "stage": "stage_1_control_validity",
        "seed": int(pilot[STAGE1_KEY]["seed"]),
        "attempts": [],
    }


def record_attempt(
    *,
    pilot: dict[str, Any],
    ledger: dict[str, Any],
    cell_id: str,
    run_id: str,
    status: str,
    retained_evidence_ref: str,
    schema_valid: bool = False,
    raw_metric_inputs_complete: bool = False,
    expected_policy_semantics_met: bool = False,
    invalid_class: str | None = None,
    invalid_cause: str | None = None,
) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    cells = _cells_by_id(pilot)
    if cell_id not in cells:
        raise ValueError(f"unknown Stage-1 cell: {cell_id}")
    if int(ledger["seed"]) != int(pilot[STAGE1_KEY]["seed"]):
        raise ValueError("Stage-1 ledger seed differs from frozen seed")
    if not retained_evidence_ref:
        raise ValueError("attempt requires retained evidence reference")
    if any(row["run_id"] == run_id for row in ledger["attempts"]):
        raise ValueError("duplicate Stage-1 run_id")
    if status not in {"VALID", "RUN_INVALID"}:
        raise ValueError("unsupported Stage-1 attempt status")

    row: dict[str, Any] = {
        "attempt_index": len(ledger["attempts"]) + 1,
        "cell_id": cell_id,
        "seed": int(ledger["seed"]),
        "run_id": run_id,
        "status": status,
        "retained_evidence_ref": retained_evidence_ref,
        "schema_valid": bool(schema_valid),
        "raw_metric_inputs_complete": bool(raw_metric_inputs_complete),
        "expected_policy_semantics_met": bool(expected_policy_semantics_met),
    }

    if status == "VALID":
        if not (
            row["schema_valid"]
            and row["raw_metric_inputs_complete"]
            and row["expected_policy_semantics_met"]
        ):
            raise ValueError(
                "VALID Stage-1 attempt requires schema raw inputs and policy semantics"
            )
        if invalid_class is not None or invalid_cause is not None:
            raise ValueError("VALID Stage-1 attempt cannot have invalid metadata")
    else:
        if invalid_class not in {"infrastructure", "non_infrastructure"}:
            raise ValueError("RUN_INVALID requires invalid_class")
        if not invalid_cause:
            raise ValueError("RUN_INVALID requires invalid_cause")
        row["invalid_class"] = invalid_class
        row["invalid_cause"] = invalid_cause

    ledger["attempts"].append(row)
    return row


def stage1_progress(
    pilot: dict[str, Any],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    stage1_ids = list(pilot[STAGE1_KEY]["cell_ids"])
    attempts = list(ledger["attempts"])

    valid_cells = {
        row["cell_id"]
        for row in attempts
        if row["status"] == "VALID"
        and row["schema_valid"] is True
        and row["raw_metric_inputs_complete"] is True
        and row["expected_policy_semantics_met"] is True
    }
    missing = [cell_id for cell_id in stage1_ids if cell_id not in valid_cells]

    infra = [
        row
        for row in attempts
        if row["status"] == "RUN_INVALID"
        and row.get("invalid_class") == "infrastructure"
    ]
    denominator = len(stage1_ids)
    infra_fraction = len(infra) / denominator
    threshold = float(
        pilot["invalid_run_rule"][
            "maximum_infrastructure_invalid_fraction_before_pilot_halt"
        ]
    )

    cause_counts = Counter(row["invalid_cause"] for row in infra)
    repeat_threshold = int(
        pilot["stage_1_runner_contract"]["attempt_ledger"][
            "same_cause_repeat_threshold"
        ]
    )
    repeated_causes = sorted(
        cause for cause, count in cause_counts.items() if count >= repeat_threshold
    )

    halt_fraction = infra_fraction > threshold
    halt_repeat = bool(repeated_causes)
    halt = halt_fraction or halt_repeat
    complete = not missing

    return {
        "seed": int(ledger["seed"]),
        "valid_cell_count": len(valid_cells),
        "required_cell_count": denominator,
        "missing_valid_cells": missing,
        "infrastructure_invalid_attempt_count": len(infra),
        "infrastructure_invalid_fraction": infra_fraction,
        "maximum_infrastructure_invalid_fraction": threshold,
        "repeated_infrastructure_causes": repeated_causes,
        "pilot_halt_required": halt,
        "stage_1_all_cells_valid": complete,
        "stage_2_progression_gate_passed": complete and not halt,
        "replacement_attempt_seed": int(ledger["seed"]),
    }


def bind_stage1_runtime_observation(
    *,
    pilot: dict[str, Any],
    toolchain: dict[str, Any],
    schema: dict[str, Any],
    cell_id: str,
    run_id: str,
    observation_bundle: dict[str, Any],
    snapshot_id: str,
    host_architecture: str | None = None,
) -> dict[str, Any]:
    validate_stage1_contract(pilot)
    gate = pilot["instrumentation_gate"]
    if gate["pilot_execution_authorized"] is not True:
        raise PermissionError("WP8 Stage-1 pilot execution is not authorized")

    cells = _cells_by_id(pilot)
    if cell_id not in cells:
        raise ValueError(f"unknown Stage-1 cell: {cell_id}")
    cell = cells[cell_id]
    seed = int(pilot[STAGE1_KEY]["seed"])

    factor = observation_bundle["factor_context"]
    expected_factor = {
        "run_id": run_id,
        "model_version": pilot["model_version"],
        "seed": seed,
        "mission_state_id": cell["mission_state_id"],
        "event_id": cell["event_id"],
        "policy_id": cell["policy_id"],
        "contact_condition_id": cell["contact_condition_id"],
        "evidence_condition_id": cell["evidence_condition_id"],
    }
    if factor != expected_factor:
        raise ValueError("retained runtime factor context differs from Stage-1 cell")

    execution_metadata = observation_bundle.get("execution_metadata")
    if not isinstance(execution_metadata, dict):
        raise ValueError("retained runtime observation lacks execution metadata")
    if "effective_policy_id" not in execution_metadata:
        raise ValueError("retained runtime observation lacks actual effective policy")
    actual_effective = execution_metadata["effective_policy_id"]
    if actual_effective != cell["expected_effective_policy_id"]:
        raise ValueError("observed effective policy differs from frozen cell semantics")

    runtime_observation = observation_bundle["runtime_observation"]
    expected_family = dispatch_for_cell(pilot, cell)["runtime_family"]
    if runtime_observation["family"] != expected_family:
        raise ValueError("retained observation dispatched through wrong runtime family")
    if runtime_observation.get("development_preflight", False) is not False:
        raise ValueError("Stage-1 pilot observation cannot be development preflight")
    if runtime_observation.get("pilot_data") is not True:
        raise ValueError("Stage-1 pilot observation must explicitly mark pilot_data=true")

    environment = environment_from_toolchain_lock(
        toolchain,
        snapshot_id=snapshot_id,
        host_architecture=host_architecture,
    )
    result = bind_runtime_observation(
        contract=pilot["runtime_measurement_contract"],
        factor_context=factor,
        environment=environment,
        observation=runtime_observation,
        notes=observation_bundle.get("notes"),
    )

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(result["run_record"]),
        key=lambda err: list(err.path),
    )
    if errors:
        raise ValueError("Stage-1 bound run record is not schema-valid")

    provenance = result["binding_provenance"]
    if provenance["development_preflight"] is not False:
        raise ValueError("Stage-1 provenance incorrectly marked development preflight")
    if provenance["pilot_data"] is not True:
        raise ValueError("Stage-1 provenance is not marked pilot data")

    return {
        **result,
        "stage1_acceptance": {
            "cell_id": cell_id,
            "seed": seed,
            "schema_valid": True,
            "raw_metric_inputs_complete": True,
            "expected_policy_semantics_met": True,
            "actual_effective_policy_id": actual_effective,
        },
    }


def _cmd_plan(args: argparse.Namespace) -> int:
    pilot = load_json(args.pilot_config)
    plan = build_offline_stage1_plan(pilot)
    output = json.dumps(plan, sort_keys=True, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    print("WP8_STAGE1_OFFLINE_PLAN_STATUS=PASS")
    print("pilot_execution_authorized=false")
    print("pilot_seed_consumed=false")
    print("pilot_data_generated=false")
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    pilot = load_json(args.pilot_config)
    ledger = load_json(args.ledger_json)
    progress = stage1_progress(pilot, ledger)
    print(json.dumps(progress, sort_keys=True, indent=2))
    print("WP8_STAGE1_LEDGER_AUDIT_STATUS=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--pilot-config", required=True)
    plan.add_argument("--output-json")
    plan.set_defaults(func=_cmd_plan)

    audit = sub.add_parser("audit-ledger")
    audit.add_argument("--pilot-config", required=True)
    audit.add_argument("--ledger-json", required=True)
    audit.set_defaults(func=_cmd_audit)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
