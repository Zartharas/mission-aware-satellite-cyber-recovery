<div align="center">

# Mission-Aware Satellite Cyber Response and Trusted Recovery

**Reproducible research on cyber response and trusted recovery under mission, contact, evidence, and bounded-compromise constraints.**

[![Study 1 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22181540.svg)](https://doi.org/10.5281/zenodo.22181540)
[![Study 2 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22289114.svg)](https://doi.org/10.5281/zenodo.22289114)
[![Study 7 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22732060.svg)](https://doi.org/10.5281/zenodo.22732060)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--9752--3743-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-9752-3743)
[![Research data](https://img.shields.io/badge/data-CC%20BY%204.0-blue)](LICENSE)
[![Code](https://img.shields.io/badge/code-MIT-green)](LICENSE)

[Current publication state](docs/CURRENT_PUBLICATION_STATE.md) · [Publication phase map](docs/PUBLICATION_PHASE_MAP.md) · [Publication packages](publication/README.md) · [Reproduce](docs/REPRODUCIBILITY_GUIDE.md) · [Security](SECURITY.md) · [Citation](CITATION.cff)

</div>

![Repository research workflow](docs/assets/repository-overview.svg)

## Current publication state

Read [`docs/CURRENT_PUBLICATION_STATE.md`](docs/CURRENT_PUBLICATION_STATE.md) before using older preparation, freeze, venue-fit, or handoff documents.

The repository now has **four submitted publication lines**:

| Publication | Studies | Journal | Submission / manuscript ID | Submitted | Current state |
|---|---|---|---|---|---|
| Paper 1 | Studies 1 + 2 | AIAA Journal of Aerospace Information Systems | `2026-09-I012066` | 2026-09-05 | Editorial/peer-review workflow |
| Paper 4 | Study 8 | Acta Astronautica | `AA-D-26-02872` | 2026-09-06 | `With Editor` |
| Paper 2 | Studies 3 + 4 + 6 | IEEE Transactions on Aerospace and Electronic Systems | `cd1dfa89-4a24-4451-bdd4-af31ce3367f4` | 2026-09-07 | Editorial processing |
| Paper 3 | Study 7 | CEAS Space Journal | `6db04a31-8223-4aaf-af02-e4bafe06ef89` | 2026-09-13 | `Technical check` |

All four submitted lines are frozen. Do not modify publisher-facing packages or rerun frozen studies unless the corresponding journal requests a technical correction or revision.

## Research and publication boundaries

The program intentionally keeps separately frozen studies and publication populations distinct.

- **Study 1:** 720 VALID observations across 24 frozen cells.
- **Study 2 / S2-AEATR-001:** 3,872 VALID observations across 85 cells.
- **Study 3 / S3-K4E-001:** 1,380 deterministic trajectories.
- **Study 4 / S4-MPQ-001:** 4,608 exact rule-by-subset observations.
- **Study 6 / S6-SCTR-001:** 420 exact observations.
- **Study 7 / S7-LSO-001:** 1,033 exact modeled observations.
- **Study 8 / S8-PQC-ICR-001:** 3,456 deterministic modeled positions.

These populations are not silently pooled across papers.

## Submitted publication packages

### Paper 1 - Studies 1 + 2

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Manuscript ID: `2026-09-I012066`.

### Paper 4 - Study 8

`publication/Paper_4_Study_8/Acta_Astronautica/`

Manuscript ID: `AA-D-26-02872`.

### Paper 2 - Studies 3 + 4 + 6

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`.

### Paper 3 - Study 7

`publication/Paper_3_Study_7/CEAS_Space_Journal/`

Submission ID: `6db04a31-8223-4aaf-af02-e4bafe06ef89`.

Current authority:

- `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_INITIAL_SUBMISSION_RECORD_2026-09-13.md`
- `publication/Paper_3_Study_7/CEAS_Space_Journal/README_CURRENT.md`

Study-7 durable evidence:

- version DOI: `10.5281/zenodo.22732060`
- concept DOI: `10.5281/zenodo.22732059`

The historical Paper-3 `Journal_of_Aerospace_Information_Systems/` directory was never submitted and is retained only as superseded venue-development provenance.

## Next publication-development work

Paper 3 is no longer a candidate. Study 7 is consumed by the submitted CEAS paper.

The next publication gate is a **read-only audit of remaining eligible work**, beginning with Study 5 / `S5-CUCD-001` and any other complete repository experiment not already consumed by Papers 1, 2, 3, or 4.

No next venue or manuscript is currently locked. Fresh literature, novelty, overlap, claim-boundary, reproducibility, and live-venue review are required before creating a new publication branch.

## Scientific interpretation boundaries

The repository intentionally preserves negative, null, conditional, and scope-limited findings.

- Never pool separately frozen study populations without a prospectively authorized analysis.
- Logical model time is not operational spacecraft time.
- Modeled cryptographic-object bytes are not measured onboard CPU, energy, RF, or flight performance.
- Same-repository separately implemented reproduction is reproducibility, not external empirical replication.
- Study 4 is not a Byzantine-consensus experiment.
- Study 6 is an abstract artifact-trust model, not an operational supply-chain attack experiment.
- Study 7 is an observability/information-sufficiency assurance study, not a global ML-superiority result.
- No operational spacecraft, RF, flightworthiness, certification, or production-performance claim is supported without new frozen evidence.

## Repository map

| Location | Purpose |
|---|---|
| [`docs/CURRENT_PUBLICATION_STATE.md`](docs/CURRENT_PUBLICATION_STATE.md) | Canonical current cross-publication handoff |
| [`docs/PUBLICATION_PHASE_MAP.md`](docs/PUBLICATION_PHASE_MAP.md) | Operational publication sequencing |
| [`publication/`](publication/README.md) | Submitted packages and publication controls |
| [`tracker/PUBLICATION_STATE.csv`](tracker/PUBLICATION_STATE.csv) | Machine-readable publication state |
| [`tracker/RESEARCH_TRACKER.md`](tracker/RESEARCH_TRACKER.md) | Narrative research-program state |
| [`analysis/`](analysis/README.md) | Study-1 statistical reconstruction and validation |
| [`docs/`](docs/) | Theory, methods, governance, provenance, and publication closeouts |
| [`configs/`](configs/) | Frozen experiment designs, schemas, adapters, and toolchain locks |
| [`tests/`](tests/) | Unit, contract, regression, and governance tests |
| [`scripts/`](scripts/) | Validation, audit, runtime, campaign, and release tooling |

## Safe validation

Normal repository validation must not rerun frozen canonical campaigns or rewrite frozen statistical outputs.

Every future publisher submission requires a separate explicit final author authorization.
