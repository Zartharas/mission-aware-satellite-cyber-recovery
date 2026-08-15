# WP6 P4 — Modeled Safe-Mode Command Effect

## Purpose

This adapter validates the restrictive command effect assigned to P4 and exposes its mission-preservation cost relative to P0.

It does not claim that NOS3/cFS enters a native spacecraft hardware safe mode.

## Matched design

P0 and P4 run in separate fresh accepted nominal NOS3 runtimes with the same E1 instance (`M0/C0/T0`, seed 1).

Each receives the same validated Sample NOOP packet twice:

1. from `modeled_attacker`;
2. from `authorized_ground`.

## P0

`OBSERVE_ONLY` forwards both commands:

- attacker acceptance `+1`;
- authorized acceptance `+1`;
- modeled unauthorized effect completes;
- legitimate routine-command rejection rate is `0.0`.

## P4

`ENTER_SAFE_MODE` activates a research-owned routine-command gate. For this treatment-mechanics adapter, routine external commands are withheld regardless of source:

- attacker acceptance `+0`;
- authorized acceptance `+0`;
- modeled unauthorized effect does not complete;
- legitimate routine-command rejection rate is `1.0`.

This intentionally gives P4 a stronger containment effect and a larger mission-availability cost than P1/P2.

## Claim boundary

The command gate represents the post-response effect of the P4 treatment. It is not evidence of a native cFS safe-mode state transition or an operational spacecraft safe mode.

Mission objective completion, safety-invariant outcomes, containment latency, final mission cost, and trusted recovery are measured in later work.
