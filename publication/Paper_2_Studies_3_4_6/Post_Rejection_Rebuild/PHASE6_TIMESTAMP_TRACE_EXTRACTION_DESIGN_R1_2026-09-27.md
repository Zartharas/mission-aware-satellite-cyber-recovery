# Paper 2 Phase-6 Timestamp-Level Trace Extraction Design R1

**Status:** `DESIGN ONLY__NO_TIMESTAMP_EXTRACTION_AUTHORIZED`  
**Authorization date:** 2026-09-27  
**Branch:** `paper2/post-rejection-phase6-timestamp-trace-design`  
**Branch base:** `1d36b224e46c15653f0c5d76dce6da26f7d9a6e1`

## Purpose

Phase 6A prepares a deterministic, fail-closed implementation for later timestamp-level materialization of the already frozen `P99_X10` telemetry inter-sample interval diagnostic.

This phase is repository design only. It does not inspect timestamp locations from the frozen ESA-v2 source, does not execute the extractor against real telemetry, does not freeze an S3X trace population, does not execute Study-3 recovery policies, does not generate scientific results, and does not create manuscript claims.

## Frozen upstream authority

Experiment:

`S3X-ETA-001`

Source freeze:

`S3X-ESA-V2-SOURCE-FREEZE-001`

Source-freeze SHA-256:

`dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27`

Mission archive SHA-256 values:

- ESA-Mission1: `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72`
- ESA-Mission2: `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5`

Frozen gap-rule authority:

`S3X-P99X10-GAP-RULE-FREEZE-001`

Rule:

`P99_X10`

Formula:

`threshold_seconds = 10 * channel-specific cadence_p99_seconds`

Comparison:

`positive inter-sample delta > threshold_seconds`

The comparison remains strict greater-than. Equality is not an exceedance.

The Phase-5B bound aggregate remains:

- channels: 176;
- intervals/exceedances: 1,919;
- channels with exceedances: 171;
- zero-exceedance channels: 5;
- canonical channel projection SHA-256:
  `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

These quantities are validation invariants, not targets for threshold tuning.

## Exact numerical reproduction contract

Phase 6 must reproduce the Phase-5 numerical path rather than substitute a mathematically similar implementation.

For each frozen channel archive:

1. load the channel with `pandas.read_pickle`;
2. convert the dataframe index with `pandas.to_datetime`;
3. obtain exact timestamp integers from `DatetimeIndex.asi8`;
4. compute adjacent nanosecond differences;
5. fail on duplicate timestamps;
6. fail on negative/non-monotonic timestamp transitions;
7. retain strictly positive deltas;
8. convert each positive delta using `delta_nanoseconds / 1000000000.0`;
9. compute the channel P99 using the same repository linear-interpolation algorithm used by Phase 5;
10. calculate `threshold_seconds = cadence_p99_seconds * 10.0`;
11. emit only intervals satisfying strict `delta_seconds > threshold_seconds`.

No runtime multiplier or threshold override is permitted.

## Source integrity requirements

Before source timestamps may be evaluated during a later authorized run, the extractor must verify:

- the source-freeze JSON SHA-256;
- source-freeze ID and experiment ID;
- both frozen outer archive SHA-256 values;
- both frozen schema-report SHA-256 values;
- the expected 76 Mission-1 and 100 Mission-2 channel counts;
- every individual channel archive SHA-256 against the frozen schema report;
- each channel row count against the frozen schema report.

Any mismatch fails closed before candidate output is accepted.

## Runtime authorization separation

The Phase-6A design protocol intentionally records:

`timestamp_level_extraction_authorized = false`

The extractor and independent validator both require a separate versioned runtime authorization record with the fixed identity:

`S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001`

That record is intentionally not created in Phase 6A.

A future authorization record must bind the exact SHA-256 of the merged Phase-6 protocol and may authorize only timestamp-level candidate extraction. It must continue to keep trace-population freeze, recovery-policy execution, and scientific execution closed.

The record must also explicitly state that the Phase-6 design merge has been verified, that its post-merge CI succeeded, and that author execution approval has been recorded. The local runner additionally requires the authorization record to be a tracked, unmodified file under study3x/config, requires execution from main, and requires a clean tracked worktree.

This separation prevents design approval, a local hand-crafted JSON file, or design merge from silently becoming scientific execution approval.

## Candidate interval identity

Each candidate interval receives a stable full SHA-256 identifier.

Canonical preimage fields, separated by a literal vertical bar, are:

1. experiment ID;
2. gap-rule freeze ID;
3. mission;
4. channel filename;
5. channel SHA-256;
6. preceding timestamp in integer nanoseconds;
7. following timestamp in integer nanoseconds.

The identifier is:

`S3X-INT-<full SHA-256 hex digest>`

Digest truncation is not permitted.

The interval identity therefore remains independent of filesystem enumeration and CSV row position.

## Timestamp representation

The candidate CSV preserves both:

- exact integer nanoseconds used in computation; and
- a human-readable ISO representation derived from the same integer timestamp.

The design does not append a UTC designator or make a timezone claim that is absent from the source timestamp representation.

## Candidate row contract

Each emitted row contains:

- schema version;
- experiment ID;
- source-freeze ID and SHA-256;
- gap-rule freeze ID and rule;
- mission;
- channel filename and channel SHA-256;
- preceding timestamp in nanoseconds and human-readable form;
- following timestamp in nanoseconds and human-readable form;
- delta nanoseconds;
- delta seconds;
- channel P99 seconds;
- threshold seconds;
- strict comparison operator;
- diagnostic label;
- stable interval ID.

The diagnostic label is:

`EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC`

It is not an RF-outage, spacecraft-outage, communications-outage, cyberattack, recovery-episode, or contact-window label.

## Deterministic ordering

Candidate output is sorted by:

1. fixed mission order: ESA-Mission1, then ESA-Mission2;
2. numeric channel number;
3. preceding timestamp nanoseconds;
4. following timestamp nanoseconds;
5. interval ID.

Filesystem ordering is never an output-order authority.

The independent Phase-5B canonical channel projection remains separate and retains the exact original Phase-5B serialization: a fixed seven-column header, lexicographic `(mission, channel_file)` ordering, and `.17g` float normalization.

## Aggregate invariants

A later authorized real-source execution must fail unless it independently reproduces:

- 176 channels;
- 1,919 candidate intervals;
- 171 channels with candidate intervals;
- exactly five zero-interval channels:
  - ESA-Mission2/channel_66.zip
  - ESA-Mission2/channel_67.zip
  - ESA-Mission2/channel_68.zip
  - ESA-Mission2/channel_69.zip
  - ESA-Mission2/channel_100.zip
- canonical channel projection SHA-256:
  `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

