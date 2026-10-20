# Architecture-Grounded Trust Separation for Satellite Cyber-Recovery Decisions in Space-Enabled Critical Infrastructure

**Paper 3 — IJCIP venue-adapted manuscript R3**  
**Target journal:** International Journal of Critical Infrastructure Protection (IJCIP)  
**Studies:** Study 7 / S7-LSO-001 and Study 7E / S7E-AERC-001  
**Draft state:** IJCIP_R3__VENUE_LOCKED_FOR_PREPARATION__SCIENCE_FROZEN  
**Submission authorization:** NOT GRANTED

## Abstract

Space systems directly provide or enable services used by communications, transportation, defense, emergency response, and other critical-infrastructure functions, making trustworthy cyber recovery an infrastructure-protection concern rather than only an onboard software problem. This paper studies how recovery decisions behave when apparently valid evidence can be incomplete, compromised, or produced by shared trust paths. Two separately frozen finite experiments are reported. Study 7 isolates information sufficiency: across 1,033 modeled observations, a visible-only learned selector exactly reproduces its deterministic visible decision boundary but cannot distinguish safe and signed-but-false states with identical policy-visible inputs. Study 7E prospectively extends that result into a core Flight System-grounded reference architecture with explicit source, key, execution, transport, and authorization trust domains; deterministic and learned policy pairs receiving byte-identical inputs; frozen decision-tree models; thirteen fault profiles; and held-out evaluation on unseen faults and higher-separation topologies. Its 196 held-out scenarios produce 784 decisions with zero invalid scenarios and zero audit mismatches. Equal-information deterministic/learned pairs disagree in 67 of 196 base-information scenarios and 72 of 196 corroborated scenarios. Deterministic corroboration reduces unsafe proceeds from 9 to 4 while increasing false-conservative holds from 31 to 45; learned corroboration increases unsafe proceeds from 21 to 31 while reducing false-conservative holds from 26 to 12. Topology-controlled results are non-monotonic, including adverse learned transfer as separation increases. The evidence supports a critical-infrastructure assurance conclusion rather than a policy ranking: recovery correctness depends jointly on decision-relevant observability, selector behavior, and the architecture that produces and shares evidence.

**Keywords:** satellite cybersecurity; cyber recovery; critical infrastructure protection; trust domains; machine-learning assurance; common-cause failure

## 1. Introduction

Cyber detection and cyber recovery answer different questions. Detection identifies evidence that something may be wrong; recovery logic must decide what action is justified after that signal, using only the state visible to the decision process. Space-domain response concepts such as cyber-safe mode similarly connect cyber-threat recognition to a controlled transition toward a trusted or integrity-protected state [1]. That transition creates an assurance problem when the evidence authorizing recovery is itself exposed to compromise.

Space systems are relevant to critical-infrastructure protection because they directly provide important services and enable other infrastructure sectors and industries [22]. CISA's Communications infrastructure description explicitly includes satellite systems and identifies communications dependencies across energy, transportation, water and wastewater, emergency services, information technology, and financial services [23]. U.S. space-cybersecurity policy likewise calls for protecting space assets and supporting infrastructure from cyber threats [24]. This paper therefore treats spacecraft recovery assurance as a protection problem for a space-enabled critical-infrastructure asset. It does **not** claim that the controlled experiments quantify cross-sector cascading failures, national-level consequences, or operational service-outage probabilities.

A record can remain signed, current, and structurally acceptable to a recovery gate while being false relative to a state that the selector cannot observe. A prior experiment in this research program instantiated that signed-but-false condition as an antecedent deterministic recovery boundary [2]. The present work does not reuse those observations as new evidence. Instead, it asks two downstream questions. First, can learning overcome such a boundary when the learned selector sees the same information as a deterministic rule? Second, once an additional corroborating path is introduced, what happens when its trust relationship is represented as an architecture rather than a single stipulated independence bit?

These questions are distinct from conventional satellite machine-learning performance studies. Recent spacecraft ML work has emphasized anomaly detection, telemetry classification, model comparison, and adaptation to changing mission data [4]-[6]. Those are important upstream problems, but a high-performing detector does not by itself establish that a downstream recovery action is justified. Aerospace ML assurance literature likewise treats confidence as a lifecycle evidence problem involving requirements, data, model behavior, integration, verification, validation, robustness, traceability, and system context rather than only predictive performance [3]. Partial observability and latent state are also established safety problems in their own right [7], [8]. The novelty claimed here is therefore not a new theory of hidden state, secure spacecraft recovery, resilient flight-software architecture, cFS security, or evidence redundancy. Prior work has addressed trusted-hardware spacecraft recovery, software-resilient space-system architectures, mission-specific cybersecurity architecture, cFS attack surfaces, malicious spacecraft peripherals, and adversarial risk around satellite ML [14]-[20]. The narrower contribution here is a controlled satellite cyber-recovery assurance construction that separates information availability, selector class, and trust-domain architecture, then freezes learned models before evaluating equal-information policy pairs on held-out faults and trust topologies.

The paper reports two separate frozen studies.

**Study 7 / S7-LSO-001** is the information-sufficiency foundation. It evaluates a deterministic visible-only comparator, a learned selector trained on the same eight visible features, and a corroboration-aware learned selector. The complete finite population contains 1,033 observations. The study asks whether exact fit to a visible rule implies correctness when relevant adjudication truth is hidden and how a corroborating observable changes that boundary when it is independent versus correlated with the compromised evidence path.

**Study 7E / S7E-AERC-001** is a new prospective extension. It was designed after the Study-7 publication package exposed an application-specific limitation: the original corroboration variable was stipulated rather than instantiated in a concrete spacecraft recovery architecture, and the corroboration-aware learned selector lacked an equal-information deterministic comparator. Study 7E addresses those limitations without modifying or rerunning Study 7. It uses a cFS-grounded reference architecture, five explicit trust-domain dimensions, equal-information deterministic/learned policy pairs, frozen source/key/time/fault semantics, separately frozen decision-tree models, and a held-out evaluation population covering unseen fault classes and topologies excluded from training.

The studies answer a layered set of research questions.

