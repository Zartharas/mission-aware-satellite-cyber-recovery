# Paper 3 / Study 7 Publication Boundary and Originality Gate

**Gate date:** 2026-09-07  
**Gate status:** `PASS__STUDY7_SELECTED__VENUE_NOT_LOCKED__MANUSCRIPT_NOT_AUTHORIZED`  
**Scoped branch:** `publication/paper3-study7-boundary-audit`  
**Base clean-main commit:** `3b02edc3dfe75ab64a42adc6b10d1acb3089c96e`  
**Purpose:** publication-boundary, originality, overlap, claim-scope, article-form, and live venue-fit control before any Paper-3 manuscript drafting.

## 1. Control prerequisites

The author supplied a local clean-main attestation immediately before branch creation:

- branch: `main`;
- local `HEAD`: `3b02edc3dfe75ab64a42adc6b10d1acb3089c96e`;
- `origin/main`: `3b02edc3dfe75ab64a42adc6b10d1acb3089c96e`;
- `branch_main=PASS`;
- `worktree_clean=PASS`;
- `local_equals_origin_main=PASS`;
- `expected_head=PASS`;
- final `git status --short`: empty.

The remote `main` branch at that commit records the Paper-2 governance reconciliation and the canonical current-state documents identify three submitted, frozen publication lines: Paper 1 / Studies 1+2, Roadmap Paper 4 / Study 8, and Paper 2 / Studies 3+4+6.

This branch was therefore created from the exact locally and remotely synchronized clean-main state.

## 2. Governance effect of this record

This file is a publication-governance record only. It does **not** modify any frozen design, code, observation, result, trained model, analysis output, submitted manuscript, reviewer PDF, publisher-facing package, DOI record, or study provenance artifact.

This record selects Study 7 as the next publication-development boundary after a read-only candidate audit. It does **not** lock a journal, article type, title, manuscript outline, abstract, or publisher submission.

No manuscript drafting is authorized by this record.

## 3. Candidate selection disposition

### 3.1 Selected candidate: Study 7 / `S7-LSO-001`

**Study title:** *Learned Selector Observability Under Adversarial Evidence and Independent Corroboration*  
**Repository status:** `CANONICAL_RESULTS_FROZEN_MERGED`  
**Canonical results merge:** PR #87 / `f582c36cc5747a6703ec651bb957bbfea5852a7e`  
**Accepted execution:** workflow run `33689625480` / commit `f1530b0b2e81a5916adaf7ce808075156424dfb5`  
**Independent audit:** PASS

Study 7 is selected because it has the strongest remaining combination of scientific coherence, publication independence, deterministic reproducibility, cybersecurity relevance, and aerospace-assurance fit.

### 3.2 Deferred alternative: Study 5 / `S5-CUCD-001`

Study 5 remains a valid separately frozen portability/external-validity boundary study, but it is not selected for Paper 3.

Its frozen contribution is intentionally narrow: the CuCD-ID external dataset does not directly provide the recovery-state inputs needed to execute the repository's trusted-recovery selectors without fabrication; the study therefore evaluates input sufficiency/taxonomy transferability and an offline oracle-alarm portability construction rather than row-level recovery-policy performance.

Study 5 must not be combined with Study 7 merely because both remain unconsumed. Their scientific questions, experimental units, interventions, endpoints, evidence sources, and reviewer communities differ materially.

**Disposition:** `DEFER__DO_NOT_COMBINE_WITH_STUDY7`.

### 3.3 No other eligible study population identified

The repository program scope is Studies 1-8. Studies 1+2 are consumed by submitted Paper 1; Studies 3+4+6 by submitted Paper 2; Study 8 by submitted Roadmap Paper 4. The historical WP0-WP11 register is Study-1 work-package history, not a set of new publication-independent study populations.

Accordingly, the remaining complete unconsumed frozen scientific lines are Study 5 and Study 7; Study 7 is selected here.

## 4. Immutable Paper-3 evidence boundary

Paper 3 may use **Study 7 / `S7-LSO-001` only as new experimental evidence**.

The frozen Study-7 population is exactly **1,033 observations**:

