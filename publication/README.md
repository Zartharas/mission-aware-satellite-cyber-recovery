# Publication Package

This directory is the human-facing publication layer for the `mission-aware-satellite-cyber-recovery` research program.

For the current cross-publication state, read [`../docs/CURRENT_PUBLICATION_STATE.md`](../docs/CURRENT_PUBLICATION_STATE.md) first.

The repository currently contains two submitted publication lines plus separately frozen studies for later papers:

1. **Paper 1:** Studies 1 + 2, submitted to the AIAA Journal of Aerospace Information Systems.
2. **Roadmap Paper 4:** Study 8, submitted to Acta Astronautica.
3. **Next publication-development priority:** Paper 2, Studies 3 + 4 + 6.
4. **Later:** Paper 3, Study 7, plus the deferred Study-5 publication disposition.

Paper 1 contains **two separately frozen empirical studies**. Study 8 is a separate **companion-paper** line. Separately frozen study populations must never be silently pooled.

## 1. Paper 1 - Studies 1 + 2

Paper 1 reports two separately frozen empirical studies in one manuscript without pooling their statistical populations.

**Journal:** AIAA Journal of Aerospace Information Systems  
**Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints  
**Manuscript type:** Full Paper  
**Manuscript ID:** `2026-09-I012066`  
**Submission date:** 2026-09-05  
**Current state:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

The target-neutral manuscript components remain retained as publication-development provenance under `publication/manuscript/`. In particular, the separately frozen Study-2 integration remains documented in `03-study2-methods-extension.md` and `04-study2-results-extension.md`.

### Study 1 boundary

- 24 frozen cells x 30 valid repetitions
- 720 VALID statistical observations
- 9 retained INVALID attempts outside statistical membership
- 696-observation final-commit complete-block analysis is sensitivity only
- DOI-bearing public evidence-of-record: Zenodo v1.0.0, version DOI `10.5281/zenodo.22181540`
- concept DOI: `10.5281/zenodo.22181539`

### Study 2 boundary

- experiment: `S2-AEATR-001`
- 85 frozen cells
- 3,872 VALID observations
- 0 INVALID attempts
- 162 primary paired contrasts
- 432 prespecified secondary contrasts
- independent reproduction: 0 mismatches
- canonical freeze: `study2/PHASE7_RESULTS_FREEZE.json`
- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public Phase-6 ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- public-byte verified: PASS against the frozen source identity

Study 1 and Study 2 are not pooled into one statistical population. No submitted Paper-1 manuscript or publisher-facing file should change unless JAIS explicitly requests a revision.

## 2. Roadmap Paper 4 - Study 8

Study 8 (`S8-PQC-ICR-001`) remains a separate deterministic modeled companion study and is not a third population in Paper 1.

### Frozen science

