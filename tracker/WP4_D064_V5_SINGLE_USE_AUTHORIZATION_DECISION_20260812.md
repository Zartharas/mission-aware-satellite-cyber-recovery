# WP4 C3B-I2D D-064 V5 Single-Use Authorization Decision

Date: `2026-08-12`
Decision: `D-063R2-C3B-I2D-D064-V5-AUTH1`
Authorization marker: `USER_AUTHORIZED_WP4_C3B_I2D_D064_V5_SINGLE_USE_AUTHORIZATION_DECISION_PUBLICATION_20260812`
Contract transition: `0.4.19` -> `0.4.20`
Source commit: `78b7dfb601aaddea0b286b8463792f70d25b028b`

## Decision

Authorize exactly one future controlled D-064 attempt for the exact V5 candidate
identity below. The authorization is single-use and initially unconsumed.

This governance publication **does not authorize the D-064 execution gate or the
attempt itself**. Candidate execution, production materialization, runtime,
Docker, NOS3, Fortytwo, event injection, command transmission, baseline
execution, static-verifier rerun, Execution #11 rerun, xattr/ACL/ownership
mutation, schema-1 fallback, and WP5 remain unauthorized.

A later separately authorized execution gate must repeat the mutable host checks
immediately before execution and must require the transaction's nonblocking
`fcntl.flock(LOCK_EX|LOCK_NB)` control before any materialization.

## Frozen identities

- V5 candidate SHA-256: `6d9158287b8addeea41740a2b50538ea545d4d5d3463d649ba5938be7b5b197e` (69951 bytes)
- transaction-v3 SHA-256: `ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e`
- generator-v5 SHA-256: `9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7`
- verifier-v5 SHA-256: `a688ba002b243a07ddb95a7819b19875a7020132812c6fccfc65c01c93eda5c5`
- schema-2 host evidence SHA-256: `c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a` (8400 bytes)
- static report SHA-256: `7268ebfb15f5929a90e1ffbb4e42b926eb46dec740fc92237857208bf9c5a8ac`
- static evidence manifest SHA-256: `11d515856942d096d75dbdea1731317feb7031a57ba93597df52c40c841842a3`
- R3 readiness reviewer SHA-256: `6c861907d4aacc62ec2cd6fbcfa4e63d18880b8b5f3f24000ba29843a89a6665` (25331 bytes), result `PASS`, findings `0`
- independent readiness reviewer SHA-256: `d1cbfa46fd8cfd6aac48ee98c4232d90fea85edb48a7ddbe9602b2686035e1b3` (25649 bytes), result `PASS`, findings `0`
- successor contract SHA-256: `7a2ad901ceffec6fe3cfb10b7d6c926313e3c2cab5844506a9d9a39fd1bf2d79` (170290 bytes)
- successor decision log SHA-256: `4c470992ccd6923e4bba15b1f66add7504a33bec17c7ebe376f422b82f171e6f` (82608 bytes)

## Authorization state after publication

- `d064_authorized=true`
- `d064_authorization_single_use=true`
- `d064_authorization_consumed=false`
- `authorization_scope_attempt_limit=1`
- `d064_execution_authorized=false`
- `d064_execution_attempts_authorized=0`
- `d064_execution_attempts=0`
- `runtime_authorized=false`
- `runtime_attempts=0`
- `production_candidate_execution_count=0`
- `production_materialization_count=0`
- `static_verifier_rerun_authorized=false`
- `execution_11_rerun_authorized=false`
- `schema1_production_fallback_allowed=false`
- `wp5_execution_authorized=false`

## Preserved limitation

`EXTERNAL_NONCOOPERATING_WRITER_ABSENCE_PROVEN=false`

`FRESH_CONTENTION_PROBE_PERFORMED=false`

The two readiness reviews establish current-host consistency with the retained
schema-2 evidence; they do not prove the absence of a privileged or
noncooperating writer.

## Next boundary

`SEPARATELY_AUTHORIZED_SINGLE_USE_D064_EXECUTION_GATE_REQUIRED`

No D-064 attempt is performed by this publication.