- Block A / visible-state lattice: **512** observations = all 256 eight-feature visible states crossed with `D0_S1_VISIBLE_ONLY` and `L0_ERM_VISIBLE_ONLY`;
- Block B / corroboration lattice: **512** observations = all 512 nine-feature states for `L1_ERM_WITH_INDEPENDENT_CORROBORATION`;
- Block C / hidden-truth collision cases: **9** observations = three adjudicated hidden-truth/corroboration scenarios crossed with all three policies.

The research-only hidden authorization value is an adjudication variable only. It is not supplied as a policy input to D0, L0, or L1.

No observations, contrasts, success rates, confidence intervals, p-values, timing measurements, tables, or figures from Studies 1, 2, 3, 4, 5, 6, or 8 may be silently treated as Paper-3 experimental evidence.

Earlier studies may be cited only as prior work, specification lineage, motivation, or comparator provenance where scientifically necessary.

## 5. Frozen Study-7 mechanism and findings

The learner is intentionally transparent: deterministic empirical-risk minimization over a small integer linear-threshold hypothesis class. There is no neural network, reinforcement-learning environment, online exploration, adversarial perturbation optimizer, or external ML library.

Frozen models:

- `L0_ERM_VISIBLE_ONLY`: quality weight 2, authorization weight 1, security weight -1, threshold 12, training errors 0;
- `L1_ERM_WITH_INDEPENDENT_CORROBORATION`: quality weight 2, authorization weight 0, corroboration weight 1, security weight -1, threshold 12, training errors 0.

Frozen canonical findings:

1. `L0` reproduces the visible S1-equivalent decision boundary with zero training error and zero error across all 256 possible eight-feature visible states, but it cannot distinguish safe and V5 signed-but-false states that are identical in those visible inputs.
2. `L1` changes the available information by receiving an additional corroboration bit and avoids unsafe proceed in `V5_INDEPENDENT_DISAGREEMENT`.
3. Across the complete 512-state corroboration lattice, `L1` has exactly two objective decision errors: one unsafe proceed and one false-conservative hold.
4. In `V5_CORRELATED_FALSE_CORROBORATION`, D0, L0, and L1 all proceed unsafely relative to hidden adjudication truth.
5. The result is an observability/information-sufficiency finding, not an ML-superiority result.

The same-repository independently written audit reconstructs the learner search, objectives, decisions, error categories, and all 1,033 observations and reports zero mismatches.

## 6. Publication contribution boundary

### 6.1 Contribution that is defensible

The defensible Paper-3 contribution is:

> A deterministic finite assurance experiment for learned satellite cyber-recovery decision logic that isolates the information boundary between policy-visible trusted evidence and research-only adjudication truth; demonstrates that exact visible-state agreement does not remove a hidden-truth failure when the trusted evidence path is compromised; and shows that an added corroborating observable changes the decision boundary only while its trust failure remains independent of the compromised evidence path.

The scientific emphasis is therefore **information sufficiency, observable trust boundaries, and assurance of a learned recovery decision**, not classifier performance.

### 6.2 Claims that are not novel by themselves

Paper 3 must not claim as novel that:

- partially observed or latent state can limit safe learned decision making;
- a model cannot infer a hidden variable from two states with identical observable features;
- additional information can improve a decision;
- evidence redundancy or corroboration can improve assurance;
- correlated failures can defeat nominally redundant evidence paths;
- machine learning generally requires verification, validation, robustness, or assurance evidence.

Those propositions have substantial prior foundations.

### 6.3 Novelty must be application-specific and experimental

The novelty claim must remain tied to the **specific satellite cyber-recovery assurance construction** and its frozen complete finite population. The paper should present the simple learner as an experimental control that isolates the information boundary, not as an algorithmic advance.

A targeted live literature search conducted on 2026-09-07 did not identify a prior publication with the exact combination of:

- learned satellite cyber-recovery decision logic;
- policy-visible signed/trusted evidence that can be false relative to hidden adjudication truth;
- an exhaustive visible-state and extended-corroboration state lattice;
- explicit comparison of independent versus correlated corroboration failure.

This negative search result is **not proof of novelty** and must not be represented as such. It only supports continuing to a manuscript-level literature review rather than stopping at this gate.

## 7. Self-overlap and prior-paper audit

### 7.1 Paper 1 / Studies 1 + 2 / JAIS

Submitted Paper 1 already establishes the antecedent V5 trust-boundary result: a controlled policy-visible producer can produce evidence that remains authenticated/current enough for the recovery gate while being false relative to research-only adjudication truth.

