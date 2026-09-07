# Current Publication State

**Current-state date:** 2026-09-07

This is the canonical cross-publication handoff for the `mission-aware-satellite-cyber-recovery` repository. Read this file before using older preparation, freeze, handoff, venue-fit, compression, submission-control, or work-package records.

Historical records retain the stage-local wording that was true when they were created. They are provenance and must not be rewritten merely to look current. Current-state documents, however, must reflect the actual repository and publisher state.

## Current publication portfolio

The repository currently has three submitted publication lines. No unsent manuscript is presently venue-locked as the next publication.

### Paper 1 - Studies 1 + 2

**Journal:** AIAA Journal of Aerospace Information Systems  
**Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints  
**Manuscript ID:** `2026-09-I012066`  
**Submission date:** 2026-09-05  
**State:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study 1 and Study 2 remain separately frozen and are not pooled into one statistical population. No publisher-facing file or frozen scientific result may change unless JAIS explicitly requests a revision.

### Paper 4 - Study 8

**Journal:** Acta Astronautica  
**Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems  
**Manuscript ID:** `AA-D-26-02872`  
**Article type:** Research paper  
**Submission date:** 2026-09-06  
**Current status:** `With Editor`

Canonical submitted-state authority:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Machine-readable publisher state:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Exact submitted package freeze:

`S8-ACTA-PKGFREEZE-002`

Study 8 remains a complete deterministic finite modeled population of 3,456 positions. The frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. No scientific reexecution or statistical reanalysis is authorized while the submission is active.

### Paper 2 - Studies 3 + 4 + 6

**Journal:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Article type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance  
**Submission date:** 2026-09-07  
**Research Exchange submission UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`  
**Formal TAES manuscript ID:** pending / not yet present in the captured post-submission state  
**State:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`

Canonical submitted-state package:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

Current machine-readable authority:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_PACKAGE_STATUS.json`

Initial-submission record:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_INITIAL_SUBMISSION_RECORD_2026-09-07.md`

Exact reviewer PDF:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_REVIEWER_PDF_INITIAL_SUBMISSION_2026-09-07.pdf`

Reviewer PDF SHA-256:

`34c4691381fe521bbd161f34878a33c82799abae18bd62dafab5ac7b2e05327c`

Initial-submission record SHA-256:

`3a23567db6c68d4e7541b9d7cfa65acda6f6c4e0f980ca67d7b06c669d7b346d`

Paper 2 remains limited to three separately frozen populations:

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories.
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations.
- Study 6 / `S6-SCTR-001`: 420 exact observations.

These populations must not be pooled into one Paper-2 sample size, success rate, confidence interval, p-value, or global ranking.

The abandoned `paper2/taes-10-page-compression` branch is explicitly `SUPERSEDED_UNSUBMITTED__R10_INITIAL_SUBMISSION_COMPLETED_2026-09-07`. It is historical development provenance only and is not the reviewer-facing submission.

No Paper-2 manuscript, frozen result, submission artifact, or reviewer-facing file may change unless TAES requests a revision.

## Next independent publication work

There is no currently authorized Paper-3 venue package or manuscript branch.

The next publication action is a **read-only candidate audit** over the remaining eligible research lines. The audit must not assume in advance that a particular study is the next paper.

Known remaining candidates include:

- Study 7 / `S7-LSO-001`, a separately frozen learned-selector study;
- Study 5 / `S5-CUCD-001`, a deferred portability/external-validity boundary study;
- any other repository study or experiment that is demonstrably complete, publication-independent, and not already consumed by Papers 1, 2, or 4.

The next-paper audit must verify scientific coherence, novelty, reproducibility, overlap risk, venue fit, and publication independence before creating a new development branch.

Studies already consumed by submitted papers may be cited as background where appropriate, but must not be silently reused as new experimental evidence.

## Historical work-package register

`tracker/work_packages.csv` is intentionally the historical Study-1 WP0-WP11 register. It is not a live publication-level state machine and must not be expanded by rewriting the closed Study-1 work-package history.

Current publication-level state is tracked separately in:

`tracker/PUBLICATION_STATE.csv`

and narratively in:

`tracker/RESEARCH_TRACKER.md`

## Authority hierarchy

When current-state documents disagree, use this order:

1. per-study scientific freeze/provenance records for scientific facts;
2. exact submitted-state package and publisher-status record for an already submitted paper;
3. this `docs/CURRENT_PUBLICATION_STATE.md` cross-publication handoff;
4. `tracker/PUBLICATION_STATE.csv` for machine-readable publication state;
5. `tracker/RESEARCH_TRACKER.md` for narrative program tracking;
6. `docs/PUBLICATION_PHASE_MAP.md` for operational sequencing;
7. `publication/README.md` for the human-facing publication index;
8. historical preparation, venue-fit, authorization, compression, freeze, work-package, and handoff records.

Historical records may contain superseded status wording by design. Their historical wording is not a current-state contradiction when a newer authority is explicitly identified.

## Global safeguards

- Never silently pool separately frozen populations.
- Never rerun a frozen study merely to obtain a more publishable result.
- Never modify submitted publisher-facing files unless the journal requests a revision.
- Never convert logical model time into operational spacecraft time without new evidence.
- Never infer RF, flight, CPU, energy, ground-station, certification, or operational performance from modeled quantities.
- Same-repository independently written reproduction is reproducibility, not external empirical replication.
- Every future publisher submission requires separate explicit final author authorization.
- Before the next publication branch is created, verify `main` is clean and perform the candidate audit read-only.
