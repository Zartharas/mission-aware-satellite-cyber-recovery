# AERC Recovery Action Sink

This is a pre-canonical cFS component for `S7E-AERC-001`.

The sink has one responsibility: receive a requested recovery action and publish a deterministic record of what was requested. It does not decide whether the request is correct and it does not actuate hardware.

Allowed action codes:

- `HOLD`
- `ENTER_RECOVERY_GATE`

The sink accepts only the four registered Study-7E policy identifiers and the two allowed action codes. The record preserves scenario ID, policy ID, requested action, and a local monotonic receipt sequence.

The sink contains no research-only truth, fault identity, topology identity, objective/correct action, learner, signing key, or canonical-execution logic.
