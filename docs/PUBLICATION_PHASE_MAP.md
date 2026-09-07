# Publication Phase Map

**Current-state reference:** 2026-09-07

This document is the operational publication-order reference for the `mission-aware-satellite-cyber-recovery` research program. It summarizes how separately frozen studies are grouped into publication units and which publication work should happen next.

This is a publication/governance document only. It does not change any frozen design, observation, analysis, statistical result, evidence identity, claim boundary, package freeze, or submitted publisher file.

For the canonical cross-publication state, read [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md) first.

## Scope boundary

This map applies only to this repository and its Studies 1-8. Related repositories remain separate research workstreams and are not pooled into this program.

## Overall publication-phase map

```text
MISSION-AWARE SATELLITE CYBER RECOVERY PROGRAM
|
+-- PUBLICATION PHASE 1 - COMPLETE AT SUBMISSION GATE
|   |
|   +-- PAPER 1
|       +-- Study 1
|       +-- Study 2
|       Journal: AIAA Journal of Aerospace Information Systems
|       Manuscript ID: 2026-09-I012066
|       Submitted: 2026-09-05
|       State: editorial/peer-review workflow pending
|
+-- PUBLICATION PHASE 2 - COMPLETE AT SUBMISSION GATE
|   |
|   +-- ROADMAP PAPER 4
|       +-- Study 8 / S8-PQC-ICR-001
|       Journal: Acta Astronautica
|       Manuscript ID: AA-D-26-02872
|       Submitted: 2026-09-06
|       State: With Editor
|
+-- PUBLICATION PHASE 3 - COMPLETE AT SUBMISSION GATE
|   |
|   +-- PAPER 2
|       +-- Study 3 / S3-K4E-001
|       +-- Study 4 / S4-MPQ-001
|       +-- Study 6 / S6-SCTR-001
|       Journal: IEEE Transactions on Aerospace and Electronic Systems
|       Article type: Regular Paper
|       Submitted: 2026-09-07
|       Research Exchange UUID: cd1dfa89-4a24-4451-bdd4-af31ce3367f4
|       State: R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING
|
+-- PUBLICATION PHASE 4 - NEXT ACTIVE GATE
    |
    +-- REMAINING-CANDIDATE AUDIT
        +-- Study 7 / S7-LSO-001
        +-- Study 5 / S5-CUCD-001
        +-- any other still-eligible repository study not consumed by Papers 1, 2, or 4
        State: READ_ONLY_CANDIDATE_SELECTION_REQUIRED
        Next gate: evidence-first candidate matrix + novelty/overlap + live venue review
```

## Publication Phase 1 - Paper 1: Studies 1 + 2

Paper 1 combines two separately frozen empirical studies without pooling their statistical populations.

- Study 1: 720 VALID observations across 24 frozen cells.
- Study 2: `S2-AEATR-001`, 3,872 VALID observations across 85 cells, 0 INVALID attempts, 162 primary paired contrasts, 432 prespecified secondary contrasts, and independent reproduction with 0 mismatches.

**Submitted venue:** AIAA Journal of Aerospace Information Systems.

