# WP4 Nominal Baseline Protocol — Gate 3A/3B

## Status

This protocol governs the first benign NOS3/cFS baseline. It authorizes dependency resolution, network-disabled compilation, bounded headless launch, nominal command/telemetry verification, clean shutdown, and evidence capture. It does not authorize cyber-event injection.

## Purpose

The baseline must demonstrate that the selected testbed can be reproduced independently of the planned cyber scenarios. Testbed installation failures, timing instability, container drift, or telemetry defects must not be misclassified as cyber-response effects.

## Fixed environment

- Host: verified Intel `x86_64` macOS system
- Execution: Docker Desktop using `linux/amd64`
- NOS3 commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- NOS3 image: `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`
- cFE commit: `87e273743f3d07ed9216462b461e9f398ff96c87`
- OSAL commit: `08a79bb6ac02b9ced8aa555853ecdd96e5ebc1a7`
- PSP commit: `d0a5d6fa4093d473a929fde42a0983e489d89d4a`
- 42 source: `nasa-itc/42`, initially resolved from upstream reference `dev_20260403`, then frozen by exact commit

## Why the upstream `make prep` path is not used directly

The selected NOS3 revision's preparation script:

- Pulls a mutable image tag
- Clones 42 from a named branch rather than an exact commit
- Installs optional GUI Python packages on the host
- Starts the Igniter GUI

Those behaviors are appropriate for an interactive development setup but do not satisfy this study's reproducibility and minimal-host-change requirements. The project therefore resolves 42 once, records its exact commit, builds it with the pinned image, and performs the remaining compilation with network access disabled.

## Gate 3A — exact 42 resolution and build

Run:

```bash
bash scripts/prepare_42_candidate.sh
```

The script must:

1. Clone or reuse `external/fortytwo`.
2. Resolve `dev_20260403` only when no exact 42 lock exists.
3. Check out a detached exact commit.
4. Initialize any recursive submodules.
5. Require a clean worktree before compilation.
6. Compile using the pinned NOS3 image by digest.
7. Disable container networking during compilation.
8. Record the exact commit, image identity, executable checksum, and log location in `artifacts/fortytwo-lock.txt`.

Acceptance output:

```text
FORTYTWO_PREPARATION_STATUS=PASS
```

A later run must reuse the exact commit from the lock unless an explicit reviewed change is made.

## Gate 3A — deterministic NOS3/cFS build

Run:

```bash
bash scripts/build_nominal_nos3.sh
```

The script must verify:

- The committed NOS3 lock exists.
- The committed 42 lock exists.
- NOS3 is at the exact selected commit.
- The NOS3 worktree is clean.
- No recursive submodule has a leading `+` or `-` status.
- The local image matches the committed digest.
- Compilation occurs with Docker network mode `none`.

The build includes:

- NOS3 mission configuration
- cFS/cFE flight-software build
- NOS3 simulator build
- CryptoLib standalone support build

Required outputs include:

- `cfg/build/launch.sh`
- `fsw/build/exe/cpu1/core-cpu1`
- `sims/build/bin/nos3-single-simulator`
- `sims/build/bin/nos3-sim-cmdbus-bridge`
- `gsw/build/support/standalone`

The script records exact component commits and output checksums in `artifacts/nominal-build-lock.txt`.

Acceptance output:

```text
NOMINAL_BUILD_STATUS=PASS
```

## Gate 3B — bounded headless launch

Gate 3B begins only after both Gate 3A scripts pass and their lock files are reviewed.

The headless launch must use the selected NOS3 commit's CI-oriented launch path as a reference, but the research wrapper must add the following controls:

- Bounded maximum runtime
- Project-specific container labels
- Explicit container inventory before and after the run
- No host networking
- No external target addresses
- Clean shutdown even on failure or interruption
- Separate raw container logs for cFS, simulators, 42, ground software, and CryptoLib
- An append-only baseline manifest
- A run classification of `RUN_INVALID` for infrastructure failures

## Benign baseline checks

Each accepted baseline run must demonstrate:

1. cFS starts and remains running for the configured observation interval.
2. Required NOS3 simulator processes remain running.
3. 42 starts from the pinned executable and configuration.
4. The ground software receives nominal telemetry.
5. At least one predefined benign command is accepted and produces its expected state or counter change.
6. Telemetry continues after the benign command.
7. No safety/trust invariant is violated.
8. No container connects to an undeclared external network.
9. Shutdown removes project containers and networks without affecting unrelated Docker workloads.
10. Evidence files and checksums are complete.

## Two-run reproducibility requirement

The nominal baseline must pass twice from clean build/runtime state. The two runs must use:

- The same source and image locks
- The same mission configuration
- The same benign command sequence
- The same observation interval
- Separate run identifiers and evidence directories

The following may vary and must be recorded:

- Wall-clock timestamps
- Container IDs
- Host process IDs
- Non-deterministic startup timing within the allowed tolerance

The following must not vary without explanation:

- Source commits
- Image digest
- Required container set
- Command sequence
- Required telemetry fields
- Terminal classification

## Failure handling

A build or launch failure is not a cyber result. It is classified as infrastructure evidence and retained under ignored logs or runtime artifacts. The failure must be diagnosed and resolved before event injection is enabled.

## Gate 3B acceptance

Gate 3B passes only when two clean nominal runs satisfy all required checks and the evidence manifests are reviewed. Until then:

- WP4 remains in progress.
- WP5 event injection remains blocked.
- No attack or containment policy may be scored.
