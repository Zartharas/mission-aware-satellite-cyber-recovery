from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Mapping

from study8.src.contact_recovery_model import OBJECT_PRIORITY, PROFILE_OBJECTS


POLICY_SET = {
    "P0_HARD_CUTOVER",
    "P1_STAGED_CUTOVER",
    "P2_HYBRID_OVERLAP",
    "P3_CONTACT_AWARE_STAGED",
}

DISRUPTION_SET = {
    "A0_NONE",
    "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
    "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
    "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
}


def _f(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value, 1)


def _merge(
    windows: Iterable[tuple[int | Fraction, int | Fraction]],
) -> list[tuple[Fraction, Fraction]]:
    items = sorted((_f(a), _f(b)) for a, b in windows)
    if any(a < 0 or b <= a for a, b in items):
        raise ValueError("invalid window")
    if not items:
        return []
    result = [items[0]]
    for start, end in items[1:]:
        old_start, old_end = result[-1]
        if start <= old_end:
            result[-1] = (old_start, max(old_end, end))
        else:
            result.append((start, end))
    return result


def _capacity(start: Fraction, end: Fraction, rate: int) -> int:
    return int((Fraction(rate, 1) * (end - start)) // 8)


def independent_evaluate(
    *,
    profile: str,
    policy: str,
    disruption: str,
    horizon_s: int | Fraction,
    rate_bps: int,
    windows: Iterable[tuple[int | Fraction, int | Fraction]],
) -> dict[str, object]:
    if profile not in PROFILE_OBJECTS:
        raise ValueError("unknown profile")
    if policy not in POLICY_SET:
        raise ValueError("unknown policy")
    if disruption not in DISRUPTION_SET:
        raise ValueError("unknown disruption")
    horizon = _f(horizon_s)
    if horizon <= 0 or rate_bps <= 0:
        raise ValueError("invalid horizon/rate")

    merged = _merge(windows)
    schedule: list[tuple[Fraction, Fraction]] = []
    for start, end in merged:
        if start >= horizon:
            continue
        clipped_end = min(end, horizon)
        if clipped_end > start:
            schedule.append((start, clipped_end))

    size_map = PROFILE_OBJECTS[profile]
    sizes = [size_map[name] for name in OBJECT_PRIORITY]
    delivered = [0] * 7
    largest_value = max(sizes)
    largest_index = next(
        i for i, value in enumerate(sizes) if value == largest_value
    )

    transferred = 0
    consumed_windows = 0
    attempts = 0
    lost_once = False
    delayed_once = False
    replay_once = False
    guard_blocked = False
    proof_time: Fraction | None = None
    commit_time: Fraction | None = None
    completion_time: Fraction | None = None

    def ready_index() -> int | None:
        if delivered[0] < sizes[0]:
            return 0
        for i in (1, 2, 3):
            if delivered[i] < sizes[i]:
                return i
        if delivered[4] < sizes[4]:
            return 4
        if guard_blocked:
            return None
        if delivered[5] < sizes[5]:
            return 5
        if delivered[6] < sizes[6]:
            return 6
        return None

    capacities = [
        _capacity(start, end, rate_bps) for start, end in schedule
    ]

    for pos, ((start, _end), initial_capacity) in enumerate(
        zip(schedule, capacities)
    ):
        if completion_time is not None:
            break
        if initial_capacity <= 0:
            continue

        remaining = initial_capacity
        sent_in_window = 0
        touched = False

        while remaining > 0:
            idx = ready_index()
            if idx is None:
                break

            if (
                idx == 4
                and disruption
                == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT"
                and not delayed_once
            ):
                delayed_once = True
                touched = True
                remaining = 0
                break

            if idx == 5:
                if policy == "P3_CONTACT_AWARE_STAGED":
                    required = (
                        sizes[5] - delivered[5]
                        + sizes[6] - delivered[6]
                    )
                    nominal = remaining + sum(capacities[pos + 1 :])
                    if nominal < required:
                        guard_blocked = True
                        touched = True
                        remaining = 0
                        break

                if (
                    disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT"
                    and not replay_once
                ):
                    replay_once = True
                    attempts += 1
                    touched = True
                    remaining = 0
                    break

            amount = min(sizes[idx] - delivered[idx], remaining)
            if amount <= 0:
                raise AssertionError("non-positive independent transfer")

            transferred += amount
            remaining -= amount
            sent_in_window += amount
            touched = True

            if (
                disruption == "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT"
                and idx == largest_index
                and not lost_once
            ):
                lost_once = True
            else:
                delivered[idx] += amount

            if delivered[idx] != sizes[idx]:
                continue

            event_time = start + Fraction(sent_in_window * 8, rate_bps)
            if idx == 4:
                proof_time = event_time
            elif idx == 5:
                attempts += 1
                commit_time = event_time
            elif idx == 6:
                completion_time = event_time
                break

        if touched:
            consumed_windows += 1

    success = completion_time is not None and completion_time < horizon

    if success:
        terminal = "TRUST_RESTORED"
    elif commit_time is not None and delivered[6] < sizes[6]:
        terminal = "EPOCH_DIVERGENCE"
    elif guard_blocked and any(delivered[i] < sizes[i] for i in range(6)):
        terminal = "CONTACT_BUDGET_EXHAUSTED"
    elif any(delivered[i] < sizes[i] for i in range(6)):
        terminal = "INSUFFICIENT_MATERIAL_TRANSFER"
    else:
        terminal = "RECOVERY_DEADLINE_EXCEEDED"

    if policy == "P0_HARD_CUTOVER":
        legacy = Fraction(0, 1)
        unavailable = (
            horizon if commit_time is None else min(commit_time, horizon)
        )
    else:
        legacy = horizon if commit_time is None else min(commit_time, horizon)
        unavailable = Fraction(0, 1)

    if policy == "P2_HYBRID_OVERLAP" and proof_time is not None:
        overlap_end = (
            horizon if commit_time is None else min(commit_time, horizon)
        )
        overlap = max(Fraction(0, 1), overlap_end - proof_time)
    else:
        overlap = Fraction(0, 1)

    return {
        "profile": profile,
        "policy": policy,
        "disruption": disruption,
        "horizon_s": horizon,
        "rate_bps": rate_bps,
        "trusted_recovery_success": int(success),
        "recovery_completion_time_s": completion_time,
        "windows_consumed": consumed_windows,
        "cryptographic_bytes_transferred": transferred,
        "transition_attempts": attempts,
        "legacy_exposure_s": legacy,
        "control_unavailable_s": unavailable,
        "dual_epoch_overlap_s": overlap,
        "rollback_invoked": 0,
        "stale_epoch_acceptance": 0,
        "terminal_state": terminal,
        "proof_accepted_time_s": proof_time,
        "commit_time_s": commit_time,
        "p3_guard_blocked": int(guard_blocked),
    }


def compare_observation(
    observation: Mapping[str, object],
    reference: Mapping[str, object],
) -> tuple[bool, tuple[str, ...]]:
    keys = tuple(reference)
    mismatches = tuple(
        key for key in keys if observation.get(key) != reference.get(key)
    )
    return (not mismatches, mismatches)


if __name__ == "__main__":
    raise SystemExit(
        "Study 8E independent reference is synthetic-audit construction only."
    )
