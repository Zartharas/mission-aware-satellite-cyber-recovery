# Paper 2 Phase-5 Cadence Sensitivity Gate R1

**Status:** `AUTHORIZED_READ_ONLY_SENSITIVITY_TOOLING__AWAITING_LOCAL_EXECUTION`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase5-cadence-sensitivity`  
**Branch base:** `cd4ad45e3f9112967ef24bde0b1258f0dce3d797`

## Basis

Phase 4 completed the authorized local source-verification and pre-runtime validation gates.

S3X local source identity is frozen against ESA Anomaly Dataset v2 Mission-1 and Mission-2. The author-provided local evidence recorded:

- Mission-1 archive SHA-256: `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72`
- Mission-2 archive SHA-256: `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5`
- Mission-1 schema-report SHA-256: `696ad9bfa90ff37e2c22bb7eb0c1778af4225a09b02038130698d402b53aaa0a`
- Mission-2 schema-report SHA-256: `25533581a3585a8b3056081e1e47f4907d7664103aad5527e374510c0ffba62e`
- channel count: 176
- cadence-review CSV SHA-256: `7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`

The cadence review showed multiple timing regimes across the 176 channels, so a single absolute or median-multiple threshold is not frozen from summary statistics alone.

## Authorized diagnostic analysis

The local analyzer may read the already frozen channel archives and calculate aggregate sensitivity diagnostics for these candidate formulas:

- `P99_X1`
- `P99_X2`
- `P99_X3`
- `P99_X5`
- `P99_X10`
- `MAX_P99_MEDIAN_X2`
- `MAX_P99_MEDIAN_X3`
- `MAX_P99_MEDIAN_X5`

For each channel and candidate formula, the tool may report:

- positive-delta count;
- threshold value;
- exceedance count and fraction;
- minimum, median, p95, p99, and maximum exceedance duration;
- total interval duration represented by exceedances;
- total excess duration above the candidate threshold;
- cadence class;
- top ten positive-delta values by frequency.

The summary may report zero-exceedance channels and deterministic exceedance-fraction bands. These are diagnostics only; they are not labels of operational plausibility or anomaly truth.

## Provenance controls

Before analyzing a channel, the tool must:

1. bind the exact source-freeze record;
2. bind the exact schema-report SHA-256 recorded by that freeze;
3. verify the actual local channel-archive SHA-256 against the frozen schema report;
4. fail closed on duplicate or non-monotonic timestamps.

The audit emits only aggregate interval diagnostics. It does not emit timestamp-level gap intervals.

## Outputs

Local-only, ignored outputs:

- `study3x/local_freeze_work/S3X_GAP_SENSITIVITY_001.csv`
- `study3x/local_freeze_work/S3X_DELTA_FREQUENCIES_001.csv`
- `study3x/local_freeze_work/S3X_GAP_SENSITIVITY_SUMMARY_001.json`

## Closed gates

The following remain unauthorized:

- selecting a gap rule;
- freezing a gap rule;
- emitting timestamp-level gap traces;
- freezing a trace population;
- recovery-policy replay;
- S3X scientific execution;
- manuscript claims based on S3X;
- S6X build or scientific execution;
- S4X execution.

The next gate is author review of the complete sensitivity outputs before any gap-rule selection.
