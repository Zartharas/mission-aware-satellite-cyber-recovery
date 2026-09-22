# Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing

**{{AUTHOR_DISPLAY_NAME}}, MS, PhD**  
{{AUTHOR_AFFILIATION}}, {{AUTHOR_LOCATION}}  
ORCID: {{AUTHOR_ORCID}}  
Corresponding author: {{AUTHOR_DISPLAY_NAME}}, {{AUTHOR_EMAIL}}

**Short title:** Post-Quantum Satellite Recovery Under Intermittent Connectivity

## Abstract

Long-lived satellite systems may need to replace compromised cryptographic state during intermittent connectivity while post-quantum transition objects impose substantial transfer burden. This paper evaluates trusted post-compromise recovery using two separately governed finite studies that are reported together but never statistically pooled. Study 8 exhaustively evaluates 3,456 deterministic logical-contact positions spanning three standardized post-quantum algorithm-pair profiles, four transition policies, four equal-full-cycle-capacity contact regimes, four bounded disruptions, six compromise offsets, and three logical deadlines. All four policies recover in 635 of 864 positions (73.4954%), and the prespecified contact-aware staged minus staged difference is exactly 0.000000 percentage points. Fixed-capacity success is 93.7500%, 64.9306%, and 61.8056% across the three increasing transition-object burdens. Study 8E applies the same frozen transition requirements to prospectively governed public SatNOGS observation-opportunity timing. Across 65,376 cases, 17,640 (26.9824%) have a finite minimum hypothetical uniform effective payload-rate threshold, ranging from 48 to 57,727 modeled bit/s with a median of 345 bit/s. All 4,410 both-finite P3 versus P1 comparisons differ by exactly 0 bit/s. Together, the studies distinguish fixed-capacity feasibility from required-rate burden and show how communication opportunity, recovery horizon, and cryptographic-object burden constrain modeled recovery. SatNOGS observations are timing proxies only, not authenticated command contacts or measured throughput.

**Keywords:** post-quantum cryptography; satellite communications; post-compromise recovery; intermittent connectivity; observation-opportunity timing; cryptographic transition; recovery feasibility; SatNOGS

## 1. Introduction

Satellite systems combine long service lives, constrained physical maintenance opportunities, intermittent communications, and increasing requirements for cyber resilience. These characteristics make cryptographic transition more than an algorithm-replacement problem. When predecessor credentials or cryptographic state can no longer be trusted, recovery requires a successor state to be selected, transferred, accepted, committed, confirmed, and made authoritative before the available communication opportunity or recovery horizon is exhausted. Post-quantum cryptography can intensify this systems problem because standardized public keys, ciphertexts, and signatures can be materially larger than the classical artifacts they replace.

NIST defines crypto agility as the capabilities needed to replace or adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving security and ongoing operations [@NIST_CSWP39_2026]. FIPS 203 and FIPS 204 standardize ML-KEM and ML-DSA [@NIST_FIPS203_2024; @NIST_FIPS204_2024], while SP 800-227 emphasizes that safe KEM use depends on the surrounding protocol and system context rather than the primitive in isolation [@NIST_SP800227_2025]. This systems perspective is especially important after compromise, when the transition must preserve an acceptable trust state while successor material is staged and activated.

Recent space and non-terrestrial-network research has examined post-quantum algorithms, migration, hybrid mechanisms, authentication burden, implementation constraints, key management, and crypto agility [@GSMA_PQ07_2026; @Mahn_Muller_Zielinski_2025; @Wildfeuer_etal_2025; @Robles_etal_2025; @Kim_2026_PQCSpace]. Ghosh and Nath analyze lattice-based PQC in satellite communication settings [@Ghosh_Nath_2026]. Eichen et al. examine post-quantum authentication pressure in bandwidth- and power-constrained environments, including NTNs [@Eichen_etal_2026]. De Zuane et al. evaluate efficient quantum-safe IKE variants for satellite communications, including hybrid transition mechanisms and communication-resource considerations [@DeZuane_etal_2026]. These studies establish that PQC overhead and transition design are active satellite and NTN research problems. The contribution of the present work is therefore not that PQC is relevant to satellites, that post-quantum objects can be large, or that crypto agility is desirable.

The narrower question considered here is what constrains trusted post-compromise cryptographic recovery when communication opportunity is intermittent. That question couples transition-object burden, the temporal placement of communication opportunity, trust-state progression, disruption, and recovery horizon. Satellite cybersecurity literature has long emphasized the dependence of missions on trustworthy communications and resilient software-defined infrastructure [@HousenCouriel_2016; @Falco_2019], while protocol and platform studies have examined security mechanisms for federated satellite systems [@vonMaurich_Golkar_2018]. IEEE 3536-2026 provides contemporary space-system cybersecurity design context [@IEEE3536_2026]. The CCSDS data-link security architecture is also relevant as algorithm-independent architectural context, but this paper does not claim that ML-KEM or ML-DSA are operational CCSDS profiles or that the modeled transition is a CCSDS-prescribed protocol [@CCSDS_SDLS].

