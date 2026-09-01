from __future__ import annotations

import base64
import json
from collections import Counter
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Any, Iterable, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class EvidenceCondition(str, Enum):
    """Prospective Study-2 evidence treatments; Study-1 T1 remains omission-only."""

    CURRENT = "V0"
    OMITTED = "V1"
    STALE_OR_REPLAYED = "V2"
    CONTRADICTORY = "V3"
    MANIPULATED = "V4"
    PARTIAL_COMPROMISE = "V5"


@dataclass(frozen=True)
class EvidenceClaim:
    source_id: str
    subject_id: str
    key: str
    value: Any
    epoch: int
    sequence: int
    issued_at_s: float
    valid_for_s: float
    provenance: str

    def __post_init__(self) -> None:
        if not self.source_id or not self.subject_id or not self.key:
            raise ValueError("source_id, subject_id, and key are required")
        if self.epoch < 0 or self.sequence < 0:
            raise ValueError("epoch and sequence must be non-negative")
        if self.issued_at_s < 0 or self.valid_for_s <= 0:
            raise ValueError("invalid evidence timing")
        if not self.provenance:
            raise ValueError("provenance is required")
        _canonical_bytes(asdict(self))


@dataclass(frozen=True)
class SignedEvidence:
    claim: EvidenceClaim
    signature_b64: str


@dataclass(frozen=True)
class EvidenceVerification:
    signed: SignedEvidence
    signature_valid: bool
    source_trusted: bool
    fresh: bool
    epoch_valid: bool
    sequence_valid: bool
    accepted: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True, order=True)
class EvidenceContradiction:
    subject_id: str
    key: str
    epoch: int


@dataclass(frozen=True)
class AttestationResult:
    verifications: tuple[EvidenceVerification, ...]
    contradictions: tuple[EvidenceContradiction, ...]

    @property
    def accepted(self) -> tuple[EvidenceVerification, ...]:
        return tuple(row for row in self.verifications if row.accepted)

    @property
    def rejected(self) -> tuple[EvidenceVerification, ...]:
        return tuple(row for row in self.verifications if not row.accepted)

    def contradiction_keys(self, *, subject_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {row.key for row in self.contradictions if row.subject_id == subject_id}
            )
        )

    def current_values(self, *, subject_id: str) -> dict[str, Any]:
        contradictory = set(self.contradiction_keys(subject_id=subject_id))
        latest: dict[tuple[str, str, int], EvidenceVerification] = {}
        for row in self.accepted:
            claim = row.signed.claim
            if claim.subject_id != subject_id or claim.key in contradictory:
                continue
            identity = (claim.source_id, claim.key, claim.epoch)
            previous = latest.get(identity)
            if previous is None or claim.sequence > previous.signed.claim.sequence:
                latest[identity] = row

        values: dict[str, Any] = {}
        for row in latest.values():
            claim = row.signed.claim
            values[claim.key] = claim.value
        return values

    def requirements_satisfied(
        self,
        required: Mapping[str, Any],
        *,
        subject_id: str,
    ) -> bool:
        values = self.current_values(subject_id=subject_id)
        return all(
            key in values and values[key] == expected
            for key, expected in required.items()
        )


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def claim_bytes(claim: EvidenceClaim) -> bytes:
    return _canonical_bytes(asdict(claim))


def sign_claim(
    claim: EvidenceClaim,
    private_key: Ed25519PrivateKey,
) -> SignedEvidence:
    signature = private_key.sign(claim_bytes(claim))
    return SignedEvidence(
        claim=claim,
        signature_b64=base64.b64encode(signature).decode("ascii"),
    )


