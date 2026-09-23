# S7E-AERC-001 cFE Ed25519 Verification Boundary Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Selected cFS baseline:** v7.0.1 at `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`  
**Selected verifier:** Monocypher 4.0.3 at `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`  
**Qualification head:** `2c5725e0c43114a087da1087f7fb1d94814661e0`  
**Pull request:** #167  
**Canonical scientific execution:** NOT AUTHORIZED

## Result

**cFE Ed25519 verification boundary: PASS**

The selected Monocypher verification subset compiles inside the selected cFS baseline and verifies/rejects the bounded RFC-8032 engineering cases through cFE Software Bus.

This checkpoint does not bind cryptographic verification to Study-7E authorization features.

## Exact evidence

- workflow: `Study 7E cFS runtime smoke`
- workflow ID: `365269942`
- run ID: `35890910760`
- job ID: `107282876318`
- conclusion: `success`
- artifact ID: `10765340878`
- artifact digest: `sha256:ef74d724eb61548ad41b59356b77874a4285c34b6fdcab40ce712553576c0496`
- pre-canonical qualification run `35890910817`: success

Compile assertions:

- `aerc_sigverify_compile=PASS`
- `aerc_sigverify_probe_compile=PASS`

## Structurally valid verification requests

Valid RFC 8032 Test 1:

`AERC_SIGV RESULT scenario=0x53374701 request=1 verify_sequence=1 valid=1 reason=0 key_id=1 message_len=0`

Mutated signature:

`AERC_SIGV RESULT scenario=0x53374702 request=2 verify_sequence=2 valid=0 reason=1 key_id=1 message_len=0`

All-zero signature:

`AERC_SIGV RESULT scenario=0x53374703 request=3 verify_sequence=3 valid=0 reason=1 key_id=1 message_len=0`

Changed message:

`AERC_SIGV RESULT scenario=0x53374704 request=4 verify_sequence=4 valid=0 reason=1 key_id=1 message_len=1`

Final repeat of the valid vector:

`AERC_SIGV RESULT scenario=0x53374705 request=10 verify_sequence=5 valid=1 reason=0 key_id=1 message_len=0`

## Fail-closed framing checks

Short cFE packet:

`AERC_SIGV REJECT_LENGTH expected=156 actual=20 status=0x00000000`

Wrong wire version:

`AERC_SIGV REJECT_CONTRACT scenario=0x5337470C reason=1 key_id=1 message_len=0 index=0`

Wrong key ID:

`AERC_SIGV REJECT_CONTRACT scenario=0x5337470D reason=2 key_id=2 message_len=0 index=0`

Message length beyond the 64-byte engineering capacity:

`AERC_SIGV REJECT_CONTRACT scenario=0x5337470E reason=3 key_id=1 message_len=65 index=0`

Nonzero inactive message padding:

`AERC_SIGV REJECT_CONTRACT scenario=0x5337470F reason=5 key_id=1 message_len=0 index=63`

Probe completion:

`AERC_SIGVERIFY_PROBE PASS valid=2 crypto_reject=3 malformed_reject=5 final_sequence=5`

The final valid request produced verification sequence 5, proving the five malformed requests did not create verification results or advance the sequence.

## Dependency/provenance boundary

The cFS build bootstraps only the selected Monocypher source subset from exact commit:

`ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`

The bootstrap verifies the 4.0.3 revision, the Ed25519 API, and the source license marker before cFS configure.

No Monocypher signing API is invoked by the Study-7E cFS wrapper.

## Security boundary

The wrapper enforces:

- exact cFE request-packet size;
- fixed 32-byte engineering public key;
- fixed 64-byte signature array;
- bounded message length;
- wire version;
- key ID;
- reserved-byte rules;
- zero padding outside the active message.

The run recorded:

- `secret_key_in_flight_software=false`;
- `policy_authorization_binding_present=false`.

Monocypher's upstream caveat that callers must validate inputs remains applicable. This gate is functional integration evidence; it is not a side-channel evaluation, FIPS validation, flight qualification, or certification result.

## Scientific boundary

The run recorded:

- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

No production authorization key registry was frozen, no authorization feature was populated from the verifier, no learned policy was run, and no canonical Study-7E scenario was executed.

## Next gate

Define and review:

1. canonical signed authorization-evidence byte serialization;
2. test/production public-key provenance and stable key IDs;
3. mapping from source/key/authority domains to the key registry;
4. freshness/epoch fields included in signed bytes;
5. fail-closed qualifier behavior when signature verification is unavailable or invalid.

Only after those contracts are approved should the verifier be bound to `primary_signature_valid` or `corr_signature_valid`.
