from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .completions import PartialObservation
from .contracts import FROZEN_DATASET_IDS, REQUIRED_VARIABLES


@dataclass(frozen=True)
class NativeStateGroup:
    dataset_id: str
    known: tuple[tuple[str, bool], ...]
    unresolved: tuple[str, ...]
    multiplicity: int

    def partial_observation(self) -> PartialObservation:
        return PartialObservation.build(known=dict(self.known), unresolved=self.unresolved)


def _validate_partial_for_grouping(partial: PartialObservation) -> None:
    known = partial.known_dict()
    if any(type(value) is not bool for value in known.values()):
        raise ValueError("native-state grouping requires boolean known values")
    if set(known) | set(partial.unresolved) != set(REQUIRED_VARIABLES):
        raise ValueError("native-state grouping requires a complete known/unresolved partition")
    if set(known) & set(partial.unresolved):
        raise ValueError("native-state grouping cannot overlap known and unresolved variables")


def _group_sort_key(item: tuple[tuple[tuple[str, bool], ...], tuple[str, ...]]) -> tuple[int, ...]:
    known_tuple, unresolved = item
    known = dict(known_tuple)
    unresolved_set = set(unresolved)
    encoded: list[int] = []
    for name in REQUIRED_VARIABLES:
        if name in unresolved_set:
            encoded.append(0)
        elif known[name] is False:
            encoded.append(1)
        else:
            encoded.append(2)
    return tuple(encoded)


def collapse_native_states(
    dataset_id: str,
    partials: Iterable[PartialObservation],
    *,
    expected_row_count: int,
) -> tuple[NativeStateGroup, ...]:
    """Losslessly collapse selector-equivalent rows with exact integer multiplicity."""
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    if type(expected_row_count) is not int or expected_row_count < 0:
        raise ValueError("expected_row_count must be a non-negative integer")

    counts: Counter[tuple[tuple[tuple[str, bool], ...], tuple[str, ...]]] = Counter()
    observed_rows = 0
    for partial in partials:
        _validate_partial_for_grouping(partial)
        key = (partial.known, partial.unresolved)
        counts[key] += 1
        observed_rows += 1

    if observed_rows != expected_row_count:
        raise ValueError(
            f"native-state multiplicity conservation failed: "
            f"observed={observed_rows} expected={expected_row_count}"
        )

    groups = tuple(
        NativeStateGroup(
            dataset_id=dataset_id,
            known=known,
            unresolved=unresolved,
            multiplicity=counts[(known, unresolved)],
        )
        for known, unresolved in sorted(counts, key=_group_sort_key)
    )
    if any(type(group.multiplicity) is not int or group.multiplicity <= 0 for group in groups):
        raise ValueError("native-state group multiplicities must be positive integers")
    if sum(group.multiplicity for group in groups) != expected_row_count:
        raise ValueError("native-state group multiplicities do not reconstruct the source row count")
    return groups
