# Research Tracker

Last updated: 2026-08-22

## Current focus

**WP9 campaign-safe runtime route adapters — E1/A01–A09 command route**

WP9-A through WP9-C and the pre-campaign timing/seed freezes are closed. R-051 freezes 30 valid repetitions per cell / 720 total valid executions. R-052 freezes the modeled C1 one-missed-contact window at 10 seconds and the E3 post-event analysis horizon at 30 seconds. R-053 freezes 30 campaign seed blocks (`10001`–`10030`) and a deterministic SHA-256-derived A01–A24 execution order per seed; invalid attempts retain the same seed/cell with a new run ID, with no automatic retry or automatic next case. R-054 adds a fail-closed one-trial controller and passed exact-SHA GitHub Actions run `32590641756`. R-055 freezes a common 30-second post-event analysis/right-censoring horizon across E1–E4 and passed exact-SHA GitHub Actions run `32591203615`. R-056 closes campaign-safe A19–A21/E2 observation binding and passed exact-SHA GitHub Actions run `32591739213`. R-057 closes bounded E2 single-trial route validation: implementation CI `32592274322`; cleanup-only first V01 attempt retained invalid; cleanup ownership fix passed CI `32593243192`; valid V01 replacement (A19/P0), V02 (A20/P1), and V03 (A21/P7→P1) all passed treatment fidelity, 30-second observation, legitimate-command probe, and residue checks. R-058 closes campaign-safe A22–A24/E4 observation binding at commit `70f728290c14788c31071b52875b5030d6ea4237`: 12/12 dedicated tests, full 399-test suite, expected A24 P7→P4 binding, deliberately unexpected A22 legitimate-service loss retained as scientific observation, explicit execution rejection, zero campaign files, and exact-SHA GitHub Actions run `32597726630`. R-059 closes bounded E4 single-trial route validation: implementation `76a61e11d46897edbfee0e730d904be12f111627` passed 12/12 dedicated tests, full 411-test suite, and exact-SHA CI `32599292779`; W01/A22/P0→P0 seed 9911, W02/A23/P4→P4 seed 9912, and W03/A24/P7→P4 seed 9913 each produced valid retained development-runtime evidence with treatment fidelity, full 30-second observation, post-response authorized-NOOP measurement, and residue-free cleanup. W03 specifically confirmed P7→P4 selection without immutable-ground-truth oracle use. No campaign seed has been consumed and no campaign data has been generated. Next: build the campaign-safe E1/A01–A09 observation/runtime route using the already validated command mechanisms, then E3/A10–A18 and the separate final-campaign authorization gate.

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
| WP9 | Frozen experiment campaign | **Campaign-safe route adapter validation pending** | R-057 E2 and R-059 E4 route families closed; R-059 implementation CI `32599292779`, 3/3 valid E4 development routes, zero campaign seeds/data; 24×30=720 planned valid executions; next: E1/A01–A09 campaign-safe observation/runtime route, then E3/A10–A18 and separate final-campaign authorization |
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
