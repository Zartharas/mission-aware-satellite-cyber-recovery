# Research Program Provenance and Publication Roadmap

**Current-state document — 2026-09-03**

This document explains why the research program contains multiple separately frozen studies, how each study follows a limitation or trust-boundary question raised by prior work, and how the completed evidence is intended to become a small number of citable publications rather than one paper per study.

It is a publication/governance document. It does not change any frozen design, observation, statistical result, canonical finding, or claim boundary.

## Program rule

A new study is justified only when the prior frozen population cannot answer a materially different research question without changing its design, treatment, outcome definition, or trust assumptions. New evidence is therefore created under a new experiment identifier and frozen separately rather than appended to an earlier statistical population.

The resulting studies are related by research question and hash-bound dependencies where stated, but their observations are not silently pooled.

## Study sequence

| Study | Experiment / evidence | Why the prior study could not answer it | Canonical state | Publication disposition |
|---|---|---|---|---|
| Study 1 | 720 VALID software-in-the-loop observations | Establish the initial mission/contact/evidence response and trusted-recovery comparison | frozen and DOI-backed | Paper 1 with Study 2 |
| Study 2 | `S2-AEATR-001`, 3,872 VALID observations | Study 1 did not separately instantiate richer evidence-integrity, producer-compromise, ambiguity/control, and contact conditions | Phase-7 findings frozen; independent reproduction 0 mismatches | Paper 1 with Study 1; Study-2 source DOI is the remaining archive blocker |
| Study 3 | `S3-K4E-001`, 1,380 trajectories / 67,620 epochs | Study 2 does not model one-shot/persistent false evidence across repeated K4 contact transitions | canonical results merged in PR #79 / `68a2c9a1394743e9a233e93586e86a6179a0793c`; independent audit PASS | candidate component of Paper 2 |
| Study 4 | `S4-MPQ-001`, 4,608 exact observations | Study 3 has a single evidence-producer trust boundary and cannot quantify quorum/provenance-diversity trade-offs | canonical results merged in PR #81 / `09a3fa61276e348b58a852c156e7bfc64b25d32d` | candidate component of Paper 2 |
| Study 5 | `S5-CUCD-001`, 80 deterministic portability decisions plus sufficiency/transferability rows | Studies 1–4 do not test whether an external published satellite-cyber dataset supplies the state required by frozen recovery policies | canonical results merged in PR #83 / `6415a391dc2337c51ce72442ac7d86a25b4fbc02`; independent mismatches 0 | validation/portability stream; final vehicle deliberately deferred |
| Study 6 | `S6-SCTR-001`, 420 exact observations | Studies 2–4 trust the recovery artifact itself; Study 6 moves the trust boundary upstream to artifact qualification | canonical results merged in PR #85 / `0dfe7f4331fc1f8864344c95d39e0d8dcb74c8f4`; independent audit PASS | candidate component of Paper 2 |
| Study 7 | `S7-LSO-001`, 1,033 exact observations | Earlier selectors are deterministic rule-based mechanisms and cannot answer whether a learned selector over the same visible information can escape the V5 information boundary | canonical results merged in PR #87 / `f582c36cc5747a6703ec651bb957bbfea5852a7e`; independent audit PASS | separate AI/autonomy-compatible Paper 3 |
| Study 8 | `S8-PQC-ICR-001`, 3,456 canonical + 3,456 independently reproduced rows, 0 mismatches | Earlier studies do not model cryptographic-transition byte burden and finite intermittent-contact recovery budgets | science closed; publication package hash-frozen and merged | separate Paper 4 / venue-specific submission preparation is the next gate |

## Publication portfolio

### Paper 1 — Studies 1 + 2

**Theme:** mission-aware post-detection response and trusted recovery under contact and evidence constraints.

The two populations remain statistically separate inside one manuscript. The current Computers & Security package is already structured around this boundary.

**Blocking item:** the exact responsible-release-reviewed Study-2 Phase-6 source ZIP must receive its own durable DOI, and the publicly served bytes must be re-verified before the DOI is inserted into Data Availability.

No Study-3–8 finding should be added to Paper 1 as a new statistical result. Follow-on studies may be cited later as separate research outputs if and when they become public.

### Paper 2 — candidate synthesis of Studies 3 + 4 + 6

**Working theme:** evidence-plane trust composition for intermittent-contact trusted recovery.

The scientific progression is coherent:

1. Study 3 asks how false-but-qualified evidence persists or recurs through contact windows.
2. Study 4 asks how multi-producer quorum and provenance diversity alter the safety/availability frontier.
3. Study 6 asks what happens when the recovery artifact itself is inside the trust boundary.

The synthesis should preserve all three frozen populations separately and use a systems/assurance narrative rather than pooling observations into a single score.

**Current venue-fit candidates, not commitments:**

- *Acta Astronautica* — broad space-systems design/operation and satellite-technology scope;
- *IEEE Systems Journal* — systems modeling/simulation, resilience, security, reliability/availability, and systems-of-systems framing;
- *Journal of Aerospace Information Systems* — aerospace computing/information, software verification and validation, autonomy, safety, and mission assurance.

A fresh venue/literature review is required before manuscript freeze. No target is authorized by this roadmap.

### Study 5 — portability/validation disposition

Study 5 should not be forced into a standalone paper merely because it is frozen. Its strongest result is a disciplined external-validity boundary: the CuCD-ID labels broaden scenario/taxonomy coverage, but the packet-row schema supplies 0/8 direct trusted-recovery inputs, so row-level policy benchmarking would require fabrication.

Two publication paths remain open after Paper-1 submission:

- integrate Study 5 as a clearly separated external-validity/portability section in a larger follow-on paper if the venue permits and the narrative remains coherent; or
- prepare a focused validation/reproducibility paper or research note.

A direct detector-performance claim is prohibited because Study 5 did not measure CuCD-ID IDS accuracy, recall, false-positive rate, or per-packet recovery-policy performance.

### Paper 3 — Study 7

**Theme:** observability limits of learned recovery selectors under trusted-producer compromise.

Study 7 remains separate because machine learning is a significant scientific component. Its contribution is not “ML superiority.” The visible-only learner reproduces the visible-state decision boundary but cannot resolve hidden-truth collisions unavailable in its inputs; independent corroboration helps only when it is actually independent.

**Current venue-fit candidates, not commitments:**

- *Journal of Aerospace Information Systems* — explicitly includes machine learning, autonomous systems, aerospace software/information, verification/validation, safety and mission assurance;
- *Aerospace Science and Technology* — includes complex-system engineering, decision aid, information processing, robotics/intelligent systems, and space-vehicle/satellite engineering.

A fresh AI/autonomy literature and venue review is required before publication development.

### Paper 4 — Study 8

Study 8 already has a separate hash-frozen companion-paper package. Its current venue-fit analysis favors a systems-oriented venue and keeps the negative primary policy result visible. Venue-specific submission preparation is a later explicit gate and does not authorize scientific re-execution.

## Why the studies are not scope creep

The sequence is limitation-driven rather than feature-driven:

- Study 1 → richer evidence/adversary boundary (Study 2);
- Study 2 → temporal persistence under intermittent contact (Study 3);
- Study 2/3 → multi-producer trust composition (Study 4);
- Studies 1–4 → external-dataset input sufficiency and portability (Study 5);
- Studies 2–4 → upstream recovery-artifact trust (Study 6);
- Study 2 → information-boundary test with a learned selector (Study 7);
- broader recovery program → cryptographic-transition/contact-budget sibling dimension (Study 8).

The program should therefore be described as a sequence of separately frozen boundary studies, not as one eight-study pooled experiment.

## Publication-order recommendation

1. Complete the Study-2 DOI and close Paper 1 submission preparation.
2. Continue Study-8 venue-specific preparation from its already frozen companion package.
3. Perform a dedicated literature/novelty/venue review for the proposed Studies 3+4+6 synthesis before authorizing Paper 2 development.
4. Decide Study-5 integration versus standalone validation vehicle after Paper 1 is submitted.
5. Perform a dedicated learned-selector/AI literature review before authorizing Study-7 Paper 3 development.

This order reduces simultaneous manuscript churn and prevents venue strategy from driving changes to frozen science.

## Infrastructure policy

Per-study scientific implementations and frozen environments should not be refactored in place after freeze merely to reduce duplication. Shared non-scientific CI/test utilities may be consolidated prospectively for future studies after current submission work, provided historical reproducibility remains intact.

## External scope sources checked for this roadmap

The 2026-09-03 venue-fit check used current publisher/society scope pages for Acta Astronautica, Journal of Aerospace Information Systems, Aerospace Science and Technology, and International Journal of Satellite Communications and Networking. These sources support candidate fit only; they do not constitute acceptance predictions or final venue commitments.
