from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping

from .completions import PartialObservation
from .contracts import FROZEN_DATASET_IDS, REQUIRED_VARIABLES, FrozenContracts, load_frozen_contracts


class StateProjectionError(RuntimeError):
    """Raised when a native row cannot satisfy the frozen direct-state contract."""


@dataclass(frozen=True)
class DirectProjectionRule:
    recovery_state_variable: str
    native_field_name: str
    value_rule: str


@dataclass(frozen=True)
class ProjectionPlan:
    dataset_id: str
    direct_rules: tuple[DirectProjectionRule, ...]
    unresolved_variables: tuple[str, ...]


def normalize_binary_numeric(value: object) -> bool:
    """Strictly normalize a numeric representation of 0 or 1 to bool."""
    if isinstance(value, bool):
        raise StateProjectionError("boolean source values are not accepted as numeric 0/1 evidence")
    text = str(value).strip()
    if not text:
        raise StateProjectionError("direct recovery-state value is empty")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise StateProjectionError(f"direct recovery-state value is not numeric 0/1: {value!r}") from exc
    if not number.is_finite():
        raise StateProjectionError(f"direct recovery-state value is not finite: {value!r}")
    if number == 0:
        return False
    if number == 1:
        return True
    raise StateProjectionError(f"direct recovery-state value is outside frozen 0/1 domain: {value!r}")


def build_projection_plan(
    dataset_id: str,
    contracts: FrozenContracts | None = None,
) -> ProjectionPlan:
    if dataset_id not in FROZEN_DATASET_IDS:
        raise StateProjectionError(f"unknown frozen dataset: {dataset_id}")
    frozen = contracts or load_frozen_contracts()
    dataset = next(
        row for row in frozen.semantic["dataset_contracts"] if row["dataset_id"] == dataset_id
    )

    direct_rules: list[DirectProjectionRule] = []
    unresolved: list[str] = []
    for row in dataset["variable_contracts"]:
        variable = row["recovery_state_variable"]
        mapping_class = row["frozen_mapping_class"]
        if mapping_class == "DIRECT":
            fields = tuple(row.get("native_field_names", ()))
            if dataset_id != "UNSW_IOTSAT_2026" or variable != "security_signal":
                raise StateProjectionError(
                    f"unexpected frozen DIRECT mapping: {dataset_id}:{variable}"
                )
            if fields != ("Position_Anomaly",):
                raise StateProjectionError("UNSW security_signal direct-field contract drift")
            if row.get("value_rule") != "0 -> false; 1 -> true":
                raise StateProjectionError("UNSW Position_Anomaly value-rule drift")
            direct_rules.append(
                DirectProjectionRule(
                    recovery_state_variable=variable,
                    native_field_name=fields[0],
                    value_rule=row["value_rule"],
                )
            )
        elif mapping_class == "DERIVABLE_BY_PREDECLARED_RULE":
            raise StateProjectionError(
                "DERIVABLE mapping encountered although the frozen derivation registry is empty"
            )
        elif mapping_class in {"AMBIGUOUS", "ABSENT"}:
            unresolved.append(variable)
        else:
            raise StateProjectionError(f"unknown frozen mapping class: {mapping_class}")

    known_variables = tuple(rule.recovery_state_variable for rule in direct_rules)
    unresolved_tuple = tuple(name for name in REQUIRED_VARIABLES if name in unresolved)
    if set(known_variables) | set(unresolved_tuple) != set(REQUIRED_VARIABLES):
        raise StateProjectionError("projection plan does not partition all eight recovery variables")
    if set(known_variables) & set(unresolved_tuple):
        raise StateProjectionError("projection plan overlaps known and unresolved variables")
    return ProjectionPlan(
        dataset_id=dataset_id,
        direct_rules=tuple(direct_rules),
        unresolved_variables=unresolved_tuple,
    )


def project_native_row(
    plan: ProjectionPlan,
    row: Mapping[str, object],
) -> PartialObservation:
    """Project only frozen DIRECT state; all other raw fields are ignored by construction."""
    known: dict[str, bool] = {}
    for rule in plan.direct_rules:
        if rule.native_field_name not in row:
            raise StateProjectionError(
                f"required DIRECT field missing for {plan.dataset_id}: {rule.native_field_name}"
            )
        if rule.value_rule != "0 -> false; 1 -> true":
            raise StateProjectionError(f"unsupported frozen direct-value rule: {rule.value_rule}")
        known[rule.recovery_state_variable] = normalize_binary_numeric(row[rule.native_field_name])

    return PartialObservation.build(
        known=known,
        unresolved=plan.unresolved_variables,
    )
