# Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance

## Abstract

Trusted cyber recovery for satellite systems can depend on policy-visible evidence whose authenticity, freshness, composition, or provenance remains acceptable even when research-only authorization or correctness differs. This paper reports three separately frozen deterministic studies of recovery qualification without pooling their populations. Study 3 evaluates 1,380 temporal trajectories and shows that affected post-signature-manipulated records are rejected, whereas false but validly signed evidence from a compromised trusted producer can persist or recur across continuous and synthetic intermittent-contact schedules; the design separately identifies ordinary pre-onset cache exposure. Study 4 evaluates 4,608 exact observations across 18 vote and synthetic provenance-domain rules. Provenance constraints delay systematic unsafe qualification for selected thresholds without always changing first failure, while some constraints produce earlier false-conservative rejection under benign producer loss and others produce no threshold effect. Study 6 evaluates 420 exact artifact-assurance observations. Composed assurance gates reduce the prespecified incorrect states that remain qualified from four of five under signature-only checking to one of five under the six-signal composite gate, while increasing sensitivity to benign assurance-signal unavailability. Across the three finite models, stronger trust composition closes specified failure pathways but does not automatically make policy-visible evidence equivalent to hidden or objective truth. The results characterize residual trust boundaries rather than a globally best recovery policy, producer-composition rule, or artifact gate.

**Index Terms:** Aerospace cybersecurity, cyber recovery, evidence qualification, trust management, software supply-chain assurance.

## I. Introduction

Cyber recovery in satellite systems can require trust decisions under conditions that differ from continuously connected terrestrial environments. Communication gaps can limit when evidence is refreshed or when a ground operator can intervene, while postlaunch physical access is constrained and mission continuity can remain important during cyber response [1]. These characteristics make recovery not only a restoration problem but also a qualification problem: before a policy permits a recovery path, it must determine whether the available runtime evidence, the sources producing that evidence, and the recovery artifact itself are sufficiently trustworthy for the modeled decision.

Space-specific research already frames these decisions in terms of internal trust boundaries and testable cyber-resilience requirements [2], [3], while SPARTA recognizes integrity-protected trusted recovery baselines and cyber-safe recovery concepts [4]. Remote-attestation architectures distinguish evidence from the policy that appraises it and treat freshness as an explicit concern [5], and current RATS work also studies composition across multiple Verifiers in complex attestation topologies [6]. Quorum systems formalize how trust and failure assumptions interact with the sets of participants required for a decision [7], [8], and recent satellite trusted-execution research has used Byzantine-tolerant endorsement quorums as part of its architecture [9]. Software-supply-chain mechanisms use signatures, hashes, provenance, controlled build processes, reproducibility, review, and release metadata to establish properties of software artifacts [10]-[12]. The present work does not introduce these mechanisms.

The unresolved systems question addressed here is narrower: **what residual trust boundary remains when a recovery-qualification policy relies on evidence that can satisfy its visible checks while differing from a research-only authorization or correctness state?** The answer depends on where the trust boundary is placed. Runtime evidence can be authentic and fresh but semantically false if the trusted producer itself is compromised. Multiple evidence producers can reduce dependence on one source, but the resulting boundary depends on vote count, assumed provenance diversity, and producer unavailability. Recovery-artifact assurance can close several integrity and process failures while still depending on a higher-level assumption about the correctness of the approved source.

This paper investigates those boundaries through three separately frozen deterministic studies. The studies do not form one integrated experiment and their populations are never pooled. Study 3 evaluates temporal recovery-evidence qualification over 1,380 trajectories under continuous and synthetic intermittent contact, truthful evidence, post-signature manipulation, and false but validly signed claims from a compromised trusted producer. Study 4 evaluates 4,608 exact rule-by-subset observations across 18 total-vote and synthetic provenance-domain rules under separate producer-compromise and benign producer-unavailability populations. Study 6 evaluates 420 exact observations across six recovery-artifact states, six assurance gates, and every subset of benign assurance-signal unavailability.

The three studies share one analytical structure without sharing a common statistical unit. A frozen qualification policy acts only on prespecified policy-visible evidence. The research design retains a hidden authorization state or objective artifact-correctness oracle that is not supplied to the policy. This separation permits the experiments to identify states in which visible evidence remains qualified while research-only truth is false, and, where prospectively defined, states in which stricter evidence requirements reject a true or correct condition under benign evidence loss. In this paper, the term **residual trust boundary** refers only to these remaining finite-model states and corresponding qualification boundaries. It is not a universal impossibility theorem or a claim about all spacecraft recovery architectures.

The research questions are:

**RQ1:** Under the frozen continuous and intermittent-contact schedules, how do truthful evidence, post-signature modification, and false but validly signed claims from a compromised trusted producer affect the duration and recurrence of false recovery qualification across the Study-3 policy semantics?

**RQ2:** When recovery authorization is supported by multiple modeled evidence producers, how do absolute vote thresholds and synthetic provenance-domain requirements change the first and systematic failure boundaries for unsafe qualification under producer compromise and false-conservative qualification under benign producer loss?

**RQ3:** When the recovery artifact is subjected to progressively composed assurance requirements, which prespecified incorrect artifact states remain qualified, and what benign qualification loss results when required assurance signals become unavailable?

A final systems-level question guides the synthesis: **how do these independently measured residual qualification boundaries relate across temporal runtime evidence, producer composition, and recovery-artifact assurance?** The synthesis is qualitative and mechanism based. It does not estimate a common treatment effect, pooled success rate, or end-to-end recovery probability.

The paper makes four bounded contributions.

1. **Temporal qualification boundary.** Study 3 exactly characterizes false qualification across the frozen onset, contact, persistence, and policy grid. It separates a short truthful pre-onset cache boundary from false qualification caused by a compromised trusted producer that continues to generate fresh and validly signed false evidence. The contrast with post-signature manipulation also distinguishes semantic trusted-producer failure from altered records whose signatures become invalid.

2. **Producer-composition boundary.** Study 4 provides an exhaustive first-versus-systematic failure map across 18 total-vote and synthetic provenance-domain rules. The results show when provenance requirements change which compromised subsets can qualify, when they delay systematic unsafe qualification, when they introduce earlier false-conservative rejection under benign producer loss, and when they have no additional threshold effect.

3. **Artifact-assurance boundary.** Study 6 maps the specific incorrect recovery-artifact states that survive signature, digest, provenance, reproduced-build, source-review, and composite gates. It also exhaustively quantifies rejection of the objectively correct baseline under benign assurance-signal unavailability, preserving the different residual state identities of gates with equal aggregate counts.

4. **Residual-boundary synthesis.** Across the three separately frozen studies, the manuscript shows that composing stronger trust evidence can close or narrow specified failure pathways without automatically making policy-visible evidence equivalent to hidden or objective truth. The synthesis identifies the residual trust assumption at each layer rather than ranking a universal best policy, producer-composition rule, or artifact gate.

Several results constrain stronger interpretations and are intentionally retained. In Study 3, the `B2` policy has structural-zero false qualification in the frozen persistent-`V5` cells, but the design does not support a claim of universal immunity or global superiority. The synthetic K4 schedule reduces modeled mean exposure for selected persistent-`V5` comparisons but does not establish that intermittent contact improves security. In Study 4, provenance diversity produces conditional and null effects rather than a monotonic benefit, and the safety and benign-unavailability blocks are separate. In Study 6, the six-signal composite gate still qualifies `APPROVED_BAD_SOURCE`, while stronger gates become increasingly sensitive to benign assurance-signal loss. These results are central because they show where each visible trust mechanism stops adding discrimination within its frozen model.

The manuscript is also deliberately bounded in its aerospace interpretation. Only Study 3 directly models contact, and its logical seconds are not converted to orbital, network, processor, or operator time. Study 4's producer unavailability is not spacecraft contact loss or mission availability. Study 6's assurance-signal unavailability is not contact loss, and its Boolean variables do not represent an operational software-supply-chain compromise. None of the studies measures flight safety, RF performance, mission availability, energy, CPU, thermal behavior, or operational recovery probability.

The remainder of the paper is organized as follows. Section II positions the work relative to spacecraft cybersecurity, remote attestation and freshness, quorum trust, and software-supply-chain assurance. Section III defines the common trust-qualification abstraction while preserving study separation. Sections IV, V, and VI present the temporal evidence, producer-composition, and recovery-artifact studies, respectively. Section VII synthesizes their residual trust boundaries without pooling outcomes. Section VIII discusses validity, aerospace interpretation limits, reproducibility, and future evaluation. Section IX concludes.

## II. Related Work and Scientific Positioning

### A. Space Cybersecurity and Recovery Context

Spacecraft cybersecurity is shaped by operating constraints that can make evidence collection, human intervention, and recovery qualitatively different from continuously connected terrestrial systems. Thummala, Rice, and Falco identify communication gaps, permanent loss of physical access after launch, tight subsystem coupling, and mission-continuity requirements as interacting characteristics of the space-security problem [1]. Their argument is important here because it motivates recovery decisions that may need to be made from incomplete or intermittently refreshed evidence. It does not, however, imply that any particular contact schedule used in this paper is an orbital or ground-station visibility model.

Recent work also emphasizes that trust boundaries inside satellite flight software can be weak even when components operate through legitimate interfaces. Vanlyssel et al. analyze cFS and other modular flight-software frameworks and show how a compromised onboard component can abuse authority that is architecturally available to trusted peers [2]. Curbo and Falco similarly argue for testable, secure-by-design flight-software requirements that make cyber-resilience properties explicit rather than treating security as an untestable global property [3]. These studies reinforce a systems question that is central to cyber recovery: which evidence and authority relationships should a recovery mechanism trust when a component, producer, or software artifact may remain syntactically valid while its semantic trustworthiness has changed?

Space-specific guidance already recognizes the need for controlled recovery baselines. The Aerospace Corporation's SPARTA material describes cyber-safe recovery from an integrity-protected and validated software and configuration baseline, together with authenticated and integrity-verified maintenance of recoverable trusted versions [4]. The present work therefore does not claim that trusted recovery baselines, cyber-safe mode, or integrity-protected recovery are new concepts. Instead, it examines narrower qualification questions that arise before a policy treats runtime evidence, producer agreement, or a recovery artifact as sufficiently trustworthy.

### B. Evidence Appraisal, Freshness, and Policy-Visible Trust

The IETF Remote ATtestation procedureS architecture provides a mature vocabulary for evidence-based trust decisions. RFC 9334 distinguishes an Attester that produces Evidence, a Verifier that appraises Evidence under an appraisal policy, and a Relying Party that consumes Attestation Results to make application-specific decisions [5]. It also treats freshness as an explicit appraisal concern. Freshness can bound how old evidence is relative to the policy's tolerance, but it cannot guarantee instantaneous synchronization with a state that may change immediately after evidence is generated [5].