**Foundation RQ — Study 7.** How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and how does adding a corroborating observable change that boundary when corroboration is independent versus correlated with the compromised path?

**RQ1 — Study 7E equal-information comparison.** In a concrete cFS-grounded recovery architecture, how do deterministic and learned selectors differ when paired policies receive exactly the same policy-visible evidence?

**RQ2 — Study 7E trust-domain separation.** How does explicit separation of source, signing-key, execution, transport, and authorization domains change unsafe-recovery and false-conservative outcomes?

**RQ3 — Study 7E common-cause failure.** Under which shared-domain and common-cause compromises does the benefit of corroborating evidence collapse?

**RQ4 — Study 7E topology/fault transfer.** How do frozen learned selectors behave when evaluated on fault classes and higher-separation trust topologies excluded from training?

The contribution is fivefold. First, the paper preserves the exact Study-7 information-sufficiency result instead of treating model fit as evidence of hidden-state knowledge. Second, Study 7E introduces deterministic and learned comparators with cryptographically hash-verified equal policy inputs. Third, it replaces a single abstract independence flag with an explicit topology over source, key, execution, transport, and authority domains. Fourth, it evaluates complete finite held-out populations with no post-hoc scenario deletion and retains adverse and null results. Fifth, it shows that architecture and selector behavior interact: deterministic corroboration and learned corroboration can move unsafe and false-conservative outcomes in opposite directions, and greater trust-domain separation does not produce a monotonic policy-level improvement.

The paper does not claim global superiority of learned or deterministic logic, operational spacecraft safety probabilities, certification sufficiency, flight qualification, NASA endorsement, measured RF-link performance, or independence beyond the experimental domains instantiated here.

## 2. Related Work and Assurance Boundary

### 2.1 Recovery authorization versus anomaly detection

Satellite anomaly-detection research provides important evidence on telemetry representation and detector behavior. The OPS-SAT benchmark supplies labeled spacecraft telemetry fragments and evaluates a broad range of anomaly-detection algorithms [4]. Transformer-based work has compared deep architectures for satellite telemetry anomaly detection [5], while validation-gated continual learning addresses changing telemetry distributions and data scarcity [6]. These studies concern identifying anomalous conditions from telemetry. The present work begins after a security signal is already part of the policy-visible state and asks whether the evidence available to a recovery selector justifies entering a recovery gate.

This distinction matters because recovery actions can alter mission state. A selector may receive apparently valid evidence from a path whose producer, key, execution environment, transport, or authorizing authority has been compromised. The resulting assurance question is not only whether the selector has low classification error but whether its inputs distinguish the states that matter for a safe recovery decision.

### 2.2 Learning-enabled assurance and partial observability

NASA guidance for learning-enabled aerospace components emphasizes that assurance depends on evidence across the component and system lifecycle, including requirements, model and data properties, integration, coverage, traceability, verification, validation, and robustness [3]. The present studies fit that framing by treating model behavior and input provenance as separate assurance objects. They do not attempt to establish a certification method or sufficient evidence set.

The general problem of safe decision making under partial observability is established. Safe action-model learning under partial observability [7] and safety certification with latent variables [8] illustrate broader theoretical settings in which unobserved state constrains what can be inferred or guaranteed. Study 7 therefore does not claim that an unobserved variable is a novel ML problem. Its purpose is narrower: to make the information boundary explicit in a satellite cyber-recovery selector, evaluate the complete modeled visible state space, and then carry the question into an architecture where trust-path relationships can be faulted and measured.

### 2.3 Secure recovery and resilient spacecraft software

Secure spacecraft recovery and resilient software architecture are established research areas. Juliato and Gebotys proposed trusted-hardware mechanisms and recovery protocols for restoring spacecraft and cryptographic capabilities after failures or attacks [19]. Phillips, Mazzuchi, and Sarkani treated software resiliency as a systems-engineering and architecture problem spanning the space-system lifecycle [21]. Driouch, Bah, and Guennoun later proposed a mission-specific defensible cybersecurity architecture based on threat analysis and layered controls [20]. These works establish that secure recovery, architectural resilience, and mission-specific cybersecurity are not novel concepts by themselves.

Recent flight-software research also narrows any broad cFS novelty claim. Curbo and Falco analyze the spacecraft flight-software attack surface and argue for architectural simplification and stronger security principles [14]. McAmis et al. demonstrate, using cFS, a security/reliability dilemma created by a malicious spacecraft peripheral [15]. A contemporaneous 2026 preprint by Vanlyssel et al. analyzes authority, identity, communication, observability, and persistence in cFS and reports experiments with a malicious onboard component [16]. Because [16] is a preprint, it is used as contemporaneous positioning evidence rather than peer-reviewed validation.

Study 7E therefore does not claim to introduce secure spacecraft recovery, cFS security, or trust boundaries. Its narrower question is how a frozen recovery selector behaves when policy-visible evidence is held equal within deterministic/learned pairs while source, key, execution, transport, and authority relationships are prospectively instantiated and faulted.

### 2.4 Satellite ML security and the remaining assurance gap

Satellite ML security is also developing rapidly. Shigol et al. provide a structured risk assessment of adversarial-ML threats for satellite applications, including integrity risks and mitigations such as resilient data pipelines and runtime monitoring [17]. Belali et al. propose S-LARF, a system-level framework that hardens spaceborne anomaly-detection pipelines against adversarial ML and evaluates architectural controls using spacecraft telemetry and FPGA deployment [18]. These studies strengthen the case that ML security must be considered at system level, but they remain primarily focused on ML threat assessment, anomaly-detection security, or adversarial robustness.

The present paper addresses a different downstream decision boundary. It does not evaluate anomaly-detector accuracy or adversarial perturbation robustness. It asks whether recovery authorization is justified after a security signal exists, whether deterministic and learned selectors behave differently under byte-identical inputs, and how those decisions change when evidence paths share or separate experimentally defined trust domains.

