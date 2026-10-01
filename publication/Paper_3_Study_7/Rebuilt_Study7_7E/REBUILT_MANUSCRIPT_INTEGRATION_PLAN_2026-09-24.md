# Rebuilt Paper 3 — Study 7 + Study 7E Manuscript Integration Plan

**Plan date:** 2026-09-24  
**State:** `AUTHORIZED__VENUE_NEUTRAL_INTEGRATION_IN_PROGRESS`  
**Paper:** Paper 3  
**Studies:** S7-LSO-001 + S7E-AERC-001

## 1. Working title

**Architecture-Grounded Trust Separation for Satellite Cyber-Recovery Decisions Under Compromised Evidence**

Alternative title for later venue fit:

**From Observability Limits to Architecture-Grounded Trust Separation in Satellite Cyber-Recovery Decisions**

No title is publisher-locked at this stage.

## 2. Core contribution statement

The paper should establish a two-layer assurance result:

1. Study 7 shows that exact learning of a visible recovery-decision boundary cannot resolve a hidden-truth collision when decisive truth is absent from the selector's observable state.
2. Study 7E prospectively grounds the question in a cFS-based recovery architecture, equalizes information between deterministic and learned comparators, instantiates source/key/execution/transport/authority trust domains, and evaluates unseen faults and held-out topologies.
3. The combined evidence shows that selector behavior and trust architecture interact: corroboration and greater domain separation can alter safety/availability outcomes, but their effects are policy- and fault-dependent rather than universally beneficial.

## 3. Research-question placement

### Foundation question — Study 7

How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and what changes when a corroborating observable is added?

### Study-7E RQ1 — equal information

How do deterministic and learned recovery selectors differ when paired policies receive exactly the same policy-visible evidence?

### Study-7E RQ2 — trust separation

How does explicit separation of source, signing-key, execution, transport, and authorization domains change unsafe-recovery and false-conservative outcomes?

### Study-7E RQ3 — common cause

Under which shared-domain/common-cause compromises does corroboration benefit collapse?

### Study-7E RQ4 — held-out transfer

How do frozen learned selectors behave on fault classes and higher-separation trust topologies excluded from training?

## 4. Section architecture

1. Abstract
2. Introduction
3. Related Work and Assurance Boundary
4. Two-Study Research Design
   - Study 7 information-sufficiency experiment
   - Study 7E cFS-grounded architecture
   - equal-information policy contracts
   - trust topologies and faults
   - frozen learner/training/evaluation protocol
   - validity and independent audit
5. Results
   - Study 7 exact observability results
   - Study 7E aggregate outcomes
   - equal-information disagreements
   - topology-controlled trust-separation analysis
   - common-cause and adverse transfer cases
   - hypothesis disposition
6. Discussion
   - information versus model class
   - trust separation versus policy behavior
   - safety/availability trade-offs
   - implications for assurance
7. Limitations
8. Reproducibility and Data/Code Availability
9. Conclusion
10. References

## 5. Table plan

- Table 1: separate Study-7 and Study-7E designs/populations.
- Table 2: Study-7 policy/input boundary and exact outcomes.
- Table 3: Study-7E trust topologies.
- Table 4: Study-7E aggregate policy outcomes.
- Table 5: Study-7E E1/E2/C0 outcomes.
- Table 6: topology-controlled F6-F12 results.
- Table 7: frozen hypothesis disposition.

Tables must not contain a global winner column.

## 6. Figure plan

### Figure 1 — architecture-grounded evidence path

Show:

primary producer -> signed evidence -> qualifier -> base snapshot -> D0/L0  
corroboration producer -> signed evidence -> qualifier -> extended snapshot -> D1/L1  
health/readiness -> snapshot  
decision application -> recovery-action sink  
research-only adjudicator/fault controller outside policy-visible paths  
cFE Software Bus and SBN where applicable.

Visually distinguish policy-visible paths from research-only truth.

### Figure 2 — trust-domain topology ladder

Show T0 through T4 with progressive separation of source, key, execution, transport, and authority. Caption must state that separation denotes experimental domain identifiers/instances, not certification-grade independence.

### Figure 3 — two-study evidence chain

Show Study 7 as information-sufficiency foundation and Study 7E as architecture-grounded prospective extension. Do not display a pooled N.

### Figure 4 — safety/availability trade-off

Plot exact unsafe-proceed and false-conservative counts by policy, preferably faceted or separately labeled by E1/E2. Do not convert to a single scalar score.

## 7. Claim discipline

Every quantitative claim must be traceable to one frozen study. Cross-study claims are interpretive synthesis only and must not create a new pooled statistic.

Required adverse findings:

- D1 has the lowest aggregate unsafe-proceed count but the highest false-conservative count and total error count.
- L1 has the highest aggregate unsafe-proceed count and lowest false-conservative count.
- in the common F6-F12 subset, L1 unsafe proceeds rise from 3/28 at T0 to 6/28 at T4;
- F12 yields an L1 unsafe proceed at T1-T4 while L0 remains error-free;
- C0 is a complete null/control result with all policies HOLD and zero error.

## 8. Literature strategy

Retain the prior manuscript's distinction between downstream recovery authorization and upstream anomaly detection.

Use existing repository-vetted sources for:

- SPARTA cyber-safe mode;
- NASA learning-enabled-component assurance;
- partial observability / latent-state safety context;
- OPS-SAT and satellite telemetry ML as adjacent detector literature;
- NASA cFS/cFE/HS/SBN and NOS3 as reference-architecture sources.

Do not describe NASA architecture sources as validating Study-7E scientific conclusions.

A live literature and venue review should be performed after the venue-neutral manuscript reaches internal scientific stability.

## 9. Article-form decision

**Recommendation:** full research article.

Rationale:

- Study 7 alone supported a concise note;
- Study 7E adds a prospectively frozen architecture, fault model, trust-topology matrix, model-freeze process, held-out evaluation, and adverse-transfer analysis;
- compressing both studies into the prior Technical Note format would understate the architecture and trust-validation evidence that the CEAS editor found missing.

## 10. Next quality gates

Before venue lock:

1. complete venue-neutral R1 manuscript;
2. perform claim-to-source audit;
3. perform cross-paper self-overlap audit;
4. perform references and terminology audit;
5. verify all tables against frozen JSON;
6. ensure adverse/null findings remain visible;
7. verify no pooled population or global ranking appears;
8. run repository CI on the manuscript integration branch.

Publisher submission remains separately gated.
