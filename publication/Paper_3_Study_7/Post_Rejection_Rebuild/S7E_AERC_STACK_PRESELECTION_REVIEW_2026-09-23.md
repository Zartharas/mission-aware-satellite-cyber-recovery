# S7E-AERC-001 Stack Preselection Review — 2026-09-23

**Review ID:** `S7E-AERC-STACK-PRESELECT-002`  
**Experiment:** `S7E-AERC-001`  
**State:** `DECISION_DEFERRED__PRESELECTION_SEAM_PROOFS_PENDING`  
**Scientific execution:** NOT AUTHORIZED

## Decision

**No final cFS-vs-NOS3 stack selection is made at this checkpoint.**

Both candidate feasibility gates are green at their present scope, but the repository's preregistered selection criteria require additional integration evidence before either candidate may be selected.

This is a deliberate fail-closed decision. It prevents a build-only success from being treated as proof of the architecture seams needed by Study 7E.

## Evidence now established

### Standalone cFS v7.0.1

Established:

- exact official release pin;
- native build/test feasibility;
- custom Study-7E engineering application build/load;
- live cFE execution;
- cFE Software Bus fixed-message publish/receive self-loop;
- repository governance/contract checks remain green.

Not yet established before selection:

- HS/readiness observation through the intended Study-7E seam;
- two cFS instances exchanging Study-7E messages through SBN;
- end-to-end preservation of deterministic scenario IDs across that topology;
- recovery action-sink telemetry/capture across the intended seam.

### NOS3 v1.7.5

Established:

- exact official release pin;
- exact recursive dependency/gitlink assertions for key cFS-family components;
- controlled `config`;
- FSW unit-test build and tests;
- simulator build;
- provenance artifact;
- zero Study-7E scientific scenarios/results.

Not yet established before selection:

- Study-7E custom application integration;
- deterministic non-canonical scenario control;
- required T3/T4 multi-instance/SBN topology;
- Study-7E command/telemetry observation/capture;
- controlled runtime network-dependency boundary.

## Same-criteria comparison

| Criterion | standalone cFS v7.0.1 | NOS3 v1.7.5 |
|---|---|---|
| Exact release/dependency provenance | established | established |
| Reproducible CI build/test | established | established |
| Live custom Study-7E cFE app | established for SB probe | not yet demonstrated |
| Direct cFE/SB control | demonstrated | available by architecture, Study-7E seam not yet demonstrated |
| Multi-instance/SBN proof needed for T3/T4 | pending | pending |
| Deterministic scenario-ID end-to-end proof | pending | pending |
| Study-7E telemetry/action capture | pending | pending |
| Ground/operator integration | minimal lab apps | integrated NOS3 capability |
| Dynamics/environment/hardware models | outside baseline | integrated NOS3 capability |
| Qualification surface / dependency burden | smaller | materially broader |
| Runtime network-dependency containment | simpler boundary, still to prove | broader boundary, still to prove |
| Scientific benefit for RQ1-RQ4 | sufficient if T3/T4 and capture seams are proven | potentially stronger architecture realism if added layers remain deterministic and do not alter policy-visible evidence |

## Scientific relevance

Study 7E's primary questions concern equal-information policy behavior and trust-domain separation/common-cause propagation, not orbital dynamics or hardware performance.

Therefore NOS3's additional dynamics, hardware-model, and operator layers are scientifically useful only if they strengthen the concrete architecture and reviewer-facing integration evidence without injecting irrelevant nondeterminism or changing policy-visible information.

Conversely, standalone cFS is scientifically adequate only if it can prove the T3/T4 SBN separation, HS/readiness observation, deterministic scenario propagation, and action/telemetry capture required by the protocol.

## Minimum evidence required to close this decision

### cFS candidate

1. observe HS/readiness through the controlled Study-7E evidence seam;
2. demonstrate two-instance SBN transport relevant to T3/T4;
3. preserve a deterministic scenario ID across the cross-instance path;
4. capture a non-canonical action-sink telemetry/result record.

### NOS3 candidate

1. integrate a Study-7E custom app into the pinned NOS3 mission;
2. demonstrate deterministic non-canonical scenario control;
3. demonstrate the required SBN/multi-instance topology;
4. capture the relevant command/telemetry or equivalent deterministic trace;
5. document and constrain runtime network dependencies for future reproducibility.

## Guardrail

No candidate is frozen, no canonical environment is selected, no model is trained/frozen, and no scientific campaign is authorized by this review.
