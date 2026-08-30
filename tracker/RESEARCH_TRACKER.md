# Research Tracker

Last updated: 2026-08-30

## Current focus

**WP11 responsible release preparation is COMPLETE. The exact six-object local release candidate generated from merge commit `eb3be7aaaed9e60c54843d9a7b9ace1a0fa5812e` passed the independent release audit and the manual rights/privacy/misuse review. The final responsible-release disposition is `PUBLIC_FILES` / `APPROVED_FOR_PUBLICATION`. No Zenodo upload, publication, or DOI assignment has occurred. See `docs/39-wp11-release-preparation-closeout.md` for the exact candidate, audit, review identities, and remaining external archive actions. WP0-WP11 research/release-preparation work is closed; journal-specific submission preparation and actual archive publication are separate next actions.**

The frozen design was 24 cells × 30 valid repetitions = 720 valid executions with campaign seeds `10001`–`10030` and the deterministic R-053 within-seed order. One trial was executed per invocation throughout; automatic retry and automatic next-case execution never occurred. An INVALID attempt never advanced the frozen position and required the same seed/cell with a fresh run ID. Expected values remained acceptance-only and never replaced raw metrics. Trial-validity gate failures invalidated 9 retained attempts; unexpected but treatment-valid scientific outcomes were retained. One additional interrupted never-ledgered run at position 660 was quarantined intact and is not part of the 720-valid analysis membership.

## Current campaign/runtime baseline

Per-attempt execution provenance is now frozen and must be distinguished from the final campaign baseline and later documentation commits:

- **Execution-provenance commit `aae2239753119c92e7633db3b6c73aee94c7b6dd`:** 2 ledgered attempts (1 VALID, 1 INVALID), global-position range 1–2.
- **Execution-provenance commit `97074d0cdc4261de02bc6f618e891a88f45f9cfc`:** 10 ledgered attempts (9 VALID, 1 INVALID), global-position range 2–11.
- **Execution-provenance commit `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`:** 717 ledgered attempts (710 VALID, 7 INVALID), global-position range 11–720.
- **Final campaign execution baseline:** `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446` (R-070 fixture-fidelity fields). The final retained position-720 run independently records this SHA in `immutable-ground/campaign-plan.json`, `immutable-ground/development-plan.json`, and `immutable-ground/r066-runtime-request.json`.
- **Cryptographic-freeze source repository checkpoint:** `18596ea32c696b65bbdaf5676b1157d633ed59b5`. This is a later documentation checkpoint, not the execution baseline for all attempts.
- All three execution commits resolve in Git history and are ancestors of the freeze source checkpoint. The overlaps at positions 2 and 11 are INVALID→VALID retry boundaries that straddled compatibility/plumbing promotions, not duplicate valid observations.
- R-066 validated source mechanisms remain the scientific runtime basis; R-067/R-068/R-069/R-070 are compatibility, continuity, operator-control, and contract-fidelity changes whose exact per-attempt repository identity is retained in the freeze manifest.

The prior wording that every one of the 720 valid trials executed against `7ed85d5` is superseded by the per-attempt provenance above and by `docs/27-wp9-cryptographic-integrity-freeze.md`.

### R-064 through R-070

