# WP10 Analysis Artifact Register

**Register date:** 2026-08-29  
**Status:** Active — authoritative analysis outputs identified for manuscript integration  
**Scope:** Repository-facing identities for local WP10 analysis products; no raw campaign result files are added to Git.

## Frozen source inputs

- WP9 authoritative ledger SHA-256: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- WP9 720-valid analysis-membership SHA-256: `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`
- locked WP10 analysis extraction SHA-256: `bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265`
- frozen campaign design: `docs/18-wp9a-final-campaign-design.md`
- WP9 integrity/provenance authority: `docs/27-wp9-cryptographic-integrity-freeze.md`

## WP10 stage register

| Stage | Purpose | Authoritative status | Key identity / note |
|---|---|---|---|
| WP10-A | Schema audit and locked 720-row extraction | PASS | locked extraction SHA-256 `bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265` |
| WP10-B | Endpoint/model diagnostics and fallback routing | PASS | established exact/descriptive/RMST/mixed-model applicability before inference |
| WP10-C1 | Primary P1/P2/P3 analysis | PASS | P1 null on predeclared primary outcomes; P2 timing effects; P3 evidence-dependent recovery result |
| WP10-C2 | M07 divergence analysis | PASS | P2 and P3 divergence sensitivities retained without replacing primary proposition endpoints |
| WP10-D1 | P4 semantic/provenance audit | PASS | actual effective-policy and selected-action pathways bound; no correctness oracle manufactured |
| WP10-D2 attempt 1 | Initial P4 provenance binding | ABORTED_PRE_ANALYSIS | provenance search was too narrow; no scientific P4 result produced |
| WP10-D2-R1 | Final P4 analysis | PASS / AUTHORITATIVE | output-manifest SHA-256 `b3239968b596edf1183f4ad6b93a34cf317a794ab86920a775d1e1e9045ad9ff`; locked P4 table SHA-256 `f848a448cc75818d37a7827df9e8936ff7a4bf60075ca25b102e858df7f56af3` |
| WP10-E0 attempt 1 | Execution-provenance equivalence audit | ABORTED_PRE_CLASSIFICATION | shell `PATH` variable collision; no scientific verdict produced |
| WP10-E0-R1 | Execution-provenance equivalence audit | PASS after manual classification | manifest SHA-256 `3c4b141352c8ce9f2341cbc3acb2b6f5f0e7f97847fcc19f258ba1c2dc90eeb4`; final verdict: analytically exchangeable with versioned runtime-orchestration/finalization provenance |
| WP10-F attempt 1 | P5 Pareto analysis | ABORTED_PRE_ANALYSIS | wrong-repository / shell guard failure; no P5 result |
| WP10-F-R1 | P5 Pareto analysis | ABORTED_DURING_ANALYSIS_CONTRACT_CHECK | M05 analysis-time column was incorrectly treated as an event indicator; no authoritative P5 result |
| WP10-F-R2 | P5 Pareto analysis | ABORTED_PRE_PARETO_ESTIMATION | M01 `true`/`false` strings were parsed with `int()`; latent commit-B variable shadowing also identified |
| WP10-F-R3 | Final P5 Pareto analysis | PASS / AUTHORITATIVE | output-manifest SHA-256 `c31b357cb454ed96d60708f96b27e1993ef002b76a3cd36d90d36a437b3cbc9c` |

## Authoritative M05 survival binding

The locked extraction contains the explicit pair:

- event indicator: `M05_verified_recovery_event`
- analysis time: `M05_verified_recovery_analysis_time_s`

Counts:

- observed trusted-recovery events: `180`
- administratively right-censored observations: `540`
- censoring horizon: `30 s`
- all 540 censored observations have analysis time exactly `30 s`
- all 180 observed events occur before `30 s`

The analysis must not infer event status from nonblank time values; the event column is authoritative.

## Execution-provenance equivalence record

The 720 VALID observations were generated under three repository commits:

- `aae2239753119c92e7633db3b6c73aee94c7b6dd`: 1 VALID
- `97074d0cdc4261de02bc6f618e891a88f45f9cfc`: 9 VALID
- `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`: 710 VALID

The E0 review found no changes across these commits to the frozen scientific core, event simulation, treatment/policy selection, timing horizon, primary metric generation, or frozen configuration. The actual `shim_plan` AST SHA-256 is identical across A/B/C:

`d933c537d745ab0554f46b326602f29f8877e1f8381bd60c28bfd04aed953749`

Changes were classified as runtime orchestration, finalization compatibility, fidelity/consumer validation, and INVALID-result evidence handling. Therefore no VALID observation is excluded because of execution commit.

## P5 provenance sensitivity

The final-commit sensitivity uses complete seed blocks `10002`–`10030`:

- seeds: `29`
- observations: `696`
- execution commit: `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`
- P7 Pareto-front membership/non-membership classification stable across all 9 groups
- pairwise Pareto relations stable across all 9 groups
- primary-metric directions stable across all 9 groups

This sensitivity is supportive only. The primary analysis remains all 720 frozen VALID observations.

## Local-output handling

WP10 analysis directories are retained outside the tracked raw-results boundary. Repository documentation records the identities necessary for review, while the raw campaign tree and local analysis outputs are not silently promoted into Git.

WP11 will determine which sanitized analysis tables, scripts, manifests, or archives are appropriate for the public reproducibility release and Zenodo deposit.

## Post-Zenodo, pre-journal-submission executable reconstruction

The local-output handling above describes the historical WP10 analysis state at the time of the original analysis. After the campaign and Zenodo v1.0.0 publication, the preserved WP10 output directories were recovered from the private preservation archive and re-verified. No original executable analysis-source candidates were present.

A separate reconstruction, prepared after campaign/Zenodo v1.0.0 publication and before journal submission, is now tracked under `analysis/`. It starts from the frozen 720-row derived extraction plus the retained P4 selection/provenance binding, and regression-validates the manuscript-facing statistical contracts against preserved authoritative WP10 outputs. It must not be cited or described as recovered original WP10 source. Zenodo v1.0.0 remains unchanged.
