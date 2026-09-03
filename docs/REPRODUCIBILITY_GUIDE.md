# Reproducibility Guide

This guide separates **safe repository validation**, **Study-1 statistical reproduction**, **Study-2 result verification**, **Study-8 frozen-result and publication-package verification**, **bounded testbed validation**, and **new scientific replication**. The purpose is to make the research reproducible without accidentally rewriting any frozen experimental or modeled record.

## 1. Current frozen evidence map

### Study 1

Study 1 contains **720 VALID observations** from 24 frozen cells × 30 repetitions. Nine retained INVALID attempts remain provenance outside statistical membership. The DOI-bearing public evidence-of-record is Zenodo v1.0.0:

- version DOI: <https://doi.org/10.5281/zenodo.22181540>
- concept DOI: <https://doi.org/10.5281/zenodo.22181539>

That Zenodo record is **Study-1 evidence only**.

### Study 2

Study 2 contains **3,872 VALID observations**, **0 INVALID attempts**, and **85 frozen cells**. Its canonical statistical closeout is recorded by:

- [`../study2/PHASE7_RESULTS_FREEZE.json`](../study2/PHASE7_RESULTS_FREEZE.json)
- [`../study2/PHASE7_PROVENANCE.json`](../study2/PHASE7_PROVENANCE.json)
- [`../study2/docs/PHASE7_RESULTS_FREEZE.md`](../study2/docs/PHASE7_RESULTS_FREEZE.md)
- [`../study2/evidence/phase7/INDEPENDENT_REPRODUCTION_AUDIT.json`](../study2/evidence/phase7/INDEPENDENT_REPRODUCTION_AUDIT.json)

Frozen Study-2 identities include:

- Phase-6 evidence ZIP SHA-256 `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- observations SHA-256 `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- trial-manifest SHA-256 `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`
- Phase-7 result ZIP SHA-256 `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`
- independent auditor SHA-256 `3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d`

The exact Phase-7 result ZIP is durably retained in repository history under `study2/evidence/phase7/archive/`. The underlying Phase-6 source evidence remains hash-bound but still requires a responsible-release-reviewed DOI-bearing archive before the existing journal submission. Do not reuse the Study-1 DOI for Study 2 and do not invent a Study-2 DOI.

### Study 8

Study 8 (`S8-PQC-ICR-001`) is a **complete deterministic finite modeled population**, not a probabilistic sample. It contains exactly **3,456 canonical observations** and a separately written implementation-level reproduction of all **3,456** factor positions with **0 mismatches**.

Scientific technical-close/freeze records:

- [`../study8/README.md`](../study8/README.md)
- [`../study8/STUDY8_TECHNICAL_CLOSE.json`](../study8/STUDY8_TECHNICAL_CLOSE.json)
- [`../study8/docs/PHASE8_7_TECHNICAL_CLOSE.md`](../study8/docs/PHASE8_7_TECHNICAL_CLOSE.md)
- [`../study8/analysis/RESULTS_FREEZE_MANIFEST.json`](../study8/analysis/RESULTS_FREEZE_MANIFEST.json)
- [`../study8/results/S8-PQC-ICR-001/independent_audit_summary.json`](../study8/results/S8-PQC-ICR-001/independent_audit_summary.json)

Frozen Study-8 scientific identities include:

- canonical observations SHA-256 `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary findings SHA-256 `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- independent findings SHA-256 `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation audit SHA-256 `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`
- science/results merge commit `63106778559c3127a7d6e8765d52939b73a3f35b`
- post-science-merge repository validation run `33761681328` — `SUCCESS`

The dedicated Study-8 companion publication package is also frozen and merged without changing those scientific identities:

- current publication state: `PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`
- publication status: [`../publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json`](../publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json)
- publication freeze manifest: [`../publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`](../publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json)
- publication checksums: [`../publication/study8/SHA256SUMS.txt`](../publication/study8/SHA256SUMS.txt)
- frozen package commit: `cbad15227bf99d1b7b19d95b0581196d78208f95`
- publication PR: `#92`
- publication merge commit: `87bcec000d278aeffef1222ce814098c93ada362`
- post-merge results-freeze CI: `33781901833` — `SUCCESS`
- post-merge repository CI: `33781901724` — `SUCCESS`

