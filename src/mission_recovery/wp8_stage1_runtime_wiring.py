from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy
from .rollback_requests import build_verified_rollback_request
from .trusted_recovery import validate_rollback_request, verify_replacement_source
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)
from .wp8_command_observation_contract import (
    derive_command_runtime_observation,
    require_command_observation_acceptance,
)
from .wp8_recovery_observation_contract import (
    derive_recovery_runtime_observation,
    require_recovery_observation_acceptance,
)
from .wp8_stage1_family_dispatch import (
    PILOT_RUNTIME_PATH_BY_CELL,
    bind_authorized_family_observation,
)

DECISION_ID = "R-040"
RUN_ID_PATTERN = re.compile(
    r"^\d{8}T\d{6}\.\d{6}Z-wp8-stage1-"
    r"(?P<cell>[a-z0-9]+)-s101-(?P<token>[0-9a-f]{32})$"
)
COMMAND_CELLS = tuple(f"C{i:02d}" for i in range(1, 8))
RECOVERY_GENERIC_CELLS = ("R01", "R04")
RECOVERY_FULL_CELLS = ("R02", "R03")


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: str | Path, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _cell(pilot: dict[str, Any], cell_id: str) -> dict[str, Any]:
    cells = {row["cell_id"]: row for row in pilot["cells"]}
    if cell_id not in cells:
        raise ValueError(f"unknown Stage-1 cell: {cell_id}")
    return deepcopy(cells[cell_id])


def _factor(
    pilot: dict[str, Any], *, cell_id: str, run_id: str
) -> dict[str, Any]:
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if match is None:
        raise ValueError(
            "pilot run_id is not controller-allocated Stage-1 identity"
        )
    if match.group("cell") != cell_id.lower():
        raise ValueError(
            "pilot run_id cell differs from requested Stage-1 cell"
        )
    cell = _cell(pilot, cell_id)
    seed = int(pilot["stage_1_control_validity"]["seed"])
    if seed != 101:
        raise ValueError("Stage-1 pilot seed is not frozen at 101")
    return {
        "run_id": run_id,
        "model_version": pilot["model_version"],
        "seed": seed,
        "mission_state_id": cell["mission_state_id"],
        "event_id": cell["event_id"],
        "policy_id": cell["policy_id"],
        "contact_condition_id": cell["contact_condition_id"],
        "evidence_condition_id": cell["evidence_condition_id"],
    }


def _semantic_contract_view(pilot: dict[str, Any]) -> dict[str, Any]:
    view = deepcopy(pilot)
    gate = view["instrumentation_gate"]
    gate["pilot_execution_authorized"] = False
    gate["component_status"]["stage_1_family_runtime_dispatch_adapters"] = False
    for row in view["stage_1_runner_contract"]["dispatch_by_event_id"].values():
        row["pilot_executor_ready"] = False
    return view


def validate_runtime_wiring_contract(pilot: dict[str, Any]) -> None:
    dispatch = pilot["stage_1_runner_contract"][
        "family_runtime_dispatch_adapter_contract"
    ]
    r039 = dispatch["pilot_mode_contract"]
    r040 = dispatch["runtime_wiring_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    if pilot["status"] != (
        "STAGE1_RUNTIME_WIRING_STATIC_VALIDATED_AUTHORIZATION_PENDING"
    ):
        raise ValueError("R-040 lifecycle status changed")
    if dispatch["decision_id"] != "R-038":
        raise ValueError("R-040 requires R-038")
    if dispatch["pilot_mode_materialization_complete"] is not True:
        raise ValueError("R-040 requires R-039 materialization")
    if r039["decision_id"] != "R-039" or r039["runtime_wiring_complete"] is not True:
        raise ValueError("R-040 requires completed R-039 wiring declaration")
    if r040["decision_id"] != DECISION_ID:
        raise ValueError("runtime wiring decision is not R-040")
    if r040["controller"] != "scripts/run_wp8_stage1_pilot.sh":
        raise ValueError("Stage-1 pilot controller changed")
    if r040["adapter_module"] != "src.mission_recovery.wp8_stage1_runtime_wiring":
        raise ValueError("Stage-1 pilot adapter module changed")
    if r040["binding_entrypoint"] != (
        "src.mission_recovery.wp8_stage1_family_dispatch."
        "bind_authorized_family_observation"
    ):
        raise ValueError("Stage-1 binding entrypoint changed")
    if r040["ledger_module"] != "src.mission_recovery.wp8_stage1_pilot":
        raise ValueError("Stage-1 ledger module changed")
    if r040["runtime_path_by_cell"] != PILOT_RUNTIME_PATH_BY_CELL:
        raise ValueError("R-040 runtime path mapping changed")
    if r040["single_cell_per_controller_invocation"] is not True:
        raise ValueError("R-040 controller must execute one cell per call")
    if r040["frozen_order_enforced"] is not True:
        raise ValueError("R-040 must enforce frozen Stage-1 order")
    if r040["invalid_attempt_retention_enabled"] is not True:
        raise ValueError("R-040 invalid-attempt retention changed")
    if r040["expected_values_used_as_metric_inputs"] is not False:
        raise ValueError("R-040 cannot use expected values as metric inputs")
    if r040["runtime_execution_performed"] is not False:
        raise ValueError("R-040 static wiring cannot execute runtime")
    if r040["pilot_seed_consumed"] is not False:
        raise ValueError("R-040 static wiring cannot consume seed 101")
    if r040["pilot_data_generated"] is not False:
        raise ValueError("R-040 static wiring cannot generate pilot data")
    if r040["authorization_pending"] is not True:
        raise ValueError("R-040 must remain authorization-pending")
    if r040["pilot_mode_requires_explicit_environment_gate"] != (
        "WP8_STAGE1_PILOT=1 AND WP8_STAGE1_CONTROLLER=1"
    ):
        raise ValueError("R-040 controller-dispatch gate changed")

    expected_sources = {
        "command_generic": "scripts/run_wp8_command_stage1_development.sh",
        "recovery_generic": "scripts/run_wp8_recovery_stage1_development.sh",
        "recovery_full_trusted": "scripts/run_wp8_recovery_binding_preflight.sh",
        "observability_generic": "scripts/run_wp8_observability_stage1_development.sh",
    }
    if r040["pilot_runtime_source_by_path"] != expected_sources:
        raise ValueError("R-040 pilot runtime sources changed")
    for path_name, source in r039["runtime_path_sources"].items():
        if source["pilot_runtime_wiring_complete"] is not True:
            raise ValueError(f"R-040 runtime path is not wired: {path_name}")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("R-040 cannot activate dispatch before CI closure")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("R-040 cannot authorize pilot before CI closure")
    for row in pilot["stage_1_runner_contract"]["dispatch_by_event_id"].values():
        if row["pilot_executor_ready"] is not False:
            raise ValueError("R-040 cannot activate family readiness before CI")


