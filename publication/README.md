# Publication Package

This directory is the human-facing publication layer for two deliberately separate publication streams:

1. the **submitted Study-1/Study-2 journal article**, which reports two separately frozen empirical studies; and
2. the **Study-8 companion paper**, a separately frozen deterministic modeled study under [`study8/`](study8/README.md).

The streams must not be silently pooled or merged into one statistical population or one manuscript.

## 1. Submitted Study-1/Study-2 journal article

The target-neutral manuscript components remain retained as publication-development provenance:

1. [`manuscript/00-title-abstract.md`](manuscript/00-title-abstract.md) - combined title, abstract, keywords, running-title candidate
2. [`manuscript/01-introduction.md`](manuscript/01-introduction.md) - two-study problem framing, contributions, and scope
3. [`manuscript/02-background-and-related-work.md`](manuscript/02-background-and-related-work.md) - related literature and novelty boundary
4. [`manuscript/03-methods.md`](manuscript/03-methods.md) - frozen Study-1 methods and provenance
5. [`manuscript/03-study2-methods-extension.md`](manuscript/03-study2-methods-extension.md) - separately frozen Study-2 design, runtime/evidence boundary, endpoints, analysis, and bounded pre-runtime formal/security assurance
6. [`manuscript/04-results.md`](manuscript/04-results.md) - frozen Study-1 results
7. [`manuscript/04-study2-results-extension.md`](manuscript/04-study2-results-extension.md) - frozen Study-2 RQ1-RQ5 results and interpretation limits
8. [`manuscript/05-discussion.md`](manuscript/05-discussion.md) - cross-study interpretation, limitations, and implications
9. [`manuscript/06-conclusion.md`](manuscript/06-conclusion.md) - combined bounded conclusions and remaining research path
10. [`manuscript/07-declarations-and-availability.md`](manuscript/07-declarations-and-availability.md) - ethics, responsible-research boundary, data/code availability, funding, and declarations

Historical assembly controls remain under `publication/manuscript/`, including claim traceability, citation readiness, and submission-input records.

### Current Paper-1 authority

Paper 1 was submitted to the **AIAA Journal of Aerospace Information Systems (JAIS)** on **2026-09-05**.

- manuscript title: **Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints**
- ScholarOne manuscript type: Full Paper
- manuscript ID: `2026-09-I012066`
- publisher state: `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`
- co-authors: none
- final ScholarOne proof: 26 pages total, one ScholarOne cover sheet plus the 25-page manuscript
- final ScholarOne proof SHA-256: `47fc96b00ef7a3c7ac280a71b1397320f5b10ef75412805c8f76c6d0dbf63888`

The canonical publisher-facing and post-submission source of truth is:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Use that directory for the submitted manuscript, cover letter, final ScholarOne values, compliance checklist, file hashes, proof-QA record, submission authorization, confirmation, and confirmation-email record.

Historical Computers & Security and JAIS preparation directories under `publication/submission/` are retained as provenance. They do not supersede the canonical submitted-state package.

Study 1 and Study 2 remain frozen and separate. Do not modify the submitted manuscript, scientific populations, exclusions, statistical results, or publisher-facing package unless JAIS explicitly requests a revision.

## 2. Study-8 companion paper - frozen and merged publication package

Study 8 (`S8-PQC-ICR-001`) remains outside the Study-1/Study-2 JAIS manuscript. Its dedicated companion-paper package has been developed, adversarially reviewed, hash-frozen, and merged under [`study8/`](study8/README.md).

Current Study-8 publication-package state:

- status: `PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`
- publication-package PR: `#92`
- final reviewed head: `75c98356751087dd648684ade7cb973c166cbce0`
- frozen-package commit: `cbad15227bf99d1b7b19d95b0581196d78208f95`
- squash merge commit on `main`: `87bcec000d278aeffef1222ce814098c93ada362`
- post-merge Study-8 results-freeze CI: `33781901833` - `SUCCESS`
- post-merge repository CI: `33781901724` - `SUCCESS`
- current status authority: [`study8/PUBLICATION_DEVELOPMENT_STATUS.json`](study8/PUBLICATION_DEVELOPMENT_STATUS.json)
- frozen-package manifest: [`study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`](study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json)

The Study-8 package did **not** alter the Study-1/Study-2 manuscript and did not rerun or modify Study-8 science.

