from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "configs" / "wp9b2_e4_fixed_runtime_gate.json"
CASES_PATH = ROOT / "configs" / "wp9b2_development_cases.json"
CAMPAIGN_PATH = ROOT / "configs" / "wp9_campaign_design.json"

DECISION_ID = "R-049"
CASE_IDS = ("D09", "D10")
EXPECTED = {
    "D09": {
        "campaign_cell_id": "A22",
        "development_seed": 9609,
        "policy_id": "P0",
        "effective_policy_id": "P0",
        "selected_action": "OBSERVE_ONLY",
    },
    "D10": {
        "campaign_cell_id": "A23",
        "development_seed": 9610,
        "policy_id": "P4",
        "effective_policy_id": "P4",
        "selected_action": "ENTER_SAFE_MODE",
    },
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate {key}")
    return result


def validate_gate() -> None:
    gate = _load(GATE_PATH)
    cases = _load(CASES_PATH)
    campaign = _load(CAMPAIGN_PATH)

    if gate["decision_id"] != DECISION_ID:
        raise ValueError("fixed-E4 gate decision changed")
    if gate["status"] != "WP9B2_E4_FIXED_DEVELOPMENT_GATE_READY_D09_D10_ONLY":
        raise ValueError("fixed-E4 gate status changed")

    boundary = gate["scientific_boundary"]
    required_true = (
        "development_only",
        "single_case_per_invocation",
    )
    for key in required_true:
        if boundary[key] is not True:
            raise ValueError(f"scientific boundary changed: {key}")
    required_false = (
        "automatic_next_case",
        "campaign_seed_consumed",
        "campaign_data",
        "final_campaign_execution_authorized",
        "ground_truth_policy_oracle_allowed",
        "p4_native_safe_mode_claim",
        "p4_telemetry_restoration_claim",
        "spacecraft_failure_claim",
        "rf_interference",
        "live_spacecraft_access",
    )
    for key in required_false:
        if boundary[key] is not False:
            raise ValueError(f"scientific boundary changed: {key}")

    measurement = gate["measurement_contract"]
    if measurement["high_value_mid"] != "0x08E9":
        raise ValueError("E4 high-value MID changed")
    if int(measurement["visibility_deadline_s"]) != 3:
        raise ValueError("E4 visibility deadline changed")
    for name in ("event_success", "matched_post_response_probe"):
        row = measurement[name]
        if int(row["immutable_truth_high_value_delta"]) != 1:
            raise ValueError(f"{name} immutable-truth delta changed")
        if int(row["policy_visible_high_value_delta"]) != 0:
            raise ValueError(f"{name} policy-visible delta changed")

    registry = _by_id(cases["cases"], "case_id")
    campaign_cells = _by_id(campaign["cells"], "cell_id")
    if set(gate["cases"]) != set(CASE_IDS):
        raise ValueError("fixed-E4 gate must contain exactly D09/D10")

    for case_id in CASE_IDS:
        exp = EXPECTED[case_id]
        registered = registry[case_id]
        if registered["campaign_cell_id"] != exp["campaign_cell_id"]:
            raise ValueError(f"{case_id}: R-046 campaign-cell identity changed")
        if int(registered["development_seed"]) != exp["development_seed"]:
            raise ValueError(f"{case_id}: development seed changed")
        if registered["runtime_family"] != "observability":
            raise ValueError(f"{case_id}: runtime family changed")
        if registered["runtime_variant"] != "e4_fixed_policy":
            raise ValueError(f"{case_id}: runtime variant changed")

        cell = campaign_cells[exp["campaign_cell_id"]]
        expected_factors = {
            "event_id": "E4",
            "mission_state_id": "M2",
            "contact_condition_id": "C0",
            "evidence_condition_id": "T0",
            "policy_id": exp["policy_id"],
            "expected_effective_policy_id": exp["effective_policy_id"],
        }
        for key, value in expected_factors.items():
            if cell[key] != value:
                raise ValueError(f"{case_id}: campaign factor changed: {key}")

        gate_case = gate["cases"][case_id]
        for key, value in {
            "campaign_cell_id": exp["campaign_cell_id"],
            "development_seed": exp["development_seed"],
            **expected_factors,
        }.items():
            if gate_case[key] != value:
                raise ValueError(f"{case_id}: gate factor changed: {key}")
        if gate_case["selected_action"] != exp["selected_action"]:
            raise ValueError(f"{case_id}: selected action changed")

        event = materialize_event(
            "E4",
            mission_state="M2",
            contact_condition="C0",
            evidence_condition="T0",
            seed=exp["development_seed"],
        )
        visible = event["policy_visible_evidence"]
        if event["ground_truth"]["telemetry_truth_available"] is not True:
            raise ValueError("E4 immutable telemetry truth changed")
        expected_visible = {
            "telemetry_stream_present": True,
            "high_value_channels_complete": False,
            "evidence_fresh": False,
            "state_estimate_complete": False,
        }
        if visible != expected_visible:
            raise ValueError("E4 degraded policy-visible evidence changed")

        decision = evaluate_policy(exp["policy_id"], event)
        if decision["requested_policy_id"] != exp["policy_id"]:
            raise ValueError(f"{case_id}: requested policy changed")
        if decision["delegated_policy_id"] != exp["effective_policy_id"]:
            raise ValueError(f"{case_id}: effective policy changed")
        if decision["selected_action"] != exp["selected_action"]:
            raise ValueError(f"{case_id}: action changed")
        if decision["oracle_ground_truth_read"] is not False:
            raise ValueError(f"{case_id}: policy crossed oracle boundary")


def build_plan(
    *,
    case_id: str,
    run_id: str,
    repo_commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_gate()
    if case_id not in CASE_IDS:
        raise ValueError("fixed-E4 plan supports D09/D10 only")

    exp = EXPECTED[case_id]
    event = materialize_event(
        "E4",
        mission_state="M2",
        contact_condition="C0",
        evidence_condition="T0",
        seed=exp["development_seed"],
    )
    plan = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E4_FIXED_DEVELOPMENT_PLAN",
        "run_id": run_id,
        "repo_commit": repo_commit,
        "case_id": case_id,
        "campaign_cell_id": exp["campaign_cell_id"],
        "development_seed": exp["development_seed"],
        "event_id": "E4",
        "mission_state_id": "M2",
        "contact_condition_id": "C0",
        "evidence_condition_id": "T0",
        "requested_policy_id": exp["policy_id"],
        "expected_effective_policy_id_for_acceptance_only": exp[
            "effective_policy_id"
        ],
        "expected_selected_action_for_acceptance_only": exp[
            "selected_action"
        ],
        "event_instance_sha256": event["instance_sha256"],
        "high_value_mid": "0x08E9",
        "visibility_deadline_s": 3,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "automatic_next_case": False,
        "expected_values_used_as_measurements": False,
        "ground_truth_policy_oracle_allowed": False,
    }
    return plan, event


def observe_policy(
    *,
    plan: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    validate_gate()
    case_id = plan["case_id"]
    exp = EXPECTED[case_id]
    if event["instance_sha256"] != plan["event_instance_sha256"]:
        raise ValueError("event identity differs from plan")

    decision = evaluate_policy(exp["policy_id"], event)
    if decision["delegated_policy_id"] != exp["effective_policy_id"]:
        raise ValueError("fixed-E4 effective policy differs from frozen design")
    if decision["selected_action"] != exp["selected_action"]:
        raise ValueError("fixed-E4 selected action differs from frozen design")
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("fixed-E4 policy read immutable ground truth")
    return decision


def _delta(after: int, before: int, label: str) -> int:
    value = int(after) - int(before)
    if value < 0:
        raise ValueError(f"negative counter delta: {label}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def finalize(
    *,
    plan: dict[str, Any],
    policy: dict[str, Any],
    event_truth_before: int,
    event_truth_after: int,
    event_visible_before: int,
    event_visible_after: int,
    post_truth_before: int,
    post_truth_after: int,
    post_visible_before: int,
    post_visible_after: int,
    gateway_decisions_path: Path | None,
    noop_before: int,
    noop_after: int,
) -> dict[str, Any]:
    validate_gate()
    case_id = plan["case_id"]
    exp = EXPECTED[case_id]

    if policy["requested_policy_id"] != exp["policy_id"]:
        raise ValueError("runtime requested policy changed")
    if policy["delegated_policy_id"] != exp["effective_policy_id"]:
        raise ValueError("runtime effective policy changed")
    if policy["selected_action"] != exp["selected_action"]:
        raise ValueError("runtime selected action changed")
    if policy["oracle_ground_truth_read"] is not False:
        raise ValueError("runtime policy crossed oracle boundary")

    event_truth_delta = _delta(event_truth_after, event_truth_before, "event truth")
    event_visible_delta = _delta(
        event_visible_after, event_visible_before, "event policy-visible"
    )
    post_truth_delta = _delta(post_truth_after, post_truth_before, "post truth")
    post_visible_delta = _delta(
        post_visible_after, post_visible_before, "post policy-visible"
    )

    if (event_truth_delta, event_visible_delta) != (1, 0):
        raise ValueError("E4 event-success observation failed")
    if (post_truth_delta, post_visible_delta) != (1, 0):
        raise ValueError("E4 matched post-response observation failed")

    noop_delta = _delta(noop_after, noop_before, "authorized NOOP")
    gateway_rows: list[dict[str, Any]] = []
    modeled_gate = False
    legitimate_attempted = 0
    legitimate_rejected = 0

    if case_id == "D09":
        if gateway_decisions_path is not None and _read_jsonl(gateway_decisions_path):
            raise ValueError("D09/P0 must not produce P4 gateway decisions")
        if noop_delta != 0:
            raise ValueError("D09 has no command-gateway probe")
    else:
        if gateway_decisions_path is None:
            raise ValueError("D10 requires retained P4 gateway decisions")
        gateway_rows = _read_jsonl(gateway_decisions_path)
        if len(gateway_rows) != 1:
            raise ValueError("D10 requires exactly one P4 gateway decision")
        row = gateway_rows[0]
        expected_gateway = {
            "action": "ENTER_SAFE_MODE",
            "source_id": "authorized_ground",
            "command_class": "sample_noop",
            "forwarded": False,
        }
        for key, value in expected_gateway.items():
            if row[key] != value:
                raise ValueError(f"D10 P4 gateway decision changed: {key}")
        if noop_delta != 0:
            raise ValueError("D10 authorized NOOP unexpectedly reached cFS")
        modeled_gate = True
        legitimate_attempted = 1
        legitimate_rejected = 1

    result = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B2_E4_FIXED_DEVELOPMENT_ACCEPTANCE_PASS",
        "case_id": case_id,
        "campaign_cell_id": plan["campaign_cell_id"],
        "development_seed": plan["development_seed"],
        "requested_policy_id": policy["requested_policy_id"],
        "actual_effective_policy_id": policy["delegated_policy_id"],
        "selected_action": policy["selected_action"],
        "event_success_observed": True,
        "event_truth_high_value_delta": event_truth_delta,
        "event_policy_visible_high_value_delta": event_visible_delta,
        "immutable_ground_truth_separate": True,
        "policy_visible_evidence_degraded": True,
        "post_response_truth_high_value_delta": post_truth_delta,
        "post_response_policy_visible_high_value_delta": post_visible_delta,
        "telemetry_restoration_observed": False,
        "containment_observed": False,
        "modeled_conservative_command_gate_observed": modeled_gate,
        "legitimate_commands_attempted": legitimate_attempted,
        "legitimate_commands_rejected": legitimate_rejected,
        "authorized_noop_marker_delta": noop_delta,
        "p4_native_safe_mode_claim": False,
        "p4_telemetry_restoration_claim": False,
        "spacecraft_failure_claim": False,
        "expected_values_used_as_measurements": False,
        "ground_truth_used_as_policy_oracle": False,
        "development_runtime_data": True,
        "campaign_seed_consumed": False,
        "campaign_data": False,
        "automatic_next_case": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    p = sub.add_parser("plan")
    p.add_argument("--case-id", required=True, choices=CASE_IDS)
    p.add_argument("--run-id", required=True)
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--output-plan-json", required=True)
    p.add_argument("--output-event-json", required=True)

    p = sub.add_parser("observe-policy")
    p.add_argument("--plan-json", required=True)
    p.add_argument("--event-json", required=True)
    p.add_argument("--output-policy-json", required=True)

    p = sub.add_parser("finalize")
    p.add_argument("--plan-json", required=True)
    p.add_argument("--policy-json", required=True)
    p.add_argument("--event-truth-before", required=True, type=int)
    p.add_argument("--event-truth-after", required=True, type=int)
    p.add_argument("--event-visible-before", required=True, type=int)
    p.add_argument("--event-visible-after", required=True, type=int)
    p.add_argument("--post-truth-before", required=True, type=int)
    p.add_argument("--post-truth-after", required=True, type=int)
    p.add_argument("--post-visible-before", required=True, type=int)
    p.add_argument("--post-visible-after", required=True, type=int)
    p.add_argument("--gateway-decisions-jsonl")
    p.add_argument("--noop-before", required=True, type=int)
    p.add_argument("--noop-after", required=True, type=int)
    p.add_argument("--output-summary-json", required=True)

    args = parser.parse_args()
    if args.command == "validate":
        validate_gate()
        print("WP9B2_E4_FIXED_STATIC_GATE=PASS")
        return 0

    if args.command == "plan":
        plan, event = build_plan(
            case_id=args.case_id,
            run_id=args.run_id,
            repo_commit=args.repo_commit,
        )
        _write(Path(args.output_plan_json), plan)
        _write(Path(args.output_event_json), event)
        print("WP9B2_E4_FIXED_DEVELOPMENT_PLAN=PASS")
        print("case_id=" + plan["case_id"])
        print("campaign_cell_id=" + plan["campaign_cell_id"])
        print("development_seed=" + str(plan["development_seed"]))
        return 0

    if args.command == "observe-policy":
        plan = _load(Path(args.plan_json))
        event = _load(Path(args.event_json))
        decision = observe_policy(plan=plan, event=event)
        _write(Path(args.output_policy_json), decision)
        print("WP9B2_E4_FIXED_RUNTIME_POLICY=PASS")
        print("actual_effective_policy_id=" + decision["delegated_policy_id"])
        print("selected_action=" + decision["selected_action"])
        print("policy_trigger_uses_ground_truth=false")
        return 0

    plan = _load(Path(args.plan_json))
    policy = _load(Path(args.policy_json))
    summary = finalize(
        plan=plan,
        policy=policy,
        event_truth_before=args.event_truth_before,
        event_truth_after=args.event_truth_after,
        event_visible_before=args.event_visible_before,
        event_visible_after=args.event_visible_after,
        post_truth_before=args.post_truth_before,
        post_truth_after=args.post_truth_after,
        post_visible_before=args.post_visible_before,
        post_visible_after=args.post_visible_after,
        gateway_decisions_path=(
            Path(args.gateway_decisions_jsonl)
            if args.gateway_decisions_jsonl
            else None
        ),
        noop_before=args.noop_before,
        noop_after=args.noop_after,
    )
    _write(Path(args.output_summary_json), summary)
    print("WP9B2_E4_FIXED_ACCEPTANCE=PASS")
    print("case_id=" + summary["case_id"])
    print("immutable_ground_truth_separate=true")
    print("policy_visible_evidence_degraded=true")
    print("telemetry_restoration_observed=false")
    print("containment_observed=false")
    print(
        "modeled_conservative_command_gate_observed="
        + str(summary["modeled_conservative_command_gate_observed"]).lower()
    )
    print("p4_native_safe_mode_claim=false")
    print("p4_telemetry_restoration_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
