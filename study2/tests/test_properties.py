from dataclasses import replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hypothesis import given, settings, strategies as st

from study2_security.evidence import EvidenceClaim, SignedEvidence, sign_claim, verify_bundle
from study2_security.recovery_gate import evaluate_trusted_recovery_gate


PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
PUBLIC_KEYS = {"trusted-verifier": PRIVATE_KEY.public_key()}
TRUSTED = {"trusted-verifier"}


def claim(*, key="integrity_measurement_valid", value=True, sequence=10, issued=100.0, valid=30.0):
    return EvidenceClaim(
        source_id="trusted-verifier",
        subject_id="sat-1",
        key=key,
        value=value,
        epoch=3,
        sequence=sequence,
        issued_at_s=issued,
        valid_for_s=valid,
        provenance="synthetic-study2-property-test",
    )


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.one_of(st.booleans(), st.integers(-10_000, 10_000), st.text(max_size=24)))
def test_any_changed_signed_value_fails_signature(new_value):
    original = claim(value={"state": "known-good"})
    if new_value == original.value:
        return
    signed = sign_claim(original, PRIVATE_KEY)
    tampered = SignedEvidence(
        claim=replace(original, value=new_value),
        signature_b64=signed.signature_b64,
    )
    result = verify_bundle(
        [tampered],
        public_keys=PUBLIC_KEYS,
        trusted_sources=TRUSTED,
        now_s=110.0,
    )
    assert not result.accepted
    assert "invalid_signature" in result.rejected[0].reasons


@settings(max_examples=80, derandomize=True, deadline=None)
@given(
    sequence=st.integers(min_value=0, max_value=1_000_000),
    delta=st.integers(min_value=0, max_value=100),
)
def test_sequence_not_strictly_newer_than_baseline_is_rejected(sequence, delta):
    signed = sign_claim(claim(sequence=sequence), PRIVATE_KEY)
    result = verify_bundle(
        [signed],
        public_keys=PUBLIC_KEYS,
        trusted_sources=TRUSTED,
        now_s=110.0,
        minimum_sequence_by_source_epoch={("trusted-verifier", 3): sequence + delta},
    )
    assert not result.accepted
    assert "replayed_or_rolled_back_sequence" in result.rejected[0].reasons


@settings(max_examples=80, derandomize=True, deadline=None)
@given(
    now_s=st.one_of(
        st.floats(max_value=99.999, allow_nan=False, allow_infinity=False),
        st.floats(
            min_value=130.001,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
)
def test_out_of_window_evidence_is_never_accepted(now_s):
    signed = sign_claim(claim(), PRIVATE_KEY)
    result = verify_bundle(
        [signed],
        public_keys=PUBLIC_KEYS,
        trusted_sources=TRUSTED,
        now_s=now_s,
    )
    assert not result.accepted
    assert "stale_or_future_evidence" in result.rejected[0].reasons


@settings(max_examples=80, derandomize=True, deadline=None)
@given(residual=st.booleans(), criterion_value=st.booleans())
def test_trusted_recovery_requires_true_attested_criteria_and_no_residual_state(
    residual, criterion_value
):
    signed = sign_claim(claim(value=criterion_value), PRIVATE_KEY)
    attestation = verify_bundle(
        [signed],
        public_keys=PUBLIC_KEYS,
        trusted_sources=TRUSTED,
        now_s=110.0,
    )
    decision = evaluate_trusted_recovery_gate(
        attestation,
        subject_id="sat-1",
        applicable_criteria=("integrity_measurement_valid",),
        residual_unauthorized_state=residual,
    )
    assert decision.trusted_recovery_allowed is (criterion_value and not residual)


@settings(max_examples=80, derandomize=True, deadline=None)
@given(expected_epoch=st.integers(min_value=0, max_value=1000))
def test_wrong_epoch_never_becomes_decision_eligible(expected_epoch):
    if expected_epoch == 3:
        return
    signed = sign_claim(claim(), PRIVATE_KEY)
    result = verify_bundle(
        [signed],
        public_keys=PUBLIC_KEYS,
        trusted_sources=TRUSTED,
        now_s=110.0,
        expected_epoch_by_subject={"sat-1": expected_epoch},
    )
    assert not result.accepted
    assert "wrong_evidence_epoch" in result.rejected[0].reasons
