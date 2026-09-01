from __future__ import annotations

from dataclasses import dataclass, replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .evidence import (
    AttestationResult,
    EvidenceClaim,
    SignedEvidence,
    sign_claim,
    verify_bundle,
)
from .recovery_gate import evaluate_trusted_recovery_gate


@dataclass(frozen=True)
class MutationResult:
    mutant: str
    killed: bool
    counterexample: str


def _claim(
    source_id: str,
    *,
    value: bool = True,
    epoch: int = 7,
    sequence: int = 1,
    issued_at_s: float = 990.0,
    valid_for_s: float = 20.0,
    provenance: str = "mutation-assay",
) -> EvidenceClaim:
    return EvidenceClaim(
        source_id=source_id,
        subject_id="sat-1",
        key="authorization_valid",
        value=value,
        epoch=epoch,
        sequence=sequence,
        issued_at_s=issued_at_s,
        valid_for_s=valid_for_s,
        provenance=provenance,
    )


def _gate(
    attestation: AttestationResult,
    *,
    residual_unauthorized_state: bool = False,
) -> bool:
    return evaluate_trusted_recovery_gate(
        attestation,
        subject_id="sat-1",
        applicable_criteria=("authorization_valid",),
        residual_unauthorized_state=residual_unauthorized_state,
    ).trusted_recovery_allowed


def _accept_verification_mutant(
    attestation: AttestationResult,
    *,
    row_index: int,
    **flag_overrides: bool,
) -> AttestationResult:
    rows = list(attestation.verifications)
    rows[row_index] = replace(
        rows[row_index],
        accepted=True,
        **flag_overrides,
    )
    return AttestationResult(
        verifications=tuple(rows),
        contradictions=attestation.contradictions,
    )


def run_semantic_mutation_assay() -> tuple[MutationResult, ...]:
    """Run targeted semantic mutants against production verifier/recovery paths.

    Each baseline uses the actual Study-2 evidence verifier and trusted-recovery
    gate.  The paired mutant changes exactly one security decision at the
    verifier/gate boundary.  If production enforcement regresses, the baseline
    becomes permissive and the corresponding mutant is no longer reported as
    killed.
    """

    source_a = Ed25519PrivateKey.generate()
    source_b = Ed25519PrivateKey.generate()
    public_keys = {
        "source-a": source_a.public_key(),
        "source-b": source_b.public_key(),
    }
    results: list[MutationResult] = []

    valid_a = sign_claim(_claim("source-a"), source_a)
    tampered = SignedEvidence(
        claim=replace(valid_a.claim, provenance="post-signature-tamper"),
        signature_b64=valid_a.signature_b64,
    )
    attestation = verify_bundle(
        (tampered,),
        public_keys=public_keys,
        trusted_sources={"source-a"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    mutant_attestation = _accept_verification_mutant(
        attestation,
        row_index=0,
        signature_valid=True,
    )
    results.append(
        MutationResult(
            "MUT_ACCEPT_INVALID_SIGNATURE",
            (not _gate(attestation)) and _gate(mutant_attestation),
            "post-signature claim tamper",
        )
    )

    attestation = verify_bundle(
        (valid_a,),
        public_keys=public_keys,
        trusted_sources=set(),
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    mutant_attestation = _accept_verification_mutant(
        attestation,
        row_index=0,
        source_trusted=True,
    )
    results.append(
        MutationResult(
            "MUT_ACCEPT_UNTRUSTED_SOURCE",
            (not _gate(attestation)) and _gate(mutant_attestation),
            "valid signature from untrusted producer",
        )
    )

    stale = sign_claim(
        _claim("source-a", issued_at_s=900.0, valid_for_s=20.0),
        source_a,
    )
    attestation = verify_bundle(
        (stale,),
        public_keys=public_keys,
        trusted_sources={"source-a"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    mutant_attestation = _accept_verification_mutant(
        attestation,
        row_index=0,
        fresh=True,
    )
    results.append(
        MutationResult(
            "MUT_ACCEPT_STALE",
            (not _gate(attestation)) and _gate(mutant_attestation),
            "expired signed evidence",
        )
    )

    wrong_epoch = sign_claim(_claim("source-a", epoch=6), source_a)
    attestation = verify_bundle(
        (wrong_epoch,),
        public_keys=public_keys,
        trusted_sources={"source-a"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    mutant_attestation = _accept_verification_mutant(
        attestation,
        row_index=0,
        epoch_valid=True,
    )
    results.append(
        MutationResult(
            "MUT_ACCEPT_WRONG_EPOCH",
            (not _gate(attestation)) and _gate(mutant_attestation),
            "wrong recovery epoch",
        )
    )

    replay = sign_claim(_claim("source-a", sequence=5), source_a)
    attestation = verify_bundle(
        (replay,),
        public_keys=public_keys,
        trusted_sources={"source-a"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
        minimum_sequence_by_source_epoch={("source-a", 7): 5},
    )
    mutant_attestation = _accept_verification_mutant(
        attestation,
        row_index=0,
        sequence_valid=True,
    )
    results.append(
        MutationResult(
            "MUT_ACCEPT_REPLAYED_SEQUENCE",
            (not _gate(attestation)) and _gate(mutant_attestation),
            "non-increasing source/epoch sequence",
        )
    )

    false_a = sign_claim(_claim("source-a", value=False), source_a)
    true_b = sign_claim(_claim("source-b", value=True), source_b)
    attestation = verify_bundle(
        (false_a, true_b),
        public_keys=public_keys,
        trusted_sources={"source-a", "source-b"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    contradiction_ignored = AttestationResult(
        verifications=attestation.verifications,
        contradictions=(),
    )
    results.append(
        MutationResult(
            "MUT_IGNORE_CONTRADICTION",
            (not _gate(attestation)) and _gate(contradiction_ignored),
            "conflicting current trusted-source claims",
        )
    )

    qualified = verify_bundle(
        (valid_a,),
        public_keys=public_keys,
        trusted_sources={"source-a"},
        now_s=1000.0,
        expected_epoch_by_subject={"sat-1": 7},
    )
    results.append(
        MutationResult(
            "MUT_IGNORE_RESIDUAL_STATE",
            (not _gate(qualified, residual_unauthorized_state=True))
            and _gate(qualified, residual_unauthorized_state=False),
            "qualified evidence with residual unauthorized state",
        )
    )

    frozen = tuple(results)
    if not all(row.killed for row in frozen):
        alive = [row.mutant for row in frozen if not row.killed]
        raise AssertionError(f"semantic mutation assay left mutants alive: {alive}")
    return frozen
