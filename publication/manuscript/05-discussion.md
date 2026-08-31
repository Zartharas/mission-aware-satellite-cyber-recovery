# 5. Discussion

## 5.1 Principal findings

This study was designed to test a comparative question rather than to demonstrate the superiority of a proposed adaptive policy. Across 720 frozen VALID software-in-the-loop observations, that design produced a mixed empirical record. Mission-state dependence was not demonstrated on the predeclared P1 primary outcomes; a modeled missed-contact condition strongly delayed the ground-authorized P6 path; reduced policy-visible evidence altered P7 recovery and action-selection pathways; and P7’s Pareto position varied from supported benefit to equivalence, mixed performance, and supported disadvantage depending on the frozen condition.

The resulting interpretation is therefore narrower than a generic claim that mission-aware autonomy improves spacecraft cybersecurity. The evidence instead supports a conditional proposition: response value depends on the interaction between the implemented policy mechanism and the information/operational constraints present in the tested scenario. In this experiment, contact availability and evidence sufficiency were stronger discriminators than mission state on the predeclared P1 endpoints.

This pattern is consistent with the study’s original multi-objective motivation. Cyber containment is not interchangeable with mission preservation, and nominal operation is not interchangeable with trusted recovery. A policy can reduce one form of exposure while increasing command rejection, mission interruption, recovery delay, or dependence on information that may itself be incomplete.

## 5.2 Mission-state dependence: a theoretically plausible effect that was not demonstrated here

Mission Aware cybersecurity provides a systems-theoretic method for relating mission requirements, critical functions, architecture, and cyberattack consequences [@bakirtzis2026missionaware]. Spacecraft fault-management literature likewise treats operational state, resource condition, and communication availability as relevant to recovery logic [@wanninger2025fdir; @thangavel2024trusted; @sarri2026juice]. These foundations made mission-state dependence a reasonable pre-experiment proposition.

The P1 result nevertheless was null on the predeclared M01, M02, M03, and M06 contrasts/interactions. This finding should not be reframed as confirmation of the Mission Aware framework, nor should it be rescued with an exploratory endpoint. Instead, it identifies a boundary of the tested implementation: the specific mission-state manipulations and policy mechanisms in the P1 block did not produce measurable differences on those primary outcomes.

Several interpretations remain possible without changing that conclusion. The selected states may not have induced sufficiently different resource or mission constraints for the applicable policy comparison; the deterministic event/policy mechanisms may have dominated the state context; or the primary endpoints may have been insensitive to differences that would matter in a richer physical or operational model. Those possibilities are hypotheses for later work, not explanations established by the present campaign.

The null result is scientifically useful because current space-cyber and spacecraft-resilience discussions often treat mission context as intrinsically important. Recent work on temporal satellite risk similarly argues that consequences can vary across operationally meaningful time windows [@liu2026temporal]. The present result shows that theoretical relevance does not guarantee an observable response-policy interaction in every controlled implementation. For manuscript framing, Mission Aware is therefore best treated as the design and analysis lens that motivated the controlled factors and unacceptable-loss model, rather than as a general mission-state-dependence theory empirically validated by P1.

## 5.3 Contact constraints primarily exposed the cost of ground authorization

P2 produced the clearest timing result. Under one modeled missed-contact window, P6 containment, verified-recovery RMST, and ground/spacecraft divergence each increased by approximately 10 s, whereas P7 changed by approximately zero on the same contact contrasts. The interaction was correspondingly large and consistent across the three timing endpoints.

This result is mechanistically coherent with the frozen policy definitions. P6 is ground-authorized WAIT: it must reach the modeled authorization gate before delegating the verified-rollback action. P7 does not wait on that gate in the corresponding autonomous path. The result therefore demonstrates the timing cost of the implemented authorization dependency under the controlled contact condition. It does not establish that autonomous policies are universally superior to ground-authorized recovery.

