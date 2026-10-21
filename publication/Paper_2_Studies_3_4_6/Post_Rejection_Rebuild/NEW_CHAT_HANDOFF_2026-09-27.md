# Paper 2 New-Chat Handoff — 2026-09-27 — Phase 7D Closeout

## Authority

This file is the current repository handoff for continuing the Paper-2 post-rejection rebuild in a new ChatGPT session.

Repository:

`Zartharas/mission-aware-satellite-cyber-recovery`

Authoritative `main` at this handoff:

`c3fae865dc3f19871a5a58ffac1bebdfe55fa223`

Phase-7D post-merge validation:

- PR: `#192`
- accepted pre-merge head: `164b4f6f8af1d1458c64a7bcf50734d901b0042f`
- pre-merge CI: run `#1261`, run id `36373674725`, success
- merge commit: `c3fae865dc3f19871a5a58ffac1bebdfe55fa223`
- post-merge CI: run `#1262`, run id `36374775344`, success

Always verify live GitHub `main` and current open PRs before acting because other study streams may advance the repository.

## Paper 2 identity and publication boundary

Title:

**Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance**

Aman Kumar Singh is the sole independent author/corresponding author.

The rejected TAES R10 submission is immutable historical provenance:

- manuscript id: `TAES-2026-4182`
- decision: `EDITORIAL_PRESCREEN_REJECTION`
- external peer review: NO

No R11/R12 manuscript rewrite is currently authorized.

Paper 2 remains scientifically limited to frozen Studies 3, 4, and 6 plus separately governed extension work. Do not import Study 5 or Studies 1/2/7/7E/8/8E/9 as Paper-2 evidence and do not pool populations.

## Frozen original studies

- Study 3 `S3-K4E-001`: 1,380 trajectories / 67,620 epochs
- Study 4 `S4-MPQ-001`: 4,608 observations / 18 vote-provenance rules
- Study 6 `S6-SCTR-001`: 420 observations

Do not modify, rerun, enlarge, or replace these frozen studies.

## Core rebuild principle

> A recovery decision cannot infer a trust property that is absent from the evidence it can observe.

Working central RQ:

> Which trust failures remain invisible to a satellite cyber-recovery decision when it relies on fresh evidence, multiple trusted producers, and an approved recovery artifact?

## S3X identity and source freeze

Extension:

`S3X-ETA-001`

Public source:

ESA Anomaly Dataset v2

Source freeze:

`S3X-ESA-V2-SOURCE-FREEZE-001`

Mission archive SHA-256:

- Mission 1: `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72`
- Mission 2: `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5`

Source-freeze SHA-256:

`dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27`

Channels:

- Mission 1: 76
- Mission 2: 100
- total: 176

Interpretation firewall: telemetry gaps remain only extreme telemetry inter-sample intervals unless separately supported. Never relabel them as RF contact loss, ground-station visibility loss, spacecraft outage, cyberattack truth, onboard recovery latency, or operational command unavailability.

## Frozen Phase-5C gap rule

Freeze id:

`S3X-P99X10-GAP-RULE-FREEZE-001`

Rule:

`P99_X10`

Generation contract:

`threshold_seconds = channel-specific cadence_p99_seconds * 10.0`

Membership:

`positive inter-sample delta > threshold_seconds`

The comparison is strict `>`. Equality is not an exceedance.

Selection characterization:

`DATA_INFORMED_SELECTION_FROM_PRESPECIFIED_PHASE5_CANDIDATE_FAMILY`

P99_X10 was selected after the prespecified eight-rule sensitivity analysis; do not describe it as prospectively fixed before inspection.

Retuning is prohibited.

## Phase 6 frozen trace population

The Phase-6/6C pipeline extracted, independently validated, repeated, and froze the P99_X10 timestamp population.

Frozen interval artifact:

`S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv`

SHA-256:

`cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`

Invariants:

- channels: 176
- frozen intervals: 1,919
- channels with intervals: 171
- zero-interval channels: 5

Canonical channel projection SHA-256:

`f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`

Zero-interval channels:

- `ESA-Mission2/channel_66.zip`
- `ESA-Mission2/channel_67.zip`
- `ESA-Mission2/channel_68.zip`
- `ESA-Mission2/channel_69.zip`
- `ESA-Mission2/channel_100.zip`

Trace-population freeze is effective. Interval-membership retuning is prohibited.

## Phase 7A design

Protocol:

`S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001`

Prospective deterministic grid:

`1,919 intervals × 3 policies × 3 evidence states × 2 timing arms = 34,542 cases`

Policies:

- `S2_B0_FAIL_CLOSED`
- `S2_B2_RISK_THRESHOLD`
- `S2_S1_EVIDENCE_AWARE`

Evidence states:

- V0 = truthful post-onset evidence
- V4 = post-signature value manipulation / invalid signature
- V5 = false-but-valid trusted-producer evidence

Timing arms:

- `EMPIRICAL_HIATUS_PROXY`
- `MATCHED_CONTINUOUS_REFRESH_CONTROL`

