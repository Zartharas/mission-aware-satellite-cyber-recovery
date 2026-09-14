# Study 9 synthetic implementation phase

This directory documents the implementation-only phase for **S9-RTSI-001** after the primary population, semantic-adjudication contracts, primary policy scope, and canonical execution design were frozen.

## Scope

The implementation under `study9/src/study9_semantic/` remains deliberately **synthetic-only**. It may load frozen Study 9 governance metadata and the frozen Study 2 selector implementation, but it must not open or process the real CuCD-ID, AegisSat, or UNSW-IoTSAT row populations during this phase.

The code provides:

- fail-closed validation of the frozen population, semantic freeze, policy-scope freeze, canonical execution-design freeze, rubric, schema manifest, and Study 2 selector hash;
- materialization of the frozen 3-dataset x 8-variable semantic mapping contract;
- deterministic enumeration of admissible binary completions for unresolved state;
- a thin adapter to the frozen Study 2 selector;
- assignment-conditioned minimal-sidecar combinatorics for synthetic fixtures only;
- canonical guaranteed-minimal-sidecar combinatorics that never require unavailable actual missing values;
- an independently implemented audit path for completion/action-set/guaranteed-sidecar reconstruction.

It does **not** produce Study 9 scientific results.

## Run the synthetic test suite

From the repository root:

```bash
PYTHONPATH="study9/src:study2/src" \
python3 -m unittest discover -s study9/tests -p 'test_*.py' -v
```

The test suite includes exhaustive adapter equivalence over all 256 binary eight-variable states and every `Study2Policy` enum value. It also verifies the frozen 24-record semantic matrix, label exclusions, fail-closed governance bindings, completion enumeration, assignment-conditioned tie retention, canonical guaranteed-sidecar semantics, canonical-versus-independent synthetic reconstruction, the exact primary policy set, exclusion of mechanistic ablations, and tamper detection for the canonical execution design.

## Fail-closed behavior

`contracts.py` rejects execution if, among other things:

- any of the three frozen population members changes;
- a canonical artifact hash, path, row count, or column count in the execution design drifts from the frozen schema manifest;
- the required eight-variable interface changes;
- dataset artifact/population/schema locks are not all active;
- the semantic freeze and schema manifest disagree about a mapping;
- a deterministic derivation rule appears in the currently empty frozen registry;
- the frozen Study 2 selector byte hash changes;
- the `Study2Policy` enum names, values, or order change;
- a primary policy is missing, reordered, or replaced by a mechanistic ablation;
- an excluded `NO_*` ablation is admitted to the primary policy set;
- policy pooling, policy averaging, or a canonical default policy is introduced;
- lossless state-collapse or exact multiplicity rules change;
- actual unavailable values are allowed into the canonical sidecar endpoint;
- attack/scenario labels are allowed to influence primary state, grouping, selector action, or sidecar results;
- deterministic-output or independent-audit requirements are weakened;
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

## Frozen canonical execution design

`study9/CANONICAL_EXECUTION_DESIGN_FREEZE.json` prospectively fixes the real-data execution semantics before any canonical row is opened.

### Input identity

A future canonical loader must verify the frozen container/artifact SHA-256 values and expected artifact shape before semantic row processing. Any identity or shape mismatch fails closed and produces no endpoint output. Dataset bytes remain outside the repository.

### Lossless native-state collapse

The frozen Study 2 selector consumes only the eight boolean recovery-state variables plus an explicitly supplied policy. Therefore, within one dataset, source rows are decision-equivalent when they have the same qualifying directly observed/derivable recovery-state values and the same ordered unresolved-variable set.

Canonical execution may collapse those rows into a native-state group with an **exact positive integer multiplicity**. This is not sampling, deduplication, weighting by prevalence, or row exclusion. The sum of group multiplicities must equal the verified canonical source-row count, and all row-level finite-population denominators are reconstructed exactly through multiplicity.

Raw fields that are not qualifying `DIRECT` or `DERIVABLE_BY_PREDECLARED_RULE` recovery state cannot enter the collapse key. Attack/scenario labels cannot enter the key. Policy is applied after native-state grouping and does not enter the native group key.

### Assignment-conditioned helper versus canonical guaranteed sidecar

`minimal_sidecar_sets()` is retained only for synthetic fixtures where a complete synthetic state is deliberately known. It asks which smallest subset would have been sufficient **for those supplied actual synthetic values**. This helper is not the Study 9 primary endpoint.

`guaranteed_minimal_sidecar_sets()` is the canonical endpoint helper. For unresolved set `U`, a candidate subset `S` is sufficient only when **every possible boolean assignment to `S`** leaves exactly one reachable action across **every possible assignment to `U \\ S`**. The function returns all sufficient subsets of minimum cardinality in frozen variable order.

This definition never asks for, imputes, predicts, or substitutes unavailable actual values of ambiguous or absent recovery state. Full revelation must always be sufficient because the frozen Study 2 selector is deterministic.

### Labels and primary execution

Offline attack/scenario ground truth may not influence:

- primary recovery-state construction;
- native-state collapse;
- primary selector actions;
- the guaranteed-sidecar endpoint.

Any later descriptive label stratification remains secondary and must occur only after primary endpoints have been frozen.

### Determinism and independent audit

Future canonical outputs must use stable dataset, policy, and recovery-variable ordering; exact integer counts; integer numerator/denominator fraction representation; canonical UTF-8 JSON with sorted keys and a trailing newline; and a SHA-256 output manifest.

A separately implemented audit must independently reconstruct source-group multiplicities and primary endpoint counts from the same hash-verified source artifacts. It may not take canonical result files as analytical inputs. Any canonical-versus-audit mismatch must fail closed before a results freeze.

## Not authorized in this phase

Execution-design freeze does not authorize:

- reading or processing real dataset rows;
- dataset ingestion into the repository;
- per-dataset coverage calculations as scientific results;
- real admissible-action-set computation;
- real unique-action-identifiability computation;
- real guaranteed-minimal-sidecar computation;
- creation of `study9/results/`;
- execution of the four excluded mechanistic ablations as a Study 9 sensitivity analysis;
- modification of Study 2;
- modification of submitted Papers 1 through 4;
- manuscript drafting or journal submission.

Those remain separate governance gates.