Study 8 first isolated the recovery question in a complete deterministic logical-contact population. It found an exact negative primary result: adding a contact-aware pre-commit guard to staged cutover did not increase modeled trusted-recovery success. Feasibility instead varied with standardized cryptographic-object burden, temporal contact structure, disruption, and logical deadline. Because Study 8 deliberately used logical slots with no physical duration, it could not address how the same frozen transition requirements interact with externally observed timing.

Study 8E therefore adds a separately governed external timing layer without modifying Study 8. It uses prospectively frozen public SatNOGS observation start and end times as observation-opportunity timing proxies [@SATNOGS_API_2026]. It does not treat those observations as authenticated command contacts, infer payload throughput from transmitter metadata, assign cryptographic trust to ground stations, or convert Study 8 logical slots to seconds. Instead, it solves a different endpoint: the minimum hypothetical uniform effective payload rate required for the frozen transition model to reach TRUST_RESTORED strictly before a 6 h, 12 h, or 24 h extension-only horizon.

The two studies answer complementary systems questions. Study 8 asks whether a transition fits within a fixed modeled opportunity budget. Study 8E asks what modeled rate would be required for the transition to fit within separately sourced opportunity timing. Their populations, time representations, and estimands remain distinct, and no pooled denominator, effect estimate, confidence interval, or slot-to-seconds mapping is used.

The resulting article makes three bounded contributions. First, it turns post-compromise PQC transition into a quantified recovery-feasibility problem: given exact standardized ML-KEM and ML-DSA transition-object burdens and a frozen trust-state progression, can the required state change complete before an intermittent modeled opportunity boundary? Second, it tests whether additional contact-aware policy logic moves that feasibility boundary under matched conditions while separately retaining predecessor exposure, availability, overlap, transfer, attempt, and failure-classification behavior. Third, it evaluates the same frozen transition requirements over an independently governed observation-opportunity timing population and distinguishes fixed-capacity feasibility from solved-rate burden without pooling the studies. The scientific object of interest is therefore the recovery-feasibility boundary and the mechanisms that can move it, not generic PQC overhead, algorithm benchmarking, or an overall ranking of recovery policies.

## 2. Recovery Model and Methods

### 2.1 Two-study evidence architecture

This article reports Study 8, experiment `S8-PQC-ICR-001`, together with Study 8E, experiment `S8E-ECTV-001`. The studies share a frozen cryptographic-recovery mechanism but use separate evidence populations and endpoints. Study 8 is a deterministic finite logical-contact experiment. Study 8E is a separately frozen replay over public observation-opportunity timing. Integration in one manuscript does not create a common sample or a common physical timescale.

The manuscript-level framing question is: **What constrains trusted post-compromise post-quantum cryptographic recovery when communication opportunity is intermittent, and which structural findings remain when analysis moves from a controlled logical contact budget to separately governed public observation-opportunity timing?** This framing does not replace either study's frozen research question or endpoint.

### 2.2 Trusted-recovery mechanism

Both studies use the same frozen logical state progression: COMPROMISED, RECOVERY_AUTHORITY_ESTABLISHED, SUCCESSOR_CRYPTO_PROFILE_SELECTED, SUCCESSOR_KEY_MATERIAL_STAGED, TRANSITION_PROOF_ACCEPTED, NEW_EPOCH_COMMITTED, OLD_EPOCH_REVOKED, and TRUST_RESTORED. The state machine is an experimental abstraction for trusted post-compromise transition and is not asserted to be a NIST- or CCSDS-prescribed operational protocol. Figure 1 summarizes this shared frozen progression.

FIPS 203 and FIPS 204 provide the standardized ML-KEM and ML-DSA object sizes used in three frozen algorithm-pair profiles [@NIST_FIPS203_2024; @NIST_FIPS204_2024]. PROFILE_512_44 combines ML-KEM-512 with ML-DSA-44, PROFILE_768_65 combines ML-KEM-768 with ML-DSA-65, and PROFILE_1024_87 combines ML-KEM-1024 with ML-DSA-87. The identifiers denote exact algorithm pairs only and are not claims that the paired algorithms share an identical NIST security category.

Each transition carries seven cryptographic objects in fixed priority order: a recovery-authority assertion signature, successor KEM encapsulation key, successor signature-verification key, KEM ciphertext, transition-proof signature, new-epoch commit signature, and post-commit confirmation signature. Private keys are never transmitted. The resulting base cryptographic-object budgets are 12,560 bytes for PROFILE_512_44, 17,460 bytes for PROFILE_768_65, and 24,236 bytes for PROFILE_1024_87. These budgets cover the standardized cryptographic objects only. They exclude certificate chains, transport and protocol headers, CCSDS framing, coding overhead, implementation metadata, and private keys.

