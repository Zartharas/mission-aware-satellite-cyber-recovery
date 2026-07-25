# WP1 Literature and Novelty Validation — Review 1

Date: 2026-07-24

## Review question

Does published research already provide a controlled satellite experiment that compares cyber-response policies using security containment, mission continuity, safety constraints, intermittent ground contact, and evidence-based trusted recovery as concurrent outcomes?

## Current conclusion

No directly equivalent study was identified in the first focused review. The topic remains defensible, but the novelty is narrower than the original concept.

The paper must not claim novelty for any of the following individually:

- Mission-aware cybersecurity analysis
- Spacecraft autonomy
- Failure detection, isolation, and recovery
- Cyber-safe mode
- Satellite cybersecurity testbeds
- NOS3/cFS event generation
- Telemetry anomaly detection
- General cyber-resilience engineering

The strongest remaining contribution is:

> A reproducible controlled experiment that compares cyber-containment and trusted-recovery policies using both adversary-control and mission-preservation outcomes under mission-state, telemetry-quality, and intermittent-contact constraints.

## Evidence clusters

### 1. Mission-centric cybersecurity already exists

Mission Aware research connects mission requirements, system functions, architecture, and cyberattack evidence. It supplies the systems-theoretic foundation for defining mission impact but does not eliminate the need for controlled policy-comparison experiments.

Implication: cite Mission Aware as prior theory. Do not claim that linking cyber events to mission functions is new.

### 2. Trusted autonomy and spacecraft FDIR already exist

Recent research demonstrates rule-based FDIR and reviews trusted autonomous satellite operations. Telemetry-loss recovery studies also distinguish onboard autonomous recovery from ground-command recovery.

Implication: ordinary fault isolation, safe mode, and recovery logic are baselines. The proposed work must distinguish adversarial evidence, malicious command activity, and cyber-originated containment trade-offs from non-adversarial fault management.

### 3. Cyber-safe mode is already prescribed

SPARTA defines a cyber-safe mode based on a known, integrity-protected software and configuration state and expects restoration of functionality after attack. SPARTA also identifies attacks that can exploit or induce safe mode, including relaxed controls and reduced telemetry.

Implication: entering cyber-safe mode is not itself a novel contribution. The experiment should test when safe mode is beneficial, when it creates mission loss, and when the recovery posture can be abused.

### 4. Satellite cyber testbeds and datasets already exist

AegisSat, NOS3/cFS studies, CuCD-ID, HADES, and testbed-fidelity research provide digital-twin or physical/emulated environments for attack generation and telemetry capture.

Implication: the simulator is research infrastructure. Novelty must come from the response-policy experiment, mission metrics, trusted-recovery criteria, and generated outcome dataset.

### 5. Detection datasets do not answer the recovery question

CuCD-ID, ESA telemetry, and OPSSAT-AD support anomaly detection and robustness work. They do not provide ground truth for comparative containment decisions, mission objective completion, safety-invariant violations, or verified trusted recovery.

Implication: public data may calibrate telemetry behavior and validate the pipeline, but the primary causal dataset must be generated in the controlled experiment.

### 6. Cyber-resilience engineering supports the study design

NIST SP 800-160 Volume 2 defines cyber-resilient systems as systems able to anticipate, withstand, recover from, and adapt to cyber adversity while reducing mission risk.

Implication: use cyber-resilience objectives to define recovery and adaptation, but operationalize them with satellite-specific measurable endpoints.

## Refined gap statement

Published work provides theories, standards, safe-mode requirements, FDIR mechanisms, testbeds, and detection datasets. The unresolved empirical question is how alternative cyber-response policies perform when:

1. The same cyber event occurs in different spacecraft mission states.
2. Ground contact is immediate, delayed, or unavailable.
3. Telemetry is complete, missing, delayed, or manipulated.
4. Containment protects one asset while threatening another mission objective.
5. Recovery must be supported by current integrity, authorization, configuration, and health evidence.

## Publication-strength requirements

The paper will need all of the following:

- At least four credible response baselines
- Explicit mission objectives and safety invariants
- Multiple contact-delay conditions
- Adversarial telemetry conditions
- Trusted-recovery acceptance criteria
- Repeated randomized trials
- Negative cases where the proposed policy loses
- Multi-objective analysis rather than a single arbitrary score
- Version-pinned reproducible artifacts
- A bounded external-validity statement

## Proposed contribution hierarchy

### Primary contribution

A satellite-specific benchmark and experiment for comparing cyber-response and recovery policies.

### Secondary contribution

A trusted-recovery evidence model covering approved software/configuration, integrity, authorization, telemetry restoration, state agreement, and health checks.

### Supporting contribution

A reusable, sanitized response-and-recovery outcome dataset generated from NOS3/cFS or an equivalent software-in-the-loop environment.

## Revised hypotheses for later preregistration

- H1: Response-policy effects differ materially by mission state.
- H2: More restrictive containment reduces unauthorized effect but increases legitimate mission interruption.
- H3: Contact delay increases compromise duration and decreases recovery success for ground-dependent policies.
- H4: Evidence-based rollback reduces time to verified trusted recovery compared with restart-only recovery.
- H5: Mission-aware policy selection improves the security–mission Pareto frontier but does not dominate every baseline in every condition.
- H6: Reduced or manipulated telemetry increases unsafe or ineffective response selection.

## Legal and data-source finding

The first phase remains low risk when limited to public software, synthetic events, isolated networking, and properly licensed public datasets. Raw third-party data should remain outside Git.

A licensing discrepancy was identified for CuCD-ID: the repository register currently states CC BY 4.0, while the published 2026 Data in Brief article reports CC BY-NC-ND 4.0. The dataset must remain conditionally held until the exact Mendeley record terms for the selected version are captured and reconciled.

## WP1 status

WP1 remains **In progress**. The initial gap is defensible, but the acceptance gate should not be marked complete until:

- The matrix contains at least 30 directly relevant sources.
- Searches cover security, spacecraft FDIR, mission assurance, autonomy, cyber-physical response, and recovery verification.
- At least one independent red-team review challenges the gap statement.
- The final gap statement is tied to a frozen minimum viable experiment.