That distinction matters for Study 3. A record may be authentic and still fresh under the policy while no longer matching the research-only authorization truth. Conversely, a compromised trusted producer can generate a false claim that remains both fresh and cryptographically valid. The contribution of Study 3 is therefore not the observation that freshness matters or that signatures authenticate origin. Its contribution is the exact temporal characterization of the remaining false-qualification exposure across the frozen onset, contact, persistence, and policy grid, including prespecified separation of ordinary pre-onset cache exposure from false evidence generated by the compromised trusted producer.

Current RATS work also considers complex attestation topologies. The 2026 RATS Working Group draft on multiple Verifiers describes hierarchical, cascaded, and hybrid patterns in which different Verifiers appraise portions of a composite system and coordinate partial Evidence or partial Attestation Results [6]. This is related to the broader problem of composing trust evidence, but it is not the mechanism evaluated by Study 4. Study 4 does not distribute appraisal across multiple Verifiers. It models seven evidence producers whose visible claims are evaluated by a recovery-qualification rule requiring an absolute vote threshold and, for selected rules, a minimum number of synthetic provenance domains. The distinction between evidence producers and evidence Verifiers is maintained throughout this paper.

### C. Quorum Trust and Producer Composition

Quorum systems are established foundations for fault-tolerant distributed computing. Malkhi and Reiter formalized Byzantine quorum systems that preserve consistency and availability under arbitrary repository failures [7]. More recent work extends quorum reasoning to asymmetric or subjective trust assumptions in which participants can hold different fail-prone assumptions [8]. These results establish that quorum structure, fault assumptions, consistency, and availability tradeoffs are not new contributions of this paper.

Satellite-specific work further narrows the novelty boundary. Space Fabric uses a Byzantine-tolerant endorsement quorum of distributed ground stations and diversified secure elements as part of a satellite-enhanced trusted-execution and attestation architecture [9]. Thus, combining satellite systems with quorum endorsement or diversified trust anchors is also not, by itself, a novel contribution of Study 4.

Study 4 asks a more limited recovery-qualification question. Given a fixed registered set of seven modeled evidence producers assigned to three synthetic provenance domains, it exhaustively evaluates every producer subset under 18 prespecified total-vote and provenance-domain rules. The experiment records both the first affected-producer count at which a qualification failure becomes possible and the affected-producer count at which failure becomes systematic across all subsets of that size. It evaluates malicious producer compromise and benign producer unavailability in separate exhaustive blocks. The resulting contribution is an exact threshold map for this finite recovery-evidence model, including conditions in which provenance diversity changes systematic failure without changing first failure, and conditions in which provenance requirements have no additional effect. The model is not a Byzantine consensus protocol, does not establish real organizational or hardware independence, and does not estimate compromise or outage probabilities.

### D. Artifact Provenance and Software Supply-Chain Assurance

Software-supply-chain security already provides several mechanisms relevant to recovery-artifact qualification. in-toto uses cryptographically verifiable metadata to provide evidence about the sequence of steps used to produce software [10]. The Update Framework uses trusted roles, signed metadata, cryptographic hashes, expiration, versioning, and configurable signature thresholds to secure software update distribution and limit the effects of key compromise [11]. SLSA defines source and build assurance requirements intended to increase confidence that software was created through expected, auditable processes [12]. These mechanisms establish provenance, target binding, controlled build processes, and authenticated release metadata as prior art.

The current SLSA v1.2 threat model is especially relevant to the interpretation of Study 6. SLSA explicitly states that an intentionally malicious software producer cannot be directly mitigated by SLSA controls alone and that consumers need some independent basis for trusting the producer [12]. Therefore, Study 6's `APPROVED_BAD_SOURCE` state must not be presented as the discovery that provenance or process compliance cannot prove benevolent source intent. That limitation is already recognized in contemporary supply-chain assurance.

Study 6 instead provides an exact residual-state map for a frozen six-state, six-gate artifact model. It asks which prespecified incorrect recovery-artifact states remain qualified as signature, digest, provenance, reproduced-build, source-review, and approval signals are composed, and it separately enumerates the benign qualification loss produced when required assurance signals become unavailable. Equal aggregate counts are preserved when different gates leave different residual states. The resulting contribution is not a new provenance mechanism. It is a finite characterization of which modeled trust assumptions each gate closes and which assumption remains outside the gate's observability.

### E. Scientific Positioning and Gap Addressed

The literature reviewed above establishes the main primitives that appear in this paper. Space cybersecurity already treats communication gaps, autonomy, continuity, trusted baselines, and internal trust boundaries as important concerns [1]-[4]. RATS already formalizes Evidence, appraisal, Relying Parties, and freshness [5], [6]. Distributed-systems research already formalizes quorum trust and availability relationships [7], [8], and current satellite trust architectures already use endorsement quorums [9]. Software-supply-chain research already provides provenance, signed update metadata, target binding, reproducible-process concepts, and explicit limits on what those controls can establish about producer intent [10]-[12].

Accordingly, this paper does not claim novelty for any of those individual mechanisms. Its contribution is the exact characterization of three distinct residual recovery-qualification boundaries under separately frozen finite models. Study 3 isolates temporal evidence validity and trusted-producer semantics under a frozen continuous or intermittent-contact schedule. Study 4 isolates producer-count and synthetic provenance-domain composition under exhaustive compromise and benign-unavailability subsets. Study 6 isolates recovery-artifact assurance composition under prespecified incorrect states and exhaustive benign assurance-signal loss.

In the reviewed literature, we did not identify a directly matching spacecraft cyber-recovery study that reports these three residual qualification perspectives as separately frozen experiments while preserving their distinct populations and then synthesizes them without pooling. That observation is a literature-positioning statement, not a priority claim. The paper's systems contribution is therefore a bounded residual-trust interpretation: adding or composing trusted evidence can move a qualification boundary and close specified failure pathways, but the remaining boundary depends on what the policy can observe and what trust assumptions are left outside that observation set.

## III. Common Trust-Qualification Framework and Study Separation

### A. Policy-Visible Evidence and Research-Only Truth

The three studies use different mechanisms, but they share one analytical structure. A qualification policy acts only on a prespecified set of visible evidence. The research design separately retains a hidden or objective adjudication variable that is not available to the policy. This separation allows the experiment to determine when policy-visible evidence supports qualification even though the research-only truth says that qualification is incorrect.

For study `j`, let `E_j` denote the vector of policy-visible evidence and let

`Q_j(E_j) in {0,1}`

represent the frozen qualification decision, where `1` means that the modeled recovery evidence or artifact satisfies the study-specific gate. Let `T_j in {0,1}` denote the corresponding research-only adjudication state, where `1` means that the hidden authorization state or objective artifact correctness supports qualification. `T_j` is used for evaluation only and is never supplied to `Q_j`.

The generic unsafe-qualification condition is therefore

`U_j = 1[Q_j(E_j) = 1 and T_j = 0]`.

Where a study separately evaluates benign evidence loss, the complementary false-conservative condition is

`C_j = 1[Q_j(E_j) = 0 and T_j = 1]`.

These expressions are a manuscript-level abstraction, not new experimental endpoints. Each study retains its own frozen endpoint definitions, units, state space, and reporting rules. In Study 3, for example, unsafe qualification is evaluated across temporal epochs and summarized at the trajectory level, whereas Study 4 evaluates exact producer subsets and Study 6 evaluates exact artifact states and assurance-signal subsets.

Within this paper, a **residual trust boundary** means the remaining set of frozen modeled states for which the visible evidence satisfies the qualification rule while the research-only adjudication state is false, together with the study-specific boundary at which stricter visible-evidence requirements begin producing false-conservative rejection under benign evidence loss. This is a descriptive term for the finite experiments. It is not an impossibility theorem, a universal security boundary, or a claim about all spacecraft recovery architectures.

### B. Study-Specific Realizations of the Common Structure

Table I summarizes how the common abstraction is instantiated without merging the studies.

| Study | Qualification layer | Research-only adjudication | Principal policy-visible evidence | Frozen population | Contact model |
|---|---|---|---|---:|---|
| Study 3, `S3-K4E-001` | Temporal runtime evidence | Hidden authorization truth | Signature validity, trusted source semantics, freshness, epoch/contact-dependent record availability, security signal | 1,380 trajectories | Yes, K0 and synthetic K4 |
| Study 4, `S4-MPQ-001` | Producer composition | Hidden authorization truth | Signed producer claims, total-vote threshold, synthetic provenance-domain count | 4,608 exact rule-by-subset observations | No |
| Study 6, `S6-SCTR-001` | Recovery-artifact assurance | Objective baseline correctness | Signature, independent target digest, provenance, independent reproduced build, source-review attestation, release approval | 420 exact observations | No |

Only Study 3 directly models intermittent contact. Study 4 producer unavailability and Study 6 assurance-signal unavailability are different abstractions and are not interpreted as contact loss, orbital visibility, or mission availability.

#### 1) Study 3: temporal evidence qualification

Study 3 uses deterministic logical time with a 240-logical-second horizon, five-logical-second epochs, and five-logical-second evidence validity. The complete onset grid contains 46 onset phases from 10 through 235 logical seconds. K0 provides continuous modeled contact over the horizon. K4 is a frozen synthetic flapping-contact schedule with windows `[25,35]`, `[75,90]`, `[145,165]`, and `[220,240]` logical seconds. These windows are model inputs, not orbital passes.

The hidden authorization state is true before onset and false at and after onset. The selector cannot observe this hidden truth. The visible evidence treatments distinguish truthful current authorization evidence (`V0`), post-signature value manipulation with an invalid signature (`V4`), and a compromised trusted producer that validly signs a false authorization claim (`V5`). `V4` and `V5` are evaluated under one-shot and persistent modes. The frozen matrix contains 30 cells and 1,380 trajectories. Its 67,620 epoch states are repeated states within trajectories and are not independent statistical observations.

The design also prespecifies the origin of false qualification. `PRE_ONSET_CACHE` identifies a still-fresh truthful record generated before hidden authorization changed. `V5_AFFECTED_RECORD` identifies false qualification associated with a validly signed false record from the compromised trusted producer. This decomposition is central to the paper because it separates ordinary freshness lag from adversarial semantic falsity.

#### 2) Study 4: multi-producer qualification

