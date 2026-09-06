# Reproducibility Guide

This guide separates **safe repository validation**, **Study-1 statistical reproduction**, **Study-2 result verification**, **Study-8 frozen-result and submitted-package verification**, **bounded testbed validation**, and **new scientific replication**.

The goal is to keep the repository reproducible without accidentally rewriting a frozen scientific record or a submitted publisher package.

For the live publication state, read [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md) first.

## 1. Current evidence and publication map

### Study 1

Study 1 contains **720 VALID observations** from 24 frozen cells x 30 repetitions. Nine retained INVALID attempts remain provenance outside statistical membership.

Public evidence-of-record:

- version DOI: `10.5281/zenodo.22181540`
- concept DOI: `10.5281/zenodo.22181539`

Study 1 is reported in Paper 1 together with Study 2, but the two statistical populations remain separate.

### Study 2

Study 2 contains **3,872 VALID observations**, **0 INVALID attempts**, and **85 frozen cells**.

Canonical statistical closeout:

- `study2/PHASE7_RESULTS_FREEZE.json`
- `study2/PHASE7_PROVENANCE.json`
- independent reproduction with 0 mismatches

Public Phase-6 source-evidence archive:

- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

### Study 8

Study 8 / `S8-PQC-ICR-001` is a separate deterministic finite modeled study.

- canonical positions: **3,456**
- same-repository independently written reproduction: **3,456/3,456 exact row matches, 0 mismatches**
- all four policies: `635/864` trusted-recovery success
- prespecified primary contrast: `P3 - P1 = 0/1 = 0.000000 percentage points`
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation-audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`

Frozen target-neutral publication package:

`publication/study8/`

Current submitted Acta state:

- journal: Acta Astronautica
- manuscript ID: `AA-D-26-02872`
- submitted: 2026-09-06
- current status: `With Editor`
- submitted package freeze: `S8-ACTA-PKGFREEZE-002`
- submitted package source commit: `f5e9a1d4553737e534821bf647463abfd44fa0dd`

Canonical live publisher-state records:

- `publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`
- `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Historical pre-submission freeze-002 files intentionally retain their stage-local wording and must not be rewritten merely to appear current.

## 2. Safe repository validation

Safe validation checks structure, frozen hashes, schemas, deterministic reconstruction contracts, and current publication state without changing canonical observations or statistical results.

A standard release-gate validation may include:

```bash
python scripts/audit_repository_release_gate.py
python scripts/audit_study8_publication_current_state.py
```

For Study 8 specifically, safe frozen-state checks include:

```bash
python study8/scripts/check_phase8_hash_binding.py
python study8/analysis/scripts/check_phase8_6_results_freeze.py
python study8/scripts/check_study8_technical_close.py
python publication/study8/scripts/check_publication_freeze.py
python scripts/audit_study8_publication_current_state.py
```

The final command verifies both the historical frozen source package and the later Acta submitted-state package, including the exact five publisher-facing file hashes.

Safe validation does **not** authorize:

- rerunning a canonical campaign;
- regenerating frozen statistical outputs;
- changing a frozen endpoint or population;
- changing submitted publisher-facing files;
- replacing a null or negative result with a post-hoc alternative.

## 3. Study-1 statistical reproduction

Study-1 reconstruction tooling may reproduce the frozen statistical summaries from the preserved evidence and reference outputs. It must not silently change the 720-observation statistical population or promote the 696-observation complete-block sensitivity analysis to the primary population.

Study-1 reproduction is not permission to rerun the original study with new conditions.

## 4. Study-2 verification and reproduction

Study-2 verification should use the canonical Phase-7 results/provenance files and the independently reproduced result record.

The public Phase-6 ZIP can be re-downloaded and SHA-256 checked against:

`195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

Do not regenerate a different Phase-6 archive and describe it as the published evidence-of-record.

## 5. Study-8 verification

Study 8 has two distinct frozen layers:

1. **scientific/results freeze** under `study8/`;
2. **target-neutral publication freeze** under `publication/study8/`.

It also has a later venue-specific submitted package under:

`publication/Paper_4_Study_8/Acta_Astronautica/`

The submitted package is not a new scientific population. Venue formatting, editorial review, portal entry, and submission did not rerun the model or statistics.

To verify the current state, use:

```bash
python scripts/audit_study8_publication_current_state.py
```

That check should confirm:

- source publication freeze remains intact;
- manuscript ID is `AA-D-26-02872`;
- publisher state is `With Editor`;
- exact submitted file hashes match `S8-ACTA-PKGFREEZE-002`;
- no scientific reexecution or statistical reanalysis is recorded.

## 6. Interpretation boundaries during reproduction

Reproduction must preserve the scientific meaning of the frozen studies.

For Study 8:

- logical slots are model indices, not seconds or milliseconds;
- standardized cryptographic-object bytes are modeled transfer burden, not measured onboard execution cost;
- the study does not measure RF throughput, orbit timing, ground-station latency, CPU, energy, thermal load, or flight performance;
- `TRUST_RESTORED` is a modeled state, not proof that a real mission recovered;
- same-repository independently written reproduction is reproducibility, not external laboratory or independent-human replication.

For Studies 1 and 2:

- do not pool their statistical populations;
- preserve frozen invalid-attempt handling;
- preserve sensitivity-versus-primary distinctions;
- preserve structural-control interpretations where prespecified.

## 7. New scientific replication

A genuinely new replication is a different activity from repository verification.

A new replication may require new data, a new environment, independent implementation, or external experimental execution. It must be prospectively authorized and must not overwrite the frozen original-study evidence.

If a future replication is performed, store it as a new evidence object with its own protocol, provenance, hashes, and interpretation boundary.

## 8. Submitted-paper rule

Paper 1 and Study-8 Paper 4 are already submitted.

Do not modify their submitted publisher-facing files merely to improve wording, formatting, or publication optics while editorial review is active.

Changes are permitted only if the relevant journal explicitly requests a revision or the submission is otherwise formally reopened under a new controlled revision gate.

## 9. Next publication-development work

The next unsent publication priority is the Studies 3 + 4 + 6 synthesis described in [`PUBLICATION_PHASE_MAP.md`](PUBLICATION_PHASE_MAP.md).

Begin with frozen-state verification and literature/novelty/claim-boundary/live-venue review. Do not rerun those studies simply because a venue prefers a different result or scope.