- **R-064 — final-campaign bridge and attempt history:** exact one-trial campaign bridge plus run-ID uniqueness, exact-next-position enforcement, INVALID non-advancement, same-seed/cell retry, fresh-run-ID requirement, duplicate-valid prevention, and hidden-rerun prevention.
- **R-065 — bounded production integration:** representative Z01–Z09 development cases exercised the production mechanism families/variants with seeds `9941`–`9949`. No campaign seed/data was consumed. The bounded series closed with treatment fidelity, raw-metric completeness, runtime-health, cleanup, and claim-boundary checks passing across the intended representative cases.
- **R-066 — production campaign runtime binding:** all A01–A24 cells bind to previously runtime-validated E1/E2/E3/E4 source harnesses by exact Git blob identity. R-066 added campaign evidence freshness controls, post-readiness seed commitment, JSON-persistence stability, exact single-trial authorization, source-harness derivation checks, and wrapper-composition preflight.
- **R-066 JSON persistence remediation:** the first production start of position 1 stopped pre-runtime because a tuple-valued source binding changed representation after JSON persistence. CI reproduced the exact defect and the binding was normalized to a JSON-native representation. No source harness was invoked and no campaign seed was consumed.
- **R-066 wrapper-composition remediation:** a subsequent production start of position 1 stopped pre-runtime on wrapper self-recursion. The retained run directory contained only plan/request evidence, no campaign-seed commit marker, no runtime observation, no canonical VALID/INVALID result, and no attempt-history entry. It is preserved as `PRE_RUNTIME_ABORT_UNCONSUMED` and does not count as a scientific campaign attempt. The remediation added immutable base-function capture, exact zero-write wrapper-composition preflight, fail-closed global restoration checks, and static composition validation across all 24 frozen cells. Promoted composition-hardening baseline: `aae2239753119c92e7633db3b6c73aee94c7b6dd`.
- **R-067 — legacy finalization-summary compatibility:** position 2 (`10001/A13`) produced a retained INVALID scientific attempt after the E3 runtime/treatment completed successfully but the historical R-063 source harness failed in `MEASUREMENT_BINDING`. R-066 finalization had supplied the canonical campaign bundle where the legacy E1/E3 summary reader expected the historical compatibility field `unexpected_scientific_outcome_would_be_retained_in_campaign`. R-067 restores the legacy summary alias while preserving the canonical campaign result. No source harness, frozen design, seed order, timing, treatment, policy, raw metric, or scientific acceptance semantics changed. Merged as PR #35, merge `05dcb05bf73d6d2a52c0baf55c3e919d4278b7fe`.
- **R-068 — baseline-aware campaign continuity:** retained trials are validated against the repository SHA they actually executed on, and that historical execution SHA must remain an ancestor of the current campaign baseline. This prevents false continuity failure after plumbing-only promotions without relaxing frozen order, ledger integrity, treatment fidelity, retry/next controls, or evidence requirements. Merged as PR #36, merge `72e3a9d81d70b2b993bf28228f3b7b0af24c9908`.
- **R-069 — canonical one-position campaign operator:** added the reusable schema-aware operator `scripts/run_wp9_r069_campaign_one_position.sh`. It derives the exact next frozen position from retained R-064/R-068 state, builds the exact single-trial authorization/request, validates the canonical nested schema, enforces an operator lock and clean NOS3 snapshot, invokes R-066 exactly once, atomically appends one returned VALID/INVALID result, performs residue/alias audits, and never retries or advances automatically. This replaced ad-hoc per-position wrappers and avoids the prior top-level-schema assumption that stopped a position-2 retry pre-runtime. Merged as PR #37, merge baseline `97074d0cdc4261de02bc6f618e891a88f45f9cfc`. This operator ran every remaining frozen position through campaign completion.
- **R-070 — E1 legacy-finalize consumer contract:** enforces the exact E1 legacy finalize consumer contract (`e1_legacy_finalize_consumer_contract_enforced=true`), confirmed present in every applicable campaign trial's static-contract section for the remainder of the campaign. Commits `6a9aa42` (red), `e90989a` (enforce), `7ed85d5` (fixture fidelity fields).
- **Campaign completion (2026-08-29):** the R-069 operator, invoked one position at a time under human supervision, carried the campaign from position 1 through position 720. Nine retained INVALID attempts occurred, each cleared by a same-seed/cell fresh-run-ID retry per the frozen design; they span 5 distinct `failed_phase` values (`CFS_READINESS` ×3, `MEASUREMENT_BINDING` ×2, `NOMINAL_RUNTIME_COMPLETION` ×2, `RUNTIME_HEALTH` ×1, `FROZEN_ANALYSIS_HORIZON` ×1). One additional interrupted mid-harness-preflight attempt at position 660 was never ledgered; it was quarantined intact to `results/wp9/campaign/_quarantined-unledgered/` rather than deleted or fabricated into a ledger entry, and position 660 was then re-derived and executed cleanly. Full per-attempt table and taxonomy: `docs/26-wp9-r069-campaign-closeout.md`.

## Final campaign progress

**Campaign complete: 720/720 valid positions retained as of 2026-08-29. Cryptographic integrity freeze complete and PASS.**

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

See `docs/26-wp9-r069-campaign-closeout.md` for the authoritative incident account. The nine ledgered INVALID attempts are classified by `failed_phase` as `CFS_READINESS` ×3 (positions 120, 594, 627), `MEASUREMENT_BINDING` ×2 (positions 2, 11), `NOMINAL_RUNTIME_COMPLETION` ×2 (positions 407, 582), `RUNTIME_HEALTH` ×1 (position 404), and `FROZEN_ANALYSIS_HORIZON` ×1 (position 353). Position 582 was independently confirmed as a Docker-container termination; position 407's proximate cause is not generalized beyond its retained `NOMINAL_RUNTIME_COMPLETION` phase without separate stderr review. Three additional pre-flight blocks produced no ledger entry, and the interrupted position-660 attempt was quarantined unledgered and later re-derived cleanly.

## Campaign ledger / final state

Durable scientific state, independently verified against `results/wp9/campaign/attempt-history.json` and the completed integrity freeze on 2026-08-29:

- valid frozen positions: `720` of `720` — **campaign target met**
- retained scientific INVALID attempts: `9`
- authoritative ledger records: `729`
- quarantined never-ledgered attempts: `1` (position 660 interrupted attempt)
- campaign seeds `10001`–`10030`: all 30 represented, contiguous, no gaps
- all 24 frozen cells (A01–A24): exactly 30 valid repetitions each
- unique valid `(seed, cell)` pairs: `720`, zero duplicates, zero gaps
- consumed ledgered attempts: `726` = 720 VALID + 6 post-readiness INVALID
- `CFS_READINESS` INVALID attempts without seed consumption: `3`
- complete local campaign-tree files: `17182`, zero unclassified
- deterministic campaign-tree SHA-256: `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`
- authoritative ledger SHA-256: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- 720-valid analysis-membership SHA-256: `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The local `results/wp9/campaign/attempt-history.json` remains the execution authority. `docs/27-wp9-cryptographic-integrity-freeze.md` records the durable cryptographic identities and scope partitions without replacing the raw evidence.

## Next exact action

**No further WP9 `run-once` invocations are expected or authorized by this tracker.** WP9 campaign execution and the read-only cryptographic integrity freeze are complete.

No further WP9 campaign runtime or WP10 scientific analysis is required for this phase. WP10 is scientifically closed and WP11 responsible release preparation is complete. The next actions are journal-specific submission preparation and, under separate explicit authorization, Zenodo metadata/license review, authenticated upload, checksum verification, publication, DOI capture, and the corresponding Data Availability update.

In parallel as a publication-governance task, Zenodo is selected as the primary archive target for the frozen data/integrity bundle. The deposit and DOI remain pending package-size/limit verification and post-upload checksum verification; see `docs/27-wp9-cryptographic-integrity-freeze.md`.

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
| WP9 | Frozen experiment campaign | **Complete — 720/720 valid; cryptographic freeze PASS** | `docs/26-wp9-r069-campaign-closeout.md`; `docs/27-wp9-cryptographic-integrity-freeze.md` |
| WP10 | Analysis and manuscript | **Complete — target-neutral manuscript assembled and audited** | `docs/28-wp10-integrated-findings-freeze.md` through `docs/37-wp10-g7-presubmission-quality-audit.md`; scientifically closed pending journal-specific formatting/submission metadata and final archive DOI |
| WP11 | Responsible artifact release | **Complete — responsible release preparation; archive publication pending** | `docs/39-wp11-release-preparation-closeout.md`; exact six-object candidate generated and audited PASS; rights/privacy/misuse decision `PUBLIC_FILES` / `APPROVED_FOR_PUBLICATION`; Zenodo upload/publication/DOI remain separate pending external actions |

## Remaining research path

1. ~~Complete WP9 frozen campaign to 720 valid positions using R-069 one position per invocation.~~ **Done 2026-08-29.**
2. ~~Perform the read-only campaign integrity freeze: ledger/run-ID reconciliation, seed/cell continuity, INVALID classification, seed-consumption boundary, non-ledgered evidence separation, complete-tree checksums, and source immutability verification.~~ **Done 2026-08-29 — PASS.** See `docs/27-wp9-cryptographic-integrity-freeze.md`.
3. **Current:** complete WP10 statistical analysis using only the frozen 720-valid membership and predeclared metrics; retain unexpected valid science.
4. Final-review WP1–WP3 against the empirical findings and current publication literature.
5. Draft and revise the journal manuscript from the locked evidence, including appropriate methods/limitations treatment of the 9 INVALID attempts and quarantined position-660 evidence without including them in the 720-valid analysis population.
6. Deposit the frozen publication dataset/integrity bundle to Zenodo, verify post-upload checksums, capture DOI(s), and update the Data Availability statement.
7. Complete WP11 sanitized reproducibility/artifact release and submission package.

## Scientific and claim boundaries

Preserve throughout analysis and publication:

- controlled NOS3 software-in-the-loop only;
- no real spacecraft access;
- no RF interference/transmission claim;
- no native spacecraft safe-mode claim;
- no real ground-contact timing claim;
- no real human-operator timing claim;
- C1 timing is synthetic/modelled only;
- immutable ground truth never acts as a policy oracle;
- expectations are acceptance-only and are not metric inputs;
- trial-validity gate failures are classified by retained evidence rather than blanket-labelled as treatment-fidelity failures;
- unexpected treatment-valid outcomes are retained;
- trusted recovery is reported only when all applicable/current terminal evidence supports it;
- A16/A17 remain P6-initiated trials with recorded P5 delegation after synthetic ground authorization; do not collapse them into P5-only recovery;
- one runtime trial per invocation;
- no automatic retry and no automatic next-case execution.
