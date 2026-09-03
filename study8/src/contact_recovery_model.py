from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

PROFILE_OBJECTS = {
    "PROFILE_512_44": {
        "recovery_authority_assertion_signature": 2420,
        "successor_kem_encapsulation_key": 800,
        "successor_signature_verification_key": 1312,
        "kem_ciphertext": 768,
        "transition_proof_signature": 2420,
        "new_epoch_commit_signature": 2420,
        "post_commit_confirmation_signature": 2420,
    },
    "PROFILE_768_65": {
        "recovery_authority_assertion_signature": 3309,
        "successor_kem_encapsulation_key": 1184,
        "successor_signature_verification_key": 1952,
        "kem_ciphertext": 1088,
        "transition_proof_signature": 3309,
        "new_epoch_commit_signature": 3309,
        "post_commit_confirmation_signature": 3309,
    },
    "PROFILE_1024_87": {
        "recovery_authority_assertion_signature": 4627,
        "successor_kem_encapsulation_key": 1568,
        "successor_signature_verification_key": 2592,
        "kem_ciphertext": 1568,
        "transition_proof_signature": 4627,
        "new_epoch_commit_signature": 4627,
        "post_commit_confirmation_signature": 4627,
    },
}

OBJECT_PRIORITY = (
    "recovery_authority_assertion_signature",
    "successor_kem_encapsulation_key",
    "successor_signature_verification_key",
    "kem_ciphertext",
    "transition_proof_signature",
    "new_epoch_commit_signature",
    "post_commit_confirmation_signature",
)

BASE_CONTACTS = {
    "R1_FREQUENT_SMALL": (
        4096,
        (0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44),
    ),
    "R2_PERIODIC_MEDIUM": (
        8192,
        (0, 5, 11, 17, 23, 29, 35, 41),
    ),
    "R3_SPARSE_LARGE": (
        16384,
        (0, 11, 23, 37),
    ),
    "R4_CLUSTERED_MEDIUM": (
        8192,
        (0, 1, 13, 14, 29, 30, 44, 45),
    ),
}

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

DEADLINES = (12, 24, 48)
PHASE_OFFSETS = (0, 1, 2, 3, 4, 5)


@dataclass(frozen=True)
class Case:
    profile: str
    policy: str
    regime: str
    disruption: str
    phase_offset: int
    deadline: int


@dataclass
class MutableRun:
    delivered: dict[str, int]
    cryptographic_bytes_transferred: int = 0
    contacts_consumed: int = 0
    transition_attempts: int = 0
    a1_used: bool = False
    a2_used: bool = False
    a3_used: bool = False
    proof_accepted_slot: int | None = None
    commit_slot: int | None = None
    completion_slot: int | None = None
    p3_guard_blocked: bool = False
    stale_epoch_acceptance: bool = False
    rollback_invoked: bool = False


def materialize_contacts(regime: str, phase_offset: int) -> tuple[tuple[int, int], ...]:
    if regime not in BASE_CONTACTS:
        raise ValueError(f"unknown contact regime: {regime}")
    if phase_offset not in PHASE_OFFSETS:
        raise ValueError(f"invalid phase offset: {phase_offset}")
    capacity, base_slots = BASE_CONTACTS[regime]
    effective = sorted(((slot - phase_offset) % 48, capacity) for slot in base_slots)
    return tuple(effective)


def validate_case(case: Case) -> None:
    if case.profile not in PROFILE_OBJECTS:
        raise ValueError(f"unknown profile: {case.profile}")
    if case.policy not in POLICIES:
        raise ValueError(f"unknown policy: {case.policy}")
    if case.regime not in BASE_CONTACTS:
        raise ValueError(f"unknown regime: {case.regime}")
    if case.disruption not in DISRUPTIONS:
        raise ValueError(f"unknown disruption: {case.disruption}")
    if case.phase_offset not in PHASE_OFFSETS:
        raise ValueError(f"invalid phase offset: {case.phase_offset}")
    if case.deadline not in DEADLINES:
        raise ValueError(f"invalid deadline: {case.deadline}")


def factor_population() -> tuple[Case, ...]:
    rows = []
    for profile in PROFILE_OBJECTS:
        for policy in POLICIES:
            for regime in BASE_CONTACTS:
                for disruption in DISRUPTIONS:
                    for phase_offset in PHASE_OFFSETS:
                        for deadline in DEADLINES:
                            rows.append(
                                Case(
                                    profile=profile,
                                    policy=policy,
                                    regime=regime,
                                    disruption=disruption,
                                    phase_offset=phase_offset,
                                    deadline=deadline,
                                )
                            )
    return tuple(rows)


def _bundle_staged(delivered: Mapping[str, int], sizes: Mapping[str, int]) -> bool:
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
    contacts: Sequence[tuple[int, int]],
    *,
    contact_index: int,
    current_remaining: int,
    deadline: int,
) -> int:
    total = current_remaining
    for slot, capacity in contacts[contact_index + 1 :]:
        if slot < deadline:
            total += capacity
    return total


def _terminal_state(
    *,
    run: MutableRun,
    sizes: Mapping[str, int],
    deadline: int,
) -> str:
    if run.stale_epoch_acceptance:
        return "STALE_EPOCH_ACCEPTED"

    commit = "new_epoch_commit_signature"
    confirmation = "post_commit_confirmation_signature"

    if run.commit_slot is not None and run.delivered[confirmation] < sizes[confirmation]:
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


def _legacy_exposure_slots(policy: str, commit_slot: int | None, deadline: int) -> int:
    if policy == "P0_HARD_CUTOVER":
        return 0
    return deadline if commit_slot is None else min(commit_slot, deadline)