def require_active_pilot(
    pilot: dict[str, Any], *, cell_id: str | None = None
) -> None:
    dispatch = pilot["stage_1_runner_contract"][
        "family_runtime_dispatch_adapter_contract"
    ]
    r039 = dispatch["pilot_mode_contract"]
    r040 = dispatch["runtime_wiring_contract"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]
    if r039["runtime_wiring_complete"] is not True:
        raise PermissionError("Stage-1 pilot runtime wiring is incomplete")
    if r040["decision_id"] != DECISION_ID:
        raise PermissionError("Stage-1 runtime wiring is not R-040")
    if status["stage_1_family_runtime_dispatch_adapters"] is not True:
        raise PermissionError("Stage-1 family runtime dispatch is not activated")
    if gate["pilot_execution_authorized"] is not True:
        raise PermissionError("Stage-1 pilot execution is not authorized")
    for event in ("E1", "E3", "E4"):
        if pilot["stage_1_runner_contract"]["dispatch_by_event_id"][event][
            "pilot_executor_ready"
        ] is not True:
            raise PermissionError(f"Stage-1 pilot executor is not ready: {event}")
    if cell_id is not None and cell_id not in PILOT_RUNTIME_PATH_BY_CELL:
        raise ValueError(f"unknown Stage-1 cell: {cell_id}")


def _select_policy(
    pilot: dict[str, Any], *, cell_id: str, event: dict[str, Any]
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
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
                f"runtime event {event_key} differs from frozen cell"
            )
    if int(event["seed"]) != 101:
        raise ValueError("pilot runtime event seed is not 101")
    decision = evaluate_policy(cell["policy_id"], event)
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("pilot policy selection cannot read ground truth")
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
    pilot: dict[str, Any], *, cell_id: str, seed: int, run_id: str
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
    if cell_id not in COMMAND_CELLS or int(seed) != 101:
        raise ValueError("invalid command pilot cell/seed")
    factor = _factor(pilot, cell_id=cell_id, run_id=run_id)
    cell = _cell(pilot, cell_id)
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=101,
    )
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_STAGE1_COMMAND_PILOT_PLAN",
        "factor_context": factor,
        "event_instance": event,
        "runtime_path": "command_generic",
        "development_preflight": False,
        "pilot_data": True,
    }


def recovery_plan(
    pilot: dict[str, Any], *, cell_id: str, seed: int, run_id: str
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
    if cell_id not in RECOVERY_GENERIC_CELLS or int(seed) != 101:
        raise ValueError("invalid generic recovery pilot cell/seed")
    factor = _factor(pilot, cell_id=cell_id, run_id=run_id)
    cell = _cell(pilot, cell_id)
    event = materialize_event(
        "E3",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=101,
    )
    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_STAGE1_RECOVERY_GENERIC_PILOT_PLAN",
        "factor_context": factor,
        "event_instance": event,
        "artifacts": {
            "approved_bytes": approved,
            "tampered_bytes": tampered,
            "manifest": manifest,
            "tampered_verification": verify_candidate(tampered, manifest),
        },
        "development_preflight": False,
        "pilot_data": True,
    }


def prepare_verified_rollback_pilot(
    *, event: dict[str, Any], policy_decision: dict[str, Any]
) -> dict[str, Any]:
    manifest = build_manifest()
    approved = build_approved_update()
    tampered = build_tampered_update()
    verification = verify_candidate(tampered, manifest)
    request = build_verified_rollback_request(
        event_instance=event,
        policy_decision=policy_decision,
        manifest=manifest,
        candidate_verification=verification,
    )
    validation = validate_rollback_request(
        request=request,
        policy_decision=policy_decision,
        manifest=manifest,
        pre_recovery_candidate_sha256=verification["actual_sha256"],
    )
    source = verify_replacement_source(approved, manifest)
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "rollback_request": request,
        "rollback_request_validation": validation,
        "rollback_request_validated": validation["accepted"] is True and validation["reasons"] == [],
        "replacement_source_verification": source,
        "replacement_source_verified": source["accepted"] is True and source["reasons"] == [],
        "development_preflight": False,
        "pilot_data": True,
    }



