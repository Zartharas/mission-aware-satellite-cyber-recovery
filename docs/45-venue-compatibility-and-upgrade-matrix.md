# Venue Compatibility and Research-Upgrade Matrix

## Status

`HISTORICAL_2026-09-04_PRE_SUBMISSION_VENUE_MATRIX__PAPER1_NOW_SUBMITTED_TO_JAIS`

This document preserves the venue-comparison logic used before Paper 1 was submitted. It is no longer the live Paper-1 venue-selection authority.

For the current publication state, use:

- `docs/CURRENT_PUBLICATION_STATE.md`
- `docs/PUBLICATION_PHASE_MAP.md`
- `publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

## Current Paper-1 outcome

The two-study article was ultimately submitted to the **AIAA Journal of Aerospace Information Systems (JAIS)** rather than Computers & Security.

- title: **Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints**
- manuscript type: Full Paper
- manuscript ID: `2026-09-I012066`
- submission date: `2026-09-05`
- current state: editorial/peer-review workflow pending

The exact submitted publisher-facing package is frozen under:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

No submitted Paper-1 file should change unless JAIS explicitly requests a revision.

## Frozen scientific basis

Paper 1 combines two scientifically separate empirical studies without pooling their statistical populations:

- **Study 1:** 720 VALID observations across 24 frozen cells; 9 retained INVALID attempts outside statistical membership.
- **Study 2:** 3,872 VALID observations across 85 frozen cells; 0 INVALID attempts; 162 primary paired contrasts; 432 prespecified secondary contrasts; independent reproduction with 0 mismatches.

Study-1 science and Zenodo v1.0.0 remain unchanged. Study-2 is a separately frozen extension with adversarial evidence mechanisms, broader contact regimes, context ablations, and bounded adversary-budget stress.

Study-2 public archive:

- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- public ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- public-byte verification: PASS

## Historical pre-submission venue assessment

### Computers & Security

Computers & Security was initially assessed as a strong applied-cybersecurity fit because the manuscript centered on authorization/contact-dependent response and recovery, evidence sufficiency/integrity, bounded producer compromise, mission/command-availability tradeoffs, and trusted-recovery qualification.

That assessment is historical. The journal was not the final submitted Paper-1 venue.

### AIAA Journal of Aerospace Information Systems

JAIS was identified as a strong aerospace-computing/information-systems fit, particularly for contact-constrained response/recovery, mission assurance, deterministic state-machine logic, reproducibility, and assurance traceability.

JAIS became the final submitted venue.

### IEEE Transactions on Aerospace and Electronic Systems

TAES was considered plausible but better suited to a future separately frozen study with stronger orbital/access, resource/performance, or HIL evidence. Those additions were not required for the submitted Paper-1 claims and were not retrofitted into the frozen populations.

### IEEE TDSC / ACM TOPS

These were retained as higher-bar security-methodology alternatives. No venue change was used to trigger new observations, endpoint weighting, or global policy ranking.

## Reviewer-sensitive boundaries retained in the submitted Paper 1

- Block-C BENIGN/ADVERSARIAL results are structural label-invariance/control evidence only.
- K4 is intermittent/flapping contact, not ordinal severity 4.
- A2/K2 is a coupled producer-compromise/contact-loss profile.
- logical SIL seconds are modeled time, not real spacecraft/network/ground/operator latency.
- secondary n=32 blocks are sensitivity/estimation evidence rather than small-effect confirmatory evidence.
- no weighted global policy score or global policy rank is supported.
- no operational spacecraft, RF, flightworthiness, or certification claim is supported.

## Capability matrix retained as historical planning provenance

| Research capability | Computers & Security | JAIS | TAES | TDSC / TOPS |
|---|---:|---:|---:|---:|
| Study-1 720-run controlled SIL comparison | Core | Core | Foundation | Foundation |
| Study-2 3,872-run adversarial-evidence extension | Core | Strong | Strong | Core |
| Explicit trust/adversary boundary | Core | Strong | Strong | Core |
| Multiple evidence-failure mechanisms | Core | Strong | Strong | Core |
| Multiple modeled contact regimes | Core | Core | Core | Strong |
| Context ablations | Strong | Strong | Useful | Core |
| Independent statistical reproduction | Core | Strong | Strong | Core |
| Formal assurance/model checking | Strong | Strong | Strong | Core differentiator |
| Orbital/access realism | Not required for submitted claims | Useful | Core for stronger future version | Useful |
| Flight-like resource measurements | Not required | Useful | Core for stronger future version | Limited/useful |
| RF-free HIL subset | Future validation only | Strong future value | Strong future value | Optional |

## Current publication-program rule

Do not expand either frozen study merely to increase sample size or improve publication optics.

- Study 1 remains exactly 720 VALID observations.
- Study 2 remains exactly 3,872 VALID observations.
- Any later orbital/HIL/operator validation requires a separate frozen protocol, evidence identity, analysis plan, and archive.
- Paper 1 is already submitted to JAIS as `2026-09-I012066`.
- The next new publication-development priority is the Studies 3 + 4 + 6 synthesis, not a retrospective Paper-1 venue change.

## Historical decision rule

The original pre-submission decision rule was superseded by the successful JAIS submission. It is preserved only in Git history and earlier preparation records. Future venue decisions must use fresh live scope/policy checks for the specific unsent manuscript under consideration.
