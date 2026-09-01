from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .evidence import EvidenceCondition


class AdversaryClass(str, Enum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"


class ContactRegime(str, Enum):
    K0 = "K0"
    K1 = "K1"
    K2 = "K2"
    K3 = "K3"
    K4 = "K4"


class CauseClass(str, Enum):
    BENIGN = "BENIGN"
    ADVERSARIAL = "ADVERSARIAL"


@dataclass(frozen=True)
class ScenarioIdentity:
    experiment_id: str
    scenario_id: str
    seed: int
    treatment_id: str
    evidence_condition: EvidenceCondition
    adversary_class: AdversaryClass
    contact_regime: ContactRegime
    ground_truth_token: str
    provenance_token: str
    analysis_control_token: str

    def __post_init__(self) -> None:
        if not all((self.experiment_id, self.scenario_id, self.treatment_id)):
            raise ValueError("experiment, scenario, and treatment identifiers are required")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if not all((self.ground_truth_token, self.provenance_token, self.analysis_control_token)):
            raise ValueError("immutable research tokens are required")


@dataclass(frozen=True)
class AdversaryBudget:
    adversary_class: AdversaryClass
    compromised_sources: tuple[str, ...] = ()
    independent_trust_anchor: str = "verifier-root"
    may_read_policy_schema: bool = True
    may_read_public_keys: bool = True
    may_read_ground_truth: bool = False
    may_read_analysis_controls: bool = False
    may_change_seed: bool = False
    may_change_treatment_id: bool = False
    may_compromise_verifier: bool = False

    def validate(self, *, contact_regime: ContactRegime) -> None:
        unique = tuple(dict.fromkeys(self.compromised_sources))
        if unique != self.compromised_sources:
            raise ValueError("compromised_sources must be unique and ordered")
        if any((self.may_read_ground_truth, self.may_read_analysis_controls,
                self.may_change_seed, self.may_change_treatment_id,
                self.may_compromise_verifier)):
            raise ValueError("adversary budget crosses frozen research/trust boundary")
        n = len(self.compromised_sources)
        if self.adversary_class is AdversaryClass.A0 and n != 0:
            raise ValueError("A0 permits no compromised evidence producer")
        if self.adversary_class is AdversaryClass.A1 and n != 1:
            raise ValueError("A1 requires exactly one compromised producer")
        if self.adversary_class is AdversaryClass.A2:
            if n != 1:
                raise ValueError("A2 requires exactly one compromised producer")
            if contact_regime is ContactRegime.K0:
                raise ValueError("A2 requires modeled contact unavailability")
        if self.adversary_class is AdversaryClass.A3:
            if n < 2:
                raise ValueError("A3 requires at least two compromised producers")
            if not self.independent_trust_anchor:
                raise ValueError("A3 requires an independent trust anchor")
            if self.independent_trust_anchor in self.compromised_sources:
                raise ValueError("A3 excludes the independent trust anchor from compromise")


def validate_treatment_budget(
    condition: EvidenceCondition,
    budget: AdversaryBudget,
    *,
    contact_regime: ContactRegime,
) -> None:
    budget.validate(contact_regime=contact_regime)
    allowed: Mapping[EvidenceCondition, frozenset[AdversaryClass]] = {
        EvidenceCondition.CURRENT: frozenset({AdversaryClass.A0}),
        EvidenceCondition.OMITTED: frozenset({AdversaryClass.A0, AdversaryClass.A1}),
        EvidenceCondition.STALE_OR_REPLAYED: frozenset({AdversaryClass.A0, AdversaryClass.A1, AdversaryClass.A2}),
        EvidenceCondition.CONTRADICTORY: frozenset({AdversaryClass.A0, AdversaryClass.A1, AdversaryClass.A2, AdversaryClass.A3}),
        EvidenceCondition.MANIPULATED: frozenset({AdversaryClass.A1, AdversaryClass.A2, AdversaryClass.A3}),
        EvidenceCondition.PARTIAL_COMPROMISE: frozenset({AdversaryClass.A1, AdversaryClass.A2, AdversaryClass.A3}),
    }
    if budget.adversary_class not in allowed[condition]:
        raise ValueError(f"{condition.value} incompatible with {budget.adversary_class.value}")