A mismatch is a stop condition. The implementation must never change the multiplier, quantile method, comparison operator, channel population, or source selection to force the count back to 1,919.

## Deterministic repeatability gate

A later authorized Phase-6 execution is not complete after a single successful extraction.

The exact frozen source, merged protocol, tracked authorization record, extractor, and independent validator must be run into two separate clean local output directories. SHA-256 values must match for all four canonical candidate artifacts:

- `S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json`

Canonical outputs may not contain wall-clock timestamps, hostnames, usernames, temporary paths, or other execution-specific metadata that would defeat byte-for-byte reproducibility.

A repeatability mismatch is a stop condition and must be investigated before any trace-population freeze review.

## Candidate local outputs

Generated real-data outputs remain under the already ignored local tree:

`study3x/local_freeze_work/phase6/`

Planned files are:

- `S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json`
- `S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json`

Phase 6A commits none of those outputs.

The repository paths `study3x/traces`, `study3x/results`, and `study3x/canonical` remain prohibited by the current gate.

## Independent validator

The independent validator does not import the extractor.

During a later authorized execution it independently:

- verifies the same source and channel hashes;
- re-reads every frozen channel;
- independently recomputes positive deltas;
- independently recomputes the linear P99;
- independently applies strict `delta > 10 * P99`;
- independently recreates stable interval IDs;
- confirms all candidate rows are present and no extras exist;
- confirms deterministic ordering;
- confirms every exact timestamp/delta relationship;
- confirms the five zero-exceedance channels;
- confirms the 1,919 total;
- confirms the Phase-5B canonical channel projection hash;
- confirms candidate output hashes through the manifest.

The validator emits only a validation record. It does not freeze the population.

## Repository-safe tests

Phase 6A CI uses synthetic-only unit tests.

The tests cover:

- exact linear P99 interpolation;
- strict-greater-than threshold behavior, including equality exclusion;
- stable full SHA-256 interval identities;
- numeric channel output ordering;
- exact Phase-5B projection serialization agreement;
- closed runtime gates;
- absence of a committed runtime authorization record.

CI does not read ESA telemetry, invoke the real-source runner, produce timestamp-level candidate rows, or perform recovery execution.

## Fail-closed repository audit

The repository audit verifies:

- protocol/status file identities;
- frozen source/rule bindings;
- exact 1,919/171/5 aggregate invariants;
- strict comparison and multiplier;
- no runtime threshold or multiplier CLI overrides;
- no committed runtime authorization record;
- no `study3x/traces`, `study3x/results`, or `study3x/canonical` path;
- Python syntax of dormant Phase-6 modules;
- Bash syntax of the local runner;
- ignored local source/output paths;
- release-gate CI wiring for the design audit;
- absence of real Phase-6 source execution from GitHub Actions.

## Interpretation firewall

A P99_X10-positive observation is only an extreme telemetry inter-sample interval derived from the frozen ESA-v2 timestamp sequence.

It does not, by itself, establish:

- RF contact loss;
- ground-station visibility loss;
- spacecraft outage;
- cyberattack truth;
- onboard recovery latency;
- operational command unavailability.

## Phase-6A completion boundary

Phase 6A may:

- add this design;
- add machine-readable protocol/status records;
- add dormant repository-safe implementation;
- add synthetic tests;
- add the fail-closed audit;
- open a draft PR;
- run pre-merge CI.

Phase 6A may not:

- create the runtime authorization record;
- execute the extractor against ESA telemetry;
- materialize real timestamp-level rows;
- freeze a trace population;
- run Study-3 recovery policies;
- create scientific results;
- modify frozen Studies 3, 4, or 6;
- retune P99_X10;
- rewrite Paper-2 R11/R12;
- create manuscript claims from S3X.

## Next gate

After the draft PR diff and pre-merge CI are reviewed:

`AUTHOR_REVIEW_AFTER_PHASE6_DESIGN_PR_AND_PREMERGE_CI_BEFORE_MERGE`

Even after a future design merge, timestamp-level execution still requires a separately authorized and versioned runtime-authorization record.

Phase 6A therefore **does not freeze** the extracted trace population and does not authorize scientific execution.