The four recovery policies preserve the same required transition bundle but differ in state-transition semantics. P0 hard cutover revokes predecessor control acceptance at recovery start, permits successor acceptance at commit, and requires post-commit confirmation for trust restoration. P1 staged cutover retains predecessor acceptance during staging and changes predecessor and successor acceptance atomically at commit. P2 hybrid overlap retains predecessor acceptance while allowing successor acceptance after transition-proof acceptance, creating a bounded dual-epoch interval until commit. P3 contact-aware staged uses P1 semantics plus a deterministic pre-commit guard. That guard can inspect only frozen schedule or timing information, current transition state, delivered bytes, selected profile, and deadline or horizon. It cannot inspect future disruption outcomes. P3 can block or defer a nominally infeasible commit, but it cannot create communication opportunity, increase capacity, or reduce the required object bundle.

Both studies use four bounded mechanistic disruption schedules: A0_NONE, A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT, A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT, and A3_STALE_EPOCH_REPLAY_AT_COMMIT. The adversary cannot forge ML-DSA signatures, recover private keys, break ML-KEM, perform quantum cryptanalysis, adapt its schedule to observed outcomes, or modify frozen study factors.

### 2.3 Study 8 controlled logical-contact design

Study 8 asks: **How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?**

The complete deterministic population crosses 3 cryptographic profiles, 4 recovery policies, 4 contact regimes, 4 disruption schedules, 6 compromise phase offsets, and 3 logical recovery deadlines. The Cartesian population therefore contains 3 x 4 x 4 x 4 x 6 x 3 = 3,456 positions, each evaluated exactly once. Table 1 summarizes the frozen design. Because the object of inference is the complete modeled population rather than a sample drawn from a larger stochastic population, the study reports exact counts and arithmetic summaries rather than sampling p-values or confidence intervals.

Logical time consists of slots 0 through 47. A slot is an ordering unit only and has no physical duration. Each of the four contact regimes provides exactly 65,536 nominal cryptographic-object bytes over the full 48-slot cycle while distributing the opportunity differently. R1_FREQUENT_SMALL provides 16 contacts of 4,096 bytes, R2_PERIODIC_MEDIUM provides 8 contacts of 8,192 bytes, R3_SPARSE_LARGE provides 4 contacts of 16,384 bytes, and R4_CLUSTERED_MEDIUM provides 8 contacts of 8,192 bytes arranged as four two-contact clusters. Six deterministic compromise offsets shift the post-compromise contact schedule. The deadlines are D12, D24, and D48, and TRUST_RESTORED must occur at a slot strictly less than the selected deadline. No slot is converted to seconds, minutes, orbital periods, or physical contact duration.

The primary endpoint is modeled trusted recovery before the selected deadline without stale or compromised epoch acceptance. Each policy has 864 equally weighted positions. The prespecified primary contrast is P3 minus P1 because P3 adds only the contact-budget guard to the staged-cutover semantics of P1. Secondary endpoints include completion slot among successes, contacts consumed, modeled cryptographic bytes transferred, transition attempts, predecessor exposure, control unavailability, dual-epoch overlap, rollback invocation, stale-epoch acceptance, and terminal state.

A separately implemented same-repository reference model reproduced all 3,456 canonical rows exactly, and a separate statistical implementation reproduced the frozen machine-readable findings byte-for-byte. These checks establish implementation-separated reproduction within the repository, not external laboratory replication.

### 2.4 Study 8E observation-opportunity timing design

Study 8E prospectively asks how public observation-opportunity timing is distributed under a frozen source-selection rule, what minimum hypothetical uniform effective payload rate is required to complete the frozen transition before extension-only elapsed-time horizons, whether policy semantics change that threshold or primarily redistribute transition-state costs, and which Study 8 findings remain directionally consistent without pooling the evidence populations.

The extension uses the SatNOGS Network observations API as its public timing source [@SATNOGS_API_2026]. The acquisition window was frozen to June 1 through June 30, 2026 UTC. The trace unit is NORAD catalog identifier by ground station. Qualifying pairs required at least 20 observations in the frozen source window. Candidate pairs were ranked by a deterministic SHA-256 key, with at most two selected pairs per NORAD identifier and at most two per station, under a hard acquisition request cap.

The corrected population `S8E-SATNOGS-POP-002` contains 20 satellite-station trace pairs. The frozen source projection `S8E-SATNOGS-TRACE-002` contains 476 observation rows and only the fields id, start, end, ground_station, and norad_cat_id. Its JSONL SHA-256 is `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`. An earlier POP-001 qualification attempt was invalidated before any recovery endpoint was calculated because the generated API filtering parameter did not match live API behavior. The corrected POP-002 acquisition used the verified norad_cat_id plus ground_station filter and was frozen before timing analysis. POP-001 is not used for scientific claims.

