# Reproducibility Guide

This guide separates **safe repository validation**, **bounded testbed validation**, and **new scientific replication** so users can reproduce the software and evidence controls without accidentally rewriting the historical experiment record.

The DOI-bearing evidence-of-record for the completed WP9 campaign is Zenodo v1.0.0:

- version DOI: <https://doi.org/10.5281/zenodo.22181540>
- concept DOI: <https://doi.org/10.5281/zenodo.22181539>

## 1. What can be reproduced from GitHub alone?

A normal clone contains the experiment design, source code, tests, testbed/release tooling, manuscript, figures, tables, provenance documentation, and cryptographic identities. The full raw WP9 campaign tree is intentionally not committed to GitHub; it is distributed through the Zenodo dataset.

There are three useful reproducibility levels:

| Level | Purpose | Starts simulator/runtime? | Writes new scientific campaign evidence? |
|---|---|---:|---:|
| A — repository validation | Validate current-state release controls, schemas, contracts, all tracked script syntax, and Python test suite | No | No |
| A2 — WP10 statistical reproduction | Recompute and regression-check the frozen manuscript-facing statistical contracts from the tracked derived analysis inputs | No | No |
| B — bounded testbed preflight | Rebuild pinned NOS3/Fortytwo/cFS environment and verify isolated runtime liveness | Yes | No scored campaign |
| C — scientific replication | Execute new experimental observations under a separately controlled replication protocol | Yes | Yes — new evidence, not the archived WP9 record |

Start with Level A. Most users who want to inspect or test the repository do not need the full simulator stack.

## 2. Frozen reference environment

The retained toolchain lock records the validated baseline as:

- host operating system: macOS 26.5.2;
- host architecture: x86_64;
- Python: 3.11.7;
- Git: 2.54.0;
- Docker CLI/server: 29.6.2;
- Docker Compose: 5.3.1;
- `jsonschema`: 4.26.0;
- execution platform requested by the testbed scripts: `linux/amd64`;
- NOS3 commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`;
- Fortytwo commit: `eda252bf31f27850e867e698cfdd963e143ead1f`;
- pinned NOS3 container digest: `sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`.

See [`configs/toolchain-lock.json`](../configs/toolchain-lock.json) and the lock files in [`artifacts/`](../artifacts/).

The GitHub Actions validation path uses Ubuntu with Python 3.11 for repository-level validation. A different host can therefore validate the Python code even when it cannot reproduce the full historical simulator host exactly.

## 3. Prerequisites

### Level A — repository validation

Required:

- Git;
- Python 3.11 recommended for Level A and required for Level A2 statistical reproduction;
- internet access for the initial clone and Python dependency installation.

### Level B — full testbed preflight

Also required:

- Docker Desktop or Docker Engine with a reachable daemon;
- support for `linux/amd64` containers;
- internet access for the initial NOS3/Fortytwo clones and container-image pull;
- enough local disk space for NOS3, its recursive submodules, the Fortytwo source/build, container image, and generated build artifacts;
- Bash and standard Unix utilities (`awk`, `shasum`, etc.).

On Apple Silicon, Docker must be able to run the scripts' explicit `linux/amd64` platform. The frozen host baseline itself was x86_64 macOS, so Apple Silicon execution should be treated as a compatible reproduction target rather than an identical host reproduction.

Windows users should prefer WSL2 for the Bash/Docker workflow.

## 4. Clone and create an isolated Python environment

```bash
git clone https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git
cd mission-aware-satellite-cyber-recovery

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell for Level A only, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
```

The development dependency is pinned in [`requirements-dev.txt`](../requirements-dev.txt).

## 5. Level A — run the safe validation suite

### 5.1 Record the local environment

```bash
bash scripts/verify_environment.sh
```

This is an inventory step. Missing Docker or GitHub CLI does not prevent the pure Python test suite, but Docker is required for Level B.

### 5.2 Run the current-state repository release-gate audit

```bash
python scripts/audit_repository_release_gate.py
```

This fail-closed audit parses every tracked JSON/CSV/TOML artifact, checks active-document local links and recommended script entry points, verifies current submission/tracker state, cross-checks frozen DOI/hash identities, verifies key historical Git commits from a full checkout, and rejects unresolved `TODO`/`FIXME`/`XXX`/`HACK` markers in Python/shell sources. It does not start the simulator or execute a campaign trial.

### 5.3 Validate the experiment schemas and historical/frozen fixtures

```bash
python scripts/validate_experiment_schema.py
```

This validates the machine-readable experiment schema and the retained positive/negative fixtures. Some stage-local messages describe the historical state encoded by a frozen WP5–WP9 fixture (for example, an authorization being active at that checkpoint). Those messages are not current runtime authorization; current state is governed by the tracker and final release-gate audit.

### 5.4 Run all Python tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

The suite covers the event library, policy logic, trusted-recovery behavior, primary metrics, runtime contracts, pilot controls, WP9 campaign design/governance, compatibility constraints, and regression tests.

### 5.5 Parse every tracked shell script without executing it

```bash
find scripts -type f -name '*.sh' -print0 \
  | sort -z \
  | while IFS= read -r -d '' script; do
      echo "bash -n: $script"
      bash -n "$script"
    done
