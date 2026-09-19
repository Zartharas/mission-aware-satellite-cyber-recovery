# Study 8 Retarget Manuscript Revision Blueprint

**Date:** 2026-09-19  
**Study:** `S8-PQC-ICR-001`  
**Roadmap publication label:** Paper 4  
**Status:** `PUBLICATION_LAYER_REVISION_BLUEPRINT__NO_SCIENCE_CHANGE`

## Purpose

This blueprint defines how to improve the rejected Acta manuscript without changing the frozen Study 8 science. It is not a new scientific protocol and does not authorize reexecution or statistical reanalysis.

The exact Acta package remains historical evidence of what was submitted as `AA-D-26-02872`.

## Candidate title

**Post-Compromise Post-Quantum Cryptographic Transition Under Intermittent Satellite Contact: Feasibility and State-Cost Tradeoffs**

Why this is stronger than the Acta title:

- it does not make the P3 contact-aware policy appear to be the sole contribution;
- it places the post-compromise transition problem first;
- it names the satellite-network constraint directly;
- it previews the paper's two distinct result dimensions: terminal feasibility and transition-state cost.

## Candidate retarget abstract

Post-quantum migration in satellite networks is often evaluated through algorithm or handshake performance, but post-compromise recovery also depends on whether successor cryptographic state can traverse intermittent contact opportunities before a recovery deadline. This study models that problem as a complete deterministic finite population of 3,456 positions crossing three exact ML-KEM/ML-DSA profiles, four transition policies, four equal-total-capacity contact regimes, four bounded non-cryptanalytic disruptions, six compromise offsets, and three logical deadlines. All four policies achieved the same trusted-recovery proportion, 635/864 (73.4954%), and the prespecified contact-aware staged-minus-staged difference was 0.000000 percentage points in every prespecified stratum. Feasibility instead varied with standardized cryptographic-object burden: success was 93.7500%, 64.9306%, and 61.8056% for the three profiles and was non-increasing with object burden across all 1,152 matched non-profile positions. Contact placement and deadline also changed feasibility despite equal full-cycle nominal capacity. Policy choice did not enlarge the terminal feasible set under the frozen common object bundle and scheduler, but it redistributed predecessor exposure, control unavailability, dual-epoch overlap, transfer use, attempts, and failure classification. The results separate two satellite-network transition questions: whether required cryptographic material fits within a finite contact/deadline envelope and what security-state and availability costs are incurred while attempting the transition. The model concerns logical contact opportunities and standardized cryptographic-object bytes, not physical-link or onboard execution performance.

**Word count:** 211.

## Revised contribution hierarchy

The next manuscript should state four contributions clearly and early.

### C1. Finite post-compromise transition model

A complete deterministic finite model couples standardized ML-KEM/ML-DSA transition-object burden with intermittent logical contact, deadline, epoch-state semantics, and bounded disruption.

### C2. Feasibility result

Object burden, contact placement, and deadline change the frozen terminal feasible set. The matched-profile result is especially strong: success is non-increasing with the frozen standardized object bundle across all 1,152 matched non-profile positions.

### C3. Negative policy result with mechanism

All four policies have identical terminal success in the frozen population. The study should explain early that every policy shares the same required object bundle and priority scheduler, so the experiment isolates acceptance/revocation semantics rather than comparing different wire protocols. The null result therefore says that these semantics did not enlarge the terminal feasible set under the frozen design.

### C4. State-cost decomposition

Policy remains consequential because it redistributes predecessor exposure, control unavailability, dual-epoch overlap, modeled transfer use, attempts, and terminal failure classification.

## Proposed manuscript structure

### 1. Introduction

Reduce generic PQC-for-space background.

Use this logic:

1. satellite and NTN environments can have intermittent or constrained communication opportunities;
2. post-quantum transition objects can be large;
3. prior work studies algorithms, implementation, handshake overhead, migration, and crypto agility;
4. after compromise, a distinct question remains: can successor trust state be established before a deadline under intermittent contact?
5. define the paper's two questions: terminal feasibility and transition-state cost;
6. state the four contributions above;
7. state the negative primary policy result up front.

### 2. Related work

Organize around three interfaces rather than broad topic buckets:

1. **PQC for satellite/NTN systems**
2. **Key management under disrupted or delay-tolerant connectivity**
3. **Crypto agility and post-compromise transition**

End with an explicit gap paragraph explaining that Study 8 does not compete with hardware benchmark papers; it studies the state-transition/contact-budget interaction.

### 3. Model and methods

Retain the frozen design exactly.

Improve readability by distinguishing:

