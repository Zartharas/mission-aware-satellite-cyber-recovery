# Study 9 implementation phase

This directory documents the pre-real-data implementation phase for **S9-RTSI-001** after the primary population, semantic-adjudication contract, primary policy scope, canonical execution design, guarded loader/runner, pre-real-data adversarial audit, performance remediation, and canonical-run code freeze were established.

## Current boundary

The implementation under `study9/src/study9_semantic/` contains the future hash-verified loader and canonical runner, but the current phase remains **synthetic-test only**. The protocol does not authorize opening or processing the real CuCD-ID, AegisSat, or UNSW-IoTSAT row populations.

`run_canonical_sources()` loads frozen governance contracts and immediately checks the real-execution authorization gate. In the current closed phase it must raise `RealExecutionNotAuthorized` before external source-spec construction, user-supplied dataset-path access, or result-directory creation.

No local download path is hard-coded. A future authorized run must explicitly supply the CuCD-ID v3 release ZIP, deposited `AegisSat-AD.csv`, and UNSW-IoTSAT release ZIP. Dataset bytes remain outside the repository.

## Pre-real-data adversarial audit

`study9/PRE_REAL_DATA_ADVERSARIAL_AUDIT.json` preserves five findings identified after the actual-clone 57-test validation at commit `f7723ffd7d2e9a6127f260f83d5a0d36cf7ffff1`, before any real Study 9 row was opened.

The findings were:

1. canonical and independent grouping shared the canonical raw-row projector;
2. policy-independent mapping and coverage lacked an independent reconstruction;
3. the complete post-guard runner path had not been exercised end-to-end on synthetic files;
4. the future closed-to-open execution transition needed an atomic contract rather than isolated flag edits;
5. `run_manifest.json` needed SHA-256 identities for the exact governance and runtime implementation used for a run.

The audit record itself is additive and remains a historical pre-result record. The remediation state is recorded prospectively in `STUDY9_PROTOCOL.json` and the implementation history rather than rewriting the audit findings.

## Pre-real-data performance remediation

`study9/PRE_REAL_DATA_PERFORMANCE_REMEDIATION.json` records a performance defect discovered during the first actual-clone run of the hardened synthetic integration suite at commit `6c6968c08c186927bdab8bf1371c80dd809db29c`.

The suite remained CPU-bound for more than twenty minutes on `test_full_synthetic_runner_detects_corrupted_canonical_projection`. The interrupt traceback showed the hot path repeatedly entering `selector_adapter._selector_module() -> load_frozen_contracts() -> validate_contracts()` from exhaustive sidecar evaluation. The independent audit used the same repeated frozen-contract initialization pattern in its own selector loader.

The defect was computational redundancy, not a scientific endpoint defect. The remediation therefore does **not** change the completion space, policy set, mapping semantics, sidecar definition, source population, or selector logic.

The canonical selector adapter now:

- validates and loads the frozen Study 2 selector once per Python process;
- memoizes the deterministic mapping from `(policy, complete eight-Boolean state)` to Study 2 action;
- exposes an explicit cache-clear hook for tests.

The independent audit implements the same optimization **separately**, with its own selector/module cache and its own policy-state action cache. It does not use the canonical cache.

The guaranteed-sidecar algorithm still enumerates every required subset, every revealed Boolean assignment, and every remaining admissible completion exactly as frozen. No completion sampling, heuristic pruning, approximate search, or policy reduction was introduced.

Performance regression tests are intentionally machine-independent. They verify bounded selector/contract initialization counts rather than asserting a wall-clock duration. The exhaustive canonical selector-equivalence test still covers all 256 complete Boolean states across all eight `Study2Policy` values.

The remediated implementation at commit `039bca319987ceebdba52f080fb0f87b1d4e67ed` subsequently passed the actual-clone runner suite **6/6** and the complete Study 9 suite **69/69**, with both commands returning zero and the working tree clean. This closes the performance-remediation validation rather than leaving it pending.

## Canonical-run code freeze

`study9/CANONICAL_RUN_CODE_FREEZE.json` freezes the exact computational runtime that produced the successful pre-real-data actual-clone validation at commit `039bca319987ceebdba52f080fb0f87b1d4e67ed`.

