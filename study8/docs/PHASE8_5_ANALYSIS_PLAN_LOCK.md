# Phase 8.5 Statistical Analysis Plan Lock

**Experiment:** `S8-PQC-ICR-001`  
**Authorization:** `S8-ANALYSIS-001`  
**Plan:** `S8-SAP-001`  
**Source evidence commit:** `a31c574e4887e3b92b72dad84933905feb100ef8`  
**Canonical dataset SHA-256:** `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`

## Lock timing

This plan was authored from the frozen Phase-8 protocol, amendment, canonical provenance/audit metadata, and the canonical CSV header only. Canonical outcome values were not inspected before this lock.

## Primary analysis

The primary endpoint is `trusted_recovery_success`. Each recovery policy has 864 equally weighted positions in the complete 3,456-position deterministic factorial population. The primary estimand is the exact marginal success proportion for each policy. The primary contrast is the exact success risk difference `P3_CONTACT_AWARE_STAGED - P1_STAGED_CUTOVER` because P3 adds the frozen deterministic contact-budget guard to staged-cutover semantics.

No sampling p-values, sampling confidence intervals, bootstrap intervals, or permutation tests are authorized. The analysis concerns the complete frozen modeled finite population, not a random sample from a superpopulation.

## Supporting analyses

Supporting policy contrasts include P0-minus-P1, P2-minus-P1, and all six unordered pairwise policy success differences. The P3-minus-P1 contrast is also reported within each contact regime, cryptographic profile, disruption schedule, and recovery deadline. Cryptographic-profile success proportions and ordered within-position success patterns are reported descriptively.

Secondary endpoints are summarized exactly as specified in `PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json`. Logical slots remain logical slots; modeled cryptographic bytes remain standardized-object transfer budgets. No physical latency, RF throughput, onboard compute, energy, flight, ground-station, or operational CCSDS/PQC performance inference is permitted.

## Independence and freeze gates

A primary statistical implementation and a separately written statistical reproducer must produce the same canonicalized findings. The reproducer must not import the primary analysis implementation. Findings may be audited and interpreted under this authorization, but statistical findings freeze, results merge, and publication remain separately prohibited.

**Status:** `PHASE8_5_PLAN_LOCKED_BEFORE_OUTCOME_VALUE_INSPECTION`
