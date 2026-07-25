# Research Tracker

Last updated: 2026-07-24

## Status legend

- Not started
- In progress
- Blocked
- Ready for review
- Complete

## Work packages

| ID | Work package | Status | Current output | Next acceptance gate |
|---|---|---|---|---|
| WP0 | Research governance and workspace | Complete | Private GitHub repository, initial commit, data and legal controls | Maintain clean synchronized repository |
| WP1 | Literature and novelty validation | Ready for review | Two gap reviews, reviewer challenge, final novelty statement, and 30-source matrix | Citation/metadata audit and approval of final gap statement |
| WP2 | Theoretical and conceptual model | In progress | Mission Aware + FDIR + cyber-resilience/RMF/SPARTA structure; contribution boundaries frozen | Final construct definitions and proposition-to-metric traceability |
| WP3 | Threat and mission model | In progress | Mission objectives, unacceptable losses, safety/trust invariants, trusted-recovery terminal states, pilot boundary | Independent red-team review and machine-readable specification |
| WP4 | Testbed selection and architecture | Not started | Candidate NOS3/cFS design | Nominal commands, telemetry, mission states reproducible |
| WP5 | Event-injection library | Not started | — | Each event deterministic and contained |
| WP6 | Response-policy implementation | Not started | — | Baseline policies pass unit and integration tests |
| WP7 | Trusted-recovery implementation | Not started | — | Recovery evidence checklist verified |
| WP8 | Pilot experiment | Not started | — | Variability and final design established |
| WP9 | Final experiment | Not started | — | Pre-registered campaign completed |
| WP10 | Analysis and manuscript | Not started | — | Reproducible tables, figures, and paper draft |
| WP11 | Artifact and responsible release | Not started | — | License, secrets, misuse, and reproducibility review passed |

## Completed setup and WP1 tasks

- [x] Create private GitHub repository
- [x] Push initial scaffold
- [x] Create research, legal, data, risk, and decision records
- [x] Complete first focused novelty review
- [x] Expand literature matrix from 12 to 22 sources
- [x] Flag CuCD-ID license discrepancy and place it on conditional hold
- [x] Expand literature matrix to 30 sources
- [x] Search adjacent cyber-physical attack-recovery and spacecraft fault-management literature
- [x] Conduct reviewer-style challenge of the novelty claim
- [x] Produce final defensible gap and falsification criteria
- [x] Finalize initial mission objectives and unacceptable losses
- [x] Freeze safety/trust invariants and trusted-recovery criteria
- [x] Freeze the minimum viable pilot boundary

## Immediate tasks

- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Verify Mac architecture and available virtualization
- [ ] Pin cFS and NOS3 candidate versions
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Build proposition-to-variable-to-metric traceability table
- [ ] Convert mission states, events, policies, invariants, and terminal states into machine-readable schemas
- [ ] Conduct independent red-team review of the threat and mission model
- [ ] Draft laboratory Rules of Engagement
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Final candidate novelty statement

This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Gate 1 decision

Proceed to WP2/WP3 refinement. WP4 implementation remains blocked until the citation audit, traceability model, and machine-readable mission/threat specification are complete.