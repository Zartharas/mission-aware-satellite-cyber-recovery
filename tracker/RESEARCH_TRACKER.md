# Research Tracker

Last updated: 2026-08-22

## Current focus

**WP9 campaign-safe runtime route adapters — E4 observability route**

WP9-A through WP9-C and the pre-campaign timing/seed freezes are closed. R-051 freezes 30 valid repetitions per cell / 720 total valid executions. R-052 freezes the modeled C1 one-missed-contact window at 10 seconds and the E3 post-event analysis horizon at 30 seconds. R-053 freezes 30 campaign seed blocks (`10001`–`10030`) and a deterministic SHA-256-derived A01–A24 execution order per seed; invalid attempts retain the same seed/cell with a new run ID, with no automatic retry or automatic next case. R-054 adds a fail-closed one-trial controller and passed 8/8 dedicated tests, the full 366-test research suite, explicit execution rejection, and exact-SHA GitHub Actions run `32590641756` at commit `efbcc1baf9e468e59619cebffb35414e9033c148`. R-055 freezes a common 30-second post-event analysis/right-censoring horizon across E1–E4 and passed exact-SHA GitHub Actions run `32591203615` at commit `fd0be827728658e420dff97e416d7b43dac5b16d`. R-056 closes campaign-safe A19–A21/E2 observation binding and passed 10/10 dedicated tests, the full 377-test suite, unexpected-outcome retention proof, zero campaign files, explicit execution rejection, and exact-SHA GitHub Actions run `32591739213` at commit `cada349897a595ef0effac5d275ef417433620f8`. R-057 closes bounded E2 single-trial route validation: implementation CI `32592274322`; cleanup-only first V01 attempt retained invalid; cleanup ownership fix passed 10/10 focused tests, full 387-test suite, and CI `32593243192` at commit `42efa37efb66b9d3fdc5be84aa7bd3f795982a69`; valid V01 replacement (A19/P0), V02 (A20/P1), and V03 (A21/P7→P1) all passed treatment fidelity, 30-second observation, legitimate-command probe, and residue checks. No campaign seed has been consumed and no campaign data has been generated. The next smallest remaining route family is E4/A22–A24, covering fixed P0/P4 and adaptive P7→P4 observability-degradation behavior.

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
| WP9 | Frozen experiment campaign | **Campaign-safe route adapter validation pending** | WP9-A/B/C plus R-052–R-056 closed; R-057 E2/A19–A21 route validation closed with 3 valid development routes + 1 retained cleanup-invalid attempt; 24×30=720 planned valid executions; zero campaign seeds/data; next: E4/A22–A24 campaign-safe observation/runtime route, then E1/E3 families and separate explicit authorization gate |
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