def verify_signed_evidence(
    signed: SignedEvidence,
    *,
    public_keys: Mapping[str, Ed25519PublicKey],
    trusted_sources: set[str] | frozenset[str],
    now_s: float,
    expected_epoch_by_subject: Mapping[str, int] | None = None,
    minimum_sequence_by_source_epoch: Mapping[tuple[str, int], int] | None = None,
) -> EvidenceVerification:
    claim = signed.claim
    reasons: list[str] = []

    public_key = public_keys.get(claim.source_id)
    signature_valid = public_key is not None
    if public_key is None:
        reasons.append("unknown_source_key")
    else:
        try:
            signature = base64.b64decode(signed.signature_b64, validate=True)
            public_key.verify(signature, claim_bytes(claim))
        except (InvalidSignature, ValueError):
            signature_valid = False
            reasons.append("invalid_signature")

    source_trusted = claim.source_id in trusted_sources
    if not source_trusted:
        reasons.append("untrusted_source")

    fresh = claim.issued_at_s <= now_s <= claim.issued_at_s + claim.valid_for_s
    if not fresh:
        reasons.append("stale_or_future_evidence")

    expected_epochs = expected_epoch_by_subject or {}
    expected_epoch = expected_epochs.get(claim.subject_id)
    if expected_epoch is None:
        epoch_valid = False
        reasons.append("missing_expected_evidence_epoch")
    else:
        epoch_valid = claim.epoch == expected_epoch
        if not epoch_valid:
            reasons.append("wrong_evidence_epoch")

    minimums = minimum_sequence_by_source_epoch or {}
    previous = minimums.get((claim.source_id, claim.epoch), -1)
    sequence_valid = claim.sequence > previous
    if not sequence_valid:
        reasons.append("replayed_or_rolled_back_sequence")

    accepted = (
        signature_valid
        and source_trusted
        and fresh
        and epoch_valid
        and sequence_valid
    )
    return EvidenceVerification(
        signed=signed,
        signature_valid=signature_valid,
        source_trusted=source_trusted,
        fresh=fresh,
        epoch_valid=epoch_valid,
        sequence_valid=sequence_valid,
        accepted=accepted,
        reasons=tuple(reasons),
    )


def _reject_duplicate_sequences(
    rows: tuple[EvidenceVerification, ...],
) -> tuple[EvidenceVerification, ...]:
    counts = Counter(
        (
            row.signed.claim.source_id,
            row.signed.claim.epoch,
            row.signed.claim.sequence,
        )
        for row in rows
    )
    output: list[EvidenceVerification] = []
    for row in rows:
        identity = (
            row.signed.claim.source_id,
            row.signed.claim.epoch,
            row.signed.claim.sequence,
        )
        if counts[identity] <= 1:
            output.append(row)
            continue
        reasons = tuple(dict.fromkeys((*row.reasons, "duplicate_sequence_in_bundle")))
        output.append(
            replace(
                row,
                sequence_valid=False,
                accepted=False,
                reasons=reasons,
            )
        )
    return tuple(output)


def _contradictions(
    rows: tuple[EvidenceVerification, ...],
) -> tuple[EvidenceContradiction, ...]:
    latest: dict[tuple[str, str, str, int], EvidenceVerification] = {}
    for row in rows:
        if not row.accepted:
            continue
        claim = row.signed.claim
        identity = (claim.source_id, claim.subject_id, claim.key, claim.epoch)
        previous = latest.get(identity)
        if previous is None or claim.sequence > previous.signed.claim.sequence:
            latest[identity] = row

    grouped: dict[tuple[str, str, int], set[bytes]] = {}
    for row in latest.values():
        claim = row.signed.claim
        identity = (claim.subject_id, claim.key, claim.epoch)
        grouped.setdefault(identity, set()).add(_canonical_bytes(claim.value))

    return tuple(
        EvidenceContradiction(subject_id=subject, key=key, epoch=epoch)
        for (subject, key, epoch), values in sorted(grouped.items())
        if len(values) > 1
    )


def verify_bundle(
    evidence: Iterable[SignedEvidence],
    *,
    public_keys: Mapping[str, Ed25519PublicKey],
    trusted_sources: set[str] | frozenset[str],
    now_s: float,
    expected_epoch_by_subject: Mapping[str, int] | None = None,
    minimum_sequence_by_source_epoch: Mapping[tuple[str, int], int] | None = None,
) -> AttestationResult:
    rows = tuple(
        verify_signed_evidence(
            signed,
            public_keys=public_keys,
            trusted_sources=trusted_sources,
            now_s=now_s,
            expected_epoch_by_subject=expected_epoch_by_subject,
            minimum_sequence_by_source_epoch=minimum_sequence_by_source_epoch,
        )
        for signed in evidence
    )
    rows = _reject_duplicate_sequences(rows)
    return AttestationResult(
        verifications=rows,
        contradictions=_contradictions(rows),
    )