The record binds SHA-256 and byte size for twelve computational files:

- the eleven Study 9 modules that implement completion enumeration, semantic mapping, selector adaptation, sidecar analysis, source identity verification, state projection, state grouping, canonical endpoint analysis, deterministic output, independent audit, and canonical orchestration;
- the frozen Study 2 selector used as the bounded downstream decision interface.

`contracts.py` is deliberately **not** included in its own computational hash set because this governance step modifies `contracts.py` to enforce the freeze. That avoids a circular self-hash. The validator remains included in the future `run_manifest.json` reproducibility identity, so its execution-time bytes are still recorded with the run.

The freeze is an **implementation freeze only**. It does not freeze scientific results, because no real Study 9 endpoint has yet been computed. It also does not authorize real data access, row-level analysis, result-directory creation, manuscript creation, or submission.

`contracts.py` now validates the code freeze in both the current closed phase and any future authorized execution phase. It fails closed if:

- the freeze is not bound to the tested commit;
- the 69/69 full-suite or 6/6 runner-suite evidence is altered;
- a frozen computational path is added, removed, or reordered;
- a frozen file's byte size changes;
- a frozen file's SHA-256 changes;
- the code-freeze execution boundary claims real rows, endpoints, or results already existed;
- the performance-remediation validation is returned to a pending state.

Any later byte change to a frozen computational file requires a new prospective code-freeze record and complete actual-clone validation before real canonical execution can be authorized.

## Independently reconstructed raw-row projection

`independent_audit.py` now reconstructs native recovery state directly from raw rows without importing or calling `state_projection.py`.

For CuCD-ID and AegisSat, the independent projector keeps all eight frozen recovery-state variables unresolved because there are no qualifying `DIRECT` or permitted `DERIVABLE_BY_PREDECLARED_RULE` mappings.

For UNSW-IoTSAT, it independently enforces the single frozen direct rule:

`Position_Anomaly -> security_signal`, numeric `0 -> false`, numeric `1 -> true`.

The independent implementation has its own normalization code. Attack labels and ambiguous fields remain excluded from operational state. A synthetic corruption test deliberately changes the canonical projector and confirms the independent projection diverges, preventing a self-auditing failure mode.

`contracts.py` also rejects any future direct import by `independent_audit.py` from `state_projection.py`, `mapping.py`, `state_groups.py`, or `canonical_engine.py`.

## Independent policy-independent endpoint audit

The independent audit now separately reconstructs:

- the 3-dataset x 8-variable mapping matrix;
- per-dataset operational `DIRECT` coverage;
- per-dataset operational `DIRECT`-or-`DERIVABLE` coverage;
- each dataset's unresolved recovery-state variables;
- the cross-dataset common-missing-state set.

The canonical runner compares these independently reconstructed values exactly against its canonical mapping/coverage output before any result can be written.

This is in addition to the already separate reconstruction of native-state multiplicities, admissible actions, unique-action counts, and guaranteed-minimal-sidecar results.

## Input verification architecture

Real execution, if later authorized, verifies frozen source identity before semantic row processing.

For CuCD-ID and UNSW-IoTSAT, the loader:

1. verifies the frozen release-ZIP SHA-256;
2. requires exactly one ZIP member with the frozen canonical member path;
3. verifies the canonical member SHA-256;
4. verifies a unique non-empty CSV header, exact column count, uniform row width, and exact row count;
5. only then streams rows for semantic projection.

For AegisSat, the deposited CSV itself is hash-verified before the same structural CSV checks.

The runner verifies each source after the canonical semantic pass, after the independent-audit pass, and once more immediately before atomic output. Any change fails closed.

## Minimal state projection

The frozen semantic adjudication intentionally limits primary state construction:

- CuCD-ID: no qualifying known recovery-state variable;
- AegisSat: no qualifying known recovery-state variable;
- UNSW-IoTSAT: exactly one known variable, `security_signal`, from `Position_Anomaly`.

Every other raw field is ignored for primary state construction. Attack/scenario labels, identifiers, timestamps, CRC/error fields, and other `AMBIGUOUS` or `ABSENT` semantics cannot enter the known-state map merely because they are present in a row.

## Lossless native-state collapse

