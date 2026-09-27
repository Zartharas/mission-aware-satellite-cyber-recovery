# Paper 2 Phase-6B Timestamp Extraction Authorization Gate R1

**Status:** `AUTHORIZATION RECORD PREPARED__NOT MERGED__NO EXTRACTION PERFORMED`  
**Authorization date:** 2026-09-27  
**Branch:** `paper2/post-rejection-phase6b-timestamp-extraction-authorization`  
**Branch base:** `92534c45c85ee36c148acfe92dce1ec61ad49c24`

## Purpose

Phase 6B prepares the separate versioned runtime authorization record required by the merged Phase-6A design before any real ESA-v2 timestamp-level candidate extraction can occur.

The authorization record is:

`study3x/config/S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_001.json`

Authorization ID:

`S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001`

This phase does not itself run the local extractor. It does not materialize timestamp-level candidate rows, freeze a trace population, execute recovery policies, generate scientific results, or make manuscript claims.

## Bound design evidence

The record binds the merged Phase-6A design state:

- design PR: `#186`;
- validated pre-merge head:
  `1dd687683084990cc52204cd7964316782a117f6`;
- pre-merge CI: run `#1243` / run id `36334066942` / success;
- design merge commit:
  `92534c45c85ee36c148acfe92dce1ec61ad49c24`;
- design post-merge CI: run `#1244` / run id `36334882085` / success;
- merged protocol:
  `S3X-PHASE6-TIMESTAMP-TRACE-EXTRACTION-PROTOCOL-001`;
- merged protocol SHA-256:
  `f6957393a864090d484e29f16067807bf52cacf0688fc48af32164ef9f7eb5a4`.

The protocol file itself remains the immutable design artifact. Phase 6B does not modify it.

## Authorized scope

Once the authorization record is separately reviewed and merged to `main`, it authorizes only:

1. candidate P99_X10 timestamp-level interval extraction from the already frozen ESA-v2 source;
2. independent source-recomputation validation of that candidate population;
3. deterministic repeat execution into two separate clean local output directories;
4. SHA-256 comparison of the four canonical candidate artifacts across both clean runs.

The authorization does not extend beyond those operations.

## Frozen numerical and population constraints

The runtime remains bound to:

- experiment: `S3X-ETA-001`;
- source freeze: `S3X-ESA-V2-SOURCE-FREEZE-001`;
- gap-rule freeze: `S3X-P99X10-GAP-RULE-FREEZE-001`;
- rule: `P99_X10`;
- threshold:
  `10 * channel-specific cadence_p99_seconds`;
- comparison:
  strict `positive inter-sample delta > threshold_seconds`;
- channels: 176;
- expected intervals: 1,919;
- channels with intervals: 171;
- zero-interval channels: exactly five;
- canonical channel projection SHA-256:
  `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

The aggregate values are validation invariants. They are not tuning targets.

## Runtime safety conditions

The merged Phase-6A runner already requires all of the following before real extraction:

- current branch is `main`;
- tracked worktree is clean;
- authorization record is a tracked versioned file under `study3x/config/`;
- authorization record binds the merged protocol SHA-256;
- design merge verification is true;
- design post-merge CI success is recorded;
- author execution approval is recorded;
- output stays beneath ignored `study3x/local_freeze_work/`;
- output directory is empty before execution;
- source archive, source-freeze, schema-report, per-channel hash, and row-count checks pass;
- no runtime multiplier or threshold override is exposed.

This Phase-6B record satisfies the required authorization semantics, but it is not effective for the runner while it exists only on this feature branch.

## Deterministic repeatability requirement

A later authorized local execution must use two separate clean output directories.

The following artifacts must be byte-identical across the two runs:

- `S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json`

A hash mismatch is a stop condition.

No trace-population-freeze review may begin until repeatability passes.

## Explicitly closed gates

Phase 6B does not authorize:

- trace-population freeze;
- Study-3 recovery-policy execution;
- S3X scientific execution;
- Paper-2 manuscript claims based on S3X;
- P99_X10 retuning;
- source substitution;
- frozen Study 3, Study 4, or Study 6 modification;
- venue lock or submission action.

## Interpretation firewall

A P99_X10-positive row remains only an extreme telemetry inter-sample interval diagnostic.

It is not asserted to establish:

- RF contact loss;
- ground-station visibility loss;
- spacecraft outage;
- cyberattack truth;
- onboard recovery latency;
- operational command availability.

## Current effectivity

The authorization record has been prepared on a feature branch.

Therefore:

`timestamp_level_extraction_authorized_by_author = YES`

but:

`authorization_record_effective_for_runner = NO`

because the runner requires the record to be tracked on `main`.

No real ESA timestamp extraction is performed during this preparation phase.

## Next gate

After the Phase-6B authorization PR diff and pre-merge CI are reviewed:

`AUTHOR_REVIEW_AFTER_PHASE6B_AUTHORIZATION_PR_AND_PREMERGE_CI_BEFORE_MERGE`

A later merge approval may merge the authorization record. Real local extraction must still wait until the resulting `main` state and post-merge CI are verified.