Study 4 uses seven modeled evidence producers assigned to three synthetic provenance domains: `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. Eighteen qualification rules combine total vote thresholds from one through seven with a required domain count from one through `min(3,q)`. The denominator is the registered producer set, not the set of responders.

The safety block sets hidden authorization false. Compromised producers emit a visible `true` claim with a valid signature, honest producers emit `false`, and all producers are available. The benign availability block sets hidden authorization true. Affected producers are unavailable, all available claims are true and validly signed, and no producer is malicious. These blocks are evaluated separately. The design does not model simultaneous malicious compromise and benign producer loss.

Every one of the 128 producer subsets is evaluated for every rule in each block, yielding `18 x 2 x 128 = 4,608` exact observations. The primary study-specific endpoints are `unsafe_qualified` and `false_conservative`. The main summaries are the first affected-producer count at which a failure exists, the affected-producer count at which failure is systematic across all subsets of that size, and the exact subset failure rate by affected-producer count. Because the population is exhaustive, subset fractions describe the finite state space and are not probabilities of operational compromise or outage.

#### 3) Study 6: recovery-artifact assurance

Study 6 evaluates six prespecified artifact states against six assurance gates. `CLEAN_APPROVED` is objectively correct and has all six visible assurance signals true. Five additional states are objectively incorrect: `POST_RELEASE_TAMPER`, `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`. Objective correctness is a research-only oracle and is never an input to a gate.

The visible signals are signature validity, independent target-digest match, provenance validity, independent reproduced-build match, source-review attestation, and release approval. The gates range from `G0_SIGNATURE_ONLY` to `G5_COMPOSITE`, which requires all six visible signals. The adversarial-baseline block contains all six artifact states crossed with all six gates, for 36 observations. A separate benign-unavailability block uses the objectively correct baseline and exhausts all 64 subsets of unavailable assurance signals across all six gates, for 384 observations. The total frozen population is therefore 420 exact observations.

The model does not implement malware, a real build compromise, real signing keys, or an operational spacecraft supply chain. Terms such as "independent digest" and "independent reproduced build" identify modeled assurance variables, not proof that independent organizations or infrastructure were deployed.

### C. Exact Finite Populations and Non-Pooling Rule

All three studies are deterministic finite experiments. None is treated as a random sample from an operational population. Study 3 exhausts its frozen onset-phase grid. Study 4 exhausts every affected-producer subset for every registered quorum/provenance rule in each of two separately defined blocks. Study 6 exhausts its prespecified artifact states and all subsets of assurance-signal unavailability.

The populations are therefore reported separately:

- Study 3: 1,380 deterministic trajectories;
- Study 4: 4,608 exact rule-by-subset observations;
- Study 6: 420 exact artifact-state and assurance-unavailability observations.

There is no pooled Paper-2 statistical population. Because the units, interventions, outcome definitions, and state spaces differ, the three counts are not summed or reported as a manuscript sample size. No pooled success rate, pooled confidence interval, pooled p-value, or global policy ranking is defined.

This rule also constrains the cross-study synthesis. Section VII will compare mechanisms and residual boundaries qualitatively. It will not estimate a common treatment effect or an end-to-end recovery probability.

### D. Qualification Is Not Recovery Completion

The unit of analysis throughout the paper is qualification evidence, not completed spacecraft recovery. A gate can be permissive or qualified in the model without establishing that a recovery action was executed successfully, restored mission capability, or produced a safe operational spacecraft state. Study 3's `unsafe_permissive` metric is specifically a selector or gate-entry action metric. Its stronger `unsafe_qualified` endpoint means that the recovery gate remains policy-visible qualified while hidden authorization truth is false.

Similarly, Study 4's safety terminology refers to resistance to unsafe qualification in the finite model, not spacecraft physical safety. Its availability terminology refers to false-conservative rejection under modeled benign producer unavailability, not mission availability. Study 6's benign assurance-unavailability endpoint refers to rejection caused by missing modeled assurance signals, not contact loss or operational service availability.

These distinctions are maintained because translating the modeled quantities into flight safety, mission availability, contact opportunity, recovery latency, RF performance, or operator workload would require evidence that the frozen studies did not collect.

### E. Frozen Provenance and Reproducibility Controls

Each study was executed from a frozen design and bound to repository provenance. Study 3's canonical campaign contains 30 cells, 1,380 trajectories, and 67,620 epoch states. Its independent auditor reported zero trajectory, epoch-rule, false-qualification-origin, and SHA mismatches. Study 4's 4,608-observation exact population was independently reconstructed with zero observation and threshold mismatches. Study 6's accepted execution was independently audited with zero mismatches, matching frozen output hashes and no tracked-file drift.

These audits support reproducibility of the frozen repository experiments. They are not external empirical replication because the independent implementations and audits remain within the same research repository and program. The manuscript therefore uses "independent audit," "independent reconstruction," or "same-repository reproducibility" rather than "external replication."

### F. Cross-Study Interpretation Rule

The common framework permits one bounded synthesis. In each study, qualification is constrained by what the policy can observe. Study 3 can verify signature validity and freshness but cannot directly observe the hidden semantic truth of a compromised trusted producer's claim. Study 4 can require more votes and more synthetic provenance domains, but its result remains conditional on which producer subsets satisfy those visible structural requirements. Study 6 can compose increasingly demanding artifact-assurance signals, but a state in which all six visible signals are true remains qualified even when the research-only objective correctness oracle is false.

The resulting systems interpretation is not that stronger qualification fails, nor that more evidence is undesirable. Stronger composition closes specific modeled failure pathways in each study. The narrower conclusion is that the residual boundary moves with the evidence structure and with the assumptions that remain outside the gate's observation set. The following sections evaluate those movements separately before any cross-study synthesis is made.

## IV. Temporal Evidence Qualification Under Intermittent Contact

### A. Study Question and Design

Study 3 (`S3-K4E-001`) evaluates when runtime recovery evidence remains policy-qualified after the research-only authorization state has changed. The experiment isolates three factors that can affect that boundary: contact availability, the semantic condition of the received authorization evidence, and whether an affected record appears once or persists across later receptions. The study is deterministic and uses logical model time rather than wall-clock or flight time.

The horizon is 240 logical seconds, evaluated in five-logical-second epochs. Evidence remains fresh for five logical seconds. The complete onset grid contains 46 prespecified authorization-change phases from 10 through 235 logical seconds in five-second increments. Before onset, hidden authorization truth is `true`. At and after onset, hidden authorization truth is `false`, and the security signal is `true`. The selector never receives hidden authorization truth as an input.

Two contact regimes are evaluated. `K0` provides continuous modeled contact from 0 through 240 logical seconds. `K4` provides the frozen synthetic contact windows `[25,35]`, `[75,90]`, `[145,165]`, and `[220,240]`. New records are received only during modeled contact, and outside contact the selector can use only the latest previously received record subject to the frozen freshness rule. K4 is therefore a deterministic flapping-contact treatment. It is not an orbital pass schedule or an estimate of operational access.

The evidence treatments are:

1. `V0`, truthful current authorization evidence. A post-onset received record reports authorization `false` and carries a valid signature.
2. `V4`, post-signature value manipulation. The post-onset authorization value is changed from `false` to `true` after signing, which makes the signature invalid.
3. `V5`, compromised trusted-producer evidence. The producer emits authorization `true` while hidden truth is `false`, but the false claim is validly signed by the trusted producer.

`V4` and `V5` are each evaluated under one-shot and persistent modes. A one-shot treatment affects the first received post-onset record and later received records return to truthful behavior. A persistent treatment affects every received post-onset record. `V0` has no persistence treatment because its records remain truthful.

Three frozen policy semantics are evaluated: `S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`. These identifiers are retained because Study 3 reuses the frozen selector semantics, but no Study-2 statistical result is imported into the present analysis. The Study-3 population is defined solely by the Study-3 protocol and execution.

The resulting matrix contains 30 cells and 46 onset trajectories per cell, for 1,380 deterministic trajectories. Across those trajectories the execution records 67,620 epoch states. The trajectory is the study unit. Epochs within a trajectory are repeated model states and are not treated as independent observations.

### B. Endpoints and Origin Decomposition

The frozen primary endpoints are `unsafe_permissive_epoch_rate`, `unsafe_qualified_epoch_rate`, `unsafe_qualified_exposure_s`, `unsafe_qualified_episode_count`, `protective_epoch_rate`, and `action_transition_count`. This paper emphasizes `unsafe_qualified` because it is the stronger qualification endpoint. It indicates that the recovery gate is policy-visible qualified while the research-only hidden authorization state is false. `unsafe_permissive` is only a selector or gate-entry action metric and is not evidence that a recovery action was completed.

The design also prespecifies two allowed origins for false qualification. `PRE_ONSET_CACHE` denotes a truthful record received before the authorization change that remains policy-fresh for a later epoch. `V5_AFFECTED_RECORD` denotes a validly signed false record generated by the compromised trusted producer. A Study-3 false-qualified epoch must map to one of these declared origins. This decomposition prevents ordinary freshness lag from being counted as adversarial semantic falsity.

Because the onset grid is complete for the frozen design, results are reported as exact finite-grid summaries and paired phase differences rather than sampling estimates. There is no p-value gate, weighted policy score, or global policy rank.

### C. Persistent False-but-Valid Evidence Under Continuous Contact

Persistent `V5` produces the clearest semantic trust boundary. Under continuous `K0` contact, both `B0` and `S1` were unsafe-qualified in all 46 onset trajectories. Mean unsafe-qualified exposure was 122.5 logical seconds for each policy. In contrast, `B2` remained at 0 of 46 trajectories with mean unsafe-qualified exposure of zero in this frozen cell.

The important distinction is not that a signature was broken. The `V5` records are validly signed. The mismatch arises because the trusted producer itself is modeled as compromised and therefore signs a claim that is false relative to hidden authorization truth. Signature validity authenticates the modeled producer and record integrity, but it does not expose the research-only semantic falsity of a claim that the trusted producer is itself willing to sign.

The `B2` structural zero is preserved as a study result but is not interpreted as universal immunity or global superiority. It follows from the frozen policy semantics and treatment grid. The study does not define a weighted objective that would justify ranking `B2` as the best policy across recovery goals.

### D. Persistent V5 Under the Frozen K4 Contact Schedule

Intermittent `K4` contact changes the duration of exposure but does not eliminate the persistent `V5` boundary for the two gate-entering policies. `B0` remained unsafe-qualified in 46 of 46 onset trajectories with mean exposure of 55.326 logical seconds. `S1` also remained unsafe-qualified in 46 of 46 trajectories with mean exposure of 49.022 logical seconds. Relative to their truthful `V0` controls, the corresponding `V5`-attributable mean increments were 55.0 and 49.022 logical seconds. `B2` remained 0 of 46.

The difference between `B0` and `S1` under persistent `V5/K4` was approximately 6.304 logical seconds of mean unsafe-qualified exposure. The frozen `S1` contact-aware restriction therefore adds a boundary relative to `B0`, but it does not make `S1` immune. During modeled contact windows the compromised producer can continue supplying fresh, validly signed false evidence that satisfies the policy-visible evidence requirements.

This result must not be reversed into the claim that intermittent contact improves security. K4 mechanically limits when new records can be received and thereby changes exposure under the frozen cache and contact semantics. The study supports the narrower statement that the specified K4 schedule reduced modeled mean false-qualification exposure relative to K0 for the persistent `V5` cells while leaving the false-qualification condition present across the complete onset grid.

**Table II. Selected Study-3 residual-boundary results**

| Evidence / contact / policy | Unsafe-qualified trajectories | Mean unsafe-qualified exposure, logical s | Interpretation |
|---|---:|---:|---|
| Persistent `V5`, `K0`, `B0` | 46/46 | 122.500 | Sustained false qualification under continuous contact |
| Persistent `V5`, `K0`, `S1` | 46/46 | 122.500 | Same continuous-contact exposure in frozen grid |
| Persistent `V5`, `K0`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Persistent `V5`, `K4`, `B0` | 46/46 | 55.326 | Reduced modeled exposure, not elimination |
| Persistent `V5`, `K4`, `S1` | 46/46 | 49.022 | Additional K4 restriction relative to B0, not immunity |
| Persistent `V5`, `K4`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Truthful `V0`, `K4`, `B0` | 3/46 | 0.326 | Pre-onset cache boundary, not adversarial evidence |
| Truthful `V0`, `K4`, `S1` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |
| Truthful `V0`, `K4`, `B2` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |

The exposure values in Table II are logical model time. They are not spacecraft response time, communication latency, operator latency, or ground-contact duration.

### E. Post-Signature Manipulation and the Cryptographic Boundary

`V4` provides an important negative control against overinterpreting the `V5` result. Under `V4`, the authorization value is modified after signing, so the affected record has an invalid signature. The affected `V4` records never qualified. Persistent `V4` therefore adds no `V4`-attributable false qualification.

Any false qualification observed for `V4` under `B0/K4` is instead attributable to the same pre-onset cache mechanism present under truthful `V0`: a previously received truthful record can remain fresh for one post-onset epoch after hidden authorization has changed. The prespecified origin decomposition assigns those epochs to `PRE_ONSET_CACHE`, not to the manipulated `V4` record.

The contrast between `V4` and `V5` bounds the cryptographic interpretation. The study supports the claim that signature validation rejects the modeled post-signature alteration. It also supports the claim that a valid signature alone does not establish semantic truth when the trusted producer itself is the source of the false claim. It does not support a claim that cryptography in general failed or that the experiment performed cryptanalysis, key extraction, or a real signing-system attack.

### F. Freshness and the Truthful Cache Boundary

The truthful `V0/K4` control exposes a smaller nonadversarial boundary. Under `B0`, 3 of 46 onset trajectories contained unsafe qualification, with mean exposure of 0.326 logical seconds across the complete onset grid. The frozen origin decomposition attributes these epochs to `PRE_ONSET_CACHE`. A record generated while authorization was still true remains within the five-logical-second freshness threshold for a short interval after hidden authorization changes.

`S1` and `B2` had no truthful-`V0` false qualification under K4. The `B0` result is therefore schedule-, epoch-, freshness-, and policy-specific. It should not be interpreted as a general estimate of cache staleness in spacecraft systems. Its value in this study is methodological: it shows that false qualification can arise from an ordinary freshness boundary even when evidence is truthful, and it prevents that mechanism from being conflated with the stronger `V5` compromised-producer treatment.

This result is also consistent with the architectural limitation recognized by RFC 9334: evidence freshness can bound recentness without guaranteeing instantaneous synchronization to an underlying state change [5]. The present experiment quantifies that issue only for the frozen five-second epoch and validity semantics.

### G. One-Shot V5 and Temporal Persistence

The one-shot treatment separates a transient trusted-producer false claim from persistent compromise behavior. Under `K0`, one-shot `V5` produced mean unsafe-qualified exposure of five logical seconds for both `B0` and `S1` and affected all 46 onset phases. Under `K4`, all 46 `B0` and `S1` onset trajectories eventually received the one-shot compromised record; `S1` retained five logical seconds of `V5` exposure, while `B0` additionally contains the separately identified cache boundary.

The difference between one-shot and persistent `V5` is therefore temporal rather than cryptographic. Both treatments use a validly signed false claim from the trusted producer. Persistence determines whether the false claim is confined to one received record or renewed whenever post-onset contact permits another record to arrive. This is the main reason Study 3 is stronger than a static observation that a compromised signer can lie: the experiment characterizes how false-but-valid evidence persists or recurs under the frozen contact and cache semantics.

### H. Study-3 Residual Trust Boundary

Study 3 exposes two distinct residual boundaries. The smaller boundary is ordinary freshness lag: a truthful pre-onset record can remain qualified briefly after hidden authorization changes. The stronger boundary appears when the trusted producer itself is compromised: fresh and validly signed evidence can continue satisfying the gate while being false relative to hidden truth. Contact-aware restrictions reduce exposure in selected K4 comparisons, but do not eliminate that second boundary for `B0` or `S1` under persistent `V5`.

These findings are exact properties of the frozen deterministic grid. They do not estimate the prevalence of producer compromise, the probability of unsafe recovery, or operational mission risk. Logical time is not converted into orbit, RF, network, or operator time. The next study removes the temporal contact mechanism entirely and asks a different question: how the qualification boundary changes when trust is composed across multiple modeled evidence producers and synthetic provenance domains.

## V. Multi-Producer Qualification and Provenance-Domain Constraints

### A. Study Question and Exact Population

Study 4 (`S4-MPQ-001`) evaluates how recovery qualification changes when evidence is supplied by multiple modeled producers rather than by a single producer. The study asks two separate questions. First, how many compromised producers are required before false authorization can satisfy a qualification rule? Second, how many benign producer losses can occur before a true authorization state is rejected conservatively? The experiment varies both absolute vote count and a synthetic provenance-domain requirement.

Seven modeled producers, `P1` through `P7`, are assigned to three frozen provenance domains: `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. These domains are synthetic independence classes. They do not establish that the modeled producers correspond to independent organizations, hardware, software stacks, supply chains, or operators.

