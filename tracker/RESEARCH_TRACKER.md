# Research Tracker

Last updated: 2026-08-25

## Current focus

**WP9 final frozen experiment campaign is active. The canonical runtime/operator stack is R-066 through R-069. Frozen position 1 is valid; position 2 (`10001/A13`) has one retained INVALID scientific attempt and remains the exact next frozen position for a new-run-ID retry.**

The frozen design remains 24 cells × 30 valid repetitions = 720 valid executions with campaign seeds `10001`–`10030` and the deterministic R-053 within-seed order. One trial is executed per invocation. Automatic retry and automatic next-case execution are prohibited. An INVALID attempt does not advance the frozen position and requires the same seed/cell with a fresh run ID. Expected values are acceptance-only and never replace raw metrics. Treatment-fidelity failures invalidate a trial; unexpected but treatment-valid scientific outcomes are retained.

## Current campaign/runtime baseline

Current promoted campaign baseline:

- `main`: `97074d0cdc4261de02bc6f618e891a88f45f9cfc`
- merge: **R-069 canonical one-position campaign operator**
- R-066 validated source mechanisms remain the scientific runtime basis; later R-067/R-068/R-069 changes are compatibility, continuity, and operator-control plumbing only.

### R-064 through R-069

- **R-064 — final-campaign bridge and attempt history:** exact one-trial campaign bridge plus run-ID uniqueness, exact-next-position enforcement, INVALID non-advancement, same-seed/cell retry, fresh-run-ID requirement, duplicate-valid prevention, and hidden-rerun prevention.
- **R-065 — bounded production integration:** representative Z01–Z09 development cases exercised the production mechanism families/variants with seeds `9941`–`9949`. No campaign seed/data was consumed. The bounded series closed with treatment fidelity, raw-metric completeness, runtime-health, cleanup, and claim-boundary checks passing across the intended representative cases.
- **R-066 — production campaign runtime binding:** all A01–A24 cells bind to previously runtime-validated E1/E2/E3/E4 source harnesses by exact Git blob identity. R-066 added campaign evidence freshness controls, post-readiness seed commitment, JSON-persistence stability, exact single-trial authorization, source-harness derivation checks, and wrapper-composition preflight.
- **R-066 JSON persistence remediation:** the first production start of position 1 stopped pre-runtime because a tuple-valued source binding changed representation after JSON persistence. CI reproduced the exact defect and the binding was normalized to a JSON-native representation. No source harness was invoked and no campaign seed was consumed.
- **R-066 wrapper-composition remediation:** a subsequent production start of position 1 stopped pre-runtime on wrapper self-recursion. The retained run directory contained only plan/request evidence, no campaign-seed commit marker, no runtime observation, no canonical VALID/INVALID result, and no attempt-history entry. It is preserved as `PRE_RUNTIME_ABORT_UNCONSUMED` and does not count as a scientific campaign attempt. The remediation added immutable base-function capture, exact zero-write wrapper-composition preflight, fail-closed global restoration checks, and static composition validation across all 24 frozen cells. Promoted composition-hardening baseline: `aae2239753119c92e7633db3b6c73aee94c7b6dd`.
- **R-067 — legacy finalization-summary compatibility:** position 2 (`10001/A13`) produced a retained INVALID scientific attempt after the E3 runtime/treatment completed successfully but the historical R-063 source harness failed in `MEASUREMENT_BINDING`. R-066 finalization had supplied the canonical campaign bundle where the legacy E1/E3 summary reader expected the historical compatibility field `unexpected_scientific_outcome_would_be_retained_in_campaign`. R-067 restores the legacy summary alias while preserving the canonical campaign result. No source harness, frozen design, seed order, timing, treatment, policy, raw metric, or scientific acceptance semantics changed. Merged as PR #35, merge `05dcb05bf73d6d2a52c0baf55c3e919d4278b7fe`.
- **R-068 — baseline-aware campaign continuity:** retained trials are validated against the repository SHA they actually executed on, and that historical execution SHA must remain an ancestor of the current campaign baseline. This prevents false continuity failure after plumbing-only promotions without relaxing frozen order, ledger integrity, treatment fidelity, retry/next controls, or evidence requirements. Merged as PR #36, merge `72e3a9d81d70b2b993bf28228f3b7b0af24c9908`.
- **R-069 — canonical one-position campaign operator:** added the reusable schema-aware operator `scripts/run_wp9_r069_campaign_one_position.sh`. It derives the exact next frozen position from retained R-064/R-068 state, builds the exact single-trial authorization/request, validates the canonical nested schema, enforces an operator lock and clean NOS3 snapshot, invokes R-066 exactly once, atomically appends one returned VALID/INVALID result, performs residue/alias audits, and never retries or advances automatically. This replaced ad-hoc per-position wrappers and avoids the prior top-level-schema assumption that stopped a position-2 retry pre-runtime. Merged as PR #37, merge/current baseline `97074d0cdc4261de02bc6f618e891a88f45f9cfc`.

## Final campaign progress

### Frozen position 1 — VALID

- global order index: `1`
- campaign seed: `10001`
- cell: `A19`
- event: `E2` replayed command
- requested/effective policy: `P0 → P0`
- action: `OBSERVE_ONLY`
- run ID: `20260824T145723Z-wp9-r066-p0001-s10001-a19-69fe370fe1d249e68ebf05671a630b9d`
- attempt status: `VALID`
- source harness invocation count: `1`
- campaign seed consumed: `true`
- campaign data generated: `true`
- treatment fidelity valid: `true`
- raw metric inputs complete: `true`
- outcome matched predeclared expectation: `true`
- automatic retry/next: `false / false`

Retained E2/P0 discriminators:

