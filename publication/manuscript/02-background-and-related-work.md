# 2. Background and Related Work

## 2.1 Mission-centric cybersecurity and cyber resilience

Mission Aware cybersecurity provides the primary systems-theoretic lens for this study. Rather than treating cybersecurity as a collection of isolated component protections, Mission Aware analysis traces mission requirements and unacceptable losses through system functions, architecture, dependencies, and attack consequences. Recent Mission Aware work formalizes this mission-centric cyber-physical perspective and reinforces that the framework is prior theory rather than a new contribution of the present experiment [@bakirtzis2026missionaware].

Cyber-resilience engineering provides a complementary systems-security perspective. NIST SP 800-160 Vol. 2 Rev. 1 frames cyber resilience around the ability to anticipate, withstand, recover from, and adapt to adverse conditions, attacks, or compromises while reducing mission or business risk [@nist800160v2r1]. NIST SP 800-61 Rev. 3 similarly places incident response inside broader cybersecurity risk management and emphasizes improving detection, response, and recovery effectiveness [@nist80061r3]. In this study, those frameworks motivate separate containment, mission-continuity, recovery, and evidence outcomes. They are used as engineering and lifecycle structures rather than as causal theories for the observed experimental effects or as claims of NIST compliance.

The present results also impose an important limit on the theoretical framing. Although mission state was included because Mission Aware and spacecraft fault-management reasoning make state-dependent consequences plausible, the predeclared P1 primary outcomes did not demonstrate a mission-state interaction. Accordingly, Mission Aware is retained as the design and interpretation lens rather than described as a theory empirically confirmed by the P1 result.

## 2.2 Spacecraft FDIR, autonomy, and contact constraints

Spacecraft FDIR and autonomy are mature engineering areas. Rule-based satellite FDIR implementations, trusted-autonomy reviews, and long-duration mission designs demonstrate that spacecraft may need to isolate faults, preserve essential functions, enter restricted operating states, and recover without immediate ground intervention [@thangavel2024trusted; @wanninger2025fdir; @sarri2026juice]. Communication delay and periods without contact are therefore established spacecraft-engineering concerns, not a novelty claim of this paper. The JUICE system design, for example, reflects substantial onboard autonomy and fault-management requirements for an interplanetary mission with long communication delays [@sarri2026juice].

Current operational guidance similarly recognizes that satellite incident-response actions may depend on contact windows and approval gates. A 2026 AWS satellite incident-response playbook discusses containment waiting for orbital passes, trade-offs between mission continuity and security, remotely inaccessible endpoints, automated runbooks, and human approval for high-impact actions [@chunawala2026satelliteir]. These sources establish the practical relevance of the problem. The contribution here is the controlled cyber-response experiment, not the observation that contact constraints exist.

The study therefore models contact as a controlled experimental factor rather than as RF physics. C1 represents one synthetic/modelled missed-contact window. It does not reproduce orbital geometry, ground-station scheduling, antenna availability, operator latency, or link performance.

## 2.3 Cyber-safe response and trusted recovery

SPARTA and related space-security guidance include cyber-safe mode, recovery/reconstitution to known state, integrity-protected recovery images, and safeguards intended to preserve control after cyber compromise [@sparta_cybersafe]. These concepts make clear that safe mode and trusted-image rollback are not individually novel. They also motivate a stricter recovery question: when is a recovered system sufficiently evidenced to be called trusted?

The experiment operationalizes trusted recovery using a frozen checklist covering approved software/configuration, integrity, authorization, current measured-state evidence, restored command authority, ground/spacecraft state agreement, telemetry restoration, health checks, absence of modeled residual unauthorized state, and a complete recovery record. A run can therefore be operational without being classified as trusted recovery.

This distinction is adjacent to broader cyber-physical attack-recovery research, which already studies dedicated recovery controllers, self-healing systems, predictive recovery, and restoration of physical state after attack [@lu2024attackrecovery]. The satellite-specific evaluation problem addressed here combines controlled evidence/authorization conditions, intermittent modeled contact, mission outcomes, and evidence-qualified recovery in one comparison rather than proposing a new generic recovery-controller architecture.

## 2.4 Satellite cyber testbeds, datasets, detection, and exposure analysis

Satellite cybersecurity testbeds and datasets have expanded rapidly. NOS3/cFS research provides software-based spacecraft development and simulation infrastructure [@geletko2019nos3; @nasa_nos3; @nasa_cfs]. AegisSat provides an open-source satellite-cybersecurity testbed with a physical Earth-based CubeSat and environment emulator [@idan2025aegissat], while HADES uses NOS3, cFS, Open MCT, and T-Pot in a CubeSat-scale honeypot/testbed for adversary detection and emulation [@chan2026hades]. CuCD-ID provides a NOS3/cFS-based cybersecurity dataset [@cucdid_2026], and ESA/OPS-SAT telemetry datasets support anomaly-detection research [@esa_anomaly_2024; @opssat_ad_2025]. These artifacts demonstrate that constructing a satellite cyber range, generating attacks, or collecting telemetry is not sufficient novelty by itself.

Recent Computers & Security work establishes particularly close venue adjacency. CANSat-IDS evaluates an adaptive distributed intrusion-detection architecture for satellite CAN traffic [@driouch2024cansatids]. Casaril and Galletta analyze SatCom user-segment vulnerabilities and risk management [@casaril2024satcom], and later introduce a data-driven Risk Exposure Framework for measuring Internet-facing attack-surface exposure of space-sector organizations [@casaril2026attack_surface]. SCASS demonstrates an extensible open cyber-physical security testbed for SCADA/ICS experimentation [@dambrosio2025scass]. These studies address important upstream problems—detection, exposure assessment, risk analysis, and testbed capability—but their primary research objects differ from the response/recovery comparison studied here.

