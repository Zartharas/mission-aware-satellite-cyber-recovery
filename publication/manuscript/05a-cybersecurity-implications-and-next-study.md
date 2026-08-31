# 5A. Cybersecurity Implications and Research Extension

## 5A.1 Practical cybersecurity interpretation

The retained results are most useful when interpreted as evidence about **security decision architecture** rather than as a ranking of individual response mechanisms. P2 shows that authorization topology can become a measurable cyber-recovery dependency: when response is gated on modeled ground authorization, loss of contact propagates into containment, recovery, and state-divergence delay. P3/P4 show that the evidence plane is itself part of the attack surface of an adaptive response system: changing the information available to the selector can change the effective policy/action and therefore the resulting mission and recovery consequences. P5 shows why response evaluation should preserve multiple security/dependability objectives rather than collapse them into a single score.

For practitioners, the experiment suggests that spacecraft cyber-response architecture reviews should explicitly identify at least four dependency classes:

1. **authorization dependencies** — which actions require remote approval and what happens when that approval path is unavailable;
2. **evidence dependencies** — which telemetry, attestation, integrity, or authorization observations must remain current for a response/recovery decision;
3. **availability dependencies** — what mission or legitimate-command functionality is sacrificed by containment or fallback behavior;
4. **recovery-assurance dependencies** — what evidence must be re-established before an apparently operational spacecraft is declared trusted.

These dependencies are design-review targets, not operational prescriptions. The controlled study does not establish the correct thresholds for a flight mission, but it shows that leaving these dependencies implicit can hide important trade-offs.

## 5A.2 Relationship to conventional incident response

NIST SP 800-61 Rev. 3 treats cybersecurity incident response as a risk-management capability spanning preparation, detection, response, and recovery [@nist80061r3]. The experiment deliberately narrows that lifecycle to the response/recovery decision once a modeled event has been established. Within that boundary, the results reinforce two mainstream incident-response principles in a spacecraft-specific setting.

First, containment and recovery should be treated as distinct objectives. A response can reduce an immediate unauthorized effect while leaving the system unavailable, unverified, or dependent on evidence that is incomplete or insufficient under the frozen recovery criteria. Second, recovery should restore trustworthy operation rather than merely observable functionality. The frozen `TRUSTED_RECOVERY_CONFIRMED` criteria make this distinction explicit by requiring software/configuration identity, integrity/authorization evidence, current state evidence, command authority, telemetry, state agreement, health, and absence of modeled residual unauthorized state.

This mapping increases transferability to mainstream cybersecurity without implying that the laboratory experiment implements a complete organizational incident-response program.

## 5A.3 Why the evidence plane should be treated as an attackable dependency

Many autonomous or semi-autonomous defense concepts assume that state information supplied to the decision logic is trustworthy enough to support action selection. P3/P4 show why that assumption should be tested directly. Under the frozen E3/T1 condition, P7's policy-visible evidence became insufficient, the effective mechanism changed, and trusted recovery fell from 30/30 under full evidence to 0/30 under degraded evidence. In E1, degraded evidence redirected P7 toward the experimental safe-mode action and produced a mission/command-availability cost.

The important cybersecurity result is not that one particular fallback was “wrong.” The experiment intentionally lacks an objective runtime correctness oracle. The result is that **the implemented evidence treatment is causally upstream of security-response selection and its consequences in the tested architecture**. Future adaptive-response designs should therefore expose evidence provenance, freshness, contradiction, and sufficiency as explicit state variables rather than burying them inside an opaque decision function. Study 1 directly manipulated only the frozen full-versus-reduced/suppressed evidence conditions; freshness, contradiction, and deliberate value manipulation are proposed Study 2 factors rather than Study 1 observations.

## 5A.4 Follow-on research required for higher-bar security venues

The current 720-observation campaign should remain frozen. Additional research should be conducted as a separately preregistered/frozen study rather than appended post hoc to the existing statistical population.

A higher-bar follow-on study suitable for IEEE TDSC or ACM TOPS should focus on **generalization of secure response under partial/adversarial observation**. The highest-value additions are not additional repetitions of the same 24 cells, but new estimands that broaden attacker capability and system conditions.

### Evidence-degradation ladder

Replace the current binary full/reduced evidence treatment with separately controlled conditions such as:

- complete/current evidence;
- evidence omission;
- stale evidence;
- contradictory evidence sources;
- manipulated policy-visible state;
- authorization/evidence-path disruption.

This would determine whether the observed P3/P4 behavior is specific to one degradation mechanism or general across qualitatively different evidence failures.

### Contact-regime expansion

Replace the current C0/C1 binary treatment with multiple modeled connectivity regimes, for example immediate, short outage, medium outage, extended outage, and intermittent/flapping contact. The objective would be to estimate whether response/recovery cost is linear, thresholded, saturating, or policy-specific rather than merely demonstrating one missed-contact contrast.

### Fault/attack ambiguity

Introduce matched benign-fault and adversarial conditions that create similar observable symptoms, such as telemetry loss caused by a simulated fault versus deliberate evidence suppression. This would connect spacecraft FDIR and cybersecurity more directly and test whether response mechanisms remain safe and available when the cause of degraded evidence is ambiguous.

### Selector ablation

Evaluate the mission-aware selector with individual context dimensions removed: no-mission, no-evidence, no-contact, and security-only variants. This can test which context actually contributes useful decision information and may explain why mission state was null in P1 while evidence/contact were strong discriminators elsewhere.

### Stronger policy baselines

Add interpretable baselines such as fail-closed, fail-operational, and predefined risk-threshold policies. The objective would not be to create a universally optimal policy, but to establish whether contextual selection offers benefit beyond reasonable conservative or availability-preserving alternatives.

### Formal assurance

Model the response/recovery state machine in a formal verification framework and verify bounded properties such as:

- unauthorized state cannot be classified as trusted recovery;
- trusted recovery requires the frozen evidence preconditions;
- authorization-gated actions cannot execute before authorization;
- evidence-insufficient paths cannot bypass the defined fallback;
- every terminating response path reaches an explicitly defined terminal state.

A formal model combined with empirical SIL validation would shift the contribution from an application experiment toward a general dependable/secure-response methodology.

## 5A.5 Aerospace-system validation path

A separate engineering-validation phase could support IEEE TAES or AIAA JAIS by increasing system realism without using operational spacecraft or RF. Candidate extensions include:

- simulated orbital/access schedules rather than one abstract missed-contact interval;
- mission-phase profiles such as payload operations, eclipse/low-power, maneuver, update, and recovery;
- flight-like CPU, memory, command-processing, and telemetry-load measurements;
- a limited hardware-in-the-loop subset using a flight-like single-board computer, cFS, simulated sensors/actuators, and a software-only ground link.

The purpose of HIL would be to test implementation/performance transfer, not to claim flight qualification or certification.

## 5A.6 Research-program separation rule

The current paper and future studies should remain scientifically distinct:

- **Study 1 / current paper:** frozen 720-run comparative response/recovery experiment; primary target Computers & Security.
- **Study 2:** adversarial evidence/contact generalization, policy ablation, fault/attack ambiguity, stronger baselines, and formal assurance; primary target IEEE TDSC with ACM TOPS as a strong alternative.
- **Study 3:** orbital/contact realism, flight-like resource characterization, and HIL validation; target IEEE TAES or AIAA JAIS depending on the resulting center of gravity.

This separation prevents post-hoc inflation of the current dataset and allows each paper to make a genuinely distinct scholarly contribution.
