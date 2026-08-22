# WP8 Pilot Closeout

**Closeout date:** 2026-08-21  
**Status:** Complete  
**Role:** Scientific provenance record for the transition from WP8 pilot work to WP9 pre-campaign repetition-count selection.

## Frozen implementation identity

- Stage-2 implementation commit: `b575e8029592a712e2580371d10444b8323aad37`
- Exact-SHA validation workflow: `Validate research configurations`
- CI run: `32504671207`
- CI conclusion: `success`
- Read-only closeout audit script SHA-256: `967edd217975e02dea4272192df540bcbfa4cecf17521d20223aa0a90c0edeea`

## Pilot closeout result

The read-only WP8 closeout audit passed without pilot execution, repository mutation, ledger mutation, or seed consumption.

- Stage 1: 12 valid cells from 13 retained attempts.
- Stage 1 excluded attempt: `20260821T023416.716772Z-wp8-stage1-r02-s101-99cec463d05f4c2fa4802d6140bd09f6`.
- Excluded-attempt classification: `RUN_INVALID`, `non_infrastructure`, cause `post_recovery_verification`, `experiment_failure_claimed=false`, `pilot_data=false`.
- Stage 2: 28 valid repetitions from 28 retained attempts; 0 invalid attempts.
- Total scientifically valid pilot executions: 40.
- Frozen attempt archives independently verified: 41, with 41 SHA-256 sidecars.
- Stage-2 anchor balance: 5 valid observations per anchor using seeds `101, 202, 303, 404, 505` for `C02`, `C03`, `C05`, `C06`, `R02`, `R03`, and `O01`.

The retained runtime archives remain outside the implementation repository. This record preserves the audited closeout facts and decision boundary without importing raw pilot evidence into GitHub.

## Scientific claim boundary

WP8 establishes control validity, reproducible measurement, observed pilot variability, censoring behavior, and readiness for repetition-count selection. WP8 pilot results are not final hypothesis tests and must not be reported as final effect-size or recovery-rate estimates.

The following distinctions remain mandatory:

- Expected values are post-observation acceptance criteria, not raw measurement inputs.
- Ground truth is not a policy oracle.
- Evidence availability/currentness is distinct from trusted-recovery criterion satisfaction.
- Unobserved containment or trusted-recovery times remain right-censored rather than being imputed as zero.
- A `RECOVERY_FAILED` study classification is not a spacecraft-failure claim.
- Findings are limited to the controlled NOS3/software-in-the-loop surrogate environment.

## WP9 transition gate

No WP9 final-campaign execution is authorized by this closeout.

The frozen repetition-selection rule must be executed as a separate read-only statistical-design gate using the retained WP8 pilot distributions:

- Candidate valid repetitions per final-campaign cell: `12, 16, 20, 24, 30`.
- Ratio-metric 95% CI half-width target: `<= 0.10`.
- Binary-metric 95% CI half-width target: `<= 0.18`.
- Time-metric relative 95% CI half-width target: `<= 0.25`.
- Model-fit convergence target: `>= 0.90`.
- Selection rule: choose the smallest candidate satisfying all applicable precision and model-stability targets. If none through 30 satisfies the rule, do not freeze WP9; revise instrumentation/design or extend the pilot instead.

WP9 campaign execution remains blocked until that repetition-count gate is completed, independently reviewed, and explicitly authorized.
