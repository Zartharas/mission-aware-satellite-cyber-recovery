# Publication Phase Map

**Current-state reference — 2026-09-04**

This document is the operational publication-order reference for the `mission-aware-satellite-cyber-recovery` research program. It summarizes how the separately frozen studies are grouped into a small number of publications and the order in which those publication packages should be developed or submitted.

This is a publication/governance document only. It does **not** change any frozen design, observation, analysis, statistical result, evidence identity, claim boundary, or publication-package freeze.

## Scope boundary

This map applies **only** to the `mission-aware-satellite-cyber-recovery` repository and its Studies 1–8.

The following related research projects remain separate research and publication workstreams and are **not** part of this map:

- `verifiable-spacecraft-lifecycle`
- `satcom-ttc-post-compromise-recovery`

No evidence, observations, statistical populations, manuscript results, or publication identities from those repositories are pooled into this research program.

## Authority and terminology

The detailed scientific/publication rationale remains governed by:

- `docs/RESEARCH_PROGRAM_PROVENANCE_AND_PUBLICATION_ROADMAP.md`
- `tracker/RESEARCH_TRACKER.md`
- the per-study frozen provenance/results records
- the relevant publication package under `publication/`

**Publication phase** in this document means the recommended operational order for publication work. It is not the same as the existing portfolio paper numbering. In particular, Study 8 remains the roadmap's separate **Paper 4**, but because its companion manuscript/package is already hash-frozen, it is recommended as **Publication Phase 2** operationally.

## Overall publication-phase map

```text
MISSION-AWARE SATELLITE CYBER RECOVERY PROGRAM
│
├── PUBLICATION PHASE 1
│   │
│   └── PAPER 1
│       ├── Study 1
│       └── Study 2
│
│       Primary target:
│       Computers & Security
│
│       Backups / alternatives:
│       AIAA Journal of Aerospace Information Systems (JAIS)
│       IEEE Transactions on Dependable and Secure Computing (TDSC)
│       ACM Transactions on Privacy and Security (TOPS)
│       IEEE Transactions on Aerospace and Electronic Systems (TAES)
│       if a stronger separately frozen aerospace-validation/HIL basis is added
│
│       Current state:
│       science frozen; Study-1 and Study-2 DOI/archive state complete;
│       remaining gate is submission-day live-policy/portal verification
│       plus exact final-export validation
│
├── PUBLICATION PHASE 2
│   │
│   └── STUDY-8 COMPANION PAPER
│       └── Study 8 / S8-PQC-ICR-001
│
│       Roadmap portfolio label:
│       Paper 4
│
│       Current venue hierarchy:
│       1. IEEE Systems Journal
│       2. Acta Astronautica
│       3. International Journal of Satellite Communications and Networking
│
│       Current state:
│       science closed; companion manuscript/package hash-frozen and merged;
│       venue-specific submission preparation remains a separate explicit gate
│
├── PUBLICATION PHASE 3
│   │
│   └── PAPER 2
│       ├── Study 3
│       ├── Study 4
│       └── Study 6
│
│       Working theme:
│       evidence-plane trust composition for intermittent-contact trusted recovery
│
│       Candidate venues, not commitments:
│       IEEE Systems Journal
│       Acta Astronautica
│       AIAA Journal of Aerospace Information Systems
│
│       Current state:
│       component studies frozen; dedicated literature/novelty/venue review
│       required before manuscript development/freeze
│
├── PUBLICATION PHASE 4
│   │
│   └── PAPER 3
│       └── Study 7 / S7-LSO-001
│
│       Working theme:
│       observability limits of learned recovery selectors under
│       trusted-producer compromise
│
│       Candidate venues, not commitments:
│       AIAA Journal of Aerospace Information Systems
│       Aerospace Science and Technology
│
│       Current state:
│       science frozen; fresh AI/autonomy literature and venue review required
│       before publication development
│
└── PUBLICATION PHASE 5
    │
    └── STUDY-5 PUBLICATION DISPOSITION
        └── Study 5 / S5-CUCD-001

        Option A:
        integrate as a clearly separated external-validity/portability section
        in an appropriate larger follow-on paper, potentially Paper 2

        Option B:
        prepare a focused validation/reproducibility paper or research note

        Current state:
        disposition deliberately deferred until after Paper-1 submission;
        no detector-performance claim is authorized from Study 5
```

