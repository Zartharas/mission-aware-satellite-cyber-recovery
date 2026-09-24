# S7E-AERC-001 Ed25519 Verification Dependency Decision — 2026-09-23

**Decision ID:** `S7E-AERC-ED25519-SELECT-001`  
**Experiment:** `S7E-AERC-001`  
**Scope:** pre-canonical cFS signature verification only  
**Canonical scientific execution:** NOT AUTHORIZED

## Decision

Select **Monocypher 4.0.3** at commit:

`ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`

for the next pre-canonical Study-7E Ed25519 verification-integration gate.

Verification API:

`crypto_ed25519_check`

License:

`BSD-2-Clause OR CC0-1.0`

libsodium 1.0.22 remains a green reference alternative and is not selected for the baseline integration.

## Evidence

Bounded feasibility workflow:

- workflow ID: `365298193`
- run ID: `35887743822`
- head: `e5ce0606f23ffbb9c1f80fe6f0f32feda70c3242`

Monocypher:

- job ID: `107272117959`
- artifact ID: `10764060669`
- artifact digest: `sha256:9c83f78b9c963ca641e543e7f509652f66bd1175c7f7f6966e777e3dbfde0833`
- RFC 8032 valid signature: PASS
- mutated signature rejected: PASS
- zero signature rejected: PASS
- changed message rejected: PASS
- selected source subset: `136,736` bytes
- static subset archive: `97,982` bytes
- test binary: `33,728` bytes

libsodium:

- version: `1.0.22`
- release commit: `77e1ce5d6dee871c49ef211222ba18ef0c486bda`
- official tarball SHA-256: `adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349`
- job ID: `107272118271`
- artifact ID: `10764075880`
- artifact digest: `sha256:5294101bd3ed217faf80c69c6ea3808c56c5ac75fd4b7d6d512aabc44eb2220e`
- RFC 8032 valid signature: PASS
- mutated signature rejected: PASS
- zero signature rejected: PASS
- changed message rejected: PASS
- static archive: `927,808` bytes
- test binary: `314,960` bytes

## Selection rationale

Both finalists satisfy the bounded functional verification gate. The selection is therefore based on the Study-7E integration requirement rather than on a claim of general cryptographic superiority.

Study 7E requires a narrow, verification-only Ed25519 surface inside the selected standalone cFS baseline. Monocypher provides the materially smaller tested source/runtime surface and can be integrated as a pinned source subset without bringing the broader general-purpose libsodium runtime into the cFS application.

Monocypher 4.0.3 is also the release that fixes the 2026 EdDSA/Ed25519 timing-leak issue identified by its upstream project.

## Mandatory caveats and controls

Monocypher documents that it performs no input validation and that deviations from required input/output lengths are undefined behavior.

Therefore the Study-7E integration must enforce, before every verification call:

1. exact cFE packet size;
2. exactly 32 public-key bytes;
3. exactly 64 signature bytes;
4. exact canonical message length;
5. fixed/pinned public-key provenance;
6. fail-closed behavior on any malformed input or nonzero verification result.

Additional boundaries:

- no Ed25519 secret/signing key in flight software;
- no runtime signing;
- no FIPS claim;
- no flight-qualification/certification claim;
- no side-channel-resistance claim based solely on this CI gate;
- no scientific-result claim.

## Next gate

Integrate only the pinned Monocypher verification subset into the selected cFS baseline behind the length/provenance wrapper above. Re-run RFC 8032 positive and negative cases through the cFE application boundary before using the verifier to populate any authorization feature.
