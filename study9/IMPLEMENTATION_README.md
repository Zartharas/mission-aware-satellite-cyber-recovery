# Study 9 implementation phase

This directory documents the implementation-only phase for **S9-RTSI-001** after the primary population, semantic-adjudication contracts, primary policy scope, and canonical execution design were frozen.

## Current boundary

The implementation under `study9/src/study9_semantic/` now includes the future hash-verified loader and canonical runner, but the phase remains **synthetic-test only**. The current protocol does not authorize opening or processing the real CuCD-ID, AegisSat, or UNSW-IoTSAT row populations.

`run_canonical_sources()` loads frozen governance contracts and immediately checks the real-execution authorization gate. With the current protocol it must raise `RealExecutionNotAuthorized` **before constructing external source specifications, probing any user-supplied dataset path, or creating an output directory**.

No local download path is hard-coded. A future authorized run must supply exactly three external source paths explicitly:

- the CuCD-ID v3 release ZIP;
- the deposited `AegisSat-AD.csv` file;
- the UNSW-IoTSAT release ZIP.

Dataset bytes remain outside the repository.

## Implemented components

The implementation provides:

- fail-closed validation of the frozen population, semantic freeze, policy-scope freeze, canonical execution-design freeze, schema manifest, and Study 2 selector hash;
- `input_identity.py` for SHA-256, ZIP-member, header, row-width, row-count, and column-count verification;
- `state_projection.py` for frozen DIRECT/DERIVABLE state projection only;
- `state_groups.py` for exact multiplicity-preserving native-state collapse;
- `canonical_engine.py` for pure in-memory policy-stratified endpoint computation;
- `deterministic_io.py` for canonical sorted-key UTF-8 JSON and SHA-256 output manifests;
- `canonical_runner.py` for future guarded orchestration after a separate real-data authorization phase;
- deterministic enumeration of admissible binary completions for unresolved state;
- a thin adapter to the frozen Study 2 selector;
- assignment-conditioned minimal-sidecar combinatorics for synthetic fixtures only;
- canonical guaranteed-minimal-sidecar combinatorics that never require unavailable actual missing values;
- an independently implemented audit path for completion, sidecar, native-state grouping, multiplicity, and primary policy endpoint reconstruction.

The loader/runner layer uses only the Python standard library plus relative imports from this repository. `contracts.py` parses those modules and fails closed if a non-standard-library absolute dependency or a hard-coded `/Users/...` path is introduced.

## Input verification architecture

Real execution, when separately authorized, is designed to verify source identity **before semantic row processing**.

For CuCD-ID and UNSW-IoTSAT, the loader will:

1. verify the frozen release-ZIP SHA-256;
2. require exactly one ZIP member with the frozen canonical member path;
3. verify that member's frozen SHA-256;
4. verify a unique non-empty CSV header, exact column count, uniform row width, and exact row count;
5. only then stream rows for semantic projection.

For AegisSat, the deposited CSV itself is hash-verified before the same structural CSV checks.

The future runner re-verifies source identity after both the canonical semantic pass and the independent-audit pass, so mutation during execution fails closed before results are written.

## Minimal streaming projection

The frozen semantic adjudication means primary state construction is intentionally small:

- CuCD-ID has no `DIRECT` or permitted `DERIVABLE_BY_PREDECLARED_RULE` recovery variable, so all eight required states remain unresolved;
- AegisSat likewise has no qualifying directly observed or permitted derivable recovery state;
- UNSW-IoTSAT has exactly one `DIRECT` mapping: `Position_Anomaly -> security_signal`, normalized strictly from numeric 0/1.

Every other raw field is ignored for primary state construction. Attack/scenario labels, identifiers, timestamps, CRC/error fields, and other `AMBIGUOUS` or `ABSENT` semantics cannot enter the known-state map merely because they are present in a row.

This allows full byte/shape validation without retaining irrelevant source columns in memory.

## Lossless native-state collapse

The frozen Study 2 selector consumes only the eight Boolean recovery-state variables plus an explicitly supplied policy. Within one dataset, rows are therefore decision-equivalent when they have identical qualifying known recovery-state values and the same ordered unresolved-variable set.

`state_groups.py` collapses such rows into native-state groups with an **exact positive integer multiplicity**. The sum of multiplicities must equal the verified canonical source-row count. This is not sampling, deduplication, prevalence weighting, or row exclusion.

Raw fields outside qualifying `DIRECT`/`DERIVABLE_BY_PREDECLARED_RULE` state cannot enter the grouping key. Attack labels and policy values cannot enter the native-state key.

## Frozen primary policy scope

`study9/POLICY_SCOPE_FREEZE.json` freezes four substantive Study 2 policies as the primary set, in this order:

1. `S2_B0_FAIL_CLOSED`
2. `S2_B1_FAIL_OPERATIONAL`
3. `S2_B2_RISK_THRESHOLD`
4. `S2_S1_EVIDENCE_AWARE`

