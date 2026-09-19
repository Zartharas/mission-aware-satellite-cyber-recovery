# Study 8 / Paper 4 Retarget Venue Assessment

**Date:** 2026-09-19  
**Status:** recommendation only, no venue lock  
**Scientific basis:** frozen Study 8 / `S8-PQC-ICR-001`  
**Rejected venue:** Acta Astronautica / `AA-D-26-02872`

## Retargeting principle

The next venue should fit the actual evidence: deterministic systems modeling of post-compromise cryptographic transition under finite intermittent contact. The study is not an RF experiment, cryptographic primitive design, flight test, onboard benchmark, orbital-access study, or empirical spacecraft mission evaluation.

No venue is selected on assumed acceptance probability. The assessment is based on current published scope and the manuscript's actual methodological contribution.

## Candidate 1 - IEEE Systems Journal

### Current scope fit

The IEEE Systems Journal describes itself as a systems-level forum for application-oriented work on complex systems and systems-of-systems. Its current scope explicitly includes modeling, analysis, simulation, mission assurance, robustness, reliability, availability, communications, security, standards, and cyber-physical systems.

That aligns closely with the strongest defensible Study 8 framing:

- finite systems feasibility under interacting contact, deadline, and cryptographic-object constraints;
- explicit separation of recovery feasibility from transition-state availability/security costs;
- deterministic modeling and simulation;
- mission-assurance and resilience implications without claiming flight validation.

### Manuscript implications

A retargeted version should reduce "PQC for satellites" framing and strengthen "systems-level cryptographic transition under constrained connectivity." The paper should present the three cryptographic profiles as controlled system-burden configurations rather than as a cryptographic algorithm comparison.

The current IEEE Systems Journal instructions allow regular papers up to 12 pages during review.

### Main risk

The contribution must be shown as a systems-engineering result, not merely a deterministic simulation where larger byte bundles predictably consume more capacity. The equal-total-capacity temporal-contact control and feasibility-versus-state-cost distinction therefore need to become central.

### Assessment

**Strong methodological fit.**

## Candidate 2 - International Journal of Satellite Communications and Networking

### Current scope fit

The journal states that it covers the theory, practice, and operation of satellite systems and networks, including satellite communications, satellite networks, performance analysis, interoperability, enabling technologies, standards/regulation, and network protocols. It explicitly requires a satellite component.

Recent journal content includes a 2026 paper on lattice-based post-quantum cryptography for satellite communication, demonstrating clear topical adjacency.

### Manuscript implications

A submission here should emphasize:

- satellite-network contact intermittency;
- transition-object burden at the communication/network layer;
- deadline-constrained trusted recovery;
- protocol-state behavior;
- controlled contact-capacity distribution.

The manuscript must differentiate itself sharply from recent satellite-PQC benchmarking and algorithm-comparison work. Its novelty is the post-compromise recovery state machine, finite contact schedule, controlled equal-capacity timing experiment, and security-state/availability tradeoff analysis.

Current author guidance permits free-format initial submission, requires an abstract up to 250 words, up to eight keywords, and a graphical table-of-contents item.

### Main risk

Because the journal already publishes satellite-PQC security work, editors may demand a very clear communication/networking contribution beyond the observation that PQC objects are larger. The synthetic contact model must therefore be presented as a controlled network-recovery experiment, with limitations explicit.

### Assessment

**Strong topical fit, but novelty differentiation must be exceptionally clear.**

## Candidate 3 - IEEE Open Journal of Systems Engineering

The journal focuses on systems-engineering science, methodology, tools, requirements, validation/verification, integration, and lifecycle support for complex systems. It is fully open access.

Study 8 has some alignment through its deterministic systems methodology and validation/reproducibility discipline. However, the paper currently reports an application of a frozen model more than a new general systems-engineering method or tool.

### Assessment

**Plausible but secondary fit unless the manuscript is strengthened around a reusable systems-engineering methodology.**

## Candidate 4 - Journal of Space Safety Engineering

The journal focuses on space safety design, research, development, technology, and practice.

Study 8 can be related to secure recovery and mission assurance, but it does not directly model hazard analysis, safety assurance, fault trees, operational safety, or flight safety.

### Assessment

**Possible but weaker direct fit than IEEE Systems Journal or the satellite communications journal.**

## Candidate not recommended - Computers & Security

The current journal scope explicitly excludes submissions in which cryptology is a principal component. Although Study 8 is a systems-recovery paper rather than a new cryptographic primitive, ML-KEM/ML-DSA object profiles and cryptographic transition are central enough that desk-scope risk is material.

### Assessment

**Do not prioritize for this manuscript.**

## Recommended retarget sequence

1. **IEEE Systems Journal** for the systems-modeling, security, resilience, and mission-assurance framing.
2. **International Journal of Satellite Communications and Networking** if the author prefers a more satellite-network-specific audience and the manuscript is revised to foreground protocol/contact behavior and sharply distinguish prior satellite-PQC work.
3. **IEEE Open Journal of Systems Engineering** as a systems-engineering alternative, particularly if a reusable methodological framing is strengthened.
4. **Journal of Space Safety Engineering** only if the manuscript is reframed around assurance/safety relevance without overstating evidence.

## Current recommendation

Proceed with a new venue-specific revision architecture for **IEEE Systems Journal**, but do not lock the venue or create publisher-facing submission files until the author approves this recommendation after reviewing the forensic audit.

This recommendation is based on scope fit, not an acceptance prediction.
