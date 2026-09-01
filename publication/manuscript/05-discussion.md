# 5. Discussion

## 5.1 Principal findings across two separately frozen studies

The two studies were designed to test comparative response/recovery questions rather than to demonstrate superiority of a proposed autonomous policy. Their populations and analyses remain separate, but together they expose a consistent systems-security theme: cyber-response value depends on the interaction between the policy mechanism, available contact, and the quality and trustworthiness of policy-visible evidence.

Study 1 produced a mixed 720-observation empirical record. Mission-state dependence was not demonstrated on the predeclared P1 primary outcomes; one modeled missed-contact condition strongly delayed the ground-authorized P6 path; controlled omission/reduction of policy-visible evidence altered P7 recovery and actual action-selection pathways; and P7's Pareto position ranged from benefit to equivalence, mixed performance, and disadvantage depending on the frozen condition.

Study 2 then tested a higher-bar evidence and contact model in a separate 3,872-observation campaign. The strongest finding was not that one policy won. It was that **evidence qualification and objective correctness can diverge when an evidence producer itself is within the adversary budget**. Under V5, both the fail-closed and evidence-aware policies achieved evidence-qualified recovery in all 96 paired primary observations while the adjudicated unsafe-permissive rate remained 1.0. The finding establishes a trust-boundary limitation: a verifier can correctly validate evidence that is authentic and current relative to a compromised producer yet still receive a false statement about the underlying system.

The two studies therefore refine the original motivation. Cyber containment is not interchangeable with mission preservation, nominal operation is not interchangeable with trusted recovery, and evidence authenticity is not interchangeable with truth. A response architecture can reduce one risk while increasing command rejection, mission interruption, recovery delay, or dependence on an evidence plane whose trust assumptions must themselves be explicit.

## 5.2 Mission state, contact, and authorization dependencies

Mission Aware cybersecurity provides a systems-theoretic method for relating mission requirements, critical functions, architecture, and cyberattack consequences [@bakirtzis2026missionaware]. Spacecraft fault-management literature likewise treats operational state, resource condition, and communication availability as relevant to recovery logic [@wanninger2025fdir; @thangavel2024trusted; @sarri2026juice]. Those foundations made mission-state dependence a reasonable Study-1 proposition, but the P1 result was null on the predeclared M01, M02, M03, and M06 contrasts/interactions. The result should not be rescued with an exploratory endpoint or reframed as confirmation of Mission Aware theory. It identifies a boundary of the tested implementation: the selected states and policy mechanisms did not produce measurable differences on those primary outcomes.

Contact and authorization produced clearer effects in both studies. In Study 1, one synthetic missed-contact window increased P6 containment RMST by 10.0831 s, verified-recovery RMST by 10.4246 s, and ground/spacecraft state-divergence duration by 10.0676 s, while the corresponding P7 contrasts were approximately zero. This demonstrates the timing cost of the implemented authorization dependency under that frozen model, not a universal advantage for autonomous response.

Study 2 generalized the contact question across K0–K3 ordered outages plus K4 intermittent/flapping contact. The evidence-aware selector retained an unsafe-permissive rate of 0 under K1–K4 by restricting first and proceeding at the next modeled contact opportunity, reaching recovery at 25, 65, 185, and 30 logical seconds. The fail-closed baseline also eventually recovered, but its initial permissive action under unavailable authorization created a +1.0 unsafe-permissive increase relative to K0 at each non-K0 profile. Its K0–K3 unsafe-permissive slope was +0.3 per severity step, compared with 0 for the evidence-aware selector.

These findings do not make K4 a fourth severity level; K4 was prospectively separated as intermittent/flapping contact. Nor do the Study-2 time values represent orbital-access or communications latency. They are deterministic logical SIL constants. The broader engineering implication is that authorization semantics must be evaluated together with the contact regime: a label such as “fail closed” is insufficient to predict safe behavior unless the action taken while authorization is unavailable is defined precisely.

## 5.3 From evidence sufficiency to evidence-plane trust

Study 1 established the first evidence dependency. In the retained compromised-update block, fixed P5 achieved trusted recovery in all repetitions under both evidence conditions, while P7 moved from 30/30 trusted recoveries under T0 to 0/30 trusted recoveries and 30/30 recovery failures under T1. The P4 semantic audit showed that field omission/reduction changed the actual P7 selection basis and effective-policy/action pathway rather than merely changing an analysis label.

That result should remain bounded. Study-1 T1 removed selected fields from the policy-visible evidence map; it did not independently manipulate staleness, source contradiction, post-signature modification, or producer compromise. Its causal statement is therefore limited to omission/reduction within the implemented deterministic architecture.

