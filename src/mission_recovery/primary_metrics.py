from __future__ import annotations

from copy import deepcopy
from typing import Any

RECOVERY_CRITERIA = (
    "approved_version",
    "integrity_measurement_valid",
    "authorization_valid",
    "measured_state_current",
    "authorized_command_path_restored",
    "ground_spacecraft_state_agreed",
    "required_telemetry_restored",
    "health_checks_passed",
    "no_residual_unauthorized_state",
    "recovery_manifest_complete",
)

TERMINAL_PRECEDENCE = (
    ("run_invalid", "RUN_INVALID"),
    ("mission_loss", "MISSION_LOSS"),
    ("trusted_recovery_confirmed", "TRUSTED_RECOVERY_CONFIRMED"),
    ("operational_restored", "OPERATIONAL_BUT_UNVERIFIED"),
    ("recovery_failed", "RECOVERY_FAILED"),
    ("contained", "CONTAINED_NOT_RECOVERED"),
)


def _bounded_timestamp(
    evidence: dict[str, Any],
    *,
    label: str,
    event_activation_s: float,
    run_end_s: float,
) -> float | None:
    predicate = evidence["predicate"]
    timestamp = evidence["timestamp_s"]

    if predicate:
        if timestamp is None:
            raise ValueError(f"{label} predicate true without timestamp")
        value = float(timestamp)
        if value < event_activation_s or value > run_end_s:
            raise ValueError(
                f"{label} timestamp before event activation or after run end"
            )
        return value

    if timestamp is not None:
        raise ValueError(f"{label} predicate false with timestamp")
    return None


def _union_duration(
    intervals: list[dict[str, Any]],
    *,
    run_end_s: float,
) -> float:
    spans: list[tuple[float, float]] = []

    for row in intervals:
        start = float(row["start_s"])
        end = float(row["end_s"])

        if start < 0 or end < start or end > run_end_s:
            raise ValueError("divergence interval outside run bounds")

        spans.append((start, end))

    if not spans:
        return 0.0

    spans.sort()
    merged_start, merged_end = spans[0]
    total = 0.0

    for start, end in spans[1:]:
        if start <= merged_end:
            merged_end = max(merged_end, end)
            continue

        total += merged_end - merged_start
        merged_start, merged_end = start, end

    total += merged_end - merged_start
    return total


def classify_terminal_state(
    predicates: dict[str, bool],
) -> str:
    for key, terminal_state in TERMINAL_PRECEDENCE:
        if predicates[key]:
            return terminal_state
    raise ValueError("no terminal-state predicate is true")


