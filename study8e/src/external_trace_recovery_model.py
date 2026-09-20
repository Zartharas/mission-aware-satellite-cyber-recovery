from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
BUDGET_PATH = ROOT / "study8" / "STUDY8_CRYPTO_OBJECT_BUDGETS.json"

OBJECT_PRIORITY = (
    "recovery_authority_assertion_signature",
    "successor_kem_encapsulation_key",
    "successor_signature_verification_key",
    "kem_ciphertext",
    "transition_proof_signature",
    "new_epoch_commit_signature",
    "post_commit_confirmation_signature",
)

POLICIES = (
    "P0_HARD_CUTOVER",
    "P1_STAGED_CUTOVER",
    "P2_HYBRID_OVERLAP",
    "P3_CONTACT_AWARE_STAGED",
)

DISRUPTIONS = (
    "A0_NONE",
    "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
    "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
    "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
)

MAX_SEARCH_RATE_BPS = 1_000_000_000_000
BITS_PER_BYTE = 8
MICROSECONDS_PER_SECOND = 1_000_000
CAPACITY_DENOMINATOR = BITS_PER_BYTE * MICROSECONDS_PER_SECOND


def _load_profile_objects() -> dict[str, dict[str, int]]:
    payload = json.loads(BUDGET_PATH.read_text(encoding="utf-8"))
    profiles = payload["profiles"]
    result: dict[str, dict[str, int]] = {}
    for profile, values in profiles.items():
        modeled = values["modeled_transition_objects_bytes"]
        result[profile] = {name: int(modeled[name]) for name in OBJECT_PRIORITY}
    return result


PROFILE_OBJECTS = _load_profile_objects()
PROFILES = tuple(PROFILE_OBJECTS)


@dataclass(frozen=True, order=True)
class Window:
    start_us: int
    end_us: int

    def __post_init__(self) -> None:
        if self.start_us < 0:
            raise ValueError("window start must be non-negative")
        if self.end_us <= self.start_us:
            raise ValueError("window end must be strictly greater than start")


@dataclass(frozen=True)
class ExternalCase:
    profile: str
    policy: str
    disruption: str
    horizon_us: int
    rate_bps: int
    windows: tuple[Window, ...]


@dataclass
class MutableRun:
    delivered: dict[str, int]
    cryptographic_bytes_transferred: int = 0
    opportunities_consumed: int = 0
    transition_attempts: int = 0
    a1_used: bool = False
    a2_used: bool = False
    a3_used: bool = False
    proof_accepted_us: int | None = None
    commit_us: int | None = None
    completion_us: int | None = None
    p3_guard_blocked: bool = False
    stale_epoch_acceptance: bool = False
    rollback_invoked: bool = False


def merge_windows(windows: Iterable[Window]) -> tuple[Window, ...]:
    ordered = sorted(windows)
    if not ordered:
        return ()
    merged: list[Window] = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start_us <= previous.end_us:
            merged[-1] = Window(previous.start_us, max(previous.end_us, current.end_us))
        else:
            merged.append(current)
    return tuple(merged)


def effective_windows(windows: Iterable[Window], horizon_us: int) -> tuple[Window, ...]:
    if horizon_us <= 0:
        raise ValueError("horizon_us must be positive")
    result: list[Window] = []
    for window in merge_windows(windows):
        if window.start_us >= horizon_us:
            continue
        end = min(window.end_us, horizon_us)
        if end > window.start_us:
            result.append(Window(window.start_us, end))
    return tuple(result)


def capacity_bytes(window: Window, rate_bps: int) -> int:
    if rate_bps <= 0:
        raise ValueError("rate_bps must be positive")
    duration_us = window.end_us - window.start_us
    return (duration_us * rate_bps) // CAPACITY_DENOMINATOR


def _event_time_us(window: Window, bytes_consumed_in_window: int, rate_bps: int) -> int:
    if bytes_consumed_in_window < 0:
        raise ValueError("bytes_consumed_in_window must be non-negative")
    numerator = bytes_consumed_in_window * CAPACITY_DENOMINATOR
    elapsed = (numerator + rate_bps - 1) // rate_bps
    return window.start_us + elapsed


def _bundle_staged(delivered: Mapping[str, int], sizes: Mapping[str, int]) -> bool:
    return all(
        delivered[name] == sizes[name]
        for name in (
            "successor_kem_encapsulation_key",
            "successor_signature_verification_key",
            "kem_ciphertext",
        )
    )


