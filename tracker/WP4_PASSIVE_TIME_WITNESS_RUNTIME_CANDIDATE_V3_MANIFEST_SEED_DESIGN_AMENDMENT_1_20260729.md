# WP4 Passive Time-Witness Runtime-Candidate v3 Manifest-Seed Design Amendment 1

Decision: D-063R2
Governance date: 2026-07-29
Amendment status: DESIGN_AMENDMENT_LOCKED_IMPLEMENTATION_NOT_AUTHORIZED

## Scope

This amendment is a governance-only correction to the locked D-063R1 v3 manifest-seed design. It does not implement, authorize, or execute any manifest, materializer, generator, candidate, verifier, workspace, runtime, command, or event. It does not create any implementation artifact.

## Immutable historical D-063R1 references

D-063R1 remains the historical design baseline. Its provisional counts were correct for the audit classification then applied.

- Historical design record: `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_20260729.md`
- Historical design record SHA-256: `c089ffacac68694de2d446acbd301d0a96bc270fa9d1042e7e4c2c6f5bdf2f14`
- Historical design lock: `artifacts/wp4-passive-time-witness-runtime-candidate-v3-manifest-seed-design-lock.txt`
- Historical design lock SHA-256: `cebd5933d2bea7246f2a4d14d0f1efacafcb4f20afa5b901ba505a9c2512263d`

D-063R2 supersedes only the effective inventory counts, exact-exclusion model, byte calculations, identity controls, canonicalization details, and phase-governance sequencing identified below. D-063R2 does not erase, rewrite, or invalidate the D-063R1 record. Both historical D-063R1 hashes remain preserved and immutable. The historical D-063R1 record and lock files are not modified by this amendment.

## Reason for amendment

Independent review of the D-063R1 design and four read-only implementation-planning analyses identified material defects: the cFS source-root included-file count and exclusion model were incorrect, four `.goutputstream-*` stale temporary files were not individually classified, byte and footprint calculations contained internal contradictions, the canonical-manifest ordering and collision model lacked byte-exact specification, the identity-control model was incomplete, and the implementation/static-verification boundary and contract-schema compatibility model were not fully locked. This amendment corrects those defects without expanding scope beyond governance.

## Corrected inventory

Source-root counts:

| Source root | Raw regular files | Included regular files | Exact exclusions | Included bytes |
|---|---|---|---|---|
| Simulator (`sims/build/bin` + `sims/build/lib`) | 27 | 25 | 2 | 54427517 |
| cFS (`fsw/build/exe/cpu1`) | 1370 | 1361 | 9 | 45877946 |
| Configuration (`cfg/build/InOut`) | 36 | 36 | 0 | 190651 |

Aggregate:

- Raw regular files: 1433
- Included regular-file manifest entries: 1422
- Manifest directory entries: 89
- Exact exclusion entries: 11
- Unsupported filesystem objects: 0
- Escaping symlinks: 0
- Hard-link aliases: 0
- Unclassified source paths: 0

Corrected byte calculations:

- Seventeen simulator-family workspace bytes: 925267789
- One cFS workspace bytes: 45877946
- Eighteen private-workspace bytes: 971145735
- Separate Fortytwo configuration scratch bytes: 190651
- Optional canonical staging-seed bytes: 100496114
- Prelaunch bytes without staging seed: 971336386
- Prelaunch bytes with staging seed: 1071832500
- Recommended free-space bytes: 3215497500
- Recommended formula: `3 * max(prelaunch_without_staging, prelaunch_with_staging)`

Fortytwo scratch bytes are not included inside private-workspace bytes. Logical file counts are distinct from expanded copy counts.

### Inventory snapshot versus invariant semantics

The above counts are the 2026-07-29 amendment snapshot. Raw regular-file counts are amendment-time snapshot values; they are not unconditional future gates. Included-entry counts, the included byte count, and the exact-exclusion-record count are future invariants.

