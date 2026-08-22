from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policy_gateway import build_command_envelope, decide_forward
from .rollback_requests import build_verified_rollback_request
from .trusted_recovery import validate_rollback_request, verify_replacement_source
from .update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)
from .wp9_static_contracts import campaign_cells, evaluate_wp9_policy, load_campaign_design
from .wp9b2_development import case_registry, load_development_cases

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GATE = ROOT / "configs" / "wp9b2_e3_fixed_runtime_gate.json"
DECISION_ID = "R-048"
CASE_IDS = ("D06", "D07", "D08")
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: Path | str, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def load_gate(path: Path | str = DEFAULT_GATE) -> dict[str, Any]:
    return _load(path)


def validate_gate(gate: dict[str, Any] | None = None) -> None:
    gate = gate or load_gate()
    if gate["decision_id"] != DECISION_ID:
        raise ValueError("fixed-E3 development gate is not R-048")
    if gate["status"] != (
        "WP9B2_E3_FIXED_DEVELOPMENT_EXECUTOR_STATICALLY_READY_"
        "RUNTIME_VALIDATION_PENDING"
    ):
        raise ValueError("R-048 status changed")
    if gate["case_ids"] != list(CASE_IDS):
        raise ValueError("R-048 case set changed")
    if gate["campaign_cell_ids"] != ["A10", "A12", "A15"]:
        raise ValueError("R-048 campaign cells changed")
    if gate["development_seeds"] != [9606, 9607, 9608]:
        raise ValueError("R-048 development seeds changed")

    boundary = gate["scientific_boundary"]
    for key in (
        "development_only",
        "single_case_per_invocation",
    ):
        if boundary[key] is not True:
            raise ValueError(f"R-048 boundary must be true: {key}")
    for key in (
        "automatic_next_case",
        "final_campaign_seed_consumption",
        "final_campaign_data_generation",
        "repetition_count_frozen",
        "final_campaign_execution_authorized",
        "expected_values_used_as_measurements",
        "ground_truth_policy_oracle_allowed",
        "d08_t1_causal_recovery_failure_claim_allowed",
        "trusted_recovery_claim_allowed",
    ):
        if boundary[key] is not False:
            raise ValueError(f"R-048 boundary must be false: {key}")

    clarification = gate["d08_r046_clarification"]
    if clarification["r046_case_factor_mapping_changed"] is not False:
        raise ValueError("R-048 cannot change R-046 D08 factors")
    if clarification["r046_seed_changed"] is not False:
        raise ValueError("R-048 cannot change R-046 D08 seed")
    if clarification["r044_campaign_cell_changed"] is not False:
        raise ValueError("R-048 cannot change R-044 A15")

    r046 = load_development_cases()
    rows = case_registry(r046)
    expected = {
        "D06": ("A10", 9606, "recovery", "e3_fixed_p2_command_gateway"),
        "D07": ("A12", 9607, "recovery", "e3_fixed_p2_command_gateway"),
        "D08": ("A15", 9608, "recovery", "e3_fixed_p5_reduced_evidence"),
    }
    for case_id, values in expected.items():
        row = rows[case_id]
        if (
            row["campaign_cell_id"],
            int(row["development_seed"]),
            row["runtime_family"],
            row["runtime_variant"],
        ) != values:
            raise ValueError(f"R-046 identity changed for {case_id}")
        if row["executor_ready"] is not False:
            raise ValueError("R-046 history must remain pending for fixed E3")


def _case_row(case_id: str) -> dict[str, Any]:
    validate_gate()
    if case_id not in CASE_IDS:
        raise ValueError("fixed-E3 development accepts D06-D08 only")
    return case_registry()[case_id]


def _artifacts() -> dict[str, Any]:
    approved = build_approved_update()
    tampered = build_tampered_update()
    manifest = build_manifest()
    tampered_verification = verify_candidate(tampered, manifest)
    if tampered_verification["accepted"] is not False:
        raise ValueError("tampered E3 candidate unexpectedly accepted")
    return {
        "approved": approved,
        "tampered": tampered,
        "manifest": manifest,
        "tampered_verification": tampered_verification,
        "approved_sha256": sha256_hex(approved),
        "tampered_sha256": sha256_hex(tampered),
    }


