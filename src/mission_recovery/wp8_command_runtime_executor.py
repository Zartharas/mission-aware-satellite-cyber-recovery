from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy
from .wp8_command_effect_contract import (
    AUTHORIZED_COMMAND_CLASS,
    AUTHORIZED_GROUND_SOURCE,
    ATTACKER_COMMAND_CLASS,
    COMMAND_CELL_IDS,
    MATCHED_ATTACKER_PROBE_COUNT,
    MODELED_ATTACKER_SOURCE,
    build_command_cell_effect_contract,
    command_cells,
)
from .wp8_command_observation_contract import (
    derive_command_runtime_observation,
    require_command_observation_acceptance,
)

DECISION_ID = "R-032"
RUNTIME_VALIDATION_DECISION_ID = "R-033"
STATIC_DEVELOPMENT_SEED = 9401
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def _cell_by_id(
    pilot: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    cells = {row["cell_id"]: row for row in command_cells(pilot)}
    if cell_id not in cells:
        raise ValueError(f"not a frozen Stage-1 command cell: {cell_id}")
    return deepcopy(cells[cell_id])


def reserved_pilot_seeds(pilot: dict[str, Any]) -> set[int]:
    values = {int(pilot["stage_1_control_validity"]["seed"])}
    values.update(
        int(value)
        for value in pilot["stage_2_variability"]["additional_seeds"]
    )
    return values


def validate_command_runtime_executor_contract(
    pilot: dict[str, Any],
) -> None:
    runner = pilot["stage_1_runner_contract"]
    contract = runner["command_runtime_executor_contract"]
    dispatch = runner["dispatch_by_event_id"]["E1"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    if contract["decision_id"] != DECISION_ID:
        raise ValueError("command runtime executor contract is not R-032")
    if contract["controller_module"] != (
        "src.mission_recovery.wp8_command_runtime_executor"
    ):
        raise ValueError("unexpected command runtime controller module")
    if contract["development_runner"] != (
        "scripts/run_wp8_command_stage1_development.sh"
    ):
        raise ValueError("unexpected command development runner")
    if contract["supported_cell_ids"] != list(COMMAND_CELL_IDS):
        raise ValueError("command runtime executor cells changed")
    if contract["factor_source"] != "wp8_pilot_design.cells":
        raise ValueError("command runtime factors must come from pilot cells")
    if contract["runtime_policy_selection_source"] != (
        "src.mission_recovery.policies.evaluate_policy"
    ):
        raise ValueError("runtime policy selection source changed")
    if contract["gateway_action_source"] != (
        "runtime_policy_decision.selected_action"
    ):
        raise ValueError("gateway action must come from runtime policy decision")
    if contract["raw_observation_validator"] != (
        "R-029_R-030_R-031_command_contract_chain"
    ):
        raise ValueError("command raw observation validator changed")
    if contract["development_only"] is not True:
        raise ValueError("R-032 executor must remain development-only")
    if contract["pilot_seed_collision_rejected"] is not True:
        raise ValueError("development executor must reject pilot seeds")
    if contract["pilot_executor_ready"] is not False:
        raise ValueError("R-032 cannot declare pilot executor ready")
    if contract["runtime_binding_performed"] is not False:
        raise ValueError("R-032 cannot perform runtime binding")
    if contract["primary_metrics_emitted"] is not False:
        raise ValueError("R-032 cannot emit primary metrics")
    if contract["terminal_state_emitted"] is not False:
        raise ValueError("R-032 cannot emit terminal state")
    if contract["offline_validation_executes_runtime"] is not False:
        raise ValueError("R-032 offline validation cannot execute runtime")
    if contract["offline_validation_consumes_pilot_seed"] is not False:
        raise ValueError("R-032 offline validation cannot consume pilot seed")

    if dispatch.get("development_executor") != contract["development_runner"]:
        raise ValueError("E1 development dispatch does not name R-032 runner")
    if dispatch["pilot_executor_ready"] is not False:
        raise ValueError("E1 pilot executor cannot be ready in R-032")

    if status["stage_1_command_effect_contract"] is not True:
        raise ValueError("R-029 command effect contract regressed")
    if status["stage_1_command_observation_contract"] is not True:
        raise ValueError("R-030 command observation contract regressed")
    if (
        status["stage_1_command_observation_temporal_order_corrected"]
        is not True
    ):
        raise ValueError("R-031 temporal correction regressed")
    if status["stage_1_command_runtime_executor_static"] is not True:
        raise ValueError("R-032 command executor static gate is not closed")
    if status["stage_1_command_runtime_executor_runtime_validated"] is not True:
        raise ValueError("R-033 command executor runtime validation is not closed")

    runtime_validation = contract.get("runtime_validation")
    if not isinstance(runtime_validation, dict):
        raise ValueError("R-033 command runtime validation metadata is missing")
    if runtime_validation["decision_id"] != RUNTIME_VALIDATION_DECISION_ID:
        raise ValueError("command runtime validation decision is not R-033")
    if runtime_validation["validation_status"] != "PASS":
        raise ValueError("command runtime validation status is not PASS")
    if runtime_validation["validation_role"] != (
        "development_mechanism_branch_coverage_not_cellwise_pilot_validation"
    ):
        raise ValueError("command runtime validation role changed")
    if runtime_validation["validated_against_repo_commit"] != (
        "00b82ad290d626e9e32ce32f0cb297141aec363a"
    ):
        raise ValueError("command runtime validation base commit changed")
    if runtime_validation["runtime_rerun_required_for_closure"] is not False:
        raise ValueError("R-033 closure cannot require a hidden runtime rerun")
    if runtime_validation["generic_executor_cells_executed"] != [
        "C01", "C05", "C06"
    ]:
        raise ValueError("R-033 generic executor evidence cells changed")
    if runtime_validation["generic_executor_cells_not_executed"] != [
        "C02", "C03", "C04", "C07"
    ]:
        raise ValueError("R-033 nonexecuted command cell boundary changed")
    if runtime_validation["generic_executor_policy_engine_paths_observed"] != [
        "fixed_policy",
        "mission_aware_p7_evidence_sufficient",
        "mission_aware_p7_evidence_insufficient",
    ]:
        raise ValueError("R-033 policy-engine branch coverage changed")
    if runtime_validation["generic_executor_gateway_actions_observed"] != [
        "OBSERVE_ONLY",
        "RESTRICT_HIGH_RISK_COMMANDS",
        "ENTER_SAFE_MODE",
    ]:
        raise ValueError("R-033 gateway branch coverage changed")

    prior = runtime_validation["prior_reference_gateway_action"]
    if prior["action"] != "ISOLATE_MODELED_SOURCE":
        raise ValueError("R-033 prior P1 gateway reference changed")
    if prior["evidence_ref"] != (
        "results/wp8/runtime-binding/command/"
        "20260816T013055Z-wp8-command-binding-dev"
    ):
        raise ValueError("R-033 prior P1 evidence reference changed")

    retained = runtime_validation["retained_development_runs"]
    if [row["cell_id"] for row in retained] != ["C01", "C05", "C06"]:
        raise ValueError("R-033 retained development run ordering changed")
    if [int(row["development_seed"]) for row in retained] != [9401, 9403, 9402]:
        raise ValueError("R-033 retained development seeds changed")
    if any(row["pilot_data"] is not False for row in retained):
        raise ValueError("R-033 retained development run cannot be pilot data")
    if any(row["pilot_seed_consumed"] is not False for row in retained):
        raise ValueError("R-033 retained development run cannot consume pilot seed")
    if any(row["runtime_binding_performed"] is not False for row in retained):
        raise ValueError("R-033 closure cannot claim runtime binding")
    if any(row["primary_metrics_emitted"] is not False for row in retained):
        raise ValueError("R-033 closure cannot claim primary metrics")
    if any(row["terminal_state_emitted"] is not False for row in retained):
        raise ValueError("R-033 closure cannot claim terminal states")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("family runtime dispatch adapters cannot pass in R-032")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("pilot execution must remain blocked in R-032")


def _validate_development_seed(
    pilot: dict[str, Any],
    development_seed: int,
) -> int:
    seed = int(development_seed)
    if seed <= 0:
        raise ValueError("development seed must be positive")
    if seed in reserved_pilot_seeds(pilot):
        raise ValueError(
            f"development seed collides with frozen pilot seed: {seed}"
        )
    return seed


def _validate_run_id(run_id: str) -> str:
    if not run_id or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError(
            "development run_id must contain only A-Z a-z 0-9 _ . -"
        )
    return run_id


def build_development_execution_plan(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    development_seed: int,
    run_id: str,
) -> dict[str, Any]:
    validate_command_runtime_executor_contract(pilot)

    seed = _validate_development_seed(pilot, development_seed)
    run_id = _validate_run_id(run_id)
    cell = _cell_by_id(pilot, cell_id)

    factor = {
        "run_id": run_id,
        "model_version": pilot["model_version"],
        "seed": seed,
        "mission_state_id": cell["mission_state_id"],
        "event_id": cell["event_id"],
        "policy_id": cell["policy_id"],
        "contact_condition_id": cell["contact_condition_id"],
        "evidence_condition_id": cell["evidence_condition_id"],
    }

    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )

    expected = build_command_cell_effect_contract(pilot, cell_id)
    expected_policy = expected["policy_evaluation"]
    gateway = expected["gateway_execution"]

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": (
            "WP8_COMMAND_RUNTIME_EXECUTOR_DEVELOPMENT_PLAN"
        ),
        "cell_id": cell_id,
        "development_preflight": True,
        "pilot_data": False,
        "pilot_seed_consumed": False,
        "factor_context": factor,
        "event_instance": event,
        "runtime_policy_selection": {
            "must_occur_after_event_activation": True,
            "must_not_wait_for_ground_truth_event_success": True,
            "requested_policy_id": cell["policy_id"],
            "expected_effective_policy_id_for_acceptance_only": (
                expected_policy["actual_effective_policy_id"]
            ),
            "expected_selected_action_for_acceptance_only": (
                expected_policy["selected_action"]
            ),
        },
        "probe_sequence": [
            {
                "ordinal": 1,
                "source_id": MODELED_ATTACKER_SOURCE,
                "command_class": ATTACKER_COMMAND_CLASS,
            },
            {
                "ordinal": 2,
                "source_id": MODELED_ATTACKER_SOURCE,
                "command_class": ATTACKER_COMMAND_CLASS,
            },
            {
                "ordinal": 3,
                "source_id": AUTHORIZED_GROUND_SOURCE,
                "command_class": AUTHORIZED_COMMAND_CLASS,
            },
        ],
        "acceptance_only_expected_effects": {
            "matched_attacker_probe_count": MATCHED_ATTACKER_PROBE_COUNT,
            "attacker_reset_marker_delta": gateway["attacker_probe"][
                "expected_cfs_reset_marker_delta_for_acceptance_only"
            ],
            "authorized_noop_marker_delta": gateway["authorized_probe"][
                "expected_cfs_noop_marker_delta_for_acceptance_only"
            ],
        },
        "runtime_binding_performed": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "pilot_runtime_execution_authorized": False,
    }


