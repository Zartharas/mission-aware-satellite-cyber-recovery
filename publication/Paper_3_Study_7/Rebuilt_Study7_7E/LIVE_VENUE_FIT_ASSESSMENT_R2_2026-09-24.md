# Paper 3 — Portfolio-Adjusted Live Venue-Fit Assessment R2 — 2026-09-24

**Assessment ID:** `PAPER3-S7-S7E-LIVE-VENUE-AUDIT-002`  
**Supersedes for current venue recommendation:** `PAPER3-S7-S7E-LIVE-VENUE-AUDIT-001`  
**Manuscript:** rebuilt Paper 3 / Study 7 + Study 7E  
**State:** `COMPLETE__PORTFOLIO_ADJUSTED__VENUE_NOT_LOCKED`  
**Submission authorization:** NOT GRANTED

## 1. Why R2 is required

The first venue assessment correctly compared journal scope but did not fully account for two active manuscripts by the same author that materially affect portfolio concentration.

### Active JSSE manuscript from a different research repository

Repository: `Zartharas/verifiable-spacecraft-lifecycle`

Submitted manuscript:

**Measuring Software Supply-Chain Assurance for Spacecraft Flight Software: A Controlled, Comparative Evaluation**

Current publisher state supplied by the author: **Under Review** at the Journal of Space Safety Engineering.

That paper evaluates a six-level S0-S5 software-supply-chain assurance ladder across spacecraft flight-software targets, including cFS and F Prime, using attack/failure injection, detection/false-positive/false-negative metrics, lifecycle evidence, ablation, and a TUF baseline.

### Active JAIS manuscript from the same research program

Repository: `Zartharas/mission-aware-satellite-cyber-recovery`

Paper 1 / Studies 1+2:

**Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints**

- venue: AIAA Journal of Aerospace Information Systems;
- manuscript ID: `2026-09-I012066`;
- submitted: 2026-09-05;
- state: `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`.

Paper 1 is scientifically distinct from Paper 3, but it is closer than the separate JSSE supply-chain paper because both belong to the same mission-aware recovery program and share terminology around recovery, adversarial evidence, and trusted state.

## 2. Scientific overlap audit: active JSSE paper versus Paper 3

### Active JSSE supply-chain paper

Primary question:

How much assurance is gained, and at what cost, by progressively adding supply-chain mechanisms to spacecraft flight-software lifecycle/update pipelines?

Primary mechanisms and evidence:

- S0-S5 assurance ladder;
- signing, SBOM, provenance, attestation, rollback, authorization evidence;
- cFS and F Prime software targets;
- 15 attack/failure cases;
- TUF baseline;
- detection/FP/FN, timing/storage/evidence-overhead, reproducibility, ablation.

### Rebuilt Paper 3

Primary question:

How do recovery-decision correctness and safety/availability trade-offs depend on information sufficiency, deterministic-versus-learned selector behavior, and explicit trust-domain sharing/separation?

Primary mechanisms and evidence:

- Study 7 observability/information-sufficiency construction;
- Study 7E equal-information D0/L0 and D1/L1 pairs;
- source/key/execution/transport/authority domain aliases;
- F0-F12 fault and common-cause profiles;
- frozen learned models;
- unseen-fault and held-out-topology transfer;
- unsafe-proceed and false-conservative-hold endpoints.

### Overlap decision

`LOW_SCIENTIFIC_OVERLAP__NONZERO_DOMAIN_AND_CFS_OVERLAP`

The two papers do not share:

- research questions;
- experimental populations;
- frozen result sets;
- primary endpoints;
- policy families;
- software-supply-chain ladder;
- Paper-3 learned-selector models.

They do share:

- spacecraft cybersecurity domain;
- cFS as one technical reference surface;
- assurance/resilience vocabulary;
- same author.

Therefore simultaneous presence at JSSE is scientifically defensible but creates avoidable **same-journal portfolio concentration** while the first manuscript is still under review.

## 3. Scientific overlap audit: active JAIS Paper 1 versus Paper 3

### Paper 1 / Studies 1+2

