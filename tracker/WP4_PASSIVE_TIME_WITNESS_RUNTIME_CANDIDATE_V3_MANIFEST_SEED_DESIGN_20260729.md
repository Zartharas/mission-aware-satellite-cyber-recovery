# WP4 Passive Time-Witness Runtime-Candidate v3 Manifest-Seed Design (D-063R1)

Governance date: 2026-07-29

Decision: D-063R1

Disposition: `DESIGN_LOCKED_IMPLEMENTATION_NOT_AUTHORIZED`

Architecture identifier: `PINNED_IMAGE_BASE_PLUS_CANONICAL_MANIFEST_BOUND_PRIVATE_HOST_WORKSPACES`

Contract version after this lock: `0.4.10`

Contract status after this lock: `PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_LOCKED_IMPLEMENTATION_PENDING`

## Scope

This phase records the design and governance lock for a future versioned passive time-witness runtime candidate only. It does not implement, authorize, or execute anything. It creates no v3 generator, candidate, verifier, materializer, or runtime-material manifest. It does not modify any existing generator or verifier.

## Prohibitions

- Do not modify any existing generator or verifier.
- Do not create the v3 generator, candidate, verifier, materializer, or runtime-material manifest.
- Do not invoke Docker.
- Do not execute any generator for emission.
- Do not execute any candidate or verifier.
- Do not compile anything.
- Do not launch NOS3, NOS Engine, TimeDriver, simulators, bridge, cFS, 42, witnesses, or diagnostics.
- Do not transmit commands or inject events.
- Do not modify external/nos3 or retained evidence.
- Do not authorize runtime, baselines, D-064, scientific outcomes, command transmission, event injection, CryptoLib, or SDLS semantics.
- Do not stage, commit, push, merge, or create a PR.

## Evidence basis

This design is based on three read-only remediation-analysis supplements completed on the branch `wp4-v2-nos3-readonly-remediation-analysis`:

- Supplement 1 corrected the mount counts (6 textual `$NOS3 -> /work/nos3` directives; 14 hardware simulators; 18 runtime NOS3 mount instances) and identified 16 shared `SimConfig`/log-config loaders. Sixteen loaders resolve the same relative log configuration and writable path under the historical shared mount, creating a cross-container writable-path collision risk. The number of processes that actually open or write the file remains UNPROVEN. Per-container output isolation is required.
- Supplement 2 established runtime-material provenance: only 3 of the required host binaries are bound by `nominal-build-lock.txt`; `libsim_common.so`, all sim plugins, and several configs are gitignored (`build` rule) and unbound; image-owned libraries (`libitc_logger.so`, `libnos_engine_*.so`, `/usr/bin/nos_engine_server_standalone`) are absent from the host tree and are bound only by the pinned image digest.
- Supplement 3 established the canonical host-seed closure: image-owned files remain in the image and are never copied into the host seed; the host seed is a manifest-bound conservative runtime superset with per-file SHA-256; stale runtime state (including ItcLogger rollover archives and cFS key files) is `MUST_BE_ABSENT_AT_START` by source evidence. A canonical manifest containing normalized paths, entry types, modes, regular-file sizes and SHA-256 values, directory entries, explicit exclusions, and deterministic serialization—bound by the SHA-256 of the canonical manifest—is sufficient to bind the host seed. Coarse, implementation-dependent, or noncanonical directory hashes are not accepted as substitutes.

## Frozen historical identities