- canonical modeled positions: 3,456
- same-repository independently written reproduction: 3,456/3,456 exact row matches, 0 mismatches
- all four policies: `635/864` trusted-recovery success
- prespecified `P3 - P1`: `0/1 = 0.000000 percentage points`
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation-audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`

The target-neutral Study-8 publication source package is hash-frozen under:

`publication/study8/`

Historical source-package state:

`PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`

That status remains correct for the source-package freeze stage and should not be rewritten merely because a later venue-specific submission occurred.

### Acta Astronautica submission

**Journal:** Acta Astronautica  
**Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems  
**Article type:** Research paper  
**Manuscript ID:** `AA-D-26-02872`  
**Submission date:** 2026-09-06  
**Current Editorial Manager status:** `With Editor`

Canonical current-state authority:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Machine-readable publisher state:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Exact submitted package freeze:

`S8-ACTA-PKGFREEZE-002`

Exact submitted-package source commit:

`f5e9a1d4553737e534821bf647463abfd44fa0dd`

The five submitted publisher-facing files remain immutable unless Acta explicitly requests a revision.

Historical Acta preparation files such as `README_SUBMISSION.md`, `ACTA_PACKAGE_STATUS.json`, `SUBMISSION_CHECKLIST.md`, `EDITORIAL_MANAGER_SUBMISSION_VALUES.md`, `UPLOAD_FILES.md`, `SHA256SUMS.txt`, and `ACTA_PACKAGE_FREEZE_MANIFEST.json` intentionally retain their pre-submission freeze-002 wording. They are provenance, not the live publisher-status authority.

## 3. Next publication-development priority - Paper 2

The next unsent publication unit is the proposed synthesis of **Studies 3 + 4 + 6**.

Working theme:

**Evidence-plane trust composition for intermittent-contact trusted recovery.**

The three study populations must remain separate inside the synthesis.

Before manuscript development:

1. verify the frozen design, evidence, results, and provenance for Studies 3, 4, and 6 independently;
2. identify all null, negative, conditional, structural-zero, and scope-limiting findings;
3. perform a fresh literature and novelty review;
4. perform a claim-boundary audit;
5. perform a live venue review before selecting a target;
6. assess Study 5 only as a clearly separated portability/external-validity component;
7. obtain explicit author approval before venue lock or venue-specific package preparation.

Historical venue candidates include IEEE Systems Journal, Acta Astronautica, and AIAA Journal of Aerospace Information Systems. They are not current commitments and must be rechecked live.

## 4. Later publication lines

### Paper 3 - Study 7

Study 7 / `S7-LSO-001` remains a separate frozen publication line because learned selectors represent a materially different mechanism from the deterministic selectors studied earlier.

Working theme:

**Observability limits of learned recovery selectors under trusted-producer compromise.**

Before publication development, perform a fresh AI/autonomy literature review, novelty audit, claim-boundary review, and live venue review. Do not frame the frozen results as generic ML superiority.

### Study 5 disposition

Study 5 / `S5-CUCD-001` is an external-validity/portability boundary study, not a detector-performance experiment.

Possible publication vehicles remain:

- integration as a clearly separated portability/external-validity section in a larger follow-on paper, potentially Paper 2; or
- a focused validation/reproducibility paper or research note.

Do not claim IDS accuracy, recall, false-positive rate, or per-packet recovery-policy effectiveness from Study 5 because those outcomes were not measured.

## 5. Main publication displays

### Study-1 frozen displays

1. `tables/table-r1-proposition-summary.csv`
2. `tables/table-r2-p2-contact-effects.csv`
3. `tables/table-r3-p3-p4-evidence-pathways.csv`
4. `tables/table-r4-p5-pareto-status.csv`
5. `tables/table-r5-cybersecurity-positioning.csv`
6. `tables/table-r6-security-property-mapping.csv`
7. `tables/table-s1-execution-provenance-sensitivity.csv`

Tracked Study-1 figures remain under `figures/`.

### Study-2 journal displays

- `tables/table-r7-study2-prespecified-findings.csv`
- `tables/table-s2-study2-secondary-holm.csv`
- `tables/table-s3-study2-formal-assurance.csv`
- `tables/table-s4-sparta-v4.0.1-crosswalk.csv`

These are publication projections of frozen evidence and do not replace the machine-readable Study-2 source records.

### Study-8 companion displays

The frozen target-neutral Study-8 package contains four tables and two SVG figures under `publication/study8/tables/` and `publication/study8/figures/`. They are projections of frozen Study-8 findings and do not replace the authoritative records under `study8/analysis/` and `study8/results/`.

## 6. Interpretation boundaries

Any reuse or revision must preserve the following:

- Study 1 remains exactly 720 VALID observations; Study 2 remains exactly 3,872 VALID observations; never report a pooled Paper-1 statistical population.
- Study-1 P1 remains unsupported on its predeclared primary outcomes.
- Study-1 C1 timing is modeled contact, not operational ground-contact timing.
- Study-1 T1 is omission/reduction of selected policy-visible evidence, not stale/contradictory/forged evidence.
- Study-1 P7 is deterministic rule-based, not AI/ML.
- Study-2 V5 shows that evidence can remain policy-qualified while being false relative to research-only adjudication truth under the bounded compromise model.
- Study-2 Block-C BENIGN/ADVERSARIAL contrasts are a structural label-invariance/control result only.
- Study-2 K4 is separate intermittent/flapping contact, not ordinal severity 4.
- Study-2 A2/K2 is a coupled producer-compromise/contact-loss profile.
- Study-2 secondary n=32 blocks are estimation/sensitivity evidence, not prospectively powered small-effect confirmatory evidence.
- SPARTA mappings are behavioral/taxonomy correspondence only and do not establish compliance.
- Study 8 remains outside Paper 1.
- Study-8 `P3 - P1 = 0/1` remains the frozen negative primary result.
- Study 8 is a complete deterministic finite factorial population, not a sample.
- Study-8 logical slots are model indices, not operational time.
- Study-8 standardized ML-KEM/ML-DSA object bytes are modeled burden, not measured onboard execution performance.
- Same-repository independently written reproduction is reproducibility, not external empirical replication.
- No weighted global score, global policy rank, operational spacecraft, RF, flightworthiness, CPU, energy, ground-station, or certification claim is supported without new frozen evidence.

## 7. Repository authority for publication work

Use this order when records disagree:

1. per-study scientific freeze/provenance records;
2. exact submitted-state package for an already submitted paper;
3. `docs/CURRENT_PUBLICATION_STATE.md`;
4. `docs/PUBLICATION_PHASE_MAP.md`;
5. this publication index;
6. historical preparation, venue-fit, freeze, authorization, and handoff records.

Every future publisher submission requires a separate explicit final author authorization.
