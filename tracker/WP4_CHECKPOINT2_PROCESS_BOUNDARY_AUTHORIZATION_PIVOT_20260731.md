# WP4 Checkpoint 2PB1 Process-Boundary Authorization Pivot

- Decision identifier: D-063R2-PB1
- Date approved: 2026-07-31
- Checkpoint: WP4 Checkpoint 2PB1 (documentation-only)
- Phase: WP4 v3 combined implementation, process-boundary authorization pivot record
- Record type: Governance-only architectural pivot decision. Documentation only.
- Mutability: This decision does not modify the implementation tool, the manifest,
  the downlink-diagnostic contract, retained evidence, external/nos3, external/fortytwo,
  any implementation, test, candidate, verifier, or runtime file.

## 1. Purpose

Record the approved architectural pivot from an in-process Python bearer boundary to a
separate-process authorization and materialization boundary. This checkpoint is
documentation-only and authorizes no code, no implementation, no candidate, no transaction,
no materialization, no Docker, and no runtime attempt.

## 2. Immutable identities at decision time (unchanged by this decision)

| Artifact | SHA-256 | Role at decision time |
|---|---|---|
| scripts/nos3_runtime_material.py | 37c2a033f8b0fb0de17d1940c1cc12c13c52de4ec415a0e4afa16cb7dbc9e51c | retained experimental source |
| manifests/nos3-runtime-material-manifest.json | 5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd | canonical manifest |
| configs/downlink-diagnostic-contract.json | 8ccca3104564abccfdecb715374bca77ea8c70953e7525bdb6f026acef25b3b7 | closed contract 0.4.11 |

Contract version at decision time: 0.4.11 (unchanged, closed).
external/nos3 HEAD: 5a3bdee6be9a2c67fdf994ae6db56d5c60395302 (unchanged, clean).

The current tool SHA 37c2a033... must not be treated as an accepted production
runtime-material tool identity. It remains the retained source for the accepted
Checkpoint 1 core, the accepted Checkpoint 2B1R2 self-test isolation evidence, and the
rejected Checkpoint 2B1 in-process authorization experiment.

## 3. Decision

1. The Checkpoint 2B1R2 self-test isolation correction is accepted.
2. The production authorization architecture based on MaterializationAuthorized,
   authorize_v3_materialization(), an in-process weak registry, a closure-contained
   issuer, and a bearer passed into materialize_workspace() is rejected.
3. Python closure cells, function objects, class methods, registries, and mutable objects
   inside the same interpreter are not treated as a security boundary against code
   executing in that interpreter.
4. The host v3 candidate must not import nos3_runtime_material.py.
5. The host v3 candidate must invoke the runtime-material tool as a separate operating-system
   process.
6. Authorization and all materialization activity must occur in one tool process.
7. No authorization bearer, registry object, issuer, token, secret, receipt object, or
   capability is returned to or shared with the candidate.
8. A successful authorization decision must be retained only as internal process-local
   transaction state.
9. The production process call graph is:

   host v3 candidate
     -> execute runtime-material tool as a separate CLI process
     -> open and bind repository root
     -> validate actual contract bytes
     -> validate candidate identity
     -> validate executing tool identity
     -> validate canonical manifest identity and contents
     -> validate D-064 structured authorization
     -> validate exclusive-writer operational prerequisites
     -> create one outer private staging transaction
     -> materialize all 18 private NOS3 workspaces
     -> create separate Fortytwo configuration scratch
     -> verify every workspace and scratch object
     -> atomically publish the complete transaction root
     -> emit one success marker and transaction receipt
     -> exit

10. Docker remains outside the materialization process.
11. Docker may be invoked by the host candidate only after the runtime-material process
    exits successfully and the published transaction receipt is validated.
12. Under the current contract 0.4.11, the future production CLI must fail before
    authorized-root inspection, staging creation, workspace creation, source copying,
    Fortytwo scratch creation, materialization, Docker, fake Docker, and retained-runtime
    evidence creation.

## 4. Implementation disposition (recorded exactly)

CHECKPOINT_1_MATERIALIZATION_CORE=ACCEPTED

The accepted core includes canonical manifest generation and verification; the
VerifiedManifest registry boundary; descriptor-bound source traversal; descriptor-relative
destination mutation; exact workspace-policy validation; source and destination identity
checks; exclusion and deny-pattern enforcement; no-replace file and workspace publication;
complete destination audit; and cleanup under D-063R2-TM1.

CHECKPOINT_2B1R2_SELFTEST_ISOLATION=ACCEPTED

The accepted isolation correction includes the temporary regular-file manifest copy; no
write to the canonical manifest; temporary-manifest drift invalidating authorization; the
canonical-manifest identity guard; and removal of the misleading duplicate stale-bearer test.

CHECKPOINT_2B1_IN_PROCESS_AUTHORIZATION=REJECTED

The rejected layer includes MaterializationAuthorized; authorize_v3_materialization(); the
closure-contained _issue function; the in-process authorization registry; bearer-based
_require_auth(); and --authorize-v3-check as the proposed production authorization boundary.

## 5. Next implementation architecture

The subsequent code checkpoint must replace the rejected authorization layer with a
process-boundary transaction CLI. The expected production CLI is conceptually
`--materialize-v3-transaction`. The final exact arguments will be locked during the
implementation prompt, but the CLI must receive or derive repository root, contract path,
canonical manifest path, candidate path, authorized transaction root, and final transaction
basename. The runtime-material tool must identify itself from __file__ and must not trust a
caller-supplied tool hash or alternate tool path as authority.