```

This is intentionally exhaustive: it covers historical WP5/WP6/WP7/WP8/WP9/WP9-B2 scripts and current setup/reproducibility helpers. `bash -n` parses shell syntax and does not execute script bodies.

### 5.6 Compile every tracked Python source

```bash
python -m compileall -q src scripts tests analysis
```

### Level A acceptance

A Level A validation is successful when:

- the current-state release-gate audit exits zero;
- all tracked JSON/CSV/TOML documents parse;
- schema validation exits zero;
- the Python unit-test discovery exits zero;
- every tracked shell script passes `bash -n`;
- every tracked Python source compiles.

This level does **not** claim that NOS3, cFS, Fortytwo, Docker networking, or the historical campaign have been reproduced.

## 5A. Level A2 — reproduce the frozen WP10 statistical contracts

The [`analysis/`](../analysis/README.md) directory contains a reconstruction of the frozen WP10 statistical analysis prepared **after the campaign and Zenodo v1.0.0 publication but before journal submission**. The original executable WP10 analysis source was not preserved; this implementation is explicitly identified as a reconstruction and is validated against cryptographically verified historical outputs.

Create a separate statistical environment and run:

```bash
python3.11 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install --upgrade pip
python -m pip install --only-binary=:all: -r analysis/requirements.txt
python analysis/reproduce_wp10.py --validate
python -m unittest discover -s analysis/tests -p 'test_*.py'
```

This path reads only the tracked derived analysis inputs under `analysis/reference/`. It does not read or modify the raw WP9 campaign, start NOS3/cFS, consume campaign seeds, or create a new observation.

The C1/C2 bootstrap RNG settings were recovered and reproduce their retained Monte Carlo endpoints numerically. The original P5 bootstrap RNG seed was not preserved, so the reconstruction does not fabricate one: it uses a separately identified deterministic reconstruction seed to confirm that the retained marginal dominance/uncertainty classifications are stable. Original P5 interval endpoints remain historical reference values.

A PASS validates the covered frozen statistical contracts; it does not reclassify the reconstruction as original source code and does not modify Zenodo v1.0.0.

## 6. Level B — rebuild the pinned testbed and run the bounded preflight

Run Level B from a disposable/working clone because the preparation/build scripts intentionally regenerate local lock/evidence files. Do not commit generated lock drift unless you are deliberately creating a new reviewed baseline.

### 6.1 Confirm Docker is available

```bash
docker info
```

### 6.2 Prepare the pinned NOS3 checkout and image

```bash
PULL_IMAGE=1 bash scripts/prepare_nos3_candidate.sh
```

This clones NOS3 into the ignored `external/nos3/` directory, checks out the pinned commit, initializes recursive submodules, and records a local lock inventory.

### 6.3 Prepare and build Fortytwo

```bash
bash scripts/prepare_42_candidate.sh
```

The script uses the pinned NOS3 image and performs the Fortytwo build with container networking disabled.

Expected terminal marker:

```text
FORTYTWO_PREPARATION_STATUS=PASS
```

### 6.4 Build the nominal NOS3 stack

```bash
bash scripts/build_nominal_nos3.sh
```

The build runs inside the pinned container with `--network none` and verifies required output artifacts.

Expected terminal marker:

```text
NOMINAL_BUILD_STATUS=PASS
```

### 6.5 Run the bounded nominal runtime preflight

```bash
DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=30 \
  bash scripts/run_nominal_runtime_preflight.sh
