# Research Program Provenance and Publication Roadmap

**Current-state document - 2026-09-06**

This document explains why the research program contains multiple separately frozen studies, how each study follows a limitation or trust-boundary question raised by prior work, and how the completed evidence is organized into a small number of citable publications rather than one paper per study.

For the shortest authoritative current-state handoff, read [`CURRENT_PUBLICATION_STATE.md`](CURRENT_PUBLICATION_STATE.md) first.

This is a publication/governance document. It does not change any frozen design, observation, statistical result, canonical finding, claim boundary, publication-package freeze, or submitted publisher file.

## Program rule

A new study is justified only when the prior frozen population cannot answer a materially different research question without changing its design, treatment, outcome definition, or trust assumptions. New evidence is therefore created under a new experiment identifier and frozen separately rather than appended to an earlier statistical population.

The studies are related by research question and hash-bound dependencies where stated, but their observations are not silently pooled.

## Study sequence

| Study | Experiment / evidence | Why the prior study could not answer it | Canonical state | Publication disposition |
|---|---|---|---|---|
| Study 1 | 720 VALID software-in-the-loop observations | Establish the initial mission/contact/evidence response and trusted-recovery comparison | frozen and DOI-backed | Paper 1 with Study 2; submitted to JAIS |
| Study 2 | `S2-AEATR-001`, 3,872 VALID observations | Study 1 did not separately instantiate richer evidence-integrity, producer-compromise, ambiguity/control, and contact conditions | Phase-7 findings frozen; independent reproduction 0 mismatches; source archive DOI/checksum verified | Paper 1 with Study 1; submitted to JAIS |
| Study 3 | `S3-K4E-001`, 1,380 trajectories / 67,620 epochs | Study 2 does not model one-shot/persistent false evidence across repeated K4 contact transitions | canonical results merged in PR #79 / `68a2c9a1394743e9a233e93586e86a6179a0793c`; independent audit PASS | candidate component of Paper 2 |
| Study 4 | `S4-MPQ-001`, 4,608 exact observations | Study 3 has a single evidence-producer trust boundary and cannot quantify quorum/provenance-diversity trade-offs | canonical results merged in PR #81 / `09a3fa61276e348b58a852c156e7bfc64b25d32d`; independent audit PASS, 0 observation and 0 threshold mismatches | candidate component of Paper 2 |
| Study 5 | `S5-CUCD-001`, 80 deterministic portability decisions plus sufficiency/transferability rows | Studies 1-4 do not test whether an external published satellite-cyber dataset supplies the state required by frozen recovery policies | canonical results merged in PR #83 / `6415a391dc2337c51ce72442ac7d86a25b4fbc02`; independent mismatches 0 | validation/portability stream; final vehicle deliberately deferred |
| Study 6 | `S6-SCTR-001`, 420 exact observations | Studies 2-4 trust the recovery artifact itself; Study 6 moves the trust boundary upstream to artifact qualification | canonical results merged in PR #85 / `0dfe7f4331fc1f8864344c95d39e0d8dcb74c8f4`; independent audit PASS | candidate component of Paper 2 |
| Study 7 | `S7-LSO-001`, 1,033 exact observations | Earlier selectors are deterministic rule-based mechanisms and cannot answer whether a learned selector over the same visible information can escape the V5 information boundary | canonical results merged in PR #87 / `f582c36cc5747a6703ec651bb957bbfea5852a7e`; independent audit PASS | separate Paper 3 line |
| Study 8 | `S8-PQC-ICR-001`, 3,456 canonical + 3,456 independently reproduced rows, 0 mismatches | Earlier studies do not model cryptographic-transition byte burden and finite intermittent-contact recovery budgets | science closed; source publication package frozen; Acta package submitted | roadmap Paper 4; Acta manuscript `AA-D-26-02872`, `With Editor` |

## Publication portfolio

### Paper 1 - Studies 1 + 2

**Theme:** mission-aware post-detection response and trusted recovery under contact and evidence constraints.

The two populations remain statistically separate inside one manuscript.

**Submitted venue:** AIAA Journal of Aerospace Information Systems  
**Manuscript ID:** `2026-09-I012066`  
**Submission date:** 2026-09-05  
**Current state:** editorial/peer-review workflow pending

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study-2 archive state:

- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public ZIP SHA-256 independently verified against the frozen source identity

No Study-3-8 finding should be inserted into Paper 1 as a new statistical result. No submitted Paper-1 publisher-facing file should change unless JAIS explicitly requests a revision.

### Paper 2 - candidate synthesis of Studies 3 + 4 + 6

**Working theme:** evidence-plane trust composition for intermittent-contact trusted recovery.

The scientific progression is coherent:

1. Study 3 asks how false-but-qualified evidence persists or recurs through contact windows.
2. Study 4 asks how multi-producer quorum and provenance diversity alter the safety/availability frontier.
3. Study 6 asks what happens when the recovery artifact itself is inside the trust boundary.