Recent onboard cybersecurity work also focuses on detector performance. TinyML-driven autonomous-spacecraft research evaluates latency/accuracy trade-offs for lightweight onboard cyber/RF threat detection [@le2026tinyml]. Broader reviews identify onboard intrusion detection, recovery, trusted supply chains, and real-time impact assessment as continuing research gaps [@mattar2025spacecyber]. The present study addresses a downstream question: given a modeled cyber event, what mission, containment, command-availability, and trusted-recovery consequences follow from alternative response policies?

## 2.5 Post-detection security-response positioning

The present experiment is best positioned as a **post-detection cyber-response and recovery evaluation**. Event establishment is an experimental precondition. The study does not estimate detector precision/recall, discover vulnerabilities, evaluate cryptographic primitives, or measure organizational attack surface. Its research question begins after a cyber-relevant state has been established: which response/recovery mechanism is selected, what security and mission costs follow, and when can the resulting state be called trusted recovery rather than merely operational restoration?

This positioning is important because it narrows the novelty claim. The study does not claim to introduce satellite intrusion detection, satellite cybersecurity testbeds, safe mode, rollback, Mission Aware theory, spacecraft FDIR, cyber-resilience engineering, or attack-surface measurement. Instead, it contributes a reproducible comparative method and evidence record for what happens **after a modeled cyber event when response and recovery choices themselves create security, availability, mission, and trust-evidence trade-offs**.

Table R5 provides a conservative closest-work comparison. Cells use language such as “not primary focus” rather than asserting that a dimension is completely absent from a cited implementation. This avoids manufacturing novelty from incomplete literature inspection while making the paper's research object visible to reviewers.

## 2.6 SPARTA behavioral correspondence of the frozen event families

The frozen Study 1 event catalog already recorded SPARTA identifiers before the final analysis. The publication uses those identifiers as **behavioral/experimental correspondences**, not as claims that complete operational attack chains were reproduced.

- **E1 — unauthorized valid command:** frozen mapping `IA-0007.02`, Malicious Commanding via Valid GS [@sparta_malicious_valid_gs]. The experiment models a syntactically valid but unauthorized command through the synthetic command path; it does not model the real compromise of a mission ground station or operational credentials.
- **E2 — replayed command:** frozen mapping `EX-0001.01`, Replay — Command Packets [@sparta_replay_command_packets]. The experiment models replay of a previously authorized laboratory command; it does not acquire or retransmit a real RF command packet.
- **E3 — compromised synthetic update:** frozen mappings `IA-0007.01`, Compromise On-Orbit Update, and `EX-0004`, Compromise Boot Memory [@sparta_onorbit_update; @sparta_compromise_boot_memory]. The treatment uses synthetic update artifacts and does not compromise a real mission supply chain, signing key, or flight image.
- **E4 — telemetry/evidence degradation:** frozen mapping `DE-0003.06`, Telemetry Downlink Modes [@sparta_telemetry_downlink_modes]. The treatment reduces/suppresses selected policy-visible evidence fields in software; it does not jam RF, intercept operational telemetry, or reproduce every mechanism covered by the SPARTA technique.

The mapping strengthens cybersecurity interpretation because the event families can be related to recognized spacecraft cyber behaviors while preserving the experimental boundary. SPARTA is a taxonomy for correspondence, not proof that all tactic stages, delivery mechanisms, preconditions, or impacts of those techniques were implemented.

## 2.7 Incident-response lifecycle position

NIST SP 800-61 Rev. 3 treats incident response as part of cybersecurity risk management and aims to improve the efficiency and effectiveness of detection, response, and recovery [@nist80061r3]. The present experiment isolates only a bounded portion of that lifecycle:

1. modeled cyber-relevant event established;
2. response-policy selection;
3. containment where applicable;
4. recovery/reconstitution;
5. evidence-qualified recovery validation; and
6. mission/security consequence measurement.

The study does not evaluate SOC alert triage, incident declaration, staffing, forensic attribution, notification/legal reporting, or organizational lessons learned. The mapping is therefore explanatory, not a claim of organizational NIST compliance.

## 2.8 Mission and temporal context as active prior art

The idea that cyber risk can vary with mission or time is active prior art. Recent temporal-risk research explicitly models how the same satellite vulnerability may have different consequences across operationally meaningful mission windows [@liu2026temporal]. The present study therefore does not claim that time- or mission-sensitive cybersecurity is new.

This adjacency makes the P1 null result especially relevant. Mission context can be theoretically important without producing a measurable policy interaction on every endpoint in every implementation. The controlled experiment varied mission state, but the predeclared P1 endpoints were unchanged across the tested state contrast. The paper consequently avoids using mission-state variation itself as a positive novelty result.

## 2.9 Remaining empirical gap and study position

The targeted publication-era literature refresh did not identify a directly equivalent controlled small-satellite experiment that jointly:

1. compares multiple cyber-response/recovery policies rather than one detector or mechanism;
2. varies spacecraft mission context and modeled contact availability;
3. reduces the evidence visible to the response policy as a controlled factor;
4. reports security containment, mission completion, command rejection, safety-invariant outcomes, and evidence-qualified recovery separately;
5. uses condition-specific Pareto comparison rather than a primary weighted score; and
6. retains conditions in which the adaptive rule-based policy is equivalent to or worse than simpler alternatives.

This is a narrow gap statement, not a first-ever or exhaustive-literature claim. The contribution is the joint comparative experimental method and the resulting conditional outcome record. Mission Aware analysis, spacecraft autonomy, FDIR, safe mode, trusted recovery concepts, satellite testbeds, anomaly detection, attack-surface measurement, and cyber-resilience engineering remain prior art and foundations for the study.
