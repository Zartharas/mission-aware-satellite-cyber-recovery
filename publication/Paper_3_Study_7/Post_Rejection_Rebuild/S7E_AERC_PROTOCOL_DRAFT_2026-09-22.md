# S7E-AERC-001 Prospective Protocol

**Experiment ID:** `S7E-AERC-001`  
**Working title:** Architecture-Grounded Equal-Information Recovery Comparators Under Correlated Trust Failures  
**Protocol state:** `DRAFT_FOR_AUTHOR_REVIEW__NOT_FROZEN__EXECUTION_PROHIBITED`  
**Protocol date:** 2026-09-22  
**Parent publication line:** Paper 3  
**Frozen antecedent:** Study 7 / `S7-LSO-001`  
**Scientific execution authorization:** NOT GRANTED

## 1. Purpose

Study 7 established an exact information-sufficiency result in a finite modeled state space. CEAS rejected the resulting manuscript after handling-editor assessment, identifying four limitations: the central result was too directly implied by the formulation, the work lacked a concrete spacecraft recovery architecture, trust assumptions were stipulated rather than validated, and the corroboration-aware learned policy lacked an equal-information deterministic comparator.

Study 7E is a new prospective experiment designed to address those limitations without altering Study 7.

## 2. Research questions

**RQ1. Equal-information policy comparison.**  
In a concrete cFS-grounded spacecraft cyber-recovery architecture, how do deterministic and learned recovery selectors differ when paired policies receive exactly the same policy-visible evidence?

**RQ2. Trust-domain separation.**  
How does explicit separation of source, signing-key, execution, transport, and authorization domains change unsafe-recovery and false-conservative outcomes?

**RQ3. Common-cause failure.**  
Under which shared-domain and common-cause compromises does the benefit of corroborating evidence collapse for deterministic and learned selectors?

**RQ4. Topology/fault transfer.**  
How do the learned selectors behave when evaluated on fault classes and higher-separation trust topologies excluded from their training block?

## 3. Reference architecture

The reference implementation is based on NASA core Flight System (cFS). If the feasibility gate passes, NASA Operational Simulator for Space Systems (NOS3) is used as the canonical simulation/integration environment.

The study is a research reference architecture. It is **not** a flight distribution, flight qualification, NASA endorsement, or operational spacecraft validation.

### 3.1 Architecture components

1. **Primary authorization producer**
   - emits signed recovery-authorization evidence;
   - represents the primary mission/ground authorization path.

2. **Corroboration authorization producer**
   - emits a separately signed authorization assertion;
   - may share or not share source/key/execution/transport/authority domains with the primary producer according to the topology.

3. **Health/readiness producer**
   - uses cFS Health & Safety (HS) or a controlled adapter to expose the modeled recovery-readiness state;
   - not a substitute for actual spacecraft flight qualification.

4. **Evidence qualifier**
   - verifies message presence, signature, configured source identity, freshness, epoch, and internal consistency;
   - produces the exact policy-visible feature snapshots.

5. **Recovery decision application**
   - hosts D0, L0, D1, and L1;
   - each policy consumes only its registered feature projection.

6. **Recovery action sink**
   - records HOLD or ENTER_RECOVERY_GATE;
   - does not actuate real hardware.

7. **Research-only adjudicator and fault controller**
   - external to policy-visible flight-software inputs;
   - records true authorization, true health/readiness, topology, and injected fault;
   - must be proven unable to leak research-only truth into policy inputs.

8. **cFE Software Bus**
   - local publish/subscribe message path.

9. **Software Bus Network (SBN)**
   - used where the topology requires process/processor separation and cross-instance message transfer.

10. **NOS3 ground/simulation layer**
    - candidate environment for command/telemetry, dynamics/environment, software hardware models, and repeatable scenario control.

## 4. Architecture truth and objective action

The research-only adjudicator maintains:

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- `security_signal ∈ {0,1}`

The objective action is defined prospectively as:

`ENTER_RECOVERY_GATE` iff

`security_signal == 1 AND true_authorization == 1 AND true_health_ready == 1`.

Otherwise the objective action is `HOLD`.

This objective is not visible directly to any policy.

## 5. Policy-visible evidence

### 5.1 Base evidence vector B

Both `D0_BASE` and `L0_BASE` receive the same ordered base vector:

1. `primary_signature_valid`
2. `primary_source_trusted`
3. `primary_fresh`
4. `primary_epoch_valid`
5. `primary_noncontradictory`
6. `primary_complete`
7. `primary_authorization`
8. `health_ready`
9. `security_signal`

### 5.2 Corroborated evidence vector C

Both `D1_CORROBORATED` and `L1_CORROBORATED` receive exactly the same ordered extended vector B plus:

10. `corr_signature_valid`
11. `corr_source_trusted`
12. `corr_fresh`
13. `corr_epoch_valid`
14. `corr_noncontradictory`
15. `corr_complete`
16. `corr_authorization`

The policies do **not** receive:

