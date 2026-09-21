# Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing

**Aman Kumar Singh, MS, DSc**  
Independent Researcher, The Woodlands, Texas, United States  
ORCID: https://orcid.org/0009-0008-9752-3743

**Venue-neutral rebuilt Paper 4 working manuscript**  
**Studies:** S8-PQC-ICR-001 and S8E-ECTV-001  
**Status:** integrated draft for scientific and editorial review; venue not locked

## Abstract

Long-lived satellite systems may need to replace compromised cryptographic state while communication opportunity is intermittent and post-quantum transition objects impose nontrivial transfer burden. This paper evaluates that problem using two separately governed finite studies that are reported together but never statistically pooled. Study 8 is a controlled deterministic logical-contact experiment with 3,456 factorial positions spanning three exact ML-KEM/ML-DSA algorithm-pair profiles, four transition policies, four equal-full-cycle-capacity contact regimes, four bounded non-cryptanalytic disruptions, six compromise offsets, and three logical deadlines. Study 8E is a prospectively governed external timing extension that applies the frozen transition object requirements and policy semantics to public SatNOGS observation-opportunity timing, producing 65,376 canonical cases across 20 selected satellite-station traces and 454 eligible anchors.

In Study 8, all four policies restored modeled trust in 635/864 positions, and the prespecified contact-aware staged-minus-staged difference was exactly 0.000000 percentage points. Fixed-capacity success nevertheless declined with standardized transition-object burden: 93.7500% for ML-KEM-512/ML-DSA-44, 64.9306% for ML-KEM-768/ML-DSA-65, and 61.8056% for ML-KEM-1024/ML-DSA-87. Study 8E found a finite minimum hypothetical uniform effective payload-rate threshold in 17,640/65,376 cases (26.9824%), with finite thresholds from 48 to 57,727 modeled bit/s and a median of 345 bit/s. The finite fraction increased from 5.2863% at 6 h to 20.5947% at 12 h and 55.0661% at 24 h. P3 and P1 again showed no feasibility advantage: all 4,410 both-finite matched comparisons had exactly 0 bit/s threshold difference. Profile feasibility classification was identical, but the cryptographic-burden ordering was preserved in all 21,792 matched profile comparisons.

Together, the studies distinguish two complementary questions: whether recovery fits within a fixed modeled contact budget and what modeled rate is required under an externally observed timing structure. The results show that a pre-commit guard does not create communication capacity; transition-object burden, temporal opportunity, and recovery horizon constrain modeled feasibility, while policy semantics primarily redistribute transition-state costs. SatNOGS observations are used only as public observation-opportunity timing proxies and are not treated as authenticated command contacts or measured link throughput.

**Keywords:** post-quantum cryptography; cryptographic agility; ML-KEM; ML-DSA; satellite cybersecurity; post-compromise recovery; intermittent connectivity; SatNOGS; observation-opportunity timing; systems modeling

---

## 1. Introduction

Space systems combine long service lives, constrained opportunities for physical maintenance, intermittent communications, and growing requirements for cybersecurity resilience. These characteristics make cryptographic transition more than an algorithm-replacement problem. When predecessor credentials or cryptographic state are suspected to be compromised, recovery requires a successor security state to be established, transferred, accepted, committed, confirmed, and made authoritative before an operationally relevant deadline. Post-quantum cryptography can intensify this systems problem because standardized public keys, ciphertexts, and signatures may be materially larger than the classical artifacts they replace.

NIST defines crypto agility as the capabilities needed to replace and adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving security and ongoing operations [@NIST_CSWP39_2026]. NIST FIPS 203 and FIPS 204 standardize ML-KEM and ML-DSA [@NIST_FIPS203_2024; @NIST_FIPS204_2024], while SP 800-227 emphasizes that safe KEM use depends on surrounding protocol and system conditions rather than algorithm selection alone [@NIST_SP800227_2025]. The June 2026 update to NIST CSWP 39 reinforces that crypto agility is environment-specific and operational: changing cryptography must be possible without treating the cryptographic primitive in isolation.

The space and non-terrestrial-network literature already addresses post-quantum algorithms, migration, hybrid approaches, constrained authentication, key management, implementation, and crypto agility [@GSMA_PQ07_2026; @Mahn_Muller_Zielinski_2025; @Wildfeuer_etal_2025; @Robles_etal_2025; @Kim_2026_PQCSpace]. Ghosh and Nath analyze lattice-based PQC for satellite communications [@Ghosh_Nath_2026]. Eichen et al. identify bandwidth, memory, computation, and energy pressure from post-quantum authentication in bandwidth-constrained and non-terrestrial networks [@Eichen_etal_2026]. De Zuane et al. study efficient and quantum-safe IKE variants for satellite communications, including hybrid transition mechanisms and bandwidth/resource considerations [@DeZuane_etal_2026]. These works establish that PQC overhead and transition design in satellite or NTN environments are active research areas. The contribution here is therefore not that PQC exists for satellites, that post-quantum objects can be large, or that crypto agility is desirable.

A narrower post-compromise systems question remains: if a trusted predecessor state can no longer be assumed, what determines whether a successor cryptographic epoch can be established before the available communication opportunity or recovery horizon is exhausted? That question requires more than a cryptographic benchmark. It couples transition-object burden, the temporal placement of communication opportunity, state-acceptance semantics, disruption, and deadline.

A previous controlled study, Study 8, isolated this question using a deterministic finite logical-contact model. It found an exact negative primary result: a contact-aware pre-commit guard did not increase the probability of modeled trusted recovery relative to ordinary staged cutover. The strongest fixed-capacity differences were instead associated with standardized cryptographic-object burden, contact timing, and recovery deadline. That controlled design, however, intentionally used synthetic logical contact slots with no physical duration.