## Publication Phase 1 — Paper 1: Studies 1 + 2

### Scientific grouping

Paper 1 combines two **separately frozen** empirical studies in one manuscript without pooling their statistical populations.

- **Study 1:** 720 VALID observations across 24 frozen cells.
- **Study 2:** `S2-AEATR-001`, 3,872 VALID observations across 85 cells, 0 INVALID attempts, 162 primary paired contrasts, 432 prespecified secondary contrasts, and independent reproduction with 0 mismatches.

### Publication focus

Mission-aware post-detection cyber response and trusted recovery under mission, contact, evidence, authorization, and bounded-compromise constraints.

### Current target order

1. **Computers & Security** — primary target.
2. **AIAA Journal of Aerospace Information Systems (JAIS)** — immediate domain-fit backup if the primary issue is aerospace/editorial fit rather than scientific quality.
3. **IEEE TDSC / ACM TOPS** — higher-bar security/dependability alternatives using the already frozen evidence.
4. **IEEE TAES** — retained as an aerospace-systems alternative, but stronger if supported by a future separately frozen aerospace/HIL validation study.

### Current state

The Study-2 durable-archive blocker is closed.

- Study-2 version DOI: `10.5281/zenodo.22289114`
- Study-2 concept DOI: `10.5281/zenodo.22289113`
- Study-2 public Phase-6 ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- public-byte verification: PASS

The remaining Paper-1 work is publication preparation only:

1. live Computers & Security scope/policy/portal verification;
2. exact manuscript/submission export assembly;
3. exact citation, DOI, reference, frozen-claim, and scope-fit audit;
4. explicit publisher-submission authorization.

No additional Study-1 or Study-2 scientific execution is required for the current frozen claims.

## Publication Phase 2 — Study-8 companion paper

### Scientific grouping

Study 8 remains a **separate companion study** and is not a third statistical population in Paper 1.

- experiment: `S8-PQC-ICR-001`
- canonical modeled positions: 3,456
- independent reproduction: 3,456/3,456 exact row matches, 0 mismatches
- prespecified primary contrast `P3 - P1`: exactly 0

### Working title

**Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems**

### Current venue hierarchy

1. **IEEE Systems Journal**
2. **Acta Astronautica**
3. **International Journal of Satellite Communications and Networking**

### Current state

The Study-8 science is technically closed and its companion publication package is separately hash-frozen and merged. The negative primary policy-success result remains visible and must not be rescued or reframed as superiority.

Venue-specific package preparation and actual publisher submission remain separate explicit gates.

## Publication Phase 3 — Paper 2: Studies 3 + 4 + 6

### Scientific grouping

This proposed synthesis follows the trust boundary across three separately frozen populations:

1. **Study 3** — persistence/recurrence of false-but-qualified evidence across intermittent-contact transitions.
2. **Study 4** — multi-producer quorum and provenance-diversity tradeoffs.
3. **Study 6** — recovery artifact itself moves inside the trust boundary and requires qualification.

The populations must remain separate inside the synthesis. They must not be pooled into one global score or statistical population.

### Working theme

**Evidence-plane trust composition for intermittent-contact trusted recovery.**

### Candidate venues

- IEEE Systems Journal
- Acta Astronautica
- AIAA Journal of Aerospace Information Systems

These are candidates only, not commitments.

### Current state

Studies 3, 4, and 6 are canonically frozen. Before manuscript development, perform a dedicated literature, novelty, claim-boundary, and live venue review. Venue strategy must not drive post-hoc changes to the frozen studies.

