# Research Topic Scrutiny Report

## Executive assessment

The topic remains feasible and potentially publishable, but the original framing was too broad. Recent literature already covers:

- Mission-aware cyber-physical security analysis
- Trusted autonomous satellite operations
- Rule-based spacecraft FDIR
- Satellite cybersecurity testbeds
- Satellite telemetry anomaly benchmarks
- Automated self-healing in general cyber-physical systems

The paper therefore should not claim novelty from combining a simulator, anomaly detection, and safe mode. Its strongest defensible gap is the **controlled evaluation of cyber-response choices against mission outcomes and trusted-state recovery under intermittent contact**.

## What is theoretically new enough

The proposed study integrates three previously separated bodies of work:

1. Mission-centric security analysis identifies which functions and assets matter to mission success.
2. Spacecraft FDIR provides fault isolation, safe-mode, and recovery mechanisms.
3. Cyber incident response evaluates containment, eradication, and restoration.

The research question is not whether these concepts exist. It is whether different cyber-response policies produce measurably different security and mission outcomes under spacecraft-specific operating constraints.

## Recommended research design

Use a **theory-informed design-science methodology with a controlled factorial or fractional-factorial simulation evaluation**.

Use the dissertation findings as the prior empirical motivation. Do not call the new paper mixed methods unless the original interview data are formally reanalyzed and integrated into the new experiment under a documented institutional determination.

### Design-science stages

1. Problem identification from practitioner findings and literature
2. Objective definition
3. Artifact design
4. Demonstration in a digital twin
5. Controlled evaluation
6. Communication and reproducibility release

### Experimental logic

Independent variables:
- Cyber-event family
- Mission state
- Response policy
- Ground-contact delay
- Telemetry completeness
- Link impairment

Primary outcomes:
- Residual unauthorized effect
- Mission objective completion
- Safety-invariant violations
- Time to verified trusted recovery
- Legitimate command rejection
- Recovery success

Do not use a single weighted score as the only outcome. Report a multi-objective Pareto analysis and use any composite score only as a sensitivity analysis.

## Recommended minimum viable experiment

To avoid an unmanageable study, begin with:

Cyber events:
- Unauthorized or replayed command
- Tampered or unauthorized update
- Telemetry suppression during response

Mission states:
- Nominal operations
- Payload operation
- Low-power or eclipse
- Software-update/recovery state

Response policies:
- Observe only
- Identity/source isolation
- Selective command restriction
- Safe mode
- Rollback
- Mission-aware selection

Contact conditions:
- Immediate ground contact
- One missed pass
- Two missed passes

The pilot should determine which factors materially change outcomes before the final design is frozen.

## Novelty threats

### Mission Aware overlap

Published Mission Aware research already links cybersecurity to mission requirements and system structure. Our work must use that as a theoretical basis, not present mission-centric security as a new concept.

### FDIR overlap

Rule-based satellite FDIR and autonomous fault recovery already exist. Our contribution must distinguish cyber-originated response selection, adversarial evidence manipulation, and containment-versus-mission trade-offs from ordinary fault recovery.

### Testbed overlap

NOS3-based and physical CubeSat cyber testbeds already exist. The digital twin is infrastructure, not the principal contribution.

### Dataset overlap

Public telemetry and cyberattack datasets already support anomaly detection. Our paper should generate response and recovery outcome data that those datasets do not contain.

## Strongest publication claim

> The study provides a controlled, reproducible benchmark for comparing cyber-response and trusted-recovery policies across mission states and ground-contact delays, reporting both adversary containment and mission-preservation outcomes.

## Go/no-go recommendation

Proceed, subject to four gates:

1. The literature matrix confirms no directly equivalent satellite experiment.
2. The mission model contains defensible safety invariants and measurable objectives.
3. The simulator can reproduce nominal operations and trusted rollback consistently.
4. The study remains software-only until legal, licensing, and institutional reviews justify any expansion.