The frozen Study 2 selector consumes only the eight Boolean recovery-state variables plus an explicitly supplied policy. Rows within one dataset are decision-equivalent only when their qualifying known recovery-state values and ordered unresolved-variable sets are identical.

`state_groups.py` collapses those rows into native-state groups with exact positive integer multiplicity. The sum of multiplicities must equal the verified source-row count. This is not sampling, deduplication, prevalence weighting, or row exclusion.

Raw fields outside qualifying recovery state, attack labels, and policy values do not enter the native-state grouping key.

## Frozen primary policy scope

Four substantive Study 2 policies remain primary and are evaluated separately in this frozen order:

1. `S2_B0_FAIL_CLOSED`
2. `S2_B1_FAIL_OPERATIONAL`
3. `S2_B2_RISK_THRESHOLD`
4. `S2_S1_EVIDENCE_AWARE`

The four `S2_ABL_NO_*` policies remain excluded mechanistic ablations. There is no canonical default or preferred policy, no primary policy pooling, and no policy-superiority claim.

Semantic mapping/coverage endpoints are policy-independent. Action-set, unique-action-identifiability, and guaranteed-sidecar endpoints are stratified by dataset and primary policy, yielding 12 primary analysis strata.

## Guaranteed sidecar endpoint

`minimal_sidecar_sets()` remains an assignment-conditioned synthetic helper only.

`guaranteed_minimal_sidecar_sets()` is the canonical Study 9 endpoint helper. For unresolved set `U`, subset `S` is sufficient only when every possible Boolean assignment to `S` leaves exactly one reachable action across every possible assignment to `U \\ S`. Every tied minimum-cardinality subset is retained in frozen variable order.

The canonical endpoint never asks for, predicts, imputes, or substitutes unavailable actual values of ambiguous or absent recovery state.

## Full synthetic end-to-end runner test

The runner test suite contains an end-to-end integration test using only temporary synthetic files. It creates:

- a tiny ZIP-backed CuCD-like CSV;
- a tiny direct Aegis-like CSV;
- a tiny ZIP-backed UNSW-like CSV containing synthetic `Position_Anomaly` values.

The test bypasses the real-execution gate only through `unittest.mock` inside the test process and replaces the frozen real input specifications only with temporary synthetic specifications. It then exercises the complete downstream pipeline:

verified source -> canonical raw-row projection -> lossless grouping -> four policy strata -> guaranteed sidecar -> independent raw-row projection -> independent grouping/endpoints -> canonical/audit comparisons -> deterministic eight-artifact output.

The synthetic pipeline runs twice against the same temporary inputs and requires every output artifact to be byte-identical across runs. It verifies the SHA-256 output manifest and confirms the independently reconstructed mapping/coverage outputs equal the canonical mapping/coverage outputs.

A separate synthetic integration test deliberately inverts the canonical UNSW `security_signal` projection. Because the independent audit projects raw rows separately, the runner detects a canonical/audit native-state grouping mismatch and produces no result directory.

A bounded-initialization integration test clears both selector caches, executes the complete synthetic runner, and requires exactly one frozen-contract initialization on the canonical selector path and exactly one on the independently implemented audit selector path.

These tests do not access any Study 9 real source bytes.

## Reproducibility identity in `run_manifest.json`

A future successful canonical run records a deterministic `reproducibility_identity` block using SHA-256 and byte size for the exact governance and runtime implementation files used by the run.

The bound governance files include:

- `STUDY9_PROTOCOL.json`;
- primary-population, semantic-adjudication, policy-scope, and canonical-execution-design freeze records;
- `PRE_REAL_DATA_ADVERSARIAL_AUDIT.json`;
- the recovery-state mapping rubric;
- the frozen dataset schema manifest.

The runtime identity includes every Study 9 semantic module used by canonical or independent execution plus the frozen Study 2 selector.

The runner captures this identity immediately after the authorization gate and recomputes it immediately before atomic output. Any governance or implementation byte change during execution fails closed.

The canonical-run code-freeze record is also added to the future run identity after the freeze is active.

## Deterministic outputs

A future authorized canonical run is designed to emit exactly:

