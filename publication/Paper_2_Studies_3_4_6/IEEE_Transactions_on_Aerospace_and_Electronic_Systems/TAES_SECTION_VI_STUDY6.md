# VI. Recovery-Artifact Assurance and Residual Incorrect States

## A. Study Question and Model Boundary

Study 6 (`S6-SCTR-001`) moves the trust question upstream from runtime authorization evidence to the recovery artifact itself. The study asks when artifact-provenance and release-verification gates can still qualify an objectively incorrect recovery baseline, and what benign qualification cost is introduced when stronger gates require more assurance signals.

The experiment is an exact finite Boolean assurance model. It does not implement malware, an exploit, a real software-supply-chain compromise, a production build system, real signing keys, or an operational spacecraft recovery pipeline. The artifact states and assurance signals are prespecified model variables. SLSA, TUF, SPARTA, and related assurance concepts motivate the selected dimensions but do not validate the model or establish standards compliance.

The research-only oracle is `objective_baseline_correct`. It identifies whether the modeled recovery artifact is objectively correct, but it is never provided to an assurance gate. A gate sees only its required policy-visible assurance signals.

## B. Artifact States and Assurance Signals

The frozen model contains six artifact states. `CLEAN_APPROVED` is objectively correct and has all six visible assurance signals true. Five states are objectively incorrect:

1. `POST_RELEASE_TAMPER`: signature, digest, provenance, and reproduced-build signals are false, while review and approval remain true.
2. `TRUSTED_SIGNER_COMPROMISE`: the signature remains valid, but independent digest, provenance, and reproduced-build signals are false; review is true and release approval is false.
3. `TRUSTED_BUILDER_COMPROMISE`: signature, digest, provenance, review, and approval are true, while independent reproduced-build match is false.
4. `SOURCE_REVIEW_BYPASS`: signature, digest, provenance, reproduced-build, and approval are true, while source-review attestation is false.
5. `APPROVED_BAD_SOURCE`: all six gate-visible assurance signals are true while objective baseline correctness is false.

The six visible assurance signals are:

- `signature_valid`;
- `independent_target_digest_match`;
- `provenance_valid`;
- `independent_reproduced_build_match`;
- `source_review_attested`;
- `release_approved`.

Terms such as "independent" in the signal names are part of the frozen abstraction. They do not establish that different real organizations, hardware roots, networks, or build infrastructures were used.

## C. Assurance Gates and Exact Population

Six deterministic gates compose these signals in progressively different combinations:

- `G0_SIGNATURE_ONLY`: signature validity;
- `G1_SIGNATURE_TARGET_DIGEST`: signature plus independent target digest;
- `G2_SIGNATURE_PROVENANCE`: signature plus provenance;
- `G3_PROVENANCE_REPRODUCED_BUILD`: signature, provenance, and reproduced-build match;
- `G4_PROVENANCE_SOURCE_REVIEW`: signature, provenance, and source-review attestation;
- `G5_COMPOSITE`: all six visible signals.

The experiment has two separate blocks. Block A crosses all six artifact states with all six gates, producing 36 observations. The key endpoint is `unsafe_qualified`, which is true when a gate qualifies an objectively incorrect artifact state.

Block B uses only the objectively correct `CLEAN_APPROVED` baseline and exhausts all 64 subsets of unavailable assurance signals across all six gates. This produces 384 observations. The endpoint `benign_availability_loss` is true when the gate rejects the correct baseline because one or more required assurance signals are unavailable.

The full frozen population is therefore 420 exact observations. The adversarial artifact-state block and the benign assurance-unavailability block are separate. The study does not model a compromised artifact and assurance-signal loss occurring simultaneously.

## D. Signature-Only Qualification Leaves Four Incorrect States

`G0_SIGNATURE_ONLY` requires only a valid signature. It rejects `POST_RELEASE_TAMPER`, where the modeled signature is invalid, but qualifies the other four incorrect states: `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`.

