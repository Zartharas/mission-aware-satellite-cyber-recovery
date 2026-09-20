# Study 8E: External Observation-Opportunity Timing Extension

**Experiment:** `S8E-ECTV-001`  
**Current status:** `CORRECTED_CANONICAL_RESULTS_AUDITED__FORMAL_RESULT_FREEZE_PENDING`  
**Current authority:** `study8e/CURRENT_EXTENSION_STATE.md`

Study 8E is a separate extension of frozen Study 8. It evaluates the frozen cryptographic transition semantics against a prospectively governed public SatNOGS observation-opportunity timing population without modifying the original deterministic Study 8 population or the rejected Acta package.

## Current authoritative artifacts

- corrected population: `S8E-SATNOGS-POP-002`
- corrected trace: `S8E-SATNOGS-TRACE-002`
- extension implementation: `S8E-IMPLFREEZE-001`
- canonical protocol: `S8E-CANON-EXEC-001`
- corrected canonical runner: `S8E-CANON-RUNNER-004`
- invalidated first canonical results: `S8E-CANON-RESULTS-001-INVALIDATION`
- corrected execution closeout: `S8E-CANON-GOLIVE-002-CLOSEOUT`
- corrected result audit: `S8E-CANON-RESULTS-002-AUDIT-001`
- new-chat handoff: `study8e/NEW_CHAT_HANDOFF_20260920.md`

## Corrected evidence population

`S8E-SATNOGS-POP-002` contains 20 deterministic rate-bounded satellite-station trace pairs selected under the frozen seed-window, threshold, SHA-256 ranking, entity-cap, and 50-request stopping rules.

`S8E-SATNOGS-TRACE-002` contains 476 frozen first-page observation rows.

Canonical trace JSONL SHA-256:

`6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`

SatNOGS timing is treated only as an observation-opportunity timing proxy. It is not treated as authenticated/bidirectional command availability or measured link throughput.

## Corrected canonical execution

Corrected workflow run:

`35536583594`

Corrected result artifact:

- artifact ID: `10613372166`
- artifact: `study8e-canonical-results-002`
- ZIP SHA-256: `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`

The run passed:

- 10/10 canonical runner tests;
- two deterministic executions;
- byte-identical scientific-output comparison;
- independent case audit with zero mismatches;
- repository drift check.

Key corrected counts:

- traces: 20
- eligible anchors: 454
- canonical cases: 65,376
- finite minimum-rate thresholds: 17,640
- non-finite cases: 47,736
- profile-ordering violations: 0

Detailed findings and hashes are in:

`study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`

## Historical invalidated result

The first canonical result package from workflow run `35529423881` is invalidated.

The strict-before-horizon upper-bound defect was:

- old: `ceil(8B/d_min)`
- corrected: `floor(8B/d_min)+1`

The defect affected 24 exact-divisibility A1/12-hour cases and created four spurious profile-ordering violations.

Never use the first canonical result package for scientific claims.

## Current gate

Corrected results are audited but **not yet formally frozen**.

Do not:

- treat results 002 as manuscript-integrated final science until formal result freeze is approved;
- rerun TRACE-002 merely to clean metadata;
- rewrite the immutable Actions artifact;
- change POP-002 or TRACE-002;
- modify frozen Study 8;
- submit a publisher package.

The next controlled decision is formal corrected-result freeze, followed by Study 8 / Study 8E manuscript architecture and venue strategy.