- **scientific factors:** profile, policy, contact regime, disruption, offset, deadline;
- **shared mechanism:** required object bundle and deterministic priority scheduler;
- **policy-specific mechanism:** acceptance/revocation/overlap/gating semantics;
- **model boundary:** logical slots and synthetic byte opportunities.

No physical time conversion is allowed.

### 4. Results

Reorganize around mechanisms rather than the original factor sequence.

#### 4.1 Terminal feasible set and exact policy equivalence

Lead with 635/864 for all policies and the zero P3-P1 contrast.

Immediately connect this result to the common-bundle/common-scheduler design.

#### 4.2 Object-burden feasibility boundary

Report the three exact profile proportions and the 1,152/1,152 non-increasing matched ordering.

Do not call a lower-burden profile "better" or recommend weaker cryptography.

#### 4.3 Contact placement and deadline

Show that equal full-cycle nominal capacity does not imply equal deadline-constrained feasibility.

Do not call this a physical link-performance result.

#### 4.4 Transition-state costs

Present predecessor exposure, control-unavailable slots, P2 overlap, transfer/attempt burden, and failure classifications as a separate design dimension.

#### 4.5 Structural invariants

Keep stale-epoch acceptance and rollback structural zeros clearly labeled as invariant checks.

### 5. Discussion

Lead with the feasibility-versus-state-cost separation.

Then discuss:

- why P3 does not create capacity;
- why a guard can reduce wasted modeled resources or reclassify failure without improving terminal success;
- why larger standardized objects shrink the frozen feasible set;
- why contact timing matters even when total-cycle capacity is controlled;
- how this informs protocol/planning analysis without constituting RF or spacecraft-performance evidence.

### 6. Limitations

Retain all existing limitations.

Consider grouping them as:

1. contact abstraction;
2. cryptographic-object accounting;
3. adversary and protocol abstraction;
4. external-validity/reproduction boundary.

### 7. Conclusion

Do not end with "one policy wins."

End with the two-dimensional result:

- feasibility is constrained by material burden, contact placement, and deadline;
- policy semantics determine transition-state cost within that feasibility envelope.

## Literature additions to verify before freeze

The revised literature review should consider adding, after exact bibliographic verification:

1. Menesidou et al., **Cryptographic Key Management in Delay Tolerant Networks: A Survey**, Future Internet, 2017.
2. **Automated key exchange protocol evaluation in delay tolerant networks**, Computers & Security, 2016.
3. **Experimental evaluation of PQ-WireGuard and PQ-IPsec over LEO satellite networks**, ICT Express, 2026.
4. Current NIST `CSWP 39-upd1`, not the withdrawn predecessor.
5. Current GSMA PQ.07 NTN migration guidance.
6. Ghosh and Nath 2026 in International Journal of Satellite Communications and Networking.
7. Kim 2026 systematic survey in Acta Astronautica.
8. Eichen et al. 2026, retained explicitly as a preprint if still unpublished at package freeze.
9. Mähn, Müller, and Zielinski 2025 on crypto-agility definitions for space systems.

The literature review must distinguish peer-reviewed papers, standards/guidance, conference material, and preprints.

## Visual revision

A revised package should include a simple publication-layer schematic that explains:

**standardized transition-object bundle -> intermittent contact/deadline envelope -> terminal feasibility**

and separately:

**policy acceptance/revocation semantics -> predecessor exposure / unavailability / overlap / failure classification**

The schematic must be derived solely from frozen model definitions and findings. It must not depict real orbital geometry, RF performance, spacecraft hardware, or measured timing.

## Venue-specific requirements if IJSCCN is later locked

Current journal instructions should be rechecked again at package freeze, but the 2026-09-19 live review identified:

- editable manuscript required;
- free-format initial submission available;
- abstract up to 250 words;
- up to eight keywords;
- data-availability statement required;
- public repository for supporting data expected;
- graphical table of contents required;
- GTOC text limited to 80 words or three sentences;
- numbered reference style for final journal presentation;
- author biography requested;
- Wiley AI-use disclosure must be aligned to current policy.

## Hard boundaries

No retarget revision may:

- alter `3,456` as the frozen population;
- alter any canonical count or proportion;
- replace or demote the prespecified P3-P1 primary contrast;
- add sampling p-values/confidence intervals;
- infer physical time from logical slots;
- infer RF, orbit, CPU, energy, thermal, flight, or ground-station performance;
- claim external replication;
- modify the rejected Acta package;
- modify scientific Study 4 / `S4-MPQ-001`, which is already consumed by the active TAES Paper 2 submission.

Final publisher submission remains separately gated.
