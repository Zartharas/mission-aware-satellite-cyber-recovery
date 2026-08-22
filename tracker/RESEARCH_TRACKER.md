# Research Tracker

Last updated: 2026-08-21

## Current focus

**WP9-B2 — bounded development runtime validation**

Current gate: R-045/WP9-B1 is closed on exact implementation commit `617279212aea5edd89e63b6f382633325c06d699`: 11/11 WP9 static tests passed, the WP8 regression/schema validator passed, the full 296-test research suite passed, and GitHub Actions run `32549670609` completed successfully on that exact SHA. The additive WP9 model/schema/contracts represent P6 and the E2 protected-state replay-effect measurement while leaving WP8 artifacts unchanged. WP9-B2 must now execute only the bounded development-runtime discriminators required by `configs/wp9b_static_contract.json`; final-campaign seeds, final-campaign data, repetition-count freeze, and final-campaign execution remain blocked.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Gap: comparative mission-aware response and evidence-based trusted recovery |
| WP2 | Theoretical model | Ready for final review | Mission Aware + FDIR + cyber-resilience framing |
| WP3 | Threat and mission model | Ready for final review | Mission states, invariants, trust boundaries, evidence separation |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and bounded runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1-E4 deterministic event adapters validated against the accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Deterministic fixed-policy and P7 mechanisms validated for the WP8 scope; WP9-B1 now statically represents the bounded P6 extension, with runtime validation remaining a WP9-B2 gate |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery plus four bounded failure-mode validations passed; reproducibility harness retained |
| WP8 | Pilot | **Complete** | Read-only closeout passed: 12 Stage-1 valid cells + 28 Stage-2 valid repetitions = 40 valid pilot executions; one Stage-1 invalid attempt retained/excluded; 41 frozen archives verified; see `docs/17-wp8-pilot-closeout.md` |
| WP9 | Frozen experiment campaign | **Pre-campaign runtime validation in progress** | WP9-A/R-044 froze the 24-cell design; WP9-B1/R-045 static mechanisms passed exact-SHA local/CI validation; next execute bounded WP9-B2 development-runtime discriminators, then WP9-B3 readiness audit and WP9-C repetition selection; final campaign remains unauthorized |
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