Study 8 remains a separate companion-paper research stream and is not part of the existing Study-1/Study-2 journal manuscript.

## 2. Reproducibility levels

| Level | Purpose | Starts simulator/runtime? | Writes new scientific campaign evidence? |
|---|---|---:|---:|
| A — repository validation | Validate current-state documents, schemas, publication controls, Python/shell sources, and tests | No | No |
| A1 — Study-1 statistical reproduction | Recompute/regression-check frozen Study-1 WP10 manuscript contracts from tracked derived inputs | No | No |
| A2 — Study-2 Phase-7 verification | Verify frozen Study-2 provenance/results and, when the immutable Phase-6 source ZIP is available, run the independent auditor | No | No |
| A3 — Study-8 technical-close verification + publication-package verification | Verify frozen Study-8 design/implementation hashes, results-freeze hashes, 3,456/3,456 audit identity, technical close, and 11-file publication-package freeze/merge state | No | No |
| B — bounded testbed preflight | Rebuild pinned NOS3/Fortytwo/cFS environment and verify isolated runtime liveness | Yes | No scored campaign |
| C — new scientific replication | Execute new observations under a separately frozen protocol | Yes | Yes — new evidence, not any frozen study |

Start with Level A. Normal repository inspection does not require NOS3, Docker, a historical Study-1/Study-2 operator, or the Study-8 canonical runner.

## 3. Clone and create an isolated validation environment

```bash
git clone https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git
cd mission-aware-satellite-cyber-recovery

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Windows users should prefer WSL2 for Bash/Docker workflows. Pure Python Level-A checks can also run in a normal Python environment.

## 4. Level A — safe repository validation

Run:

```bash
python scripts/audit_repository_release_gate.py
python scripts/audit_bibliography_metadata.py
python scripts/validate_experiment_schema.py
python -m unittest discover -s tests -p 'test_*.py'
```

Compile tracked Python sources:

```bash
python -m compileall -q src scripts tests analysis study2 study8 publication/study8/scripts
```

Parse every tracked shell script without executing it:

```bash
find scripts study2 study8 -type f -name '*.sh' -print0 \
  | sort -z \
  | while IFS= read -r -d '' script; do
      echo "bash -n: $script"
      bash -n "$script"
    done
```

### Level-A acceptance

A safe repository validation passes when:

- current-state release-gate audit exits zero, including the Study-8 publication current-state overlay;
- bibliography metadata audit exits zero;
- experiment schema validation exits zero;
- all Python unit tests pass;
- all tracked Python sources compile;
- all tracked shell scripts parse with `bash -n`;
- validation produces no tracked-file drift.

This level executes no campaign trial and changes no frozen evidence.

## 5. Level A1 — reproduce the frozen Study-1 WP10 contracts

The [`../analysis/`](../analysis/README.md) directory contains an executable reconstruction prepared after the Study-1 campaign/Zenodo publication and before journal submission. The original executable WP10 source was not preserved. The reconstruction is explicitly labeled and regression-validated against preserved authoritative outputs.

Create a separate environment:

```bash
python3.11 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install --upgrade pip
python -m pip install --only-binary=:all: -r analysis/requirements.txt
python analysis/reproduce_wp10.py --validate
python -m unittest discover -s analysis/tests -p 'test_*.py'
```

This reads tracked derived Study-1 inputs only. It does not read or modify the raw WP9 campaign, start NOS3/cFS, consume campaign seeds, or create observations.

A PASS validates the covered frozen statistical contracts; it does not reclassify the reconstruction as the original WP10 analysis source.

## 6. Level A2 — verify frozen Study-2 Phase-7 results

### 6.1 Repository-retained checks

A clone can inspect the canonical freeze/provenance records and verify that the exact Phase-7 result ZIP is present:

```bash
python -m json.tool study2/PHASE7_RESULTS_FREEZE.json >/dev/null
python -m json.tool study2/PHASE7_PROVENANCE.json >/dev/null
python -m json.tool study2/evidence/phase7/INDEPENDENT_REPRODUCTION_AUDIT.json >/dev/null

shasum -a 256 \
  study2/evidence/phase7/archive/study2-phase7-results-60f64327c45efda24cbb5b342f9d0eac908e1934.zip
