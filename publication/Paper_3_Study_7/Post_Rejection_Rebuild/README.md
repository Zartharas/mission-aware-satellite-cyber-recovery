# Paper 3 Post-Rejection Rebuild

**Current state:** `S7E_AERC_001_PROTOCOL_DRAFT_COMPLETE__AUTHOR_REVIEW_REQUIRED__EXECUTION_NOT_AUTHORIZED`  
**Date:** 2026-09-22

Paper 3 was rejected by CEAS Space Journal after handling-editor assessment. The rejected CEAS package and frozen Study 7 remain immutable provenance.

## Current recovery authorities

1. `../CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-09-22.md`
2. `PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`
3. `STUDY7E_AERC_PROSPECTIVE_EXTENSION_PROPOSAL_2026-09-22.md`
4. `S7E_AERC_PROTOCOL_DRAFT_2026-09-22.md`
5. `S7E_AERC_IMPLEMENTATION_PLAN_2026-09-22.md`
6. `S7E_AERC_TEST_AND_AUDIT_PLAN_2026-09-22.md`
7. `S7E_AERC_ARCHITECTURE_SOURCE_LEDGER_2026-09-22.md`
8. `S7E_AERC_CANDIDATE_ENVIRONMENT_BASELINE_2026-09-22.md`
9. `S7E_AERC_PROTOCOL_REVIEW_R1_2026-09-22.md`
10. `S7E_AERC_PROTOCOL_REVIEW_R2_2026-09-22.md`
11. `S7E_AERC_STACK_COMPATIBILITY_DECISION_2026-09-22.md`
12. `S7E_AERC_DESIGN_STATUS.json`
10. `../../../../study7/STUDY7_PROTOCOL.json`
11. `../../../../study7/results/RESULTS_FREEZE.json`

## Current design

The prospective extension `S7E-AERC-001` now has a complete draft protocol and implementation/test plan for author review.

Design highlights:

- cFS-grounded spacecraft recovery reference architecture;
- NOS3 as the preferred canonical integration environment if feasibility qualification passes;
- five explicit trust-domain topologies;
- twelve fault/compromise profiles;
- equal-information policy pairs:
  - `D0_BASE` / `L0_BASE`;
  - `D1_CORROBORATED` / `L1_CORROBORATED`;
- 84 training architecture scenarios (TR1 = 72, TR0 = 12);
- 196 canonical evaluation/control architecture scenarios;
- 784 canonical evaluation policy-decision observations;
- separately implemented repository audit requirement.

These quantities are prospective protocol design values, not results.

A protocol-review correction made before freeze added no-signal examples to training and removed overlapping no-signal controls from T0-T2. The complete manifest now contains 280 scenarios after adding direct execution-domain fault coverage.

## Environment candidates

Current upstream release candidates recorded at design time:

- NASA cFS `v7.0.1`;
- NASA NOS3 `v1_07_05` / 1.7.5.

They are not yet pinned as canonical dependencies. Exact commits/submodules and reproducibility must be established through a separate feasibility qualification before protocol freeze.

## Hard stop

The author authorized protocol and implementation-plan development only.

The following remain prohibited:

- creating canonical Study-7E observations;
- canonical cFS/NOS3 scientific execution;
- freezing trained production models;
- creating a Zenodo Study-7E dataset;
- making publication claims from Study 7E;
- modifying or rerunning `S7-LSO-001`.

A future `study7e/` implementation workspace may be created only after the author approves the draft protocol/implementation design and authorizes the next implementation phase. Canonical scientific execution requires an additional, separate authorization after implementation qualification and protocol freeze.

No replacement journal is locked.