Paper 1 evaluates deterministic mission-aware cyber response and trusted recovery under contact, evidence, authorization, and bounded adversarial conditions. Study 2 includes the signed-but-false / research-truth distinction that later serves as antecedent motivation for Study 7.

### Paper 3 / Studies 7+7E

Paper 3 isolates information sufficiency and then compares deterministic and learned equal-information recovery selectors under explicit trust-domain topology and held-out fault transfer.

### Overlap decision

`SEPARATE_FROZEN_SCIENCE__MODERATE_CONCEPTUAL_LINEAGE__SAME_PROGRAM`

The populations, endpoints, and experiments are separate. However, the papers share more conceptual lineage than the JSSE supply-chain manuscript, including:

- satellite cyber recovery;
- adversarial evidence;
- trusted-state/recovery authorization;
- Study-2/V5 antecedent lineage;
- same repository/research program.

A second concurrent JAIS paper would therefore create the strongest editorial self-overlap/portfolio scrutiny among the otherwise technically suitable venues.

AIAA publication ethics prohibit submitting the same or closely related work to another publisher while under AIAA consideration and require disclosure of related publication history. Paper 3 is not the same work, but any eventual JAIS submission would need especially explicit related-work disclosure and differentiation from Paper 1.

## 4. Revised venue strategy

The revised recommendation separates **scientific fit** from **portfolio concentration**.

### Primary candidate — International Journal of Critical Infrastructure Protection (IJCIP)

**Assessment:** `PRIMARY_CANDIDATE__STRONG_SECURITY_FIT__NO_CURRENT_PORTFOLIO_COLLISION`

Current publisher scope emphasizes practical scientific and engineering solutions for critical-infrastructure protection, including security challenges, security principles/techniques, dependencies/interdependencies, cascading failure, and protection/continuity.

The journal has current precedent for spaceborne cybersecurity/ML-security work, including the 2026 S-LARF paper.

Why it now leads:

- Paper 3 is fundamentally a security/assurance paper;
- common-cause trust failure and recovery continuity map naturally to protection/resilience;
- no active manuscript from this author is currently under IJCIP;
- the paper can remain technically specific without competing with an existing same-journal spacecraft paper.

Required discipline:

- frame spacecraft/space services as a critical cyber-physical/communications/defense infrastructure context without claiming that the experiment measures national-infrastructure resilience;
- retain the exact finite-population and non-operational-probability caveats.

### Second candidate — Journal of Information Security and Applications (JISA)

**Assessment:** `SECONDARY_CANDIDATE__STRONG_INFORMATION_SECURITY_APPLICATION_FIT__NO_CURRENT_PORTFOLIO_COLLISION`

JISA focuses on original research and practice-driven applications in information security and emphasizes technical contributions and modern security problems.

Why it is attractive:

- recovery authorization under compromised evidence is directly an information-security application;
- equal-information selector behavior and trust-domain faulting are technical rather than policy-only contributions;
- no existing author manuscript in this portfolio is currently under JISA.

Main trade-off:

- less aerospace-specific editorial audience than JSSE/JAIS;
- R2 would need to foreground the general security-assurance problem while retaining the spacecraft reference architecture as the application domain.

### Third candidate — Journal of Space Safety Engineering (JSSE)

**Assessment:** `VERY_STRONG_SCIENTIFIC_FIT__ACTIVE_UNRELATED_MANUSCRIPT_CAUTION`

JSSE remains a strong scientific match because the journal explicitly centers space safety and the Paper-3 outcomes concern unsafe recovery, conservative holds, common-cause failure, and assurance.

The existing JSSE manuscript is scientifically distinct enough that a second paper would not be duplicate publication on the evidence reviewed here.

However, while **Measuring Software Supply-Chain Assurance for Spacecraft Flight Software** remains under review, submitting Paper 3 to the same journal would concentrate two spacecraft-cybersecurity manuscripts from the same author in one editorial pipeline.

This is a portfolio consideration, not a finding that JSSE prohibits the submission.

### Fourth candidate — Journal of Systems Architecture (JSA)

