# Paper 4 / Study 8 Venue-Neutral Manuscript Rebuild Plan

**Date:** 2026-09-19  
**Status:** `RETARGET_REBUILD_PLAN_READY__VENUE_NOT_LOCKED`  
**Scientific basis:** frozen Study 8 / `S8-PQC-ICR-001` only

## Rule

This plan does not modify:

- the frozen Study 8 science;
- the frozen target-neutral publication package;
- the rejected Acta package;
- the primary endpoint;
- the primary null result;
- any canonical numeric result.

It defines how a new derivative manuscript can present the existing evidence more effectively.

## Recommended scientific center

The rebuilt paper should be organized around this statement:

> Under the frozen intermittent-contact model, standardized post-quantum transition-object burden, contact timing, and recovery deadline determine the feasible trusted-recovery set, while transition policy primarily redistributes security-state and availability costs within that set.

The prespecified P3-versus-P1 null remains explicitly identified as the primary policy result.

## Recommended title

### Preferred

**Post-Quantum Trusted Recovery Under Intermittent Satellite Contact: Feasibility Limits from Cryptographic Object Burden and Timing**

### Alternative 1

**Feasibility and State Tradeoffs in Post-Quantum Satellite Recovery Under Intermittent Contact**

### Alternative 2

**Trusted Post-Compromise Cryptographic Recovery for Satellite Networks Under Finite Contact Budgets**

Avoid leading the title with "contact-aware" because the frozen contact-aware policy does not improve the primary success endpoint.

## Abstract candidate

Long-lived satellite systems may need to replace compromised cryptographic state despite intermittent connectivity and finite recovery windows. This study evaluates trusted post-compromise transition as an exhaustive deterministic design-space problem using standardized ML-KEM and ML-DSA object sizes. A frozen factorial model crosses three cryptographic profiles, four recovery policies, four equal-total-capacity contact regimes, four bounded disruptions, six compromise offsets, and three logical deadlines, yielding 3,456 modeled positions. The prespecified primary policy result is negative: all four policies restore modeled trust in 635/864 positions (73.4954%), and the contact-aware staged-minus-staged success difference is exactly 0 percentage points in every prespecified stratum. Feasibility instead changes sharply with transition-object burden. Success is 93.7500%, 64.9306%, and 61.8056% across the three increasing object bundles, and is non-increasing with object burden in all 1,152 matched non-profile positions. Contact timing also matters: regimes with the same 65,536-byte complete-cycle capacity produce different deadline-constrained success, while longer logical deadlines expand the feasible set. Policy choice remains consequential through predecessor exposure, control unavailability, dual-epoch overlap, modeled transfer use, transition attempts, and failure classification. The results separate recovery feasibility from transition-state cost and show why post-quantum migration planning for intermittently connected satellite systems should account for both cryptographic-object burden and when contact capacity becomes available.

## Contribution statement

The rebuilt introduction should state three contributions clearly.

1. **Trusted-recovery design-space model.** An exhaustive deterministic model couples post-compromise epoch transition, exact NIST-standardized ML-KEM/ML-DSA object sizes, intermittent logical contact, deadlines, and bounded non-cryptanalytic disruption.

2. **Feasibility result.** Standardized transition-object burden and contact timing change the deadline-feasible recovery set even when complete-cycle capacity is held constant.

3. **Feasibility-versus-state-cost separation.** The four tested policies are identical on the primary success proportion but differ in predecessor exposure, control unavailability, overlap, transfer use, attempts, and terminal failure classification.

Do not claim that larger cryptographic profiles are weaker or worse cryptographically. The result concerns transfer burden only.

## Recommended manuscript architecture

### 1. Introduction

- satellite/PQC transition problem;
- post-compromise recovery gap;
- closest prior work;
- research question;
- three contributions;
- explicit statement that the primary policy comparison is prespecified and retained even though null.

### 2. Related Work

Use four compact categories:

1. satellite PQC algorithm and implementation studies;
2. quantum-safe handshake/key-management work for satellite/NTN environments;
3. crypto-agility and migration guidance;
4. satellite cybersecurity and recovery-state context.

End with a closest-work paragraph explaining the exact gap.

### 3. Recovery Model

Lead with a visual.

- state machine;
- predecessor/successor acceptance semantics;
- seven transition objects and dependency order;
- policy definitions.

### 4. Intermittent Contact and Exhaustive Design

