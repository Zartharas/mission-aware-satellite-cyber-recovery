# Study 8E Current Extension State

**Experiment:** `S8E-ECTV-001`  
**Status:** `CORRECTED_POPULATION_AND_TRACE_FROZEN_ON_BRANCH__IMPLEMENTATION_SYNTHETIC_PASS__REAL_TRACE_EXECUTION_NOT_AUTHORIZED`  
**Date:** 2026-09-20

## Corrected evidence chain

1. `S8E-SATNOGS-POP-001` is preserved as historical evidence but is scientifically invalidated by `S8E-POP001-INVALIDATION-001`.
2. Root cause: the qualification workflow used the stale generated OpenAPI parameter `satellite__norad_cat_id`. SatNOGS Network release 1.134 uses the live `norad_cat_id` observation filter.
3. The corrected filter was verified directly against the live API and release 1.134 source.
4. `S8E-SATNOGS-POP-002` supersedes POP-001:
   - 149 candidates discovered from the prospectively frozen seed windows;
   - 40 candidates evaluated under the corrected pair filter;
   - 20 qualified;
   - 50/50 request ceiling reached;
   - target 32 not reached;
   - the frozen stopping rule requires retaining the observed 20-pair population without retuning.
5. `S8E-SATNOGS-TRACE-002` contains the frozen first-page projection of POP-002:
   - 20 pairs;
   - 476 observations;
   - 20 materialization requests;
   - canonical JSONL SHA-256 `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`;
   - no next cursor was followed.
6. `S8E-IMPLFREEZE-001` is the continuous-time implementation freeze candidate:
   - 10 behavioral unit tests passed;
   - 144 synthetic main-vs-independent comparisons;
   - zero mismatches;
   - real SatNOGS trace not loaded by the implementation-validation workflow.

## Scientific boundary

No Study 8E real-trace timing distribution, gap statistic, burstiness statistic, payload-rate threshold, policy result, profile result, disruption result, or trusted-recovery endpoint has been computed.

The external trace remains evidence input only. Canonical real-trace execution requires a separate prospective execution protocol and explicit author authorization after this remediation/freeze package is merged and post-merge validated.

## Parent-study integrity

Frozen `S8-PQC-ICR-001`, its results and hashes, and `S8-ACTA-PKGFREEZE-002` remain unchanged.

No observation or scientific result from Study 5, Study 7, or Study 9 has been imported into Study 8E.
