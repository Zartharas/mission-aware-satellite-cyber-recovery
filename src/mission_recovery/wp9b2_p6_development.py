from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .events import materialize_event
from .rollback_requests import build_verified_rollback_request
from .trusted_recovery import validate_rollback_request, verify_replacement_source
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)
from .wp9_static_contracts import (
    build_p6_handoff_contract,
    campaign_cells,
    evaluate_wp9_policy,
    load_campaign_design,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GATE = ROOT / "configs" / "wp9b2_p6_runtime_gate.json"
DEFAULT_R046 = ROOT / "configs" / "wp9b2_development_cases.json"
DECISION_ID = "R-047"
P6_CASE_IDS = {"D01", "D02"}
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _sha_record(value: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def load_p6_gate(path: Path | str = DEFAULT_GATE) -> dict[str, Any]:
    return _load(path)


def _r046_rows(path: Path | str = DEFAULT_R046) -> dict[str, dict[str, Any]]:
    data = _load(path)
    return {row["case_id"]: row for row in data["cases"]}


def validate_p6_gate(gate: dict[str, Any] | None = None) -> None:
    gate = gate or load_p6_gate()
    if gate["decision_id"] != DECISION_ID:
        raise ValueError("WP9-B2 P6 gate decision is not R-047")
    if gate["status"] != (
        "WP9B2_P6_DEVELOPMENT_EXECUTOR_STATICALLY_READY_"
        "RUNTIME_VALIDATION_PENDING"
    ):
        raise ValueError("WP9-B2 P6 gate status changed")
    if gate["case_ids"] != ["D01", "D02"]:
        raise ValueError("WP9-B2 P6 gate cases changed")
    if gate["campaign_cell_ids"] != ["A16", "A17"]:
        raise ValueError("WP9-B2 P6 campaign cells changed")
    if gate["development_seeds"] != [9601, 9602]:
        raise ValueError("WP9-B2 P6 development seeds changed")

    timing = gate["development_contact_window"]
    if int(timing["seconds"]) != 2:
        raise ValueError("P6 development timing surrogate changed")
    if timing["final_campaign_parameter"] is not False:
        raise ValueError("development timing cannot become campaign timing")
    if timing["final_campaign_duration_frozen"] is not False:
        raise ValueError("final campaign contact-window duration is not frozen here")
    if timing["wp9b3_campaign_duration_freeze_required"] is not True:
        raise ValueError("WP9-B3 contact-window freeze requirement changed")

    boundary = gate["scientific_boundary"]
    for key in ("development_only", "single_case_per_invocation", "development_runtime_data"):
        if boundary[key] is not True:
            raise ValueError(f"P6 gate boundary must remain true: {key}")
    for key in (
        "automatic_next_case",
        "final_campaign_seed_consumption",
        "final_campaign_data_generation",
        "repetition_count_frozen",
        "final_campaign_execution_authorized",
        "real_human_operator_required",
        "real_world_ground_contact_required",
        "external_network_required",
        "rf_transmission_allowed",
        "ground_truth_policy_oracle_allowed",
    ):
        if boundary[key] is not False:
            raise ValueError(f"P6 gate boundary must remain false: {key}")

    rows = _r046_rows()
    design = load_campaign_design()
    cells = campaign_cells(design)
    expected = {
        "D01": ("A16", 9601, "C0", True, 0),
        "D02": ("A17", 9602, "C1", False, 1),
    }
    for case_id, (cell_id, seed, contact, available, missed) in expected.items():
        historical = rows[case_id]
        if historical["campaign_cell_id"] != cell_id:
            raise ValueError(f"{case_id}: historical R-046 cell changed")
        if int(historical["development_seed"]) != seed:
            raise ValueError(f"{case_id}: historical R-046 seed changed")
        if historical["executor_ready"] is not False:
            raise ValueError(
                f"{case_id}: R-046 must remain the historical pre-readiness record"
            )
        if historical["executor"] != "scripts/run_wp9b2_p6_development.sh":
            raise ValueError(f"{case_id}: historical executor path changed")

        cell = cells[cell_id]
        if (
            cell["event_id"],
            cell["mission_state_id"],
            cell["contact_condition_id"],
            cell["evidence_condition_id"],
            cell["policy_id"],
            cell["expected_effective_policy_id"],
        ) != ("E3", "M4", contact, "T0", "P6", "P6"):
            raise ValueError(f"{case_id}: frozen campaign P6 factors changed")

        semantics = gate["case_semantics"][case_id]
        if semantics["contact_condition_id"] != contact:
            raise ValueError(f"{case_id}: P6 contact semantics changed")
        if semantics["authorization_available_at_response_boundary"] is not available:
            raise ValueError(f"{case_id}: P6 boundary availability changed")
        if int(semantics["missed_contact_windows"]) != missed:
            raise ValueError(f"{case_id}: P6 missed-window semantics changed")


def build_p6_plan(*, case_id: str, run_id: str, repo_commit: str) -> dict[str, Any]:
    validate_p6_gate()
    if case_id not in P6_CASE_IDS:
        raise ValueError("P6 development plan accepts D01/D02 only")
    if not run_id or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("P6 development run_id contains unsupported characters")
    if not repo_commit or len(repo_commit) < 7:
        raise ValueError("P6 development repo identity is missing")

    gate = load_p6_gate()
    rows = _r046_rows()
    row = rows[case_id]
    design = load_campaign_design()
    cell = campaign_cells(design)[row["campaign_cell_id"]]
    seed = int(row["development_seed"])
    event = materialize_event(
        "E3",
        mission_state="M4",
        contact_condition=cell["contact_condition_id"],
        evidence_condition="T0",
        seed=seed,
    )
    decision = evaluate_wp9_policy("P6", event)
    if decision["delegated_policy_id"] != "P6":
        raise ValueError("P6 pre-authorization delegate changed")
    if decision["selected_action"] != "WAIT_FOR_GROUND_AUTHORIZATION":
        raise ValueError("P6 pre-authorization action changed")
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("P6 cannot read immutable ground truth")

    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    tampered_verification = verify_candidate(tampered, manifest)
    if tampered_verification["accepted"] is not False:
        raise ValueError("P6 E3 tampered candidate must be rejected")
    if "sha256_mismatch" not in tampered_verification["reasons"]:
        raise ValueError("P6 E3 tampered candidate rejection changed")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_P6_DEVELOPMENT_RUNTIME_PLAN",
        "case_id": case_id,
        "campaign_cell_id": row["campaign_cell_id"],
        "run_id": run_id,
        "repo_commit": repo_commit,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": "M4",
            "event_id": "E3",
            "policy_id": "P6",
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": "T0",
        },
        "event_instance": event,
        "pre_authorization_policy_decision": decision,
        "p6_handoff_contract": build_p6_handoff_contract(event),
        "development_contact_window_seconds": int(
            gate["development_contact_window"]["seconds"]
        ),
        "development_contact_window_final_campaign_parameter": False,
        "artifact_evidence": {
            "approved_sha256": sha256_hex(approved),
            "tampered_sha256": sha256_hex(tampered),
            "manifest": manifest,
            "tampered_verification": tampered_verification,
        },
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "trusted_recovery_claim": False,
        "actual_recovery_execution_required": False,
        "automatic_next_case": False,
    }


