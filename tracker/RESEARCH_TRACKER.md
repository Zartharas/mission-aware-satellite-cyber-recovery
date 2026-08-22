# Research Tracker

Last updated: 2026-08-21

## Current focus

**WP9 — repetition-count selection / pre-campaign design**

Current gate: WP8 pilot closeout passed with 12/12 valid Stage-1 cells, 28/28 valid Stage-2 repetitions, 40 scientifically valid pilot executions total, one transparently retained/excluded Stage-1 `RUN_INVALID` attempt, and 41 frozen attempt archives independently verified. Execute the predeclared bootstrap/precision/model-stability rule to select the smallest defensible WP9 repetition count from `12, 16, 20, 24, 30`. No WP9 final-campaign execution is authorized yet.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Gap: comparative mission-aware response and evidence-based trusted recovery |
| WP2 | Theoretical model | Ready for final review | Mission Aware + FDIR + cyber-resilience framing |
| WP3 | Threat and mission model | Ready for final review | Mission states, invariants, trust boundaries, evidence separation |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and bounded runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1-E4 deterministic event adapters validated against the accepted NOS3 runtime |
| WP6 | Response-policy implementation | **Complete** | Fixed-policy effects plus corrected P7 mission-aware integration validated with functional Sample readiness and observed cFS-marker deltas; trusted-recovery execution remains WP7 |
| WP7 | Trusted-recovery implementation | **Complete** | Hardened E3/P5 trusted recovery plus four bounded failure-mode validations passed; reproducibility harness retained |
| WP8 | Pilot | **Complete** | Read-only closeout passed: 12 Stage-1 valid cells + 28 Stage-2 valid repetitions = 40 valid pilot executions; one Stage-1 invalid attempt retained/excluded; 41 frozen archives verified; see `docs/17-wp8-pilot-closeout.md` |
| WP9 | Frozen experiment campaign | **Pre-campaign design in progress** | Apply frozen repetition-selection rule to WP8 distributions; campaign execution remains blocked pending selected count, review, and explicit authorization |
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