The distinction matters because intermittent communication is established spacecraft-engineering prior art rather than a novel problem. Spacecraft FDIR, safing, and autonomous-recovery designs have long accounted for delayed or unavailable ground intervention [@wanninger2025fdir; @sarri2026juice], and contemporary satellite incident-response guidance also recognizes that containment or recovery actions may depend on contact windows and approval gates [@chunawala2026satelliteir]. The contribution here is not recognition of that constraint; it is the controlled cyber-response comparison showing how a ground-authorization dependency propagates into containment, trusted-recovery, and state-divergence timing under a frozen experiment.

The synthetic nature of C1 is also important. The approximately 10-s effect is tied to the configured missed-contact model and 30-s analysis horizon. It is not a measured ground-station latency, operator-response distribution, orbital-access statistic, or RF-link characteristic. Operational extrapolation would require mission-specific communication geometry, scheduling, link performance, human procedures, and recovery authority models that were deliberately outside this experiment.

## 5.4 Evidence sufficiency was a central determinant of trusted recovery and deterministic selection

The P3 and P4 results elevate policy-visible evidence sufficiency from a supporting design consideration to a central empirical finding. In the retained E3 block, fixed P5 achieved trusted recovery in all repetitions under both evidence conditions, while P7 moved from 30/30 trusted recoveries under T0 to 0/30 trusted recoveries and 30/30 recovery failures under T1. The P4 semantic audit further showed that reduced evidence changed the actual P7 selection basis and effective-policy/action pathway rather than merely changing an analysis label.

Study 1's evidence treatment should be interpreted precisely. T1 removed selected fields from the policy-visible evidence map according to the frozen event adapter. It did not separately manipulate stale values, contradictory sources, forged observations, or probabilistic sensor corruption. The causal statement supported by Study 1 is therefore bounded: **within the implemented deterministic architecture, controlled omission/reduction of policy-visible evidence was upstream of P7 selection and downstream recovery/mission consequences.** Broader adversarial-observation mechanisms require a separate experiment.

This distinction is important for cyber recovery. Cyber-resilience guidance emphasizes recovery and reconstitution to an approved state [@nist800160v2r1], and SPARTA cyber-safe/recovery concepts emphasize integrity-protected known-good states and trusted recovery mechanisms [@sparta_cybersafe]. The present experiment operationalized that idea by requiring current evidence before `TRUSTED_RECOVERY_CONFIRMED`. The P3 result shows why this is materially different from simply asking whether a system appears operational after a response action.

At the same time, the specific mechanism differed from the anticipated one. The predeclared P3 expectation included the possibility that a run would appear nominally restored while remaining unverified. A13 did not exhibit that pattern; it failed recovery. The broader evidence-dependence proposition is therefore supported, but the narrower restoration-without-verification mechanism is not. Retaining that distinction avoids converting an expectation into an observation.

P4 also demonstrates why post-hoc correctness labels should be avoided. In E1, reduced evidence moved P7 from P2 restriction to the experimental P4 safe-mode action, reducing mission-objective completion and increasing legitimate-command rejection without producing a safety-invariant violation or mission-loss terminal event. In E3, reduced evidence caused an explicit `evidence_insufficient` basis and moved P7 from verified rollback to P2 restriction, with a corresponding loss of trusted recovery. These are observable selection and consequence differences. The experiment does not contain an independent runtime oracle that establishes one selected action as universally “correct” for the scenario.

This finding has a practical design implication: a deterministic or adaptive response engine should expose evidence sufficiency as part of its decision state, but a conservative fallback is itself a policy choice with mission and recovery costs. “Fail closed” is not cost-free. Its value must be evaluated against mission objectives, recovery paths, and the availability of trustworthy evidence rather than assumed from security posture alone.

## 5.5 Conditional Pareto performance is more informative than a single policy winner

