# Paper 3 / Study 7 — Verified Source Ledger

**Ledger date:** 2026-09-07  
**Status:** `PRE_DRAFT_SOURCE_CONTROL__PRIMARY_AND_PUBLISHER_SOURCES_VERIFIED`  
**Target:** AIAA *Journal of Aerospace Information Systems* Technical Note  
**Study:** `S7-LSO-001`

This is a pre-drafting source-control record. It identifies sources that can support the manuscript's motivation, venue compliance, prior-work boundary, and novelty positioning. It is not manuscript prose and does not authorize claims beyond the frozen Study-7 evidence.

## 1. Publisher / venue authorities

### AIAA Journal of Aerospace Information Systems scope and article types

Source:

https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/

Verified 2026-09-07.

Relevant scope facts:

- JAIS publishes original work in aerospace computing, information, networks, and communications addressing aerospace-specific issues.
- Scope explicitly includes verification and validation of embedded systems, machine learning, autonomous systems, systems engineering, and safety/mission assurance.
- JAIS features Technical Notes for recent innovations/applications.
- AIAA describes Technical Notes as approximately 2,500–3,500 words for significant new data or developments of limited scope.
- Technical Notes do not use abstracts.

Use: venue/article-form justification only.

### AIAA journal acceptance procedure

Source:

https://www.aiaa.org/publications/journals/Journal-Author/journal-acceptance-procedure/

Verified 2026-09-07.

Relevant fact: initial editorial screening considers scope, technical validity, topical importance, timeliness, relationship to prior publication, conciseness, references, and length.

Use: development and desk-risk control.

### AIAA publication ethics

Source:

https://www.aiaa.org/publications/publish-with-aiaa/ethical-standards-for-publication-of-aiaa-technical-papers/

Verified 2026-09-07.

Relevant controls:

- avoid self-plagiarism/text recycling;
- avoid fragmentation of research publications;
- give each publication a complete account of a distinct aspect of the overall research;
- properly cite/disclose related prior work and publication history;
- avoid multiple submission of the same or closely related work.

Use: Paper-1/Paper-2 overlap and cover-letter disclosure control.

## 2. Public antecedent source for Study-2 V5/S1 lineage

### Study-2 public archive

Repository publication-verification authority:

`study2/release/phase6/ZENODO_PUBLICATION_VERIFICATION.md`

Verified repository facts:

- Zenodo record: `https://zenodo.org/records/22289114`;
- version DOI: `10.5281/zenodo.22289114`;
- concept DOI: `10.5281/zenodo.22289113`;
- publication date: `2026-09-04`;
- version: `1.0.0`.

Use in Paper 3:

This public, durable Study-2 archive should be the preferred citable provenance source for the Study-2 selector/V5 antecedent when possible, rather than relying on unpublished Paper-1 prose. Paper 1 itself must still be disclosed as a related manuscript to JAIS because it is under review there.

Boundary:

Study-2 data/results remain prior work and are not Paper-3 experimental evidence.

## 3. Aerospace ML assurance context

### NASA — Recommendations on Evidence and Process for Certification of Learning-enabled Components in Aerospace Systems

NASA Technical Reports Server record:

https://ntrs.nasa.gov/citations/20240006865

Publication date: 2024-06-07.

Relevant positioning:

- assurance requires justified confidence supported by evidence;
- evidence spans requirements, model/data properties, performance, implementation, integration, and V&V;
- coverage, traceability, formal methods, robustness/generalizability, and data validity are assurance concerns;
- the report explicitly does not define sufficient certification evidence for every criticality level.

Use in Paper 3:

Support the distinction between model performance and assurance/evidence sufficiency. Do not claim Study 7 is certified, certifiable, NASA-endorsed, or sufficient for certification.

## 4. Space cyber-recovery motivation

### SPARTA cyber-safe mode / recovery countermeasure CM0044

Source:

https://sparta.aerospace.org/countermeasures/CM0044

Live page checked 2026-09-07; page records last modification 2026-08-06.

Relevant motivation:

- spacecraft cyber-safe-mode/reconstitution concepts explicitly address cyber recovery;
- the page describes integrating cyber detection/response with fault management and recovery/reconstitution procedures;
- it emphasizes validated procedures and protected recovery state.

Use in Paper 3:

A domain motivation source only. Do not imply Study 7 implements SPARTA requirements, an operational cyber-safe mode, flight software, or mission-certified recovery.

## 5. Satellite/spacecraft ML comparison literature

These sources establish that recent aerospace ML work is heavily performance/detection/data oriented, helping define Paper 3's distinct downstream recovery-decision assurance niche.