| Property | Snapshot value (2026-07-29) | Invariant? |
|---|---|---|
| Simulator included regular files | 25 | yes |
| Simulator present exact exclusions | 2 | no (may range 0-2) |
| Simulator raw regular files | 27 | no (snapshot only) |
| Simulator included bytes | 54427517 | yes (while identities unchanged) |
| cFS included regular files | 1361 | yes |
| cFS present exact exclusions | 9 | no (may range 0-9) |
| cFS raw regular files | 1370 | no (snapshot only) |
| cFS included bytes | 45877946 | yes (while identities unchanged) |
| Configuration included regular files | 36 | yes |
| Configuration present exact exclusions | 0 | yes (fixed at 0; no configuration exclusion records) |
| Configuration raw regular files | 36 | yes (= included, no exclusions) |
| Aggregate included regular files | 1422 | yes |
| Aggregate present exact exclusions | 11 | no (may range 0-11) |
| Aggregate raw regular files | 1433 | no (snapshot only) |
| Aggregate included bytes | 100496114 | yes (while identities unchanged) |

Future invariant semantics:

- Included manifest regular-file entry count = 1422
- Exact exclusion-record count = 11
- Simulator included count = 25
- cFS included count = 1361
- Configuration included count = 36
- Included bytes = 100496114 while included identities are unchanged
- Present simulator exclusion count may range from 0 to 2
- Present cFS exclusion count may range from 0 to 9
- Aggregate present exclusion count may range from 0 to 11
- Future simulator raw count = 25 + present simulator exclusions
- Future cFS raw count = 1361 + present cFS exclusions
- Future configuration raw count = 36
- Future aggregate raw count = 1422 + present exact exclusions
- Raw count 1433 is an amendment-time snapshot, not an unconditional future gate
- Absence of an exact excluded source path is not drift
- A present exact exclusion must still match its complete frozen identity
- An unlisted path still fails closed
- Every exclusion remains absent from every materialized destination

## Exact exclusions

### Complete eleven-row exclusion identity table

| # | source_root | relative_path | entry_type | mode | size | SHA-256 | nlink | present_at_amendment | classification | destination_must_be_absent |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | sim_bin | `2026-07-25-nos3-sim-log.txt` | regular_file | 0644 | 27655970 | `c63a6cd22b8c830608286cc0606ce89e14ce139c19438ef51ef0d8a31556230b` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 2 | sim_bin | `2026-07-26-nos3-sim-log.txt` | regular_file | 0644 | 12906883 | `39be49486820383a0c3319203428d812a16e361d404e88951bd12f01203ed9a1` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 3 | cfs | `log.txt` | regular_file | 0644 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 4 | cfs | `sa_save_file.bin` | regular_file | 0644 | 150272 | `5ed0c75dd2ac88af0b6311d7466c8101781dd59dab4c5a3e3c040feb392c14d2` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 5 | cfs | `.cdskeyfile` | regular_file | 0700 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 6 | cfs | `.reservedkeyfile` | regular_file | 0700 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 7 | cfs | `.resetkeyfile` | regular_file | 0700 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 8 | cfs | `data/owls/bundle/.goutputstream-3YXHA2` | regular_file | 0644 | 1369700 | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 9 | cfs | `data/owls/bundle/.goutputstream-2Z2791` | regular_file | 0644 | 1369700 | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 10 | cfs | `data/owls/bundle/.goutputstream-M5TDA2` | regular_file | 0644 | 810786 | `81fdd618434da04b838701bc08ffe7d614c8ee60a9a4d27f4108ee4541c0bddd` | 1 | true | EXACT_STALE_EXCLUSION | true |
| 11 | cfs | `data/owls/bundle/.goutputstream-PDW691` | regular_file | 0644 | 148 | `4b037466e2da3de4e1b9b94b94463c06d4caa38bd2ef36a44cc00da140756540` | 1 | true | EXACT_STALE_EXCLUSION | true |

### Four .goutputstream duplicate-target fields

| relative_path | SHA-256 | duplicate_target | duplicate_target_sha256 | bytes_equal |
|---|---|---|---|---|
| `data/owls/bundle/.goutputstream-3YXHA2` | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | `data/owls/bundle/asdp000000000.tgz` | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | true |
| `data/owls/bundle/.goutputstream-2Z2791` | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | `data/owls/bundle/asdp000000000.tgz` | `f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb` | true |
| `data/owls/bundle/.goutputstream-M5TDA2` | `81fdd618434da04b838701bc08ffe7d614c8ee60a9a4d27f4108ee4541c0bddd` | `data/owls/bundle/asdp000000001.tgz` | `81fdd618434da04b838701bc08ffe7d614c8ee60a9a4d27f4108ee4541c0bddd` | true |
| `data/owls/bundle/.goutputstream-PDW691` | `4b037466e2da3de4e1b9b94b94463c06d4caa38bd2ef36a44cc00da140756540` | `data/owls/bundle/asdp000000002_dpmsg.json` | `4b037466e2da3de4e1b9b94b94463c06d4caa38bd2ef36a44cc00da140756540` | true |

