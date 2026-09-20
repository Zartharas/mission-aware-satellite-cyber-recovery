from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping, Sequence

from study8.src.contact_recovery_model import (
    DISRUPTIONS,
    OBJECT_PRIORITY,
    POLICIES,
    PROFILE_OBJECTS,
)


@dataclass(frozen=True, order=True)
class Window:
    start_s: Fraction
    end_s: Fraction

    def __post_init__(self) -> None:
        if self.start_s < 0:
            raise ValueError("window start must be non-negative")
        if self.end_s <= self.start_s:
            raise ValueError("window end must be greater than start")


@dataclass(frozen=True)
class ExternalCase:
    profile: str
    policy: str
    disruption: str
    horizon_s: Fraction
    rate_bps: int


@dataclass
class MutableRun:
    delivered: dict[str, int]
    cryptographic_bytes_transferred: int = 0
    windows_consumed: int = 0
    transition_attempts: int = 0
    a1_used: bool = False
    a2_used: bool = False
    a3_used: bool = False
    proof_accepted_time_s: Fraction | None = None
    commit_time_s: Fraction | None = None
    completion_time_s: Fraction | None = None
    p3_guard_blocked: bool = False
    stale_epoch_acceptance: bool = False
    rollback_invoked: bool = False


def as_fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    raise TypeError("time values must be integers or Fraction")


def normalize_windows(
    windows: Iterable[Window | tuple[int | Fraction, int | Fraction]],
) -> tuple[Window, ...]:
    prepared: list[Window] = []
    for item in windows:
        if isinstance(item, Window):
            prepared.append(item)
        else:
            start, end = item
            prepared.append(Window(as_fraction(start), as_fraction(end)))

    if not prepared:
        return ()

    prepared.sort()
    merged: list[Window] = [prepared[0]]
    for window in prepared[1:]:
        previous = merged[-1]
        if window.start_s <= previous.end_s:
            merged[-1] = Window(
                previous.start_s,
                max(previous.end_s, window.end_s),
            )
        else:
            merged.append(window)
    return tuple(merged)


def validate_case(case: ExternalCase) -> None:
    if case.profile not in PROFILE_OBJECTS:
        raise ValueError(f"unknown profile: {case.profile}")
    if case.policy not in POLICIES:
        raise ValueError(f"unknown policy: {case.policy}")
    if case.disruption not in DISRUPTIONS:
        raise ValueError(f"unknown disruption: {case.disruption}")
    if case.horizon_s <= 0:
        raise ValueError("horizon must be positive")
    if not isinstance(case.rate_bps, int) or case.rate_bps <= 0:
        raise ValueError("rate_bps must be a positive integer")


def clip_windows_before_horizon(
    windows: Sequence[Window],
    horizon_s: Fraction,
) -> tuple[Window, ...]:
    clipped: list[Window] = []
    for window in windows:
        if window.start_s >= horizon_s:
            continue
        end = min(window.end_s, horizon_s)
        if end > window.start_s:
            clipped.append(Window(window.start_s, end))
    return tuple(clipped)