P5 was intentionally framed so that either universal failure or universal dominance of P7 would be scientifically suspicious. The retained result falls between those extremes. P7 was on the point-estimate Pareto front in five of nine groups, but three of those groups were principally tie/delegation-equivalence cases. P7 was point-dominated in four groups, and marginal intervals supported both P7 advantages and comparator advantages in different conditions.

The strongest favorable comparisons occurred in G07 and G08. In G07, P7 selected P5 and dominated the ground-authorized P6 alternative, primarily through substantially shorter verified-recovery time under the contact-constrained condition. In G08, P7 selected P1, dominated the observe-only P0 baseline, and tied the fixed P1 comparator. These cases show where contextual selection can avoid a weak baseline or an authorization delay.

The unfavorable cases are equally important. In G04, P7’s P4 selection incurred lower mission completion and higher command rejection than P2 without a compensating primary-endpoint advantage. In G06, reduced evidence caused P7 to select P2 while fixed P5 retained trusted recovery. In G09, P7’s P4 selection added rejection cost without improving the five Pareto dimensions relative to P0. G05 illustrates a different form of limitation: P7 matched the effective P5 mechanism closely enough to dominate weaker comparators, yet the fixed P5 cell had a slightly better point-estimate M05 RMST, with the marginal comparison remaining uncertain/tied.

These results argue against reducing spacecraft cyber-response evaluation to one composite score. A weighted score could conceal whether an apparent gain came from sacrificing command availability, mission completion, or recovery time. Pareto analysis preserves the multidimensional structure and makes condition-specific equivalence and disadvantage visible. This is aligned with broader cyber-resilience engineering, which treats mission risk reduction as a set of system objectives rather than a single universal performance metric [@nist800160v2r1].

The P5 outcome also constrains how “mission-aware” should be used in the paper. P7 is mission-aware by construction because it deterministically selects responses from policy-visible cyber, mission, evidence, and contact context. The results do not justify redefining mission-aware response as superior response. In several groups, P7 simply selected the same effective mechanism as a fixed comparator; in others it selected a worse trade-off. The contribution is therefore evidence about conditional rule-based selection behavior, not proof of a preferred flight architecture or a learned autonomous agent.

## 5.6 Relation to prior satellite cybersecurity and recovery research

The publication-era literature refresh reinforces a narrow novelty boundary. Satellite cybersecurity testbeds and datasets—including NOS3/cFS-based work, AegisSat, CuCD-ID, HADES, and telemetry anomaly benchmarks—demonstrate that building a simulator, generating attacks, or collecting telemetry is not itself novel [@geletko2019nos3; @idan2025aegissat; @cucdid_2026; @chan2026hades; @esa_anomaly_2024; @opssat_ad_2025]. Similarly, trusted autonomy, spacecraft FDIR, safe mode, recovery from known-good images, and cyber-safe recovery are established topics in spacecraft engineering and security guidance [@thangavel2024trusted; @wanninger2025fdir; @sparta_cybersafe].

Recent Computers & Security work provides direct scope-adjacent examples but a different research center of gravity: CANSat-IDS targets satellite CAN intrusion detection [@driouch2024cansatids]; SatCom user-segment work emphasizes vulnerability/risk-management analysis [@casaril2024satcom]; the Risk Exposure Framework measures Internet-facing attack-surface exposure of space organizations [@casaril2026attack_surface]; and SCASS emphasizes an extensible cyber-physical security testbed [@dambrosio2025scass]. Table R5 compares these primary research objects conservatively rather than asserting that every non-primary dimension is absent from each implementation.

The present study differs primarily in the joint **post-detection response/recovery comparison**. It freezes multiple response/recovery policies, event families, mission contexts, evidence conditions, and contact conditions; measures security containment, mission completion, command rejection, safety invariants, divergence, and verified recovery separately; retains negative outcomes; and preserves execution/provenance identities for repeated trials. The novelty claim should therefore remain at the level of the reproducible comparative method and the resulting conditional evidence.

