# Publication Phase Map

**Current-state reference - 2026-09-06**

This document is the operational publication-order reference for the `mission-aware-satellite-cyber-recovery` research program. It summarizes how separately frozen studies are grouped into publication units and which publication work should happen next.

This is a publication/governance document only. It does **not** change any frozen design, observation, analysis, statistical result, evidence identity, claim boundary, publication-package freeze, or submitted publisher file.

For the canonical cross-publication current state, read [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md) first.

## Scope boundary

This map applies only to the `mission-aware-satellite-cyber-recovery` repository and its Studies 1-8.

The following related projects remain separate workstreams and are not part of this map:

- `verifiable-spacecraft-lifecycle`
- `satcom-ttc-post-compromise-recovery`

No evidence, observations, statistical populations, manuscript results, or publication identities from those repositories are pooled into this research program.

## Authority and terminology

Detailed scientific and publication authority remains governed by:

- per-study frozen provenance/results records;
- submitted-state publisher packages for papers already submitted;
- [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md);
- `tracker/RESEARCH_TRACKER.md`;
- the relevant publication package under `publication/`.

Historical freeze and preparation records retain their stage-local wording and are not rewritten to appear current.

**Publication phase** means the recommended operational order for publication work. It is not the same as roadmap paper numbering. Study 8 remains roadmap **Paper 4**, even though it was operational Publication Phase 2.

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
+-- PUBLICATION PHASE 3 - NEXT ACTIVE DEVELOPMENT PRIORITY
|   |
|   +-- PAPER 2
|       +-- Study 3
|       +-- Study 4
|       +-- Study 6
|       Working theme:
|       evidence-plane trust composition for intermittent-contact trusted recovery
|       Next gate:
|       frozen-state audit + fresh literature/novelty/claim-boundary/live-venue review
|
+-- PUBLICATION PHASE 4
|   |
|   +-- PAPER 3
|       +-- Study 7 / S7-LSO-001
|       Working theme:
|       observability limits of learned recovery selectors under trusted-producer compromise
|       Next gate:
|       fresh AI/autonomy literature + live venue review
|
+-- PUBLICATION PHASE 5
    |
    +-- STUDY 5 / S5-CUCD-001
        Decision pending:
        integrate as a clearly separated portability/external-validity component
        or prepare a focused validation/reproducibility vehicle
```

## Publication Phase 1 - Paper 1: Studies 1 + 2

### Scientific grouping

Paper 1 combines two separately frozen empirical studies in one manuscript without pooling their statistical populations.

- **Study 1:** 720 VALID observations across 24 frozen cells.
- **Study 2:** `S2-AEATR-001`, 3,872 VALID observations across 85 cells, 0 INVALID attempts, 162 primary paired contrasts, 432 prespecified secondary contrasts, and independent reproduction with 0 mismatches.

### Submitted venue

**AIAA Journal of Aerospace Information Systems (JAIS)**

- title: **Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints**
- manuscript type: Full Paper
- manuscript ID: `2026-09-I012066`
- submission date: `2026-09-05`
- publisher state: `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

No Study-1 or Study-2 scientific execution, statistical revision, manuscript modification, or publisher-package modification is authorized unless JAIS explicitly requests a revision.

Study 8 remains excluded from Paper 1.

## Publication Phase 2 - Roadmap Paper 4: Study 8

### Scientific grouping

Study 8 is a separate deterministic modeled study and is not a third statistical population in Paper 1.

- experiment: `S8-PQC-ICR-001`
- canonical modeled positions: 3,456
- same-repository independently written reproduction: 3,456/3,456 exact row matches, 0 mismatches
- prespecified primary contrast `P3 - P1`: exactly `0/1 = 0.000000 percentage points`

### Submitted venue

**Acta Astronautica**

- title: **Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems**
- article type: Research paper
- manuscript ID: `AA-D-26-02872`
- submission date: `2026-09-06`
- current Editorial Manager status: `With Editor`

Canonical submitted-state authority:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Machine-readable publisher status:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Exact submitted package freeze:

`S8-ACTA-PKGFREEZE-002`

Submitted package source commit:

`f5e9a1d4553737e534821bf647463abfd44fa0dd`

The Study-8 science remains frozen. The negative primary policy-success result must not be rescued or reframed as superiority. No publisher-facing file should change unless Acta explicitly requests a revision.

Historical source-package status remains `PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`; that frozen source-package status is not a contradiction with the later publisher submission state.

## Publication Phase 3 - Paper 2: Studies 3 + 4 + 6

### Scientific grouping

This proposed synthesis follows the evidence-plane trust boundary across three separately frozen studies:

1. **Study 3:** persistence/recurrence of false-but-qualified evidence across intermittent-contact transitions.
2. **Study 4:** multi-producer quorum and provenance-diversity tradeoffs.
3. **Study 6:** the recovery artifact itself moves inside the trust boundary and requires qualification.