The present rebuilt paper preserves Study 8 unchanged and adds a separately governed extension, Study 8E. Study 8E does not convert logical slots to seconds, modify the original population, or pool results. Instead, it applies the frozen transition-object requirements and policy semantics to a prospectively selected public SatNOGS observation-opportunity timing population and solves a different endpoint: the minimum hypothetical uniform effective payload rate required to restore modeled trust before an elapsed-time horizon.

The manuscript is organized around the following systems-level framing question:

> **What constrains trusted post-compromise post-quantum cryptographic recovery when communication opportunity is intermittent, and which structural findings remain when analysis moves from a controlled logical contact budget to independently sourced public observation-opportunity timing?**

This framing question does not replace the frozen research question or endpoints of either study. It provides the manuscript-level structure for reporting them together.

The paper makes four contributions.

First, it presents a controlled post-compromise transition model coupling exact standardized ML-KEM/ML-DSA object sizes, a frozen recovery state machine, four transition policies, intermittent logical contact, deadlines, and bounded non-cryptanalytic disruption.

Second, it separates fixed-capacity recovery feasibility from transition-state cost. Study 8 shows that the four tested policies have identical primary success but differ in predecessor exposure, control unavailability, overlap, transfer use, transition attempts, and failure classification.

Third, it adds a separately frozen external timing layer. Study 8E uses public SatNOGS observation start/end timing as an observation-opportunity proxy and solves the modeled minimum effective payload rate required for the same frozen transition semantics under 6 h, 12 h, and 24 h extension-only horizons.

Fourth, it provides a bounded cross-study synthesis without pooling. The exact P3-versus-P1 feasibility null remains structurally consistent across the two studies under different endpoints; longer allowed recovery time expands the feasible set in both; and cryptographic-object burden appears differently depending on whether capacity is fixed or rate is solved.

The resulting contribution is a two-layer systems analysis: Study 8 asks whether a cryptographic transition fits within a fixed modeled opportunity budget, whereas Study 8E asks what modeled rate would be required for the transition to fit within externally observed timing windows. These endpoints are complementary but not interchangeable.

## 2. Related Work and Standards Context

### 2.1 Post-quantum cryptography for space and non-terrestrial systems

Kim's systematic survey reviews a broad space-oriented PQC literature spanning algorithms, implementation platforms, software integration, hybrid migration, crypto agility, and standards gaps [@Kim_2026_PQCSpace]. Ghosh and Nath evaluate lattice-based PQC in satellite-communication settings using prior benchmark evidence to compare computational and communication burdens [@Ghosh_Nath_2026]. GSMA PQ.07 frames PQC migration for non-terrestrial networks around long satellite lifecycles, constrained processing, latency, interoperability, PKI, hardware readiness, and phased or hybrid migration [@GSMA_PQ07_2026].

Eichen et al. focus directly on post-quantum authentication pressure in bandwidth- and power-constrained environments, including NTNs, and motivate alternative key-management architectures to reduce certificate and handshake burden [@Eichen_etal_2026]. De Zuane et al. study quantum-safe IKE designs for satellite communications from both protocol-design and experimental perspectives, including hybrid cryptographic variants [@DeZuane_etal_2026]. These studies are closest in recognizing that post-quantum authentication and key-establishment artifacts interact with communication constraints. The present work differs by focusing on post-compromise trusted-state transition with explicit predecessor/successor epoch semantics and a recovery deadline, rather than handshake benchmarking or general key exchange.

### 2.2 Crypto agility and secure transition

NIST CSWP 39upd1 treats crypto agility as the capability to replace or adapt cryptographic algorithms while preserving security and ongoing operations [@NIST_CSWP39_2026]. This systems framing is particularly relevant after compromise because replacing cryptography safely involves not only selecting a new primitive but coordinating state, dependencies, acceptance rules, and transition mechanisms.

Space-focused work by Mähn, Müller, and Zielinski develops crypto-agility terminology for space systems and discusses secure update and fallback concerns [@Mahn_Muller_Zielinski_2025]. ESA-associated work has examined quantum-safe satellite data-link architecture and high-assurance post-quantum integration for software-defined payloads [@Wildfeuer_etal_2025; @Robles_etal_2025]. The ACES activity further reflects institutional interest in advanced cryptography and security-by-design for satellite and future NTN systems [@ESA_ACES_2026].

The present study does not propose a complete operational crypto-agility architecture. It isolates one recoverability question inside such an architecture: can the modeled successor cryptographic state be transferred and committed before opportunity or deadline is exhausted, and what state costs arise while doing so?

### 2.3 Satellite cybersecurity and trust continuity

Satellite cybersecurity literature has emphasized the dependence of missions on trustworthy communications, software-defined infrastructure, and resilient security controls [@HousenCouriel_2016; @Falco_2019]. Security mechanisms for federated satellite systems have also been evaluated at protocol and platform levels [@vonMaurich_Golkar_2018]. IEEE 3536-2026 provides current space-system cybersecurity design context across system layers [@IEEE3536_2026].

The CCSDS data-link security architecture is relevant as architectural context because its algorithm-independent framing supports analysis of cryptographic replacement without implying that ML-KEM or ML-DSA are already approved as an operational CCSDS PQC profile [@CCSDS_SDLS]. This paper therefore does not claim CCSDS conformance.

### 2.4 Public observation timing as external evidence

SatNOGS Network provides an open API for scheduled jobs and observation data and distributes API data under CC BY-SA [@SATNOGS_API_2026]. Observation records expose fields including start, end, ground station, and NORAD catalog identifier. In Study 8E, only a prospectively frozen subset of those fields is used to construct observation-opportunity timing traces.

