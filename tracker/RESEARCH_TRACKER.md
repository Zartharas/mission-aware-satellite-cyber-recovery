# Research Tracker

Last updated: 2026-08-21

## Current focus

**WP9-B — final-campaign runtime readiness**

Current gate: R-044/WP9-A froze a 24-cell estimand-driven final-campaign matrix and endpoint/model applicability contract in `configs/wp9_campaign_design.json`. Campaign execution and repetition-count freeze remain blocked. WP9-B must perform development-only runtime validation for the required P6 ground-authorization policy extension, E2 replay policy binding, new E3 T0/T1 fixed-policy cells, E4 fixed/sentinel cells, and all A01-A24 factor/runtime mappings without consuming final-campaign seeds or generating final-campaign data. After WP9-B passes, WP9-C will apply the predeclared repetition-selection rule to `12, 16, 20, 24, 30` valid repetitions per cell.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Gap: comparative mission-aware response and evidence-based trusted recovery |
| WP2 | Theoretical model | Ready for final review | Mission Aware + FDIR + cyber-resilience framing |
| WP3 | Threat and mission model | Ready for final review | Mission states, invariants, trust boundaries, evidence separation |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and bounded runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1-E4 deterministic event adapters validated against the accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Deterministic fixed-policy and P7 mechanisms validated for the WP8 scope; WP9-B contains one explicitly bounded P6 extension required by R-044 |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery plus four bounded failure-mode validations passed; reproducibility harness retained |
| WP8 | Pilot | **Complete** | Read-only closeout passed: 12 Stage-1 valid cells + 28 Stage-2 valid repetitions = 40 valid pilot executions; one Stage-1 invalid attempt retained/excluded; 41 frozen archives verified; see `docs/17-wp8-pilot-closeout.md` |
| WP9 | Frozen experiment campaign | **Pre-campaign runtime validation in progress** | WP9-A/R-044 froze 24 cells and endpoint/model rules; execute WP9-B development-only runtime support checks before WP9-C repetition selection; final campaign remains unauthorized |
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