A qualification rule is denoted `Qq_Dd`, where `q` is the required number of qualifying producer claims and `d` is the required number of represented provenance domains. Total-vote thresholds range from one through seven. The domain threshold ranges from one through `min(3,q)`, producing 18 prespecified rules. The denominator is always the registered seven-producer set, not the number of producers that happen to respond.

The study contains two separate exhaustive blocks. In the **safety block**, hidden authorization truth is false, all producers are available, compromised producers emit a visible authorization-true claim with a valid signature, and honest producers emit authorization false. The endpoint `unsafe_qualified` is true when the compromised subset satisfies the rule despite hidden authorization being false.

In the **benign availability block**, hidden authorization truth is true, affected producers are unavailable, all available producers emit a true claim with valid signatures, and no producer is malicious. The endpoint `false_conservative` is true when the rule rejects the true authorization state because too few producers or provenance domains remain available.

Every subset of the seven producers is evaluated. There are 128 subsets per block per rule. The complete population is therefore `18 x 2 x 128 = 4,608` exact observations. The compromise and benign-unavailability blocks are not combined, and the study does not evaluate simultaneous malicious compromise plus benign producer loss.

### B. First and Systematic Failure Definitions

For each rule and block, the analysis records two thresholds.

The **first failure count** is the smallest number of affected producers for which at least one subset of that size causes the endpoint to fail. It identifies when failure becomes possible.

The **systematic failure count** is the smallest number of affected producers for which every subset of that size causes failure. It identifies when failure becomes unavoidable within the frozen producer assignment.

The distinction is necessary whenever provenance diversity matters. A rule can first fail at a given compromised-producer count because one cross-domain subset satisfies the rule, while other same-size subsets remain blocked. The systematic threshold captures when subset composition no longer matters because every subset of that size crosses the boundary.

Because the study exhausts all subsets, these thresholds and subset proportions are finite combinatorial properties. They are not estimates of operational compromise probability, outage probability, or mission availability.

### C. Exact Threshold Map

Table III reports the complete frozen threshold map. Safety entries are shown as `first/systematic` compromised-producer counts. Availability entries are shown as `first/systematic` unavailable-producer counts.

**Table III. Study-4 first and systematic failure thresholds**

| Rule | Unsafe qualification, compromised producers | False-conservative rejection, unavailable producers |
|---|---:|---:|
| `Q1_D1` | 1/1 | 7/7 |
| `Q2_D1` | 2/2 | 6/6 |
| `Q2_D2` | 2/4 | 4/6 |
| `Q3_D1` | 3/3 | 5/5 |
| `Q3_D2` | 3/4 | 4/5 |
| `Q3_D3` | 3/6 | 2/5 |
| `Q4_D1` | 4/4 | 4/4 |
| `Q4_D2` | 4/4 | 4/4 |
| `Q4_D3` | 4/6 | 2/4 |
| `Q5_D1` | 5/5 | 3/3 |
| `Q5_D2` | 5/5 | 3/3 |
| `Q5_D3` | 5/6 | 2/3 |
| `Q6_D1` | 6/6 | 2/2 |
| `Q6_D2` | 6/6 | 2/2 |
| `Q6_D3` | 6/6 | 2/2 |
| `Q7_D1` | 7/7 | 1/1 |
| `Q7_D2` | 7/7 | 1/1 |
| `Q7_D3` | 7/7 | 1/1 |

The table exposes two separate effects. Raising the absolute vote threshold increases the number of compromised producers required to qualify false authorization, but reduces tolerance to benign producer loss. Adding provenance-domain requirements can further delay systematic unsafe qualification for selected vote thresholds, but can also make false-conservative rejection possible after fewer unavailable producers.

### D. Absolute Vote Count Sets the Basic Compromise Boundary

Without an added provenance constraint beyond one represented domain, the safety threshold follows the absolute vote count directly. `Q1_D1` fails with one compromised producer, `Q2_D1` with two, `Q3_D1` with three, and so on through `Q7_D1`, which requires all seven producers to be compromised before false authorization qualifies.

The corresponding benign-unavailability boundary moves in the opposite direction. `Q1_D1` continues to qualify a true authorization state until all seven producers are unavailable. `Q4_D1` first and systematically fails after four producers are unavailable. `Q7_D1` becomes false-conservative after loss of any single producer. The finite model therefore exposes the expected tension between requiring more positive claims for resistance to compromise and requiring fewer unavailable producers for continued qualification.

This pattern is not presented as new quorum theory. Quorum safety and availability relationships are well established [7], [8]. The Study-4 contribution is the exact mapping of those structural effects onto the frozen recovery-evidence qualification problem, including the additional domain-composition rules and the distinction between first and systematic failure.

