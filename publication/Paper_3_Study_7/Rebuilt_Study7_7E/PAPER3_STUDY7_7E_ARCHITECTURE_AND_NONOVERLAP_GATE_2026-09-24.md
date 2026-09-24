# Paper 3 — Study 7 + Study 7E Architecture and Cross-Publication Non-Overlap Gate

**Gate date:** 2026-09-24  
**Gate status:** `PASS__PAPER3_STUDY7_PLUS_STUDY7E_ARCHITECTURE_LOCKED__VENUE_NEUTRAL_MANUSCRIPT_INTEGRATION_AUTHORIZED`  
**Base main commit:** `740cc4984387b2c4f14b337b76d66198406f22c4`  
**Studies:** Study 7 / S7-LSO-001 and Study 7E / S7E-AERC-001

## 1. Author decision

The rebuilt Paper 3 will combine two separately frozen studies in one manuscript:

1. **Study 7 / S7-LSO-001** — the information-sufficiency and observability foundation; and
2. **Study 7E / S7E-AERC-001** — the prospectively designed architecture-grounded equal-information extension.

The studies remain separate experimental populations. No pooled N, pooled error rate, pooled denominator, combined confidence interval, or retroactive protocol change is permitted.

The rejected CEAS package remains immutable provenance and is not edited by this rebuild.

## 2. Scientific lane

The rebuilt paper asks how recovery-decision assurance depends jointly on:

- what information is visible to the selector;
- whether deterministic and learned comparators receive the same information;
- how corroborating evidence is instantiated across explicit trust domains;
- how common-cause compromise propagates through shared domains; and
- how learned selectors behave on fault classes and trust topologies excluded from training.

Study 7 establishes that exact learning of a visible decision boundary does not resolve a hidden-truth collision when decisive truth is absent from the visible state. Study 7E then removes the principal application-specific limitations of that abstract construction by using a cFS-grounded reference architecture, explicit source/key/execution/transport/authority domains, equal-information deterministic/learned policy pairs, frozen faults, and held-out fault/topology evaluation.

## 3. Evidence separation

### Study 7

Frozen population:

- Block A: 512 observations;
- Block B: 512 observations;
- Block C: 9 observations;
- total: 1,033 observations.

Frozen role in Paper 3:

- establish the visible-information boundary;
- show that L0 exactly reproduces the visible decision rule but does not escape the hidden-truth collision;
- show that added corroboration changes information availability;
- show correlated false corroboration restores the unsafe condition.

### Study 7E

Frozen held-out population:

- E1 unseen faults: 84 scenarios;
- E2 held-out topologies: 104 scenarios;
- C0 no-signal controls: 8 scenarios;
- total: 196 scenarios;
- four policies per scenario;
- 784 policy decisions;
- invalid scenarios: 0;
- audit mismatches: 0.

Frozen role in Paper 3:

- compare D0/L0 and D1/L1 under byte-identical paired inputs;
- instantiate five explicit trust-domain dimensions;
- evaluate F0-F12 fault/compromise profiles;
- measure exact unsafe-proceed and false-conservative behavior;
- test common-cause collapse and topology/fault transfer;
- retain adverse and null findings.

## 4. Combined contribution

The manuscript may make the following combined argument:

> Recovery-decision assurance is constrained first by information sufficiency and then by the architecture that produces, separates, and can jointly compromise that information. Study 7 isolates the observability boundary; Study 7E shows that, even after comparator information is equalized and trust domains are made explicit, corroboration and greater domain separation do not produce a universal or monotonic policy-level benefit.

This is not a claim of global deterministic superiority, global ML superiority, or universal corroboration benefit.

## 5. Separation from Paper 1

Paper 1 / Studies 1+2 concerns deterministic mission-aware response and trusted recovery under contact, evidence, and adversarial conditions. Its V5 treatment is an antecedent specification for the signed-but-false evidence problem.

Paper 3 must not reuse Paper-1 observations as new evidence, claim V5 as a new discovery, or restate Paper-1 quantitative results as Paper-3 results.

Paper 3 is distinct because it evaluates learned-selector information sufficiency and, in Study 7E, equal-information deterministic-versus-learned behavior across explicit trust-domain topologies and held-out architecture faults.

**Overlap determination:** manageable with explicit antecedent citation and no data reuse.

## 6. Separation from Paper 2

Paper 2 / Studies 3+4+6 concerns temporal evidence persistence, producer/provenance composition, quorum behavior, and recovery-artifact assurance.

Paper 3 must not claim provenance diversity, quorum composition, or independent evidence as newly invented concepts. Study 7E uses explicit trust-domain separation to test selector behavior, not to recreate Paper-2 quorum theory or reuse Paper-2 populations.

**Overlap determination:** low to moderate concept overlap; experimental evidence and endpoints remain distinct.

## 7. Separation from rebuilt Paper 4

Rebuilt Paper 4 / Studies 8+8E concerns cryptographic-transition burden and trusted post-compromise recovery feasibility under intermittent contact, including external observation-opportunity timing.

Paper 3 does not evaluate ML-KEM/ML-DSA transition burdens, minimum effective payload rates, SatNOGS timing, or P0-P3 transition policies.

**Overlap determination:** low.

## 8. Separation from Paper 5

Paper 5 / Study 9 concerns recovery-state semantic interoperability and downstream decision identifiability across public space-cyber datasets.

Paper 3 does not map public datasets into recovery semantics, compute sidecar-state requirements, or use CuCD-ID, AegisSat, or UNSW-IoTSAT as evidence.

**Overlap determination:** low.

## 9. Study 7 versus Study 7E integration rules

The manuscript must:

- identify the studies separately in Methods and Results;
- never report 1,033 + 196 or 1,033 + 784 as a combined sample size;
- distinguish Study-7 model labels from Study-7E policy labels;
- state that Study 7E is a new prospective extension rather than a rerun of Study 7;
- preserve Study-7 corroboration as a stipulated model variable;
- preserve Study-7E separation as instantiated experimental domain identifiers, not certification-grade independence;
- state that cFS runtime qualification grounds architecture contracts but the canonical held-out learned-policy inference uses the frozen Python/joblib execution and an independent semantic-tree audit rather than a flight-certified onboard ML runtime;
- preserve all adverse and null findings;
- avoid significance testing for the complete finite populations;
- avoid global policy rankings.

## 10. Gate decision

**GO:** `GO__REBUILD_PAPER3_AS_STUDY7_PLUS_STUDY7E_TWO_STUDY_FULL_ARTICLE`

The former concise Technical Note architecture is superseded for the rebuild. The new evidence justifies a full research-article structure because the paper now contains an abstract information-sufficiency foundation plus a separately designed architecture/fault/topology evaluation.

No venue is locked by this gate. Venue assessment must occur after the venue-neutral scientific manuscript is internally stable.

## 11. Hard prohibitions

Do not:

- modify the rejected CEAS package;
- alter either frozen study;
- rerun either canonical scientific campaign;
- tune Study-7E models after held-out evaluation;
- pool Study 7 and Study 7E;
- rank policies globally;
- claim operational spacecraft safety probabilities;
- claim NASA endorsement, flight qualification, or certification sufficiency;
- imply that more trust-domain separation is monotonically safer;
- omit the adverse L1 transfer findings or C0 null result;
- submit to a publisher without separate explicit authorization.
