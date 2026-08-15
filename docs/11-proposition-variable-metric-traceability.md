# Proposition–Variable–Metric Traceability — Gate 2 Draft

## Purpose

This document connects the research questions and theory-derived propositions to controlled factors, observed variables, primary outcomes, statistical comparisons, and falsification conditions. It is the scientific contract for the pilot design.

## Traceability rules

1. Every primary claim must trace to a predeclared proposition and outcome.
2. Primary outcomes are reported separately; no composite score may replace them.
3. A mission-aware policy is not presumed superior.
4. A proposition is unsupported when its predeclared directional or interaction effect is absent, practically negligible, or contradicted.
5. Exploratory metrics must be labeled exploratory.

## Controlled factors

| Factor | ID | Levels | Role |
|---|---|---|---|
| Response policy | `policy_id` | P0, P1, P2, P4, P5, P7 | Primary treatment |
| Cyber event | `event_id` | E1, E2, E3, E4 | Adversarial condition |
| Mission state | `mission_state_id` | M0, M2, M4 | Operational context |
| Contact condition | `contact_condition_id` | C0, C1 | Ground-intervention constraint |
| Evidence condition | `evidence_condition_id` | T0, T1 | Observability/trust constraint |
| Random seed | `seed` | Recorded integer | Reproducibility/blocking |

## Primary observed variables

| Variable | Type | Definition |
|---|---|---|
| `unauthorized_effect_completed` | Boolean | The event achieved its modeled unauthorized effect before containment or trial termination. |
| `mission_objective_completion_ratio` | Continuous 0–1 | Completed weighted mission objectives divided by objectives scheduled for the trial. Weights are fixed before the final campaign. |
| `safety_invariant_violation_count` | Count | Number of distinct frozen invariants violated during the trial. |
| `time_to_containment_s` | Time | Seconds from event activation to termination of the modeled unauthorized capability/effect. |
| `time_to_verified_recovery_s` | Time/censored | Seconds from event activation to `TRUSTED_RECOVERY_CONFIRMED`; right-censored when not confirmed. |
| `recovery_terminal_state` | Categorical | One of the frozen terminal states. |
| `legitimate_command_rejection_rate` | Continuous 0–1 | Rejected authorized commands divided by authorized commands attempted during the response/recovery interval. |
| `ground_spacecraft_state_divergence_s` | Time | Duration of disagreement in command-authority or approved-version state. |
| `evidence_completeness_ratio` | Continuous 0–1 | Available required recovery-evidence elements divided by applicable required elements. |

## Secondary observed variables

- Time in degraded mode
- Time in safe mode
- Contact windows consumed
- Simulated energy reserve minimum
- CPU and memory overhead
- Number of policy transitions
- False-containment event
- Residual unauthorized identity/process/configuration count
- Event-timeline reconstruction completeness

## Proposition traceability

### P1 — Mission-state dependence

**Proposition:** The value and cost of containment are mission-state dependent.

| Element | Specification |
|---|---|
| Manipulated factors | Response policy × mission state |
| Primary outcomes | Mission-objective completion ratio; safety-invariant violations; unauthorized-effect completion; legitimate-command rejection |
| Expected pattern | Policy effects differ across M0, M2, and M4; no single fixed policy is uniformly optimal across all mission states. |
| Primary analysis | Policy-by-state interaction using an appropriate generalized mixed-effects model; report marginal effects and confidence intervals. |
| Falsification condition | Policy ranking and practical effect are stable across mission states, with no meaningful interaction. |

### P2 — Contact-delay effect

**Proposition:** Contact delay increases the risk of unresolved compromise and inconsistent ground/spacecraft state.

| Element | Specification |
|---|---|
| Manipulated factors | Contact condition × response policy |
| Primary outcomes | Time to containment; time to verified recovery; ground-spacecraft divergence; recovery terminal state |
| Expected pattern | C1 increases unresolved duration and worsens recovery outcomes for ground-dependent policies more than autonomous policies. |
| Primary analysis | Time-to-event analysis for containment/recovery; ordinal or multinomial model for terminal state; interaction contrasts. |
| Falsification condition | Missing one contact window produces no practically meaningful difference, or autonomous policies worsen at least as much as ground-dependent policies. |

