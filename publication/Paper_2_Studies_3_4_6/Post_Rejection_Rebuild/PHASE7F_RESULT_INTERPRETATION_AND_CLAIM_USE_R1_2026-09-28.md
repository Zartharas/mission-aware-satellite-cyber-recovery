# Paper 2 Phase 7F — Frozen-Result Interpretation and Manuscript Claim-Use Review

**Experiment:** `S3X-ETA-001`  
**Frozen result identity:** `S3X-PHASE7-RESULT-FREEZE-001`  
**Effective freeze main:** `74c124290fce0f46f1687f277edeff28d4d82dc1`  
**Post-merge CI:** #1266 / run `36431944810` — SUCCESS  
**Status:** interpretation and rebuild claim-use package prepared; merge still requires separate author review.

## 1. Interpretation boundary

Phase 7F does not rerun, retune, or modify S3X. It interprets only the already-frozen Phase-7 finite population.

The five canonical result files remain local/ignored. This phase therefore authorizes only claims that are exact consequences of the frozen factor grid and bound policy truth table and that are supported by the completed 34,542-case execution with zero case-level and matched-comparison mismatches.

No minimum, median, maximum, mean, percentile, or mission-specific Phase-7 outcome is introduced without direct inspection of the hash-verified frozen result bytes.

## 2. RQ1 answer supported by Phase 7

The rebuild asks:

> How does intermittent evidence availability affect exposure to false but validly signed recovery evidence?

The S3X answer is bounded but clear:

**Under the frozen external timing abstraction, a telemetry-derived evidence-refresh hiatus changes when the modeled trust failure can surface and creates a one-cadence B0 truthful-cache boundary, but it does not change the first-refresh V5 qualification classification. Once false-but-valid trusted-producer evidence arrives, B0 and S1 qualify it for every frozen interval in both timing arms; B2 does not under the frozen post-onset signal.**

Thus the timing structure can delay manifestation of producer-origin semantic falsity, but timing alone does not make a validly signed false claim observable as false.

## 3. Exact structural findings

### F1 — Pre-refresh cache boundary

Every frozen P99_X10 member has normalized hiatus `g_i > 10`.

During the empirical hiatus, B0 admits the still-fresh truthful pre-onset cache for exactly one cadence unit. Under the same post-onset signal and no refresh opportunity, S1 and B2 select protective actions instead.

Across the 1,919 intervals and three first-refresh evidence states, the prespecified B0-versus-S1 cache comparison contains:

`1,919 × 3 = 5,757`

rows, each with a B0-minus-S1 cache-origin unsafe-qualified exposure difference of exactly **+1 cadence unit**.

This is not an estimate of real spacecraft cache staleness.

### F2 — V4 remains an integrity-detectable failure

At first refresh, V4 carries `authorization=true` with an invalid signature. Because signature validity is required for evidence qualification, the V4 record cannot qualify the recovery gate.

This structural result applies to:

`1,919 × 3 policies × 2 timing arms = 11,514`

V4 cases.

The claim is limited to modeled post-signature alteration. It is not evidence about cryptanalysis or key compromise.

### F3 — V5 remains a semantic trust failure

At first refresh, V5 carries `authorization=true` with a valid signature even though modeled hidden authorization is false.

For the frozen post-onset signal:

- B0 selects `PROCEED_TO_RECOVERY_GATE`;
- S1 selects `PROCEED_TO_RECOVERY_GATE` because the refresh opportunity is present;
- B2 selects `RESTRICT_AND_REQUEST_AUTHORIZATION`.

Therefore B0 and S1 are unsafe-qualified in:

`1,919 × 2 policies × 2 timing arms = 7,676`

V5 cases combined.

B2 is non-qualifying in:

`1,919 × 1 policy × 2 timing arms = 3,838`

V5 cases.

The B2 structural zero is not a global policy ranking or an operational recommendation.

### F4 — The hiatus shifts time, not first-refresh classification

For each interval-policy V5 pair, gap and continuous arms have the same first-refresh gate classification:

- B0: qualified / qualified;
- S1: qualified / qualified;
- B2: non-qualifying / non-qualifying.

This yields:

`1,919 × 3 policies = 5,757`

agreement comparisons for the prespecified V5 first-refresh gate metric.

The difference is timing. The continuous control refreshes at `q=0`; the empirical-hiatus arm refreshes at `q=g_i`, and every frozen `g_i > 10`.

For B0 and S1, V5-origin qualification is therefore delayed to `g_i` in the hiatus arm rather than eliminated.

## 4. Relationship to frozen Study 3

S3X does not append observations to Study 3 and does not reproduce Study 3 externally.

Its manuscript value is narrower: an independently sourced telemetry timing population is used only to stress the timing dimension of the already-frozen Study-3 decision semantics.

The qualitative Study-3 distinction survives that stress test:

1. a truthful cache can create a bounded freshness-origin boundary;
2. invalidly signed V4 manipulation is rejected;
3. false-but-valid V5 evidence remains inside the modeled trust boundary when the signer itself is compromised.

The extension strengthens the manuscript's observability argument without changing the Study-3 population or claiming real operational contact behavior.

## 5. Claims withheld from the manuscript at this stage

Phase 7F does not introduce:

- minimum/median/maximum/mean/percentile hiatus or V5-delay values;
- mission-specific Phase-7 outcome summaries;
- RF/contact/outage claims;
- cyberattack labels for ESA events;
- operational recovery-latency claims;
- external empirical replication language;
- global policy ranking;
- pooled Study-3/S3X statistics.

Those claims require either different evidence or, for allowed descriptive output summaries, direct inspection of the already-frozen hash-verified canonical artifacts.

## 6. Manuscript-use decision

The exact structural claims F1–F4 and the bounded RQ1 synthesis are eligible for the **post-rejection rebuild** after this governance record is separately reviewed, merged, and validated on `main`.

The historical submitted TAES R10 package remains immutable.

## Next gate

`AUTHOR_REVIEW_AFTER_PHASE7F_INTERPRETATION_CLAIM_USE_PR_AND_PREMERGE_CI_BEFORE_MERGE`
