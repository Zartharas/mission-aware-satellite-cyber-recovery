# Publication Package

This directory is the human-facing publication layer for the `mission-aware-satellite-cyber-recovery` research program.

For canonical current state, read [`../docs/CURRENT_PUBLICATION_STATE.md`](../docs/CURRENT_PUBLICATION_STATE.md) first.

The repository contains **four publication lines that have been submitted**. Papers 1 and 2 remain active with their publishers. Paper 3 was rejected by CEAS Space Journal on 2026-09-22 and has entered a controlled post-rejection research-requirements phase. Paper 4 was first rejected by Acta Astronautica; its rebuilt Study 8 + Study 8E manuscript was then submitted to IJSCCN as manuscript `4920969` and declined at editorial screening on 2026-09-24 as `out of scope`, with no external reviewer reports supplied.

1. **Paper 1:** Studies 1 + 2, submitted to AIAA Journal of Aerospace Information Systems.
2. **Paper 4:** Study 8 + Study 8E rebuilt manuscript, most recently submitted to IJSCCN; prior Acta submission retained as historical provenance.
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
- **Current state:** `Rejected` / `REJECTED__EDITORIAL_DECISION`
- **Decision recorded:** 2026-09-19
- **Authority:** `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Study 8 remains a separate deterministic modeled population of 3,456 positions. Its frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. Acta supplied no external reviewer reports and did not enumerate a specific methodological defect in the decision letter.

### Rebuilt Paper 4 - Study 8 + Study 8E

- **Journal:** International Journal of Satellite Communications and Networking
- **Manuscript ID:** `4920969`
- **Submission date:** 2026-09-22
- **Decision date:** 2026-09-24
- **Current state:** `REJECTED__EDITORIAL_SCREENING__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW`
- **Authority:** `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`
- **Decision record:** `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

The IJSCCN decision does not alter frozen Study 8 or Study 8E science. The submitted R5 package remains immutable historical provenance. The next Paper 4 action is a fresh venue-fit audit plus optional review of Wiley Transfer Desk suggestions; no automatic transfer is authorized.

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
- **Decision date:** 2026-09-22
- **Current state:** `REJECTED__EDITORIAL_ASSESSMENT`
- **Current authority:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- **Decision record:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-09-22.md`
- **Recovery audit:** `publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`

Paper 3's rejected CEAS package used Study 7 only. Study 7 remains exactly 1,033 modeled observations and is immutable.

Durable evidence:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

The rejection audit finds that a manuscript-only retarget is insufficient. A new prospective extension, `S7E-AERC-001`, is proposed to address architecture grounding, trust-domain validation, and equal-information deterministic/learned comparison. It has not been implemented or executed.

The older `publication/Paper_3_Study_7/Journal_of_Aerospace_Information_Systems/` directory remains historical, unsubmitted venue-development provenance.

## Paper 4 post-IJSCCN gate

The immediate active publication-development priority is the Paper 4 post-IJSCCN venue-retarget workstream; it is not a scientific rerun.

The rejected Acta package and rejected IJSCCN R5 package remain immutable historical provenance. A future retarget may adapt presentation, framing, literature positioning, explanatory depth, figures/tables, and venue formatting only within the frozen Study 8 + Study 8E claim boundaries. No Wiley transfer or fallback venue is automatically selected.

Canonical handoff:

`publication/Paper_4_Study_8/POST_REJECTION_RESUBMISSION_HANDOFF_2026-09-19.md`

Paper 4 is the Study 8 publication. Do not confuse it with Study 4 / `S4-MPQ-001`, which is already part of submitted Paper 2 / TAES.

## Deferred independent publication work

Paper 3 recovery is now a separately authorized workstream. Frozen Study 7 remains part of that publication line, and any future Study 7E will be separately designed and unpooled.

The independent remaining-study audit is still separate. When resumed, it includes Study 5 / `S5-CUCD-001` and any other complete repository experiment not already consumed by Papers 1, 2, 3, or 4.

No remaining-study evidence may be imported into Paper 3 merely to answer the CEAS rejection.

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