def _ready_object(
    delivered: Mapping[str, int],
    sizes: Mapping[str, int],
    *,
    p3_guard_blocked: bool,
) -> str | None:
    ra = "recovery_authority_assertion_signature"
    if delivered[ra] < sizes[ra]:
        return ra

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
    for name in OBJECT_PRIORITY:
        if sizes[name] == maximum:
            return name
    raise AssertionError("largest object not found")


def _remaining_nominal_capacity(
    windows: Sequence[Window],
    capacities: Sequence[int],
    *,
    window_index: int,
    current_remaining: int,
) -> int:
    return current_remaining + sum(capacities[window_index + 1 :])


def _terminal_state(run: MutableRun, sizes: Mapping[str, int]) -> str:
    if run.stale_epoch_acceptance:
        return "STALE_EPOCH_ACCEPTED"

    confirmation = "post_commit_confirmation_signature"
    if run.commit_us is not None and run.delivered[confirmation] < sizes[confirmation]:
        return "EPOCH_DIVERGENCE"

    precommit = (
        "recovery_authority_assertion_signature",
        "successor_kem_encapsulation_key",
        "successor_signature_verification_key",
        "kem_ciphertext",
        "transition_proof_signature",
        "new_epoch_commit_signature",
    )
    if any(run.delivered[name] < sizes[name] for name in precommit):
        if run.p3_guard_blocked:
            return "CONTACT_BUDGET_EXHAUSTED"
        return "INSUFFICIENT_MATERIAL_TRANSFER"

    return "RECOVERY_DEADLINE_EXCEEDED"


def _legacy_exposure_us(policy: str, commit_us: int | None, horizon_us: int) -> int:
    if policy == "P0_HARD_CUTOVER":
        return 0
    return horizon_us if commit_us is None else min(commit_us, horizon_us)


def _control_unavailable_us(policy: str, commit_us: int | None, horizon_us: int) -> int:
    if policy != "P0_HARD_CUTOVER":
        return 0
    return horizon_us if commit_us is None else min(commit_us, horizon_us)


def _dual_epoch_overlap_us(
    policy: str,
    proof_us: int | None,
    commit_us: int | None,
    horizon_us: int,
) -> int:
    if policy != "P2_HYBRID_OVERLAP" or proof_us is None:
        return 0
    end = horizon_us if commit_us is None else min(commit_us, horizon_us)
    return max(0, end - proof_us)


def validate_case(case: ExternalCase) -> None:
    if case.profile not in PROFILE_OBJECTS:
        raise ValueError(f"unknown profile: {case.profile}")
    if case.policy not in POLICIES:
        raise ValueError(f"unknown policy: {case.policy}")
    if case.disruption not in DISRUPTIONS:
        raise ValueError(f"unknown disruption: {case.disruption}")
    if case.horizon_us <= 0:
        raise ValueError("horizon_us must be positive")
    if case.rate_bps <= 0:
        raise ValueError("rate_bps must be positive")


