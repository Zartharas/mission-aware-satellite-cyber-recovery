# S7E-AERC-001 Result-Freeze Candidate 001 — Scientific Review

**Review ID:** `S7E-AERC-RESULT-FREEZE-REVIEW-001`  
**Candidate:** `S7E-AERC-RESULT-FREEZE-CANDIDATE-001`  
**Proposed freeze:** `S7E-AERC-RESULT-FREEZE-001`  
**Basis head:** `2e2ccbd19ecc87457f9092c5cba631ebc7e9804a`  
**Date:** 2026-09-23  
**State:** candidate prepared; explicit author result-freeze authorization required  
**Publication/result claims:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED

## 1. Scope

This review evaluates the already completed and sealed held-out execution `S7E-AERC-HELDOUT-EXEC-001`. It does not retrain, refit, tune, alter, replace, or re-execute any model or scientific scenario. It does not expand the endpoint set or population and does not activate a result freeze.

The purpose is to determine whether the existing evidence is internally consistent enough to present to the author as a result-freeze candidate while retaining adverse, null, and counterexample findings.

## 2. Live repository and CI verification

At the review basis head:

- PR #167 is open, unmerged, and mergeable.
- PR head was exactly `2e2ccbd19ecc87457f9092c5cba631ebc7e9804a` before candidate-package creation.
- repository-wide `Validate research configurations` run `35951474152` completed successfully.
- all Study-7E workflows attached to the basis head completed successfully.
- the held-out workflow remains sealed; no scientific rerun was performed.

## 3. Evidence identity and review recomputation

The execution-of-record artifact is GitHub Actions artifact `10787499194`.

- artifact SHA-256: `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`
- recomputed artifact SHA-256: identical
- artifact expiry: `2026-10-24T02:50:03Z`
- topology/fault table SHA-256: `4c24c9db4a9ce86d510df43dac7f709196af56d5cac7c769f69e07d528d95991`
- policy-decision ledger SHA-256: `ff6c3d553bf31b7dddc4c5206c9a8111795261f9466581e0757b7a782a315ce0`
- scenario-attempt ledger SHA-256: `297770841b110df02f14a25237f43c09999d8423fc434756b56e941da8dac81a`
- output-hash manifest SHA-256: `634657f75f568868504653b65558e937a3f552f62613ded03be56d9edacddead`

A separate review recomputation over the downloaded byte-exact artifact found 196 unique held-out scenarios, 784 decisions, exact E1/E2/C0 cardinalities of 84/104/8, four policies per scenario, zero invalid scenarios, zero audit mismatches, exact objective-action recomputation, equal-information pair-hash identity for every scenario, no TR0/TR1 decision records, matching endpoint counts, and matching artifact-member hashes.

No integrity discrepancy was found.

## 4. Direct finite-population observations

These are exact counts for the defined held-out population, not operational spacecraft probabilities.

| Policy | Errors | Unsafe proceed | False-conservative hold | ENTER | HOLD |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

By block, using `error / unsafe proceed / false-conservative hold`:

- E1 (unseen faults, n=84): D0 `18/3/15`; L0 `21/9/12`; D1 `24/3/21`; L1 `17/11/6`.
- E2 (held-out topologies, n=104): D0 `22/6/16`; L0 `26/12/14`; D1 `25/1/24`; L1 `26/20/6`.
- C0 (held-out-topology no-signal control, n=8): all four policies returned HOLD in all eight scenarios with zero error.

Equal-information disagreements:

- D0 versus L0: `67/196` overall, `27/84` in E1, `40/104` in E2, `0/8` in C0.
- D1 versus L1: `72/196` overall, `29/84` in E1, `43/104` in E2, `0/8` in C0.

The disagreements are not evidence of unequal information: paired input hashes are identical within each policy pair for every scenario.

## 5. Topology-controlled F6-F12 subset

To avoid confounding topology with different fault sets, the review compares the common F6-F12 subset. Each topology contributes 28 scenarios.

| Policy | T0 error/unsafe/FCH | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| D0_BASE | 6/1/5 | 6/1/5 | 6/1/5 | 6/1/5 | 6/1/5 |
| D1_CORROBORATED | 8/1/7 | 8/1/7 | 8/1/7 | 8/1/7 | 7/0/7 |
| L0_BASE | 7/3/4 | 7/3/4 | 7/3/4 | 7/3/4 | 7/3/4 |
| L1_CORROBORATED | 5/3/2 | 6/4/2 | 6/4/2 | 6/4/2 | 8/6/2 |

The base policies are topology-invariant over the common subset. Deterministic corroboration changes only at fully separated T4, removing one unsafe proceed while retaining seven false-conservative holds. Learned corroboration does not improve monotonically with separation: unsafe proceeds rise from `3/28` at T0 to `6/28` at T4.

Trust-domain separation therefore must be described as a mechanism whose policy-level effect depends on selector and fault pattern, not as an automatic safety improvement.

## 6. Common-cause and counterexample review

### F10 — primary authority compromise

For T0-T3, authority remains shared. D0 and D1 both produce `2 errors / 1 unsafe / 1 FCH` per four scenarios. At T4, D0 remains `2/1/1` while D1 becomes `1/0/1`.

This supports a deterministic common-cause interpretation: shared authority removes the corroboration unsafe-proceed advantage, while authority separation at T4 restores one unsafe-proceed reduction in this finite population.

The learned pair behaves differently: L0 and L1 are error-free at T0-T3, while at T4 L0 remains error-free and L1 incurs one unsafe proceed.

### F11 — compound authority + transport compromise

