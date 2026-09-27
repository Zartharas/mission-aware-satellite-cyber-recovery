# Study 3 Extension Workspace — S3X-ETA-001

**State:** `PHASE5C_P99_X10_GAP_RULE_FROZEN__NO_TRACE_EXTRACTION__NO_RECOVERY_EXECUTION__NO_SCIENTIFIC_EXECUTION`  
**Authorization date:** 2026-09-26  
**Phase-5C branch base:** `042a9461b86322c4e445adff70ff64089e7b9dc6`

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

## Historical Phase-5 gate

`AWAITING_LOCAL_READ_ONLY_GAP_SENSITIVITY_EXECUTION_AND_AUTHOR_REVIEW`


## Phase-5 local result

The author-executed R1 sensitivity run completed successfully:

- channels analyzed: 176;
- candidate rules: 8;
- sensitivity rows: 1,408;
- post-run Git working tree: clean;
- gap rule selected: no;
- gap rule frozen: no;
- trace extraction: no;
- recovery-policy execution: no;
- scientific execution: no.

R1 local evidence hashes are recorded in `PAPER2_PHASE5A_SENSITIVITY_OUTPUT_FIX_STATUS.json`.

## Phase-5A output-contract correction

Review of the R1 sensitivity CSV identified an output-schema collision: generic cadence metric names were overwritten by generic exceedance metric names during dictionary expansion. Recalculation against the separately preserved cadence review found zero threshold-formula mismatches across all 1,408 rows, so Phase 5A corrects the exported representation rather than changing the threshold formulas.

The corrected analyzer emits distinct `cadence_*` and `exceedance_*` metrics, and the R2 summary binds the SHA-256 values of both generated CSV files.

Historical R1 tooling is preserved as:

- `study3x/validation/analyze_cadence_gap_sensitivity_r1.py`
- `study3x/validation/run_local_gap_sensitivity.sh`

The corrected R2 runner is:

`/bin/bash study3x/validation/run_local_gap_sensitivity_r2.sh`

R2 output names:

- `S3X_GAP_SENSITIVITY_002.csv`
- `S3X_DELTA_FREQUENCIES_002.csv`
- `S3X_GAP_SENSITIVITY_SUMMARY_002.json`

## Current gate

`AWAITING_PHASE5A_CI_AND_CORRECTED_LOCAL_R2_RERUN_BEFORE_ANY_GAP_RULE_SELECTION`


## Phase-5B pre-freeze validation

The corrected R2 evidence is now bound in `PAPER2_PHASE5B_P99X10_PREFREEZE_STATUS.json`. `P99_X10` advances only to pre-freeze validation and remains unselected and unfrozen. The validator checks the 176 channel-level rows, the 1,919 aggregate exceedances, the exact five zero-exceedance channels, the channel-specific P99 multiplier, strict exceedance semantics, and the canonical channel projection digest. It consumes only the R2 aggregate artifacts and does not read source telemetry or emit timestamp-level intervals.

Current gate: `AUTHOR_REVIEW_OF_P99_X10_PRE_FREEZE_VALIDATION_BEFORE_GAP_RULE_FREEZE_OR_TIMESTAMP_TRACE_EXTRACTION`.


## Phase-5C frozen gap rule

The author-approved machine-readable freeze record is:

`study3x/config/S3X_GAP_RULE_FREEZE_001.json`

Frozen method:

- rule: `P99_X10`;
- threshold: `10 * channel-specific cadence_p99_seconds`;
- comparison: strict `delta > threshold`;
- selection basis: data-informed selection from the eight formulas already evaluated in Phase 5;
- cadence-class-specific retuning: not introduced.

The freeze binds the successful Phase-5B validation record SHA-256 `cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0` and canonical 176-channel projection SHA-256 `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

The frozen rule must not be retuned after timestamp-level locations are inspected. Any future change requires a separately authorized, versioned protocol.

Phase 5C does not authorize timestamp-level trace extraction, trace-population freeze, recovery execution, scientific execution, or manuscript claims.

## Phase-5C current gate

`AUTHOR_REVIEW_BEFORE_PHASE6_TIMESTAMP_LEVEL_TRACE_EXTRACTION_DESIGN`