def build_plan(*, case_id: str, run_id: str, repo_commit: str) -> dict[str, Any]:
    if RUN_ID_PATTERN.fullmatch(run_id or "") is None:
        raise ValueError("unsupported development run_id")
    if len(repo_commit or "") < 7:
        raise ValueError("repo commit identity missing")

    row = _case_row(case_id)
    design = load_campaign_design()
    cell = campaign_cells(design)[row["campaign_cell_id"]]
    seed = int(row["development_seed"])
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=seed,
    )
    expected_decision = evaluate_wp9_policy(cell["policy_id"], event)
    if expected_decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
        raise ValueError("fixed-E3 effective policy differs from R-044")
    if expected_decision["oracle_ground_truth_read"] is not False:
        raise ValueError("policy crossed immutable-ground-truth boundary")

    artifacts = _artifacts()
    plan: dict[str, Any] = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E3_FIXED_DEVELOPMENT_PLAN",
        "case_id": case_id,
        "campaign_cell_id": row["campaign_cell_id"],
        "run_id": run_id,
        "repo_commit": repo_commit,
        "factor_context": {
            "model_version": "0.4.0",
            "seed": seed,
            "mission_state_id": cell["mission_state_id"],
            "event_id": cell["event_id"],
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance": event,
        "expected_effective_policy_id_for_acceptance_only": cell[
            "expected_effective_policy_id"
        ],
        "expected_selected_action_for_acceptance_only": expected_decision[
            "selected_action"
        ],
        "artifact_identities": {
            "approved_sha256": artifacts["approved_sha256"],
            "tampered_sha256": artifacts["tampered_sha256"],
        },
        "runtime_policy_selection_must_follow_event_activation": True,
        "policy_time_visibility_used_as_classification_evidence": False,
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "automatic_next_case": False,
    }
    if case_id in {"D06", "D07"}:
        attacker = build_command_envelope("modeled_attacker", "sample_reset_counters")
        authorized = build_command_envelope("authorized_ground", "sample_noop")
        action = expected_decision["selected_action"]
        plan["p2_gateway_acceptance"] = {
            "attacker_probe_count": 2,
            "authorized_noop_attempt_count": 1,
            "attacker_forwarded_for_acceptance_only": decide_forward(action, attacker),
            "authorized_noop_forwarded_for_acceptance_only": decide_forward(
                action, authorized
            ),
            "expected_reset_marker_delta_for_acceptance_only": 0,
            "expected_noop_marker_delta_for_acceptance_only": 1,
        }
    else:
        plan["d08_bounded_scope"] = {
            "modeled_rollback_execution_required": True,
            "complete_ten_criterion_manifest_emitted": False,
            "trusted_recovery_confirmation_allowed": False,
            "nonconfirmation_causal_t1_claim_allowed": False,
            "policy_time_approved_version_omitted": True,
        }
    return plan


def observe_runtime_policy(plan: dict[str, Any]) -> dict[str, Any]:
    decision = evaluate_wp9_policy(
        plan["factor_context"]["policy_id"],
        plan["event_instance"],
    )
    if decision["delegated_policy_id"] != plan[
        "expected_effective_policy_id_for_acceptance_only"
    ]:
        raise ValueError("runtime policy delegate differs from frozen design")
    if decision["selected_action"] != plan[
        "expected_selected_action_for_acceptance_only"
    ]:
        raise ValueError("runtime policy action differs from frozen design")
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("runtime policy used immutable ground truth")
    return decision


def build_runtime_rollback(
    *, plan: dict[str, Any], runtime_policy: dict[str, Any]
) -> dict[str, Any]:
    if plan["case_id"] != "D08":
        raise ValueError("runtime rollback builder is D08-only")
    artifacts = _artifacts()
    request = build_verified_rollback_request(
        event_instance=plan["event_instance"],
        policy_decision=runtime_policy,
        manifest=artifacts["manifest"],
        candidate_verification=artifacts["tampered_verification"],
    )
    validation = validate_rollback_request(
        request=request,
        policy_decision=runtime_policy,
        manifest=artifacts["manifest"],
        pre_recovery_candidate_sha256=artifacts["tampered_sha256"],
    )
    replacement = verify_replacement_source(artifacts["approved"], artifacts["manifest"])
    if validation["accepted"] is not True:
        raise ValueError("D08 rollback request validation failed")
    if replacement["accepted"] is not True:
        raise ValueError("D08 approved replacement source validation failed")
    return {
        "request": request,
        "request_validation": validation,
        "replacement_verification": replacement,
    }


