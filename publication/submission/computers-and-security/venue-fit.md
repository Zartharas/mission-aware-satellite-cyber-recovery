# Venue Fit and Backup Strategy

## Primary: Computers & Security (Elsevier)

### Why the two-study article fits

Computers & Security targets the information-security community and emphasizes research with practical security relevance. The manuscript's core contribution is a controlled **post-detection response/recovery** investigation rather than cryptology, intrusion-detection model development, or general aerospace performance analysis.

The article now reports two separately frozen studies. Study 1 establishes the baseline comparative response/recovery method under mission-state, modeled-contact, and evidence-sufficiency conditions. Study 2 prospectively raises the security bar with stale/replay evidence, contradiction, post-signature manipulation, bounded producer compromise, multiple contact regimes, context ablations, and adversary-budget stress. The two populations remain separate: 720 VALID observations in Study 1 and 3,872 VALID observations in Study 2.

The topic has direct venue adjacency. Recent Computers & Security work includes space-sector attack-surface analysis, SatCom cybersecurity, satellite intrusion detection, cyber-physical security testbeds, and intrusion-response research. These establish a credible applied-security neighborhood without implying that each prior implementation lacks every dimension considered here.

The manuscript is differentiated by the joint evaluation of response/recovery policies under common cyber-physical constraints; explicit evidence-integrity and authorization/contact factors; separate security, mission, command-availability, and recovery outcomes; independent result reproduction for Study 2; and strict retention of negative/null/conditional findings.

### Current scope constraints that matter

The journal's current page was rechecked on **2026-09-01**.

**Cryptology.** Cryptology remains excluded as a principal component. This manuscript uses cryptographic/evidence checks as bounded system mechanisms and provenance controls; it does not contribute a new cryptographic algorithm or protocol.

**AI/ML moratorium.** The current journal page still displays the moratorium language for submissions in which AI/ML is a significant scientific component. Neither Study 1 nor Study 2 uses AI/ML as the response mechanism. Their evaluated selectors and baselines are **frozen deterministic rule-based policies**. This distinction must stay explicit in the title/abstract, Methods, cover letter, and submission metadata so “mission-aware,” “context-aware,” or “adaptive” wording is not mistaken for learned autonomy.

AI-assisted manuscript preparation, source checking, reproducibility reconstruction/review, and code testing are separately disclosed under Elsevier publication policy; they are not experimental treatment mechanisms.

### Desk-review positioning

Lead with the transferable cybersecurity decision problem:

- detection/event establishment is a precondition;
- the evaluated problem begins at response selection and recovery;
- authorization/contact availability can change containment/recovery behavior;
- evidence integrity and evidence sufficiency can change response selection;
- authenticated/current policy-visible evidence can still be false under bounded producer compromise;
- containment, evidence-qualified recovery, and objective correctness are distinct concepts;
- conservative security behavior can impose mission/command-availability cost;
- negative, equivalent, and adverse policy outcomes are retained;
- no weighted global score or global policy rank is used.

The satellite setting is materially important because intermittent contact, command authority, recovery windows, mission continuity, and evidence availability make response/recovery decisions nontrivial. The methodological lessons remain relevant to cyber-resilience and other cyber-physical systems.

Avoid positioning the article as:

- a new Mission Aware theory;
- a new satellite IDS;
- a satellite threat taxonomy;
- an AI/ML autonomy paper;
- a cryptographic-protocol paper;
- an empirical proof that benign and adversarial causes are distinguishable or indistinguishable from matched observations;
- a flight-autonomy certification study;
- a real-RF or operational-spacecraft experiment;
- a universal policy-superiority result.

### Study-2 reviewer-sensitive boundaries

**RQ3 structural-control boundary.** All 54 Block-C BENIGN/ADVERSARIAL contrasts are zero, but the frozen runtime changes only the cause label within each ambiguity family; hidden truth and generated policy-visible evidence remain the same. This is a structural label-invariance/control check, not empirical causal-discrimination evidence.

**K4 boundary.** K4 is intermittent/flapping contact and is not ordinal severity 4.

**A2/K2 boundary.** A2/K2 combines producer compromise with modeled contact loss and cannot support an unconfounded adversary-only effect claim.