## 6. Process-local authorization context

The future implementation may use an internal process-local data structure after successful
validation. That context is not a security bearer; is not returned to the caller; is not
serialized; is not written to the contract; is not stored in a module-global registry; is not
passed across a process boundary; exists only for the lifetime of one CLI transaction; and
contains descriptor-bound identities and opened descriptors required by the transaction. It
must be destroyed when the process exits.

## 7. Outer transaction model

Use one outer run-scoped staging directory beneath the authorized root. Required conceptual
layout:

```
<authorized-root>/
  <final-run-basename>.staging-<unpredictable-suffix>/
    workspaces/
      nos_engine/
      time_driver/
      hw_sim_01/
      hw_sim_02/
      hw_sim_03/
      hw_sim_04/
      hw_sim_05/
      hw_sim_06/
      hw_sim_07/
      hw_sim_08/
      hw_sim_09/
      hw_sim_10/
      hw_sim_11/
      hw_sim_12/
      hw_sim_13/
      hw_sim_14/
      cmd_bus_bridge/
      cfs/
    fortytwo/
      configuration/
    transaction-receipt.json
```

All 18 workspaces remain private physical writable copies. The separate Fortytwo configuration
scratch is not counted as one of the 18 workspaces. No live external/nos3 path may be mounted
into runtime containers. The transaction must not publish individual workspaces separately.
After every component is materialized and independently verified, publish the complete outer
transaction directory through one atomic no-replace rename:

```
<final-run-basename>.staging-...  ->  <final-run-basename>
```

A failure before outer publication must remove the complete staging transaction under the
accepted D-063R2-TM1 exclusive-writer prerequisite. No partially published final transaction
may remain.

## 8. Transaction receipt

The later implementation must create a canonical transaction receipt inside the staging
transaction before final publication. The receipt must include at minimum: schema; repository
device and inode; contract relative path, device, inode, and SHA-256; candidate relative path,
device, inode, and SHA-256; executing-tool relative path, device, inode, and SHA-256;
canonical-manifest relative path, device, inode, and SHA-256; authorized-root device and
inode; final transaction basename; all 18 component IDs; Fortytwo scratch identity;
per-workspace verification disposition; aggregate workspace count; aggregate included file
count; aggregate copied byte count; no-replace publication disposition; exclusive-writer
evidence references; and runtime attempt value. Do not define a timestamp, random identifier,
or host-dependent value as an implementation identity. The receipt is runtime evidence only
after a later D-064 authorization and actual execution. No receipt is created in this
documentation checkpoint.

## 9. Exclusive-writer requirements

D-063R2-TM1 is preserved. The future production CLI must technically validate what it can,
including authorized-root type; authorized-root owner; authorized-root mode; no group/world
write unless separately reviewed and explicitly permitted; no unexpected ACL grants; staging
mode 0700; authorized-root device/inode binding; serialized transaction lock; no existing
final basename; no existing staging basename collision; and no symlinked path components. The
following remain D-064 retained operational evidence: dedicated materializer operating
identity; no concurrent maintenance writer; no concurrent indexing writer; no concurrent backup
writer; no concurrent orchestration writer; mount/shared-volume access review; ACL review;
serialization evidence; and retained pre-runtime device/inode, owner, mode, and ACL capture.

## 10. Candidate responsibilities

The future host candidate must calculate its own SHA-256; validate that it equals
gate.accepted_runtime_entrypoint_v3_sha256; verify schema 1 structured authorization; invoke
the runtime-material tool as a separate process; pass explicit canonical paths and transaction
destination; require one exact successful completion marker; validate the published transaction
receipt; and invoke Docker only after materialization success. The candidate must not import the
runtime-material Python module; access Python closures or registries; mint an authorization
capability; pass a parsed contract dictionary; pass proposed identity as authorization;
materialize workspaces itself; mount external/nos3 directly; or invoke Docker before
transaction publication.

## 11. Status recorded

- D063R2_PB1_DECISION=APPROVED
- CHECKPOINT_1_MATERIALIZATION_CORE=ACCEPTED
- CHECKPOINT_2B1R2_SELFTEST_ISOLATION=ACCEPTED
- CHECKPOINT_2B1_IN_PROCESS_AUTHORIZATION=REJECTED
- PROCESS_BOUNDARY_ARCHITECTURE=REQUIRED
- CURRENT_TOOL_PRODUCTION_IDENTITY_ACCEPTED=false
- CURRENT_TOOL_RETAINED_AS_EXPERIMENTAL_SOURCE=true
- CHECKPOINT_2PB2_IMPLEMENTATION_AUTHORIZED=false
- GENERATOR_IMPLEMENTATION_AUTHORIZED=false
- CHECKPOINT_3_AUTHORIZED=false
- STAGING_AUTHORIZED=false
- COMMIT_AUTHORIZED=false
- RUNTIME_AUTHORIZED=false
- RUNTIME_ATTEMPTS=0
- D064_STATUS=BLOCKED

## 12. Scope boundary and non-claims

- This decision is documentation only. It implements no file, candidate, verifier, transaction,
  or runtime path.
- This decision does not authorize staging, commit, runtime, any attempt, Docker, fake Docker,
  compilation, generator creation, candidate emission, or retained runtime evidence.
- This decision does not accept the current tool SHA as a production identity.
- This decision makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS
  claim.

## 13. Next required step

The process-boundary transaction CLI implementation remains separately governed. No staging,
commit, runtime, or attempt is authorized by this record. Runtime authorization remains false;
runtime attempts remain zero; D-064 remains BLOCKED.
