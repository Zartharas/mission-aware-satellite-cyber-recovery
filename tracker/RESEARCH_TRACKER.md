# Research Tracker

Last updated: 2026-08-29

## Current focus

**WP9 final frozen experiment campaign is COMPLETE. The canonical runtime/operator stack is R-064 through R-070. All 720/720 valid frozen positions are retained (24 cells × 30 campaign seeds, zero gaps, zero duplicates), independently verified against `results/wp9/campaign/attempt-history.json`. See `docs/26-wp9-r069-campaign-closeout.md` for the full closeout record. WP10 statistical analysis is the current focus.**

The frozen design was 24 cells × 30 valid repetitions = 720 valid executions with campaign seeds `10001`–`10030` and the deterministic R-053 within-seed order. One trial was executed per invocation throughout; automatic retry and automatic next-case execution never occurred. An INVALID attempt never advanced the frozen position and required the same seed/cell with a fresh run ID. Expected values remained acceptance-only and never replaced raw metrics. Treatment-fidelity failures invalidated a trial; unexpected but treatment-valid scientific outcomes were retained. Nine INVALID attempts and one quarantined (never-ledgered) interrupted attempt occurred across the campaign — see `docs/26-wp9-r069-campaign-closeout.md`.

## Current campaign/runtime baseline

Current promoted campaign baseline:

- **Final campaign execution baseline (the commit every one of the 720 valid trials, including the last, actually ran against):** `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446` (R-070: E1 legacy-finalize consumer contract fidelity fix). Independently confirmed via the last valid trial's own `repo_commit` field (position 720, seed 10030, cell A23).
- **Current repository HEAD (documentation-only commits after campaign completion, no campaign-affecting code):** `a0ba4b4` (docs: record WP9 R-069 campaign completion) and onward as further docs land. This will keep moving as documentation is revised; the final campaign execution baseline above will not.
- R-066 validated source mechanisms remain the scientific runtime basis; later R-067/R-068/R-069/R-070 changes are compatibility, continuity, and operator-control plumbing only.
- The campaign executed to completion on the `7ed85d5` baseline; no campaign-affecting commits occurred after R-070.

### R-064 through R-070