Each accepted observation start and end defines an observation-opportunity timing window. Overlapping or directly abutting windows within one trace are unioned for timing arithmetic while source identifiers are retained for provenance. The corrected population contains 476 raw observations and 476 merged windows, so no frozen source windows were collapsed by that rule. No cross-station or cross-satellite merging is used in the primary analysis. SatNOGS transmitter baud is not used as payload throughput, station identity is not treated as cryptographic trust, and an observation does not establish a bidirectional, authenticated, mission-authorized command link.

The frozen timing population contains 20 to 25 merged windows per trace. Per-trace median window duration ranges from 180 to 603.5 seconds, maximum window duration reaches 771 seconds, and median inter-opportunity gaps range from 31,165 to 132,427.5 seconds. Frozen gap coefficients of variation range from 0.373159 to 1.334886, with corresponding burstiness indices from -0.456496 to 0.143427. These values characterize only the selected public observation-opportunity timing and do not establish operational communications performance.

Each accepted merged-window end is a candidate compromise anchor. Primary comparisons require complete source coverage through the full 24-hour follow-up horizon, yielding 454 eligible anchors. Every anchor is crossed with three extension-only horizons (6 h, 12 h, and 24 h), three cryptographic profiles, four recovery policies, and four disruption schedules. This yields 144 cases per anchor and 65,376 canonical cases.

The central Study 8E endpoint is the minimum hypothetical uniform effective payload rate, in integer bit/s, required to reach TRUST_RESTORED strictly before the selected horizon. The rate is modeled as a constant net payload rate available only within accepted observation-opportunity windows. It is a solved threshold parameter, not a SatNOGS measurement. A case is non-finite if no finite rate can complete the frozen transition under the available timing windows before the horizon.

The corrected canonical search uses a strict-before-horizon sufficient upper bound. Let B equal sum(profile_object_bytes) + max(profile_object_bytes), representing the complete nominal profile-object bundle plus one retransmission of the largest object. Let d_min be the shortest positive duration, in exact seconds, among future observation-opportunity windows available to the case. The integer sufficient bound is U_strict = floor(8B/d_min) + 1 bit/s. This construction is used to bound the model search. It is not a measured physical link capacity, SatNOGS throughput, or recommended mission data rate.

The first canonical extension result package was invalidated before scientific freeze after adversarial review identified a strict-before-horizon bound defect affecting 24 exact-divisibility cases. The corrected execution, GitHub Actions run 35536583594, used `S8E-CANON-RUNNER-004`, passed 10 runner tests, produced byte-identical outputs across two execution passes, and had zero independent case mismatches. The corrected result is frozen as `S8E-CANON-RESULTS-002-FREEZE-001`. The immutable package retains one documented packaging-only discrepancy: `CANONICAL_FINDINGS.json` identifies Results-002, while `RESULTS_HASH_MANIFEST.json` retains a stale Results-001 label. The corrected file hashes are bound by the audit and freeze records, so the package is preserved rather than silently rewritten.

### 2.5 Reproducibility, interpretation boundaries, and AI-assisted preparation

Neither study measures onboard ML-KEM or ML-DSA execution time, CPU use, memory, accelerator performance, energy, thermal behavior, side-channel behavior, RF performance, link margin, bit-error rate, coding efficiency, packet framing, certification, operator workload, or operational spacecraft availability. Study 8 evaluates logical trust-state progression under a deterministic capacity abstraction. Study 8E evaluates the same frozen transition semantics over public observation-opportunity timing while solving a hypothetical payload-rate threshold. Any operational inference would require separate mission-specific evidence.

The frozen research repository contains the study protocols, source code, validation scripts, canonical results, result manifests, evidence hashes, and audit records supporting this paper [@Singh_Paper4_Repository_2026]. The invalidated Study 8E Results-001 package remains preserved for provenance but is not used scientifically.

OpenAI ChatGPT / GPT-5.6 Sol was used during 2026 manuscript preparation for drafting and restructuring assistance, language editing, literature navigation and metadata checking, claim-boundary review, and venue-specific submission preparation. The author independently reviewed and verified the scientific claims, citations, numerical values, equations, source identities, interpretations, and publisher-facing materials. The tool did not generate, alter, manipulate, or replace Study 8 data, Study 8E data, study protocols, canonical result files, evidence hashes, prespecified endpoints, or corrected Results-002 scientific findings. The author retains full responsibility for the manuscript.

## 3. Results

### 3.1 Study 8 fixed-capacity feasibility

Across the complete Study 8 population, each of the four policies achieved modeled trusted recovery in exactly 635 of 864 positions, or 73.4954%. The prespecified P3 minus P1 difference is therefore exactly 0.000000 percentage points. The null contrast also holds within every prespecified contact-regime, disruption, and deadline stratum.

For P1 and P3, success by contact regime is 171/216 (79.1667%) in R1, 173/216 (80.0926%) in R2, 166/216 (76.8519%) in R3, and 125/216 (57.8704%) in R4. By disruption, both achieve 163/216 (75.4630%) under A0, 160/216 (74.0741%) under A1, and 156/216 (72.2222%) under both A2 and A3. By logical deadline, both achieve 94/288 (32.6389%) at D12, 253/288 (87.8472%) at D24, and 288/288 (100%) at D48. These are logical deadline effects only.

