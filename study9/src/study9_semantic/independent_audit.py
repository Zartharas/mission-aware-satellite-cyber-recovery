from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from itertools import combinations, product
import sys
from typing import Iterable, Mapping

from .completions import PartialObservation
from .contracts import (
    FROZEN_DATASET_IDS,
    PRIMARY_POLICY_VALUES,
    REQUIRED_VARIABLES,
    FrozenContracts,
    load_frozen_contracts,
)


@lru_cache(maxsize=1)
def _selectors():
    """Load and validate the frozen Study 2 selector once for the audit path."""
    contracts = load_frozen_contracts()
    src = contracts.repo_root / "study2" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from study2_security import selectors

    return selectors


@lru_cache(maxsize=None)
def _audit_select_action_cached(policy_value: str, state_values: tuple[bool, ...]) -> str:
    """Independent deterministic selector cache; does not use selector_adapter.py."""
    if len(state_values) != len(REQUIRED_VARIABLES):
        raise ValueError("audit cached state does not contain all required variables")
    selectors = _selectors()
    policy = selectors.Study2Policy(policy_value)
    obs = selectors.ObservationSummary(
        **dict(zip(REQUIRED_VARIABLES, state_values, strict=True))
    )
    return selectors.select_action(policy, obs).value


def clear_audit_caches() -> None:
    """Clear independent-audit caches for tests and process-boundary control."""
    _audit_select_action_cached.cache_clear()
    _selectors.cache_clear()


def _validate(known: Mapping[str, bool], unresolved: tuple[str, ...]) -> None:
    if set(known) & set(unresolved):
        raise ValueError("known and unresolved overlap")
    if set(known) | set(unresolved) != set(REQUIRED_VARIABLES):
        raise ValueError("known and unresolved must partition all required variables")
    if len(unresolved) != len(set(unresolved)):
        raise ValueError("duplicate unresolved variable")
    if any(type(value) is not bool for value in known.values()):
        raise ValueError("known values must be boolean")


def _audit_normalize_binary_numeric(value: object) -> bool:
    """Independent 0/1 normalization; does not call state_projection.py."""
    if isinstance(value, bool):
        raise ValueError("boolean source values are not accepted as numeric 0/1 evidence")
    text = str(value).strip()
    if not text:
        raise ValueError("direct recovery-state value is empty")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"direct recovery-state value is not numeric 0/1: {value!r}") from exc
    if not number.is_finite():
        raise ValueError(f"direct recovery-state value is not finite: {value!r}")
    if number == Decimal(0):
        return False
    if number == Decimal(1):
        return True
    raise ValueError(f"direct recovery-state value is outside frozen 0/1 domain: {value!r}")


def audit_project_native_row(
    dataset_id: str,
    row: Mapping[str, object],
    contracts: FrozenContracts | None = None,
) -> PartialObservation:
    """Independently reconstruct frozen native state directly from one raw row."""
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    frozen = contracts or load_frozen_contracts()
    dataset = next(
        item for item in frozen.semantic["dataset_contracts"] if item["dataset_id"] == dataset_id
    )

    known: dict[str, bool] = {}
    unresolved: list[str] = []
    for item in dataset["variable_contracts"]:
        variable = item["recovery_state_variable"]
        mapping_class = item["frozen_mapping_class"]
        if mapping_class == "DIRECT":
            fields = tuple(item.get("native_field_names", ()))
            if (
                dataset_id != "UNSW_IOTSAT_2026"
                or variable != "security_signal"
                or fields != ("Position_Anomaly",)
                or item.get("value_rule") != "0 -> false; 1 -> true"
            ):
                raise ValueError(
                    f"unexpected frozen DIRECT mapping in independent audit: {dataset_id}:{variable}"
                )
            if "Position_Anomaly" not in row:
                raise ValueError("independent audit missing frozen UNSW Position_Anomaly field")
            known[variable] = _audit_normalize_binary_numeric(row["Position_Anomaly"])
        elif mapping_class == "DERIVABLE_BY_PREDECLARED_RULE":
            raise ValueError(
                "independent audit encountered DERIVABLE mapping although frozen derivation registry is empty"
            )
        elif mapping_class in {"AMBIGUOUS", "ABSENT"}:
            unresolved.append(variable)
        else:
            raise ValueError(f"unknown frozen mapping class in independent audit: {mapping_class}")

    ordered_known = {name: known[name] for name in REQUIRED_VARIABLES if name in known}
    ordered_unresolved = tuple(name for name in REQUIRED_VARIABLES if name in unresolved)
    _validate(ordered_known, ordered_unresolved)
    return PartialObservation.build(known=ordered_known, unresolved=ordered_unresolved)