- title: **Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints**
- manuscript ID: `2026-09-I012066`
- submission date: `2026-09-05`
- state: `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

No Study-1 or Study-2 scientific execution, statistical revision, manuscript modification, or publisher-package modification is authorized unless JAIS explicitly requests a revision.

## Publication Phase 2 - Roadmap Paper 4: Study 8

Study 8 is a separate deterministic modeled study and is not a third statistical population in Paper 1.

- experiment: `S8-PQC-ICR-001`
- canonical modeled positions: 3,456
- same-repository independently written reproduction: 3,456/3,456 exact row matches, 0 mismatches
- prespecified primary contrast `P3 - P1`: exactly `0/1 = 0.000000 percentage points`

**Submitted venue:** Acta Astronautica.

- title: **Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems**
- manuscript ID: `AA-D-26-02872`
- submission date: `2026-09-06`
- current publisher status: `With Editor`

No Study-8 scientific or publisher-facing artifact should change unless Acta explicitly requests a revision.

## Publication Phase 3 - Paper 2: Studies 3 + 4 + 6

Paper 2 is complete at the initial-submission gate.

**Submitted venue:** IEEE Transactions on Aerospace and Electronic Systems.

- title: **Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance**
- article type: Regular Paper
- primary Technical Area: Aerospace Information Systems
- submission date: `2026-09-07`
- Research Exchange submission UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- formal TAES manuscript ID: pending / not yet shown in the captured post-submission state
- submission revision: R10
- state: `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`

The frozen scientific populations remain separate:

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories.
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations.
- Study 6 / `S6-SCTR-001`: 420 exact observations.

There is no pooled Paper-2 statistical population.

The historical 10-page short-track alternative was not submitted and is explicitly superseded. It remains provenance only.

No Paper-2 study result, manuscript, exact reviewer PDF, or publisher-facing submission artifact should change unless TAES explicitly requests a revision.

## Publication Phase 4 - Remaining-candidate audit

The next publication is not preselected by this phase map.

Before creating a new manuscript or venue branch, perform a read-only candidate audit over every remaining eligible study or experiment.

At minimum, evaluate:

### Study 7 / S7-LSO-001

Study 7 remains scientifically separate because learned selectors are a materially different mechanism from the deterministic selectors evaluated in earlier work.

Frozen population: 1,033 observations.

Historical working theme:

**Observability limits of learned recovery selectors under trusted-producer compromise.**

This is a candidate, not an automatic next paper. A fresh AI/autonomy literature review, novelty audit, overlap analysis, claim-boundary review, and live venue review are required.

### Study 5 / S5-CUCD-001

Study 5 remains a portability/external-validity boundary study. It is not a detector-performance experiment and was not part of Paper 2.

Its final publication vehicle remains deferred. It may support a focused validation/reproducibility vehicle or another scientifically justified publication structure, but only after fresh candidate comparison.

Do not claim IDS accuracy, recall, false-positive rate, or packet-level recovery-policy effectiveness from Study 5 because those outcomes were not measured.

### Other remaining studies

Any other repository study may enter the candidate audit only if it is demonstrably complete, provenance-bound, scientifically independent of the three submitted publication lines, and not already consumed as experimental evidence.

## Recommended operational order from 2026-09-07

1. Keep Paper 1 frozen while JAIS review proceeds.
2. Keep Roadmap Paper 4 / Study 8 frozen while Acta review proceeds.
3. Keep Paper 2 R10 frozen while TAES editorial processing proceeds.
4. Start the next publication with a read-only repository and study-candidate audit from clean `main`.
5. Rank remaining candidates by scientific coherence, novelty, evidence strength, reproducibility, publication independence, reviewer risk, and live venue fit.
6. Create a new publication branch only after the candidate and publication boundary are explicitly selected.
7. Keep actual publisher submission as a separate explicit authorization gate.

## Governance rules

- Never pool separately frozen study populations unless a new prospectively authorized analysis explicitly permits it.
- Never rerun or enlarge a frozen study merely to improve publication optics or venue fit.
- Preserve negative, null, conditional, and structural findings.
- Submitted packages are immutable unless the journal requests revision.
- Historical freeze, compression, handoff, and work-package documents retain stage-local wording and are not rewritten to appear current.
- Current-state documents must identify the actual live/submitted package and must be reconciled after each submission gate.
- New orbital, HIL, operator, RF, spacecraft-performance, CPU, energy, or flight-validation claims require separately designed and frozen evidence.

## Quick reference

| Phase | Publication unit | Studies | Current venue/state | Next gate |
|---|---|---|---|---|
| 1 | Paper 1 | Study 1 + Study 2 | JAIS `2026-09-I012066`, submitted | Editorial/peer review; revise only if requested |
| 2 | Roadmap Paper 4 | Study 8 | Acta `AA-D-26-02872`, `With Editor` | Editorial/peer review; revise only if requested |
| 3 | Paper 2 | Studies 3 + 4 + 6 | TAES, R10 submitted 2026-09-07 | Editorial processing; revise only if requested |
| 4 | Next independent candidate | Remaining eligible studies | Not venue-locked | Read-only candidate audit and live venue review |