### E. Provenance Diversity Changes Systematic Failure Without Necessarily Changing First Failure

The clearest provenance effect appears at `Q3`. Under `Q3_D1`, three compromised producers are sufficient for both first and systematic unsafe qualification. Every three-producer compromise contains enough positive votes because no cross-domain requirement is imposed.

Under `Q3_D3`, the first unsafe qualification still occurs at three compromised producers, but only a three-producer subset spanning all three provenance domains can satisfy the rule. Same-domain or two-domain triples remain blocked. Systematic unsafe qualification does not occur until six of the seven producers are compromised. Thus the provenance requirement leaves the first possible failure count unchanged at three while moving systematic failure from three to six.

The same structural effect appears at `Q4_D3` and `Q5_D3`. `Q4_D3` first fails for unsafe qualification at four compromised producers but does not fail systematically until six. `Q5_D3` first fails at five and becomes systematic at six.

This distinction matters because a single threshold such as "fails at three" would obscure the subset dependence introduced by provenance composition. First and systematic counts are therefore reported together whenever interpretation depends on which provenance domains are represented in the affected subset.

### F. Provenance Diversity Also Creates Earlier Benign Rejection for Selected Rules

The stronger safety boundary carries a corresponding qualification-availability cost. Under `Q3_D1`, benign producer unavailability first causes false-conservative rejection at five unavailable producers and is systematic at five. Under `Q3_D3`, the first false-conservative failure occurs after only two unavailable producers because a subset can remove an entire provenance domain even while five producers remain. Systematic false-conservative rejection still occurs at five.

`Q4_D3` has the same qualitative pattern. `Q4_D1` first and systematically fails after four unavailable producers. `Q4_D3` can first fail after only two unavailable producers while becoming systematic at four. `Q5_D3` can also first fail after two unavailable producers, whereas `Q5_D1` first fails at three.

These results do not mean that provenance diversity reduces mission availability. The endpoint is narrower: under the frozen registered-producer denominator and domain assignment, selected benign producer-loss subsets can make the recovery-evidence gate reject a true authorization state earlier because the required diversity of visible evidence is no longer present.

### G. Null and Equal-Threshold Results

The provenance requirement does not always change the qualification boundary. These null results are important because they prevent a monotonic "more provenance is always better" interpretation.

At `Q4`, `Q4_D1` and `Q4_D2` have identical first and systematic thresholds in both blocks: safety 4/4 and benign availability 4/4. Requiring two domains adds no threshold effect under this particular producer allocation and vote requirement.

At `Q5`, `Q5_D1` and `Q5_D2` are also identical: safety 5/5 and benign availability 3/3. Again, the two-domain requirement does not alter the frozen thresholds.

At `Q6`, all three domain variants are identical. Safety fails at 6/6 and benign availability at 2/2 for `D1`, `D2`, and `D3`. At `Q7`, every domain variant is also identical at safety 7/7 and benign availability 1/1 because requiring all seven producers necessarily includes all three provenance domains.

These equal-threshold cases show that the effect of provenance constraints is conditional on the interaction among vote threshold, domain allocation, and affected subset composition. The experiment does not support the claim that increasing provenance-domain requirements universally improves resistance to unsafe qualification.

### H. The Q4 Boundary as a Symmetric Reference Case

`Q4_D1` provides a useful finite-model reference because the first and systematic thresholds are symmetric across the two separately evaluated blocks. Four compromised producers are required for unsafe qualification, and four unavailable producers cause false-conservative rejection. Adding a three-domain requirement in `Q4_D3` changes that structure: safety first failure remains four, systematic safety failure moves to six, benign availability first failure moves to two, and systematic availability failure remains four.

This comparison illustrates why a single vote threshold does not fully describe the qualification rule once provenance constraints are added. Absolute vote count establishes the base boundary, while provenance composition determines which same-size subsets can satisfy that boundary.

### I. High Vote Thresholds and the Loss-Tolerance Boundary

At high vote thresholds, compromise tolerance increases while benign loss tolerance becomes restrictive. `Q5_D1` requires five compromised producers for unsafe qualification but rejects true authorization after three producers become unavailable. `Q6` requires six compromised producers for unsafe qualification and becomes false-conservative after two unavailable producers. `Q7` requires all seven producers to be compromised before false authorization can qualify, but any single unavailable producer prevents qualification of the true state.

The finite grid therefore does not identify a globally best rule. A higher threshold can reduce the modeled unsafe-qualification region while increasing the modeled false-conservative region. The study contains no utility weights, operational failure probabilities, or mission costs that would justify collapsing those two objectives into a single score.

### J. Relationship to Distributed Trust Prior Art

The Study-4 model deliberately stops short of Byzantine consensus or distributed agreement. Producers do not run a protocol to reach agreement with one another. The model does not analyze message scheduling, leaders, forks, liveness, replicated state, network partitions, or Byzantine broadcast. Instead, a recovery gate receives modeled producer claims and applies a deterministic qualification rule.

The connection to quorum-system literature [7], [8] is therefore conceptual and structural. That literature establishes that fault assumptions and quorum structure govern consistency and availability properties in distributed systems. Study 4 uses a simpler finite qualification abstraction to ask how total vote count and synthetic provenance-domain composition affect one recovery-authorization decision boundary. Likewise, the existence of satellite architectures using endorsement quorums [9] means that satellite quorum trust itself is not claimed as novel.

### K. Study-4 Residual Trust Boundary

Study 4 shows that producer composition can move the residual qualification boundary without eliminating the underlying dependence on trusted producer structure. Absolute vote count sets the minimum compromised-producer count needed for false qualification. Provenance-domain requirements can prevent selected same-size compromised subsets from qualifying and can therefore delay systematic failure. The same requirements can also reject a true authorization state after fewer benign producer losses when domain diversity disappears.

The result is a finite safety-versus-qualification-availability frontier, not a global policy ranking. The synthetic provenance domains are model labels rather than demonstrated real independence, and the 128 subsets in each block are model states rather than probabilities. Study 4 also contains no contact model. The next study moves to a third boundary, asking which incorrect recovery artifacts remain qualified when progressively stronger artifact-assurance signals are required.

## VI. Recovery-Artifact Assurance and Residual Incorrect States

### A. Study Question and Model Boundary

Study 6 (`S6-SCTR-001`) moves the trust question upstream from runtime authorization evidence to the recovery artifact itself. The study asks when artifact-provenance and release-verification gates can still qualify an objectively incorrect recovery baseline, and what benign qualification cost is introduced when stronger gates require more assurance signals.

The experiment is an exact finite Boolean assurance model. It does not implement malware, an exploit, a real software-supply-chain compromise, a production build system, real signing keys, or an operational spacecraft recovery pipeline. The artifact states and assurance signals are prespecified model variables. SLSA, TUF, SPARTA, and related assurance concepts motivate the selected dimensions but do not validate the model or establish standards compliance.

The research-only oracle is `objective_baseline_correct`. It identifies whether the modeled recovery artifact is objectively correct, but it is never provided to an assurance gate. A gate sees only its required policy-visible assurance signals.

### B. Artifact States and Assurance Signals

The frozen model contains six artifact states. `CLEAN_APPROVED` is objectively correct and has all six visible assurance signals true. Five states are objectively incorrect:

1. `POST_RELEASE_TAMPER`: signature, digest, provenance, and reproduced-build signals are false, while review and approval remain true.
2. `TRUSTED_SIGNER_COMPROMISE`: the signature remains valid, but independent digest, provenance, and reproduced-build signals are false; review is true and release approval is false.
3. `TRUSTED_BUILDER_COMPROMISE`: signature, digest, provenance, review, and approval are true, while independent reproduced-build match is false.
4. `SOURCE_REVIEW_BYPASS`: signature, digest, provenance, reproduced-build, and approval are true, while source-review attestation is false.
5. `APPROVED_BAD_SOURCE`: all six gate-visible assurance signals are true while objective baseline correctness is false.

The six visible assurance signals are:

- `signature_valid`;
- `independent_target_digest_match`;
- `provenance_valid`;
- `independent_reproduced_build_match`;
- `source_review_attested`;
- `release_approved`.

Terms such as "independent" in the signal names are part of the frozen abstraction. They do not establish that different real organizations, hardware roots, networks, or build infrastructures were used.

### C. Assurance Gates and Exact Population

Six deterministic gates compose these signals in progressively different combinations:

- `G0_SIGNATURE_ONLY`: signature validity;
- `G1_SIGNATURE_TARGET_DIGEST`: signature plus independent target digest;
- `G2_SIGNATURE_PROVENANCE`: signature plus provenance;
- `G3_PROVENANCE_REPRODUCED_BUILD`: signature, provenance, and reproduced-build match;
- `G4_PROVENANCE_SOURCE_REVIEW`: signature, provenance, and source-review attestation;
- `G5_COMPOSITE`: all six visible signals.

The experiment has two separate blocks. Block A crosses all six artifact states with all six gates, producing 36 observations. The key endpoint is `unsafe_qualified`, which is true when a gate qualifies an objectively incorrect artifact state.

Block B uses only the objectively correct `CLEAN_APPROVED` baseline and exhausts all 64 subsets of unavailable assurance signals across all six gates. This produces 384 observations. The endpoint `benign_availability_loss` is true when the gate rejects the correct baseline because one or more required assurance signals are unavailable.

The full frozen population is therefore 420 exact observations. The adversarial artifact-state block and the benign assurance-unavailability block are separate. The study does not model a compromised artifact and assurance-signal loss occurring simultaneously.

### D. Signature-Only Qualification Leaves Four Incorrect States

`G0_SIGNATURE_ONLY` requires only a valid signature. It rejects `POST_RELEASE_TAMPER`, where the modeled signature is invalid, but qualifies the other four incorrect states: `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`.

The result is 4 of 5 prespecified incorrect states qualified under the signature-only gate. This ratio is not a detection rate, false-negative rate, or estimate over a real attack population. The five incorrect states are a deliberately constructed finite set, not a sample from software-supply-chain incidents.

The result supports a narrower systems interpretation: signature validity can establish the modeled integrity/authenticity property required by `G0`, but cannot by itself establish objective recovery-baseline correctness when the signer or upstream production process is inside the modeled trust boundary.

### E. Digest and Provenance Close the Signer-Only Gap but Leave Upstream States

`G1_SIGNATURE_TARGET_DIGEST` adds independent target-digest match. It rejects both `POST_RELEASE_TAMPER` and `TRUSTED_SIGNER_COMPROMISE`, reducing unsafe qualification to three states: `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`.