The ONE_SHOT/PERSISTENT dimension is deliberately excluded because a single frozen interval does not establish a repeated post-hiatus refresh schedule.

Expected matched-comparison rows:

`30,704`

Sampling p-values, confidence intervals, bootstrap/permutation inference, global policy scores/rankings, post-hoc exclusions, and pooling with Study 3 are prohibited.

## Phase 7B / 7C historical v1 implementation

Historical implementation candidate:

`S3X-PHASE7-IMPLEMENTATION-CANDIDATE-001`

Historical runtime authorization:

`S3X-PHASE7-RUNTIME-AUTH-001`

Pre-runtime synthetic parity:

- synthetic fixture intervals: 3
- synthetic primary/reference cases: 54
- mismatches: 0

The v1 authorization became effective after PR #191 / CI #1259.

### First real v1 execution attempt

The user authorized the first real replay.

Preflight passed:

- authorized main verified
- frozen CSV SHA verified as `cfa4fa3d...`
- bound code identity PASS
- output directories initially unused

Run 1 then stopped in interval parsing with:

`ValueError: frozen P99_X10 threshold relationship is inconsistent`

The failure occurred **before case generation**:

- scientific case rows generated: 0
- independent full-population validation started: NO
- result freeze changed: NO
- manuscript claim use changed: NO

The input was not invalidated.

## Phase 7D root cause

Phase 6 computed threshold with Python binary floating-point and serialized cadence and threshold independently.

The frozen numerical relation is therefore:

`float(threshold_seconds) == float(cadence_p99_seconds) * 10.0`

and membership is:

`float(delta_seconds) > float(threshold_seconds)`

Candidate 001 incorrectly re-parsed independent CSV strings as exact decimals and required:

`Decimal(threshold) == Decimal(cadence) * 10`

which is stronger than the Phase-6 contract.

Example edge:

- cadence string `0.07`
- Phase-6 threshold string `0.7000000000000001`
- float relation is true
- exact-decimal relation is false

Classification:

`IMPLEMENTATION_VALIDATION_CONTRACT_MISMATCH__NOT_DATA_OR_RULE_FAILURE`

No epsilon or tolerance was introduced in the correction.

## Corrected Phase-7D v2 stack

Corrected implementation candidate:

`S3X-PHASE7-IMPLEMENTATION-CANDIDATE-002`

Blob:

`d7ee15c6a2bfe818ee016eadba0893ef74aa8f18`

Corrected runtime authorization:

`S3X-PHASE7-RUNTIME-AUTH-002`

Blob:

`bb7978052cf03bdfaa628a44d7d268d73e9c005a`

Corrected code identities:

- primary v2: `40e3bd0406f1f0bedecbac9cb1386699a8619318`
- reference v2: `26444d206f18bededa656b1de56d9ba0948c6ef3`
- runtime v2: `f2a789edd24a0e23ff0d256312fc7d2b7e656573`
- full-population validator v2: `15796f7b8e2da3f92e941021839b387ad365394e`
- local gate v2: `95cb497cd0465a34e1e8e17609c4e5f781ba8aaf`

Corrected numerical contract:

- threshold/membership validation: Phase-6 binary-float semantics
- normalized hiatus analysis: exact rational arithmetic over canonical CSV decimal tokens
- tolerance added: NO
- epsilon added: NO
- P99_X10 retuned: NO
- interval membership changed: NO
- frozen input changed: NO

PR #192 merged this corrected stack and post-merge CI #1262 succeeded.

The historical JSON records retain creation-state strings such as `PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE`. Do not rewrite them. Their effectivity conditions are now satisfied by the separately authorized merge to `main` and successful post-merge CI. The post-merge closeout record is the authority for current effectivity.

## Current formal state

```text
PHASE7D_CORRECTION_MERGED
POST_MERGE_CI_1262_SUCCESS
CORRECTED_RUNTIME_AUTHORIZATION_002_EFFECTIVE

FROZEN_INTERVALS = 1919
AUTHORIZED_CASES = 34542
MATCHED_COMPARISON_ROWS = 30704
REQUIRED_DETERMINISTIC_RUNS = 2
CASE_MISMATCH_TOLERANCE = 0
MATCHED_COMPARISON_MISMATCH_TOLERANCE = 0

CORRECTED_REAL_REPLAY_PERFORMED = NO
CORRECTED_SCIENTIFIC_RESULTS_GENERATED = NO
INDEPENDENT_FULL_POPULATION_VALIDATION_PERFORMED = NO
DETERMINISTIC_REPEATABILITY_VERIFIED = NO

RESULT_FREEZE = NOT AUTHORIZED
CANONICAL_RESULT_COMMIT = NOT AUTHORIZED
MANUSCRIPT_CLAIM_USE = NOT AUTHORIZED

P99_X10_RETUNING = PROHIBITED
INTERVAL_MEMBERSHIP_RETUNING = PROHIBITED
STUDY3_MODIFICATION = PROHIBITED
STUDY3_S3X_POOLING = PROHIBITED
```

