# Evidence Observability Limits in Learned Satellite Cyber-Recovery Decisions

**Working title — not yet frozen**  
**Target:** AIAA *Journal of Aerospace Information Systems* Technical Note  
**Study:** `S7-LSO-001`  
**Draft status:** `R1__SECTIONS_I_III_ONLY__CLAIM_AUDIT_REQUIRED_BEFORE_RESULTS_DRAFTING`  

No abstract is included because the locked article form is an AIAA Technical Note.

## I. Introduction

Cyber recovery aboard a spacecraft or within its supporting mission system is not the same problem as detecting that something is wrong. Detection can raise an alarm or identify an anomalous condition; recovery logic must decide what action remains justified after that alarm, using whatever state is visible to the decision process. Space-domain recovery concepts such as cyber-safe mode similarly distinguish recognition of a cyber threat from the controlled transition to an integrity-protected recovery state [1]. That distinction matters when the evidence used to authorize recovery is itself exposed to compromise. A recovery selector can receive information that is timely, authenticated, and internally consistent yet still be false relative to a state that the selector cannot observe.

A prior frozen study in this research program evaluated that condition directly. Under its `V5` treatment, a controlled policy-visible producer could supply a validly signed, current value that remained acceptable to the recovery selector while disagreeing with research-only adjudication truth. The resulting boundary was not a cryptographic verification failure: the record could satisfy the implemented evidence checks while the hidden authorization state was false. The complete Study-2 record has been released as a durable public research archive [2]. The present note does not reuse that study's observations or statistical results. Instead, it treats the signed-but-false condition and the earlier deterministic selector semantics as antecedent specification for a separately designed and frozen machine-learning assurance experiment.

The question is whether learning changes that boundary. A more flexible model may reproduce a decision rule more accurately than a hand-written approximation, but no increase in model capacity can directly supply information that is absent from the model input. Conversely, adding another observable can change the decision problem, although the benefit depends on whether the added evidence fails independently of the compromised path. These distinctions are especially important for aerospace assurance, where confidence in a learning-enabled component cannot be reduced to model performance alone. NASA assurance work for learning-enabled aerospace components emphasizes evidence about requirements, data and model properties, implementation, integration, coverage, traceability, robustness, and verification and validation across the lifecycle [3].

Recent spacecraft machine-learning literature has largely concentrated on anomaly detection and telemetry performance. The OPS-SAT benchmark provides real spacecraft telemetry fragments and labels for comparing anomaly-detection methods [4]; transformer-based work evaluates competing architectures on satellite telemetry anomaly detection [5]; and recent continual-learning research evaluates validation-gated model updates under telemetry drift and data scarcity [6]. Those efforts address important detection and health-monitoring problems. The present study instead examines a downstream assurance question: once a cyber-recovery decision must be made, what can a learned selector justify from the evidence that is actually visible to it?

This Technical Note reports Study 7 (`S7-LSO-001`), a deterministic finite experiment designed specifically to isolate that information boundary. It compares a fixed visible-only recovery rule, a learned selector trained on the same eight policy-visible inputs, and a second learned selector that receives one additional corroboration bit. The complete modeled population contains 1,033 exact observations and is independently audited; it is not a random sample of operational spacecraft behavior.

The primary research question is:

**RQ1. How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and how does adding a corroborating observable change that boundary when corroboration is independent versus correlated with the compromised evidence path?**

The contribution is intentionally narrow. First, the study exhausts the finite visible and corroboration state spaces used by the three decision policies. Second, it tests whether exact reproduction of a visible decision boundary implies correctness when relevant truth is hidden. Third, it isolates the effect of an added corroborating observable under independent and correlated failure. Fourth, the execution and resulting evidence are hash-frozen and independently reproduced. The note does not claim a new general theory of partial observability, operational spacecraft autonomy, certification sufficiency, or global superiority of learned over deterministic recovery logic.

## II. Assurance and Novelty Boundary

The scientific novelty of this study is not the statement that a learner cannot infer an unobserved variable from two input states that are identical to the learner. Partial observability is a long-established property of decision problems, and aerospace autonomy research has addressed partially observable environments through estimation, memory, stress testing, and other mechanisms. Likewise, redundancy and corroboration are not new assurance concepts. The narrower issue examined here is how those principles manifest in a frozen satellite cyber-recovery decision boundary when the evidence path itself is part of the adversarial model.

This distinction separates the present work from two adjacent literatures. The first is aerospace machine-learning assurance. NASA's recent technical memorandum on learning-enabled components frames assurance as an evidence problem that spans functional intent, model and data properties, implementation, integration, and V&V rather than as a single performance score [3]. Study 7 adopts that assurance perspective but does not attempt certification analysis. Its learner is deliberately simple so that model complexity does not obscure the information question being tested. The experiment asks whether the evidence available to a recovery selector is sufficient for the decision being adjudicated, not whether a sophisticated model can maximize an accuracy benchmark.

