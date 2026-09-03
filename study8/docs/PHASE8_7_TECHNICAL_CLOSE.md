# Phase 8.7 — Study 8 Technical Close

**Experiment:** `S8-PQC-ICR-001`  
**Technical close date:** 2026-09-03  
**Final science PR:** `#89`  
**Final validated PR head:** `1356b73d1edc01c8618c9290460f4fbf22c458df`  
**Science merge commit on `main`:** `63106778559c3127a7d6e8765d52939b73a3f35b`  
**Post-merge validation run:** `33761681328` — `SUCCESS`

## Disposition

Study 8 is technically closed. Design, implementation, canonical execution, independent implementation-level reproduction, prespecified statistical analysis, independent statistical reproduction, interpretation audit, SHA-256 results freeze, merge, and post-merge repository validation are complete.

This close does **not** authorize publication, manuscript integration, new canonical execution, or statistical re-execution.

## Frozen lineage

The final scientific lineage is:

```text
Phase 8.0 design lock
  -> design amendment S8-DESIGN-AMEND-001
  -> Phase 8.1 implementation + independent auditor freeze
  -> Phase 8.2 pre-runtime validation/hash binding
  -> Phase 8.3 pre-runtime merge/post-merge CI
  -> Phase 8.4 one-time canonical campaign
  -> 3,456 primary observations
  -> 3,456 independent recomputations
  -> 0 row mismatches
  -> Phase 8.5 prespecified statistical analysis
  -> independent statistical reproduction
  -> interpretation audit
  -> Phase 8.6 SHA-256 statistical-results freeze
  -> Phase 8.7 exact-head review/merge
  -> post-merge main CI SUCCESS
```

## Canonical evidence

The canonical factorial population contains exactly **3,456 observations**. The independent reference implementation recomputed all 3,456 factor positions and matched all canonical rows exactly.

```text
expected population        3,456
primary observations       3,456
independent observations   3,456
exact row matches          3,456
mismatches                 0
```

Canonical dataset SHA-256:

```text
cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf
```

## Statistical freeze

Primary and independent findings are byte-identical:

```text
26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e
```

Interpretation-audit SHA-256:

```text
620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413
```

The controlling hash-freeze authorities are:

- `study8/analysis/RESULTS_FREEZE_MANIFEST.json`
- `study8/analysis/RESULTS_FREEZE_SHA256SUMS.txt`

The Phase-8.6 freeze manifest intentionally records `results_merge_authorized=false` because it is the immutable pre-merge freeze artifact. The later user authorization to merge is preserved in PR `#89`, its Phase-8.7 review record, and merge commit `63106778559c3127a7d6e8765d52939b73a3f35b`. The frozen Phase-8.6 evidence is not rewritten after merge.

## Frozen primary finding

All four policies have the same trusted-recovery success result:

```text
P0_HARD_CUTOVER          635 / 864
P1_STAGED_CUTOVER        635 / 864
P2_HYBRID_OVERLAP        635 / 864
P3_CONTACT_AWARE_STAGED  635 / 864
```

The prespecified primary risk-difference contrast is:

```text
P3 - P1 = 0/1 = 0.000000 percentage points
```

This is a negative primary policy result. No hypothesis rescue, policy-success superiority claim, or post-hoc significance claim is supported.

The frozen profile result is:

```text
PROFILE_512_44   1080 / 1152
PROFILE_768_65    748 / 1152
PROFILE_1024_87   712 / 1152
```

Across all 1,152 matched positions formed by holding non-profile factors fixed, trusted-recovery success is non-increasing as the modeled standardized cryptographic-object byte budget increases.

## Inference boundary

The 3,456 observations constitute the complete deterministic finite factorial population defined by the frozen protocol. They are not treated as a probabilistic sample. The prespecified analysis therefore does not use sampling p-values, sampling confidence intervals, bootstrap inference, or permutation inference.

## Claim boundary

Study 8 supports claims only about the frozen deterministic model:

- logical contact-slot opportunity;
- modeled byte-capacity availability;
- standardized cryptographic-object byte burden;
- frozen transition-policy state semantics;
- bounded modeled disruption;
- logical recovery/exposure/unavailability/overlap endpoints.

Study 8 does **not** establish measured performance for:

- operational spacecraft;
- flight hardware;
- RF links;
- real orbit/contact timing;
- ground stations or operators;
- onboard ML-KEM/ML-DSA CPU time or energy;
- operational CCSDS/PQC deployments;
- flightworthiness, certification, or production suitability.

NIST-standardized ML-KEM/ML-DSA object sizes are used as standardized cryptographic-object sizes in the model. They are not represented as empirical space-system performance measurements.

## Validation closeout

Before merge, the exact final PR head passed:

- `Validate Study 8 results freeze` — run `33760360044` — `SUCCESS`
- lifecycle-aware `Validate Study 8 pre-runtime` — run `33760360089` — `SUCCESS`
- `Validate research configurations` — run `33760360043` — `SUCCESS`

After merge, `main` commit `63106778559c3127a7d6e8765d52939b73a3f35b` passed:

- `Validate research configurations` — run `33761681328` — attempt `1` — `SUCCESS`

The post-merge run passed repository release/bibliography checks, JSON/Python/schema validation, research unit tests, shell syntax validation, frozen WP10 reproduction/regression, and final no-tracked-file-drift verification.

## Publication relationship

Study 8 is a **separate companion-paper research stream**. The existing `publication/` directory currently represents the earlier Study-1/Study-2 journal article and must not silently absorb Study-8 material.

A future publication gate may create a dedicated Study-8 manuscript package and publication displays from the frozen records. That work may summarize or visualize the frozen evidence but must not modify the canonical dataset, rerun the campaign to improve results, replace the negative primary finding, introduce unsupported sampling inference, or expand the operational claim boundary.

## Current authority

Use these records together for current Study-8 state:

1. `study8/STUDY8_TECHNICAL_CLOSE.json`
2. `study8/analysis/RESULTS_FREEZE_MANIFEST.json`
3. `study8/analysis/RESULTS_FREEZE_SHA256SUMS.txt`
4. `study8/results/S8-PQC-ICR-001/independent_audit_summary.json`
5. `study8/analysis/results/primary_findings.json`
6. `study8/analysis/results/interpretation_audit.json`
7. PR `#89` and merge commit `63106778559c3127a7d6e8765d52939b73a3f35b`

Historical Phase-8 documents retain stage-local authorization wording as provenance and must not be interpreted as superseding this later technical close.