Cryptographic-object burden produces a different pattern. Fixed-capacity success is 1,080/1,152 (93.7500%) for PROFILE_512_44, 748/1,152 (64.9306%) for PROFILE_768_65, and 712/1,152 (61.8056%) for PROFILE_1024_87. Across all 1,152 matched positions holding policy, contact regime, disruption, compromise phase, and deadline constant, success is non-increasing as the frozen object bundle grows. The matched patterns are 111 in 712 positions, 110 in 36, 100 in 332, and 000 in 72. No matched position has a larger frozen object bundle succeed when the smaller bundle fails. Figure 2 summarizes the profile-level fixed-capacity success proportions. This is a transfer-burden result under the frozen contact model, not an algorithm security, computation-speed, or implementation-quality ranking.

Because all four contact regimes provide exactly 65,536 bytes over the complete logical cycle, their different success proportions also show that equal aggregate capacity does not uniquely determine deadline feasibility in this model. The partitioning and placement of the opportunity matter.

Although policy does not change primary success, it changes modeled state and resource behavior. P0 has zero predecessor exposure by construction but mean logical control unavailability of 12.195602 slots. P1 has zero control-unavailable slots and mean predecessor exposure of 12.195602 slots. P2 retains predecessor exposure and introduces mean dual-epoch overlap of 3.403935 logical slots. P3 retains P1-like zero control unavailability but has mean predecessor exposure of 12.497685 logical slots. Relative to P1, P3 uses 0.020833 fewer contacts, 433.711806 fewer modeled cryptographic bytes, and 0.116898 fewer transition attempts on average. P1 and P2 each produce 52 EPOCH_DIVERGENCE and 177 INSUFFICIENT_MATERIAL_TRANSFER terminal failures; P3 produces 148 CONTACT_BUDGET_EXHAUSTED and 81 INSUFFICIENT_MATERIAL_TRANSFER failures while retaining the same 635 successes. Rollback invocation and stale-epoch acceptance are zero throughout the frozen Study 8 lattice. These are model-invariant checks, not evidence that operational systems cannot roll back or accept stale state.

### 3.2 Study 8E observation-opportunity timing and modeled rate

Table 2 summarizes the corrected Study 8E authority. Across 65,376 canonical cases, 17,640 have a finite minimum-rate threshold and 47,736 are non-finite. The finite fraction is 245/908, or 26.9824%. Among finite cases, the minimum hypothetical uniform effective payload-rate threshold ranges from 48 to 57,727 modeled bit/s, with a median of 345 bit/s. These are model thresholds only.

Finite-threshold availability increases with elapsed-time horizon. At 6 h, 1,152 of 21,792 cases are finite (5.2863%). At 12 h, 4,488 of 21,792 are finite (20.5947%). At 24 h, 12,000 of 21,792 are finite (55.0661%). The extension therefore shows that additional elapsed-time opportunity expands the finite set within the frozen public timing population. Figure 3 summarizes the horizon-specific finite fractions. These horizons have no mapping to Study 8 D12, D24, or D48 logical deadlines.

Disruption also changes finite classification under the extension endpoint. A0 and A1 each have 6,624 finite cases of 16,344 (40.5286%), while A2 and A3 each have 2,196 of 16,344 (13.4361%). These fractions are properties of the frozen extension mechanics and timing population. They do not estimate attack prevalence, outage probability, or operational mission risk.

Each recovery policy has exactly 4,410 finite and 11,934 non-finite cases among its 16,344 Study 8E cases. For the prespecified P3 versus P1 matched contrast, all 16,344 comparisons have the same finite/non-finite classification: 4,410 are both finite and 11,934 are both non-finite. P3 has zero lower-threshold cases and zero higher-threshold cases. Every one of the 4,410 both-finite differences is exactly 0 bit/s. Thus the contact-aware guard provides no minimum-rate feasibility advantage over ordinary staged cutover in the frozen extension.

Each cryptographic profile has exactly 5,880 finite cases among 21,792. Profile choice therefore does not alter finite versus non-finite classification under the solved-rate endpoint. The communication-burden ordering is nevertheless preserved in all 21,792 matched profile comparisons, with zero ordering violations. Larger standardized transition bundles require no less modeled rate burden than smaller bundles in matched finite cases.

Rollback invocation and stale-epoch acceptance sums are zero in both finite-threshold and non-finite sufficient-bound evaluations. Again, these are structural checks of the frozen model rather than operational safety claims.

### 3.3 Cross-study synthesis without pooling