D0 and D1 both produce `1/0/1` across every topology. L0 and L1 are error-free at T0-T3; at T4, L1 incurs one unsafe proceed while L0 remains error-free. F11 therefore does not reproduce the deterministic F10 unsafe contrast.

### F12 — primary execution compromise

D0 and D1 both produce `1/0/1` across every topology. L0 remains error-free across T0-T4. L1 is error-free at T0 but incurs one unsafe proceed at each of T1-T4.

F12 is an adverse transfer counterexample: separating execution reduces domain aliasing but does not guarantee improved learned-policy output.

## 7. Research-question interpretation

### RQ1 — equal-information policy comparison

**Supported by direct observation.** D0/L0 and D1/L1 receive byte-identical policy-visible evidence within each scenario, yet disagree in 67 and 72 scenarios respectively. The within-pair differences therefore reflect selector behavior under equal information rather than an information-access advantage. This does not establish global superiority for either policy class.

### RQ2 — trust-domain separation

**Mixed result.** The architecture instantiates increasing domain separation, but policy outcomes are not monotonic with separation. D1 obtains a narrow unsafe-proceed reduction only at T4 in the common subset, while L1 moves in the opposite direction over the same topology-controlled subset.

### RQ3 — common-cause failure

**Supported with qualification.** F10 shows that deterministic corroboration provides no unsafe-proceed advantage while authority is shared at T0-T3, whereas T4 authority separation removes the D1 unsafe proceed. F11 does not show the same deterministic unsafe contrast, and the learned selector exhibits a separate adverse T4 pattern.

### RQ4 — topology/fault transfer

**Supported by direct observation.** Learned selectors behave differently across unseen-fault and held-out-topology conditions. L1 changes its error composition and exhibits adverse topology-dependent transfer in the common F6-F12 subset. C0 remains a clean no-signal control with no recovery-gate entry by any policy. No claim of improved generalization is supported.

## 8. Prespecified hypothesis disposition

| Hypothesis | Disposition | Basis |
|---|---|---|
| H1 | SUPPORTED | Equal-information hash identity plus nonzero paired disagreements separates selector behavior from policy-visible information access. |
| H2 | PARTIALLY SUPPORTED | Domain separation is instantiated and fault-confirmed, but endpoint outcomes do not improve monotonically with increasing separation. |
| H3 | PARTIALLY SUPPORTED | F10 supports deterministic shared-authority common-cause collapse and T4 recovery of one unsafe reduction; F11 and learned behavior are not universal extensions. |
| H4 | PARTIALLY SUPPORTED | Deterministic corroboration shows the expected safety/availability trade-off; learned corroboration moves in the opposite direction. |
| H5 | SUPPORTED | Learned behavior differs on unseen faults and held-out topologies, with no prespecified direction required. |

For H4, the exact corroborated-minus-base deltas are deterministic overall `unsafe -5 / FCH +14`, deterministic E2 `-5 / +8`, learned overall `+10 / -14`, and learned E2 `+8 / -8`.

## 9. Adversarial findings that must remain visible

1. Aggregate counts cannot justify a global policy ranking because unsafe proceeds and false-conservative holds trade off materially.
2. L1 has the highest aggregate unsafe-proceed count while also having the lowest aggregate false-conservative count.
3. D1 has the lowest aggregate unsafe-proceed count but the highest false-conservative count and highest total error count.
4. L1 common-subset unsafe proceeds rise with topology separation and reach `6/28` at T4.
5. F12 creates an L1 unsafe-proceed counterexample at every separated-execution topology T1-T4 while L0 remains error-free.
6. F10/F11 produce an adverse L1 T4 result even though the learned pair is error-free at T0-T3.
7. D1 adds false-conservative holds under F6 and F8 without reducing unsafe proceeds in the common subset.
8. C0 is a meaningful null result: all four policies HOLD in every no-signal control.
9. Historical freeze manifests contain immutable stage-local status text superseded by later state records; rewriting them would damage provenance.
10. The raw Actions artifact is byte-bound but temporary. Durable preservation should occur before or with result-freeze activation.

## 10. Claims not supported

The candidate must not be used to claim a global policy winner, global ML superiority, universal corroboration benefit, monotonic benefit from greater trust-domain separation, operational spacecraft probability/rate estimates, flight qualification or certification sufficiency, NASA endorsement, RF-link performance, unmeasured hardware performance, or independence beyond the instantiated experimental trust domains.

## 11. Result-freeze candidate decision

**Scientific internal consistency: PASS.**

No mismatch was found between the repository checkpoint, byte-exact artifact hashes, recomputed ledger cardinalities, validity/audit records, equal-information invariants, or exact endpoints. The evidence is suitable to present as `S7E-AERC-RESULT-FREEZE-CANDIDATE-001`, with adverse and null findings retained as part of the candidate.

This review does **not** activate `S7E-AERC-RESULT-FREEZE-001`.

Before activation:

1. obtain explicit author authorization for the result freeze;
2. durably preserve the byte-exact raw artifact before its GitHub Actions expiry, preferably in the authorized freeze change;
3. bind the activated freeze to the existing checkpoint, artifact, and member hashes;
4. retain the hypothesis dispositions and counterexamples without post-hoc reinterpretation;
5. keep PR #167 merge and manuscript/publication claim authorization as separate later gates.

## 12. Governance stop

Until explicit author result-freeze authorization is granted:

- do not activate `S7E-AERC-RESULT-FREEZE-001`;
- do not rerun `S7E-AERC-HELDOUT-EXEC-001`;
- do not retrain or alter frozen models;
- do not expand the population or endpoints;
- do not merge PR #167;
- do not write manuscript/publication result claims.
