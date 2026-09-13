# Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence

**Candidate title — whole-manuscript title review pending**  
**Target:** AIAA *Journal of Aerospace Information Systems* Technical Note  
**Study:** `S7-LSO-001`  
**Draft status:** `R3__FIRST_COMPLETE_TECHNICAL_NOTE__WHOLE_MANUSCRIPT_AUDIT_REQUIRED`  

No abstract is included because the locked article form is an AIAA Technical Note.

## I. Introduction

Cyber recovery is a different decision problem from cyber detection. Detection can raise an alarm or identify an anomalous condition; recovery logic must decide what action remains justified after that alarm, using the state visible to the decision process. Space-domain concepts such as cyber-safe mode similarly connect cyber-threat response to controlled transition toward an integrity-protected recovery baseline [1]. That distinction becomes important when the evidence used to authorize recovery is itself exposed to compromise. A recovery selector can receive a record that remains authenticated and current enough for policy qualification while still being false relative to a state that the selector cannot observe.

A prior frozen study in this research program evaluated that condition directly. Under its `V5` treatment, a controlled policy-visible producer could supply a validly signed, current value that remained acceptable to the recovery gate while disagreeing with research-only adjudication truth. The resulting boundary was not a cryptographic verification failure: the record could satisfy the implemented qualification checks while the hidden authorization state was false. The Study-2 source-evidence package is publicly archived on Zenodo [2]. The present note does not reuse Study-2 observations or statistical results; it uses the signed-but-false condition and deterministic selector semantics only as antecedent specification for a separately designed and frozen machine-learning assurance experiment.

The question is whether a learned selector changes that boundary when it receives the same information. Exact fit to a visible decision rule does not itself provide hidden information absent from the model input. Conversely, adding another observable changes the information available to the decision process, but any benefit depends on the failure relationship between that observable and the compromised evidence path. This distinction is relevant to aerospace assurance, where evidence concerning functional intent, model and data properties, implementation, integration, coverage, traceability, robustness, and verification and validation matters in addition to model performance [3].

Recent spacecraft machine-learning work has largely emphasized anomaly detection and telemetry performance. The OPS-SAT benchmark provides real spacecraft telemetry fragments and labels for comparing anomaly-detection methods [4]; transformer-based work compares architectures for satellite telemetry anomaly detection [5]; and validation-gated continual learning addresses telemetry drift and data scarcity [6]. Study 7 instead begins downstream of detection and asks what a learned cyber-recovery selector can justify from the evidence visible to it.

This Technical Note reports `S7-LSO-001`, a deterministic finite experiment comparing a fixed visible-only recovery rule, a learned selector trained on the same eight policy-visible inputs, and a second learned selector that receives one additional corroboration bit. The complete modeled population contains 1,033 exact observations and is independently audited.

**RQ1. How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and how does adding a corroborating observable change that boundary when corroboration is independent versus correlated with the compromised evidence path?**

The contribution is intentionally narrow: exhaustive evaluation of the frozen visible and corroboration state spaces; a test of whether exact visible-rule learning implies correctness when relevant truth is hidden; an explicit independent-versus-correlated corroboration boundary; and hash-frozen, independently audited evidence. The note does not claim a new general theory of partial observability, operational spacecraft autonomy, certification sufficiency, or global superiority of learned over deterministic recovery logic.

## II. Assurance and Novelty Boundary

This note does not claim partial observability, corroboration, or redundancy as new general concepts. Its contribution is an application-specific assurance construction for a satellite cyber-recovery decision in which the evidence path is part of the adversarial model.

The first adjacent literature is aerospace machine-learning assurance. NASA's recent technical memorandum on learning-enabled components treats assurance as a lifecycle evidence problem spanning functional intent, model and data properties, implementation, integration, and V&V rather than as a single performance score [3]. Study 7 adopts that perspective but does not attempt certification analysis. Its learner is deliberately simple so that model complexity does not obscure the information question being tested.

