# Paper 2 Phase-5C P99_X10 Gap-Rule Freeze Gate R1

**Status:** `TECHNICALLY_COMPLETE__MERGED__POST_MERGE_CI_SUCCESS__RULE_FROZEN`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase5c-p99x10-gap-rule-freeze`  
**Branch base:** `042a9461b86322c4e445adff70ff64089e7b9dc6`

## Basis

Phase 5B completed successfully and produced a local pre-freeze validation record:

- `S3X_P99_X10_PREFREEZE_VALIDATION_001.json`
- SHA-256: `cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0`
- audit id: `S3X-P99-X10-PREFREEZE-VALIDATION-001`
- candidate status: `VALIDATED_FOR_AUTHOR_REVIEW_NOT_SELECTED_NOT_FROZEN`
- channels: 176
- total exceedances: 1,919
- channels with exceedances: 171
- zero-exceedance channels: 5
- canonical channel projection SHA-256: `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`

The local pre-freeze run left the Git worktree clean.

## Frozen rule

Phase 5C records and freezes exactly:

`P99_X10`

Formula:

`threshold_seconds = 10 * channel-specific cadence_p99_seconds`

Comparison:

`positive inter-sample delta > threshold_seconds`

The comparison is strict greater-than. Equality with the threshold is not an exceedance.

## Selection characterization

This freeze is explicitly data-informed.

`P99_X10` was selected from the eight candidate formulas already evaluated in the Phase-5 sensitivity analysis. It was not prespecified as the final rule before inspection of the cadence distributions.

No cadence-class-specific multiplier is introduced. No new candidate family is added. The MAX_P99_MEDIAN family is not advanced.

## Provenance binding

The machine-readable freeze record binds:

- source freeze `S3X-ESA-V2-SOURCE-FREEZE-001`;
- cadence-review SHA-256 `7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`;
- R2 sensitivity CSV SHA-256 `f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e`;
- R2 delta-frequency CSV SHA-256 `1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349`;
- R2 summary JSON SHA-256 `c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6`;
- Phase-5B validation JSON SHA-256 `cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0`;
- canonical 176-channel projection SHA-256 `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

## Lock policy

Once this Phase-5C freeze is merged:

- the next timestamp-level extraction must use this exact rule;
- the threshold may not be retuned after inspecting extracted timestamp locations;
- this freeze record may not be overwritten;
- any future rule change requires a new versioned protocol and separate author authorization.

## Interpretation firewall

A `P99_X10` exceedance is only an extreme telemetry inter-sample interval diagnostic.

It is not asserted to be:

- RF contact loss;
- ground-station visibility;
- spacecraft outage;
- cyberattack truth;
- onboard recovery latency;
- operational command availability.

## Closed gates

Phase 5C does **not** authorize:

- timestamp-level gap-trace extraction;
- trace-population freeze;
- recovery-policy execution;
- S3X scientific execution;
- manuscript claims based on S3X;
- changes to frozen Studies 3, 4, or 6;
- venue lock or publisher submission.

## Next gate

`AUTHOR_REVIEW_BEFORE_PHASE6_TIMESTAMP_LEVEL_TRACE_EXTRACTION_DESIGN`


## Completion record

Phase 5C is technically complete.

- PR: `#180`
- pre-merge head: `a85b1cefa50d55adc1c61ee581cf6a3ad2279ddd`
- pre-merge CI: run `36298410362` / run number `1226` / success
- merge commit: `ac5b2e1cedafbcc2c15da41f5c0b254256850afc`
- post-merge CI: run `36299292647` / run number `1227` / success
- `main` after merge: `ac5b2e1cedafbcc2c15da41f5c0b254256850afc`

The P99_X10 freeze is therefore active repository state. Timestamp-level extraction remains closed pending a separately authorized Phase-6 design.
