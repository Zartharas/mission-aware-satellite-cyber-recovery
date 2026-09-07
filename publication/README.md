# Publication Package

This directory is the human-facing publication layer for the `mission-aware-satellite-cyber-recovery` research program.

For the current cross-publication state, read [`../docs/CURRENT_PUBLICATION_STATE.md`](../docs/CURRENT_PUBLICATION_STATE.md) first.

The repository currently contains three submitted publication lines and separately frozen remaining studies for later publication work:

1. **Paper 1:** Studies 1 + 2, submitted to the AIAA Journal of Aerospace Information Systems.
2. **Roadmap Paper 4:** Study 8, submitted to Acta Astronautica.
3. **Paper 2:** Studies 3 + 4 + 6, submitted to IEEE Transactions on Aerospace and Electronic Systems.
4. **Remaining publication candidates:** Study 7, deferred Study 5, and any other repository study not already consumed by a submitted paper, subject to a fresh read-only candidate audit.

Separately frozen study populations must never be silently pooled or reused as new evidence merely because they remain in the repository.

## 1. Paper 1 - Studies 1 + 2

**Journal:** AIAA Journal of Aerospace Information Systems  
**Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints  
**Manuscript type:** Full Paper  
**Manuscript ID:** `2026-09-I012066`  
**Submission date:** 2026-09-05  
**Current state:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

### Study 1 boundary

- 24 frozen cells x 30 valid repetitions.
- 720 VALID statistical observations.
- 9 retained INVALID attempts outside statistical membership.
- 696-observation final-commit complete-block analysis is sensitivity only.
- Zenodo version DOI: `10.5281/zenodo.22181540`.
- concept DOI: `10.5281/zenodo.22181539`.

### Study 2 boundary

- experiment: `S2-AEATR-001`.
- 85 frozen cells.
- 3,872 VALID observations.
- 0 INVALID attempts.
- 162 primary paired contrasts.
- 432 prespecified secondary contrasts.
- independent reproduction: 0 mismatches.
- Zenodo version DOI: `10.5281/zenodo.22289114`.
- concept DOI: `10.5281/zenodo.22289113`.

Study 1 and Study 2 are not pooled into one statistical population. No submitted Paper-1 manuscript or publisher-facing file should change unless JAIS explicitly requests a revision.

## 2. Roadmap Paper 4 - Study 8

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

Study 8 (`S8-PQC-ICR-001`) remains a separate deterministic modeled companion study. Its frozen population is 3,456 positions, and its prespecified primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`.

The submitted publisher-facing package must remain unchanged unless Acta explicitly requests a revision.

## 3. Paper 2 - Studies 3 + 4 + 6

Paper 2 is no longer an unsent development priority. It was submitted to TAES on 2026-09-07 and is now frozen at initial-submission revision R10.

**Journal:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance  
**Manuscript type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Submission date:** 2026-09-07  
**Research Exchange submission UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`  
**Formal TAES manuscript ID:** pending / not yet shown in the captured post-submission state  
**Current state:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`

Canonical submitted-state package:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

Current state authority:

- `TAES_PACKAGE_STATUS.json`
- `TAES_INITIAL_SUBMISSION_RECORD_2026-09-07.md`
- `TAES_REVIEWER_PDF_INITIAL_SUBMISSION_2026-09-07.pdf`

Exact reviewer PDF SHA-256:

`34c4691381fe521bbd161f34878a33c82799abae18bd62dafab5ac7b2e05327c`

Exact normalized initial-submission record SHA-256:

`3a23567db6c68d4e7541b9d7cfa65acda6f6c4e0f980ca67d7b06c669d7b346d`

### Frozen Paper-2 populations

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories.
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations.
- Study 6 / `S6-SCTR-001`: 420 exact observations.

These populations remain separate. There is no scientifically meaningful pooled Paper-2 `N = 6,408`.

Study 5 / `S5-CUCD-001` is not part of Paper 2.

The historical `paper2/taes-10-page-compression` branch is explicitly superseded and unsubmitted. It must not be confused with the actual R10 reviewer-facing package.

No Paper-2 manuscript, study result, submission artifact, or publisher-facing file should change unless TAES explicitly requests a revision.

## 4. Next independent publication work

No next-paper venue or manuscript package is currently locked.

The next action is a read-only publication-candidate audit over remaining eligible studies. The audit must not assume in advance which study or combination should become the next paper.

Known remaining candidates include:

- Study 7 / `S7-LSO-001`, a separately frozen learned-selector study focused on observability limits under trusted-producer compromise;
- Study 5 / `S5-CUCD-001`, a portability/external-validity boundary study whose final publication vehicle remains deferred;
- any other repository study or experiment that is independently complete and not already consumed by Papers 1, 2, or 4.

Before any new publication branch is created, perform fresh literature, novelty, overlap, claim-boundary, reproducibility, and live-venue review.

Do not reuse Papers 1, 2, or 4 study populations as new experimental evidence in the next paper.

## 5. Main publication displays and frozen evidence

Historical display files under `publication/tables/`, `publication/figures/`, `publication/manuscript/`, and `publication/study8/` remain projections of their corresponding frozen evidence. They do not replace per-study machine-readable freeze/provenance records or exact submitted-state packages.

## 6. Interpretation boundaries

Any reuse or revision must preserve the following:

- Study 1 remains exactly 720 VALID observations; Study 2 remains exactly 3,872 VALID observations; never report a pooled Paper-1 statistical population.
- Study-1 P1 remains unsupported on its predeclared primary outcomes.
- Study-1 C1 timing is modeled contact, not operational ground-contact timing.
- Study-1 P7 is deterministic rule-based, not AI/ML.
- Study-2 V5 shows that policy-visible authenticated/current evidence can remain qualified while false relative to research-only adjudication truth under the bounded compromise model.
- Study-2 K4 is intermittent/flapping contact, not ordinal severity 4.
- Study 8 remains outside Paper 1 and its `P3 - P1 = 0/1` negative primary result remains frozen.
- Study 8 is a complete deterministic finite factorial population, not a sample.
- Paper 2 uses Studies 3, 4, and 6 only and keeps their populations separate.
- Only Study 3 directly models intermittent contact in Paper 2.
- Study-4 producer unavailability is not orbital contact loss or mission availability.
- Study-6 assurance-signal unavailability is not contact loss.
- Study-4 provenance domains are synthetic independence classes.
- Study 4 is not a Byzantine-consensus experiment.
- Study 6 is an abstract artifact-trust model, not an operational supply-chain attack experiment.
- Same-repository independently written reproduction is reproducibility, not external empirical replication.
- No weighted global score, global policy rank, operational spacecraft, RF, flightworthiness, CPU, energy, ground-station, or certification claim is supported without new frozen evidence.

## 7. Repository authority for publication work

Use this order when records disagree:

1. per-study scientific freeze/provenance records;
2. exact submitted-state package and publisher-status record for a submitted paper;
3. `docs/CURRENT_PUBLICATION_STATE.md`;
4. `tracker/PUBLICATION_STATE.csv`;
5. `tracker/RESEARCH_TRACKER.md`;
6. `docs/PUBLICATION_PHASE_MAP.md`;
7. this publication index;
8. historical preparation, venue-fit, compression, freeze, authorization, work-package, and handoff records.

`tracker/work_packages.csv` remains the historical Study-1 WP0-WP11 register and is not the live publication-level state machine.

Every future publisher submission requires a separate explicit final author authorization.
