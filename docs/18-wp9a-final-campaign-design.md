# WP9-A Final Campaign Matrix and Analysis Contract

**Decision:** R-044  
**Status:** Matrix and endpoint/model rules frozen; runtime validation required before repetition-count freeze or campaign execution.  
**Campaign execution authorized:** No.

## Purpose

WP9-A converts the audited WP8 pilot into a minimal, identifiable final-campaign design. It freezes the cells and analysis applicability rules needed to test P1-P5 without running a broad full factorial.

The design is estimand-driven:

- use complete low-dimensional factorial blocks where a predeclared interaction must be estimated;
- reuse cells across propositions when factor identities are exactly compatible;
- keep matched fixed-policy versus P7 comparisons for condition-specific trade-off analysis;
- retain one untreated sentinel for E2 and E4 so those event families have same-campaign absolute reference behavior;
- omit combinations that do not identify a predeclared proposition or event-generalization claim.

This yields **24 final-campaign cells**, not a full factor cross-product.

## Reviewer challenge that changed the design

The original P2 proposition requires a comparison between a ground-dependent policy and an autonomous policy under contact delay. The implemented experiment model contains P0/P1/P2/P4/P5/P7 but does not contain P6, even though the initial experiment design defined P6 as `Wait for ground authorization`.

WP9-A therefore restores P6 **only as a required pre-campaign policy extension** for the E3 contact-delay contrast:

- `P6/C0`: current synthetic ground authorization is available at the response boundary; after authorization, verified rollback is requested.
- `P6/C1`: one modeled contact window is missed before current synthetic ground authorization becomes available; verified rollback is then requested.
- `P7`: remains autonomous and, for E3/T0/M4, delegates to P5 without waiting for the ground-authorization gate.

This change is driven by proposition identifiability, not by a favorable WP8 outcome. P6 is not yet present in `configs/experiment_model.json`, the run schema, or runtime execution. **WP9-B must implement and validate it before any final-campaign execution or repetition-count freeze.**

## Frozen 24-cell matrix

| ID | Event | Mission | Contact | Evidence | Requested policy | Expected effective policy | Primary role |
|---|---|---|---|---|---|---|---|
| A01 | E1 | M0 | C0 | T0 | P1 | P1 | P1 mission-state fixed M0 |
| A02 | E1 | M0 | C0 | T0 | P7 | P1 | P1 mission-state adaptive M0 |
| A03 | E1 | M2 | C0 | T0 | P1 | P1 | P1 mission-state fixed M2 |
| A04 | E1 | M2 | C0 | T0 | P7 | P2 | P1/P4 shared adaptive cell |
| A05 | E1 | M4 | C0 | T0 | P1 | P1 | P1 mission-state fixed M4 |
| A06 | E1 | M4 | C0 | T0 | P7 | P2 | P1 mission-state adaptive M4 |
| A07 | E1 | M2 | C0 | T0 | P2 | P2 | P4 E1 fixed/full evidence |
| A08 | E1 | M2 | C0 | T1 | P2 | P2 | P4 E1 fixed/reduced evidence |
| A09 | E1 | M2 | C0 | T1 | P7 | P4 | P4 E1 adaptive/reduced evidence |
| A10 | E3 | M4 | C0 | T0 | P2 | P2 | P4 E3 fixed/full evidence |
| A11 | E3 | M4 | C0 | T0 | P7 | P5 | P2/P3/P4 shared adaptive cell |
| A12 | E3 | M4 | C0 | T1 | P2 | P2 | P4 E3 fixed/reduced evidence |
| A13 | E3 | M4 | C0 | T1 | P7 | P2 | P3/P4 adaptive/reduced evidence |
| A14 | E3 | M4 | C0 | T0 | P5 | P5 | P3 fixed recovery/full evidence |
| A15 | E3 | M4 | C0 | T1 | P5 | P5 | P3 fixed recovery/reduced evidence |
| A16 | E3 | M4 | C0 | T0 | P6 | P6 | P2 ground-authorized/immediate contact |
| A17 | E3 | M4 | C1 | T0 | P6 | P6 | P2 ground-authorized/missed contact |
| A18 | E3 | M4 | C1 | T0 | P7 | P5 | P2 autonomous/missed contact |
| A19 | E2 | M0 | C0 | T0 | P0 | P0 | Replay untreated sentinel |
| A20 | E2 | M0 | C0 | T0 | P1 | P1 | Replay fixed containment |
| A21 | E2 | M0 | C0 | T0 | P7 | P1 | Replay matched P7 |
| A22 | E4 | M2 | C0 | T0 | P0 | P0 | Observability untreated sentinel |
| A23 | E4 | M2 | C0 | T0 | P4 | P4 | Observability fixed conservative response |
| A24 | E4 | M2 | C0 | T0 | P7 | P4 | Observability matched P7 |

## Identifiability audit

The primary interaction blocks are complete rather than aliased fractions:

- **P1:** `policy {P1,P7} × mission {M0,M2,M4}` = 6/6 cells.
- **P2:** `policy {P6,P7} × contact {C0,C1}` under E3/M4/T0 = 4/4 cells.
- **P3:** `policy {P5,P7} × evidence {T0,T1}` under E3/M4/C0 = 4/4 cells.
- **P4:** `event {E1,E3} × policy {P2,P7} × evidence {T0,T1}` = 8/8 cells.

A classical low-resolution fractional factorial was rejected for these primary interactions because aliasing would weaken interpretation. The economical reduction comes instead from sharing cells across proposition blocks and omitting scientifically non-identifying combinations.