def observe_p6_policy(*, plan: dict[str, Any], observed_monotonic_ns: int) -> dict[str, Any]:
    event = plan["event_instance"]
    decision = evaluate_wp9_policy("P6", event)
    if decision != plan["pre_authorization_policy_decision"]:
        raise ValueError("runtime-observed P6 decision differs from frozen plan")
    return {
        "schema": 1,
        "case_id": plan["case_id"],
        "observed_monotonic_ns": int(observed_monotonic_ns),
        "requested_policy_id": "P6",
        "delegated_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        "decision_sha256": decision["decision_sha256"],
    }


def validate_authorization_observation(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
) -> None:
    gate = load_p6_gate()
    case_id = plan["case_id"]
    expected = gate["case_semantics"][case_id]
    if authorization["source"] != "synthetic_ground_authorization_schedule":
        raise ValueError("P6 authorization source changed")
    if authorization["authorization_current"] is not True:
        raise ValueError("P6 handoff requires current observed authorization")
    if authorization["rollback_request_exists_before_authorization"] is not False:
        raise ValueError("rollback request existed before P6 authorization")
    if authorization["available_at_response_boundary"] is not expected[
        "authorization_available_at_response_boundary"
    ]:
        raise ValueError("P6 observed boundary availability changed")
    if int(authorization["missed_contact_windows"]) != int(
        expected["missed_contact_windows"]
    ):
        raise ValueError("P6 observed missed-window count changed")
    if authorization["contact_condition_id"] != expected["contact_condition_id"]:
        raise ValueError("P6 authorization contact condition changed")

    boundary_ns = int(authorization["response_boundary_monotonic_ns"])
    observed_ns = int(authorization["authorization_observed_monotonic_ns"])
    if observed_ns < boundary_ns:
        raise ValueError("P6 authorization observation predates response boundary")

    window_ns = int(plan["development_contact_window_seconds"] * 1_000_000_000)
    if case_id == "D01":
        if authorization["pre_release_probe_performed"] is not False:
            raise ValueError("D01 must not fabricate a missed-window probe")
        if int(authorization["release_after_modeled_window_count"]) != 0:
            raise ValueError("D01 authorization must be immediate")
    else:
        if authorization["pre_release_probe_performed"] is not True:
            raise ValueError("D02 requires a pre-release no-authorization probe")
        if authorization["pre_release_authorization_current"] is not False:
            raise ValueError("D02 authorization became current before the missed window")
        if int(authorization["release_after_modeled_window_count"]) != 1:
            raise ValueError("D02 must release after exactly one modeled window")
        if observed_ns - boundary_ns < window_ns:
            raise ValueError("D02 authorization released before one development window")


