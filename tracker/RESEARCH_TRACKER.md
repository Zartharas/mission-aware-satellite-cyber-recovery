# Research Tracker

Last updated: 2026-08-22

## Current focus

**WP9 final pre-campaign readiness / authorization gate**

WP9-A through WP9-C and the pre-campaign timing freeze are closed. R-051 freezes 30 valid repetitions per cell / 720 total valid executions. R-052 freezes the modeled C1 one-missed-contact window at 10 seconds and the common E3 post-event analysis horizon at 30 seconds, with early absorbing trusted recovery permitted and unrecovered E3 runs right-censored at the horizon. R-052 passed its reviewed-result SHA-256 check, 12/12 focused WP9-C/R-052 tests, the full 357-test research suite, and exact-SHA GitHub Actions run `32589978843` at commit `f653befad221834c4b29b39c95be63272461d1a9`. No campaign seed has been consumed and no campaign data has been generated. The next gate is a static final pre-campaign readiness audit that must verify the frozen 24-cell design, 30 repetitions per cell, timing contract, campaign seed plan, runtime-family coverage, analysis/schema boundaries, and isolation/cleanup prerequisites. Final-campaign execution remains unauthorized until separately and explicitly authorized.

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
| WP9 | Frozen experiment campaign | **Final pre-campaign readiness audit pending** | WP9-A design, WP9-B runtime/readiness, WP9-C repetition selection, and R-052 timing freeze are closed; 24 cells × 30 valid repetitions = 720 planned valid executions; C1=10 s; common E3 post-event horizon=30 s; next: static final readiness/authorization gate; final campaign remains unauthorized |
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