A targeted literature search updated through 24 September 2026 located the adjacent work above but did not identify a publication combining all of the following in one satellite cyber-recovery experiment: (i) downstream recovery authorization rather than detector performance; (ii) deterministic and learned equal-information policy pairs with byte-identical policy inputs; (iii) explicit source/key/execution/transport/authority alias topologies; (iv) frozen common-cause fault transformations; (v) learned models frozen before held-out unseen-fault and topology evaluation; and (vi) exact finite-population unsafe-proceed and false-conservative-hold outcomes. This negative search observation is not proof of novelty and should not be interpreted as an exhaustive claim of priority.

### 2.5 Spacecraft recovery architecture substrate

Study 7E uses NASA core Flight System documentation as an architecture substrate rather than as scientific validation. cFS is a reusable embedded flight-software framework built around cFE services and application-level components [9], [10]. The reference design uses cFE Software Bus concepts for local publish/subscribe communication, Health & Safety as a bounded readiness/health source, and Software Bus Network concepts where the experimental topology requires cross-instance transport [11], [12]. NOS3 is retained as an integration and simulation reference but is not the selected Study-7E baseline [13].

The selected Study-7E environment is standalone cFS v7.0.1 at the frozen commit recorded in the protocol freeze. The architecture is explicitly a research reference implementation. It is not a NASA flight distribution, flight qualification, or operational mission validation.


### 2.6 Space-enabled critical-infrastructure context

The critical-infrastructure relevance of the study is architectural and service-enabling rather than a claim that the experiment models an entire infrastructure sector. U.S. space policy describes space systems as an essential component of critical infrastructure because they both provide important services directly and enable other infrastructure sectors and industries [22]. CISA identifies satellite as part of communications infrastructure and documents communications dependencies spanning energy, transportation, water and wastewater, emergency services, information technology, and financial services [23]. SPD-5 establishes cybersecurity principles for protecting space systems and supporting infrastructure [24].

Within that context, the experimental unit in this paper remains a spacecraft cyber-recovery decision. The study measures whether a modeled recovery gate proceeds unsafely or holds conservatively under specified evidence and trust-domain conditions. It does not simulate downstream telecommunications loss, financial disruption, transportation interruption, defense mission effects, or other cross-sector cascades. The infrastructure-protection contribution is therefore a bounded assurance result about the cyber-recovery layer of a space-enabled asset, not a system-level estimate of societal infrastructure resilience.

## 3. Two-Study Research Design

### 3.1 Scientific separation

The two studies are synthesized narratively but remain separate populations and provenance chains.

| Dimension | Study 7 / S7-LSO-001 | Study 7E / S7E-AERC-001 |
|---|---|---|
| Scientific role | information-sufficiency foundation | architecture-grounded prospective extension |
| Unit | modeled policy observation | architecture scenario with four policy decisions |
| Frozen evaluation population | 1,033 observations | 196 scenarios / 784 decisions |
| Policy information | eight base features; L1 additionally receives one corroboration bit | byte-identical base pair D0/L0 and byte-identical corroborated pair D1/L1 |
| Trust representation | stipulated corroboration condition | explicit source/key/execution/transport/authority domains |
| Learner | deterministic integer linear-threshold ERM | frozen scikit-learn decision trees |
| Architecture | abstract finite state model | cFS-grounded signed-evidence, qualifier, decision, and sink contracts |
| Primary assurance question | can learning escape an information boundary? | how do equal-information policies behave across trust topologies and faults? |

No combined sample size or pooled error rate is computed.

### 3.2 Study 7: visible state and adjudication

Study 7 uses eight binary policy-visible features:

1. signature validity;
2. source trust;
3. freshness;
4. epoch validity;
5. noncontradiction;
6. minimum evidence completeness;
7. security signal; and
8. visible authorization availability.

A separate hidden authorization variable is maintained by the research adjudicator and never supplied to the policies. Outside the collision block, hidden and visible authorization agree. In the collision block they may differ. This allows the experiment to create two states that are identical from the selector's perspective while different under research-only adjudication truth.

Three policies are evaluated.

- D0_S1_VISIBLE_ONLY is the fixed visible-only deterministic comparator.
- L0_ERM_VISIBLE_ONLY is learned from the same eight visible inputs.
- L1_ERM_WITH_INDEPENDENT_CORROBORATION receives the eight base inputs plus one corroboration bit.

Both learned policies use deterministic empirical-risk minimization over a bounded integer linear-threshold hypothesis class. The deliberately simple learner is an experimental control rather than an algorithmic contribution: it keeps the decision boundary inspectable so that information sufficiency can be separated from model capacity and optimization behavior. When adjudication states produce identical policy-visible inputs, increasing model complexity does not itself supply the missing distinguishing variable; additional decision-relevant information or a different observable state is required. The frozen L0 parameters are quality weight 2, authorization weight 1, security weight -1, and threshold 12. The frozen L1 parameters are quality weight 2, authorization weight 0, corroboration weight 1, security weight -1, and threshold 12. Both have zero training errors.

Study 7 has three finite blocks. Block A exhausts all 256 eight-feature visible states for D0 and L0, yielding 512 observations. Block B exhausts all 512 nine-feature states for L1. Block C contains three hidden-truth/corroboration scenarios crossed with all three policies, yielding nine observations. The total frozen population is 1,033 observations.

Primary endpoints are objective decision error, unsafe proceed, false-conservative hold, hidden-truth collision indistinguishability, and resolution of the independent-disagreement collision.

### 3.3 Study 7E: cFS-grounded reference architecture

Study 7E introduces a component and message-path interpretation for the recovery decision.

The architecture contains:

- a primary authorization producer;
- a corroborating authorization producer;
- a health/readiness source;
- a signed-evidence qualifier;
- a recovery decision application;
- a recovery-action sink;
- a research-only adjudicator and fault controller;
- cFE Software Bus for local message exchange; and
- SBN-style cross-instance transport where the topology requires separation.

The policy-visible path and research-only truth path are deliberately separated. The adjudicator retains true authorization, true health/readiness, topology identity, fault identity, and domain aliasing. Those fields are prohibited from policy input.

The objective action is defined prospectively:

ENTER_RECOVERY_GATE if and only if security signal, true authorization, and true health readiness are all one; otherwise HOLD.

