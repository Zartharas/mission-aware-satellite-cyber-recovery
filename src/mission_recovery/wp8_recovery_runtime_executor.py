from __future__ import annotations

import argparse
import json
import re
import socket
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .nos3_e1_adapter import ALLOWED_HOST, ALLOWED_PORT, build_sample_noop_packet
from .policies import evaluate_policy
from .rollback_requests import build_verified_rollback_request
from .trusted_recovery import (
    validate_rollback_request,
    verify_replacement_source,
)
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)
from .wp8_recovery_effect_contract import (
    RECOVERY_CELL_IDS,
    build_recovery_cell_effect_contract,
    recovery_cells,
)
from .wp8_recovery_observation_contract import (
    derive_recovery_runtime_observation,
    require_recovery_observation_acceptance,
)

DECISION_ID = "R-037"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
DEVELOPMENT_VALIDATION_CELLS = ("R01", "R02", "R04")


def _cell_by_id(pilot: dict[str, Any], cell_id: str) -> dict[str, Any]:
    cells = {row["cell_id"]: row for row in recovery_cells(pilot)}
    if cell_id not in cells:
        raise ValueError(f"not a frozen Stage-1 recovery cell: {cell_id}")
    return deepcopy(cells[cell_id])


def reserved_pilot_seeds(pilot: dict[str, Any]) -> set[int]:
    values = {int(pilot["stage_1_control_validity"]["seed"])}
    values.update(int(x) for x in pilot["stage_2_variability"]["additional_seeds"])
    return values


def _validate_development_seed(pilot: dict[str, Any], seed: int) -> int:
    value = int(seed)
    if value <= 0:
        raise ValueError("development seed must be positive")
    if value in reserved_pilot_seeds(pilot):
        raise ValueError(f"development seed collides with frozen pilot seed: {value}")
    return value


def _validate_run_id(run_id: str) -> str:
    if not run_id or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("development run_id must contain only A-Z a-z 0-9 _ . -")
    return run_id


def validate_recovery_runtime_executor_contract(pilot: dict[str, Any]) -> None:
    runner = pilot["stage_1_runner_contract"]
    contract = runner["recovery_runtime_executor_contract"]
    dispatch = runner["dispatch_by_event_id"]["E3"]
    gate = pilot["instrumentation_gate"]
    status = gate["component_status"]

    expected = {
        "decision_id": DECISION_ID,
        "controller_module": "src.mission_recovery.wp8_recovery_runtime_executor",
        "development_runner": "scripts/run_wp8_recovery_stage1_development.sh",
        "factor_source": "wp8_pilot_design.cells",
        "runtime_policy_selection_source": "src.mission_recovery.policies.evaluate_policy",
        "raw_observation_validator": "R034_R035_R036_recovery_contract_chain",
        "development_only": True,
        "pilot_seed_collision_rejected": True,
        "pilot_executor_ready": False,
        "runtime_binding_performed": False,
        "primary_metrics_emitted": False,
        "terminal_state_emitted": False,
        "offline_validation_executes_runtime": False,
        "offline_validation_consumes_pilot_seed": False,
    }
    for key, value in expected.items():
        if contract[key] != value:
            raise ValueError(f"recovery runtime executor contract changed: {key}")

    if contract["supported_cell_ids"] != list(RECOVERY_CELL_IDS):
        raise ValueError("recovery runtime executor cells changed")
    if contract["development_validation_cells"] != list(DEVELOPMENT_VALIDATION_CELLS):
        raise ValueError("recovery development discriminator cells changed")
    if contract["development_validation_rationale"] != (
        "R01_covers_observe_only_R02_covers_verified_rollback_"
        "R04_covers_P7_to_P2_command_gateway_R03_runtime_duplicate_"
        "omitted_because_R02_covers_same_rollback_effect_family"
    ):
        raise ValueError("recovery development validation rationale changed")
    if contract["trusted_recovery_reference_run"] != (
        "results/wp8/runtime-binding/recovery/"
        "20260816T052549Z-wp8-recovery-binding-dev"
    ):
        raise ValueError("accepted trusted-recovery reference changed")
    if contract["development_r02_scope"] != (
        "generic_executor_verified_rollback_containment_and_R036_"
        "observation_adapter_not_duplicate_all_ten_criteria_runtime_proof"
    ):
        raise ValueError("R02 development validation scope changed")

    if dispatch.get("development_executor") != contract["development_runner"]:
        raise ValueError("E3 dispatch does not name recovery development executor")
    if dispatch["pilot_executor_ready"] is not False:
        raise ValueError("E3 pilot executor cannot be ready in R-037")

    if status["stage_1_recovery_effect_contract"] is not True:
        raise ValueError("R-034 recovery effect contract regressed")
    if status["recovery_evidence_semantics_separated"] is not True:
        raise ValueError("R-035 recovery evidence semantics regressed")
    if status["stage_1_recovery_observation_contract"] is not True:
        raise ValueError("R-036 recovery observation contract regressed")
    if status["stage_1_recovery_runtime_executor_static"] is not True:
        raise ValueError("R-037 recovery executor static gate is not closed")
    if status["stage_1_recovery_runtime_executor_runtime_validated"] is not False:
        raise ValueError("R-037 cannot predeclare runtime validation success")
    if status["stage_1_family_runtime_dispatch_adapters"] is not False:
        raise ValueError("family runtime dispatch adapters cannot pass in R-037")
    if gate["pilot_execution_authorized"] is not False:
        raise ValueError("R-037 cannot authorize pilot execution")


