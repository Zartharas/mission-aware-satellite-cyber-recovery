# Paper 3 / Study 7 — JAIS Technical Note Manuscript Architecture

**Architecture date:** 2026-09-07  
**Architecture status:** `PASS__JAIS_TECHNICAL_NOTE_LOCKED__RQ_AND_CONTRIBUTIONS_LOCKED__PROSE_NOT_YET_AUTHORIZED`  
**Study:** `S7-LSO-001`  
**Target journal:** AIAA *Journal of Aerospace Information Systems*  
**Article form:** Technical Note  
**Target length:** approximately 2,800–3,300 words, remaining below the AIAA Technical Note guidance of approximately 2,500–3,500 words  
**Abstract:** none; AIAA Technical Notes do not use an abstract  
**Branch:** `publication/paper3-study7-boundary-audit`

This record controls Paper-3 manuscript development before prose drafting. It freezes the publication question, contribution boundary, related-work separation, evidence-display inventory, and section budget. It does not modify the Study-7 protocol or frozen results and does not authorize publisher submission.

## 1. Venue and article-form decision

### Locked target

**AIAA Journal of Aerospace Information Systems — Technical Note.**

JAIS is the strongest current fit because its live scope includes aerospace computing and information systems, verification and validation of embedded systems, machine learning, applications of autonomous systems, systems engineering, and safety/mission assurance. The Technical Note form is specifically intended for significant developments of limited scope and avoids forcing this finite assurance experiment into a 10,000–12,000-word full article.

Live AIAA sources checked 2026-09-07:

- Journal scope and content: https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/
- Acceptance procedure: https://www.aiaa.org/publications/journals/Journal-Author/journal-acceptance-procedure/
- Publication ethics: https://www.aiaa.org/publications/publish-with-aiaa/ethical-standards-for-publication-of-aiaa-technical-papers/

### Why not a JAIS full-length paper

A full paper would create pressure to add unrelated experiments, reproduce already-submitted Study-2 context at excessive length, or inflate a deliberately narrow finite assurance result. Those actions would increase fragmentation and self-overlap risk without adding scientific evidence.

### Why TDSC is secondary rather than primary

IEEE *Transactions on Dependable and Secure Computing* is substantively relevant: its scope covers secure/dependable system design, modeling and evaluation, online recovery, authorization, experimental methods, V&V, aerospace safety-critical computing, and networks of satellites. However, TDSC generally expects a broad archival systems contribution with substantial technical novelty. Study 7's intentionally simple linear-threshold learner and application-specific finite model make desk/reviewer risk higher there than at JAIS.

Current TDSC sources checked 2026-09-07:

- https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing
- https://www.computer.org/digital-library/journals/tq/tdsc-topics

### Why TAES is not primary

TAES is in scope for aerospace information systems and concise correspondence/regular-paper contributions, but Paper 2 has just been submitted there and already develops the repository's temporal-evidence, producer-composition, and artifact-assurance trust-boundary line. Sending Study 7 to TAES would create avoidable same-program concentration and sharper self-overlap questions without a better scope match than JAIS.

### Computers & Security

Not selected. Study 7 has ML as a significant scientific component, and the repository already records this as a separate AI/ML-compatible publication line.

## 2. One primary research question

**RQ1. How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and how does adding a corroborating observable change that boundary when corroboration is independent versus correlated with the compromised evidence path?**

This is the only primary research question for Paper 3.

The paper must not split this into multiple nominal RQs merely to make the Technical Note appear larger. The three experimental blocks are complementary tests of this single information-sufficiency question.

## 3. Scientific contribution ledger

Only the following contribution claims are authorized.

### C1 — Exhaustive finite assurance construction

Paper 3 may claim a deterministic finite assurance experiment for learned satellite cyber-recovery decisions that exhausts:

- all 256 eight-feature policy-visible states for both the deterministic visible-only comparator and the visible-only learner;
- all 512 nine-feature states for the corroboration-aware learner; and
- three hidden-truth/corroboration collision scenarios crossed with all three policies.

The resulting evidence population is exactly 1,033 observations. This is a complete modeled population, not a random sample from operational spacecraft behavior.

### C2 — Visible-boundary fit does not establish hidden-truth correctness

