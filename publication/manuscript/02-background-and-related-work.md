# 2. Background and Related Work

## 2.1 Mission-centric cybersecurity and cyber resilience

Mission Aware cybersecurity provides the primary systems-theoretic lens for this study. Rather than treating cybersecurity as a collection of isolated component protections, Mission Aware analysis traces mission requirements and unacceptable losses through system functions, architecture, dependencies, and attack consequences. Recent Mission Aware work formalizes this mission-centric cyber-physical perspective and reinforces that the framework is prior theory rather than a new contribution of the present experiment [Bakirtzis et al., 2026].

Cyber-resilience engineering provides a complementary systems-security perspective. NIST SP 800-160 Vol. 2 Rev. 1 frames cyber resilience around the ability to anticipate, withstand, recover from, and adapt to adverse conditions, attacks, or compromises while reducing mission or business risk [NIST, 2021]. In this study, that framing motivates separate containment, mission-continuity, recovery, and evidence outcomes. NIST guidance is used as an engineering/evidence structure, not as a causal theory for the observed experimental effects.

The present results also impose an important limit on the theoretical framing. Although mission state was included because Mission Aware and spacecraft fault-management reasoning make state-dependent consequences plausible, the predeclared P1 primary outcomes did not demonstrate a mission-state interaction. Accordingly, Mission Aware is retained as the design and interpretation lens rather than described as a theory empirically confirmed by the P1 result.

## 2.2 Spacecraft FDIR, autonomy, and contact constraints

Spacecraft FDIR and autonomy are mature engineering areas. Rule-based satellite FDIR implementations, trusted-autonomy reviews, and long-duration mission designs demonstrate that spacecraft may need to isolate faults, preserve essential functions, enter restricted operating states, and recover without immediate ground intervention [Thangavel et al., 2024; Wanninger, 2025/2026]. Communication delay and periods without contact are therefore established spacecraft-engineering concerns, not a novelty claim of this paper. The JUICE system design, for example, reflects substantial onboard autonomy and fault-management requirements for an interplanetary mission with long communication delays [Sarri et al., 2026].

Current operational guidance similarly recognizes that satellite incident-response actions may depend on contact windows and approval gates. A 2026 AWS satellite incident-response playbook explicitly discusses containment waiting for orbital passes, trade-offs between mission continuity and security, remotely inaccessible endpoints, automated runbooks, and human approval for high-impact actions [Chunawala, 2026]. These sources establish the practical relevance of the problem. The contribution here is the controlled cyber-response experiment, not the observation that contact constraints exist.

The study therefore models contact as a controlled experimental factor rather than as RF physics. C1 represents one synthetic/modelled missed-contact window. It does not reproduce orbital geometry, ground-station scheduling, antenna availability, operator latency, or link performance.

## 2.3 Cyber-safe response and trusted recovery

SPARTA and related space-security guidance include cyber-safe mode, recovery/reconstitution to known state, integrity-protected recovery images, and safeguards intended to preserve control after cyber compromise. These concepts make clear that safe mode and trusted-image rollback are not individually novel. They also motivate a stricter recovery question: when is a recovered system sufficiently evidenced to be called trusted?

The experiment operationalizes trusted recovery using a frozen checklist covering approved software/configuration, integrity, authorization, current measured-state evidence, restored command authority, ground/spacecraft state agreement, telemetry restoration, health checks, absence of modeled residual unauthorized state, and a complete recovery record. A run can therefore be operational without being classified as trusted recovery.

This distinction is adjacent to broader cyber-physical attack-recovery research, which already studies dedicated recovery controllers, self-healing systems, predictive recovery, and restoration of physical state after attack. The satellite-specific evaluation problem addressed here combines adversarial evidence/authorization conditions, intermittent modeled contact, mission outcomes, and evidence-qualified recovery in one controlled comparison rather than proposing a new generic recovery-controller architecture.

## 2.4 Satellite cyber testbeds, datasets, and detector-focused work

Satellite cybersecurity testbeds and datasets have expanded rapidly. NOS3/cFS research provides software-based spacecraft development and simulation infrastructure; AegisSat and HADES illustrate broader space-cyber testbed approaches; CuCD-ID provides a NOS3/cFS-based cybersecurity dataset; and ESA/OPS-SAT telemetry benchmarks support anomaly-detection research. These artifacts demonstrate that constructing a satellite cyber range, generating attacks, or collecting telemetry is not sufficient novelty by itself.

Recent onboard cybersecurity work also focuses on detector performance. TinyML-driven autonomous-spacecraft research evaluates latency/accuracy trade-offs for lightweight onboard cyber/RF threat detection [Le, Tran, and Le, 2026]. Broader reviews identify onboard intrusion detection, recovery, trusted supply chains, and real-time impact assessment as continuing research gaps [Mattar et al., 2025]. The present study addresses a downstream question: given a modeled cyber event, what mission, containment, command-availability, and trusted-recovery consequences follow from alternative response policies?

## 2.5 Mission and temporal context as active prior art

The idea that cyber risk can vary with mission or time is also active prior art. Recent temporal-risk research explicitly models how the same satellite vulnerability may have different consequences across operationally meaningful mission windows [Liu and Sun, 2026]. The present study therefore does not claim that time- or mission-sensitive cybersecurity is new.

This adjacency makes the P1 null result especially relevant. Mission context can be theoretically important without producing a measurable policy interaction on every endpoint in every implementation. The controlled experiment varied mission state, but the predeclared P1 endpoints were unchanged across the tested state contrast. The paper consequently avoids using mission-state variation itself as a positive novelty result.

## 2.6 Remaining empirical gap and study position

The literature reviewed for this project did not identify, in the targeted publication-era refresh, a directly equivalent controlled small-satellite experiment that jointly:

1. compares multiple cyber-response/recovery policies rather than one detector or mechanism;
2. varies spacecraft mission context and modeled contact availability;
3. degrades the evidence visible to the response policy;
4. reports security containment, mission completion, command rejection, safety-invariant outcomes, and evidence-qualified recovery separately;
5. uses condition-specific Pareto comparison rather than a primary weighted score; and
6. retains conditions in which the adaptive policy is equivalent or worse than simpler alternatives.

This is a narrow gap statement, not a first-ever or exhaustive-literature claim. The contribution is the joint comparative experimental method and the resulting conditional outcome record. Mission Aware analysis, spacecraft autonomy, FDIR, safe mode, trusted recovery concepts, satellite testbeds, anomaly detection, and cyber-resilience engineering remain prior art and foundations for the study.