# Paper 2 Phase 7A — S3X Recovery-Policy Replay Design

**Protocol:** `S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001`  
**Experiment:** `S3X-ETA-001`  
**Status:** `DESIGN ONLY — NO RECOVERY OR SCIENTIFIC EXECUTION AUTHORIZED`  
**Base main:** `38b45cd5e4674c78b432f24bfff2457affb3cb12`

## Objective

Phase 7A defines how the now-frozen 1,919-member S3X interval population may be used in a bounded external-timing stress test of the frozen Study-3 recovery-policy semantics.

The question is deliberately narrower than “replay Study 3 on real contact data.” ESA supplies only timestamp structure. The extension asks whether the Study-3 distinction between a bounded truthful cache and a false-but-valid producer record remains visible when the hiatus duration is taken from the frozen ESA telemetry interval population.

## Frozen dependencies

The design consumes, without altering:

- `S3X-P99X10-TRACE-POPULATION-FREEZE-001`: 1,919 frozen intervals across 176 channels;
- interval CSV SHA-256 `cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`;
- canonical projection SHA-256 `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`;
- frozen Study-3 experiment `S3-K4E-001`;
- exact Study-3 B0/B2/S1 decision semantics from `study3/src/temporal_model.py`.

Study 3 remains immutable and separate. S3X does not append rows to its 1,380 trajectories.

## Timing abstraction

For each frozen interval (i):

`cadence_unit_seconds_i = cadence_p99_seconds_i`

`g_i = delta_seconds_i / cadence_p99_seconds_i`

Because the frozen rule is strict `delta_seconds > 10 × cadence_p99_seconds`, every selected interval has `g_i > 10`.

The empirical arm interprets only the absence of a source timestamp strictly between the frozen endpoints as a **modeled evidence-refresh hiatus proxy**. It does **not** call that interval RF loss, spacecraft outage, ground-station unavailability, or command-contact loss.

The matched control retains the same interval/channel identity for pairing but supplies an immediate post-onset refresh and no hiatus.

## State transition

Immediately before normalized time `q=0`, the model contains a validly signed `authorization=true` record. Immediately after that record, hidden authorization changes to false and the modeled security signal becomes true.

The parent Study-3 ratio `EVIDENCE_TTL_S / EPOCH_S = 1` is preserved as a one-cadence-unit freshness relation. This is an extension normalization; it does not reinterpret Study-3 logical seconds as ESA/flight seconds.

In the empirical-hiatus arm:

- the pre-onset cache is the only record before resumption;
- no new record arrives for `0 < q < g_i`;
- the first modeled post-onset refresh occurs at `q=g_i`.

In the matched continuous-refresh control, the first post-onset refresh occurs immediately at `q=0`.

## First-refresh evidence states

The first modeled refresh uses the exact Study-3 semantic distinction:

| State | Claim | Signature | Meaning |
|---|---|---|---|
| V0 | authorization=false | valid | truthful post-onset evidence |
| V4 | authorization=true | invalid | post-signature value manipulation |
| V5 | authorization=true | valid | false-but-valid record from a compromised trusted producer |

ESA contains none of these trust labels. They are modeled factors.

### Why persistence is excluded

Phase 7A does **not** cross ONE_SHOT/PERSISTENT. A single frozen interval supplies its bounding timestamps, not a frozen repeated post-hiatus refresh schedule. Treating the first refresh as if it established repeated persistence would add unsupported timing structure.

A later repeated-refresh extension would require a separately designed and frozen schedule population.

## Policies

The three policies remain:

- `S2_B0_FAIL_CLOSED`;
- `S2_B2_RISK_THRESHOLD`;
- `S2_S1_EVIDENCE_AWARE`.

The extension adapter supplies `refresh_opportunity_proxy` to the parent policy argument named `contact`. This preserves the code-level decision semantics while explicitly rejecting the interpretation that the ESA telemetry interval measures physical contact.

Hidden authorization truth is never supplied to the policy.

## Prospective finite case population

Factors:

- 1,919 frozen intervals;
- 3 policies;
- 3 first-refresh evidence states;
- 2 timing arms.

Therefore:

`1,919 × 3 × 3 × 2 = 34,542`

deterministic cases.

This is a complete finite modeled grid over the frozen interval population. It is not a random sample and must not be assigned sampling p-values or confidence intervals.

## Primary endpoints

1. cache-origin unsafe-qualified exposure in cadence units;
2. protective hiatus duration in cadence units;
3. first-refresh selected action;
4. first-refresh gate qualification;
5. first-refresh unsafe-permissive state;
6. first-refresh unsafe-qualified state;
7. first-refresh unsafe-qualification origin;
8. V5-origin first-refresh qualification delay in cadence units.

Raw `delta_seconds`, `cadence_p99_seconds`, and normalized `g_i` are contextual timing variables, not operational recovery latency.

## Prespecified matched comparisons

### Gap versus continuous V5

Match on interval and policy. Report exact agreement/disagreement in first-refresh gate qualification, V5-origin qualification-delay difference where both arms qualify, and cache-origin exposure difference.

### B0 versus S1 cache boundary

Within each frozen interval/evidence state in the empirical arm, report the exact difference in cache-origin unsafe-qualified exposure.

### B0/S1 versus B2 at V5 first refresh

Within each interval and timing arm, report exact first-refresh unsafe-qualified classification by policy. This is a descriptive matched contrast, not a policy ranking.

## Statistical treatment

Allowed: exact counts/proportions, minimum/median/maximum, finite-population means where explicitly defined, and deterministic matched differences.

Prohibited: p-values, confidence intervals, bootstrapping, permutation tests, outcome-dependent exclusions, post-hoc subgroup creation, weighted global scores, global policy rankings, and pooling with Study 3.

## Reproducibility design

Before any scientific execution, a later implementation phase must provide:

1. a primary implementation;
2. a separately implemented reference validator;
3. exact case-level comparison with zero accepted mismatches;
4. two clean deterministic executions;
5. byte-identical SHA-256 values for all canonical scientific outputs;
6. fail-closed verification of the frozen interval CSV SHA-256;
7. local/ignored outputs until a separate result-freeze gate.

Planned outputs are:

- `S3X_PHASE7_CASE_RESULTS_001.csv`
- `S3X_PHASE7_MATCHED_COMPARISONS_001.csv`
- `S3X_PHASE7_SUMMARY_001.json`
- `S3X_PHASE7_INDEPENDENT_VALIDATION_001.json`
- `S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json`

## Claim firewall

The eventual extension may describe behavior under this frozen timing abstraction only.

It must not claim:

- the ESA gap is RF or command-contact loss;
- the ESA anomaly labels are cyberattacks;
- V4/V5 were observed in the ESA data;
- observed gap duration is spacecraft recovery latency;
- cadence units are operational latency;
- the 1,919 intervals are representative of all spacecraft or all ESA telemetry;
- S3X is external empirical replication of Study 3;
- S3X and Study 3 form one pooled population.

## Current authorization

Authorized in Phase 7A:

- protocol design;
- exact semantic bindings;
- analysis/endpoints/matched-comparison design;
- fail-closed audit and unit tests;
- draft PR and pre-merge CI.

Not authorized:

- implementation of the scientific runner;
- recovery-policy execution;
- scientific endpoint generation;
- manuscript claim use;
- P99_X10 or interval-membership retuning;
- modification of frozen Study 3.

## Next gate

`AUTHOR_REVIEW_AFTER_PHASE7A_DESIGN_PR_AND_PREMERGE_CI_BEFORE_MERGE`