Study 2 prospectively separated those mechanisms. V1–V4 caused fail-closed and evidence-aware policies to move from a V0 recovery-gate attempt to restrictive/hold behavior under the frozen Block-A prerequisites. V5 was qualitatively different because the compromised producer could make a false claim that remained cryptographically valid and sufficiently current for policy-visible qualification. Both B0 and S1 then achieved evidence-qualified recovery while the adjudicated unsafe-permissive rate remained 1.0.

This is a security-assurance result rather than an argument against cryptographic authentication. Authentication answers whether a claim came from the key holder and was unmodified after signing; it does not prove that the key holder is uncompromised or that the signed statement is objectively true. For trusted recovery, the relevant question is therefore not only whether evidence verifies, but whether the evidence-producing plane remains inside the trusted computing and adversary assumptions. Cyber-resilience guidance that emphasizes recovery to an approved state [@nist800160v2r1] and space cyber-safe/recovery concepts [@sparta_cybersafe] is consistent with this distinction, but the experiment provides a concrete controlled demonstration within its bounded model.

The result also sharpens terminology. “Evidence-qualified trusted recovery” is intentionally not called “objectively safe recovery.” The research-only adjudication truth was never selector input. That separation avoids giving the response policy an oracle that would make the experiment trivial and preserves the exact security question: how does a policy behave using only the evidence it is allowed to see?

## 5.4 Context-sensitive selection is useful only under explicit trade-offs

Study 1's P5 analysis showed why a universal policy winner is not justified. P7 was on the point-estimate Pareto front in five of nine groups, but three were principally equivalence/delegation cases, and P7 was point-dominated in four groups. Favorable cases showed that contextual selection could avoid an observe-only baseline or a ground-authorization delay. Unfavorable cases showed lower mission completion, higher command rejection, or loss of trusted recovery when the selector chose a conservative path under reduced evidence.

Study 2 reaches a compatible conclusion without reusing the Study-1 Pareto framework. Within Block A, the evidence-aware selector and fail-closed baseline had identical primary endpoint estimates. Relative to the risk-threshold baseline, the evidence-aware selector was more permissive under V0 and V5; under V5 that permissiveness yielded evidence-qualified recovery but also an unsafe-permissive difference of +1.0. Block D further showed that context dimensions have scenario-specific effects: removing mission or contact context in the unauthorized-command condition increased unsafe-permissive behavior by +1.0, while the security-only update/recovery ablation reduced evidence-qualified recovery by 1.0 and added 230 logical seconds of restricted recovery time.

The common lesson is that “mission-aware,” “fail closed,” “risk threshold,” and “evidence aware” are mechanism descriptions, not performance guarantees. Their value depends on which information is present, which information can be trusted, and which cost dimensions matter in the current scenario. The studies therefore preserve multiple endpoints and explicitly prohibit a weighted global policy score or rank.

## 5.5 Structural label invariance is not causal benign/adversarial discrimination

Study 2 originally included matched BENIGN/ADVERSARIAL cause labels in Block C. The frozen runtime reveals an important interpretation limit: within each ambiguity family, the cause label does not alter hidden truth or generated policy-visible evidence. All 54 C-family endpoint contrasts were therefore zero and 0/54 were Holm-rejected by construction of the operative variables.

This result is useful as a control: changing a non-operative label alone does not change policy outcomes. It is **not** evidence that the evaluated policies can or cannot distinguish genuinely different benign and adversarial causal mechanisms. A stronger causal-ambiguity study would need distinct benign and adversarial mechanisms that produce intentionally matched or partially overlapping observable evidence while preserving different underlying causes. That design is now a genuine future-work requirement rather than a claim extracted from Block C.

The distinction matters for journal credibility because “matched observations” can describe two very different designs. One design varies the hidden cause while keeping observables matched; another merely changes a label attached to an otherwise identical runtime condition. Study 2 implemented the latter in Block C. The manuscript therefore reports it as structural label invariance and does not promote it into empirical fault-versus-attack discrimination evidence.

## 5.6 Relation to prior satellite cybersecurity and recovery research

The publication-era literature supports a narrow novelty boundary. Satellite cybersecurity testbeds and datasets—including NOS3/cFS-based work, AegisSat, CuCD-ID, HADES, and telemetry anomaly benchmarks—show that building a simulator, generating attacks, or collecting telemetry is not itself novel [@geletko2019nos3; @idan2025aegissat; @cucdid_2026; @chan2026hades; @esa_anomaly_2024; @opssat_ad_2025]. Trusted autonomy, spacecraft FDIR, safe mode, recovery from known-good images, and cyber-safe recovery are likewise established topics [@thangavel2024trusted; @wanninger2025fdir; @sparta_cybersafe].