The second adjacent literature is spacecraft anomaly detection. OPS-SAT and related work provide realistic telemetry data, detector benchmarks, transformer comparisons, and continual-learning mechanisms for changing mission data distributions [4]-[6]. Study 7 does not compete with those methods and does not report detection accuracy, precision, recall, false-positive rate, training curves, or telemetry generalization. Its `security_signal` input is already part of the policy-visible state. The experiment begins downstream of detection and tests the recovery selector's authorization decision under controlled evidence conditions.

The application-level contribution therefore lies in a specific assurance construction. A visible-only learned selector is trained to match the same policy-visible decision semantics as the deterministic comparator. The entire eight-feature visible state space is then exhausted. A second learned selector receives an additional corroboration observable and is evaluated over the complete nine-feature state space. Finally, a hidden-truth collision block holds the original eight policy-visible inputs constant while changing research-only authorization truth and the corroboration bit. This design separates three questions that can otherwise be conflated: whether the learner fits the visible rule, whether the visible rule contains enough information to resolve hidden truth, and whether an added source changes the available information under independent versus correlated failure.

The study is also publication-independent from the program's earlier papers. Study-2 `V5` and the deterministic evidence-aware selector provide lineage and motivation through the public Study-2 archive [2], but no Study-2 observations enter the present 1,033-observation population. Other submitted studies on temporal evidence, producer composition, artifact assurance, and cryptographic agility are not pooled into this analysis. The result reported here is therefore a separate finite machine-learning assurance experiment rather than a reanalysis of an earlier manuscript.

## III. Study Design

### A. Decision Variables and Adjudication Boundary

Study 7 uses eight binary policy-visible inputs:

1. `signature_valid`;
2. `source_trusted`;
3. `fresh`;
4. `epoch_valid`;
5. `noncontradictory`;
6. `minimum_evidence_complete`;
7. `security_signal`; and
8. `authorization_available`.

The first six variables form the evidence-quality conditions used by the selector. `security_signal` indicates whether the decision occurs in the modeled security-response condition, and `authorization_available` is the authorization state visible to the policy. The corroboration-aware learner receives one additional binary feature, `independent_corroboration`.

A separate variable, `hidden_authorization`, is used only by the research adjudicator when computing whether it is objectively safe to proceed. It is never supplied to the deterministic comparator or either learned selector. When no hidden-truth collision is imposed, hidden authorization equals the policy-visible authorization value. In the collision block, the two values may differ. The objective endpoint is safe-to-proceed only when all six evidence-quality conditions hold and either no security signal is present or the adjudicated authorization is true. This construction makes the distinction between policy-visible evidence and research-only truth explicit rather than allowing the learner to access the answer through a privileged feature.

### B. Decision Policies and Deterministic Learning Procedure

Three policies are evaluated. `D0_S1_VISIBLE_ONLY` is the fixed visible-only comparator. `L0_ERM_VISIBLE_ONLY` is a learned selector trained on the same eight visible features. `L1_ERM_WITH_INDEPENDENT_CORROBORATION` extends the learned input with the corroboration bit.

Both learned policies are produced by deterministic empirical-risk minimization over a bounded integer linear-threshold hypothesis class. The visible-only model has the form

`q*sum(quality6) + wa*authorization + ws*security >= threshold`,

and the corroboration-aware model adds

`wc*independent_corroboration`.

The frozen protocol uses 10 visible-only training prototypes and 13 corroboration training prototypes. Candidate models are selected first by minimum training error, then by minimum absolute weight sum, followed by deterministic lexicographic tie-breaking over threshold and weights. No external machine-learning library, stochastic optimizer, reinforcement-learning environment, neural network, or adversarial perturbation optimizer is used. This simplicity is intentional: the experiment is designed to isolate observability and evidence sufficiency rather than model capacity.

The accepted execution produced the following frozen models. `L0_ERM_VISIBLE_ONLY` has quality weight 2, authorization weight 1, security weight -1, threshold 12, and zero training errors. `L1_ERM_WITH_INDEPENDENT_CORROBORATION` has quality weight 2, authorization weight 0, corroboration weight 1, security weight -1, threshold 12, and zero training errors. These model parameters are outcomes of the frozen deterministic training procedure and are not tuned during manuscript development.

**Table I. Frozen policy and information boundary**

| Policy | Policy-visible inputs | Corroboration visible? | Learned? | Frozen decision parameters | Hidden authorization visible? |
|---|---|---|---|---|---|
| `D0_S1_VISIBLE_ONLY` | eight base features | No | No | fixed S1-equivalent visible rule | No |
| `L0_ERM_VISIBLE_ONLY` | eight base features | No | Yes | `q=2`, `wa=1`, `ws=-1`, `threshold=12` | No |
| `L1_ERM_WITH_INDEPENDENT_CORROBORATION` | eight base features + corroboration | Yes | Yes | `q=2`, `wa=0`, `wc=1`, `ws=-1`, `threshold=12` | No |

