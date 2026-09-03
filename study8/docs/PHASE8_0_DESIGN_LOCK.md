# Phase 8.0 Design Lock

**Study:** `S8-PQC-ICR-001`  
**Base main commit:** `f582c36cc5747a6703ec651bb957bbfea5852a7e`  
**Authorized:** 2026-09-02  
**Status:** `PHASE8_0_DESIGN_LOCKED_RUNTIME_NOT_AUTHORIZED`

## Prerequisite gate

Phase 8.0 was not opened until the redundant Phase-7 post-merge CI gate was confirmed. GitHub Actions run `33690506536` completed successfully on main commit `f582c36cc5747a6703ec651bb957bbfea5852a7e` for the Study-7 canonical-results freeze.

Phase 7 is therefore closed before this Phase-8 branch begins.

## Authorized scope

The authorization covers only:

1. current standards/literature verification;
2. protocol design;
3. finite synthetic logical-time/contact model;
4. NIST-standardized cryptographic-object byte budgets;
5. claim-boundary lock;
6. adversarial review of the design and candidate finite population.

It does **not** authorize implementation, runtime execution, canonical evidence generation, statistical results, manuscript claims, or merging this design into frozen Study-1/Study-2 science.

## Six-file design-lock scope

The initial Phase-8.0 repository change is intentionally limited to:

```text
study8/STUDY8_PROTOCOL.json
study8/STUDY8_LITERATURE_REGISTER.md
study8/STUDY8_CLAIM_BOUNDARY.md
study8/STUDY8_CONTACT_MODEL.md
study8/STUDY8_CRYPTO_OBJECT_BUDGETS.json
study8/docs/PHASE8_0_DESIGN_LOCK.md
```

No implementation file belongs in this gate.

## Frozen finite population

The Phase-8.0 full-factorial design population is:

```text
3 cryptographic profiles
× 4 recovery policies
× 4 contact regimes
× 4 disruption schedules
× 6 compromise phase offsets
× 3 logical deadlines
= 3,456 observations
```

`3,456` is now the **Phase-8.0 frozen design population** after the separate adversarial static review described below. This freezes only the factor lattice, not runtime execution or scientific results.

## Adversarial design review — S8-DESIGN-AR-001

A separate static/adversarial review pass was performed against the committed six-file candidate. This review is independent of runtime because no implementation exists; it is **not represented as an external human review or a separate-laboratory replication**. The later Phase-8 independent implementation/auditor gate remains separate.

Material findings and repairs:

1. **Profile-label ambiguity — repaired.** `Q1/Q3/Q5` could be misread as matched NIST security categories even though ML-KEM-512 and ML-DSA-44 do not share the same category number. Profiles were renamed to exact algorithm-pair identifiers: `PROFILE_512_44`, `PROFILE_768_65`, and `PROFILE_1024_87`.
2. **Deadline-boundary ambiguity — repaired.** On-time recovery now requires `completion_slot < deadline`.
3. **A1 tie ambiguity — repaired.** When multiple objects share the maximum byte size, A1 targets the earliest tied object in the frozen common transmission priority.
4. **Policy determinism / P3 information boundary — repaired.** Acceptance/revocation events, common byte scheduling, and P3-visible/forbidden future information are now explicit.
5. **Terminal-state precedence — repaired.** Failure-state precedence is frozen in `STUDY8_PROTOCOL.json`.

Static review checks:

```text
factor_product_3x4x4x4x6x3=3456                         PASS
all_24_contact_regime_phase_schedules_unique            PASS
all_regimes_complete_cycle_capacity_65536_bytes         PASS
same_required_crypto_object_bundle_all_policies         PASS
FIPS203_object_sizes_match_budget                       PASS
FIPS204_object_sizes_match_budget                       PASS
physical_time_conversion_defined                        NO
runtime_or_implementation_authorized                    NO
```

Review disposition:

```text
S8-DESIGN-AR-001=PASS_AFTER_DESIGN_ONLY_REPAIR
```

The candidate literature gap remains deliberately qualified rather than promoted to an absolute “first” claim.

## Closed gates

```text
runtime_authorized=false
canonical_execution_authorized=false
implementation_creation_authorized=false
results_directory_authorized=false
campaign_authorization_present=false
independent_adversarial_design_review=PASS_SEPARATE_STATIC_REVIEW_TRACK
```

The following paths must not be created under this authorization:

```text
study8/src/
study8/analysis/
study8/results/
study8/runtime/
study8/CAMPAIGN_AUTHORIZATION.json
```

## Phase-8 publication boundary

Phase 8 remains a separate companion-publication line. Studies 1–7 stay frozen and unpooled. The Computers & Security Study-1/Study-2 manuscript record must not be changed by Phase-8 results.

## Advancement criterion

Phase 8.0 is now `DESIGN_LOCKED` after the design-only repairs and repeat static checks. Runtime remains closed. Creating implementation files requires a later, separate authorization/gate, and the later independent implementation/auditor stage is still pending.