The cFS engineering qualification path compiled and executed the producer bridge, signed-evidence qualifier, deterministic D0/D1 binding, and recovery sink on the selected standalone cFS baseline. It demonstrated a nominal signed-evidence path, fail-closed behavior for post-signature transport corruption, sticky equivocation detection for the execution-compromise construction, and malformed-ingress rejection. No Study-7E scientific scenario was executed during that engineering qualification.

The canonical held-out scientific inference is therefore best described as **cFS-grounded, not flight-software-in-the-loop learned inference**. The frozen architecture and evidence contracts are grounded in the cFS implementation surfaces, while held-out policy evaluation uses frozen deterministic rules and hash-verified decision-tree model artifacts in a bound Python environment, with an independently implemented semantic-tree interpreter auditing learned decisions.

### 3.4 Equal-information policy contracts

Study 7E defines two policy-visible feature sets.

The base vector has nine fields:

- primary_signature_valid;
- primary_source_trusted;
- primary_fresh;
- primary_epoch_valid;
- primary_noncontradictory;
- primary_complete;
- primary_authorization;
- health_ready; and
- security_signal.

D0_BASE and L0_BASE receive exactly this vector.

The corroborated vector adds seven corroborator fields:

- corr_signature_valid;
- corr_source_trusted;
- corr_fresh;
- corr_epoch_valid;
- corr_noncontradictory;
- corr_complete; and
- corr_authorization.

D1_CORROBORATED and L1_CORROBORATED receive exactly this extended vector.

For every held-out scenario, the serialized input bytes given to D0 and L0 must hash identically, and the serialized input bytes given to D1 and L1 must hash identically. A mismatch invalidates the scenario. The held-out execution satisfied this invariant for all 196 scenarios.

D0 proceeds only when all six primary evidence-quality conditions, primary authorization, health readiness, and the security signal are true. D1 adds the requirement that all six corroborator evidence-quality conditions and corroborator authorization are also true.

L0 and L1 are frozen decision-tree classifiers trained under one fixed learner protocol. Both use scikit-learn 1.9.1 in Python 3.11.16 with the same predeclared hyperparameter rule and no post-evaluation tuning. The frozen L0 semantic tree has 11 nodes and maximum depth 4; L1 has 15 nodes and maximum depth 5.

### 3.5 Trust-domain topology

Each evidence path is assigned experimental identifiers for five domains:

- source;
- signing key;
- execution;
- transport; and
- authorization authority.

The five frozen topologies progressively separate these domains.

| Topology | Separate domains |
|---|---|
| T0_SHARED_ALL | none |
| T1_SEPARATE_SOURCE_EXEC | source, execution |
| T2_SEPARATE_SOURCE_KEY_EXEC | source, key, execution |
| T3_SEPARATE_THROUGH_TRANSPORT | source, key, execution, transport |
| T4_SEPARATE_ALL | source, key, execution, transport, authority |

"Separate" means separate experimental domain identifiers and implementation instances as defined by the protocol. It does not mean operational, organizational, statistical, physical, or certification-grade independence.

### 3.6 Fault profiles

Thirteen fault profiles are frozen before evaluation:

- F0 nominal;
- F1 primary source false;
- F2 corroborator source false;
- F3 primary key compromise;
- F4 corroborator key compromise;
- F5 primary freshness delay;
- F6 corroboration freshness delay;
- F7 primary message loss;
- F8 corroboration message loss;
- F9 primary transport compromise;
- F10 primary authority compromise;
- F11 compound authority plus transport compromise; and
- F12 primary execution compromise.

Fault propagation follows domain aliasing. For example, an authority compromise can affect both evidence paths while the authority domain remains shared. F9 is implemented as a post-signature body mutation, and F12 uses separately signed same-sequence opposite-authorization bodies to exercise path-local equivocation behavior.

### 3.7 Training, model freeze, and held-out evaluation

Study 7E has 84 training scenarios:

- TR1: 72 security-response scenarios across T0-T2 and F0-F5;
- TR0: 12 no-security-signal baseline scenarios across T0-T2.

The frozen labels contain 66 HOLD and 18 ENTER_RECOVERY_GATE outcomes. E1, E2, and C0 are prohibited from training.

The held-out evaluation contains:

- E1 unseen fault classes: 84 scenarios over T0-T2 and F6-F12;
- E2 held-out topology transfer: 104 scenarios over T3-T4 and F0-F12;
- C0 held-out-topology no-signal controls: 8 scenarios over T3-T4 and F0.

The total is 196 held-out scenarios and 784 policy decisions.

Primary learned inference uses the hash-verified frozen joblib artifacts under the bound dependency environment. Independent audit uses a pure semantic-tree interpreter over frozen canonical semantic JSON rather than deserializing the primary joblib. Research truth and topology/fault metadata are joined only after policy inputs are captured and decisions emitted.

A scenario is valid only when topology and domain aliasing are recorded, the intended fault is confirmed, equal-information hashes match, research truth is absent from inputs, all four decisions are emitted, primary and audit learned actions agree, sink scenario identity matches, and provenance is complete. Final aggregate release requires zero invalid scenarios.

The execution of record satisfied all validity conditions: 196 valid scenarios, 784 decisions, zero invalid scenarios, and zero audit mismatches.


### 3.8 AI-assisted research-development provenance

OpenAI ChatGPT, accessed through the ChatGPT web interface, was used before the relevant result freezes as an interactive assistant for protocol refinement, code and test drafting, repository documentation, and verification-oriented review. The author selected and approved the research questions, protocol, endpoints, model and evaluation boundaries; controlled the repository; authorized the experimental executions; and independently checked the frozen outputs and numerical claims against repository evidence. ChatGPT did not act as an author, did not autonomously execute or authorize the frozen scientific campaigns, and did not alter the accepted Study 7 or Study 7E result populations after freeze. The separate use of ChatGPT during manuscript preparation is disclosed before the References in accordance with Elsevier policy.

## 4. Results

### 4.1 Study 7: exact information-sufficiency results

In Study-7 Block A, D0 and L0 each evaluate all 256 visible states. Both have zero objective decision errors, zero unsafe proceeds, zero false-conservative holds, and three proceed decisions. L0 therefore reproduces the complete visible decision boundary, not only the training prototypes.