Paper 3 may report that `L0_ERM_VISIBLE_ONLY` learned an exact S1-equivalent visible-state decision boundary with zero training error and zero error across all 256 visible states, while `D0_S1_VISIBLE_ONLY` and `L0_ERM_VISIBLE_ONLY` both proceed in the signed-but-false hidden-truth collision because the eight policy-visible inputs are identical.

Interpretation: exact fit to the observable decision boundary does not establish correctness against truth that is absent from the model input.

This is an application-specific assurance result. It is not a claim that the general concept of partial observability is novel.

### C3 — Independent corroboration changes information; correlated failure restores the boundary

Paper 3 may report that `L1_ERM_WITH_INDEPENDENT_CORROBORATION` avoids the unsafe proceed in `V5_INDEPENDENT_DISAGREEMENT`, while all three policies proceed unsafely in `V5_CORRELATED_FALSE_CORROBORATION`.

Across the complete 512-state extended lattice, L1 has exactly two objective decision errors: one unsafe proceed and one false-conservative hold.

Interpretation: the benefit arises from the additional observable and its independence assumptions, not from learner complexity alone. Corroboration is not a free improvement; it introduces its own safety/availability boundary and fails when the corroborating evidence path shares the false state.

### C4 — Reproducible, hash-frozen assurance evidence

Paper 3 may report that the accepted deterministic execution is provenance-bound and independently audited. The independent auditor reconstructs the objective, both learned models, and all 1,033 decisions and records zero mismatches.

The accepted artifact and the four core deterministic outputs are SHA-256 frozen.

## 4. Explicit non-contributions / forbidden claims

Paper 3 must not claim:

- a new general theorem of partial observability;
- that machine learning is inferior or superior to deterministic recovery logic in general;
- global model ranking;
- neural-network, deep-learning, reinforcement-learning, or adversarial-ML results;
- operational spacecraft autonomy;
- real spacecraft, RF, ground-station, HIL, flight, CPU, energy, or latency validation;
- detector accuracy, precision, recall, false-positive rate, or anomaly-detection performance;
- certification or certification sufficiency;
- that the modeled corroboration signal is operationally independent merely because it is labeled independent in the protocol;
- statistical population inference, confidence intervals, p-values, or probability estimates from the deterministic finite lattice;
- that a larger learner could recover hidden truth without new observables;
- that Study 5, CuCD-ID, or any earlier submitted study externally validates Study 7.

## 5. Frozen evidence ledger

### Scientific protocol

`study7/STUDY7_PROTOCOL.json`

- protocol title: *Learned Selector Observability Under Adversarial Evidence and Independent Corroboration*;
- study type: deterministic finite machine-learning assurance study;
- eight visible features plus one extended corroboration feature;
- visible-only training prototypes: 10;
- corroboration training prototypes: 13;
- deterministic ERM over an integer linear-threshold hypothesis class.

### Accepted execution

- workflow run: `33689625480`;
- accepted execution commit: `f1530b0b2e81a5916adaf7ce808075156424dfb5`;
- artifact ID: `9869488192`;
- artifact name: `study7-lso-001-evidence-f1530b0b2e81a5916adaf7ce808075156424dfb5`;
- artifact SHA-256: `26b522d2692516aa1b4ae62d032a9a909dbaccd7ef1a74104080c39bdf3a091b`;
- GitHub Actions artifact expiration currently recorded as 2026-12-01.

### Frozen core output identities

| File | Frozen SHA-256 |
|---|---|
| `observations.csv` | `5d66fe1db266e3a98532d0d0e63d1bc1a5d24eed0e831b5c91bdaa94f60d00b5` |
| `policy_summary.csv` | `bf6069e200be76f324032133b8bf5e20ad3df33d57a59d985d3e3d828304d34d` |
| `TRAINED_MODELS.json` | `8adafec923d756d91ec68c563d608ba27f5d224fea1907d5753c33944d54b362` |
| `REPORT.json` | `cd85ac132eeff15d72b9e995127d267cefbd49d033fc776885f0bfe7caef48c1` |

The exact accepted artifact was downloaded read-only on 2026-09-07 and all four core file hashes were independently recomputed and matched the frozen values above. No reexecution occurred.

### Frozen trained models

`L0_ERM_VISIBLE_ONLY`:

- quality weight = 2;
- authorization weight = 1;
- security weight = -1;
- threshold = 12;
- training errors = 0.

`L1_ERM_WITH_INDEPENDENT_CORROBORATION`:

- quality weight = 2;
- authorization weight = 0;
- corroboration weight = 1;
- security weight = -1;
- threshold = 12;
- training errors = 0.

## 6. Exact result ledger

### Block A — visible-state lattice

- `D0_S1_VISIBLE_ONLY`: 256 observations, 0 objective-decision errors, 0 unsafe proceeds, 0 false-conservative holds, 3 proceed decisions.
- `L0_ERM_VISIBLE_ONLY`: 256 observations, 0 objective-decision errors, 0 unsafe proceeds, 0 false-conservative holds, 3 proceed decisions.

### Block B — corroboration lattice

- `L1_ERM_WITH_INDEPENDENT_CORROBORATION`: 512 observations, 2 objective-decision errors, 1 unsafe proceed, 1 false-conservative hold, 6 proceed decisions.

### Block C — hidden-truth collision

For all three scenarios, the eight-feature base vector remains fully qualifying and identical. Only research-only hidden authorization and, for L1, the corroboration bit distinguish the adjudicated scenarios.

`SAFE_CORROBORATED`:

- objective safe-to-proceed = 1;
- D0 proceeds, safe;
- L0 proceeds, safe;
- L1 proceeds with corroboration = 1, safe.

`V5_INDEPENDENT_DISAGREEMENT`:

- hidden authorization = 0;
- objective safe-to-proceed = 0;
- D0 proceeds unsafely;
- L0 proceeds unsafely;
- L1 sees corroboration = 0 and holds; unsafe-proceed = 0.

`V5_CORRELATED_FALSE_CORROBORATION`:

- hidden authorization = 0;
- objective safe-to-proceed = 0;
- D0 proceeds unsafely;
- L0 proceeds unsafely;
- L1 sees corroboration = 1 and also proceeds unsafely.

## 7. Frozen table / figure inventory

The Technical Note should be visually sparse. No display may introduce new analysis.

### Table I — Model and information boundary

**Status:** authorized publication table; direct transcription/condensation only.

Sources:

- `study7/STUDY7_PROTOCOL.json`;
- accepted `TRAINED_MODELS.json`;
- `study7/results/RESULTS_FREEZE.json`.

Columns should identify:

- policy;
- visible inputs;
- whether corroboration is visible;
- learned/fixed status;
- frozen weights/threshold where applicable;
- hidden authorization available to policy? always no.

No performance ranking language.

### Table II — Exact finite-population outcomes

**Status:** authorized publication table; direct transcription only.

Primary source:

`study7/results/CANONICAL_POLICY_SUMMARY.csv`

The canonical six rows are:

| Block | Policy | N | Errors | Unsafe proceed | False conservative | Proceed decisions |
|---|---|---:|---:|---:|---:|---:|
| A | D0 | 256 | 0 | 0 | 0 | 3 |
| A | L0 | 256 | 0 | 0 | 0 | 3 |
| B | L1 | 512 | 2 | 1 | 1 | 6 |
| C | D0 | 3 | 2 | 2 | 0 | 3 |
| C | L0 | 3 | 2 | 2 | 0 | 3 |
| C | L1 | 3 | 1 | 1 | 0 | 2 |

The paper must make clear that these are counts over complete finite modeled states, not estimates of operational error rates.

### Table III or compact inset — Three collision scenarios

**Status:** optional; preferred only if Table II cannot communicate the mechanism clearly.

Source: the nine exact Block-C rows from the accepted, hash-frozen `observations.csv`.

The display may show scenario, hidden authorization, L1 corroboration, objective, and D0/L0/L1 decisions. It must not calculate new metrics.

### Figure 1 — Observability/trust-path schematic

**Status:** optional, non-evidentiary conceptual figure.

If created, it may depict:

1. the eight policy-visible inputs feeding D0/L0;
2. the additional corroboration input feeding L1;
3. research-only hidden authorization outside all policy inputs;
4. independent versus correlated false corroboration paths.

The figure must be explicitly labeled as a conceptual schematic derived from the frozen protocol, not empirical spacecraft architecture or operational topology.