def audit_mapping_and_coverage(
    contracts: FrozenContracts | None = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Independently reconstruct policy-independent mapping and coverage endpoints."""
    frozen = contracts or load_frozen_contracts()
    mapping_record: list[dict[str, object]] = []
    per_dataset: list[dict[str, object]] = []
    unresolved_sets: list[set[str]] = []

    for dataset_id in FROZEN_DATASET_IDS:
        dataset = next(
            item for item in frozen.semantic["dataset_contracts"] if item["dataset_id"] == dataset_id
        )
        variable_rows = dataset["variable_contracts"]
        observed_order = tuple(item["recovery_state_variable"] for item in variable_rows)
        if observed_order != REQUIRED_VARIABLES:
            raise ValueError(f"independent mapping variable-order drift: {dataset_id}")

        direct = 0
        direct_or_derivable = 0
        unresolved: set[str] = set()
        for item in variable_rows:
            mapping_class = item["frozen_mapping_class"]
            role = item["evidence_visibility_role"]
            variable = item["recovery_state_variable"]
            mapping_record.append(
                {
                    "dataset_id": dataset_id,
                    "recovery_state_variable": variable,
                    "mapping_class": mapping_class,
                    "evidence_visibility_role": role,
                    "native_field_names": list(item.get("native_field_names", [])),
                    "derivation_rule_if_any": item.get("derivation_rule_if_any"),
                    "semantic_rationale": item["rationale"],
                    "uncertainty_or_ambiguity_note": item.get("uncertainty_or_ambiguity_note"),
                    "value_rule": item.get("value_rule"),
                    "excluded_fields": list(item.get("excluded_fields", [])),
                    "excluded_as_substitutes": list(item.get("excluded_as_substitutes", [])),
                }
            )
            if mapping_class == "DIRECT" and role == "OPERATIONAL_NATIVE":
                direct += 1
            if (
                mapping_class in {"DIRECT", "DERIVABLE_BY_PREDECLARED_RULE"}
                and role == "OPERATIONAL_NATIVE"
            ):
                direct_or_derivable += 1
            if mapping_class in {"AMBIGUOUS", "ABSENT"}:
                unresolved.add(variable)

        unresolved_sets.append(unresolved)
        per_dataset.append(
            {
                "dataset_id": dataset_id,
                "required_variable_count": len(variable_rows),
                "operational_direct_coverage": {
                    "numerator": direct,
                    "denominator": len(variable_rows),
                },
                "operational_direct_or_derivable_coverage": {
                    "numerator": direct_or_derivable,
                    "denominator": len(variable_rows),
                },
                "unresolved_variables": [
                    name for name in REQUIRED_VARIABLES if name in unresolved
                ],
            }
        )

    common_missing = set.intersection(*unresolved_sets)
    coverage = {
        "per_dataset": per_dataset,
        "cross_dataset_common_missing_state_set": [
            name for name in REQUIRED_VARIABLES if name in common_missing
        ],
    }
    return mapping_record, coverage


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
    if isinstance(policy, selectors.Study2Policy):
        policy_value = policy.value
    else:
        policy_value = selectors.Study2Policy(policy).value
    actions: set[str] = set()
    for state in _states_recursive(dict(known), unresolved):
        state_values = tuple(state[name] for name in REQUIRED_VARIABLES)
        actions.add(_audit_select_action_cached(policy_value, state_values))
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
