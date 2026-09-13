# Paper 3 / Study 7 — CEAS Closest-Prior-Work and Novelty Audit

**Audit date:** 2026-09-12  
**Status:** `PASS__SCIENTIFICALLY_DISTINCT__TARGETED_CITATIONS_REQUIRED`  
**Target journal:** CEAS Space Journal  
**Target article type:** Original Research Article  
**Study:** `S7-LSO-001`

## Purpose

This audit evaluates the CEAS Space Journal papers closest to Paper 3 in topic or mechanism and records whether they threaten novelty, should be cited, or should be excluded as tangential. It is a publication-development control only; it does not alter Study-7 science, the frozen 1,033-observation population, or any submitted paper.

## Paper-3 scientific identity

Paper 3 studies **decision assurance under compromised evidence**. Its central question is whether a learned satellite cyber-recovery selector can make an adjudicated-correct decision when the information needed to distinguish safe from unsafe recovery is not present in the selector's visible inputs, and what changes when a corroborating observable is added under independent versus correlated failure.

The experimental evidence is the separately frozen Study-7 population:

- Block A: 512 observations over the complete eight-feature visible-state lattice for the deterministic comparator and visible-only learner;
- Block B: 512 observations over the complete nine-feature corroboration lattice for the corroboration-aware learner;
- Block C: 9 hidden-truth/corroboration collision observations;
- total: 1,033 exact deterministic observations;
- independent repository audit: 0 mismatches.

The principal endpoints are `objective_decision_error`, `unsafe_proceed`, `false_conservative_hold`, hidden-truth collision indistinguishability, and resolution/failure of corroboration under prespecified trust relationships.

## 1. Wanninger — knowledge-based satellite FDIR

**Source:** Sascha Wanninger, “Knowledge-based satellite failure detection, isolation and recovery (FDIR),” CEAS Space Journal, vol. 18, pp. 991–1004, 2026. DOI: https://doi.org/10.1007/s12567-025-00651-6

### What that paper does

The paper implements a CLIPS production-rule system as an onboard FDIR component, integrates it with a PUS-oriented onboard software architecture, and validates the concept using a rover platform. Its contribution is flexible rule-based failure handling: domain experts can represent and update FDIR logic outside dedicated OBSW code, with recovery actions coordinated through rules and PUS services.

The paper discusses machine learning as an alternative/data-driven monitoring paradigm, but its implemented contribution is explicitly a human-expert rule-base approach rather than a learned recovery selector. Its evaluation concerns FDIR implementation, integration, explainability/flexibility, and execution behavior.

### Overlap with Paper 3

Shared high-level territory:

- satellite recovery and autonomy;
- decision logic after a detected abnormal condition;
- interest in explainable/structured recovery logic;
- onboard or spacecraft-relevant recovery context.

Material differences:

- Wanninger addresses **fault detection/isolation/recovery implementation**, not cyber-recovery authorization under adversarial evidence;
- Wanninger uses a **CLIPS expert system**, not a learned ERM selector;
- Wanninger does not model a compromised trusted producer, signed-but-false evidence, hidden adjudication truth, or correlated corroboration failure;
- its evaluation uses a rover/OBSW integration scenario rather than an exhaustive binary information-state lattice;
- its main outputs concern FDIR rule execution and implementation practicality, not objective-decision error, unsafe proceed, or information sufficiency.

### Disposition

**CITE.** This is directly relevant adjacent work and should appear in Paper 3's related-work section as an example of spacecraft FDIR/recovery logic implemented through explicit expert rules. Citing it reduces reviewer risk because it shows that Paper 3 is not claiming to invent satellite recovery logic or onboard autonomous failure handling.

**Novelty risk:** low. The papers solve different research questions.

## 2. Kübler et al. — in-orbit AI optical computing concept

**Source:** Felix Kübler, Mingwei Yang, Lennart Mannteuffel, Okan Akyüz, Janik Wolters, Enrico Stoll, “Concept of an in-orbit AI-system based on optical computing,” CEAS Space Journal, vol. 18, pp. 57–68, 2026. DOI: https://doi.org/10.1007/s12567-025-00612-z

### What that paper does

The paper conceptualizes a hybrid optical/electronic computing payload for in-orbit machine-learning workloads. Its central problem is compute feasibility under spacecraft power, thermal, radiation, and payload-integration constraints. The paper proposes optical vector-matrix multiplication, discusses satellite-bus integration, and reports preliminary optical and simulated classification results.

### Overlap with Paper 3

Shared high-level territory:

- artificial intelligence / machine learning in space;
- spacecraft-constrained computing context.

Material differences:

- no cyber-recovery decision problem;
- no security or compromised-evidence threat model;
- no recovery or reconfiguration mechanism;
- no assurance analysis of decision inputs;
- no hidden-truth/corroboration experiment;
- hardware/payload-compute architecture rather than decision-assurance methodology.

### Disposition

**DO NOT CITE solely for venue familiarity.** It is not close enough to the scientific question to justify a mandatory citation. It may be cited only if the manuscript includes a specific statement about the broader trend toward onboard AI and spacecraft compute constraints. Adding it merely because it was published in CEAS would weaken the focus of the related-work section.

**Novelty risk:** negligible.

## 3. Tappe et al. — AI-based anomaly detection, diagnosis, and reconfiguration

**Source:** Mark Tappe et al., “A supervised AI-based toolchain for anomaly detection, diagnosis, and reconfiguration for the life-support system of the COLUMBUS module of the ISS,” CEAS Space Journal, 2025. DOI: https://doi.org/10.1007/s12567-025-00654-3

### Why this is the closest CEAS neighbor

