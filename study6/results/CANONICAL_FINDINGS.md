# Study 6 Canonical Findings — S6-SCTR-001

## Evidence status

Study 6 is an exact finite-grid artifact-trust model. The accepted canonical execution is bound to design merge `8522b86bec64de8723ff24e0fe204cc9d6dc3998`, execution commit `f50f4db03e27e223104df96b2dd32bea85fd6319`, workflow run `33669329819`, job `100378738630`, and evidence artifact `9861838528` (artifact SHA-256 `24e3b0f8f79df383f19ff470671ad1c61738289a69c98b46f22ca2ec7e94e67d`).

The independent auditor passed with zero mismatches, all frozen output hashes matched, and the execution produced no tracked-file drift.

## Findings

1. **A valid trusted signature is insufficient to establish recovery-baseline correctness.** `G0_SIGNATURE_ONLY` rejected ordinary post-release tampering but still qualified four of the five objectively incorrect baseline states: trusted-signer compromise, trusted-builder compromise, source-review bypass, and fully approved but objectively bad source.

2. **An independent target digest closes the signer-only gap but not upstream build/source gaps.** `G1_SIGNATURE_TARGET_DIGEST` reduced unsafe qualification from four to three incorrect states by rejecting the trusted-signer-compromise state. The trusted-builder, review-bypass, and approved-bad-source states still qualified.

3. **Build provenance by itself has the same bounded safety count as signature plus independent target digest in this model.** `G2_SIGNATURE_PROVENANCE` also unsafe-qualified three of five incorrect states. This is not a claim that provenance and target-hash verification are operationally equivalent; they reject different evidence mechanisms outside this finite abstraction.

4. **Independent reproduced-build evidence closes the compromised-builder case but cannot detect identically reproducible compromised source.** `G3_PROVENANCE_REPRODUCED_BUILD` unsafe-qualified only the source-review-bypass and approved-bad-source states (2/5).

5. **Independent source-review evidence closes the review-bypass case but not a compromised trusted builder.** `G4_PROVENANCE_SOURCE_REVIEW` unsafe-qualified the trusted-builder-compromise and approved-bad-source states (2/5). Thus reproduced-build and source-review checks are complementary rather than interchangeable.

6. **The composite gate closes all modeled artifact-integrity/provenance gaps except semantic correctness of a fully approved source.** `G5_COMPOSITE` rejected post-release tampering, signer compromise, builder compromise, and source-review bypass, but still qualified `APPROVED_BAD_SOURCE` (1/5 incorrect states). In this model, therefore, provenance-qualified recovery is not equivalent to objective baseline correctness.

7. **Stronger gates introduce a clear benign assurance-availability cost.** Across all 64 subsets of unavailable assurance signals on the objectively correct baseline, the number of subsets causing rejection was 32 for G0, 48 for G1, 48 for G2, 56 for G3, 56 for G4, and 63 for G5. Every gate can therefore fail conservatively after loss of a single signal that it requires.

8. **There is no globally best gate.** The finite model exposes a safety/availability frontier. More evidence requirements reduce modeled unsafe qualification but increase sensitivity to benign evidence unavailability. The results do not justify a weighted global score or rank.

## Relationship to earlier studies

The result extends the trust-boundary pattern established by Study 2 without pooling populations. Study 2 showed that policy-visible evidence can be authenticated/current yet false under bounded producer compromise. Study 6 shows the analogous upstream artifact boundary: a recovery baseline can satisfy signature, digest, provenance, reproduced-build, review, and approval checks yet still be objectively incorrect when the approved source itself is wrong.

## Scope limitations

No malware, exploit, real supply-chain compromise, external build-system manipulation, operational spacecraft activity, RF activity, real credentials, or real signing keys were used. These are exact findings of a six-state/six-gate Boolean assurance model and do not estimate attack prevalence, operational compromise probability, spacecraft recovery latency, standards compliance, or flightworthiness.
