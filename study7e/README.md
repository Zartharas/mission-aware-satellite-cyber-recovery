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
- E1 unseen faults = 84;
- E2 held-out topologies = 104;
- C0 held-out-topology controls = 8;
- total manifest = 280;
- canonical evaluation scenarios = 196;
- planned evaluation policy decisions = 784.

These are protocol design quantities, not results.

## Current implementation surfaces

- `PROTOCOL_DRAFT.json`
- `IMPLEMENTATION_STATE.json`
- `configs/`
- `configs/signed_evidence_contract_draft.json`
- `src/aerc_design.py`
- `validation/validate_precanonical.py`
- `validation/check_fsw_truth_leakage.py`
- `models/training_contracts.py`
- `audit/independent_design_audit.py`
- `fsw/aerc_bus_probe/`
- `fsw/aerc_recovery_sink/`
- `fsw/aerc_sink_probe/`
- `fsw/aerc_sigverify/`
- `fsw/aerc_sigverify_probe/`
- `fsw/aerc_policy/`
- `fsw/aerc_policy_probe/`
- `tests/`
- `feasibility/`

The Python implementation remains a pre-canonical architecture/contract harness. Non-canonical cFS engineering surfaces now validate Software Bus, two-instance SBN transport, deterministic scenario-ID/sink receipt, HS housekeeping observability, the recovery-action sink, and the shared B/C snapshot path with deterministic D0/D1 decisions. The sink records only requested actions and the policy path rejects malformed or contract-invalid snapshots. Learned L0/L1 and real-signature verification are not implemented. These components are not canonical scientific execution.

## Pre-freeze implementation baseline

Selected for the remaining non-canonical architecture:

- NASA cFS v7.0.1, tag commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`.

Evaluated alternative retained as bounded feasibility/reference evidence:

- NASA NOS3 v1.7.5 / `v1_07_05`, tag commit `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`.

This is **not** a canonical environment freeze. Decision record:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_SELECTION_DECISION_2026-09-23.md`

## Next gate

Perform the bounded compatibility/provenance review for the real-signature verification dependency next. Ed25519 remains the protocol candidate, but no crypto runtime should be added until that dependency decision is documented. Learned L0/L1 implementation and model freeze remain later gates. Protocol/environment freeze and canonical scientific execution remain separately prohibited.
