from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping

from .contracts import REQUIRED_VARIABLES


@dataclass(frozen=True)
class PartialObservation:
    known: tuple[tuple[str, bool], ...]
    unresolved: tuple[str, ...]

    @classmethod
    def build(
        cls,
        *,
        known: Mapping[str, bool],
        unresolved: Iterable[str],
    ) -> "PartialObservation":
        known_dict = dict(known)
        unresolved_tuple = tuple(unresolved)
        _validate_partial(known_dict, unresolved_tuple)
        return cls(
            known=tuple((name, known_dict[name]) for name in REQUIRED_VARIABLES if name in known_dict),
            unresolved=tuple(name for name in REQUIRED_VARIABLES if name in unresolved_tuple),
        )

    def known_dict(self) -> dict[str, bool]:
        return dict(self.known)


def _validate_bool_mapping(name: str, values: Mapping[str, bool]) -> None:
    unknown = set(values) - set(REQUIRED_VARIABLES)
    if unknown:
        raise ValueError(f"{name} contains unknown variables: {sorted(unknown)}")
    non_bool = [key for key, value in values.items() if type(value) is not bool]
    if non_bool:
        raise ValueError(f"{name} contains non-boolean values: {sorted(non_bool)}")


def _validate_partial(known: Mapping[str, bool], unresolved: tuple[str, ...]) -> None:
    _validate_bool_mapping("known", known)
    if len(unresolved) != len(set(unresolved)):
        raise ValueError("unresolved variables contain duplicates")
    unknown = set(unresolved) - set(REQUIRED_VARIABLES)
    if unknown:
        raise ValueError(f"unresolved contains unknown variables: {sorted(unknown)}")
    overlap = set(known) & set(unresolved)
    if overlap:
        raise ValueError(f"known/unresolved overlap: {sorted(overlap)}")
    covered = set(known) | set(unresolved)
    missing = set(REQUIRED_VARIABLES) - covered
    if missing:
        raise ValueError(f"partial observation does not cover all required variables: {sorted(missing)}")


def enumerate_admissible_states(
    partial: PartialObservation,
) -> tuple[dict[str, bool], ...]:
    known = partial.known_dict()
    unresolved = partial.unresolved
    output: list[dict[str, bool]] = []
    for bits in product((False, True), repeat=len(unresolved)):
        assignment = dict(zip(unresolved, bits, strict=True))
        state = {name: known.get(name, assignment.get(name)) for name in REQUIRED_VARIABLES}
        if any(type(value) is not bool for value in state.values()):
            raise ValueError("completion failed to produce a complete boolean state")
        output.append(state)
    return tuple(output)


def reveal_values(
    partial: PartialObservation,
    revealed: Mapping[str, bool],
) -> PartialObservation:
    _validate_bool_mapping("revealed", revealed)
    if not set(revealed).issubset(set(partial.unresolved)):
        raise ValueError("revealed values must be a subset of unresolved variables")
    known = partial.known_dict()
    known.update(revealed)
    unresolved = tuple(name for name in partial.unresolved if name not in revealed)
    return PartialObservation.build(known=known, unresolved=unresolved)