The synthesis must preserve all three frozen populations separately and use a systems/assurance narrative rather than pooling observations into a single score.

**Historical venue-fit candidates, not commitments:**

- IEEE Systems Journal
- Acta Astronautica
- AIAA Journal of Aerospace Information Systems

A fresh literature, novelty, claim-boundary, and live venue review is required before manuscript development or venue lock. No target is authorized by this roadmap.

**This is the next active publication-development priority.**

### Study 5 - portability/validation disposition

Study 5 should not be forced into a standalone paper merely because it is frozen. Its strongest result is a disciplined external-validity boundary: the CuCD-ID labels broaden scenario/taxonomy coverage, but the packet-row schema supplies 0/8 direct trusted-recovery inputs, so row-level policy benchmarking would require fabrication.

Two publication paths remain open:

- integrate Study 5 as a clearly separated external-validity/portability section in a larger follow-on paper if the venue permits and the narrative remains coherent; or
- prepare a focused validation/reproducibility paper or research note.

A direct detector-performance claim is prohibited because Study 5 did not measure CuCD-ID IDS accuracy, recall, false-positive rate, or per-packet recovery-policy performance.

### Paper 3 - Study 7

**Theme:** observability limits of learned recovery selectors under trusted-producer compromise.

Study 7 remains separate because machine learning is a significant scientific component. Its contribution is not ML superiority. The visible-only learner reproduces the visible-state decision boundary but cannot resolve hidden-truth collisions unavailable in its inputs; independent corroboration helps only when it is actually independent.

Historical candidate venues include AIAA Journal of Aerospace Information Systems and Aerospace Science and Technology. A fresh AI/autonomy literature and venue review is required before publication development.

### Roadmap Paper 4 - Study 8

Study 8 has a separate frozen target-neutral companion package and an exact submitted Acta package.

**Journal:** Acta Astronautica  
**Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems  
**Article type:** Research paper  
**Manuscript ID:** `AA-D-26-02872`  
**Submission date:** 2026-09-06  
**Current Editorial Manager status:** `With Editor`

The submitted package is `S8-ACTA-PKGFREEZE-002` from commit `f5e9a1d4553737e534821bf647463abfd44fa0dd`.

Current submitted-state authority:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Study 8 remains scientifically frozen. The negative primary policy result remains visible and exact. No scientific reexecution or statistical reanalysis was performed for submission, and no submitted publisher-facing file should change unless Acta explicitly requests a revision.

## Why the studies are not scope creep

The sequence is limitation-driven rather than feature-driven:

- Study 1 -> richer evidence/adversary boundary (Study 2);
- Study 2 -> temporal persistence under intermittent contact (Study 3);
- Study 2/3 -> multi-producer trust composition (Study 4);
- Studies 1-4 -> external-dataset input sufficiency and portability (Study 5);
- Studies 2-4 -> upstream recovery-artifact trust (Study 6);
- Study 2 -> information-boundary test with a learned selector (Study 7);
- broader recovery program -> cryptographic-transition/contact-budget sibling dimension (Study 8).

The program should therefore be described as a sequence of separately frozen boundary studies, not as one eight-study pooled experiment.

## Publication-order recommendation from 2026-09-06

1. Keep Paper 1 frozen while JAIS editorial/peer review proceeds.
2. Keep roadmap Paper 4 / Study 8 frozen while Acta manuscript `AA-D-26-02872` proceeds through editorial review.
3. Begin Paper 2 by auditing the frozen Studies 3 + 4 + 6 evidence/provenance, then perform a dedicated literature/novelty/claim-boundary/live-venue review before authorizing manuscript development.
4. Decide whether Study 5 belongs as a clearly separated portability/external-validity component of Paper 2 or a focused validation vehicle.
5. Perform a dedicated learned-selector/AI literature and venue review before authorizing Study-7 Paper 3 development.

This order reduces simultaneous manuscript churn and prevents venue strategy from driving changes to frozen science.

## Infrastructure policy

Per-study scientific implementations and frozen environments should not be refactored in place after freeze merely to reduce duplication. Shared non-scientific CI/test utilities may be consolidated prospectively for future studies provided historical reproducibility remains intact.

## Historical external scope sources

The 2026-09-03 venue-fit check used then-current publisher/society scope pages. These links remain historical evidence for candidate fit and are not acceptance predictions or current venue commitments.

- Acta Astronautica: <https://shop.elsevier.com/journals/acta-astronautica/0094-5765>
- IEEE Systems Journal: <https://ieeesystemscouncil.org/publication/ieee-systems-journal>
- AIAA Journal of Aerospace Information Systems: <https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/>
- Aerospace Science and Technology: <https://shop.elsevier.com/journals/aerospace-science-and-technology/1270-9638>

Recheck all live venue pages before selecting a target for a new manuscript.