This use is intentionally narrow. A SatNOGS observation is not treated as proof of an authenticated, bidirectional, operational command contact. Transmitter baud is not used as payload throughput. Ground-station identity is not treated as cryptographic trust. The external source contributes timing structure only.

### 2.5 Gap addressed by this paper

The closest prior work establishes that satellite/NTN PQC is relevant, that post-quantum authentication can increase communication burden, and that crypto agility must preserve security and continuity. The remaining gap addressed here is the interaction between standardized cryptographic transition-object burden, explicit trusted-state progression, intermittent communication opportunity, bounded disruption, and recovery horizon.

The two-study design addresses that gap in complementary ways. Study 8 provides controlled fixed-capacity reasoning. Study 8E replaces synthetic timing with separately frozen public observation-opportunity timing while solving rate rather than imposing a fixed rate. No cross-study sample or common physical timescale is assumed.

## 3. Shared Cryptographic-Recovery Framework

### 3.1 Trusted-recovery state machine

Both studies use the same frozen logical state progression:

COMPROMISED  
→ RECOVERY_AUTHORITY_ESTABLISHED  
→ SUCCESSOR_CRYPTO_PROFILE_SELECTED  
→ SUCCESSOR_KEY_MATERIAL_STAGED  
→ TRANSITION_PROOF_ACCEPTED  
→ NEW_EPOCH_COMMITTED  
→ OLD_EPOCH_REVOKED  
→ TRUST_RESTORED

The state machine is an experimental abstraction for trusted post-compromise transition. It is not asserted to be a NIST- or CCSDS-prescribed operational protocol.

### 3.2 Cryptographic profiles and transition objects

FIPS 203 and FIPS 204 define the standardized ML-KEM and ML-DSA objects used to construct three exact frozen algorithm-pair profiles [@NIST_FIPS203_2024; @NIST_FIPS204_2024]:

- PROFILE_512_44: ML-KEM-512 + ML-DSA-44;
- PROFILE_768_65: ML-KEM-768 + ML-DSA-65;
- PROFILE_1024_87: ML-KEM-1024 + ML-DSA-87.

The identifiers denote exact algorithm pairs only and are not asserted to be matched NIST security-category profiles.

Each transition contains seven cryptographic objects in fixed priority order: a recovery-authority assertion signature, successor KEM encapsulation key, successor signature-verification key, KEM ciphertext, transition-proof signature, new-epoch commit signature, and post-commit confirmation signature. Private keys are not transmitted.

The resulting base cryptographic-object budgets are:

- 12,560 bytes for PROFILE_512_44;
- 17,460 bytes for PROFILE_768_65;
- 24,236 bytes for PROFILE_1024_87.

These values represent standardized cryptographic objects only. They exclude certificate chains, transport headers, CCSDS framing, coding overhead, implementation metadata, and private keys.

### 3.3 Recovery policies

The same four policy semantics are used in both studies.

**P0 — Hard cutover.** Predecessor control acceptance is revoked at recovery start. Successor acceptance begins at new-epoch commit. Trust restoration requires post-commit confirmation.

**P1 — Staged cutover.** Predecessor acceptance remains during staging. Predecessor revocation and successor acceptance occur atomically at commit.

**P2 — Hybrid overlap.** Predecessor acceptance remains during staging. Successor acceptance begins after transition-proof acceptance, creating a modeled dual-epoch interval until predecessor revocation at commit.

**P3 — Contact-aware staged.** P3 uses P1 staged semantics plus a deterministic pre-commit guard. The guard may inspect only frozen schedule/timing information, current transition state, delivered bytes, selected profile, and horizon/deadline. It cannot inspect future disruption outcomes. It permits commit only when nominal remaining opportunity is sufficient for the unsent commit and confirmation requirements under the respective study model.

The policies share the same required transition-object bundle. P3 can block or defer an infeasible commitment; it cannot create opportunity, increase capacity, or shrink the bundle.

### 3.4 Bounded disruption semantics

Both studies use four mechanistic disruption schedules:

- A0_NONE;
- A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT;
- A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT;
- A3_STALE_EPOCH_REPLAY_AT_COMMIT.

The adversary cannot forge ML-DSA signatures, recover private keys, break ML-KEM, perform quantum cryptanalysis, adapt its schedule to observed outcomes, or modify frozen study factors.

### 3.5 Interpretation boundary shared by both studies

Neither study measures onboard cryptographic execution time, CPU utilization, memory use, accelerator performance, power, energy, thermal behavior, side-channel behavior, RF performance, link margin, packet framing, coding overhead, certification, or operational spacecraft availability.

The model evaluates cryptographic-object transfer and logical trust-state behavior under frozen opportunity abstractions. Any extension to operational performance would require separate evidence.

## 4. Study 1 — Controlled Logical-Contact Experiment (Study 8)

### 4.1 Frozen research question

Study 8 asks:

> **How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?**

### 4.2 Deterministic finite population

Experiment S8-PQC-ICR-001 crosses:

- 3 cryptographic profiles;
- 4 recovery policies;
- 4 contact regimes;
- 4 disruption schedules;
- 6 compromise phase offsets; and
- 3 logical recovery deadlines.

The complete Cartesian population contains 3 × 4 × 4 × 4 × 6 × 3 = 3,456 deterministic positions. Every factor position occurs exactly once.

The study reports exact finite-population counts and arithmetic summaries rather than sampling p-values or confidence intervals because the object of inference is the complete frozen modeled population.

### 4.3 Logical contact model

Logical time is represented by slots 0 through 47. A slot is an ordering unit only and has no physical duration.

All four regimes provide exactly 65,536 nominal cryptographic-object bytes over the complete 48-slot cycle while distributing opportunity differently:

