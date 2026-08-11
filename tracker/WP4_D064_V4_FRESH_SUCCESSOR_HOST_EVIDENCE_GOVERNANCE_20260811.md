# WP4 D-064 V4 Fresh Successor Host-Evidence Governance HE2 — 2026-08-11

**Decision:** `D-063R2-C3B-I2D-D064-V4-HE2`
**Authorization:** `USER_AUTHORIZED_WP4_C3B_I2D_V4_HE2_FRESH_SUCCESSOR_HOST_EVIDENCE_CONTRACT_GOVERNANCE_BINDING_20260811`
**Source commit:** `1a106e0a23244802f443872be77074940818e4ec`
**Source tree:** `dc12cf86ad4f321aad8c62796cf49dd1f892cd43`
**Contract transition:** `0.4.16` → `0.4.17`
**Contract SHA-256:** `e121c9a0f034e47639a644c39992ba07bc3c33e2ff2f4f2234943727e82a0517`
**State:** `FRESH_SUCCESSOR_HOST_EVIDENCE_BOUND_D064_BLOCKED_PENDING_CONSUMER_COMPATIBILITY_REMEDIATION`

## Fresh independently reviewed successor host evidence

- path: `review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json`
- SHA-256: `c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a`
- bytes: `8400`
- schema: `2`
- evidence type: `D064_HOST_EXCLUSIVE_WRITER_PRECONDITION_REFRESH`
- status: `CAPTURED_FRESH_SUCCESSOR_PRECONDITION_EVIDENCE_PENDING_INDEPENDENT_REVIEW_NOT_D064_AUTHORITY`
- observed at UTC: `2026-08-11T23:21:19Z`
- capture gate SHA-256: `f5aa02c3c89bcb119313a105f8606631f4353e7215d01cdc4e757c6c5800633a`
- independent review script SHA-256: `4f9a079ff7954dc3f9f52cf62b8a8a3ba79639c89fe9de508d14f2a6b6577687`
- independent review result: **PASS**
- independent review findings: **0**
- current host re-observation consistent with v3: **true**

The fresh evidence records current `com.apple.macl` SHA-256
`d66d5f6d7ae3cc3cb4144fb7baaa3ac7c6b5bceecbb5be3737eaf52859e061fe` (length `72`) and current
`com.apple.provenance` SHA-256 `f5556b5fbd36d387eebe64c9da92eb21a7af846e790cbd98bfcf742963eb683d` (length
`11`). Both differ from the immutable predecessor capture.
Causation is **not proven**, no internal semantic meaning is used for
authorization, no provenance semantics claim is made, and no xattr
remediation is authorized or performed.

## Frozen transaction-v2 consumer compatibility finding

The accepted transaction-v2 remains SHA-256 `7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29`. Its machine code
requires host-evidence schema `1`, evidence type `D064_HOST_EXCLUSIVE_WRITER_PRECONDITION`, and
status `RETAINED_PRECONDITION_EVIDENCE`. The fresh v3 evidence is schema `2`, evidence
type `D064_HOST_EXCLUSIVE_WRITER_PRECONDITION_REFRESH`, and status `CAPTURED_FRESH_SUCCESSOR_PRECONDITION_EVIDENCE_PENDING_INDEPENDENT_REVIEW_NOT_D064_AUTHORITY`.

Therefore v3 is **not compatible** with the frozen transaction-v2 host-evidence
consumer. HE2 does not modify transaction-v2, generator-v4, verifier-v4, or the
accepted candidate. The active transaction-v2 runtime evidence binding remains
the immutable v2 evidence (`af8bd76dbe81004e58abd0936f7480e371db9c09b149f0529a6f658aee106669`, `6413` bytes) solely to preserve
the already reviewed source-consumer contract; that v2 snapshot is not current
enough for a new D-064 authorization decision.

## Governance disposition

Contract `0.4.17` binds v3 as the current independently reviewed governance
evidence and records the consumer incompatibility. D-064 is now
`BLOCKED_PENDING_FRESH_HOST_EVIDENCE_CONSUMER_SCHEMA_COMPATIBILITY_REMEDIATION`.

A separately governed source/consumer compatibility remediation is required
before D-064 may return to consideration. HE2 does not itself authorize that
source remediation.

## Gates that remain closed

- D-064 authorization: **false**
- D-064 authorization-decision eligibility: **false**
- candidate execution: **false**
- production materialization: **false**
- runtime authorization: **false**
- runtime attempts: **0**
- source remediation: **not authorized / not performed**
- xattr remediation: **not authorized / not performed**
- ACL mutation: **not authorized / not performed**
- Docker/NOS3/Fortytwo execution: **not authorized / not executed**
- event injection: **not authorized / not executed**
- command transmission: **not authorized / not executed**
- baseline execution: **not authorized / not executed**
- Execution #11 rerun: **not authorized**
- WP5 execution: **not authorized**

The next decision is `SEPARATELY_GOVERNED_HOST_EVIDENCE_CONSUMER_SCHEMA_COMPATIBILITY_REMEDIATION_REQUIRED_BEFORE_D064_CONSIDERATION`.