def window_capacity_bytes(window: Window, rate_bps: int) -> int:
    return int((Fraction(rate_bps, 1) * (window.end_s - window.start_s)) // 8)


def _bundle_staged(
    delivered: Mapping[str, int],
    sizes: Mapping[str, int],
) -> bool:
    required = (
        "successor_kem_encapsulation_key",
        "successor_signature_verification_key",
        "kem_ciphertext",
    )
    return all(delivered[name] == sizes[name] for name in required)


def _ready_object(
    delivered: Mapping[str, int],
    sizes: Mapping[str, int],
    *,
    p3_guard_blocked: bool,
) -> str | None:
    recovery = "recovery_authority_assertion_signature"
    if delivered[recovery] < sizes[recovery]:
        return recovery

    if not _bundle_staged(delivered, sizes):
        for name in (
            "successor_kem_encapsulation_key",
            "successor_signature_verification_key",
            "kem_ciphertext",
        ):
            if delivered[name] < sizes[name]:
                return name

    proof = "transition_proof_signature"
    if delivered[proof] < sizes[proof]:
        return proof

    if p3_guard_blocked:
        return None

    commit = "new_epoch_commit_signature"
    if delivered[commit] < sizes[commit]:
        return commit

    confirmation = "post_commit_confirmation_signature"
    if delivered[confirmation] < sizes[confirmation]:
        return confirmation

    return None


def _a1_target(sizes: Mapping[str, int]) -> str:
    maximum = max(sizes.values())
    return next(name for name in OBJECT_PRIORITY if sizes[name] == maximum)


def _remaining_nominal_bytes(
    windows: Sequence[Window],
    *,
    window_index: int,
    current_remaining: int,
    rate_bps: int,
) -> int:
    total = current_remaining
    for future in windows[window_index + 1 :]:
        total += window_capacity_bytes(future, rate_bps)
    return total


def _terminal_state(
    *,
    run: MutableRun,
    sizes: Mapping[str, int],
) -> str:
    if run.stale_epoch_acceptance:
        return "STALE_EPOCH_ACCEPTED"

    commit = "new_epoch_commit_signature"
    confirmation = "post_commit_confirmation_signature"

    if (
        run.commit_time_s is not None
        and run.delivered[confirmation] < sizes[confirmation]
    ):
        return "EPOCH_DIVERGENCE"

    precommit = (
        "recovery_authority_assertion_signature",
        "successor_kem_encapsulation_key",
        "successor_signature_verification_key",
        "kem_ciphertext",
        "transition_proof_signature",
        commit,
    )
    if any(run.delivered[name] < sizes[name] for name in precommit):
        if run.p3_guard_blocked:
            return "CONTACT_BUDGET_EXHAUSTED"
        return "INSUFFICIENT_MATERIAL_TRANSFER"

    return "RECOVERY_DEADLINE_EXCEEDED"


def _legacy_exposure_s(
    policy: str,
    commit_time_s: Fraction | None,
    horizon_s: Fraction,
) -> Fraction:
    if policy == "P0_HARD_CUTOVER":
        return Fraction(0, 1)
    return horizon_s if commit_time_s is None else min(commit_time_s, horizon_s)


def _control_unavailable_s(
    policy: str,
    commit_time_s: Fraction | None,
    horizon_s: Fraction,
) -> Fraction:
    if policy != "P0_HARD_CUTOVER":
        return Fraction(0, 1)
    return horizon_s if commit_time_s is None else min(commit_time_s, horizon_s)


def _dual_epoch_overlap_s(
    policy: str,
    proof_time_s: Fraction | None,
    commit_time_s: Fraction | None,
    horizon_s: Fraction,
) -> Fraction:
    if policy != "P2_HYBRID_OVERLAP" or proof_time_s is None:
        return Fraction(0, 1)
    end = horizon_s if commit_time_s is None else min(commit_time_s, horizon_s)
    return max(Fraction(0, 1), end - proof_time_s)


def evaluate_case(
    case: ExternalCase,
    windows: Iterable[Window | tuple[int | Fraction, int | Fraction]],
) -> dict[str, object]:
    validate_case(case)
    normalized = normalize_windows(windows)
    effective = clip_windows_before_horizon(normalized, case.horizon_s)
    sizes = PROFILE_OBJECTS[case.profile]
    run = MutableRun(delivered={name: 0 for name in OBJECT_PRIORITY})
    a1_target = _a1_target(sizes)

    for window_index, window in enumerate(effective):
        if run.completion_time_s is not None:
            break

        remaining = window_capacity_bytes(window, case.rate_bps)
        if remaining <= 0:
            continue

        sent_or_consumed = 0
        touched = False

        while remaining > 0:
            ready = _ready_object(
                run.delivered,
                sizes,
                p3_guard_blocked=run.p3_guard_blocked,
            )
            if ready is None:
                break

            if (
                ready == "transition_proof_signature"
                and case.disruption
                == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT"
                and not run.a2_used
            ):
                run.a2_used = True
                touched = True
                remaining = 0
                break

            if ready == "new_epoch_commit_signature":
                if (
                    case.policy == "P3_CONTACT_AWARE_STAGED"
                    and not run.p3_guard_blocked
                ):
                    required = (
                        sizes["new_epoch_commit_signature"]
                        - run.delivered["new_epoch_commit_signature"]
                        + sizes["post_commit_confirmation_signature"]
                        - run.delivered["post_commit_confirmation_signature"]
                    )
                    nominal = _remaining_nominal_bytes(
                        effective,
                        window_index=window_index,
                        current_remaining=remaining,
                        rate_bps=case.rate_bps,
                    )
                    if nominal < required:
                        run.p3_guard_blocked = True
                        touched = True
                        remaining = 0
                        break

                if (
                    case.disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT"
                    and not run.a3_used
                ):
                    run.a3_used = True
                    run.transition_attempts += 1
                    touched = True
                    remaining = 0
                    break

            need = sizes[ready] - run.delivered[ready]
            send = min(need, remaining)
            if send <= 0:
                raise AssertionError("non-positive transfer")

            run.cryptographic_bytes_transferred += send
            remaining -= send
            sent_or_consumed += send
            touched = True

            if (
                case.disruption == "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT"
                and ready == a1_target
                and not run.a1_used
            ):
                run.a1_used = True
            else:
                run.delivered[ready] += send

            if run.delivered[ready] != sizes[ready]:
                continue

            event_time = window.start_s + Fraction(
                sent_or_consumed * 8,
                case.rate_bps,
            )

            if ready == "transition_proof_signature":
                run.proof_accepted_time_s = event_time

            elif ready == "new_epoch_commit_signature":
                run.transition_attempts += 1
                run.commit_time_s = event_time

            elif ready == "post_commit_confirmation_signature":
                run.completion_time_s = event_time
                break

        if touched:
            run.windows_consumed += 1

    success = (
        run.completion_time_s is not None
        and run.completion_time_s < case.horizon_s
        and not run.stale_epoch_acceptance
    )
    terminal = (
        "TRUST_RESTORED"
        if success
        else _terminal_state(run=run, sizes=sizes)
    )

    return {
        "profile": case.profile,
        "policy": case.policy,
        "disruption": case.disruption,
        "horizon_s": case.horizon_s,
        "rate_bps": case.rate_bps,
        "trusted_recovery_success": int(success),
        "recovery_completion_time_s": run.completion_time_s,
        "windows_consumed": run.windows_consumed,
        "cryptographic_bytes_transferred": run.cryptographic_bytes_transferred,
        "transition_attempts": run.transition_attempts,
        "legacy_exposure_s": _legacy_exposure_s(
            case.policy,
            run.commit_time_s,
            case.horizon_s,
        ),
        "control_unavailable_s": _control_unavailable_s(
            case.policy,
            run.commit_time_s,
            case.horizon_s,
        ),
        "dual_epoch_overlap_s": _dual_epoch_overlap_s(
            case.policy,
            run.proof_accepted_time_s,
            run.commit_time_s,
            case.horizon_s,
        ),
        "rollback_invoked": int(run.rollback_invoked),
        "stale_epoch_acceptance": int(run.stale_epoch_acceptance),
        "terminal_state": terminal,
        "proof_accepted_time_s": run.proof_accepted_time_s,
        "commit_time_s": run.commit_time_s,
        "p3_guard_blocked": int(run.p3_guard_blocked),
    }


def minimum_integer_rate_bps(
    *,
    profile: str,
    policy: str,
    disruption: str,
    horizon_s: int | Fraction,
    windows: Iterable[Window | tuple[int | Fraction, int | Fraction]],
    max_rate_bps: int = 10_000_000,
) -> int | None:
    horizon = as_fraction(horizon_s)
    frozen_windows = normalize_windows(windows)
    if max_rate_bps <= 0:
        raise ValueError("max_rate_bps must be positive")

    def succeeds(rate: int) -> bool:
        result = evaluate_case(
            ExternalCase(
                profile=profile,
                policy=policy,
                disruption=disruption,
                horizon_s=horizon,
                rate_bps=rate,
            ),
            frozen_windows,
        )
        return bool(result["trusted_recovery_success"])

    if not succeeds(max_rate_bps):
        return None

    low = 1
    high = max_rate_bps
    while low < high:
        mid = (low + high) // 2
        if succeeds(mid):
            high = mid
        else:
            low = mid + 1

    threshold = low
    if threshold > 1 and succeeds(threshold - 1):
        raise AssertionError("threshold search monotonicity/postcondition failure")
    if not succeeds(threshold):
        raise AssertionError("threshold success postcondition failure")
    return threshold


def fraction_text(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


if __name__ == "__main__":
    raise SystemExit(
        "Study 8E implementation is construction-only; "
        "canonical external-trace execution is not authorized."
    )