def evaluate_case(case: ExternalCase) -> dict[str, object]:
    validate_case(case)
    sizes = PROFILE_OBJECTS[case.profile]
    windows = effective_windows(case.windows, case.horizon_us)
    capacities = tuple(capacity_bytes(window, case.rate_bps) for window in windows)
    run = MutableRun(delivered={name: 0 for name in OBJECT_PRIORITY})
    a1_target = _a1_target(sizes)

    for window_index, (window, capacity) in enumerate(zip(windows, capacities)):
        if run.completion_us is not None:
            break
        if capacity <= 0:
            continue

        remaining = capacity
        bytes_used_in_window = 0
        opportunity_touched = False

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
                and case.disruption == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT"
                and not run.a2_used
            ):
                run.a2_used = True
                opportunity_touched = True
                remaining = 0
                break

            if ready == "new_epoch_commit_signature":
                if case.policy == "P3_CONTACT_AWARE_STAGED" and not run.p3_guard_blocked:
                    required = (
                        sizes["new_epoch_commit_signature"]
                        - run.delivered["new_epoch_commit_signature"]
                        + sizes["post_commit_confirmation_signature"]
                        - run.delivered["post_commit_confirmation_signature"]
                    )
                    nominal = _remaining_nominal_capacity(
                        windows,
                        capacities,
                        window_index=window_index,
                        current_remaining=remaining,
                    )
                    if nominal < required:
                        run.p3_guard_blocked = True
                        opportunity_touched = True
                        remaining = 0
                        break

                if (
                    case.disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT"
                    and not run.a3_used
                ):
                    run.a3_used = True
                    run.transition_attempts += 1
                    opportunity_touched = True
                    remaining = 0
                    break

            need = sizes[ready] - run.delivered[ready]
            send = min(need, remaining)
            if send <= 0:
                raise AssertionError("non-positive transfer")

            run.cryptographic_bytes_transferred += send
            remaining -= send
            bytes_used_in_window += send
            opportunity_touched = True

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

            event_time = _event_time_us(window, bytes_used_in_window, case.rate_bps)
            if event_time > window.end_us:
                raise AssertionError("event timestamp exceeds window")

            if ready == "transition_proof_signature":
                run.proof_accepted_us = event_time
            elif ready == "new_epoch_commit_signature":
                run.transition_attempts += 1
                run.commit_us = event_time
            elif ready == "post_commit_confirmation_signature":
                run.completion_us = event_time
                break

        if opportunity_touched:
            run.opportunities_consumed += 1

    success = (
        run.completion_us is not None
        and run.completion_us < case.horizon_us
        and not run.stale_epoch_acceptance
    )
    terminal = "TRUST_RESTORED" if success else _terminal_state(run, sizes)

    return {
        "profile": case.profile,
        "policy": case.policy,
        "disruption": case.disruption,
        "horizon_us": case.horizon_us,
        "rate_bps": case.rate_bps,
        "trusted_recovery_success": int(success),
        "recovery_completion_us": "" if run.completion_us is None else run.completion_us,
        "observation_opportunities_consumed": run.opportunities_consumed,
        "cryptographic_bytes_transferred": run.cryptographic_bytes_transferred,
        "transition_attempts": run.transition_attempts,
        "legacy_exposure_us": _legacy_exposure_us(case.policy, run.commit_us, case.horizon_us),
        "control_unavailable_us": _control_unavailable_us(
            case.policy, run.commit_us, case.horizon_us
        ),
        "dual_epoch_overlap_us": _dual_epoch_overlap_us(
            case.policy,
            run.proof_accepted_us,
            run.commit_us,
            case.horizon_us,
        ),
        "rollback_invoked": int(run.rollback_invoked),
        "stale_epoch_acceptance": int(run.stale_epoch_acceptance),
        "terminal_state": terminal,
        "proof_accepted_us": "" if run.proof_accepted_us is None else run.proof_accepted_us,
        "commit_us": "" if run.commit_us is None else run.commit_us,
        "p3_guard_blocked": int(run.p3_guard_blocked),
    }


def minimum_success_rate_bps(
    *,
    profile: str,
    policy: str,
    disruption: str,
    horizon_us: int,
    windows: tuple[Window, ...],
    maximum_rate_bps: int = MAX_SEARCH_RATE_BPS,
) -> dict[str, object]:
    if maximum_rate_bps <= 0:
        raise ValueError("maximum_rate_bps must be positive")

    def succeeds(rate: int) -> bool:
        row = evaluate_case(
            ExternalCase(
                profile=profile,
                policy=policy,
                disruption=disruption,
                horizon_us=horizon_us,
                rate_bps=rate,
                windows=windows,
            )
        )
        return bool(row["trusted_recovery_success"])

    upper = 1
    while upper < maximum_rate_bps and not succeeds(upper):
        upper = min(maximum_rate_bps, upper * 2)

    if not succeeds(upper):
        return {
            "minimum_rate_bps": None,
            "status": "NO_FINITE_RATE_IDENTIFIED_WITHIN_FROZEN_SEARCH_DOMAIN",
            "maximum_rate_bps": maximum_rate_bps,
        }

    lower = 1
    while lower < upper:
        middle = (lower + upper) // 2
        if succeeds(middle):
            upper = middle
        else:
            lower = middle + 1

    return {
        "minimum_rate_bps": lower,
        "status": "FINITE_THRESHOLD",
        "maximum_rate_bps": maximum_rate_bps,
    }


if __name__ == "__main__":
    raise SystemExit(
        "Study 8E implementation is fixture-only at this gate; canonical external-trace execution is not authorized."
    )
