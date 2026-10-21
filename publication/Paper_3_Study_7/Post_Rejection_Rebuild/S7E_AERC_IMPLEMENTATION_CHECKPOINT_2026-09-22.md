# S7E-AERC-001 Implementation / Feasibility Checkpoint

**Checkpoint date:** 2026-09-22  
**Experiment:** `S7E-AERC-001`  
**Branch:** `paper3/s7e-aerc-implementation-feasibility-20260922`  
**Pull request:** #167  
**PR base:** `main` at `efb0d135b962034c325c2e268c1e0fdb61712516`  
**Checkpoint parent head:** `6fcdfcbb5884d100c3e2eb7ec7e387b4bc3ae58d`  
**Phase:** implementation/feasibility only  
**Canonical scientific execution:** NOT AUTHORIZED

## 1. Design state

Two prospective defects were found and corrected before protocol freeze and before scientific execution.

### R1: no-signal training support

The initial draft trained only with `security_signal=1` while evaluating no-signal controls.

Correction:

- TR1 = 72 security-response training scenarios;
- TR0 = 12 no-signal training scenarios on T0-T2/F0;
- C0 restricted to held-out T3-T4/F0.

### R2: execution trust-domain coverage

The architecture declared an execution trust domain but originally had no direct execution-domain fault.

Correction:

- added `F12 PRIMARY_EXECUTION_COMPROMISE`.

Current prospective design:

- 13 fault profiles, F0-F12;
- 5 trust topologies, T0-T4;
- training = 84 scenarios;
- E1 = 84;
- E2 = 104;
- C0 = 8;
- canonical evaluation/control = 196 scenarios;
- planned evaluation policy decisions = 784;
- complete design manifest = 280 scenarios.

These are design quantities, not results.

## 2. Implemented pre-canonical controls

Implemented on the branch:

- machine-readable draft protocol and implementation state;
- topology/domain alias model;
- F0-F12 fault semantics;
- prospective 280-scenario manifest generator;
- expected domain-alias and affected-path oracle columns;
- deterministic D0/D1 comparator contracts;
- equal-information paired-input hashing;
- privileged-field rejection;
- learner training-boundary contracts;
- explicit prohibition on E1/E2/C0 entering training;
- candidate learner config with no library version/hyperparameter/model freeze;
- independently implemented design auditor;
- flight-software truth-leakage scanner;
- pre-canonical governance validator;
- cFS/NOS3 candidate environment lock;
- explicit rule that standalone cFS and NOS3-native pinned stacks are alternative candidates and must not be mixed casually;
- cFS custom Software Bus probe app;
- cFS/NOS3 local feasibility scripts;
- Study 7E-specific CI qualification workflow.

## 3. Completed CI evidence

Previously completed green Study-7E qualification runs established:

- topology/fault/cardinality contract tests PASS;
- training-boundary tests PASS;
- independent pre-canonical design audit PASS;
- canonical execution guard PASS;
- frozen Study 7 path guard PASS;
- exact upstream tag identities PASS;
- official cFS v7.0.1 native_std build/test feasibility PASS.

A repository-wide validation run also passed after narrow current-state compatibility reconciliation.

## 4. cFS custom-app smoke status

The first custom-app smoke run reached the cFS build successfully:

- `aerc_bus_probe` was discovered by the cFS build;
- it compiled for cpu1 and cpu2;
- the module was installed at `build-native_std/exe/cpu1/cf/aerc_bus_probe.so`.

The CI job then failed because the workflow asserted the wrong install path:

- incorrect check: `build-native_std/exe/cpu1/aerc_bus_probe.so`;
- actual path: `build-native_std/exe/cpu1/cf/aerc_bus_probe.so`.

This was an engineering harness-path defect, not a cFS compiler/app defect.

Fix commit before this checkpoint:

`6fcdfcbb5884d100c3e2eb7ec7e387b4bc3ae58d`

The runtime smoke step has not yet been accepted as PASS at this checkpoint.

## 5. CI pending at checkpoint

Exact-head runs created after the path correction:

- Study 7E pre-canonical qualification: run `35790652126`;
- repository validation: run `35790652125`.

They were queued when this checkpoint was prepared.

## 6. Frozen / prohibited surfaces

Verified branch scope:

- no `study7/` changes;
- no Study-7E canonical results;
- no publisher submission-package changes;
- no canonical execution authorization file;
- no canonical Study-7E execution workflow;
- no production L0/L1 model artifacts;
- no model freeze;
- no Study-7E Zenodo archive.

## 7. Next authorized actions

In order:

1. verify the exact-head CI runs above;
2. if the cFS bus-probe runtime passes, record Gate-A custom-app/SB smoke evidence;
3. run NOS3 revision/preflight and build feasibility in a supported Linux/VM environment;
4. compare standalone cFS and NOS3-native feasibility;
5. recommend one canonical stack for author review;
6. implement non-canonical architecture components on the selected candidate stack;
7. stop before protocol/implementation freeze and before any canonical scientific execution unless separately authorized.

## 8. Resume rule

A future chat should treat this file, PR #167, and the current PR head as the authoritative implementation handoff. Do not infer canonical execution authorization from the existence of this checkpoint.