- `true_authorization`;
- `true_health_ready` except through the explicitly modeled `health_ready` observation;
- fault-profile identity;
- topology identity;
- domain-alias map;
- objective action.

## 6. Policy families

### 6.1 D0_BASE

Deterministic base-information comparator.

Proceed only when:

- all six primary evidence-quality conditions are true;
- `primary_authorization == 1`;
- `health_ready == 1`;
- `security_signal == 1`.

### 6.2 D1_CORROBORATED

Deterministic corroborated comparator.

Proceed only when:

- D0 base conditions are satisfied;
- all six corroboration evidence-quality conditions are true;
- `corr_authorization == 1`.

D1 is intentionally conservative and transparent. Its purpose is to remove the unequal-information comparator problem in Study 7.

### 6.3 L0_BASE

Learned base-information selector.

- model class: deterministic decision-tree classifier;
- input: exact B vector;
- target: research-only objective action in the preregistered training block;
- implementation library/version pinned before protocol freeze;
- fixed random state;
- no post-evaluation hyperparameter tuning.

### 6.4 L1_CORROBORATED

Learned corroborated selector.

- same learning algorithm/hyperparameter-selection rule as L0;
- input: exact extended C vector;
- target: same objective action;
- no additional privileged feature.

### 6.5 Equal-information invariant

For every scenario:

- the serialized input bytes presented to D0 and L0 must be identical;
- the serialized input bytes presented to D1 and L1 must be identical.

The harness must hash and record those paired inputs. Any mismatch invalidates the run.

## 7. Trust-domain topology

Each evidence path is assigned domain identifiers for:

1. source/provenance;
2. signing key;
3. execution process/processor;
4. transport;
5. authorization authority.

Five topologies are prospectively defined.

| Topology | Source | Key | Execution | Transport | Authority |
|---|---|---|---|---|---|
| T0_SHARED_ALL | shared | shared | shared | shared | shared |
| T1_SEPARATE_SOURCE_EXEC | separate | shared | separate | shared | shared |
| T2_SEPARATE_SOURCE_KEY_EXEC | separate | separate | separate | shared | shared |
| T3_SEPARATE_THROUGH_TRANSPORT | separate | separate | separate | separate | shared |
| T4_SEPARATE_ALL | separate | separate | separate | separate | separate |

"Separate" means separate experimental trust-domain identifiers and separately instantiated implementation elements as specified in the implementation plan. It does not mean operational or certification-grade independence.

A targeted compromise propagates to every evidence path whose domain identifier aliases the targeted domain. This aliasing rule is the mechanism by which trust dependence is tested rather than stipulated as a policy input.

## 8. Fault/compromise profiles

Exactly thirteen profiles are defined before execution.

| ID | Profile | Target/effect |
|---|---|---|
| F0 | NOMINAL | no injected fault |
| F1 | PRIMARY_SOURCE_FALSE | primary source emits false authorization using its legitimate path |
| F2 | CORR_SOURCE_FALSE | corroborator emits false authorization using its legitimate path |
| F3 | PRIMARY_KEY_COMPROMISE | compromise primary signing-key domain; propagation follows topology aliasing |
| F4 | CORR_KEY_COMPROMISE | compromise corroborator signing-key domain; propagation follows topology aliasing |
| F5 | PRIMARY_FRESHNESS_DELAY | primary evidence intentionally exceeds freshness bound |
| F6 | CORR_FRESHNESS_DELAY | corroboration evidence intentionally exceeds freshness bound |
| F7 | PRIMARY_MESSAGE_LOSS | primary evidence omitted/dropped |
| F8 | CORR_MESSAGE_LOSS | corroboration evidence omitted/dropped |
| F9 | PRIMARY_TRANSPORT_COMPROMISE | primary transport domain corrupts/drops/rewrites as specified; propagation follows aliasing |
| F10 | PRIMARY_AUTHORITY_COMPROMISE | primary authority domain issues false authorization; propagation follows authority aliasing |
| F11 | COMPOUND_AUTHORITY_TRANSPORT | simultaneous authority and transport compromise of the primary path; propagation follows topology aliasing |
| F12 | PRIMARY_EXECUTION_COMPROMISE | compromise primary execution-domain behavior; propagation follows execution-domain aliasing |

The exact byte-level transformation for F3, F4, F9, F10, F11, and F12 must be fixed before protocol freeze.

## 9. Prospective blocks and population

### 9.1 Training block TR

The training population has two prospectively separated sub-blocks.

#### TR1: security-response training

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- topologies T0, T1, T2
- fault profiles F0 through F5
- `security_signal = 1`

Population:

`2 × 2 × 3 × 6 = 72` architecture scenarios.

#### TR0: no-signal baseline training

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- topologies T0, T1, T2
- fault profile F0 only
- `security_signal = 0`

Population:

`2 × 2 × 3 = 12` architecture scenarios.

Total training population:

`72 + 12 = 84` architecture scenarios.

TR0 prevents the learned selectors from being evaluated on an unseen value of the `security_signal` feature merely because that value was omitted from training. Training scenarios are not part of the canonical evaluation population.