**Logical-time boundary.** Study-2 times are deterministic logical SIL seconds, not real spacecraft, network, ground-station, or operator latency.

**Multiplicity/sample boundary.** Secondary n=32 blocks are sensitivity/estimation evidence. They were not prospectively powered for small-effect confirmatory inference.

### Primary submission risks and mitigations

**Domain-specificity risk.** A desk editor could view the paper as aerospace systems engineering. Mitigation: foreground the post-detection security response/recovery problem, trust/evidence boundaries, adversarial evidence mechanisms, incident-response positioning, and practical security dependencies.

**AI/ML scope-confusion risk.** “Mission-aware” or “context-aware” can be misread as learned autonomy. Mitigation: explicitly state that all evaluated policies are deterministic and rule-based and that generative-AI assistance belongs only to research/manuscript tooling disclosures.

**Simulation-validity risk.** Both studies are software-in-the-loop. Mitigation: emphasize controlled internal validity, frozen protocols, retained provenance, independent Study-2 reproduction, and bounded claims; reserve orbital/HIL validation for a separate future study.

**Novelty-overstatement risk.** Satellite testbeds, safe mode, rollback, Mission Aware, cyber resilience, and attack/fault ambiguity are established topics. Mitigation: retain the narrower contribution: controlled post-detection response/recovery evidence under contact/evidence/adversary constraints with explicit trusted-recovery semantics and reproducibility governance.

**Archive-identity risk.** Study-1 and Study-2 source evidence are now separately DOI archived. Study-2 Phase-6 source evidence is published as Zenodo v1.0.0, version DOI `10.5281/zenodo.22289114`, concept DOI `10.5281/zenodo.22289113`, and its public ZIP SHA-256 has been verified against the frozen source identity. Mitigation: preserve the distinct Study-1 and Study-2 DOI identities and recheck the exact DOI/checksum references in the final submission export.

## Backup 1: AIAA Journal of Aerospace Information Systems

Use this target if Computers & Security rejects principally for venue/domain fit rather than scientific quality. JAIS is compatible with aerospace computing, embedded-system verification/validation, autonomous systems, resilience, and mission assurance.

Backup positioning should emphasize spacecraft mission assurance, contact-constrained onboard/ground response, cFS/NOS3/Fortytwo integration, response-software architecture, V&V traceability, and trusted recovery. Preserve all cybersecurity limitations and do not convert SIL evidence into flight validation.

## Backup 2: IEEE Transactions on Aerospace and Electronic Systems

TAES remains a higher-bar aerospace-systems alternative if later work adds stronger aerospace-system realism. A future separately frozen validation study could add modeled orbital/access schedules, resource/performance characterization, richer mission phases, and representative RF-free HIL evidence.

Do not inflate the present two SIL studies into flight certification or HIL validation.

## Higher-bar security alternatives: IEEE TDSC / ACM TOPS

Study 2 materially strengthens the security-methodology case relative to the earlier Study-1-only package, especially through bounded producer compromise, evidence-integrity mechanisms, context ablations, and independent reproduction. TDSC/TOPS can therefore be reassessed if Computers & Security rejects for editorial/venue reasons rather than scientific weakness.

That reassessment should use the existing frozen Study-2 evidence. A venue change must not trigger new post-hoc observations, a weighted score, a global policy ranking, or weaker RQ3 interpretation boundaries.

## Decision rule

1. Treat the two-study journal integration and Study-2 DOI/public-byte archive gate as complete.
2. Recheck the live Computers & Security Guide/Aims/portal, run the exact final-export citation/DOI/reference/frozen-claim/scope audits, and submit there first if the deterministic rule-based article remains in scope.
3. If desk-rejected principally for aerospace-domain fit, consider JAIS without changing either frozen study.
4. If a higher-security-methodology venue is preferred after review, reassess TDSC/TOPS using the already frozen Study-2 evidence rather than enlarging the data post hoc.
5. Reserve TAES/expanded JAIS positioning for a separately frozen aerospace-validation/HIL study.

No rejection, reviewer request, or venue change may retroactively alter the frozen 720-observation Study-1 population, the frozen 3,872-observation Study-2 population, or their prespecified statistical identities.
