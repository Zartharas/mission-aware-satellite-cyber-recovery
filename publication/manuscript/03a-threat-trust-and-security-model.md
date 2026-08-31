# 3A. Cybersecurity Threat, Trust, and Security-Property Model

## 3A.1 Threat-model scope

The experiment uses a **post-access adversary model**. It does not attempt to model reconnaissance, exploit development, credential theft, RF interception, or the process by which an attacker initially reaches the command, update, or telemetry path. Instead, each event family begins from a frozen cyber-relevant state whose effect on response/recovery behavior can be measured reproducibly.

The modeled adversary’s objective is to create or sustain a condition that challenges spacecraft command integrity, software/update trust, defender evidence, or operational availability long enough to force a response/recovery decision. Depending on the frozen event family, the adversary may be represented as able to:

- submit an unauthorized but syntactically valid laboratory command through the simulated command path (E1);
- cause a previously authorized laboratory command to be replayed (E2);
- place the simulated spacecraft in a compromised software/update context (E3);
- degrade or suppress portions of the policy-visible telemetry/evidence used for response selection and recovery assessment (E4).

These are **capability abstractions**, not claims that a real adversary has compromised a specific satellite, ground station, RF link, cryptographic key, software supplier, or operator account. SPARTA mappings are used only to establish behavioral correspondence with recognized spacecraft cyber techniques; the experiment does not claim to execute complete SPARTA attack chains [@sparta_techniques].

## 3A.2 Adversary exclusions and immutable research boundary

The simulated adversary cannot modify the frozen experiment plan, campaign seed, event/cell identity, response-policy implementation, trial-validity rules, analysis-membership rules, authoritative attempt-history ledger, or immutable experiment ground truth. These controls belong to the researcher-controlled experiment plane and are outside the adversary boundary.

The adversary also cannot access post-run analysis labels as a runtime oracle. In particular, the policy selector does not read the immutable experiment ground truth or the final trusted-recovery adjudication. This separation is essential to the P3/P4 interpretation: a policy can act on incomplete or degraded evidence even while the experiment controller retains the true underlying state for later analysis.

The experiment does not evaluate confidentiality loss, data exfiltration, cryptanalytic strength, key extraction, RF jamming/spoofing resistance, physical counterspace attack, insider behavior, or human social engineering. Those threats remain outside the inferential scope even when they are relevant to operational space cybersecurity.

## 3A.3 Defender-knowledge model

The defender is represented through two distinct knowledge domains:

1. **Runtime policy-visible state.** The response policy can use only the event, mission, evidence, contact, authorization, and other context explicitly exposed by the frozen policy interface. Under Study 1, this evidence is either the frozen full-evidence condition or the specifically reduced/suppressed policy-visible evidence defined by the applicable treatment; an `evidence_insufficient` state may result from those implemented conditions. Study 1 did not separately manipulate evidence age/staleness, contradiction, or forged values as independent factors.
2. **Experiment/analysis ground truth.** The controller retains immutable treatment identity, expected treatment/fidelity conditions, run provenance, and outcome evidence required to determine whether the trial is valid and to classify the resulting terminal state. This information is not exposed to the runtime selector as a correctness oracle.

This architecture creates the core information-security problem studied by P3/P4: **response decisions are made under bounded observation, while trustworthy recovery is adjudicated only when sufficient current evidence exists.**

## 3A.4 Trust boundaries

The controlled testbed can be interpreted through the following trust boundaries.

### TB0 — research control plane

Contains the frozen campaign plan, run/cell identity, campaign seed, immutable ground truth, ledger rules, analysis-membership controls, and integrity-freeze material. TB0 is trusted for experimental validity and is not part of the simulated operational response system.

### TB1 — ground authorization and command origin

Represents the synthetic ground-side command/authorization state visible to the experiment. P6 depends on this boundary because recovery action is gated by modeled ground authorization. The C1 treatment delays availability of that authorization but does not model real operators, antenna scheduling, or ground-network performance.

### TB2 — spacecraft command and execution path