The result is 4 of 5 prespecified incorrect states qualified under the signature-only gate. This ratio is not a detection rate, false-negative rate, or estimate over a real attack population. The five incorrect states are a deliberately constructed finite set, not a sample from software-supply-chain incidents.

The result supports a narrower systems interpretation: signature validity can establish the modeled integrity/authenticity property required by `G0`, but cannot by itself establish objective recovery-baseline correctness when the signer or upstream production process is inside the modeled trust boundary.

## E. Digest and Provenance Close the Signer-Only Gap but Leave Upstream States

`G1_SIGNATURE_TARGET_DIGEST` adds independent target-digest match. It rejects both `POST_RELEASE_TAMPER` and `TRUSTED_SIGNER_COMPROMISE`, reducing unsafe qualification to three states: `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`.

`G2_SIGNATURE_PROVENANCE` also qualifies three of the five incorrect states, and in this frozen state set the same three states remain qualified. This equal aggregate count and equal residual set do not establish operational equivalence between independent target-digest verification and provenance verification. The gates represent different assurance mechanisms, and the finite state model does not enumerate every condition under which those mechanisms could diverge.

The relevant result is therefore bounded: either added signal closes the modeled signer-only state while leaving the upstream builder, review, and fully approved bad-source states visible as qualified under this abstraction.

## F. Reproduced-Build and Source-Review Gates Are Complementary

`G3_PROVENANCE_REPRODUCED_BUILD` requires signature validity, provenance validity, and an independent reproduced-build match. It rejects the trusted-builder-compromise state in addition to the post-release-tamper and trusted-signer-compromise states. Two incorrect states remain qualified: `SOURCE_REVIEW_BYPASS` and `APPROVED_BAD_SOURCE`.

`G4_PROVENANCE_SOURCE_REVIEW` also qualifies two of the five incorrect states, but the residual set is different. It qualifies `TRUSTED_BUILDER_COMPROMISE` and `APPROVED_BAD_SOURCE`, while rejecting `SOURCE_REVIEW_BYPASS`.

The equal 2-of-5 counts therefore conceal different trust boundaries. Reproduced-build evidence closes the modeled builder-compromise pathway but does not detect a source-review bypass if the resulting artifact remains reproducible. Source-review evidence closes the modeled review-bypass pathway but does not detect the trusted-builder state when the required review signal remains true. These gates are complementary in the frozen model rather than interchangeable.

## G. Composite Assurance Leaves the Approved-Bad-Source Boundary

