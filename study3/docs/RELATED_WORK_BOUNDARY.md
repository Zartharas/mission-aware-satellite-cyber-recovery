# Study-3 Related-Work Boundary

**Checked:** 2026-09-02  
**Purpose:** establish a conservative publication-era boundary before any Study-3 campaign result is frozen.

## Directly relevant adjacent work

### Intermittent connectivity and fresh assurance evidence

Berto et al., *Non-functional certification of edge-computing satellite systems*, Computer Networks 278 (2026), article 112036, DOI `10.1016/j.comnet.2026.112036`, explicitly models satellite assurance under intermittent/disrupted links. During unavailable contact the framework substitutes predicted evidence for directly collected evidence and associates uncertainty/confidence with that substitution. This is strong evidence that intermittent connectivity can create a **fresh-evidence assurance problem** in satellite systems.

Study 3 is not a replication of that work. It evaluates adversarial authorization evidence and deterministic cyber-response/recovery policy semantics rather than QoS/non-functional certification or prediction-driven evidence substitution.

### Continuous trust/attestation

MITRE's 2026 *Framework for Continuous Remote Attestation* argues that boot-time trust is insufficient for systems whose trusted state can change at runtime and motivates continuously verifiable trust. That work is not satellite-specific and does not evaluate the K4/V4/V5 response model, but it supports the broader assurance premise that trust evidence has a temporal lifecycle rather than a one-time state.

### Space cybersecurity taxonomy

SPARTA v4.0.1 includes `IMP-0010 Data Manipulation` and telemetry disruption/deception concepts under `DE-0002`/`DE-0003`. These provide current behavioral/taxonomy adjacency for falsified or manipulated policy-visible information. They do not define the Study-3 estimands, contact schedule, producer-compromise budget, or recovery-policy comparison.

### Current engineering standardization

IEEE 3536-2026, *IEEE Standard for Space System Cybersecurity Design*, was published in July 2026 and defines a component-level cybersecurity design process for space systems. Study 3 does not claim conformance or certification under IEEE 3536; the standard is contextual evidence that space-system cybersecurity design and resilience are current engineering concerns.

## Narrow novelty boundary

The literature review supports the following conservative positioning only:

> Study 3 evaluates the **temporal interaction** between a frozen intermittent-contact schedule, evidence freshness/cache semantics, detectable post-signature manipulation, compromised-producer signed false evidence, and three deterministic response-policy semantics using an exhaustive attack-onset phase grid.

No first-ever claim is made. The current search did not identify a directly equivalent controlled experiment with the same combined factors and false-qualification-origin decomposition, but absence from this targeted search is not proof that no such work exists.

## Explicit non-claims

- not an orbital-access measurement;
- not operational remote attestation;
- not a cryptographic primitive evaluation;
- not an IEEE 3536 compliance assessment;
- not a SPARTA conformance test;
- not evidence about real producer-compromise frequency;
- not operational spacecraft/RF validation.
