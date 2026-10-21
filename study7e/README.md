# Study 7E — Architecture-Grounded Equal-Information Recovery Comparators

**Experiment:** `S7E-AERC-001`  
**Current state:** `RESULTS_FROZEN__PR_MERGE_NOT_AUTHORIZED__PUBLICATION_NOT_AUTHORIZED`  
**Protocol/environment freeze:** `S7E-AERC-FREEZE-001`  
**Model freeze:** `S7E-AERC-MODEL-FREEZE-001`  
**Result freeze:** `S7E-AERC-RESULT-FREEZE-001`  
**Parent publication:** Paper 3  
**Frozen antecedent:** Study 7 / `S7-LSO-001`

Study 7E is a separate prospective extension created after the Paper 3 CEAS rejection. It does not modify or rerun Study 7.

## Current scientific state

Study 7E has completed protocol/environment freeze, deterministic production training, model freeze, held-out evaluation planning, the authorized one-shot E1/E2/C0 execution, independent result reconciliation, adversarial scientific review, and formal result freeze.

The sole held-out execution of record is `S7E-AERC-HELDOUT-EXEC-001`:

- E1 = 84 scenarios;
- E2 = 104 scenarios;
- C0 = 8 scenarios;
- total = 196 scenarios;
- four policies per scenario;
- 784 policy decisions;
- invalid scenarios = 0;
- audit mismatches = 0.

The execution is sealed and must not be rerun under the same execution identifier.

## Frozen scientific disposition

- H1: SUPPORTED
- H2: PARTIALLY SUPPORTED
- H3: PARTIALLY SUPPORTED
- H4: PARTIALLY SUPPORTED
- H5: SUPPORTED

The freeze explicitly retains adverse, null, and counterexample findings. It does not identify a global policy winner and does not treat finite-population counts as operational spacecraft probabilities.

## Durable result evidence

The original held-out Actions artifact is durably preserved under:

`frozen_results/S7E-AERC-RESULT-FREEZE-001/`

Its reconstructed ZIP SHA-256 is:

`cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`

Authoritative result-freeze records:

- `RESULT_FREEZE_MANIFEST_001.json`
- `RESULT_FREEZE_STATE.json`
- `configs/result_freeze_authorization_001.json`
- `configs/result_freeze_candidate_001.json`
- `validation/validate_result_freeze_001.py`

## Policy and architecture design

Equal-information policy pairs:

- `D0_BASE` and `L0_BASE`: identical base evidence;
- `D1_CORROBORATED` and `L1_CORROBORATED`: identical base + corroboration evidence.

Trust topologies:

- T0_SHARED_ALL
- T1_SEPARATE_SOURCE_EXEC
- T2_SEPARATE_SOURCE_KEY_EXEC
- T3_SEPARATE_THROUGH_TRANSPORT
- T4_SEPARATE_ALL

The frozen protocol uses exact finite populations rather than sampling inference. Study 7 and Study 7E remain separate populations and must not be pooled.

## Closed gates

Not authorized by the result freeze:

- model retraining or post-hoc model/hyperparameter changes;
- population or endpoint expansion;
- retry of `S7E-AERC-HELDOUT-EXEC-001`;
- PR #167 merge;
- manuscript/publication result claims.

## Next gate

Verify post-freeze CI. Any PR #167 merge requires separate explicit author authorization. Manuscript/publication result claims require a separate authorization even if the PR is later merged.