def score_raw_metric_evidence(
    *,
    event_activation_s: float,
    raw: dict[str, Any],
    recovery_evidence: dict[str, bool | None],
) -> dict[str, Any]:
    event_activation_s = float(event_activation_s)
    run_end_s = float(raw["run_end_s"])
    if event_activation_s < 0:
        raise ValueError("event_activation_s must be non-negative")
    if run_end_s <= event_activation_s:
        raise ValueError("run_end_s must be after event activation")

    event_success_s = _bounded_timestamp(
        raw["event_success"],
        label="event_success",
        event_activation_s=event_activation_s,
        run_end_s=run_end_s,
    )
    containment_s = _bounded_timestamp(
        raw["containment"],
        label="containment",
        event_activation_s=event_activation_s,
        run_end_s=run_end_s,
    )
    trusted_recovery_s = _bounded_timestamp(
        raw["trusted_recovery"],
        label="trusted_recovery",
        event_activation_s=event_activation_s,
        run_end_s=run_end_s,
    )

    objectives = raw["objective_instances"]
    if not objectives:
        raise ValueError("at least one mission objective instance is required")

    objective_ids = [row["objective_instance_id"] for row in objectives]
    if len(objective_ids) != len(set(objective_ids)):
        raise ValueError("duplicate mission objective instance id")

    total_weight = 0.0
    completed_weight = 0.0
    for row in objectives:
        weight = float(row["weight"])
        start = float(row["scheduled_start_s"])
        end = float(row["scheduled_end_s"])
        predicate = row["completion_predicate"]
        evidence_ref = row["completion_evidence_ref"]
        if weight <= 0:
            raise ValueError("mission objective weight must be positive")
        if start < 0 or end < start or end > run_end_s:
            raise ValueError("mission objective schedule outside run bounds")
        if not predicate or not evidence_ref:
            raise ValueError("mission objective predicate/evidence reference required")
        total_weight += weight
        if row["completed"]:
            completed_weight += weight

    mission_ratio = completed_weight / total_weight

    violations = raw["invariant_violation_intervals"]
    invariant_ids: set[str] = set()
    for row in violations:
        start = float(row["start_s"])
        end = row["end_s"]

        if start < 0 or start > run_end_s:
            raise ValueError("invariant interval start outside run bounds")
        if end is not None:
            end_value = float(end)
            if end_value < start or end_value > run_end_s:
                raise ValueError("invariant interval end outside run bounds")

        if not row["ground_truth_evidence_ref"]:
            raise ValueError("invariant violation requires ground-truth evidence reference")
        invariant_ids.add(row["invariant_id"])

    commands = raw["legitimate_commands"]
    attempted = int(commands["attempted"])
    rejected = int(commands["rejected"])
    if attempted < 0 or rejected < 0 or rejected > attempted:
        raise ValueError("invalid legitimate-command counts")

    rejection_rate = None if attempted == 0 else rejected / attempted

    divergence_s = _union_duration(
        raw["ground_spacecraft_divergence_intervals"],
        run_end_s=run_end_s,
    )

    checklist = raw["recovery_checklist"]
    excluded = raw["recovery_checklist_excluded"]
    if not checklist:
        raise ValueError("recovery checklist denominator is zero")

    criterion_ids = [row["criterion_id"] for row in checklist]
    if len(criterion_ids) != len(set(criterion_ids)):
        raise ValueError("duplicate recovery checklist criterion")
    if len(excluded) != len(set(excluded)):
        raise ValueError("duplicate excluded recovery criterion")

    applicable = set(criterion_ids)
    excluded_set = set(excluded)
    unknown = (applicable | excluded_set) - set(RECOVERY_CRITERIA)
    if unknown:
        raise ValueError(f"unknown recovery criterion: {sorted(unknown)}")
    if applicable & excluded_set:
        raise ValueError("recovery criterion cannot be both applicable and excluded")
    if applicable | excluded_set != set(RECOVERY_CRITERIA):
        raise ValueError("recovery checklist/exclusions must partition all criteria")

    for row in checklist:
        criterion = row["criterion_id"]
        value = recovery_evidence[criterion]
        if value is None or bool(value) != bool(row["available_current"]):
            raise ValueError(
                f"recovery evidence disagrees with raw checklist: {criterion}"
            )
        if not row["evidence_ref"]:
            raise ValueError("applicable recovery criterion requires evidence reference")

    for criterion in excluded_set:
        if recovery_evidence[criterion] is not None:
            raise ValueError(
                f"excluded recovery criterion must be null: {criterion}"
            )

    evidence_ratio = (
        sum(bool(row["available_current"]) for row in checklist)
        / len(checklist)
    )

    terminal_state = classify_terminal_state(
        raw["terminal_state_predicates"],
    )

    trusted_predicate = bool(raw["trusted_recovery"]["predicate"])
    terminal_trusted = terminal_state == "TRUSTED_RECOVERY_CONFIRMED"

    if terminal_trusted:
        if not trusted_predicate or trusted_recovery_s is None:
            raise ValueError(
                "trusted terminal state lacks trusted-recovery timestamp"
            )

        if not all(bool(row["available_current"]) for row in checklist):
            raise ValueError(
                "trusted terminal state has incomplete recovery evidence"
            )

    if bool(
        raw["terminal_state_predicates"]["trusted_recovery_confirmed"]
    ) != trusted_predicate:
        raise ValueError(
            "trusted-recovery predicate disagrees with terminal predicate"
        )

    return {
        "event_success_timestamp_s": event_success_s,
        "time_to_containment_s": (
            None
            if containment_s is None
            else containment_s - event_activation_s
        ),
        "time_to_verified_recovery_s": (
            None
            if trusted_recovery_s is None
            else trusted_recovery_s - event_activation_s
        ),
        "unauthorized_effect_completed": bool(
            raw["event_success"]["predicate"]
        ),
        "mission_objective_completion_ratio": mission_ratio,
        "safety_invariant_violations": sorted(invariant_ids),
        "safety_invariant_violation_count": len(invariant_ids),
        "legitimate_command_rejection_rate": rejection_rate,
        "ground_spacecraft_state_divergence_s": divergence_s,
        "evidence_completeness_ratio": evidence_ratio,
        "recovery_terminal_state": terminal_state,
        "run_end_censoring_s": run_end_s - event_activation_s,
    }


