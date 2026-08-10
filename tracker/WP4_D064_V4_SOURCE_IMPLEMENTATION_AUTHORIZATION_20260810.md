# WP4 D-064 V4 Source-Implementation Authorization

Date: 2026-08-10
Governance ID: `D-063R2-C3B-I2D-D064-SIA1`
Phase: `SOURCE_IMPLEMENTATION_AUTHORIZATION_ONLY`
Published R2 design commit: `e8547fec461fd2034913ef4ce71abb9989c42839`
Published R2 design tree: `ea02d1ca825c4875f50aa9c98f587ef68408f046`
Active contract at authorization: `0.4.13`
Authorized successor implementation contract revision: `0.4.14`
D-064 authorization: `false`
Runtime authorization: `false`
Runtime attempts authorized: `0`
WP5 execution authorization: `false`

## 1. Governing disposition

This record authorizes one later, separately executed and independently reviewed
versioned-v4 **source implementation phase** derived from the published R2
remediation design.  This authorization does not itself implement source,
change the active contract, emit or execute a production candidate, execute the
production static verifier, select or create a D-064 authorized root, authorize
D-064, run Docker/NOS3/Fortytwo, materialize a production transaction, inject
events, establish a scientific outcome, or start WP5.

The active repository state at this gate remains contract `0.4.13` and the
historical execution-#10 v3 static-PASS identity chain.  Those v3 bytes remain
historical and immutable.

## 2. Bound published design

The implementation must conform to the published R2 design:

- design record:
  `tracker/WP4_D064_EXCLUSIVE_WRITER_TECHNICAL_CONTROL_REMEDIATION_DESIGN_R2_20260810.md`
  SHA-256 `af2eefcc65b4f23d38c492b46d2535c1aae8b5c058477fa50fe30e8e416d1722`;
- design lock:
  `artifacts/wp4-d064-exclusive-writer-technical-control-remediation-design-r2-lock.txt`
  SHA-256 `9c4ed6ca97cf7ca6b6e991c53a2e5b0b2b9c4cc32ccc6cd8a4e1a96756ac8293`;
- active contract `0.4.13` SHA-256
  `f161169bf8096be3c9f94718c460ad3d39b6b6b6a43c1d633d3c3ec210ac15d2`;
- historical transaction-v1, generator-v3, candidate-v3, and verifier-v3 remain
  unchanged and are not edited in place;
- canonical runtime-material manifest remains unchanged.

## 3. Authorized future implementation mutation scope

Only a later source-implementation phase may mutate/create the following
implementation/governance paths:

1. `configs/downlink-diagnostic-contract.json`
2. `scripts/nos3_runtime_transaction_v2.py`
3. `scripts/prepare_passive_time_witness_runtime_candidate_v4.sh`
4. `scripts/verify_passive_time_witness_runtime_candidate_v4_static.sh`
5. `tracker/WP4_D064_V4_SOURCE_IMPLEMENTATION_20260810.md`
6. `artifacts/wp4-d064-v4-source-implementation-lock.txt`
7. `tracker/RESEARCH_TRACKER.md`
8. `tracker/decision_log.csv`
9. `tracker/work_packages.csv`

No historical v3 implementation file, canonical manifest, witness source, trace
validator, socket shim, retained execution-#10 evidence, WP5 artifact, or
third-party source is authorized for mutation.

The implementation phase may assign successor contract revision `0.4.14`.
The resulting contract must remain implementation-only with a V4 static gate
pending, runtime authorization false, runtime attempts zero, D-064 unauthorized,
and WP5 unauthorized.

## 4. Required V4 implementation semantics

The implementation must preserve all controls already accepted in transaction-v1
and add the published R2 remediation controls without weakening any prior
fail-closed condition.

The transaction-v2 implementation must include:

- descriptor-bound Darwin ACL inspection using the Darwin ACL API;
- first-attempt policy `NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT`;
- fail-closed ACL retrieval/parsing behavior;
- ACL revalidation immediately before outer transaction publication;
- advisory serialization with `fcntl.flock(LOCK_EX|LOCK_NB)`;
- lock acquisition before staging;
- lock held through the transaction `finally` boundary;
- contention failure before staging/materialization;
- lock object validation as a regular single-link object owned by the effective
  UID, mode `0600`, and on the authorized-root device;
- no claim that advisory locking proves the absence of a non-cooperating writer;
- SHA-256 binding of actual retained host-evidence bytes;
- transaction-receipt binding to that same host-evidence SHA-256;
- receipt disposition for ACL validation and serialization controls.

The detailed host-evidence content schema may be frozen by the later
implementation only to the minimum structure required to support the published
authority model.  Host-evidence path text is not authorization authority.  The
actual retained evidence SHA-256 is authority and must later be contract-bound
before any D-064 consideration.

## 5. Authorized non-runtime implementation validation

The later implementation phase may perform only source-level and synthetic
validation necessary to establish an implementation candidate:

- Python/Bash syntax checks;
- static source inspection;
- transaction-v2 self-tests using synthetic temporary fixtures only;
- verifier-v4 `--selftest` using synthetic fixtures only;
- deterministic generator-v4 double emission into temporary non-repository
  output paths;
- SHA-256 comparison of the two emitted candidate byte streams;
- Bash syntax validation of the emitted candidate;
- non-executing candidate source/order review;
- deterministic construction and hashing of the implementation record/lock.

These permissions do not authorize production materialization, candidate
execution, a production verifier `--verify`, Docker, NOS3, Fortytwo, networking,
event injection, command transmission, baseline execution, or scientific claims.

Synthetic self-test temporary directories are test fixtures and are not D-064
authorized roots.  No retained host-exclusive-writer evidence artifact may be
created by this phase.

## 6. Explicit closed gates

After this authorization record is published, and throughout the later source
implementation phase unless a new separately published decision says otherwise:

- production static-verifier execution #11 authorization: `false`;
- execution #10 rerun authorization: `false`;
- production candidate execution authorization: `false`;
- production materialization authorization: `false`;
- authorized-root selection authorization: `false`;
- authorized-root creation authorization: `false`;
- retained host-exclusive-writer evidence creation authorization: `false`;
- D-064 authorization: `false`;
- runtime authorization: `false`;
- runtime attempts authorized: `0`;
- event injection authorization: `false`;
- WP5 execution authorization: `false`.

## 7. Implementation acceptance boundary

Completion of source coding and synthetic validation will not itself establish a
V4 static PASS or FAIL.  A completed V4 implementation must be independently
reviewed and published first.  Only after that publication may a separate
authorization consider production static-verifier execution #11.

The current v3 static PASS cannot be reused for V4.

## 8. Next gate

After independent review and publication of this authorization record:

`C3B_I2D_D064_V4_SOURCE_IMPLEMENTATION`

That later gate is implementation-only.  Execution #11, D-064, authorized-root
selection/creation, retained operational evidence creation, runtime, and WP5
remain separate future gates.