Paper 3 may cite this as the motivating antecedent and as specification lineage for the D0/S1-visible comparator. It must **not** present V5 itself as a new Paper-3 discovery, reuse Paper-1 Study-2 observations as new evidence, or restate Paper-1 quantitative results as if replicated by Study 7.

The clean distinction is:

- Paper 1 asks how deterministic response/recovery policies behave under evidence and contact/adversary constraints;
- Paper 3 asks whether a learned selector given the same visible state escapes that information boundary, and what changes when an additional corroborating observable is introduced.

**Overlap status:** `MANAGEABLE_WITH_EXPLICIT_ANTECEDENT_CITATION_AND_NO_DATA_REUSE`.

### 7.2 Paper 2 / Studies 3 + 4 + 6 / TAES

Submitted Paper 2 already studies temporal evidence persistence, producer composition/provenance diversity, and artifact assurance. Study 4 in particular evaluates total-vote and provenance-domain rules over a fixed seven-producer modeled set under malicious compromise and benign unavailability.

Paper 3 therefore must not claim that the general value of producer diversity, provenance diversity, quorum composition, or independent evidence is newly discovered in Study 7.

The clean distinction is:

- Paper 2 studies deterministic residual-trust mechanisms across time, producer composition, and artifacts;
- Paper 3 studies learned-selector **observability** and the difference between changing model class versus changing the information available to the model.

Study-7's single corroboration feature is not a reanalysis of Study 4's 4,608 rule-by-subset observations.

**Overlap status:** `MANAGEABLE_IF_CORROBORATION_IS_FRAMED_AS_INFORMATION_AVAILABILITY_NOT_NEW_QUORUM_THEORY`.

### 7.3 Roadmap Paper 4 / Study 8 / Acta Astronautica

Submitted Study 8 concerns contact-aware cryptographic agility and trusted post-compromise recovery. Its 3,456-position modeled population and cryptographic-policy results are outside Study 7's learned-selector observability experiment.

Paper 3 must not import Study-8 results or recast post-quantum/cryptographic agility as part of the Study-7 evidence base.

**Overlap status:** `LOW`.

### 7.4 Study 5

Study 5 concerns cross-testbed portability/input sufficiency against CuCD-ID and uses the external scenario label only as an offline alarm oracle. It is not an ML-performance evaluation and not a learned-selector observability experiment.

Combining Study 5 and Study 7 would produce a manuscript with two different scientific questions and incompatible evidence units without a prospectively frozen joint design.

**Overlap status:** `SEPARATE__DO_NOT_COMBINE`.

## 8. External originality and assurance context

The following live sources were checked on 2026-09-07 and are positioning evidence, not Study-7 experimental evidence.

### 8.1 Aerospace ML assurance is an active evidence-sufficiency problem

NASA, *Recommendations on Evidence and Process for Certification of Learning-enabled Components in Aerospace Systems* (2024), identifies assurance needs around model/data properties, requirements, robustness/generalizability, system integration, verification and validation, coverage, traceability, and formal methods. The report explicitly does not define a universally sufficient evidence set for every criticality level.

Source: `https://ntrs.nasa.gov/citations/20240006865`

NASA, *Challenges in Assuring ML Components in Increasingly Autonomous, High Confidence Aerospace Systems* (2025), frames the central question as what constitutes sufficient evidence that an ML-containing implementation performs as intended and points to testing, modeling/simulation, formal methods, monitoring, auditability, and transparency.

Source: `https://ntrs.nasa.gov/citations/20250004716`

AIAA's 2025 autonomous-aerospace-systems research-priorities paper likewise emphasizes trustworthy and assured autonomy and warns that AI/ML benefits must be weighed against verification and lifecycle-management challenges.

Source: `https://aiaa.org/wp-content/uploads/2025/12/AIAA-Autonomy-Paper-Good-Copy-FINAL.pdf`

These sources support the relevance of an evidence/assurance framing. They do not validate the Study-7 model or establish operational certification relevance.

### 8.2 Partial observability and latent variables are established research problems

Le, Juba, and Stern, *Learning Safe Action Models with Partial Observability* (AAAI 2024), directly studies safe learned action models under partially observable states.

Source: `https://ojs.aaai.org/index.php/AAAI/article/view/29995`

