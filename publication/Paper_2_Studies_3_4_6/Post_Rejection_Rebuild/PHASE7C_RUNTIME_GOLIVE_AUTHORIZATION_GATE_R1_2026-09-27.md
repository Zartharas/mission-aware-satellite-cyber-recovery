# Paper 2 Phase 7C — Runtime / Go-Live Authorization Preparation

**Authorization ID:** `S3X-PHASE7-RUNTIME-AUTH-001`  
**Status:** `PREPARED ON FEATURE BRANCH — NOT EFFECTIVE`

## Purpose

Phase 7C prepares the bounded runtime authorization for the already merged Phase-7A design and Phase-7B implementation.

It does not execute the frozen population.

## Frozen runtime basis

The future replay is bound to:

- Phase-7B merge commit `6b890245bee10536b8600161ff5f63e7ebd5cdfa`;
- Phase-7 protocol blob `f42fe8c0c58ee3b9152e629f5673bd5c71ffede4`;
- Phase-6C trace-freeze blob `ed0bdcec443b7f0c3ee80d441e1122f32e499d3e`;
- implementation-candidate blob `6fb62e9a6d3187485d4f1591a063dd56f5ed2aa9`;
- primary evaluator blob `09a1c887f8861a6e5dba6059cab2ab906befbbcd`;
- reference evaluator blob `9e13446323be67115950374cb5debfaa7532a17e`;
- population runtime blob `1aefa814d8f619dcd5ac9c0848950965660b5c90`;
- independent full-population validator blob `df9faa48a92d0cccd32d77365a163518f8574d5b`;
- local runtime gate blob `e5b8ead787a1811070a953ff7803c948defea95d`;
- frozen interval CSV SHA-256 `cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`.

## Authorized future runtime scope

Only after a separate author-approved merge places the exact authorization record on clean `main`, the record permits:

- reading the exact frozen interval CSV;
- expanding all 1,919 intervals;
- exactly 18 modeled cases per interval;
- exactly 34,542 recovery-policy cases;
- independent reference recomputation;
- exact case-level comparison with zero accepted mismatches;
- exact matched-comparison validation with zero accepted mismatches;
- two deterministic clean executions.

Actual runtime still requires a separate explicit post-merge author instruction.

## Deterministic output contract

Each authorized run may write only under the ignored local freeze-work tree, using one of:

- `study3x/local_freeze_work/phase7_authorized_run1_001`
- `study3x/local_freeze_work/phase7_authorized_run2_001`

The required canonical outputs are:

1. `S3X_PHASE7_CASE_RESULTS_001.csv`
2. `S3X_PHASE7_MATCHED_COMPARISONS_001.csv`
3. `S3X_PHASE7_SUMMARY_001.json`
4. `S3X_PHASE7_INDEPENDENT_VALIDATION_001.json`
5. `S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json`

All five must be byte-identical across two clean runs before a result-freeze review can begin.

## Still closed

Phase 7C does not authorize:

- result freeze;
- committing canonical real-data outputs;
- manuscript claim use;
- P99_X10 retuning;
- interval-membership retuning;
- Study-3 modification;
- Study-3/S3X pooling.

## Interpretation firewall

The runtime preserves the existing S3X boundaries:

- telemetry inter-sample intervals are timing inputs only;
- they are not RF/contact-loss observations;
- the refresh-opportunity proxy is not operational command availability;
- V4/V5 remain modeled trust states;
- gap duration is not spacecraft recovery latency;
- S3X is not external empirical replication of Study 3.

## Current state

No real frozen interval has been replayed in Phase 7C.

`AUTHOR_REVIEW_AFTER_PHASE7C_RUNTIME_AUTHORIZATION_PR_AND_PREMERGE_CI_BEFORE_MERGE`