In Block B, L1 evaluates all 512 extended visible states. It has exactly two objective errors: one unsafe proceed and one false-conservative hold. Both occur when visible authorization and corroboration disagree in an otherwise fully qualifying security state.

Block C contains the hidden-truth collision.

| Scenario / block | D0 result | L0 result | L1 result | Interpretation |
|---|---|---|---|---|
| SAFE_CORROBORATED | correct proceed | correct proceed | correct proceed | visible and hidden authorization agree |
| V5_INDEPENDENT_DISAGREEMENT | unsafe proceed | unsafe proceed | correct hold | corroboration distinguishes hidden-false state |
| V5_CORRELATED_FALSE_CORROBORATION | unsafe proceed | unsafe proceed | unsafe proceed | corroboration shares the false condition |

The full exact Study-7 counts are:

| Block | Policy | N | Errors | Unsafe proceed | False-conservative hold | Proceed |
|---|---|---:|---:|---:|---:|---:|
| A | D0 | 256 | 0 | 0 | 0 | 3 |
| A | L0 | 256 | 0 | 0 | 0 | 3 |
| B | L1 | 512 | 2 | 1 | 1 | 6 |
| C | D0 | 3 | 2 | 2 | 0 | 3 |
| C | L0 | 3 | 2 | 2 | 0 | 3 |
| C | L1 | 3 | 1 | 1 | 0 | 2 |

Study 7 therefore answers the foundation question in two parts. Learning the visible rule exactly does not provide information absent from the visible state. Adding corroboration changes the information available to the selector, but its benefit depends on whether that added evidence distinguishes or shares the compromised condition.

### 4.2 Study 7E: aggregate held-out outcomes

Study 7E produced the following exact aggregate counts over 196 held-out scenarios per policy.

| Policy | Objective errors | Unsafe proceed | False-conservative hold | ENTER | HOLD |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

These counts do not support a global policy ranking. D1 has the fewest unsafe proceeds but the most false-conservative holds and the most total objective errors. L1 has the most unsafe proceeds but the fewest false-conservative holds. A single aggregate error total would therefore conceal materially different safety/availability behavior.

### 4.3 Held-out block results

Block-level exact counts, written as errors / unsafe proceed / false-conservative hold, are:

| Block | D0_BASE | L0_BASE | D1_CORROBORATED | L1_CORROBORATED |
|---|---|---|---|---|
| E1 unseen faults, n=84 | 18 / 3 / 15 | 21 / 9 / 12 | 24 / 3 / 21 | 17 / 11 / 6 |
| E2 held-out topologies, n=104 | 22 / 6 / 16 | 26 / 12 / 14 | 25 / 1 / 24 | 26 / 20 / 6 |
| C0 no-signal controls, n=8 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

C0 is a substantive null/control result: all four policies returned HOLD in all eight no-security-signal scenarios, with zero objective errors.

### 4.4 Equal-information deterministic/learned disagreement

Because paired input bytes are identical, within-pair disagreement isolates selector behavior from information access.

D0 and L0 disagree in:

- 67 of 196 scenarios overall;
- 27 of 84 E1 scenarios;
- 40 of 104 E2 scenarios; and
- 0 of 8 C0 scenarios.

D1 and L1 disagree in:

- 72 of 196 scenarios overall;
- 29 of 84 E1 scenarios;
- 43 of 104 E2 scenarios; and
- 0 of 8 C0 scenarios.

These disagreements do not establish that either selector class is globally better. They establish that learned and deterministic selectors can produce materially different decisions even when their policy-visible evidence is byte-identical.

### 4.5 Corroboration trade-offs within policy class

Across all held-out scenarios, D1 minus D0 changes:

- unsafe proceed by -5; and
- false-conservative hold by +14.

L1 minus L0 changes:

- unsafe proceed by +10; and
- false-conservative hold by -14.

In E2 specifically, deterministic corroboration changes unsafe proceed by -5 and false-conservative hold by +8, while learned corroboration changes unsafe proceed by +8 and false-conservative hold by -8.

The directions are therefore opposite across the two policy classes. Corroboration cannot be characterized as a universal safety improvement from these data.

### 4.6 Topology-controlled trust separation

Aggregate topology comparisons can be confounded when fault sets differ. The frozen review therefore compares the common F6-F12 subset, in which each topology contributes 28 scenarios.

| Policy | T0 error/unsafe/FCH | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| D0_BASE | 6/1/5 | 6/1/5 | 6/1/5 | 6/1/5 | 6/1/5 |
| D1_CORROBORATED | 8/1/7 | 8/1/7 | 8/1/7 | 8/1/7 | 7/0/7 |
| L0_BASE | 7/3/4 | 7/3/4 | 7/3/4 | 7/3/4 | 7/3/4 |
| L1_CORROBORATED | 5/3/2 | 6/4/2 | 6/4/2 | 6/4/2 | 8/6/2 |

The base policies are topology-invariant over this common subset. D1 changes only at fully separated T4, where one unsafe proceed is removed while seven false-conservative holds remain. L1 moves in the opposite direction: unsafe proceeds rise from 3/28 at T0 to 6/28 at T4.

Thus, increasing the number of experimentally separated domains does not produce a monotonic policy-level improvement.

### 4.7 Common-cause and adverse-transfer cases

F10, primary authority compromise, provides the clearest deterministic common-cause result. At T0-T3, authority remains shared. D0 and D1 each produce 2 errors / 1 unsafe proceed / 1 false-conservative hold per four scenarios. At T4, D0 remains 2/1/1 while D1 becomes 1/0/1. The deterministic corroboration advantage therefore disappears while authority is shared and reappears as a one-unsafe-proceed reduction when authority is separated.

The learned pair behaves differently. L0 and L1 are error-free under F10 at T0-T3, but at T4 L0 remains error-free while L1 incurs one unsafe proceed.

F11, compound authority plus transport compromise, does not reproduce the deterministic F10 unsafe contrast. D0 and D1 each remain at 1/0/1 across all topologies. L0 and L1 are error-free at T0-T3, while L1 incurs one unsafe proceed at T4.

