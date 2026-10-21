# Paper 2 S6X — Frozen-Result Interpretation and Manuscript Claim-Use Review

**Experiment:** `S6X-EAP-001`  
**Canonical campaign:** `S6X_CANONICAL_EXECUTION_004`  
**Effective result freeze:** `S6X-CANONICAL-RESULT-FREEZE-004`  
**Effective freeze main:** `2ddbd795c4734654f421616de996911fa62ee27a`  
**Post-merge CI:** #1314 / run `36808689393` — SUCCESS  
**Status:** interpretation and R3 claim-use package prepared; merge still requires separate author review.

## 1. Interpretation boundary

This phase does not rerun, retune, or modify S6X, Study 6, or any historical Paper-2 package. It interprets only the already-frozen Campaign-004 evidence.

S6X remains a **separate executable stress test of the Study-6 observability mechanism**. It does not add rows to Study 6 and is not an external empirical replication.

The central distinction is between the **six qualification-gate signals** inherited from Study 6 and the **research-only functional adjudication** supplied by the equality-boundary harness. The functional test result is deliberately outside the gate. The controlled bad-source variant returned a nonzero test result even though its S6X experimental evidence record represents all six gate-visible assurance signals as true.

## 2. Exact executable findings eligible for R3

### F1 — Reproducible but distinct artifact identities

Campaign 004 completed eight governed builds: clean primary/rebuild and bad-source primary/rebuild in each of two repetitions. The clean artifact SHA-256 was stable across all clean builds:

`7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670`

The approved-bad-source artifact SHA-256 was stable across all altered-source builds:

`275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c`

The clean and altered artifacts were distinct.

### F2 — The frozen functional harness distinguishes the controlled source change

The controlled fixture changes the signed-integer `GT` equality boundary from `WPValue > CompareValue` to `WPValue >= CompareValue`. The research harness evaluates the equality case `0 > 0` as false.

Under the frozen augmented `native_std.runtest` execution:

- CLEAN_APPROVED returned RC 0;
- APPROVED_BAD_SOURCE returned RC 2.

This is evidence about the single controlled fixture and frozen harness. It is not a discovered cFS/LC vulnerability and not evidence that the unmodified upstream test suite would necessarily detect or miss the change.

### F3 — Six-signal observational equivalence remains at the qualification boundary

For Block A, the S6X evidence record represents all six Study-6-aligned assurance signals as true for both CLEAN_APPROVED and APPROVED_BAD_SOURCE. Because every frozen gate is composed only from subsets of those six signals, all six gates qualify both states. The external functional adjudication distinguishes objective correctness, but that result is not supplied to the gate.

Block A contains 12 observations: two artifact states crossed with six gates. Primary and separately implemented reference evaluators agree on every row.

### F4 — Benign unavailability replay remains separate

Block B uses CLEAN_APPROVED only and enumerates all 64 unavailable-signal masks under each of the six gates, yielding 384 observations. This block checks gate semantics under missing assurance evidence; it does not estimate operational outage probabilities.

### F5 — Deterministic repeatability

Each repetition contains 396 observations: 12 Block-A plus 384 Block-B rows. Both repetitions passed independent validation with zero gate-evaluator mismatches. Their build/test records matched, and all five canonical result files were byte-identical across repetitions.

## 3. RQ3 interpretation

**S6X executable evidence supports the same residual-observability mechanism identified by Study 6. A process can produce reproducible, signed, provenance-bound, reviewed, and approved experimental evidence for a controlled source-derived artifact while objective functional correctness is adjudicated separately. If that correctness signal is not included in the qualification observation set, the six-signal gate cannot use it to distinguish the clean and controlled bad-source states.**

This is an observability result, not an indictment of process assurance. It means that a qualification rule can act only on signals it is defined to consume.

## 4. Relationship to frozen Study 6

Study 6 remains the authoritative 420-observation Boolean experiment. S6X does not mutate or enlarge it.

S6X narrows the evidentiary gap by instantiating one residual state with pinned NASA cFS/LC source, a researcher-controlled equality-boundary fixture, reproducible builds, research-only signing/attestations, and an external functional harness. That makes S6X useful as an executable stress test of the mechanism, but not as an external empirical replication of Study 6.

## 5. Display decision

A new Figure-1 revision is **not warranted**. The existing Study-6 panel already depicts the residual `APPROVED_BAD_SOURCE` observability boundary. S6X validates that same conceptual boundary rather than introducing another independent layer. Adding a second inset would increase visual density and risk implying another peer study.

R3 should instead add one compact **Table V** in RQ3 summarizing eight governed builds, artifact reproducibility, functional adjudication, the 12-row Block A, the 384-row Block B, zero evaluator mismatches, and deterministic repeatability.

## 6. Claims withheld

R3 must not claim external empirical replication of Study 6; Study-6/S6X pooling; a NASA cFS or LC vulnerability; flightworthiness, mission readiness, certification, or production assurance; real attacker/supplier compromise; that the unmodified upstream test suite misses the fixture; that research attestations equal operational independent review; that the functional-test result is one of the six qualification signals; operational risk probabilities; or global gate rankings.

## 7. Manuscript-use decision

Claims F1–F5 and the bounded RQ3 synthesis are eligible for a new **R3 post-rejection manuscript candidate**. R2 and the historical TAES R10 package remain immutable.

## Next gate

`AUTHOR_REVIEW_AFTER_S6X_INTERPRETATION_CLAIM_USE_AND_R3_PR_AND_PREMERGE_CI_BEFORE_MERGE`
