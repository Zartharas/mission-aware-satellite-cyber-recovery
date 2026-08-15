# Frozen Study Boundaries — Gate 1

## Status

This document freezes the minimum scientific boundaries required before testbed implementation. Changes require an entry in `tracker/decision_log.csv`.

## Mission objectives

### MO-1 Preserve command authority

Only authorized commands that are valid for the current mission state should alter spacecraft behavior.

### MO-2 Preserve spacecraft survivability

The simulated spacecraft must remain within defined power, thermal, control, and recoverability limits.

### MO-3 Preserve prioritized mission service

Payload and supporting functions should continue when continuation does not violate a higher-priority safety or security constraint.

### MO-4 Restore an approved operational state

After containment, the spacecraft must return to an approved software, configuration, authorization, and health state.

### MO-5 Preserve sufficient incident evidence

The system must retain enough trustworthy evidence to reconstruct the event, response, and recovery decision.

## Unacceptable losses

- UL-1: Loss of authoritative command control
- UL-2: Execution of an unauthorized safety-critical command
- UL-3: Entry into an unrecoverable or undefined spacecraft state
- UL-4: Violation of the modeled minimum energy reserve
- UL-5: Activation of an unverified software or configuration image
- UL-6: Permanent loss of the only trusted recovery path
- UL-7: Declaration of recovery without sufficient current evidence
- UL-8: Avoidable loss of a prioritized mission objective caused by the response policy
- UL-9: Irrecoverable disagreement between ground and spacecraft authorization state
- UL-10: Loss or corruption of the immutable experiment ground-truth record

## Safety and trust invariants

### SI-1 Command-state authorization

A safety-critical command must satisfy identity, authorization, freshness, and mission-state policy.

### SI-2 Energy reserve

The simulated energy state must not fall below the defined survival threshold.

### SI-3 Verified recovery image

Rollback or restart may use only an approved image with a valid integrity measurement and authorization record.

### SI-4 Recovery-path preservation

A response policy must not disable every available recovery path.

### SI-5 Evidence freshness

Recovery evidence older than the configured freshness threshold cannot independently establish trusted recovery.

### SI-6 Ground-spacecraft convergence

Normal command operations cannot resume until ground and spacecraft authorization states converge or an explicitly modeled emergency authority is invoked.

### SI-7 Minimum observability

The mission-aware policy must enter a conservative evidence-insufficient state when the minimum required telemetry or trust evidence is unavailable.

### SI-8 Immutable ground truth

The event orchestrator and immutable run log remain outside the simulated adversary trust boundary.

## Trusted-recovery criteria

A run is marked `TRUSTED_RECOVERY_CONFIRMED` only when all applicable checks pass:

1. Approved software and configuration version
2. Valid integrity hash
3. Valid authorization or package signature
4. Current attestation or equivalent measured-state evidence
5. Restored authorized command path
6. Ground-spacecraft state agreement
7. Required telemetry restored
8. Health checks passed
9. No modeled residual unauthorized process, identity, or configuration
10. Complete recovery manifest and event timeline

Other terminal states are:

- `OPERATIONAL_BUT_UNVERIFIED`
- `CONTAINED_NOT_RECOVERED`
- `RECOVERY_FAILED`
- `MISSION_LOSS`
- `RUN_INVALID`

## Minimum pilot scope

### Cyber events

- E1: Unauthorized valid command
- E3: Compromised update
- E4: Telemetry observability degradation

E2 replayed-command semantics remain in the frozen event catalog but are omitted from the minimum WP8 pilot because E1 exercises the same command-path response mechanism. E2 remains eligible for WP9.

### Mission states

- M0: Nominal operations
- M2: Low power or eclipse
- M4: Software update or recovery

### Response policies

- P0: Observe only
- P1: Identity or source isolation
- P2: Selective command restriction
- P4: Safe-mode transition
- P5: Rollback
- P7: Mission-aware selection

### Contact conditions

- C0: Immediate ground contact
- C1: One missed contact window

### Evidence conditions

- T0: Full evidence
- T1: Reduced or suppressed telemetry

## Primary outcomes

- Unauthorized effect completion
- Mission objective completion
- Safety-invariant violation
- Time to verified trusted recovery
- Recovery terminal state
- Legitimate command rejection

## Analysis boundary

Primary outcomes will be reported separately. Pareto-front analysis will evaluate trade-offs. A weighted composite score may be used only as a secondary sensitivity analysis.

## Human and operational boundary

The first study phase contains no human participants, operational satellite access, live RF, production credentials, or proprietary telemetry.

## Gate 1 decision

These boundaries are sufficiently specific to begin WP2/WP3 refinement and WP4 architecture selection. They do not authorize implementation against operational systems.
