# WP6 P5 — Verified Rollback-Request Effect

## Purpose

This adapter validates the executable boundary of P5: create an evidence-bound request for a verified rollback target after a compromised update candidate is detected.

It deliberately does **not** execute recovery.

## Matched design

P0 and P5 run in separate fresh accepted nominal NOS3 runtimes using the same E3 instance (`M4/C0/T0`, seed 1).

Both runs use the same:

- approved synthetic artifact and manifest;
- tampered same-version candidate;
- tampered candidate SHA-256;
- cFS backing stage path; and
- pinned NOS3 runtime.

The tampered candidate is staged at the same simulator path in both trials.

## P0

`OBSERVE_ONLY` leaves the tampered candidate staged and creates no rollback request.

No approved rollback candidate is staged or activated.

## P5

`REQUEST_VERIFIED_ROLLBACK` creates a deterministic request bound to:

- the approved target SHA from the manifest;
- the rejected staged candidate SHA;
- the observed `sha256_mismatch`;
- policy-visible `rollback_available=true`; and
- policy-visible integrity failure.

The request explicitly records:

- `rollback_staging_performed=false`;
- `rollback_activation_performed=false`;
- `recovery_execution_performed=false`;
- `trusted_recovery_verified=false`.

The tampered candidate remains staged throughout the WP6 observation interval, and no approved rollback artifact is placed in the simulator.

## Oracle boundary

Request construction uses policy-visible event evidence, candidate verification, and the approved manifest. It does not read immutable experiment ground truth.

## Claim boundary

WP6 establishes only that P5 creates the correct rollback request under the E3 condition.

Artifact restoration, activation, independent post-rollback verification, terminal trust, recovery success, and time to trusted recovery belong to WP7.
