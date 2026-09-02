# Formal-Assurance Traceability Candidate — Study 2

## Current status

`HISTORICAL_PRE_STUDY2_TRACEABILITY_CANDIDATE_SUPERSEDED`

> This file is retained as a historical planning/traceability record. It predates the frozen Study-2 protocol, implemented assurance foundation, Phase-6 campaign, and canonical Phase-7 analysis. It must not be read as evidence that Study 2 remains design-only or runtime-unauthorized.

Current Study-2 authority is:

- `study2/README.md`
- `study2/STUDY2_PROTOCOL.json`
- `study2/docs/PHASE5_RUNTIME_FREEZE.md`
- `study2/PHASE6_PROVENANCE.json`
- `study2/evidence/phase6/README.md`
- `study2/PHASE7_RESULTS_FREEZE.json`
- `study2/PHASE7_PROVENANCE.json`
- `study2/docs/PHASE7_RESULTS_FREEZE.md`

The original candidate version remains recoverable through Git history. This current copy records what the candidate contributed to the eventual design and what changed before the empirical freeze.

## Historical purpose

The candidate extracted implemented Study-1 response/recovery semantics as a starting point for a separately frozen Study-2 formal specification. Its central governance requirement was sound and remains applicable: **the formal model must trace to implemented behavior rather than idealized manuscript prose, and Study-2 extensions must not silently redefine frozen Study-1 P7.**

## Study-1 baseline semantics captured by the candidate

The candidate traced these Study-1 implementation surfaces:

- `src/mission_recovery/events.py` — policy-visible event creation, T1 omission treatment, separation of immutable ground truth from policy-visible evidence;
- `configs/wp5_event_catalog.json` — frozen event truth/evidence and treatment definitions;
- `src/mission_recovery/policies.py` — deterministic policy input boundary and P7 delegation;
- `configs/wp6_policy_rules.json` — fixed actions and P7 evidence-sufficient/evidence-insufficient rule tables;
- `src/mission_recovery/primary_metrics.py` — trusted-recovery criteria and terminal-state semantics.

Study-1 T1 remains an omission/reduction treatment. The later Study-2 evidence mechanisms for staleness/replay, contradiction, manipulation, and bounded producer compromise were implemented as **new Study-2 factors**, not retroactively attributed to Study 1.

## Core assurance properties proposed historically

The candidate identified properties that should be preserved in a stronger secure/dependable response design:

1. **Oracle isolation:** runtime policy cannot read research-only ground truth/adjudication controls.
2. **Deterministic delegation:** a fully specified frozen policy-visible state produces one declared effective policy/action.
3. **Evidence-path integrity:** evidence-insufficient paths cannot silently take evidence-sufficient branches.
4. **Authorization gating:** authorization-dependent actions cannot execute before the modeled authorization condition permits them.
5. **Trusted-recovery soundness:** a trusted terminal requires the applicable frozen evidence/recovery criteria.
6. **Residual-state exclusion:** modeled residual unauthorized state is incompatible with an objectively trusted terminal classification.
7. **Terminal-state uniqueness/precedence:** valid terminating paths must map to declared terminal semantics.
8. **Treatment immutability:** adversarial policy-visible evidence changes cannot mutate seed, treatment identity, immutable truth, or analysis controls.
9. **Study-1 semantic preservation:** the formal abstraction must not change frozen Study-1 policy behavior.

These concepts informed the later Study-2 assurance foundation, which added implementation-bound conformance/security testing and formal model checking before the empirical campaign. The actual assurance evidence is recorded under `study2/`; this historical candidate is not the authority for the final model state.

## What changed before Study-2 freeze

The eventual Study-2 design was more specific than this candidate:

- experiment ID `S2-AEATR-001`;
- 85 exact cells rather than the candidate approximate design size;
- 96 paired seeds for the primary Block A and 32 paired seeds for secondary Blocks B–E;
- V0–V5 evidence mechanisms, including bounded producer compromise;
- K0–K4 contact profiles with K4 explicitly intermittent/flapping rather than ordinal severity 4;
- A0–A3 adversary classes with A2/K2 explicitly contact-coupled;
- independent research-only adjudication unavailable to runtime selectors;
- frozen logical SIL time and a 240-logical-second RMST restriction;
- explicit invalid-attempt/ledger/no-hidden-retry controls;
- a separately frozen Phase-7 statistical implementation before aggregate analysis.

The campaign then completed with **3,872 VALID observations, 0 INVALID attempts, and 85 cells**. Phase 7 produced **162 primary paired contrasts** and **432 prespecified secondary contrasts**, and the independent reproduction reported **0 mismatches**.

## RQ3 correction relevant to assurance interpretation

The historical candidate envisioned matched benign-fault/adversarial ambiguity. The frozen Block-C implementation ultimately varied a `BENIGN`/`ADVERSARIAL` cause label without changing hidden truth or generated policy-visible evidence within an ambiguity family. Accordingly, the final 54 zero C-family contrasts are a **structural label-invariance/control result**, not empirical evidence that policies distinguish or fail to distinguish genuinely different benign and adversarial causal mechanisms.

That interpretation is authoritative in `study2/docs/PHASE7_RESULTS_FREEZE.md` and must not be weakened by reference to this earlier candidate.

## Current publication use

For the journal manuscript, cite or rely on the canonical Study-2 protocol/freeze/provenance and implemented assurance records, not this planning file. This document is useful only for showing the development path from Study-1 implementation semantics to the later Study-2 assurance design.

No runtime execution, statistical recalculation, or new scientific claim is authorized by this historical record.
