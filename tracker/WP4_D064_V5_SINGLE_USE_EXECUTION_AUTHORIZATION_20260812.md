# WP4 C3B-I2D D-064 V5 Single-Use Execution Authorization

Date: `2026-08-12`
Decision: `D-063R2-C3B-I2D-D064-V5-EXECAUTH1`
Authorization marker: `USER_AUTHORIZED_WP4_C3B_I2D_D064_V5_SINGLE_USE_EXECUTION_AUTHORIZATION_GOVERNANCE_PREPARATION_AND_PUBLICATION_20260812`
Contract transition: `0.4.20` -> `0.4.21`
Source commit: `badec792ac492144f8db0c9d7a4bd3c82a14123b`
Source tree: `af69a6967d6d93cc58708ca7164f5f09032ef6a9`

## Decision

Publish the repository governance state required to open exactly one future
bounded D-064 V5 execution/runtime attempt for the already accepted candidate
identity `6d9158287b8addeea41740a2b50538ea545d4d5d3463d649ba5938be7b5b197e`.

This publication opens the repository execution predicates required by the
reviewed candidate, but **does not itself authorize or perform the actual D-064
invocation**. The actual invocation remains a separate user-authorized phase.
No candidate emission, candidate execution, production materialization,
Docker, NOS3, Fortytwo, event injection, command transmission, baseline
execution, static-verifier rerun, Execution #11 rerun, xattr/ACL/ownership
mutation, schema-1 fallback, or WP5 execution occurs in this phase.

## Predecessor authorization

- decision: `D-063R2-C3B-I2D-D064-V5-AUTH1`
- record SHA-256: `1fa1cf66ea1307a6ab4a6e52e65e5a6e9c9ed0bee7763e8ff9221c90d6053574` (3342 bytes)
- lock SHA-256: `b20d477cb1f2d2632a1458412d3647d9e1beecbee5b3bbc21f2b8ca699aa1f0d` (3021 bytes)
- predecessor state: `AUTHORIZED_SINGLE_USE_UNCONSUMED_EXECUTION_NOT_AUTHORIZED_RUNTIME_NOT_AUTHORIZED`

AUTH1 remains single-use and unconsumed at publication time.

## Frozen execution identity

- V5 candidate SHA-256: `6d9158287b8addeea41740a2b50538ea545d4d5d3463d649ba5938be7b5b197e` (69951 bytes)
- transaction-v3 SHA-256: `ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e` (441397 bytes)
- generator-v5 SHA-256: `9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7` (9186 bytes)
- verifier-v5 SHA-256: `a688ba002b243a07ddb95a7819b19875a7020132812c6fccfc65c01c93eda5c5` (18171 bytes)
- canonical manifest SHA-256: `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd`
- schema-2 host evidence SHA-256: `c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a` (8400 bytes)
- static report SHA-256: `7268ebfb15f5929a90e1ffbb4e42b926eb46dec740fc92237857208bf9c5a8ac`
- static evidence manifest SHA-256: `11d515856942d096d75dbdea1731317feb7031a57ba93597df52c40c841842a3`

## Repository execution gate after publication

- `d064_authorized=true`
- `d064_authorization_single_use=true`
- `d064_authorization_consumed=false`
- `authorization_scope_attempt_limit=1`
- `d064_execution_authorized=true`
- `d064_execution_attempts_authorized=1`
- `d064_execution_attempts=0`
- `diagnostic_runtime_authorized=true`
- `diagnostic_runtime_attempts_authorized=1`
- `amendment_runtime_authorized=true`
- `amendment_runtime_attempts=1`
- `implementation_runtime_authorized=true`
- `implementation_runtime_attempts=1`
- `accepted_runtime_entrypoint_v5_identity_only_not_authorized=false`
- `d064_status=AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT`

The gate state is initially unconsumed and unexecuted.

## Execution-time requirements intentionally deferred

- `execution_time_host_recheck_required=true`
- `fresh_contention_probe_performed=false`
- `execution_time_nonblocking_flock_required=true`
- `external_noncooperating_writer_absence_proven=false`

The fresh host/contention observations and the nonblocking execution lock must
be handled immediately before the actual attempt in the separately authorized
execution phase. This publication does not manufacture those observations or
claim absence of a privileged/noncooperating writer.

## Successor governance identities

- successor contract SHA-256: `798bf3e93ab70118d70899b917ba3ae8a4b469d84d24f7f78ef041d5d18268b8` (174722 bytes)
- successor decision log SHA-256: `18569986581581bba062e96b6c19a96e1bf9757652b0b15ad5057a5a68e6882a` (84254 bytes)

## Next boundary

`SEPARATE_D064_EXECUTION_INVOCATION_AUTHORIZATION_REQUIRED`

No D-064 attempt is performed by this publication.