def build_development_execution_plan(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    development_seed: int,
    run_id: str,
    repo_commit: str,
) -> dict[str, Any]:
    validate_recovery_runtime_executor_contract(pilot)
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
        "repo_commit": repo_commit,
    }
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    effect = build_recovery_cell_effect_contract(pilot, cell_id)
    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    tampered_verification = verify_candidate(tampered, manifest)
    if sha256_hex(approved) != effect["event_artifacts"]["approved_sha256"]:
        raise ValueError("approved artifact identity changed")
    if sha256_hex(tampered) != effect["event_artifacts"]["tampered_sha256"]:
        raise ValueError("tampered artifact identity changed")
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP8_RECOVERY_RUNTIME_EXECUTOR_DEVELOPMENT_PLAN",
        "cell_id": cell_id,
        "development_preflight": True,
        "pilot_data": False,
        "pilot_seed_consumed": False,
        "factor_context": factor,
        "event_instance": event,
        "artifacts": {
            "approved_bytes": approved,
            "tampered_bytes": tampered,
            "manifest": manifest,
            "tampered_verification": tampered_verification,
        },
        "runtime_policy_selection": {
            "must_occur_after_event_activation": True,
            "must_not_read_ground_truth": True,
            "requested_policy_id": cell["policy_id"],
            "expected_effective_policy_id_for_acceptance_only":
                effect["policy_evaluation"]["actual_effective_policy_id"],
            "expected_selected_action_for_acceptance_only":
                effect["policy_evaluation"]["selected_action"],
        },
        "effect_family_for_acceptance_only":
            effect["effect_dispatch"]["effect_family"],
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
    validate_recovery_runtime_executor_contract(pilot)
    cell = _cell_by_id(pilot, cell_id)
    if event["event_id"] != "E3":
        raise ValueError("recovery runtime event must be E3")
    if event["mission_state"] != cell["mission_state_id"]:
        raise ValueError("recovery runtime mission state changed")
    if event["contact_condition"] != cell["contact_condition_id"]:
        raise ValueError("recovery runtime contact condition changed")
    if event["evidence_condition"] != cell["evidence_condition_id"]:
        raise ValueError("recovery runtime evidence condition changed")
    _validate_development_seed(pilot, int(event["seed"]))
    decision = evaluate_policy(cell["policy_id"], event)
    expected = build_recovery_cell_effect_contract(pilot, cell_id)["policy_evaluation"]
    if decision["delegated_policy_id"] != expected["actual_effective_policy_id"]:
        raise ValueError("runtime effective policy differs from frozen recovery semantics")
    if decision["selected_action"] != expected["selected_action"]:
        raise ValueError("runtime selected action differs from frozen recovery semantics")
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("runtime recovery policy cannot read ground truth")
    result = deepcopy(decision)
    result.update({
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "runtime_policy_selection": True,
        "development_preflight": True,
        "pilot_data": False,
    })
    return result


def prepare_verified_rollback(
    *,
    event: dict[str, Any],
    policy_decision: dict[str, Any],
) -> dict[str, Any]:
    manifest = build_manifest()
    approved = build_approved_update()
    tampered = build_tampered_update()
    tampered_verification = verify_candidate(tampered, manifest)
    request = build_verified_rollback_request(
        event_instance=event,
        policy_decision=policy_decision,
        manifest=manifest,
        candidate_verification=tampered_verification,
    )
    validation = validate_rollback_request(
        request=request,
        policy_decision=policy_decision,
        manifest=manifest,
        pre_recovery_candidate_sha256=(
            tampered_verification["actual_sha256"]
        ),
    )
    source_verification = verify_replacement_source(
        approved,
        manifest,
    )

    request_valid = (
        validation["accepted"] is True
        and validation["reasons"] == []
    )
    source_valid = (
        source_verification["accepted"] is True
        and source_verification["reasons"] == []
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "rollback_request": request,
        "rollback_request_validation": validation,
        "rollback_request_validated": request_valid,
        "replacement_source_verification": source_verification,
        "replacement_source_verified": source_valid,
        "recovery_execution_performed": False,
        "development_preflight": True,
        "pilot_data": False,
    }