- replay gateway action: `OBSERVE_ONLY`
- replay forwarded: `true`
- replay packet byte-identical: `true`
- post-replay reset-marker delta: `1`
- authorized NOOP forwarded: `true`
- post-response authorized-NOOP marker delta: `1`
- runtime health passed: `true`
- unauthorized effect completed: `true`
- containment: `false`
- terminal state: `RECOVERY_FAILED`
- trusted recovery confirmed: `false`
- mission objective completion ratio: `0.5`
- legitimate-command rejection rate: `0.0`
- evidence completeness ratio: `1.0`
- modeled ground/spacecraft-state divergence: `28.281255168 s`

This is a valid observation for the frozen P0 observation-only treatment; allowing the replay effect to complete is not itself a treatment-fidelity failure.

### Frozen position 2 — RETAINED INVALID; position remains current

- campaign seed: `10001`
- cell: `A13`
- event family: `E3`
- one retained scientific INVALID attempt exists from the pre-R-067 finalization-summary compatibility defect;
- the E3 runtime/treatment itself completed, but legacy `MEASUREMENT_BINDING` failed after finalization due to the schema compatibility mismatch described under R-067;
- the INVALID attempt must remain retained and does not count toward 720 valid executions;
- the exact next scientific action is a new-run-ID retry of the same frozen position `10001/A13` using the current R-069 operator;
- a later retry-wrapper schema stop occurred pre-runtime and is not a scientific campaign attempt.

## Campaign ledger / continuity state

Durable scientific state known at this checkpoint:

- valid frozen positions: `1`
- retained scientific INVALID attempts: `1` at position 2 / `10001/A13`
- preserved pre-runtime abort artifacts: retained separately and not entered as scientific attempts when no seed commitment/source-harness runtime occurred
- current frozen position: `2`
- next required campaign seed: `10001`
- next required cell: `A13`
- retry requires a fresh run ID

The local `results/wp9/campaign/attempt-history.json` remains the execution authority for exact next-position derivation. The R-068 continuity contract must pass before each new scientific invocation when the repository baseline has changed since earlier retained trials.

## Next exact action

Run **only** the canonical R-069 one-position operator for the current ledger state:

```bash
./scripts/run_wp9_r069_campaign_one_position.sh validate-static
./scripts/run_wp9_r069_campaign_one_position.sh run-once
```

The operator itself must derive the exact frozen position from the retained attempt ledger. Do not manually hard-code or skip to a later cell. If the retained position-2 attempt is the last scientific attempt, the operator should derive a fresh-run-ID retry of `10001/A13`. It must never run the following position automatically.

Continue until all 720 valid frozen positions are retained. Then perform a read-only campaign integrity freeze before any statistical analysis.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Refresh publication-era literature and finalize novelty after empirical results are locked |
| WP2 | Theoretical model | Ready for final review | Final proposition-to-metric traceability against retained campaign variables |
| WP3 | Threat and mission model | Ready for final review | Final event/scenario/claim-boundary review against observed campaign evidence |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1–E4 deterministic event adapters validated against accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Deterministic fixed-policy/P7 mechanisms and bounded P6 extension validated |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery and bounded failure-mode validations passed |
| WP8 | Pilot | **Complete** | 40 valid pilot executions; one retained/excluded Stage-1 invalid attempt; 41 frozen archives verified |
| WP9 | Frozen experiment campaign | **In progress — 1/720 valid positions complete** | Position 1 `10001/A19` VALID; position 2 `10001/A13` has one retained INVALID attempt and remains current for a fresh-run-ID retry through R-069 |
| WP10 | Analysis and manuscript | Pending campaign completion | Campaign integrity freeze → reproducible statistical analysis → figures/tables → limitations → manuscript |
| WP11 | Responsible artifact release | Not started | Sanitized reproducibility release after analysis/manuscript stabilization |

## Remaining research path

1. Complete WP9 frozen campaign to 720 valid positions using R-069 one position per invocation.
2. Perform a read-only campaign integrity freeze: exact 720 valid frozen positions, run-ID uniqueness, retained invalid/pre-runtime evidence classification, seed/cell continuity, treatment-fidelity validity, evidence completeness, and final dataset/evidence hashes.
3. Complete WP10 statistical analysis using only the frozen campaign dataset and predeclared metrics; retain unexpected valid science.
4. Final-review WP1–WP3 against the empirical findings and current publication literature.
5. Draft and revise the journal manuscript from the locked evidence.
6. Complete WP11 sanitized reproducibility/artifact release and submission package.

## Scientific and claim boundaries

Preserve throughout campaign execution, analysis, and publication:

- controlled NOS3 software-in-the-loop only;
- no real spacecraft access;
- no RF interference/transmission claim;
- no native spacecraft safe-mode claim;
- no real ground-contact timing claim;
- no real human-operator timing claim;
- C1 timing is synthetic/modelled only;
- immutable ground truth never acts as a policy oracle;
- expectations are acceptance-only and are not metric inputs;
- treatment-fidelity failures invalidate trials;
- unexpected treatment-valid outcomes are retained;
- trusted recovery is reported only when all applicable/current terminal evidence supports it;
- one runtime trial per invocation;
- no automatic retry and no automatic next-case execution.

## WP4 closeout

The passive time-witness/D-064 branch is discontinued. It is not required for the core research claims and will not receive a successor attempt.

## WP5 acceptance

WP5 is complete when the four selected event families have:

- source/threat-model mapping;
- deterministic parameters;
- immutable ground truth;
- policy-visible evidence representation;
- expected and prohibited modeled effects;
- isolation/cleanup semantics;
- positive, negative, and repeatability tests; and
- one bounded simulator adapter per retained event family.