def _command_raw(
    *, factor: dict[str, Any], policy: dict[str, Any], measurement: dict[str, Any]
) -> dict[str, Any]:
    if factor["run_id"] != measurement["run_id"]:
        raise ValueError("command measurement run_id mismatch")
    counts = measurement["counts"]
    ts = measurement["timestamps_ns"]
    return {
        "actual_effective_policy_id": policy["delegated_policy_id"],
        "selected_action": policy["selected_action"],
        "event_activation_reset_marker_delta": int(counts["reset_after_event"]) - int(counts["reset_before_event"]),
        "post_enforcement_attacker_probe_count": 2,
        "post_enforcement_attacker_reset_marker_delta": int(counts["reset_after_attacker"]) - int(counts["reset_before_attacker"]),
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": int(counts["noop_after"]) - int(counts["noop_before"]),
        "event_activation_ns": int(ts["event_activation_ns"]),
        "event_success_ns": int(ts["event_success_ns"]),
        "policy_enforcement_ns": int(ts["policy_enforcement_ns"]),
        "second_attacker_probe_observed_ns": int(ts["second_attacker_probe_observed_ns"]),
        "authorized_noop_probe_observed_ns": int(ts["authorized_noop_probe_observed_ns"]),
        "run_end_ns": int(ts["run_end_ns"]),
    }


def command_finalize(
    pilot: dict[str, Any], *, cell_id: str, factor: dict[str, Any],
    policy: dict[str, Any], gateway_rows: list[dict[str, Any]],
    measurement: dict[str, Any]
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
    if len(gateway_rows) != 3:
        raise ValueError("command pilot requires exactly three gateway decisions")
    raw = _command_raw(factor=factor, policy=policy, measurement=measurement)
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


def _runtime_health(*, nominal_log: Path, runtime_manifest: Path) -> bool:
    if not nominal_log.is_file() or not runtime_manifest.is_file():
        return False
    return "NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS" in nominal_log.read_text(
        encoding="utf-8", errors="replace"
    )


def command_bundle(
    *, pilot: dict[str, Any], factor: dict[str, Any], policy: dict[str, Any],
    finalized: dict[str, Any], gateway_rows: list[dict[str, Any]],
    evidence_prefix: str, nominal_log: Path, runtime_manifest: Path,
    classification_path: Path, run_start_ns: int, run_start_utc: str,
    run_end_utc: str
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=finalized["cell_id"])
    derived = finalized["derived_command_observation"]
    raw = finalized["raw_observation"]
    containment = bool(derived["containment"]["predicate"])
    authority = bool(derived["authority_convergence"]["predicate"])
    path_ok = bool(derived["objective_results"]["MO-3"]["completed"])
    health_ok = _runtime_health(nominal_log=nominal_log, runtime_manifest=runtime_manifest)
    authorized_rows = [
        row for row in gateway_rows
        if row.get("source_id") == "authorized_ground"
        and row.get("command_class") == "sample_noop"
    ]
    authorization_ok = policy.get("oracle_ground_truth_read") is False and len(authorized_rows) == 1
    classification = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "family": "command",
        "health_checks_passed": health_ok,
        "recovery_manifest_complete": False,
        "development_preflight": False,
        "pilot_data": True,
    }
    _write(classification_path, classification)
    derived_ref = f"{evidence_prefix}/immutable-ground/command-runtime-observation-derived.json"
    gateway_ref = f"{evidence_prefix}/immutable-ground/gateway-decisions.jsonl"
    class_ref = f"{evidence_prefix}/immutable-ground/pilot-classification-evidence.json"
    runtime_ref = f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt"
    interval = derived["ground_spacecraft_divergence_interval"]
    divergence = [] if interval is None else [{
        "state_key": interval["state_key"],
        "start_ns": interval["start_ns"],
        "end_ns": interval["end_ns"],
    }]
    operational = containment and path_ok and authority and health_ok and authorization_ok
    return {
        "factor_context": deepcopy(factor),
        "execution_metadata": {
            "effective_policy_id": policy["delegated_policy_id"],
            "selected_action": policy["selected_action"],
            "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
        },
        "runtime_observation": {
            "family": "command",
            "clock": {
                "run_start_utc": run_start_utc,
                "run_end_utc": run_end_utc,
                "run_start_ns": int(run_start_ns),
                "event_activation_ns": raw["event_activation_ns"],
                "containment_ns": derived["containment"]["observed_ns"],
                "trusted_recovery_ns": None,
                "run_end_ns": raw["run_end_ns"],
            },
            "event_success": {
                "predicate": derived["event_success"]["predicate"],
                "observed_ns": derived["event_success"]["observed_ns"],
                "evidence_ref": derived_ref,
            },
            "objective_results": {
                key: {"completed": row["completed"], "evidence_ref": derived_ref}
                for key, row in derived["objective_results"].items()
            },
            "invariant_violation_intervals": [],
            "legitimate_commands": {
                "attempted": derived["legitimate_commands"]["attempted"],
                "rejected": derived["legitimate_commands"]["rejected"],
                "evidence_ref": gateway_ref,
            },
            "ground_spacecraft_divergence_intervals": divergence,
            "recovery_observations": {
                "authorization_valid": {"available_current": True, "criterion_satisfied": authorization_ok, "evidence_ref": gateway_ref},
                "authorized_command_path_restored": {"available_current": True, "criterion_satisfied": path_ok, "evidence_ref": derived_ref},
                "ground_spacecraft_state_agreed": {"available_current": True, "criterion_satisfied": authority, "evidence_ref": derived_ref},
                "health_checks_passed": {"available_current": True, "criterion_satisfied": health_ok, "evidence_ref": runtime_ref},
                "recovery_manifest_complete": {"available_current": True, "criterion_satisfied": False, "evidence_ref": class_ref},
            },
            "recovery_checklist_excluded": [
                "approved_version", "integrity_measurement_valid",
                "measured_state_current", "required_telemetry_restored",
                "no_residual_unauthorized_state",
            ],
            "terminal_state_predicates": {
                "run_invalid": False,
                "mission_loss": False,
                "trusted_recovery_confirmed": False,
                "operational_restored": operational,
                "recovery_failed": not containment,
                "contained": containment,
            },
            "containment_evidence_ref": derived_ref,
            "trusted_recovery_evidence_ref": None,
            "terminal_state_evidence_refs": [derived_ref, class_ref, runtime_ref],
            "source_observation_refs": [
                f"{evidence_prefix}/immutable-ground/factor-context.json",
                f"{evidence_prefix}/immutable-ground/event-instance.json",
                f"{evidence_prefix}/immutable-ground/runtime-policy-decision.json",
                gateway_ref, derived_ref, class_ref, runtime_ref,
            ],
            "development_preflight": False,
            "pilot_data": True,
        },
        "notes": "WP8 Stage-1 command pilot; controlled NOS3 SAMPLE-state surrogate only.",
    }