### P3 — Evidence requirement for trusted recovery

**Proposition:** Restart or nominal telemetry alone is insufficient evidence of trusted recovery.

| Element | Specification |
|---|---|
| Manipulated factors | Recovery method and evidence condition |
| Primary outcomes | Recovery terminal state; residual unauthorized state; evidence completeness; state divergence |
| Expected pattern | Some trials return to nominal behavior while remaining `OPERATIONAL_BUT_UNVERIFIED` or retaining modeled unauthorized state. |
| Primary analysis | Compare behavioral restoration with evidence-confirmed recovery; report discordant cases and false-recovery rate. |
| Falsification condition | Every nominally restored trial also satisfies all frozen trust criteria with no residual unauthorized state. |

### P4 — Degraded-evidence effect

**Proposition:** Reduced or manipulated telemetry can cause a response policy to select an unsafe or ineffective action.

| Element | Specification |
|---|---|
| Manipulated factors | Evidence condition × response policy × event |
| Primary outcomes | Incorrect policy action; safety-invariant violations; unauthorized-effect completion; mission loss; evidence-insufficient state entry |
| Expected pattern | T1 increases unsafe/ineffective selections for policies that depend on incomplete evidence; conservative handling may reduce unsafe actions at mission cost. |
| Primary analysis | Binary/generalized mixed-effects comparisons; stratified confusion matrix for policy selection; report conservative-action cost. |
| Falsification condition | Evidence degradation does not change action selection or outcomes, or the mission-aware policy does not respond differently to insufficient evidence. |

### P5 — Conditional benefit of mission-aware response

**Proposition:** A mission-aware policy can improve security–mission trade-offs, but it will not dominate simpler policies under every condition.

| Element | Specification |
|---|---|
| Manipulated factors | Policy across all frozen conditions |
| Primary outcomes | Unauthorized-effect completion; mission-objective completion; invariant violations; time to verified recovery; legitimate-command rejection |
| Expected pattern | P7 is Pareto-efficient in a meaningful subset of conditions but is matched or outperformed by simpler policies in others. |
| Primary analysis | Pareto-front membership; condition-specific effect estimates; no primary weighted score. |
| Falsification condition A | P7 is never Pareto-efficient or consistently worse than a simpler policy. |
| Falsification condition B | P7 dominates every policy in every condition, suggesting scenario or implementation bias rather than a credible trade-off. |

## Research-question coverage

| Research question | Propositions | Primary evidence |
|---|---|---|
| RQ1 Response effectiveness | P1, P5 | Unauthorized effects, containment time, terminal state |
| RQ2 Mission-state cost | P1, P5 | Mission completion, invariant violations, command rejection |
| RQ3 Contact delay | P2 | Recovery time, containment time, state divergence |
| RQ4 Harmful automation | P1, P4, P5 | Mission loss, invariant violations, condition-specific policy comparisons |
| RQ5 Trusted-state evidence | P3, P4 | Evidence completeness, residual state, terminal-state classification |

## WP8 minimal pilot subset

WP8 uses E1, E3, and E4 as the high-information pilot subset. E2 remains in the frozen event catalog but is omitted from the pilot because E1 already exercises the command-path response mechanism; replay-specific coverage remains eligible for WP9.

The pilot is staged: one control-validity run is required for every declared pilot cell before replicated variability runs begin. Pilot results determine campaign readiness and repetition count; they are not used as final hypothesis tests.

## Blocking and replication

- Trial order will be randomized within reproducible blocks.
- The simulator snapshot and dependency versions will be fixed within a campaign.
- Each condition will be repeated with multiple recorded seeds.
- Pilot variance and failure rates will determine final repetitions.
- Failed infrastructure runs are classified `RUN_INVALID` using predeclared rules and are not silently discarded.

## Gate 2 acceptance criteria

This traceability model is accepted when:

- Every frozen factor and outcome exists in the machine-readable configuration.
- Every metric has a deterministic calculation specification.
- Every proposition has a falsification condition.
- The experiment runner can emit all required raw fields without manual reconstruction.
