# Publication Phase Map

**Current-state reference:** 2026-09-22

**Paper 4 IJSCCN decision overlay:** 2026-09-24

This document is the operational publication-order reference for the `mission-aware-satellite-cyber-recovery` research program. It is a publication/governance map only and does not alter any frozen study evidence or submitted publisher package.

For canonical current state, read [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md) first.

## Scope boundary

This map applies only to this repository and its Studies 1-8. Unrelated repositories and external research programs remain separate and are not pooled into this publication program.

## Overall publication-phase map

```text
MISSION-AWARE SATELLITE CYBER RECOVERY PROGRAM
|
+-- PHASE 1 - SUBMITTED
|   +-- PAPER 1: Studies 1 + 2
|       Journal: AIAA Journal of Aerospace Information Systems
|       Manuscript ID: 2026-09-I012066
|       Submitted: 2026-09-05
|
+-- PHASE 2 - SUBMITTED
|   +-- PAPER 4: Study 8
|       Journal: Acta Astronautica
|       Manuscript ID: AA-D-26-02872
|       Submitted: 2026-09-06
|       State: Rejected - editorial decision recorded 2026-09-19
|
+-- PHASE 3 - SUBMITTED
|   +-- PAPER 2: Studies 3 + 4 + 6
|       Journal: IEEE Transactions on Aerospace and Electronic Systems
|       Submitted: 2026-09-07
|       Research Exchange UUID: cd1dfa89-4a24-4451-bdd4-af31ce3367f4
|
+-- PHASE 4 - SUBMITTED
|   +-- PAPER 3: Study 7 / S7-LSO-001
|       Journal: CEAS Space Journal
|       Submission ID: 6db04a31-8223-4aaf-af02-e4bafe06ef89
|       Submitted: 2026-09-13
|       State: Rejected - handling-editor decision 2026-09-22
|
+-- PHASE 4R - PAPER 3 RECOVERY
|   +-- PROSPECTIVE EXTENSION DESIGN
|       Proposed experiment: S7E-AERC-001
|       State: PROTOCOL_DRAFT_COMPLETE__AUTHOR_REVIEW_REQUIRED__EXECUTION_NOT_AUTHORIZED
|
+-- PHASE 5 - NEXT ACTIVE GATE
|   +-- PAPER 4 / STUDY 8 + STUDY 8E FRESH VENUE-FIT AUDIT
|       Latest manuscript: IJSCCN 4920969
|       Submitted: 2026-09-22
|       Decision: rejected 2026-09-24 as out of scope; no external review supplied
|       State: IJSCCN_OUT_OF_SCOPE_CLOSEOUT__FRESH_VENUE_FIT_AUDIT
|       Decision record: publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md
|
+-- PHASE 6 - DEFERRED
    +-- REMAINING-CANDIDATE AUDIT
        +-- Study 5 / S5-CUCD-001
        +-- any other still-eligible repository study not consumed by Papers 1, 2, 3, or 4
        State: DEFERRED_WHILE_PAPER4_RETARGET_AUDIT_ACTIVE
```

## Phase 1 - Paper 1

Paper 1 combines Studies 1 and 2 without pooling their statistical populations.

- Study 1: 720 VALID observations across 24 frozen cells.
- Study 2 / `S2-AEATR-001`: 3,872 VALID observations across 85 cells.
- Venue: AIAA Journal of Aerospace Information Systems.
- Manuscript ID: `2026-09-I012066`.
- Submitted: 2026-09-05.

No Paper-1 scientific or publisher-facing artifact should change unless JAIS requests a revision.

## Phase 2 - Paper 4

- Studies: Study 8 / `S8-PQC-ICR-001` plus separately frozen Study 8E / `S8E-ECTV-001`.
- Study 8 population: 3,456 deterministic modeled positions.
- Study 8E authority: `S8E-CANON-RESULTS-002-FREEZE-001`.
- Latest venue: International Journal of Satellite Communications and Networking.
- Manuscript ID: `4920969`.
- Submitted: 2026-09-22.
- Decision date: 2026-09-24.
- Current state: `REJECTED__EDITORIAL_SCREENING__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW`.
- Decision record: `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`.
- Prior Acta manuscript `AA-D-26-02872` remains immutable historical provenance.

The IJSCCN decision supplied no external reviewer reports and identified no specific technical or methodological defect. Study 8 and Study 8E remain separate and unpooled. Neither study should be rerun or reanalyzed merely to improve publication prospects.

## Phase 3 - Paper 2

- Studies: 3, 4, and 6 only.
- Venue: IEEE Transactions on Aerospace and Electronic Systems.
- Submitted: 2026-09-07.
- Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`.
- State: `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`.

The three scientific populations remain separate and there is no pooled Paper-2 sample size.

## Phase 4 - Paper 3

Paper 3 completed its CEAS initial-submission gate and was rejected after handling-editor editorial assessment.

- Study: Study 7 / `S7-LSO-001` only.
- Frozen population: 1,033 exact modeled observations.
- Venue: CEAS Space Journal.
- Title: **Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**.
- Submission ID: `6db04a31-8223-4aaf-af02-e4bafe06ef89`.
- Submitted: 2026-09-13.
- Decision date: 2026-09-22.
- Current state: `REJECTED__EDITORIAL_ASSESSMENT`.
- Current authority: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`.

