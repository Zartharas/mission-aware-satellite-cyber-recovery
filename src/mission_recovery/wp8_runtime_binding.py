from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .primary_metrics import (
    RECOVERY_CRITERIA,
    build_invalid_run_record,
    build_run_record,
)

FAMILIES = {"command", "recovery", "observability"}


def environment_from_toolchain_lock(
    toolchain: dict[str, Any],
    *,
    snapshot_id: str,
    host_architecture: str | None = None,
) -> dict[str, Any]:
    simulator = toolchain["simulator"]
    flight = toolchain["flight_software"]
    host = toolchain["host"]

    return {
        "host_architecture": (
            host_architecture
            if host_architecture is not None
            else host["kernel_architecture"]
        ),
        "simulator": simulator["short_name"],
        "simulator_commit": simulator["commit"],
        "flight_software": flight["name"],
        "flight_software_commit": flight["cfe_commit"],
        "snapshot_id": snapshot_id,
        "container_or_vm_digest": simulator["container_digest"],
    }


def _clock_offsets(clock: dict[str, Any]) -> dict[str, float | None]:
    run_start_ns = int(clock["run_start_ns"])
    event_activation_ns = int(clock["event_activation_ns"])
    run_end_ns = int(clock["run_end_ns"])

    if run_start_ns < 0:
        raise ValueError("run_start_ns must be non-negative")
    if event_activation_ns < run_start_ns:
        raise ValueError("event activation precedes run start")
    if run_end_ns <= event_activation_ns:
        raise ValueError("run end must follow event activation")

    containment_ns = clock.get("containment_ns")
    trusted_recovery_ns = clock.get("trusted_recovery_ns")

    for label, value in (
        ("containment", containment_ns),
        ("trusted_recovery", trusted_recovery_ns),
    ):
        if value is None:
            continue
        value = int(value)
        if value < event_activation_ns or value > run_end_ns:
            raise ValueError(
                f"{label} timestamp before event activation or after run end"
            )

    def offset(value: int | None) -> float | None:
        if value is None:
            return None
        return (int(value) - run_start_ns) / 1_000_000_000.0

    return {
        "event_activation_s": offset(event_activation_ns),
        "containment_s": offset(containment_ns),
        "trusted_recovery_s": offset(trusted_recovery_ns),
        "run_end_s": offset(run_end_ns),
    }


def _observed_timestamp(
    evidence: dict[str, Any],
    *,
    run_start_ns: int,
    event_activation_ns: int,
    run_end_ns: int,
    label: str,
) -> float | None:
    predicate = bool(evidence["predicate"])
    observed_ns = evidence.get("observed_ns")

    if not predicate:
        if observed_ns is not None:
            raise ValueError(f"{label} false predicate has observed_ns")
        return None

    if observed_ns is None:
        raise ValueError(f"{label} true predicate lacks observed_ns")

    observed_ns = int(observed_ns)
    if observed_ns < event_activation_ns or observed_ns > run_end_ns:
        raise ValueError(
            f"{label} observation before event activation or after run end"
        )

    return (observed_ns - run_start_ns) / 1_000_000_000.0


def _objective_instances(
    *,
    family: str,
    contract: dict[str, Any],
    objective_results: dict[str, Any],
    event_activation_s: float,
    run_end_s: float,
) -> list[dict[str, Any]]:
    declarations = contract["family_objectives"][family]
    expected_ids = [row["objective_id"] for row in declarations]

    if set(objective_results) != set(expected_ids):
        raise ValueError(
            "objective results do not exactly match the frozen family schedule"
        )

    unit_weight = float(
        contract["primary_objective_weighting"]["unit_weight"]
    )
    if unit_weight != 1.0:
        raise ValueError("WP8 primary objective weight is not frozen at 1.0")

    rows: list[dict[str, Any]] = []
    for declaration in declarations:
        objective_id = declaration["objective_id"]
        result = objective_results[objective_id]
        evidence_ref = result["evidence_ref"]
        if not evidence_ref:
            raise ValueError("objective completion requires evidence_ref")

        rows.append(
            {
                "objective_instance_id": (
                    f"{family}-{objective_id}-response-interval"
                ),
                "weight": unit_weight,
                "scheduled_start_s": event_activation_s,
                "scheduled_end_s": run_end_s,
                "completion_predicate": declaration[
                    "completion_predicate"
                ],
                "completion_evidence_ref": evidence_ref,
                "completed": bool(result["completed"]),
            }
        )

    return rows