## Publication Phase 4 — Paper 3: Study 7

### Scientific grouping

Study 7 remains separate because machine learning is a materially different scientific mechanism from the deterministic selectors evaluated earlier.

- experiment: `S7-LSO-001`
- frozen population: 1,033 observations

### Working theme

**Observability limits of learned recovery selectors under trusted-producer compromise.**

The defensible contribution is not an "ML superiority" claim. The central interpretation is that a learner using only policy-visible information cannot recover hidden truth that is absent from its inputs; independent corroboration helps only when it is actually independent.

### Candidate venues

- AIAA Journal of Aerospace Information Systems
- Aerospace Science and Technology

These are candidates only, not commitments.

### Current state

Study-7 science is frozen. A fresh AI/autonomy literature and live venue review is required before publication development.

## Publication Phase 5 — Study-5 disposition

### Scientific role

Study 5 is an external-validity/portability boundary study rather than a detector-performance experiment.

Its strongest result is that the evaluated external satellite-cyber dataset broadens scenario/taxonomy coverage but does not directly supply all state variables required for trusted-recovery policy evaluation without fabrication.

### Option A — integrate into a larger follow-on paper

Study 5 may be incorporated as a clearly separated external-validity/portability section, potentially in Paper 2, if the narrative and venue remain coherent.

### Option B — focused validation/reproducibility paper or research note

A standalone vehicle may be appropriate if the contribution is framed around benchmark/dataset sufficiency and the risks of fabricating missing recovery-state variables.

### Prohibited interpretation

Do not present Study 5 as measuring IDS accuracy, recall, false-positive rate, or per-packet recovery-policy effectiveness; those outcomes were not measured by the frozen study.

### Current state

The final publication vehicle is deliberately deferred until after Paper-1 submission.

## Recommended operational order

1. **Phase 1:** finish and submit Paper 1 (Studies 1 + 2), subject to live Computers & Security checks and explicit submission authorization.
2. **Phase 2:** prepare the venue-specific Study-8 companion package from the already frozen publication package.
3. **Phase 3:** perform the literature/novelty/venue review and develop the Studies 3 + 4 + 6 synthesis if authorized.
4. **Phase 4:** perform the learned-selector/AI literature and venue review and develop Study-7 Paper 3 if authorized.
5. **Phase 5:** decide whether Study 5 belongs inside a larger follow-on paper or merits a focused validation/reproducibility vehicle.

This order is intended to minimize simultaneous manuscript churn and prevent publication strategy from altering frozen science.

## Governance rules

- Never pool separately frozen study populations unless a new, prospectively authorized analysis explicitly permits it.
- Never rerun or enlarge a frozen study merely to improve publication optics or respond to venue preference.
- Preserve negative, null, and conditional findings.
- Treat candidate venues as planning aids until a live venue/policy review is completed.
- Publisher submission is a separate explicit authorization gate.
- Historical freeze/handoff documents retain their stage-local states and are not rewritten to appear current.
- New orbital, HIL, operator, RF, spacecraft-performance, CPU, energy, or flight-validation claims require separately designed and frozen evidence.

## Quick reference table

| Publication phase | Publication unit | Studies | Primary/current venue direction | Current next gate |
|---|---|---|---|---|
| 1 | Paper 1 | Study 1 + Study 2 | Computers & Security | Live policy/portal check + exact final export |
| 2 | Study-8 companion / roadmap Paper 4 | Study 8 | IEEE Systems Journal | Separate venue-specific submission-package authorization |
| 3 | Paper 2 synthesis | Studies 3 + 4 + 6 | IEEE Systems Journal / Acta Astronautica / JAIS candidates | Dedicated literature/novelty/venue review |
| 4 | Paper 3 | Study 7 | JAIS / Aerospace Science and Technology candidates | Fresh AI/autonomy literature + venue review |
| 5 | Study-5 disposition | Study 5 | Deferred | Decide integration vs focused research note after Paper 1 submission |