## Local runtime path

Expected local repository:

`/Users/zarthras/Documents/Development Projects/Satellite-Cybersecurity-Research/mission-aware-satellite-cyber-recovery`

Frozen input path:

`study3x/local_freeze_work/phase6_run1/S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv`

Corrected runner:

`study3x/validation/run_local_phase7_replay_v2.sh`

Authorization record:

`study3x/config/S3X_PHASE7_RUNTIME_AUTH_002.json`

Canonical outputs:

- `study3x/local_freeze_work/phase7_authorized_run1_001`
- `study3x/local_freeze_work/phase7_authorized_run2_001`

The failed v1 attempt may have created `phase7_authorized_run1_001` as an **empty directory** before parsing stopped. An empty directory is not a scientific result. Do not delete or overwrite any non-empty output directory; inspect first and fail closed if files are present.

## Next controlled gate

`AUTHOR_APPROVAL_BEFORE_PHASE7D_CORRECTED_REAL_REPLAY`

A new chat must **not** assume that the earlier v1 execution authorization automatically authorizes v2 execution.

After explicit new authorization, the corrected execution should:

1. verify live `main` and successful latest CI;
2. fast-forward local `main` only if origin/main remains the authorized state or a later verified documentation-only handoff commit;
3. verify the frozen interval CSV SHA exactly;
4. verify `AUTH-002` and corrected v2 code identities;
5. verify both canonical output directories are absent or empty;
6. execute corrected Run 1;
7. independently recompute and require 34,542 cases, 30,704 comparisons, and zero mismatches;
8. execute corrected Run 2;
9. independently validate Run 2;
10. require byte-identical SHA-256 for all five canonical outputs across both runs;
11. verify tracked repository drift remains zero;
12. stop before result freeze, committing outputs, or manuscript interpretation.

## New-chat operating instructions

At the beginning of the next chat:

1. use the live GitHub repository as authority;
2. verify current `main`, open PRs, and latest successful CI;
3. read this handoff and `PAPER2_PHASE7D_POST_MERGE_CLOSEOUT_STATUS.json`;
4. read `S3X_PHASE7_RUNTIME_AUTH_002.json` and the Phase-7D correction record;
5. preserve all frozen Studies 3/4/6 and S3X source/trace identities;
6. do not alter P99_X10 or interval membership;
7. do not rerun v1;
8. do not execute v2 until the author explicitly authorizes the corrected real replay;
9. after successful corrected two-run replay, stop before result freeze and manuscript interpretation for another author gate.

## Copy-paste continuation prompt

> Continue Paper 2 from the authoritative private GitHub repository `https://github.com/Zartharas/mission-aware-satellite-cyber-recovery`. Use live `main` as authority and verify it before any work. The Phase-7D float-contract correction was merged through PR #192; its merge commit was `c3fae865dc3f19871a5a58ffac1bebdfe55fa223` and post-merge CI #1262 / run id `36374775344` succeeded. Read `publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/NEW_CHAT_HANDOFF_2026-09-27.md`, `PAPER2_PHASE7D_POST_MERGE_CLOSEOUT_STATUS.json`, `PAPER2_PHASE7D_FLOAT_CONTRACT_CORRECTION_STATUS.json`, `study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json`, and `study3x/config/S3X_PHASE7_RUNTIME_AUTH_002.json` before acting.
>
> The v1 real replay stopped before case generation because Candidate 001 imposed decimal-exact threshold multiplication that was stricter than the frozen Phase-6 binary-float serialization contract. The frozen interval CSV SHA remained exact at `cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`; zero scientific case rows were generated. Do not rerun v1.
>
> The corrected v2 contract is `float(threshold_seconds) == float(cadence_p99_seconds) * 10.0` with strict `float(delta_seconds) > float(threshold_seconds)`; normalized hiatus analysis remains exact rational arithmetic over canonical decimal tokens. No epsilon/tolerance, P99_X10 retuning, interval reselection, or frozen-input change occurred.
>
> Corrected runtime authority is `S3X-PHASE7-RUNTIME-AUTH-002`. The v2 stack is present on main. The next gate is `AUTHOR_APPROVAL_BEFORE_PHASE7D_CORRECTED_REAL_REPLAY`. Do not execute the corrected replay unless I explicitly authorize it in the new chat. If I authorize it, use `study3x/validation/run_local_phase7_replay_v2.sh`, run exactly the frozen 1,919 intervals into 34,542 cases and 30,704 matched-comparison rows twice, require zero primary/reference mismatches and byte-identical hashes for all five canonical outputs, and then stop before result freeze, canonical result commit, or manuscript interpretation.
>
> Paper 2 remains limited to frozen Studies 3, 4, and 6 plus the separately governed S3X extension. Do not import or pool Studies 1/2/5/7/7E/8/8E/9. Keep all interpretation-firewall restrictions in force.
