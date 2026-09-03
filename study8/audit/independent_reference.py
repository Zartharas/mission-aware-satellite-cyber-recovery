from __future__ import annotations

from typing import Mapping

OBJECTS = (
    "recovery_authority_assertion_signature",
    "successor_kem_encapsulation_key",
    "successor_signature_verification_key",
    "kem_ciphertext",
    "transition_proof_signature",
    "new_epoch_commit_signature",
    "post_commit_confirmation_signature",
)

SIZES = {
    "PROFILE_512_44": (2420, 800, 1312, 768, 2420, 2420, 2420),
    "PROFILE_768_65": (3309, 1184, 1952, 1088, 3309, 3309, 3309),
    "PROFILE_1024_87": (4627, 1568, 2592, 1568, 4627, 4627, 4627),
}

CONTACTS = {
    "R1_FREQUENT_SMALL": (4096, (0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44)),
    "R2_PERIODIC_MEDIUM": (8192, (0, 5, 11, 17, 23, 29, 35, 41)),
    "R3_SPARSE_LARGE": (16384, (0, 11, 23, 37)),
    "R4_CLUSTERED_MEDIUM": (8192, (0, 1, 13, 14, 29, 30, 44, 45)),
}


def _schedule(regime: str, phase: int) -> list[tuple[int, int]]:
    capacity, slots = CONTACTS[regime]
    return sorted((((slot - phase) % 48), capacity) for slot in slots)


def _largest(profile: str) -> int:
    values = SIZES[profile]
    maximum = max(values)
    return next(i for i, size in enumerate(values) if size == maximum)


def independently_recompute_case(factors: Mapping[str, object]) -> dict[str, object]:
    profile = str(factors["profile"])
    policy = str(factors["policy"])
    regime = str(factors["regime"])
    disruption = str(factors["disruption"])
    phase = int(factors["phase_offset"])
    deadline = int(factors["deadline"])

    if profile not in SIZES:
        raise ValueError("unknown profile")
    if regime not in CONTACTS:
        raise ValueError("unknown regime")
    if policy not in {
        "P0_HARD_CUTOVER",
        "P1_STAGED_CUTOVER",
        "P2_HYBRID_OVERLAP",
        "P3_CONTACT_AWARE_STAGED",
    }:
        raise ValueError("unknown policy")
    if disruption not in {
        "A0_NONE",
        "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
        "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
        "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
    }:
        raise ValueError("unknown disruption")
    if phase not in range(6) or deadline not in {12, 24, 48}:
        raise ValueError("invalid factor")

    sizes = SIZES[profile]
    delivered = [0] * len(OBJECTS)
    tx_bytes = 0
    contacts_consumed = 0
    attempts = 0
    lost_once = False
    delay_once = False
    replay_once = False
    guard_blocked = False
    proof_slot = None
    commit_slot = None
    completion_slot = None
    largest_index = _largest(profile)
    schedule = _schedule(regime, phase)

    def next_index() -> int | None:
        if delivered[0] < sizes[0]:
            return 0
        if any(delivered[i] < sizes[i] for i in (1, 2, 3)):
            return next(i for i in (1, 2, 3) if delivered[i] < sizes[i])
        if delivered[4] < sizes[4]:
            return 4
        if guard_blocked:
            return None
        if delivered[5] < sizes[5]:
            return 5
        if delivered[6] < sizes[6]:
            return 6
        return None

    for pos, (slot, capacity) in enumerate(schedule):
        if slot >= deadline or completion_slot is not None:
            continue
        remaining = capacity
        touched = False

        while remaining:
            idx = next_index()
            if idx is None:
                break

            if idx == 4 and disruption == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT" and not delay_once:
                delay_once = True
                touched = True
                remaining = 0
                break

            if idx == 5:
                if policy == "P3_CONTACT_AWARE_STAGED":
                    needed = (sizes[5] - delivered[5]) + (sizes[6] - delivered[6])
                    nominal = remaining + sum(c for s, c in schedule[pos + 1 :] if s < deadline)
                    if nominal < needed:
                        guard_blocked = True
                        touched = True
                        remaining = 0
                        break
                if disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT" and not replay_once:
                    replay_once = True
                    attempts += 1
                    touched = True
                    remaining = 0
                    break

            amount = min(sizes[idx] - delivered[idx], remaining)
            if amount <= 0:
                raise AssertionError("invalid amount")
            tx_bytes += amount
            remaining -= amount
            touched = True

            if (
                disruption == "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT"
                and idx == largest_index
                and not lost_once
            ):
                lost_once = True
            else:
                delivered[idx] += amount

            if delivered[idx] == sizes[idx]:
                if idx == 4:
                    proof_slot = slot
                elif idx == 5:
                    attempts += 1
                    commit_slot = slot
                elif idx == 6:
                    completion_slot = slot
                    break

        contacts_consumed += int(touched)

    success = completion_slot is not None and completion_slot < deadline

    if success:
        terminal = "TRUST_RESTORED"
    elif commit_slot is not None and delivered[6] < sizes[6]:
        terminal = "EPOCH_DIVERGENCE"
    elif guard_blocked:
        terminal = "CONTACT_BUDGET_EXHAUSTED"
    elif any(delivered[i] < sizes[i] for i in range(6)):
        terminal = "INSUFFICIENT_MATERIAL_TRANSFER"
    else:
        terminal = "RECOVERY_DEADLINE_EXCEEDED"

    legacy = 0 if policy == "P0_HARD_CUTOVER" else (
        deadline if commit_slot is None else min(commit_slot, deadline)
    )
    unavailable = 0 if policy != "P0_HARD_CUTOVER" else (
        deadline if commit_slot is None else min(commit_slot, deadline)
    )
    if policy == "P2_HYBRID_OVERLAP" and proof_slot is not None:
        overlap_end = deadline if commit_slot is None else min(commit_slot, deadline)
        dual_overlap = max(0, overlap_end - proof_slot)
    else:
        dual_overlap = 0

    return {
        "profile": profile,
        "policy": policy,
        "regime": regime,
        "disruption": disruption,
        "phase_offset": phase,
        "deadline": deadline,
        "trusted_recovery_success": int(success),
        "recovery_completion_slot": "" if completion_slot is None else completion_slot,
        "contacts_consumed": contacts_consumed,
        "cryptographic_bytes_transferred": tx_bytes,
        "transition_attempts": attempts,
        "legacy_exposure_slots": legacy,
        "control_unavailable_slots": unavailable,
        "dual_epoch_overlap_slots": dual_overlap,
        "rollback_invoked": 0,
        "stale_epoch_acceptance": 0,
        "terminal_state": terminal,
        "proof_accepted_slot": "" if proof_slot is None else proof_slot,
        "commit_slot": "" if commit_slot is None else commit_slot,
    }


def audit_observation(observation: Mapping[str, object]) -> tuple[bool, tuple[str, ...]]:
    expected = independently_recompute_case(observation)
    mismatches = tuple(key for key, value in expected.items() if observation.get(key) != value)
    return (not mismatches, mismatches)


if __name__ == "__main__":
    raise SystemExit(
        "Phase 8.1 independent auditor is construction-only; artifact audit execution is not authorized."
    )
