# WP4 D-064 V4 Successor Host-Evidence Governance — 2026-08-11

**Decision:** `D-063R2-C3B-I2D-D064-V4-HE1`
**Authorization:** `USER_AUTHORIZED_WP4_C3B_I2D_V4_SUCCESSOR_EVIDENCE_CONTRACT_GOVERNANCE_BINDING_20260811`
**Source commit:** `af002020edde5490085446207eb3b754ab893ba5`
**Source tree:** `4d798b2d3b5bc082695ab5a70c87e48f9329d50c`
**Contract transition:** `0.4.15` → `0.4.16`
**State:** `SUCCESSOR_HOST_EVIDENCE_BOUND_D064_NOT_AUTHORIZED`

## Independently reviewed successor host evidence

- path: `review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v2.json`
- SHA-256: `af8bd76dbe81004e58abd0936f7480e371db9c09b149f0529a6f658aee106669`
- bytes: `6413`
- schema: `1`
- status: `RETAINED_PRECONDITION_EVIDENCE`
- R5 preparation gate SHA-256: `5adc4800cbd4c267bf6dcdfbbfd67e90088b3dddbda6a777baff0ab082a0c1bf`
- independent successor review script SHA-256: `3bc3bcce7ea91a9eb987a5c13ed8435c167030871dd15dd691e07ad470b5894d`
- independent successor review result: **PASS**
- independent successor review findings: **0**

## Authorized-root and serialization state

The independently reviewed retained root is
`/Users/zarthras/.wp4-d064-v4-authorized-root`, device `16777221`, inode
`359966629`, UID `599`, GID `20`, mode `0700`, with zero extended ACL
entries. It was empty at the independent review and the transaction lock was
absent after the serialization probe.

Serialization readiness was demonstrated under the dedicated materializer UID
using `fcntl.flock(LOCK_EX|LOCK_NB)`, a mode-`0600` lock, and an independent
cross-process contention rejection. The lock is advisory. The evidence does
**not** prove absence of a privileged or otherwise noncooperating writer.

## Parent traversal and accepted retained metadata finding

The accepted parent traversal state is limited to
`user:wp4d064mat allow search` on `/Users/zarthras/Documents`, with no
inheritance. UID `599` can traverse to and read the reviewed repository inputs
but cannot list or write the `Documents` directory.

The retained `com.apple.provenance` extended attribute is accepted only as a
documented host metadata side effect with length `11` and
SHA-256 `739fa17afddf55e97efadf89eebac7c3b0dae01478a2634454d592b3073d4df0`. Causation is **not proven**, no semantic or
security meaning is assigned, and cleanup/removal is **not authorized**.
`com.apple.macl` remained bound to SHA-256 `fa684fb95f30efabd12c9e2c52418f015d17c0f465d531bde3f7eff15495501a`.

## Governance result

Contract `0.4.16` binds the exact successor host-evidence path and SHA-256 and
records the independently reviewed authorized-root, serialization, and
least-privilege parent-traversal state. The accepted V4 candidate remains
identity-only and is not runtime-authorized.

D-064 remains
`READY_FOR_SEPARATE_D064_CONSIDERATION_NOT_AUTHORIZED`. This governance
binding does **not** itself authorize D-064, candidate execution, production
materialization, or any runtime attempt.

## Gates that remain closed

- D-064 authorization: **false**
- candidate execution: **not authorized / not executed**
- production materialization: **not authorized / not executed**
- runtime authorization: **false**
- runtime attempts: **0**
- Docker/NOS3/Fortytwo execution: **not authorized / not executed**
- event injection: **not authorized / not executed**
- command transmission: **not authorized / not executed**
- baseline execution: **not authorized / not executed**
- Execution #11 rerun: **not authorized**
- WP5 execution: **not authorized**

The next permissible governance step after independent review and publication
of this HE1 package is a separate explicit D-064 decision.
