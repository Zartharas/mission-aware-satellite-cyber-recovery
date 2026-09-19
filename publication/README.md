# Publication Package

This directory is the human-facing publication layer for the `mission-aware-satellite-cyber-recovery` research program.

For canonical current state, read [`../docs/CURRENT_PUBLICATION_STATE.md`](../docs/CURRENT_PUBLICATION_STATE.md) first.

The repository contains **four publication lines that have been submitted**. Papers 1, 2, and 3 remain active with their publishers. Paper 4 / Study 8 was rejected by Acta Astronautica and is frozen pending a controlled retargeting audit.

1. **Paper 1:** Studies 1 + 2, submitted to AIAA Journal of Aerospace Information Systems.
2. **Paper 4:** Study 8, submitted to Acta Astronautica.
3. **Paper 2:** Studies 3 + 4 + 6, submitted to IEEE Transactions on Aerospace and Electronic Systems.
4. **Paper 3:** Study 7, submitted to CEAS Space Journal.

Separately frozen study populations must never be silently pooled or reused as new evidence merely because they remain in the repository.

## Paper 1 - Studies 1 + 2

- **Journal:** AIAA Journal of Aerospace Information Systems
- **Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints
- **Manuscript ID:** `2026-09-I012066`
- **Submission date:** 2026-09-05
- **Current state:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`
- **Package:** `publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study 1 remains 720 VALID observations and Study 2 remains 3,872 VALID observations. They are separate populations.

## Paper 4 - Study 8

- **Journal:** Acta Astronautica
- **Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems
- **Manuscript ID:** `AA-D-26-02872`
- **Submission date:** 2026-09-06
- **Current state:** `REJECTED__EDITORIAL_DECISION`
- **Decision recorded:** 2026-09-19
- **Authority:** `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Study 8 remains a separate deterministic modeled population of 3,456 positions. Its frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. Acta supplied no external reviewer reports and did not enumerate a specific methodological defect in the decision letter.

## Paper 2 - Studies 3 + 4 + 6

- **Journal:** IEEE Transactions on Aerospace and Electronic Systems
- **Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance
- **Article type:** Regular Paper
- **Submission date:** 2026-09-07
- **Research Exchange UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- **Current state:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`
- **Package:** `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

Paper 2 uses Studies 3, 4, and 6 only and keeps their frozen populations separate.

## Paper 3 - Study 7

- **Journal:** CEAS Space Journal
- **Title:** Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence
- **Article type:** Research
- **Topic:** Artificial Intelligence in Space
- **Submission ID:** `6db04a31-8223-4aaf-af02-e4bafe06ef89`
- **Submission version:** `v.1.0`
- **Submission date:** 2026-09-13
- **Current state:** `SUBMITTED__TECHNICAL_CHECK`
- **Current authority:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- **Initial-submission record:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_INITIAL_SUBMISSION_RECORD_2026-09-13.md`
- **Current README:** `publication/Paper_3_Study_7/CEAS_Space_Journal/README_CURRENT.md`

Paper 3 uses Study 7 only. Study 7 remains exactly 1,033 modeled observations.

Durable evidence:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

The older `publication/Paper_3_Study_7/Journal_of_Aerospace_Information_Systems/` directory is retained only as historical, unsubmitted venue-development provenance. It is superseded by the CEAS package.

## Study 8 post-rejection gate

Study 8 may now undergo a controlled forensic manuscript/venue audit. The rejected Acta package remains immutable provenance. A retargeted package may improve presentation, framing, literature positioning, and venue formatting without changing frozen science. No fallback venue is automatically selected.

## Next independent publication work

Paper 3 and Study 7 are no longer candidates. They are consumed by the submitted CEAS publication line.

The next action is a read-only audit over the remaining eligible work, including Study 5 / `S5-CUCD-001` and any other complete repository experiment not already consumed by Papers 1, 2, 3, or 4.

No next venue or manuscript package is currently locked. Fresh novelty, overlap, reproducibility, claim-boundary, and live-venue review are required before a new publication branch is created.

## Current-state authority order

1. per-study scientific freeze/provenance records;
2. exact submitted-state package and publisher-status record for a submitted paper;
3. `docs/CURRENT_PUBLICATION_STATE.md`;
4. `tracker/PUBLICATION_STATE.csv`;
5. `tracker/RESEARCH_TRACKER.md`;
6. `docs/PUBLICATION_PHASE_MAP.md`;
7. this publication index;
8. historical preparation, venue-fit, freeze, authorization, work-package, and handoff records.

`tracker/work_packages.csv` remains the historical Study-1 WP0-WP11 register and is not the live publication-level state machine.

Every future publisher submission requires a separate explicit final author authorization.