**Assessment:** `ARCHITECTURE_FIT__NO_CURRENT_PORTFOLIO_COLLISION__REFRAMING_REQUIRED`

JSA covers embedded-system and software architecture from system software through application-specific architecture, including real-time, distributed, communications-software, and novel embedded-system applications.

Study 7E's cFS-grounded trust-domain architecture and fault-propagation design fit that scope.

Main caution:

- Paper 3's strongest contribution is assurance behavior, not a novel embedded-software architecture;
- venue adaptation would need to emphasize architectural trust dependencies without overstating architecture novelty.

### Fifth candidate — Reliability Engineering & System Safety (RESS)

**Assessment:** `STRONG_SPACE_SYSTEM_SAFETY_SCOPE__METHODOLOGY_STRETCH`

RESS explicitly includes space systems, software reliability, automatic fault detection/diagnosis, operator decision support, and safety/reliability of complex technological systems.

Paper 3 has a plausible fit around unsafe decisions, common-cause failures, and safety/availability trade-offs.

Main caution:

- the paper is not a probabilistic reliability analysis;
- exact finite-population modeled counts and cyber-assurance logic may require a stronger reliability-method framing than the frozen evidence justifies.

### Sixth candidate — AIAA Journal of Aerospace Information Systems (JAIS)

**Assessment:** `VERY_STRONG_TECHNICAL_FIT__HIGHEST_SAME_PROGRAM_PORTFOLIO_CAUTION`

JAIS remains a technically strong match for aerospace software, V&V, ML, systems engineering, and mission assurance.

It is moved down in the portfolio-adjusted order because Paper 1 is already under JAIS review and has closer conceptual lineage to Paper 3 than the unrelated JSSE supply-chain study.

This is not a scientific-overlap failure; the repository's non-overlap gate remains valid.

### Other backups

- IEEE Systems Journal — credible systems/security/mission-assurance backup.
- IEEE TAES — strong aerospace fit, but Paper 2 is already active there.
- Acta Astronautica — broad space fit, but this research program has a recent Paper-4 editorial rejection there.
- Aerospace Science and Technology — possible engineering backup, with less direct security/assurance identity.

## 5. Current no-go / concentration map

| Venue | Current portfolio factor | R2 disposition |
|---|---|---|
| IJCIP | no active manuscript identified | **primary candidate** |
| JISA | no active manuscript identified | **second candidate** |
| JSSE | different-repo supply-chain paper currently under review | strong fit, portfolio caution |
| JAIS | Paper 1 from same repo/program currently under review | strong fit, higher overlap/portfolio caution |
| TAES | Paper 2 currently active | backup only |
| IJSCCN | rebuilt Paper 4 already venue-locked | avoid for Paper 3 |
| Acta Astronautica | recent Paper-4 rejection | backup only |
| Computers & Security | current AI/ML moratorium conflicts with Paper 3 | no-go |
| CEAS Space Journal | recent Paper-3 rejection; no invitation to resubmit recorded | defer |

## 6. Recommended decision rule

If the author's priority is to minimize portfolio concentration while preserving technical fit:

1. evaluate IJCIP first;
2. evaluate JISA second;
3. retain JSSE as the strongest space-domain fallback while the current unrelated JSSE manuscript is active;
4. retain JAIS as a later technical fallback, preferably after Paper-1 editorial disposition or with especially explicit related-work disclosure.

This is **not an acceptance prediction** and does not imply that journals prohibit distinct concurrent submissions by one author.

## 7. Required next step before venue lock

The current R2 manuscript remains venue-neutral.

Before locking IJCIP, JISA, or another venue:

1. perform a full current Guide-for-Authors audit for the chosen venue;
2. examine recent articles for article form, length, figures, data/code statements, AI disclosure, and citation style;
3. verify no new scope restriction conflicts with the ML component;
4. adapt title/abstract/introduction framing without changing frozen science;
5. maintain explicit cross-paper differentiation from Paper 1 and the active JSSE supply-chain manuscript.

No venue is locked by this assessment.
