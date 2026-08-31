# Formal-Assurance Traceability Candidate — Study 2

## Status

`DESIGN_ONLY_SOURCE_TRACED_NOT_RUNTIME_AUTHORIZED_NOT_FROZEN`

This document extracts the **implemented Study 1 response/recovery semantics** that should serve as the starting point for a Study 2 formal specification. It does not modify Study 1 logic and does not claim that a formal verification has already been completed.

## Why formalization is valuable

Study 1 provides empirical evidence about a deterministic response selector, evidence-conditioned behavior, authorization dependence, and trusted-recovery adjudication. IEEE TDSC explicitly includes formal specification/verification, attack models, online recovery, experimental testbeds, and statistical methods within its scope. ACM TOPS likewise includes recovery/survivable operation, trust, authorization, and formal assurance.

A formal model can therefore turn the follow-on work from “more simulation” into a stronger **secure/dependable response methodology** by proving bounded state-machine properties and then using SIL/HIL experiments to measure performance and trade-offs that the proof does not address.

## Source-of-truth implementation traced

The starting semantics are taken from the reproducibility-hardened Study 1 repository rather than reconstructed from manuscript prose alone:

- `src/mission_recovery/events.py`
  - creates the policy-visible event instance;
  - applies T1 by omitting event-specific evidence keys;
  - preserves separate immutable `ground_truth` and `policy_visible_evidence` objects;
  - records event-level SPARTA identifiers.
- `configs/wp5_event_catalog.json`
  - defines E1–E4 ground truth, policy evidence, T1 omitted fields, prohibited actions, and frozen SPARTA associations.
- `src/mission_recovery/policies.py`
  - defines the policy input boundary;
  - computes minimum-evidence sufficiency;
  - implements deterministic P7 delegation;
  - records `oracle_ground_truth_read = False`.
- `configs/wp6_policy_rules.json`
  - defines fixed policy actions P0/P1/P2/P4/P5;
  - defines minimum evidence by event;
  - defines all P7 evidence-sufficient and evidence-insufficient delegation rules.
- `src/mission_recovery/primary_metrics.py`
  - defines the ten trusted-recovery criteria;
  - verifies evidence currentness/satisfaction consistency;
  - defines terminal-state precedence;
  - prevents trusted recovery when applicable evidence is incomplete or unsatisfied.

The formal model must remain traceable to these implementation sources. Any Study 2 policy extensions must receive new identifiers and cannot silently redefine Study 1 P7.

## Study 1 policy semantics to preserve as baseline

### Fixed actions

- `P0 → OBSERVE_ONLY`
- `P1 → ISOLATE_MODELED_SOURCE`
- `P2 → RESTRICT_HIGH_RISK_COMMANDS`
- `P4 → ENTER_SAFE_MODE` (experimental modeled action only)
- `P5 → REQUEST_VERIFIED_ROLLBACK`

### P7 input state

The implemented P7 selector receives:

`{event_id, mission_state, contact_condition, evidence_condition, policy_visible_evidence}`

and does not read immutable experiment ground truth.

### Evidence assessment

For each event, a frozen set of minimum policy-evidence fields is evaluated. The current implementation supports rules `present` and `true`. Failure of any required check produces `evidence_insufficient = True` and an explicit list of failed evidence keys.

Study 1 T1 is specifically an **omission treatment**: `events.py` removes event-defined keys from the policy-visible evidence map. Future Study 2 states for staleness, contradiction, and deliberate value manipulation must be modeled as new factors rather than retroactively attributed to T1.

### P7 transition function

If evidence is insufficient:

`P7 → rules.evidence_insufficient[mission_state][contact_condition]`

If evidence is sufficient:

`P7 → rules.evidence_sufficient[event_id][mission_state][contact_condition]`

The delegated policy then determines the selected action. This transition function is deterministic under a fully specified policy-visible input.

## Trusted-recovery semantics to preserve as assurance property

`primary_metrics.py` defines the recovery criteria:

1. approved version;
2. valid integrity measurement;
3. valid authorization;
4. current measured state;
5. authorized command path restored;
6. ground/spacecraft state agreement;
7. required telemetry restored;
8. health checks passed;
9. no residual unauthorized state;
10. complete recovery manifest.

For applicable criteria, a satisfied criterion must have available/current evidence. The implementation rejects a trusted-recovery predicate if applicable recovery evidence is incomplete or a criterion is unsatisfied. Conversely, complete/current and satisfied applicable evidence requires the trusted-recovery predicate.

Study 2 formalization should model this as a conjunction over applicable criteria rather than as a single unconstrained Boolean flag.

## Candidate formal variables

A minimal state-machine model should separate at least:

- `event ∈ {E1,E2,E3,E4,...Study2 extensions}`
- `mission ∈ MissionStates`
- `contact ∈ ContactStates`
- `authorization ∈ AuthorizationStates`
- `evidence ∈ EvidenceObservationStates`
- `evidenceSufficient ∈ BOOLEAN`
- `requestedPolicy ∈ Policies`
- `effectivePolicy ∈ Policies`
- `selectedAction ∈ Actions`
- `systemSecurityState ∈ SecurityStates`
- `recoveryState ∈ RecoveryStates`
- `recoveryEvidence[i] ∈ {unavailable,current_unsatisfied,current_satisfied,not_applicable}`
- `terminalState ∈ TerminalStates`
- `oracleVisibleToPolicy ∈ BOOLEAN`

