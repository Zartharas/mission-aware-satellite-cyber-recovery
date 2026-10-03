# Residual Trust Boundaries in Satellite Cyber-Recovery Qualification: Temporal Evidence, Producer Composition, and Artifact Assurance

> **CEAS Space Journal — R2 substantive author-review manuscript (NOT a submitted manuscript).**
>
> Source authority: Paper-2 venue-neutral R4, git blob `069e319864b1f5c1ee201b31872e68572fea1923`, and CEAS R1, blob `a16fba122ad1b42a54c26bffee68ff05ad477b51`. This R2 changes editorial framing, application mapping and reference disposition only; Studies 3, 4 and 6, subordinate S3X/S6X evidence and original Figure 1 remain frozen and separate.
>
> Article type proposed: Original Research Article. Publication route planned: traditional subscription (no APC); neither article type nor publication choice has been submitted to the publisher.

**Aman Kumar Singh** — sole author  
Independent Researcher, The Woodlands, Texas, United States  
**Correspondence:** [Insert verified active email in private publisher-facing title page]  
**ORCID:** [Confirm the author's ORCID before publisher-facing export]

## Abstract

Satellite cyber-recovery qualification depends on evidence available to an authorization gate, which may establish less than the correctness of the state being approved. We quantify two consequences through independently frozen finite models. Study 4 evaluates 4,608 observations under 18 producer-voting and provenance rules: an all-domain constraint can delay systematic unsafe qualification without moving first unsafe failure, while also reducing tolerance to benign evidence loss. Study 6 evaluates 420 observations: combining six artifact-assurance signals reduces the prespecified incorrect artifact states qualified from four of five under signature-only checking to one of five under the composite gate; the benign unavailable-evidence subsets rejected increase from 32 of 64 to 63 of 64. Study 3 independently distinguishes bounded use of truthful but stale authorization evidence from false claims validly signed by a compromised trusted producer. A separate timing sensitivity analysis uses 1,919 selected extreme European Space Agency telemetry inter-sample intervals only as evidence-refresh-hiatus proxies, not measured communications outages. A separate executable existence demonstration uses pinned NASA core Flight System/Limit Checker source and a researcher-introduced equality-boundary change: the research functional harness distinguishes clean and altered artifacts, although their six deliberately restricted gate-visible signals are equivalent. The engineering contribution is a reproducible mapping between a satellite recovery qualification rule, the property warranted by its visible evidence, and its remaining trust assumption. The three core models and two supporting analyses are independent; none implements an end-to-end operational spacecraft recovery.

**Keywords:** Aerospace cybersecurity, cyber-recovery qualification, evidence qualification, trust management, telemetry timing, software supply-chain assurance.

## 1 Introduction

A spacecraft recovery controller must decide whether to authorize progression using available records rather than direct access to every relevant fact. Signed authorization evidence may be stale; producer agreement may come from correlated trust domains; and an approved recovery image may satisfy release controls while still containing an incorrect behavior. Intermittent evidence receipt and limited post-launch physical access make these distinctions relevant to mission-security requirements [1], [2]. The assurance question is therefore concrete: **which properties does the evidence admitted to a recovery gate actually establish, and which failure remains outside that observation set?**

Two exact finite findings motivate the investigation. First, Study 4 shows that adding a three-domain provenance constraint to a three-vote rule changes the compromised-producer count for *systematic* unsafe qualification from three to six, while its *first* unsafe count remains three. The same change moves the first benign-unavailability rejection from five affected producers to two. Second, in Study 6, a six-signal artifact gate reduces the prespecified incorrect states still qualified from four of five under signature-only checking to one of five, but rejects 63 of 64 benign unavailable-signal subsets rather than 32 of 64. These denominators enumerate designed finite states, not spacecraft incidence rates. They expose two different engineering tasks: specify the independence represented by provenance and specify the availability cost of mandatory assurance signals.

Published aerospace work supplies the context. Satellite cybersecurity spans spacecraft, ground and communications segments [3], [4]; flight-software security requirements [5], selected zero-trust satellite scenarios [6], and supplier-origin telemetry manipulation [7] address complementary concerns. NIST and NASA place cybersecurity within spacecraft mission risk and recovery assurance [2], [8]. SPARTA describes cyber-safe operation from a validated, integrity-protected baseline [9]. Remote attestation distinguishes evidence, appraisal and the relying-party decision [10]; quorum research establishes threshold/failure trade-offs [11], [12]; and published software supply-chain mechanisms specify signatures, digests, provenance and build assurance [13]–[3]. Our contribution is an exact study-specific qualification-failure map rather than a claim that these established mechanisms or legitimate-looking false telemetry are new.

We ask: **Across separately evaluated temporal, producer-composition and recovery-artifact layers, which modeled failures remain invisible to a satellite cyber-recovery qualification decision?** We answer through three independently frozen finite experiments, each with its own adjudication state and observational unit:

- **Study 3 — temporal evidence:** 1,380 trajectories and 67,620 epoch states distinguish truthful-cache exposure, invalid post-signature alteration and false-but-valid trusted-producer claims.
- **Study 4 — producer composition:** 4,608 rule-by-subset observations across 18 voting/provenance rules quantify first versus systematic unsafe qualification and the matching benign-unavailability cost.
- **Study 6 — recovery-artifact assurance:** 420 observations identify which prescribed incorrect artifact states remain qualified under six increasingly composed evidence gates and enumerate benign unavailable-signal subsets.

Two subordinate investigations probe particular boundaries without enlarging those core populations. **S3X** is a timing sensitivity analysis using 1,919 extreme European Space Agency (ESA) telemetry inter-sample intervals as imposed evidence-refresh-hiatus proxies; the source does not provide cyberattack or radio-contact labels. **S6X** is an executable existence demonstration using pinned NASA core Flight System (cFS)/Limit Checker (LC) source, one researcher-introduced source change and research-controlled assurance records. It illustrates the deliberately constrained Study-6 observation set and is not an independent empirical replication.

The individual questions are RQ1 (temporal evidence and the trusted-producer boundary), RQ2 (producer and provenance composition under compromise versus benign loss), and RQ3 (artifact-assurance residuals and their benign-evidence costs). The first two quantitative contributions are the Study-4 subset-dependent compromise/availability map and the Study-6 state-by-state assurance trade-off. Study 3 separates freshness failure from producer-origin semantic falsity. Their synthesis yields an **assurance-contract interpretation**: the origin, freshness, independence, correctness property and missing-evidence behavior of every mission-specific gate input must be specified before a qualification decision is relied on. The paper evaluates three independent models, not a connected spacecraft architecture, common pooled sample or operational success probability.

## 2 Related Work and Scientific Positioning

### 2.1 Space-system security and recovery assurance

Spacecraft cyber protection combines flight-software, ground and communications trust with mission-specific availability constraints [1], [14], [15], [2], [8]. Curbo and Falco describe testable flight-software cyber requirements [5]; Utsash et al. investigate selected zero-trust controls for satellite attack scenarios [6]. In *Silent Subversion*, published supplier-origin telemetry manipulation shows how a compromised onboard component can produce plausible evidence to downstream ground tooling [7]. This article studies a distinct dependent variable: whether a specified qualification rule can distinguish an incorrect hidden state from a correct one using its declared evidence.

SPARTA's CM0044 describes cyber-safe-mode recovery from a validated integrity-protected configuration [9]. That guidance motivates examining what signing and baseline approval warrant at the qualification boundary, without suggesting that signature validity alone is intended to certify semantic correctness.

### 2.2 Evidence appraisal, freshness and producer truth

RFC 9334 separates the Attester, evidence, Verifier and relying-party roles [10]. For Study 3, a recent validly signed record and the underlying authorization truth are different variables; freshness addresses one part of appraisal, whereas compromised producer semantics require a different trust assumption. Study 4 models **multiple evidence producers evaluated by one modeled gate**, a different question from multi-Verifier coordination.

### 2.3 Quorum and provenance composition

Published quorum results characterize consistency, threshold structure and fault assumptions [11], [12]. The Study-4 contribution lies in the exhaustive first/systematic failure map for seven producers in three explicitly synthetic domains under 18 vote/domain rules. The modeled domain label is a hypothesized trust-separation property, not evidence that actual spacecraft organizations or devices fail independently.

### 2.4 Recovery-artifact assurance

in-toto establishes supply-chain metadata provenance [13]. The Update Framework specifies signed update metadata and associated trust controls [16], while SLSA publishes source/build requirements and discusses the threat of malicious provenance producers [17], [3]. Study 6 deliberately holds six analogous visible signals fixed and enumerates which five prescribed incorrect artifact states remain acceptable under each gate. It neither certifies a real supplier nor supersedes those standards.

### 2.5 Satellite telemetry and timing-proxy construct validity

The separately frozen timing sensitivity analysis derives inter-sample intervals from the ESA Anomaly Dataset [4]. Published CEAS studies show both that spacecraft telemetry evaluation needs careful methodological interpretation [18] and that explicitly synthetic satellite telemetry offers a distinct tool for reproducible method studies [19]. These publications concern anomaly methods and synthetic telemetry; they do not validate the present selected extreme intervals as real recovery-evidence refresh gaps. Here the timestamps perturb a specified decision model, while authorization and signature states remain researcher-defined.

## 3 Common Qualification Framework and Study Separation

Let E_j denote the policy-visible evidence for study j and let Q_j(E_j) be the fixed qualification decision. Let T_j denote the research-only adjudication state: hidden authorization truth in Studies 3 and 4, and objective recovery-artifact correctness in Study 6. T_j is never supplied to the modeled qualification decision.

The generic unsafe-qualification condition is:

U_j = 1[Q_j(E_j) = 1 and T_j = 0].

Where benign evidence loss is studied separately, the false-conservative condition is:

C_j = 1[Q_j(E_j) = 0 and T_j = 1].

These expressions provide a common manuscript vocabulary, not a pooled endpoint. Each study retains its own frozen unit, interventions, state space, and outcome definitions.

**Table 1** Qualification layers and frozen populations

| Evidence layer | Experiment | Research-only adjudication | Principal visible evidence | Population | Contact/timing treatment |
|---|---|---|---|---:|---|
| Temporal runtime evidence | Study 3, S3-K4E-001 | Hidden authorization | Signature, claim, freshness, record availability, security signal | 1,380 trajectories | K0 continuous and synthetic K4 contact |
| External timing stress test | S3X-ETA-001 | Hidden authorization in frozen Study-3 semantics | Same B0/B2/S1 semantics; ESA timing structure only | 34,542 cases over 1,919 intervals | Empirical-hiatus proxy vs matched immediate-refresh control |
| Producer composition | Study 4, S4-MPQ-001 | Hidden authorization | Signed producer claims, vote threshold, synthetic provenance-domain count | 4,608 observations | No contact model |
| Artifact assurance | Study 6, S6-SCTR-001 | Objective baseline correctness | Signature, digest, provenance, reproduced build, review, approval | 420 observations | No contact model |
| Executable artifact-assurance stress test | S6X-EAP-001 | External research functional adjudication | Same six Study-6-aligned qualification signals; functional harness remains outside the gate | 396 observations/repetition × 2 deterministic repetitions | No contact model |

The arithmetic sum of these populations is not a meaningful sample size. Study 3 uses trajectories, S3X uses interval-policy-evidence-arm cases, Study 4 uses rule-by-subset observations, and Study 6 uses artifact-state and assurance-unavailability observations. No pooled N, pooled rate, pooled confidence interval, or combined policy score is defined.

Fig. 1 summarizes the three residual trust boundaries at the level of the qualification observation set. The panels compare mechanisms qualitatively; they are not sequential recovery stages, do not exchange experimental outputs, and do not share a pooled denominator. The subordinate S3X inset supplies external timing structure for the Study-3 mechanism. S6X separately instantiates the Study-6 artifact residual with executable evidence, as reported in Table 5, without becoming a fourth main panel.

![Fig. 1. Three separately evaluated residual trust boundaries in satellite cyber-recovery qualification.](../Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg)

**Fig. 1** Residual trust boundaries across three separately frozen qualification studies. (a) Temporal evidence (Study 3), including the subordinate S3X timing-proxy stress test: a truthful pre-onset cache can create bounded B0 exposure, while a false-but-valid trusted-producer claim can survive signature-only qualification; the ESA intervals are evidence-refresh proxies, not observed RF/contact outages. (b) Producer composition (Study 4): vote thresholds and synthetic provenance-domain requirements change first/systematic failure and benign-unavailability boundaries conditionally, not monotonically. (c) Recovery-artifact assurance (Study 6): composition excludes modeled integrity/provenance failures but leaves `APPROVED_BAD_SOURCE` when all six gate-visible signals remain true. The panels present a qualitative, nonpooled synthesis, not a serial architecture or a globally preferred rule. S6X is a separate executable stress test of the Study-6 residual, documented in Table 5; it is neither an additional Figure-1 panel nor an external empirical replication.


### 3.1 Illustrative engineering allocation and trust assumptions

For a future spacecraft design review, the abstract variables can be allocated to proposed interfaces without implying that these experiments implemented or validated such a system. Hidden authorization truth corresponds to the mission-defined permissible flight-software or recovery state; an onboard health/attestation component or a ground verification service could emit signed evidence about that state. A reception and cache path would provide the timestamp and freshness context at the relying-party gate. Study 4's producers could conceptually correspond to separately administered onboard, ground and software-release evidence origins, but the tested D1/D2/D3 separation is **synthetic** and requires mission-specific evidence of failure independence. A ground-side or appropriately authorized onboard recovery controller would apply the declared gate to its admitted evidence. Study 6's signatures, digests, provenance, reproduced build, review and approval correspond to candidate release-assurance records. The S6X functional harness represents an **external research adjudicator**, not a seventh signal currently available to the gate.

A spacecraft implementation would need to verify, in order: what hidden authorization state each record claims; who owns each signing key and attestation root; how evidence arrives and expires; whether producer domains can fail jointly; which requirements fail closed on missing signals; and whether objective functional correctness is to be an independently established, *gate-visible* requirement. This is a requirements-to-component mapping and validation agenda, not a deployed or experimentally integrated architecture.

### 3.2 Manuscript preparation disclosure

OpenAI ChatGPT (GPT-5.6 Sol) materially assisted manuscript restructuring, drafting, editorial revision, claim-to-source organization and preparation scripts. It neither generated nor altered frozen experiment results. The sole human author checked the evidence identities, model arithmetic, references and claims and accepts responsibility for the final scientific and editorial content.

## 4 RQ1 — Temporal Evidence and the Trusted-Producer Boundary

The temporal experiment is the core result of RQ1. The separate ESA-derived analysis tests its timing sensitivity under deliberately selected extreme inter-sample intervals.

### 4.1 Study-3 Design

Study 3 evaluates 30 frozen cells crossed with 46 onset phases, yielding 1,380 trajectories. Hidden authorization is true before onset and false at and after onset. The selector never receives hidden authorization directly.

The evidence treatments separate three mechanisms:

- **V0:** truthful post-onset evidence reports authorization false with a valid signature.
- **V4:** post-signature value manipulation changes the signed post-onset value and invalidates the affected signature.
- **V5:** a compromised trusted producer reports authorization true and validly signs the false claim.

K0 represents continuous modeled contact. K4 contains four synthetic intermittent-contact windows. These are model treatments, not orbital pass schedules or measured ground-station access.

### 4.2 Study-3 Finding: Integrity Failure and Semantic Failure Are Different

Under persistent V5/K0, both B0 and S1 are unsafe-qualified in all 46 onset trajectories, with mean exposure of 122.5 logical seconds. B2 is 0/46 in that frozen cell. The signature remains valid because the trusted producer itself signs the false authorization claim.

Under persistent V5/K4, B0 remains unsafe-qualified in 46/46 trajectories with mean exposure of 55.326 logical seconds; S1 remains unsafe-qualified in 46/46 with mean exposure of 49.022 logical seconds. B2 remains 0/46. The K4 restriction therefore reduces selected exposure for B0/S1 without eliminating the V5 boundary.

V4 behaves differently. The affected post-signature manipulation invalidates the signature, so the affected V4 record does not qualify. Any B0/K4 false qualification in V4 cells originates instead from a still-fresh truthful pre-onset record.

The temporal result is therefore not simply “stale data are risky.” Study 3 separates two mechanisms:

1. **freshness-origin exposure:** a truthful pre-onset record remains temporarily usable after hidden truth changes;
2. **producer-origin semantic falsity:** a compromised trusted producer supplies a fresh, validly signed false claim.

### 4.3 Truthful Cache Boundary

Under truthful V0/K4/B0, 3 of 46 onset trajectories contain unsafe qualification, with mean exposure of 0.326 logical seconds, all attributed to PRE_ONSET_CACHE. S1 and B2 have no truthful-V0 false qualification under K4.

These values are exact properties of the frozen Study-3 grid. They are not estimates of real spacecraft cache staleness or operational delay.

### 4.4 Supporting external-timing sensitivity analysis (S3X)

S3X asks whether the Study-3 distinction survives when evidence-refresh timing is driven by an externally sourced, separately frozen telemetry interval population rather than the synthetic K4 schedule.

The source is ESA Anomaly Dataset v2 [4]. Missions 1 and 2 contribute 176 telemetry channels. The imposed P99_X10 subset deliberately emphasizes extreme positive intervals; this selection is a sensitivity stress condition and is not intended to represent the distribution of operational link availability. A prespecified eight-rule cadence-sensitivity analysis was performed; P99_X10 was selected after that analysis and then frozen before timestamp-trace extraction and recovery replay. The resulting trace population contains 1,919 positive inter-sample intervals satisfying the strict relation:

delta_seconds > 10 × cadence_p99_seconds.

For each frozen interval i:

g_i = delta_seconds_i / cadence_p99_seconds_i,

so every selected interval satisfies g_i > 10.

The empirical-hiatus arm uses the interval only as a modeled evidence-refresh hiatus: no new record arrives for 0 < q < g_i, and the first refresh occurs at q = g_i. The matched control refreshes at q = 0. The adapter preserves the Study-3 B0/B2/S1 decision semantics. ESA provides none of the V0/V4/V5 trust labels; those remain modeled factors.

The complete extension grid contains:

1,919 intervals × 3 policies × 3 evidence states × 2 timing arms = 34,542 cases.

A separately implemented repository reference evaluator recomputed all 34,542 cases with zero case-level mismatches and all 30,704 prespecified matched comparisons with zero mismatches. Two clean runs produced byte-identical canonical outputs.

### 4.5 Timing sensitivity: the one-cadence B0 cache boundary

Immediately after modeled authorization changes, the pre-hiatus record is still fresh for one cadence unit. Under the empirical-hiatus condition, B0 admits that cache to the recovery gate for exactly one cadence unit. With the same post-onset security signal and no refresh opportunity, S1 and B2 select protective actions instead.

Across all 1,919 intervals and all three first-refresh evidence states, the prespecified B0-versus-S1 cache contrast contains 5,757 comparisons. Each has the same B0-minus-S1 cache-origin unsafe-qualified exposure difference:

+1 cadence unit.

This result is structural under the frozen normalization. It is not a measurement of physical cache duration in flight.

### 4.6 Timing sensitivity: invalid post-signature alteration

At first refresh, V4 carries authorization=true with an invalid signature. Evidence qualification therefore fails, and the affected V4 record does not qualify the recovery gate.

This applies to all:

1,919 intervals × 3 policies × 2 timing arms = 11,514 V4 cases.

The result is limited to modeled post-signature alteration. It does not evaluate cryptanalysis, key extraction, or compromise of a real signing implementation.

### 4.7 Timing sensitivity: V5 delay and unchanged first-refresh classification

At first refresh, V5 carries authorization=true with a valid signature while hidden authorization is false.

Under the frozen post-onset security signal:

- B0 selects PROCEED_TO_RECOVERY_GATE;
- S1 selects PROCEED_TO_RECOVERY_GATE when the refresh opportunity is present;
- B2 selects RESTRICT_AND_REQUEST_AUTHORIZATION.

Therefore B0 and S1 are unsafe-qualified in all 7,676 corresponding V5 interval-arm cases, while B2 is non-qualifying in all 3,838 V5 cases.

For V5, all 5,757 gap-versus-continuous first-refresh gate comparisons agree by policy. The timing arms do not change first-refresh classification. They change **when** the first refresh occurs:

- matched continuous-refresh control: q = 0;
- empirical-hiatus arm: q = g_i, with every g_i > 10.

The externally sourced hiatus therefore postpones the modeled manifestation of the producer-origin failure for B0/S1 but does not make the false claim observable as false.

**Table 2** RQ1 temporal qualification results with study-specific units

| Evidence population | Condition | Policy / comparison | Qualification result | Exposure / timing statement |
|---|---|---|---|---|
| Study 3 | Persistent V5, K0 | B0 | 46/46 unsafe-qualified | Mean 122.500 logical s |
| Study 3 | Persistent V5, K0 | S1 | 46/46 unsafe-qualified | Mean 122.500 logical s |
| Study 3 | Persistent V5, K0 | B2 | 0/46 unsafe-qualified | 0 logical s |
| Study 3 | Persistent V5, K4 | B0 | 46/46 unsafe-qualified | Mean 55.326 logical s |
| Study 3 | Persistent V5, K4 | S1 | 46/46 unsafe-qualified | Mean 49.022 logical s |
| Study 3 | Persistent V5, K4 | B2 | 0/46 unsafe-qualified | 0 logical s |
| Study 3 | Truthful V0, K4 | B0 | 3/46 unsafe-qualified from PRE_ONSET_CACHE | Mean 0.326 logical s |
| S3X | Empirical hiatus | B0 minus S1 cache-origin contrast | 5,757/5,757 comparisons have the same difference | +1 cadence unit |
| S3X | V4 at first refresh | All policies, both timing arms | Affected record non-qualifying in 11,514 cases | Signature invalid |
| S3X | V5 at first refresh | B0 + S1 | 7,676/7,676 unsafe-qualified | q=0 in control; q=g_i in hiatus |
| S3X | V5 at first refresh | B2 | 3,838/3,838 non-qualifying | Same classification in both timing arms |

Study-3 logical seconds and S3X cadence units are distinct analysis units and are not converted or pooled.

### 4.8 RQ1 Answer

Intermittent evidence availability affects both the cache-origin and producer-origin boundaries, but in different ways. The frozen hiatus exposes a one-cadence B0 cache boundary before evidence expires, then creates a protective interval until refresh. Once false-but-valid V5 evidence arrives, timing no longer distinguishes truth from the validly signed false claim: B0 and S1 qualify it under the frozen semantics, while B2 remains non-qualifying under the post-onset signal.

The result supports a bounded conclusion: **intermittent availability can delay when a producer-origin semantic failure reaches the decision, but timing alone does not repair a trust property that is absent from the visible evidence.**

## 5 RQ2 — Producer Composition and Provenance-Domain Constraints

### 5.1 Study-4 Design

Study 4 evaluates seven producers P1–P7 assigned to three synthetic provenance domains:

D1 = {P1, P2, P3}, D2 = {P4, P5}, D3 = {P6, P7}.

A rule Qq_Dd requires q qualifying claims and d represented domains, with q = 1…7 and d = 1…min(3,q), giving 18 rules.

Two blocks are evaluated separately:

- **malicious compromise block:** hidden authorization is false, all producers are available, and compromised producers emit validly signed authorization-true claims;
- **benign unavailability block:** hidden authorization is true, unavailable producers emit no claim, and available producers emit validly signed authorization-true claims.

Every producer subset is evaluated in both blocks:

18 rules × 2 blocks × 128 subsets = 4,608 observations.

### 5.2 First and Systematic Failure

For each rule, **first failure** is the smallest affected-producer count at which at least one subset fails. **Systematic failure** is the smallest count at which every subset fails.

That distinction is necessary because provenance composition makes same-size subsets behave differently.

**Table 3** Study-4 exact first/systematic failure map

| Rule | Unsafe qualification under compromise | False-conservative rejection under benign loss |
|---|---:|---:|
| Q1_D1 | 1/1 | 7/7 |
| Q2_D1 | 2/2 | 6/6 |
| Q2_D2 | 2/4 | 4/6 |
| Q3_D1 | 3/3 | 5/5 |
| Q3_D2 | 3/4 | 4/5 |
| Q3_D3 | 3/6 | 2/5 |
| Q4_D1 | 4/4 | 4/4 |
| Q4_D2 | 4/4 | 4/4 |
| Q4_D3 | 4/6 | 2/4 |
| Q5_D1 | 5/5 | 3/3 |
| Q5_D2 | 5/5 | 3/3 |
| Q5_D3 | 5/6 | 2/3 |
| Q6_D1 | 6/6 | 2/2 |
| Q6_D2 | 6/6 | 2/2 |
| Q6_D3 | 6/6 | 2/2 |
| Q7_D1 | 7/7 | 1/1 |
| Q7_D2 | 7/7 | 1/1 |
| Q7_D3 | 7/7 | 1/1 |

### 5.3 Provenance Changes Systematic Failure Without Necessarily Changing First Failure

Q3_D3 provides the clearest example. First unsafe failure remains at three compromised producers, the same first count as Q3_D1. But Q3_D3 requires a qualifying subset to span all three domains, so not every three-, four-, or five-producer compromised subset qualifies. Systematic failure moves from 3 under Q3_D1 to 6 under Q3_D3.

The same pattern appears at Q4_D3 (4/6) and Q5_D3 (5/6). Provenance therefore changes the subset structure of the failure boundary even when the first failure count is unchanged.

### 5.4 The Same Structure Can Reduce Benign Tolerance

The tradeoff appears immediately in the benign block. Q3_D1 first and systematically fails only after five unavailable producers, whereas Q3_D3 first fails after two and becomes systematic at five. Two unavailable producers can eliminate a required domain even while enough producers remain for the raw vote threshold.

Q4_D3 similarly changes benign failure from 4/4 under Q4_D1 to 2/4, and Q5_D3 first fails at two unavailable producers rather than three under Q5_D1.

### 5.5 Provenance Effects Are Conditional, Not Monotonic

Some domain constraints produce no threshold improvement. Q4_D1 and Q4_D2 are both 4/4 in each block. Q5_D1 and Q5_D2 are identical at 5/5 for unsafe qualification and 3/3 for benign rejection. All Q6 variants are 6/6 and 2/2, and all Q7 variants are 7/7 and 1/1.

The result therefore does not support “more provenance diversity is always better.” Its effect depends on the vote threshold, the frozen 3/2/2 domain allocation, and the particular affected subset.

### 5.6 RQ2 Answer

Producer diversity changes the compromise-versus-availability boundary by changing **which subsets** can satisfy a rule. In selected cells it delays systematic unsafe qualification without moving first unsafe failure. The same constraint can cause earlier rejection when benign evidence is unavailable. Absolute vote count and provenance structure therefore control different aspects of the finite qualification frontier.

These provenance domains are synthetic independence classes. The study does not establish that real producers are organizationally, physically, administratively, or supply-chain independent.

## 6 RQ3 — Recovery-Artifact Assurance and Residual Incorrect States

### 6.1 Study-6 Design

Study 6 evaluates six recovery-artifact states against six assurance gates. CLEAN_APPROVED is objectively correct and has all six visible signals true. Five states are objectively incorrect:

1. POST_RELEASE_TAMPER;
2. TRUSTED_SIGNER_COMPROMISE;
3. TRUSTED_BUILDER_COMPROMISE;
4. SOURCE_REVIEW_BYPASS;
5. APPROVED_BAD_SOURCE.

The visible assurance signals are signature validity, independent target digest match, provenance validity, independent reproduced-build match, source-review attestation, and release approval.

The gates are:

- G0_SIGNATURE_ONLY;
- G1_SIGNATURE_TARGET_DIGEST;
- G2_SIGNATURE_PROVENANCE;
- G3_PROVENANCE_REPRODUCED_BUILD;
- G4_PROVENANCE_SOURCE_REVIEW;
- G5_COMPOSITE, which requires all six signals.

Block A crosses all six artifact states with all six gates, producing 36 observations. Block B keeps CLEAN_APPROVED as the objectively correct baseline and evaluates all 64 subsets of unavailable assurance signals under each gate, producing 384 observations. The total population is 420 exact observations.

### 6.2 Stronger Gates Close Specific Incorrect States

Signature-only checking rejects POST_RELEASE_TAMPER because its signature is invalid, but it leaves four of the five prespecified incorrect states qualified.

Adding target-digest or provenance requirements reduces the surviving incorrect set to three. G3 adds reproduced-build evidence and leaves only SOURCE_REVIEW_BYPASS and APPROVED_BAD_SOURCE. G4 adds source-review evidence instead and leaves TRUSTED_BUILDER_COMPROMISE and APPROVED_BAD_SOURCE. The equal 2/5 counts therefore hide different residual trust assumptions.

The six-signal G5 composite gate leaves only APPROVED_BAD_SOURCE. In that state every gate-visible assurance signal is true while objective baseline correctness is false.

**Table 4** Study-6 residual incorrect-state and benign-loss counts

| Gate | Visible requirements | Incorrect states remaining qualified | Benign unavailable-signal subsets rejected |
|---|---:|---:|---:|
| G0_SIGNATURE_ONLY | 1 | 4/5 | 32/64 |
| G1_SIGNATURE_TARGET_DIGEST | 2 | 3/5 | 48/64 |
| G2_SIGNATURE_PROVENANCE | 2 | 3/5 | 48/64 |
| G3_PROVENANCE_REPRODUCED_BUILD | 3 | 2/5 | 56/64 |
| G4_PROVENANCE_SOURCE_REVIEW | 3 | 2/5 | 56/64 |
| G5_COMPOSITE | 6 | 1/5 | 63/64 |

### 6.3 Assurance Composition Has a Benign Evidence Cost

The benign block moves in the opposite direction. G0 rejects the objectively correct baseline in 32 of the 64 unavailable-signal subsets. The two-signal gates reject 48/64, the three-signal gates reject 56/64, and the six-signal composite rejects 63/64.

These are finite subset counts, not operational outage probabilities. They show that a gate requiring more evidence is structurally more sensitive to loss of evidence that it declares mandatory.

### 6.4 Residual state: approved but incorrect source

The prespecified APPROVED_BAD_SOURCE state has all six gate-visible assurance signals true while objective correctness is false. Thus the composite rule, which receives exactly those signals, qualifies that state. This is an explicit limitation of its defined observation vector rather than a surprising discovery about real release systems. It identifies a concrete *verification requirement* for any application that needs to exclude source-level semantic defects: independently justified functional or semantic evidence would need to be admitted to the relying-party decision, with its availability and fault independence assessed separately. The present frozen design does not evaluate that added rule.

### 6.5 Executable existence demonstration (S6X)

The executable extension tests whether the prespecified Study-6 residual can be reproduced in one controlled software example. It uses pinned NASA cFS v7.0.1 / Limit Checker source and a researcher-introduced signed-integer equality-boundary fixture that changes the `GT` branch from `WPValue > CompareValue` to `WPValue >= CompareValue`. A separately authored equality-boundary test checks the case where `0 > 0` should be false. **Both the fault and the detecting oracle were constructed for this experiment**; S6X demonstrates a possible observational mismatch and does not estimate its natural occurrence or validate a general attack class.

The source-derived artifacts were built as clean/altered primary and rebuild variants in two independently checked deterministic repetitions. Clean artifacts had SHA-256 `7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670`; the altered-source artifacts had SHA-256 `275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c`. The frozen augmented `native_std.runtest` harness returned RC 0 for CLEAN_APPROVED and RC 2 for APPROVED_BAD_SOURCE. This functional adjudication was *research-only* and absent from the six qualification inputs. The experiment's evidence records represent signature validity, digest match, provenance, independent reproduced build, source-review attestation and release approval as true for both states. Their qualification equivalence therefore follows from the deliberately restricted evidence vector; the executable builds show that this construction can be made reproducible for the selected source/fixture.

**Execution transparency.** Attempts 001 and 002 stopped before canonical observations: the first lacked the `jq` prerequisite and designated an incorrect artifact path; the second mixed build output with a captured artifact hash. Attempt 003 completed two repetitions, eight governed builds, 396 observations per repetition, independent scientific validation and zero primary/reference gate-evaluator mismatches. It was failed closed because a shell-variable expansion error prevented the terminal reporting step. A reporting-only correction preceded successful Campaign 004, which reached runner RC 0 and became the separately authorized frozen result. The Attempt-003 and Campaign-004 gate-observation CSVs have the **same recorded SHA-256** (`cb840a8d89267b313be79280d2909e708327cb5ca333e23dbfc7e50b9e37dc63`); this establishes identity of that file, not all execution artifacts or retroactive canonical status for Attempt 003. Historical attempt directories remain immutable.

Block A crosses the two artifact states with six gates (12 observations); primary and reference gate evaluators agree on all rows. Block B crosses the clean state with all 64 benign unavailable-signal masks under each gate (384 observations). Both 396-observation Campaign-004 repetitions passed independent validation with zero primary/reference mismatches and byte-identical canonical result files across repetitions.

**Table 5** S6X executable validation of the Study-6 observability mechanism

| S6X property | Frozen Campaign-004 result |
|---|---|
| Governed builds | 8 total: clean/bad × primary/rebuild × 2 repetitions |
| Artifact reproducibility | CLEAN primary = CLEAN rebuild; BAD primary = BAD rebuild in both repetitions |
| Cross-state identity | CLEAN artifact SHA-256 differs from controlled BAD artifact SHA-256 |
| Research functional adjudication | CLEAN `native_std.runtest` RC 0; controlled BAD RC 2 under the frozen equality-boundary harness |
| Block A | 12 state-by-gate observations; six gate-visible signals true for both states; 0 primary/reference mismatches |
| Block B | 384 CLEAN_APPROVED assurance-unavailability observations; 0 primary/reference mismatches |
| Deterministic repeat | 396 observations/repetition; independent validation PASS; all five canonical result files byte-identical |

This is a reproducible **existence demonstration of a constructed observation-set boundary**, not an empirical replication of the Study-6 420-observation population. It does not establish a vulnerability in unmodified NASA cFS/LC, NASA endorsement or certification, actual supplier compromise, flightworthiness, operational assurance, or that an unmodified upstream test suite would detect or miss the fixture. The externally defined functional oracle does not become a seventh gate signal by virtue of detecting the designed change. Measuring the effect and benign-loss cost of adding such a signal would require a separate prospective experiment with its own hypothesis, population, and approval.

### 6.6 RQ3 Answer

The six-signal composite excludes four of five prespecified incorrect artifact states compared with one excluded under signature-only checking; its benign unavailable-signal rejection increases from 32/64 to 63/64. APPROVED_BAD_SOURCE survives because correctness is not represented by a distinguishing gate input. S6X provides a controlled executable instance of that **constructed** distinction, with the source alteration detected by a research-only functional oracle and with six identical gate-visible assurance values. Study 6 and S6X remain independent populations, and the data do not quantify how a prospective functional seventh signal would behave under benign unavailability.

## 7 Cross-Study Synthesis — Observability Defines the Residual Boundary

Three separate finite experiments locate complementary recovery qualification contracts: runtime-state evidence (Study 3), subset and provenance composition (Study 4), and approved-artifact assurance (Study 6). Their connection is a comparison of *which hidden property the declared observation set omits*, not an experimentally connected pipeline. The timing sensitivity analysis and executable existence demonstration remain subordinate, separately governed illustrations. No cross-study pooled endpoint is defined.

### 7.1 Integrity Is Necessary but Not Equivalent to Truth

Study 3 shows that post-signature alteration is detected because the signature becomes invalid, while V5 remains acceptable to B0/S1 because the trusted producer signs the false claim itself. S3X preserves that distinction under an externally sourced timing population: delaying the next refresh postpones V5 manifestation but does not change its first-refresh qualification for B0/S1.

Study 6 shows an analogous boundary at the artifact level. Additional digest, provenance, reproduced-build, review, and approval evidence closes multiple modeled failure states, but APPROVED_BAD_SOURCE remains because all visible assurance signals are satisfied. S6X separately instantiates that residual with executable cFS/LC artifacts: the controlled source change is exposed by the external research equality-boundary harness, while the six Study-6-aligned qualification signals remain true for both states.

These results point to the same systems principle within these finite models: an integrity or process-assurance mechanism establishes the property represented in its policy-visible evidence; it does not automatically establish a different semantic property that is absent from that evidence.

### 7.2 Composition Moves a Frontier Rather Than Producing Universal Dominance

Study 4 shows that additional provenance structure can delay systematic unsafe qualification while reducing benign-loss tolerance. Study 6 shows that stronger assurance composition reduces the number of modeled incorrect states that remain qualified while increasing rejection under missing assurance evidence. Study 3/S3X shows that B2 is structurally non-qualifying for V5 under the frozen post-onset signal, but that result is not a global policy ranking because the studies do not define mission utility, recovery cost, or operational performance.

Across layers, “stronger” visible evidence changes a boundary condition. Whether the change is operationally desirable depends on costs, availability, mission context, and failure assumptions that are outside these finite models.

### 7.3 Residual Identity Matters

An aggregate number alone does not identify the remaining trust assumption.

- Study 3 records whether unsafe qualification originated from PRE_ONSET_CACHE or V5_AFFECTED_RECORD.
- Study 4 distinguishes first from systematic failure because same-size subsets can differ by provenance composition.
- Study 6 preserves which incorrect artifact state survives each gate because equal residual counts can hide different mechanisms.
- S3X distinguishes timing delay from classification change: the empirical hiatus changes q, not the V5 first-refresh classification for a given policy.
- S6X distinguishes gate-visible process-assurance evidence from external research functional adjudication: the controlled bad-source variant can remain qualification-equivalent under the six gate signals even though the frozen equality-boundary harness marks it functionally incorrect.

This is why the paper reports origin, subset structure, and residual-state identity rather than collapsing results into a scalar trust score.

### 7.4 Systems Answer to the Central Question

The central research question asks which trust failures remain invisible when recovery relies on fresh evidence, multiple trusted producers, and an approved recovery artifact.

The combined answer is:

1. **Freshness and valid signatures can leave producer-origin semantic falsity invisible.** A trusted producer can issue a fresh, correctly signed false claim.
2. **Producer count and provenance constraints can leave common or insufficiently represented failure assumptions invisible.** Diversity changes which subsets qualify, but the rule sees only the modeled vote/domain structure.
3. **Artifact assurance can leave upstream semantic correctness invisible.** A gate cannot reject APPROVED_BAD_SOURCE when every gate-visible signal is true. S6X shows the same mechanism with executable artifact identities when the functional harness remains outside the gate observation set.
4. **External timing can delay manifestation without adding missing semantics.** S3X changes when V5 reaches the gate but does not add a signal that reveals the false claim.

The residual trust boundary is therefore determined by the distinction between **visible evidence** and the **property that the system actually needs to know**.

### 7.5 Engineering implications for a spacecraft qualification contract

The quantitative results suggest concrete questions a spacecraft recovery engineering review should answer before authorizing a transition.

1. **Semantic authority:** document the mission state represented by signed runtime evidence, its update/expiration path, and how a trusted producer's incorrect claim could be independently challenged. Study 3 makes freshness-origin and producer-origin failure distinct, rather than treating every valid signature as truthful state.
2. **Independent origins and availability:** justify actual trust-domain boundaries with hardware, organizational, administrative and supply-chain evidence. Study 4's Q3_D1 versus Q3_D3 comparison changes systematic unsafe failure from three to six affected producers while moving first benign-unavailability rejection from five to two. The seven-producer, 3/2/2 allocation is a design probe rather than a proposed mission quorum configuration.
3. **Artifact correctness:** state whether signatures, digest, build identity, review and approval warrant only process provenance or also an independently established behavioral requirement. Study 6's residual APPROVED_BAD_SOURCE motivates *considering* functional/semantic evidence as a gate input; S6X exposes the difference between having a diagnostic oracle and admitting its result into the authorization decision.

Each added mandatory condition has an availability cost to be specified before deployment. The existing exact loss counts apply to the six frozen Study-6 signals, while no effectiveness or benign-loss estimate exists for a new functional seventh signal. A flight architecture would additionally have to test evidence paths, authority mappings and independence assumptions under its own mission requirements.

## 8 Validity, reproducibility and transfer

### 8.1 What the finite experiments establish

Studies 3, 4 and 6 exhaustively evaluate their registered finite grids. Their counts, state identities and first/systematic thresholds are exact for the defined treatments, without sampling-based confidence intervals. S3X separately evaluates 34,542 interval-policy-state-arm cases and 30,704 matched comparisons under its frozen timing adapter, with zero independently evaluated case/match discrepancies and byte-identical canonical outputs in two runs. S6X's successful Campaign 004 has two deterministic repetitions with eight governed builds in total, 396 gate observations per repetition, zero primary/reference gate discrepancies and independent validation PASS. These are reproducibility controls within the research implementation, not a claim of independent human or external replication.

### 8.2 Construct validity and operational transfer

Study 3 uses logical model time and synthetic K4 contact windows. S3X selects P99_X10 extreme positive ESA inter-sample intervals only to perturb imposed evidence refresh; selection occurred following a prespecified eight-rule sensitivity analysis and before the frozen trace extraction. ESA supplied timestamps, **not** RF-outage, command-contact, cyberattack or recovery-truth labels. The results establish sensitivity of Study-3 decision semantics to that chosen timing distribution, not physical mission-contact performance.

Study 4 assumes seven producers and synthetic D1/D2/D3 domain membership in a fixed 3/2/2 allocation. Independent operational compromise, correlation, dynamic membership, weighted votes and simultaneous compromise/unavailability were outside its frozen design. Domain names therefore denote modeled equivalence classes, not validated physical or organizational independence. Study 6 uses six Boolean evidence signals, five prescribed incorrect artifacts and 64 benign unavailable-signal masks; these counts are model-state fractions rather than incident frequencies or mission probabilities.

S6X introduces one researcher-selected `>` to `>=` modification and an externally researcher-specified equality oracle in pinned cFS/LC source. The assurance record explicitly represents both artifacts as satisfying six gate-visible values; the resulting observational equivalence is constructed. The augmented `native_std.runtest` RC 0/RC 2 contrast is specific to that frozen harness and does not demonstrate an upstream NASA vulnerability, a production quality-assurance process, flight readiness or certification.

### 8.3 External validation required

Application to a real mission requires validated allocation of attesters, key owners, onboard state authority, independent provenance domains, evidence-refresh paths and a recovery gate with declared fail-closed behavior. Operational measurement would be needed to relate selected timestamp gaps to actual evidence delivery. A new gate-visible functional/semantic signal and its benign-loss cost would require separately registered, prospectively frozen experimental design and execution. Until then, the contribution is the exact mechanism-specific qualification contract and residual-assumption map, without pooled cross-study rate or on-orbit performance claim.

## 9 Conclusion

Satellite cyber-recovery qualification is a requirements problem about what declared evidence allows a relying-party decision to establish. Study 4 quantifies how provenance-domain constraints can shift systematic unsafe qualification while changing tolerance to missing benign evidence; the result depends on vote threshold and producer composition rather than monotonically improving with additional domains. Study 6 reduces the finite incorrect artifacts still qualified from four of five under signature-only checking to one of five under the six-signal composite, with a corresponding increase in rejection of unavailable benign-evidence subsets. Study 3 distinguishes truthful-cache exposure from false but validly signed claims made inside a trusted producer boundary.

The supporting timing sensitivity analysis uses selected ESA inter-sample intervals to perturb evidence refresh; the executable existence demonstration makes the Study-6 process-evidence-versus-functional-oracle distinction reproducible in one controlled cFS/LC source example. Neither extends the core samples or measures operational recovery. Together, the independent findings identify three mission-engineering obligations: specify semantic authority and freshness, substantiate failure independence among evidence origins, and determine which artifact correctness properties must be independently evidenced at the gate. Verification of an integrated spacecraft implementation and any additional gate-visible signal remains future, separately governed work.



## Statements and Declarations

**Funding.** No external funding was reported in the Paper-2 research record; the sole author will confirm this declaration in the publisher portal.

**Competing interests.** The author declares no competing interests, consistently with the earlier author-confirmed Paper-2 submission record. Reconfirm against current circumstances at final upload.

**Author contributions.** Aman Kumar Singh is the sole human author and is responsible for conceptualization, methodology, software, validation, formal analysis, investigation, resources, data curation, original drafting, review and editing, visualization and project administration, subject to final author confirmation in Springer's submission interface.

**Data availability.** The underlying Study-3, Study-4 and Study-6 canonical summary outputs, frozen protocols, source code and associated audit records are maintained in the author's version-controlled research materials. Supporting derived results and reproducibility evidence for the separate S3X and S6X investigations may be obtained from the corresponding author on reasonable request, subject to preservation and third-party redistribution restrictions. The externally sourced ESA Anomaly Dataset is cited at [16] with DOI https://doi.org/10.5281/zenodo.15237121; selected timing inputs are derived from its timestamp structure and are not labeled contact outages. A new independent deposit DOI for this manuscript has not been minted. **Author confirmation of the request/access procedure is required before submission.**

**Code availability.** Model implementations and independent-validation scripts supporting the finite analyses are maintained by the author; a reader-accessible reproduction manifest can be provided upon reasonable request. This statement does not represent an uncommitted local execution workspace as a public archival release.

**Ethics approval and consent.** Not applicable to the computational studies and reuse of non-human spacecraft telemetry timestamps reported here.

## References

[1] R. Thummala, E. Rice, and G. Falco, “Why is space cybersecurity unique?,” in Proc. 4th Workshop Security Space Satellite Syst. (SpaceSec), San Diego, CA, USA, Feb. 23, 2026, https://doi.org/10.14722/spacesec.2026.23055.

[2] M. Scholl and T. Suloway, “Introduction to Cybersecurity for Commercial Satellite Operations,” NIST IR 8270, Jul. 2023, https://doi.org/10.6028/NIST.IR.8270.

[3] SLSA, “Threats & mitigations,” SLSA Specification, v1.2. Accessed: Sep. 28, 2026. [Online]. Available: https://slsa.dev/spec/v1.2/threats

[4] G. De Canio, K. Kotowski, and C. Haskamp, “ESA Anomaly Dataset,” Zenodo, 2025, https://doi.org/10.5281/zenodo.15237121.

[5] J. Curbo and G. Falco, “Testable cyber requirements for space flight software,” in Proc. 2025 IEEE Aerosp. Conf., Big Sky, MT, USA, 2025, pp. 1–20, https://doi.org/10.1109/AERO63441.2025.11068629.

[6] M. M. Utsash, G. Kavallieratos, K. Antonakopoulos, and S. K. Katsikas, “Investigating the Effectiveness of Zero–Trust Architecture for Satellite Cybersecurity,” in Proc. 11th International Conference on Information Systems Security and Privacy (ICISSP), vol. 2, pp. 133–140, 2025, https://doi.org/10.5220/0013103200003899.

[7] J. Vanlyssel, G.-C. Roman, and A. Anwar, “Silent Subversion: Sensor Spoofing Attacks via Supply Chain Implants in Satellite Systems,” in 2026 IEEE Aerospace Conference, pp. 1–10, 2026, https://doi.org/10.1109/AERO66936.2026.11519913.

[8] National Aeronautics and Space Administration, “Space Security: Best Practices Guide,” Rev. B, Jan. 19, 2024. Accessed: Sep. 28, 2026. [Online]. Available: https://swehb.nasa.gov/spaces/SWEHBVD/pages/146540183/7.22+-+Space+Security+Best+Practices+Guide

[9] The Aerospace Corporation, “Cyber-safe Mode (CM0044),” Space Attack Research & Tactic Analysis (SPARTA). Accessed: Sep. 28, 2026. [Online]. Available: https://sparta.aerospace.org/countermeasures/CM0044

[10] H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, “Remote ATtestation procedureS (RATS) architecture,” RFC 9334, Jan. 2023, https://doi.org/10.17487/RFC9334.

[11] D. Malkhi and M. Reiter, “Byzantine quorum systems,” Distrib. Comput., vol. 11, no. 4, pp. 203–213, Oct. 1998, https://doi.org/10.1007/s004460050050.

[12] O. Alpos, C. Cachin, B. Tackmann, and L. Zanolini, “Asymmetric distributed trust,” Distrib. Comput., vol. 37, no. 3, pp. 247–277, May 2024, https://doi.org/10.1007/s00446-024-00469-1.

[13] S. Torres-Arias, H. Afzali, T. K. Kuppusamy, R. Curtmola, and J. Cappos, “in-toto: Providing farm-to-table guarantees for bits and bytes,” in Proc. 28th USENIX Security Symp. (USENIX Security 19), Santa Clara, CA, USA, Aug. 2019, pp. 1393–1410.

[14] S. Salim, N. Moustafa, and M. Reisslein, “Cybersecurity of Satellite Communications Systems: A Comprehensive Survey of the Space, Ground, and Links Segments,” IEEE Communications Surveys & Tutorials, vol. 27, no. 1, pp. 372–425, 2025, https://doi.org/10.1109/COMST.2024.3408277.

[15] B. Wang et al., “A Comprehensive Literature Review of Cybersecurity in Satellite Networks,” Aerospace, vol. 13, no. 3, p. 249, 2026, https://doi.org/10.3390/aerospace13030249.

[16] The Update Framework, “The Update Framework Specification, v1.0.36,” Aug. 10, 2026.

[17] SLSA, “Source: Requirements for producing source,” SLSA Specification, v1.2. Accessed: Sep. 28, 2026. [Online]. Available: https://slsa.dev/spec/v1.2/source-requirements

[18] L. Herrmann, M. Bieber, W. J. C. Verhagen, F. Cosson, and B. F. Santos, “Unmasking overestimation: a re-evaluation of deep anomaly detection in spacecraft telemetry,” CEAS Space J., vol. 16, pp. 225–237, 2024. https://doi.org/10.1007/s12567-023-00529-5.

[19] C. Schefels, L. Schlag, and K. Helmsauer, “Synthetic satellite telemetry data for machine learning,” CEAS Space J., vol. 17, pp. 863–875, 2025. https://doi.org/10.1007/s12567-024-00589-1.