Jing and Nakahira, *Safety Certificate against Latent Variables with Partially Unidentifiable Dynamics* (ICML 2025), addresses safety certification in systems with latent variables and partially unidentifiable dynamics.

Source: `https://proceedings.mlr.press/v267/jing25b.html`

These sources reinforce the prohibition on claiming generic partial-observability theory as a Study-7 novelty.

### 8.3 Current satellite ML literature is largely detector/performance oriented

The 2025 OPS-SAT benchmark publishes 2,123 labeled real satellite telemetry fragments and benchmarks 30 supervised/unsupervised anomaly-detection algorithms.

Source: `https://www.nature.com/articles/s41597-025-05035-3`

A 2026 Acta Astronautica paper compares transformer architectures for anomaly detection on satellite telemetry including the ESA OPS-SAT dataset.

Source: `https://www.sciencedirect.com/science/article/pii/S0094576525006095`

A 2025 IEEE Space Computing Conference paper evaluates deep-learning spacecraft anomaly detection for edge devices and reports detection and resource-performance tradeoffs.

Source: `https://doi.org/10.1109/SCC66396.2025.00019`

A 2026 physics-informed satellite-cybersecurity paper uses ML anomaly detection plus a physics validation gate for suspicious orbital manipulation.

Source: `https://doi.org/10.1016/j.array.2026.100799`

These examples make clear that Study 7 should not compete as a detector-accuracy or model-performance paper. Its distinct lane is the assurance boundary of a learned recovery decision after evidence has already been made policy-visible.

### 8.4 Trusted recovery with learning-enabled components is not an untouched concept

NASA TechPort project *Safe Aviation Autonomy with Learning-enabled Components in the Loop: From Formal Assurances to Trusted Recovery Methods* develops assurance and fault-detection/isolation/recovery concepts for ML-enabled autonomy.

Source: `https://techport.nasa.gov/projects/96906`

This further narrows the novelty claim: Study 7 must not claim to originate the broad idea of learned-component trusted recovery. Its contribution is the specific cyber-evidence observability experiment and correlated-corroboration boundary.

## 9. Claim-boundary lock for future manuscript work

### 9.1 Claims the frozen evidence can support

A future Paper-3 manuscript may, subject to accurate wording and citations, support claims that:

- the visible-only learner exactly reproduced the specified visible-state decision boundary in the complete finite Study-7 lattice;
- this exact visible-state agreement did not eliminate unsafe proceed in a hidden-truth collision where the policy-visible state was unchanged;
- adding the stipulated independent corroboration feature changed the information available to the learned selector and avoided unsafe proceed in the prespecified independent-disagreement collision;
- the same corroboration-aware learner remained vulnerable when corroboration was falsely positive in correlation with the compromised evidence path;
- the complete finite Study-7 design demonstrates an information-sufficiency/trust-boundary limitation within the modeled decision architecture.

### 9.2 Claims the frozen evidence cannot support

A future Paper-3 manuscript must not claim:

- operational spacecraft autonomy validation;
- flight, RF, hardware-in-the-loop, ground-station, CPU, energy, or latency performance;
- certification or certifiability;
- real-world probability of independent or correlated evidence compromise;
- empirical independence of a real corroborating sensor, producer, organization, or trust domain;
- superiority of machine learning over deterministic recovery logic;
- superiority of the selected linear-threshold model over other ML architectures;
- adversarial-ML robustness;
- reinforcement-learning behavior;
- generalization under noise, distribution shift, unseen operational states, or stochastic training;
- detector accuracy, recall, false-positive rate, or attack prevalence;
- a globally optimal recovery policy;
- a pooled sample size with any other study.

The word **independent** in the Study-7 experiment refers to a stipulated model variable/experimental condition. It must not be transformed into an empirical claim that a deployed corroboration channel is organizationally, physically, cryptographically, or statistically independent unless new evidence is prospectively designed and collected.

## 10. Article-form gate

Study 7 is a complete finite experiment, so its scientific strength does not depend on increasing `N`. The main publication risk is instead the narrowness of the learner, scenario family, and external-validity envelope.

**Current article-form recommendation:** `CONCISE_ARTICLE_PREFERRED__DO_NOT_PAD`.

