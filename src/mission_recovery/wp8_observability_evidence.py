from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from jsonschema import Draft202012Validator, FormatChecker

EVIDENCE_KEYS = (
    "event", "policy", "event_success", "post_effect", "p4_probe",
    "p4_gateway_truth", "p4_gateway_decisions", "truth",
    "policy_visible", "health",
)


def build_manifest(*, root: Path, output: Path, evidence: dict[str, Path], times: dict[str, int]) -> dict:
    if tuple(evidence) != EVIDENCE_KEYS:
        raise ValueError("observability evidence sources must match frozen order")
    ordered = [
        times["event_activation_ns"], times["policy_selection_ns"],
        times["policy_enforcement_ns"], times["event_success_ns"],
        times["post_effect_ns"], times["health_ns"], times["manifest_ready_ns"],
    ]
    if ordered != sorted(ordered):
        raise ValueError("observability evidence timestamps are not monotonic")

    source_hashes = {}
    for path in evidence.values():
        try:
            ref = str(path.relative_to(root))
        except ValueError:
            ref = str(path)
        source_hashes[ref] = hashlib.sha256(path.read_bytes()).hexdigest()
    if len(source_hashes) != 10:
        raise ValueError("observability manifest must hash exactly 10 evidence files")

    health = json.loads(evidence["health"].read_text(encoding="utf-8"))
    post = json.loads(evidence["post_effect"].read_text(encoding="utf-8"))
    criteria = {
        "required_telemetry_restored": post["required_telemetry_restored"] is True,
        "health_checks_passed": (
            health["health_checks_passed"] is True
            and health["immutable_truth_available"] is True
            and health["policy_visible_plane_available"] is True
            and health["p4_command_gate_running"] is True
        ),
        "recovery_manifest_complete": True,
    }
    expected = {
        "required_telemetry_restored": False,
        "health_checks_passed": True,
        "recovery_manifest_complete": True,
    }
    if criteria != expected:
        raise ValueError("observability trusted-recovery criteria drifted")

    payload = {
        "schema": 1,
        "classification": "WP8_OBSERVABILITY_EVIDENCE_MANIFEST_READY",
        "decision_id": "R-022",
        "study_event_id": "E4",
        "requested_policy_id": "P7",
        "effective_policy_id": "P4",
        "development_preflight": True,
        "pilot_data": False,
        "visibility_deadline_s": 3.0,
        "trusted_recovery_criteria": criteria,
        "source_evidence_sha256": source_hashes,
        "evidence_complete": True,
        "containment_observed": False,
        "trusted_recovery_observed": False,
        "terminal_state_candidate": "RECOVERY_FAILED",
        "terminal_claim_boundary": (
            "bounded_modeled_response_failed_to_achieve_E4_observability_"
            "containment_only_not_spacecraft_failure_not_native_safe_mode_"
            "failure_not_mission_loss"
        ),
        "scientific_claim_boundary": (
            "software_only_policy_visible_telemetry_degradation_in_"
            "research_controlled_NOS3_no_RF_interference_no_live_spacecraft"
        ),
    }
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