def build_run_record(
    *,
    run_id: str,
    model_version: str,
    seed: int,
    mission_state_id: str,
    event_id: str,
    policy_id: str,
    contact_condition_id: str,
    evidence_condition_id: str,
    environment: dict[str, Any],
    run_start_utc: str,
    event_activation_s: float,
    run_end_utc: str,
    raw_metric_evidence: dict[str, Any],
    recovery_evidence: dict[str, bool | None],
    invalid_run_reason: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    scored = score_raw_metric_evidence(
        event_activation_s=event_activation_s,
        raw=raw_metric_evidence,
        recovery_evidence=recovery_evidence,
    )

    terminal_state = scored["recovery_terminal_state"]
    if terminal_state == "RUN_INVALID":
        if not invalid_run_reason:
            raise ValueError("RUN_INVALID requires invalid_run_reason")
    elif invalid_run_reason is not None:
        raise ValueError(
            "invalid_run_reason is only allowed for RUN_INVALID"
        )

    return {
        "run_id": run_id,
        "model_version": model_version,
        "seed": int(seed),
        "mission_state_id": mission_state_id,
        "event_id": event_id,
        "policy_id": policy_id,
        "contact_condition_id": contact_condition_id,
        "evidence_condition_id": evidence_condition_id,
        "environment": deepcopy(environment),
        "timing": {
            "run_start_utc": run_start_utc,
            "event_activation_s": float(event_activation_s),
            "containment_s": scored["time_to_containment_s"],
            "verified_recovery_s": scored[
                "time_to_verified_recovery_s"
            ],
            "run_end_utc": run_end_utc,
        },
        "outcomes": {
            "unauthorized_effect_completed": scored[
                "unauthorized_effect_completed"
            ],
            "mission_objective_completion_ratio": scored[
                "mission_objective_completion_ratio"
            ],
            "safety_invariant_violations": scored[
                "safety_invariant_violations"
            ],
            "legitimate_command_rejection_rate": scored[
                "legitimate_command_rejection_rate"
            ],
            "ground_spacecraft_state_divergence_s": scored[
                "ground_spacecraft_state_divergence_s"
            ],
            "evidence_completeness_ratio": scored[
                "evidence_completeness_ratio"
            ],
        },
        "recovery_evidence": deepcopy(recovery_evidence),
        "raw_metric_evidence": deepcopy(raw_metric_evidence),
        "terminal_state": terminal_state,
        "invalid_run_reason": invalid_run_reason,
        "notes": notes,
    }

def build_invalid_run_record(
    *,
    run_id: str,
    model_version: str,
    seed: int,
    mission_state_id: str,
    event_id: str,
    policy_id: str,
    contact_condition_id: str,
    evidence_condition_id: str,
    environment: dict[str, Any],
    invalid_run_reason: str,
    notes: str | None = None,
) -> dict[str, Any]:
    if not invalid_run_reason:
        raise ValueError("RUN_INVALID requires invalid_run_reason")

    return {
        "run_id": run_id,
        "model_version": model_version,
        "seed": int(seed),
        "mission_state_id": mission_state_id,
        "event_id": event_id,
        "policy_id": policy_id,
        "contact_condition_id": contact_condition_id,
        "evidence_condition_id": evidence_condition_id,
        "environment": deepcopy(environment),
        "terminal_state": "RUN_INVALID",
        "invalid_run_reason": invalid_run_reason,
        "notes": notes,
    }