def recovery_generic_raw(
    *, policy: dict[str, Any], measurement: dict[str, Any], evidence_prefix: str
) -> dict[str, Any]:
    approved_sha = sha256_hex(build_approved_update())
    tampered_sha = sha256_hex(build_tampered_update())
    containment = (
        measurement["post_response_slot_sha256"] == approved_sha
        and measurement["rejected_sha256_absent"] is True
        and measurement["temporary_recovery_state_absent"] is True
    )
    slot_ns = int(measurement["post_response_slot_observed_ns"])
    noop_ns = int(measurement["authorized_noop_probe_observed_ns"])
    cls_ns = int(measurement["criteria_classification_ns"])
    noop_delta = int(measurement["authorized_noop_marker_delta"])
    def criterion(available: bool, satisfied: bool, ref: str, observed_ns: int) -> dict[str, Any]:
        return {
            "available_current": bool(available),
            "criterion_satisfied": bool(satisfied),
            "evidence_ref": f"{evidence_prefix}/{ref}",
            "observed_ns": int(observed_ns),
        }
    scope_ref = "immutable-ground/pilot-evidence-scope.json"
    slot_ref = "immutable-ground/post-response-slot.json"
    criteria = {
        "approved_version": criterion(True, containment, slot_ref, slot_ns),
        "integrity_measurement_valid": criterion(True, containment, slot_ref, slot_ns),
        "authorization_valid": criterion(False, False, scope_ref, cls_ns),
        "measured_state_current": criterion(True, containment, slot_ref, slot_ns),
        "authorized_command_path_restored": criterion(True, noop_delta == 1, "immutable-ground/authorized-noop-probe.json", noop_ns),
        "ground_spacecraft_state_agreed": criterion(True, containment, slot_ref, slot_ns),
        "required_telemetry_restored": criterion(False, False, scope_ref, cls_ns),
        "health_checks_passed": criterion(False, False, scope_ref, cls_ns),
        "no_residual_unauthorized_state": criterion(True, containment, slot_ref, slot_ns),
        "recovery_manifest_complete": criterion(False, False, scope_ref, cls_ns),
    }
    raw = {
        "actual_effective_policy_id": policy["delegated_policy_id"],
        "selected_action": policy["selected_action"],
        "event_slot_sha256": measurement["event_slot_sha256"],
        "post_response_slot_sha256": measurement["post_response_slot_sha256"],
        "rejected_sha256_absent": measurement["rejected_sha256_absent"],
        "temporary_recovery_state_absent": measurement["temporary_recovery_state_absent"],
        "rollback_request_emitted": measurement["rollback_request_emitted"],
        "rollback_request_validated": measurement["rollback_request_validated"],
        "replacement_source_verified": measurement["replacement_source_verified"],
        "event_activation_ns": int(measurement["event_activation_ns"]),
        "event_success_ns": int(measurement["event_success_ns"]),
        "policy_selection_ns": int(measurement["policy_selection_ns"]),
        "policy_enforcement_ns": int(measurement["policy_enforcement_ns"]),
        "post_response_slot_observed_ns": slot_ns,
        "authorized_noop_probe_observed_ns": noop_ns,
        "criteria_classification_ns": cls_ns,
        "run_end_ns": int(measurement["run_end_ns"]),
        "authorized_noop_attempt_count": 1,
        "authorized_noop_marker_delta": noop_delta,
        "recovery_criteria": criteria,
    }
    if "matched_attacker_probe_count" in measurement:
        raw["command_gateway_observation"] = {
            "matched_attacker_probe_count": int(measurement["matched_attacker_probe_count"]),
            "attacker_reset_marker_delta": int(measurement["attacker_reset_marker_delta"]),
            "authorized_noop_attempt_count": 1,
            "authorized_noop_marker_delta": noop_delta,
        }
        raw["command_gateway_probe_observed_ns"] = int(measurement["command_gateway_probe_observed_ns"])
    if measurement["event_slot_sha256"] != tampered_sha:
        raise ValueError("E3 event slot does not retain tampered SHA")
    return raw


