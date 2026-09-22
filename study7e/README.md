# Study 7E — Architecture-Grounded Equal-Information Recovery Comparators

**Experiment:** `S7E-AERC-001`  
**Current state:** `IMPLEMENTATION_FEASIBILITY_IN_PROGRESS__CANONICAL_EXECUTION_PROHIBITED`  
**Parent publication:** Paper 3  
**Frozen antecedent:** Study 7 / `S7-LSO-001`

Study 7E is a new prospective extension created after the CEAS Space Journal editorial rejection of Paper 3. It does not modify or rerun Study 7.

## Current authorization boundary

Authorized:

- implementation scaffolding;
- machine-readable protocol/configuration;
- scenario-manifest generation;
- topology/fault semantics;
- deterministic comparator implementation;
- learned-policy interface/training-pipeline scaffolding;
- unit/contract tests;
- cFS/NOS3 feasibility qualification;
- provenance and execution guards.

Not authorized:

- canonical scientific execution;
- canonical Study-7E observations/results;
- freezing final learned models;
- Zenodo publication;
- manuscript claims based on Study 7E.

No canonical execution authorization file exists.

## Prospective design

Policy pairs:

- `D0_BASE` and `L0_BASE`: identical base evidence;
- `D1_CORROBORATED` and `L1_CORROBORATED`: identical base + corroboration evidence.

Trust topologies:

- T0_SHARED_ALL
- T1_SEPARATE_SOURCE_EXEC
- T2_SEPARATE_SOURCE_KEY_EXEC
- T3_SEPARATE_THROUGH_TRANSPORT
- T4_SEPARATE_ALL

Prospective scenario counts:

- training = 84 (TR1 = 72, TR0 = 12);
- E1 unseen faults = 72;
- E2 held-out topologies = 96;
- C0 held-out-topology controls = 8;
- total manifest = 260;
- canonical evaluation scenarios = 176;
- planned evaluation policy decisions = 704.

These are protocol design quantities, not results.

## Current implementation surfaces

- `PROTOCOL_DRAFT.json`
- `IMPLEMENTATION_STATE.json`
- `configs/`
- `src/aerc_design.py`
- `validation/validate_precanonical.py`
- `tests/`
- `feasibility/`

The current Python implementation is a pre-canonical architecture/contract harness. It exists to validate the design before cFS applications are introduced. It must not be represented as the final cFS/NOS3 scientific implementation.

## External-stack candidates

- NASA cFS v7.0.1, tag commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`
- NASA NOS3 v1.7.5 / `v1_07_05`, tag commit `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`

External builds are feasibility checks only.

## Next gate

Run and review pre-canonical unit/contract tests and local cFS/NOS3 feasibility qualification. Resolve any design defect before freezing the protocol. Canonical scientific execution requires a later, separate explicit author authorization.