`G2_SIGNATURE_PROVENANCE` also qualifies three of the five incorrect states, and in this frozen state set the same three states remain qualified. This equal aggregate count and equal residual set do not establish operational equivalence between independent target-digest verification and provenance verification. The gates represent different assurance mechanisms, and the finite state model does not enumerate every condition under which those mechanisms could diverge.

The relevant result is therefore bounded: either added signal closes the modeled signer-only state while leaving the upstream builder, review, and fully approved bad-source states visible as qualified under this abstraction.

### F. Reproduced-Build and Source-Review Gates Are Complementary

`G3_PROVENANCE_REPRODUCED_BUILD` requires signature validity, provenance validity, and an independent reproduced-build match. It rejects the trusted-builder-compromise state in addition to the post-release-tamper and trusted-signer-compromise states. Two incorrect states remain qualified: `SOURCE_REVIEW_BYPASS` and `APPROVED_BAD_SOURCE`.

`G4_PROVENANCE_SOURCE_REVIEW` also qualifies two of the five incorrect states, but the residual set is different. It qualifies `TRUSTED_BUILDER_COMPROMISE` and `APPROVED_BAD_SOURCE`, while rejecting `SOURCE_REVIEW_BYPASS`.

The equal 2-of-5 counts therefore conceal different trust boundaries. Reproduced-build evidence closes the modeled builder-compromise pathway but does not detect a source-review bypass if the resulting artifact remains reproducible. Source-review evidence closes the modeled review-bypass pathway but does not detect the trusted-builder state when the required review signal remains true. These gates are complementary in the frozen model rather than interchangeable.

### G. Composite Assurance Leaves the Approved-Bad-Source Boundary

