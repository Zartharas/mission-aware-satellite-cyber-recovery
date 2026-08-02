# WP4 Checkpoint 1 Cleanup Threat-Model Amendment

- Amendment identifier: D-063R2-TM1
- Date approved: 2026-07-31
- Checkpoint: WP4 Checkpoint 1 (documentation-only)
- Phase: WP4 v3 combined implementation, pre-implementation threat-model record
- Record type: Governance-only threat-model amendment. Documentation only.
- Mutability: This amendment does not modify the implementation tool, the manifest,
  the downlink-diagnostic contract, retained evidence, external/nos3, external/fortytwo,
  any implementation, test, candidate, verifier, or runtime file.

## 1. Purpose

Record the approved cleanup threat-model amendment for the Checkpoint 1 workspace
materialization and failure-cleanup path. This amendment restates the cleanup
concurrency model, the scope boundary of the Checkpoint 1 cleanup guarantee, the
defense-in-depth controls that are still required, and the D-064 runtime-authorization
dependency on a proven exclusive-writer operational prerequisite.

This amendment:
- does not accept Checkpoint 1 implementation by itself;
- does not authorize staging, commit, runtime, or any attempt;
- does not weaken any existing identity, manifest, publication, authorization, or
  exclusion/deny-pattern control.

## 2. Immutable implementation identities (unchanged by this amendment)

| Artifact | SHA-256 | Mode |
|---|---|---|
| scripts/nos3_runtime_material.py | 9c1b1e0abcb7e30df40df8c91c4ce9ec600571a575c68a26b978b5778075c15f | 0755 |
| manifests/nos3-runtime-material-manifest.json | 5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd | 0644 |

Contract version at amendment time: 0.4.11 (unchanged).
external/nos3 HEAD: 5a3bdee6be9a2c67fdf994ae6db56d5c60395302 (unchanged, clean).

## 3. Normative decision (recorded precisely)

During workspace materialization and failure cleanup, the retained authorized-root
directory and every staging directory are required to be exclusively writable by
the materializer's operating-system identity for the duration of the transaction.

Descriptor-relative traversal, O_NOFOLLOW opens, device/inode continuity checks,
retained directory descriptors, destination audits, and atomic no-replace
publication protect against:

- symlink substitution;
- stale pathname use;
- accidental object replacement;
- unsupported destination objects;
- changes detected before the final removal or publication operation;
- overwrite of a pre-existing final workspace.

Checkpoint 1 does not claim protection against a concurrent hostile process that
already possesses the same effective filesystem write authority and mutates a
cleanup basename during the final unlink() or rmdir() syscall window.

That same-authority concurrent-mutation case is outside the Checkpoint 1 cleanup
guarantee.

This limitation applies only to cleanup-name removal.

It must not weaken:

- source identity verification;
- manifest verification;
- destination completeness auditing;
- exclusion and deny-pattern enforcement;
- per-file no-replace publication;
- final workspace no-replace publication;
- runtime authorization gates.

D-064 must not authorize runtime until the operational environment proves the
exclusive-writer prerequisite.

D-064 evidence must include, at minimum:

1. The authorized-root directory is owned or controlled by the dedicated
   materializer identity.

2. The authorized root is not group-writable or world-writable unless an
   independently reviewed access-control mechanism proves that no other principal
   can mutate it.

3. Filesystem ACLs, container mounts, bind mounts, shared volumes, and host
   permissions do not grant another process concurrent write access.

4. Staging directories are created with mode 0700 or a stricter equivalent.

5. Workspace materialization is serialized so only one materializer transaction
   can operate on the authorized root at a time.

6. No maintenance, cleanup, synchronization, antivirus, indexing, backup, or
   orchestration process writes into the authorized root during the transaction.

7. The operating identity, authorized-root device/inode, ownership, mode, ACL
   state, and serialization control are captured as retained evidence before the
   first authorized runtime attempt.

8. A failure of any exclusive-writer prerequisite keeps runtime authorization
   false and D-064 BLOCKED.

## 4. Assurance classification

| Control | Classification |
|---|---|
| cleanup_concurrency_model | EXCLUSIVE_WRITER_OPERATIONAL_PRECONDITION |
| same_authority_concurrent_mutation | OUTSIDE_CHECKPOINT_1_GUARANTEE |
| descriptor_relative_identity_controls | REQUIRED_DEFENSE_IN_DEPTH |
| atomic_final_publication | REQUIRED_NO_REPLACE |
| d064_runtime_authorization_dependency | EXCLUSIVE_WRITER_EVIDENCE_REQUIRED |

These classifications are exact and normative for this amendment.

## 5. Current status (recorded)

- implementation tool identity remains
  9c1b1e0abcb7e30df40df8c91c4ce9ec600571a575c68a26b978b5778075c15f;
- manifest identity remains
  5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd;
- this amendment does not accept Checkpoint 1 implementation by itself;
- test-integrity review remains pending;
- Checkpoint 2 remains unauthorized;
- staging and commit remain unauthorized;
- runtime authorization remains false;
- runtime attempts remain zero;
- D-064 remains BLOCKED.

## 6. Scope boundary and non-claims

- This amendment is a threat-model record only. It does not implement any file,
  candidate, verifier, or runtime path.
- This amendment does not authorize a telemetry runtime, diagnostic, baseline,
  command transmission, event injection, Docker invocation, build, compile, or
  scientific outcome.
- This amendment does not claim a portable guarantee against same-authority
  concurrent cleanup basename replacement; that case is explicitly outside the
  Checkpoint 1 cleanup guarantee.
- This amendment does not weaken source-identity, manifest, destination-audit,
  exclusion/deny-pattern, per-file no-replace, final-workspace no-replace, or
  runtime-authorization controls.
- This amendment makes no scientific, mission-impact, generic-radio-defect,
  CryptoLib, or SDLS claim.

## 7. Next required step

Final bounded test-integrity review of the Checkpoint 1 implementation remains
pending. No staging, commit, runtime, or attempt is authorized by this record.
D-064 remains BLOCKED until the exclusive-writer operational prerequisite is
proven and a separate explicit D-064 governance decision authorizes it.