The populations must remain separate inside the synthesis. They must not be pooled into one global score or statistical population.

### Working theme

**Evidence-plane trust composition for intermittent-contact trusted recovery.**

### Required opening audit

Before drafting a manuscript:

1. verify the frozen design, evidence, results, and provenance for Studies 3, 4, and 6 separately;
2. identify all null, negative, conditional, structural-zero, and scope-limiting findings;
3. perform a fresh literature and novelty review using current primary sources;
4. perform a claim-boundary review that distinguishes modeled quantities from spacecraft/RF/operational claims;
5. perform a live venue review before selecting a target;
6. evaluate Study 5 only as a clearly separated portability/external-validity component, not as a silently pooled population;
7. obtain explicit author approval before venue lock or venue-specific package preparation.

### Candidate venues

Historical candidates include:

- IEEE Systems Journal
- Acta Astronautica
- AIAA Journal of Aerospace Information Systems

These are planning inputs only. Recheck live scope, policies, article types, and submission requirements before recommending a venue.

### Current state

Studies 3, 4, and 6 are frozen. Dedicated publication development has not yet been locked to a venue. This is the **next active publication-development priority** after the submitted Paper 1 and Paper 4 packages.

## Publication Phase 4 - Paper 3: Study 7

### Scientific grouping

Study 7 remains separate because machine learning is a materially different scientific mechanism from the deterministic selectors evaluated earlier.

- experiment: `S7-LSO-001`
- frozen population: 1,033 observations

### Working theme

**Observability limits of learned recovery selectors under trusted-producer compromise.**

The defensible contribution is not an ML-superiority claim. The central interpretation is that a learner using only policy-visible information cannot recover hidden truth that is absent from its inputs; independent corroboration helps only when it is actually independent.

### Current state

Study 7 science is frozen. A fresh AI/autonomy literature review, novelty audit, claim-boundary review, and live venue review are required before publication development.

## Publication Phase 5 - Study 5 disposition

### Scientific role

Study 5 is an external-validity/portability boundary study rather than a detector-performance experiment.

Its strongest result is that the evaluated external satellite-cyber dataset broadens scenario/taxonomy coverage but does not directly supply all state variables required for trusted-recovery policy evaluation without fabrication.

### Possible vehicles

**Option A:** integrate Study 5 as a clearly separated external-validity/portability section in an appropriate larger follow-on paper, potentially Paper 2.

**Option B:** prepare a focused validation/reproducibility paper or research note.

### Prohibited interpretation

Do not present Study 5 as measuring IDS accuracy, recall, false-positive rate, or per-packet recovery-policy effectiveness; those outcomes were not measured by the frozen study.

### Current state

The final publication vehicle remains deliberately deferred.

## Recommended operational order from 2026-09-06

1. Keep Paper 1 frozen while JAIS editorial/peer review proceeds.
2. Keep Study 8 / Paper 4 frozen while Acta manuscript `AA-D-26-02872` proceeds through editorial review.
3. Begin Paper 2 with a repository/science audit of Studies 3 + 4 + 6, followed by literature/novelty/claim-boundary/live-venue review.
4. Develop Study 7 only after a fresh AI/autonomy publication review.
5. Decide the Study-5 publication vehicle only after Paper-2 coherence is assessed.

## Governance rules

- Never pool separately frozen study populations unless a new prospectively authorized analysis explicitly permits it.
- Never rerun or enlarge a frozen study merely to improve publication optics or respond to venue preference.
- Preserve negative, null, conditional, and structural findings.
- Treat candidate venues as planning aids until a live venue/policy review is completed and the author explicitly selects a target.
- Publisher submission is a separate explicit authorization gate for every new submission.
- Historical freeze/handoff documents retain their stage-local states and are not rewritten to appear current.
- Historical venue-preparation directories may be retained for provenance, but current-state documents must identify the canonical live or submitted package.
- New orbital, HIL, operator, RF, spacecraft-performance, CPU, energy, or flight-validation claims require separately designed and frozen evidence.

## Quick reference

| Phase | Publication unit | Studies | Current venue/state | Next gate |
|---|---|---|---|---|
| 1 | Paper 1 | Study 1 + Study 2 | JAIS `2026-09-I012066`, submitted | Editorial/peer review; revise only if requested |
| 2 | Roadmap Paper 4 | Study 8 | Acta `AA-D-26-02872`, `With Editor` | Editorial/peer review; revise only if requested |
| 3 | Paper 2 | Studies 3 + 4 + 6 | Venue not locked | Frozen-state + literature/novelty/claim-boundary/live-venue review |
| 4 | Paper 3 | Study 7 | Venue not locked | Fresh AI/autonomy literature + venue review |
| 5 | Study 5 disposition | Study 5 | Deferred | Decide integration vs focused vehicle |