### No performance plots

Do not create ROC curves, accuracy charts, bar charts implying sampled rates, confidence intervals, training curves, timing plots, or model-ranking graphics. They are unsupported by the frozen design and would distort the claim boundary.

## 8. Self-overlap and related-publication disclosure map

### Paper 1 — JAIS manuscript `2026-09-I012066`

Paper 1 uses Studies 1 and 2 only.

Relevant antecedents available to Paper 3 as prior work/specification lineage:

- Study-2 V5 signed-but-false producer condition;
- deterministic S1 evidence-aware selector semantics;
- the principle that valid/current policy-visible evidence can remain false relative to research-only adjudication truth.

Paper 3 must not reuse Paper-1 observations, statistical results, tables, figures, wording, or claim its V5 antecedent as new.

Paper-3 novelty begins with the separately frozen Study-7 learner, exhaustive visible/corroboration state spaces, and hidden-truth collision/corroboration analysis.

Because Paper 1 is currently under review at the same journal, its relationship must be disclosed to JAIS at submission. Avoid textual recycling; paraphrase and cite/disclose the antecedent rather than copying Paper-1 prose.

### Paper 2 — TAES submission UUID `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`

Paper 2 uses Studies 3, 4, and 6 only.

Conceptual overlap:

- trust composition;
- producer/provenance diversity;
- residual trust boundaries.

Paper 3 must not claim trust diversity or independent evidence as a new general concept, nor reuse Paper-2 data, figures, or results.

Distinct Paper-3 contribution:

- learned decision logic under fixed observability;
- exact visible-state reproduction;
- hidden-truth collision;
- extra observable versus correlated-failure boundary.

### Roadmap Paper 4 — Acta manuscript `AA-D-26-02872`

Study 8 is a cryptographic-agility/contact-aware modeled study. Its evidence, PQC claims, policy results, and submission package remain outside Paper 3.

Overlap risk is low. Use only background citation if directly necessary.

### Study 5 / `S5-CUCD-001`

Study 5 is deferred and is not part of Paper 3. Do not use the CuCD-ID external dataset as evidence for Study 7 and do not imply external empirical validation.

## 9. Literature positioning boundary

The Technical Note should distinguish its contribution from two adjacent literatures.

### Aerospace ML assurance

NASA's 2024 technical memorandum on evidence and process for certification of learning-enabled aerospace components emphasizes requirements, model/data properties, robustness/generalizability, integration, lifecycle evidence, coverage, traceability, and V&V. This supports framing Study 7 as an assurance/evidence-sufficiency problem rather than a model-performance paper.

Source:

- https://ntrs.nasa.gov/citations/20240006865

The manuscript must not imply NASA certification endorsement or that Study 7 satisfies certification evidence requirements.

### Satellite/spacecraft ML performance literature

Recent work predominantly emphasizes anomaly-detection performance, real/satellite telemetry datasets, continual learning, transformers, explainability, or deployability. Examples to review/cite where relevant include:

- *Validation-gated continual learning for anomaly detection in satellite telemetry*, Acta Astronautica, DOI `10.1016/j.actaastro.2026.07.065`;
- *Transformer-based anomaly detection for satellite telemetry data*, Acta Astronautica, DOI `10.1016/j.actaastro.2025.09.035`;
- *The OPS-SAT benchmark for detecting anomalies in satellite telemetry*, Scientific Data (2025), https://www.nature.com/articles/s41597-025-05035-3;
- NASA assurance memorandum `20240006865` above.

Paper 3 should state that its target is downstream recovery-decision assurance under compromised evidence, not anomaly-detection benchmark performance.

## 10. Section architecture and word budget

AIAA Technical Notes do not use an abstract. Keep the note self-contained but concise.

### Title

**Status:** not yet frozen.

Preferred working title:

**Evidence Observability Limits in Learned Satellite Cyber-Recovery Decisions**

Alternative working title:

**Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**

Do not use a title that promises operational spacecraft validation, generic AI safety, certification, adversarial ML, or global ML superiority.

### I. Introduction — target 450–550 words

Required functions:

