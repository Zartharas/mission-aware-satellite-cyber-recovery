# Paper 2 P2X — v2f runtime dependency inventory and materializer/verifier design review

**Scope:** authorized **static design review only**, at exact successful #1422 baseline `98b57564c6f448299b63584e32dc0aeabb023725` (run ID `37796520897`). This does not create an inventory from the author's preserved host bytes, a workspace, a runtime experiment, or scientific evidence.

## Authority and observed proof

The 2026-10-07 v2f dual offline build has nine matching raw artifacts across independent `primary/source` and `repeat/source` candidates. Its protected manifest is `artifacts/runtime/p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1/p2x-v2f-build-manifest.json`, with sole-author host-observed SHA-256 `cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee`. The build head is `8f5faef3830646eae065e8210216a2ed4301316c`. The full runtime dependency closure **has not been measured or accepted**.

## Code-derived dependency classification

The companion JSON matrix enumerates 11 source-code-derived dependency **classes**; each is explicitly marked unverified for runtime (including the nine reproducible outputs). It covers:

1. Nine built artifacts as reproducible outputs only, **not** run readiness.
2. `sims/build/bin`, `sims/build/lib`, simulator assets and bridge.
3. cFS `fsw/build/exe/cpu1`, support libraries, `cf/`, `data/`, table/configuration dependencies and controlled writable overlays.
4. `cfg/build/InOut`, NOS3 simulator configuration, NOS engine JSON resources.
5. CryptoLib / GSW `gsw/build` support beyond the qualified `standalone` binary.
6. The separately pinned FortyTwo `42` candidate plus all discovered companion assets.
7. FortyTwo input derivatives: copy `Inp_Sim.txt` and `Inp_IPC.txt` *only to run-scoped inputs*; a headless `FALSE` change must have before/after bytes, explanation and digest. The pinned IPC blocking-order checks must be independently reviewed, not assumed.
8. OCI-image executable `/usr/bin/nos_engine_server_standalone`, container libraries and runtime platform/mqueue assumptions.
9. Internal network identities, engine, truth sink, radio and cFS command ingress are **interface requirements**, not artifacts with observed runtime readiness.
10. Git/submodule metadata, case/Unicode collisions, source symlinks, special filesystem entries, hardlink aliases and permission preservation.
11. Evidence/logs/temporary files and all mutable runtime state, isolated from frozen source inputs.

The legacy WP4 materializer `scripts/nos3_runtime_material.py` names `external/nos3` source roots and July-specific exclusions. It is a **reference for design safeguards**, not a production-ready v2f source manifest and not an authorized v2f copy path. Do not automatically import its exclusions or a previous historical PASS.

## Proposed materializer interface — specification, not implementation

A future `--plan` operation would consume only a separately authorized complete recursive inventory and an exact parent SHA-256/pin binding. A later independently authorized `--materialize` would stage into a unique run-scoped directory under ignored `artifacts/runtime`, with exclusive creation, no direct execution of preserved evidence, no source hardlinks, no symlink escape, no missing/unclassified file kinds, explicit exact-path exclusions, frozen-binary preservation and separately staged pinned FortyTwo material. A deterministic canonical inventory plus detached SHA-256 would bind every source-to-destination path/type/size/mode/hash/target. The preexisting staged or published workspace must cause a HOLD, not a merge/overwrite. Atomic publication must occur only after independent verification, followed by a separate post-publication readback.

No host inventory, copier, manifest emitter, directory staging, or runtime adapter is authorized or implemented by this review.

## Independent verifier design and acceptance

The future verifier must be separately implemented and must not import the copier as its source of expected files. It must load a verified manifest independently, rewalk the **whole** source and destination namespaces without following untrusted links, verify all selected file bytes and file metadata, verify exclusions and directory coverage, reject unexpected or missing entries, test aliasing/hardlinks and path traversal, inspect 42 binary provenance and run-scoped headless InOut derivations, and recheck the protected source/evidence before and after. A complete dependency-closure proof is a separate gate; nine byte-identical build outputs alone can never satisfy it.

The JSON contract declares negative controls for tampering, extra/missing files, modes, escaping symlinks, hardlinks, nonapproved exclusions, Unicode collisions, FortyTwo drift, unrecorded derivations, source drift, unresolved dependency closure and pre-existing destinations. **These are future test requirements, not claimed executed tests.**

## Current disposition

**FAIL-CLOSED REVIEW.** Complete host inventory: **NOT CAPTURED**. Actual runtime dependency closure: **UNRESOLVED**. Implementation of materializer and independent verifier: **NOT IMPLEMENTED**. Workspace copied/verified: **NO**. Nominal runtime, internal NOOP, COSMOS, fault campaign, new observations, final environment acceptance, and PR #215 merge remain **NOT AUTHORIZED**.

**Next legitimate step:** a separately scoped author-approved *read-only host inventory discovery* of both preserved build candidates and the pinned FortyTwo tree, after the design review's exact-head CI passes. That would inventory/read only and cannot authorize copying or runtime.