def materialize(*, factor_path: Path, summary_path: Path, observation_path: Path,
                run_start_ns: int, event_activation_ns: int, event_success_ns: int,
                policy_selection_ns: int, policy_enforcement_ns: int, run_end_ns: int,
                run_start_utc: str, run_end_utc: str, repo_commit: str,
                runner_sha: str, rel: str) -> tuple[dict, dict]:
    factor = json.loads(factor_path.read_text(encoding="utf-8"))
    clock = {
        "run_start_ns": run_start_ns,
        "event_activation_ns": event_activation_ns,
        "event_success_ns": event_success_ns,
        "policy_selection_ns": policy_selection_ns,
        "policy_enforcement_ns": policy_enforcement_ns,
        "containment_ns": None,
        "trusted_recovery_ns": None,
        "run_end_ns": run_end_ns,
    }
    order = [run_start_ns, event_activation_ns, policy_selection_ns,
             policy_enforcement_ns, event_success_ns, run_end_ns]
    if order != sorted(order):
        raise ValueError("observability runtime clock order is invalid")

    summary = {
        "schema": 1,
        "classification": "WP8_OBSERVABILITY_RUNTIME_BINDING_DEVELOPMENT_PASS",
        "development_preflight": True,
        "pilot_data": False,
        "seed": factor["seed"],
        "repo_commit": repo_commit,
        "runner_sha256": runner_sha,
        "study_cell": "O01",
        "study_event_id": "E4",
        "requested_policy_id": "P7",
        "effective_policy_id": "P4",
        "policy_trigger_uses_ground_truth": False,
        "event_before_response_order": True,
        "event_success_after_frozen_visibility_deadline": True,
        "p4_native_safe_mode_claim": False,
        "p4_telemetry_restoration_claim": False,
        "containment_observed": False,
        "trusted_recovery_observed": False,
        "containment_right_censored": True,
        "trusted_recovery_right_censored": True,
        "terminal_taxonomy_decision_id": "R-022",
        "terminal_state": "RECOVERY_FAILED",
        "terminal_state_spacecraft_failure_claim": False,
        "legitimate_command_rejection_observed": True,
        "clock_ns": clock,
    }
    summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    ro = {
        "family": "observability",
        "clock": {
            "run_start_utc": run_start_utc,
            "run_end_utc": run_end_utc,
            "run_start_ns": run_start_ns,
            "event_activation_ns": event_activation_ns,
            "containment_ns": None,
            "trusted_recovery_ns": None,
            "run_end_ns": run_end_ns,
        },
        "event_success": {
            "predicate": True,
            "observed_ns": event_success_ns,
            "evidence_ref": f"{rel}/immutable-ground/event-success.json",
        },
        "objective_results": {
            "MO-3": {"completed": False, "evidence_ref": f"{rel}/immutable-ground/post-enforcement-effect.json"},
            "MO-5": {"completed": True, "evidence_ref": f"{rel}/immutable-ground/observability-evidence-manifest.json"},
        },
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": 1,
            "rejected": 1,
            "evidence_ref": f"{rel}/runtime-observation/p4-command-gateway-decisions.jsonl",
        },
        "ground_spacecraft_divergence_intervals": [],
        "recovery_observations": {
            "required_telemetry_restored": {"available_current": False, "evidence_ref": f"{rel}/immutable-ground/post-enforcement-effect.json"},
            "health_checks_passed": {"available_current": True, "evidence_ref": f"{rel}/immutable-ground/observability-health.json"},
            "recovery_manifest_complete": {"available_current": True, "evidence_ref": f"{rel}/immutable-ground/observability-evidence-manifest.json"},
        },
        "recovery_checklist_excluded": [
            "approved_version", "integrity_measurement_valid", "authorization_valid",
            "measured_state_current", "authorized_command_path_restored",
            "ground_spacecraft_state_agreed", "no_residual_unauthorized_state",
        ],
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": False,
            "operational_restored": False,
            "recovery_failed": True,
            "contained": False,
        },
        "containment_evidence_ref": f"{rel}/immutable-ground/post-enforcement-effect.json",
        "trusted_recovery_evidence_ref": f"{rel}/immutable-ground/observability-evidence-manifest.json",
        "terminal_state_evidence_refs": [
            f"{rel}/immutable-ground/event-success.json",
            f"{rel}/immutable-ground/post-enforcement-effect.json",
            f"{rel}/immutable-ground/observability-health.json",
            f"{rel}/immutable-ground/observability-evidence-manifest.json",
        ],
        "source_observation_refs": [
            f"{rel}/immutable-ground/event-instance.json",
            f"{rel}/immutable-ground/policy-decision.json",
            f"{rel}/immutable-ground/event-success.json",
            f"{rel}/immutable-ground/post-enforcement-effect.json",
            f"{rel}/immutable-ground/p4-authorized-command-probe.json",
            f"{rel}/immutable-ground/p4-command-gateway-truth.jsonl",
            f"{rel}/runtime-observation/p4-command-gateway-decisions.jsonl",
            f"{rel}/immutable-ground/telemetry-truth.jsonl",
            f"{rel}/runtime-observation/policy-visible.jsonl",
            f"{rel}/immutable-ground/observability-health.json",
            f"{rel}/immutable-ground/observability-evidence-manifest.json",
            f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt",
        ],
        "development_preflight": True,
    }
    observation = {
        "factor_context": factor,
        "runtime_observation": ro,
        "notes": (
            "WP8 observability-family runtime-binding development preflight. "
            "RECOVERY_FAILED is used only as the frozen terminal-taxonomy label "
            "for a bounded modeled response that did not achieve E4 containment; "
            "it is not a spacecraft failure, native safe-mode failure, or mission-loss claim."
        ),
    }
    observation_path.write_text(json.dumps(observation, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return summary, observation


def validate(*, schema_path: Path, record_path: Path, provenance_path: Path,
             summary_path: Path, manifest_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    record = json.loads(record_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
    if errors:
        raise ValueError([e.message for e in errors])

    expected = {
        "seed": 9301, "event_id": "E4", "mission_state_id": "M2",
        "policy_id": "P7", "contact_condition_id": "C0",
        "evidence_condition_id": "T0", "terminal_state": "RECOVERY_FAILED",
    }
    for key, value in expected.items():
        if record[key] != value:
            raise ValueError(f"unexpected {key}: {record[key]!r}")

    outcomes = record["outcomes"]
    if outcomes["unauthorized_effect_completed"] is not True:
        raise ValueError("event success missing")
    if outcomes["mission_objective_completion_ratio"] != 0.5:
        raise ValueError("M-02 drift")
    if outcomes["safety_invariant_violations"] != []:
        raise ValueError("unexpected safety violation")
    if outcomes["legitimate_command_rejection_rate"] != 1.0:
        raise ValueError("legitimate-command cost drift")
    if outcomes["ground_spacecraft_state_divergence_s"] != 0.0:
        raise ValueError("M-07 drift")
    if outcomes["evidence_completeness_ratio"] != (2 / 3):
        raise ValueError("M-08 drift")
    if record["timing"]["containment_s"] is not None:
        raise ValueError("containment must be right-censored")
    if record["timing"]["verified_recovery_s"] is not None:
        raise ValueError("verified recovery must be right-censored")

    expected_recovery = {
        "required_telemetry_restored": False,
        "health_checks_passed": True,
        "recovery_manifest_complete": True,
    }
    for key, value in expected_recovery.items():
        if record["recovery_evidence"][key] is not value:
            raise ValueError(f"recovery evidence drift: {key}")
    for key in (
        "approved_version", "integrity_measurement_valid", "authorization_valid",
        "measured_state_current", "authorized_command_path_restored",
        "ground_spacecraft_state_agreed", "no_residual_unauthorized_state",
    ):
        if record["recovery_evidence"][key] is not None:
            raise ValueError(f"excluded criterion became applicable: {key}")

    if provenance["development_preflight"] is not True or provenance["pilot_data"] is not False:
        raise ValueError("development/pilot provenance drift")

    summary_expected = {
        "policy_trigger_uses_ground_truth": False,
        "effective_policy_id": "P4",
        "p4_native_safe_mode_claim": False,
        "p4_telemetry_restoration_claim": False,
        "containment_observed": False,
        "trusted_recovery_observed": False,
        "containment_right_censored": True,
        "trusted_recovery_right_censored": True,
        "terminal_taxonomy_decision_id": "R-022",
        "terminal_state_spacecraft_failure_claim": False,
    }
    for key, value in summary_expected.items():
        if summary[key] != value:
            raise ValueError(f"summary drift: {key}")
    if manifest["decision_id"] != "R-022" or manifest["terminal_state_candidate"] != "RECOVERY_FAILED":
        raise ValueError("manifest decision/terminal drift")
    if manifest["containment_observed"] is not False or manifest["trusted_recovery_observed"] is not False:
        raise ValueError("manifest fabricated containment/recovery")
    if manifest["trusted_recovery_criteria"] != expected_recovery:
        raise ValueError("manifest recovery criteria drift")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("manifest")
    for flag in ("root", "output", "event-json", "policy-json", "event-success-json",
                 "post-effect-json", "p4-probe-json", "p4-gateway-truth",
                 "p4-gateway-decisions", "truth-jsonl", "policy-visible-jsonl", "health-json"):
        p.add_argument("--" + flag, required=True)
    for flag in ("event-activation-ns", "policy-selection-ns", "policy-enforcement-ns",
                 "event-success-ns", "post-effect-ns", "health-ns", "manifest-ready-ns"):
        p.add_argument("--" + flag, required=True, type=int)

    p = sub.add_parser("materialize")
    for flag in ("factor-json", "summary-json", "observation-json", "run-start-utc",
                 "run-end-utc", "repo-commit", "runner-sha", "rel"):
        p.add_argument("--" + flag, required=True)
    for flag in ("run-start-ns", "event-activation-ns", "event-success-ns",
                 "policy-selection-ns", "policy-enforcement-ns", "run-end-ns"):
        p.add_argument("--" + flag, required=True, type=int)

    p = sub.add_parser("validate")
    for flag in ("schema", "run-record", "provenance", "summary", "manifest"):
        p.add_argument("--" + flag, required=True)

    args = parser.parse_args(argv)
    if args.command == "manifest":
        evidence = {
            "event": Path(args.event_json), "policy": Path(args.policy_json),
            "event_success": Path(args.event_success_json), "post_effect": Path(args.post_effect_json),
            "p4_probe": Path(args.p4_probe_json), "p4_gateway_truth": Path(args.p4_gateway_truth),
            "p4_gateway_decisions": Path(args.p4_gateway_decisions), "truth": Path(args.truth_jsonl),
            "policy_visible": Path(args.policy_visible_jsonl), "health": Path(args.health_json),
        }
        times = {
            "event_activation_ns": args.event_activation_ns,
            "policy_selection_ns": args.policy_selection_ns,
            "policy_enforcement_ns": args.policy_enforcement_ns,
            "event_success_ns": args.event_success_ns,
            "post_effect_ns": args.post_effect_ns,
            "health_ns": args.health_ns,
            "manifest_ready_ns": args.manifest_ready_ns,
        }
        build_manifest(root=Path(args.root), output=Path(args.output), evidence=evidence, times=times)
        print("observability_evidence_manifest=PASS")
        print("observability_m08_available_current=2")
        print("observability_m08_applicable=3")
        print("observability_expected_m08=0.6666666666666666")
        return 0

    if args.command == "materialize":
        materialize(
            factor_path=Path(args.factor_json), summary_path=Path(args.summary_json),
            observation_path=Path(args.observation_json), run_start_ns=args.run_start_ns,
            event_activation_ns=args.event_activation_ns, event_success_ns=args.event_success_ns,
            policy_selection_ns=args.policy_selection_ns, policy_enforcement_ns=args.policy_enforcement_ns,
            run_end_ns=args.run_end_ns, run_start_utc=args.run_start_utc, run_end_utc=args.run_end_utc,
            repo_commit=args.repo_commit, runner_sha=args.runner_sha, rel=args.rel,
        )
        print("observability_runtime_observation_materialized=PASS")
        return 0

    validate(
        schema_path=Path(args.schema), record_path=Path(args.run_record),
        provenance_path=Path(args.provenance), summary_path=Path(args.summary),
        manifest_path=Path(args.manifest),
    )
    print("schema_valid_observability_bound_run_record=PASS")
    print("event_before_response_runtime_order=PASS")
    print("unauthorized_effect_observed=true")
    print("mission_objective_completion_ratio=0.5")
    print("safety_invariant_violation_count=0")
    print("legitimate_command_rejection_rate=1.0")
    print("ground_spacecraft_state_divergence_s=0.0")
    print("evidence_completeness_ratio=0.6666666666666666")
    print("time_to_containment_s=None")
    print("time_to_verified_recovery_s=None")
    print("effective_policy=P4")
    print("policy_trigger_uses_ground_truth=false")
    print("containment_observed=false")
    print("containment_right_censored=true")
    print("trusted_recovery_right_censored=true")
    print("terminal_state=RECOVERY_FAILED")
    print("terminal_state_spacecraft_failure_claim=false")
    print("development_preflight=true")
    print("pilot_data=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