Recent Computers & Security work provides direct venue adjacency but a different center of gravity: CANSat-IDS targets satellite CAN intrusion detection [@driouch2024cansatids]; SatCom user-segment work emphasizes vulnerability/risk-management analysis [@casaril2024satcom]; the Risk Exposure Framework measures Internet-facing attack-surface exposure [@casaril2026attack_surface]; and SCASS emphasizes an extensible cyber-physical security testbed [@dambrosio2025scass]. Detector-focused and TinyML studies primarily assess detection accuracy or latency [@driouch2024cansatids; @le2026tinyml], while telemetry benchmarks emphasize anomaly-detection performance [@esa_anomaly_2024; @opssat_ad_2025]. Those are upstream questions.

The contribution here is the reproducible comparison of **post-detection response and recovery** under mission, contact, evidence, and adversary constraints. Study 1 establishes the condition-specific multi-objective response comparison; Study 2 adds explicit evidence-integrity and producer-compromise semantics, a broader contact model, interpretable baselines, context ablations, and independently reproduced statistical outputs. The novelty claim therefore remains methodological and empirical rather than conceptual ownership of autonomy, safing, cryptography, or recovery.

The work is also adjacent to cyber-physical attack-recovery research on recovery controllers, predictive recovery, and self-healing systems [@lu2024attackrecovery]. Its spacecraft-specific contribution is not a new generic recovery-controller concept; it is the controlled combination of intermittent modeled contact, evidence-plane trust, mission constraints, and response/recovery consequences in a reproducible software-in-the-loop setting.

## 5.7 Implications for response-system design and assurance

The combined evidence suggests five dependency classes that should be explicit during spacecraft cyber-response architecture review.

**Authorization dependencies.** Which actions require remote approval, and what action is taken while approval is unavailable? Study 1 shows the timing cost of a modeled wait-for-ground policy; Study 2 shows that an initially permissive action under unavailable authorization can become unsafe even if recovery later succeeds.

**Evidence sufficiency dependencies.** Which fields or observations must be present before a selector can choose or complete a recovery path? Study 1 shows that controlled omission can redirect the deterministic selector and prevent trusted recovery.

**Evidence trust dependencies.** Which producers are assumed uncompromised, and can a validly signed/current claim be false if its producer is controlled? Study 2 V5 demonstrates why producer trust must be separated from signature verification.

**Availability and mission-cost dependencies.** What legitimate command or mission functionality is sacrificed by a containment or fallback action? Study-1 P4/P5 and Study-2 ablations show that more restrictive behavior can impose command, mission, or recovery costs without automatically improving every endpoint.

**Recovery-assurance dependencies.** What evidence must be re-established before an operational-looking system is considered recovered? Both studies require recovery evidence beyond nominal behavior, while Study 2 additionally demonstrates that the provenance and trustworthiness of that evidence plane matter.

These dependencies map naturally to the response/recovery portion of NIST SP 800-61 Rev. 3 [@nist80061r3], but the experiments do not implement a complete organizational incident-response program and do not establish NIST compliance. Their practical role is to make assumptions measurable before operational adoption.

## 5.8 Limitations

The two studies share important limitations and also have study-specific ones.

**Software-in-the-loop fidelity.** The experiments used controlled NOS3/Fortytwo/cFS-based software environments [@nasa_nos3; @nasa_cfs]. They did not reproduce full spacecraft dynamics, flight-processor constraints, RF propagation, ground-network behavior, orbital-access scheduling, or operational procedures. `ENTER_SAFE_MODE` in Study 1 was an experimental modeled action rather than a native spacecraft safe-mode implementation.

**Synthetic time and contact.** Study-1 C1 represented one modeled missed-contact window and its approximately 10-s effect must not be extrapolated to ground-station or RF latency. Study-2 K0–K4 timings are deterministic logical SIL time with a 240-s censor horizon. They likewise are not measured orbital access, operator response, network latency, or spacecraft timing.

**Bounded scenario coverage.** Study 1 covered its frozen E1–E4 events and selected mission/evidence/contact cells. Study 2 expanded evidence, contact, adversary, and context factors but remains a bounded synthetic model. Neither campaign establishes behavior for untested attack chains, mission phases, architectures, or evidence producers.

**Deterministic policy mechanisms.** The mission-aware/evidence-aware selectors are frozen rule-based mechanisms, not learned or continuously adapting agents. This supports reproducibility and internal validity but prevents generalization to all autonomous or AI/ML-based systems.