def send_authorized_noop(
    *,
    host: str = ALLOWED_HOST,
    port: int = ALLOWED_PORT,
) -> dict[str, Any]:
    if host != ALLOWED_HOST or port != ALLOWED_PORT:
        raise ValueError("authorized NOOP target is restricted to internal nos-fsw:5012")
    packet = build_sample_noop_packet()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sent = sock.sendto(packet, (host, port))
    finally:
        sock.close()
    if sent != len(packet):
        raise RuntimeError(f"short authorized NOOP send: {sent}/{len(packet)}")
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "source_id": "authorized_ground",
        "command_class": "sample_noop",
        "target": f"{host}:{port}",
        "datagrams_sent": 1,
        "bytes_sent": sent,
        "packet_hex": packet.hex(),
        "packet_sha256": sha256_hex(packet),
        "study_event": False,
        "development_preflight": True,
        "pilot_data": False,
    }


def build_development_observation(
    pilot: dict[str, Any],
    *,
    cell_id: str,
    policy_decision: dict[str, Any],
    measurement: dict[str, Any],
    evidence_prefix: str,
) -> dict[str, Any]:
    validate_recovery_runtime_executor_contract(pilot)
    effect = build_recovery_cell_effect_contract(pilot, cell_id)
    family = effect["effect_dispatch"]["effect_family"]
    containment = (
        measurement["post_response_slot_sha256"]
        == effect["event_artifacts"]["approved_sha256"]
        and measurement["rejected_sha256_absent"] is True
        and measurement["temporary_recovery_state_absent"] is True
    )
    slot_ns = int(measurement["post_response_slot_observed_ns"])
    noop_ns = int(measurement["authorized_noop_probe_observed_ns"])
    cls_ns = int(measurement["criteria_classification_ns"])
    rollback_validated = bool(measurement["rollback_request_validated"])
    replacement_verified = bool(measurement["replacement_source_verified"])
    noop_delta = int(measurement["authorized_noop_marker_delta"])

    def row(available: bool, satisfied: bool, ref: str, observed_ns: int) -> dict[str, Any]:
        return {
            "available_current": available,
            "criterion_satisfied": satisfied,
            "evidence_ref": f"{evidence_prefix}/{ref}",
            "observed_ns": int(observed_ns),
        }

    criteria = {
        "approved_version": row(True, containment, "immutable-ground/post-response-slot.json", slot_ns),
        "integrity_measurement_valid": row(True, containment, "immutable-ground/post-response-slot.json", slot_ns),
        "authorization_valid": row(
            family == "rollback_request",
            (
                family == "rollback_request"
                and rollback_validated
                and replacement_verified
            ),
            (
                "immutable-ground/rollback-preparation.json"
                if family == "rollback_request"
                else "immutable-ground/development-evidence-scope.json"
            ),
            int(measurement["policy_enforcement_ns"]),
        ),
        "measured_state_current": row(True, containment, "immutable-ground/post-response-slot.json", slot_ns),
        "authorized_command_path_restored": row(
            True, noop_delta == 1, "immutable-ground/authorized-noop-probe.json", noop_ns
        ),
        "ground_spacecraft_state_agreed": row(True, containment, "immutable-ground/post-response-slot.json", slot_ns),
        "required_telemetry_restored": row(
            False, False, "immutable-ground/development-evidence-scope.json", cls_ns
        ),
        "health_checks_passed": row(
            False, False, "immutable-ground/development-evidence-scope.json", cls_ns
        ),
        "no_residual_unauthorized_state": row(True, containment, "immutable-ground/post-response-slot.json", slot_ns),
        "recovery_manifest_complete": row(
            False, False, "immutable-ground/development-evidence-scope.json", cls_ns
        ),
    }

    observation = {
        "actual_effective_policy_id": policy_decision["delegated_policy_id"],
        "selected_action": policy_decision["selected_action"],
        "event_slot_sha256": measurement["event_slot_sha256"],
        "post_response_slot_sha256": measurement["post_response_slot_sha256"],
        "rejected_sha256_absent": measurement["rejected_sha256_absent"],
        "temporary_recovery_state_absent": measurement["temporary_recovery_state_absent"],
        "rollback_request_emitted": measurement["rollback_request_emitted"],
        "rollback_request_validated": rollback_validated,
        "replacement_source_verified": replacement_verified,
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
    if family == "command_gateway":
        observation["command_gateway_observation"] = {
            "matched_attacker_probe_count": int(measurement["matched_attacker_probe_count"]),
            "attacker_reset_marker_delta": int(measurement["attacker_reset_marker_delta"]),
            "authorized_noop_attempt_count": 1,
            "authorized_noop_marker_delta": noop_delta,
        }
        observation["command_gateway_probe_observed_ns"] = int(
            measurement["command_gateway_probe_observed_ns"]
        )

    derived = derive_recovery_runtime_observation(
        pilot=pilot,
        cell_id=cell_id,
        observation=observation,
    )
    require_recovery_observation_acceptance(derived)
    return {
        "raw_observation": observation,
        "derived_observation": derived,
        "development_evidence_scope": {
            "required_telemetry_restored_measured": False,
            "health_checks_passed_measured": False,
            "recovery_manifest_complete_measured": False,
            "trusted_recovery_runtime_claimed": False,
            "trusted_recovery_reference_run":
                pilot["stage_1_runner_contract"]["recovery_runtime_executor_contract"][
                    "trusted_recovery_reference_run"
                ],
            "purpose": "generic_executor_branch_and_R036_adapter_validation_only",
        },
    }


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--pilot-config", required=True)
    plan.add_argument("--cell-id", required=True, choices=list(RECOVERY_CELL_IDS))
    plan.add_argument("--development-seed", required=True, type=int)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--repo-commit", required=True)
    plan.add_argument("--output-plan-json", required=True)
    plan.add_argument("--output-factor-json", required=True)
    plan.add_argument("--output-event-json", required=True)
    plan.add_argument("--output-approved", required=True)
    plan.add_argument("--output-tampered", required=True)
    plan.add_argument("--output-manifest-json", required=True)
    plan.add_argument("--output-tampered-verification-json", required=True)

    select = sub.add_parser("select-policy")
    select.add_argument("--pilot-config", required=True)
    select.add_argument("--cell-id", required=True, choices=list(RECOVERY_CELL_IDS))
    select.add_argument("--event-json", required=True)
    select.add_argument("--output-policy-json", required=True)

    rollback = sub.add_parser("prepare-rollback")
    rollback.add_argument("--event-json", required=True)
    rollback.add_argument("--policy-json", required=True)
    rollback.add_argument("--output-json", required=True)

    noop = sub.add_parser("send-authorized-noop")
    noop.add_argument("--output-json", required=True)

    finalize = sub.add_parser("finalize-observation")
    finalize.add_argument("--pilot-config", required=True)
    finalize.add_argument("--cell-id", required=True, choices=list(RECOVERY_CELL_IDS))
    finalize.add_argument("--policy-json", required=True)
    finalize.add_argument("--measurement-json", required=True)
    finalize.add_argument("--evidence-prefix", required=True)
    finalize.add_argument("--output-raw-observation-json", required=True)
    finalize.add_argument("--output-derived-observation-json", required=True)
    finalize.add_argument("--output-scope-json", required=True)

    args = parser.parse_args()

    if args.command == "plan":
        pilot = _load_json(args.pilot_config)
        result = build_development_execution_plan(
            pilot,
            cell_id=args.cell_id,
            development_seed=args.development_seed,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        serializable = dict(result)
        artifacts = serializable.pop("artifacts")
        _write_json(args.output_plan_json, serializable)
        _write_json(args.output_factor_json, result["factor_context"])
        _write_json(args.output_event_json, result["event_instance"])
        Path(args.output_approved).write_bytes(artifacts["approved_bytes"])
        Path(args.output_tampered).write_bytes(artifacts["tampered_bytes"])
        _write_json(args.output_manifest_json, artifacts["manifest"])
        _write_json(
            args.output_tampered_verification_json,
            artifacts["tampered_verification"],
        )
        print("recovery_development_plan=PASS")
        return 0

    if args.command == "select-policy":
        pilot = _load_json(args.pilot_config)
        result = select_runtime_policy(
            pilot,
            cell_id=args.cell_id,
            event=_load_json(args.event_json),
        )
        _write_json(args.output_policy_json, result)
        print("runtime_effective_policy=" + result["delegated_policy_id"])
        print("runtime_selected_action=" + result["selected_action"])
        return 0

    if args.command == "prepare-rollback":
        result = prepare_verified_rollback(
            event=_load_json(args.event_json),
            policy_decision=_load_json(args.policy_json),
        )
        _write_json(args.output_json, result)
        print("verified_rollback_preparation=PASS")
        return 0

    if args.command == "send-authorized-noop":
        result = send_authorized_noop()
        _write_json(args.output_json, result)
        print("authorized_noop_send=PASS")
        return 0

    pilot = _load_json(args.pilot_config)
    result = build_development_observation(
        pilot,
        cell_id=args.cell_id,
        policy_decision=_load_json(args.policy_json),
        measurement=_load_json(args.measurement_json),
        evidence_prefix=args.evidence_prefix,
    )
    _write_json(args.output_raw_observation_json, result["raw_observation"])
    _write_json(args.output_derived_observation_json, result["derived_observation"])
    _write_json(args.output_scope_json, result["development_evidence_scope"])
    print("recovery_runtime_raw_observation=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