The next authorized Study-8 work is a **live venue review**. After the author approves a target venue, a separate venue-specific publisher projection may be prepared from the frozen Study-8 publication package. Actual publisher submission and publisher-portal action remain later explicit authorization gates.

## 3. Frozen study boundaries

### Study 1

- 24 frozen cells x 30 repetitions
- 720 VALID statistical observations
- 9 retained INVALID attempts outside statistical membership
- 696-observation final-commit complete-block analysis is sensitivity only
- DOI-bearing public evidence-of-record: Zenodo v1.0.0, `10.5281/zenodo.22181540`

### Study 2

- 85 frozen cells
- 3,872 VALID observations
- 0 INVALID attempts
- 162 primary paired contrasts
- 432 prespecified secondary contrasts
- Phase-7 independent reproduction: 0 mismatches
- canonical freeze: `study2/PHASE7_RESULTS_FREEZE.json`
- canonical provenance: `study2/PHASE7_PROVENANCE.json`
- Phase-7 result ZIP retained durably in Git history
- exact Phase-6 source ZIP passed responsible-release review and is publicly archived as Zenodo v1.0.0
- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public ZIP SHA-256 independently verified as `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- release/publication verification authority: `study2/release/phase6/ZENODO_PUBLICATION_VERIFICATION.json`

The two empirical statistical populations are **not pooled**. Study 2 is a separately frozen empirical extension and does not change Study-1 observations, statistical estimates, or historical Zenodo v1.0.0.

### Study 8 - separate companion study

Study 8 is a complete deterministic finite modeled population, not a third empirical population in Paper 1:

- 3,456 canonical modeled observations;
- 3,456 independent implementation-level recomputations;
- 0 row mismatches;
- all four policies: `635/864` trusted-recovery success;
- prespecified `P3 - P1`: `0/1` (`0.000000` percentage points);
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`;
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`.

Its dedicated publication displays, manuscript, bibliography, and claim traceability are under [`study8/`](study8/README.md). Those files preserve the finite-model/no-operational-performance claim boundary.

## 4. Main publication displays

### Study-1 frozen displays

1. [`tables/table-r1-proposition-summary.csv`](tables/table-r1-proposition-summary.csv)
2. [`tables/table-r2-p2-contact-effects.csv`](tables/table-r2-p2-contact-effects.csv)
3. [`tables/table-r3-p3-p4-evidence-pathways.csv`](tables/table-r3-p3-p4-evidence-pathways.csv)
4. [`tables/table-r4-p5-pareto-status.csv`](tables/table-r4-p5-pareto-status.csv)
5. [`tables/table-r5-cybersecurity-positioning.csv`](tables/table-r5-cybersecurity-positioning.csv)
6. [`tables/table-r6-security-property-mapping.csv`](tables/table-r6-security-property-mapping.csv)
7. [`tables/table-s1-execution-provenance-sensitivity.csv`](tables/table-s1-execution-provenance-sensitivity.csv)

Tracked Study-1 figures remain under [`figures/`](figures/).

### Study-2 journal displays

- [`tables/table-r7-study2-prespecified-findings.csv`](tables/table-r7-study2-prespecified-findings.csv) - compact RQ1-RQ5 evidence summary
- [`tables/table-s2-study2-secondary-holm.csv`](tables/table-s2-study2-secondary-holm.csv) - prespecified secondary-family Holm counts
- [`tables/table-s3-study2-formal-assurance.csv`](tables/table-s3-study2-formal-assurance.csv) - pre-runtime TLA+/implementation assurance summary with explicit interpretation limits
- [`tables/table-s4-sparta-v4.0.1-crosswalk.csv`](tables/table-s4-sparta-v4.0.1-crosswalk.csv) - publication-current SPARTA v4.0.1 behavioral/traceability crosswalk

R7/S2 summarize the frozen Phase-7 empirical/statistical record. S3 summarizes pre-runtime assurance that already existed before campaign execution. S4 is taxonomy/positioning traceability. None replaces the authoritative machine-readable results/provenance under `../study2/` or expands the frozen experimental scope.

The detailed SPARTA mapping rules and non-claims are recorded in [`../docs/49-sparta-v4.0.1-research-traceability.md`](../docs/49-sparta-v4.0.1-research-traceability.md).

### Study-8 companion displays

The hash-frozen Study-8 package contains four tables and two SVG figures under [`study8/tables/`](study8/tables/) and [`study8/figures/`](study8/figures/). They are projections of frozen Study-8 findings and do not replace or modify the authoritative records under `../study8/analysis/` and `../study8/results/`.

## 5. Data and reproducibility status

**Study 1:** the public source-evidence archive is Zenodo v1.0.0, version DOI `10.5281/zenodo.22181540`, concept DOI `10.5281/zenodo.22181539`.

**Study 2:** the exact Phase-7 statistical result ZIP is durably retained in repository history with SHA-256 `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`. The underlying Phase-6 source ZIP is cryptographically bound, responsible-release reviewed, and now publicly archived on Zenodo as version DOI `10.5281/zenodo.22289114` / concept DOI `10.5281/zenodo.22289113`. The publicly served source ZIP was independently re-downloaded and its SHA-256 exactly matched `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`.

**Study 8:** canonical/statistical evidence and the companion publication package are independently hash-frozen in Git. Use `../study8/analysis/RESULTS_FREEZE_MANIFEST.json`, `../study8/STUDY8_TECHNICAL_CLOSE.json`, and [`study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`](study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json). Study 8 has no DOI/publication identity yet, and one must not be invented before an actual release/publication gate.

See [`../docs/REPRODUCIBILITY_GUIDE.md`](../docs/REPRODUCIBILITY_GUIDE.md) for the distinction between Study-1 reproduction, Study-2 independent audit, safe Study-8 frozen-result/publication-package verification, general repository validation, and any future new replication.

## 6. Interpretation boundaries

Any reuse or export of the submitted Study-1/Study-2 journal article must preserve all of the following:

- Study 1 = exactly 720 VALID observations; Study 2 = exactly 3,872 VALID observations; never report a pooled statistical population.
- Study-1 P1 remains unsupported on its predeclared primary outcomes.
- Study-1 C1 timing is modeled contact, not operational ground-contact timing.
- Study-1 T1 is omission/reduction of selected policy-visible evidence, not stale/contradictory/forged evidence.
- Study-1 P7 is deterministic rule-based, not AI/ML.
- Study-2 V5 shows that evidence can remain policy-qualified while being false relative to the research-only adjudication truth under the bounded compromise model.
- Study-2 Block-C BENIGN/ADVERSARIAL contrasts are a structural label-invariance/control result only; they do not establish empirical benign-versus-adversarial causal discrimination.
- Study-2 K4 is separate intermittent/flapping contact, not ordinal severity 4.
- Study-2 A2/K2 is a coupled producer-compromise/contact-loss profile.
- Study-2 secondary n=32 blocks are estimation/sensitivity evidence, not prospectively powered small-effect confirmatory evidence.
- SPARTA v4.0.1 mappings are behavioral/taxonomy correspondence only; A0-A3 and K0-K4 are not SPARTA techniques and no compliance claim is supported.
- No weighted global score, global policy rank, operational spacecraft claim, RF claim, real-link latency claim, flightworthiness claim, or certification claim is supported.
- Study-8 results remain outside this two-study article.

The Study-8 companion package must additionally preserve:

- `P3 - P1 = 0/1` as the frozen negative primary result;
- the 3,456 positions as a complete deterministic finite factorial population, not a sample;
- no sampling p-values or sampling confidence intervals;
- logical slots as model indices rather than operational time;
- standardized ML-KEM/ML-DSA object bytes as modeled byte burden rather than measured onboard execution performance;
- same-repository independently written reproduction is not external empirical replication.

## 7. Submission packages

### Paper 1

The canonical submitted package is:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Paper 1 is already submitted to JAIS as manuscript `2026-09-I012066`. The older `submission/computers-and-security/` and `submission/journal-of-aerospace-information-systems/` directories are historical preparation/provenance records and tooling. They must not be treated as the current publisher state.

### Study 8

Do **not** reuse any Paper-1 submission package for Study 8. Study 8 has a dedicated frozen companion-paper package under [`study8/`](study8/README.md).

The current Study-8 gate is live venue selection. After venue approval, prepare a separate venue-specific submission package from the frozen Study-8 publication package. Publisher submission and publisher-portal action remain separately gated and require later explicit author authorization.
