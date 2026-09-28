from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
import hashlib
import math

from study3.src.temporal_model import (
    PERMISSIVE_ACTIONS,
    PROTECTIVE_ACTIONS,
    select_action,
)

EXPERIMENT_ID = "S3X-ETA-001"
PROTOCOL_ID = "S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001"
TRACE_FREEZE_ID = "S3X-P99X10-TRACE-POPULATION-FREEZE-001"
EXPECTED_INTERVAL_ARTIFACT_SHA256 = (
    "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
)
EXPECTED_GAP_RULE = "P99_X10"
EXPECTED_DIAGNOSTIC_LABEL = "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC"
POLICIES = (
    "S2_B0_FAIL_CLOSED",
    "S2_B2_RISK_THRESHOLD",
    "S2_S1_EVIDENCE_AWARE",
)
EVIDENCE_STATES = ("V0", "V4", "V5")
TIMING_ARMS = ("EMPIRICAL_HIATUS_PROXY", "MATCHED_CONTINUOUS_REFRESH_CONTROL")


@dataclass(frozen=True)
class IntervalInput:
    interval_id: str
    mission: str
    channel_file: str
    delta_seconds_token: str
    cadence_p99_seconds_token: str
    threshold_seconds_token: str
    normalized_hiatus: Fraction


@dataclass(frozen=True)
class CaseResult:
    experiment_id: str
    protocol_id: str
    trace_freeze_id: str
    interval_id: str
    mission: str
    channel_file: str
    policy: str
    evidence_state: str
    timing_arm: str
    delta_seconds: str
    cadence_p99_seconds: str
    normalized_hiatus_units: str
    cache_origin_unsafe_qualified_exposure_cadence_units: str
    protective_hiatus_duration_cadence_units: str
    first_refresh_time_cadence_units: str
    first_refresh_action: str
    first_refresh_gate_qualified: bool
    first_refresh_unsafe_permissive: bool
    first_refresh_unsafe_qualified: bool
    first_refresh_unsafe_qualification_origin: str
    v5_first_refresh_qualification_delay_cadence_units: str | None


def _decimal_fraction(token: object, *, field: str) -> tuple[str, Fraction]:
    text = str(token).strip()
    if not text:
        raise ValueError(f"{field} is empty")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a valid decimal") from exc
    if not value.is_finite():
        raise ValueError(f"{field} must be finite")
    return text, Fraction(value)


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def verify_frozen_interval_artifact(path: str | Path) -> str:
    source = Path(path)
    h = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != EXPECTED_INTERVAL_ARTIFACT_SHA256:
        raise ValueError(
            "Phase-7 interval artifact SHA-256 mismatch: "
            f"expected={EXPECTED_INTERVAL_ARTIFACT_SHA256} actual={actual}"
        )
    return actual


def parse_interval_row(row: dict[str, object]) -> IntervalInput:
    if str(row.get("experiment_id", "")) != EXPERIMENT_ID:
        raise ValueError("unexpected experiment_id")
    if str(row.get("gap_rule_freeze_id", "")) != "S3X-P99X10-GAP-RULE-FREEZE-001":
        raise ValueError("unexpected gap_rule_freeze_id")
    if str(row.get("gap_rule", "")) != EXPECTED_GAP_RULE:
        raise ValueError("unexpected gap_rule")
    if str(row.get("comparison_operator", "")) != ">":
        raise ValueError("unexpected comparison_operator")
    if str(row.get("diagnostic_label", "")) != EXPECTED_DIAGNOSTIC_LABEL:
        raise ValueError("unexpected diagnostic_label")

    interval_id = str(row.get("interval_id", "")).strip()
    mission = str(row.get("mission", "")).strip()
    channel_file = str(row.get("channel_file", "")).strip()
    if not interval_id or not mission or not channel_file:
        raise ValueError("interval identity is incomplete")

    delta_token, delta = _decimal_fraction(row.get("delta_seconds"), field="delta_seconds")
    cadence_token, cadence = _decimal_fraction(
        row.get("cadence_p99_seconds"),
        field="cadence_p99_seconds",
    )
    threshold_token, threshold = _decimal_fraction(
        row.get("threshold_seconds"),
        field="threshold_seconds",
    )
    if delta <= 0 or cadence <= 0 or threshold <= 0:
        raise ValueError("interval timing values must be positive")

    # Phase 6 generated cadence_p99_seconds and threshold_seconds as binary
    # floats and serialized each independently through csv.DictWriter.  The
    # frozen numerical contract is therefore the original float relation,
    # not exact decimal multiplication after re-parsing the CSV strings.
    delta_float = float(delta_token)
    cadence_float = float(cadence_token)
    threshold_float = float(threshold_token)
    if not all(math.isfinite(v) for v in (delta_float, cadence_float, threshold_float)):
        raise ValueError("interval timing float values must be finite")
    if threshold_float != cadence_float * 10.0:
        raise ValueError("frozen P99_X10 threshold float relationship is inconsistent")
    if not delta_float > threshold_float:
        raise ValueError("row is not a member of the frozen strict P99_X10 population")

    normalized = delta / cadence
    if not normalized > 10:
        raise AssertionError("frozen interval must have normalized_hiatus > 10")

    return IntervalInput(
        interval_id=interval_id,
        mission=mission,
        channel_file=channel_file,
        delta_seconds_token=delta_token,
        cadence_p99_seconds_token=cadence_token,
        threshold_seconds_token=threshold_token,
        normalized_hiatus=normalized,
    )


