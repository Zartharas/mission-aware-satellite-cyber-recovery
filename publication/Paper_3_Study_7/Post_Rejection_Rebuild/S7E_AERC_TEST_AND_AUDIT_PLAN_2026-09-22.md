# S7E-AERC-001 Test and Independent-Audit Plan

**State:** `DRAFT__NO_EXECUTION_AUTHORIZATION`  
**Date:** 2026-09-22

## 1. Test-driven development rule

Implementation must be built against tests derived from the prospective protocol. No canonical result is accepted unless every required pre-canonical test passes at the authorized commit.

## 2. Contract-test groups

### A. Architecture contracts

- every topology resolves to exactly two evidence-path domain maps;
- T0 aliases all five trust domains;
- T1 separates source/execution only;
- T2 additionally separates keys;
- T3 additionally separates transport;
- T4 additionally separates authority;
- no topology changes policy feature schema.

### B. Evidence contracts

For every snapshot:

- feature order is canonical;
- boolean encoding is canonical;
- signature validity is derived from verification;
- freshness is derived from controlled time;
- completeness is derived from message presence;
- authorization is extracted from evidence payload;
- research truth/fault/topology labels are absent.

### C. Equal-information contracts

For each scenario:

- SHA256(D0_input) == SHA256(L0_input);
- SHA256(D1_input) == SHA256(L1_input);
- D0/L0 input length and schema identical;
- D1/L1 input length and schema identical.

Any violation invalidates the entire canonical run.

### D. Truth-leakage contracts

Static and runtime checks must demonstrate that policy modules cannot import/read:

- adjudicator truth;
- objective action;
- fault profile;
- topology ID;
- expected propagation set.

### E. Fault-propagation contracts

For each F1-F12 and T0-T4:

- compute expected affected domains from topology aliases;
- inject fault;
- observe affected producers/transports;
- compare actual vs expected propagation.

Every topology/fault pair requires a golden expected propagation test before canonical execution.

### F. Scenario-cardinality contracts

Assert:

- TR1 = 72;
- TR0 = 12;
- total training = 84;
- E1 = 84;
- E2 = 104;
- C0 = 8;
- total manifest = 280;
- canonical evaluation scenarios = 196;
- decisions per canonical scenario = 4;
- canonical evaluation decision observations = 784.

### G. Policy contracts

D0 and D1 require exhaustive unit tests across their input schemas.

L0 and L1 tests must verify:

- fixed feature ordering;
- fixed model hash;
- deterministic prediction;
- refusal to load mismatched model artifacts.

### H. Replay contracts

A preregistered sample of scenarios from every topology and fault profile must be replayed at least twice before the canonical run. Feature hashes and decisions must match exactly.

## 3. Independent audit design

The independent audit must be a separately implemented repository auditor, not a call into production analysis code.

It must recompute from raw canonical artifacts:

1. scenario cardinalities;
2. block membership;
3. objective action from research truth;
4. topology alias relationships;
5. expected fault propagation;
6. B/C feature projections;
7. paired-input hash equality;
8. D0 and D1 decisions from independent rule implementations;
9. L0/L1 predictions from frozen serialized models or independently parsed tree structure;
10. objective error;
11. unsafe proceed;
12. false-conservative hold;
13. policy disagreement counts;
14. topology/fault stratified summaries;
15. artifact hashes.

The audit must report exact mismatch counts. Acceptance requires zero unexplained mismatches.

## 4. Analysis anti-leakage design

Canonical analysis code may read adjudication truth only after decision records are immutable.

Training code must not read E1/E2/C0 labels before model freeze.

The workflow should physically separate:

- training artifacts;
- frozen models;
- evaluation evidence;
- evaluation decisions;
- post-evaluation truth join.

## 5. Failure handling

No silent retry may overwrite a failed canonical run.

If infrastructure fails:

- retain the failed run;
- classify infrastructure vs scientific failure;
- repair under a new commit;
- require a new canonical-execution authorization if the authorized code/config changed.

If a protocol defect is discovered after freeze but before execution, unfreeze by explicit author decision, revise protocol, and create a new protocol version.

If discovered after canonical execution, do not rewrite results in place; create a corrected experiment/result version with explicit invalidation provenance.

## 6. Reviewer-facing reproducibility evidence

A future publication package should expose:

- protocol version;
- exact source commit;
- environment lock;
- scenario manifest;
- topology/fault definitions;
- frozen model hashes;
- canonical workflow/run identifiers;
- raw decision table;
- independent audit report;
- Zenodo archive if authorized after results freeze.

The audit must be described as implementation-independent repository verification, not external human replication.
