# Paper 4 / Study 8 Post-Rejection Forensic Quality Audit

**Date:** 2026-09-19  
**Publication line:** Paper 4  
**Study:** Study 8 / `S8-PQC-ICR-001`  
**Rejected venue:** Acta Astronautica  
**Rejected manuscript:** `AA-D-26-02872`  
**Audit status:** `FORENSIC_AUDIT_COMPLETE__NO_FROZEN_SCIENCE_DEFECT_DEMONSTRATED`

## Purpose

This audit examines the exact frozen Study 8 manuscript and scientific record after the Acta Astronautica editorial rejection. It separates:

1. manuscript and presentation weaknesses that can be corrected without reopening the frozen study;
2. limitations of the frozen scientific design that must remain explicit;
3. genuinely new scientific work that would require a separate prospective study authorization.

The Acta decision did not enumerate a methodological, statistical, reproducibility, ethics, data, or scope defect. The audit therefore does not attribute any specific weakness below to the editor. These are independent publication-quality findings.

## Frozen authority

Study 8 remains a complete deterministic finite population of 3,456 modeled positions.

The following are immutable for this retargeting audit:

- primary result: all four policies = `635/864 = 73.4954%`;
- prespecified primary contrast: `P3 - P1 = 0/1 = 0.000000 percentage points`;
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`;
- primary findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`;
- interpretation audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`;
- exact rejected Acta package: `S8-ACTA-PKGFREEZE-002`.

No canonical rerun, endpoint change, population change, selective exclusion, or post-hoc primary-result replacement is authorized.

## Overall finding

The frozen study is internally coherent and reproducible within its declared abstraction boundary. The strongest publication weakness is not an identified statistical or reproducibility defect. It is that the manuscript's current organization does not make the strongest systems contribution as clear and immediate as it could.

A manuscript-only retarget is scientifically defensible.

A stronger empirical or operational claim would require a new study rather than alteration of Study 8.

## A. Scientific-design audit

### A1. The primary null is real and must remain primary

The prespecified P3-versus-P1 contrast is exactly zero marginally and in every prespecified regime, profile, disruption, and deadline stratum.

This is a valid negative result.

However, P3 shares P1's required object bundle, byte scheduler, and staged state semantics except for a pre-commit guard that cannot create capacity, shrink the object bundle, or add contacts. The discussion already explains this. That means the null result is mechanistically understandable from the design and can appear less surprising than the title suggests.

**Publication implication:** do not market P3 as the paper's main innovation. Treat the null as a design result that clarifies what contact awareness can and cannot do under a fixed transfer architecture.

### A2. The strongest result is the feasibility envelope

The most distinctive quantitative finding is the interaction between standardized cryptographic-object burden and finite intermittent contact:

- `PROFILE_512_44`: `1080/1152 = 93.7500%`;
- `PROFILE_768_65`: `748/1152 = 64.9306%`;
- `PROFILE_1024_87`: `712/1152 = 61.8056%`;
- success is non-increasing with larger frozen object burden in all 1,152 matched non-profile positions.

The second strong result is that equal complete-cycle capacity does not imply equal deadline-constrained feasibility when contact timing differs.

The third strong result is the separation between:

- whether trusted recovery is feasible; and
- what predecessor exposure, control unavailability, overlap, transfer burden, attempts, and failure-state costs are incurred.

**Publication implication:** these results should form the organizing systems thesis of the retargeted paper.

### A3. The abstraction is rigorous but externally narrow

The frozen model deliberately excludes:

- physical contact durations and orbital geometry;
- RF throughput and link behavior;
- packet/framing/certificate overhead;
- directional uplink/downlink constraints;
- onboard ML-KEM/ML-DSA execution cost;
- energy, memory, thermal, and side-channel behavior;
- adaptive adversary behavior;
- external laboratory replication.

These are correctly disclosed and do not invalidate Study 8.

They do limit the strength of operational spacecraft claims and make venue selection important.

### A4. No sampling-inference defect identified

The study evaluates the complete frozen deterministic population rather than a sample. Exact finite-population summaries without sampling p-values or sampling confidence intervals are coherent with that object of inference.

The retargeted manuscript should explain this once, clearly, and avoid repeatedly defending the absence of sampling inference.

## B. Manuscript-quality findings

### B1. Title and scientific center are misaligned

Current title:

> Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems

The wording foregrounds contact awareness even though the contact-aware policy has no success advantage. The title therefore directs editorial attention toward the paper's null mechanism instead of its stronger systems result.

**Recommended direction:** foreground post-quantum recovery feasibility under intermittent contact, standardized object burden, and timing. Keep contact-aware policy comparison as one result, not the title's central promise.

### B2. Abstract is too dense and provenance-heavy

The abstract carries:

- the full six-factor design;
- exact population size;
- inference-policy explanation;
- same-repository reproduction;
- several exact percentages;
- matched-profile monotonicity;
- deadline/contact result;
- policy state-cost result.

All of these are accurate, but together they reduce accessibility.

**Recommended correction:** use a four-part abstract:

1. problem and gap;
2. deterministic design-space method;
3. three principal results;
4. bounded systems implication.

Move repository implementation details out of the abstract.

### B3. The novelty statement is cautious but not sufficiently comparative

The manuscript correctly avoids claiming novelty for:

- PQC in satellites;
- crypto agility;
- hybrid migration;
- larger PQC objects;
- constrained satellite links.

However, it does not sharply contrast its contribution against the closest adjacent work in one compact section.

A stronger retarget should explicitly distinguish this study from:

- satellite PQC algorithm/performance comparison;
- quantum-safe or hybrid handshake design;
- generic crypto-agility migration guidance;
- bandwidth-constrained PQ authentication;
- physical-layer or implementation benchmarking.

The narrow novelty is the modeled **post-compromise trusted-state transition problem under finite intermittent contact**, with explicit epoch-state semantics and separate feasibility versus transition-state-cost endpoints.

### B4. The method lacks an immediate visual model

The manuscript describes the protocol and contact model in prose, but the reader has to reconstruct the design mentally.

At minimum, a retargeted paper should add non-analytic schematic figures derived directly from the frozen design:

1. recovery state machine and predecessor/successor acceptance semantics;
2. seven transition objects and dependency order;
3. the four equal-total-capacity contact schedules on the 48-slot logical timeline.

These are design visualizations, not new scientific analyses.

### B5. The results should be reordered

Current ordering begins with the exact null policy result.

For transparency, the primary result must remain clearly labeled primary, but the paper does not have to make the null comparison the entire narrative center.

Recommended structure:

1. prespecified primary policy result, concise and explicit;
2. cryptographic-object feasibility envelope;
3. equal-capacity contact-timing result;
4. deadline result;
5. policy-state and resource tradeoffs;
6. invariant/structural-zero checks.

This keeps the primary endpoint honest while allowing the more informative system-design findings to carry the discussion.

### B6. Repository provenance is overexposed in the reader-facing narrative

Hashes and exact repository provenance are valuable for reproducibility, but too much of that material in the main narrative can make the paper feel like a release artifact rather than a journal article.

**Recommended correction:** retain a concise reproducibility statement in the article and move detailed hashes, commit identities, and audit lineage to the public repository/data-availability record or supplement.

### B7. Limitation language is accurate but too dominant

The paper repeatedly states what is not measured. That discipline is valuable, but repeated boundary language can dilute the contribution.

**Recommended correction:** preserve every claim boundary, but consolidate most of it into:

- one concise scope paragraph in Methods;
- one focused limitations section;
- short precision qualifiers only where needed elsewhere.

### B8. Discussion needs more mechanism-to-literature comparison

The discussion explains internal mechanisms well, but the retargeted version should compare them directly with recent satellite/NTN PQC work.

The paper should show that existing work often asks whether PQC can be implemented efficiently, how handshake/authentication overhead can be reduced, or how algorithms compare, while Study 8 asks whether a trusted successor epoch can be completed before a deadline under a finite contact schedule after compromise.

That distinction is stronger than a generic statement that "PQC overhead matters."

### B9. The phrase `0/1` is machine-precise but editorially awkward

The frozen fraction is legitimate in the machine-readable results.

In journal prose, the primary contrast should normally be expressed as:

> exactly 0.000000 percentage points

with the exact fraction retained in traceability/supplementary material.

### B10. Current figures emphasize outcomes but not mechanism

The two frozen result figures are useful, but they do not explain why the results occur.

For the retargeted paper, the visual hierarchy should include mechanism before outcome:

- state/transition schematic;
- contact-timing schematic;
- profile-success result;
- contact-regime result.

## C. Improvements allowed without reopening Study 8

The following can be performed using frozen evidence only:

- new title;
- rewritten abstract;
- reorganized introduction;
- tighter contribution statement;
- updated and expanded related work;
- direct closest-prior-work comparison;
- revised section order;
- state-machine diagram;
- transition-object dependency diagram;
- logical contact-schedule schematic;
- improved captions and graphical abstract;
- stronger discussion of the feasibility-versus-state-cost distinction;
- consolidated limitations;
- concise reproducibility statement;
- venue-specific formatting and metadata.

No new numerical result is required for these changes.

## D. Improvements that would require a separate scientific extension

The following would constitute new scientific work and must not be inserted into frozen Study 8 without a new prospective protocol:

1. physical or TLE/orbit-derived contact schedules;
2. uplink/downlink directionality and real scheduling constraints;
3. certificate, framing, transport, coding, or retransmission overhead;
4. onboard ML-KEM/ML-DSA latency, memory, power, or energy measurement;
5. an adaptive policy that changes object ordering, pre-staging, retransmission, or contact allocation rather than only gating commit;
6. adaptive attack schedules;
7. hardware-in-the-loop validation;
8. external independent implementation/replication.

If the author later chooses this route, create a separately identified extension study. Do not rewrite the original 3,456-position population.

## E. Publication-quality judgment

### Manuscript-only path

**Status:** viable for retargeting after substantial editorial restructuring.

The frozen evidence supports a defensible systems/networking paper if the manuscript is reorganized around:

> standardized post-quantum transition-object burden and contact timing determine the feasible recovery set, while transition policy primarily redistributes security-state and availability costs within that set.

The negative primary policy result remains visible and is part of the contribution.

### Scientific-extension path

**Status:** optional, not required to make the existing study publishable at a better-aligned venue.

A new realism/validation layer would materially broaden external validity and could support stronger engineering claims. It should be considered only if the desired venue requires physical-network or implementation evidence.

## F. Recommended retargeting strategy

Proceed in two controlled stages:

1. first, retarget the frozen Study 8 evidence through a substantially improved manuscript at a venue whose scope directly covers satellite networks, network protocols, security, and performance analysis;
2. only if that audit shows the venue requires stronger physical realism should a new extension study be designed and prospectively frozen.

Do not rerun Study 8 merely in response to the Acta rejection.

## Next gate

The live venue shortlist is recorded separately in:

`publication/Paper_4_Study_8/NEXT_VENUE_SHORTLIST_2026-09-19.md`

No venue is locked by this audit. Venue lock and venue-specific derivative-package creation require explicit author approval.