- **R-064 — final-campaign bridge and attempt history:** exact one-trial campaign bridge plus run-ID uniqueness, exact-next-position enforcement, INVALID non-advancement, same-seed/cell retry, fresh-run-ID requirement, duplicate-valid prevention, and hidden-rerun prevention.
- **R-065 — bounded production integration:** representative Z01–Z09 development cases exercised the production mechanism families/variants with seeds `9941`–`9949`. No campaign seed/data was consumed. The bounded series closed with treatment fidelity, raw-metric completeness, runtime-health, cleanup, and claim-boundary checks passing across the intended representative cases.
- **R-066 — production campaign runtime binding:** all A01–A24 cells bind to previously runtime-validated E1/E2/E3/E4 source harnesses by exact Git blob identity. R-066 added campaign evidence freshness controls, post-readiness seed commitment, JSON-persistence stability, exact single-trial authorization, source-harness derivation checks, and wrapper-composition preflight.
- **R-066 JSON persistence remediation:** the first production start of position 1 stopped pre-runtime because a tuple-valued source binding changed representation after JSON persistence. CI reproduced the exact defect and the binding was normalized to a JSON-native representation. No source harness was invoked and no campaign seed was consumed.
- **R-066 wrapper-composition remediation:** a subsequent production start of position 1 stopped pre-runtime on wrapper self-recursion. The retained run directory contained only plan/request evidence, no campaign-seed commit marker, no runtime observation, no canonical VALID/INVALID result, and no attempt-history entry. It is preserved as `PRE_RUNTIME_ABORT_UNCONSUMED` and does not count as a scientific campaign attempt. The remediation added immutable base-function capture, exact zero-write wrapper-composition preflight, fail-closed global restoration checks, and static composition validation across all 24 frozen cells. Promoted composition-hardening baseline: `aae2239753119c92e7633db3b6c73aee94c7b6dd`.
- **R-067 — legacy finalization-summary compatibility:** position 2 (`10001/A13`) produced a retained INVALID scientific attempt after the E3 runtime/treatment completed successfully but the historical R-063 source harness failed in `MEASUREMENT_BINDING`. R-066 finalization had supplied the canonical campaign bundle where the legacy E1/E3 summary reader expected the historical compatibility field `unexpected_scientific_outcome_would_be_retained_in_campaign`. R-067 restores the legacy summary alias while preserving the canonical campaign result. No source harness, frozen design, seed order, timing, treatment, policy, raw metric, or scientific acceptance semantics changed. Merged as PR #35, merge `05dcb05bf73d6d2a52c0baf55c3e919d4278b7fe`.
- **R-068 — baseline-aware campaign continuity:** retained trials are validated against the repository SHA they actually executed on, and that historical execution SHA must remain an ancestor of the current campaign baseline. This prevents false continuity failure after plumbing-only promotions without relaxing frozen order, ledger integrity, treatment fidelity, retry/next controls, or evidence requirements. Merged as PR #36, merge `72e3a9d81d70b2b993bf28228f3b7b0af24c9908`.
- **R-069 — canonical one-position campaign operator:** added the reusable schema-aware operator `scripts/run_wp9_r069_campaign_one_position.sh`. It derives the exact next frozen position from retained R-064/R-068 state, builds the exact single-trial authorization/request, validates the canonical nested schema, enforces an operator lock and clean NOS3 snapshot, invokes R-066 exactly once, atomically appends one returned VALID/INVALID result, performs residue/alias audits, and never retries or advances automatically. This replaced ad-hoc per-position wrappers and avoids the prior top-level-schema assumption that stopped a position-2 retry pre-runtime. Merged as PR #37, merge baseline `97074d0cdc4261de02bc6f618e891a88f45f9cfc`. This operator ran every remaining frozen position through campaign completion.
- **R-070 — E1 legacy-finalize consumer contract:** enforces the exact E1 legacy finalize consumer contract (`e1_legacy_finalize_consumer_contract_enforced=true`), confirmed present in every campaign trial's static-contract section for the remainder of the campaign. Commits `6a9aa42` (red), `e90989a` (enforce), `7ed85d5` (fixture fidelity fields).
- **Campaign completion (2026-08-29):** the R-069 operator, invoked one position at a time under human supervision, carried the campaign from position 1 through position 720. Nine retained INVALID attempts occurred, each cleared by a same-seed/cell fresh-run-ID retry per the frozen design; they span 5 distinct `failed_phase` values (`CFS_READINESS` ×3, `MEASUREMENT_BINDING` ×2 — including position 2/`10001/A13`, the R-067-motivating case — `NOMINAL_RUNTIME_COMPLETION` ×2, `RUNTIME_HEALTH` ×1, `FROZEN_ANALYSIS_HORIZON` ×1), not the two informal signatures an earlier draft of the closeout used. One additional interrupted mid-harness-preflight attempt (position 660) was never ledgered; it was quarantined intact to `results/wp9/campaign/_quarantined-unledgered/` rather than deleted or fabricated into a ledger entry, and position 660 was then re-derived and executed cleanly. Full per-attempt table and taxonomy: `docs/26-wp9-r069-campaign-closeout.md`.

## Final campaign progress

**Campaign complete: 720/720 valid positions retained as of 2026-08-29. Full closeout record: `docs/26-wp9-r069-campaign-closeout.md`.**

### Frozen position 1 — VALID (first position executed; retained as historical record)

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

### Frozen position 2 — RETAINED INVALID then cleared (historical record)

- campaign seed: `10001`
- cell: `A13`
- one retained scientific INVALID attempt occurred from the pre-R-067 finalization-summary compatibility defect: the E3 runtime/treatment itself completed, but legacy `MEASUREMENT_BINDING` failed after finalization due to the schema compatibility mismatch described under R-067.
- the INVALID attempt was retained and did not count toward the 720 valid executions.
- position `10001/A13` was subsequently retried with a fresh run ID under the R-069 operator and cleared to VALID; the campaign proceeded from there.

