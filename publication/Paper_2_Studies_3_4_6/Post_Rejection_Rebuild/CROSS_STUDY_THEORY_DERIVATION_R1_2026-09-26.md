# Cross-Study Theory Derivation R1

**Status:** `READ_ONLY_DERIVATION_FROM_FROZEN_MODELS`  
**Scientific populations modified:** none

## 1. Study 3 — freshness and semantic truth

Let a policy accept an evidence record while its age is no greater than freshness lifetime `tau`.

If a truthful authorization state changes at `t0`, a pre-change record issued at `ti < t0` can remain fresh only while `t - ti <= tau`. A truthful cached record therefore creates only a bounded stale-visible interval after the hidden state changes. In Study 3, `tau = 5` logical seconds.

A compromised trusted producer is different. If it issues a new false record after `t0` with a valid signature, each false record resets the freshness age. Freshness alone therefore does not bound total false-qualification exposure by `tau`; exposure depends on record-arrival opportunities, policy semantics, and the finite horizon.

## 2. Study 4 — closed-form thresholds

Let there be `N` registered producers, provenance-domain sizes `n1,...,nm`, absolute vote threshold `q`, and minimum provenance domains `d`, with `q >= d`.

Define `L(k)` as the total size of the `k` largest domains, with `L(0)=0`.

Under Study-4 safety semantics:

`k_first_safety = q`

and

`k_systematic_safety = max(q, L(d-1) + 1)`.

For benign availability:

`k_first_availability = min(N - q + 1, N - L(d-1))`

and

`k_systematic_availability = N - q + 1`.

For frozen Study 4 (`N=7`, domains `3/2/2`), these formulas reproduce all 36 rows in `study4/results/canonical/thresholds.csv` with zero mismatches.

This characterizes the existing model class; it is not a new quorum protocol or a novelty claim for quorum theory.

## 3. Study 6 — observational equivalence

Let `E(x)` be gate-visible assurance evidence and `T(x)` research-only objective correctness. For deterministic gate `Q(E)`, if `E(x_good)=E(x_bad)` while `T(x_good) != T(x_bad)`, then `Q(E(x_good))=Q(E(x_bad))`.

In the frozen protocol, `CLEAN_APPROVED` and `APPROVED_BAD_SOURCE` are identical on all six gate-visible signals but differ in objective correctness. Every frozen gate therefore qualifies both states, leaving `APPROVED_BAD_SOURCE` as the residual incorrect state under `G5_COMPOSITE`.

This is an observability statement, not a theorem that semantic correctness is impossible in general.

## 4. Study 6 — exact benign-loss count

With `m=6` assurance signals and a gate requiring `r` signals, all `2^m` missing-signal subsets are enumerated. The subsets preserving every required signal number `2^(m-r)`; rejection therefore occurs for:

`2^m - 2^(m-r)`.

For `r=1,2,3,6`, the exact counts are `32,48,56,63`, matching the frozen gate summary.

## Manuscript implication

A clearer common statement is:

> A recovery decision cannot infer a trust property that is absent from the evidence it can observe.

The three frozen studies instantiate that statement at different layers without pooling their populations.