The strongest structural consistency concerns P3 versus P1. Study 8 reports an exact 0.000000 percentage-point P3 minus P1 fixed-capacity success difference. Study 8E reports identical finite/non-finite classification for P3 and P1, and every both-finite minimum-rate difference is 0 bit/s. Across both evidence layers, the pre-commit guard changes no respective feasibility endpoint because it does not add communication opportunity, enlarge capacity, or shrink the transition bundle. This is structural consistency across separate studies, not an external replication or pooled effect.

The studies show cryptographic-object burden differently because they hold different quantities fixed. In Study 8, capacity is fixed, so larger bundles remove positions from the feasible set and success falls from 93.7500% to 64.9306% and 61.8056% across the three profiles. In Study 8E, rate is the solved quantity. All three profiles therefore have the same finite/non-finite counts, but the required-rate burden ordering is preserved in every matched profile comparison. The two endpoints answer different engineering questions: whether a transition fits a fixed modeled budget, and what modeled rate would be required for it to fit when a finite threshold exists.

Time allowance also has a consistent directional role without becoming a common scale. Study 8 P1/P3 success increases from 32.6389% at D12 to 87.8472% at D24 and 100% at D48. Study 8E finite cases increase from 5.2863% at 6 h to 20.5947% at 12 h and 55.0661% at 24 h. The permitted synthesis is only that longer allowed recovery time expands the feasible set in both studies. The percentages are not directly comparable, and no Study 8 logical deadline is mapped to an elapsed-time horizon.

## 4. Discussion

### 4.1 What the null policy contrast means

The repeated absence of a P3 feasibility advantage is mechanistically informative. P3 can decide whether sufficient nominal opportunity remains to enter the commit portion of the transition. That guard can reduce modeled transfer use, transition attempts, or change terminal classification. It cannot create a contact, lengthen an observation window, increase capacity, or reduce the required cryptographic-object bundle. A policy intended to increase terminal feasibility in this model family would therefore need to change a feasibility-driving mechanism, such as scheduling, pre-staging, object requirements, retransmission behavior, or another feature that changes what can be delivered before the deadline. The value of the null contrast is therefore diagnostic rather than competitive: it identifies a class of policy intervention that changes transition behavior without moving the terminal feasibility boundary under the frozen constraints.

The result should not be generalized into universal policy equivalence. P0, P1, P2, and P3 have identical primary Study 8 success and identical Study 8E finite counts, but their trust-state trajectories differ. Hard cutover minimizes predecessor exposure by accepting modeled control unavailability. Staged cutover preserves modeled control availability while retaining predecessor acceptance during staging. Hybrid overlap permits a bounded interval in which predecessor and successor acceptance coexist. Contact-aware staged cutover changes resource use and failure classification and slightly increases mean predecessor exposure in Study 8. Mission-specific preferences among these tradeoffs are outside the evidence presented here.

### 4.2 Fixed-capacity feasibility and solved-rate burden

The central conceptual distinction is between a fixed-capacity feasibility problem and a solved-rate requirement. Study 8 asks whether a frozen transition bundle can traverse a fixed synthetic opportunity budget before a logical deadline. Study 8E asks how much hypothetical uniform payload rate would be required within separately sourced timing windows. A transition can have a finite modeled rate threshold and still exceed the actual capacity of a real mission. Conversely, a fixed-capacity failure identifies that the bundle does not fit the assumed budget but does not identify a physical rate requirement. Together, these estimands provide complementary views of the same recovery-feasibility boundary: one holds modeled opportunity capacity fixed and observes completion, while the other holds the observation-opportunity timing trace fixed and solves the uniform rate required for completion.

This distinction helps separate four engineering questions that are often conflated: what cryptographic objects and state transitions are required; when communication opportunity exists; what actual or assumed capacity is available; and what security or availability state is exposed during transition. The present studies address the first two directly within frozen abstractions and examine the third only as fixed capacity or a solved model parameter. They do not measure the operational link.

### 4.3 Timing structure, disruption, and transition burden

Study 8 deliberately holds full-cycle aggregate capacity constant while changing its temporal distribution. The resulting regime differences show that aggregate capacity alone is insufficient under deadlines. Study 8E adds public observation-opportunity timing with heterogeneous durations and gaps, reinforcing the need to represent the placement of opportunity rather than only a nominal average rate or total budget.

This timing argument is consistent with broader NTN work in which intermittent connectivity, latency, handovers, and constrained communication complicate post-quantum authentication and key management [@GSMA_PQ07_2026; @Eichen_etal_2026]. The present evidence is narrower: it concerns a frozen recovery-state transition and does not estimate NTN performance generally.

The disruption findings should be interpreted similarly. Study 8 disruption strata alter success levels while leaving P3 equal to P1 within every disruption category. Study 8E produces lower finite fractions under A2 and A3 than under A0 and A1 because the specified disruption mechanics consume or delay critical opportunity in the finite timing windows. No cross-study disruption effect size is calculated, and the findings do not estimate how frequently such attacks or disruptions occur operationally.

### 4.4 Engineering implications and external-validity limits

