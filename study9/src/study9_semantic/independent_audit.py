from __future__ import annotations

from collections import Counter
from itertools import combinations, product
import sys
from typing import Iterable, Mapping

from .completions import PartialObservation
from .contracts import FROZEN_DATASET_IDS, PRIMARY_POLICY_VALUES, REQUIRED_VARIABLES, load_frozen_contracts


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


def _audit_group_sort_key(
    item: tuple[tuple[tuple[str, bool], ...], tuple[str, ...]],
) -> tuple[int, ...]:
    known_tuple, unresolved = item
    known = dict(known_tuple)
    unresolved_set = set(unresolved)
    key: list[int] = []
    for name in REQUIRED_VARIABLES:
        if name in unresolved_set:
            key.append(0)
        elif known[name] is False:
            key.append(1)
        else:
            key.append(2)
    return tuple(key)


def audit_collapse_native_states(
    dataset_id: str,
    partials: Iterable[PartialObservation],
    *,
    expected_row_count: int,
) -> tuple[dict[str, object], ...]:
    """Independently reconstruct native-state multiplicities without state_groups.py."""
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    if type(expected_row_count) is not int or expected_row_count < 0:
        raise ValueError("expected_row_count must be a non-negative integer")

    counter: Counter[tuple[tuple[tuple[str, bool], ...], tuple[str, ...]]] = Counter()
    row_count = 0
    for partial in partials:
        known = partial.known_dict()
        unresolved = tuple(partial.unresolved)
        _validate(known, unresolved)
        ordered_known = tuple((name, known[name]) for name in REQUIRED_VARIABLES if name in known)
        ordered_unresolved = tuple(name for name in REQUIRED_VARIABLES if name in unresolved)
        counter[(ordered_known, ordered_unresolved)] += 1
        row_count += 1

    if row_count != expected_row_count:
        raise ValueError(
            f"audit multiplicity conservation failed: observed={row_count} expected={expected_row_count}"
        )
    groups = tuple(
        {
            "dataset_id": dataset_id,
            "known": known,
            "unresolved": unresolved,
            "multiplicity": counter[(known, unresolved)],
        }
        for known, unresolved in sorted(counter, key=_audit_group_sort_key)
    )
    if sum(int(group["multiplicity"]) for group in groups) != expected_row_count:
        raise ValueError("audit group multiplicities do not reconstruct source row count")
    return groups


def _audit_ordered_actions(actions: frozenset[str]) -> list[str]:
    selectors = _selectors()
    order = {action.value: index for index, action in enumerate(selectors.Study2Action)}
    if set(actions) - set(order):
        raise ValueError("independent audit observed an unknown selector action")
    return sorted(actions, key=order.__getitem__)


def audit_analyze_native_state_groups(
    dataset_id: str,
    groups: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    """Independently reconstruct primary policy endpoint summaries."""
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    group_tuple = tuple(groups)
    if not group_tuple:
        raise ValueError("independent audit requires at least one native-state group")
    selectors = _selectors()
    policies = tuple(selectors.Study2Policy(value) for value in PRIMARY_POLICY_VALUES)
    source_row_count = sum(int(group["multiplicity"]) for group in group_tuple)

    strata: list[dict[str, object]] = []
    for policy in policies:
        group_results: list[dict[str, object]] = []
        unique_rows = 0
        for index, group in enumerate(group_tuple):
            if group["dataset_id"] != dataset_id:
                raise ValueError("cross-dataset group entered independent audit")
            known = dict(group["known"])
            unresolved = tuple(group["unresolved"])
            multiplicity = int(group["multiplicity"])
            _validate(known, unresolved)
            if multiplicity <= 0:
                raise ValueError("audit multiplicity must be positive")
            actions = audit_reachable_actions(policy, known=known, unresolved=unresolved)
            ordered_actions = _audit_ordered_actions(actions)
            sidecars = audit_guaranteed_minimal_sidecar_sets(
                policy,
                known=known,
                unresolved=unresolved,
            )
            sidecar_cardinality = len(sidecars[0])
            unique = len(ordered_actions) == 1
            if unique:
                unique_rows += multiplicity
            group_results.append(
                {
                    "group_index": index,
                    "multiplicity": multiplicity,
                    "reachable_actions": ordered_actions,
                    "action_set_cardinality": len(ordered_actions),
                    "unique_action": unique,
                    "guaranteed_sidecar_cardinality": sidecar_cardinality,
                    "guaranteed_sidecar_sets": [list(item) for item in sidecars],
                }
            )
        strata.append(
            {
                "dataset_id": dataset_id,
                "policy": policy.value,
                "source_row_count": source_row_count,
                "native_state_group_count": len(group_tuple),
                "unique_action_fraction": {
                    "numerator": unique_rows,
                    "denominator": source_row_count,
                },
                "group_results": group_results,
            }
        )

    return {
        "dataset_id": dataset_id,
        "source_row_count": source_row_count,
        "native_state_group_count": len(group_tuple),
        "groups": [
            {
                "dataset_id": dataset_id,
                "known": [
                    {"variable": name, "value": value}
                    for name, value in tuple(group["known"])
                ],
                "unresolved": list(tuple(group["unresolved"])),
                "multiplicity": int(group["multiplicity"]),
            }
            for group in group_tuple
        ],
        "policy_strata": strata,
    }