- R1_FREQUENT_SMALL: 16 contacts × 4,096 bytes;
- R2_PERIODIC_MEDIUM: 8 contacts × 8,192 bytes;
- R3_SPARSE_LARGE: 4 contacts × 16,384 bytes;
- R4_CLUSTERED_MEDIUM: 8 contacts × 8,192 bytes in four two-contact clusters.

Six deterministic compromise offsets shift the post-compromise contact schedule. The deadlines are D12, D24, and D48. TRUST_RESTORED must occur at a slot strictly less than the selected deadline.

No conversion from slots to seconds, minutes, orbital periods, or physical contact duration is permitted.

### 4.4 Endpoint and frozen analysis

The primary endpoint is modeled trusted recovery before the selected deadline without stale or compromised epoch acceptance. Each policy has 864 equally weighted positions. The prespecified primary contrast is P3 minus P1 because P3 adds the contact-budget guard to P1 staged-cutover semantics.

Secondary endpoints include completion slot among successes, contacts consumed, modeled cryptographic bytes transferred, transition attempts, legacy exposure, control unavailability, dual-epoch overlap, rollback invocation, stale-epoch acceptance, and terminal state.

A separately implemented same-repository reference model reproduced all 3,456 canonical rows exactly. A separate statistical implementation reproduced the frozen machine-readable findings byte-for-byte. These checks demonstrate same-repository implementation-separated reproducibility, not external laboratory replication.

### 4.5 Primary policy result

All four transition policies achieved modeled trusted recovery in exactly 635/864 positions, or 73.4954%. The prespecified P3-minus-P1 risk difference was therefore exactly 0/1, or 0.000000 percentage points.

The null result also held in every prespecified stratum.

By contact regime, P1 and P3 each achieved:

- R1: 171/216 = 79.1667%;
- R2: 173/216 = 80.0926%;
- R3: 166/216 = 76.8519%;
- R4: 125/216 = 57.8704%.

By disruption, both achieved:

- A0: 163/216 = 75.4630%;
- A1: 160/216 = 74.0741%;
- A2: 156/216 = 72.2222%;
- A3: 156/216 = 72.2222%.

By deadline, both achieved:

- D12: 94/288 = 32.6389%;
- D24: 253/288 = 87.8472%;
- D48: 288/288 = 100%.

The P3 guard therefore did not increase fixed-capacity recovery success in the frozen Study 8 population.

### 4.6 Cryptographic-object burden under fixed capacity

Profile success differed substantially:

- PROFILE_512_44: 1080/1152 = 93.7500%;
- PROFILE_768_65: 748/1152 = 64.9306%;
- PROFILE_1024_87: 712/1152 = 61.8056%.

Across all 1,152 matched positions that held policy, contact regime, disruption, phase, and deadline constant, success was non-increasing as the standardized object bundle increased. The exact matched patterns were:

- 111: 712 positions;
- 110: 36 positions;
- 100: 332 positions;
- 000: 72 positions.

No matched position showed a larger frozen object bundle succeeding when a smaller bundle failed.

This finding concerns transfer burden under the frozen contact model. It does not compare algorithm security strength, processor execution time, energy, or implementation quality.

### 4.7 Contact timing and logical recovery horizon

Because all four contact regimes have the same 65,536-byte full-cycle nominal capacity, their different success proportions demonstrate that aggregate capacity alone does not determine deadline feasibility. The partitioning and temporal placement of capacity matter.

The deadline gradient is also strong: P1/P3 success rises from 32.6389% at D12 to 87.8472% at D24 and 100% at D48.

These are logical deadline effects only.

### 4.8 Policy-state and resource tradeoffs

Policy did not alter the primary success proportion, but it altered modeled state and resource endpoints.

P0 had zero predecessor exposure by construction but mean logical control unavailability of 12.195602 slots. P1 had zero control-unavailable slots and mean predecessor exposure of 12.195602 slots. P2 retained predecessor exposure and added mean dual-epoch overlap of 3.403935 logical slots.

P3 retained P1-like zero control unavailability but had mean predecessor exposure of 12.497685 logical slots. Compared with P1, P3 used 0.020833 fewer contacts on average, 433.711806 fewer modeled cryptographic bytes on average, and 0.116898 fewer transition attempts on average.

Terminal failure distributions also differed. P1 and P2 each produced 52 EPOCH_DIVERGENCE and 177 INSUFFICIENT_MATERIAL_TRANSFER outcomes. P3 produced 148 CONTACT_BUDGET_EXHAUSTED and 81 INSUFFICIENT_MATERIAL_TRANSFER outcomes while retaining the same 635 successes.

Rollback invocation and stale-epoch acceptance were zero throughout the frozen Study 8 lattice. These are model-invariant checks rather than evidence about operational spacecraft behavior.

## 5. Study 2 — External Observation-Opportunity Timing Extension (Study 8E)

### 5.1 Frozen extension questions

Study 8E asks four prospectively frozen questions.

**RQ1.** What observation-opportunity duration, inter-opportunity-gap, window-count, and gap-variability structure is observed in prospectively selected public satellite observation traces under a frozen source-selection rule?

**RQ2.** For the frozen Study 8 cryptographic transition-object bundles replayed over externally observed observation-opportunity windows, what minimum hypothetical uniform effective payload rate is required to reach TRUST_RESTORED within each extension-only elapsed-time horizon?

**RQ3.** Under the same externally observed observation-opportunity timing traces and transition-object requirements, do the four frozen Study 8 policy semantics change the minimum-rate feasibility threshold or primarily redistribute transition-state costs and terminal failure classifications?

**RQ4.** Which qualitative Study 8 findings remain directionally consistent, differ, or become non-identifiable when synthetic contact timing is replaced by external contact timing, without pooling the two evidence populations?

### 5.2 External source and frozen population governance