This distinction also separates the work from detector-focused research. Recent onboard and TinyML cybersecurity studies emphasize detection accuracy and latency [@driouch2024cansatids; @le2026tinyml], while telemetry benchmark work emphasizes anomaly-detection performance [@esa_anomaly_2024; @opssat_ad_2025]. Those are upstream problems. The current experiment assumes a modeled event has occurred and asks what happens after alternative response/recovery policies are applied under incomplete information and contact constraints.

The work is also adjacent to cyber-physical attack-recovery research, which already studies dedicated recovery controllers, predictive recovery, and self-healing systems [@lu2024attackrecovery]. The spacecraft-specific contribution is not a new generic recovery-controller concept; it is the combination of intermittent modeled contact, trusted-state evidence, spacecraft mission constraints, and controlled cyber-response comparisons within a reproducible small-satellite software-in-the-loop environment.

## 5.7 Implications for cybersecurity response-system design and evaluation

The results suggest four dependency classes that should be made explicit during spacecraft cyber-response architecture review.

**Authorization dependencies.** Which containment or recovery actions require remote approval, and what happens when the approval path is unavailable? P2 shows that the implemented ground-authorization requirement becomes measurable containment, recovery, and state-divergence delay under the modeled missed-contact condition.

**Evidence dependencies.** Which telemetry, integrity, authorization, or attestation observations must be available and current for a response/recovery decision? P3/P4 show that changing the evidence available to the deterministic selector changes the implemented response pathway even though immutable experiment ground truth remains unchanged. Runtime policy-visible state, experiment ground truth, and recovery evidence should therefore be logged and evaluated separately.

**Availability dependencies.** What legitimate command or mission functionality is sacrificed by a containment/fallback action? P4/P5 show that a more conservative response can impose mission-completion or command-rejection costs without automatically improving every primary security/recovery dimension.

**Recovery-assurance dependencies.** What evidence must be re-established before an apparently operational system is called trusted? The frozen recovery criteria require software/configuration identity, integrity/authorization evidence, current state evidence, restored command authority, telemetry, state agreement, health, and absence of modeled residual unauthorized state.

These dependencies map naturally to the response/recovery portion of NIST SP 800-61 Rev. 3 [@nist80061r3], but the experiment does not implement a complete organizational incident-response program. Its practical contribution is to make response/recovery dependencies measurable before operational adoption, not to prescribe mission-specific thresholds or procedures.

More generally, response evaluation should preserve multiple mission/security outcomes. The P5 results show that a policy can appear attractive on one outcome while incurring mission or command-availability costs on another. For safety- and mission-critical systems, condition-specific trade-off reporting is more informative than choosing a universal winner from an arbitrary weighting scheme.

These implications are method-level rather than deployment prescriptions. They identify factors that should be represented in design reviews, simulations, digital twins, and assurance experiments. They do not establish flightworthiness, certification, or a production-ready autonomous recovery architecture.

## 5.8 Limitations

The study has several important limitations.

**Software-in-the-loop fidelity.** The experiment used a controlled NOS3/Fortytwo software environment [@nasa_nos3; @nasa_cfs]. It did not reproduce the full dynamics, hardware timing, flight-processor constraints, RF propagation, ground-network behavior, or operational procedures of a deployed satellite system. `ENTER_SAFE_MODE` was an experimental modeled action rather than a native spacecraft safe-mode implementation.

**Synthetic contact condition.** C1 represented one modeled missed-contact window. Its approximately 10-s effect should not be extrapolated directly to orbital access, antenna scheduling, operator behavior, or RF-link outages.

**Bounded event and state coverage.** The final campaign covered the frozen E1–E4 event families and selected mission/evidence/contact conditions. The P1 null result and P5 Pareto relations are conditional on those implemented cells and do not establish behavior for untested mission phases, attack chains, resource states, or architectures.

