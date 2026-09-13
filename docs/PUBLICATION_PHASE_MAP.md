# Publication Phase Map

**Current-state reference:** 2026-09-13

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
|       State: With Editor
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
|       State: Technical check
|
+-- PHASE 5 - NEXT ACTIVE GATE
    +-- REMAINING-CANDIDATE AUDIT
        +-- Study 5 / S5-CUCD-001
        +-- any other still-eligible repository study not consumed by Papers 1, 2, 3, or 4
        State: READ_ONLY_CANDIDATE_SELECTION_REQUIRED
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

- Study: Study 8 / `S8-PQC-ICR-001`.
- Frozen population: 3,456 deterministic modeled positions.
- Venue: Acta Astronautica.
- Manuscript ID: `AA-D-26-02872`.
- Submitted: 2026-09-06.
- Current state: `With Editor`.

No Study-8 scientific or publisher-facing artifact should change unless Acta requests a revision.

## Phase 3 - Paper 2

- Studies: 3, 4, and 6 only.
- Venue: IEEE Transactions on Aerospace and Electronic Systems.
- Submitted: 2026-09-07.
- Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`.
- State: `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`.

The three scientific populations remain separate and there is no pooled Paper-2 sample size.

## Phase 4 - Paper 3

Paper 3 is complete at the initial-submission gate.

- Study: Study 7 / `S7-LSO-001` only.
- Frozen population: 1,033 exact modeled observations.
- Venue: CEAS Space Journal.
- Title: **Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**.
- Article type: Research.
- Topic: Artificial Intelligence in Space.
- Peer review: Single anonymous.
- Submission ID: `6db04a31-8223-4aaf-af02-e4bafe06ef89`.
- Submission version: `v.1.0`.
- Submitted: 2026-09-13.
- Current state: `SUBMITTED__TECHNICAL_CHECK`.
- Current authority: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`.

Zenodo Study-7 evidence:

- version DOI: `10.5281/zenodo.22732060`
- concept DOI: `10.5281/zenodo.22732059`

The historical Paper-3 JAIS folder was not submitted and is superseded venue-development provenance only.

No Paper-3 scientific or publisher-facing artifact should change unless CEAS requests a technical correction or revision.

## Phase 5 - Remaining-candidate audit

The next publication is not preselected.

Known remaining work includes Study 5 / `S5-CUCD-001` plus any other repository experiment that is complete, provenance-bound, scientifically independent, and not already consumed by Papers 1, 2, 3, or 4.

The next-paper audit must include fresh literature review, novelty/self-overlap analysis, claim-boundary review, reproducibility review, and live venue review before any new publication branch is created.

Study 5 remains a portability/external-validity boundary study and must not be misrepresented as measuring detector accuracy, recall, false-positive rate, or packet-level recovery effectiveness.

## Recommended operational order from 2026-09-13

1. Keep Papers 1, 2, 3, and 4 frozen while their journal workflows proceed.
2. Record publisher status changes without modifying submitted scientific packages.
3. Start the next publication only with a read-only audit of remaining eligible studies from clean `main`.
4. Select a candidate publication boundary before creating any new venue branch.
5. Keep actual publisher submission as a separate explicit author-authorization gate.

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
| 2 | Paper 4 | Study 8 | Acta `AA-D-26-02872`, With Editor | Wait for journal action |
| 3 | Paper 2 | Studies 3 + 4 + 6 | TAES, submitted | Wait for journal action |
| 4 | Paper 3 | Study 7 | CEAS `6db04a31-8223-4aaf-af02-e4bafe06ef89`, Technical check | Wait for journal action |
| 5 | Next independent candidate | Remaining eligible studies | Not venue-locked | Read-only candidate audit |
