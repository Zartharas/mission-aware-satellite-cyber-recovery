# Paper 2 Rebuild — Phase 7F Manuscript-Ready Inserts

These are manuscript-ready candidate passages for the **post-rejection rebuild only**. They do not modify the historical TAES R10 submission.

## RQ1 result paragraph

To test whether the Study-3 temporal trust boundary persisted under externally sourced timing structure, S3X applied the frozen B0/B2/S1 decision semantics to 1,919 P99_X10-positive ESA telemetry inter-sample intervals, used only as cadence-normalized evidence-refresh-hiatus proxies. The resulting 34,542-case deterministic grid reproduced against a separately implemented reference evaluator with zero case-level mismatches. In the empirical-hiatus arm, B0 admitted the truthful pre-onset cache for one cadence unit before expiry, whereas S1 and B2 did not admit that cache to the recovery gate under the same post-onset signal. Across the 5,757 prespecified B0-versus-S1 cache comparisons, this produced a fixed one-cadence-unit boundary.

At the first modeled refresh, V4 post-signature manipulation remained non-qualifying because the affected signature was invalid. False-but-valid V5 evidence produced a different boundary: B0 and S1 were unsafe-qualified in all 7,676 corresponding interval-arm cases, while B2 remained non-qualifying in all 3,838 V5 cases. Gap versus continuous timing did not change those first-refresh classifications. Instead, it shifted the B0/S1 V5 qualification time from `q=0` in the matched continuous-refresh control to `q=g_i` in the hiatus arm, where every frozen `g_i` was strictly greater than 10 cadence units. The externally sourced timing structure therefore delayed the modeled manifestation of false-but-valid producer evidence without repairing the underlying producer-origin trust failure.

## Cross-study synthesis insertion

S3X adds a timing stress test to the Study-3 interpretation without pooling populations. Its result sharpens the observability principle: absence of a refresh opportunity can postpone when a false-but-valid trusted-producer record reaches the gate, but timing does not reveal semantic falsity that remains hidden behind a valid signature. The extension therefore corroborates the qualitative distinction between freshness-origin exposure and producer-origin false evidence under a separate finite timing population, rather than providing an external empirical replication of Study 3.

## Contribution statement candidate

A frozen external-timing stress test over 1,919 telemetry inter-sample intervals shows that evidence-refresh hiatus can delay, but does not remove, the first-refresh false-but-valid trusted-producer boundary for B0/S1 under the modeled recovery semantics.

## Validity paragraph

S3X uses ESA telemetry inter-sample spacing only as a cadence-normalized evidence-refresh-hiatus proxy. It does not identify RF contact loss, command-link unavailability, ground-station visibility loss, spacecraft outage, cyberattack truth, or operational recovery latency. V4 and V5 are modeled trust states rather than ESA labels, and S3X remains separate from the 1,380-trajectory Study-3 population. The extension is therefore an external-timing stress test of frozen decision semantics, not an external empirical replication of Study 3.

## Claims intentionally excluded pending direct frozen-output inspection

Do not add Phase-7 minimum, median, maximum, mean, percentile, mission-specific, or other distributional summaries unless the corresponding canonical artifact is directly inspected and its SHA-256 matches the effective result-freeze record.
