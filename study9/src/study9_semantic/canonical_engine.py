from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import FROZEN_DATASET_IDS, PRIMARY_POLICY_VALUES
from .selector_adapter import selector_types
from .sidecar import guaranteed_minimal_sidecar_sets, reachable_actions
from .state_groups import NativeStateGroup


@dataclass(frozen=True)
class GroupPolicyResult:
    group_index: int
    multiplicity: int
    reachable_actions: tuple[str, ...]
    action_set_cardinality: int
    unique_action: bool
    guaranteed_sidecar_cardinality: int
    guaranteed_sidecar_sets: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class PolicyStratumResult:
    dataset_id: str
    policy: str
    source_row_count: int
    native_state_group_count: int
    unique_action_numerator: int
    unique_action_denominator: int
    group_results: tuple[GroupPolicyResult, ...]


@dataclass(frozen=True)
class CanonicalDatasetAnalysis:
    dataset_id: str
    source_row_count: int
    native_state_group_count: int
    policy_strata: tuple[PolicyStratumResult, ...]


def _ordered_actions(actions: frozenset[str]) -> tuple[str, ...]:
    _, Study2Action, _ = selector_types()
    order = {action.value: index for index, action in enumerate(Study2Action)}
    unknown = set(actions) - set(order)
    if unknown:
        raise ValueError(f"selector returned unknown actions: {sorted(unknown)}")
    return tuple(sorted(actions, key=order.__getitem__))


def analyze_native_state_groups(
    dataset_id: str,
    groups: Iterable[NativeStateGroup],
) -> CanonicalDatasetAnalysis:
    """Evaluate frozen primary policies over already verified native-state groups."""
    if dataset_id not in FROZEN_DATASET_IDS:
        raise ValueError(f"unknown frozen dataset: {dataset_id}")
    group_tuple = tuple(groups)
    if not group_tuple:
        raise ValueError("canonical endpoint engine requires at least one native-state group")
    for group in group_tuple:
        if group.dataset_id != dataset_id:
            raise ValueError("cross-dataset native-state groups cannot enter one analysis")
        if type(group.multiplicity) is not int or group.multiplicity <= 0:
            raise ValueError("native-state group multiplicity must be a positive integer")

    source_row_count = sum(group.multiplicity for group in group_tuple)
    Study2Policy, _, _ = selector_types()
    policies = tuple(Study2Policy(value) for value in PRIMARY_POLICY_VALUES)
    if tuple(policy.value for policy in policies) != PRIMARY_POLICY_VALUES:
        raise ValueError("primary policy ordering drift")

    strata: list[PolicyStratumResult] = []
    for policy in policies:
        group_results: list[GroupPolicyResult] = []
        unique_rows = 0
        for index, group in enumerate(group_tuple):
            partial = group.partial_observation()
            actions = reachable_actions(policy, partial)
            ordered_actions = _ordered_actions(actions)
            sidecars = guaranteed_minimal_sidecar_sets(policy, partial)
            sidecar_cardinality = len(sidecars[0])
            if any(len(item) != sidecar_cardinality for item in sidecars):
                raise ValueError("guaranteed sidecar helper returned mixed cardinalities")
            unique = len(ordered_actions) == 1
            if unique:
                unique_rows += group.multiplicity
            group_results.append(
                GroupPolicyResult(
                    group_index=index,
                    multiplicity=group.multiplicity,
                    reachable_actions=ordered_actions,
                    action_set_cardinality=len(ordered_actions),
                    unique_action=unique,
                    guaranteed_sidecar_cardinality=sidecar_cardinality,
                    guaranteed_sidecar_sets=sidecars,
                )
            )
        strata.append(
            PolicyStratumResult(
                dataset_id=dataset_id,
                policy=policy.value,
                source_row_count=source_row_count,
                native_state_group_count=len(group_tuple),
                unique_action_numerator=unique_rows,
                unique_action_denominator=source_row_count,
                group_results=tuple(group_results),
            )
        )

    return CanonicalDatasetAnalysis(
        dataset_id=dataset_id,
        source_row_count=source_row_count,
        native_state_group_count=len(group_tuple),
        policy_strata=tuple(strata),
    )


def analysis_to_record(analysis: CanonicalDatasetAnalysis) -> dict[str, object]:
    return {
        "dataset_id": analysis.dataset_id,
        "source_row_count": analysis.source_row_count,
        "native_state_group_count": analysis.native_state_group_count,
        "policy_strata": [
            {
                "dataset_id": stratum.dataset_id,
                "policy": stratum.policy,
                "source_row_count": stratum.source_row_count,
                "native_state_group_count": stratum.native_state_group_count,
                "unique_action_fraction": {
                    "numerator": stratum.unique_action_numerator,
                    "denominator": stratum.unique_action_denominator,
                },
                "group_results": [
                    {
                        "group_index": group.group_index,
                        "multiplicity": group.multiplicity,
                        "reachable_actions": list(group.reachable_actions),
                        "action_set_cardinality": group.action_set_cardinality,
                        "unique_action": group.unique_action,
                        "guaranteed_sidecar_cardinality": group.guaranteed_sidecar_cardinality,
                        "guaranteed_sidecar_sets": [list(item) for item in group.guaranteed_sidecar_sets],
                    }
                    for group in stratum.group_results
                ],
            }
            for stratum in analysis.policy_strata
        ],
    }
