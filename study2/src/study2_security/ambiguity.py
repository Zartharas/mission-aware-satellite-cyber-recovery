from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .evidence import SignedEvidence, claim_bytes
from .protocol import CauseClass


@dataclass(frozen=True)
class AmbiguityObservation:
    family_id: str
    cause: CauseClass
    evidence: tuple[SignedEvidence, ...]
    hidden_cause_token: str


def policy_visible_fingerprint(observation: AmbiguityObservation) -> str:
    digest = hashlib.sha256()
    for row in sorted(observation.evidence, key=lambda item: (
        item.claim.source_id, item.claim.key, item.claim.epoch, item.claim.sequence
    )):
        digest.update(claim_bytes(row.claim))
        digest.update(row.signature_b64.encode("ascii"))
    return digest.hexdigest()


def matched_pair(
    family_id: str,
    evidence: tuple[SignedEvidence, ...],
) -> tuple[AmbiguityObservation, AmbiguityObservation]:
    benign = AmbiguityObservation(family_id, CauseClass.BENIGN, evidence, f"{family_id}:benign")
    adversarial = AmbiguityObservation(family_id, CauseClass.ADVERSARIAL, evidence, f"{family_id}:adversarial")
    if policy_visible_fingerprint(benign) != policy_visible_fingerprint(adversarial):
        raise AssertionError("matched ambiguity observations must be policy-visible identical")
    return benign, adversarial