def finalize_p2(
    *,
    plan: dict[str, Any],
    runtime_policy: dict[str, Any],
    gateway_decisions: list[dict[str, Any]],
    event_slot_sha256: str,
    post_response_slot_sha256: str,
    reset_before: int,
    reset_after: int,
    noop_before: int,
    noop_after: int,
) -> dict[str, Any]:
    if plan["case_id"] not in {"D06", "D07"}:
        raise ValueError("P2 finalizer accepts D06/D07 only")
    if runtime_policy["delegated_policy_id"] != "P2":
        raise ValueError("fixed-E3 P2 runtime delegate changed")
    if runtime_policy["selected_action"] != "RESTRICT_HIGH_RISK_COMMANDS":
        raise ValueError("fixed-E3 P2 action changed")

    ids = plan["artifact_identities"]
    if event_slot_sha256 != ids["tampered_sha256"]:
        raise ValueError("E3 event activation slot identity changed")
    if post_response_slot_sha256 != ids["tampered_sha256"]:
        raise ValueError("P2 must not mutate the E3 update slot")

    if len(gateway_decisions) != 3:
        raise ValueError("P2 fixed-E3 validation requires exactly three decisions")
    attacker = [
        row for row in gateway_decisions
        if row.get("source_id") == "modeled_attacker"
        and row.get("command_class") == "sample_reset_counters"
    ]
    authorized = [
        row for row in gateway_decisions
        if row.get("source_id") == "authorized_ground"
        and row.get("command_class") == "sample_noop"
    ]
    if len(attacker) != 2 or any(row.get("forwarded") is not False for row in attacker):
        raise ValueError("P2 attacker reset probes were not both blocked")
    if len(authorized) != 1 or authorized[0].get("forwarded") is not True:
        raise ValueError("P2 authorized NOOP was not forwarded")
    if any(row.get("action") != "RESTRICT_HIGH_RISK_COMMANDS" for row in gateway_decisions):
        raise ValueError("P2 gateway action changed")

    reset_delta = int(reset_after) - int(reset_before)
    noop_delta = int(noop_after) - int(noop_before)
    if reset_delta != 0:
        raise ValueError("P2 attacker reset effect was observed")
    if noop_delta != 1:
        raise ValueError("P2 authorized NOOP effect was not observed exactly once")

    event = plan["event_instance"]
    if plan["case_id"] == "D07":
        if event["evidence_condition"] != "T1":
            raise ValueError("D07 evidence condition changed")
        if "approved_version" not in event["policy_evidence_omitted"]:
            raise ValueError("D07 must omit approved_version at policy time")
        if "approved_version" in event["policy_visible_evidence"]:
            raise ValueError("D07 leaked approved_version to policy-time evidence")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E3_FIXED_P2_DEVELOPMENT_RUNTIME_PASS",
        "case_id": plan["case_id"],
        "campaign_cell_id": plan["campaign_cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": plan["factor_context"]["seed"],
        "evidence_condition_id": plan["factor_context"]["evidence_condition_id"],
        "actual_effective_policy_id": "P2",
        "selected_action": "RESTRICT_HIGH_RISK_COMMANDS",
        "matched_attacker_probe_count": 2,
        "attacker_reset_marker_delta": reset_delta,
        "authorized_noop_attempt_count": 1,
        "authorized_noop_marker_delta": noop_delta,
        "command_path_mitigation_observed": True,
        "command_path_mitigation_counts_as_update_containment": False,
        "update_containment_observed": False,
        "containment_right_censored_at_run_end": True,
        "trusted_recovery_observed": False,
        "trusted_recovery_right_censored_at_run_end": True,
        "policy_time_approved_version_omitted": (
            "approved_version" in event["policy_evidence_omitted"]
        ),
        "policy_time_visibility_used_as_classification_evidence": False,
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "automatic_next_case": False,
        "acceptance_status": "PASS",
    }