def build_p5_handoff(
    *,
    plan: dict[str, Any],
    authorization: dict[str, Any],
    handoff_monotonic_ns: int,
) -> dict[str, Any]:
    validate_authorization_observation(plan=plan, authorization=authorization)
    observed_ns = int(authorization["authorization_observed_monotonic_ns"])
    if int(handoff_monotonic_ns) < observed_ns:
        raise ValueError("P6 handoff predates observed authorization")

    event = plan["event_instance"]
    transition = plan["p6_handoff_contract"]
    decision = {
        "requested_policy_id": "P6",
        "delegated_policy_id": transition["post_authorization_delegated_policy_id"],
        "selected_action": transition["post_authorization_action"],
        "autonomy_level": "ground_dependent_handoff",
        "decision_basis": "runtime_observed_synthetic_ground_authorization_current",
        "event_id": event["event_id"],
        "mission_state": event["mission_state"],
        "contact_condition": event["contact_condition"],
        "evidence_condition": event["evidence_condition"],
        "oracle_ground_truth_read": False,
        "trusted_recovery_verification_deferred_to_wp7": True,
        "handoff_monotonic_ns": int(handoff_monotonic_ns),
    }
    decision["decision_sha256"] = _sha_record(decision)
    if decision["delegated_policy_id"] != "P5":
        raise ValueError("P6 post-authorization delegate changed")
    if decision["selected_action"] != "REQUEST_VERIFIED_ROLLBACK":
        raise ValueError("P6 post-authorization action changed")

    manifest = plan["artifact_evidence"]["manifest"]
    tampered_verification = plan["artifact_evidence"]["tampered_verification"]
    request = build_verified_rollback_request(
        event_instance=event,
        policy_decision=decision,
        manifest=manifest,
        candidate_verification=tampered_verification,
    )
    validation = validate_rollback_request(
        request=request,
        policy_decision=decision,
        manifest=manifest,
        pre_recovery_candidate_sha256=plan["artifact_evidence"]["tampered_sha256"],
    )
    if validation["accepted"] is not True:
        raise ValueError("P6 handoff rollback request did not validate")

    replacement = verify_replacement_source(build_approved_update(), manifest)
    if replacement["accepted"] is not True:
        raise ValueError("P6 approved replacement source did not verify")

    return {
        "schema": 1,
        "case_id": plan["case_id"],
        "originating_policy_id": "P6",
        "delegated_policy_id": "P5",
        "handoff_policy_decision": decision,
        "rollback_request": request,
        "rollback_request_validation": validation,
        "replacement_source_verification": replacement,
        "actual_recovery_execution_performed": False,
        "trusted_recovery_claim": False,
    }


