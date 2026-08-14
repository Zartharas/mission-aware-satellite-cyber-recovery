# WP6 P0/P1 — Source-Isolation Effect Adapter

## Purpose

This adapter validates the executable effect of the first two response treatments against retained event E1. It does not estimate final policy effect sizes or containment latency.

## Matched design

P0 and P1 run in separate fresh accepted nominal NOS3 runtimes with the same E1 event instance (`M0/C0/T0`, seed 1), exact Sample NOOP packet, pinned software, isolated topology, and two synthetic source envelopes.

The research gateway receives `modeled_attacker` and `authorized_ground`. Both carry the exact E1 Sample NOOP bytes.

## Expected effects

P0 `OBSERVE_ONLY` forwards both envelopes, so both NOOPs must be accepted by cFS.

P1 `ISOLATE_MODELED_SOURCE` withholds only `modeled_attacker` while forwarding `authorized_ground`. The attacker acceptance delta must be zero and the authorized acceptance delta must be one.

## Claim boundary

`source_id` is research-owned synthetic envelope metadata. This adapter does not claim native cFS or CI_LAB identity authentication/revocation.

Policy timing, final comparative effect sizes, mission cost, and trusted recovery belong to later WP6-WP9 work.