**Evidence-model abstraction.** Study-1 T1 is omission/reduction only. Study 2 adds stale/replay, contradiction, post-signature manipulation, and bounded producer compromise, but still uses deterministic synthetic evidence and deterministic producer keys. The studies do not evaluate real key theft, supply-chain compromise, hardware roots of trust, cryptographic algorithm strength, or operational attestation infrastructure.

**Block-C structural control.** Study-2 BENIGN/ADVERSARIAL labels are non-operative with respect to truth and policy-visible evidence. Block C cannot support causal benign-versus-adversarial discrimination claims.

**Secondary sample-size role.** Study-2 Blocks B–E use 32 paired seeds and were prospectively designated for estimation/sensitivity rather than powered detection of small effects. Large deterministic contrasts can be reported, but absence of a small effect should not be interpreted as evidence of equivalence unless supported by the corresponding design and interval.

**Administrative censoring.** Study-1 M04/M05 used a frozen 30-s horizon; Study 2 used a frozen 240-logical-second restricted-time horizon. Conclusions about time-to-event outcomes are horizon-specific.

**Study-1 structural zero.** No M03 violations occurred in the 720 VALID Study-1 runs. This prevents meaningful differential violation-risk estimation and is not proof of universal safety.

**Study-1 execution provenance.** Ten VALID Study-1 observations were executed on two earlier runtime-orchestration/finalization commits. The analytical-exchangeability review and 29-seed final-commit complete-block sensitivity found no scientific-core difference or P5 relation change, but the versioned history remains a reproducibility consideration and is reported rather than hidden.

**No human/operator study.** Human cognition, workload, trust, decision latency, and operational approval behavior were not measured. Ground authorization is synthetic and supports no conclusion about operator performance.

**No operational validation.** Neither study establishes flightworthiness, certification, production incident-response readiness, or safe autonomous control of an operational spacecraft. No operational spacecraft, ground station, real credentials, proprietary mission telemetry, or RF transmission/interference was used.

## 5.9 Future research after Study 2

Study 1 and Study 2 should remain frozen. Additional evidence should be generated under new protocols rather than appended to either statistical population.

The first priority is a **causal fault-versus-attack ambiguity study** that corrects the Block-C limitation. Benign and adversarial mechanisms should differ in hidden cause and state evolution while producing deliberately matched or partially overlapping policy-visible evidence. Such a design could measure whether response policies remain bounded when causal attribution is genuinely unresolved rather than when only a label changes.

A second priority is **aerospace-system validation**. A separate engineering study should add simulated orbital/access schedules, richer mission-phase profiles, flight-like CPU/memory/command/telemetry measurements, and an RF-free hardware-in-the-loop subset using cFS with simulated sensors/actuators and a software-only ground link. Its purpose would be implementation/performance transfer, not flight qualification.

A third priority is **human authorization and operational decision research**. Operator workload, trust, approval timing, escalation behavior, and human-machine responsibility should be studied separately under the appropriate human-subject and operational approvals. Any move toward RF, proprietary telemetry, operational assets, or real credentials would require a new legal, safety, and responsible-research review.

A fourth priority is **evidence-plane assurance** beyond the deterministic producer model. Hardware-backed roots of trust, key compromise/revocation, independent corroboration, provenance diversity, delayed evidence, and recovery from compromised evidence producers are natural extensions of the V5 boundary. These should remain distinct from cryptographic-algorithm research; the present result concerns producer trust and claim correctness, not cryptanalytic strength.

The research-program rule remains separation: each new study should have its own frozen design, estimands, seeds, provenance, analysis implementation, and archive. Larger sample counts are useful only when they answer a new validity or generalization question.

## 5.10 Overall interpretation

Across two controlled studies, the strongest conclusion is not that mission-aware or evidence-aware autonomy is universally superior. It is that satellite cyber-response and trusted-recovery mechanisms should be evaluated under explicit **mission, authorization, contact, evidence-sufficiency, and evidence-trust assumptions**, with security and mission outcomes retained separately.

Study 1 shows that contact availability and evidence sufficiency can dominate the implemented response pathway even when mission-state dependence is not demonstrated. Study 2 shows that valid/current policy-visible evidence can still be wrong when its producer is compromised, and that a policy's behavior under lost authorization depends critically on whether its initial action is restrictive or permissive. Together, these findings make the trust boundary around recovery evidence a first-class part of response evaluation.

That combination of supported, null, adverse, structural-control, and conditional findings provides a stronger basis for journal contribution than a single-policy superiority claim. The paper therefore presents a reproducible post-detection cyber-response/trusted-recovery evaluation method and a pair of integrity-frozen empirical records, bounded to their controlled software-in-the-loop assumptions.
