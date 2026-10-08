# P2X Phase A — v2f deterministic Git-metadata proposal

**Status:** `V2F_DESIGN_AND_STATIC_VALIDATION_ONLY__NO_BUILD_AUTHORIZED`  
**Experiment:** `P2X-NOS3-RG-001`  
**Date:** 2026-10-05

## Evidence basis

The separately authorized v2e dual offline build produced a preserved strict HOLD at
`artifacts/runtime/p2xa-nos3-v2e-build-20261005T141959Z-7c8ceaa570`.
Eight of nine required artifacts were byte-identical. The sole mismatch remained
`fsw/build/exe/cpu1/core-cpu1`.

Read-only diagnosis established:

- machine-code `.text`, `.data`, debug sections, symbol table and string table were identical;
- repeat `.rela.dyn` contained one additional ELF64 relocation;
- generated `cfe_module_version_table.c` differed at exactly one semantic entry:
  primary `{ "onair", NULL }`; repeat `{ "onair", "git:v1_07_05" }`;
- primary and repeat `mission_vars.cache` were byte-identical and both recorded
  `onair_MISSION_DIR=/work/nos3/components/onair`;
- both preserved OnAIR submodules are clean at
  `aa5559c0f234eba263041b6007573f16870194e5` and describe as
  `v0.0.13-119-gaa5559c`;
- pinned-OCI replay showed that Git normally rejects the bind-mounted NOS3
  superproject as dubious ownership at `/work/nos3`; the actual
  `components/onair/fsw` submodule remains valid;
- one replay of the parent-path probe succeeded and returned `v1_07_05`, exactly
  matching the repeat build's generated cFE version string.

Pinned cFE `cmake/generate_git_module_version.cmake` performs
`git describe --tags --always --dirty` in each recorded dependency directory.
For the logical OnAIR dependency, the recorded directory is
`/work/nos3/components/onair`, so Git repository discovery walks upward to the
NOS3 superproject. Git's safe-directory decision therefore becomes an implicit
build input unless it is controlled explicitly.

## v2f hypothesis

Make repository trust an explicit, ephemeral container input before configuration
and ensure every build sees the same version-control metadata.

The candidate mechanism is **environment-scoped Git configuration**, inherited by
all child Git processes:

```text
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0=/work/nos3
```

This is preferred over editing `.git/config`, altering source ownership,
changing cFE/NOS3 source, or writing a persistent user-global configuration.
The container already uses `HOME=/tmp`; v2f must not rely on mutable persistent
host or container Git configuration.

## Required pre-build metadata gate

A future separately authorized v2f builder must fail before compilation unless,
inside each newly staged source tree and the pinned offline OCI:

1. `/work/nos3` is the exact container worktree;
2. the environment-scoped Git safe-directory configuration is present exactly once;
3. `git -C /work/nos3 rev-parse HEAD` equals
   `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`;
4. `git -C /work/nos3 describe --tags --always --dirty` returns exactly
   `v1_07_05`;
5. `git -C /work/nos3/components/onair describe --tags --always --dirty`
   returns exactly `v1_07_05`;
6. `git -C /work/nos3/components/onair/fsw rev-parse HEAD` equals
   `aa5559c0f234eba263041b6007573f16870194e5`;
7. `git -C /work/nos3/components/onair/fsw describe --tags --always --dirty`
   returns exactly `v0.0.13-119-gaa5559c`;
8. the complete dependency Git-descriptor map captured for the two staged trees is
   byte-identical before any compilation proceeds;
9. all four historical July lock hashes and both prior v2/v2e HOLD manifests remain
   unchanged.

A descriptor failure is a HOLD. No fallback to `NULL`, no retry-until-success,
and no binary normalization is allowed.

## Build controls retained unchanged

If v2f execution is separately authorized later, retain:

- pinned NOS3, LC, HWLIB, FortyTwo and OCI revisions/digests;
- `--network none`, `linux/amd64`, fixed `/work/nos3`;
- synthetic cFE labels `BUILDDATE=202610030000`,
  `HOSTNAME=p2x-v2e-builder`, `USER=p2x-builder`;
- the existing source/object-specific GCC `-frandom-seed` launcher;
- two independently staged clean source populations;
- original NOS3 build order;
- strict 9/9 raw SHA-256 and byte-size identity for all nine required artifacts;
- independent read-back;
- immutable original v2 and v2e HOLD evidence.

Success may be classified only as
`V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED`.
It is not final environment acceptance.

## Current authorization boundary

This record authorizes **design and static validation only**. It does not authorize:

- a v2f Docker/NOS3 full build;
- a v2e rerun;
- A1 nominal runtime;
- COSMOS;
- faults or F1/F2/G0/G1;
- manuscript scientific claim changes;
- final environment acceptance;
- merging PR #215.

A separate explicit author decision and tracked execution-gate update are required
before any v2f full build.