`G5_COMPOSITE` requires all six visible assurance signals. It rejects `POST_RELEASE_TAMPER`, `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, and `SOURCE_REVIEW_BYPASS`. The only prespecified incorrect state that remains qualified is `APPROVED_BAD_SOURCE`.

This state is deliberately important. All six gate-visible signals are true, including signature, independent digest, provenance, reproduced-build match, source-review attestation, and release approval, while the research-only objective-correctness oracle is false. The gate therefore has no visible signal on which to reject the state.

The result should not be overstated. `APPROVED_BAD_SOURCE` is a structural observability boundary of the frozen model, not an information-theoretic impossibility result. The study does not prove that no assurance mechanism could detect bad source. A different model could include additional evidence, such as independent semantic validation, formal verification, behavioral testing, or other assurance signals. Those signals were not part of the frozen Study-6 design and are not added post hoc to remove the residual state.

The result also overlaps conceptually with established supply-chain guidance. SLSA v1.2 explicitly recognizes that an intentionally malicious software producer cannot be directly mitigated through SLSA controls and that the consumer must establish a basis for trusting the producer [12]. The contribution here is therefore not the discovery of that principle. It is the exact residual-state mapping of the frozen recovery-artifact gate composition.

### H. Exact Gate Frontier

Table IV reports the canonical gate summary. The unsafe count is the number of the five prespecified incorrect states that remain qualified. The benign-loss count is the number of the 64 unavailable-signal subsets that cause the objectively correct baseline to be rejected.

**Table IV. Study-6 residual incorrect states and benign assurance loss**

| Gate | Required visible signals | Incorrect states still qualified | Unsafe count | Benign-loss subsets |
|---|---:|---|---:|---:|
| `G0_SIGNATURE_ONLY` | 1 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE`; `TRUSTED_SIGNER_COMPROMISE` | 4/5 | 32/64 |
| `G1_SIGNATURE_TARGET_DIGEST` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G2_SIGNATURE_PROVENANCE` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G3_PROVENANCE_REPRODUCED_BUILD` | 3 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS` | 2/5 | 56/64 |
| `G4_PROVENANCE_SOURCE_REVIEW` | 3 | `APPROVED_BAD_SOURCE`; `TRUSTED_BUILDER_COMPROMISE` | 2/5 | 56/64 |
| `G5_COMPOSITE` | 6 | `APPROVED_BAD_SOURCE` | 1/5 | 63/64 |

For every gate, loss of a single signal that the gate requires is sufficient to produce benign rejection in at least one unavailable-signal subset. The minimum missing-signal count for benign loss is therefore one for all six gates.

Again, the denominators in Table IV are finite model populations. `1/5` must not be interpreted as a 20 percent residual attack rate, and `63/64` must not be interpreted as a 98.4 percent operational outage probability. They describe how many prespecified model states or signal-unavailability subsets cross a deterministic qualification rule.

### I. Stronger Gates Increase Sensitivity to Benign Assurance Loss

The benign block exposes the cost of requiring more evidence. `G0`, which requires only signature validity, rejects the correct baseline in 32 of 64 unavailable-signal subsets. Both two-signal gates reject 48 of 64 subsets. The two three-signal gates reject 56 of 64. The six-signal composite gate rejects 63 of 64, qualifying the correct baseline only when none of its required assurance signals is unavailable.

This monotonic count progression within the frozen gate definitions does not establish a global optimization rule. A stricter gate narrows the modeled set of incorrect states that qualify, but also increases the number of benign missing-evidence states that cause rejection. The study does not assign operational probabilities, mission costs, or utility weights to either side of that frontier.

The term "availability" is therefore used cautiously. Study 6 measures qualification availability under modeled assurance-signal loss. It does not measure mission availability, network availability, spacecraft contact, or service uptime.

### J. Relationship to Provenance and Update-Security Prior Art

The Study-6 gates intentionally use assurance concepts that are already established in software-supply-chain and update-security systems. in-toto provides verifiable supply-chain step metadata [10]. TUF uses signed metadata, target hashes, trusted roles, thresholds, and expiration to secure software updates [11]. SLSA defines source and build assurance levels and threat boundaries [12]. SPARTA also motivates integrity-protected and validated recovery baselines in the spacecraft context [4].

Study 6 neither replaces nor validates those systems. It also does not claim standards compliance. The model asks a different question: if a recovery-qualification policy can observe selected assurance signals corresponding to these broad concepts, which prespecified incorrect artifact states remain observationally indistinguishable from acceptable artifacts under each gate?

That question makes the residual state set, rather than the existence of provenance itself, the primary result.

### K. Study-6 Residual Trust Boundary

Study 6 shows that composing more artifact-assurance signals closes specific modeled failure pathways, but the residual boundary changes with which assurance dimensions are visible. Signature-only qualification leaves four prespecified incorrect states. Adding digest or provenance closes the signer-only state. Adding reproduced-build evidence closes the modeled builder-compromise state, while adding source-review evidence closes the review-bypass state. The composite gate closes all modeled integrity/provenance pathways except `APPROVED_BAD_SOURCE`, where every gate-visible assurance signal remains true despite objective incorrectness.

The same composition increases sensitivity to benign assurance-signal loss. The result is therefore a finite residual-correctness versus qualification-availability frontier, not a globally best gate. It completes the third study-specific layer needed for the cross-study synthesis: Study 3 addresses temporal runtime evidence, Study 4 addresses producer composition, and Study 6 addresses the recovery artifact itself.

## VII. Cross-Study Residual Trust Boundaries

### A. Scope of the Synthesis

Studies 3, 4, and 6 were designed, executed, and frozen as separate experiments. Their populations, mechanisms, and endpoints are not pooled in this section. The purpose of the synthesis is narrower: to compare what each experiment shows about a recovery-qualification decision that depends on policy-visible evidence while some relevant truth remains outside the gate's direct observation set.

This layered interpretation was developed after the individual studies were frozen. It is therefore a manuscript-level systems synthesis, not a prospectively tested integrated architecture or a fourth experiment. No end-to-end recovery probability, combined success rate, common effect size, or pooled statistical population is defined.

### B. Three Distinct Qualification Layers

The three studies expose residual boundaries at different points in a recovery decision chain.

Study 3 operates at the **temporal runtime-evidence layer**. The gate observes record properties such as signature validity, freshness, and policy-visible authorization evidence while research-only authorization truth can change independently. Its principal residual boundary appears when a trusted producer continues to issue fresh and validly signed false evidence. A smaller nonadversarial boundary appears when a truthful pre-onset record remains fresh briefly after hidden authorization changes.

Study 4 operates at the **producer-composition layer**. The gate observes signed producer claims, total vote count, and synthetic provenance-domain representation. Hidden authorization truth is fixed separately in the malicious-compromise and benign-unavailability blocks. The residual boundary depends on which producer subsets can satisfy the rule, and provenance requirements can change systematic failure even when the first possible failure count is unchanged.

Study 6 operates at the **recovery-artifact assurance layer**. The gate observes selected artifact-assurance signals while objective baseline correctness remains a research-only oracle. Stronger gates close specific modeled signer, builder, review, or post-release tamper states, but the fully approved bad-source state remains qualified because every gate-visible signal is true.

**Table V. Cross-study residual-boundary comparison**

| Layer | Study | What the gate can observe | Research-only truth outside the gate | Principal residual boundary | Effect of stronger composition in frozen model |
|---|---|---|---|---|---|
| Temporal runtime evidence | Study 3 | Signature validity, freshness, received authorization evidence, contact-dependent record availability, security signal | Hidden authorization truth | Fresh valid evidence can remain false; truthful cache can briefly lag a state change | Contact-aware restriction reduces selected K4 exposure but does not eliminate persistent V5 qualification for B0/S1 |
| Producer composition | Study 4 | Signed claims, vote threshold, synthetic provenance-domain count | Hidden authorization truth | Some compromised subsets satisfy the rule while others of the same size do not | Provenance can delay systematic unsafe qualification but can also cause earlier false-conservative rejection |
| Recovery artifact | Study 6 | Signature, digest, provenance, reproduced-build, review, approval | Objective baseline correctness | All visible assurance signals can be true for `APPROVED_BAD_SOURCE` | Additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss |

Table V is a qualitative comparison. The rows do not share a common measurement scale, and no numeric outcome is combined across them.

### C. Integrity and Authenticity Do Not Exhaust Semantic Trust

The strongest common pattern is the distinction between evidence integrity and the semantic truth needed for a recovery decision.

Study 3 makes this distinction directly through the contrast between `V4` and `V5`. Post-signature alteration in `V4` invalidates the signature, and the affected record never qualifies. In `V5`, the false record is validly signed by the trusted producer and can remain qualified. The experiment therefore separates detectable record alteration from false content generated inside the modeled trust boundary.

Study 6 shows an analogous upstream distinction. Signature-only qualification rejects ordinary post-release tampering but cannot identify several prespecified incorrect artifacts whose visible signature state remains valid. Additional digest, provenance, reproduced-build, review, and approval signals close more of those modeled states. Even the composite gate, however, cannot distinguish `APPROVED_BAD_SOURCE` because the research-only correctness failure is not represented in any visible signal.

These results do not imply that signatures, provenance, or other assurance mechanisms are ineffective. Each closes specific modeled failure pathways. The narrower implication is that an assurance property can establish only the property represented by the evidence and trust anchors on which it depends. A policy cannot infer a research-only semantic truth solely because the visible evidence is authentic, fresh, or process-conformant.

### D. Composition Moves the Boundary Rather Than Producing Universal Dominance

The three studies also caution against interpreting additional evidence requirements as a universally monotonic improvement.

In Study 4, adding provenance-domain requirements can substantially delay systematic unsafe qualification for selected vote thresholds. `Q3_D3`, for example, moves systematic safety failure from three compromised producers under `Q3_D1` to six while leaving first failure at three. That added constraint also makes benign false-conservative rejection possible after only two unavailable producers instead of five. Other provenance additions produce no threshold change, including `Q4_D1` versus `Q4_D2`, `Q5_D1` versus `Q5_D2`, and all domain variants at `Q6` and `Q7`.

Study 6 shows a related but distinct frontier. Adding assurance signals reduces the number of prespecified incorrect artifact states that remain qualified, from four under signature-only checking to one under the six-signal composite gate. The number of benign assurance-unavailability subsets causing rejection rises from 32 of 64 to 63 of 64. Equal aggregate counts can also conceal different residual mechanisms, as shown by the different state sets left by `G3` and `G4`.

Study 3 does not contain the same benign-unavailability endpoint and therefore is not folded into a common safety-versus-availability statistic. Its evidence-aware/contact-aware policy can reduce modeled exposure in selected K4 comparisons, but the study does not support a cross-study claim that every stronger policy produces the same type of availability tradeoff.

The common systems lesson is therefore conditional: adding structure to qualification can close or narrow selected failure regions, but the resulting residual boundary depends on which evidence dimensions are added and which failure assumptions remain outside the gate.

### E. First Failure, Systematic Failure, and Residual-State Identity

A second cross-study insight is that aggregate counts alone can hide the mechanism that remains.

Study 4 distinguishes first failure from systematic failure because subset composition matters. A three-producer compromise under `Q3_D3` can be sufficient if all three provenance domains are represented, but other three-producer subsets remain blocked. The first threshold therefore describes possibility, whereas the systematic threshold describes inevitability across subsets of that size.

Study 6 provides the analogous lesson in state identity. `G3` and `G4` each qualify two of five incorrect states, but `G3` leaves `SOURCE_REVIEW_BYPASS` while `G4` leaves `TRUSTED_BUILDER_COMPROMISE`; both leave `APPROVED_BAD_SOURCE`. The equal count does not make the gates equivalent.

Study 3 similarly benefits from origin identity. The same generic endpoint, unsafe qualification, can arise from a truthful pre-onset cache record or from a false record generated by the compromised trusted producer. The prespecified origin decomposition prevents these mechanisms from being merged.

Across the three studies, the identity of the residual mechanism is therefore as important as the count or duration of the residual state. This is why the manuscript emphasizes origin, subset structure, and surviving artifact states rather than collapsing results into a single scalar measure.

### F. Observability as the Common Constraint

The common abstraction can be stated in terms of observability. A recovery gate evaluates only what has been represented in its policy-visible evidence.

In Study 3, hidden authorization truth is intentionally unavailable to the selector. A compromised trusted producer can therefore produce a valid visible claim that disagrees with hidden truth. The gate can reject an invalid signature, but it cannot directly observe that the trusted signer is semantically lying.

In Study 4, the gate observes producer claims and structural provenance labels, not an oracle identifying which producers are compromised. Quorum and provenance rules change how many and which visible claims are required, but qualification still depends on the assumed relationship between producer identity, provenance class, and trustworthiness.

In Study 6, the gate observes assurance signals rather than objective correctness. When `APPROVED_BAD_SOURCE` makes every visible assurance signal true, the gate has no frozen variable that distinguishes the artifact from the objectively correct state.

This does not establish a universal impossibility result. It identifies a model-specific principle: within each frozen experiment, a mismatch that is not represented in policy-visible evidence cannot be corrected by rearranging evidence that remains observationally identical with respect to that mismatch.

### G. Aerospace Systems Implications

The experiments do not evaluate a deployed spacecraft architecture, but they identify several design questions relevant to aerospace information systems.

First, recovery requirements should distinguish **evidence integrity** from **evidence authority and semantic trust**. A design that checks only whether evidence is signed and fresh should document what assumptions are made about the signer remaining semantically trustworthy.

Second, multi-source recovery evidence should state what producer diversity is intended to represent. Study 4 uses synthetic provenance domains precisely because real independence was not measured. An operational architecture would need to justify whether producer diversity corresponds to separate organizations, software stacks, hardware roots, sensing paths, administrative authorities, supply chains, or some other failure-separation assumption.

Third, evidence requirements should be evaluated together with the conditions under which required evidence may be unavailable. Studies 4 and 6 show that stricter qualification can reduce selected unsafe states while increasing false-conservative rejection under their respective benign-loss models. In an operational mission, the acceptable balance would depend on mission phase, hazard state, autonomy requirements, and available recovery alternatives. Those mission tradeoffs were not measured here.

Fourth, recovery-artifact assurance should identify the highest-level trust assumption that remains outside the gate. Provenance, reproduced builds, source review, and release approval each provide useful evidence, but a system still needs a justified basis for trusting the process or authority that ultimately defines acceptable source and behavior.

These are design implications, not prescriptive flight requirements. The studies provide finite-model evidence about qualification boundaries, not evidence that a particular spacecraft architecture, producer-composition rule, contact policy, or artifact gate should be adopted operationally.

### H. Synthesis Result

Taken together, the three studies support a layered residual-trust interpretation of satellite cyber-recovery qualification. Temporal evidence qualification can fail when fresh, authentic evidence diverges from hidden authorization truth. Producer composition can shift the subset boundary at which false claims satisfy a recovery rule, with conditional gains and benign-loss costs from provenance requirements. Artifact assurance can close selected integrity and process failures while leaving a residual state that is indistinguishable under the frozen visible signals.

The synthesis therefore does not identify a globally best policy, producer-composition rule, or artifact gate. Its contribution is to make the residual assumption explicit at each layer. Stronger evidence composition can move or narrow a qualification boundary, but it does not automatically convert policy-visible trust evidence into direct observation of hidden or objective truth.

## VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation

### A. Internal and Construct Validity

The three experiments are exact evaluations of frozen finite models, so their strongest validity claim is internal to those models. Study 3 preserves the distinction between policy-visible evidence and hidden authorization truth, prespecifies the two allowable origins of false qualification, and independently audits the resulting trajectories and epoch rules. Study 4 exhausts every producer subset for every registered quorum/provenance rule in two separately defined blocks. Study 6 exhausts its prespecified artifact states and all subsets of benign assurance-signal unavailability. These controls reduce ambiguity about what each frozen endpoint represents.

The common residual-trust framework introduced in this manuscript was not itself a prospectively tested experimental treatment. Studies 3, 4, and 6 were designed and frozen independently. The common framework is a post hoc systems-level interpretation used to compare their mechanisms without changing the frozen outcomes. It should therefore be evaluated as a synthesis of three separately supported results, not as evidence that an integrated three-layer recovery architecture was experimentally validated.

The endpoint terminology also requires care. In Study 3, `unsafe_qualified` means that the modeled recovery gate remains policy-visible qualified while hidden authorization truth is false. In Study 4, the safety block measures resistance to unsafe qualification, and the availability block measures false-conservative rejection under benign producer unavailability. In Study 6, benign availability loss means rejection of the objectively correct artifact when required assurance signals are unavailable. None of these constructs is equivalent to spacecraft physical safety, mission availability, or successful completion of a recovery procedure.

### B. Study-3 Boundary Conditions

Study 3 uses one continuous-contact regime and one synthetic intermittent-contact regime. K4 contains four fixed contact windows over a 240-logical-second horizon. The result therefore characterizes that registered schedule and the associated five-logical-second epoch and freshness semantics. It does not establish how the same policies would behave under other contact schedules, real orbital geometry, different latency distributions, variable evidence lifetimes, or mission-specific ground coverage.

Logical seconds are model units. Although the labels preserve the frozen timing semantics, they are not measurements of spacecraft processor time, radio-link latency, ground-station delay, operator response time, or elapsed orbital time. The reported 122.5, 55.326, 49.022, 5, and 0.326 logical-second exposures must therefore remain model quantities.

The 46 onset phases exhaust the frozen onset grid, but they are not 46 random draws from an operational distribution. Similarly, the 67,620 epoch states are repeated states nested within 1,380 trajectories and are not independent statistical observations. The trajectory remains the study unit.

The trusted-producer compromise in `V5` is also abstract. It assumes that a trusted producer can validly sign a false authorization claim. The experiment does not model how that compromise occurs, whether a signing key is stolen, whether software is maliciously modified, or how likely the condition is in a real mission. Conversely, `V4` models a post-signature value change that invalidates the signature. The contrast establishes a bounded difference between altered signed data and false data signed by the trusted producer; it does not evaluate cryptographic strength or key-management security.

### C. Study-4 Boundary Conditions

Study 4 fixes the producer population at seven and the synthetic provenance allocation at 3/2/2. Its exact thresholds are therefore conditional on that registered producer set, domain allocation, denominator, and 18 rule definitions. A different number of producers, a different provenance allocation, dynamic membership, weighted voting, or a responder-based denominator could produce different thresholds.

The provenance domains are synthetic independence classes. The experiment does not demonstrate organizational, hardware, software, network, administrative, sensing-path, or supply-chain independence among real producers. Any operational use of a provenance constraint would require an external justification for what failure separation the domains represent.

The safety and benign-availability populations are deliberately separate. The study does not evaluate simultaneous malicious compromise and benign producer unavailability. It also does not model adaptive adversaries, collusion strategies beyond the affected-subset state, network timing, Byzantine agreement, leader election, or sensor-estimation error.

The 128 subsets per block are the complete power set of the seven modeled producers. Fractions of failing subsets at a given affected-producer count are therefore combinatorial properties of the model, not probabilities that a real subset will be compromised or unavailable. First and systematic failure thresholds likewise describe the frozen set structure and should not be interpreted as operational reliability limits.

### D. Study-6 Boundary Conditions

Study 6 is an abstract six-state, six-gate Boolean assurance model. The five objectively incorrect states were selected to expose distinct trust assumptions, but they are not an exhaustive taxonomy of software-supply-chain failure. Consequently, values such as 4/5, 3/5, 2/5, and 1/5 are finite state counts rather than detection rates, false-negative rates, or estimates of residual compromise probability.

The six assurance signals are also modeled Boolean variables. `independent_target_digest_match` and `independent_reproduced_build_match` do not demonstrate real organizational or infrastructure independence. `source_review_attested` and `release_approved` do not measure the quality, competence, or adversarial resistance of a real review and approval process.

`APPROVED_BAD_SOURCE` is intentionally defined so that all six gate-visible signals are true while objective correctness is false. It therefore identifies the observability boundary of the frozen model. The result is not a theorem that semantic correctness can never be established, nor does it imply that additional techniques such as formal verification, independent behavioral testing, semantic review, runtime validation, or diverse implementations could not add evidence. Those mechanisms were outside the frozen Study-6 design and were not added after observing the result.

The benign assurance-unavailability block is likewise structural. All 64 unavailable-signal subsets are evaluated with the objectively correct baseline. Counts such as 63/64 describe deterministic rejection across that finite subset space. They do not estimate service outage probability, contact probability, or the frequency with which real assurance systems become unavailable.

### E. External Validity and Aerospace Generalization

No experiment in Paper 2 operates an on-orbit spacecraft, ground station, RF link, flight processor, production key infrastructure, or real mission command path. No operational spacecraft recovery is executed. The results therefore do not establish flightworthiness, certification, mission assurance compliance, operational attack prevalence, recovery success probability, or mission-level availability.

Only Study 3 directly includes a contact variable. Study 4 producer unavailability must not be interpreted as loss of spacecraft contact, and Study 6 assurance-signal unavailability must not be interpreted as either contact loss or network outage. Treating all three as manifestations of intermittent connectivity would erase important construct differences among the experiments.

The spacecraft relevance instead comes from the systems question being modeled: recovery qualification can depend on evidence received under intermittent contact, evidence composed across trusted producers, and assurance about the recovery artifact itself. The experiments isolate those mechanisms in deterministic abstractions. Generalization to a specific spacecraft program would require mapping the abstract evidence producers, provenance domains, gates, timing semantics, and failure states to mission-specific components and then validating that mapping against the target architecture.

### F. Statistical Interpretation

The studies evaluate complete finite populations specified by their frozen protocols. Sampling-based inferential statistics are therefore not used to make claims about the registered grids. No p-value gate, confidence interval over an assumed superpopulation, or pooled effect estimate is required to establish an exact count or threshold within the enumerated state space.

This does not make the results universal. Exactness applies to the registered model population, not to all possible spacecraft or attack conditions. The absence of sampling uncertainty within a finite grid is distinct from uncertainty about model choice, external validity, or omitted operational variables.

The three populations also remain incommensurate. Study 3 uses trajectories, Study 4 uses rule-by-subset observations, and Study 6 uses artifact-state and assurance-unavailability observations. Their arithmetic sum is not a scientifically meaningful sample size. No pooled `N`, success percentage, confidence interval, or global rank is defined in this paper.

### G. Reproducibility and Independence

Each experiment is provenance-bound and independently audited within the repository. Study 3 reports zero trajectory, epoch-rule, false-qualification-origin, and hash mismatches. Study 4 reports zero observation and threshold mismatches under independent reconstruction. Study 6 reports zero mismatches with matching frozen outputs and no tracked-file drift.

These controls support same-repository reproducibility and strengthen confidence that the reported manuscript projections reflect the frozen experiments. They do not constitute external empirical replication because the independent implementations and audits remain within the same research program and repository. External replication would require an independent research group, environment, or evidence source beyond the present repository controls.

### H. Standards and Framework Interpretation

RATS, SPARTA, SLSA, TUF, in-toto, and related sources are used to position the modeled evidence dimensions against established security concepts. The studies do not implement every requirement of those frameworks, and no compliance assessment was performed. References to provenance, attestation, reproducible builds, trusted baselines, or cyber-safe recovery therefore identify conceptual relationships only.

This distinction is particularly important for Study 6. The presence of model variables named provenance, reproduced build, source review, and release approval does not establish that a deployed implementation would satisfy SLSA, TUF, SPARTA, or any other standard or framework.

### I. Limits of the Cross-Study Synthesis

The cross-study synthesis compares residual mechanisms, not causal transitions from one experiment to the next. Study 4 does not experimentally mitigate Study 3, and Study 6 does not experimentally validate a downstream artifact gate for either Study 3 or Study 4. No data flow connects the frozen populations.

The synthesis also does not imply that the three qualification layers are complete. Real recovery systems can depend on additional dimensions, including command authority, hardware roots of trust, behavioral verification, physical-state estimation, network path integrity, human authorization, fault-management logic, and mission-phase constraints. The present paper focuses only on the three independently frozen mechanisms that were evaluated.

Accordingly, the layered residual-trust interpretation should be read as an analytical decomposition: temporal evidence, producer composition, and artifact assurance each expose a distinct trust boundary. It is not a claim that every recovery architecture should contain exactly these three layers or evaluate them in this order.

### J. Future Evaluation

Several extensions could test the portability of the present findings without altering the frozen evidence reported here. Study 3 could be complemented by prospectively designed orbital-contact schedules, variable evidence lifetimes, or hardware/software-in-the-loop timing measurements. Study 4 could be extended to different producer counts, empirically justified failure domains, dynamic membership, or joint compromise-and-unavailability conditions. Study 6 could be evaluated against real build pipelines, independently operated assurance services, additional semantic-validation mechanisms, or prospectively defined joint artifact-compromise and evidence-loss scenarios.

A separate integrated experiment could also test how runtime evidence, multi-producer composition, and artifact assurance interact in one recovery architecture. Such an experiment would be scientifically different from the present manuscript because it would define new joint interventions, units, and endpoints. It should therefore be designed and frozen prospectively rather than inferred from the three existing populations.

These extensions are opportunities for external validation and broader generalization. They are not defects that justify reopening or rerunning the frozen Studies 3, 4, or 6 for the present paper.

## IX. Conclusion

This paper examines trusted cyber-recovery qualification through three separately frozen deterministic studies rather than through a single integrated experiment. The common analytical question is whether policy-visible evidence is sufficient to support qualification when a relevant research-only truth remains outside the gate's direct observation set.

Study 3 identifies a temporal trust boundary. The affected post-signature-manipulated `V4` records have invalid signatures and do not qualify, while a compromised trusted producer can continue to issue false `V5` authorization evidence that remains both fresh and validly signed. Under persistent `V5`, `B0` and `S1` remain unsafe-qualified across all 46 onset trajectories under both continuous `K0` and synthetic intermittent `K4` contact, although K4 reduces mean modeled exposure. The separate truthful `V0` control shows a smaller pre-onset cache boundary, allowing adversarial false evidence and ordinary freshness lag to remain distinguishable.

Study 4 identifies a producer-composition boundary. Absolute vote count establishes the basic number of compromised producers needed for false qualification, while synthetic provenance-domain requirements change which same-size subsets can satisfy the rule. For selected thresholds, provenance requirements substantially delay systematic unsafe qualification without changing first failure, but they can also make false-conservative rejection possible after fewer benign producer losses. Other domain requirements produce no threshold change. The result is therefore a conditional qualification frontier rather than evidence that provenance diversity is universally beneficial or that one producer-composition rule is globally best.

Study 6 identifies a recovery-artifact assurance boundary. Signature-only qualification leaves four of five prespecified incorrect states qualified. Adding digest, provenance, reproduced-build, source-review, and approval evidence closes specific modeled pathways, while the composite gate leaves only `APPROVED_BAD_SOURCE`. At the same time, stronger gates reject the correct baseline under increasingly many benign assurance-signal-loss subsets. The residual approved-bad-source state is a boundary of the frozen visible signals, not a universal impossibility result or an operational attack rate.

Across the three studies, the central systems finding is that stronger trust composition can move or narrow a recovery-qualification boundary without automatically making policy-visible evidence equivalent to hidden or objective truth. The identity of the remaining trust assumption matters as much as the aggregate count or duration of residual qualification. For aerospace information systems, this result motivates explicit documentation of what each recovery gate verifies, what trust assumption remains outside its observability, and what benign evidence-loss conditions the system is prepared to tolerate.

The reported findings remain bounded to exact finite models. Only Study 3 models intermittent contact, logical time is not operational spacecraft time, synthetic provenance domains do not establish real independence, and Study 6 does not evaluate a real supply-chain compromise. No pooled population, global policy ranking, flight-safety claim, mission-availability claim, or operational recovery probability is inferred. Within those boundaries, the three studies provide a reproducible characterization of residual trust at the temporal evidence, producer-composition, and recovery-artifact layers of satellite cyber-recovery qualification.

## References

[1] R. Thummala, E. Rice, and G. Falco, "Why is Space Cybersecurity Unique?" NDSS SpaceSec, 2026.

[2] J. Vanlyssel, G.-C. Roman, K. Cook, S. Rahaman, and A. Anwar, "Trust Without Boundaries: An Architectural Analysis of Satellite Flight Software," arXiv:2608.14532, Aug. 2026.

[3] J. Curbo and G. Falco, "Testable Cyber Requirements for Space Flight Software," in Proc. 2025 IEEE Aerospace Conference, 2025, doi: 10.1109/AERO63441.2025.11068629.

[4] The Aerospace Corporation, "Space Attack Research and Tactic Analysis (SPARTA)," online resource, accessed Sep. 2026.

[5] H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, "Remote ATtestation procedureS (RATS) Architecture," RFC 9334, Jan. 2023, doi: 10.17487/RFC9334.

[6] Y. Deshpande, J. Zhang, H. Labiod, and H. Birkholz, "Remote Attestation with Multiple Verifiers," draft-ietf-rats-multi-verifier-00, IETF RATS Working Group, May 2026, work in progress.

[7] D. Malkhi and M. Reiter, "Byzantine quorum systems," Distributed Computing, vol. 11, no. 4, pp. 203-213, 1998, doi: 10.1007/s004460050050.

[8] O. Alpos, C. Cachin, B. Tackmann, and L. Zanolini, "Asymmetric distributed trust," Distributed Computing, vol. 37, pp. 247-277, 2024, doi: 10.1007/s00446-024-00469-1.

[9] F. Rezabek, D. Malkhi, and A. Yahalom, "Space Fabric: A Satellite-Enhanced Trusted Execution Architecture," arXiv:2603.23745, Mar. 2026.

[10] S. Torres-Arias, H. Afzali, T. K. Kuppusamy, R. Curtmola, and J. Cappos, "in-toto: Providing farm-to-table guarantees for bits and bytes," in Proc. 28th USENIX Security Symposium, 2019.

[11] The Update Framework, "The Update Framework Specification," current specification, 2026.

[12] SLSA, "SLSA v1.2 Source Requirements" and "Threats & Mitigations," current approved specification, 2026.