F12, primary execution compromise, is an adverse learned-transfer counterexample. D0 and D1 each remain at 1/0/1 across topologies. L0 is error-free from T0 through T4. L1 is error-free at T0 but incurs one unsafe proceed at each T1-T4.

These cases prevent a simple narrative in which more domain separation automatically improves every selector.

### 4.8 Frozen Study-7E hypothesis disposition

| Hypothesis | Frozen disposition | Evidence |
|---|---|---|
| H1: equal-information comparison separates information advantage from policy behavior | SUPPORTED | equal paired hashes plus nonzero D0/L0 and D1/L1 disagreement |
| H2: increasing separation reduces targeted compromise propagation | PARTIALLY SUPPORTED | domain separation is instantiated, but endpoint improvement is non-monotonic |
| H3: shared/common authority can defeat corroboration | PARTIALLY SUPPORTED | F10 deterministic collapse at T0-T3 and one T4 recovery; not universal across F11/learned behavior |
| H4: separated corroboration may trade unsafe proceeds for conservative holds | PARTIALLY SUPPORTED | deterministic and learned classes move in opposite directions |
| H5: learned selectors may behave differently on unseen faults/topologies | SUPPORTED | E1/E2 differences and adverse topology-dependent transfer |

## 5. Discussion

### 5.1 Information sufficiency precedes model sophistication

Study 7 isolates a fundamental assurance distinction. L0 has zero training error and zero error over every ordinary eight-feature visible state, yet it does not avoid the hidden-truth collision. The reason is not failure to fit the visible rule. The safe and signed-but-false cases are identical in the inputs provided to the selector.

This result makes model-class escalation an incomplete response to a missing-information problem. A more expressive learner cannot be assumed to recover truth that is not represented in its observable state. The experiment deliberately uses a simple transparent learner so that this information boundary remains visible.

Study 7 also shows why adding a feature must be interpreted as an information intervention rather than proof of learning superiority. L1 changes the collision outcome only when its corroboration input distinguishes the hidden-false condition. When corroboration shares the false state, the unsafe decision returns.

### 5.2 Study 7E separates information access from selector behavior

The principal comparator asymmetry in Study 7 is removed in Study 7E. D0 and L0 receive the same base bytes; D1 and L1 receive the same corroborated bytes. The pair hashes match in all 196 held-out scenarios.

The observed 67 and 72 within-pair disagreements therefore cannot be explained by one policy receiving an extra corroboration field. They reflect differences in the selectors' frozen decision logic under the same observable state. This is an important assurance property because it permits policy-class behavior to be studied without conflating it with information access.

The result is still not a ranking. The learned and deterministic selectors distribute their errors differently. D1 is strongly conservative in aggregate; L1 enters the recovery gate much more frequently and consequently has fewer false-conservative holds but more unsafe proceeds. Whether that trade-off is desirable cannot be determined from the study without an externally justified utility or mission-cost function, which was intentionally not introduced post hoc.

### 5.3 Corroboration moves the trust boundary rather than removing it

The two studies tell a consistent but nontrivial story.

In Study 7, corroboration resolves the independent-disagreement collision because it changes the observable state. Correlated false corroboration defeats that benefit.

In Study 7E, corroboration is represented by its own evidence-quality and authorization fields and by domain relationships that can be shared or separated. Deterministic corroboration reduces aggregate unsafe proceeds but increases conservative holds. Learned corroboration does the opposite relative to its learned base policy. Under common fault/topology controls, these effects are not monotonic.

The appropriate conclusion is therefore not that corroboration is good or bad. It relocates and restructures trust. The benefit depends on what the corroborating path can observe, which failures it shares with the primary path, and how the selector interprets disagreements.

### 5.4 Domain separation is an architectural property, not a scalar safety score

Study 7E was designed to make "independence" inspectable rather than merely asserted. Source, key, execution, transport, and authority can be represented by separate or aliased experimental identifiers, and fault propagation follows those aliases.

This makes specific common-cause statements possible. Under F10, deterministic corroboration has no unsafe-proceed advantage while authority remains shared, but one unsafe proceed is removed when authority becomes separate at T4. That is a concrete architecture-specific result.

The same architecture does not imply that every selector improves as separation increases. L1's common F6-F12 unsafe count rises from 3/28 at T0 to 6/28 at T4, and F12 yields adverse L1 behavior at every topology where execution is separated. Greater domain separation can reduce one form of common-cause coupling while also presenting combinations of evidence not handled favorably by a frozen learned selector. Architecture and decision logic must therefore be assured together.

### 5.5 Held-out transfer should retain adverse results

Study 7E excludes E1, E2, and C0 from training and freezes both learned models before held-out inference. The resulting adverse findings are scientifically important.

F12 demonstrates that a change intended to reduce execution-domain aliasing does not guarantee a better learned decision. F10 and F11 show a similar T4 learned-policy counterexample. C0, by contrast, is a clean null result: no policy spuriously enters the recovery gate when the security signal is absent.

Retaining both adverse and null cases is part of the assurance argument. Removing difficult held-out cases after model freeze would convert the study from a prospective transfer evaluation into post-hoc optimization.

### 5.6 Implications for assurance practice

Within the limits of these modeled systems, the evidence suggests several practical assurance principles.

First, recovery-policy evaluation should record what each selector can actually observe. Comparing policy outcomes without an information-equivalence check can confuse information advantage with algorithmic behavior.

Second, corroboration should be accompanied by a trust-dependency model. Describing a second signal as independent is insufficient if source, key, execution, transport, or authority remain shared.

Third, common-cause faults should be evaluated explicitly. The F10 result would be invisible in an aggregate analysis that ignored whether authority was shared.

Fourth, safety and availability outcomes should remain separate unless a mission-specific utility function is defined prospectively. The D1 and L1 results show why total error alone can obscure qualitatively different failure modes.

Fifth, learned-policy transfer should be evaluated after model freeze on conditions excluded from training. The E1/E2 structure and semantic-tree audit make that boundary explicit.

