# Paper 2 Phase-5B P99_X10 Pre-Freeze Validation Gate R1

**Status:** `AUTHORIZED_PREFREEZE_VALIDATION_TOOLING__AWAITING_CI_AND_LOCAL_EXECUTION`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase5b-p99x10-prefreeze`  
**Branch base:** `6c8d91b75e7ad994bfb02d041ba46a0eab52b89b`

## Evidence basis

The corrected Phase-5A R2 local run completed successfully with a clean post-run worktree.

Bound R2 evidence:

- `S3X_GAP_SENSITIVITY_002.csv`: `f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e`
- `S3X_DELTA_FREQUENCIES_002.csv`: `1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349`
- `S3X_GAP_SENSITIVITY_SUMMARY_002.json`: `c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6`

The R2 package contains 176 channels, eight candidate rules, and 1,408 sensitivity rows. The output contract separates cadence and exceedance metrics and binds both CSV hashes in the summary.

## Candidate advanced to pre-freeze validation

`P99_X10` is advanced to a validation gate only.

Formula:

`threshold_seconds = 10 * channel-specific cadence_p99_seconds`

Comparison semantics:

`positive inter-sample delta > threshold_seconds`

Expected aggregate from the reviewed R2 evidence:

- channels: 176;
- total exceedances: 1,919;
- channels with exceedances: 171;
- zero-exceedance channels: 5.

The five zero-exceedance channels are:

- `ESA-Mission2/channel_66.zip`
- `ESA-Mission2/channel_67.zip`
- `ESA-Mission2/channel_68.zip`
- `ESA-Mission2/channel_69.zip`
- `ESA-Mission2/channel_100.zip`

A canonical, sorted channel-level projection over mission, channel file, channel SHA-256, positive-delta count, channel P99, threshold, and exceedance count is bound by:

`f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`

This digest allows fail-closed verification of all 176 channel-level counts without storing or emitting timestamp-level intervals.

## Why Phase 5B does not freeze the rule

Advancement is not rule selection or rule freeze. Phase 5B only checks whether the already observed R2 `P99_X10` aggregate can be reproduced exactly from the bound diagnostic artifacts and whether the formula/comparison semantics are internally consistent.

No cadence-class-specific multiplier is introduced in this phase. No new candidate family is created.

## Authorized validation

The local pre-freeze validator may:

1. verify exact SHA-256 values for the three R2 artifacts;
2. verify R2 summary identity, schema, and closed scientific gates;
3. select only existing `P99_X10` rows from the R2 sensitivity CSV;
4. verify 176 unique channel records;
5. verify `threshold = 10 * channel-specific P99`;
6. verify nonzero rows have a minimum exceedance strictly greater than threshold;
7. verify zero rows contain no exceedance-distribution values and have channel maximum no greater than threshold;
8. verify the canonical 176-channel projection digest;
9. verify the aggregate total of 1,919 and the exact five zero-exceedance channels;
10. emit one local aggregate pre-freeze validation JSON record.

The validator must not read the original telemetry archives and must not emit timestamp-level gap traces.

## Interpretation firewall

A `P99_X10` exceedance remains an extreme telemetry inter-sample interval diagnostic. It is not asserted to be:

- RF contact loss;
- a ground-station visibility interval;
- a spacecraft outage;
- a cyberattack;
- onboard recovery latency;
- operational command availability.

## Closed gates

Still prohibited:

- gap-rule selection;
- gap-rule freeze;
- timestamp-level gap traces;
- trace-population freeze;
- recovery-policy execution;
- S3X scientific execution;
- changes to frozen Studies 3, 4, or 6;
- manuscript claims based on S3X;
- venue lock or publisher submission.

Next gate:

`AUTHOR_REVIEW_OF_P99_X10_PRE_FREEZE_VALIDATION_BEFORE_GAP_RULE_FREEZE_OR_TIMESTAMP_TRACE_EXTRACTION`