def finalize_p5(
    *,
    plan: dict[str, Any],
    runtime_policy: dict[str, Any],
    rollback_bundle: dict[str, Any],
    event_slot_sha256: str,
    post_response_slot_sha256: str,
    authorized_noop_delta: int,
) -> dict[str, Any]:
    if plan["case_id"] != "D08":
        raise ValueError("P5 finalizer accepts D08 only")
    if runtime_policy["delegated_policy_id"] != "P5":
        raise ValueError("D08 fixed P5 delegate changed")
    if runtime_policy["selected_action"] != "REQUEST_VERIFIED_ROLLBACK":
        raise ValueError("D08 fixed P5 action changed")

    event = plan["event_instance"]
    if event["evidence_condition"] != "T1":
        raise ValueError("D08 evidence condition changed")
    if "approved_version" not in event["policy_evidence_omitted"]:
        raise ValueError("D08 must omit approved_version at policy time")
    if "approved_version" in event["policy_visible_evidence"]:
        raise ValueError("D08 leaked approved_version to policy-time evidence")

    ids = plan["artifact_identities"]
    if event_slot_sha256 != ids["tampered_sha256"]:
        raise ValueError("D08 E3 activation slot identity changed")
    if post_response_slot_sha256 != ids["approved_sha256"]:
        raise ValueError("D08 approved artifact did not occupy activation slot")
    if rollback_bundle["request_validation"]["accepted"] is not True:
        raise ValueError("D08 rollback request was not validated")
    if rollback_bundle["replacement_verification"]["accepted"] is not True:
        raise ValueError("D08 replacement source was not verified")
    if int(authorized_noop_delta) != 1:
        raise ValueError("D08 authorized command path did not remain available")

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E3_FIXED_P5_T1_DEVELOPMENT_RUNTIME_PASS",
        "case_id": "D08",
        "campaign_cell_id": plan["campaign_cell_id"],
        "run_id": plan["run_id"],
        "repo_commit": plan["repo_commit"],
        "development_seed": plan["factor_context"]["seed"],
        "evidence_condition_id": "T1",
        "actual_effective_policy_id": "P5",
        "selected_action": "REQUEST_VERIFIED_ROLLBACK",
        "policy_time_approved_version_omitted": True,
        "rollback_request_validated": True,
        "approved_replacement_source_verified": True,
        "modeled_rollback_execution_performed": True,
        "update_containment_observed": True,
        "authorized_command_path_probe_delta": 1,
        "complete_ten_criterion_manifest_emitted": False,
        "trusted_recovery_observed": False,
        "trusted_recovery_right_censored_at_run_end": True,
        "trusted_recovery_nonconfirmation_reason": (
            "bounded_development_scope_does_not_emit_complete_ten_criterion_manifest"
        ),
        "t1_causal_recovery_failure_claim": False,
        "policy_time_visibility_used_as_classification_evidence": False,
        "final_campaign_trusted_recovery_rule": (
            "all_applicable_classification_time_criteria_required"
        ),
        "development_preflight": True,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "automatic_next_case": False,
        "acceptance_status": "PASS",
    }


