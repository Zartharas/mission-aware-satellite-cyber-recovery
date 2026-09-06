# VII. Cross-Study Residual Trust Boundaries

## A. Scope of the Synthesis

Studies 3, 4, and 6 were designed, executed, and frozen as separate experiments. Their populations, mechanisms, and endpoints are not pooled in this section. The purpose of the synthesis is narrower: to compare what each experiment shows about a recovery-qualification decision that depends on policy-visible evidence while some relevant truth remains outside the gate's direct observation set.

This layered interpretation was developed after the individual studies were frozen. It is therefore a manuscript-level systems synthesis, not a prospectively tested integrated architecture or a fourth experiment. No end-to-end recovery probability, combined success rate, common effect size, or pooled statistical population is defined.

## B. Three Distinct Qualification Layers

The three studies expose residual boundaries at different points in a recovery decision chain.

Study 3 operates at the **temporal runtime-evidence layer**. The gate observes record properties such as signature validity, freshness, and policy-visible authorization evidence while research-only authorization truth can change independently. Its principal residual boundary appears when a trusted producer continues to issue fresh and validly signed false evidence. A smaller nonadversarial boundary appears when a truthful pre-onset record remains fresh briefly after hidden authorization changes.

Study 4 operates at the **producer-composition layer**. The gate observes signed producer claims, total vote count, and synthetic provenance-domain representation. Hidden authorization truth is fixed separately in the malicious-compromise and benign-unavailability blocks. The residual boundary depends on which producer subsets can satisfy the rule, and provenance requirements can change systematic failure even when the first possible failure count is unchanged.

Study 6 operates at the **recovery-artifact assurance layer**. The gate observes selected artifact-assurance signals while objective baseline correctness remains a research-only oracle. Stronger gates close specific modeled signer, builder, review, or post-release tamper states, but the fully approved bad-source state remains qualified because every gate-visible signal is true.

### Table V. Cross-study residual-boundary comparison

| Layer | Study | What the gate can observe | Research-only truth outside the gate | Principal residual boundary | Effect of stronger composition in frozen model |
|---|---|---|---|---|---|
| Temporal runtime evidence | Study 3 | Signature validity, freshness, received authorization evidence, contact-dependent record availability, security signal | Hidden authorization truth | Fresh valid evidence can remain false; truthful cache can briefly lag a state change | Contact-aware restriction reduces selected K4 exposure but does not eliminate persistent V5 qualification for B0/S1 |
| Producer composition | Study 4 | Signed claims, vote threshold, synthetic provenance-domain count | Hidden authorization truth | Some compromised subsets satisfy the rule while others of the same size do not | Provenance can delay systematic unsafe qualification but can also cause earlier false-conservative rejection |
| Recovery artifact | Study 6 | Signature, digest, provenance, reproduced-build, review, approval | Objective baseline correctness | All visible assurance signals can be true for `APPROVED_BAD_SOURCE` | Additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss |

Table V is a qualitative comparison. The rows do not share a common measurement scale, and no numeric outcome is combined across them.

## C. Integrity and Authenticity Do Not Exhaust Semantic Trust

The strongest common pattern is the distinction between evidence integrity and the semantic truth needed for a recovery decision.

Study 3 makes this distinction directly through the contrast between `V4` and `V5`. Post-signature alteration in `V4` invalidates the signature, and the affected record never qualifies. In `V5`, the false record is validly signed by the trusted producer and can remain qualified. The experiment therefore separates detectable record alteration from false content generated inside the modeled trust boundary.

Study 6 shows an analogous upstream distinction. Signature-only qualification rejects ordinary post-release tampering but cannot identify several prespecified incorrect artifacts whose visible signature state remains valid. Additional digest, provenance, reproduced-build, review, and approval signals close more of those modeled states. Even the composite gate, however, cannot distinguish `APPROVED_BAD_SOURCE` because the research-only correctness failure is not represented in any visible signal.

These results do not imply that signatures, provenance, or other assurance mechanisms are ineffective. Each closes specific modeled failure pathways. The narrower implication is that an assurance property can establish only the property represented by the evidence and trust anchors on which it depends. A policy cannot infer a research-only semantic truth solely because the visible evidence is authentic, fresh, or process-conformant.

## D. Composition Moves the Boundary Rather Than Producing Universal Dominance

The three studies also caution against interpreting additional evidence requirements as a universally monotonic improvement.

In Study 4, adding provenance-domain requirements can substantially delay systematic unsafe qualification for selected vote thresholds. `Q3_D3`, for example, moves systematic safety failure from three compromised producers under `Q3_D1` to six while leaving first failure at three. That added constraint also makes benign false-conservative rejection possible after only two unavailable producers instead of five. Other provenance additions produce no threshold change, including `Q4_D1` versus `Q4_D2`, `Q5_D1` versus `Q5_D2`, and all domain variants at `Q6` and `Q7`.

Study 6 shows a related but distinct frontier. Adding assurance signals reduces the number of prespecified incorrect artifact states that remain qualified, from four under signature-only checking to one under the six-signal composite gate. The number of benign assurance-unavailability subsets causing rejection rises from 32 of 64 to 63 of 64. Equal aggregate counts can also conceal different residual mechanisms, as shown by the different state sets left by `G3` and `G4`.

