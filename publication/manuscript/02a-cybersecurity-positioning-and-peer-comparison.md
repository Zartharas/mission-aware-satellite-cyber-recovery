# 2A. Cybersecurity Positioning and Closest-Work Comparison

## 2A.1 Security problem addressed by the study

The study is positioned as a **post-detection cyber-response and recovery evaluation**, not as an intrusion-detection, vulnerability-discovery, cryptographic-protocol, or attack-surface paper. Detection of the modeled event is an experimental precondition. The research question begins after a cyber-relevant event has been established: which response/recovery mechanism is selected, what security and mission costs follow, and when can the resulting state be called trusted recovery rather than merely operational restoration?

This distinction is important because recent satellite-cybersecurity work already provides strong contributions upstream of that decision point. CANSat-IDS focuses on adaptive distributed intrusion detection for satellite CAN traffic [@driouch2024cansatids]. Casaril and Galletta analyze SatCom user-segment vulnerabilities and cyber-risk management [@casaril2024satcom], while their later Risk Exposure Framework quantifies externally observable attack-surface exposure for space organizations, primarily in ground/enterprise environments [@casaril2026attack_surface]. AegisSat provides an open satellite-cybersecurity testbed capable of supporting attack, detection, and defense research [@idan2025aegissat], and HADES develops a CubeSat-scale honeypot/testbed for adversary detection and emulation [@chan2026hades]. SCASS demonstrates the value of extensible cyber-physical testbeds and digital-twin-style security experimentation in industrial control systems [@dambrosio2025scass].

The present work occupies a different point in the security lifecycle. It compares alternative containment/recovery policies under common controlled conditions and measures security containment, legitimate-command availability, mission completion, evidence sufficiency, state divergence, and evidence-qualified recovery separately. The contribution is therefore best described as **comparative cyber-response and trusted-recovery evaluation under constrained connectivity and imperfect defender evidence**.

## 2A.2 Closest empirical-work comparison

Table R5 summarizes the relationship between this study and several close or venue-adjacent works. The comparison intentionally uses conservative labels such as “primary focus” and “not primary focus” rather than claiming that an omitted dimension is absent from every implementation detail of the cited work. The purpose is to identify the principal contribution each source reports and the specific comparative gap addressed here.

The key differentiator is not that the current study uses a satellite simulator, since satellite and cyber-physical testbeds are established prior art. It is the joint experimental structure: multiple response/recovery policies are evaluated under the same frozen design while contact availability and policy-visible evidence are manipulated, trusted recovery is separately adjudicated from nominal operation, and adverse/equivalent outcomes for the mission-aware selector are retained rather than converted into a single composite ranking.

The related-work comparison also limits the novelty claim. The paper does **not** claim to introduce satellite intrusion detection, satellite cyber testbeds, safe mode, rollback, mission-aware systems engineering, cyber-resilience engineering, or attack-surface measurement. Instead, it contributes a reproducible method and outcome record for evaluating what happens **after a modeled cyber event when response and recovery choices themselves create security, availability, mission, and trust-evidence trade-offs**.

## 2A.3 Space-specific threat-framework alignment

The frozen event catalog already recorded SPARTA identifiers for each E1–E4 event family. The publication mapping therefore follows those **pre-existing event-catalog associations** rather than introducing a new post-hoc technique assignment. SPARTA is used as a vocabulary for behavioral correspondence; the experiment does not reproduce complete operational attack chains, real initial access, RF delivery, operational credentials, or adversary infrastructure [@sparta_techniques].

- **E1 — unauthorized valid command.** The frozen catalog maps E1 to SPARTA **IA-0007.02, Malicious Commanding via Valid GS** [@sparta_malicious_valid_gs]. The laboratory treatment reproduces only the consequential security condition—a syntactically valid command on an expected source path that is not authorized. It does not model compromise of a real ground system, operator account, waveform, antenna, or mission command infrastructure.
- **E2 — replay of an authorized laboratory command.** The frozen catalog maps E2 to **EX-0001.01, Replay — Command Packets** [@sparta_replay_command_packets]. The experiment replays a synthetic previously valid command and does not model interception or acquisition of an operational telecommand.
- **E3 — compromised synthetic software/update context.** The frozen catalog associates E3 with **IA-0007.01, Compromise On-Orbit Update**, and **EX-0004, Compromise Boot Memory** [@sparta_onorbit_update; @sparta_compromise_boot_memory]. The implemented treatment uses synthetic update artifacts and integrity/rollback state. It does not compromise a real mission software supply chain, flight image, boot device, signing key, or operational update service.
- **E4 — policy-visible telemetry/evidence degradation.** The frozen catalog maps E4 to **DE-0003.06, Telemetry Downlink Modes** [@sparta_telemetry_downlink_modes]. The laboratory event selectively represents suppressed/delayed or incomplete policy-visible telemetry/evidence while immutable experiment ground truth remains available outside the runtime policy. It does not alter or intercept an operational spacecraft downlink.

This alignment strengthens external cybersecurity interpretation without changing the frozen treatments. The SPARTA identifiers describe **behavioral adjacency/experimental abstraction**, not evidence that every prerequisite, tactic stage, technical mechanism, or operational effect defined by SPARTA was reproduced.

## 2A.4 Incident-response lifecycle positioning

NIST SP 800-61 Rev. 3 integrates incident response into broader cybersecurity risk management and emphasizes the effectiveness of incident detection, response, and recovery [@nist80061r3]. The present experiment covers only a bounded portion of that lifecycle. Event establishment is treated as a precondition; the study does not evaluate detector accuracy, alert triage, SOC staffing, or human incident-declaration latency.

Within that boundary, the experiment can be mapped as follows:

1. **Modeled incident/event established** — synthetic E1–E4 treatment state becomes active.
2. **Response-policy selection** — a fixed, ground-authorized, recovery, or mission-aware response mechanism is invoked.
3. **Containment** — M04 captures time to the modeled containment event where applicable.
4. **Recovery/reconstitution** — the response may isolate, restrict, enter the experimental safe-mode action, or perform verified rollback.
5. **Recovery validation** — trusted recovery requires current evidence satisfying the frozen checklist rather than nominal behavior alone.
6. **Operational consequence measurement** — mission completion, legitimate-command rejection, state divergence, safety invariants, and recovery outcome are retained separately.

This is an analytical mapping rather than a claim of NIST compliance. Its value is to make the spacecraft experiment legible to mainstream incident-response and cyber-resilience reviewers: the experiment isolates the response/recovery decision problem while explicitly excluding upstream detection and downstream organizational lessons-learned processes.

## 2A.5 Resulting novelty boundary

After the publication-era literature refresh, the defensible novelty statement is narrow but strong: **the study jointly evaluates alternative satellite cyber-response/recovery policies under controlled contact and evidence constraints while preserving separate security, mission, availability, safety, and trusted-recovery outcomes and retaining conditions in which the adaptive selector is equivalent or inferior to simpler policies.**

That claim should remain conditional on the implemented NOS3/Fortytwo/cFS environment. It should not be expanded into a claim of first-ever satellite autonomy, first trusted-recovery mechanism, first spacecraft cyber testbed, or universal superiority of mission-aware response.