This paper is more scientifically adjacent to Study 7 than the optical-computing paper because it combines AI, anomaly detection, diagnosis, and reconfiguration in a safety-critical space-system context. It uses time-series ML for anomaly detection, expert/model-based diagnosis, reconfiguration logic, supervisory evaluation, and MLOps integration for the ISS COLUMBUS life-support system.

### Important difference

Its core question is **how to detect, diagnose, and recommend/reconfigure around faults** in a physical life-support system. Paper 3's core question is **whether a recovery authorization decision remains trustworthy when the evidence presented to the selector can be valid-looking but false because the evidence path itself is compromised**.

The Tappe paper does not present a cyber-adversary model, signed-but-false trusted evidence, policy-visible versus hidden authorization truth, or independent-versus-correlated corroboration failure. Its use of “cyber-physical” describes the system class, not a cybersecurity/adversarial-evidence experiment.

### Disposition

**CITE.** This is the most useful CEAS-native contrast paper. Paper 3 should explicitly state that existing AI-enabled space fault-management work can integrate detection, diagnosis, and reconfiguration, while Study 7 addresses a different downstream assurance question: whether the evidence driving a recovery authorization decision is sufficient and trustworthy when an adversary can compromise an evidence producer.

**Novelty risk:** moderate if ignored, low if cited and separated explicitly.

## 4. Other relevant CEAS literature checked

### Schefels et al. — Synthetic satellite telemetry data for machine learning

DOI: https://doi.org/10.1007/s12567-024-00589-1

Focus: generation of labeled synthetic telemetry for ML training, validation, and anomaly-detection benchmarking. This reinforces the distinction between detector/data quality and downstream recovery-decision assurance.

**Disposition:** optional citation if a concise CEAS-native anomaly-detection/data contrast is useful.

### Herrmann et al. — Unmasking overestimation in deep anomaly detection

DOI: https://doi.org/10.1007/s12567-023-00529-5

Focus: re-evaluation of deep anomaly-detection performance on spacecraft telemetry. This is useful background for the point that model-performance evaluation is not identical to recovery-decision assurance.

**Disposition:** optional; use only if the related-work section needs a stronger anomaly-detection evaluation contrast.

## 5. Novelty comparison matrix

| Dimension | Wanninger FDIR | Kübler in-orbit AI | Tappe AI reconfiguration | Paper 3 / Study 7 |
|---|---|---|---|---|
| Primary problem | FDIR implementation | AI compute/payload concept | anomaly detection, diagnosis, reconfiguration | cyber-recovery decision assurance under compromised evidence |
| Decision mechanism | CLIPS rule base | neural-network/optical compute concept | ML + diagnosis + reconfiguration toolchain | deterministic comparator + learned ERM selectors |
| Security adversary | No | No | No explicit cyber-adversarial evidence model | Yes, signed-but-false/compromised evidence path |
| Hidden adjudication truth | No | No | No | Yes |
| Corroboration independence/correlation | No | No | No | Explicit experimental factor |
| Population | integrated rover/OBSW scenario | hardware/simulation results | ISS/ECLSS data/toolchain evaluation | exhaustive finite 1,033-state population |
| Main endpoint | FDIR behavior/implementation | compute feasibility/performance | detection/diagnosis/reconfiguration | unsafe proceed / false-conservative hold / decision error |
| Core contribution | flexible expert-rule FDIR | optical onboard AI architecture | holistic AI fault-management toolchain | information-sufficiency/trust-boundary assurance for learned recovery decisions |

## 6. Rejection-risk assessment

### Similar-work desk rejection

**Assessment: LOW**, provided the manuscript cites and distinguishes the closest work.

Paper 3 is not another implementation of FDIR, another anomaly detector, another reconfiguration planner, or another onboard AI computing platform. Its contribution is the adversarial information/trust boundary of the recovery selector itself.

### Reviewer misclassification risk

**Assessment: MODERATE if framing is loose; LOW after controlled revision.**

A reviewer could initially group the work with AI-FDIR/reconfiguration if the introduction simply says “AI for satellite recovery.” The manuscript should instead say, early and explicitly, that Study 7 begins after a security signal exists and does not optimize fault detection, diagnosis, or recovery planning. It evaluates whether a learned authorization selector can make the correct recovery decision from the evidence visible to it when that evidence may be compromised.

### Novelty overclaim risk

**Assessment: controlled.**

Do not claim:

- invention of satellite FDIR or autonomous recovery;
- invention of AI/ML in spacecraft operations;
- a new general theorem of partial observability;
- generic superiority of learned or deterministic recovery logic;
- operational proof that corroboration is independent.

The novel claim remains application-specific: exhaustive assurance evaluation of learned satellite cyber-recovery decisions under signed-but-false evidence and modeled independent/correlated corroboration.

## 7. Required manuscript citation action

For the CEAS version of Paper 3:

1. **Add Wanninger (FDIR) as a direct related-work citation.**
2. **Add Tappe et al. as the closest AI fault-management/reconfiguration citation.**
3. Keep anomaly-detection literature to a small number of representative sources; do not inflate the bibliography with tangential ML papers.
4. Do **not** cite Kübler et al. unless a specific onboard-AI/computing-context claim requires it.
5. State the exact novelty separation in the Introduction/Related Work: prior work addresses fault detection, diagnosis, recovery implementation, reconfiguration, and onboard AI; Study 7 instead evaluates decision correctness when policy-visible recovery evidence may itself be adversarially wrong.

## 8. Gate disposition

**PASS — CEAS remains a strong target.**

The closest published CEAS papers do not subsume Study 7's scientific question, experimental design, adversarial evidence model, endpoints, or principal result.

The venue-switch may proceed without changing the frozen science.