Evidence wording for all four `.goutputstream-*` exclusions: "The name is consistent with a temporary GIO output file. Classification as an exact stale exclusion is based on exact byte duplication, no repository references, hidden temporary-style naming, and the presence of the intended duplicate file." A specific GUI event is not claimed as proven.

### Deny guard

A narrow deny guard is added for `data/owls/bundle/.goutputstream-*`. The deny guard supplements exact classification and does not replace it. Any newly appearing deny-pattern match fails unless separately and exactly classified.

## Exclusion-presence policy

- An exact excluded source path may be absent.
- Its absence does not constitute source drift.
- When present, its type, mode, size, and SHA-256 must match the exact exclusion record.
- A present mismatch fails closed.
- Any unlisted source path fails closed.
- Any newly appearing deny-pattern match fails closed unless it has an exact classification.
- Every exact exclusion and deny-pattern match must be absent from all materialized destination workspaces.

This policy applies to all eleven exact exclusions, including the four `.goutputstream-*` paths. Source-exclusion semantics (a path may be absent from source) are distinct from destination-exclusion semantics (an excluded path must be absent from every destination workspace).

## SimConfig and workspace model

| Component | SimConfig loaders | Source evidence |
|---|---|---|
| TimeDriver | 1 | `external/nos3/sims/nos_time_driver/src/nos_time_driver.cpp` line 31: `Nos3::SimConfig sc(argc, argv);` |
| Hardware simulators | 14 | `external/nos3/sims/sim_common/src/single_simulator.cpp` line 31: `Nos3::SimConfig sc(argc, argv);` |
| Command-bus bridge | 1 | `external/nos3/sims/sim_common/src/sim_cmdbus_bridge.cpp` line 117: `sim_cfg = new Nos3::SimConfig(argc, argv);` |
| NOS Engine | UNPROVEN | Image-owned executable; no source-level SimConfig evidence found |
| cFS | separate | Uses separate runtime-state paths |

Confirmed total SimConfig loaders: 16. `NOS_ENGINE_SIMCONFIG_STATUS=UNPROVEN`. `NOS_ENGINE_HOST_CONFIG_SIM_LOG_REFERENCE=NOT_FOUND`. This does not state that the image-owned NOS Engine executable definitively does not construct or use equivalent logging behavior.

Eighteen-workspace requirement:

- NOS Engine: 1
- TimeDriver: 1
- Hardware simulators: 14
- Command-bus bridge: 1
- cFS: 1
- Total: 18

Every workspace remains a private physical copy with no hard links, reflinks, overlays, source aliases, or runtime mount sourced from `external/nos3`. The 42 InOut scratch material remains separate from the eighteen NOS3 workspaces.

## Canonical manifest model

- The canonical manifest contains no internal manifest SHA-256.
- A detached SHA-256 is computed over the complete canonical file bytes.
- `ensure_ascii=True`; `sort_keys=True`; `separators=(",", ":")`; exactly one final LF.
- Exact UTF-8 bytes remain path identity.

### Byte-exact sort keys

Every sort-key element is encoded as bytes.

Included-entry sort key: `(source_root UTF-8 bytes, relative_path UTF-8 bytes, entry_type ASCII bytes, destination_relative UTF-8 bytes, component_scope UTF-8 bytes)`

Excluded-entry sort key: `(source_root UTF-8 bytes, relative_path UTF-8 bytes, exclusion_classification ASCII bytes)`

Directory-entry sort key: `(source_root UTF-8 bytes, relative_path UTF-8 bytes, component_scope UTF-8 bytes)`

Deny-pattern sort key: `(pattern UTF-8 bytes, scope UTF-8 bytes)`

Workspace-declaration sort key: `(component_id UTF-8 bytes, workspace_host_path UTF-8 bytes, mount_destination UTF-8 bytes)`

### Path validation