def _invariant_intervals(
    rows: list[dict[str, Any]],
    *,
    run_start_ns: int,
    event_activation_ns: int,
    run_end_ns: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for row in rows:
        start_ns = int(row["start_ns"])
        end_ns = row.get("end_ns")

        if start_ns < event_activation_ns or start_ns > run_end_ns:
            raise ValueError(
                "invariant violation starts outside post-activation run"
            )

        if end_ns is not None:
            end_ns = int(end_ns)
            if end_ns < start_ns or end_ns > run_end_ns:
                raise ValueError("invariant violation end outside run")

        result.append(
            {
                "invariant_id": row["invariant_id"],
                "start_s": (
                    start_ns - run_start_ns
                ) / 1_000_000_000.0,
                "end_s": (
                    None
                    if end_ns is None
                    else (end_ns - run_start_ns) / 1_000_000_000.0
                ),
                "ground_truth_evidence_ref": row[
                    "ground_truth_evidence_ref"
                ],
            }
        )

    return result


def _divergence_intervals(
    rows: list[dict[str, Any]],
    *,
    run_start_ns: int,
    event_activation_ns: int,
    run_end_ns: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for row in rows:
        start_ns = int(row["start_ns"])
        end_ns = int(row["end_ns"])

        if start_ns < event_activation_ns:
            raise ValueError(
                "divergence interval starts before event activation"
            )
        if end_ns < start_ns or end_ns > run_end_ns:
            raise ValueError("divergence interval outside run")

        result.append(
            {
                "state_key": row["state_key"],
                "start_s": (
                    start_ns - run_start_ns
                ) / 1_000_000_000.0,
                "end_s": (
                    end_ns - run_start_ns
                ) / 1_000_000_000.0,
            }
        )

    return result


def _recovery_partition(
    observation: dict[str, Any],
    *,
    family: str,
    contract: dict[str, Any],
    development_preflight: bool,
    pilot_data_marker: bool | None,
) -> tuple[dict[str, bool | None], list[dict[str, Any]], list[str], bool]:
    applicable = observation["recovery_observations"]
    excluded = list(observation["recovery_checklist_excluded"])

    declared = contract["family_recovery_criteria_applicability"][family]
    if set(applicable) != set(declared["applicable"]):
        raise ValueError(
            "runtime recovery applicability differs from frozen family rule"
        )
    if set(excluded) != set(declared["excluded"]):
        raise ValueError(
            "runtime recovery exclusions differ from frozen family rule"
        )

    if set(applicable) & set(excluded):
        raise ValueError(
            "recovery criterion cannot be both applicable and excluded"
        )
    if set(applicable) | set(excluded) != set(RECOVERY_CRITERIA):
        raise ValueError(
            "runtime recovery applicability must partition all criteria"
        )

    recovery_evidence: dict[str, bool | None] = {}
    checklist: list[dict[str, Any]] = []
    legacy_fallback_used = False

    for criterion in RECOVERY_CRITERIA:
        if criterion in excluded:
            recovery_evidence[criterion] = None
            continue

        row = applicable[criterion]
        evidence_ref = row["evidence_ref"]
        if not evidence_ref:
            raise ValueError(
                f"recovery criterion lacks evidence_ref: {criterion}"
            )

        available_current = bool(row["available_current"])
        if "criterion_satisfied" in row:
            criterion_satisfied = bool(row["criterion_satisfied"])
        else:
            if not development_preflight or pilot_data_marker is True:
                raise ValueError(
                    "pilot/runtime recovery observation requires explicit "
                    f"criterion_satisfied: {criterion}"
                )
            criterion_satisfied = available_current
            legacy_fallback_used = True

        if criterion_satisfied and not available_current:
            raise ValueError(
                "criterion_satisfied=true requires "
                f"available_current=true: {criterion}"
            )

        recovery_evidence[criterion] = criterion_satisfied
        checklist.append(
            {
                "criterion_id": criterion,
                "available_current": available_current,
                "criterion_satisfied": criterion_satisfied,
                "evidence_ref": evidence_ref,
            }
        )

    if not checklist:
        raise ValueError("runtime recovery checklist denominator is zero")

    return recovery_evidence, checklist, excluded, legacy_fallback_used


def bind_runtime_observation(
    *,
    contract: dict[str, Any],
    factor_context: dict[str, Any],
    environment: dict[str, Any],
    observation: dict[str, Any],
    notes: str | None = None,
) -> dict[str, Any]:
    family = observation["family"]
    if family not in FAMILIES:
        raise ValueError(f"unsupported WP8 runtime family: {family}")

    if contract["decision_id"] != "R-015":
        raise ValueError("runtime measurement contract is not R-015")

    if contract["controller_clock"] != "experiment_controller_monotonic_ns":
        raise ValueError("unexpected WP8 controller clock")

    development_preflight = bool(observation.get("development_preflight", False))
    pilot_data_marker = observation.get("pilot_data")
    if pilot_data_marker is not None and not isinstance(pilot_data_marker, bool):
        raise ValueError("pilot_data marker must be boolean when supplied")
    if development_preflight and pilot_data_marker is True:
        raise ValueError(
            "development runtime-binding preflight cannot be pilot data"
        )

    clock = observation["clock"]
    run_start_ns = int(clock["run_start_ns"])
    event_activation_ns = int(clock["event_activation_ns"])
    run_end_ns = int(clock["run_end_ns"])
    offsets = _clock_offsets(clock)

    event_success_timestamp_s = _observed_timestamp(
        observation["event_success"],
        run_start_ns=run_start_ns,
        event_activation_ns=event_activation_ns,
        run_end_ns=run_end_ns,
        label="event_success",
    )

    (
        recovery_evidence,
        checklist,
        excluded,
        legacy_recovery_semantics_fallback_used,
    ) = _recovery_partition(
        observation,
        family=family,
        contract=contract,
        development_preflight=development_preflight,
        pilot_data_marker=pilot_data_marker,
    )

    objectives = _objective_instances(
        family=family,
        contract=contract,
        objective_results=observation["objective_results"],
        event_activation_s=float(offsets["event_activation_s"]),
        run_end_s=float(offsets["run_end_s"]),
    )

    invariant_intervals = _invariant_intervals(
        observation["invariant_violation_intervals"],
        run_start_ns=run_start_ns,
        event_activation_ns=event_activation_ns,
        run_end_ns=run_end_ns,
    )

    divergence_intervals = _divergence_intervals(
        observation["ground_spacecraft_divergence_intervals"],
        run_start_ns=run_start_ns,
        event_activation_ns=event_activation_ns,
        run_end_ns=run_end_ns,
    )

    containment_timestamp_s = offsets["containment_s"]
    trusted_recovery_timestamp_s = offsets["trusted_recovery_s"]

    raw = {
        "event_success": {
            "predicate": bool(observation["event_success"]["predicate"]),
            "timestamp_s": event_success_timestamp_s,
        },
        "containment": {
            "predicate": containment_timestamp_s is not None,
            "timestamp_s": containment_timestamp_s,
        },
        "trusted_recovery": {
            "predicate": trusted_recovery_timestamp_s is not None,
            "timestamp_s": trusted_recovery_timestamp_s,
        },
        "objective_instances": objectives,
        "invariant_violation_intervals": invariant_intervals,
        "legitimate_commands": {
            "attempted": int(
                observation["legitimate_commands"]["attempted"]
            ),
            "rejected": int(
                observation["legitimate_commands"]["rejected"]
            ),
        },
        "ground_spacecraft_divergence_intervals": divergence_intervals,
        "recovery_checklist": checklist,
        "recovery_checklist_excluded": excluded,
        "run_end_s": float(offsets["run_end_s"]),
        "terminal_state_predicates": deepcopy(
            observation["terminal_state_predicates"]
        ),
    }

    record = build_run_record(
        run_id=factor_context["run_id"],
        model_version=factor_context["model_version"],
        seed=int(factor_context["seed"]),
        mission_state_id=factor_context["mission_state_id"],
        event_id=factor_context["event_id"],
        policy_id=factor_context["policy_id"],
        contact_condition_id=factor_context["contact_condition_id"],
        evidence_condition_id=factor_context["evidence_condition_id"],
        environment=environment,
        run_start_utc=clock["run_start_utc"],
        event_activation_s=float(offsets["event_activation_s"]),
        run_end_utc=clock["run_end_utc"],
        raw_metric_evidence=raw,
        recovery_evidence=recovery_evidence,
        notes=notes,
    )

    provenance = {
        "binding_version": "0.1.0",
        "decision_id": "R-015",
        "recovery_evidence_semantics_decision_id": "R-035",
        "legacy_recovery_semantics_fallback_used": (
            legacy_recovery_semantics_fallback_used
        ),
        "family": family,
        "run_id": factor_context["run_id"],
        "controller_clock": contract["controller_clock"],
        "event_success_evidence_ref": observation[
            "event_success"
        ]["evidence_ref"],
        "containment_evidence_ref": observation.get(
            "containment_evidence_ref"
        ),
        "trusted_recovery_evidence_ref": observation.get(
            "trusted_recovery_evidence_ref"
        ),
        "legitimate_command_evidence_ref": observation[
            "legitimate_commands"
        ]["evidence_ref"],
        "terminal_state_evidence_refs": list(
            observation["terminal_state_evidence_refs"]
        ),
        "source_observation_refs": list(
            observation["source_observation_refs"]
        ),
        "development_preflight": development_preflight,
        "pilot_data": (
            False if development_preflight else pilot_data_marker
        ),
    }

    if provenance["development_preflight"] is True:
        if provenance["pilot_data"] is not False:
            raise ValueError(
                "development runtime-binding preflight cannot be pilot data"
            )

    return {
        "run_record": record,
        "binding_provenance": provenance,
    }


def bind_invalid_runtime_observation(
    *,
    factor_context: dict[str, Any],
    environment: dict[str, Any],
    invalid_run_reason: str,
    source_observation_refs: list[str],
    notes: str | None = None,
) -> dict[str, Any]:
    record = build_invalid_run_record(
        run_id=factor_context["run_id"],
        model_version=factor_context["model_version"],
        seed=int(factor_context["seed"]),
        mission_state_id=factor_context["mission_state_id"],
        event_id=factor_context["event_id"],
        policy_id=factor_context["policy_id"],
        contact_condition_id=factor_context["contact_condition_id"],
        evidence_condition_id=factor_context["evidence_condition_id"],
        environment=environment,
        invalid_run_reason=invalid_run_reason,
        notes=notes,
    )

    return {
        "run_record": record,
        "binding_provenance": {
            "binding_version": "0.1.0",
            "decision_id": "R-015",
            "run_id": factor_context["run_id"],
            "invalid_run_reason": invalid_run_reason,
            "source_observation_refs": list(source_observation_refs),
            "fabricated_primary_metrics": False,
            "pilot_data": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observation-json", required=True)
    parser.add_argument("--pilot-config", required=True)
    parser.add_argument("--toolchain-lock", required=True)
    parser.add_argument("--output-run-json", required=True)
    parser.add_argument("--output-provenance-json", required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--host-architecture")
    args = parser.parse_args()

    observation = json.loads(
        Path(args.observation_json).read_text(encoding="utf-8")
    )
    pilot = json.loads(
        Path(args.pilot_config).read_text(encoding="utf-8")
    )
    toolchain = json.loads(
        Path(args.toolchain_lock).read_text(encoding="utf-8")
    )

    environment = environment_from_toolchain_lock(
        toolchain,
        snapshot_id=args.snapshot_id,
        host_architecture=args.host_architecture,
    )

    result = bind_runtime_observation(
        contract=pilot["runtime_measurement_contract"],
        factor_context=observation["factor_context"],
        environment=environment,
        observation=observation["runtime_observation"],
        notes=observation.get("notes"),
    )

    Path(args.output_run_json).write_text(
        json.dumps(result["run_record"], sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    Path(args.output_provenance_json).write_text(
        json.dumps(
            result["binding_provenance"],
            sort_keys=True,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("WP8_RUNTIME_BINDING_STATUS=PASS")
    print(
        "terminal_state="
        + result["run_record"]["terminal_state"]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
