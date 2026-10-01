# Paper 2 Rebuild R3 — S6X Manuscript-Ready Inserts

These passages are for the post-rejection R3 candidate only. R2 and the historical TAES R10 submission remain immutable.

## Abstract insertion

A separate S6X executable stress test instantiates the Study-6 residual with pinned NASA cFS/LC source and a controlled signed-integer equality-boundary fixture. Across two complete repetitions and eight governed builds, clean and altered-source artifacts were reproducible within state and distinct across state. The frozen research harness distinguished objective correctness (clean `native_std.runtest` RC 0; controlled bad-source RC 2), while the S6X evidence record held all six Study-6-aligned qualification signals true for both states. The two 396-observation repetitions had zero primary/reference evaluator mismatches and byte-identical canonical outputs. S6X is a separate executable stress test, not an external empirical replication of Study 6.

## RQ3 executable-stress-test paragraph

S6X instantiates the Study-6 residual mechanism with a pinned NASA cFS v7.0.1 / Limit Checker source tree. A researcher-controlled fixture changes the signed-integer `GT` equality boundary from `>` to `>=`, while a frozen research harness checks that `0 > 0` remains false. The clean and controlled bad-source variants each reproduced byte-identically between primary and rebuild instances in both repetitions, and the two artifact identities remained distinct. Under the augmented `native_std.runtest` execution, CLEAN_APPROVED returned RC 0 and APPROVED_BAD_SOURCE returned RC 2.

That functional result is deliberately not one of the six qualification-gate signals. In the S6X experimental evidence record, both CLEAN_APPROVED and APPROVED_BAD_SOURCE have signature validity, target-digest match, provenance validity, reproduced-build match, source-review attestation, and release approval set true. Consequently, all six frozen Study-6 gates qualify both states even though the external research adjudication marks the controlled bad-source state incorrect. Block A contains 12 state-by-gate observations; Block B separately contains 384 clean-artifact assurance-unavailability observations. Both repetitions produced 396 observations with zero primary/reference evaluator mismatches and independent validation PASS.

## RQ3 answer replacement

Progressively composed assurance evidence removes specific incorrect artifact states, but the residual state depends on which property is visible to the gate. Study 6 leaves APPROVED_BAD_SOURCE after the six-signal composite because semantic correctness remains outside the observation set. S6X separately instantiates that mechanism with executable cFS/LC artifacts: a frozen functional harness distinguishes the clean and controlled bad-source variants, while the six Study-6-aligned qualification signals remain observationally equivalent. The result does not pool S6X with Study 6 and does not make the functional test a seventh gate signal; it shows that functional correctness can affect the research-only adjudication without affecting a qualification rule that is not allowed to observe it.

## Validity paragraph

S6X is bounded to one pinned cFS v7.0.1 / Limit Checker source identity, one signed-integer GT/GE equality-boundary fixture, one frozen Linux/amd64 build environment, and research-only signing, review, and approval metadata. It does not establish a vulnerability in cFS or Limit Checker, NASA certification status, flightworthiness, mission readiness, production supply-chain assurance, or arbitrary aerospace-software correctness. The executed `native_std.runtest` path includes the frozen research equality-boundary harness; therefore the RC 0/RC 2 contrast must not be described as a property of the unmodified upstream test suite. The functional test/harness is research-only objective adjudication and is deliberately outside the six qualification-gate signals.

## Reproducibility paragraph

Campaign 004 completed two deterministic repetitions, each with four governed builds and 396 gate observations. CLEAN_APPROVED and APPROVED_BAD_SOURCE each reproduced to stable within-state artifact hashes, the clean and altered artifacts remained distinct, primary and reference gate evaluators had zero mismatches, independent validation passed, repeated build/test records matched, and all five canonical result files were byte-identical across repetitions. These controls support repository reproducibility of the S6X mechanism; they are not independent human or external replication.

## Figure decision

Do not revise Figure 1 for S6X. Use a compact RQ3 Table V instead. S6X validates the existing Study-6 residual-observability concept rather than adding a new conceptual layer.