`G5_COMPOSITE` requires all six visible assurance signals. It rejects `POST_RELEASE_TAMPER`, `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, and `SOURCE_REVIEW_BYPASS`. The only prespecified incorrect state that remains qualified is `APPROVED_BAD_SOURCE`.

This state is deliberately important. All six gate-visible signals are true, including signature, independent digest, provenance, reproduced-build match, source-review attestation, and release approval, while the research-only objective-correctness oracle is false. The gate therefore has no visible signal on which to reject the state.

The result should not be overstated. `APPROVED_BAD_SOURCE` is a structural observability boundary of the frozen model, not an information-theoretic impossibility result. The study does not prove that no assurance mechanism could detect bad source. A different model could include additional evidence, such as independent semantic validation, formal verification, behavioral testing, or other assurance signals. Those signals were not part of the frozen Study-6 design and are not added post hoc to remove the residual state.

The result also overlaps conceptually with established supply-chain guidance. SLSA v1.2 explicitly recognizes that an intentionally malicious software producer cannot be directly mitigated through SLSA controls and that the consumer must establish a basis for trusting the producer [12]. The contribution here is therefore not the discovery of that principle. It is the exact residual-state mapping of the frozen recovery-artifact gate composition.

## H. Exact Gate Frontier

Table IV reports the canonical gate summary. The unsafe count is the number of the five prespecified incorrect states that remain qualified. The benign-loss count is the number of the 64 unavailable-signal subsets that cause the objectively correct baseline to be rejected.

### Table IV. Study-6 residual incorrect states and benign assurance loss

| Gate | Required visible signals | Incorrect states still qualified | Unsafe count | Benign-loss subsets |
|---|---:|---|---:|---:|
| `G0_SIGNATURE_ONLY` | 1 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE`; `TRUSTED_SIGNER_COMPROMISE` | 4/5 | 32/64 |
| `G1_SIGNATURE_TARGET_DIGEST` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G2_SIGNATURE_PROVENANCE` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G3_PROVENANCE_REPRODUCED_BUILD` | 3 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS` | 2/5 | 56/64 |
| `G4_PROVENANCE_SOURCE_REVIEW` | 3 | `APPROVED_BAD_SOURCE`; `TRUSTED_BUILDER_COMPROMISE` | 2/5 | 56/64 |
| `G5_COMPOSITE` | 6 | `APPROVED_BAD_SOURCE` | 1/5 | 63/64 |

For every gate, loss of a single signal that the gate requires is sufficient to produce benign rejection in at least one unavailable-signal subset. The minimum missing-signal count for benign loss is therefore one for all six gates.

Again, the denominators in Table IV are finite model populations. `1/5` must not be interpreted as a 20 percent residual attack rate, and `63/64` must not be interpreted as a 98.4 percent operational outage probability. They describe how many prespecified model states or signal-unavailability subsets cross a deterministic qualification rule.

## I. Stronger Gates Increase Sensitivity to Benign Assurance Loss

The benign block exposes the cost of requiring more evidence. `G0`, which requires only signature validity, rejects the correct baseline in 32 of 64 unavailable-signal subsets. Both two-signal gates reject 48 of 64 subsets. The two three-signal gates reject 56 of 64. The six-signal composite gate rejects 63 of 64, qualifying the correct baseline only when none of its required assurance signals is unavailable.

This monotonic count progression within the frozen gate definitions does not establish a global optimization rule. A stricter gate narrows the modeled set of incorrect states that qualify, but also increases the number of benign missing-evidence states that cause rejection. The study does not assign operational probabilities, mission costs, or utility weights to either side of that frontier.

The term "availability" is therefore used cautiously. Study 6 measures qualification availability under modeled assurance-signal loss. It does not measure mission availability, network availability, spacecraft contact, or service uptime.

## J. Relationship to Provenance and Update-Security Prior Art

The Study-6 gates intentionally use assurance concepts that are already established in software-supply-chain and update-security systems. in-toto provides verifiable supply-chain step metadata [10]. TUF uses signed metadata, target hashes, trusted roles, thresholds, and expiration to secure software updates [11]. SLSA defines source and build assurance levels and threat boundaries [12]. SPARTA also motivates integrity-protected and validated recovery baselines in the spacecraft context [4].

Study 6 neither replaces nor validates those systems. It also does not claim standards compliance. The model asks a different question: if a recovery-qualification policy can observe selected assurance signals corresponding to these broad concepts, which prespecified incorrect artifact states remain observationally indistinguishable from acceptable artifacts under each gate?

That question makes the residual state set, rather than the existence of provenance itself, the primary result.

## K. Study-6 Residual Trust Boundary

Study 6 shows that composing more artifact-assurance signals closes specific modeled failure pathways, but the residual boundary changes with which assurance dimensions are visible. Signature-only qualification leaves four prespecified incorrect states. Adding digest or provenance closes the signer-only state. Adding reproduced-build evidence closes the modeled builder-compromise state, while adding source-review evidence closes the review-bypass state. The composite gate closes all modeled integrity/provenance pathways except `APPROVED_BAD_SOURCE`, where every gate-visible assurance signal remains true despite objective incorrectness.

The same composition increases sensitivity to benign assurance-signal loss. The result is therefore a finite residual-correctness versus qualification-availability frontier, not a globally best gate. It completes the third study-specific layer needed for the cross-study synthesis: Study 3 addresses temporal runtime evidence, Study 4 addresses producer composition, and Study 6 addresses the recovery artifact itself.
