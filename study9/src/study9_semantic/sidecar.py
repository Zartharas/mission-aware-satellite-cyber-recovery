from __future__ import annotations

from itertools import combinations
from typing import Mapping

from .completions import PartialObservation, enumerate_admissible_states, reveal_values
from .selector_adapter import select_action_from_state


def reachable_actions(policy, partial: PartialObservation) -> frozenset[str]:
    return frozenset(
        select_action_from_state(policy, state).value
        for state in enumerate_admissible_states(partial)
    )


def action_set_cardinality(policy, partial: PartialObservation) -> int:
    return len(reachable_actions(policy, partial))


def minimal_sidecar_sets(
    policy,
    partial: PartialObservation,
    actual_unresolved_values: Mapping[str, bool],
) -> tuple[tuple[str, ...], ...]:
    if set(actual_unresolved_values) != set(partial.unresolved):
        raise ValueError("actual_unresolved_values must provide every unresolved variable exactly once")
    if any(type(value) is not bool for value in actual_unresolved_values.values()):
        raise ValueError("sidecar values must be boolean")

    unresolved = partial.unresolved
    for size in range(len(unresolved) + 1):
        winners: list[tuple[str, ...]] = []
        for subset in combinations(unresolved, size):
            revealed = {name: actual_unresolved_values[name] for name in subset}
            candidate = reveal_values(partial, revealed)
            if action_set_cardinality(policy, candidate) == 1:
                winners.append(subset)
        if winners:
            return tuple(winners)
    raise RuntimeError("full revelation should always identify a deterministic selector action")