- `run_manifest.json`
- `mapping_matrix.json`
- `coverage_summary.json`
- `native_state_groups.json`
- `policy_strata.json`
- `guaranteed_sidecar.json`
- `independent_audit.json`
- `output_sha256_manifest.json`

Outputs use canonical UTF-8 JSON with sorted keys, compact separators, no non-finite numeric values, and a trailing newline. Counts remain integers and fractions store integer numerator/denominator pairs. The output SHA-256 manifest hashes the seven substantive artifacts. Source dataset bytes are never copied into results.

## Atomic future execution-phase transition

The current protocol defines exactly two valid execution states.

### Closed hardened phase

All four execution authorization flags are false:

- `dataset_ingestion_authorized`
- `row_level_analysis_authorized`
- `canonical_execution_authorized`
- `results_directory_authorized`

The corresponding four implementation-phase execution booleans are also false, `synthetic_only=true`, and `loader_runner_synthetic_test_only=true`.

The canonical-run code freeze already exists in this closed phase. That is intentional: implementation is frozen before execution is authorized.

### Future open canonical phase

A future open transition is valid only when all four authorization flags and all four implementation-phase execution flags move to true together. The protocol status must simultaneously move to the prospectively declared canonical-execution-authorized status, and `synthetic_only` plus `loader_runner_synthetic_test_only` must become false.

The existing `study9/CANONICAL_RUN_CODE_FREEZE.json` remains mandatory and must continue to match every frozen computational file exactly. Any mixed or piecemeal transition fails closed. Manuscript creation and submission remain separate authorizations even after a future canonical execution phase is opened.

## Run the synthetic test suite

From the repository root:

```bash
PYTHONPATH="study9/src:study2/src" \
python3 -m unittest discover -s study9/tests -p 'test_*.py' -v
```

The suite covers frozen governance, temporary direct/ZIP input verification, projection, label exclusion, multiplicity conservation, completion enumeration, exhaustive selector equivalence, policy-stratified endpoint weighting, guaranteed-sidecar semantics, deterministic serialization, independent reconstruction, the closed execution guard, adversarial-audit bindings, atomic phase-transition rejection, bounded selector initialization, full synthetic eight-artifact runner behavior, and canonical-run code-freeze integrity/tamper checks.

Synthetic fixture files are created only in temporary directories and are not Study 9 source data.

## Fail-closed behavior

Among other invariants, `contracts.py` rejects the implementation if:

- a frozen dataset, semantic, policy, selector hash, input identity, or expected shape changes;
- a forbidden derivation rule appears;
- an excluded policy ablation enters primary analysis;
- policy pooling, averaging, or a default policy is introduced;
- unavailable actual state is allowed into the guaranteed-sidecar endpoint;
- attack labels influence primary state, grouping, action, or sidecar computation;
- exact multiplicity or deterministic-output requirements are weakened;
- independent audit imports canonical projection/mapping/grouping/engine modules;
- required loader/runner modules disappear, add non-standard-library absolute dependencies, or embed a local `/Users/...` path;
- the runner authorization guard is no longer immediately after frozen-contract loading;
- the adversarial-audit finding set or remediation bindings are altered;
- the run-manifest reproducibility identity path set changes;
- a frozen canonical-run computational byte size or SHA-256 changes;
- the actual-clone code-freeze evidence is altered;
- canonical execution flags are changed partially.

The separate performance-remediation tests additionally fail if exhaustive cached selector behavior diverges from the frozen selector or if either selector path repeatedly initializes frozen contracts after its cache is cleared.

## Not authorized in this phase

The current code-frozen phase does **not** authorize:

- reading or processing real dataset rows;
- probing the user's real dataset paths through `run_canonical_sources()`;
- committing dataset bytes to the repository;
- computing real Study 9 primary endpoints;
- creating a real `study9/results/` directory;
- executing excluded mechanistic ablations;
- modifying Study 2;
- modifying submitted Papers 1 through 4;
- drafting the Study 9 manuscript as a result-bearing manuscript;
- journal submission.

The next step, after this code-freeze governance update itself passes the actual-clone suite, is a **separate explicit real-data execution authorization gate**. Only that later atomic transition may permit the canonical runner to open the three frozen source populations and create the deterministic result artifacts.
