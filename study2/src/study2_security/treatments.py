from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .evidence import EvidenceCondition, SignedEvidence, sign_claim
from .protocol import AdversaryBudget, ScenarioIdentity, validate_treatment_budget


@dataclass(frozen=True)
class TreatmentResult:
    scenario: ScenarioIdentity
    evidence: tuple[SignedEvidence, ...]
    changed_sources: tuple[str, ...]
    treatment_note: str


def _find(bundle: tuple[SignedEvidence, ...], source_id: str, key: str) -> int:
    for idx, row in enumerate(bundle):
        if row.claim.source_id == source_id and row.claim.key == key:
            return idx
    raise ValueError(f"claim not found for {source_id}:{key}")


def _next_sequence(
    bundle: tuple[SignedEvidence, ...],
    *,
    source_id: str,
    epoch: int,
) -> int:
    used = [
        row.claim.sequence
        for row in bundle
        if row.claim.source_id == source_id and row.claim.epoch == epoch
    ]
    return (max(used) if used else -1) + 1


def apply_treatment(
    scenario: ScenarioIdentity,
    evidence: tuple[SignedEvidence, ...],
    *,
    budget: AdversaryBudget,
    private_keys: Mapping[str, Ed25519PrivateKey],
    target_source: str | None = None,
    target_key: str | None = None,
    alternate_source: str | None = None,
    now_s: float = 1000.0,
    v2_mode: str = "stale",
) -> TreatmentResult:
    if budget.adversary_class is not scenario.adversary_class:
        raise ValueError(
            "adversary budget class must match frozen scenario adversary class"
        )

    validate_treatment_budget(
        scenario.evidence_condition,
        budget,
        contact_regime=scenario.contact_regime,
    )
    condition = scenario.evidence_condition
    if condition is EvidenceCondition.CURRENT:
        return TreatmentResult(scenario, evidence, (), "unchanged_current_evidence")

    if not target_source or not target_key:
        raise ValueError("non-V0 treatments require target_source and target_key")
    idx = _find(evidence, target_source, target_key)
    target = evidence[idx]

    if condition is EvidenceCondition.OMITTED:
        changed = tuple(row for i, row in enumerate(evidence) if i != idx)
        return TreatmentResult(scenario, changed, (target_source,), "claim_omitted")

    if condition is EvidenceCondition.STALE_OR_REPLAYED:
        signer = private_keys[target_source]
        if v2_mode == "stale":
            if now_s <= target.claim.valid_for_s:
                raise ValueError(
                    "V2 stale treatment requires a clock beyond the claim validity duration"
                )
            claim = replace(
                target.claim,
                issued_at_s=max(0.0, now_s - target.claim.valid_for_s - 1.0),
            )
            if claim.issued_at_s <= now_s <= claim.issued_at_s + claim.valid_for_s:
                raise AssertionError("V2 stale treatment failed to produce expired evidence")
            note = "validly_signed_stale_claim"
        elif v2_mode == "replay":
            claim = replace(target.claim, sequence=0)
            note = "validly_signed_replayed_sequence"
        else:
            raise ValueError("v2_mode must be stale or replay")
        changed = list(evidence)
        changed[idx] = sign_claim(claim, signer)
        return TreatmentResult(scenario, tuple(changed), (target_source,), note)

    if condition is EvidenceCondition.CONTRADICTORY:
        if not alternate_source:
            raise ValueError("V3 requires alternate_source")
        signer = private_keys[alternate_source]
        conflict_value = (
            not target.claim.value
            if isinstance(target.claim.value, bool)
            else f"conflict:{target.claim.value}"
        )
        conflict = replace(
            target.claim,
            source_id=alternate_source,
            value=conflict_value,
            sequence=_next_sequence(
                evidence,
                source_id=alternate_source,
                epoch=target.claim.epoch,
            ),
        )
        return TreatmentResult(
            scenario,
            (*evidence, sign_claim(conflict, signer)),
            (alternate_source,),
            "independent_signed_contradiction",
        )

    if condition is EvidenceCondition.MANIPULATED:
        manipulated_value = (
            not target.claim.value
            if isinstance(target.claim.value, bool)
            else f"tampered:{target.claim.value}"
        )
        changed = list(evidence)
        changed[idx] = SignedEvidence(
            replace(target.claim, value=manipulated_value),
            target.signature_b64,
        )
        return TreatmentResult(
            scenario,
            tuple(changed),
            (target_source,),
            "post_signature_value_tamper",
        )

    if condition is EvidenceCondition.PARTIAL_COMPROMISE:
        if target_source not in budget.compromised_sources:
            raise ValueError("V5 target must be inside adversary budget")
        signer = private_keys[target_source]
        false_value = (
            not target.claim.value
            if isinstance(target.claim.value, bool)
            else f"false:{target.claim.value}"
        )
        forged = replace(
            target.claim,
            value=false_value,
            sequence=_next_sequence(
                evidence,
                source_id=target_source,
                epoch=target.claim.epoch,
            ),
        )
        changed = list(evidence)
        changed[idx] = sign_claim(forged, signer)
        return TreatmentResult(
            scenario,
            tuple(changed),
            (target_source,),
            "compromised_source_validly_signed_false_claim",
        )

    raise AssertionError("unhandled evidence condition")
