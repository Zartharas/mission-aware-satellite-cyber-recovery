# IV. Temporal Evidence Qualification Under Intermittent Contact

## A. Study Question and Design

Study 3 (`S3-K4E-001`) evaluates when runtime recovery evidence remains policy-qualified after research-only authorization has changed. It varies contact availability, evidence semantics, and whether an affected post-onset record occurs once or persists. The model is deterministic and uses logical time rather than wall-clock or flight time.

The horizon is 240 logical seconds in five-logical-second epochs, with five logical seconds of evidence validity. The onset grid contains 46 prespecified phases from 10 through 235 logical seconds in five-second increments. Hidden authorization is `true` before onset and `false` at and after onset; the post-onset security signal is `true`. Hidden authorization is never supplied to the selector.

`K0` provides continuous modeled contact from 0 through 240. `K4` provides synthetic windows `[25,35]`, `[75,90]`, `[145,165]`, and `[220,240]`. New records arrive only during modeled contact; otherwise the selector can use the latest received record subject to freshness. K4 is a deterministic contact treatment, not an orbital pass schedule or operational-access estimate.

The evidence treatments are:

1. `V0`: truthful evidence. A post-onset record reports authorization `false` with a valid signature.
2. `V4`: post-signature value manipulation. The signed post-onset value is changed from `false` to `true`, invalidating the signature.
3. `V5`: compromised trusted-producer evidence. The producer reports authorization `true` while hidden truth is `false`, and validly signs the false claim.

`V4` and `V5` are each evaluated as one-shot and persistent treatments; `V0` remains truthful. The frozen policy semantics are `S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`. The identifiers reuse frozen selector semantics, but no Study-2 result is imported. Thirty cells crossed with 46 onset phases yield 1,380 trajectories and 67,620 epoch states. The trajectory is the study unit; epochs within a trajectory are repeated model states.

## B. Endpoints and Origin Decomposition

Primary endpoints are `unsafe_permissive_epoch_rate`, `unsafe_qualified_epoch_rate`, `unsafe_qualified_exposure_s`, `unsafe_qualified_episode_count`, `protective_epoch_rate`, and `action_transition_count`. This paper emphasizes `unsafe_qualified`: the gate is policy-visible qualified while hidden authorization is false. `unsafe_permissive` is only a selector or gate-entry action metric, not completed recovery.

False-qualified epochs must map to one of two prespecified origins. `PRE_ONSET_CACHE` is a truthful record received before onset that remains policy-fresh afterward; `V5_AFFECTED_RECORD` is a validly signed false record from the compromised trusted producer. This separates ordinary freshness lag from adversarial semantic falsity. Because the frozen onset grid is complete, results are exact finite-grid summaries and paired phase differences, with no p-value gate, weighted policy score, or global policy rank.

## C. Persistent False-but-Valid Evidence Under Continuous Contact

Under persistent `V5/K0`, both `B0` and `S1` were unsafe-qualified in all 46 onset trajectories, with mean exposure 122.5 logical seconds. `B2` remained 0/46 with zero mean exposure in this frozen cell. The V5 records are validly signed; the mismatch exists because the trusted producer itself signs a claim that is false relative to hidden authorization. Signature validity therefore authenticates the modeled producer and record integrity without exposing producer-origin semantic falsity.

The `B2` zero is structural to the frozen policy and treatment grid, not evidence of universal immunity or global superiority.

## D. Persistent V5 Under the Frozen K4 Contact Schedule

Under persistent `V5/K4`, `B0` remained unsafe-qualified in 46/46 trajectories with mean exposure 55.326 logical seconds and a 55.0-logical-second increment over truthful `V0`. `S1` remained unsafe-qualified in 46/46 with mean exposure 49.022 logical seconds, equal to its V5-attributable increment. `B2` remained 0/46. The B0-S1 mean difference was approximately 6.304 logical seconds, so the frozen S1 contact-aware restriction reduced exposure relative to B0 but did not eliminate the V5 boundary.

### Table II. Selected Study-3 residual-boundary results

| Evidence / contact / policy | Unsafe-qualified trajectories | Mean unsafe-qualified exposure, logical s | Interpretation |
|---|---:|---:|---|
| Persistent `V5`, `K0`, `B0` | 46/46 | 122.500 | Sustained false qualification under continuous contact |
| Persistent `V5`, `K0`, `S1` | 46/46 | 122.500 | Same continuous-contact exposure in frozen grid |
| Persistent `V5`, `K0`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Persistent `V5`, `K4`, `B0` | 46/46 | 55.326 | Reduced modeled exposure, not elimination |
| Persistent `V5`, `K4`, `S1` | 46/46 | 49.022 | Additional K4 restriction relative to B0, not immunity |
| Persistent `V5`, `K4`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Truthful `V0`, `K4`, `B0` | 3/46 | 0.326 | Pre-onset cache boundary, not adversarial evidence |
| Truthful `V0`, `K4`, `S1` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |
| Truthful `V0`, `K4`, `B2` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |

K4 mechanically limits record reception under the registered cache semantics; the result does not establish that intermittent contact improves security. Table II values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.

## E. Post-Signature Manipulation and the Cryptographic Boundary

Under `V4`, post-signature modification invalidates the affected record's signature, and affected V4 records never qualify. Any B0/K4 false qualification in V4 cells comes instead from a previously received truthful record and is assigned to `PRE_ONSET_CACHE`, not to the manipulated record.

The V4-V5 contrast therefore supports two bounded claims: signature validation rejects the modeled post-signature alteration, while a valid signature alone does not establish semantic truth when the trusted producer signs the false claim. The experiment does not evaluate cryptanalysis, key extraction, or a real signing-system attack.

## F. Freshness and the Truthful Cache Boundary

Under truthful `V0/K4/B0`, 3/46 onset trajectories contained unsafe qualification, with mean exposure 0.326 logical seconds, all attributed to `PRE_ONSET_CACHE`. `S1` and `B2` had no truthful-V0 false qualification under K4. The result is schedule-, epoch-, freshness-, and policy-specific and is not an estimate of spacecraft cache staleness. It demonstrates that ordinary freshness lag can produce false qualification without being conflated with V5 producer-origin false evidence, consistent with RFC 9334's freshness limitation [5].

## G. One-Shot V5 and Temporal Persistence

One-shot `V5/K0` produced five logical seconds of mean unsafe-qualified exposure for both `B0` and `S1` across all 46 onset phases. Under K4, all 46 B0 and S1 trajectories eventually received the one-shot compromised record; S1 retained five logical seconds of V5 exposure, while B0 also contains the separately identified cache boundary. One-shot and persistent V5 are cryptographically the same false-but-valid producer claim; persistence determines whether the claim appears once or is renewed after later contact.

## H. Study-3 Residual Trust Boundary

Study 3 therefore separates two residual boundaries: brief truthful freshness lag and false but validly signed evidence from a compromised trusted producer. Contact-aware restrictions reduce selected K4 exposure but do not eliminate persistent V5 qualification for `B0` or `S1`. These are exact properties of the frozen grid, not estimates of compromise prevalence, unsafe-recovery probability, operational mission risk, or real spacecraft timing.