Study 3 does not contain the same benign-unavailability endpoint and therefore is not folded into a common safety-versus-availability statistic. Its evidence-aware/contact-aware policy can reduce modeled exposure in selected K4 comparisons, but the study does not support a cross-study claim that every stronger policy produces the same type of availability tradeoff.

The common systems lesson is therefore conditional: adding structure to qualification can close or narrow selected failure regions, but the resulting residual boundary depends on which evidence dimensions are added and which failure assumptions remain outside the gate.

## E. First Failure, Systematic Failure, and Residual-State Identity

A second cross-study insight is that aggregate counts alone can hide the mechanism that remains.

Study 4 distinguishes first failure from systematic failure because subset composition matters. A three-producer compromise under `Q3_D3` can be sufficient if all three provenance domains are represented, but other three-producer subsets remain blocked. The first threshold therefore describes possibility, whereas the systematic threshold describes inevitability across subsets of that size.

Study 6 provides the analogous lesson in state identity. `G3` and `G4` each qualify two of five incorrect states, but `G3` leaves `SOURCE_REVIEW_BYPASS` while `G4` leaves `TRUSTED_BUILDER_COMPROMISE`; both leave `APPROVED_BAD_SOURCE`. The equal count does not make the gates equivalent.

Study 3 similarly benefits from origin identity. The same generic endpoint, unsafe qualification, can arise from a truthful pre-onset cache record or from a false record generated by the compromised trusted producer. The prespecified origin decomposition prevents these mechanisms from being merged.

Across the three studies, the identity of the residual mechanism is therefore as important as the count or duration of the residual state. This is why the manuscript emphasizes origin, subset structure, and surviving artifact states rather than collapsing results into a single scalar measure.

## F. Observability as the Common Constraint

The common abstraction can be stated in terms of observability. A recovery gate evaluates only what has been represented in its policy-visible evidence.

In Study 3, hidden authorization truth is intentionally unavailable to the selector. A compromised trusted producer can therefore produce a valid visible claim that disagrees with hidden truth. The gate can reject an invalid signature, but it cannot directly observe that the trusted signer is semantically lying.

In Study 4, the gate observes producer claims and structural provenance labels, not an oracle identifying which producers are compromised. Quorum and provenance rules change how many and which visible claims are required, but qualification still depends on the assumed relationship between producer identity, provenance class, and trustworthiness.

In Study 6, the gate observes assurance signals rather than objective correctness. When `APPROVED_BAD_SOURCE` makes every visible assurance signal true, the gate has no frozen variable that distinguishes the artifact from the objectively correct state.

This does not establish a universal impossibility result. It identifies a model-specific principle: within each frozen experiment, a mismatch that is not represented in policy-visible evidence cannot be corrected by rearranging evidence that remains observationally identical with respect to that mismatch.

## G. Aerospace Systems Implications

The experiments do not evaluate a deployed spacecraft architecture, but they identify several design questions relevant to aerospace information systems.

First, recovery requirements should distinguish **evidence integrity** from **evidence authority and semantic trust**. A design that checks only whether evidence is signed and fresh should document what assumptions are made about the signer remaining semantically trustworthy.

Second, multi-source recovery evidence should state what producer diversity is intended to represent. Study 4 uses synthetic provenance domains precisely because real independence was not measured. An operational architecture would need to justify whether producer diversity corresponds to separate organizations, software stacks, hardware roots, sensing paths, administrative authorities, supply chains, or some other failure-separation assumption.

Third, evidence requirements should be evaluated together with the conditions under which required evidence may be unavailable. Studies 4 and 6 show that stricter qualification can reduce selected unsafe states while increasing false-conservative rejection under their respective benign-loss models. In an operational mission, the acceptable balance would depend on mission phase, hazard state, autonomy requirements, and available recovery alternatives. Those mission tradeoffs were not measured here.

Fourth, recovery-artifact assurance should identify the highest-level trust assumption that remains outside the gate. Provenance, reproduced builds, source review, and release approval each provide useful evidence, but a system still needs a justified basis for trusting the process or authority that ultimately defines acceptable source and behavior.

These are design implications, not prescriptive flight requirements. The studies provide finite-model evidence about qualification boundaries, not evidence that a particular spacecraft architecture, quorum size, contact policy, or artifact gate should be adopted operationally.

## H. Synthesis Result

Taken together, the three studies support a layered residual-trust interpretation of satellite cyber-recovery qualification. Temporal evidence qualification can fail when fresh, authentic evidence diverges from hidden authorization truth. Producer composition can shift the subset boundary at which false claims satisfy a recovery rule, with conditional gains and benign-loss costs from provenance requirements. Artifact assurance can close selected integrity and process failures while leaving a residual state that is indistinguishable under the frozen visible signals.

The synthesis therefore does not identify a globally best policy, quorum, or gate. Its contribution is to make the residual assumption explicit at each layer. Stronger evidence composition can move or narrow a qualification boundary, but it does not automatically convert policy-visible trust evidence into direct observation of hidden or objective truth.
