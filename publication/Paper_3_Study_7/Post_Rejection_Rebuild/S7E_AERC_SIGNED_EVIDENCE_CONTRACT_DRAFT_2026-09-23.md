# S7E-AERC-001 Signed Authorization-Evidence Contract Draft — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Status:** `DRAFT__NOT_FROZEN__NO_POLICY_BINDING`  
**Canonical scientific execution:** NOT AUTHORIZED

## Purpose

This record proposes a concrete byte/provenance contract for later review. It does not amend or freeze the Study-7E protocol.

The existing protocol requires signed primary/corroborating authorization evidence and an evidence qualifier that derives signature validity, source trust, freshness, epoch validity, contradiction/completeness state, and authorization. It also requires explicit source/key/execution/transport/authority trust domains and controlled logical time.

The protocol does **not** yet define the exact signed byte string or final experiment public-key registry. This draft fills that implementation-design gap only as a candidate.

## Source-required semantics versus proposed encoding

### Required by the current Study-7E design

The current protocol/implementation plan supports these requirements:

- primary and corroborating authorization producers emit signed authorization evidence;
- qualifier outputs are derived, not injected policy truth;
- source, signing-key, execution, transport, and authority domains are explicit;
- key IDs map to key domains;
- test keys are experiment-only;
- controlled logical time, not wall clock, is required for canonical reproducibility;
- topology/fault identity cannot be policy-visible input.

### Proposed by this draft, not yet frozen

Candidate signed body v1 uses explicit fixed-width big-endian encoding. Native C-struct `memcpy` serialization is prohibited.

| Offset | Bytes | Candidate field |
|---:|---:|---|
| 0 | 16 | ASCII domain separator `S7E-AERC-AUTH-V1` |
| 16 | 1 | schema version = 1 |
| 17 | 1 | producer role: 1 primary, 2 corroborator |
| 18 | 1 | authorization value: 0/1 |
| 19 | 1 | reserved = 0 |
| 20 | 4 | source ID, unsigned big-endian |
| 24 | 4 | authority ID, unsigned big-endian |
| 28 | 4 | key ID, unsigned big-endian |
| 32 | 8 | evidence epoch, unsigned big-endian |
| 40 | 8 | issued logical time, unsigned big-endian |
| 48 | 8 | evidence sequence, unsigned big-endian |

Candidate total signed bytes: **56**.

The 56-byte candidate fits inside the already-qualified 64-byte engineering verification-message capacity, but that implementation convenience is not itself a reason to freeze the format.

## Why these fields are proposed

The draft signs source ID, authority ID, key ID, producer role, and authorization value so those semantics cannot be relabeled after signing.

Epoch, controlled logical time, and evidence sequence are signed to support future freshness/replay checks.

A fixed domain separator is proposed to reduce accidental cross-protocol signature reuse.

The candidate deliberately does not put topology or fault identity in the signed policy evidence.

## Draft public-key provenance model

The experiment public-key registry is **not populated or frozen**.

Candidate requirements:

- 32-byte Ed25519 public keys;
- stable numeric key IDs map to key domains;
- each entry records public-key SHA-256 and generation provenance;
- private/signing keys remain at test producer/harness boundaries and never in verifier FSW;
- T0/T1 may alias the primary/corroborator key domain;
- T2/T3/T4 require separate primary/corroborator key domains;
- T4 also requires separate authority provenance.

No final test key pair is created or committed by this draft.

## Adversarial review

The candidate addresses several relabeling/ambiguity risks:

- **source relabel:** source ID is signed;
- **authority relabel:** authority ID is signed;
- **key-ID substitution:** key ID is signed and registry-bound;
- **primary/corroborator role swap:** producer role is signed;
- **cross-protocol signature reuse:** domain separator is signed;
- **padding/endian ambiguity:** native struct serialization is prohibited;
- **verifier secret exposure:** public keys only in verifier FSW.

Important risks remain unresolved and therefore block freeze:

1. scenario/context binding and cross-scenario splice prevention;
2. final registry IDs and key-generation provenance;
3. logical-time units and freshness thresholds;
4. epoch semantics;
5. evidence-sequence replay/ordering rule;
6. contradiction semantics;
7. completeness semantics;
8. authorization-value behavior when qualification/signature fails;
9. T4 separate-authority representation;
10. exact byte transformations for F3/F4/F9/F10/F11/F12;
11. final test key pairs and public-key hashes.

## Guardrail

Until these items are reviewed:

- canonical signed bytes are **not** defined;
- public-key registry is **not** frozen;
- signing keys are **not** frozen;
- verifier output must **not** populate `primary_signature_valid` or `corr_signature_valid`;
- the draft must **not** be used to populate `primary_authorization` or `corr_authorization`;
- no protocol freeze or canonical scientific execution is authorized.
