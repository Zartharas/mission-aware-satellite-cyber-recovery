from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy
from .wp8_command_observation_contract import (
    derive_command_runtime_observation,
    require_command_observation_acceptance,
)
from .wp8_stage1_pilot import stage1_progress
from .wp8_stage1_runtime_wiring import (
    _command_raw,
    _read_jsonl,
    _semantic_contract_view,
    command_bundle as shared_command_bundle,
)
from .wp8_stage2_pilot import (
    bind_stage2_runtime_observation,
    load_json,
    stage2_order_for_seed,
    validate_stage2_contract,
    validate_stage2_run_id,
)

DECISION_ID = "WP8-STAGE2-RUNTIME-V1"
COMMAND_ANCHORS = ("C02", "C03", "C05", "C06")
FULL_RECOVERY_ANCHORS = ("R02", "R03")
OBSERVABILITY_ANCHOR = "O01"


def _write(path: str | Path, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _cell(pilot: dict[str, Any], cell_id: str) -> dict[str, Any]:
    cells = {row["cell_id"]: row for row in pilot["cells"]}
    if cell_id not in cells:
        raise ValueError(f"unknown pilot cell: {cell_id}")
    return deepcopy(cells[cell_id])


def _require_stage2_runtime(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    seed: int,
) -> None:
    validate_stage2_contract(pilot)
    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not True:
        raise PermissionError("WP8 pilot execution is not authorized")
    if cell_id not in pilot["stage_2_variability"]["anchor_cell_ids"]:
        raise ValueError(f"cell is not a frozen Stage-2 anchor: {cell_id}")
    if int(seed) not in {
        int(x) for x in pilot["stage_2_variability"]["additional_seeds"]
    }:
        raise ValueError(f"seed is not a frozen Stage-2 seed: {seed}")


def _factor(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    seed: int,
    run_id: str,
) -> dict[str, Any]:
    _require_stage2_runtime(pilot, cell_id=cell_id, seed=seed)
    validate_stage2_run_id(
        pilot=pilot,
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
    )
    cell = _cell(pilot, cell_id)
    return {
        "run_id": run_id,
        "model_version": pilot["model_version"],
        "seed": int(seed),
        "mission_state_id": cell["mission_state_id"],
        "event_id": cell["event_id"],
        "policy_id": cell["policy_id"],
        "contact_condition_id": cell["contact_condition_id"],
        "evidence_condition_id": cell["evidence_condition_id"],
    }


def _exact_factor_from_retained(
    pilot: dict[str, Any],
    retained: dict[str, Any],
    *,
    cell_id: str,
) -> dict[str, Any]:
    seed = int(retained["seed"])
    expected = _factor(
        pilot,
        cell_id=cell_id,
        seed=seed,
        run_id=retained["run_id"],
    )
    for key, value in expected.items():
        if retained.get(key) != value:
            raise ValueError(
                f"{cell_id}: retained factor differs from Stage-2 repetition: {key}"
            )
    return expected


def _select_policy(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    event: dict[str, Any],
) -> dict[str, Any]:
    seed = int(event["seed"])
    _require_stage2_runtime(pilot, cell_id=cell_id, seed=seed)
    cell = _cell(pilot, cell_id)
    factor_keys = {
        "event_id": "event_id",
        "mission_state": "mission_state_id",
        "contact_condition": "contact_condition_id",
        "evidence_condition": "evidence_condition_id",
    }
    for event_key, cell_key in factor_keys.items():
        if event[event_key] != cell[cell_key]:
            raise ValueError(
                f"runtime event {event_key} differs from frozen Stage-2 anchor"
            )
    decision = evaluate_policy(cell["policy_id"], event)
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("Stage-2 policy selection cannot read ground truth")
    result = deepcopy(decision)
    result.update(
        {
            "schema": 1,
            "decision_id": DECISION_ID,
            "cell_id": cell_id,
            "runtime_policy_selection": True,
            "development_preflight": False,
            "pilot_data": True,
        }
    )
    return result


def command_plan(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    seed: int,
    run_id: str,
) -> dict[str, Any]:
    if cell_id not in COMMAND_ANCHORS:
        raise ValueError("Stage-2 command runtime supports C02/C03/C05/C06 only")
    factor = _factor(
        pilot,
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
    )
    cell = _cell(pilot, cell_id)
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=int(seed),
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_STAGE2_COMMAND_PILOT_PLAN",
        "factor_context": factor,
        "event_instance": event,
        "runtime_path": "command_generic",
        "development_preflight": False,
        "pilot_data": True,
    }