The second adjacent literature is spacecraft anomaly detection. OPS-SAT and related work provide realistic telemetry data, detector benchmarks, transformer comparisons, and continual-learning mechanisms for changing mission data distributions [4]-[6]. Study 7 does not report detector accuracy, precision, recall, false-positive rate, training curves, or telemetry generalization. Its `security_signal` is already part of the policy-visible state. The experiment therefore tests recovery authorization after a security signal exists rather than detection performance itself.

The distinct construction holds model-visible state and research-only truth apart. A visible-only learner is trained against the same policy-visible decision semantics as the deterministic comparator and evaluated over the entire eight-feature state space. A second learner receives one corroboration observable and is evaluated over the complete nine-feature state space. A final collision block then holds the original eight visible inputs constant while changing research-only authorization truth and corroboration. No observation from Study 2 or any other submitted study enters the 1,033-observation Study-7 population.

## III. Study Design

### A. Visible State and Adjudication

Study 7 uses eight binary policy-visible inputs: `signature_valid`, `source_trusted`, `fresh`, `epoch_valid`, `noncontradictory`, `minimum_evidence_complete`, `security_signal`, and `authorization_available`. The corroboration-aware learner receives one additional binary feature, `independent_corroboration`.

A separate `hidden_authorization` value is used only by the research adjudicator. It is never supplied to the deterministic comparator or either learned selector. When no hidden-truth collision is imposed, hidden authorization equals visible authorization. In the collision block, the two may differ. The adjudicated objective is safe-to-proceed only when all six evidence-quality conditions hold and either no security signal is present or adjudicated authorization is true. This construction prevents the learner from receiving the research-only answer through a privileged feature.

### B. Policies and Learning Procedure

Three policies are evaluated. `D0_S1_VISIBLE_ONLY` is the fixed visible-only comparator. `L0_ERM_VISIBLE_ONLY` is learned from the same eight visible inputs. `L1_ERM_WITH_INDEPENDENT_CORROBORATION` adds the corroboration bit.

Both learned policies use deterministic empirical-risk minimization over a bounded integer linear-threshold hypothesis class. The visible-only rule has form

`q*sum(quality6) + wa*authorization + ws*security >= threshold`,

and the corroboration-aware rule adds `wc*independent_corroboration`. The frozen protocol uses 10 visible-only and 13 corroboration training prototypes, with deterministic tie-breaking after minimum training error and minimum absolute weight sum. No external ML library, neural network, stochastic optimizer, reinforcement-learning environment, or adversarial perturbation optimizer is used.

The accepted execution produced the frozen models in Table I. Both have zero training errors.

**Table I. Frozen policy and information boundary**

| Policy | Visible inputs | Learned? | Frozen parameters | Hidden authorization visible? |
|---|---|---:|---|---:|
| `D0_S1_VISIBLE_ONLY` | eight base features | No | fixed visible rule | No |
| `L0_ERM_VISIBLE_ONLY` | eight base features | Yes | `q=2`, `wa=1`, `ws=-1`, `t=12` | No |
| `L1_ERM_WITH_INDEPENDENT_CORROBORATION` | base features + corroboration | Yes | `q=2`, `wa=0`, `wc=1`, `ws=-1`, `t=12` | No |

### C. Finite Evaluation

Block A exhausts all `2^8=256` eight-feature states for D0 and L0, yielding 512 observations. Hidden authorization equals visible authorization in this block. Block B exhausts all `2^9=512` combinations of the eight base features and corroboration for L1, yielding another 512 observations. Hidden authorization again equals visible authorization.

Block C holds the eight-feature base vector fixed at a fully qualifying state while varying research-only authorization truth and corroboration across three prespecified scenarios: `SAFE_CORROBORATED`, `V5_INDEPENDENT_DISAGREEMENT`, and `V5_CORRELATED_FALSE_CORROBORATION`. All three policies are evaluated in each scenario, yielding nine observations. The complete finite population is therefore 1,033 observations.

Primary endpoints are `objective_decision_error`, `unsafe_proceed`, `false_conservative_hold`, hidden-truth collision indistinguishability, and resolution of the independent-disagreement case by the corroboration-aware learner. Counts are finite-population results, not estimates of operational spacecraft error probabilities.

