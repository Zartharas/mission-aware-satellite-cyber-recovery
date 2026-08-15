# Primary Metric Specification — Gate 3 Draft

## Purpose

This document defines deterministic calculations for the frozen primary outcomes. Implementations must preserve the raw events, counts, timestamps, and denominators needed to reproduce every reported metric.

## Common time basis

- `t0` is the monotonic timestamp at event activation.
- `raw_metric_evidence.*.timestamp_s` and `run_end_s` are monotonic offsets from run start; reported time-to-event values subtract `event_activation_s` (`t0`).
- All elapsed-time metrics use the experiment controller's monotonic clock.
- UTC timestamps are retained for provenance but are not used to calculate elapsed durations.
- A time-to-event value is `null` when the event was not observed before the run ended.
- Statistical analysis must treat unobserved recovery or containment times as right-censored, not as zero.

## M-01 Unauthorized effect completion

### Raw inputs

- Event-specific unauthorized success predicate
- Predicate timestamp
- Containment timestamp
- Run terminal timestamp

### Calculation

```text
unauthorized_effect_completed = true
```

when the frozen event-specific success predicate becomes true at least once after `t0` and before the run terminal timestamp.

The value remains true even if the effect is later reversed. Reversal is measured through recovery and residual-state outcomes.

### Event-specific predicates

- E1: A protected state is changed by the unauthorized valid command.
- E2: A replayed command produces a duplicate or stale protected-state effect.
- E3: An unapproved software/configuration version becomes active or is accepted for activation.
- E4: Required policy-visible telemetry is suppressed or stale beyond the configured threshold.

## M-02 Mission objective completion ratio

### Raw inputs

For every scheduled objective instance:

- Objective instance ID
- Frozen objective weight
- Scheduled start/end
- Completion predicate
- Completion status

### Calculation

```text
mission_objective_completion_ratio =
  sum(weight_i for completed scheduled objective instances) /
  sum(weight_i for all scheduled objective instances)
```

### Rules

- Weights are fixed before the final campaign.
- An objective instance is counted once.
- An objective prevented by a safety-preserving response remains incomplete; it is not silently removed from the denominator.
- Runs with no scheduled objective weight are invalid for this metric and must not be assigned a zero denominator.

## M-03 Safety-invariant violations

### Raw inputs

- Invariant ID
- Violation start timestamp
- Violation end timestamp or unresolved marker
- Ground-truth evidence supporting the violation

### Calculations

```text
safety_invariant_violation_count =
  number of distinct frozen invariant IDs violated at least once
```

The run record also stores the unique invariant ID list. Duration and recurrence are secondary metrics.

### Rule

A missing sensor or missing policy-visible observation is not itself proof that the physical invariant was violated. Invariant evaluation uses immutable experiment ground truth.

## M-04 Time to containment

### Raw inputs

- `t0`
- First timestamp when the event-specific unauthorized capability and active effect are both unable to progress

### Calculation

```text
time_to_containment_s = containment_timestamp - t0
```

### Rules

- Temporary interruption does not count when the capability resumes without a new adversary action.
- When containment is not reached, the value is `null` and the observation is right-censored at run end.

## M-05 Time to verified trusted recovery

### Raw inputs

- `t0`
- First timestamp at which all applicable trusted-recovery criteria are simultaneously true and current

### Calculation

```text
time_to_verified_recovery_s = trusted_recovery_timestamp - t0
```

### Rules

- A restart, safe-mode entry, nominal telemetry, or command acceptance does not independently establish recovery.
- If any required evidence becomes stale before classification, the timer continues.
- When trusted recovery is not confirmed, the value is `null` and is right-censored at run end.

## M-06 Legitimate command rejection rate

### Raw inputs

- Count of authorized, state-valid command attempts during the frozen response/recovery interval
- Count of those attempts rejected, dropped, or expired because of the response policy

### Calculation

```text
legitimate_command_rejection_rate =
  legitimate_commands_rejected / legitimate_commands_attempted
```

### Zero-denominator rule

When no legitimate command is attempted, the rate is `null`, not zero. The raw numerator and denominator must always be retained.

## M-07 Ground-spacecraft state divergence

### Raw inputs

Time intervals in which ground and spacecraft disagree about any frozen authoritative state:

- Active command authority
- Approved software/configuration version
- Recovery status

### Calculation

```text
ground_spacecraft_state_divergence_s =
  measure of the union of all divergence intervals
```

Overlapping divergence intervals are counted once.

## M-08 Evidence completeness ratio

### Raw inputs

- Applicable recovery-evidence checklist for the run
- Available and current evidence elements at classification time

### Calculation

```text
evidence_completeness_ratio =
  count(available and current applicable elements) /
  count(applicable required elements)
```

### Rules

- Invalid, stale, or unverifiable evidence is not complete.
- Non-applicable elements are excluded only by a predeclared scenario rule.
- The denominator and excluded elements must be recorded.

## Terminal-state classification

Classification occurs at the run timeout or earlier absorbing condition using this precedence:

1. `RUN_INVALID` — protocol, environment, evidence-capture, or isolation failure makes scientific interpretation invalid.
2. `MISSION_LOSS` — a frozen unacceptable-loss predicate is reached.
3. `TRUSTED_RECOVERY_CONFIRMED` — every applicable trusted-recovery criterion is simultaneously true and current.
4. `OPERATIONAL_BUT_UNVERIFIED` — prioritized operations are restored, but trusted-recovery evidence is incomplete, stale, or contradictory.
5. `RECOVERY_FAILED` — an attempted recovery exhausts its bounded actions or loses the approved recovery path while the system is not in an acceptable stable contained state.
6. `CONTAINED_NOT_RECOVERED` — unauthorized capability/effect is contained, but approved operations are not restored before timeout.

The classifier must store the predicates that selected the terminal state.

## Required raw fields for implementation

The WP8 run-record schema preserves the raw evidence required to derive these primary metrics. Runtime adapters must populate these fields from observations rather than expected values. The retained evidence includes at least:

- Event success predicate and timestamp
- Containment predicate and timestamp
- Objective instance weights and completion states
- Invariant violation intervals
- Legitimate commands attempted and rejected
- Ground-spacecraft divergence intervals
- Recovery checklist denominator and element states
- Run-end censoring timestamp
- Terminal-state predicate evidence

## Missing-data rule

No primary metric is imputed for an individual run. Missing required ground-truth data makes the run `RUN_INVALID`. Missing policy-visible telemetry may be an intended experimental condition and does not invalidate a run when immutable ground truth remains complete.

The WP8 schema therefore permits a `RUN_INVALID` record to retain factor/environment provenance and an invalid-run reason without fabricating unavailable outcome or raw-metric fields. Recovery-evidence elements excluded by a predeclared scenario rule are recorded explicitly and represented as `null` in the top-level recovery-evidence object.

## Reporting rule

Report raw counts and denominators alongside ratios. Report time-to-event censoring and use analysis methods that retain censored runs. Never discard failed or unrecovered trials solely because a duration is unavailable.
