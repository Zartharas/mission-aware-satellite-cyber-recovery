from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .contracts import (
    FROZEN_DATASET_IDS,
    REQUIRED_VARIABLES,
    FrozenContracts,
    load_frozen_contracts,
)


@dataclass(frozen=True)
class MappingRecord:
    dataset_id: str
    recovery_state_variable: str
    mapping_class: str
    evidence_visibility_role: str
    native_field_names: tuple[str, ...]
    derivation_rule_if_any: str | None
    semantic_rationale: str
    uncertainty_or_ambiguity_note: str | None
    value_rule: str | None
    excluded_fields: tuple[str, ...]
    excluded_as_substitutes: tuple[str, ...]


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("expected list[str]")
    return tuple(value)


def materialize_mapping_matrix(
    contracts: FrozenContracts | None = None,
) -> tuple[MappingRecord, ...]:
    frozen = contracts or load_frozen_contracts()
    rows: list[MappingRecord] = []
    for dataset in frozen.semantic["dataset_contracts"]:
        dataset_id = dataset["dataset_id"]
        for item in dataset["variable_contracts"]:
            mapping_class = item["frozen_mapping_class"]
            derivation_rule = item.get("derivation_rule_if_any")
            if mapping_class == "DERIVABLE_BY_PREDECLARED_RULE" and not derivation_rule:
                raise ValueError("DERIVABLE mapping lacks frozen derivation rule")
            if mapping_class != "DERIVABLE_BY_PREDECLARED_RULE" and derivation_rule:
                raise ValueError("non-DERIVABLE mapping unexpectedly carries derivation rule")
            rows.append(
                MappingRecord(
                    dataset_id=dataset_id,
                    recovery_state_variable=item["recovery_state_variable"],
                    mapping_class=mapping_class,
                    evidence_visibility_role=item["evidence_visibility_role"],
                    native_field_names=_as_tuple(item.get("native_field_names", [])),
                    derivation_rule_if_any=derivation_rule,
                    semantic_rationale=item["rationale"],
                    uncertainty_or_ambiguity_note=item.get("uncertainty_or_ambiguity_note"),
                    value_rule=item.get("value_rule"),
                    excluded_fields=_as_tuple(item.get("excluded_fields", [])),
                    excluded_as_substitutes=_as_tuple(item.get("excluded_as_substitutes", [])),
                )
            )

    expected_pairs = {
        (dataset_id, variable)
        for dataset_id in FROZEN_DATASET_IDS
        for variable in REQUIRED_VARIABLES
    }
    observed_pairs = {(row.dataset_id, row.recovery_state_variable) for row in rows}
    if observed_pairs != expected_pairs or len(rows) != len(expected_pairs):
        raise ValueError("frozen mapping matrix is not the exact 3 x 8 design")
    return tuple(rows)


def records_for_dataset(
    dataset_id: str,
    records: Iterable[MappingRecord] | None = None,
) -> tuple[MappingRecord, ...]:
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    source = tuple(records) if records is not None else materialize_mapping_matrix()
    selected = tuple(row for row in source if row.dataset_id == dataset_id)
    if tuple(row.recovery_state_variable for row in selected) != REQUIRED_VARIABLES:
        raise ValueError(f"dataset mapping is incomplete or reordered: {dataset_id}")
    return selected