- Main starting commit: `88cceeb1fa3abfca86f1592c8eb79691788319b9`
- NOS3 HEAD: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- Pinned image: `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`
- Historical v2 generator SHA-256: `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- Historical rejected v2 candidate SHA-256: `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`
- Historical D-063 verifier SHA-256: `879dcac237717e84043cac5cdcd89c8c546f568c48e4ec7c897dc5c15cfbf87f`
- Historical D-063 retained log SHA-256: `753bcc17a6b3cda9686f76b7120edc588da6b22cdc28757d8af942aba6fab87f`
- Historical D-060 accepted entrypoint: `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`

These historical identities remain unchanged by this design. Historical v2 files remain immutable.

## Corrected raw and included counts

Pre-write audit of the three host source roots:

- Simulator seed roots (`external/nos3/sims/build/bin` + `external/nos3/sims/build/lib`): 27 raw regular files; 25 included after 2 excluded.
- cFS seed root (`external/nos3/fsw/build/exe/cpu1`): 1370 raw regular files; 1365 included after 5 excluded.
- Configuration root (`external/nos3/cfg/build/InOut`): 36 raw regular files; 36 included.

Provisional sanitized included counts:

- included_simulator=25
- included_cfs=1365
- included_config=36

## Distinct plugin mapping summary

Parsed from `external/nos3/sims/build/bin/nos3-simulator.xml`:

- 14 hardware simulator instances.
- reactionwheel0, reactionwheel1, and reactionwheel2 share one plugin (`libgeneric_rw_sim.so`).
- 12 distinct hardware plugin files.
- TimeDriver plugin: `libnos_time_driver.so`.
- 13 distinct simulator plugin files including TimeDriver.

## Exact architecture

`PINNED_IMAGE_BASE_PLUS_CANONICAL_MANIFEST_BOUND_PRIVATE_HOST_WORKSPACES`:

- The exact pinned image remains the immutable execution base.
- Image-owned files remain in the image; no `/usr/bin` or `/usr/lib` image file is copied into the host seed.
- The image digest transitively binds its manifest, configuration, and layer identities.
- File-level image inventory is not required because image-owned files are never extracted into the host seed.
- Only host-provided `external/nos3` runtime material is represented by the canonical per-file seed manifest.
- Each component receives a private run-scoped writable workspace populated only from manifest-approved host files.
- No runtime write reaches `external/nos3`.
- No stale state is copied.
- No two components share a writable log file.

## Source-inventory closure

A future canonical manifest must classify every source-root entry. Every source entry must be included or excluded; unknown entries fail closed. Open classifications:

- included regular files: `source_root`, `relative_path`, `destination-relative path`, `component scope`, `entry type`, `mode`, `size`, `SHA-256`, `provenance`, `mutable-state classification`, `include decision`, `justification`.
- directories: normalized relative path, mode, component scope.
- excluded paths: exact path or narrowly bounded pattern; exclusion classification; reason; `MUST_BE_ABSENT_AT_WORKSPACE_START=true`.

Confirmed exclusions:

- Simulator `bin/`: `2026-07-25-nos3-sim-log.txt`, `2026-07-26-nos3-sim-log.txt` (prior-run ItcLogger rollover archives).
- cFS `cpu1/`: `log.txt`, `sa_save_file.bin`, `.cdskeyfile`, `.reservedkeyfile`, `.resetkeyfile` (prior-run cFE runtime state; `MUST_BE_ABSENT_AT_START`).

Audit results: 0 symlinks; 0 absolute/escaping symlinks; 0 sockets/FIFOs/devices; 0 unsupported filesystem objects; 0 hard-link aliases; 0 unclassified source paths.

## Canonical manifest model

Locked canonicalization rules:

- UTF-8 JSON; POSIX forward-slash paths; bytewise sorted normalized relative paths; deterministic object-key ordering.
- No absolute paths; no `..` traversal; no duplicate paths; no unsupported object types; no hard-link aliases.
- Modes included; regular-file sizes and SHA-256 included.
- Timestamps, UID, and GID are normalized and not identity-bearing.
- Exactly one final newline.
- SHA-256 of the canonical manifest binds the complete host-seed definition.

A future verifier must compare the complete source inventory to the manifest: all source paths classified; every included file hash exact; no unclassified extras; excluded mutable files never copied. A canonical manifest containing normalized paths, entry types, modes, regular-file sizes and SHA-256 values, directory entries, explicit exclusions, and deterministic serialization—bound by the SHA-256 of the canonical manifest—is sufficient to bind the host seed. Coarse, implementation-dependent, or noncanonical directory hashes are not accepted as substitutes.

## Private-copy materialization

Locked private-copy model (not an overlay):

- Materialization begins only after cleanup traps exist.
- The candidate creates a run-scoped workspace root.
- It copies only manifest-approved files; it never copies the full source tree and then deletes stale files.
- It never creates hard links, reflinks, or aliases back to `external/nos3`.
- It preserves manifest-approved executable modes.
- It validates the completed workspace against the manifest; unlisted destination files fail closed; excluded files in a destination fail closed.
- `external/nos3` is never mounted into a runtime container.

## Eighteen-workspace mapping

Exactly 18 private NOS3 workspaces, each mounted at `/work/nos3` from a different run-scoped private host workspace (never `external/nos3`):

- NOS Engine: 1
- TimeDriver: 1
- hardware simulators: 14
- command-bus bridge: 1
- cFS: 1
- total: 18

For the 17 simulator-family components (NOS Engine, TimeDriver, 14 hardware simulators, bridge), each materializes a private sanitized simulator workspace containing the canonical included simulator seed. Relative paths and existing commands remain unchanged. Each `SimConfig` loader resolves `sim_log_config.xml` privately; each `nos3-sim-log.txt` resolves inside a unique private workspace; no cross-container writable log-file alias exists; NOS Engine unknown cwd writes remain private; no logger-configuration rewrite is required solely for isolation. Historical rollover logs must be absent at workspace start.

## cFS workspace

One private sanitized cFS workspace. The following must be absent at workspace start: `log.txt`, `sa_save_file.bin`, `.cdskeyfile`, `.reservedkeyfile`, `.resetkeyfile`, `core`, `core.*`, `*.pid`, `*.lock`, Python cache files. They may be created only inside the private run-scoped workspace where runtime behavior permits; their creation is neither claimed nor required by this design except where source evidence later establishes it.

## Configuration templates

The complete sanitized configuration-template root is bound by manifest. `Inp_Sim.txt` is preserved as a template subject to the existing deterministic headless rewrite; `Inp_IPC.txt` is preserved as the existing bound template. The current 42 InOut scratch handling remains separate from the 18 private NOS3 workspaces and may not alias `external/nos3`.

## Image boundary

- The exact pinned image remains the immutable execution base.
- Image-owned files remain in the image; no `/usr/bin` or `/usr/lib` image file is copied into the host seed.
- The image digest transitively binds its manifest, configuration, and layer identities.
- File-level image inventory is not required for this design because image-owned files are never extracted into the host seed.

## Cleanup

- Every workspace and output path is run-scoped.
- Cleanup remains reverse-order, bounded, and fail-closed.
- Only current-run paths may be removed.
- No prune operation is allowed.
- Cleanup failure overrides success.
- Nothing survives between attempts.
- The design does not authorize an attempt.

## Future implementation requirements

Historical v2 files remain immutable. Future implementation must create a new versioned generator, a new deterministic candidate, a canonical runtime-material manifest, and a new versioned static verifier. No filenames or hashes for those implementation artifacts are accepted in this design phase except provisional future paths documented as such by the implementation phase. No implementation scripts are created in this phase.

`implementation_status=NOT_STARTED`; `static_verification=PENDING`; `runtime_authorized=false`; authorized attempts `0`; `D-064=BLOCKED`; `next decision=SEPARATELY_GOVERNED_V3_IMPLEMENTATION_REQUIRED_BEFORE_D064`.

## Future verifier requirements

The future verifier must fail closed unless it proves:

- exact new generator and candidate hashes;
- exact canonical manifest hash;
- complete source inventory classification;
- exact hashes for all included files;
- no unclassified source paths;
- no excluded file copied;
- no unsupported objects or hard-link aliases;
- exactly 18 private runtime workspaces;
- 14 hardware simulator instances;
- 12 distinct hardware plugin files;
- 13 distinct simulator plugin files including TimeDriver;
- no mount source resolves to `external/nos3`;
- every `/work/nos3` mount source is unique and run-scoped;
- no two writable component paths alias the same host file;
- workspace files exactly match manifest-approved entries before launch;
- historical D-060, D-062, and D-063 identities remain unchanged;
- runtime authorization remains false;
- authorized attempts remain zero.

## Governance sequence

1. Remediation design lock — D-063R1 (this phase).
2. Separately governed versioned implementation (new generator, candidate, manifest, verifier).
3. Separate versioned static verification.
4. Governance disposition.
5. Only afterward may D-064 be considered.

No D-064 authorization is granted. No remediation decision identifier is invented beyond D-063R1.

## Explicit statements

- Runtime compatibility remains `UNPROVEN`. The design requires every runtime write to be contained within a private run-scoped workspace. Implementation correctness, runtime containment, and runtime compatibility remain UNPROVEN until a separately governed implementation and static verification are completed.
- No runtime is authorized by this design.