Study 8E uses the SatNOGS Network observations API as its primary external observation-opportunity timing source [@SATNOGS_API_2026]. The source window was frozen prospectively to June 1 through June 30, 2026 UTC.

The trace unit is NORAD catalog identifier × ground station. Selection used only pre-endpoint source metadata. Qualifying pairs required at least 20 observations in the frozen source window. Candidate pairs were ranked by a deterministic SHA-256 key, with a maximum of two selected pairs per NORAD identifier and two per station, under a hard acquisition request cap.

The corrected frozen population, S8E-SATNOGS-POP-002, contains 20 selected satellite-station trace pairs. The frozen first-page source projection, S8E-SATNOGS-TRACE-002, contains 476 observation rows and only five persisted fields: id, start, end, ground_station, and norad_cat_id. Its JSONL SHA-256 is 6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e.

The earlier POP-001 qualification attempt was invalidated before any recovery endpoint was computed because the generated API parameter used for satellite filtering did not match the live API behavior. The corrected POP-002 acquisition used the verified norad_cat_id + ground_station filter and was frozen before timing analysis. POP-001 is never used scientifically.

### 5.3 Observation-opportunity timing mapping

For each valid selected observation, source start and end are treated as an external observation-opportunity timing window. Overlapping or directly abutting windows within one trace are unioned for timing arithmetic while retaining source IDs for provenance.

No cross-station or cross-satellite merging is used in the primary analysis. The model does not infer communication capacity from SatNOGS source metadata. In particular, transmitter baud is not used as recovery throughput.

A SatNOGS observation-opportunity window is not an authenticated or bidirectional command link. It does not establish mission authorization, cryptographic trust, RF quality, payload capacity, or operational spacecraft availability.

### 5.4 External timing population

The corrected canonical artifact retains 20 traces, 476 raw observations, and 476 merged timing windows. Thus no frozen source windows were collapsed by the within-trace overlap/abutment rule in this population.

The per-trace frozen timing summaries show heterogeneous opportunity structures. Each trace contains 20 to 25 merged windows. Per-trace median window duration ranges from 180 to 603.5 seconds, while per-trace maximum window duration ranges up to 771 seconds. Median inter-opportunity gaps vary from 31,165 to 132,427.5 seconds across the 20 traces. The frozen gap coefficient of variation ranges from 0.373159 to 1.334886, and the corresponding burstiness index ranges from -0.456496 to 0.143427.

These descriptors characterize only the frozen public observation-opportunity traces. They do not establish operational communications performance.

### 5.5 Extension replay and endpoint

Each accepted merged observation-window end time is a candidate compromise anchor. Only anchors with complete source coverage through the full 24-hour follow-up horizon are eligible for all primary horizon comparisons. The corrected population contains 454 eligible anchors.

For each anchor, Study 8E crosses:

- 3 elapsed-time horizons: 6 h, 12 h, 24 h;
- 3 cryptographic profiles;
- 4 recovery policies;
- 4 disruption schedules.

This gives 144 cases per eligible anchor and 65,376 canonical cases.

The central endpoint is the minimum hypothetical uniform effective payload rate in bit/s required to reach TRUST_RESTORED strictly before the selected horizon. The rate is modeled as a constant net payload rate available only during accepted observation-opportunity windows. It is a solved threshold parameter, not a SatNOGS measurement.

A case is classified non-finite when no finite rate can complete the frozen transition under the available timing windows before the horizon. The corrected canonical runner uses the strict-before-horizon sufficient upper bound floor(8B/d_min)+1 and is independently audited.

### 5.6 Corrected canonical result and audit status

The first canonical result package was invalidated before scientific freeze after an adversarial review found a strict-before-horizon bound defect that misclassified 24 exact-divisibility cases. Those results are not used here.

The corrected execution, workflow run 35536583594, used S8E-CANON-RUNNER-004. It passed 10 runner tests, produced byte-identical outputs across two execution passes, and had zero independent case mismatches. The corrected artifact is formally frozen under S8E-CANON-RESULTS-002-FREEZE-001.

The immutable artifact contains one documented non-scientific metadata inconsistency: CANONICAL_FINDINGS.json identifies Results-002, while RESULTS_HASH_MANIFEST.json retains the stale Results-001 label. The corrected file hashes are bound by the audit and freeze records; the artifact is not rewritten and no rerun is required for scientific validity.

### 5.7 Overall minimum-rate feasibility

Across 65,376 canonical cases:

- finite minimum-rate threshold: 17,640 cases;
- non-finite: 47,736 cases;
- finite fraction: 245/908 = 0.269824 = 26.9824%.

Among finite cases, the minimum hypothetical uniform effective payload-rate threshold ranges from 48 to 57,727 modeled bit/s, with a median of 345 bit/s.

These values are model thresholds only. They are not measured satellite, ground-station, or RF link rates.

### 5.8 Recovery-horizon dependence

Finite threshold availability increases with elapsed-time horizon:

- 6 h: 1,152/21,792 = 0.052863 = 5.2863%;
- 12 h: 4,488/21,792 = 0.205947 = 20.5947%;
- 24 h: 12,000/21,792 = 0.550661 = 55.0661%.

Longer available elapsed time therefore expands the finite-feasibility set in the frozen external timing population.

These elapsed-time horizons must not be mapped to Study 8 D12, D24, or D48 logical deadlines.

### 5.9 Disruption dependence

Finite threshold fractions also differ by disruption schedule:

- A0: 6,624/16,344 = 0.405286;
- A1: 6,624/16,344 = 0.405286;
- A2: 2,196/16,344 = 0.134361;
- A3: 2,196/16,344 = 0.134361.

The result shows that timing-sensitive disruption semantics can materially restrict the set of cases with a finite modeled rate under the available observation-opportunity windows. It does not estimate attack prevalence, mission risk, or real-world outage frequency.