- four contact regimes;
- equal 65,536-byte complete-cycle capacity;
- six offsets;
- three deadlines;
- four disruptions;
- complete 3,456-position factorial population;
- exact finite-population reporting policy.

### 5. Results

#### 5.1 Prespecified primary policy result

Report the exact null concisely.

Use "0.000000 percentage points" in prose. Retain `0/1` in traceability records.

#### 5.2 Object-burden feasibility

Make this the main quantitative results subsection.

#### 5.3 Contact timing and deadline

Emphasize equal total capacity but different feasibility.

#### 5.4 State and availability tradeoffs

Present P0/P1/P2/P3 distinctions.

#### 5.5 Invariant checks

Keep structural zeros clearly bounded.

### 6. Systems Interpretation

Organize around mechanisms:

- capacity cannot be created by a commit guard;
- larger required objects consume more finite opportunity;
- temporal placement of capacity matters under deadlines;
- policy semantics matter even without changing terminal feasibility.

### 7. Limitations and External Validity

Consolidate boundary language here rather than repeating it throughout the manuscript.

### 8. Conclusion

One concise systems lesson, no operational overreach.

## Visual rebuild

### Figure 1: Trusted-recovery state machine

Show:

`COMPROMISED -> RECOVERY_AUTHORITY_ESTABLISHED -> SUCCESSOR_CRYPTO_PROFILE_SELECTED -> SUCCESSOR_KEY_MATERIAL_STAGED -> TRANSITION_PROOF_ACCEPTED -> NEW_EPOCH_COMMITTED -> OLD_EPOCH_REVOKED -> TRUST_RESTORED`

Overlay predecessor/successor acceptance changes for P0-P3.

### Figure 2: Transition-object dependency and byte-burden schematic

Show the seven fixed-priority objects and the three profile totals:

- 12,560 bytes;
- 17,460 bytes;
- 24,236 bytes.

State clearly that these are standardized cryptographic-object bytes only.

### Figure 3: Equal-capacity contact schedules

Show the four 48-slot logical schedules with the same 65,536-byte complete-cycle capacity.

This figure should make the "same total capacity, different temporal opportunity" result immediately understandable.

### Figure 4: Profile success

Reuse or redesign the frozen profile-success visualization without changing values.

### Figure 5: Contact-regime success

Reuse or redesign the frozen regime-success visualization without changing values.

## Graphical table-of-contents concept

For a Wiley satellite-network venue, combine:

- three increasing PQC object bundles on the left;
- four intermittent contact patterns in the center;
- trusted-recovery state progression on the right;
- a simple message: larger transition bundles and delayed capacity reduce the deadline-feasible set, while policy changes state cost rather than overall success.

Do not include new derived numbers in the graphical abstract.

## Literature refresh priorities

The rebuilt paper should explicitly include and distinguish at least:

- NIST FIPS 203 and 204;
- NIST SP 800-227;
- NIST CSWP 39 crypto-agility guidance;
- Ghosh and Nath 2026, satellite PQC algorithm/performance analysis;
- Eichen et al. 2026, constrained/NTN PQ authentication and key-management pressure;
- De Zuane et al. 2026, quantum-safe IKE for satellite communications;
- Mähn, Müller, and Zielinski, space-system crypto-agility definitions;
- relevant satellite cybersecurity/network-security literature.

Any preprint must be labeled as a preprint unless a peer-reviewed version is verified.

## Prose changes

### Reduce

- repository hashes in the Abstract and Results;
- repeated "not measured" statements;
- repeated finite-population defense;
- internal phase/freeze terminology in the reader-facing narrative;
- machine-oriented fraction notation where ordinary journal notation is clearer.

### Preserve

- exact primary null;
- all negative and conditional findings;
- distinction between modeled bytes and physical network throughput;
- logical-slot boundary;
- same-repository reproduction boundary;
- no operational spacecraft claim.

## Study-strengthening option

No additional study is required for a careful retarget.

If the author later chooses to strengthen external validity, do it as a new prospectively frozen extension rather than changing Study 8. The highest-value extension would combine:

1. representative physical/orbit-derived contact opportunities;
2. concrete protocol/framing/certificate overhead;
3. directional transfer constraints;
4. at least one policy that actually changes scheduling or pre-staging behavior;
5. optionally, implementation measurements.

That extension would answer a different question and must receive its own experiment identifier and frozen analysis plan.

## Next gate

Obtain explicit author venue-lock approval.

After venue lock, create a new venue-specific derivative directory and build the revised manuscript from frozen evidence only.
