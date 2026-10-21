# Paper 2 Phase-4 Local Validation Gate R1

**Status:** `AUTHORIZED_LOCAL_VALIDATION_TOOLING_PREPARED__AWAITING_USER_MACHINE_EXECUTION`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase4-local-validation`  
**Branch base:** `a46960b3aa56e9a51c4bf917dbe34e93dffb16e9`

## Predecessor

PR #174 merged the Phase-3 pre-execution workspaces.

Post-merge research-validation run:

- workflow: `Validate research configurations`
- run ID: `36270742611`
- run number: `1212`
- conclusion: `success`

## S3X local source verification

The authorized local workflow now has a resumable acquisition wrapper:

`study3x/validation/acquire_verify_freeze_esa_v2.sh`

It binds the exact Zenodo v2 files:

- Mission 1 URL: `https://zenodo.org/records/15237121/files/ESA-Mission1.zip?download=1`
- Mission 1 bytes: `3776246073`
- Mission 1 MD5: `9770ad12ed730238f37c42d5c27ab436`
- Mission 2 URL: `https://zenodo.org/records/15237121/files/ESA-Mission2.zip?download=1`
- Mission 2 bytes: `4098539932`
- Mission 2 MD5: `bfc72012691427d9327eb41f726ce45e`

The wrapper resumes interrupted downloads, verifies byte length and Zenodo MD5, computes SHA-256, extracts the two archives, runs the complete channel/schema inspector, and invokes the source-freeze finalizer.

It still does **not** freeze a gap rule, derive an empirical trace population, or run a recovery-policy experiment.

## S6X local pre-runtime validation

The authorized local workflow now has a materialization wrapper:

`study6x/validation/materialize_validate_cfs_v701.sh`

It:

- clones cFS `v7.0.1` only if the local checkout is absent;
- initializes only the `apps/lc` submodule needed for validation;
- verifies cFS and LC commit identities;
- runs the independent invariant-oracle unit tests;
- runs the static source-pin and fixture-patch dry-run validator;
- emits a local pre-runtime validation JSON.

It does **not** build cFS/LC, apply the fixture, sign artifacts, generate provenance observations, or execute a scientific campaign.

## Current gate

The repository cannot manufacture the local source-freeze or pre-runtime validation outputs because the user's local source/archive bytes are not available through the GitHub connector.

Required next evidence:

1. `study3x/local_freeze_work/S3X_SOURCE_FREEZE_001.json`
2. `study3x/local_freeze_work/ESA-Mission1.schema.json`
3. `study3x/local_freeze_work/ESA-Mission2.schema.json`
4. `study6x/workspace/S6X_PRE_RUNTIME_VALIDATION_001.json`

Only after those records are reviewed may a later gate consider an S3X gap-rule freeze or any S6X build.

Scientific execution remains unauthorized.