For Study 2, `evidence` should decompose into omission, freshness, contradiction, and manipulation dimensions rather than being represented by one binary T0/T1 value.

## Candidate invariants

### F1 — oracle isolation

`oracleVisibleToPolicy = FALSE`

The runtime response selector must never gain access to the experiment/adjudication ground truth that is reserved for validity and post-run analysis.

### F2 — deterministic delegation

For an unchanged frozen policy-visible state, P7 must delegate to exactly one effective policy and selected action.

### F3 — evidence-insufficient path integrity

If minimum evidence is insufficient, P7 must use the explicitly declared evidence-insufficient transition table and cannot take an evidence-sufficient branch.

### F4 — authorization gating

Any Study 2 action declared ground-authorization dependent must not execute before the modeled authorization state permits it.

### F5 — trusted-recovery soundness

`terminalState = TRUSTED_RECOVERY_CONFIRMED`

implies every applicable frozen recovery criterion is current and satisfied, including `no_residual_unauthorized_state`.

### F6 — no residual unauthorized state in trusted terminal

`residualUnauthorizedState = TRUE`

implies

`terminalState ≠ TRUSTED_RECOVERY_CONFIRMED`.

### F7 — trusted-recovery completeness

If every applicable recovery criterion is current and satisfied, the model must not terminate in a non-trusted recovery state unless a separately declared higher-precedence terminal condition (for example `RUN_INVALID` or `MISSION_LOSS`) applies according to the frozen terminal semantics.

### F8 — terminal-state uniqueness

Every terminating valid path reaches one allowed terminal state according to a declared precedence/transition rule; terminal classifications cannot be simultaneously ambiguous at the exported state boundary.

### F9 — treatment immutability

Adversarial changes to policy-visible evidence cannot mutate the immutable treatment identity, seed, experiment ground truth, or analysis-control variables.

### F10 — Study 1 semantic preservation

For every Study 1 P7 input combination represented by the current rule table, the formal transition function must produce the same delegated policy/action as `policies.py` and `wp6_policy_rules.json`.

F10 is essential: the formal model should be checked against the implementation, not merely reviewed manually.

## Candidate temporal/liveness properties

Some properties require assumptions and should not be asserted unconditionally.

- Under a declared recovery-enabled environment and eventual availability of required authorization/evidence, a recovery-capable path should eventually reach a defined terminal state.
- A ground-authorization wait path should not remain indefinitely authorized-and-enabled without progressing unless the model explicitly permits a timeout/failure terminal.
- An evidence-insufficient fallback should eventually produce either containment/recovery progress or a declared non-recovery terminal state under bounded-run assumptions.

These properties require exact timeout/contact semantics before freeze. They should not be written as unconditional liveness claims while the Study 2 timing model remains open.

## Recommended formalism

### Primary recommendation: TLA+

TLA+ is a strong first choice for the Study 2 control-plane model because the key questions are discrete state transitions, information visibility, authorization ordering, fallback behavior, recovery predicates, and invariant preservation. It can represent nondeterministic environment/adversary transitions without forcing premature probability assignments.

### Complementary option: PRISM

PRISM becomes attractive if Study 2 later defines probabilistic contact availability, fault/attack occurrence distributions, or stochastic recovery transitions and seeks quantified reliability/security properties. PRISM should complement rather than replace the implementation-traced discrete safety model if probabilistic assumptions are introduced.

### Why not start with an ML policy

Computers & Security currently excludes work in which AI/ML is a significant scientific component, and Study 1 P7 is already deterministic and interpretable. More importantly, TDSC/TOPS value does not require ML. A traceable deterministic formal model, strong adversary/evidence design, and controlled empirical validation provide a cleaner path to methodological novelty.

## Required implementation-conformance tests before formal claims

Before Study 2 calls any property “verified,” add automated conformance tests that enumerate the finite Study 1 policy state space and compare:

`formal-model decision ↔ Python evaluate_policy decision`

for every supported combination of event, mission state, contact condition, evidence condition, and valid policy-visible evidence class.

The test should additionally verify:

- `oracle_ground_truth_read` remains false;
- evidence failure sets match the implementation;
- delegated policy and selected action match exactly;
- trusted-recovery classification in the formal abstraction agrees with implementation-generated criterion states for representative exhaustive criterion combinations where computationally feasible.

## Next design gate

Before writing an executable TLA+/PRISM specification, resolve and freeze the Study 2 definitions for:

1. evidence omission, staleness, contradiction, and manipulation;
2. contact/authorization state transitions and timeouts;
3. benign-fault versus adversarial cause representation;
4. new baselines and selector ablations;
5. any prospective correctness/acceptability oracle and its strict runtime isolation;
6. terminal states added or retained from Study 1.

No Study 2 runtime execution is authorized by this document.