```

The preflight is an infrastructure/liveness test. It is not a scored cyber-response trial and does not authorize event injection.

Expected terminal marker:

```text
NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS
```

The script records runtime evidence under `artifacts/runtime/<RUN_ID>/` and cleans project-labeled containers/networks on exit.

### 6.6 Explicit cleanup check

```bash
bash scripts/cleanup_nominal_runtime.sh
```

A clean environment reports that no project-labeled runtime resources remain, or removes only resources carrying this project's research label.

## 7. Do not use the historical campaign operator as a generic smoke test

The repository contains historical WP9 campaign/runtime tooling because it is part of the research provenance. In particular, `scripts/run_wp9_r069_campaign_one_position.sh` is **not** a normal installation test. It was designed to advance the frozen campaign one authorized position at a time and can create scientific evidence.

For repository verification, use Level A. For simulator verification, use Level B.

If a researcher intentionally performs new experimental executions, those runs are a **new replication** and must use a new provenance boundary. They must not overwrite, append to, or be represented as the original archived WP9 campaign.

## 8. Verify the published Zenodo archive

Download all six files from Zenodo v1.0.0 into one directory:

```text
01-wp9-campaign-raw.tar.gz
02-wp9-integrity-freeze.tar.gz
03-publication-and-provenance.tar.gz
README_RELEASE.txt
RELEASE_CHECKSUMS.sha256
RELEASE_MANIFEST.json
```

Then run from that directory:

```bash
shasum -a 256 -c RELEASE_CHECKSUMS.sha256
```

On Linux systems where `sha256sum` is available instead of `shasum`, use the equivalent command appropriate for the checksum-file format.

The repository-side publication closeout records the frozen SHA-256 identities in [`docs/40-zenodo-publication-closeout.md`](40-zenodo-publication-closeout.md).

## 9. Reproduce the manuscript-facing artifacts

The DOI archive includes the publication/provenance bundle that was used to support manuscript-facing outputs. The GitHub repository also tracks the final target-neutral manuscript components, tables, and SVG figures under [`publication/`](../publication/).

Use [`publication/README.md`](../publication/README.md) as the ordered index rather than inferring chronology from directory listings.

## 10. Scientific boundary for replications

A successful local test or new simulation does not change the original study's frozen statistical population. The publication baseline remains:

- 720 VALID observations;
- 9 ledgered INVALID attempts retained as provenance;
- 24 frozen cells × 30 valid repetitions;
- the original ledger, membership, and campaign-tree identities recorded in the integrity freeze;
- the DOI-bearing v1.0.0 archive as the public evidence-of-record.

A new run should be reported as an independent reproduction/replication with its own environment, commit, seeds, run IDs, evidence, and analysis membership.

## 11. Safety boundary

Do not adapt these instructions to operational spacecraft, production TT&C systems, live RF links, real credentials, proprietary mission telemetry, or unauthorized targets. The reported study is a controlled defensive software-in-the-loop experiment.

See [`SECURITY.md`](../SECURITY.md) and [`docs/13-laboratory-rules-of-engagement.md`](13-laboratory-rules-of-engagement.md).