If AIAA Journal of Aerospace Information Systems is selected, an AIAA Technical Note is scientifically credible because AIAA describes Technical Notes as approximately 2,500-3,500 words for new significant data or developments of limited scope. A full archival paper remains possible only if the manuscript-level literature/assurance synthesis creates a genuinely necessary argument without importing unrelated studies or padding the evidence.

No article type is locked by this record.

## 11. Live venue-fit review

No venue is locked. Current ranking is a decision aid only.

### 11.1 AIAA Journal of Aerospace Information Systems — strongest topical fit, editorial-overlap caution

AIAA's current scope explicitly includes aerospace systems/software engineering, verification and validation of embedded systems, machine learning, autonomous systems, systems engineering, and safety/mission assurance, and it publishes Technical Notes.

Source: `https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/`

**Fit:** very strong for an assurance-focused learned aerospace decision component.  
**Risk:** Paper 1 is already under active JAIS review and supplies the Study-2/V5 antecedent. A second submission to the same journal must have unusually clean self-overlap disclosure and a clearly independent Study-7 evidence population.  
**Current rank:** 1, but **not locked**.

### 11.2 IEEE Transactions on Dependable and Secure Computing — strongest security/dependability alternative

TDSC publishes archival work on foundations, methodologies, and mechanisms for dependable and secure systems through design, modeling, evaluation, measurement, and simulation.

Source: `https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing`

**Fit:** strong if the paper generalizes the information-sufficiency/observable-trust argument beyond one satellite model while keeping the aerospace case concrete.  
**Risk:** the simple learner and finite modeled case may be viewed as insufficiently general or technically deep for a full TDSC article.  
**Current rank:** 2.

### 11.3 IEEE Transactions on Aerospace and Electronic Systems — strong scope, portfolio-overlap caution

TAES covers complex aerospace/space systems. Its Aerospace Information Systems technical area explicitly includes verification/validation, safety/mission assurance, systems/software engineering for AI-based systems, algorithms and AI. Its Avionics area includes cyber-physical security of space systems and AI certification/explainability concerns; Intelligent Systems includes resilient decision making under uncertainty and V&V.

Sources:

- `https://ieee-aess.org/publications/transactions-aes/technical-areas-editors/descriptions`
- `https://ieee-aess.org/publications/taes`

**Fit:** strong.  
**Risk:** Paper 2 has just been submitted to TAES from the same repository and already treats producer composition and residual trust. Study 7 is independent, but a second near-simultaneous TAES paper would require a very explicit novelty and related-manuscript disclosure.  
**Current rank:** 3.

### 11.4 Aerospace Science and Technology — plausible but higher scientific-depth mismatch risk

The journal scope includes complex system engineering, information processing, robotics and intelligent systems, and space vehicle/satellite engineering.

Source: `https://shop.elsevier.com/journals/aerospace-science-and-technology/1270-9638`

**Fit:** plausible.  
**Risk:** current aerospace-ML publications commonly present richer algorithmic, real-data, or performance validation. Study 7 intentionally does not.  
**Current rank:** 4.

### 11.5 Computers & Security — exclude under current scope

Elsevier's current journal listing states that since early 2024 Computers & Security has a moratorium on submissions in which AI or ML is a significant component, including applying AI/ML techniques to security/privacy or work directed at AI/ML-system security.

Source: `https://shop.elsevier.com/journals/subjects/physical-sciences-and-engineering/computer-science/computing-milieux`

Study 7 explicitly has ML as a significant scientific component.

**Disposition:** `OUT_OF_SCOPE__DO_NOT_TARGET_UNDER_CURRENT_POLICY`.

## 12. Reviewer-attack register

The following foreseeable criticisms must be answered in the manuscript design rather than hidden:

1. **"The main result is tautological."** A model cannot infer hidden truth from identical visible inputs. Response: do not claim that theorem as the novelty; frame the contribution as a controlled assurance experiment quantifying the consequence in a trusted satellite cyber-recovery decision architecture.
2. **"This is barely machine learning."** The learner is a small deterministic ERM linear-threshold model. Response: that simplicity is deliberate to isolate information availability from model capacity; do not market algorithmic novelty.
3. **"Independence is assumed."** Correct. The corroboration bit is stipulated independent in one experimental condition. The paper must distinguish modeled independence from deployed-channel independence.
4. **"There is no real spacecraft validation."** Correct. State this directly. No operational generalization is permitted.
5. **"The collision block has only nine rows."** The nine rows are a complete prespecified finite collision design, not a random sample. The limitation is scenario breadth, not sampling uncertainty.
6. **"Why aerospace?"** The paper must ground the decision semantics in satellite post-compromise recovery, current aerospace ML-assurance evidence needs, and the repository's space-specific recovery architecture without claiming flight validation.
7. **"This overlaps the author's earlier papers."** The manuscript must identify Study 2/V5 and Paper-2 producer-diversity results as antecedents, cite them when publicly available, and state that Study 7 contributes a separate frozen 1,033-observation population with a learned-selector question.