def command_finalize(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    factor: dict[str, Any],
    policy: dict[str, Any],
    gateway_rows: list[dict[str, Any]],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    seed = int(factor["seed"])
    _require_stage2_runtime(pilot, cell_id=cell_id, seed=seed)
    if cell_id not in COMMAND_ANCHORS:
        raise ValueError("Stage-2 command runtime supports C02/C03/C05/C06 only")
    if len(gateway_rows) != 3:
        raise ValueError("Stage-2 command pilot requires three gateway decisions")
    raw = _command_raw(
        factor=factor,
        policy=policy,
        measurement=measurement,
    )
    derived = derive_command_runtime_observation(
        pilot=_semantic_contract_view(pilot),
        cell_id=cell_id,
        observation=raw,
    )
    require_command_observation_acceptance(derived)
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "run_id": factor["run_id"],
        "factor_context": deepcopy(factor),
        "raw_observation": raw,
        "derived_command_observation": derived,
        "development_preflight": False,
        "pilot_data": True,
    }


def command_bundle(
    *,
    pilot: dict[str, Any],
    factor: dict[str, Any],
    policy: dict[str, Any],
    finalized: dict[str, Any],
    gateway_rows: list[dict[str, Any]],
    evidence_prefix: str,
    nominal_log: Path,
    runtime_manifest: Path,
    classification_path: Path,
    run_start_ns: int,
    run_start_utc: str,
    run_end_utc: str,
) -> dict[str, Any]:
    seed = int(factor["seed"])
    _require_stage2_runtime(
        pilot,
        cell_id=finalized["cell_id"],
        seed=seed,
    )
    bundle = shared_command_bundle(
        pilot=pilot,
        factor=factor,
        policy=policy,
        finalized=finalized,
        gateway_rows=gateway_rows,
        evidence_prefix=evidence_prefix,
        nominal_log=nominal_log,
        runtime_manifest=runtime_manifest,
        classification_path=classification_path,
        run_start_ns=run_start_ns,
        run_start_utc=run_start_utc,
        run_end_utc=run_end_utc,
    )
    bundle["notes"] = (
        "WP8 Stage-2 command variability repetition; controlled NOS3 "
        "SAMPLE-state surrogate only."
    )
    return bundle