### 9.2 Evaluation block E1: unseen fault classes

Evaluate:

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- T0, T1, T2
- F6 through F12
- `security_signal = 1`

Population:

`2 × 2 × 3 × 7 = 84` architecture scenarios.

### 9.3 Evaluation block E2: held-out topology transfer

Evaluate:

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- T3 and T4
- F0 through F12
- `security_signal = 1`

Population:

`2 × 2 × 2 × 13 = 104` architecture scenarios.

### 9.4 Control block C0: held-out-topology no-security-signal controls

Evaluate:

- `true_authorization ∈ {0,1}`
- `true_health_ready ∈ {0,1}`
- T3 and T4 only
- F0 only
- `security_signal = 0`

Population:

`2 × 2 × 2 = 8` architecture scenarios.

Because T3 and T4 are excluded from training, C0 does not duplicate the TR0 training scenarios.

### 9.5 Canonical evaluation population

Canonical evaluation scenarios:

`84 + 104 + 8 = 196`.

Each scenario is evaluated by four policies:

`196 × 4 = 784` policy-decision observations.

The 84 training scenarios are reported separately and never pooled into the 784 evaluation observations. The complete prospective manifest contains 280 architecture scenarios.

These counts are prospective design quantities, not observed results.

## 10. Primary endpoints

For each policy and evaluation block:

1. `objective_decision_error`;
2. `unsafe_proceed`: policy enters recovery gate when objective is HOLD;
3. `false_conservative_hold`: policy holds when objective is ENTER_RECOVERY_GATE;
4. exact policy action counts;
5. D0-vs-L0 paired disagreement count;
6. D1-vs-L1 paired disagreement count.

For trust architecture:

7. change in unsafe-proceed counts from shared to separated topologies;
8. change in false-conservative holds from shared to separated topologies;
9. corroboration benefit within policy class:
   - D1 minus D0;
   - L1 minus L0;
10. common-cause collapse under F10/F11.

All results are exact finite-population counts for the defined evaluation population. They are not operational probabilities.

## 11. Secondary endpoints

- topology-specific confusion tables;
- fault-profile-specific action tables;
- policy disagreement by topology/fault;
- learner tree structure and depth;
- feature-use trace;
- training error;
- E1 unseen-fault exact errors;
- E2 held-out-topology exact errors;
- C0 spurious recovery-gate entries.

## 12. Predeclared analysis rules

- no statistical significance testing is required for the complete finite evaluation population;
- proportions may be reported descriptively with exact numerators/denominators;
- no confidence interval is interpreted as a spacecraft operational-rate interval;
- no policy is declared globally superior based on aggregate counts alone;
- topology and fault stratification must accompany aggregate counts;
- null and adverse findings are retained;
- no post-hoc deletion of difficult scenarios;
- any failed/invalid execution is documented and excluded only according to a frozen validity rule.

## 13. Validity criteria

A scenario is VALID only if:

- expected topology is instantiated;
- expected domain-alias map is recorded;
- intended fault is confirmed by harness instrumentation;
- both policy pairs receive byte-identical paired inputs;
- adjudication truth is absent from policy inputs;
- all four decisions are emitted;
- action sink records the same scenario ID;
- hashes/provenance records are complete.

Otherwise the scenario is INVALID with an explicit reason.

## 14. Prospective hypotheses / expected invariants

These are design expectations, not results.

- H1: equal-information comparison will separate information advantage from policy-class behavior.
- H2: increasing trust-domain separation should reduce propagation of targeted single-domain compromise into both evidence paths.
- H3: authority/common-cause compromise can defeat corroboration when the affected domain remains shared.
- H4: a separated corroboration path may reduce unsafe proceeds while increasing conservative holds under disagreement.
- H5: learned selectors may exhibit different behavior on unseen fault classes or held-out topologies; no direction is assumed.

## 15. Claim boundaries

Study 7E will not claim:

- flight qualification or certification sufficiency;
- operational spacecraft safety/failure probabilities;
- NASA endorsement;
- real RF-link performance;
- hardware CPU/energy/latency unless separately measured;
- global ML superiority;
- independence beyond the instantiated trust-domain separation;
- external human replication from same-repository auditing.

## 16. Relationship to Study 7

Study 7 remains frozen at 1,033 observations.

Study 7E is a separate prospective experiment. If eventually executed and frozen, a rebuilt Paper 3 may synthesize both studies narratively, but:

- populations remain separate;
- no pooled sample size;
- no retroactive Study-7 protocol change;
- no Study-7 rerun for publication optics.

## 17. Freeze and execution gates

Before scientific execution, the author must separately approve:

1. exact pinned cFS/NOS3 commits and environment;
2. exact cryptographic/signature mechanism;
3. exact byte-level fault transformations;
4. exact learner library/version and hyperparameters;
5. final topology implementation;
6. final scenario manifest and expected cardinalities;
7. test suite;
8. independent audit implementation;
9. provenance/hash schema;
10. final claim boundaries.

Until that approval, this protocol remains a draft and no canonical Study-7E execution is permitted.