def select_runtime_policy(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    event: dict[str, Any],
) -> dict[str, Any]:
    validate_command_runtime_executor_contract(pilot)
    cell = _cell_by_id(pilot, cell_id)

    if event["event_id"] != cell["event_id"]:
        raise ValueError("runtime event_id differs from command cell")
    if event["mission_state"] != cell["mission_state_id"]:
        raise ValueError("runtime mission state differs from command cell")
    if event["contact_condition"] != cell["contact_condition_id"]:
        raise ValueError("runtime contact condition differs from command cell")
    if event["evidence_condition"] != cell["evidence_condition_id"]:
        raise ValueError("runtime evidence condition differs from command cell")

    _validate_development_seed(pilot, int(event["seed"]))

    decision = evaluate_policy(cell["policy_id"], event)

    expected = build_command_cell_effect_contract(pilot, cell_id)
    expected_policy = expected["policy_evaluation"]

    if (
        decision["delegated_policy_id"]
        != expected_policy["actual_effective_policy_id"]
    ):
        raise ValueError(
            "runtime effective policy differs from frozen command semantics"
        )
    if decision["selected_action"] != expected_policy["selected_action"]:
        raise ValueError(
            "runtime selected action differs from frozen command semantics"
        )
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("runtime command policy cannot read ground truth")

    result = deepcopy(decision)
    result["schema"] = 1
    result["decision_id"] = DECISION_ID
    result["cell_id"] = cell_id
    result["runtime_policy_selection"] = True
    result["development_preflight"] = True
    result["pilot_data"] = False
    return result


