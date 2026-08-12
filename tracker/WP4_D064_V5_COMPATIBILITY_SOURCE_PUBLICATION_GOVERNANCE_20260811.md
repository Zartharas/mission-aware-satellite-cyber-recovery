# WP4 D-064 V5 Compatibility Source-Publication Governance — 2026-08-11

**Decision:** `D-063R2-C3B-I2D-D064-V5-COMPAT-PUB1`
**Authorization:** `USER_AUTHORIZED_WP4_C3B_I2D_D064_V5_CONTRACT_GOVERNANCE_BINDING_AND_SOURCE_PUBLICATION_20260811`
**Source commit:** `3aadfff088af896d29d7bedd809cf785ef187ee9`
**Source tree:** `1015f68279243b10331d27bc6eca8caba8298f70`
**Contract transition:** `0.4.17` → `0.4.18`
**Contract SHA-256:** `252c4cd069d02783a91cc587c4d019516f3be9b28f5887d866096c8586793add`
**State:** `V5_SOURCE_IMPLEMENTED_INDEPENDENT_REVIEW_PASS_COMPATIBILITY_GOVERNANCE_BOUND_STATIC_VERIFICATION_PENDING_D064_BLOCKED_RUNTIME_NOT_AUTHORIZED`

## Independently reviewed V5 successor source

- transaction-v3: `scripts/nos3_runtime_transaction_v3.py`
  - SHA-256: `ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e`
  - bytes: `441397`
- generator-v5: `scripts/prepare_passive_time_witness_runtime_candidate_v5.sh`
  - SHA-256: `9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7`
  - bytes: `9186`
- verifier-v5: `scripts/verify_passive_time_witness_runtime_candidate_v5_static.sh`
  - SHA-256: `a688ba002b243a07ddb95a7819b19875a7020132812c6fccfc65c01c93eda5c5`
  - bytes: `18171`
- source implementation gate SHA-256: `3be5e2c1a05780e62b8adaf1f2980b1c857656b1e8930f1bc991a1e37059989b`
- independent source-worktree reviewer SHA-256: `a5db61451b245d4216627a776a07a6dd5ad04f32c2ee855e6c490de46869d305`
- independent source-worktree review result: **PASS**
- independent source-worktree findings: **0**

## Deterministic proposed V5 candidate

The reviewed generator was emitted twice into the physical system temporary tree.
The two candidate byte sequences were identical.

- SHA-256: `6d9158287b8addeea41740a2b50538ea545d4d5d3463d649ba5938be7b5b197e`
- bytes: `69951`
- candidate executed: **false**
- accepted candidate identity: **not yet**
- V5 static verification: **PENDING**

## Fresh schema-2 host evidence

- path: `review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json`
- SHA-256: `c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a`
- bytes: `8400`
- schema: `2`
- evidence type: `D064_HOST_EXCLUSIVE_WRITER_PRECONDITION_REFRESH`
- capture status: `CAPTURED_FRESH_SUCCESSOR_PRECONDITION_EVIDENCE_PENDING_INDEPENDENT_REVIEW_NOT_D064_AUTHORITY`
- observed at UTC: `2026-08-11T23:21:19Z`
- capture gate SHA-256: `f5aa02c3c89bcb119313a105f8606631f4353e7215d01cdc4e757c6c5800633a`
- fresh-evidence independent review SHA-256: `4f9a079ff7954dc3f9f52cf62b8a8a3ba79639c89fe9de508d14f2a6b6577687`
- fresh-evidence independent review: **PASS / 0 findings**

The immutable capture-time flags remain capture-time facts. They are not rewritten by
this publication. Current review authority is cross-bound through the separately
published governance envelope.

## Compatibility disposition

Historical HE2 remains immutable: transaction-v2 `7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29` is still incompatible
with fresh schema-2 v3 evidence. This publication does not alter transaction-v2,
generator-v4, verifier-v4, the accepted V4 candidate, HE1, HE2, or Execution #11.

The separately versioned transaction-v3/V5 source line has passed independent source
review for schema-2 governance-envelope compatibility. Production schema-1 fallback is
prohibited. This is a source/contract compatibility state only; it is **not** a V5
static PASS and is **not** a D-064 or runtime authorization.

## Gates that remain closed

- V5 production static-verifier `--verify`: **not authorized / not executed**
- V5 static verification: **PENDING**
- D-064 authorization-decision eligibility: **false**
- D-064 authorization: **false**
- candidate execution: **false**
- production materialization: **false**
- runtime authorization: **false**
- runtime attempts: **0**
- schema-1 V5 production fallback: **false**
- Docker/NOS3/Fortytwo execution: **not authorized / not executed**
- event injection: **not authorized / not executed**
- command transmission: **not authorized / not executed**
- baseline execution: **not authorized / not executed**
- xattr remediation: **not authorized / not performed**
- ACL/ownership/permission mutation: **not authorized / not performed**
- Execution #11 rerun: **false**
- WP5 execution: **not authorized**

The next decision is `SEPARATELY_AUTHORIZED_V5_STATIC_VERIFICATION_REQUIRED_BEFORE_D064_CONSIDERATION`.