Represents command ingest and execution within the cFS/NOS3/Fortytwo-based software environment. E1/E2 challenge the integrity and freshness assumptions of this path. The experiment measures resulting unauthorized-effect completion and containment/recovery behavior rather than cryptographic protocol strength.

### TB3 — policy-visible evidence/telemetry plane

Provides the selector with the evidence and state information allowed by the frozen policy interface. E4 and T1 treatments can reduce the evidence available across this boundary. This boundary is intentionally treated as attackable/degradable because response systems should not assume that all telemetry used for autonomous security decisions remains complete and current during a compromise.

### TB4 — response/recovery mechanism

Contains fixed response mechanisms, ground-authorized behavior, rollback behavior, the modeled safe-mode action, and the mission-aware selector. P7 may select among effective mechanisms based only on policy-visible context.

### TB5 — recovery evidence adjudication

Contains the post-action evidence needed to classify trusted recovery, including approved software/configuration identity, integrity/authorization evidence, current measured-state/attestation evidence, restored command authority, telemetry restoration, ground/spacecraft state agreement, health checks, and absence of modeled residual unauthorized state. TB5 is an **analysis and assurance boundary**, not a source of privileged runtime guidance to P7.

## 3A.5 Security properties and measurable proxies

The experiment evaluates multiple security/dependability properties rather than a single security score. Table R6 provides the full mapping.

### Integrity

Integrity is represented through whether an unauthorized effect completes (M01), whether restored software/configuration and authorization evidence satisfy the trusted-recovery checklist, and whether the modeled ground/spacecraft states converge after response (M07). The study does not claim cryptographic-integrity assurance beyond the synthetic checks implemented in the testbed.

### Availability and mission continuity

Availability is represented through mission-objective completion (M02), legitimate-command rejection (M06), containment/recovery delay (M04/M05), and state-divergence duration (M07). A response can therefore be secure in the narrow containment sense while still imposing an availability or mission cost.

### Safety

Safety is represented by the count of frozen invariant violations (M03). M03 was structurally zero in the final 720-run extraction. This is retained as an observed result and does not establish universal safety.

### Recoverability and cyber resilience

Recoverability is represented by verified-recovery time (M05), terminal recovery states, restored authorized command path, and the requirement that trusted recovery be supported by current evidence. Operational behavior without sufficient evidence does not automatically satisfy the trusted-recovery definition.

### Evidence assurance

Evidence assurance is represented by the controlled evidence condition and M08 evidence-completeness ratio together with the specific currentness/integrity/authorization checks required for trusted recovery. P3/P4 test the consequence of treating this evidence plane as fallible rather than implicitly trustworthy.

## 3A.6 Incident-response mapping

NIST SP 800-61 Rev. 3 frames incident response as part of cybersecurity risk management and seeks to improve the efficiency and effectiveness of incident detection, response, and recovery [@nist80061r3]. The present experiment isolates only the **response/recovery** segment of that larger lifecycle.

The mapping is:

`event established → response selection → containment → recovery/reconstitution → evidence-qualified recovery validation → mission/security consequence measurement`.

The study does not measure detector precision/recall, incident triage, escalation staffing, forensic attribution, legal reporting, or human lessons-learned processes. Therefore, the mapping is explanatory rather than a claim of organizational NIST compliance.

## 3A.7 Security-model implications for interpretation

Three interpretation rules follow from this model.

First, **ground truth is not policy-visible truth**. P4 selection outcomes must be interpreted from the actual information available to the selector, not judged using information withheld from it at runtime.

Second, **containment is not equivalent to trusted recovery**. A response can stop or restrict an unauthorized effect without establishing that software, authorization state, telemetry, health, and command authority have returned to a trustworthy condition.

Third, **fail-closed behavior has measurable system cost**. A conservative response may improve one security dimension while degrading mission completion or legitimate-command availability. That trade-off is why the primary study retains separate outcomes and uses condition-specific Pareto reasoning rather than a post-hoc weighted security score.
