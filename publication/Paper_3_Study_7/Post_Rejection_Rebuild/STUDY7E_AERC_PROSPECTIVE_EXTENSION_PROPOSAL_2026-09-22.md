# Study 7E Prospective Extension Proposal

**Proposed experiment ID:** `S7E-AERC-001`  
**Working title:** Architecture-Grounded Equal-Information Recovery Comparators Under Correlated Trust Failures  
**Status:** `PROPOSED__PROTOCOL_NOT_FROZEN__EXECUTION_NOT_AUTHORIZED`  
**Parent publication line:** Paper 3  
**Frozen antecedent:** `S7-LSO-001`

## 1. Motivation

Study 7 established a narrow information-sufficiency boundary, but the CEAS handling editor identified missing architecture grounding, unvalidated trust assumptions, and an unequal-information corroboration comparison.

Study 7E is proposed as a **new** prospective study. It must not modify Study 7.

## 2. Research questions

**RQ1.** In a concrete spacecraft recovery architecture, how do deterministic and learned recovery selectors differ when both receive exactly the same policy-visible evidence?

**RQ2.** How does explicit trust-domain separation of a corroborating evidence path change unsafe-recovery and false-hold outcomes for deterministic and learned policies?

**RQ3.** Under which common-cause compromise conditions does the benefit of corroboration collapse for both policy classes?

## 3. Reference architecture concept

Candidate implementation baseline: NASA cFS, optionally exercised within NOS3 after a feasibility gate.

Proposed components:

- command/authorization evidence producer;
- security-monitor evidence producer;
- evidence qualification service;
- cFS Health and Safety or equivalent health-state producer;
- corroboration producer located in a separately defined trust domain;
- cFE Software Bus for local messaging;
- Software Bus Network where cross-process/cross-processor separation is required;
- recovery-decision application;
- recovery-action interface/state machine;
- ground/mission-authorization simulator where required.

The architecture must map every policy-visible field to a concrete producer and message path.

## 4. Equal-information policy families

At minimum:

- `D0_BASE`: deterministic, base information set;
- `L0_BASE`: learned, same base information set;
- `D1_CORROBORATED`: deterministic, base + corroboration information;
- `L1_CORROBORATED`: learned, exactly the same base + corroboration information.

No learned policy may receive an observable that its paired deterministic comparator does not receive.

## 5. Trust-domain model

Prospectively define domains for:

- producer identity/provenance;
- signing/key authority;
- process/processor;
- transport;
- mission/ground authority.

The study must distinguish source independence from transport independence and authority independence.

Candidate topology classes:

- shared source/key domain;
- separate source and key domains on shared transport;
- separate source/key/execution domains;
- common-cause transport or authority compromise.

## 6. Scenario generation

Architecture states, failures, and compromise injections should generate policy observables. Do not manually set a hidden truth collision as the primary experiment mechanism.

Candidate scenario factors include:

- true recovery authorization state;
- security condition;
- primary evidence-producer compromise;
- corroborator compromise;
- shared key-authority compromise;
- transport/common-bus compromise;
- stale or missing evidence;
- architecture topology/trust-domain separation.

The exact finite population must be derived and frozen before execution.

## 7. Primary endpoints

- objective decision error;
- unsafe proceed / unsafe recovery authorization;
- false-conservative hold;
- deterministic-versus-learned disagreement under identical inputs;
- safety benefit from trust-domain separation;
- common-cause collapse of corroboration benefit.

Any availability or recovery-completion metric must be defined prospectively and must not be labeled operational spacecraft availability unless the experimental environment actually supports that claim.

## 8. Validation requirements

Before canonical execution:

1. unit tests for every architecture-to-observable mapping;
2. test that paired D/L policies receive byte-equivalent logical inputs;
3. test that research-only adjudication truth is never leaked into policy inputs;
4. fault-injection tests for each trust domain;
5. common-cause tests;
6. complete-population cardinality test if finite enumeration is used;
7. deterministic replay test;
8. independent/separately implemented audit plan;
9. hash/provenance manifest design;
10. frozen claim-boundary tests.

## 9. Claim boundaries

Study 7E must not claim:

- flight qualification;
- operational spacecraft safety probability;
- certification sufficiency;
- general ML superiority;
- empirical independence beyond the implemented trust-domain architecture;
- real RF or ground-link performance;
- hardware timing/energy/CPU results unless separately measured;
- external human replication from a same-repository audit.

## 10. Relationship to Study 7

Study 7 remains the exact 1,033-observation frozen information-sufficiency study.

Study 7E, if authorized and executed, will be a separate architecture-grounded population. A rebuilt Paper 3 may synthesize the two studies narratively, but their populations and provenance must remain separate.

## 11. Pre-execution gates

Execution is prohibited until the author explicitly approves:

- final reference architecture;
- whether cFS-only or cFS+NOS3 is feasible and justified;
- exact comparator definitions;
- exact trust-domain topology;
- scenario matrix and population cardinality;
- endpoints and expected invariants;
- implementation/test plan;
- independent-audit design;
- claim boundaries.

No new journal is locked at this stage.