The accepted execution is bound to workflow run `33689625480` and commit `f1530b0b2e81a5916adaf7ce808075156424dfb5`. Core outputs are SHA-256 frozen. An independently written auditor reconstructs the objective, both learned models, and all 1,033 policy decisions and reports zero mismatches. Manuscript development does not rerun or alter the frozen experiment.

## IV. Results

### A. Visible-State Equivalence and Corroboration Lattice

In Block A, D0 and L0 each contributed 256 observations. Both produced zero objective-decision errors, zero unsafe proceeds, zero false-conservative holds, and exactly three proceed decisions. L0 therefore reproduced the complete visible decision boundary rather than only its 10 training prototypes.

Block B evaluated L1 over all 512 extended visible states. L1 produced six proceed decisions and 506 holds, with exactly two objective-decision errors: one unsafe proceed and one false-conservative hold. Both errors occurred in the fully qualifying evidence-quality state with `security_signal=1` when visible authorization and corroboration disagreed. With visible authorization 0 and corroboration 1, L1 proceeded although adjudicated authorization was false. With visible authorization 1 and corroboration 0, L1 held although adjudicated authorization was true. These are exact state counts, not estimated error rates.

**Table II. Exact finite-population outcomes**

| Block | Policy | N | Errors | Unsafe proceed | False-conservative hold | Proceed decisions |
|---|---|---:|---:|---:|---:|---:|
| A | D0 | 256 | 0 | 0 | 0 | 3 |
| A | L0 | 256 | 0 | 0 | 0 | 3 |
| B | L1 | 512 | 2 | 1 | 1 | 6 |
| C | D0 | 3 | 2 | 2 | 0 | 3 |
| C | L0 | 3 | 2 | 2 | 0 | 3 |
| C | L1 | 3 | 1 | 1 | 0 | 2 |

### B. Hidden-Truth Collisions

Block C keeps all eight original policy-visible inputs equal to one. In `SAFE_CORROBORATED`, hidden authorization and corroboration are also one; the adjudicated objective is proceed, and D0, L0, and L1 all proceed correctly.

In `V5_INDEPENDENT_DISAGREEMENT`, visible authorization remains one but hidden authorization is zero. D0 and L0 receive exactly the same eight inputs as in the safe case and both proceed unsafely. L1 receives corroboration zero and holds, matching the adjudicated objective.

In `V5_CORRELATED_FALSE_CORROBORATION`, hidden authorization remains zero while corroboration returns to one. D0 and L0 again proceed unsafely, and L1 also proceeds unsafely. Thus, adding corroboration resolves the prespecified disagreement case only while the added evidence distinguishes the hidden-false condition. When corroboration shares the false state, the unsafe decision returns.

Together, the blocks answer RQ1 in two parts. Exact learning of the visible decision boundary does not resolve a hidden-truth collision when the model inputs are identical. Adding a corroborating observable changes the information available to the selector and resolves the prespecified independent-disagreement case, but Block B and the correlated-failure collision show that the added observable introduces its own trust dependency rather than eliminating the evidence boundary.

## V. Discussion and Limitations

The central result concerns information sufficiency, not model performance. L0 achieved zero training error and zero error over all 256 visible states, yet it had no protection in the hidden-truth collision because the relevant distinction was not in its input. In the independent-disagreement case, D0 and L0 saw the same fully qualifying vector as in the safe case; their unsafe decisions therefore reflect an observability boundary rather than a failure to fit the visible rule.

L1 changed the outcome because the input changed. A zero corroboration bit distinguished the hidden-false disagreement state from the safe corroborated state, allowing L1 to hold. This is not evidence that learned logic is intrinsically safer than deterministic recovery logic. It shows instead that decision correctness can depend on whether a decision-relevant observable distinguishes the hidden condition being adjudicated.