**Deterministic policy mechanisms.** P7 was a frozen rule-based mission-aware selector rather than a learned or continuously adapting agent. This supports reproducibility and internal validity but limits conclusions about adaptive learning systems. Conversely, the result should not be generalized to all rule-based mission-aware designs.

**Evidence model abstraction.** Study 1's T1 manipulation was omission/reduction of selected policy-visible fields rather than a factorial study of stale, contradictory, forged, or probabilistically corrupted evidence. Trusted recovery was separately defined by a frozen evidence checklist containing currentness, integrity, authorization, state-convergence, telemetry, and health requirements. These controls are not equivalent to flight certification or comprehensive operational attestation.

**Administrative censoring.** M04/M05 used a 30-s frozen analysis horizon. Runs without observed events were right-censored rather than imputed. RMST conclusions are therefore specific to this horizon.

**Safety-invariant structural zero.** No M03 violations occurred in the 720 VALID runs. This prevents meaningful estimation of differential violation risk and should not be interpreted as proof that the policies cannot violate safety constraints under broader conditions.

**Execution provenance.** Ten VALID observations were executed on two earlier runtime-orchestration/finalization commits. The analytical-exchangeability review and 29-seed final-commit complete-block sensitivity found no scientific-core difference or P5 relation change, but the versioned execution history remains a reproducibility consideration and is reported rather than hidden.

**No human/operator study.** Human cognition, workload, trust, decision latency, and operational approval behavior were not measured. The ground-authorization mechanism is synthetic and cannot support conclusions about operator performance.

## 5.9 Future research program

The current 720-observation campaign should remain frozen. Additional evidence should be generated under separately specified Study 2/Study 3 protocols rather than appended post hoc to Study 1.

**Study 2 — secure response under partial/adversarial observation.** A higher-bar security study should independently vary evidence omission, staleness, contradiction, and manipulation; expand modeled connectivity from the current C0/C1 contrast to several outage/intermittency regimes; introduce matched benign-fault versus adversarial evidence-loss conditions; ablate mission/evidence/contact inputs from the rule-based selector; compare against interpretable fail-closed, fail-operational, and risk-threshold baselines; and add formal assurance of response/recovery invariants. This study is intended as a generalization/methodology contribution suitable for IEEE TDSC or ACM TOPS, not as extra observations for the current paper.

**Study 3 — aerospace-system validation.** A separate engineering-validation phase should add simulated orbital/access schedules, mission-phase profiles, flight-like CPU/memory/command/telemetry measurements, and a limited RF-free hardware-in-the-loop configuration using cFS with simulated sensors/actuators and a software-only ground link. Its purpose would be implementation/performance transfer for IEEE TAES or AIAA JAIS, not flight qualification or certification.

The key research-program rule is separation: each follow-on study should have its own frozen design, estimands, seed policy, provenance, and archive. A larger number of observations is valuable only when it answers a new validity/generalization question rather than repeating the current cells for publication optics.

## 5.10 Overall interpretation

The study supports a bounded view of mission-aware satellite cyber response. Context-sensitive deterministic selection can improve response/recovery trade-offs when it avoids an ineffective baseline or a modeled authorization delay, but contextual selection is not inherently beneficial. Reduced policy-visible evidence can redirect the implemented selector into a pathway with worse mission or recovery outcomes, and fixed policies can be preferable in some conditions.

The strongest empirical contribution is therefore not a universal policy recommendation. It is evidence that satellite cyber-response and trusted-recovery mechanisms should be evaluated under explicit mission, contact, and evidence constraints using separate security and mission outcomes, with negative cases and recovery evidence retained. Within the controlled environment studied here, contact availability and evidence sufficiency materially shaped several response/recovery outcomes, while the predeclared mission-state effect was not demonstrated.

That combination of supported, null, adverse, and conditional findings provides a more credible basis for further spacecraft cyber-resilience research than a single-policy superiority claim.