## P5 condition-specific trade-off groups

P5 is analyzed without a weighted primary composite. Pareto membership is evaluated within exact condition groups:

- G01: A01/A02
- G02: A03/A04/A07
- G03: A05/A06
- G04: A08/A09
- G05: A10/A11/A14/A16
- G06: A12/A13/A15
- G07: A17/A18
- G08: A19/A20/A21
- G09: A22/A23/A24

The primary Pareto dimensions remain unauthorized-effect completion, mission-objective completion, safety-invariant violations, time to verified recovery, and legitimate-command rejection. No single weighted score replaces them.

## Endpoint and model applicability

Global rules:

1. Random seed is a reproducible block. The same final-campaign seed runs every frozen cell, with randomized cell order within each seed block and a clean snapshot before each trial.
2. Raw counts and denominators are reported with ratios.
3. Missing primary metrics are not imputed.
4. Unobserved containment or trusted recovery remains right-censored.
5. Expected values are never substituted for observations.
6. Ground truth remains separate from policy-visible evidence and is never a runtime policy oracle.
7. A structurally constant pilot endpoint cannot pass WP9-C merely because empirical bootstrap width is zero. Conservative sensitivity must also pass.
8. Model-fit convergence is evaluated only on nondegenerate simulated datasets; singular fits, separation, invalid variance estimates, or nonfinite coefficients are failures. Structural-degeneracy fallbacks are tracked separately.

Primary model rules:

- **M01 unauthorized effect:** binomial mixed model for factorial contrasts; exact cellwise intervals and seed-blocked risk-difference bootstrap if separation occurs.
- **M02 mission objective ratio:** run-level mixed model with seed block and bootstrap marginal contrasts; seed-blocked nonparametric contrast is the fallback.
- **M03 safety violations:** Poisson or negative-binomial mixed model selected by a predeclared dispersion diagnostic; structurally all-zero cells use exact counts/upper bounds rather than a manufactured regression.
- **M04 containment time:** restricted-mean-time contrast through the frozen run horizon with seed-block bootstrap; Cox proportional-hazards analysis is sensitivity-only when proportional-hazards diagnostics are acceptable.
- **M05 verified-recovery time:** same right-censored restricted-mean-time approach as M04.
- **Terminal state:** multinomial model for P2/P3 when at least two outcome categories are estimable; otherwise use the predeclared `TRUSTED_RECOVERY_CONFIRMED` binary contrast plus full category counts.
- **M06 legitimate rejection:** binomial mixed model from raw rejected/attempted counts rather than a precomputed ratio.
- **M07 state divergence:** seed-blocked mixed model with bootstrap marginal contrasts; rank/quantile bootstrap sensitivity under strong skew.
- **M08 evidence completeness:** seed-blocked run-level contrast with checklist numerator/denominator summaries retained.
- **Effective policy:** derived from retained execution metadata for P4 selection analysis; it is not inferred from immutable ground truth.

## WP9-C repetition candidates

The frozen candidates remain:

| Valid repetitions/cell | 24-cell campaign valid executions |
|---:|---:|
| 12 | 288 |
| 16 | 384 |
| 20 | 480 |
| 24 | 576 |
| 30 | 720 |

WP9-C must choose the smallest candidate satisfying all applicable frozen targets under both empirical WP8 resampling and conservative sensitivity:

- ratio-metric 95% CI half-width ≤ 0.10;
- binary-metric 95% CI half-width ≤ 0.18;
- time-metric relative 95% CI half-width ≤ 0.25;
- planned-model convergence ≥ 0.90.

WP8 pilot effect estimates are not treated as final effect-size assumptions.

## WP9-B runtime gate

Before WP9-C can freeze a repetition count, development-only validation must establish all final-campaign mechanisms without consuming final-campaign seeds or generating final-campaign data:

1. Implement P6 synthetic ground-authorization timing and post-authorization verified rollback.
2. Extend the experiment model and run schema to P6 only after its semantics pass.
3. Bind E2 byte-identical replay to the final command-policy measurement path.
4. Validate fixed P2/P5 E3 cells under T0/T1, preserving nonrecovery and censoring semantics.
5. Validate P0/P1/P7 replay cells using the accepted E2 adapter.
6. Validate P0/P4/P7 E4 cells while preserving immutable ground truth and degraded policy-visible evidence.
7. Validate every A01-A24 factor tuple, expected effective policy, runtime family, raw-metric completeness, isolation, and cleanup.

**No WP9 final-campaign execution is authorized by R-044.**

## Methodological basis

- NIST/SEMATECH, *Use of fractional factorial designs*: low-resolution fractions are efficient for screening, while interaction-focused work requires designs that preserve interaction estimability.
- Kumle, Võ, and Draschkow (2021), *Estimating power in (generalized) linear mixed models*, DOI `10.3758/s13428-021-01546-0`: simulation-based planning is appropriate for complex mixed models and depends on an accurately specified model/design.
- Ying et al. (2025), *Determining sample size for pilot trials: a tutorial*, BMJ 390: pilot effect and variance estimates can be imprecise and should not be treated as definitive effect assumptions.
- Royston and Parmar (2013), *Restricted mean survival time: an alternative to the hazard ratio for the design and analysis of randomized trials with a time-to-event outcome*, DOI `10.1186/1471-2288-13-152`: RMST provides an interpretable time-to-event estimand without requiring proportional hazards.
