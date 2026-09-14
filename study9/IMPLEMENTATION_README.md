# Study 9 synthetic implementation phase

This directory documents the implementation-only phase for **S9-RTSI-001** after the primary population, semantic-adjudication contracts, and primary policy scope were frozen.

## Scope

The implementation under `study9/src/study9_semantic/` is deliberately **synthetic-only**. It may load frozen Study 9 governance metadata and the frozen Study 2 selector implementation, but it must not open or process the real CuCD-ID, AegisSat, or UNSW-IoTSAT row populations during this phase.

The code provides:

- fail-closed validation of the frozen population, semantic freeze, policy-scope freeze, rubric, schema manifest, and Study 2 selector hash;
- materialization of the frozen 3-dataset x 8-variable semantic mapping contract;
- deterministic enumeration of admissible binary completions for unresolved state;
- a thin adapter to the frozen Study 2 selector;
- generic action-set and minimal-sidecar combinatorics for synthetic fixtures;
- an independently implemented audit path for completion/action-set reconstruction.

It does **not** produce Study 9 scientific results.

## Run the synthetic test suite

From the repository root:

```bash
PYTHONPATH="study9/src:study2/src" \
python3 -m unittest discover -s study9/tests -p 'test_*.py' -v
```

The test suite includes exhaustive adapter equivalence over all 256 binary eight-variable states and every `Study2Policy` enum value. It also verifies the frozen 24-record semantic matrix, label exclusions, fail-closed governance bindings, completion enumeration, minimal-sidecar tie retention, canonical-versus-independent synthetic reconstruction, the exact primary policy set, and exclusion of mechanistic ablations.

## Fail-closed behavior

`contracts.py` rejects execution if, among other things:

- any of the three frozen population members changes;
- the required eight-variable interface changes;
- dataset artifact/population/schema locks are not all active;
- the semantic freeze and schema manifest disagree about a mapping;
- a deterministic derivation rule appears in the currently empty frozen registry;
- the frozen Study 2 selector byte hash changes;
- the `Study2Policy` enum names, values, or order change;
- a primary policy is missing, reordered, or replaced by a mechanistic ablation;
- an excluded `NO_*` ablation is admitted to the primary policy set;
- policy pooling, policy averaging, or a canonical default policy is introduced;
- any real-data, row-level, canonical-execution, results, manuscript, or submission authorization becomes true without a later protocol phase.

## Frozen primary policy scope

`study9/POLICY_SCOPE_FREEZE.json` freezes four substantive Study 2 policies as the primary policy set, in this order:

1. `S2_B0_FAIL_CLOSED`
2. `S2_B1_FAIL_OPERATIONAL`
3. `S2_B2_RISK_THRESHOLD`
4. `S2_S1_EVIDENCE_AWARE`

All four are primary and must be evaluated **separately**. There is no canonical default policy, no preferred policy, and no policy-superiority claim in Study 9.

The following four Study 2 policies are frozen outside the primary analysis as mechanistic ablations:

- `S2_ABL_NO_FRESHNESS`
- `S2_ABL_NO_CONTRADICTION`
- `S2_ABL_NO_EPOCH`
- `S2_ABL_NO_SIGNATURE_TRUST`

Each `NO_*` policy bypasses one evidence check and therefore changes the mechanism under study. A future ablation sensitivity analysis would require separate prospective authorization before real endpoint inspection.

Semantic-mapping and semantic-coverage endpoints remain **policy-independent**. Downstream action-set, unique-action-identifiability, and minimal-sidecar endpoints are prospectively stratified by dataset and primary policy, yielding **3 datasets x 4 policies = 12 primary analysis strata**. Those strata must not be pooled, averaged, or treated as interchangeable replicates for primary claims.

## Not authorized in this phase

Policy-scope freeze does not authorize:

- reading or processing real dataset rows;
- dataset ingestion into the repository;
- per-dataset coverage calculations as scientific results;
- real admissible-action-set computation;
- real unique-action-identifiability computation;
- real minimal-sidecar computation;
- creation of `study9/results/`;
- execution of the four excluded mechanistic ablations as a Study 9 sensitivity analysis;
- modification of Study 2;
- modification of submitted Papers 1 through 4;
- manuscript drafting or journal submission.

Those remain separate governance gates.