Four implications are supported within the modeled evidence. Transition planning should account for the byte structure of the recovery transition itself, not only steady-state algorithm selection. Temporal opportunity should be represented explicitly because equal aggregate capacity can produce different deadline outcomes. Terminal feasibility and transition-state cost should be evaluated separately because equal success does not imply equal predecessor exposure, control interruption, overlap, or transfer behavior. Finally, a guard that only prevents an infeasible commitment cannot improve terminal feasibility unless it also changes a capacity-, timing-, or object-burden mechanism.

These implications remain bounded by the study abstractions. Study 8 and Study 8E are separate finite populations. Study 8 slots have no physical duration. Study 8E timestamps represent public observation opportunities, not authenticated, bidirectional, mission-authorized command contacts. The solved rate is not SatNOGS transmitter baud, measured payload throughput, link margin, or ground-station performance. Neither study includes certificate chains, transport framing, CCSDS framing, coding overhead, implementation-specific encoding, real acknowledgments, uplink/downlink asymmetry, duplex restrictions, scheduling contention, antenna availability, RF propagation, or mission operations.

The studies also do not benchmark ML-KEM or ML-DSA execution latency, CPU, memory, accelerators, energy, thermal behavior, or side channels. The disruption model is deterministic, nonadaptive, and non-cryptanalytic. It excludes private-key recovery, signature forgery, KEM compromise, quantum cryptanalysis, fault injection, adaptive timing attacks, and side channels. The Study 8E source-selection procedure is frozen and finite; its target count of 32 trace pairs was not forced after the stopping rule yielded 20 selected pairs, and no additional cursor pages were followed after the acquisition boundary.

Study 8E is not an external experimental replication of Study 8. It provides independently sourced timing while reusing the frozen transition mechanism. The corrected Results-002 package also retains the documented stale Results-001 label in `RESULTS_HASH_MANIFEST.json`; this packaging inconsistency does not change the corrected scientific rows or hashes and is preserved for provenance.

Accordingly, the numerical findings describe only the frozen populations evaluated. They do not identify real spacecraft command-contact availability, real RF throughput, mission-specific recovery probability, operator workload, or an overall best recovery policy. Extending the conclusions to deployment requires new prospectively governed evidence for mission contact schedules, measured capacity, framing and coding overhead, directional links, onboard cryptographic execution, and operational recovery requirements.

## 5. Data, Code, and Reproducibility

Study 8 is frozen under experiment `S8-PQC-ICR-001`. Its canonical population contains 3,456 observations. The canonical observations SHA-256 is `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`, and the frozen primary findings SHA-256 is `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`.

Study 8E is frozen under experiment `S8E-ECTV-001`. The corrected authority is `S8E-CANON-RESULTS-002-FREEZE-001`. The source trace `S8E-SATNOGS-TRACE-002` contains 476 rows and has SHA-256 `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`. The corrected canonical execution is GitHub Actions run 35536583594, artifact 10613372166, whose ZIP SHA-256 is `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`. Corrected canonical case results contain 65,376 rows, independent case mismatches are zero, two execution passes are byte-identical, and the corrected strict-bound audit passes.

Detailed protocols, source code, result manifests, invalidation records, population freezes, validation scripts, and audit evidence are preserved in the public research repository snapshot cited with this article [@Singh_Paper4_Repository_2026]. Results-001 remains non-authoritative and must not be used for scientific claims.

## 6. Conclusions

This article quantifies a recovery-feasibility boundary for trusted post-compromise post-quantum cryptographic transition under intermittent modeled communication opportunity. The central question is not whether constrained communication or larger cryptographic objects can make recovery harder in the abstract, but which frozen transition requirements and opportunity structures determine whether recovery can complete, and whether added contact-aware policy logic changes that boundary.

Study 8 evaluates a complete 3,456-position deterministic logical-contact population. All four tested policies achieve the same primary trusted-recovery proportion, 635/864 or 73.4954%, and the prespecified P3 minus P1 difference is 0.000000 percentage points in every prespecified stratum. Fixed-capacity feasibility instead changes with standardized transition-object burden, temporal opportunity structure, disruption, and logical recovery deadline.

Study 8E preserves the transition mechanism while replacing synthetic timing with a separately frozen public observation-opportunity timing population. Across 65,376 corrected canonical cases, 17,640 (26.9824%) have a finite minimum hypothetical uniform effective payload-rate threshold. Finite thresholds range from 48 to 57,727 modeled bit/s with a median of 345 bit/s. Longer elapsed-time horizons expand the finite set, and P3 again has no feasibility advantage over P1. The three cryptographic profiles have identical finite/non-finite counts, while their modeled communication-burden ordering is preserved in every matched comparison.

