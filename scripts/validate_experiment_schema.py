#!/usr/bin/env python3
"""Validate experiment schema fixtures, model alignment, and WP8 pilot design."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Run: python3 -m pip install -r requirements-dev.txt"
    ) from exc

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.primary_metrics import score_raw_metric_evidence

SCHEMA_PATH = PROJECT_ROOT / "configs" / "experiment_run.schema.json"
MODEL_PATH = PROJECT_ROOT / "configs" / "experiment_model.json"
PILOT_PATH = PROJECT_ROOT / "configs" / "wp8_pilot_design.json"
VALID_PATH = PROJECT_ROOT / "configs" / "examples" / "valid_run.json"
INVALID_PATH = PROJECT_ROOT / "configs" / "examples" / "invalid_trusted_recovery.json"

def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unable to load {path}: {exc}") from exc

def format_errors(errors: list) -> str:
    lines: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        lines.append(f"- {location}: {error.message}")
    return "\n".join(lines)

def assert_model_schema_alignment(schema: dict, model: dict) -> None:
    expected = {
        "mission_state_id": {row["id"] for row in model["mission_states"]},
        "event_id": {row["id"] for row in model["events"]},
        "policy_id": {row["id"] for row in model["response_policies"]},
        "contact_condition_id": {row["id"] for row in model["contact_conditions"]},
        "evidence_condition_id": {row["id"] for row in model["evidence_conditions"]},
    }
    for field, ids in expected.items():
        actual = set(schema["properties"][field]["enum"])
        if actual != ids:
            raise SystemExit(
                f"{field} enum mismatch: schema={sorted(actual)} model={sorted(ids)}"
            )

def assert_pilot_design(pilot: dict, model: dict) -> None:
    if pilot["model_version"] != model["model_version"]:
        raise SystemExit("WP8 pilot model_version does not match model")

    cells = pilot["cells"]
    ids = [cell["cell_id"] for cell in cells]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate WP8 pilot cell_id")

    stage1 = pilot["stage_1_control_validity"]
    stage2 = pilot["stage_2_variability"]
    if set(stage1["cell_ids"]) != set(ids):
        raise SystemExit("Stage-1 cells do not equal declared WP8 cells")

    anchors = set(stage2["anchor_cell_ids"])
    if not anchors.issubset(set(ids)):
        raise SystemExit("Stage-2 anchor is not a declared WP8 cell")

    if stage2["total_valid_repetitions_per_anchor_after_stage_2"] != (
        1 + len(stage2["additional_seeds"])
    ):
        raise SystemExit("Stage-2 repetition count is inconsistent")

    model_events = {row["id"] for row in model["events"]}
    model_states = {row["id"] for row in model["mission_states"]}
    model_policies = {row["id"] for row in model["response_policies"]}
    model_contacts = {row["id"] for row in model["contact_conditions"]}
    model_evidence = {row["id"] for row in model["evidence_conditions"]}
    seed = int(stage1["seed"])

    for cell in cells:
        if cell["event_id"] not in model_events:
            raise SystemExit(f"{cell['cell_id']}: unknown event")
        if cell["mission_state_id"] not in model_states:
            raise SystemExit(f"{cell['cell_id']}: unknown mission state")
        if cell["policy_id"] not in model_policies:
            raise SystemExit(f"{cell['cell_id']}: unknown policy")
        if cell["contact_condition_id"] not in model_contacts:
            raise SystemExit(f"{cell['cell_id']}: unknown contact")
        if cell["evidence_condition_id"] not in model_evidence:
            raise SystemExit(f"{cell['cell_id']}: unknown evidence condition")

        event = materialize_event(
            cell["event_id"],
            mission_state=cell["mission_state_id"],
            contact_condition=cell["contact_condition_id"],
            evidence_condition=cell["evidence_condition_id"],
            seed=seed,
        )
        decision = evaluate_policy(cell["policy_id"], event)
        if decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
            raise SystemExit(
                f"{cell['cell_id']}: expected effective policy "
                f"{cell['expected_effective_policy_id']} but policy engine "
                f"returned {decision['delegated_policy_id']}"
            )

    included = set(pilot["pilot_event_subset"]["included"])
    omitted = set(pilot["pilot_event_subset"]["omitted_but_retained_for_wp9"])
    if included != {"E1", "E3", "E4"} or omitted != {"E2"}:
        raise SystemExit("WP8 event subset does not match the frozen pilot design")

    if pilot["instrumentation_gate"]["pilot_execution_authorized"] is not False:
        raise SystemExit(
            "WP8 pilot execution must remain unauthorized until instrumentation passes"
        )

def main() -> int:
    schema = load_json(SCHEMA_PATH)
    model = load_json(MODEL_PATH)
    pilot = load_json(PILOT_PATH)
    valid_fixture = load_json(VALID_PATH)
    invalid_fixture = load_json(INVALID_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    valid_errors = sorted(
        validator.iter_errors(valid_fixture),
        key=lambda err: list(err.path),
    )
    if valid_errors:
        print("[FAIL] Positive fixture did not validate:")
        print(format_errors(valid_errors))
        return 1
    print("[OK] Positive fixture validates")

    minimal_invalid = {
        key: valid_fixture[key]
        for key in (
            "run_id",
            "model_version",
            "seed",
            "mission_state_id",
            "event_id",
            "policy_id",
            "contact_condition_id",
            "evidence_condition_id",
            "environment",
        )
    }
    minimal_invalid["run_id"] = "schema-valid-run-invalid"
    minimal_invalid["terminal_state"] = "RUN_INVALID"
    minimal_invalid["invalid_run_reason"] = "evidence_capture_failure"

    minimal_invalid_errors = sorted(
        validator.iter_errors(minimal_invalid),
        key=lambda err: list(err.path),
    )
    if minimal_invalid_errors:
        print("[FAIL] Minimal RUN_INVALID record did not validate:")
        print(format_errors(minimal_invalid_errors))
        return 1
    print("[OK] RUN_INVALID record validates without fabricated metrics")

    invalid_errors = sorted(
        validator.iter_errors(invalid_fixture),
        key=lambda err: list(err.path),
    )
    if not invalid_errors:
        print("[FAIL] Negative fixture unexpectedly validated")
        return 1

    expected_guardrail = any(
        "measured_state_current"
        in ".".join(str(part) for part in error.absolute_path)
        or "True was expected" in error.message
        for error in invalid_errors
    )
    if not expected_guardrail:
        print(
            "[FAIL] Negative fixture failed, but not on the "
            "trusted-recovery freshness guardrail:"
        )
        print(format_errors(invalid_errors))
        return 1

    unexpected_invalid_errors = [
        error
        for error in invalid_errors
        if list(error.absolute_path)
        != ["recovery_evidence", "measured_state_current"]
    ]
    if unexpected_invalid_errors:
        print(
            "[FAIL] Negative fixture has failures beyond the intended "
            "measured-state freshness guardrail:"
        )
        print(format_errors(unexpected_invalid_errors))
        return 1

    try:
        score_raw_metric_evidence(
            event_activation_s=invalid_fixture["timing"][
                "event_activation_s"
            ],
            raw=invalid_fixture["raw_metric_evidence"],
            recovery_evidence=invalid_fixture["recovery_evidence"],
        )
    except ValueError as exc:
        if "incomplete recovery evidence" not in str(exc):
            print(
                "[FAIL] Negative fixture scorer rejected for an "
                f"unexpected reason: {exc}"
            )
            return 1
    else:
        print(
            "[FAIL] Negative trusted-recovery fixture unexpectedly "
            "passed raw metric scoring"
        )
        return 1

    print(
        "[OK] Negative trusted-recovery fixture rejected only on "
        "the intended freshness fault"
    )

    try:
        scored = score_raw_metric_evidence(
            event_activation_s=valid_fixture["timing"]["event_activation_s"],
            raw=valid_fixture["raw_metric_evidence"],
            recovery_evidence=valid_fixture["recovery_evidence"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] Positive fixture raw metric scoring failed: {exc}")
        return 1

    expected_pairs = {
        "unauthorized_effect_completed": valid_fixture["outcomes"][
            "unauthorized_effect_completed"
        ],
        "mission_objective_completion_ratio": valid_fixture["outcomes"][
            "mission_objective_completion_ratio"
        ],
        "safety_invariant_violations": valid_fixture["outcomes"][
            "safety_invariant_violations"
        ],
        "legitimate_command_rejection_rate": valid_fixture["outcomes"][
            "legitimate_command_rejection_rate"
        ],
        "ground_spacecraft_state_divergence_s": valid_fixture["outcomes"][
            "ground_spacecraft_state_divergence_s"
        ],
        "evidence_completeness_ratio": valid_fixture["outcomes"][
            "evidence_completeness_ratio"
        ],
        "time_to_containment_s": valid_fixture["timing"]["containment_s"],
        "time_to_verified_recovery_s": valid_fixture["timing"][
            "verified_recovery_s"
        ],
        "recovery_terminal_state": valid_fixture["terminal_state"],
    }

    for key, expected in expected_pairs.items():
        if scored[key] != expected:
            print(
                f"[FAIL] Positive fixture metric mismatch for {key}: "
                f"derived={scored[key]!r} fixture={expected!r}"
            )
            return 1

    print("[OK] Positive fixture metrics derive from raw evidence")

    try:
        assert_model_schema_alignment(schema, model)
        assert_pilot_design(pilot, model)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] Model/pilot validation error: {exc}")
        return 1

    print("[OK] Experiment schema factor enums align with experiment model")
    print("[OK] WP8 pilot cells match current policy semantics")
    print("[OK] WP8 pilot execution remains gated on runtime metric binding")
    print("[OK] Primary metrics derive from retained raw evidence")
    print("[OK] JSON Schema Draft 2020-12 structure is valid")
    print("SCHEMA_VALIDATION_STATUS=PASS")
    print("WP8_PILOT_CONTRACT_STATUS=PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
