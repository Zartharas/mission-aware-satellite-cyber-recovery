# WP6 P7 — Mission-Aware Dispatch and Effect Integration

## Purpose

This is the final WP6 integration step. It verifies that P7 selects a fixed treatment from policy-visible event context and that the selected treatment's already-validated runtime effect is executed.

No composite response score is used.

## Runtime matrix

Five fresh nominal runtimes are used:

| Case | Event | State | Contact | Evidence | P7 delegate |
|---|---|---|---|---|---|
| A | E1 | M0 | C0 | T0 | P1 |
| B | E1 | M0 | C1 | T0 | P2 |
| C | E1 | M2 | C0 | T0 | P2 |
| D | E1 | M2 | C0 | T1 | P4 |
| E | E3 | M4 | C0 | T0 | P5 |

Cases A-D use the exact retained E1 Sample NOOP bytes for the attacker and authorized-ground probes.

Case E uses the retained E3 approved and tampered synthetic artifacts and stops at the verified rollback-request boundary.

## One-factor contrasts

### Contact only: A versus B

Event, mission state, evidence condition, and seed are held constant.

Changing `C0` to `C1` changes the P7 delegate from P1 to P2.

For the canonical low-risk E1 NOOP:

- P1 blocks the modeled attacker while preserving authorized ground;
- P2 preserves both paths.

This is a deliberate negative case: mission-aware selection does not dominate the stricter source-isolation treatment in every condition.

### Mission state only: A versus C

Event, contact, evidence condition, and seed are held constant.

Changing `M0` to `M2` changes the delegate from P1 to P2 and changes the canonical E1 unauthorized-effect outcome from blocked to allowed.

### Evidence only: C versus D

Event, mission state, contact, and seed are held constant.

Changing `T0` to `T1` removes required authorization evidence, changing the delegate from P2 to P4.

For the same NOOP probes:

- P2 permits both attacker and authorized-ground commands;
- P4 blocks both.

This exposes the containment-versus-legitimate-interruption cost of conservative response under insufficient evidence.

## P5 boundary

Case E requires P7 to delegate to P5 and create a rollback request bound to the approved artifact hash and rejected candidate hash.

WP6 does not stage the approved rollback artifact, activate it, execute recovery, or verify terminal trust.

Those steps remain WP7.

## Oracle guard

For every runtime case, the P7 decision is recomputed after mutating immutable ground-truth fields. The decision must remain byte-for-byte identical.

P7 therefore depends only on event identity, mission state, contact condition, evidence condition, and policy-visible evidence.

## Claim boundary

This WP6 integration establishes deterministic selector-to-treatment mechanics and concrete single-run tradeoff examples.

It does not estimate final policy effect sizes, containment latency, mission objective completion probability, or trusted recovery. Those require the later repeated experimental campaign and WP7 recovery implementation.
