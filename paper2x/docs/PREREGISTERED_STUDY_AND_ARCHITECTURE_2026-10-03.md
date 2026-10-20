# Paper 2 P2X — Prospective NOS3/cFS recovery-gate study

**ID:** `P2X-NOS3-RG-001`  
**State:** `DESIGN_ONLY__AUTHOR_RUNTIME_AUTHORIZATION_REQUIRED`  
**Date:** 2026-10-03  
**Authority:** `main=4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4`; historic Paper-2 R4 and draft CEAS R2 are separate and unchanged.

## Why another experiment?

R4/R2 contains three finite core studies and two separately frozen supporting analyses. The external editorial challenge is not solved by repackaging the constructed S6X observation-vector equivalence or saying a hypothetical gate is a spacecraft architecture. A separate software-in-the-loop rehearsal should demonstrate (a) a genuinely connected cFS command-and-telemetry path, (b) an explicit independently specified behaviour requirement and hidden adjudicator, and (c) a quantified safety/benign-availability trade-off for an **additional gate-visible functional requirement**.

The scientific question is not whether an intentionally wrong artifact can be made wrong. It is whether an implementable, independently specified pre-admission functional-conformance check changes measured *unsafe command dispatch*, correct-case deferral and evidence-collection latency on fresh preregistered scenarios when compared with the six-process-signal gate. Equal-information decisions must be reconstructed from the same preregistered scenario trace and run after a clean reset.

## Why NOS3 instead of another toy model?

Existing repository scripts already register and pin a NASA NOS3 environment, source checkout `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`, OCI image `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`, and a cFS command/telemetry integration script. These **infrastructure tools** may be inspected and reused, but no prior Paper-1/P7 outcomes, Study-5 CuCD-ID data, Paper-3 7/7E, Paper-4 8/8E or Paper-5 Study-9 data/populations may enter P2X. NOS3 uses COSMOS and cFS's command-ingest and telemetry-output interfaces; its UDP channels are a software test interface, **not a real flight radio**.

Official sources:
- NASA NOS3 and purpose: https://github.com/nasa/nos3
- NOS3 ground software CI/TO and COSMOS channels: https://github.com/nasa/nos3/blob/main/docs/wiki/NOS3_Ground_Software.md
- cFS open-source bundle and lab caveats: https://github.com/nasa/cFS
- Limit Checker telemetry/watchpoint and RTS behaviour: https://github.com/nasa/LC
- CEAS cybersecurity for space systems remit: https://link.springer.com/journal/12567/aims-and-scope

## Rehearsal architecture (to be confirmed by Phase A packet traces)

1. A separate **scenario controller** stages correct or researcher-introduced faults in an isolated, pinned simulator/build and records independent state truth for adjudication. No live operational credentials, target or spacecraft used.
2. cFS/Limit Checker receives a controlled monitored variable and produces an actual event/telemetry response. The selected nominal test/recovery command is sent through the NOS3 simulated ground command interface only after an explicit gate decision.
3. The **evidence adapter** collects measured command/telemetry receipts and the six process/release signals from separately generated, frozen records. It must never see the scenario truth oracle.
4. Gate **G0** checks the six Study-6-style process signals; gate **G1** sees exactly the same evidence plus one separately generated, preregistered functional-conformance signal. Both gates are fixed prior to any primary result.
5. An out-of-band **truth assessor** checks the prepared scenario's expected requirement and actual cFS/simulator command outcome. It must not write any gate input. An independent second trace parser reconstructs packets and outcomes. Tests should freeze process/input-output contracts and hashes before faults are revealed to the gate evaluator.

A successful readiness gate requires a clean baseline packet trail demonstrating cFS command ingest, application-level response and ground telemetry receipt. Local policy decisions, a fabricated CSV, or replay of the old S6X equality fixture **alone do not qualify as integrated evidence**.

## Preregistered scenarios and controls

| ID | Scenario | Primary data? | Role |
|---|---|---|---|
| C0 | Valid approved artifact with normal telemetry/command path | Yes | Clean baseline |
| C1 | Correct artifact, controlled benign telemetry delivery delay/drop | Yes | Benign availability cost |
| C2 | Correct artifact, additional functional-conformance evidence delayed/unavailable | Yes | Incremental-evidence cost |
| F1 | New, approved, incorrect watchpoint/limit-table configuration; end-to-end deviation must be shown | Yes | Held-out fault family |
| F2 | Separate approved watchpoint predicate defect; end-to-end deviation must be shown | Yes | Second fault family |
| CAL1 | Previous S6X equality-change fixture | **No** | Environment/oracle calibration only; never migrate old observations |

The primary result is paired **G0 versus G1** per frozen scenario, not a pooled comparison against old Study 6 or Paper 1. Do not declare F1/F2 feasible until an independent measured cFS/LC requirement trace distinguishes the controlled fault in Phase A. Where a fault cannot compile, reach a monitored state or yield the expected differential without leaking hidden truth to the gate, record a fail-closed exclusion *before* primary observation generation.

**Direct observable endpoints:** command packet actually sent, cFS command-ingest receipt, monitored application's response/state transition, unsafe dispatch under hidden truth, correct-case hold/deferral, qualification duration, time to gather functional evidence, evidence availability, ground command-to-telemetry confirmation. Preserve per-scenario logs, source digests and two independent evaluator outputs.

## Design limitations, even if tests succeed

The environment would be an isolated **software-in-the-loop** simulator. Faults remain researcher-engineered; an independently implemented correctness assessor is not independent human replication. An actual cFS packet chain provides better applicability than a standalone Boolean example, but does not validate flight hardware, real RF outages, real organizational independence or field attack prevalence. It will not by itself turn all original three studies into a validated connected experiment: it directly tests the Study-6 assurance question and can inform an illustrative mission-recovery decision, with Study 3/4 remaining separate mechanisms. Negative, neutral and adverse results must be retained.

## Governance

No build, clone, Docker/network command, simulation replay, experimental output generation, canonical campaign start, paper manuscript change, public deposition, PR merge or publisher submission has been authorized by **this design record**. The separate author runtime gate requires a frozen environment lock, source and benchmark requirements, true data-flow separation, selected fault families, seeds/order/repeats and sample-size rationale. An environment preflight may be a separate explicitly approved bounded step. R4/R1/R2 and Campaign004 remain immutable.