```

Expected result-ZIP SHA-256:

```text
0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417
```

The canonical record reports:

- 3,872 VALID observations;
- 0 INVALID attempts;
- 85 cells;
- 162 primary paired contrasts;
- 432 secondary contrasts;
- independent reproduction mismatches = 0.

### 6.2 Independent arithmetic reproduction from source observations

The repository retains the independent auditor at:

```text
study2/scripts/audit_phase7_independent.py
```

It does **not** import or invoke the primary Phase-7 analyzer. It independently recomputes the frozen numerical cell summaries, primary contrasts, secondary contrasts, Holm adjustments/rejections, and terminal-state distributions from the immutable Phase-6 observations.

Running that auditor requires the exact Phase-6 source-evidence ZIP plus the exact Phase-7 result ZIP. The original Phase-6 Actions artifact is hash-bound but temporary; the journal package therefore requires a durable responsible-release-reviewed source archive before submission. Once that archive is published, this guide should be updated with the actual DOI/download identity rather than a placeholder.

Do not regenerate Study-2 campaign observations merely to satisfy this prerequisite.

## 7. Study-2 interpretation checks during reproduction

Reproducibility includes claim discipline, not only arithmetic identity:

- Block-C BENIGN/ADVERSARIAL contrasts are a **structural label-invariance/control** result because the cause label does not change hidden truth or generated policy-visible evidence within an ambiguity family.
- The 54 zero Block-C contrasts do not establish empirical discrimination or non-discrimination between genuinely different causal mechanisms.
- K4 is an intermittent/flapping profile and is not ordinal severity 4.
- A2/K2 combines producer compromise and modeled contact loss.
- Study-2 logical SIL seconds are not operational latency.
- secondary n=32 blocks are sensitivity/estimation evidence.
- no weighted global policy score or global policy rank is supported.

These boundaries are part of the frozen journal evidence contract.

## 8. Level A3 — verify frozen Study-8 results, publication package, and current state

Study-8 verification is intentionally **read-only**. Do not run `study8/runtime/run_phase8_canonical.py`, the historical statistical-analysis workflow, or the historical publication-freeze executor as a clone smoke test.

Run the safe integrity gates:

```bash
python study8/scripts/check_phase8_hash_binding.py
python study8/analysis/scripts/check_phase8_6_results_freeze.py
python study8/scripts/check_study8_technical_close.py
python publication/study8/scripts/check_publication_freeze.py
python scripts/audit_repository_release_gate.py
```

The technical-close checker verifies the historical scientific close, including:

- all 12 Phase-8.6 bound source/evidence SHA-256 values;
- canonical population = 3,456;
- independent implementation-level reproduction = 3,456 rows;
- exact row matches = 3,456;
- mismatches = 0;
- all four policy-success fractions = `635/864`;
- prespecified `P3 - P1` risk difference = `0/1`;
- finite-population inference policy forbids sampling p-values/CIs/bootstrap/permutation inference.

Its historical technical-close status predates publication development. The current repository release gate separately verifies that publication development, freeze, PR #92 merge, and post-merge CI are complete while scientific re-execution remains prohibited.

The primary and independent findings must remain byte-identical at SHA-256:

```text
26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e
```

The canonical observations must remain:

```text
cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf
```

The publication-freeze checker additionally verifies:

- exactly 11 publication artifacts remain hash-identical to `PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`;
- publication PR #92 is recorded as completed;
- final reviewed head = `75c98356751087dd648684ade7cb973c166cbce0`;
- `main` publication merge commit = `87bcec000d278aeffef1222ce814098c93ada362`;
- post-merge Study-8 results-freeze run `33781901833` = `SUCCESS`;
- post-merge repository run `33781901724` = `SUCCESS`;
- publication submission and scientific re-execution remain prohibited.

### Study-8 interpretation checks during reproduction

- `P3 - P1 = 0/1` is a negative primary policy result; do not convert it into a superiority claim.
- the profile result concerns standardized cryptographic-object byte burden interacting with the frozen logical contact model; it is not measured onboard PQC CPU/energy/latency.
- logical slots are model indices, not real contact seconds or milliseconds.
- the 3,456 positions are a complete deterministic finite factorial population, not a sample from a superpopulation.
- no sampling significance inference is supported.
- no operational spacecraft, RF, flightworthiness, certification, or production claim is supported.
- same-repository independently written reproduction is not external laboratory or independent-human replication.

Study-8 venue adaptation must consume the frozen publication package; it must not recreate the canonical campaign or rerun statistics to obtain a more favorable result.

## 9. Frozen reference testbed environment

The retained Study-1 toolchain lock records the validated baseline as:

- host operating system: macOS 26.5.2;
- host architecture: x86_64;
- Python: 3.11.7;
- Git: 2.54.0;
- Docker CLI/server: 29.6.2;
- Docker Compose: 5.3.1;
- `jsonschema`: 4.26.0;
- execution platform: `linux/amd64`;
- NOS3 commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`;
- Fortytwo commit: `eda252bf31f27850e867e698cfdd963e143ead1f`;
- pinned NOS3 container digest: `sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`.