def recovery_generic_finalize(
    pilot: dict[str, Any], *, cell_id: str, factor: dict[str, Any],
    policy: dict[str, Any], measurement: dict[str, Any], evidence_prefix: str
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
    if cell_id not in RECOVERY_GENERIC_CELLS:
        raise ValueError("generic recovery pilot supports R01/R04 only")
    raw = recovery_generic_raw(policy=policy, measurement=measurement, evidence_prefix=evidence_prefix)
    derived = derive_recovery_runtime_observation(
        pilot=_semantic_contract_view(pilot), cell_id=cell_id, observation=raw
    )
    require_recovery_observation_acceptance(derived)
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "run_id": factor["run_id"],
        "factor_context": deepcopy(factor),
        "raw_observation": raw,
        "derived_recovery_observation": derived,
        "development_preflight": False,
        "pilot_data": True,
    }


def recovery_generic_bundle(
    *, pilot: dict[str, Any], factor: dict[str, Any], policy: dict[str, Any],
    raw: dict[str, Any], cell_id: str, evidence_prefix: str,
    nominal_log: Path, runtime_manifest: Path, classification_path: Path,
    run_start_ns: int, run_start_utc: str, run_end_utc: str
) -> dict[str, Any]:
    require_active_pilot(pilot, cell_id=cell_id)
    raw = deepcopy(raw)
    health_ok = _runtime_health(nominal_log=nominal_log, runtime_manifest=runtime_manifest)
    health_ref = f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt"
    class_ref = f"{evidence_prefix}/immutable-ground/pilot-classification-evidence.json"
    _write(classification_path, {
        "schema": 1, "decision_id": DECISION_ID, "family": "recovery",
        "health_checks_passed": health_ok, "recovery_manifest_complete": False,
        "development_preflight": False, "pilot_data": True,
    })
    cls_ns = int(raw["criteria_classification_ns"])
    raw["recovery_criteria"]["health_checks_passed"] = {
        "available_current": True, "criterion_satisfied": health_ok,
        "evidence_ref": health_ref, "observed_ns": cls_ns,
    }
    raw["recovery_criteria"]["recovery_manifest_complete"] = {
        "available_current": True, "criterion_satisfied": False,
        "evidence_ref": class_ref, "observed_ns": cls_ns,
    }
    derived = derive_recovery_runtime_observation(
        pilot=_semantic_contract_view(pilot), cell_id=cell_id, observation=raw
    )
    require_recovery_observation_acceptance(derived)
    containment = bool(derived["containment"]["predicate"])
    trusted = bool(derived["trusted_recovery"]["predicate"])
    operational = containment and health_ok and raw["recovery_criteria"]["authorized_command_path_restored"]["criterion_satisfied"]
    interval = derived["ground_spacecraft_divergence_interval"]
    derived_ref = f"{evidence_prefix}/immutable-ground/recovery-runtime-observation-derived.json"
    return {
        "factor_context": deepcopy(factor),
        "execution_metadata": {
            "effective_policy_id": policy["delegated_policy_id"],
            "selected_action": policy["selected_action"],
            "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
        },
        "runtime_observation": {
            "family": "recovery",
            "clock": {
                "run_start_utc": run_start_utc, "run_end_utc": run_end_utc,
                "run_start_ns": int(run_start_ns),
                "event_activation_ns": raw["event_activation_ns"],
                "containment_ns": derived["containment"]["observed_ns"],
                "trusted_recovery_ns": derived["trusted_recovery"]["observed_ns"],
                "run_end_ns": raw["run_end_ns"],
            },
            "event_success": {
                "predicate": True, "observed_ns": raw["event_success_ns"],
                "evidence_ref": f"{evidence_prefix}/runtime-observation/event-slot-sha256.txt",
            },
            "objective_results": {
                key: {"completed": row["completed"], "evidence_ref": derived_ref}
                for key, row in derived["objective_results"].items()
            },
            "invariant_violation_intervals": [],
            "legitimate_commands": {
                "attempted": derived["legitimate_commands"]["attempted"],
                "rejected": derived["legitimate_commands"]["rejected"],
                "evidence_ref": f"{evidence_prefix}/immutable-ground/authorized-noop-probe.json",
            },
            "ground_spacecraft_divergence_intervals": [{
                "state_key": interval["state_key"], "start_ns": interval["start_ns"], "end_ns": interval["end_ns"]
            }],
            "recovery_observations": deepcopy(derived["recovery_observations"]),
            "recovery_checklist_excluded": [],
            "terminal_state_predicates": {
                "run_invalid": False, "mission_loss": False,
                "trusted_recovery_confirmed": trusted,
                "operational_restored": operational,
                "recovery_failed": not containment,
                "contained": containment,
            },
            "containment_evidence_ref": derived_ref,
            "trusted_recovery_evidence_ref": derived_ref if trusted else None,
            "terminal_state_evidence_refs": [derived_ref, class_ref, health_ref],
            "source_observation_refs": [
                f"{evidence_prefix}/immutable-ground/factor-context.json",
                f"{evidence_prefix}/immutable-ground/event-instance.json",
                f"{evidence_prefix}/immutable-ground/runtime-policy-decision.json",
                f"{evidence_prefix}/immutable-ground/post-response-slot.json",
                f"{evidence_prefix}/immutable-ground/authorized-noop-probe.json",
                derived_ref, class_ref, health_ref,
            ],
            "development_preflight": False,
            "pilot_data": True,
        },
        "notes": "WP8 Stage-1 generic recovery pilot; R04 command mitigation never counts as E3 update containment.",
    }