### 5.10 Policy threshold comparison

Each policy has exactly 4,410 finite and 11,934 non-finite cases out of 16,344.

For the prespecified P3/P1 matched contrast:

- matched comparisons: 16,344;
- both finite: 4,410;
- both non-finite: 11,934;
- P3 lower threshold: 0;
- P3 higher threshold: 0;
- all 4,410 both-finite threshold differences: exactly 0 bit/s.

The contact-aware guard therefore has no minimum-rate feasibility advantage over ordinary staged cutover in the frozen Study 8E population.

### 5.11 Cryptographic-profile burden

Each profile has exactly 5,880 finite cases out of 21,792. Thus profile choice does not change finite versus non-finite classification under the solved-rate endpoint.

However, the matched rate-burden ordering is preserved in all 21,792 profile comparisons, with zero ordering violations. This means the larger standardized transition bundles require no less modeled communication burden than the smaller bundles when comparing matched external-timing cases.

This result is not inconsistent with Study 8's profile-specific success proportions. The studies use different estimands: Study 8 fixes capacity and observes success, whereas Study 8E solves the rate required to achieve success when a finite threshold exists.

### 5.12 Structural safety fields

Rollback invocation and stale-epoch acceptance sums are zero at both finite thresholds and non-finite sufficient-bound evaluations in the corrected extension outputs.

These are structural model checks. They do not prove that operational systems cannot roll back or accept stale state.

## 6. Cross-Study Synthesis

Study 8 and Study 8E are separately frozen evidence populations. They have different time representations and different feasibility endpoints. No pooled sample size, pooled effect, combined confidence interval, or slot-to-seconds conversion is valid.

The purpose of synthesis is therefore structural: identify findings that are directionally consistent, findings that change under the different endpoint, and findings that are not comparable.

### 6.1 Does contact-aware staging increase feasibility?

In Study 8, P3 and P1 have identical fixed-capacity recovery success. The prespecified marginal difference is 0.000000 percentage points, and the contrast is zero in every prespecified stratum.

In Study 8E, P3 and P1 again have identical feasibility classification. Among all 4,410 both-finite comparisons, the minimum-rate threshold difference is exactly 0 bit/s.

The bounded cross-study conclusion is:

> Across both frozen evidence layers, the P3 pre-commit guard does not increase the respective feasibility endpoint because it does not add communication opportunity, increase capacity, or reduce the required cryptographic-object bundle.

This is a structural consistency result, not an external replication claim.

### 6.2 How does cryptographic-object burden appear under different estimands?

Study 8 fixes modeled contact capacity. Under that condition, larger transition bundles reduce the set of positions that can complete before the logical deadline: success falls from 93.7500% to 64.9306% and 61.8056% across the three increasing object bundles.

Study 8E instead solves for the minimum rate. Under this endpoint, the three profiles have the same finite/non-finite classification count, but their required-rate burden ordering is preserved in all 21,792 matched comparisons.

The distinction is important. A larger bundle can make recovery fail when capacity is fixed. If rate is instead allowed to increase as a solved parameter, profile size can appear as a higher required rate rather than a change in whether some finite rate exists.

The two results therefore describe complementary system-design questions:

- **fixed-capacity question:** does the transition fit?;
- **solved-rate question:** what modeled communication rate would make it fit?

### 6.3 What does additional recovery time change?

Study 8 shows a strong logical deadline gradient: P1/P3 success increases from 32.6389% at D12 to 87.8472% at D24 and 100% at D48.

Study 8E shows an elapsed-time horizon gradient: finite-threshold cases increase from 5.2863% at 6 h to 20.5947% at 12 h and 55.0661% at 24 h.

The only permitted cross-study statement is qualitative:

> Longer allowed recovery time expands the feasible set in both studies.

The percentages cannot be directly compared because the endpoints and time representations differ. D12, D24, and D48 are logical slot deadlines and have no mapping to 6, 12, or 24 hours.

### 6.4 What does timing structure contribute?

Study 8 demonstrates under controlled conditions that equal aggregate full-cycle capacity does not imply equal deadline success when opportunity is partitioned and placed differently in logical time.

Study 8E contributes separately sourced observation-opportunity timing with substantial variation in window duration and inter-opportunity gap structure. The extension therefore strengthens the evidence that temporal opportunity should be represented explicitly rather than reduced to an aggregate capacity number.

Study 8E does not establish that the SatNOGS traces are operational command schedules. It provides an external timing stress layer only.

### 6.5 What do disruption results imply?

In Study 8, disruption changes success strata under fixed capacity, but P3 remains identical to P1 within every disruption category.

In Study 8E, A0 and A1 each have a 40.5286% finite fraction, whereas A2 and A3 each have 13.4361%. Because the extension endpoint solves rate under finite observed opportunity windows, disruptions that consume or delay critical timing opportunities can move many cases into the non-finite set.

The magnitude of these effects is specific to each model and endpoint. No cross-study disruption effect size is calculated.

### 6.6 What remains non-identifiable?

The combined evidence does not identify:

- real spacecraft command-contact availability;
- real RF throughput;
- mission-specific recovery success probability;
- onboard ML-KEM/ML-DSA execution cost;
- energy or thermal burden;
- certificate or protocol-framing overhead;
- operator workload;
- policy superiority in unmodeled missions;
- causal effects of particular SatNOGS trace characteristics on real recovery.

These remain outside the evidence boundary.

## 7. Discussion

### 7.1 A guard cannot create communication capacity

The most consistent result across the two evidence layers is the absence of a P3 feasibility advantage over P1.

