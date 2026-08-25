# Research Tracker

Last updated: 2026-08-25

## Current focus

**WP9 final frozen experiment campaign is active under the promoted R-066 production single-trial runtime. Frozen position 1 is valid and retained; the next required frozen position is position 2: seed 10001 / A13.**

The pre-campaign engineering sequence is closed. R-064 added the single-trial campaign bridge and exact-attempt-history semantics. R-065 completed bounded production-integration validation across representative Z01–Z09 development cases without consuming campaign seeds. R-066 bound the frozen campaign to the already runtime-validated E1/E2/E3/E4 mechanisms, added exact source-harness blob checks, campaign evidence freshness controls, post-readiness seed-commit semantics, exact one-trial authorization, JSON-persistence stability, wrapper-composition preflight, and fail-closed restoration checks. The promoted R-066 main baseline for campaign position 1 was commit `aae2239753119c92e7633db3b6c73aee94c7b6dd`, tree `105bc8a868ab90e0c1cfd2385e4e0b50924312df`.

The frozen campaign remains 24 cells × 30 valid repetitions = 720 valid executions. Campaign seeds are `10001`–`10030`; within-seed order is deterministic under the frozen R-053 ordering rule. C1 is a modeled 10-second synthetic missed-contact window. E1–E4 use the common 30-second post-event observation/right-censoring horizon where applicable. One trial is executed per invocation. Automatic retry and automatic next-case execution remain prohibited. Invalid attempts retain the same frozen seed/cell and require a fresh run ID. Expected values are acceptance-only and never replace raw metric inputs. Treatment-fidelity failures invalidate a trial; unexpected but treatment-valid scientific outcomes are retained.

## R-064 through R-066 closeout

- **R-064:** final-campaign bridge and one-trial campaign routing established; final campaign still fail-closed without a production executor.
- **R-065:** bounded integration closed across Z01–Z09 using development seeds `9941`–`9949`; all intended runtime mechanism families/variants passed. No campaign seed was consumed and no campaign data was generated.
- **R-064 attempt-history guard:** enforces global run-ID uniqueness, exact next frozen position, invalid-attempt non-advancement, new-run-ID requirement after invalidity, duplicate-valid rejection, and hidden-rerun rejection.
- **R-066 production binding:** all A01–A24 cells bind to the previously validated E1/E2/E3/E4 source harnesses by exact Git blob identity. Campaign seed/cell identities are passed through to the runtime while the scientific mechanism body remains derived from the validated source harness.
- **R-066 evidence freshness:** both `results/wp9/campaign/<seed>/<cell>/<run_id>` and `artifacts/runtime/<run_id>` must be fresh and symlink-safe before execution.
- **R-066 seed commitment:** campaign seed commitment is recorded only after nominal NOS3 readiness and isolation and before seed-dependent scientific runtime effects.
- **R-066 persistence defect:** the first production attempt to start position 1 exposed a JSON tuple/list equality defect in the persisted `source_harness` binding. It was reproduced in CI, fixed by using a JSON-native list, and promoted. No source harness was invoked and no campaign seed was consumed.
- **R-066 composition defect:** a subsequent position-1 start exposed recursion in the wrapper composition layer. The retained run directory contains only pre-runtime request/plan evidence and no seed-commit marker, runtime observation, canonical campaign result, or attempt-history entry. It is classified `PRE_RUNTIME_ABORT_UNCONSUMED`, preserved as evidence, and does not count as a scientific campaign attempt. The defect was independently reproduced by focused tests and fixed by immutable base-function capture, exact zero-write wrapper-composition preflight, fail-closed restoration checks, and static composition validation across all 24 cells.
- **Composition hardening promotion:** commit `aae2239753119c92e7633db3b6c73aee94c7b6dd`, tree `105bc8a868ab90e0c1cfd2385e4e0b50924312df`.

## Final campaign progress

### Frozen position 1 — VALID

