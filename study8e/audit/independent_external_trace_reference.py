from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUDGET_PATH = ROOT / "study8" / "STUDY8_CRYPTO_OBJECT_BUDGETS.json"

ORDER = [
    "recovery_authority_assertion_signature",
    "successor_kem_encapsulation_key",
    "successor_signature_verification_key",
    "kem_ciphertext",
    "transition_proof_signature",
    "new_epoch_commit_signature",
    "post_commit_confirmation_signature",
]

BITS_PER_BYTE_US = 8_000_000


def _sizes(profile: str) -> dict[str, int]:
    payload = json.loads(BUDGET_PATH.read_text(encoding="utf-8"))
    profiles = payload["profiles"]
    if profile not in profiles:
        raise ValueError(f"unknown profile: {profile}")
    objects = profiles[profile]["modeled_transition_objects_bytes"]
    return {name: int(objects[name]) for name in ORDER}


def _merge(raw_windows: tuple[tuple[int, int], ...], horizon_us: int) -> list[tuple[int, int]]:
    if horizon_us <= 0:
        raise ValueError("horizon_us must be positive")
    checked = []
    for start, end in raw_windows:
        if start < 0 or end <= start:
            raise ValueError("invalid window")
        if start >= horizon_us:
            continue
        checked.append((start, min(end, horizon_us)))
    checked.sort()
    merged: list[list[int]] = []
    for start, end in checked:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(a, b) for a, b in merged]


def _cap(start: int, end: int, rate_bps: int) -> int:
    return ((end - start) * rate_bps) // BITS_PER_BYTE_US


def _event_us(start: int, bytes_used: int, rate_bps: int) -> int:
    numerator = bytes_used * BITS_PER_BYTE_US
    return start + (numerator + rate_bps - 1) // rate_bps


def independently_evaluate(
    *,
    profile: str,
    policy: str,
    disruption: str,
    horizon_us: int,
    rate_bps: int,
    windows: tuple[tuple[int, int], ...],
) -> dict[str, object]:
    if rate_bps <= 0:
        raise ValueError("rate_bps must be positive")
    if policy not in {
        "P0_HARD_CUTOVER",
        "P1_STAGED_CUTOVER",
        "P2_HYBRID_OVERLAP",
        "P3_CONTACT_AWARE_STAGED",
    }:
        raise ValueError(f"unknown policy: {policy}")
    if disruption not in {
        "A0_NONE",
        "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
        "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
        "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
    }:
        raise ValueError(f"unknown disruption: {disruption}")

    sizes = _sizes(profile)
    merged = _merge(windows, horizon_us)
    capacities = [_cap(a, b, rate_bps) for a, b in merged]
    delivered = {name: 0 for name in ORDER}

    a1_target_size = max(sizes.values())
    a1_target = next(name for name in ORDER if sizes[name] == a1_target_size)

    bytes_transferred = 0
    opportunities = 0
    attempts = 0
    a1 = a2 = a3 = False
    proof_us = commit_us = completion_us = None
    p3_blocked = False

    def next_object() -> str | None:
        if delivered[ORDER[0]] < sizes[ORDER[0]]:
            return ORDER[0]
        for name in ORDER[1:4]:
            if delivered[name] < sizes[name]:
                return name
        if delivered[ORDER[4]] < sizes[ORDER[4]]:
            return ORDER[4]
        if p3_blocked:
            return None
        if delivered[ORDER[5]] < sizes[ORDER[5]]:
            return ORDER[5]
        if delivered[ORDER[6]] < sizes[ORDER[6]]:
            return ORDER[6]
        return None

    for i, ((start, end), cap) in enumerate(zip(merged, capacities)):
        if completion_us is not None:
            break
        if cap <= 0:
            continue

        left = cap
        used = 0
        touched = False
        while left:
            obj = next_object()
            if obj is None:
                break

            if (
                obj == "transition_proof_signature"
                and disruption == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT"
                and not a2
            ):
                a2 = True
                touched = True
                left = 0
                break

            if obj == "new_epoch_commit_signature":
                if policy == "P3_CONTACT_AWARE_STAGED" and not p3_blocked:
                    required = (
                        sizes["new_epoch_commit_signature"] - delivered["new_epoch_commit_signature"]
                        + sizes["post_commit_confirmation_signature"]
                        - delivered["post_commit_confirmation_signature"]
                    )
                    remaining_capacity = left + sum(capacities[i + 1 :])
                    if remaining_capacity < required:
                        p3_blocked = True
                        touched = True
                        left = 0
                        break

                if disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT" and not a3:
                    a3 = True
                    attempts += 1
                    touched = True
                    left = 0
                    break

            amount = min(sizes[obj] - delivered[obj], left)
            if amount <= 0:
                raise AssertionError("reference non-positive transfer")
            left -= amount
            used += amount
            bytes_transferred += amount
            touched = True

            if (
                disruption == "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT"
                and obj == a1_target
                and not a1
            ):
                a1 = True
            else:
                delivered[obj] += amount

            if delivered[obj] != sizes[obj]:
                continue

            when = _event_us(start, used, rate_bps)
            if when > end:
                raise AssertionError("reference event beyond window")
            if obj == "transition_proof_signature":
                proof_us = when
            elif obj == "new_epoch_commit_signature":
                attempts += 1
                commit_us = when
            elif obj == "post_commit_confirmation_signature":
                completion_us = when
                break

        opportunities += int(touched)

    success = completion_us is not None and completion_us < horizon_us

    if success:
        terminal = "TRUST_RESTORED"
    elif commit_us is not None and delivered["post_commit_confirmation_signature"] < sizes[
        "post_commit_confirmation_signature"
    ]:
        terminal = "EPOCH_DIVERGENCE"
    else:
        precommit = ORDER[:6]
        if any(delivered[name] < sizes[name] for name in precommit):
            terminal = "CONTACT_BUDGET_EXHAUSTED" if p3_blocked else "INSUFFICIENT_MATERIAL_TRANSFER"
        else:
            terminal = "RECOVERY_DEADLINE_EXCEEDED"

    legacy = 0 if policy == "P0_HARD_CUTOVER" else (
        horizon_us if commit_us is None else min(commit_us, horizon_us)
    )
    unavailable = (
        horizon_us if commit_us is None else min(commit_us, horizon_us)
    ) if policy == "P0_HARD_CUTOVER" else 0
    if policy == "P2_HYBRID_OVERLAP" and proof_us is not None:
        overlap_end = horizon_us if commit_us is None else min(commit_us, horizon_us)
        overlap = max(0, overlap_end - proof_us)
    else:
        overlap = 0

    return {
        "profile": profile,
        "policy": policy,
        "disruption": disruption,
        "horizon_us": horizon_us,
        "rate_bps": rate_bps,
        "trusted_recovery_success": int(success),
        "recovery_completion_us": "" if completion_us is None else completion_us,
        "observation_opportunities_consumed": opportunities,
        "cryptographic_bytes_transferred": bytes_transferred,
        "transition_attempts": attempts,
        "legacy_exposure_us": legacy,
        "control_unavailable_us": unavailable,
        "dual_epoch_overlap_us": overlap,
        "rollback_invoked": 0,
        "stale_epoch_acceptance": 0,
        "terminal_state": terminal,
        "proof_accepted_us": "" if proof_us is None else proof_us,
        "commit_us": "" if commit_us is None else commit_us,
        "p3_guard_blocked": int(p3_blocked),
    }


if __name__ == "__main__":
    raise SystemExit(
        "Study 8E independent reference is fixture-only; canonical external-trace audit execution is not authorized."
    )
