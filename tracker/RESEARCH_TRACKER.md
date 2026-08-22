# Research Tracker

Last updated: 2026-08-22

## Current focus

**WP9 pre-campaign timing freeze — final C1 modeled contact-window duration**

WP9-C is closed. R-050 identified 30 valid repetitions per cell as the smallest candidate satisfying the frozen empirical-precision, conservative-sensitivity, and model-stability gates; R-051 reviewed and froze that result at 30 repetitions per cell / 720 total valid executions. The R-051 freeze contract, 11/11 dedicated WP9-C tests, full 356-test research suite, exact selection-result SHA-256 `027a83947537ddcaa9b6700cb543e4749b079502dcedc2290d86e9ea75b1bbb1`, and GitHub Actions run `32585590793` all passed at commit `56b05e4a7fecbf246e20222348ab42919e7903b4`. No campaign seed has been consumed and no campaign data has been generated. Final-campaign execution remains unauthorized. The remaining pre-campaign design blocker is the final duration of the modeled C1 one-missed-contact window; the 2-second R-047 value was development-only and must not be inherited silently. The next gate is a read-only timing audit of retained WP8 recovery evidence followed by an explicit timing freeze.

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
| WP9 | Frozen experiment campaign | **Pre-campaign timing parameter closure in progress** | WP9-A design, WP9-B runtime/readiness, and WP9-C repetition selection are closed; R-051 freezes 30 valid repetitions/cell (720 total). Next: freeze the final modeled C1 contact-window duration from retained timing evidence; final campaign remains unauthorized |
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