See [`../configs/toolchain-lock.json`](../configs/toolchain-lock.json) and the retained lock files under [`../artifacts/`](../artifacts/).

## 10. Level B — bounded testbed preflight

Level B validates infrastructure/liveness; it is not a scored scientific trial.

```bash
docker info
PULL_IMAGE=1 bash scripts/prepare_nos3_candidate.sh
bash scripts/prepare_42_candidate.sh
bash scripts/build_nominal_nos3.sh
DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=30 \
  bash scripts/run_nominal_runtime_preflight.sh
bash scripts/cleanup_nominal_runtime.sh
```

Expected PASS markers include:

```text
FORTYTWO_PREPARATION_STATUS=PASS
NOMINAL_BUILD_STATUS=PASS
NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS
```

Run Level B from a disposable/working clone because preparation/build steps can regenerate local evidence/lock material.

## 11. Do not use historical campaign operators as smoke tests

Historical Study-1, Study-2, and Study-8 campaign tooling remains in Git because it is part of scientific provenance. It is **not** a normal installation test.

Do not use a historical campaign operator to validate a clone. Use Level A for repository validation, Level A1/A2/A3 for frozen evidence verification, and Level B for infrastructure validation.

Any intentional new execution must be treated as a new replication or validation study with its own protocol, seeds/factor positions, run IDs, environment identity, evidence archive, and analysis membership. It must not overwrite or append to any frozen population.

## 12. Verify the published Study-1 Zenodo archive

Download the Study-1 Zenodo v1.0.0 files and verify the included checksum manifest:

```bash
shasum -a 256 -c RELEASE_CHECKSUMS.sha256
```

See [`40-zenodo-publication-closeout.md`](40-zenodo-publication-closeout.md) for the frozen Study-1 release identities.

## 13. Publication boundaries

### Existing Study-1/Study-2 journal article

The authoritative article assembly is [`../publication/manuscript/MANUSCRIPT-ASSEMBLY.md`](../publication/manuscript/MANUSCRIPT-ASSEMBLY.md). Study-1 and Study-2 Methods/Results are separate components so future editing cannot silently merge populations or change historical findings.

A successful clone validation does not make the current branch a submitted journal version. The final submission snapshot must be recorded only after:

1. two-study manuscript integration passes CI and claim/citation audits;
2. Study-2 source evidence passes responsible-release review and is durably DOI archived;
3. the actual Study-2 DOI is inserted into Data Availability;
4. the live target-journal requirements are rechecked;
5. the exact export passes final frozen-claim/DOI/scope review.

### Study-8 companion paper

Study 8 is technically closed and its dedicated companion publication package is now **hash-frozen, merged to `main`, and post-merge validated**. The current package is indexed at [`../publication/study8/README.md`](../publication/study8/README.md).

The next gate is venue-specific submission-package preparation using the frozen package. That work must not silently modify the existing two-study journal manuscript, rerun the Study-8 canonical campaign, rerun statistics to search for a preferable result, or broaden the frozen claim/inference boundary.

No Study-8 DOI, venue acceptance, publisher submission, or publication identity is claimed until those events actually occur.

## 14. Safety boundary

Do not adapt these instructions to operational spacecraft, production TT&C systems, live RF links, real credentials, proprietary mission telemetry, or unauthorized targets. The reported work is controlled defensive software simulation/modeling research.

See [`../SECURITY.md`](../SECURITY.md), [`05-legal-ethical-boundaries.md`](05-legal-ethical-boundaries.md), and [`13-laboratory-rules-of-engagement.md`](13-laboratory-rules-of-engagement.md).
