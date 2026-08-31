# Venue Fit and Backup Strategy

## Primary: Computers & Security (Elsevier)

### Why the paper fits

Computers & Security describes its audience as the information-security community and emphasizes a combination of leading-edge research and practical advice. The manuscript's core contribution is a controlled post-detection security response/recovery comparison rather than cryptology, intrusion-detection model development, or general aerospace performance analysis. That places the current Study 1 near the journal's applied-security center of gravity.

The topic also has direct venue precedent. Recent Computers & Security papers include:

- **Assessing the attack surface of space organizations: A data-driven analysis**, Vol. 164 (2026), 104848, DOI 10.1016/j.cose.2026.104848 — direct space-sector cybersecurity and measurable risk/exposure precedent.
- **Securing SatCom user segment: A study on cybersecurity challenges in view of IRIS2**, Vol. 140 (2024), 103799, DOI 10.1016/j.cose.2024.103799 — direct satellite-communications cybersecurity precedent.
- **CANSat-IDS: An adaptive distributed Intrusion Detection System for satellites, based on combined classification of CAN traffic**, Vol. 146 (2024), 104033, DOI 10.1016/j.cose.2024.104033 — direct satellite cybersecurity/experimental precedent, but centered on IDS classification rather than post-event response/recovery.
- **SCASS: Breaking into SCADA Systems Security**, Vol. 151 (2025), 104315, DOI 10.1016/j.cose.2025.104315 — open/modular cyber-physical security-testbed precedent.
- **Intrusion response systems for cyber-physical systems: A comprehensive survey**, Vol. 124 (2023), 102984, DOI 10.1016/j.cose.2022.102984 — intrusion-response and resilient-CPS adjacency.

The manuscript is differentiated from those works by the joint comparison of response/recovery policies under common satellite conditions; explicit modeled contact and policy-visible evidence factors; separate security, mission, command-availability, safety, and trusted-recovery outcomes; condition-specific Pareto analysis; and an integrity-frozen reproducibility record.

### Current scope constraints that matter

The current journal scope explicitly excludes cryptology as a principal component. This manuscript does not make cryptographic algorithm/protocol design a principal contribution.

The journal also currently states a moratorium on submissions in which AI/ML is a significant scientific component. That point required special scrutiny because the manuscript uses terms such as “adaptive” and “mission-aware.” The implemented Study 1 P7 mechanism is a **frozen deterministic rule-based selector**, not a learned model or AI/ML method. Its decision table is versioned configuration, its inputs are bounded policy-visible event/mission/evidence/contact state, and the implementation records that immutable experiment ground truth is not read as a runtime oracle. AI-assisted manuscript preparation and post-publication reproducibility-code reconstruction are disclosed separately under Elsevier publication policy and are not the experimental security mechanism.

The deterministic-method distinction should remain explicit in the title/abstract/Methods/cover letter so a desk editor does not incorrectly classify the scientific contribution under the AI/ML moratorium.

### Desk-review positioning

Lead with the **cybersecurity response/recovery decision problem**, not satellite engineering alone:

- detection/event establishment is a precondition;
- the evaluated problem begins at response selection;
- authorization and modeled contact can delay containment/recovery;
- policy-visible evidence can alter deterministic response selection;
- containment and trusted recovery are not equivalent;
- conservative security behavior can impose mission/command-availability cost;
- negative/equivalent P7 outcomes are retained.

The satellite setting is substantively important because intermittent contact, command authority, evidence availability, mission continuity, and recovery interact in ways that make post-event security decisions nontrivial. The contribution nevertheless remains legible to broader cyber-resilience and CPS-security readers through the NIST response/recovery mapping and explicit trust model.

Avoid positioning the paper as:

- a new Mission Aware theory;
- a new satellite IDS;
- a satellite threat taxonomy;
- an AI/ML autonomy paper;
- a cryptographic-protocol paper;
- a flight-autonomy certification study;
- a real-RF or operational-spacecraft experiment;
- a universal-autonomy superiority result.

### Primary submission risks and mitigations

**Domain-specificity risk.** A desk editor could view the manuscript as aerospace systems engineering rather than information security. Mitigation: foreground the transferable post-detection cyber-response/recovery problem, trust/evidence boundaries, incident-response positioning, and practical security dependencies.

**AI/ML scope-confusion risk.** “Adaptive” or “mission-aware” could be misread as learned autonomy. Mitigation: state repeatedly and accurately that P7 is frozen deterministic rule logic and that no AI/ML model generates Study 1 responses.

**Simulation-validity risk.** The work is SIL rather than operational or HIL. Mitigation: emphasize controlled internal validity, public frozen evidence/reproducibility, and bounded claims; reserve orbital/HIL validation for a separate Study 3.

**Novelty-overstatement risk.** Satellite testbeds, detection, safe mode, rollback, Mission Aware, and cyber resilience are established prior art. Mitigation: retain the narrow novelty claim of a joint controlled response/recovery comparison under contact/evidence constraints with evidence-qualified recovery and condition-specific multi-objective outcomes.

## Backup 1: AIAA Journal of Aerospace Information Systems

Use this target if Computers & Security rejects primarily for venue/domain fit rather than scientific quality. JAIS covers aerospace computing and information systems, software engineering, embedded-system verification/validation, autonomous systems, systems health management, resilience, safety, and mission assurance. The Study 1 architecture and a future HIL extension have strong compatibility with that scope.

Backup-positioning change: emphasize aerospace mission assurance, contact-constrained onboard/ground response, cFS/NOS3/Fortytwo integration, response-software architecture, V&V traceability, and trusted spacecraft recovery. Preserve all cybersecurity limitations and do not convert SIL evidence into flight validation.

## Backup 2: IEEE Transactions on Aerospace and Electronic Systems

Use as the higher-bar aerospace-systems alternative if the work is expanded with stronger aerospace-system realism. TAES covers complex aerospace/electronic systems including spacecraft, telemetry, command/control, automated testing, and fault-tolerant systems, including recovery and fault-containment topics.

Backup-positioning change: strengthen systems methodology, modeled orbital/access conditions, resource/performance characterization, mission-phase variation, and representative RF-free HIL validation. Do not inflate the present SIL evidence into flight certification.

## Separate higher-bar security track: IEEE TDSC / ACM TOPS

These should not be treated as simple formatting backups for the same Study 1 manuscript. Their strongest fit emerges from the separately designed Study 2, which adds multiple evidence-failure mechanisms, multiple contact regimes, fault/attack ambiguity, selector ablation, stronger baselines, and formal assurance. Keeping that evidence in a new frozen study creates a genuine methodology/generalization contribution rather than post-hoc enlargement of the current dataset.

## Decision rule

1. Complete the current C&S-specific author attestations and submission-day policy checks, then submit Study 1 to Computers & Security first.
2. If desk-rejected principally for aerospace-domain fit, retarget Study 1 to JAIS without changing the frozen scientific results.
3. If additional aerospace engineering validation is completed under a new frozen study, evaluate TAES versus JAIS based on the resulting systems-methodology depth.
4. Pursue TDSC/TOPS with Study 2 rather than retrofitting new observations into Study 1.

No rejection or venue change may trigger post-hoc changes to the frozen 720-observation population or reinterpretation of P1/P3/P4/P5 beyond the evidence-locked controls.
