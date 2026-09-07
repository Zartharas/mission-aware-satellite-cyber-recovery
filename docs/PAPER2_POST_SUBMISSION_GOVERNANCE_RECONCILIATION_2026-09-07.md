# Paper 2 Post-Submission Governance Reconciliation - 2026-09-07

## Purpose

This record closes a cross-repository publication-governance drift identified after Paper 2 was successfully submitted to IEEE Transactions on Aerospace and Electronic Systems.

The TAES venue package itself had already completed its post-submission closeout. The defect was that several repository-level current-state surfaces still described Paper 2 as unsent or under manuscript development.

This was a provenance/governance defect only. No scientific defect was identified.

## Verified submitted Paper-2 state

**Journal:** IEEE Transactions on Aerospace and Electronic Systems  
**Article type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance  
**Submission date:** 2026-09-07  
**Research Exchange submission UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`  
**Submission revision:** R10  
**Current state:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`

Canonical venue-level authority:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_PACKAGE_STATUS.json`

Exact reviewer PDF SHA-256:

`34c4691381fe521bbd161f34878a33c82799abae18bd62dafab5ac7b2e05327c`

Normalized initial-submission record SHA-256:

`3a23567db6c68d4e7541b9d7cfa65acda6f6c4e0f980ca67d7b06c669d7b346d`

## Drift found

At canonical `main` commit `15967a7e4d0539a20093d573c85358f6799f30cd`, the following current-state files still carried pre-submission wording:

- `publication/README.md`
  - described Paper 2 as the current unsent publication-development priority;
  - reported `VENUE_LOCKED__MANUSCRIPT_DEVELOPMENT_IN_PROGRESS__NOT_SUBMITTED`.
- `docs/CURRENT_PUBLICATION_STATE.md`
  - was dated 2026-09-06;
  - described Paper 2 as the next unsent publication work.
- `docs/PUBLICATION_PHASE_MAP.md`
  - still placed Paper 2 in the next-active-development phase and said its venue was not locked.
- `tracker/RESEARCH_TRACKER.md`
  - was dated 2026-09-04 and still described older publication preparation gates.

`tracker/work_packages.csv` was also reviewed. It is intentionally the historical closed Study-1 WP0-WP11 register and is not itself erroneous. The governance gap was the absence of a distinct current publication-level machine-readable tracker.

## Reconciliation applied

The following current-state surfaces were updated on scoped branch:

`paper2-post-submission-governance-reconcile-2026-09-07`

Updated:

- `docs/CURRENT_PUBLICATION_STATE.md`
- `docs/PUBLICATION_PHASE_MAP.md`
- `publication/README.md`
- `tracker/RESEARCH_TRACKER.md`

Added:

- `tracker/PUBLICATION_STATE.csv`
- this reconciliation record

`tracker/work_packages.csv` was deliberately left unchanged because its WP0-WP11 rows are historical Study-1 provenance.

## Current publication-state rule

The repository now distinguishes:

1. historical scientific/work-package provenance;
2. exact submitted-state packages;
3. current cross-publication governance state;
4. machine-readable publication-level tracking.

For current publication state, use:

1. exact submitted package/publisher-status record for the relevant paper;
2. `docs/CURRENT_PUBLICATION_STATE.md`;
3. `tracker/PUBLICATION_STATE.csv`;
4. `tracker/RESEARCH_TRACKER.md`;
5. `docs/PUBLICATION_PHASE_MAP.md`;
6. `publication/README.md`.

Historical work-package, preparation, compression, venue-fit, authorization, and freeze records retain their stage-local wording.

## Scientific preservation

This reconciliation changes no study design, data, population, endpoint, analysis, result, figure, table, manuscript text, submitted publisher file, author metadata, or reviewer-facing artifact.

Paper 2 remains limited to:

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories;
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations;
- Study 6 / `S6-SCTR-001`: 420 exact observations.

The populations remain separate and must not be pooled.

The superseded 10-page short-track branch remains historical and unsubmitted.

## Next gate

The next independent publication begins with a read-only remaining-study candidate audit from clean canonical `main`.

No next-paper venue, study combination, manuscript branch, rerun, or new analysis is authorized by this reconciliation itself.

## Verdict

`PASS_PAPER2_POST_SUBMISSION_CROSS_REPOSITORY_GOVERNANCE_RECONCILIATION`
