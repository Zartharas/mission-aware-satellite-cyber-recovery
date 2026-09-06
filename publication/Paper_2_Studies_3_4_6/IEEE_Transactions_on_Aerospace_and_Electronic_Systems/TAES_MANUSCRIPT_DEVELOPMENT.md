# TAES Manuscript Development Control - Paper 2

**Status:** `MANUSCRIPT_DEVELOPMENT_AUTHORIZED__NOT_SUBMISSION_READY`  
**Target journal:** IEEE Transactions on Aerospace and Electronic Systems  
**Manuscript type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Core studies:** Study 3 + Study 4 + Study 6 only

## 1. Working manuscript identity

Current working title candidate:

**Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Quorums, and Artifact Assurance**

This title is not frozen. It must be reviewed against the completed manuscript, current literature, TAES discoverability, and TAES guidance before submission.

Working scientific identity:

**Layered residual trust boundaries in satellite cyber-recovery qualification.**

The term `evidence plane` remains retired from the preferred title/central contribution language unless later manuscript development demonstrates that it provides necessary precision.

## 2. Research questions

### RQ1 - Temporal qualification

Under frozen continuous and intermittent-contact schedules, how do truthful evidence, post-signature modification, and false but validly signed claims from a compromised trusted producer affect the duration and recurrence of false recovery qualification across the frozen Study-3 policy semantics?

### RQ2 - Producer composition

When recovery authorization is supported by multiple modeled evidence producers, how do absolute vote thresholds and synthetic provenance-domain requirements change first and systematic failure boundaries for unsafe qualification under producer compromise and false-conservative qualification under benign producer loss?

### RQ3 - Artifact assurance

When the recovery artifact itself is subjected to progressively composed assurance requirements, which prespecified incorrect artifact states remain qualified, and what benign qualification loss results when required assurance evidence becomes unavailable?

### Cross-study systems question

How do these independently measured residual qualification boundaries relate when satellite trusted recovery is viewed across temporal runtime evidence, producer composition, and recovery-artifact assurance?

The cross-study synthesis is qualitative and mechanism-based. It does not pool observations, create a common success rate, or estimate an end-to-end treatment effect.

## 3. Contribution architecture

### C1 - Temporal qualification boundary

Study 3 provides an exact finite characterization of false qualification caused by a compromised trusted producer across one-shot/persistent evidence and frozen continuous/intermittent contact schedules, while separating adversarial qualification from ordinary fresh-cache exposure.

### C2 - Producer-composition boundary

Study 4 provides an exact all-subset characterization of first and systematic qualification failure thresholds across 18 combinations of absolute quorum and synthetic provenance-domain requirements under separate compromise and benign producer-unavailability populations.

### C3 - Artifact-assurance boundary

Study 6 provides an exact residual-state map for signature, digest, provenance, reproduced-build, source-review, and approval requirements, together with the corresponding benign assurance-signal unavailability boundary.

### C4 - Cross-study residual-boundary synthesis

The three studies collectively support the conclusion that stronger trust composition can close or narrow specified failure pathways without automatically establishing research-only hidden or objective truth.

This is a synthesis claim, not a pooled experimental endpoint.

## 4. Frozen findings that must remain visible

### Study 3

- Persistent V5/K0 unsafe qualification occurs in 46/46 trajectories for B0 and S1, mean exposure 122.5 logical seconds.
- Persistent V5/K4 unsafe qualification remains 46/46 for B0 and S1, with lower mean exposures of approximately 55.326 and 49.022 logical seconds.
- B2 remains 0/46 in the frozen persistent-V5 cells but must not be described as universally immune or globally best.
- V4 affected records never qualify because post-signature modification invalidates the signature.
- Truthful V0/K4 B0 has a short pre-onset cache boundary in 3/46 onset phases, mean 0.326 logical seconds across the frozen grid.
- `unsafe_permissive` is not actual trusted recovery; `unsafe_qualified` is the stronger qualification endpoint.

### Study 4

- Absolute vote count establishes a basic compromise threshold.
- Synthetic provenance diversity changes which subsets can satisfy the qualification rule.
- First failure and systematic failure must be reported together where interpretation depends on both.
- Provenance effects are conditional, not monotonic.
- Q4 D1/D2, Q5 D1/D2, and the high-threshold Q6/Q7 domain variants include important null/equal-threshold results.
- The safety and availability blocks are separate. Simultaneous malicious compromise plus benign producer loss was not evaluated.
- Producer unavailability is not orbital contact loss or mission availability.

### Study 6

- G0 signature-only qualifies 4 of 5 prespecified incorrect states.
- G1 and G2 each qualify 3 of 5 incorrect states but are not operationally equivalent.
- G3 and G4 each qualify 2 of 5 incorrect states but leave different residual states.
- G5 qualifies `APPROVED_BAD_SOURCE`, 1 of 5 prespecified incorrect states.
- Benign assurance-signal loss increases as gate requirements become stricter: 32/64, 48/64, 48/64, 56/64, 56/64, and 63/64 rejected subsets from G0 through G5.
- `APPROVED_BAD_SOURCE` is a structural observability boundary of the frozen Boolean model, not an attack prevalence result or formal impossibility theorem.

## 5. Mandatory manuscript claim controls

- Only Study 3 directly models intermittent contact.
- K4 is a synthetic flapping-contact schedule, not an orbit or ground-station visibility model.
- Logical seconds are not operational spacecraft/network/operator latency.
- Study 4 provenance domains are synthetic classes, not demonstrated organizational/hardware/software independence.
- Study 4 is not a Byzantine-consensus experiment.
- Study 6 is an abstract artifact-trust model, not a real supply-chain compromise experiment.
- SLSA, TUF, SPARTA, RATS, and related standards/frameworks are prior-art/context sources, not validation or compliance claims.
- Stronger qualification may reduce selected unsafe pathways and increase conservative loss, but no global best policy/gate is supported.
- No operational attack/outage prevalence is estimated.
- No real flight, RF, energy, CPU, thermal, or mission-availability claim is supported.
- Same-repository independent audit is reproducibility, not external replication.
- The three studies do not form one integrated tested architecture.

## 6. Planned manuscript structure

1. Introduction
2. Related Work and Scientific Positioning
3. Common Trust-Qualification Framework and Study Separation
4. Study 3: Temporal Evidence Qualification
5. Study 4: Multi-Producer Qualification
6. Study 6: Recovery-Artifact Assurance
7. Cross-Study Residual Trust Boundaries
8. Validity, Aerospace Interpretation Boundaries, and Implications
9. Conclusion

Acknowledgments should include the required IEEE AI-use disclosure.

## 7. Development sequence

1. finalize literature source ledger and novelty positioning;
2. draft Related Work;
3. draft common framework and terminology;
4. draft Study-3 methods/results from frozen records;
5. draft Study-4 methods/results from frozen records;
6. draft Study-6 methods/results from frozen records;
7. draft cross-study synthesis;
8. draft limitations and aerospace implications;
9. complete conclusion;
10. rewrite abstract after the complete manuscript is stable;
11. create TAES two-column source and PDF;
12. perform scientific, citation, formatting, and visual QA;
13. decide supplementary snapshot;
14. freeze upload files and portal values;
15. obtain explicit final author authorization before submission.

## 8. No-silent-correction rule

If manuscript development exposes a genuine scientific inconsistency in a frozen result, stop and document the defect. Do not silently change frozen evidence, rerun a study, or revise an output merely to make the manuscript internally convenient.