def finalize_p6_runtime(
    *,
    plan: dict[str, Any],
    event_observation: dict[str, Any],
    runtime_policy_observation: dict[str, Any],
    authorization: dict[str, Any],
    handoff: dict[str, Any],
    staged_approved_sha256: str,
) -> dict[str, Any]:
    validate_p6_gate()
    case_id = plan["case_id"]
    if case_id not in P6_CASE_IDS:
        raise ValueError("P6 finalization accepts D01/D02 only")

    if event_observation["event_activation_observed"] is not True:
        raise ValueError("P6 E3 activation was not observed")
    if event_observation["observed_sha256"] != plan["artifact_evidence"]["tampered_sha256"]:
        raise ValueError("P6 E3 activation hash differs from tampered candidate")
    activation_ns = int(event_observation["event_activation_monotonic_ns"])
    policy_ns = int(runtime_policy_observation["observed_monotonic_ns"])
    if policy_ns < activation_ns:
        raise ValueError("P6 runtime policy observation predates event activation")
    if runtime_policy_observation["requested_policy_id"] != "P6":
        raise ValueError("P6 runtime policy identity changed")
    if runtime_policy_observation["delegated_policy_id"] != "P6":
        raise ValueError("P6 runtime pre-authorization delegate changed")
    if runtime_policy_observation["selected_action"] != "WAIT_FOR_GROUND_AUTHORIZATION":
        raise ValueError("P6 runtime pre-authorization action changed")
    if runtime_policy_observation["oracle_ground_truth_read"] is not False:
        raise ValueError("P6 runtime policy crossed oracle boundary")

    validate_authorization_observation(plan=plan, authorization=authorization)
    boundary_ns = int(authorization["response_boundary_monotonic_ns"])
    if boundary_ns < policy_ns:
        raise ValueError("P6 response boundary predates runtime policy observation")

    decision = handoff["handoff_policy_decision"]
    handoff_ns = int(decision["handoff_monotonic_ns"])
    auth_ns = int(authorization["authorization_observed_monotonic_ns"])
    if handoff_ns < auth_ns:
        raise ValueError("P6 handoff occurred before authorization observation")
    if handoff["originating_policy_id"] != "P6":
        raise ValueError("P6 handoff origin changed")
    if handoff["delegated_policy_id"] != "P5":
        raise ValueError("P6 handoff delegate changed")
    if decision["selected_action"] != "REQUEST_VERIFIED_ROLLBACK":
        raise ValueError("P6 handoff action changed")
    if handoff["rollback_request_validation"]["accepted"] is not True:
        raise ValueError("P6 rollback request validation failed")
    if handoff["replacement_source_verification"]["accepted"] is not True:
        raise ValueError("P6 replacement source verification failed")
    if staged_approved_sha256 != plan["artifact_evidence"]["approved_sha256"]:
        raise ValueError("P6 staged approved source identity changed")
    if handoff["actual_recovery_execution_performed"] is not False:
        raise ValueError("P6 development discriminator cannot execute recovery")
    if handoff["trusted_recovery_claim"] is not False:
        raise ValueError("P6 development discriminator cannot claim trusted recovery")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_P6_DEVELOPMENT_RUNTIME_PASS",
        "case_id": case_id,
        "campaign_cell_id": plan["campaign_cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": plan["factor_context"]["seed"],
        "contact_condition_id": plan["factor_context"]["contact_condition_id"],
        "pre_authorization_policy_id": "P6",
        "pre_authorization_action": "WAIT_FOR_GROUND_AUTHORIZATION",
        "authorization_source": authorization["source"],
        "authorization_available_at_response_boundary": authorization[
            "available_at_response_boundary"
        ],
        "missed_contact_windows_observed": authorization["missed_contact_windows"],
        "authorization_delay_s": (auth_ns - boundary_ns) / 1_000_000_000.0,
        "handoff_after_authorization_observed": True,
        "post_authorization_delegate": "P5",
        "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
        "rollback_request_validated": True,
        "approved_replacement_source_verified": True,
        "approved_source_staged_for_verification_only": True,
        "actual_recovery_execution_performed": False,
        "trusted_recovery_claim": False,
        "development_contact_window_seconds": plan[
            "development_contact_window_seconds"
        ],
        "development_contact_window_final_campaign_parameter": False,
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "repetition_count_frozen": False,
        "campaign_execution_authorized": False,
        "automatic_next_case": False,
        "acceptance_status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    plan = sub.add_parser("plan")
    plan.add_argument("--case-id", required=True)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--repo-commit", required=True)
    plan.add_argument("--output-plan-json", required=True)
    plan.add_argument("--output-event-json", required=True)
    plan.add_argument("--output-policy-json", required=True)
    plan.add_argument("--output-approved", required=True)
    plan.add_argument("--output-tampered", required=True)
    plan.add_argument("--output-manifest-json", required=True)
    plan.add_argument("--output-tampered-verification-json", required=True)

    observe = sub.add_parser("observe-policy")
    observe.add_argument("--plan-json", required=True)
    observe.add_argument("--observed-monotonic-ns", type=int, required=True)
    observe.add_argument("--output-json", required=True)

    handoff = sub.add_parser("handoff")
    handoff.add_argument("--plan-json", required=True)
    handoff.add_argument("--authorization-json", required=True)
    handoff.add_argument("--handoff-monotonic-ns", type=int, required=True)
    handoff.add_argument("--output-json", required=True)
    handoff.add_argument("--output-p5-policy-json", required=True)
    handoff.add_argument("--output-rollback-request-json", required=True)
    handoff.add_argument("--output-rollback-validation-json", required=True)
    handoff.add_argument("--output-replacement-verification-json", required=True)

    fin = sub.add_parser("finalize")
    fin.add_argument("--plan-json", required=True)
    fin.add_argument("--event-observation-json", required=True)
    fin.add_argument("--runtime-policy-observation-json", required=True)
    fin.add_argument("--authorization-json", required=True)
    fin.add_argument("--handoff-json", required=True)
    fin.add_argument("--staged-approved-sha256", required=True)
    fin.add_argument("--output-summary-json", required=True)

    args = parser.parse_args()
    if args.command == "validate":
        validate_p6_gate()
        print("WP9B2_P6_STATIC_GATE=PASS")
        return 0

    if args.command == "plan":
        value = build_p6_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write(args.output_plan_json, value)
        _write(args.output_event_json, value["event_instance"])
        _write(args.output_policy_json, value["pre_authorization_policy_decision"])
        approved = build_approved_update()
        tampered = build_tampered_update()
        Path(args.output_approved).write_bytes(approved)
        Path(args.output_tampered).write_bytes(tampered)
        _write(args.output_manifest_json, value["artifact_evidence"]["manifest"])
        _write(
            args.output_tampered_verification_json,
            value["artifact_evidence"]["tampered_verification"],
        )
        print("WP9B2_P6_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + value["case_id"])
        print("campaign_cell_id=" + value["campaign_cell_id"])
        print("development_seed=" + str(value["factor_context"]["seed"]))
        print("contact_condition_id=" + value["factor_context"]["contact_condition_id"])
        return 0

    if args.command == "observe-policy":
        value = observe_p6_policy(
            plan=_load(args.plan_json),
            observed_monotonic_ns=args.observed_monotonic_ns,
        )
        _write(args.output_json, value)
        print("WP9B2_P6_RUNTIME_POLICY_OBSERVATION=PASS")
        return 0

    if args.command == "handoff":
        value = build_p5_handoff(
            plan=_load(args.plan_json),
            authorization=_load(args.authorization_json),
            handoff_monotonic_ns=args.handoff_monotonic_ns,
        )
        _write(args.output_json, value)
        _write(args.output_p5_policy_json, value["handoff_policy_decision"])
        _write(args.output_rollback_request_json, value["rollback_request"])
        _write(
            args.output_rollback_validation_json,
            value["rollback_request_validation"],
        )
        _write(
            args.output_replacement_verification_json,
            value["replacement_source_verification"],
        )
        print("WP9B2_P6_HANDOFF=PASS")
        print("post_authorization_delegate=P5")
        print("post_authorization_action=REQUEST_VERIFIED_ROLLBACK")
        return 0

    value = finalize_p6_runtime(
        plan=_load(args.plan_json),
        event_observation=_load(args.event_observation_json),
        runtime_policy_observation=_load(args.runtime_policy_observation_json),
        authorization=_load(args.authorization_json),
        handoff=_load(args.handoff_json),
        staged_approved_sha256=args.staged_approved_sha256,
    )
    _write(args.output_summary_json, value)
    print("WP9B2_P6_DEVELOPMENT_ACCEPTANCE=PASS")
    print("case_id=" + value["case_id"])
    print(
        "missed_contact_windows_observed="
        + str(value["missed_contact_windows_observed"])
    )
    print(
        "authorization_available_at_response_boundary="
        + str(value["authorization_available_at_response_boundary"]).lower()
    )
    print("post_authorization_delegate=P5")
    print("rollback_request_validated=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