- Reject surrogate code points before UTF-8 encoding.
- Reject NUL.
- Reject absolute paths.
- Reject empty, ".", and ".." components.
- Reject backslashes.
- Reject repeated separators.
- Reject duplicate source identities.
- Reject duplicate destination identities within a component.
- Reject directory/file and prefix collisions.

### Collision model

1. NFD-decompose the validated path.
2. Apply `str.casefold()` (not `str.lower()`).
3. Normalize the folded value independently to NFC and NFD.
4. Encode both values as UTF-8.
5. Reject distinct exact paths if either normalized collision key matches.

Normalized values are collision guards only. Exact UTF-8 bytes remain the identity. Lowercasing is distinct from Unicode case folding.

### Source versus destination exclusion semantics

- Excluded paths may exist in source; their identity must match the exclusion record when present; their absence is not source drift.
- Excluded paths must be absent from every materialized destination workspace.
- Deny patterns are additional fail-closed guards; they do not replace exact classification.
- Any unlisted source path fails closed.

## Eleven logical candidate dependencies

1. Contract JSON (governance)
2. Canonical manifest (runtime)
3. Runtime-material tool (runtime)
4. Witness source (runtime)
5. Trace validator (runtime)
6. Socket-shim source (runtime)
7. Baseline contract (governance)
8. NOS3 runtime material (runtime)
9. Fortytwo executable (runtime)
10. Fortytwo configuration templates (runtime)
11. Pinned OCI image (runtime)

Logical candidate dependency count: 11. Host-or-governance dependency count: 10. OCI image dependency count: 1.

## Fourteen implementation/runtime identity controls

1. Contract schema/revision control
2. Generator SHA-256
3. Proposed candidate SHA-256
4. Runtime-material tool SHA-256
5. Canonical manifest SHA-256
6. Verifier SHA-256
7. Witness-source SHA-256
8. Trace-validator SHA-256
9. Socket-shim-source SHA-256
10. Baseline-contract SHA-256
11. NOS3 commit
12. Fortytwo commit
13. Fortytwo executable SHA-256
14. Pinned OCI-image digest

Baseline-contract SHA-256 (`configs/benign-baseline-contract.json`): `86d365fe08d7ee177e74192cead71dc366e9c546e81668261c770350003e37ca`

Fortytwo executable SHA-256 (`external/fortytwo/42`): `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7`

Identity controls are distinct from logical dependencies and from semantic/runtime compatibility status.

## Seven governance-artifact identity categories

1. Future amendment-record SHA-256 (this record)
2. Future amendment-lock SHA-256 (this lock)
3. Future implementation-record SHA-256
4. Future implementation-lock SHA-256
5. Later disposition-record SHA-256
6. Later retained-log SHA-256
7. Later static-gate-lock SHA-256

Governance-artifact identity count: 7.

## Contract-schema compatibility

A future candidate verifies contract compatibility through a stable schema field `passive_time_witness_runtime_candidate_v3_contract_schema=1`, not from the mutable governance revision string alone. The candidate must require the supported schema identifier, all mandatory v3 gate fields, an accepted candidate identity matching its own complete-file SHA-256, explicit runtime authorization, and exactly one authorized attempt when later governed. The candidate must not trust a narrative status string alone and must not fail solely because the governance revision advances from 0.4.12 to 0.4.13.

## Proposed and accepted candidate identity distinction

- `proposed_runtime_entrypoint_v3_sha256`: populated by implementation governance; records the implementation identity only.
- `accepted_runtime_entrypoint_v3_sha256`: empty until a separately governed static verification passes.

A candidate must not authorize itself from the proposed identity. The accepted identity is the only authority-equivalent field and remains empty until the later static-verification phase passes.

## Host-side materialization and authorization ordering

- Contract authorization checks occur before workspace-root creation, materialization, copying, fake Docker, or real Docker.
- The runtime-material tool executes on the host.
- Source verification and materialization occur on the host.
- The tool is never invoked inside a runtime container.
- Under the current closed contract, candidate negative testing exits before materializer execution and before fake-Docker invocation.
- Static verification invokes no real Docker.

## Non-circular identity DAG

