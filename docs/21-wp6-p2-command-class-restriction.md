# WP6 P2 — Selective Command-Class Restriction Effect

## Purpose

This treatment-mechanics probe validates that P2 can block one declared restricted command class while preserving a lower-risk command path.

The retained E1 event remains unchanged. This WP6 probe uses additional harmless Sample commands solely to test treatment selectivity.

## Why RESET COUNTERS is used

An earlier development probe used `SAMPLE_DISABLE_CC`. The pinned Sample application initializes `DeviceEnabled` to `SAMPLE_DEVICE_DISABLED`, so a fresh nominal runtime does not satisfy the successful-disable precondition. That run is debugging evidence only.

The final safe surrogate is `SAMPLE_RESET_COUNTERS_CC` (function code 1). It has no device-enabled precondition, deterministically resets application counters, and emits `SAMPLE: RESET counters command received`.

The word "high-risk" here is a treatment label required by P2 semantics, not a claim that resetting Sample counters is an operationally high-risk spacecraft command.

## Matched design

P0 and P2 use separate fresh accepted nominal NOS3 runtimes with the same E1 decision context (`M0/C0/T0`, seed 1).

Source identity is held constant as `modeled_attacker` for both probe commands:

1. `sample_reset_counters` — safe restricted-class surrogate;
2. `sample_noop` — low-risk preserved-path control.

## Expected effects

P0 forwards both commands. The reset event marker and NOOP acceptance marker must each increase by one.

P2 withholds `sample_reset_counters` but forwards `sample_noop`. The reset marker must remain unchanged while the NOOP acceptance marker increases by one.

## Important negative case

P2 intentionally does not block every command from the modeled attacker. The low-risk NOOP remains accepted.

This distinguishes selective command restriction from P1 source isolation.

## Claim boundary

This adapter validates treatment mechanics only. It does not establish a universal command-risk taxonomy, operational command authorization, final policy effect sizes, mission cost, containment latency, or trusted recovery.