def _exact_factor_from_retained(
    pilot: dict[str, Any], retained: dict[str, Any], *, cell_id: str
) -> dict[str, Any]:
    expected = _factor(pilot, cell_id=cell_id, run_id=retained["run_id"])
    for key, value in expected.items():
        if retained.get(key) != value:
            raise ValueError(f"{cell_id}: retained factor differs from pilot cell: {key}")
    return expected


def transform_full_recovery_bundle(
    pilot: dict[str, Any], *, cell_id: str, factor: dict[str, Any],
    policy: dict[str, Any], observation: dict[str, Any], manifest: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    require_active_pilot(pilot, cell_id=cell_id)
    if cell_id not in RECOVERY_FULL_CELLS:
        raise ValueError("full trusted recovery supports R02/R03 only")
    exact = _exact_factor_from_retained(pilot, factor, cell_id=cell_id)
    criteria = manifest["trusted_recovery_criteria"]
    if len(criteria) != 10 or not all(value is True for value in criteria.values()):
        raise ValueError("full recovery pilot lacks all-ten proof")
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
    return ({
        "factor_context": exact,
        "execution_metadata": {
            "effective_policy_id": policy["delegated_policy_id"],
            "selected_action": policy["selected_action"],
            "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
        },
        "runtime_observation": runtime,
        "notes": "WP8 Stage-1 full trusted-recovery pilot; all ten criteria derive from retained runtime evidence.",
    }, manifest_out)


def transform_observability_bundle(
    pilot: dict[str, Any], *, factor: dict[str, Any], policy: dict[str, Any],
    observation: dict[str, Any], manifest: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    require_active_pilot(pilot, cell_id="O01")
    exact = _exact_factor_from_retained(pilot, factor, cell_id="O01")
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
    return ({
        "factor_context": exact,
        "execution_metadata": {
            "effective_policy_id": policy["delegated_policy_id"],
            "selected_action": policy["selected_action"],
            "oracle_ground_truth_read": policy["oracle_ground_truth_read"],
        },
        "runtime_observation": runtime,
        "notes": "WP8 Stage-1 O01 pilot; RECOVERY_FAILED is bounded E4 containment failure only.",
    }, manifest_out)


def _bind_outputs(
    *, pilot_path: str, toolchain_path: str, schema_path: str,
    cell_id: str, run_id: str, bundle: dict[str, Any], bundle_path: str,
    run_record_path: str, provenance_path: str, acceptance_path: str,
    snapshot_id: str, host_architecture: str | None
) -> None:
    result = bind_authorized_family_observation(
        pilot=_load(pilot_path), toolchain=_load(toolchain_path), schema=_load(schema_path),
        cell_id=cell_id, run_id=run_id, observation_bundle=bundle,
        snapshot_id=snapshot_id, host_architecture=host_architecture,
    )
    _write(bundle_path, bundle)
    _write(run_record_path, result["run_record"])
    _write(provenance_path, result["binding_provenance"])
    _write(acceptance_path, result["stage1_acceptance"])


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-gate")
    p.add_argument("--pilot-config", required=True)
    p.add_argument("--cell-id", required=True)
    p.add_argument("--run-id", required=True)

    p = sub.add_parser("command-plan")
    for f in ("pilot-config","cell-id","run-id","output-plan-json","output-factor-json","output-event-json"):
        p.add_argument("--"+f, required=True)
    p.add_argument("--development-seed", required=True, type=int)
    p = sub.add_parser("command-select-policy")
    for f in ("pilot-config","cell-id","event-json","output-policy-json"): p.add_argument("--"+f, required=True)
    p = sub.add_parser("command-finalize-observation")
    for f in ("pilot-config","cell-id","factor-json","policy-json","gateway-decisions-jsonl","measurement-json","output-json"): p.add_argument("--"+f, required=True)
    p = sub.add_parser("command-bind-pilot")
    for f in ("pilot-config","toolchain-lock","schema","cell-id","factor-json","policy-json","finalized-json","gateway-decisions-jsonl","evidence-prefix","nominal-log","runtime-manifest","classification-json","run-start-utc","run-end-utc","bundle-json","run-record-json","provenance-json","acceptance-json","snapshot-id"): p.add_argument("--"+f, required=True)
    p.add_argument("--run-start-ns", required=True, type=int); p.add_argument("--host-architecture")

    p = sub.add_parser("recovery-plan")
    for f in ("pilot-config","cell-id","run-id","repo-commit","output-plan-json","output-factor-json","output-event-json","output-approved","output-tampered","output-manifest-json","output-tampered-verification-json"): p.add_argument("--"+f, required=True)
    p.add_argument("--development-seed", required=True, type=int)
    p = sub.add_parser("recovery-select-policy")
    for f in ("pilot-config","cell-id","event-json","output-policy-json"): p.add_argument("--"+f, required=True)
    p = sub.add_parser("recovery-prepare-rollback")
    for f in (
        "pilot-config",
        "cell-id",
        "event-json",
        "policy-json",
        "output-json",
    ):
        p.add_argument("--"+f, required=True)
    p = sub.add_parser("recovery-finalize-observation")
    for f in ("pilot-config","cell-id","policy-json","measurement-json","evidence-prefix","output-raw-observation-json","output-derived-observation-json","output-scope-json"): p.add_argument("--"+f, required=True)
    p = sub.add_parser("recovery-bind-pilot")
    for f in ("pilot-config","toolchain-lock","schema","cell-id","factor-json","policy-json","raw-json","evidence-prefix","nominal-log","runtime-manifest","classification-json","run-start-utc","run-end-utc","bundle-json","run-record-json","provenance-json","acceptance-json","snapshot-id"): p.add_argument("--"+f, required=True)
    p.add_argument("--run-start-ns", required=True, type=int); p.add_argument("--host-architecture")

    p = sub.add_parser("full-recovery-validate-factor")
    for f in ("pilot-config","cell-id","factor-json","repo-commit"):
        p.add_argument("--"+f, required=True)
    p = sub.add_parser("full-recovery-bind-existing")
    for f in ("pilot-config","toolchain-lock","schema","cell-id","factor-json","policy-json","observation-json","manifest-json","summary-json","bundle-json","run-record-json","provenance-json","acceptance-json","snapshot-id"): p.add_argument("--"+f, required=True)
    p.add_argument("--host-architecture")
    p = sub.add_parser("observability-bind-existing")
    for f in ("pilot-config","toolchain-lock","schema","factor-json","policy-json","observation-json","manifest-json","summary-json","bundle-json","run-record-json","provenance-json","acceptance-json","snapshot-id"): p.add_argument("--"+f, required=True)
    p.add_argument("--host-architecture")

    args = parser.parse_args()
    if args.command == "check-gate":
        pilot = _load(args.pilot_config)
        require_active_pilot(pilot, cell_id=args.cell_id)
        _factor(pilot, cell_id=args.cell_id, run_id=args.run_id)
        print("wp8_stage1_pilot_gate=PASS")
        return 0
    if args.command == "command-plan":
        value=command_plan(_load(args.pilot_config),cell_id=args.cell_id,seed=args.development_seed,run_id=args.run_id)
        _write(args.output_plan_json,value); _write(args.output_factor_json,value["factor_context"]); _write(args.output_event_json,value["event_instance"]); print("command_pilot_plan=PASS"); return 0
    if args.command == "command-select-policy":
        value=_select_policy(_load(args.pilot_config),cell_id=args.cell_id,event=_load(args.event_json)); _write(args.output_policy_json,value); print("command_pilot_policy_selection=PASS"); return 0
    if args.command == "command-finalize-observation":
        value=command_finalize(_load(args.pilot_config),cell_id=args.cell_id,factor=_load(args.factor_json),policy=_load(args.policy_json),gateway_rows=_read_jsonl(args.gateway_decisions_jsonl),measurement=_load(args.measurement_json)); _write(args.output_json,value); print("command_pilot_observation=PASS"); return 0
    if args.command == "command-bind-pilot":
        pilot=_load(args.pilot_config); factor=_load(args.factor_json); policy=_load(args.policy_json); finalized=_load(args.finalized_json); rows=_read_jsonl(args.gateway_decisions_jsonl)
        bundle=command_bundle(pilot=pilot,factor=factor,policy=policy,finalized=finalized,gateway_rows=rows,evidence_prefix=args.evidence_prefix,nominal_log=Path(args.nominal_log),runtime_manifest=Path(args.runtime_manifest),classification_path=Path(args.classification_json),run_start_ns=args.run_start_ns,run_start_utc=args.run_start_utc,run_end_utc=args.run_end_utc)
        _bind_outputs(pilot_path=args.pilot_config,toolchain_path=args.toolchain_lock,schema_path=args.schema,cell_id=args.cell_id,run_id=factor["run_id"],bundle=bundle,bundle_path=args.bundle_json,run_record_path=args.run_record_json,provenance_path=args.provenance_json,acceptance_path=args.acceptance_json,snapshot_id=args.snapshot_id,host_architecture=args.host_architecture); print("command_stage1_pilot_binding=PASS"); return 0
    if args.command == "recovery-plan":
        value=recovery_plan(_load(args.pilot_config),cell_id=args.cell_id,seed=args.development_seed,run_id=args.run_id); artifacts=value.pop("artifacts"); _write(args.output_plan_json,value); _write(args.output_factor_json,value["factor_context"]); _write(args.output_event_json,value["event_instance"]); Path(args.output_approved).write_bytes(artifacts["approved_bytes"]); Path(args.output_tampered).write_bytes(artifacts["tampered_bytes"]); _write(args.output_manifest_json,artifacts["manifest"]); _write(args.output_tampered_verification_json,artifacts["tampered_verification"]); print("recovery_generic_pilot_plan=PASS"); return 0
    if args.command == "recovery-select-policy":
        value=_select_policy(_load(args.pilot_config),cell_id=args.cell_id,event=_load(args.event_json)); _write(args.output_policy_json,value); print("recovery_pilot_policy_selection=PASS"); return 0
    if args.command == "recovery-prepare-rollback":
        pilot = _load(args.pilot_config)
        require_active_pilot(pilot, cell_id=args.cell_id)
        value=prepare_verified_rollback_pilot(event=_load(args.event_json),policy_decision=_load(args.policy_json)); _write(args.output_json,value); print("recovery_pilot_rollback_preparation=PASS"); return 0
    if args.command == "recovery-finalize-observation":
        pilot=_load(args.pilot_config); require_active_pilot(pilot,cell_id=args.cell_id); policy=_load(args.policy_json); raw=recovery_generic_raw(policy=policy,measurement=_load(args.measurement_json),evidence_prefix=args.evidence_prefix); derived=derive_recovery_runtime_observation(pilot=_semantic_contract_view(pilot),cell_id=args.cell_id,observation=raw); require_recovery_observation_acceptance(derived); _write(args.output_raw_observation_json,raw); _write(args.output_derived_observation_json,derived); _write(args.output_scope_json,{"schema":1,"decision_id":DECISION_ID,"cell_id":args.cell_id,"runtime_path":"recovery_generic","development_preflight":False,"pilot_data":True}); print("recovery_generic_pilot_observation=PASS"); return 0
    if args.command == "recovery-bind-pilot":
        pilot=_load(args.pilot_config); factor=_load(args.factor_json); policy=_load(args.policy_json); bundle=recovery_generic_bundle(pilot=pilot,factor=factor,policy=policy,raw=_load(args.raw_json),cell_id=args.cell_id,evidence_prefix=args.evidence_prefix,nominal_log=Path(args.nominal_log),runtime_manifest=Path(args.runtime_manifest),classification_path=Path(args.classification_json),run_start_ns=args.run_start_ns,run_start_utc=args.run_start_utc,run_end_utc=args.run_end_utc); _bind_outputs(pilot_path=args.pilot_config,toolchain_path=args.toolchain_lock,schema_path=args.schema,cell_id=args.cell_id,run_id=factor["run_id"],bundle=bundle,bundle_path=args.bundle_json,run_record_path=args.run_record_json,provenance_path=args.provenance_json,acceptance_path=args.acceptance_json,snapshot_id=args.snapshot_id,host_architecture=args.host_architecture); print("recovery_generic_stage1_pilot_binding=PASS"); return 0
    if args.command == "full-recovery-validate-factor":
        pilot=_load(args.pilot_config); require_active_pilot(pilot,cell_id=args.cell_id); retained=_load(args.factor_json); _exact_factor_from_retained(pilot,retained,cell_id=args.cell_id)
        if retained.get("repo_commit") != args.repo_commit:
            raise ValueError("full recovery retained factor repo_commit mismatch")
        print("full_recovery_pilot_factor_validation=PASS"); return 0
    if args.command == "full-recovery-bind-existing":
        pilot=_load(args.pilot_config); factor=_load(args.factor_json); policy=_load(args.policy_json); bundle,manifest=transform_full_recovery_bundle(pilot,cell_id=args.cell_id,factor=factor,policy=policy,observation=_load(args.observation_json),manifest=_load(args.manifest_json)); _write(args.manifest_json,manifest); summary=_load(args.summary_json); summary["development_preflight"]=False; summary["pilot_data"]=True; summary["study_cell"]=args.cell_id; _write(args.summary_json,summary); _bind_outputs(pilot_path=args.pilot_config,toolchain_path=args.toolchain_lock,schema_path=args.schema,cell_id=args.cell_id,run_id=bundle["factor_context"]["run_id"],bundle=bundle,bundle_path=args.bundle_json,run_record_path=args.run_record_json,provenance_path=args.provenance_json,acceptance_path=args.acceptance_json,snapshot_id=args.snapshot_id,host_architecture=args.host_architecture); print("full_recovery_stage1_pilot_binding=PASS"); return 0
    pilot=_load(args.pilot_config); factor=_load(args.factor_json); policy=_load(args.policy_json); bundle,manifest=transform_observability_bundle(pilot,factor=factor,policy=policy,observation=_load(args.observation_json),manifest=_load(args.manifest_json)); _write(args.manifest_json,manifest); summary=_load(args.summary_json); summary["development_preflight"]=False; summary["pilot_data"]=True; _write(args.summary_json,summary); _bind_outputs(pilot_path=args.pilot_config,toolchain_path=args.toolchain_lock,schema_path=args.schema,cell_id="O01",run_id=bundle["factor_context"]["run_id"],bundle=bundle,bundle_path=args.bundle_json,run_record_path=args.run_record_json,provenance_path=args.provenance_json,acceptance_path=args.acceptance_json,snapshot_id=args.snapshot_id,host_architecture=args.host_architecture); print("observability_stage1_pilot_binding=PASS"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
