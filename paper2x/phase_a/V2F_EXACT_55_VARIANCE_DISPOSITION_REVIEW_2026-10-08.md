# P2X v2f — exact 55 observed variances: conditional runtime workspace disposition proposal

**Authority:** exact PR #215 head `276330544700661f756c58e02cf8b3a86b493d40`, workflow **#1426 SUCCESS**. **Scope:** static review and prospective, **not-approved** exclusion design only. No file changes, workspace copies, additional inventory, runtime, faults or scientific observations.

## Source-evidence boundary

The sole author's uploaded ZIP contains `v2f_full_source_inventory.jsonl` SHA-256 `edeba9101e56000a4ca1eb12f67105a05865627c5d39416db521991b6bf50e38` and diagnostics SHA-256 `f770806e11e3a452a37c8b6e4a8ca6fa0d35e0daa688d6237a58a286af043f88`. Its derivative 55-row CSV SHA-256 is `abc92c738d2d58adef7174ca8bd313b79ab9d8294c2421a74c633785c20d745c`. Exactly 20,034/20,089 primary/repeat regular-file SHA-256s match; **55 differ** (51 nested Git indexes and four CMake configuration logs). The nine reproducible raw build outputs remain matched, but the full source trees are **not** byte-identical and future runtime closure is **UNRESOLVED**. The exact 55 relative path identities appear in the companion JSON; their ordered newline-path digest is `216fa6147bc4a32c0aee8eda5f882cf11d6df3839447ba32c785c2e9c6c3dc80`. Individual primary/repeat SHA values remain in the original evidence and accompanying CSV, not remeasured here.

## Class 1 — 51 exact Git index files

These are `.git/index` or `.git/modules/**/index` (nested submodule checkout bookkeeping). They are **candidates for conditional omission from a minimal run-scoped runtime workspace**, not candidates for deletion from source evidence. The legacy nominal wrapper/preflight executes Git revision/status checks against `external/nos3` and pinned submodules; therefore do not infer that Git metadata can be omitted while invoking that legacy wrapper unchanged.

**Minimum acceptance conditions:** prove that provenance/revision/submodule checks are already independently satisfied against the immutable qualified source; identify any future workspace tool/launcher that invokes `git`; prove none requires these index files at runtime; separately classify *all other* Git metadata and `.git` gitdir links (no blanket exclusion); then authorize any exact omission in a separately validated materialization manifest. If a Git consumer exists, **retain or HOLD**, rather than excluding.

## Class 2 — 4 exact `CMakeConfigureLog.yaml` files

The observed paths are:

- `fsw/build/CMakeFiles/CMakeConfigureLog.yaml`
- `fsw/build/amd64-nos3/default_cpu1/CMakeFiles/CMakeConfigureLog.yaml`
- `gsw/build/CMakeFiles/CMakeConfigureLog.yaml`
- `sims/build/CMakeFiles/CMakeConfigureLog.yaml`

These are CMake configure-session diagnostic files, **candidate runtime-copy omissions** only after source-level analysis proves no launch-time tool consumes them. Their bytes remain preserved in both original offline-build candidates for reproducibility and build forensics. Do **not** generalize to all `CMakeFiles` or `.yaml` files: generated runtime inputs, cFS libraries, configuration tables and dependency-bearing metadata must be inventoried and proven separately. An unobserved consumer triggers **HOLD**, not automatic exclusion.

## Complete inclusion/exclusion boundary (not decided)

The proposal covers **exactly the 55 observed hash-different paths**; it is not a complete runtime materialization list. No policy has been granted for other `.git` entries, unchanged build outputs, NOS3 simulator libraries/configuration, cFS image/tables, FortyTwo resources, symlinks, derived InOut inputs or OCI-image libraries. Future approval requires a complete dependency graph and independent source-to-workspace verifier, with exact path inventory, owner/rationale for each omission, explicit 42 binary pin and source immutability. The nine qualified artifacts remain included and hashed without modification.

**Decision:** `STATIC_CONDITIONAL_PROPOSAL__EXCLUSIONS_NOT_AUTHORIZED`. No exclusion has been applied, no historical exclusion list adopted, no runtime dependency closure claimed. Runtime/workspace creation/NOOP/COSMOS/faults/science/final environment acceptance/merge remain **DENIED**.
