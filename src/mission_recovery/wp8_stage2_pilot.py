from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

from .wp8_runtime_binding import (
    bind_runtime_observation,
    environment_from_toolchain_lock,
)
from .wp8_stage1_family_dispatch import (
    PILOT_RUNTIME_PATH_BY_CELL,
    PILOT_RUNTIME_PATH_FAMILY,
)
from .wp8_stage1_pilot import stage1_progress, validate_stage1_contract

ORDERING_METHOD = "sha256_rank_v1"
RUNNER_VERSION = "0.1.0"
STAGE2_KEY = "stage_2_variability"
RUN_ID_PATTERN = re.compile(
    r"^\d{8}T\d{6}\.\d{6}Z-wp8-stage2-"
    r"(?P<cell>[a-z0-9]+)-s(?P<seed>\d+)-(?P<token>[0-9a-f]{32})$"
)


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cells_by_id(pilot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cells = pilot["cells"]
    by_id = {row["cell_id"]: row for row in cells}
    if len(by_id) != len(cells):
        raise ValueError("duplicate pilot cell_id")
    return by_id


def validate_stage2_contract(pilot: dict[str, Any]) -> None:
    validate_stage1_contract(pilot)
    stage2 = pilot[STAGE2_KEY]

    seeds = [int(x) for x in stage2["additional_seeds"]]
    anchors = list(stage2["anchor_cell_ids"])

    if seeds != [202, 303, 404, 505]:
        raise ValueError("Stage-2 additional seeds changed")
    if anchors != ["C02", "C03", "C05", "C06", "R02", "R03", "O01"]:
        raise ValueError("Stage-2 anchor cells changed")
    if len(anchors) != len(set(anchors)):
        raise ValueError("duplicate Stage-2 anchor cell")
    if int(stage2["total_valid_repetitions_per_anchor_after_stage_2"]) != 5:
        raise ValueError("Stage-2 total repetitions per anchor changed")
    if stage2["randomize_order_within_seed_block"] is not True:
        raise ValueError("Stage-2 order must be randomized within seed block")
    if stage2["execute_only_after_stage_1_pass"] is not True:
        raise ValueError("Stage-2 must remain gated on Stage-1 pass")

    cells = _cells_by_id(pilot)
    for cell_id in anchors:
        if cell_id not in cells:
            raise ValueError(f"unknown Stage-2 anchor cell: {cell_id}")
        path = PILOT_RUNTIME_PATH_BY_CELL[cell_id]
        if path == "recovery_generic":
            raise ValueError("Stage-2 cannot route through generic recovery")
        if path not in {
            "command_generic",
            "recovery_full_trusted",
            "observability_generic",
        }:
            raise ValueError(f"unsupported Stage-2 runtime path: {path}")


def stage2_order_for_seed(
    pilot: dict[str, Any],
    seed: int,
) -> list[str]:
    validate_stage2_contract(pilot)
    seeds = [int(x) for x in pilot[STAGE2_KEY]["additional_seeds"]]
    if int(seed) not in seeds:
        raise ValueError(f"unknown Stage-2 seed: {seed}")
    anchors = list(pilot[STAGE2_KEY]["anchor_cell_ids"])

    def rank(cell_id: str) -> bytes:
        material = f"WP8-STAGE2|{int(seed)}|{cell_id}".encode("utf-8")
        return hashlib.sha256(material).digest()

    return sorted(anchors, key=rank)


def stage2_execution_plan(pilot: dict[str, Any]) -> list[dict[str, Any]]:
    validate_stage2_contract(pilot)
    plan: list[dict[str, Any]] = []
    position = 0
    for seed in [int(x) for x in pilot[STAGE2_KEY]["additional_seeds"]]:
        for cell_id in stage2_order_for_seed(pilot, seed):
            position += 1
            plan.append(
                {
                    "position": position,
                    "seed": seed,
                    "cell_id": cell_id,
                    "runtime_path": PILOT_RUNTIME_PATH_BY_CELL[cell_id],
                    "runtime_family": PILOT_RUNTIME_PATH_FAMILY[
                        PILOT_RUNTIME_PATH_BY_CELL[cell_id]
                    ],
                }
            )
    if len(plan) != 28:
        raise ValueError("Stage-2 execution plan must contain 28 repetitions")
    return plan


def allocate_stage2_run_id(
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
    token = token_factory() if token_factory is not None else uuid.uuid4().hex
    if not token or any(ch not in "0123456789abcdefABCDEF" for ch in token):
        raise ValueError("run-id token must be non-empty hexadecimal")
    stamp = when.strftime("%Y%m%dT%H%M%S.%fZ")
    return (
        f"{stamp}-wp8-stage2-{cell_id.lower()}-s{int(seed)}-"
        f"{token.lower()}"
    )


def validate_stage2_run_id(
    *,
    pilot: dict[str, Any],
    cell_id: str,
    seed: int,
    run_id: str,
) -> None:
    validate_stage2_contract(pilot)
    if cell_id not in pilot[STAGE2_KEY]["anchor_cell_ids"]:
        raise ValueError(f"cell is not a Stage-2 anchor: {cell_id}")
    if int(seed) not in {
        int(x) for x in pilot[STAGE2_KEY]["additional_seeds"]
    }:
        raise ValueError(f"seed is not a frozen Stage-2 seed: {seed}")
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if match is None:
        raise ValueError("run_id is not a controller-allocated Stage-2 identity")
    if match.group("cell") != cell_id.lower():
        raise ValueError("run_id cell differs from Stage-2 cell")
    if int(match.group("seed")) != int(seed):
        raise ValueError("run_id seed differs from Stage-2 seed")


def new_stage2_ledger(pilot: dict[str, Any]) -> dict[str, Any]:
    validate_stage2_contract(pilot)
    return {
        "schema": 1,
        "stage": "stage_2_variability",
        "ordering_method": ORDERING_METHOD,
        "runner_version": RUNNER_VERSION,
        "additional_seeds": [
            int(x) for x in pilot[STAGE2_KEY]["additional_seeds"]
        ],
        "anchor_cell_ids": list(pilot[STAGE2_KEY]["anchor_cell_ids"]),
        "attempts": [],
    }


def validate_stage2_ledger(
    pilot: dict[str, Any],
    ledger: dict[str, Any],
) -> None:
    validate_stage2_contract(pilot)
    if ledger.get("schema") != 1:
        raise ValueError("unexpected Stage-2 ledger schema")
    if ledger.get("stage") != "stage_2_variability":
        raise ValueError("unexpected Stage-2 ledger stage")
    if ledger.get("ordering_method") != ORDERING_METHOD:
        raise ValueError("Stage-2 ledger ordering changed")
    if ledger.get("runner_version") != RUNNER_VERSION:
        raise ValueError("Stage-2 ledger runner version changed")
    if ledger.get("additional_seeds") != [
        int(x) for x in pilot[STAGE2_KEY]["additional_seeds"]
    ]:
        raise ValueError("Stage-2 ledger seeds differ from frozen design")
    if ledger.get("anchor_cell_ids") != list(
        pilot[STAGE2_KEY]["anchor_cell_ids"]
    ):
        raise ValueError("Stage-2 ledger anchors differ from frozen design")
    seen: set[str] = set()
    for row in ledger.get("attempts", []):
        run_id = row["run_id"]
        if run_id in seen:
            raise ValueError("duplicate Stage-2 run_id")
        seen.add(run_id)
        validate_stage2_run_id(
            pilot=pilot,
            cell_id=row["cell_id"],
            seed=int(row["seed"]),
            run_id=run_id,
        )
        if row["status"] not in {"VALID", "RUN_INVALID"}:
            raise ValueError("unsupported Stage-2 attempt status")


def record_stage2_attempt(
    *,
    pilot: dict[str, Any],
    ledger: dict[str, Any],
    cell_id: str,
    seed: int,
    run_id: str,
    status: str,
    retained_evidence_ref: str,
    schema_valid: bool = False,
    raw_metric_inputs_complete: bool = False,
    expected_policy_semantics_met: bool = False,
    invalid_class: str | None = None,
    invalid_cause: str | None = None,
) -> dict[str, Any]:
    validate_stage2_ledger(pilot, ledger)
    validate_stage2_run_id(
        pilot=pilot,
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
    )
    if any(row["run_id"] == run_id for row in ledger["attempts"]):
        raise ValueError("duplicate Stage-2 run_id")
    if not retained_evidence_ref:
        raise ValueError("Stage-2 attempt requires retained evidence reference")
    if status not in {"VALID", "RUN_INVALID"}:
        raise ValueError("unsupported Stage-2 attempt status")

    row: dict[str, Any] = {
        "attempt_index": len(ledger["attempts"]) + 1,
        "cell_id": cell_id,
        "seed": int(seed),
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
                "VALID Stage-2 attempt requires schema raw inputs and policy semantics"
            )
        if invalid_class is not None or invalid_cause is not None:
            raise ValueError("VALID Stage-2 attempt cannot have invalid metadata")
    else:
        if invalid_class not in {"infrastructure", "non_infrastructure"}:
            raise ValueError("RUN_INVALID requires invalid_class")
        if not invalid_cause:
            raise ValueError("RUN_INVALID requires invalid_cause")
        row["invalid_class"] = invalid_class
        row["invalid_cause"] = invalid_cause

    ledger["attempts"].append(row)
    return row


def stage2_progress(
    pilot: dict[str, Any],
    stage1_ledger: dict[str, Any],
    stage2_ledger: dict[str, Any],
    *,
    reviewed_invalid_run_ids: set[str] | None = None,
) -> dict[str, Any]:
    validate_stage2_ledger(pilot, stage2_ledger)
    stage1 = stage1_progress(pilot, stage1_ledger)
    if stage1["stage_2_progression_gate_passed"] is not True:
        raise PermissionError("Stage-1 progression gate is not passed")

    attempts = list(stage2_ledger["attempts"])
    invalid = [row for row in attempts if row["status"] == "RUN_INVALID"]
    reviewed = reviewed_invalid_run_ids or set()
    invalid_ids = {row["run_id"] for row in invalid}
    if not reviewed.issubset(invalid_ids):
        raise ValueError("reviewed Stage-2 invalid run ID is not retained in ledger")
    unreviewed_invalid = [
        row for row in invalid if row["run_id"] not in reviewed
    ]
    valid_pairs = {
        (int(row["seed"]), row["cell_id"])
        for row in attempts
        if row["status"] == "VALID"
        and row["schema_valid"] is True
        and row["raw_metric_inputs_complete"] is True
        and row["expected_policy_semantics_met"] is True
    }
    plan = stage2_execution_plan(pilot)
    missing = [
        row for row in plan
        if (int(row["seed"]), row["cell_id"]) not in valid_pairs
    ]
    blocked = bool(unreviewed_invalid)
    next_item = None if blocked or not missing else deepcopy(missing[0])

    return {
        "required_valid_repetitions": len(plan),
        "valid_repetition_count": len(valid_pairs),
        "remaining_valid_repetitions": len(missing),
        "run_invalid_attempt_count": len(invalid),
        "reviewed_invalid_attempt_count": len(invalid) - len(unreviewed_invalid),
        "unreviewed_invalid_attempt_count": len(unreviewed_invalid),
        "progression_blocked_for_review": blocked,
        "stage_2_complete": not missing and not blocked,
        "next_repetition": next_item,
    }


def bind_stage2_runtime_observation(
    *,
    pilot: dict[str, Any],
    toolchain: dict[str, Any],
    schema: dict[str, Any],
    cell_id: str,
    seed: int,
    run_id: str,
    observation_bundle: dict[str, Any],
    snapshot_id: str,
    host_architecture: str | None = None,
) -> dict[str, Any]:
    validate_stage2_run_id(
        pilot=pilot,
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
    )
    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not True:
        raise PermissionError("WP8 pilot execution is not authorized")

    cells = _cells_by_id(pilot)
    cell = cells[cell_id]
    factor = observation_bundle["factor_context"]
    expected_factor = {
        "run_id": run_id,
        "model_version": pilot["model_version"],
        "seed": int(seed),
        "mission_state_id": cell["mission_state_id"],
        "event_id": cell["event_id"],
        "policy_id": cell["policy_id"],
        "contact_condition_id": cell["contact_condition_id"],
        "evidence_condition_id": cell["evidence_condition_id"],
    }
    if factor != expected_factor:
        raise ValueError("retained runtime factor context differs from Stage-2 repetition")

    execution_metadata = observation_bundle.get("execution_metadata")
    if not isinstance(execution_metadata, dict):
        raise ValueError("retained Stage-2 observation lacks execution metadata")
    actual_effective = execution_metadata.get("effective_policy_id")
    if actual_effective != cell["expected_effective_policy_id"]:
        raise ValueError(
            "observed effective policy differs from frozen Stage-2 acceptance semantics"
        )

    runtime_observation = observation_bundle.get("runtime_observation")
    if not isinstance(runtime_observation, dict):
        raise ValueError("retained Stage-2 observation lacks runtime observation")
    path = PILOT_RUNTIME_PATH_BY_CELL[cell_id]
    expected_family = PILOT_RUNTIME_PATH_FAMILY[path]
    if runtime_observation.get("family") != expected_family:
        raise ValueError("Stage-2 observation dispatched through wrong runtime family")
    if runtime_observation.get("development_preflight") is not False:
        raise ValueError("Stage-2 pilot observation cannot be development preflight")
    if runtime_observation.get("pilot_data") is not True:
        raise ValueError("Stage-2 pilot observation must mark pilot_data=true")

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

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(result["run_record"]),
        key=lambda err: list(err.path),
    )
    if errors:
        raise ValueError("Stage-2 bound run record is not schema-valid")

    provenance = result["binding_provenance"]
    if provenance["development_preflight"] is not False:
        raise ValueError("Stage-2 provenance incorrectly marked development")
    if provenance["pilot_data"] is not True:
        raise ValueError("Stage-2 provenance is not marked pilot data")

    return {
        **result,
        "stage2_acceptance": {
            "cell_id": cell_id,
            "seed": int(seed),
            "schema_valid": True,
            "raw_metric_inputs_complete": True,
            "expected_policy_semantics_met": True,
            "actual_effective_policy_id": actual_effective,
        },
    }


def _cmd_plan(args: argparse.Namespace) -> int:
    pilot = load_json(args.pilot_config)
    plan = stage2_execution_plan(pilot)
    payload = {
        "schema": 1,
        "ordering_method": ORDERING_METHOD,
        "ordered_repetitions": plan,
        "runtime_execution_authorized": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
    }
    output = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    print("WP8_STAGE2_OFFLINE_PLAN_STATUS=PASS")
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    pilot = load_json(args.pilot_config)
    stage1 = load_json(args.stage1_ledger)
    stage2 = (
        load_json(args.stage2_ledger)
        if Path(args.stage2_ledger).exists()
        else new_stage2_ledger(pilot)
    )
    print(
        json.dumps(
            stage2_progress(pilot, stage1, stage2),
            sort_keys=True,
            indent=2,
        )
    )
    print("WP8_STAGE2_LEDGER_AUDIT_STATUS=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan")
    p.add_argument("--pilot-config", required=True)
    p.add_argument("--output-json")
    p.set_defaults(func=_cmd_plan)

    p = sub.add_parser("audit-ledger")
    p.add_argument("--pilot-config", required=True)
    p.add_argument("--stage1-ledger", required=True)
    p.add_argument("--stage2-ledger", required=True)
    p.set_defaults(func=_cmd_audit)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
