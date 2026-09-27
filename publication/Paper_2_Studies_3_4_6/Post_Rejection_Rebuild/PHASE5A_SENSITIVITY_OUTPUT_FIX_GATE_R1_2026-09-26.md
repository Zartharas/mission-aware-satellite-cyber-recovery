# Paper 2 Phase-5A Sensitivity Output-Fix Gate R1

**Status:** `AUTHORIZED_OUTPUT_SCHEMA_CORRECTION__AWAITING_CI_AND_LOCAL_RERUN`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-phase5a-sensitivity-output-fix`  
**Branch base:** `834b13864b86d474c1f69ae2b6b8800a0bab3250`

## Basis

Phase 5 completed successfully on the author's machine against the frozen ESA-v2 source identity:

- 176 channels analyzed;
- 8 candidate threshold rules;
- 1,408 channel/rule sensitivity rows;
- no gap rule selected;
- no gap rule frozen;
- no timestamp-level gap trace emitted;
- no recovery-policy execution;
- no scientific execution;
- post-run Git working tree clean.

Author-supplied Phase-5 local evidence is bound by:

- `S3X_GAP_SENSITIVITY_001.csv`: `033912eedd7ab1398d07e396c671b95912924f554b35e9eedbc6813eedbc68c5`
- `S3X_DELTA_FREQUENCIES_001.csv`: `1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349`
- `S3X_GAP_SENSITIVITY_SUMMARY_001.json`: `7d752002b4d91f8789d58c97a79dd7e0a9bcda9f296e3d96816d9cf7fc24ee51`
- cadence review: `7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`
- source freeze: `dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27`

## Defect isolated

The R1 sensitivity calculations are not invalidated. The defect is in the exported sensitivity-row field contract.

R1 inserted cadence fields such as `median_seconds`, `p95_seconds`, `p99_seconds`, and `max_seconds`, then expanded the exceedance-distribution dictionary using the same names. Python dictionary expansion therefore replaced the cadence values in the exported CSV row with exceedance values.

Independent review of all 1,408 rows found zero threshold-formula mismatches when R1 thresholds were recomputed from the separately preserved cadence review.

Phase 5A corrects the output representation before any gap-rule decision.

## Authorized correction

The corrected R2 output contract must keep cadence and exceedance metrics distinct.

Cadence fields:

- `cadence_min_seconds`
- `cadence_median_seconds`
- `cadence_mode_seconds`
- `cadence_p95_seconds`
- `cadence_p99_seconds`
- `cadence_max_seconds`
- `cadence_sum_interval_seconds`

Exceedance fields:

- `exceedance_count`
- `exceedance_fraction`
- `exceedance_min_seconds`
- `exceedance_median_seconds`
- `exceedance_p95_seconds`
- `exceedance_p99_seconds`
- `exceedance_max_seconds`
- `sum_interval_seconds_represented_by_exceedances`
- `sum_excess_above_threshold_seconds`

The R2 summary must bind the SHA-256 of both generated CSV files.

The R1 analyzer and runner are preserved separately so the exact historical R1 local-output contract is not silently rewritten.

## R2 local outputs

- `study3x/local_freeze_work/S3X_GAP_SENSITIVITY_002.csv`
- `study3x/local_freeze_work/S3X_DELTA_FREQUENCIES_002.csv`
- `study3x/local_freeze_work/S3X_GAP_SENSITIVITY_SUMMARY_002.json`

## Closed gates

Phase 5A does not authorize:

- selecting or freezing a gap rule;
- emitting timestamp-level gap traces;
- freezing a trace population;
- recovery-policy execution;
- S3X scientific execution;
- changes to frozen Studies 3, 4, or 6;
- manuscript claims based on S3X;
- venue lock or publisher submission.

The next gate is author review of the corrected R2 outputs before any gap-rule selection.