def transform_full_recovery_bundle(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    factor: dict[str, Any],
    policy: dict[str, Any],
    observation: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if cell_id not in FULL_RECOVERY_ANCHORS:
        raise ValueError("Stage-2 full recovery supports R02/R03 only")
    exact = _exact_factor_from_retained(
        pilot,
        factor,
        cell_id=cell_id,
    )
    criteria = manifest["trusted_recovery_criteria"]
    if len(criteria) != 10 or not all(value is True for value in criteria.values()):
        raise ValueError("Stage-2 full recovery lacks all-ten proof")

    runtime = deepcopy(observation["runtime_observation"])
    runtime["development_preflight"] = False
    runtime["pilot_data"] = True
    for criterion, row in runtime["recovery_observations"].items():
        row["criterion_satisfied"] = bool(criteria[criterion])

    manifest_out = deepcopy(manifest)
    manifest_out["policy_id"] = exact["policy_id"]
    manifest_out["requested_policy_id"] = exact["policy_id"]
    manifest_out["effective_policy_id"] = policy["delegated_policy_id"]
    manifest_out["development_preflight"] = False
    manifest_out["pilot_data"] = True

    return (
        {
            "factor_context": exact,
            "execution_metadata": {
                "effective_policy_id": policy["delegated_policy_id"],
                "selected_action": policy["selected_action"],
                "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
            },
            "runtime_observation": runtime,
            "notes": (
                "WP8 Stage-2 full trusted-recovery variability repetition; "
                "all ten criteria derive from retained runtime evidence."
            ),
        },
        manifest_out,
    )


def transform_observability_bundle(
    pilot: dict[str, Any],
    *,
    factor: dict[str, Any],
    policy: dict[str, Any],
    observation: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    exact = _exact_factor_from_retained(
        pilot,
        factor,
        cell_id=OBSERVABILITY_ANCHOR,
    )
    criteria = manifest["trusted_recovery_criteria"]
    runtime = deepcopy(observation["runtime_observation"])
    runtime["development_preflight"] = False
    runtime["pilot_data"] = True
    for criterion, row in runtime["recovery_observations"].items():
        row["criterion_satisfied"] = bool(criteria[criterion])

    manifest_out = deepcopy(manifest)
    manifest_out["requested_policy_id"] = exact["policy_id"]
    manifest_out["effective_policy_id"] = policy["delegated_policy_id"]
    manifest_out["development_preflight"] = False
    manifest_out["pilot_data"] = True

    return (
        {
            "factor_context": exact,
            "execution_metadata": {
                "effective_policy_id": policy["delegated_policy_id"],
                "selected_action": policy["selected_action"],
                "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
            },
            "runtime_observation": runtime,
            "notes": (
                "WP8 Stage-2 O01 variability repetition; RECOVERY_FAILED "
                "remains bounded E4 containment failure only."
            ),
        },
        manifest_out,
    )


def _bind_outputs(
    *,
    pilot_path: str,
    toolchain_path: str,
    schema_path: str,
    cell_id: str,
    seed: int,
    run_id: str,
    bundle: dict[str, Any],
    bundle_path: str,
    run_record_path: str,
    provenance_path: str,
    acceptance_path: str,
    snapshot_id: str,
    host_architecture: str | None,
) -> None:
    result = bind_stage2_runtime_observation(
        pilot=load_json(pilot_path),
        toolchain=load_json(toolchain_path),
        schema=load_json(schema_path),
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
        observation_bundle=bundle,
        snapshot_id=snapshot_id,
        host_architecture=host_architecture,
    )
    _write(bundle_path, bundle)
    _write(run_record_path, result["run_record"])
    _write(provenance_path, result["binding_provenance"])
    _write(acceptance_path, result["stage2_acceptance"])


def _check_gate(args: argparse.Namespace) -> int:
    pilot = load_json(args.pilot_config)
    stage1_ledger = load_json(args.stage1_ledger)
    progress = stage1_progress(pilot, stage1_ledger)
    if progress["stage_2_progression_gate_passed"] is not True:
        raise PermissionError("Stage-1 progression gate is not passed")
    _factor(
        pilot,
        cell_id=args.cell_id,
        seed=args.seed,
        run_id=args.run_id,
    )
    print("wp8_stage2_pilot_gate=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-gate")
    for name in ("pilot-config", "stage1-ledger", "cell-id", "run-id"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--seed", required=True, type=int)

    p = sub.add_parser("command-plan")
    for name in (
        "pilot-config",
        "cell-id",
        "run-id",
        "output-plan-json",
        "output-factor-json",
        "output-event-json",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--development-seed", required=True, type=int)

    p = sub.add_parser("command-select-policy")
    for name in (
        "pilot-config",
        "cell-id",
        "event-json",
        "output-policy-json",
    ):
        p.add_argument("--" + name, required=True)

    p = sub.add_parser("command-finalize-observation")
    for name in (
        "pilot-config",
        "cell-id",
        "factor-json",
        "policy-json",
        "gateway-decisions-jsonl",
        "measurement-json",
        "output-json",
    ):
        p.add_argument("--" + name, required=True)

    p = sub.add_parser("command-bind-pilot")
    for name in (
        "pilot-config",
        "toolchain-lock",
        "schema",
        "cell-id",
        "factor-json",
        "policy-json",
        "finalized-json",
        "gateway-decisions-jsonl",
        "evidence-prefix",
        "nominal-log",
        "runtime-manifest",
        "classification-json",
        "run-start-utc",
        "run-end-utc",
        "bundle-json",
        "run-record-json",
        "provenance-json",
        "acceptance-json",
        "snapshot-id",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--run-start-ns", required=True, type=int)
    p.add_argument("--host-architecture")

    p = sub.add_parser("full-recovery-validate-factor")
    for name in (
        "pilot-config",
        "cell-id",
        "factor-json",
        "repo-commit",
    ):
        p.add_argument("--" + name, required=True)

    p = sub.add_parser("full-recovery-bind-existing")
    for name in (
        "pilot-config",
        "toolchain-lock",
        "schema",
        "cell-id",
        "factor-json",
        "policy-json",
        "observation-json",
        "manifest-json",
        "summary-json",
        "bundle-json",
        "run-record-json",
        "provenance-json",
        "acceptance-json",
        "snapshot-id",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--host-architecture")

    p = sub.add_parser("observability-bind-existing")
    for name in (
        "pilot-config",
        "toolchain-lock",
        "schema",
        "factor-json",
        "policy-json",
        "observation-json",
        "manifest-json",
        "summary-json",
        "bundle-json",
        "run-record-json",
        "provenance-json",
        "acceptance-json",
        "snapshot-id",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--host-architecture")

    args = parser.parse_args()

    if args.command == "check-gate":
        return _check_gate(args)

    if args.command == "command-plan":
        pilot = load_json(args.pilot_config)
        value = command_plan(
            pilot,
            cell_id=args.cell_id,
            seed=args.development_seed,
            run_id=args.run_id,
        )
        _write(args.output_plan_json, value)
        _write(args.output_factor_json, value["factor_context"])
        _write(args.output_event_json, value["event_instance"])
        print("command_stage2_pilot_plan=PASS")
        return 0

    if args.command == "command-select-policy":
        value = _select_policy(
            load_json(args.pilot_config),
            cell_id=args.cell_id,
            event=load_json(args.event_json),
        )
        _write(args.output_policy_json, value)
        print("command_stage2_pilot_policy_selection=PASS")
        return 0

    if args.command == "command-finalize-observation":
        value = command_finalize(
            load_json(args.pilot_config),
            cell_id=args.cell_id,
            factor=load_json(args.factor_json),
            policy=load_json(args.policy_json),
            gateway_rows=_read_jsonl(args.gateway_decisions_jsonl),
            measurement=load_json(args.measurement_json),
        )
        _write(args.output_json, value)
        print("command_stage2_pilot_observation=PASS")
        return 0

    if args.command == "command-bind-pilot":
        pilot = load_json(args.pilot_config)
        factor = load_json(args.factor_json)
        policy = load_json(args.policy_json)
        finalized = load_json(args.finalized_json)
        rows = _read_jsonl(args.gateway_decisions_jsonl)
        bundle = command_bundle(
            pilot=pilot,
            factor=factor,
            policy=policy,
            finalized=finalized,
            gateway_rows=rows,
            evidence_prefix=args.evidence_prefix,
            nominal_log=Path(args.nominal_log),
            runtime_manifest=Path(args.runtime_manifest),
            classification_path=Path(args.classification_json),
            run_start_ns=args.run_start_ns,
            run_start_utc=args.run_start_utc,
            run_end_utc=args.run_end_utc,
        )
        _bind_outputs(
            pilot_path=args.pilot_config,
            toolchain_path=args.toolchain_lock,
            schema_path=args.schema,
            cell_id=args.cell_id,
            seed=int(factor["seed"]),
            run_id=factor["run_id"],
            bundle=bundle,
            bundle_path=args.bundle_json,
            run_record_path=args.run_record_json,
            provenance_path=args.provenance_json,
            acceptance_path=args.acceptance_json,
            snapshot_id=args.snapshot_id,
            host_architecture=args.host_architecture,
        )
        print("command_stage2_pilot_binding=PASS")
        return 0

    if args.command == "full-recovery-validate-factor":
        pilot = load_json(args.pilot_config)
        retained = load_json(args.factor_json)
        _exact_factor_from_retained(
            pilot,
            retained,
            cell_id=args.cell_id,
        )
        if retained.get("repo_commit") != args.repo_commit:
            raise ValueError("full recovery retained factor repo_commit mismatch")
        print("full_recovery_stage2_pilot_factor_validation=PASS")
        return 0

    if args.command == "full-recovery-bind-existing":
        pilot = load_json(args.pilot_config)
        factor = load_json(args.factor_json)
        policy = load_json(args.policy_json)
        bundle, manifest = transform_full_recovery_bundle(
            pilot,
            cell_id=args.cell_id,
            factor=factor,
            policy=policy,
            observation=load_json(args.observation_json),
            manifest=load_json(args.manifest_json),
        )
        _write(args.manifest_json, manifest)
        summary = load_json(args.summary_json)
        summary["development_preflight"] = False
        summary["pilot_data"] = True
        summary["study_cell"] = args.cell_id
        summary["stage"] = "stage2"
        _write(args.summary_json, summary)
        _bind_outputs(
            pilot_path=args.pilot_config,
            toolchain_path=args.toolchain_lock,
            schema_path=args.schema,
            cell_id=args.cell_id,
            seed=int(factor["seed"]),
            run_id=bundle["factor_context"]["run_id"],
            bundle=bundle,
            bundle_path=args.bundle_json,
            run_record_path=args.run_record_json,
            provenance_path=args.provenance_json,
            acceptance_path=args.acceptance_json,
            snapshot_id=args.snapshot_id,
            host_architecture=args.host_architecture,
        )
        print("full_recovery_stage2_pilot_binding=PASS")
        return 0

    pilot = load_json(args.pilot_config)
    factor = load_json(args.factor_json)
    policy = load_json(args.policy_json)
    bundle, manifest = transform_observability_bundle(
        pilot,
        factor=factor,
        policy=policy,
        observation=load_json(args.observation_json),
        manifest=load_json(args.manifest_json),
    )
    _write(args.manifest_json, manifest)
    summary = load_json(args.summary_json)
    summary["development_preflight"] = False
    summary["pilot_data"] = True
    summary["stage"] = "stage2"
    _write(args.summary_json, summary)
    _bind_outputs(
        pilot_path=args.pilot_config,
        toolchain_path=args.toolchain_lock,
        schema_path=args.schema,
        cell_id=OBSERVABILITY_ANCHOR,
        seed=int(factor["seed"]),
        run_id=bundle["factor_context"]["run_id"],
        bundle=bundle,
        bundle_path=args.bundle_json,
        run_record_path=args.run_record_json,
        provenance_path=args.provenance_json,
        acceptance_path=args.acceptance_json,
        snapshot_id=args.snapshot_id,
        host_architecture=args.host_architecture,
    )
    print("observability_stage2_pilot_binding=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
