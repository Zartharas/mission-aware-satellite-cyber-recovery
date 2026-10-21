from __future__ import annotations

from decimal import Decimal, InvalidOperation
from math import gcd

POLICIES = (
    "S2_B0_FAIL_CLOSED",
    "S2_B2_RISK_THRESHOLD",
    "S2_S1_EVIDENCE_AWARE",
)
EVIDENCE_STATES = ("V0", "V4", "V5")
TIMING_ARMS = ("EMPIRICAL_HIATUS_PROXY", "MATCHED_CONTINUOUS_REFRESH_CONTROL")
PERMISSIVE = {"PRESERVE_LIMITED_OPERATION", "PROCEED_TO_RECOVERY_GATE"}
PROTECTIVE = {"HOLD_AND_REQUIRE_EVIDENCE", "RESTRICT_AND_REQUEST_AUTHORIZATION"}


def _ratio(token: object, field: str) -> tuple[int, int]:
    text = str(token).strip()
    if not text:
        raise ValueError(f"{field} is empty")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is invalid") from exc
    if not value.is_finite():
        raise ValueError(f"{field} must be finite")
    numerator, denominator = value.as_integer_ratio()
    return int(numerator), int(denominator)


def _reduce(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator == 0:
        raise ZeroDivisionError("zero denominator")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    common = gcd(abs(numerator), denominator)
    return numerator // common, denominator // common


def _divide(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return _reduce(left[0] * right[1], left[1] * right[0])


def _subtract_one(value: tuple[int, int]) -> tuple[int, int]:
    return _reduce(value[0] - value[1], value[1])


def _text(value: tuple[int, int]) -> str:
    n, d = _reduce(*value)
    return str(n) if d == 1 else f"{n}/{d}"


def _greater(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] * right[1] > right[0] * left[1]


def _equal(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] * right[1] == right[0] * left[1]


def _policy_action(policy: str, qualified: bool, signal: bool, proxy: bool) -> str:
    if policy == "S2_B0_FAIL_CLOSED":
        return (
            "PROCEED_TO_RECOVERY_GATE"
            if qualified
            else "RESTRICT_AND_REQUEST_AUTHORIZATION"
        )
    if policy == "S2_B2_RISK_THRESHOLD":
        if not qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        return (
            "RESTRICT_AND_REQUEST_AUTHORIZATION"
            if signal
            else "PRESERVE_LIMITED_OPERATION"
        )
    if policy == "S2_S1_EVIDENCE_AWARE":
        if not qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        if signal and not proxy:
            return "RESTRICT_AND_REQUEST_AUTHORIZATION"
        return "PROCEED_TO_RECOVERY_GATE"
    raise ValueError(f"unknown policy: {policy}")


def _refresh_record(evidence_state: str) -> tuple[bool, bool]:
    table = {
        "V0": (False, True),
        "V4": (True, False),
        "V5": (True, True),
    }
    try:
        return table[evidence_state]
    except KeyError as exc:
        raise ValueError(f"unknown evidence state: {evidence_state}") from exc


def evaluate_reference(
    row: dict[str, object],
    *,
    policy: str,
    evidence_state: str,
    timing_arm: str,
) -> dict[str, object]:
    if policy not in POLICIES:
        raise ValueError("unsupported policy")
    if evidence_state not in EVIDENCE_STATES:
        raise ValueError("unsupported evidence state")
    if timing_arm not in TIMING_ARMS:
        raise ValueError("unsupported timing arm")
    if str(row.get("experiment_id")) != "S3X-ETA-001":
        raise ValueError("unexpected experiment")
    if str(row.get("gap_rule")) != "P99_X10":
        raise ValueError("unexpected gap rule")
    if str(row.get("comparison_operator")) != ">":
        raise ValueError("unexpected comparison")

    delta_token = str(row.get("delta_seconds", "")).strip()
    cadence_token = str(row.get("cadence_p99_seconds", "")).strip()
    threshold_token = str(row.get("threshold_seconds", "")).strip()

    delta = _ratio(delta_token, "delta_seconds")
    cadence = _ratio(cadence_token, "cadence_p99_seconds")
    threshold = _ratio(threshold_token, "threshold_seconds")
    if not _greater(delta, (0, 1)) or not _greater(cadence, (0, 1)):
        raise ValueError("timing values must be positive")

    # Independently reproduce the Phase-6 binary-float membership contract.
    delta_float = float(delta_token)
    cadence_float = float(cadence_token)
    threshold_float = float(threshold_token)
    if threshold_float != cadence_float * 10.0:
        raise ValueError("threshold float relationship mismatch")
    if not delta_float > threshold_float:
        raise ValueError("not a frozen strict P99_X10 member")

    normalized = _divide(delta, cadence)
    if not _greater(normalized, (10, 1)):
        raise AssertionError("normalized hiatus must exceed ten")

    if timing_arm == "EMPIRICAL_HIATUS_PROXY":
        initial_action = _policy_action(policy, True, True, False)
        cache_exposure = (
            (1, 1)
            if initial_action == "PROCEED_TO_RECOVERY_GATE"
            else (0, 1)
        )
        initial_protective = (1, 1) if initial_action in PROTECTIVE else (0, 1)
        expired_action = _policy_action(policy, False, True, False)
        expired_protective = (
            _subtract_one(normalized)
            if expired_action in PROTECTIVE
            else (0, 1)
        )
        protective = _reduce(
            initial_protective[0] * expired_protective[1]
            + expired_protective[0] * initial_protective[1],
            initial_protective[1] * expired_protective[1],
        )
        first_time = normalized
    else:
        cache_exposure = (0, 1)
        protective = (0, 1)
        first_time = (0, 1)

    claim, signature = _refresh_record(evidence_state)
    action = _policy_action(policy, signature, True, True)
    gate = action == "PROCEED_TO_RECOVERY_GATE" and signature and claim
    unsafe_permissive = action in PERMISSIVE
    origin = "V5_AFFECTED_RECORD" if gate and evidence_state == "V5" else "NONE"

    return {
        "interval_id": str(row.get("interval_id")),
        "policy": policy,
        "evidence_state": evidence_state,
        "timing_arm": timing_arm,
        "normalized_hiatus_units": _text(normalized),
        "cache_origin_unsafe_qualified_exposure_cadence_units": _text(
            cache_exposure
        ),
        "protective_hiatus_duration_cadence_units": _text(protective),
        "first_refresh_time_cadence_units": _text(first_time),
        "first_refresh_action": action,
        "first_refresh_gate_qualified": gate,
        "first_refresh_unsafe_permissive": unsafe_permissive,
        "first_refresh_unsafe_qualified": gate,
        "first_refresh_unsafe_qualification_origin": origin,
        "v5_first_refresh_qualification_delay_cadence_units": (
            _text(first_time) if gate and evidence_state == "V5" else None
        ),
    }


if __name__ == "__main__":
    raise SystemExit(
        "Phase-7D corrected reference module is library-only; "
        "use the separately authorized v2 validator for real execution."
    )
