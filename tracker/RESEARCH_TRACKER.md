# Research Tracker

Last updated: 2026-08-14

## Current focus

**WP6 — response-policy implementation**

Implementation objective: make each retained response policy deterministic, testable, and separable from trusted-recovery verification; mission-aware decisions must use policy-visible evidence rather than immutable experiment ground truth.

## Work packages

| ID | Work package | Status | Evidence / next step |
|---|---|---|---|
| WP0 | Research workspace | Complete | Reproducibility and responsible-use structure |
| WP1 | Literature and novelty | Ready for final review | Gap: comparative mission-aware response and evidence-based trusted recovery |
| WP2 | Theoretical model | Ready for final review | Mission Aware + FDIR + cyber-resilience framing |
| WP3 | Threat and mission model | Ready for final review | Mission states, invariants, trust boundaries, evidence separation |
| WP4 | Testbed selection and architecture | **Complete** | Pinned NOS3/Fortytwo testbed and bounded runtime-preflight evidence |
| WP5 | Deterministic event library | **Complete** | E1-E4 deterministic event adapters validated against the accepted NOS3 runtime |
| WP6 | Response-policy implementation | **In progress** | P0/P1, P0/P2, P0/P4, and P0/P5 treatment effects validated; P7 mission-aware dispatch/effect integration next |
| WP7 | Trusted-recovery implementation | Not started | Independent recovery evidence and terminal-state verification |
| WP8 | Pilot | Not started | Nominal/control validity, variability, repetition count |
| WP9 | Frozen experiment campaign | Not started | Randomized controlled repeated trials |
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