def _control_unavailable_slots(policy: str, commit_slot: int | None, deadline: int) -> int:
    if policy != "P0_HARD_CUTOVER":
        return 0
    return deadline if commit_slot is None else min(commit_slot, deadline)


def _dual_epoch_overlap_slots(
    policy: str,
    proof_slot: int | None,
    commit_slot: int | None,
    deadline: int,
) -> int:
    if policy != "P2_HYBRID_OVERLAP" or proof_slot is None:
        return 0
    end = deadline if commit_slot is None else min(commit_slot, deadline)
    return max(0, end - proof_slot)


def evaluate_case(case: Case) -> dict[str, object]:
    validate_case(case)
    sizes = PROFILE_OBJECTS[case.profile]
    contacts = materialize_contacts(case.regime, case.phase_offset)
    run = MutableRun(delivered={name: 0 for name in OBJECT_PRIORITY})
    a1_target = _a1_target(sizes)

    for contact_index, (slot, capacity) in enumerate(contacts):
        if slot >= case.deadline:
            continue
        if run.completion_slot is not None:
            break

        remaining = capacity
        contact_touched = False

        while remaining > 0:
            ready = _ready_object(
                run.delivered,
                sizes,
                p3_guard_blocked=run.p3_guard_blocked,
            )
            if ready is None:
                break

            if ready == "transition_proof_signature":
                if case.disruption == "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT" and not run.a2_used:
                    run.a2_used = True
                    contact_touched = True
                    remaining = 0
                    break

            if ready == "new_epoch_commit_signature":
                if case.policy == "P3_CONTACT_AWARE_STAGED" and not run.p3_guard_blocked:
                    required = (
                        sizes["new_epoch_commit_signature"] - run.delivered["new_epoch_commit_signature"]
                        + sizes["post_commit_confirmation_signature"]
                        - run.delivered["post_commit_confirmation_signature"]
                    )
                    nominal = _remaining_nominal_capacity(
                        contacts,
                        contact_index=contact_index,
                        current_remaining=remaining,
                        deadline=case.deadline,
                    )
                    if nominal < required:
                        run.p3_guard_blocked = True
                        contact_touched = True
                        remaining = 0
                        break

                if case.disruption == "A3_STALE_EPOCH_REPLAY_AT_COMMIT" and not run.a3_used:
                    run.a3_used = True
                    run.transition_attempts += 1
                    contact_touched = True
                    remaining = 0
                    break

            need = sizes[ready] - run.delivered[ready]
            send = min(need, remaining)
            if send <= 0:
                raise AssertionError("non-positive transfer")

            run.cryptographic_bytes_transferred += send
            remaining -= send
            contact_touched = True

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

            if ready == "transition_proof_signature":
                run.proof_accepted_slot = slot

            elif ready == "new_epoch_commit_signature":
                run.transition_attempts += 1
                run.commit_slot = slot

            elif ready == "post_commit_confirmation_signature":
                run.completion_slot = slot
                break

        if contact_touched:
            run.contacts_consumed += 1

    success = (
        run.completion_slot is not None
        and run.completion_slot < case.deadline
        and not run.stale_epoch_acceptance
    )
    terminal = "TRUST_RESTORED" if success else _terminal_state(
        run=run,
        sizes=sizes,
        deadline=case.deadline,
    )

    return {
        "profile": case.profile,
        "policy": case.policy,
        "regime": case.regime,
        "disruption": case.disruption,
        "phase_offset": case.phase_offset,
        "deadline": case.deadline,
        "trusted_recovery_success": int(success),
        "recovery_completion_slot": "" if run.completion_slot is None else run.completion_slot,
        "contacts_consumed": run.contacts_consumed,
        "cryptographic_bytes_transferred": run.cryptographic_bytes_transferred,
        "transition_attempts": run.transition_attempts,
        "legacy_exposure_slots": _legacy_exposure_slots(case.policy, run.commit_slot, case.deadline),
        "control_unavailable_slots": _control_unavailable_slots(case.policy, run.commit_slot, case.deadline),
        "dual_epoch_overlap_slots": _dual_epoch_overlap_slots(
            case.policy,
            run.proof_accepted_slot,
            run.commit_slot,
            case.deadline,
        ),
        "rollback_invoked": int(run.rollback_invoked),
        "stale_epoch_acceptance": int(run.stale_epoch_acceptance),
        "terminal_state": terminal,
        "proof_accepted_slot": "" if run.proof_accepted_slot is None else run.proof_accepted_slot,
        "commit_slot": "" if run.commit_slot is None else run.commit_slot,
    }


def development_fixture_cases() -> tuple[Case, ...]:
    return (
        Case("PROFILE_512_44", "P0_HARD_CUTOVER", "R1_FREQUENT_SMALL", "A0_NONE", 0, 12),
        Case("PROFILE_512_44", "P1_STAGED_CUTOVER", "R2_PERIODIC_MEDIUM", "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT", 1, 24),
        Case("PROFILE_768_65", "P2_HYBRID_OVERLAP", "R3_SPARSE_LARGE", "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT", 2, 48),
        Case("PROFILE_1024_87", "P3_CONTACT_AWARE_STAGED", "R4_CLUSTERED_MEDIUM", "A3_STALE_EPOCH_REPLAY_AT_COMMIT", 5, 24),
    )


if __name__ == "__main__":
    raise SystemExit(
        "Phase 8.1 is implementation-only; direct or canonical execution is not authorized."
    )