These are experiment-grounded assurance recommendations, not certification rules.

## 6. Limitations

Both studies are deterministic finite research experiments. Their completeness applies to the defined modeled populations, not to all spacecraft cyber-recovery conditions. Operational telemetry benchmarks such as OPS-SAT are appropriate for evaluating anomaly-detection performance, but they do not expose the controlled adjudication truth, trust-domain aliasing, fault interventions, and paired equal-information semantics required by the present recovery-authorization questions. The finite controlled populations are therefore used to isolate information and trust boundaries before any future validation under noisy mission telemetry.

Study 7 uses binary features and a small deterministic linear-threshold learner. It does not evaluate neural networks, stochastic training, detector performance, continuous evidence, sensor noise, online adaptation, or distribution-shift probabilities. Its corroboration variable is a stipulated experimental condition rather than an implemented independent trust path.

Study 7E addresses that last limitation only within a bounded architecture model. Its five trust domains are experimental identifiers and implementation instances; they do not establish organizational, physical, statistical, cryptographic, or certification-grade independence in a deployed system. The selected cFS environment grounds message, qualification, deterministic-policy, and sink contracts, but the canonical learned held-out inference runs in a hash-bound Python/scikit-learn environment rather than as a flight-qualified onboard ML application. The study therefore should not be described as an end-to-end flight-software validation of learned recovery logic.

The objective action is prospectively defined from true authorization, true health readiness, and security signal. Those research-only truth variables are necessary for adjudication but are not measurements of real mission truth. Fault profiles F0-F12 are controlled research transformations rather than prevalence estimates for operational attacks.

No RF channel, ground-network latency, processor load, energy use, command-link reliability, human-operator behavior, or physical spacecraft dynamics are measured. No operational probability of unsafe recovery or false-conservative hold can be inferred from the exact finite-population counts.

The studies also do not define a scalar utility for trading unsafe proceeds against false-conservative holds. As a result, they intentionally stop short of declaring a global winning policy.

## 7. Reproducibility and Evidence Integrity

Study 7 is frozen under S7-LSO-001. Its accepted execution is bound to workflow run 33689625480 and commit f1530b0b2e81a5916adaf7ce808075156424dfb5. The result freeze records SHA-256 identities for the canonical outputs, and an independently written auditor reconstructs the learner search, objective, and all 1,033 policy decisions with zero mismatches. The Study-7 durable publication archive is identified by Zenodo version DOI 10.5281/zenodo.22732060.

Study 7E is frozen under protocol/environment freeze S7E-AERC-FREEZE-001, model freeze S7E-AERC-MODEL-FREEZE-001, and result freeze S7E-AERC-RESULT-FREEZE-001. The sole held-out execution of record is S7E-AERC-HELDOUT-EXEC-001, workflow run 35948870036, job 107472877604, source commit 1cbc4be58a99e9add139e73efc9ab42a4f275864. Its raw Actions artifact SHA-256 is cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35.

The held-out execution produced 196 scenarios and 784 decisions, with zero invalid scenarios and zero audit mismatches. Equal-information hashes, objective actions, endpoint counts, paired disagreements, topology/fault tables, and the output hash manifest were independently recomputed. The original 29,892-byte Actions ZIP is durably preserved in repository history as ordered base64 chunks whose reconstruction is validated against the original SHA-256 and archive-member hashes.

No Study-7 or Study-7E scientific execution is rerun for manuscript development.

## 8. Conclusion

Study 7 and Study 7E together separate three questions that are easy to conflate in cyber-recovery assurance: whether decisive information is observable, how a selector behaves given that information, and how the architecture creates or shares failure dependencies among evidence paths.

Study 7 shows that exact learning of a visible recovery rule does not eliminate a hidden-truth failure when the decisive distinction is absent from the policy-visible state. Corroboration can resolve that collision only when it supplies genuinely distinguishing information; correlated false corroboration restores the unsafe condition.

Study 7E then equalizes information between deterministic and learned comparators and grounds corroboration in explicit source, key, execution, transport, and authority domains. The held-out results show substantial deterministic/learned disagreement under identical inputs, opposite corroboration trade-offs across policy classes, a deterministic common-authority collapse under F10, adverse learned transfer under F12, and a clean C0 no-signal control. Greater experimental trust-domain separation is therefore not a scalar or monotonic safety intervention at the policy-output level.

The assurance implication is narrower than a policy recommendation: satellite cyber-recovery logic should be evaluated together with the information and trust architecture feeding it. Evidence provenance, domain sharing, common-cause faults, equal-information comparison, and held-out transfer can be as important to the safety argument as the choice of learned versus deterministic selector. For space-enabled critical infrastructure, this supports treating trustworthy recovery authorization as part of infrastructure protection and continuity assurance. The experiments do not estimate cross-sector cascading failures or operational infrastructure outage probabilities.


## Declarations

### CRediT authorship contribution statement

Aman Kumar Singh: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, and Project administration.

### Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

### Declaration of competing interest

The author declares that he has no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### Ethics statement

Not applicable. The studies did not involve human participants, identifiable human data, animals, or biological material.

### Data availability

The Study 7 protocol, canonical result records, policy summary, and separately implemented audit materials are publicly available in the mission-aware-satellite-cyber-recovery repository. The accepted Study 7 evidence is also preserved in the Zenodo dataset *Mission-Aware Satellite Cyber Recovery - Study 7 Learned Selector Observability Evidence*, version DOI 10.5281/zenodo.22732060 (concept DOI 10.5281/zenodo.22732059). Study 7E protocol, model-freeze, held-out evaluation, result-freeze, exact endpoint, audit, and durable raw-artifact preservation records are maintained in the same public repository. No confidential, proprietary, or human-subject data are used.

### Code availability

The protocol implementations, analysis code, validation code, model-freeze records, and separately implemented audit code for Study 7 and Study 7E are available at https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. Exact scientific execution identities and frozen hashes are recorded in the repository freeze manifests.

### Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, the author used OpenAI ChatGPT to support literature organization and source discovery, manuscript structuring and drafting, consistency and compliance checking, and language refinement. The author reviewed and edited the AI-assisted material, verified references and quantitative claims against primary sources and frozen repository evidence, and takes full responsibility for the content of the publication.