### Full incident history (all 9 retained INVALID attempts, plus the one quarantined never-ledgered attempt)

See `docs/26-wp9-r069-campaign-closeout.md` for the complete account: three mid-run Docker-termination INVALID attempts (positions 404, 407, 582), two pre-execution-failure INVALID attempts (positions 594, 627), three pre-flight blocks that produced no ledger entry at all, and one interrupted mid-harness-preflight attempt at position 660 that was quarantined (not ledgered, not deleted) to `results/wp9/campaign/_quarantined-unledgered/` and then re-derived and executed cleanly.

## Campaign ledger / final state

Durable scientific state, independently verified against `results/wp9/campaign/attempt-history.json` on 2026-08-29:

- valid frozen positions: `720` of `720` — **campaign target met**
- retained scientific INVALID attempts: `9` total (see incident history above)
- quarantined never-ledgered attempts: `1` (position 660 interrupted attempt; evidence retained under `results/wp9/campaign/_quarantined-unledgered/`)
- `campaign_complete`: `true`
- campaign seeds `10001`–`10030`: all 30 represented, contiguous, no gaps
- all 24 frozen cells (A01–A24): exactly 30 valid repetitions each, no deviations
- unique (seed, cell) valid pairs: `720`, zero duplicates, zero gaps

The local `results/wp9/campaign/attempt-history.json` remains the execution authority and the sole source of truth for this state; this tracker summarizes it but is not authoritative over it.

## Next exact action

**No further `run-once` invocations are expected.** The frozen 24×30 design's target is met and `campaign_complete=true` in the ledger. The R-069 operator's next-position derivation step should refuse (or be inapplicable) for a hypothetical position 721 under the frozen design; this has not been explicitly exercised but follows directly from seed/cell exhaustion.

The next work is WP10: perform the read-only campaign integrity freeze recommended in `docs/26-wp9-r069-campaign-closeout.md` (full-tree unledgered-artifact re-audit, trial-payload spot-checks, INVALID-attempt review, decision on referencing the quarantined Signature-C evidence, and consideration of a successor decision record for the Signature-C handling policy), then proceed to the predeclared statistical analysis in `docs/18-wp9a-final-campaign-design.md`.

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
| WP9 | Frozen experiment campaign | **Complete — 720/720 valid positions retained** | Full closeout record: `docs/26-wp9-r069-campaign-closeout.md`. 9 retained INVALID attempts, 1 quarantined never-ledgered attempt (Signature C), zero unresolved incidents |
| WP10 | Analysis and manuscript | **Ready to start** | Campaign integrity freeze (recommended steps in `docs/26-wp9-r069-campaign-closeout.md`) → reproducible statistical analysis → figures/tables → limitations → manuscript |
| WP11 | Responsible artifact release | Not started | Sanitized reproducibility release after analysis/manuscript stabilization |

## Remaining research path

1. ~~Complete WP9 frozen campaign to 720 valid positions using R-069 one position per invocation.~~ **Done 2026-08-29** — see `docs/26-wp9-r069-campaign-closeout.md`.
2. Perform a read-only campaign integrity freeze: full-tree unledgered-artifact re-audit, run-ID uniqueness, retained invalid/pre-runtime/quarantined evidence classification, seed/cell continuity, treatment-fidelity validity, evidence completeness, and final dataset/evidence hashes. **Outstanding — recommended before WP10 analysis begins.**
3. Complete WP10 statistical analysis using only the frozen campaign dataset and predeclared metrics; retain unexpected valid science.
4. Final-review WP1–WP3 against the empirical findings and current publication literature.
5. Draft and revise the journal manuscript from the locked evidence, including how (or whether) to reference the quarantined Signature-C evidence in methods/limitations.
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
