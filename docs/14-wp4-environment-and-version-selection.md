# WP4 Environment and Version Selection

## Status

Candidate architecture baseline selected on 2026-07-24. Implementation remains limited to a software-only, researcher-owned environment.

## Verified local environment

The researcher reported and verified the following host environment:

- Host operating system: macOS 26.5.2, build 25F84
- Kernel architecture: `x86_64`
- Git: 2.54.0
- Python: 3.11.7
- Docker CLI: 29.6.2
- GitHub CLI: 2.96.0
- Available storage: approximately 2.5 TiB

This host is suitable for an `amd64` Linux container workflow. The study will not build or execute cFS/NOS3 components directly on macOS. Linux containers will provide the controlled execution environment.

## Selected execution strategy

### Primary path: Docker-first, headless NOS3

The primary path is a Docker-based, headless NOS3 deployment because:

1. The host is Intel `x86_64`, matching the NOS3 64-bit Linux container path without ARM emulation.
2. Docker is already installed.
3. Containers provide stronger reproducibility and reset controls than an unmanaged native build.
4. Headless execution avoids making X11, VirtualBox, or graphical display forwarding a scientific dependency.
5. Container networks can be declared `internal` and denied default outbound routing.

VirtualBox/Vagrant remains a fallback only if a required NOS3 function cannot be exercised in the container path.

## Candidate upstream pins

### NOS3

- Repository: `nasa/nos3`
- Candidate commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- Selection basis: exact main-branch commit observed during WP4 selection
- Candidate NOS3 build image: `ivvitc/nos3-64:20260619`
- Image digest: pending local pull and inspection

The exact commit is used instead of a moving branch. The final environment manifest must include all recursive submodule commits.

### cFS

The experiment will use the cFS revision pinned by the selected NOS3 commit. It will not silently replace that submodule with the newest cFS `main` revision.

For independent reference only:

- Official cFS bundle release: `v7.0.1`
- Release date: 2026-05-14
- License: Apache-2.0 for the public open-source bundle

The official cFS repository states that the bundle and laboratory applications are a development starting point rather than a verified operational flight distribution. The experiment must preserve that limitation in the manuscript.

### Schema validator

- Package: `jsonschema[format]`
- Version: `4.26.0`
- Schema draft: 2020-12

## Pinning rules

1. No experiment may record a branch name as its simulator version.
2. NOS3, every recursive submodule, and every container image must be identified by immutable commit or digest.
3. The NOS3-pinned cFS submodule is authoritative for the integrated testbed.
4. A separately checked-out cFS release may be used only for an explicitly labeled standalone validation.
5. Updating any pin creates a new environment version and requires nominal-baseline revalidation.
6. Mutable image tags may be used for initial retrieval only; the resolved digest must be recorded before scored trials.

## Known implementation concerns

- NOS3 is a multi-component environment with recursive submodules; a top-level commit alone is insufficient for reproducibility.
- Some ground-system and radio paths have had configuration-specific issues. The first baseline will use the simplest documented command/telemetry path that passes nominal validation.
- Graphical tools may introduce macOS display dependencies. They are not required for Gate 3.
- Docker CLI presence does not prove that Docker Desktop is running. `scripts/verify_wp4_runtime.sh` must pass.
- The experiment must not use Docker host networking or mount the Docker socket into experiment containers.

## Gate 3 entry checks

WP4 implementation may start after:

- Docker daemon and Compose validation pass
- An `amd64` Linux container runs successfully
- An internal Docker network is created and inspected successfully
- NOS3 is checked out at the selected commit
- Recursive submodule commits are recorded
- The NOS3 image digest is recorded
- The experiment JSON Schema passes the included positive and negative tests
- The environment-specific ROE controls are reviewed

## Decision

Proceed with a Docker-first, headless, exact-commit NOS3 architecture. Do not install or modify NOS3 inside the research repository; use the ignored `external/` directory and retain upstream licenses.