Mechanistically, this is understandable. P3 can decide whether to enter the commit portion of the transition based on remaining nominal opportunity. That can reduce modeled transfer use, transition attempts, or change terminal classification. It cannot add a contact, enlarge a window, increase capacity, or shrink the cryptographic-object bundle.

The negative result is therefore informative rather than a failed hypothesis. It distinguishes a **decision guard** from a **capacity-changing mechanism**. If a future recovery policy is expected to improve terminal feasibility, it would need to change scheduling, pre-staging, required artifacts, retransmission behavior, coding, directional transfer, or another mechanism that changes what can be delivered before the deadline.

### 7.2 Fixed-capacity feasibility and required-rate burden are different system questions

The principal conceptual contribution of the rebuilt paper is the separation between fixed-capacity success and solved-rate burden.

Study 8 asks whether a frozen transition bundle can traverse a fixed synthetic opportunity budget before a logical deadline. Under this endpoint, object size directly removes positions from the feasible set.

Study 8E instead asks how much hypothetical uniform payload rate would be required during externally observed opportunity windows. When a finite threshold exists, rate can rise to accommodate the cryptographic bundle. Profile size therefore appears primarily in the required-rate burden rather than in finite/non-finite classification.

These questions should not be collapsed. A design can be theoretically feasible at some finite modeled rate while still being infeasible under an actual system's available capacity. Conversely, a fixed-capacity model can identify where an object bundle exceeds the assumed budget without saying what physical link rate a mission would need.

The combined analysis provides a clearer engineering decomposition:

1. determine the cryptographic objects and transition semantics;
2. characterize when communication opportunity exists;
3. establish actual or assumed capacity constraints;
4. evaluate whether the transition fits, or solve the capacity/rate requirement;
5. separately evaluate the state cost incurred by the chosen transition policy.

### 7.3 Timing distribution matters independently of aggregate opportunity

Study 8 deliberately holds complete-cycle capacity constant while changing temporal distribution. The resulting success differences show that aggregate capacity is not sufficient under deadlines.

Study 8E reinforces the need to represent temporal structure with independently sourced observation-opportunity windows. The frozen traces contain varying window durations, large and heterogeneous gaps, and different gap-variability patterns. That timing structure materially determines whether a finite rate can complete the transition before the 6 h, 12 h, or 24 h horizon.

This finding is consistent with the broader NTN literature, where intermittent connectivity, long delays, handovers, and bandwidth constraints complicate post-quantum authentication and key management [@GSMA_PQ07_2026; @Eichen_etal_2026]. The present work contributes a recovery-state-specific model rather than a general claim about NTN performance.

### 7.4 Policy semantics remain important even without a feasibility winner

The four policies are identical on the Study 8 primary success proportion and Study 8E finite feasibility classification. They are not identical as state machines.

Hard cutover removes predecessor acceptance immediately but creates modeled control unavailability. Staged cutover preserves availability at the cost of predecessor exposure. Hybrid overlap permits bounded successor/predecessor overlap. Contact-aware staging changes resource use and terminal classification and slightly extends predecessor exposure in Study 8.

These differences illustrate why crypto-agility mechanisms should be evaluated on more than final success. Preserving ongoing operation while changing cryptography is explicitly part of NIST's crypto-agility framing [@NIST_CSWP39_2026]. A policy that does not enlarge the feasible set may still produce a different security-state trajectory.

The present evidence does not support an overall policy ranking. The appropriate choice depends on mission-specific tolerance for predecessor exposure, control interruption, overlap, transfer burden, and fallback behavior—quantities not fully represented here.

### 7.5 Implications for post-quantum satellite recovery engineering

Four bounded implications follow.

First, transition planning should account for the byte structure of the recovery transition itself, not only steady-state algorithm selection.

Second, timing should be represented explicitly. Aggregate capacity or a nominal average rate can hide deadline-relevant gaps and clustering.

Third, feasibility and transition-state cost should be evaluated separately. Whether a transition can finish and what security/availability state is exposed while it finishes are different design questions.

Fourth, a policy intended to improve feasibility must change a feasibility-driving mechanism. A guard that only blocks an infeasible commit may improve resource discipline or failure classification without changing which cases can ultimately succeed.

These implications are consistent with current PQC and crypto-agility work for space and NTNs [@Kim_2026_PQCSpace; @GSMA_PQ07_2026; @Mahn_Muller_Zielinski_2025; @DeZuane_etal_2026]. They are not deployment recommendations for any particular mission or cryptographic profile.

## 8. Limitations and External-Validity Boundary

### 8.1 Separate finite populations

Study 8 and Study 8E are separate frozen populations with separate endpoints. No pooled sample size or pooled statistical effect exists.

Study 8 contains 3,456 deterministic logical-contact positions. Study 8E contains 65,376 canonical external-timing cases derived from 454 eligible anchors across 20 frozen traces.

### 8.2 Logical versus elapsed time

Study 8 slots are ordering units only and have no physical duration.

Study 8E uses physical timestamps from public observation records, but those timestamps represent observation-opportunity timing only.

No Study 8 slot is converted to seconds, and no D12/D24/D48 deadline is equated with 6/12/24 h.

### 8.3 Observation opportunity is not command availability

SatNOGS observations do not prove authenticated, bidirectional, mission-authorized command contact. The source does not establish that the observed path could carry the recovery protocol modeled here.

The extension therefore supports timing sensitivity analysis, not operational link validation.

### 8.4 Modeled rate is not measured throughput

The hypothetical uniform effective payload rate is a solved model parameter. It is not a SatNOGS transmitter baud value, measured payload throughput, link margin, achievable spacecraft rate, or ground-station performance metric.

### 8.5 Cryptographic-object-only accounting

Both studies account for the frozen standardized cryptographic objects. They exclude certificate chains, protocol headers, CCSDS framing, coding overhead, metadata, retransmission protocols beyond the frozen mechanics, and implementation-specific encoding.