def _read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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
    plan.add_argument("--output-approved", required=True)
    plan.add_argument("--output-tampered", required=True)
    plan.add_argument("--output-manifest-json", required=True)
    plan.add_argument("--output-tampered-verification-json", required=True)

    policy = sub.add_parser("observe-policy")
    policy.add_argument("--plan-json", required=True)
    policy.add_argument("--output-policy-json", required=True)

    rollback = sub.add_parser("build-rollback")
    rollback.add_argument("--plan-json", required=True)
    rollback.add_argument("--policy-json", required=True)
    rollback.add_argument("--output-request-json", required=True)
    rollback.add_argument("--output-validation-json", required=True)
    rollback.add_argument("--output-replacement-json", required=True)

    p2 = sub.add_parser("finalize-p2")
    p2.add_argument("--plan-json", required=True)
    p2.add_argument("--policy-json", required=True)
    p2.add_argument("--gateway-decisions-jsonl", required=True)
    p2.add_argument("--event-slot-sha256", required=True)
    p2.add_argument("--post-response-slot-sha256", required=True)
    p2.add_argument("--reset-before", type=int, required=True)
    p2.add_argument("--reset-after", type=int, required=True)
    p2.add_argument("--noop-before", type=int, required=True)
    p2.add_argument("--noop-after", type=int, required=True)
    p2.add_argument("--output-summary-json", required=True)

    p5 = sub.add_parser("finalize-p5")
    p5.add_argument("--plan-json", required=True)
    p5.add_argument("--policy-json", required=True)
    p5.add_argument("--request-json", required=True)
    p5.add_argument("--validation-json", required=True)
    p5.add_argument("--replacement-json", required=True)
    p5.add_argument("--event-slot-sha256", required=True)
    p5.add_argument("--post-response-slot-sha256", required=True)
    p5.add_argument("--authorized-noop-delta", type=int, required=True)
    p5.add_argument("--output-summary-json", required=True)

    args = parser.parse_args()
    if args.command == "validate":
        validate_gate()
        print("WP9B2_E3_FIXED_STATIC_GATE=PASS")
        return 0

    if args.command == "plan":
        value = build_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        artifacts = _artifacts()
        _write(args.output_plan_json, value)
        _write(args.output_event_json, value["event_instance"])
        Path(args.output_approved).write_bytes(artifacts["approved"])
        Path(args.output_tampered).write_bytes(artifacts["tampered"])
        _write(args.output_manifest_json, artifacts["manifest"])
        _write(args.output_tampered_verification_json, artifacts["tampered_verification"])
        print("WP9B2_E3_FIXED_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + value["case_id"])
        print("campaign_cell_id=" + value["campaign_cell_id"])
        print("development_seed=" + str(value["factor_context"]["seed"]))
        print("evidence_condition_id=" + value["factor_context"]["evidence_condition_id"])
        return 0

    if args.command == "observe-policy":
        value = observe_runtime_policy(_load(args.plan_json))
        _write(args.output_policy_json, value)
        print("WP9B2_E3_FIXED_RUNTIME_POLICY=PASS")
        print("actual_effective_policy_id=" + value["delegated_policy_id"])
        print("selected_action=" + value["selected_action"])
        return 0

    if args.command == "build-rollback":
        value = build_runtime_rollback(
            plan=_load(args.plan_json),
            runtime_policy=_load(args.policy_json),
        )
        _write(args.output_request_json, value["request"])
        _write(args.output_validation_json, value["request_validation"])
        _write(args.output_replacement_json, value["replacement_verification"])
        print("WP9B2_E3_FIXED_ROLLBACK_REQUEST=PASS")
        return 0

    if args.command == "finalize-p2":
        value = finalize_p2(
            plan=_load(args.plan_json),
            runtime_policy=_load(args.policy_json),
            gateway_decisions=_read_jsonl(args.gateway_decisions_jsonl),
            event_slot_sha256=args.event_slot_sha256,
            post_response_slot_sha256=args.post_response_slot_sha256,
            reset_before=args.reset_before,
            reset_after=args.reset_after,
            noop_before=args.noop_before,
            noop_after=args.noop_after,
        )
        _write(args.output_summary_json, value)
        print("WP9B2_E3_FIXED_P2_ACCEPTANCE=PASS")
        print("case_id=" + value["case_id"])
        print("command_path_mitigation_observed=true")
        print("update_containment_observed=false")
        print("trusted_recovery_observed=false")
        return 0

    value = finalize_p5(
        plan=_load(args.plan_json),
        runtime_policy=_load(args.policy_json),
        rollback_bundle={
            "request": _load(args.request_json),
            "request_validation": _load(args.validation_json),
            "replacement_verification": _load(args.replacement_json),
        },
        event_slot_sha256=args.event_slot_sha256,
        post_response_slot_sha256=args.post_response_slot_sha256,
        authorized_noop_delta=args.authorized_noop_delta,
    )
    _write(args.output_summary_json, value)
    print("WP9B2_E3_FIXED_P5_ACCEPTANCE=PASS")
    print("case_id=D08")
    print("update_containment_observed=true")
    print("trusted_recovery_observed=false")
    print("t1_causal_recovery_failure_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
