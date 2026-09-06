<div align="center">

# Mission-Aware Satellite Cyber Response and Trusted Recovery

**Reproducible research on cyber response and trusted recovery under mission, contact, evidence, and bounded-compromise constraints.**

[![Study 1 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22181540.svg)](https://doi.org/10.5281/zenodo.22181540)
[![Study 2 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22289114.svg)](https://doi.org/10.5281/zenodo.22289114)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--9752--3743-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-9752-3743)
[![Research data](https://img.shields.io/badge/data-CC%20BY%204.0-blue)](LICENSE)
[![Code](https://img.shields.io/badge/code-MIT-green)](LICENSE)

[Current publication state](docs/CURRENT_PUBLICATION_STATE.md) · [Publication phase map](docs/PUBLICATION_PHASE_MAP.md) · [Publication packages](publication/README.md) · [Study 2](study2/README.md) · [Study 8](study8/README.md) · [Reproduce](docs/REPRODUCIBILITY_GUIDE.md) · [Security](SECURITY.md) · [Citation](CITATION.cff)

</div>

![Repository research workflow](docs/assets/repository-overview.svg)

## Current publication state

Read [`docs/CURRENT_PUBLICATION_STATE.md`](docs/CURRENT_PUBLICATION_STATE.md) before using older preparation, freeze, venue-fit, or handoff documents.

Two publication lines are now submitted:

| Publication | Studies | Journal | Manuscript ID | Submitted | Current state |
|---|---|---|---|---|---|
| Paper 1 | Study 1 + Study 2 | AIAA Journal of Aerospace Information Systems | `2026-09-I012066` | 2026-09-05 | Editorial/peer-review workflow pending |
| Roadmap Paper 4 | Study 8 | Acta Astronautica | `AA-D-26-02872` | 2026-09-06 | `With Editor` |

The next unsent publication-development priority is **Paper 2: Studies 3 + 4 + 6**, starting with frozen-state verification plus a fresh literature, novelty, claim-boundary, and live venue review.

Study 7 remains the later Paper-3 line. Study 5 remains a deferred portability/external-validity publication decision.

## Research at a glance

The repository contains separately frozen studies. Their statistical populations and evidence identities are not silently pooled.

### Study 1

- frozen design: 24 cells x 30 valid repetitions
- statistical population: **720 VALID observations**
- retained invalid attempts: 9 outside statistical membership
- 696-observation final-commit complete-block analysis: sensitivity only
- public evidence-of-record: Zenodo v1.0.0
- version DOI: `10.5281/zenodo.22181540`
- concept DOI: `10.5281/zenodo.22181539`

### Study 2

- experiment: `S2-AEATR-001`
- frozen design: 85 cells
- statistical population: **3,872 VALID observations**
- invalid attempts: 0
- primary paired contrasts: 162
- prespecified secondary contrasts: 432
- independent reproduction: 0 mismatches
- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public Phase-6 ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

Study 1 and Study 2 are reported together in Paper 1 but remain separate empirical populations.

### Study 8

Study 8 (`S8-PQC-ICR-001`) is a separate deterministic finite modeled study of trusted post-compromise cryptographic transition under finite logical contact budgets.

- frozen population: **3,456 modeled positions**
- same-repository independently written reproduction: **3,456/3,456 exact row matches, 0 mismatches**
- all four policies: `635/864` trusted-recovery success
- prespecified primary contrast `P3 - P1`: `0/1 = 0.000000 percentage points`
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`

Frozen source publication package:

`publication/study8/`

Current Acta submitted-state package:

`publication/Paper_4_Study_8/Acta_Astronautica/`

Canonical Acta status file:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

The exact submitted package is `S8-ACTA-PKGFREEZE-002` from commit `f5e9a1d4553737e534821bf647463abfd44fa0dd`.

## Scientific interpretation boundaries

The repository intentionally preserves negative, null, conditional, and scope-limited findings.

- Never pool separately frozen study populations without a prospectively authorized analysis.
- Study-1 P1 remains unsupported on its predeclared primary outcomes.
- Study-1 C1 timing is modeled contact, not operational ground-contact timing.
- Study-1 T1 is omission/reduction of selected policy-visible evidence, not stale/contradictory/forged evidence.
- Study-1 P7 is deterministic rule-based, not AI/ML.
- Study-2 Block-C BENIGN/ADVERSARIAL contrasts are structural label-invariance controls, not causal benign-versus-adversarial discrimination evidence.
- Study-2 K4 is intermittent/flapping contact, not ordinal severity 4.
- Study-2 A2/K2 is a coupled producer-compromise/contact-loss profile.
- Study 8 is a complete deterministic finite population, not a probabilistic sample.
- Study-8 `P3 - P1` is exactly zero and supports no policy-success superiority claim.
- Study-8 logical slots are model indices, not seconds or spacecraft latency.
- Standardized cryptographic-object bytes are modeled burden, not measured onboard CPU, energy, RF, or flight performance.
- Same-repository independently written reproduction is reproducibility, not external replication.
- No operational spacecraft, RF, flightworthiness, certification, or production-performance claim is supported without new frozen evidence.

## Submitted publication packages

### Paper 1

Canonical package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Do not modify the submitted Paper-1 manuscript or publisher-facing package unless JAIS explicitly requests a revision.

### Roadmap Paper 4 / Study 8

Canonical current-state package:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Acta manuscript ID: `AA-D-26-02872`.

Do not modify the submitted manuscript, figures, or frozen Study-8 science unless Acta explicitly requests a revision.

Historical freeze-002 preparation files in the Acta directory intentionally retain their pre-submission stage wording. Use `README_CURRENT.md` and `ACTA_SUBMISSION_STATUS.json` for the live publisher state.

## Next publication-development work

The operational sequence is maintained in [`docs/PUBLICATION_PHASE_MAP.md`](docs/PUBLICATION_PHASE_MAP.md).

Current next priority:

1. audit the frozen scientific state of Studies 3, 4, and 6 separately;
2. identify null, negative, conditional, structural-zero, and claim-limiting findings;
3. perform a fresh literature and novelty review;
4. perform a claim-boundary audit;
5. perform a live venue review before selecting a target;
6. evaluate Study 5 only as a clearly separated portability/external-validity component;
7. obtain explicit author approval before venue lock or venue-specific package preparation.

No frozen study should be rerun or enlarged merely to improve publication optics.

## Repository map

| Location | Purpose |
|---|---|
| [`docs/CURRENT_PUBLICATION_STATE.md`](docs/CURRENT_PUBLICATION_STATE.md) | Canonical current cross-publication handoff |
| [`docs/PUBLICATION_PHASE_MAP.md`](docs/PUBLICATION_PHASE_MAP.md) | Operational publication sequencing |
| [`publication/`](publication/README.md) | Submitted packages, frozen publication sources, and publication controls |
| [`study2/`](study2/README.md) | Study-2 protocol, campaign, freeze, provenance, audit, and public release |
| [`study8/`](study8/README.md) | Study-8 design, evidence, reproduction, results freeze, and submission pointers |
| [`analysis/`](analysis/README.md) | Study-1 statistical reconstruction and validation |
| [`docs/`](docs/) | Theory, methods, governance, provenance, and publication closeouts |
| [`configs/`](configs/) | Frozen experiment designs, schemas, adapters, and toolchain locks |
| [`src/mission_recovery/`](src/mission_recovery/) | Study-1 research implementation |
| [`tests/`](tests/) | Unit, contract, regression, and governance tests |
| [`scripts/`](scripts/) | Validation, audit, runtime, campaign, and release tooling |
| [`tracker/`](tracker/) | Detailed research-program history and task provenance |

## Safe validation

Normal repository validation must not rerun frozen canonical campaigns or rewrite frozen statistical outputs.

Use the repository release gate and the per-study freeze checkers. For Study 8 current publication/submission state, run:

```bash
python scripts/audit_study8_publication_current_state.py
```

Every future publisher submission requires a separate explicit final author authorization.