### 8.6 No cryptographic execution benchmarking

The studies do not measure ML-KEM or ML-DSA computation latency, CPU, memory, accelerator behavior, energy, thermal load, side channels, or flight implementation performance.

Profile findings therefore concern modeled transfer burden only.

### 8.7 Restricted adversary

The disruption model is deterministic, nonadaptive, and non-cryptanalytic. It excludes private-key recovery, signature forgery, KEM compromise, quantum cryptanalysis, fault injection, adaptive timing attacks, and side channels.

### 8.8 Simplified directionality and protocol behavior

Uplink/downlink direction, duplex restrictions, real acknowledgments, scheduling contention, antenna availability, RF propagation, coding, and mission operations are outside the model.

### 8.9 Study 8E source-selection boundary

Study 8E follows a frozen source window, deterministic ranking, entity caps, qualification threshold, request cap, and first-page acquisition rule. The target count of 32 trace pairs was not forced after the stopping rule yielded 20 selected pairs.

No additional cursor pages were followed after the frozen acquisition boundary.

### 8.10 Corrected-result metadata discrepancy

The corrected Study 8E scientific outputs are frozen and independently audited. The immutable Results-002 package contains a stale Results-001 label in RESULTS_HASH_MANIFEST.json, while CANONICAL_FINDINGS.json correctly identifies Results-002. The discrepancy affects packaging metadata only, not the frozen scientific rows or their hashes. It is preserved rather than silently rewritten.

### 8.11 No external experimental replication

Study 8 uses same-repository implementation-separated reproduction. Study 8E uses independently sourced public timing but reuses the frozen transition model. Neither constitutes an external laboratory replication of the complete scientific experiment.

### 8.12 No policy-superiority conclusion

The evidence does not support declaring P0, P1, P2, or P3 generally preferable. The primary feasibility endpoints are equal across policies in both studies, while secondary state costs differ.

### 8.13 Finite-population inference boundary

All numerical results describe the frozen finite populations evaluated. No sampling model supports generalization to arbitrary missions, constellations, operators, adversaries, or communication processes.

Future work should add actual mission contact schedules, measured capacity, protocol framing, directional links, implementation benchmarks, richer recovery mechanisms, and independent replication as new prospectively governed studies rather than altering the frozen Study 8 or Study 8E records.

## 9. Data, Code, and Reproducibility

Study 8 is frozen under experiment S8-PQC-ICR-001. Its canonical population contains 3,456 observations. The canonical observations SHA-256 is cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf. The frozen primary findings SHA-256 is 26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e.

Study 8E is frozen under experiment S8E-ECTV-001. The corrected result authority is S8E-CANON-RESULTS-002-FREEZE-001. The frozen source trace is S8E-SATNOGS-TRACE-002 with 476 source rows and SHA-256 6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e. The corrected canonical execution is GitHub Actions run 35536583594, artifact 10613372166, with artifact ZIP SHA-256 3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee.

The corrected canonical case results contain 65,376 rows. Independent case mismatches are zero, deterministic execution outputs are byte-identical across two passes, and the corrected strict-bound audit passes.

Detailed hashes, protocol deviations, invalidated prior results, population freezes, and result-freeze governance records are maintained in the public research repository. The invalidated Results-001 package must not be used for scientific claims.

## 10. Conclusion

This paper evaluated trusted post-compromise post-quantum cryptographic recovery using two separately governed evidence layers.

Study 8 examined fixed-capacity feasibility across a complete 3,456-position deterministic logical-contact population. The four tested policies achieved exactly the same primary trusted-recovery proportion, 635/864 or 73.4954%, and P3 minus P1 was 0.000000 percentage points in every prespecified stratum. Fixed-capacity feasibility instead changed substantially with standardized cryptographic-object burden, temporal contact distribution, and logical recovery deadline.

Study 8E replaced synthetic timing with a prospectively frozen public observation-opportunity timing population without modifying or pooling Study 8. Across 65,376 canonical cases, 26.9824% had a finite minimum hypothetical uniform effective payload-rate threshold. Finite thresholds ranged from 48 to 57,727 modeled bit/s with a median of 345 bit/s. Longer elapsed-time horizons expanded the finite set, and P3 again showed no feasibility advantage over P1. The three profiles had identical finite/non-finite classification counts, but their communication-burden ordering was preserved in every matched comparison.

Taken together, the studies separate fixed-capacity feasibility from required-rate burden. A contact-aware pre-commit guard can change resource use, state exposure, or failure classification, but it does not create communication opportunity. Cryptographic transition-object burden, when opportunity becomes available, and how long recovery is allowed remain central constraints.

The external timing layer strengthens the relevance of the timing argument without converting the evidence into operational spacecraft-contact or throughput measurements. Extending the conclusions to deployment will require new evidence for mission-specific contact schedules, measured link capacity, protocol overhead, onboard cryptographic execution, and operational recovery requirements.

## Declarations

### Funding

This research was conducted independently and received no external funding.

### Competing interests

The author declares no competing financial or non-financial interests.

### Author contributions

**Aman Kumar Singh:** Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing – original draft; Writing – review & editing; Visualization; Project administration.

### Ethics

The reported Studies 8 and 8E are software/modeling and public-data research. They do not involve human participants, identifiable private information, animals, live spacecraft operations, unauthorized access, or radio-frequency experimentation.

### Artificial-intelligence assistance

Generative-AI language assistance was used during manuscript development and publication-package review. The author retains responsibility for scientific interpretation, review, and final approval. The frozen Study 8 and Study 8E scientific results, evidence identities, and claim boundaries were not altered during manuscript integration. Any venue-specific disclosure will be aligned with the selected publisher's current policy at the later submission-package gate.
