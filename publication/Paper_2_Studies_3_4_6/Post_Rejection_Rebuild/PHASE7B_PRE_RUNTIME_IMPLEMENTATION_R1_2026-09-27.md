# Paper 2 Phase 7B — S3X Replay Implementation and Pre-Runtime Validation

**Status:** `SYNTHETIC VALIDATION ONLY — NO REAL FROZEN-INTERVAL EXECUTION`

Phase 7B implements the merged Phase-7A contract without evaluating the real 1,919-member trace population.

## Bound implementation

Primary:

`study3x/src/recovery_replay.py`

Git blob:

`09a1c887f8861a6e5dba6059cab2ab906befbbcd`

Reference:

`study3x/audit/reference_replay.py`

Git blob:

`9e13446323be67115950374cb5debfaa7532a17e`

The primary path calls the immutable Study-3 `select_action` function. The reference path does not import the primary implementation and separately encodes the frozen B0/B2/S1 decision table and exact rational timing arithmetic.

## Frozen bindings

- Phase-7A merge/main: `445435aaa1618e0a08df35071221451f35ef5e98`
- Phase-7 protocol blob: `f42fe8c0c58ee3b9152e629f5673bd5c71ffede4`
- Phase-6C trace-freeze blob: `ed0bdcec443b7f0c3ee80d441e1122f32e499d3e`
- Study-3 temporal model blob: `b13e62456c144db0e12808bf700586c1c844c33d`
- frozen interval CSV SHA-256: `cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`
- frozen interval count: 1,919
- later prospective runtime case count: 34,542

## Pre-runtime behavior

The primary implementation validates the interval-row contract, including frozen rule identity and strict P99_X10 membership consistency, but it does not select, drop, or retune interval membership.

For each supplied interval row it can deterministically expand the Phase-7 factor grid:

- 3 policies;
- 3 evidence states;
- 2 timing arms;
- 18 modeled cases per interval.

No population-level runner exists in Phase 7B.

Both implementation modules terminate with an explicit fail-closed message if invoked directly.

## Synthetic verification only

CI uses synthetic interval fixtures that satisfy the frozen schema and P99_X10 relationship. It verifies:

- exact rational normalization;
- all 18 combinations per synthetic interval;
- B0/S1/B2 policy behavior;
- V0/V4/V5 first-refresh semantics;
- cache-origin exposure behavior;
- protective-hiatus behavior;
- V5 qualification timing;
- exact primary/reference parity;
- rejection of inconsistent frozen-rule rows;
- rejection of a nonmatching interval-artifact SHA-256.

Synthetic fixture output is implementation verification, not scientific evidence.

## Current closed gates

Phase 7B does not authorize:

- reading the real frozen interval CSV for replay;
- expanding the real 1,919 intervals;
- producing the 34,542 scientific cases;
- canonical Phase-7 outputs;
- result interpretation;
- manuscript claims;
- P99_X10 retuning;
- interval-membership changes;
- Study-3 modification or pooling.

## Next gate

`AUTHOR_REVIEW_AFTER_PHASE7B_IMPLEMENTATION_PR_AND_PREMERGE_CI_BEFORE_MERGE`