## 13. Reproducibility and integrity controls

The following remain mandatory:

- do not rerun Study 7 to seek a more publishable outcome;
- do not expand or replace the 1,033-observation frozen population;
- do not alter trained model search ranges or tie-breaking after seeing the result;
- preserve the independent audit and frozen output hashes;
- preserve all negative/conditional findings, including the two L1 lattice errors and the correlated-false-corroboration failure;
- do not convert deterministic finite counts into probabilistic operational rates;
- do not add inferential statistics where the frozen design does not define a sampling model;
- cite earlier submitted/published work rather than copying its text, tables, or evidence into Paper 3;
- any new external dataset, spacecraft testbed, HIL experiment, stochastic learner, additional corroboration architecture, or operational evidence requires a separately prospective protocol and authorization and would constitute new research, not an edit to frozen Study 7.

## 14. Gate decision

### GO

`GO__STUDY7_AS_NEXT_INDEPENDENT_PUBLICATION_BOUNDARY`

Rationale:

- separate frozen scientific population;
- complete finite evaluation and independent audit;
- coherent cybersecurity/aerospace-assurance question;
- clear separation from Study 5;
- manageable, explicitly documented antecedent overlap with Papers 1 and 2;
- live venue scopes exist that can accommodate an assurance-focused AI/aerospace contribution;
- current literature makes evidence sufficiency and assurance of learning-enabled aerospace components timely.

### NO-GO

- `NO_GO__STUDY5_PLUS_STUDY7_COMBINATION`
- `NO_GO__IMPORT_OTHER_STUDY_POPULATIONS`
- `NO_GO__ML_SUPERIORITY_FRAMING`
- `NO_GO__OPERATIONAL_OR_CERTIFICATION_CLAIMS`
- `NO_GO__COMPUTERS_AND_SECURITY_UNDER_CURRENT_AI_ML_MORATORIUM`
- `NO_GO__MANUSCRIPT_DRAFTING_FROM_THIS_GATE_ALONE`

## 15. Next gate

The next publication-development gate is **venue/article-form lock plus manuscript architecture**, using this boundary record as a hard constraint.

Before manuscript prose is drafted, that gate must:

1. choose the target venue and article type using live requirements;
2. decide whether JAIS Technical Note versus a concise full paper is scientifically preferable;
3. define one primary research question and a minimal contribution set;
4. create a self-overlap disclosure map against Paper 1, Paper 2, and Roadmap Paper 4;
5. freeze a manuscript claim ledger tied only to Study-7 canonical files and external literature;
6. define figures/tables from existing frozen Study-7 outputs only;
7. explicitly prohibit manuscript text from implying detector performance, operational autonomy, empirical real-world corroboration independence, or certification.

Actual publisher submission remains a separate explicit author-authorization gate.

---

## Canonical repository authorities used for this gate

- `study7/README.md`
- `study7/STUDY7_PROTOCOL.json`
- `study7/results/CANONICAL_FINDINGS.md`
- `study7/results/RESULTS_FREEZE.json`
- `study7/src/learned_selector_model.py`
- `study7/analysis/audit_independent.py`
- `study5/README.md`
- `docs/CURRENT_PUBLICATION_STATE.md`
- `docs/PUBLICATION_PHASE_MAP.md`
- `docs/RESEARCH_PROGRAM_PROVENANCE_AND_PUBLICATION_ROADMAP.md`
- `tracker/PUBLICATION_STATE.csv`
- submitted Paper-1 repository manuscript/provenance surfaces containing the Study-2/V5 antecedent
- submitted Paper-2 TAES manuscript/provenance surfaces describing producer composition/provenance diversity and residual-trust scope
- submitted Roadmap Paper-4 / Study-8 current-state authority

Historical stage-local records remain provenance and are not rewritten by this gate.
