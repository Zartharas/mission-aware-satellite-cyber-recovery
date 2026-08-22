# Research Tracker

Last updated: 2026-08-22

## Current focus

**WP9 campaign-safe runtime route adapters — R-059 E4 bounded route validation**

WP9-A through WP9-C and the pre-campaign timing/seed freezes are closed. R-051 freezes 30 valid repetitions per cell / 720 total valid executions. R-052 freezes the modeled C1 one-missed-contact window at 10 seconds and the E3 post-event analysis horizon at 30 seconds. R-053 freezes 30 campaign seed blocks (`10001`–`10030`) and a deterministic SHA-256-derived A01–A24 execution order per seed; invalid attempts retain the same seed/cell with a new run ID, with no automatic retry or automatic next case. R-054 adds a fail-closed one-trial controller and passed exact-SHA GitHub Actions run `32590641756`. R-055 freezes a common 30-second post-event analysis/right-censoring horizon across E1–E4 and passed exact-SHA GitHub Actions run `32591203615`. R-056 closes campaign-safe A19–A21/E2 observation binding and passed exact-SHA GitHub Actions run `32591739213`. R-057 closes bounded E2 single-trial route validation: implementation CI `32592274322`; cleanup-only first V01 attempt retained invalid; cleanup ownership fix passed CI `32593243192`; valid V01 replacement (A19/P0), V02 (A20/P1), and V03 (A21/P7→P1) all passed treatment fidelity, 30-second observation, legitimate-command probe, and residue checks. R-058 closes campaign-safe A22–A24/E4 observation binding at commit `70f728290c14788c31071b52875b5030d6ea4237`: 12/12 dedicated tests, full 399-test suite, expected A24 P7→P4 binding, deliberately unexpected A22 legitimate-service loss retained as scientific observation, explicit execution rejection, zero campaign files, and exact-SHA GitHub Actions run `32597726630`. R-059 now provides a bounded development-only E4 single-trial route adapter for W01/A22 seed 9911, W02/A23 seed 9912, and W03/A24 seed 9913. R-059 static/local validation is the active gate; no R-059 runtime has been authorized or executed yet. No campaign seed has been consumed and no campaign data has been generated.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Gap: comparative mission-aware response and evidence-based trusted recovery |
| WP2 | Theoretical model | Ready for final review | Mission Aware + FDIR + cyber-resilience framing |
| WP3 | Threat and mission model | Ready for final review | Mission states, invariants, trust boundaries, evidence separation |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and bounded runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1-E4 deterministic event adapters validated against the accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Deterministic fixed-policy/P7 mechanisms validated for WP8 scope; bounded P6 extension subsequently passed WP9-B2 development-runtime validation |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery plus four bounded failure-mode validations passed; reproducibility harness retained |
| WP8 | Pilot | **Complete** | Read-only closeout passed: 12 Stage-1 valid cells + 28 Stage-2 valid repetitions = 40 valid pilot executions; one Stage-1 invalid attempt retained/excluded; 41 frozen archives verified; see `docs/17-wp8-pilot-closeout.md` |
| WP9 | Frozen experiment campaign | **Campaign-safe route adapter validation pending** | R-057 E2 route closed; R-058 E4 observation binding closed with CI 32597726630; R-059 E4 development-only route adapter implemented for A22–A24 with seeds 9911–9913; 24×30=720 planned valid executions; zero campaign seeds/data; next: static/exact-SHA R-059 validation, then W01 only |
| WP10 | Analysis and manuscript | Not started | Statistical analysis, figures, limitations, journal submission |
| WP11 | Responsible artifact release | Not started | Sanitized code/data/reproducibility release |

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