The handling editor recognized a relevant assurance concern and reproducible setup but identified missing architecture grounding, validated trust assumptions, and an equal-information deterministic corroboration comparator. The rejected CEAS package and frozen Study 7 remain immutable provenance.

## Phase 4R - Paper 3 post-rejection recovery

The author authorized a structured rejection-to-research-requirements audit on 2026-09-22.

- Audit result: `NEW_PROSPECTIVE_EXTENSION_REQUIRED`.
- Proposed experiment: `S7E-AERC-001`.
- Current design state: `PROTOCOL_DRAFT_COMPLETE__AUTHOR_REVIEW_REQUIRED__EXECUTION_NOT_AUTHORIZED`.
- Recovery audit: `publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`.
- Proposal: `publication/Paper_3_Study_7/Post_Rejection_Rebuild/STUDY7E_AERC_PROSPECTIVE_EXTENSION_PROPOSAL_2026-09-22.md`.

No Study-7 rerun, retroactive comparator addition, or Study-7E execution is authorized. Any future Study 7E remains a separate population.

## Paper 4 post-IJSCCN retargeting gate

IJSCCN manuscript `4920969` is closed by editorial scope rejection. No Wiley Transfer Desk recommendation or fallback venue is automatically activated. The exact IJSCCN R5 package remains immutable provenance.

## Phase 5 - Paper 4 / Study 8 + Study 8E fresh venue-fit audit

This is the immediate active Paper-4 publication-development gate.

Decision authority:

`publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

The work begins with a fresh live venue assessment against the actual rebuilt manuscript scope: satellite/space systems, cybersecurity, post-quantum cryptography, trusted recovery/key-state transition, intermittent connectivity, and contact/opportunity modeling. Transfer Desk suggestions may be inspected but do not constitute venue approval.

Study 8 and Study 8E remain separate populations. Paper 5 / Study 9 remains outside this retarget gate. No new target venue is locked. Final venue lock, transfer, and publisher submission remain separate explicit author-approval gates.

## Phase 6 - Remaining-candidate audit

The next independent publication after the active Paper-4 retarget decision is not preselected.

Known remaining work includes Study 5 / `S5-CUCD-001` plus any other repository experiment that is complete, provenance-bound, scientifically independent, and not already consumed by Papers 1, 2, 3, or 4.

The next-paper audit must include fresh literature review, novelty/self-overlap analysis, claim-boundary review, reproducibility review, and live venue review before any new publication branch is created.

Study 5 remains a portability/external-validity boundary study and must not be misrepresented as measuring detector accuracy, recall, false-positive rate, or packet-level recovery effectiveness.

## Recommended operational order from 2026-09-24

1. Keep Papers 1 and 2 frozen while their journal workflows proceed; keep rejected Paper-3 CEAS and Paper-4 Acta/IJSCCN packages frozen as provenance.
2. Review Wiley Transfer Desk suggestions if received, without approving transfer.
3. Perform a fresh live venue-fit review for the rebuilt Study 8 + Study 8E manuscript.
4. Preserve the existing scientific claim boundaries and reject venues that require unsupported operational-performance claims.
5. Present the venue shortlist and adaptation plan before creating a new venue-specific package.
6. Keep any transfer or publisher submission as a separate explicit author-authorization gate.

## Governance rules

- Never pool separately frozen study populations unless a new prospectively authorized analysis explicitly permits it.
- Never rerun or enlarge a frozen study merely to improve publication optics or venue fit.
- Preserve negative, null, conditional, and structural findings.
- Submitted packages are immutable unless the journal requests revision.
- Historical preparation and venue-development records remain provenance and are not rewritten to pretend they were submitted.
- Current-state documents must identify the actual live/submitted package and be reconciled after each submission gate.
- New orbital, HIL, operator, RF, spacecraft-performance, CPU, energy, or certification claims require separately designed and frozen evidence.

## Quick reference

| Phase | Publication unit | Studies | Current venue/state | Next gate |
|---|---|---|---|---|
| 1 | Paper 1 | Studies 1 + 2 | JAIS `2026-09-I012066`, submitted | Wait for journal action |
| 2 | Paper 4 | Study 8 + Study 8E | IJSCCN `4920969`, rejected 2026-09-24 as out of scope | Fresh venue-fit audit; review Transfer Desk suggestions only as candidates |
| 3 | Paper 2 | Studies 3 + 4 + 6 | TAES, submitted | Wait for journal action |
| 4 | Paper 3 | Study 7 | CEAS `6db04a31-8223-4aaf-af02-e4bafe06ef89`, rejected 2026-09-22 | Preserve rejected package; recovery audit complete |
| 4R | Paper 3 recovery | Study 7 + proposed Study 7E | `S7E-AERC-001` protocol draft complete, not executed | Author review; implementation remains separately gated |
| 5 | Paper 4 retarget | Study 8 + Study 8E | IJSCCN scope rejection; next venue not locked | Live venue-fit audit with no scientific rerun |
| 6 | Next independent candidate | Remaining eligible studies | Deferred while Paper-4 retarget audit is active | Resume read-only candidate audit later |
