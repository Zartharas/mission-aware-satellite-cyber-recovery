# S7E-AERC-001 Implementation Plan

**State:** `DESIGN_ONLY__NO_SCIENTIFIC_EXECUTION_AUTHORIZED`  
**Date:** 2026-09-22  
**Protocol:** `S7E_AERC_PROTOCOL_DRAFT_2026-09-22.md`

## 1. Engineering objective

Implement the prospective Study-7E protocol as a reproducible cFS-grounded research testbed in which architecture states and controlled fault/compromise injections generate the exact evidence consumed by paired deterministic and learned recovery policies.

The implementation must preserve a hard separation between:

- research-only truth/fault control;
- flight-software-visible evidence;
- policy decisions;
- post-run analysis.

## 2. Environment gate

Before implementation begins, pin exact immutable revisions for:

- NASA cFS bundle;
- cFE;
- OSAL;
- PSP;
- HS;
- SBN;
- NOS3, if feasibility passes;
- compiler/toolchain;
- Linux/container base image;
- Python analysis environment;
- ML library.

Record license obligations for every external component.

No canonical run may depend on floating branches such as `main`.

## 3. cFS/NOS3 feasibility gate

### Gate A: cFS-only baseline

Must demonstrate:

- cFS builds and runs on the controlled Linux environment;
- custom applications can publish/subscribe through cFE Software Bus;
- HS state can be observed;
- two cFS instances can exchange messages through SBN;
- deterministic scenario identifiers survive end-to-end;
- action sink telemetry can be captured.

### Gate B: NOS3 integration

If NOS3 can be pinned and built reproducibly:

- use NOS3 as canonical integration/simulation harness;
- select a maintained ground system supported by the pinned NOS3 version;
- use NOS3 command/telemetry paths for scenario control and capture where practical;
- use simulator/hardware-model hooks only where they materially support the experiment.

If NOS3 introduces non-reproducible or excessive environment risk, canonical Study 7E may use cFS-only multi-instance simulation, but the deviation must be author-reviewed before protocol freeze.

## 4. Proposed repository layout after implementation authorization

No files in this layout should be created merely by this design document.

```text
study7e/
  README.md
  STUDY7E_PROTOCOL.json
  configs/
    environment_lock.json
    topology_manifest.json
    fault_profiles.json
    scenario_manifest.csv
    policy_contracts.json
  fsw/
    aerc_primary_auth/
    aerc_corr_auth/
    aerc_evidence_qualifier/
    aerc_recovery_decision/
    aerc_recovery_sink/
  harness/
    scenario_controller/
    adjudicator/
    fault_injector/
  models/
    train_models.py
    frozen_model_manifest.json
  analysis/
    analyze.py
  audit/
    independent_recompute.py
  tests/
    ...
  results/
    ...
```

## 5. Application responsibilities

### 5.1 Primary authorization app

- receives scenario-controlled true/false authorization state through a test-only injection boundary;
- constructs primary authorization evidence;
- applies topology-specific source/key/authority assignment;
- emits signed evidence;
- never receives the objective action.

### 5.2 Corroboration app

Same responsibilities as primary authorization app, with a separately instantiated domain identity unless the topology explicitly aliases domains.

### 5.3 Evidence qualifier

Consumes evidence messages and produces immutable feature snapshots.

Responsibilities:

- signature verification;
- source identity/trust lookup;
- freshness check against scenario epoch/time;
- epoch validation;
- internal contradiction check;
- completeness check;
- extraction of authorization value;
- capture of HS-derived health/readiness;
- serialization of B and C vectors;
- SHA-256 hash of each vector.

It must not receive research-only fault labels or objective action.

### 5.4 Recovery decision app

Contains four policy adapters.

- D0 consumes B;
- L0 consumes the exact same B bytes;
- D1 consumes C;
- L1 consumes the exact same C bytes.

The app records:

- scenario ID;
- policy ID;
- input hash;
- decision;
- model/rule version.

### 5.5 Recovery action sink

Records the requested action only. No real device actuation.

Allowed canonical actions:

- `HOLD`
- `ENTER_RECOVERY_GATE`

### 5.6 Research adjudicator

External harness component.

Maintains:

- true authorization;
- true health/readiness;
- security signal;
- topology;
- fault profile;
- domain aliases;
- objective action.

The adjudicator may evaluate results only after policy-visible snapshots and decisions are committed.

## 6. Cryptographic mechanism

The implementation should use real message signatures rather than directly setting a `signature_valid` bit.

Candidate default: Ed25519 with fixed test keys generated and frozen for the experiment.

Requirements:

- key pairs are test-only;
- key IDs map to topology domains;
- compromise profiles can access the targeted signing-domain key;
- signature verification result becomes a derived evidence feature;
- cryptographic performance is not an endpoint.

The exact library and version must be selected and pinned before protocol freeze.

## 7. Topology implementation

A topology manifest assigns stable domain IDs:

```text
primary:
  source_domain
  key_domain
  execution_domain
  transport_domain
  authority_domain

corroborator:
  source_domain
  key_domain
  execution_domain
  transport_domain
  authority_domain
```

T0-T4 are generated by aliasing or separating these identifiers.

Implementation expectation:

- T0: both logical producers may execute within one controlled application/process with shared key/transport/authority.
- T1: separate cFS apps/process identities, shared key/transport/authority.
- T2: separate apps and keys, shared cFE Software Bus transport and authority.
- T3: corroborator on a second cFS instance/peer with SBN, separate source/key/execution/transport, shared authority.
- T4: T3 plus separate authorization authority/keying provenance.

The exact mechanism used to represent separate authority in T4 must be fixed in the protocol-freeze revision.

## 8. Fault injector

Fault injection occurs below the policy interface.

Each profile must have:

- target domain;
- precondition;
- deterministic transformation;
- expected propagation set calculated from topology aliases;
- instrumentation confirming actual propagation.

Examples:

- source-false: legitimate producer emits authorization opposite to research truth;
- key compromise: harness signs false evidence using compromised key;
- freshness delay: retain original signed evidence until it exceeds bound;
- message loss: suppress message before qualifier;
- transport compromise: mutate/drop/replay at defined transport adapter;
- authority compromise: authority generates an incorrect authorization assertion before producer signing;
- compound: apply both frozen transformations in deterministic order.

## 9. Learner implementation

Candidate implementation: scikit-learn `DecisionTreeClassifier`.

Before protocol freeze, pin:

- library version;
- criterion;
- splitter;
- max depth;
- minimum samples;
- class weighting;
- random state;
- feature ordering;
- serialization format.

Training procedure:

1. generate only TR scenarios;
2. extract B for L0 and C for L1;
3. train with the same target definition;
4. freeze models before E1/E2/C0 execution;
5. hash serialized models;
6. canonical evaluation must refuse to run if model hashes differ from the frozen manifest.

No hyperparameter tuning after canonical evaluation begins.

## 10. Scenario manifest

Generate a machine-readable manifest before execution with:

- scenario ID;
- block;
- true authorization;
- true health;
- security signal;
- topology;
- fault profile;
- expected domain aliases;
- expected targeted domains;
- expected validity prerequisites.

Expected counts:

- TR = 72;
- E1 = 72;
- E2 = 96;
- C0 = 20;
- total architecture scenarios represented in the manifest = 260;
- canonical evaluation scenarios = 188;
- canonical evaluation policy decisions = 752.

The manifest generator requires unit tests that assert these exact cardinalities.

## 11. Determinism and replay

Canonical requirements:

- deterministic scenario ordering;
- fixed keys and configuration;
- fixed model artifacts;
- no wall-clock-dependent freshness semantics: use controlled experiment time;
- no external network dependency during canonical runs;
- deterministic fault injection;
- deterministic cFS/NOS3 configuration;
- replay of the same scenario produces identical feature hashes and decisions.

If NOS3 dynamics introduces nondeterminism irrelevant to the study, isolate or disable those sources for the canonical experiment.

## 12. Evidence artifacts

A future canonical result package should include at minimum:

- scenario manifest;
- environment lock;
- topology manifest;
- fault-profile manifest;
- frozen model files + hashes;
- raw event/telemetry trace per scenario;
- feature snapshots + hashes;
- four policy decisions per evaluation scenario;
- adjudication truth;
- validity record;
- policy summary;
- topology/fault summaries;
- execution report;
- provenance record;
- hash manifest;
- independent audit report.

## 13. CI design

Pre-canonical CI should include:

1. build cFS/NOS3 pinned environment;
2. unit tests;
3. topology-alias tests;
4. signature/qualification tests;
5. fault-propagation tests;
6. input-equivalence tests;
7. truth-leakage tests;
8. cardinality tests;
9. deterministic-replay tests;
10. model-freeze tests;
11. analysis golden tests;
12. independent-audit dry run.

Canonical execution workflow must be separately named and manually authorized.

## 14. Canonical execution guard

The canonical workflow must fail closed unless an explicit repository-controlled authorization token/file is present, for example:

`study7e/CANONICAL_EXECUTION_AUTHORIZATION.json`

That file must not exist during protocol-development work.

The workflow must refuse execution if:

- protocol status is not FROZEN;
- environment lock is incomplete;
- models are not frozen;
- test suite is not green;
- scenario manifest cardinalities differ;
- working tree/ref differs from the authorized commit;
- provenance fields are incomplete.

## 15. Implementation stop point for current authorization

Current authorization permits:

- research;
- protocol drafting;
- architecture design;
- implementation planning;
- test/audit planning.

Current authorization does **not** permit:

- creation of canonical Study-7E observations;
- training/final freezing of production models;
- canonical cFS/NOS3 campaign execution;
- publication claims based on Study 7E;
- new Zenodo release.

The next gate is author review and protocol freeze.