## References

[1] Space Attack Research and Tactic Analysis (SPARTA), "Cyber-safe Mode," Countermeasure CM0044, The Aerospace Corporation. Available: https://sparta.aerospace.org/countermeasures/CM0044

[2] A. Singh, *Mission-Aware Satellite Cyber Response and Trusted Recovery — Study 2 Phase-6 Source Evidence*, dataset, Zenodo, ver. 1.0.0, Sep. 4, 2026, doi: 10.5281/zenodo.22289114.

[3] A. Agogino et al., *Recommendations on Evidence and Process for Certification of Learning-enabled Components in Aerospace Systems*, NASA Technical Memorandum, Document ID 20240006865, Jun. 7, 2024. Available: https://ntrs.nasa.gov/citations/20240006865

[4] B. Ruszczak, K. Kotowski, D. Evans, et al., "The OPS-SAT benchmark for detecting anomalies in satellite telemetry," *Scientific Data*, vol. 12, Art. no. 710, 2025, doi: 10.1038/s41597-025-05035-3.

[5] A. Fejjari, A. Delavault, R. Camilleri, and G. Valentino, "Transformer-based anomaly detection for satellite telemetry data," *Acta Astronautica*, vol. 238, Part A, pp. 739-745, 2026, doi: 10.1016/j.actaastro.2025.09.035.

[6] N. Kuhn, B. Sánchez Gómez, N. Moreno Blasco, P. Caserman, and F. Antonello, "Validation-gated continual learning for anomaly detection in satellite telemetry," *Acta Astronautica*, vol. 249, pp. 971-985, 2026, doi: 10.1016/j.actaastro.2026.07.065.

[7] H. S. Le, B. Juba, and R. Stern, "Learning Safe Action Models with Partial Observability," *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 38, no. 18, pp. 20159-20167, 2024, doi: 10.1609/aaai.v38i18.29995.

[8] H. Jing and Y. Nakahira, "Safety Certificate against Latent Variables with Partially Unidentifiable Dynamics," *Proceedings of the 42nd International Conference on Machine Learning*, PMLR, vol. 267, pp. 28288-28303, 2025. Available: https://proceedings.mlr.press/v267/jing25b.html

[9] NASA Goddard Space Flight Center, "Core Flight System (cFS)," NASA Software Catalog, GSC-18719-1. Available: https://software.nasa.gov/software/GSC-18719-1

[10] NASA Goddard Space Flight Center, "Core Flight Executive Version 6.7," NASA Software Catalog, GSC-18128-1. Available: https://software.nasa.gov/software/GSC-18128-1

[11] NASA Goddard Space Flight Center, "Health and Safety (HS)," NASA Software Catalog, GSC-18476-1. Available: https://software.nasa.gov/software/GSC-18476-1

[12] NASA Goddard Space Flight Center, "Software Bus Network (SBN)," NASA Software Catalog, GSC-16917-1. Available: https://software.nasa.gov/software/GSC-16917-1

[13] NASA, "NASA Operational Simulator for Small Satellites (NOS3)," NASA Software Catalog, GSC-17737-1. Available: https://software.nasa.gov/software/GSC-17737-1

[14] J. Curbo and G. Falco, "Attack Surface Analysis for Spacecraft Flight Software," in *Proc. 2024 IEEE 10th International Conference on Space Mission Challenges for Information Technology (SMC-IT)*, pp. 22-30, 2024, doi: 10.1109/SMC-IT61443.2024.00010.

[15] R. McAmis, C. Willison, R. Skowyra, and S. Mergendahl, "The Compromised Satellite Peripheral Dilemma," *Workshop on the Security of Space and Satellite Systems (SpaceSec 2026)*, 2026, doi: 10.14722/spacesec.2026.23045.

[16] J. Vanlyssel, G.-C. Roman, K. Cook, S. Rahaman, and A. Anwar, "Trust Without Boundaries: An Architectural Analysis of Satellite Flight Software," arXiv:2608.14532, 2026. Preprint.

[17] S. Shigol, R. Peled, A. Shapira, Y. Elovici, and A. Shabtai, "Risk Assessment for ML-Based Applications in Satellite Systems," *Workshop on the Security of Space and Satellite Systems (SpaceSec 2026)*, 2026, doi: 10.14722/spacesec.2026.23005.

[18] F. Belali, A. Essetty, and S. Bah, "S-LARF: Layered Adversarial Resilience Framework for spaceborne anomaly detection," *International Journal of Critical Infrastructure Protection*, 2026, Art. 100851, doi: 10.1016/j.ijcip.2026.100851.

[19] M. Juliato and C. Gebotys, "A methodology for secure recovery of spacecrafts based on a trusted hardware platform," *Advances in Space Research*, vol. 59, no. 4, pp. 1077-1094, 2017, doi: 10.1016/j.asr.2016.11.014.

[20] O. Driouch, S. Bah, and Z. Guennoun, "A Holistic Approach to Build a Defensible Cybersecurity Architecture for New Space Missions," *New Space*, vol. 11, no. 4, pp. 203-218, 2023, doi: 10.1089/space.2022.0029.

[21] D. M. Phillips, T. A. Mazzuchi, and S. Sarkani, "An architecture, system engineering, and acquisition approach for space system software resiliency," *Information and Software Technology*, vol. 94, pp. 150-164, 2018, doi: 10.1016/j.infsof.2017.10.006.

[22] Executive Office of the President, *United States Space Priorities Framework*, Dec. 2021. Available: https://www.whitehouse.gov/wp-content/uploads/2021/12/united-states-space-priorities-framework-_-december-1-2021.pdf

[23] Cybersecurity and Infrastructure Security Agency, "Communications Systems," Infrastructure Dependency Primer. Available: https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/resilience-services/infrastructure-dependency-primer/learn/communications

[24] U.S. Department of Commerce, Office of Space Commerce, "President Signs Space Cybersecurity Policy Directive," Sep. 4, 2020. Available: https://space.commerce.gov/president-signs-space-cybersecurity-policy-directive/