- Global order index: `1`
- Campaign seed: `10001`
- Cell: `A19`
- Event: `E2` replayed command
- Requested/effective policy: `P0 → P0`
- Selected action: `OBSERVE_ONLY`
- Run ID: `20260824T145723Z-wp9-r066-p0001-s10001-a19-69fe370fe1d249e68ebf05671a630b9d`
- Attempt status: `VALID`
- Source harness invocation count: `1`
- Runtime execution performed: `true`
- Campaign seed consumed: `true`
- Campaign data generated: `true`
- Treatment fidelity valid: `true`
- Raw metric inputs complete: `true`
- Outcome matched predeclared expectation: `true`
- Unexpected scientific outcome retained: `false`
- Automatic retry: `false`
- Automatic next case: `false`
- Campaign-wide execution authorization: `false`

Observed E2 discriminators for A19/P0:

- replay gateway action: `OBSERVE_ONLY`
- replay gateway forwarded: `true`
- replayed packet byte-identical: `true`
- post-replay reset-marker delta: `1`
- authorized NOOP gateway forwarded: `true`
- intervening authorized-NOOP marker delta: `1`
- post-response authorized-NOOP marker delta: `1`
- runtime health passed: `true`
- unauthorized effect completed: `true`
- containment: `false`
- terminal state: `RECOVERY_FAILED`
- trusted recovery confirmed: `false`
- mission objective completion ratio: `0.5`
- legitimate command rejection rate: `0.0`
- evidence completeness ratio: `1.0`
- ground/spacecraft-state divergence: `28.281255168 s`

These are valid observations for the frozen P0 observation-only treatment; they are not treatment failures merely because the replay effect is allowed to complete.

### Attempt-history state after position 1

- attempt count: `1`
- valid position count: `1`
- invalid attempt count: `0`
- next required global order index: `2`
- next required campaign seed: `10001`
- next required cell order index: `2`
- next required cell: `A13`

The retained pre-runtime R-066 abort remains preserved separately and is not entered in the scientific attempt-history ledger because no seed commitment or source-harness runtime occurred.

## Next exact action

Execute **only frozen position 2: seed `10001` / cell `A13`** using the promoted R-066 single-trial path and the retained attempt-history ledger. Before execution, revalidate exact repository identity, source-harness blob identity, campaign evidence freshness, zero residual NOS3 runtime, and exact next-position derivation from attempt history. Do not automatically execute position 3.

Continue the frozen campaign one invocation at a time until 720 valid positions are retained. After the campaign completes, perform a read-only campaign integrity freeze, then the statistical analysis. Do not add new development work unless a concrete scientific-validity, reproducibility, safety, or legality defect is observed.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Refresh publication-era literature and finalize novelty statement after empirical results are locked |
| WP2 | Theoretical model | Ready for final review | Final proposition-to-metric traceability against retained campaign variables |
| WP3 | Threat and mission model | Ready for final review | Final event/scenario/claim-boundary review against observed campaign evidence |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1–E4 deterministic event adapters validated against accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Deterministic fixed-policy/P7 mechanisms and bounded P6 extension validated |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery and bounded failure-mode validations passed |
| WP8 | Pilot | **Complete** | 40 valid pilot executions; one retained/excluded invalid Stage-1 attempt; 41 frozen archives verified |
| WP9 | Frozen experiment campaign | **In progress — 1/720 valid positions complete** | Position 1 `10001/A19` VALID; next exact frozen position is `10001/A13`; one preserved `PRE_RUNTIME_ABORT_UNCONSUMED` artifact exists outside scientific attempt history |
| WP10 | Analysis and manuscript | Pending campaign completion | Freeze campaign dataset, run reproducible statistical analysis, figures/tables, limitations, manuscript |
| WP11 | Responsible artifact release | Not started | Sanitized reproducibility release after analysis/manuscript stabilization |

## Scientific and claim boundaries

Preserve throughout campaign execution and publication:

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