The repeated P3-versus-P1 null result is the central mechanism finding. The contact-aware pre-commit guard changes modeled resource use, state exposure, and failure classification, but it does not create communication opportunity, increase capacity, or reduce the transition-object bundle; accordingly, it does not improve terminal feasibility in either frozen evidence layer. In contrast, cryptographic-object burden, temporal placement of opportunity, disruption, and allowed recovery horizon are the structural quantities that move the modeled feasible set.

Study 8 and Study 8E therefore provide complementary views of the same bounded engineering problem: fixed-capacity completion and required-rate burden. The external timing layer strengthens evidence about timing structure without turning SatNOGS observations into operational command contacts or measured throughput. Deployment conclusions require separate mission-specific evidence for contact authorization, measured link capacity, protocol overhead, onboard cryptographic execution, and operational recovery requirements.

## Funding

This research was conducted independently and received no external funding.

## Conflict of Interest

The author declares no competing financial or non-financial interests.

## Author Contributions

**{{AUTHOR_DISPLAY_NAME}}:** Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing - original draft; Writing - review and editing; Visualization; Project administration.

## Ethics Statement

The reported Studies 8 and 8E are software/modeling and public-data research. They do not involve human participants, identifiable private information, animals, live spacecraft operations, unauthorized access, or radio-frequency experimentation.

## Data Availability Statement

The data, code, analysis scripts, frozen protocols, result manifests, evidence hashes, and audit records supporting this article are publicly available in the *Mission-Aware Satellite Cyber Recovery* research repository [@Singh_Paper4_Repository_2026]. Study 8 materials are maintained under `study8/` and `publication/study8/`. Study 8E materials, including the frozen SatNOGS observation-opportunity trace, corrected canonical results, independent audit records, and formal Results-002 freeze, are maintained under `study8e/`. The cited repository snapshot provides an immutable commit identity for the evidence used in this manuscript. The repository also preserves invalidated intermediate Study 8E artifacts as provenance and marks them non-authoritative.

<!-- R5_REFERENCES_INSERTION_POINT -->

## Figure Legends

**Figure 1.** Frozen trusted-recovery state progression shared by Study 8 and Study 8E. The diagram is an experimental abstraction of post-compromise trust transition and is not an operational protocol standard.

**Figure 2.** Study 8 fixed-capacity modeled trusted-recovery success by standardized cryptographic algorithm-pair profile. Percentages describe the complete frozen deterministic Study 8 population and do not measure algorithm execution performance.

**Figure 3.** Study 8E fraction of cases with a finite minimum hypothetical uniform effective payload-rate threshold by extension-only elapsed-time horizon. SatNOGS observations provide timing proxies only; plotted fractions do not represent measured link feasibility.

## Table 1. Study 8 deterministic experimental design

| Factor | Levels | Frozen values / interpretation |
| --- | ---: | --- |
| Cryptographic profile | 3 | PROFILE_512_44, PROFILE_768_65, PROFILE_1024_87 |
| Recovery policy | 4 | P0 hard cutover, P1 staged cutover, P2 hybrid overlap, P3 contact-aware staged |
| Logical contact regime | 4 | R1 16 x 4,096 bytes; R2 8 x 8,192 bytes; R3 4 x 16,384 bytes; R4 8 x 8,192 bytes in four two-contact clusters |
| Disruption schedule | 4 | A0 none; A1 drop first largest-object fragment; A2 delay first transition proof by one contact; A3 stale-epoch replay at commit |
| Compromise phase offset | 6 | Six deterministic offsets of the post-compromise contact schedule |
| Logical recovery deadline | 3 | D12, D24, D48; TRUST_RESTORED must occur strictly before the selected logical deadline |
| Complete population | 3,456 | 3 x 4 x 4 x 4 x 6 x 3 deterministic positions |

**Table 1 note.** Logical slots are ordering units only and have no physical duration.

## Table 2. Study 8E corrected canonical evaluation summary

| Quantity | Frozen value |
| --- | ---: |
| Population authority | S8E-SATNOGS-POP-002 |
| Trace authority | S8E-SATNOGS-TRACE-002 |
| Satellite-station trace pairs | 20 |
| Frozen source observations | 476 |
| Eligible compromise anchors | 454 |
| Canonical cases | 65,376 |
| Finite cases | 17,640 |
| Non-finite cases | 47,736 |
| Finite fraction | 26.9824% |
| Finite threshold minimum | 48 modeled bit/s |
| Finite threshold median | 345 modeled bit/s |
| Finite threshold maximum | 57,727 modeled bit/s |
| P3 versus P1 matched comparisons | 16,344 |
| P3 versus P1 both finite | 4,410 |
| P3 versus P1 both non-finite | 11,934 |
| P3 versus P1 finite threshold differences | 0 bit/s in all 4,410 both-finite cases |
| Profile-burden ordering violations | 0 |
| Rollback violations | 0 |
| Stale-acceptance violations | 0 |

**Table 2 note.** The rate is a hypothetical uniform effective payload-rate threshold used by the frozen model. It is not SatNOGS transmitter baud, measured throughput, or an operational spacecraft link rate.
