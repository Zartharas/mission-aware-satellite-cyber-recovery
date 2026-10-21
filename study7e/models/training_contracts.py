from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from study7e.src.aerc_design import BASE_FEATURES, EXTENDED_FEATURES

TRAINING_BLOCKS = frozenset({"TR0", "TR1"})
EVALUATION_BLOCKS = frozenset({"E1", "E2", "C0"})
ALLOWED_TARGETS = frozenset({"HOLD", "ENTER_RECOVERY_GATE"})


@dataclass(frozen=True, slots=True)
class TrainingRecord:
    scenario_id: str
    block: str
    features: tuple[int, ...]
    target: str

    def __post_init__(self) -> None:
        if self.block not in TRAINING_BLOCKS:
            raise ValueError(f"non-training block rejected: {self.block}")
        if not self.scenario_id.startswith(f"{self.block}-"):
            raise ValueError("scenario_id/block mismatch")
        if self.target not in ALLOWED_TARGETS:
            raise ValueError(f"invalid training target: {self.target}")
        if any(value not in (0, 1) for value in self.features):
            raise ValueError("training features must be binary")


@dataclass(frozen=True, slots=True)
class LearnerCandidateSpec:
    policy_id: str
    algorithm: str
    feature_order: tuple[str, ...]
    library: str
    library_version: str | None
    hyperparameters: Mapping[str, object]
    frozen: bool

    def validate_precanonical(self) -> None:
        if self.policy_id == "L0_BASE":
            expected = BASE_FEATURES
        elif self.policy_id == "L1_CORROBORATED":
            expected = EXTENDED_FEATURES
        else:
            raise ValueError(f"unknown learned policy: {self.policy_id}")

        if tuple(self.feature_order) != tuple(expected):
            raise ValueError(f"feature order drift for {self.policy_id}")
        if self.algorithm != "DecisionTreeClassifier":
            raise ValueError("learner algorithm drift")
        if self.library != "scikit-learn":
            raise ValueError("learner library drift")
        if self.frozen:
            raise ValueError("production learner must not be frozen in pre-canonical phase")


def _coerce_binary_vector(
    snapshot: Mapping[str, object],
    feature_order: Sequence[str],
) -> tuple[int, ...]:
    vector: list[int] = []
    for feature in feature_order:
        if feature not in snapshot:
            raise KeyError(f"missing feature: {feature}")
        value = snapshot[feature]
        if value not in (0, 1, False, True):
            raise ValueError(f"{feature} must be binary")
        vector.append(int(value))
    return tuple(vector)


def make_training_record(
    *,
    policy_id: str,
    scenario_id: str,
    block: str,
    snapshot: Mapping[str, object],
    target: str,
) -> TrainingRecord:
    if block not in TRAINING_BLOCKS:
        raise ValueError(f"evaluation label access rejected: {block}")

    if policy_id == "L0_BASE":
        feature_order = BASE_FEATURES
    elif policy_id == "L1_CORROBORATED":
        feature_order = EXTENDED_FEATURES
    else:
        raise ValueError(f"unknown learned policy: {policy_id}")

    privileged = {
        "true_authorization",
        "true_health_ready",
        "objective_action",
        "fault_profile",
        "topology",
        "domain_alias_map",
    }
    leaked = privileged.intersection(snapshot.keys())
    if leaked:
        raise ValueError(f"privileged fields rejected: {sorted(leaked)}")

    return TrainingRecord(
        scenario_id=scenario_id,
        block=block,
        features=_coerce_binary_vector(snapshot, feature_order),
        target=target,
    )


def validate_training_partition(records: Iterable[TrainingRecord]) -> dict[str, int]:
    counts = {"TR0": 0, "TR1": 0, "TOTAL": 0}
    seen: set[str] = set()
    for record in records:
        if record.scenario_id in seen:
            raise ValueError(f"duplicate training scenario: {record.scenario_id}")
        seen.add(record.scenario_id)
        if record.block not in TRAINING_BLOCKS:
            raise ValueError(f"evaluation block entered training: {record.block}")
        counts[record.block] += 1
        counts["TOTAL"] += 1

    if counts != {"TR0": 12, "TR1": 72, "TOTAL": 84}:
        raise ValueError(f"training cardinality drift: {counts}")
    return counts
