# WP7 — Trusted Recovery of the Controlled Staged Candidate

## Purpose

This WP7 increment executes the recovery that WP6 deliberately stopped before performing.

The scope is the controlled E3 synthetic staged-update state. It is not an operational firmware reflash or spacecraft flight-software activation claim.

## Trust chain

The recovery requires all of the following:

1. a valid P5 `REQUEST_VERIFIED_ROLLBACK` request;
2. request binding to the rejected staged-candidate SHA;
3. request binding to the approved manifest SHA;
4. independent verification that the pre-recovery staged candidate is not trusted;
5. verification of the approved replacement source before use;
6. same-filesystem replacement through a temporary recovery path;
7. independent host-side verification of the terminal staged candidate;
8. terminal SHA equality with the approved manifest;
9. terminal SHA inequality with the rejected candidate;
10. removal of the temporary recovery object; and
11. accepted nominal runtime completion.

Only after all criteria pass is `trusted_recovery_verified=true`.

## Independent terminal verification

The executor performs the bounded copy/replace inside the isolated simulator runtime.

The terminal verifier is separate: the recovered candidate is copied from the simulator into retained evidence and verified on the host against the approved manifest.

The verifier therefore does not trust the executor's success message as proof of terminal trust.

## Negative verification

Before recovery, the same terminal verifier is applied to the staged tampered candidate and must reject it.

Unit tests additionally require a tampered replacement source to be rejected before use.

## Timing

`time_to_trusted_recovery_ms` begins immediately before the atomic replacement and ends after independent terminal verification succeeds.

This first measurement is descriptive implementation evidence only. Repeated-trial timing effects belong to the pilot and frozen campaign.

## Claim boundary

The recovered object is a non-executable synthetic mission-table artifact used by the controlled E3 model.

This increment establishes trusted recovery of that modeled staged state. It does not claim operational firmware activation, live spacecraft recovery, a final recovery success rate, or a final time-to-recovery effect.
