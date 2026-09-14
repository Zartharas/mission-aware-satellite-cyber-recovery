from __future__ import annotations

from itertools import combinations, product
import sys
from typing import Mapping

from .contracts import REQUIRED_VARIABLES, load_frozen_contracts


def _selectors():
    contracts = load_frozen_contracts()
    src = contracts.repo_root / "study2" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from study2_security import selectors

    return selectors


def _validate(known: Mapping[str, bool], unresolved: tuple[str, ...]) -> None:
    if set(known) & set(unresolved):
        raise ValueError("known and unresolved overlap")
    if set(known) | set(unresolved) != set(REQUIRED_VARIABLES):
        raise ValueError("known and unresolved must partition all required variables")
    if len(unresolved) != len(set(unresolved)):
        raise ValueError("duplicate unresolved variable")
    if any(type(value) is not bool for value in known.values()):
        raise ValueError("known values must be boolean")


def _states_recursive(
    known: Mapping[str, bool],
    unresolved: tuple[str, ...],
    index: int = 0,
) -> tuple[dict[str, bool], ...]:
    if index == len(unresolved):
        return ({name: known[name] for name in REQUIRED_VARIABLES},)
    name = unresolved[index]
    rows: list[dict[str, bool]] = []
    for value in (False, True):
        next_known = dict(known)
        next_known[name] = value
        rows.extend(_states_recursive(next_known, unresolved, index + 1))
    return tuple(rows)


def audit_reachable_actions(
    policy,
    *,
    known: Mapping[str, bool],
    unresolved: tuple[str, ...],
) -> frozenset[str]:
    _validate(known, unresolved)
    selectors = _selectors()
    if not isinstance(policy, selectors.Study2Policy):
        policy = selectors.Study2Policy(policy)
    actions: set[str] = set()
    for state in _states_recursive(dict(known), unresolved):
        obs = selectors.ObservationSummary(**state)
        actions.add(selectors.select_action(policy, obs).value)
    return frozenset(actions)


def audit_minimal_sidecar_sets(
    policy,
    *,
    known: Mapping[str, bool],
    unresolved: tuple[str, ...],
    actual_unresolved_values: Mapping[str, bool],
) -> tuple[tuple[str, ...], ...]:
    """Independent assignment-conditioned synthetic helper."""
    _validate(known, unresolved)
    if set(actual_unresolved_values) != set(unresolved):
        raise ValueError("actual values must exactly match unresolved variables")
    for size in range(len(unresolved) + 1):
        winners: list[tuple[str, ...]] = []
        for subset in combinations(unresolved, size):
            next_known = dict(known)
            for name in subset:
                next_known[name] = actual_unresolved_values[name]
            remaining = tuple(name for name in unresolved if name not in subset)
            if len(audit_reachable_actions(policy, known=next_known, unresolved=remaining)) == 1:
                winners.append(subset)
        if winners:
            return tuple(winners)
    raise RuntimeError("full revelation should always identify one deterministic action")


def audit_guaranteed_minimal_sidecar_sets(
    policy,
    *,
    known: Mapping[str, bool],
    unresolved: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    """Independent guaranteed-sidecar reconstruction without actual missing values."""
    _validate(known, unresolved)
    for size in range(len(unresolved) + 1):
        winners: list[tuple[str, ...]] = []
        for subset in combinations(unresolved, size):
            sufficient_for_every_assignment = True
            for bits in product((False, True), repeat=len(subset)):
                next_known = dict(known)
                next_known.update(dict(zip(subset, bits, strict=True)))
                remaining = tuple(name for name in unresolved if name not in subset)
                if len(
                    audit_reachable_actions(
                        policy,
                        known=next_known,
                        unresolved=remaining,
                    )
                ) != 1:
                    sufficient_for_every_assignment = False
                    break
            if sufficient_for_every_assignment:
                winners.append(subset)
        if winners:
            return tuple(winners)
    raise RuntimeError("full revelation should always identify one deterministic action")
