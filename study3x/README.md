# Study 3 Extension Workspace — S3X-ETA-001

**State:** `SOURCE_IDENTITY_FROZEN__READ_ONLY_CADENCE_SENSITIVITY_AUTHORIZED__NO_GAP_RULE__NO_TRACE_EXTRACTION__NO_RECOVERY_EXECUTION`  
**Authorization date:** 2026-09-26  
**Phase-5 branch base:** `cd4ad45e3f9112967ef24bde0b1258f0dce3d797`

This workspace exists only for the separately identified Paper-2 extension `S3X-ETA-001`.

The frozen Study-3 population `S3-K4E-001` is not modified, rerun, enlarged, or pooled by this workspace.

## Completed local source-verification gate

The author-executed Phase-4 workflow verified and froze ESA Anomaly Dataset v2 Mission-1 and Mission-2 source identity.

Recorded local archive SHA-256 values:

- Mission 1: `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72`
- Mission 2: `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5`

The schema inspection covered 76 Mission-1 channels and 100 Mission-2 channels, with no duplicate timestamps or non-monotonic transitions reported.

The local cadence-review CSV is bound by SHA-256:

`7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`

## Authorized in Phase 5

- read the already frozen Mission-1 and Mission-2 channel archives;
- verify each local channel archive against the SHA-256 recorded in the frozen schema report;
- calculate per-channel positive inter-sample delta distributions;
- evaluate the fixed candidate threshold formulas recorded in the Phase-5 gate;
- calculate aggregate exceedance counts, fractions, durations, and deterministic exceedance-fraction bands;
- record the top ten positive-delta values by frequency for each channel;
- write local-only sensitivity CSV/JSON outputs.

Use:

`/bin/bash study3x/validation/run_local_gap_sensitivity.sh`

## Not authorized

- selecting or freezing a gap rule;
- emitting timestamp-level gap traces;
- freezing an S3X trace population;
- replaying Study-3 recovery policies;
- generating S3X scientific results;
- appending S3X rows to the 1,380 frozen Study-3 trajectories;
- manuscript claims based on S3X;
- venue submission.

Large external source archives, extracted datasets, and generated sensitivity outputs remain local and untracked.

## Current gate

`AWAITING_LOCAL_READ_ONLY_GAP_SENSITIVITY_EXECUTION_AND_AUTHOR_REVIEW`