- The generator hash and candidate hash are separate.
- The candidate must not embed the verifier hash.
- The verifier may depend on and verify the candidate.
- The candidate must not use the generator hash as its own file hash.
- No impossible literal full-file self-hash is used.
- A future candidate checks its own accepted identity from contract state (the `accepted_runtime_entrypoint_v3_sha256` field), not by hashing itself and embedding the result.
- The manifest detached SHA-256 is read from the contract; the manifest contains no internal self-hash field.

The DAG is acyclic: contract -> {manifest, tool, generator, verifier}; generator -> candidate; verifier -> {candidate, manifest, tool, contract}; candidate -> {contract, manifest, tool}; no candidate -> verifier edge; no candidate -> generator edge; no self-referential edges.

## Combined implementation model

Manifest/materializer, generator/candidate, and static-verifier implementation are checkpoints within one governed implementation phase. Internal stop gates separate the three checkpoints. The combined implementation package modifies the contract to 0.4.12. One implementation record and one implementation lock are produced.

During the combined implementation phase, permitted validation includes runtime-material tool synthetic self-tests, canonical manifest generation and deterministic byte checks, source-inventory verification, generator bash syntax, deterministic double candidate emission, candidate bash syntax, a direct candidate closed-gate negative test that exits before workspace creation, materialization, fake Docker, or real Docker, and verifier bash syntax and read-only source review. Complete v3 verifier execution, a v3 static-gate PASS or FAIL result, a retained static-verification log, accepted candidate identity, and real Docker are not permitted during implementation.

At implementation completion: verifier implemented but unexecuted; v3 static verification=PENDING; proposed candidate hash recorded; accepted candidate hash empty; runtime authorization=false; attempts=0; D-064=BLOCKED. The later static-verification phase performs the first complete verifier execution and creates its retained raw log and governed disposition.

## Post-static-PASS D-064 boundary

The current D-064 state remains BLOCKED. The rules below describe only a future permitted transition after a governed static verification PASS.

- A static PASS may set `d064_status=READY_FOR_SEPARATE_D064_CONSIDERATION`.
- A static PASS does not authorize D-064: `static_pass_does_not_authorize_d064=true`.
- A static PASS does not authorize runtime: `static_pass_does_not_authorize_runtime=true`.
- A static PASS does not authorize attempts: `static_pass_does_not_authorize_attempts=true`.
- A static FAIL keeps D-064 BLOCKED.
- A static PASS does not itself constitute decision D-064: `static_pass_does_not_constitute_decision_d064=true`.
- A static PASS does not authorize Docker runtime execution.
- A static PASS does not authorize one attempt.
- A separate D-064 governance decision is explicitly required: `separate_d064_decision_required=true`.
- After a static PASS, runtime authorization remains false: `runtime_authorized_after_static_pass=false`.
- After a static PASS, attempts remain 0: `runtime_attempts_after_static_pass=0`.
- Only a later, explicit D-064 governance decision may authorize a bounded passive telemetry attempt.

## Contract revision sequence

- D-063R1 merged design: 0.4.10
- D-063R2 design amendment: 0.4.10 -> 0.4.11
- Combined v3 implementation: 0.4.11 -> 0.4.12
- Later v3 static-verification disposition: 0.4.12 -> 0.4.13

Each separately governed change receives a unique contract revision.

## Later file-set counts

- Design-amendment package (this phase): 7 files
- Combined implementation package (future): 11 files
- Static-verification disposition package (later): 8 files

## Authorization state

All authorization fields are closed:

- Implementation authorization: false
- Static verification authorization: false
- Runtime authorization: false
- Runtime attempts: 0
- D-064: BLOCKED
- All top-level scientific, event-injection, command-transmission, baseline, and cryptographic-semantics permissions: false

No scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim is made. Implementation correctness, runtime containment, and runtime compatibility have not been proven. The current D-064 state remains BLOCKED; a future static PASS may set D-064 to READY_FOR_SEPARATE_D064_CONSIDERATION but does not authorize D-064, runtime, or attempts; a separate explicit D-064 governance decision is required.

## Amendment lock

This amendment record is locked by `artifacts/wp4-passive-time-witness-runtime-candidate-v3-manifest-seed-design-amendment-1-lock.txt`. The amendment-record SHA-256 and amendment-lock SHA-256 are recorded in the contract and trackers.

Next decision: `SEPARATELY_GOVERNED_COMBINED_V3_IMPLEMENTATION_REQUIRED_BEFORE_STATIC_VERIFICATION`