- define the downstream recovery-decision problem;
- distinguish detection from recovery selection;
- state the signed-but-false evidence problem as prior motivation, not new discovery;
- identify the gap: whether a learned selector with the same observables changes the boundary, and what an additional corroborating observable changes;
- state RQ1 once;
- list C1–C4 concisely;
- disclose that Study 7 is deterministic finite and separately frozen.

### II. Assurance and novelty boundary — target 350–450 words

Required functions:

- place the work against aerospace ML assurance/V&V;
- contrast with satellite anomaly-detection/performance literature;
- explain that partial observability and redundancy are not claimed as new general theory;
- state the specific application-level novelty and related-publication separation.

Do not turn this into a broad literature survey.

### III. Study design — target 650–750 words

Required functions:

- define eight visible inputs and the corroboration bit;
- define hidden authorization as research-only adjudication;
- define D0, L0, and L1;
- describe deterministic ERM and tie-break without overstating ML complexity;
- describe Blocks A, B, C and exact finite population;
- identify primary endpoints;
- state freeze/provenance and independent audit.

Recommended display: Table I.

### IV. Results — target 650–750 words

Required functions:

- Block A exact visible-state equivalence;
- Block B two exact errors and their types;
- Block C safe, independent-disagreement, and correlated-false-corroboration outcomes;
- answer RQ1 directly with counts, not statistical inference.

Recommended display: Table II; optional compact Table III if needed.

### V. Discussion and limitations — target 500–600 words

Required functions:

- distinguish model fit from information sufficiency;
- explain why added observability, not complexity alone, changes the modeled decision boundary;
- explain correlated evidence failure;
- connect cautiously to assurance of learned aerospace recovery components;
- state all major external-validity limits;
- avoid certification or operational claims;
- explain relation to earlier submitted papers without reusing their evidence.

### VI. Conclusion — target 150–200 words

Required functions:

- one direct answer to RQ1;
- one assurance implication;
- one bounded limitation/future-work statement.

No new result or venue marketing language.

### Target total

Approximately **2,750–3,300 words** before references and display-equivalent adjustments, with an editorial preference toward the lower end if all evidence can be communicated cleanly.

## 11. Pre-drafting citation/source checklist

Before full prose is written:

1. Build a small verified bibliography using current primary/publisher sources.
2. Resolve how the still-under-review Paper-1 antecedent will be cited/disclosed without implying publication status it does not have.
3. Identify any public Study-2 archival/provenance source that can support the V5/S1 antecedent independently of unpublished Paper-1 text.
4. Verify all current JAIS Technical Note formatting requirements at the time the manuscript template is instantiated.
5. Recheck current journal ethics/policies immediately before submission.

## 12. Accepted-artifact preservation requirement

The accepted workflow artifact is currently available but recorded to expire on **2026-12-01**.

Before that date, create a permanent, provenance-preserving archive of the exact accepted Study-7 evidence bytes without rerunning the experiment or changing any frozen file. Suitable mechanisms may include a repository release or an external archival repository such as Zenodo, subject to a separate archival authorization and hash verification.

The archive must preserve at minimum:

- `observations.csv`;
- `policy_summary.csv`;
- `TRAINED_MODELS.json`;
- `REPORT.json`;
- `EXECUTION_PROVENANCE.json`;
- `INDEPENDENT_AUDIT.txt`;
- the artifact-level SHA-256 and individual frozen SHA-256 identities.

This preservation action is a reproducibility safeguard, not a scientific reexecution.

## 13. Submission-control gate

Manuscript development does not equal submission authorization.

Before any JAIS submission:

- complete a line-by-line scientific claim audit against the frozen Study-7 evidence;
- complete a related-work/self-overlap comparison against Paper 1, Paper 2, and Paper 4;
- disclose related manuscripts as required by AIAA policy;
- confirm the Technical Note still fits current JAIS scope and article-type rules;
- confirm no frozen or submitted paper has changed in a way that alters the overlap analysis;
- obtain explicit final author authorization for publisher submission.

## 14. Current gate disposition

**GO** — develop a concise JAIS Technical Note around Study 7 only.

**NO-GO** — full-length padding, Study-5 combination, new scientific execution, imported prior-study evidence, operational spacecraft claims, ML-superiority claims, or publisher submission without a new final authorization gate.

The next authorized development action after author review of this architecture is controlled manuscript drafting from this locked structure and source ledger.
