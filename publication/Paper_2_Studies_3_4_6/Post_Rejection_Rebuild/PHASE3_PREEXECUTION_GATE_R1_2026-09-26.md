# Paper 2 Phase-3 Pre-Execution Gate R1

**Status:** `AUTHORIZED_SCOPE_IMPLEMENTED__SCIENTIFIC_EXECUTION_CLOSED`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase3-preexecution`

## Predecessor verification

PR #173 completed branch CI successfully and was merged into `main` at:

`a2b6f2e02c4075d2e9cd1976888dae38464a11c1`

Validation records:

- pre-merge workflow run `36268050167` / run `1208` / success;
- post-merge workflow run `36268665292` / run `1209` / success.

## S3X authorization and implementation

The author authorized local verification and source-identity freeze of the ESA Anomaly Dataset v2 Mission-1 and Mission-2 source bytes.

The repository now contains:

- `study3x/S3X_SOURCE_VERIFICATION_AUTHORIZATION_20260926.json`;
- `study3x/validation/finalize_esa_v2_source_freeze.py`;
- `study3x/validation/run_local_source_freeze.sh`.

The connected repository environment does not contain the approximately 7.9 GB of authorized Mission-1/Mission-2 outer archives or their extracted local directories. Therefore the repository **does not claim the source freeze is complete**.

A valid local freeze must verify the published Zenodo MD5 values, compute local SHA-256 values, validate all 76 Mission-1 and 100 Mission-2 channel archives through the read-only schema reports, and then emit `S3X_SOURCE_FREEZE_001.json`.

Even after that source freeze, the empirical gap rule, trace population, and recovery-policy replay remain separately gated.

## S6X authorization and implementation

The author authorized creation of the S6X implementation workspace and pre-runtime validation only.

The repository now binds:

- cFS `v7.0.1` tag commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`;
- LC submodule commit `a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a`;
- exact Git blob identities for the LC comparison source, requirements, direct unit tests, and README;
- the independent frozen GT/GE equality-boundary oracle;
- fixture patch `S6X_FIXTURE_GT_EQ_BOUNDARY_001`;
- a local cFS checkout validator that performs only source identity and `git apply --check` validation.

No cFS build, fixture application, signing, provenance-observation generation, independent rebuild, qualification-gate run, or canonical S6X result is authorized.

## Scientific separation

Studies `S3-K4E-001`, `S4-MPQ-001`, and `S6-SCTR-001` remain immutable.

S3X and S6X are separately identified prospective extension populations. They may later corroborate or bound the frozen studies, but they are not appended to or pooled with the original populations.

S4X remains on hold.

## Publication gate

Paper-2 manuscript R11/R12 drafting, venue locking, and publisher submission remain closed.

## Next gate

`AUTHOR_REVIEW_AFTER_PHASE3_CI_AND_LOCAL_S3X_SOURCE_FREEZE_OUTPUT_BEFORE_ANY_BUILD_OR_SCIENTIFIC_EXECUTION`
