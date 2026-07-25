# Theoretical and Conceptual Framework

## Primary theoretical lens: Mission Aware cybersecurity

Mission Aware cybersecurity provides the main systems-theoretic lens. It connects:

- Mission requirements
- Admissible system functions
- System structure and dependencies
- Attack paths
- Mission impact

The study will use this lens to define what must be protected and what constitutes mission degradation.

## Operational recovery lens: FDIR and resilience engineering

Failure Detection, Isolation, and Recovery provides the operational vocabulary for:

- Detecting abnormal state
- Isolating affected functions
- Entering degraded or safe modes
- Restoring service
- Verifying recovery

FDIR is not treated as inherently cyber secure. Cyber events may manipulate telemetry, commands, or recovery logic, so the experiment must test whether ordinary FDIR assumptions remain valid under adversarial conditions.

## Governance and evidence lens: NIST CSF/RMF

NIST CSF and RMF will be used as governance and evidence-mapping structures rather than causal theories.

Relevant functions:
- Detect
- Respond
- Recover
- Govern

Relevant evidence:
- Detection records
- Authorization decisions
- Integrity checks
- Attestation evidence
- Recovery validation
- Continuous-monitoring records

## Threat taxonomy: SPARTA

SPARTA will be used to classify synthetic event families and countermeasures. It is a threat taxonomy, not a theoretical framework.

## Integrated conceptual model

```text
Practitioner-derived concern
        ↓
Mission requirement and unacceptable loss
        ↓
Critical function and trust boundary
        ↓
SPARTA-mapped cyber event
        ↓
Observed system and telemetry state
        ↓
Response-policy decision
        ↓
Containment and mission effect
        ↓
Recovery action
        ↓
Trusted-state evidence
```

## Construct definitions

### Mission continuity

The ability to preserve prioritized mission objectives within stated safety and resource constraints.

### Cyber containment

The reduction or termination of unauthorized capability or effect.

### Trusted recovery

Restoration to a state supported by current, verifiable evidence of approved software, configuration, authorization, and health.

### Mission-aware response

A response selected using cyber evidence, mission state, safety constraints, resource state, and contact availability.

### Recovery confidence

The strength and freshness of evidence supporting a conclusion that the system has returned to an approved state.

## Avoiding framework overload

The paper should not carry forward TAM and TPB unless human adoption or operator behavior becomes an explicit empirical component. They are not necessary for the first software-only experiment.