The complete nine-feature lattice prevents a one-sided interpretation of corroboration. L1's two errors occurred when corroboration and visible authorization disagreed in an otherwise fully qualifying security state. Positive corroboration with false adjudicated authorization produced an unsafe proceed; absent corroboration with true adjudicated authorization produced a false-conservative hold. Corroboration therefore shifts part of the trust burden rather than removing it. The correlated-false-corroboration case exposes that dependency directly.

For learned aerospace recovery logic, the assurance implication is that evaluation should trace not only model fit but also the provenance, observability, and failure relationships of decision-relevant evidence. This is consistent with aerospace ML-assurance guidance that treats confidence as a broader lifecycle evidence problem [3]. Study 7 does not establish a certification method or sufficient certification evidence.

The limitations are substantial and deliberate. The learner is a deterministic integer linear-threshold model rather than a neural or stochastic learner. Inputs are binary, and the study does not model continuous/noisy evidence, stochastic learning, or distribution shift. It does not evaluate detector performance and supports no operational spacecraft, RF, flight, hardware, CPU, energy, or latency claims. The corroboration input is designed to represent an independent evidence path in the prespecified model; operational independence is an assumption, not an empirical finding. The correlated-failure case demonstrates why that assumption matters.

These limitations constrain external validity but do not alter the finite-population claim. Every eight-feature visible state and every nine-feature corroboration state in the frozen design is evaluated. Future prospectively designed work could test the same information-sufficiency question with higher-fidelity evidence producers, noisy observables, learned representations, and empirically grounded mission trust paths.

## VI. Conclusion

Study 7 shows that exact learning of a satellite cyber-recovery decision boundary does not establish correctness when the decisive truth is absent from the learner's observables. Adding corroboration can make a hidden-false state distinguishable, but the benefit disappears when the corroborating path shares the false state and can impose its own safety/availability trade-off when evidence sources disagree.

The result is exact for the 1,033-position frozen model and does not establish operational spacecraft performance or certification sufficiency. Its assurance implication is narrower: validation of a learned recovery rule should include the information and trust architecture feeding that rule, not only the rule's fit to visible states.

## Data and Code Availability

The Study-7 protocol, implementation, frozen result records, and independent-audit code are maintained in the public `mission-aware-satellite-cyber-recovery` repository. The accepted execution and core outputs are hash-frozen; a permanent archive of the exact accepted evidence bytes is required before the current GitHub Actions artifact expires. No Study-7 data were regenerated for this manuscript.

## References

[1] Space Attack Research and Tactic Analysis (SPARTA), "Cyber-safe Mode," Countermeasure CM0044, The Aerospace Corporation. Available: https://sparta.aerospace.org/countermeasures/CM0044

[2] A. Singh, *Mission-Aware Satellite Cyber Response and Trusted Recovery — Study 2 Phase-6 Source Evidence*, dataset, Zenodo, ver. 1.0.0, Sep. 4, 2026, doi: `10.5281/zenodo.22289114`.

[3] A. Agogino et al., *Recommendations on Evidence and Process for Certification of Learning-enabled Components in Aerospace Systems*, NASA Technical Memorandum, Document ID 20240006865, Jun. 7, 2024. Available: https://ntrs.nasa.gov/citations/20240006865

[4] B. Ruszczak, K. Kotowski, D. Evans, et al., "The OPS-SAT benchmark for detecting anomalies in satellite telemetry," *Scientific Data*, vol. 12, Art. no. 710, 2025, doi: `10.1038/s41597-025-05035-3`.

[5] A. Fejjari, A. Delavault, R. Camilleri, and G. Valentino, "Transformer-based anomaly detection for satellite telemetry data," *Acta Astronautica*, vol. 238, Part A, pp. 739-745, 2026, doi: `10.1016/j.actaastro.2025.09.035`.

[6] N. Kuhn, B. Sánchez Gómez, N. Moreno Blasco, P. Caserman, and F. Antonello, "Validation-gated continual learning for anomaly detection in satellite telemetry," *Acta Astronautica*, vol. 249, pp. 971-985, 2026, doi: `10.1016/j.actaastro.2026.07.065`.