def _first_refresh_semantics(evidence_state: str) -> tuple[bool, bool]:
    if evidence_state == "V0":
        return False, True
    if evidence_state == "V4":
        return True, False
    if evidence_state == "V5":
        return True, True
    raise ValueError(f"unsupported evidence state: {evidence_state}")


def _hiatus_measures(interval: IntervalInput, policy: str, timing_arm: str) -> tuple[Fraction, Fraction]:
    if timing_arm == "MATCHED_CONTINUOUS_REFRESH_CONTROL":
        return Fraction(0, 1), Fraction(0, 1)
    if timing_arm != "EMPIRICAL_HIATUS_PROXY":
        raise ValueError(f"unsupported timing arm: {timing_arm}")

    g = interval.normalized_hiatus
    fresh_cache_span = Fraction(1, 1)

    cache_action = select_action(
        policy,
        evidence_qualified=True,
        security_signal=True,
        contact=False,
    )
    cache_gate_qualified = cache_action == "PROCEED_TO_RECOVERY_GATE"
    cache_exposure = fresh_cache_span if cache_gate_qualified else Fraction(0, 1)

    initial_protective = (
        fresh_cache_span if cache_action in PROTECTIVE_ACTIONS else Fraction(0, 1)
    )
    expired_action = select_action(
        policy,
        evidence_qualified=False,
        security_signal=True,
        contact=False,
    )
    expired_span = g - fresh_cache_span
    if expired_span < 0:
        raise AssertionError("normalized hiatus is shorter than frozen freshness span")
    expired_protective = (
        expired_span if expired_action in PROTECTIVE_ACTIONS else Fraction(0, 1)
    )
    return cache_exposure, initial_protective + expired_protective


def evaluate_case(
    row: dict[str, object],
    *,
    policy: str,
    evidence_state: str,
    timing_arm: str,
) -> CaseResult:
    if policy not in POLICIES:
        raise ValueError(f"unsupported policy: {policy}")
    if evidence_state not in EVIDENCE_STATES:
        raise ValueError(f"unsupported evidence state: {evidence_state}")
    if timing_arm not in TIMING_ARMS:
        raise ValueError(f"unsupported timing arm: {timing_arm}")

    interval = parse_interval_row(row)
    cache_exposure, protective_duration = _hiatus_measures(
        interval,
        policy,
        timing_arm,
    )

    first_refresh_time = (
        interval.normalized_hiatus
        if timing_arm == "EMPIRICAL_HIATUS_PROXY"
        else Fraction(0, 1)
    )
    claim_authorization_valid, signature_valid = _first_refresh_semantics(
        evidence_state
    )
    evidence_qualified = signature_valid

    action = select_action(
        policy,
        evidence_qualified=evidence_qualified,
        security_signal=True,
        contact=True,
    )
    gate_qualified = (
        action == "PROCEED_TO_RECOVERY_GATE"
        and evidence_qualified
        and claim_authorization_valid
    )
    unsafe_permissive = action in PERMISSIVE_ACTIONS
    unsafe_qualified = gate_qualified
    origin = (
        "V5_AFFECTED_RECORD"
        if unsafe_qualified and evidence_state == "V5"
        else "NONE"
    )
    v5_delay = (
        fraction_text(first_refresh_time)
        if unsafe_qualified and evidence_state == "V5"
        else None
    )

    return CaseResult(
        experiment_id=EXPERIMENT_ID,
        protocol_id=PROTOCOL_ID,
        trace_freeze_id=TRACE_FREEZE_ID,
        interval_id=interval.interval_id,
        mission=interval.mission,
        channel_file=interval.channel_file,
        policy=policy,
        evidence_state=evidence_state,
        timing_arm=timing_arm,
        delta_seconds=interval.delta_seconds_token,
        cadence_p99_seconds=interval.cadence_p99_seconds_token,
        normalized_hiatus_units=fraction_text(interval.normalized_hiatus),
        cache_origin_unsafe_qualified_exposure_cadence_units=fraction_text(
            cache_exposure
        ),
        protective_hiatus_duration_cadence_units=fraction_text(
            protective_duration
        ),
        first_refresh_time_cadence_units=fraction_text(first_refresh_time),
        first_refresh_action=action,
        first_refresh_gate_qualified=gate_qualified,
        first_refresh_unsafe_permissive=unsafe_permissive,
        first_refresh_unsafe_qualified=unsafe_qualified,
        first_refresh_unsafe_qualification_origin=origin,
        v5_first_refresh_qualification_delay_cadence_units=v5_delay,
    )


def evaluate_interval(row: dict[str, object]) -> tuple[CaseResult, ...]:
    output = tuple(
        evaluate_case(
            row,
            policy=policy,
            evidence_state=evidence_state,
            timing_arm=timing_arm,
        )
        for policy in POLICIES
        for evidence_state in EVIDENCE_STATES
        for timing_arm in TIMING_ARMS
    )
    if len(output) != 18:
        raise AssertionError("each interval must expand to exactly 18 cases")
    return output


def as_row(result: CaseResult) -> dict[str, object]:
    return asdict(result)


if __name__ == "__main__":
    raise SystemExit(
        "Phase-7D corrected implementation module is library-only; "
        "use the separately authorized v2 runtime gate for real execution."
    )