def _load_gateway_rows(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 3:
        raise ValueError(
            f"command development run requires 3 gateway decisions, got {len(rows)}"
        )
    return rows


def finalize_raw_observation(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    factor: dict[str, Any],
    policy_decision: dict[str, Any],
    gateway_rows: list[dict[str, Any]],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    validate_command_runtime_executor_contract(pilot)
    cell = _cell_by_id(pilot, cell_id)

    if factor["run_id"] != measurement["run_id"]:
        raise ValueError("measurement run_id differs from factor context")
    if factor["event_id"] != "E1":
        raise ValueError("command executor factor event must be E1")
    if factor["policy_id"] != cell["policy_id"]:
        raise ValueError("command executor factor policy differs from cell")
    _validate_development_seed(pilot, int(factor["seed"]))

    expected = build_command_cell_effect_contract(pilot, cell_id)
    gateway = expected["gateway_execution"]

    actual_effective = policy_decision["delegated_policy_id"]
    selected_action = policy_decision["selected_action"]

    if actual_effective != expected["policy_evaluation"][
        "actual_effective_policy_id"
    ]:
        raise ValueError("runtime policy decision effective policy mismatch")
    if selected_action != gateway["action"]:
        raise ValueError("runtime policy decision action mismatch")

    expected_rows = (
        (
            MODELED_ATTACKER_SOURCE,
            ATTACKER_COMMAND_CLASS,
            gateway["attacker_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ],
        ),
        (
            MODELED_ATTACKER_SOURCE,
            ATTACKER_COMMAND_CLASS,
            gateway["attacker_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ],
        ),
        (
            AUTHORIZED_GROUND_SOURCE,
            AUTHORIZED_COMMAND_CLASS,
            gateway["authorized_probe"][
                "expected_gateway_forwarded_for_acceptance_only"
            ],
        ),
    )

    for index, (row, expected_row) in enumerate(
        zip(gateway_rows, expected_rows),
        start=1,
    ):
        expected_source, expected_class, expected_forwarded = expected_row
        if row["action"] != selected_action:
            raise ValueError(
                f"gateway decision {index} action differs from runtime policy"
            )
        if row["source_id"] != expected_source:
            raise ValueError(
                f"gateway decision {index} source differs from probe contract"
            )
        if row["command_class"] != expected_class:
            raise ValueError(
                f"gateway decision {index} command class differs from probe contract"
            )
        if bool(row["forwarded"]) is not bool(expected_forwarded):
            raise ValueError(
                f"gateway decision {index} forwarding differs from frozen semantics"
            )

    counts = measurement["counts"]
    timestamps = measurement["timestamps_ns"]

    raw = {
        "actual_effective_policy_id": actual_effective,
        "selected_action": selected_action,
        "event_activation_reset_marker_delta": (
            int(counts["reset_after_event"])
            - int(counts["reset_before_event"])
        ),
        "post_enforcement_attacker_probe_count": 2,
        "post_enforcement_attacker_reset_marker_delta": (
            int(counts["reset_after_attacker"])
            - int(counts["reset_before_attacker"])
        ),
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": (
            int(counts["noop_after"])
            - int(counts["noop_before"])
        ),
        "event_activation_ns": int(timestamps["event_activation_ns"]),
        "event_success_ns": int(timestamps["event_success_ns"]),
        "policy_enforcement_ns": int(timestamps["policy_enforcement_ns"]),
        "second_attacker_probe_observed_ns": int(
            timestamps["second_attacker_probe_observed_ns"]
        ),
        "authorized_noop_probe_observed_ns": int(
            timestamps["authorized_noop_probe_observed_ns"]
        ),
        "run_end_ns": int(timestamps["run_end_ns"]),
    }

    derived = derive_command_runtime_observation(
        pilot=pilot,
        cell_id=cell_id,
        observation=raw,
    )
    require_command_observation_acceptance(derived)

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": (
            "WP8_COMMAND_RUNTIME_EXECUTOR_DEVELOPMENT_RAW_OBSERVATION_PASS"
        ),
        "cell_id": cell_id,
        "run_id": factor["run_id"],
        "development_preflight": True,
        "pilot_data": False,
        "pilot_seed_consumed": False,
        "factor_context": deepcopy(factor),
        "raw_observation": raw,
        "derived_command_observation": derived,
        "runtime_binding_performed": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
    }


def build_static_development_matrix(
    pilot: dict[str, Any],
    *,
    development_seed: int = STATIC_DEVELOPMENT_SEED,
) -> dict[str, Any]:
    validate_command_runtime_executor_contract(pilot)
    rows = []
    for cell_id in COMMAND_CELL_IDS:
        plan = build_development_execution_plan(
            pilot,
            cell_id=cell_id,
            development_seed=development_seed,
            run_id=f"offline-r032-{cell_id.lower()}-s{development_seed}",
        )
        preview = select_runtime_policy(
            pilot,
            cell_id=cell_id,
            event=plan["event_instance"],
        )
        rows.append(
            {
                "cell_id": cell_id,
                "development_seed": development_seed,
                "requested_policy_id": plan["factor_context"]["policy_id"],
                "actual_effective_policy_id": preview["delegated_policy_id"],
                "selected_action": preview["selected_action"],
                "development_preflight": True,
                "pilot_data": False,
            }
        )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_COMMAND_RUNTIME_EXECUTOR_STATIC_MATRIX",
        "rows": rows,
        "runtime_execution_performed": False,
        "pilot_seed_consumed": False,
        "pilot_data_generated": False,
    }