### Validation-gated continual learning for anomaly detection in satellite telemetry

Acta Astronautica (2026).

DOI: `10.1016/j.actaastro.2026.07.065`

Focus: continual learning, validation-gated model updates, ESA telemetry benchmark, forecasting/anomaly-detection performance.

Paper-3 distinction: no continual learning and no detector benchmark; Study 7 tests post-detection recovery-decision observability.

### Transformer-based anomaly detection for satellite telemetry data

Acta Astronautica, 238 Part A (2026), 739–745.

DOI: `10.1016/j.actaastro.2025.09.035`

Focus: transformer architectures and anomaly-detection performance using satellite telemetry.

Paper-3 distinction: no transformer comparison and no anomaly-detection metric.

### The OPS-SAT benchmark for detecting anomalies in satellite telemetry

Scientific Data (2025).

Source:

https://www.nature.com/articles/s41597-025-05035-3

Focus: real OPS-SAT telemetry benchmark, annotated fragments, and benchmarking of anomaly-detection algorithms.

Paper-3 distinction: Study 7 is not a telemetry-detection benchmark and must not imply external operational validation.

### Explainable anomaly detection in spacecraft telemetry

Engineering Applications of Artificial Intelligence (2024).

DOI: `10.1016/j.engappai.2024.108083`

Focus: ML anomaly detection on real spacecraft telemetry and explainability/performance.

Paper-3 distinction: the target is trust/observability in recovery decision logic rather than explainability of a detector.

## 6. Secondary venue authority

### IEEE Transactions on Dependable and Secure Computing

Scope:

https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing

Topics:

https://www.computer.org/digital-library/journals/tq/tdsc-topics

Verified 2026-09-07.

Relevant facts:

- design/modeling/evaluation of dependable and secure systems;
- online recovery and authorization;
- experimental methods and V&V;
- safety-critical/aerospace computing;
- networks of satellites.

Disposition: credible secondary venue, not primary, because Study 7 is intentionally narrow and application-specific and does not presently offer the breadth of a general dependable-systems contribution expected for TDSC.

## 7. Related manuscript disclosure ledger

### Paper 1

Journal: AIAA *Journal of Aerospace Information Systems*  
Manuscript: `2026-09-I012066`  
Submitted: 2026-09-05  
Studies: 1 + 2 only.

Relationship to Paper 3:

- provides Study-2 V5/S1 antecedent;
- does not contain Study-7 population;
- no Paper-1 observations/tables/figures/statistics may be reused as Paper-3 evidence;
- disclose to JAIS before Paper-3 submission.

### Paper 2

Journal: IEEE *Transactions on Aerospace and Electronic Systems*  
Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`  
Submitted: 2026-09-07  
Studies: 3 + 4 + 6 only.

Relationship to Paper 3:

- conceptual overlap in trust composition/provenance diversity/residual trust boundaries;
- no Paper-2 evidence is reused;
- Paper 3 must not claim evidence independence/trust diversity as a new generic concept.

### Roadmap Paper 4

Journal: Acta Astronautica  
Manuscript: `AA-D-26-02872`  
Submitted: 2026-09-06  
Study: 8 only.

Relationship to Paper 3: low; cryptographic agility/contact-aware evidence remains separate.

## 8. Title collision / discoverability check

Searches performed 2026-09-07 for the exact working-title strings did not surface an obvious exact-title collision:

- `Evidence Observability Limits in Learned Satellite Cyber-Recovery Decisions`
- `Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence`

This is a discoverability check, not proof of global title uniqueness.

Title remains **not frozen** pending the first complete Technical Note draft and final novelty-language audit.

## 9. Citation-use rules

1. Prefer primary publisher, government/agency, standards/framework, original research, and repository provenance sources.
2. Do not cite a submitted manuscript as though it were published.
3. If an under-review related manuscript is referenced, state its status accurately and satisfy JAIS related-work disclosure requirements.
4. Do not use Paper 1, Paper 2, Paper 4, or Study 5 as replacement evidence for Study 7.
5. Do not use satellite anomaly-detection performance papers to infer recovery-policy performance.
6. Every numerical Study-7 statement must trace to the frozen accepted artifact, `RESULTS_FREEZE.json`, `CANONICAL_POLICY_SUMMARY.csv`, or an exact accepted Block-C row.
7. Recheck live publisher policies immediately before submission.

## 10. Pre-drafting disposition

**PASS** — a sufficient verified source base exists to begin controlled Technical Note prose while preserving the Study-7 claim boundary.

The next manuscript stage may draft only from the locked architecture and this source ledger; it must not broaden the research question or add scientific evidence without a new prospective authorization gate.