All four are evaluated separately. There is no canonical default or preferred policy. The four `S2_ABL_NO_*` policies remain excluded mechanistic ablations unless a future sensitivity analysis is separately authorized prospectively.

Semantic mapping/coverage endpoints are policy-independent. Action-set, unique-action-identifiability, and guaranteed-sidecar endpoints are stratified by dataset and primary policy, yielding 12 primary analysis strata.

## Assignment-conditioned helper versus canonical guaranteed sidecar

`minimal_sidecar_sets()` remains only for synthetic fixtures where complete synthetic truth is deliberately supplied.

`guaranteed_minimal_sidecar_sets()` is the canonical endpoint helper. For unresolved set `U`, a subset `S` is sufficient only when every possible Boolean assignment to `S` leaves exactly one reachable action across every possible assignment to `U \\ S`. All tied minimum-cardinality subsets are retained in frozen variable order.

The canonical endpoint never asks for, predicts, imputes, or substitutes unavailable actual values of ambiguous or absent recovery state.

## Pure canonical engine and independent audit

`canonical_engine.py` operates only on already verified native-state groups. It applies all four frozen primary policies separately and records, per group and policy:

- reachable action set;
- action-set cardinality;
- unique-action status;
- exact group multiplicity;
- guaranteed minimal-sidecar cardinality;
- every tied minimum-cardinality sidecar set.

Dataset-level unique-action fractions retain integer numerators and denominators reconstructed exactly through group multiplicity.

`independent_audit.py` separately implements completion enumeration, guaranteed-sidecar reconstruction, native-state grouping, multiplicity accounting, and policy endpoint reconstruction. It does not call `state_groups.py` or `canonical_engine.py`. A future canonical run must fail closed if canonical and independent summaries disagree.

## Deterministic output design

A future authorized canonical run is designed to emit exactly the prospectively frozen artifacts:

- `run_manifest.json`
- `mapping_matrix.json`
- `coverage_summary.json`
- `native_state_groups.json`
- `policy_strata.json`
- `guaranteed_sidecar.json`
- `independent_audit.json`
- `output_sha256_manifest.json`

Outputs use canonical UTF-8 JSON with sorted keys, compact separators, no non-finite numeric values, and a trailing newline. Counts remain integers and fractions store integer numerator/denominator pairs. The SHA-256 manifest hashes the seven substantive artifacts. Source dataset bytes are never copied into result artifacts.

The runner refuses to write if the output artifact set or order differs from the frozen execution-design contract. Result writing occurs only after source verification, canonical reconstruction, independent reconstruction, and exact canonical-versus-audit comparison have succeeded.

## Run the synthetic test suite

From the repository root:

```bash
PYTHONPATH="study9/src:study2/src" \
python3 -m unittest discover -s study9/tests -p 'test_*.py' -v
```

The suite covers the frozen governance contracts plus synthetic temporary direct-CSV and ZIP-backed input fixtures. It exercises deliberate hash mismatches, missing ZIP members, malformed row widths, shape drift, duplicate headers, label exclusion, strict direct-value normalization, multiplicity conservation, policy-stratified endpoint weighting, deterministic serialization, independent reconstruction, and the hard real-execution guard.

Synthetic fixture files are created only in temporary directories and are not Study 9 source data.

## Fail-closed behavior

`contracts.py` rejects the implementation if, among other things:

- any frozen population member or eight-variable semantic changes;
- a canonical artifact identity or expected shape drifts from the frozen manifest;
- semantic freeze and schema manifest disagree;
- a deterministic derivation rule appears in the currently empty registry;
- the frozen Study 2 selector hash or policy enum changes;
- an excluded mechanistic ablation is admitted to the primary policy set;
- policy pooling, averaging, or a canonical default policy is introduced;
- lossless-collapse or exact-multiplicity rules change;
- unavailable actual values are allowed into the canonical guaranteed-sidecar endpoint;
- attack labels are allowed to influence primary state, grouping, action, or sidecar computation;
- deterministic-output or independent-audit requirements are weakened;
- any guarded loader/runner module disappears, imports a non-standard-library absolute dependency, or embeds a local `/Users/...` path;
- the canonical runner no longer places its authorization guard immediately after loading frozen contracts;
- any real-data, row-level, canonical-execution, results, manuscript, or submission authorization becomes true without a later protocol phase.

## Not authorized in this phase

Loader/runner implementation does **not** authorize:

- reading or processing real dataset rows;
- probing the user's real dataset paths through `run_canonical_sources()`;
- dataset ingestion into the repository;
- per-dataset coverage calculations as scientific results;
- real admissible-action-set computation;
- real unique-action-identifiability computation;
- real guaranteed-minimal-sidecar computation;
- creation of `study9/results/`;
- execution of excluded mechanistic ablations;
- modification of Study 2;
- modification of submitted Papers 1 through 4;
- manuscript drafting or journal submission.

Those remain separate governance gates. The next phase, after the expanded synthetic suite passes on an actual clone, is a final pre-run audit and a separately authorized prospective change to the real-data execution flags.