def _write_json(path: str | Path, value: dict[str, Any]) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--pilot-config", required=True)
    plan.add_argument("--cell-id", required=True, choices=list(COMMAND_CELL_IDS))
    plan.add_argument("--development-seed", required=True, type=int)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--output-plan-json", required=True)
    plan.add_argument("--output-factor-json", required=True)
    plan.add_argument("--output-event-json", required=True)

    select = sub.add_parser("select-policy")
    select.add_argument("--pilot-config", required=True)
    select.add_argument("--cell-id", required=True, choices=list(COMMAND_CELL_IDS))
    select.add_argument("--event-json", required=True)
    select.add_argument("--output-policy-json", required=True)

    finalize = sub.add_parser("finalize-observation")
    finalize.add_argument("--pilot-config", required=True)
    finalize.add_argument("--cell-id", required=True, choices=list(COMMAND_CELL_IDS))
    finalize.add_argument("--factor-json", required=True)
    finalize.add_argument("--policy-json", required=True)
    finalize.add_argument("--gateway-decisions-jsonl", required=True)
    finalize.add_argument("--measurement-json", required=True)
    finalize.add_argument("--output-json", required=True)

    args = parser.parse_args()
    pilot = json.loads(Path(args.pilot_config).read_text(encoding="utf-8"))

    if args.command == "plan":
        value = build_development_execution_plan(
            pilot,
            cell_id=args.cell_id,
            development_seed=args.development_seed,
            run_id=args.run_id,
        )
        _write_json(args.output_plan_json, value)
        _write_json(args.output_factor_json, value["factor_context"])
        _write_json(args.output_event_json, value["event_instance"])
        print("command_development_plan=PASS")
        print("development_preflight=true")
        print("pilot_data=false")
        print("pilot_seed_consumed=false")
        return 0

    if args.command == "select-policy":
        event = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
        value = select_runtime_policy(
            pilot,
            cell_id=args.cell_id,
            event=event,
        )
        _write_json(args.output_policy_json, value)
        print("command_runtime_policy_selection=PASS")
        print("effective_policy_id=" + value["delegated_policy_id"])
        print("selected_action=" + value["selected_action"])
        print("oracle_ground_truth_read=false")
        return 0

    factor = json.loads(Path(args.factor_json).read_text(encoding="utf-8"))
    policy = json.loads(Path(args.policy_json).read_text(encoding="utf-8"))
    measurement = json.loads(
        Path(args.measurement_json).read_text(encoding="utf-8")
    )
    gateway_rows = _load_gateway_rows(Path(args.gateway_decisions_jsonl))

    value = finalize_raw_observation(
        pilot,
        cell_id=args.cell_id,
        factor=factor,
        policy_decision=policy,
        gateway_rows=gateway_rows,
        measurement=measurement,
    )
    _write_json(args.output_json, value)
    print("command_raw_observation_validation=PASS")
    print("development_preflight=true")
    print("pilot_data=false")
    print("pilot_seed_consumed=false")
    print("runtime_binding_performed=false")
    print("primary_metrics_emitted=false")
    print("terminal_state_emitted=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
