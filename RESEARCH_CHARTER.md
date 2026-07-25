# Research Charter — Version 0.2

## Working title

**Mission-Aware Cyber Response and Trusted Recovery for Satellite Systems Under Intermittent Ground Contact**

## Refined problem statement

Satellite cybersecurity response cannot be judged solely by attack detection or containment speed. A technically successful response can interrupt critical spacecraft functions, consume constrained resources, miss a contact window, or move the spacecraft into an unsafe or unrecoverable condition.

The study will evaluate cyber-response policies using both cybersecurity and mission-facing outcomes in a controlled digital-twin environment.

## Refined novelty claim

The contribution is not a generic satellite cyber range, an anomaly detector, autonomous FDIR, or a mission-aware analysis framework by itself. Those areas already have substantial prior work.

The intended contribution is:

> A reproducible experimental method that compares cyber-containment and trusted-recovery policies using security, mission-continuity, safety, and recovery-evidence outcomes under mission-state and intermittent-contact constraints.

## Primary research question

How do different cyber-response strategies affect security containment, trusted recovery, and mission continuity under varying spacecraft states and ground-contact conditions?

## Secondary research questions

- RQ1: Which response policies most effectively limit unauthorized command or software activity?
- RQ2: How does mission state alter the safety and operational cost of containment?
- RQ3: How does delayed ground contact affect compromise duration and recovery success?
- RQ4: When does automated containment create greater mission impact than monitored continuation or delayed action?
- RQ5: What evidence is sufficient to declare that the spacecraft has returned to an approved trusted state?

## Theory-derived propositions

- P1: The value and cost of containment are mission-state dependent.
- P2: Contact delay increases the risk of unresolved compromise and inconsistent ground/spacecraft state.
- P3: Restart or nominal telemetry alone is insufficient evidence of trusted recovery.
- P4: Reduced or manipulated telemetry can cause a response policy to select an unsafe or ineffective action.
- P5: A mission-aware policy can improve trade-offs, but it will not dominate simpler policies under every condition.

## Intended artifacts

- Mission/function/structure model
- Threat model and safety invariants
- Small-satellite digital twin
- Controlled event-injection library
- Response-policy implementations
- Trusted-recovery evidence model
- Reproducible experiment runner
- Sanitized generated dataset
- Analysis scripts and release manifest

## Scope boundary

Included:
- Public software
- Researcher-owned computing
- Synthetic commands and identities
- Software-in-the-loop mission simulation
- Publicly licensed telemetry datasets
- Software-emulated contact delay, packet loss, and telemetry degradation

Excluded:
- Operational satellites or ground stations
- Live RF transmission
- Jamming or spoofing
- Stolen or production credentials
- Classified, proprietary, or export-controlled technical data
- Human operator experiments during the first study phase

## Publication posture

The paper must report:
- Failure cases
- Conditions where the mission-aware policy performs worse
- External-validity limits
- License and data provenance
- Exact simulator and dependency versions
- Negative results and excluded-run rules