### C. Finite Evaluation Blocks

The evaluation population is finite and exhaustive within the frozen design.

**Block A — visible-state lattice.** All `2^8 = 256` possible combinations of the eight policy-visible features are evaluated by both `D0_S1_VISIBLE_ONLY` and `L0_ERM_VISIBLE_ONLY`. Hidden authorization equals visible authorization in this block. The block therefore contains 512 observations and tests whether the learned selector reproduces the complete visible decision boundary rather than merely its training prototypes.

**Block B — corroboration lattice.** All `2^9 = 512` combinations of the eight base features and the corroboration bit are evaluated by `L1_ERM_WITH_INDEPENDENT_CORROBORATION`. Hidden authorization again equals visible authorization. This block contains 512 observations and exposes the complete decision surface created by adding corroboration to the policy-visible state.

**Block C — hidden-truth collisions.** The eight-feature base vector is held fixed at a fully qualifying visible state while research-only authorization truth and corroboration vary across three prespecified scenarios: `SAFE_CORROBORATED`, `V5_INDEPENDENT_DISAGREEMENT`, and `V5_CORRELATED_FALSE_CORROBORATION`. Each scenario is evaluated by all three policies, yielding nine observations. The first scenario is objectively authorized and corroborated. The second keeps policy-visible authorization true while hidden authorization is false and corroboration is negative. The third keeps the same false hidden authorization but sets corroboration positive, representing correlated false corroboration.

The three blocks therefore contain `512 + 512 + 9 = 1,033` exact observations. Primary endpoints are `objective_decision_error`, `unsafe_proceed`, `false_conservative_hold`, hidden-truth collision indistinguishability, and resolution of the independent-disagreement case by the corroboration-aware learner. Counts over these states are reported as finite-population results, not as estimates of operational spacecraft error probabilities.

### D. Freeze, Provenance, and Independent Audit

The accepted execution is bound to workflow run `33689625480` and commit `f1530b0b2e81a5916adaf7ce808075156424dfb5`. The frozen evidence artifact is identified by SHA-256 `26b522d2692516aa1b4ae62d032a9a909dbaccd7ef1a74104080c39bdf3a091b`. The four core deterministic outputs are separately hash-bound: `observations.csv` (`5d66fe1db266e3a98532d0d0e63d1bc1a5d24eed0e831b5c91bdaa94f60d00b5`), `policy_summary.csv` (`bf6069e200be76f324032133b8bf5e20ad3df33d57a59d985d3e3d828304d34d`), `TRAINED_MODELS.json` (`8adafec923d756d91ec68c563d608ba27f5d224fea1907d5753c33944d54b362`), and `REPORT.json` (`cd85ac132eeff15d72b9e995127d267cefbd49d033fc776885f0bfe7caef48c1`).

An independently written audit reconstructs the objective function, both learned models, and all 1,033 policy decisions from the frozen evidence. It reports `study7_independent_audit=PASS` with zero mismatches. No scientific reexecution or result substitution is performed for this manuscript draft.

---

## References used in Sections I-III

[1] Space Attack Research and Tactic Analysis (SPARTA), "Cyber-safe Mode," Countermeasure CM0044, Aerospace Corp. Available: https://sparta.aerospace.org/countermeasures/CM0044

[2] A. K. Singh, *Study 2 — Adversarial Evidence and Trusted Recovery*, public research archive, Zenodo, version 1.0.0, Sep. 4, 2026, doi: `10.5281/zenodo.22289114`.

[3] A. Agogino et al., *Recommendations on Evidence and Process for Certification of Learning-enabled Components in Aerospace Systems*, NASA/TM, Document ID 20240006865, Jun. 7, 2024. Available: https://ntrs.nasa.gov/citations/20240006865

[4] B. Ruszczak, K. Kotowski, D. Evans, et al., "The OPS-SAT benchmark for detecting anomalies in satellite telemetry," *Scientific Data*, vol. 12, Art. no. 710, 2025, doi: `10.1038/s41597-025-05035-3`.

[5] A. Fejjari, A. Delavault, R. Camilleri, and G. Valentino, "Transformer-based anomaly detection for satellite telemetry data," *Acta Astronautica*, vol. 238, Part A, pp. 739-745, 2026, doi: `10.1016/j.actaastro.2025.09.035`.

[6] "Validation-gated continual learning for anomaly detection in satellite telemetry," *Acta Astronautica*, 2026, doi: `10.1016/j.actaastro.2026.07.065`. Full author metadata to be verified before final bibliography freeze.

---

**Draft boundary:** Sections IV-VI are intentionally not drafted in R1. Results prose must not begin until this R1 text passes a source-by-source scientific claim audit.