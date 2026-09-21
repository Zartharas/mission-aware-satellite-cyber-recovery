# Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing

**Aman Kumar Singh, MS, DSc**  
Independent Researcher, The Woodlands, Texas, United States  
ORCID: https://orcid.org/0009-0008-9752-3743

## Abstract

Long-lived satellite and non-terrestrial systems may need to replace compromised cryptographic state without assuming continuously available communication. Post-quantum migration makes this recovery problem more demanding because standardized key, ciphertext, and signature objects can impose substantial transfer burden even before certificate, framing, retransmission, and implementation overhead are considered. This paper evaluates trusted post-compromise cryptographic recovery through two separately governed finite studies that are reported together but never pooled. **Study 8** is an exhaustive deterministic logical-contact experiment with 3,456 positions crossing three ML-KEM/ML-DSA object profiles, four recovery policies, four equal-total-capacity contact regimes, four bounded disruptions, six compromise offsets, and three logical deadlines. **Study 8E** is a prospectively governed external timing extension using 20 frozen SatNOGS satellite-station trace pairs, 476 public observation records, 454 eligible compromise anchors, and 65,376 canonical recovery cases. Study 8 asks whether trusted recovery succeeds under a fixed modeled contact budget; Study 8E instead solves the minimum hypothetical uniform effective payload rate required under externally observed observation-opportunity timing.

Study 8 produced an exact negative primary policy result: all four policies restored modeled trust in 635/864 positions (73.4954%), and the prespecified contact-aware staged-minus-staged difference was 0.000000 percentage points in every prespecified stratum. Fixed-capacity success nevertheless varied sharply with standardized transition-object burden: 93.7500%, 64.9306%, and 61.8056% across the three increasing bundles, with non-increasing success in all 1,152 matched non-profile positions. Study 8E found a finite modeled rate threshold in 17,640/65,376 cases (26.9824%), with finite thresholds from 48 to 57,727 bps and a median of 345 bps. The finite fraction increased from 5.2863% at 6 h to 20.5947% at 12 h and 55.0661% at 24 h. P3 and P1 had identical finite/non-finite classification in all 16,344 matched cases, and every one of the 4,410 both-finite comparisons had a 0 bps threshold difference. Profile finite/non-finite classification was also identical, while required-rate burden ordering was preserved in all 21,792 matched profile checks.

Together, the studies distinguish **fixed-capacity recovery feasibility** from **required-rate burden**. A contact-aware pre-commit guard does not create communication capacity or reduce the cryptographic object bundle; transition burden, opportunity timing, and recovery horizon determine the feasible set under the respective frozen models. SatNOGS observations are used only as public observation-opportunity timing proxies and are not treated as authenticated command contacts or measured link throughput.

**Keywords:** post-quantum cryptography; cryptographic agility; ML-KEM; ML-DSA; satellite cybersecurity; post-compromise recovery; intermittent connectivity; SatNOGS; recovery feasibility

---

## 1. Introduction

Space systems combine long service lives, limited physical access after deployment, constrained maintenance opportunities, intermittent communications, and increasingly explicit cybersecurity requirements. These characteristics make cryptographic transition a systems problem rather than a simple algorithm-replacement exercise. NIST defines cryptographic agility as the capability to replace or adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving security and ongoing operations [@NIST_CSWP39_2026]. NIST FIPS 203 and FIPS 204 standardize ML-KEM and ML-DSA, respectively [@NIST_FIPS203_2024; @NIST_FIPS204_2024], while SP 800-227 emphasizes that secure use of key-encapsulation mechanisms depends on surrounding protocol and system conditions rather than the KEM primitive alone [@NIST_SP800227_2025].

The space and non-terrestrial networking literature already establishes that post-quantum migration is relevant to satellite systems. Recent work spans algorithm and implementation surveys, lattice-based performance analysis, hybrid migration, quantum-safe key exchange, constrained authentication, and space-specific crypto-agility mechanisms [@Kim_2026_PQCSpace; @Ghosh_Nath_2026; @DeZuane_etal_2026; @Eichen_etal_2026; @Mahn_Muller_Zielinski_2025; @GSMA_PQ07_2026]. IEEE 3536-2026 further reflects the broader systems emphasis on cybersecurity design across space-system components and interfaces [@IEEE3536_2026]. Consequently, neither “post-quantum cryptography for satellites” nor “larger post-quantum objects” is by itself a defensible novelty claim.

A narrower question arises after compromise. If predecessor credentials or cryptographic state can no longer be trusted, a system must establish a successor cryptographic epoch, transfer the required successor material, prove the transition, commit the new epoch, revoke the predecessor state, and confirm restoration. In an intermittently connected system, those actions compete with finite communication opportunity and a recovery horizon. The engineering problem therefore depends on at least three dimensions: the amount of cryptographic material that must move, when communication opportunity is available, and how much time remains before recovery is no longer useful.

This paper addresses that problem with two separately frozen evidence layers.

**Study 8 / S8-PQC-ICR-001** is a controlled deterministic experiment over a complete 3,456-position logical-contact population. It holds total full-cycle contact capacity constant across four synthetic schedules while varying when capacity becomes available. It tests three exact ML-KEM/ML-DSA object bundles, four transition policies, four disruptions, six compromise offsets, and three logical deadlines. The primary endpoint is modeled trusted recovery before the deadline.

**Study 8E / S8E-ECTV-001** is a separately governed extension that preserves Study 8's transition objects and policy semantics but replaces the synthetic contact schedule with prospectively selected public SatNOGS observation-opportunity timing. It does not reinterpret Study 8's logical slots as physical time. Instead, for each frozen external timing case, it solves a distinct endpoint: the minimum hypothetical uniform effective payload rate that would be required for the modeled transition to reach TRUST_RESTORED strictly before a 6 h, 12 h, or 24 h extension horizon.

The two populations are not pooled, and their numerical endpoints are not treated as estimates of the same quantity. The combined manuscript asks a higher-level systems question:

> **What constrains trusted post-compromise post-quantum cryptographic recovery when communication opportunity is intermittent, and which structural findings remain when analysis moves from a controlled logical contact budget to independently sourced public observation-opportunity timing?**

Four contributions follow.

1. **Controlled trusted-recovery model.** Study 8 couples exact standardized ML-KEM/ML-DSA object sizes to an explicit post-compromise cryptographic state machine, intermittent logical contact, bounded disruption, and recovery deadlines.

2. **Feasibility-versus-state-cost separation.** Study 8 preserves the prespecified negative policy result while showing that cryptographic-object burden, contact timing, and deadline alter the fixed-capacity feasible set, whereas policy semantics redistribute predecessor exposure, control availability, overlap, resource use, and failure classification.

3. **Separately frozen external timing extension.** Study 8E evaluates the same transition semantics over prospectively governed SatNOGS observation-opportunity timing and solves minimum modeled payload-rate thresholds without inferring throughput from SatNOGS metadata.

4. **Cross-study structural synthesis.** The paper distinguishes fixed-capacity feasibility from required-rate burden and examines whether the policy null, time-horizon sensitivity, and cryptographic-burden ordering remain directionally consistent across the two non-pooled evidence layers.

The central result is deliberately not a policy-superiority claim. A contact-aware pre-commit guard does not enlarge the feasible set in either frozen study. The stronger systems contribution is the separation of three ideas that are often conflated: **whether recovery can finish under a fixed budget, how much modeled rate is required under a given timing structure, and what security-state cost is incurred while attempting the transition.**

## 2. Related Work and Standards Context

### 2.1 Post-quantum cryptography for satellite and non-terrestrial systems

NIST's post-quantum standards provide the cryptographic primitives used for the modeled object budgets in this work. FIPS 203 specifies ML-KEM and its three parameter sets, while FIPS 204 specifies ML-DSA [@NIST_FIPS203_2024; @NIST_FIPS204_2024]. These standards define cryptographic objects and algorithms, but they do not prescribe the recovery protocol modeled here.

Recent space-focused work demonstrates that PQC deployment must be treated as a systems problem. Kim's 2026 systematic survey synthesizes space-system PQC research across algorithms, hardware, software, protocol adaptation, hybrid migration, and standards gaps [@Kim_2026_PQCSpace]. Ghosh and Nath analyze lattice-based PQC in satellite-communication settings and discuss performance and migration constraints [@Ghosh_Nath_2026]. GSMA PQ.07 identifies latency, resource constraints, long platform lifecycles, interoperability, PKI, and phased migration as central NTN concerns [@GSMA_PQ07_2026].

Eichen et al. focus on the increased bandwidth, memory, computation, and energy requirements of PQ authentication in constrained and non-terrestrial networks, including key-rotation and key-management implications [@Eichen_etal_2026]. That work is currently a preprint and is cited as such. De Zuane et al. examine quantum-safe and hybrid IKE variants for satellite communications from design and experimental perspectives [@DeZuane_etal_2026]. These studies establish that bandwidth and protocol overhead matter, but they address handshake or implementation questions rather than the exact post-compromise epoch-transition state machine evaluated here.

### 2.2 Crypto agility and secure transition

NIST CSWP 39-upd1 treats cryptographic agility as a cross-layer capability needed to replace cryptography while maintaining security and operation [@NIST_CSWP39_2026]. Space-specific work by Mähn, Müller, and Zielinski develops crypto-agility definitions and considers remote update, failure, attack, and fallback mechanisms for space systems [@Mahn_Muller_Zielinski_2025]. ESA work has likewise examined quantum-safe satellite data-link architecture and high-assurance PQC for software-defined payloads [@Wildfeuer_etal_2025; @Robles_etal_2025].

The present work is narrower. It does not propose a general migration framework, a new handshake, or a flight-ready key-management architecture. Instead, it isolates the state-transition problem that occurs after predecessor cryptographic state is assumed compromised and asks whether the required successor material and proof objects can traverse finite intermittent opportunities before recovery expires.

### 2.3 Satellite cybersecurity and recovery context

Satellite cybersecurity literature has long emphasized the dependence of missions on trustworthy communications, software-controlled infrastructure, and cross-segment security [@HousenCouriel_2016; @Falco_2019]. Experimental work has also evaluated authentication, integrity, and confidentiality mechanisms for federated satellite systems [@vonMaurich_Golkar_2018]. IEEE 3536-2026 now provides a current system-level cybersecurity design standard for space systems [@IEEE3536_2026].

This study does not claim compliance with IEEE 3536, CCSDS, or a particular mission architecture. These sources provide context for why recoverable cryptographic state and secure transitions matter.

### 2.4 Public observation networks as timing evidence

SatNOGS Network provides an openly accessible API for scheduled and completed satellite observations and distributes API data under CC BY-SA [@SatNOGS_API_2026]. Study 8E uses only a narrow projection of this public source: observation identifiers, start, end, ground_station, and norad_cat_id. The source is used to obtain an external temporal structure for observation opportunities.

A SatNOGS observation is **not** assumed to be an authenticated, bidirectional, or operational spacecraft command contact. Transmitter baud is not used as recovery throughput. Station identity is not treated as cryptographic trust, observation status is not treated as authorization, and TLE state is not treated as cryptographic epoch state. These exclusions are central to the validity of Study 8E.

### 2.5 Gap addressed by this paper

The gap addressed here is therefore not PQC adoption in the abstract. It is the interaction among standardized post-quantum transition-object burden, explicit trusted post-compromise state progression, intermittent communication opportunity, finite recovery horizons, and transition policies that change security-state semantics.

The two-study design first evaluates this interaction under controlled logical contact with fixed total-cycle capacity and then challenges the timing assumption with a separately frozen public observation-opportunity population.

## 3. Shared Cryptographic-Recovery Framework

### 3.1 Recovery state machine

Both studies use the same frozen high-level state progression:

COMPROMISED  
→ RECOVERY_AUTHORITY_ESTABLISHED  
→ SUCCESSOR_CRYPTO_PROFILE_SELECTED  
→ SUCCESSOR_KEY_MATERIAL_STAGED  
→ TRANSITION_PROOF_ACCEPTED  
→ NEW_EPOCH_COMMITTED  
→ OLD_EPOCH_REVOKED  
→ TRUST_RESTORED

The transition models control-plane trust restoration rather than general mission recovery. Success requires reaching TRUST_RESTORED before the applicable study boundary without accepting stale or compromised epoch state.

### 3.2 Cryptographic object bundles

Three exact algorithm-pair profiles are frozen:

- PROFILE_512_44: ML-KEM-512 + ML-DSA-44;
- PROFILE_768_65: ML-KEM-768 + ML-DSA-65;
- PROFILE_1024_87: ML-KEM-1024 + ML-DSA-87.

The profile identifiers name exact algorithm pairs. They are not asserted to be matched NIST security-category bundles.

Each modeled transition moves seven standardized cryptographic objects in fixed priority order: a recovery-authority assertion signature, successor KEM encapsulation key, successor signature-verification key, KEM ciphertext, transition-proof signature, new-epoch commit signature, and post-commit confirmation signature. Private keys are never transmitted.

The frozen base transition-object budgets are 12,560 bytes, 17,460 bytes, and 24,236 bytes for the three profiles, respectively. These totals represent standardized cryptographic-object bytes only. They exclude certificate chains, transport headers, CCSDS framing, error correction, retransmission headers, implementation metadata, and private keys.

### 3.3 Recovery policies

The four policies use the same object bundle and deterministic object priority. Their treatment differences concern predecessor/successor acceptance state and, for P3, one pre-commit guard.

**P0 — Hard cutover.** Predecessor control acceptance is revoked at recovery start. Successor acceptance begins at new-epoch commit. Post-commit confirmation is required for trust restoration.

**P1 — Staged cutover.** Predecessor acceptance remains during staging. At commit, predecessor revocation and successor acceptance occur atomically. Confirmation is again required for TRUST_RESTORED.

**P2 — Hybrid overlap.** Predecessor acceptance remains during staging; successor acceptance begins after the transition proof; predecessor revocation occurs at commit. This creates a measurable dual-epoch overlap interval.

**P3 — Contact-aware staged.** P3 uses P1's staged acceptance semantics plus a deterministic nominal pre-commit capacity guard. The guard can inspect only information available under the frozen model. It cannot create communication opportunity, reduce the object bundle, or foresee future disruptions.

### 3.4 Disruptions and trust boundary

Both studies reuse four disruption mechanisms:

- A0_NONE;
- A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT;
- A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT;
- A3_STALE_EPOCH_REPLAY_AT_COMMIT.

The adversary is bounded and non-cryptanalytic. It cannot forge ML-DSA signatures, recover private keys, break ML-KEM, perform quantum cryptanalysis, or adapt the disruption schedule after observing outcomes.

The purpose of the disruption layer is to perturb transfer timing and state progression under a frozen deterministic design. It is not a model of the frequency or probability of real attacks.

## 4. Study 8 — Controlled Logical-Contact Experiment

### 4.1 Frozen research question

Study 8 asks:

> **How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?**

### 4.2 Complete deterministic population

Study 8 crosses three cryptographic profiles, four recovery policies, four contact regimes, four disruption schedules, six compromise phase offsets, and three logical deadlines. The complete Cartesian population therefore contains 3 × 4 × 4 × 4 × 6 × 3 = 3,456 positions.

Every position is evaluated exactly once. The object of inference is this complete frozen finite population rather than a random sample from a superpopulation. Results are therefore reported using exact counts, proportions, differences, medians, and arithmetic means without sampling p-values or sampling confidence intervals.

### 4.3 Logical contact schedules

Study 8 uses integer logical slots 0..47. A slot is an ordering unit only and has **no physical duration**.

All four contact regimes supply exactly 65,536 nominal cryptographic-object bytes over the complete 48-slot cycle:

- R1_FREQUENT_SMALL: 16 contacts × 4,096 bytes;
- R2_PERIODIC_MEDIUM: 8 contacts × 8,192 bytes;
- R3_SPARSE_LARGE: 4 contacts × 16,384 bytes;
- R4_CLUSTERED_MEDIUM: 8 contacts × 8,192 bytes arranged as four two-contact clusters.

The design therefore controls complete-cycle capacity while changing how that capacity is partitioned and placed in logical time.

Three logical deadlines are used: D12, D24, and D48. Recovery is on time only when TRUST_RESTORED occurs at a slot strictly less than the selected deadline.

### 4.4 Primary endpoint and analysis

The primary endpoint is modeled trusted recovery before the deadline without stale or compromised epoch acceptance.

Each policy has 864 equally weighted positions. The prespecified primary contrast is P3 minus P1 because P3 adds the nominal contact-budget guard to the staged-cutover semantics of P1.

Prespecified P3-minus-P1 contrasts are also evaluated by contact regime, profile, disruption, and deadline. Secondary endpoints include completion slot, contacts consumed, modeled cryptographic bytes, transition attempts, predecessor exposure, control-unavailable slots, P2 overlap, rollback invocation, stale-epoch acceptance, and terminal state.

## 5. Study 8 Results

### 5.1 Primary policy result: exact null

All four policies achieved modeled trusted recovery in exactly 635/864 positions (73.4954%). All six unordered pairwise policy success differences were therefore zero. The prespecified P3-minus-P1 risk difference was 0.000000 percentage points.

The P3/P1 null held in every prespecified stratum. P1 and P3 each achieved 94/288 (32.6389%) at D12, 253/288 (87.8472%) at D24, and 288/288 (100%) at D48.

By contact regime, each achieved 171/216 (79.1667%) in R1, 173/216 (80.0926%) in R2, 166/216 (76.8519%) in R3, and 125/216 (57.8704%) in R4.

By disruption, each achieved 163/216 (75.4630%) under A0, 160/216 (74.0741%) under A1, and 156/216 (72.2222%) under each of A2 and A3.

The frozen Study 8 population therefore does not support a claim that the P3 contact-aware guard increases modeled trusted-recovery success.

### 5.2 Cryptographic-object burden under fixed capacity

Success differed substantially across the three object bundles:

- PROFILE_512_44: 1080/1152 = 93.7500%;
- PROFILE_768_65: 748/1152 = 64.9306%;
- PROFILE_1024_87: 712/1152 = 61.8056%.

Relative to PROFILE_512_44, the exact finite-population differences are -28.819444 and -31.944444 percentage points for the middle and largest bundles. The largest-minus-middle difference is -3.125000 percentage points.

Across all 1,152 matched positions that hold policy, regime, disruption, phase, and deadline constant, success is non-increasing as the standardized object budget increases. The exact matched patterns are 712 positions where all profiles succeed, 36 where the two smaller profiles succeed, 332 where only PROFILE_512_44 succeeds, and 72 where none succeeds.

No matched position shows a larger bundle succeeding when a smaller one fails. This is a fixed-capacity transfer-burden result, not a comparison of cryptographic security strength or algorithm execution speed.

### 5.3 Contact timing and logical recovery horizon

The contact regimes differ despite identical complete-cycle capacity. In the P1/P3 strata, R2 has the highest success (80.0926%), followed by R1 (79.1667%), R3 (76.8519%), and R4 (57.8704%).

Thus, equal total-cycle byte capacity does not imply equal deadline-constrained recovery feasibility when capacity is partitioned and placed differently in logical time.

The deadline effect is larger: P1/P3 success increases from 32.6389% at D12 to 87.8472% at D24 and 100% at D48. These values are logical-model effects. D12, D24, and D48 are not 12, 24, and 48 hours.

### 5.4 State and resource tradeoffs

Although policy does not change the primary success proportion, it changes modeled transition-state exposure.

P0 has zero predecessor exposure by construction, but mean control unavailability is 12.195602 logical slots. P1 has zero control-unavailable slots and mean predecessor exposure of 12.195602 logical slots. P2 retains the P1-like predecessor exposure and adds mean dual-epoch overlap of 3.403935 logical slots.

P3 retains zero control unavailability but increases mean predecessor exposure to 12.497685 logical slots. Relative to P1, P3 uses 0.020833 fewer contacts on average, 433.711806 fewer modeled cryptographic bytes on average, and 0.116898 fewer transition attempts on average.

Terminal-state distributions also differ. P1 and P2 each produce 52 EPOCH_DIVERGENCE and 177 INSUFFICIENT_MATERIAL_TRANSFER outcomes. P3 produces 148 CONTACT_BUDGET_EXHAUSTED and 81 INSUFFICIENT_MATERIAL_TRANSFER outcomes while preserving the same 635 successes.

Rollback invocation and stale-epoch acceptance are zero across the frozen Study 8 population. These are structural invariant checks, not evidence of universal real-world safety.

## 6. Study 8E — External Observation-Opportunity Timing Extension

### 6.1 Frozen research questions

Study 8E retains four prospectively frozen research questions.

**RQ1.** What observation-opportunity duration, inter-opportunity-gap, window-count, and gap-variability structure is observed in prospectively selected public satellite observation traces under a frozen source-selection rule?

**RQ2.** For the frozen Study 8 cryptographic transition-object bundles replayed over externally observed observation-opportunity windows, what minimum hypothetical uniform effective payload rate is required to reach TRUST_RESTORED within each extension-only elapsed-time horizon?

**RQ3.** Under the same externally observed observation-opportunity timing traces and transition-object requirements, do the four frozen Study 8 policy semantics change the minimum-rate feasibility threshold or primarily redistribute transition-state costs and terminal failure classifications?

**RQ4.** Which qualitative Study 8 findings remain directionally consistent, differ, or become non-identifiable when synthetic contact timing is replaced by external contact timing, without pooling the two evidence populations?

### 6.2 Source and population governance

The primary source is the SatNOGS Network observations API [@SatNOGS_API_2026]. The frozen source window is June 2026. The trace unit is norad_cat_id × ground_station.

Population selection is based only on pre-endpoint metadata. The corrected frozen qualification rule requires at least 20 observations for a candidate satellite-station pair, deterministic SHA-256 ranking, a maximum of two selected pairs per NORAD ID, a maximum of two per station, and a hard source-request stopping rule. The corrected population contains 20 selected pairs.

An earlier candidate population was invalidated before timing/recovery endpoints were computed because a stale generated API parameter had been used for satellite filtering. The corrected population uses the verified live norad_cat_id + ground_station filter. That source-history issue is retained as provenance but is not a scientific endpoint.

The frozen source artifact contains 476 observation rows. Only five fields are used for primary timing/recovery analysis: id, start, end, ground_station, and norad_cat_id.

No transmitter baud, observation status, station identity, or TLE field is converted into a cryptographic or throughput quantity.

### 6.3 Observation-opportunity mapping

For each valid observation, start and end define an observation-opportunity timing window. Within one selected trace, overlapping or directly abutting windows are merged for timing arithmetic while retaining source observation IDs for provenance.

In this frozen population, the total raw observation count and total merged-window count are both 476. The exact 20-trace timing summaries—including duration, inter-opportunity-gap, coefficient-of-variation, and burstiness fields—are reproduced without recomputation in Supplementary Table S1 (table-p4-s8e-trace-timing-summary.csv).

These timing windows are proxies for when communication opportunity might exist. They do not prove a physical command link, bidirectional availability, authentication, authorization, usable payload throughput, or mission scheduling availability.

### 6.4 Anchors, horizons, and modeled rate endpoint

Each accepted merged observation-window end time is a candidate compromise anchor. An anchor is eligible only when the source data provide complete coverage through the full 24-hour follow-up horizon. The frozen population contains 454 eligible anchors.

Each anchor is crossed with three cryptographic profiles, four recovery policies, four disruptions, and three elapsed-time horizons: 6 h, 12 h, and 24 h. This yields 454 × 3 × 4 × 4 × 3 = 65,376 canonical extension cases.

The Study 8E endpoint is not fixed link capacity. Instead, the extension defines a **hypothetical uniform effective payload rate**: a modeled constant net payload bit rate available only during accepted observation-opportunity windows. For each case, the canonical analysis solves the minimum integer rate at which the frozen transition reaches TRUST_RESTORED strictly before the horizon.

The rate is a model threshold. It is not inferred from SatNOGS transmitter baud and is not a measured physical link capacity.

### 6.5 Reproducibility controls

Study 8E uses a separately frozen extension implementation and canonical execution protocol. The corrected canonical runner repairs a strict-before-horizon sufficient-bound defect identified after the first canonical package. The first result package was invalidated before scientific freeze and is not used here.

The corrected execution produced 10/10 passing runner tests, two byte-identical scientific execution passes, zero independent case mismatches, and zero repository drift.

The corrected package is formally frozen as S8E-CANON-RESULTS-002-FREEZE-001.

One packaging metadata inconsistency remains documented: CANONICAL_FINDINGS.json correctly identifies Results-002, while the immutable package's RESULTS_HASH_MANIFEST.json retains the stale Results-001 label. The file hashes correspond to the corrected outputs. This is treated as a non-scientific metadata defect and did not trigger re-execution.

## 7. Study 8E Results

### 7.1 Observation-opportunity timing population

The frozen external population contains 20 satellite-station traces, 476 source observations, 476 merged timing windows, and 454 eligible compromise anchors.

The complete per-trace timing descriptors are reported in Supplementary Table S1 directly from the frozen TRACE_TIMING_SUMMARY.csv. The table contains, for each selected trace, the raw and merged window counts, opportunity-duration minimum/median/maximum, inter-opportunity-gap minimum/median/maximum and mean, population gap standard deviation, gap coefficient of variation, and gap burstiness index.

The purpose of RQ1 is descriptive. These timing descriptors characterize the selected public observation-opportunity population only and are not estimates of authenticated command-link availability.

### 7.2 Overall minimum-rate feasibility

Of 65,376 canonical cases, 17,640 have a finite minimum modeled rate threshold and 47,736 are non-finite under the available windows and strict horizon rule.

The exact finite fraction is 17,640/65,376 = 245/908 = 0.269824.

Among finite cases, the minimum modeled threshold is 48 bps, the median is 345 bps, and the maximum is 57,727 bps.

These values are hypothetical uniform effective payload-rate thresholds inside the extension model. They are not SatNOGS measurements.

### 7.3 Horizon dependence

Finite threshold availability increases strongly with the elapsed-time horizon:

- 6 h: 1,152/21,792 = 12/227 = 0.052863;
- 12 h: 4,488/21,792 = 187/908 = 0.205947;
- 24 h: 12,000/21,792 = 125/227 = 0.550661.

Thus, more elapsed time before the recovery boundary increases the fraction of frozen extension cases for which some finite modeled rate can complete the transition.

These percentages must not be compared numerically with Study 8 D12/D24/D48 percentages as though they were the same endpoint. Study 8 deadlines are logical slots under fixed capacity; Study 8E horizons are physical elapsed time under a solved-rate endpoint.

### 7.4 Disruption dependence

Study 8E finite fractions differ by disruption:

- A0: 6,624/16,344 = 0.405286;
- A1: 6,624/16,344 = 0.405286;
- A2: 2,196/16,344 = 0.134361;
- A3: 2,196/16,344 = 0.134361.

The equality of A0/A1 and A2/A3 is a frozen model result. It does not imply that the real-world disruptions represented by those abstractions have equivalent operational severity.

### 7.5 Policy threshold comparison

Each of P0, P1, P2, and P3 has exactly 4,410/16,344 = 245/908 = 0.269824 finite cases.

For the prespecified P3/P1 comparison, there are 16,344 matched cases, of which 4,410 are both finite and 11,934 are both non-finite. P3 has a lower threshold in zero cases and a higher threshold in zero cases. All 4,410 both-finite cases have equal thresholds, so the minimum, median, and maximum P3-minus-P1 threshold differences are all 0 bps.

Thus, P3's pre-commit contact guard does not reduce the minimum modeled rate required relative to P1 when both are feasible, and it does not change finite/non-finite classification in the frozen external timing population.

### 7.6 Cryptographic profile burden

Each profile has the same finite/non-finite classification: 5,880/21,792 = 245/908 = 0.269824.

This differs from Study 8's fixed-capacity profile-success result. Under Study 8E's solved-rate formulation, the existence of a finite threshold is identical across the three profiles in the frozen cases.

However, profile burden ordering is preserved in all 21,792/21,792 matched profile comparisons, with zero ordering violations.

Accordingly, profile differences in Study 8E appear in the required-rate burden rather than in whether a finite threshold exists.

### 7.7 Structural safety fields

Rollback invocation sums are zero at both finite thresholds and non-finite sufficient bounds. Stale-epoch acceptance sums are also zero in both sets.

These are frozen structural checks under the modeled transition semantics, not evidence that real systems cannot require rollback or accept stale state.

## 8. Cross-Study Synthesis

### 8.1 Does contact-aware staging enlarge the feasible set?

The answer is no under both frozen endpoints.

In Study 8, P3 and P1 have identical trusted-recovery success: P3 minus P1 = 0.000000 percentage points, both marginally and in every prespecified stratum.

In Study 8E, P3 and P1 have identical finite/non-finite classification in all 16,344 matched cases, and every one of the 4,410 both-finite comparisons has an identical minimum modeled rate.

The permitted synthesis is structural rather than replicative:

> Across both frozen evidence layers, adding P3's nominal pre-commit capacity guard does not improve the respective feasibility endpoint because the guard does not add communication opportunity or reduce the transition-object bundle.

This statement does not mean that the two studies estimate the same population quantity, and Study 8E is not an external empirical replication of Study 8.

### 8.2 How does cryptographic-object burden appear under different endpoints?

Study 8 fixes modeled contact capacity and asks whether the transition finishes. Under that endpoint, success falls sharply as the frozen object bundle grows, and the success ordering is non-increasing in all 1,152 matched positions.

Study 8E instead solves the rate needed for completion under each external timing case. Under that endpoint, all three profiles have identical finite/non-finite classification, but required-rate burden ordering is preserved in all 21,792 matched comparisons.

The two results are therefore complementary:

> **When capacity is fixed, larger transition bundles can remove cases from the successful set; when rate is solved as the endpoint, larger bundles appear as greater required communication burden even when a finite threshold still exists.**

This distinction is one of the main reasons to report the studies together.

### 8.3 What does more recovery time change?

In Study 8, P1/P3 success rises from 32.6389% at D12 to 87.8472% at D24 and 100% at D48.

In Study 8E, the fraction of cases with a finite minimum-rate threshold rises from 5.2863% at 6 h to 20.5947% at 12 h and 55.0661% at 24 h.

The common qualitative lesson is that a longer recovery horizon expands the feasible set.

The numerical percentages are not directly comparable because Study 8 uses fixed modeled capacity and logical deadlines, Study 8E uses external elapsed-time windows and solves rate, and Study 8 logical slots have no physical duration.

No slot-to-hour conversion or pooled time effect is supported.

### 8.4 What does timing structure contribute?

Study 8 demonstrates that equal 65,536-byte complete-cycle capacity can produce different deadline success when capacity is partitioned and placed differently in logical time.

Study 8E replaces synthetic timing with prospectively governed public observation-opportunity windows. It does not calibrate Study 8's contact regimes to real orbital passes. Instead, it shows that the same cryptographic-transition semantics can be evaluated under an external timing structure and that minimum-rate feasibility varies strongly with horizon and disruption under that structure.

The joint conclusion is limited but useful:

> **Aggregate capacity alone is insufficient to characterize recovery feasibility; when opportunity occurs relative to the compromise anchor and recovery boundary is also part of the system constraint.**

### 8.5 Feasibility and state cost remain separate questions

Study 8 directly shows that policy semantics redistribute predecessor exposure, control unavailability, overlap, transfer use, attempts, and terminal failure labels without changing primary success.

Study 8E likewise shows policy equality on finite-rate feasibility. Where state-cost fields are defined in the frozen extension outputs, they remain secondary to the minimum-rate endpoint.

The paper therefore does not rank P0-P3. Policy choice is a security-state design decision even when terminal feasibility is unchanged.

## 9. Discussion

### 9.1 A guard cannot manufacture recovery opportunity

The exact P3/P1 null in both evidence layers is mechanistically consistent with the frozen design. P3 can avoid entering commit when nominal remaining opportunity is insufficient, but it cannot create another contact, lengthen an observation opportunity, increase modeled rate, shrink the cryptographic bundle, or alter the successor material required for trust restoration.

The guard can therefore change resource consumption, exposure duration, or terminal classification without enlarging the underlying feasible set.

This distinction matters for crypto-agility engineering. A policy may improve discipline around infeasible transitions without improving the number of situations in which recovery is possible.

### 9.2 Fixed-capacity feasibility and required-rate burden are different system questions

The two-study design provides a useful conceptual separation.

Study 8 asks:

> **Given a fixed modeled byte opportunity, can the required transition finish before the logical deadline?**

Study 8E asks:

> **Given the frozen external timing windows, what modeled uniform effective payload rate would be required for the transition to finish before the elapsed-time horizon?**

A cryptographic profile can therefore have lower fixed-capacity success while still sharing the same finite/non-finite classification under a solved-rate endpoint. In the latter case, burden is expressed through the threshold magnitude rather than through binary feasibility.

This is not a statistical paradox. It is a consequence of changing the constrained variable while keeping the transition requirement frozen.

### 9.3 Timing should be represented explicitly in recovery design

The Study 8 equal-capacity regime result demonstrates that total capacity does not fully determine deadline-constrained success. Study 8E adds a separately sourced timing layer without claiming operational realism for command traffic.

Together, the evidence supports treating temporal opportunity structure as a first-class input to recovery analysis. A recovery design that considers only nominal bandwidth or total expected contact volume can miss whether enough usable opportunity occurs after compromise and before the recovery boundary.

### 9.4 Post-quantum object burden is a systems-level transition concern

Prior work already recognizes that PQ authentication and key-management artifacts can place pressure on constrained and non-terrestrial networks [@Eichen_etal_2026; @GSMA_PQ07_2026]. The present results add a different systems perspective: standardized cryptographic objects can shape a post-compromise recovery state transition even when cryptographic computation is assumed instantaneous.

The correct engineering implication is not to prefer the smallest algorithm pair. The studies do not compare security adequacy, implementation assurance, side-channel resistance, or mission threat models. Instead, they show that cryptographic selection and recovery architecture should be co-designed with transition-object structure, communication opportunity, and recovery requirements.

### 9.5 Policy semantics matter even without a winner

The absence of a primary success difference should not be interpreted as policy irrelevance.

P0, P1, P2, and P3 expose different states during transition. Hard cutover minimizes predecessor exposure but creates control unavailability. Staged cutover preserves availability while retaining predecessor acceptance. Hybrid overlap introduces a period in which both epochs may be accepted. Contact-aware staging changes resource use and failure classification while extending predecessor exposure slightly in Study 8.

These are security and availability tradeoffs, not an overall ranking. The appropriate policy depends on requirements that lie outside the frozen experiments, including mission continuity, revocation urgency, command authority, implementation architecture, and threat assumptions.

### 9.6 Implications for space-system cybersecurity engineering

Within the declared abstraction boundary, the combined evidence suggests five design practices.

First, cryptographic migration planning should account for the byte structure of the transition itself rather than only steady-state algorithm selection.

Second, recovery analyses should represent when communication opportunity becomes available, not only aggregate capacity.

Third, recovery horizons should be explicit because feasibility can change strongly with available time.

Fourth, transition policies should be evaluated with intermediate security-state and availability endpoints in addition to terminal success.

Fifth, external timing evidence should be incorporated without silently promoting source metadata into stronger operational semantics than the source supports.

These are modeling and design implications. They are not claims of compliance with IEEE 3536, CCSDS, NIST deployment guidance, or any specific spacecraft mission.

## 10. Limitations and Threats to Validity

### 10.1 Study 8 uses logical rather than physical time

Study 8 slots are ordering indices only. They cannot be converted into seconds, minutes, pass durations, orbital periods, or link latency. The D12/D24/D48 findings are therefore logical-model results only.

### 10.2 Study 8 contact capacity is synthetic

The fixed byte budgets exclude RF throughput, propagation, fading, coding, antenna behavior, scheduling contention, link acquisition, BER, and ground-station processing.

### 10.3 Study 8E uses observation-opportunity timing, not command-contact evidence

SatNOGS observations do not establish operational command availability, bidirectionality, authentication, authorization, payload throughput, or mission scheduling permission. The source provides external timing structure only.

### 10.4 The Study 8E modeled rate is not measured throughput

The solved hypothetical_uniform_effective_payload_rate_bps is an extension-model threshold. It is not SatNOGS transmitter baud, measured link capacity, or spacecraft TT&C throughput.

### 10.5 Cryptographic accounting excludes protocol overhead

Both studies count the frozen standardized cryptographic-object bundle. They exclude certificates, packet headers, CCSDS framing, error correction, retransmission metadata, and implementation-specific encoding.

### 10.6 No onboard cryptographic performance is measured

The studies do not measure ML-KEM/ML-DSA CPU time, accelerator performance, memory, power, energy, thermal behavior, or side channels.

### 10.7 The adversary is restricted

The disruption schedules are deterministic and nonadaptive. They exclude key recovery, signature forgery, KEM break, cryptanalytic quantum attack, fault injection, and adaptive attack scheduling.

### 10.8 Directionality and feedback are abstracted

The model does not separate uplink and downlink capacity or represent full operational feedback loops, acknowledgments, and duplex scheduling.

### 10.9 Finite-population results are bounded to the frozen populations

Study 8 describes its complete 3,456-position deterministic population. Study 8E describes its frozen selected public observation population and 65,376 derived canonical cases. Neither study supports sampling-based generalization to all missions, all ground stations, all contact processes, or all adversaries.

### 10.10 Study 8E source-selection scope is intentionally narrow

The SatNOGS population is bounded by a frozen source window, qualification threshold, deterministic ranking, per-entity caps, request stopping rule, and first-page acquisition rule. Additional pages or alternative source periods were not added after endpoint inspection.

### 10.11 Results-002 contains a documented metadata-label defect

The corrected immutable artifact contains a stale results_id label in RESULTS_HASH_MANIFEST.json. The exact corrected hashes are externally bound by the independent audit and formal freeze records. This defect affects package metadata rather than scientific rows or results.

### 10.12 Study 8E is not an external replication

The extension reuses frozen Study 8 transition semantics under a new timing population. It does not independently reproduce the entire Study 8 experiment with separate hardware, laboratory infrastructure, investigators, or operational spacecraft data.

Future work should add those stronger evidence layers prospectively rather than retroactively altering either frozen study.

## 11. Reproducibility and Data Availability

The research repository preserves the protocols, source bindings, frozen results, independent checks, and publication governance for both studies.

Study 8 is identified as S8-PQC-ICR-001. Its canonical finite population contains 3,456 positions, and its independently implemented same-repository reference model reproduced all canonical rows exactly.

Study 8E is identified as S8E-ECTV-001. The corrected external population is S8E-SATNOGS-POP-002, the frozen trace is S8E-SATNOGS-TRACE-002, and the corrected formal result freeze is S8E-CANON-RESULTS-002-FREEZE-001. The corrected execution produced two byte-identical passes and zero independent case mismatches.

The rebuilt manuscript directory contains a direct copy of the frozen 20-row Study 8E timing summary and a frozen threshold-summary table for reader-facing traceability. Detailed hashes, artifact IDs, invalidation history, and execution lineage remain in the repository governance records rather than the main results narrative.

## 12. Conclusion

This paper evaluated trusted post-compromise post-quantum recovery through two separately frozen but complementary evidence layers.

Study 8 showed that a contact-aware pre-commit guard did not increase modeled trusted-recovery success. All four policies succeeded in exactly 635/864 positions, and P3 minus P1 was 0.000000 percentage points in every prespecified stratum. Fixed-capacity feasibility instead changed substantially with cryptographic-object burden, contact timing, and logical deadline.

Study 8E then replaced the synthetic timing schedule with a prospectively governed public observation-opportunity population while preserving the transition requirements. Only 26.9824% of its frozen cases had a finite minimum modeled rate threshold, and feasibility expanded strongly with longer elapsed-time horizons. P3 again showed no feasibility advantage over P1: every both-finite comparison had exactly the same required rate. Cryptographic profiles had identical finite/non-finite classification, but the required-rate burden ordering was preserved in every matched comparison.

The combined result is not that one policy or one cryptographic profile is universally preferable. It is that post-compromise recovery should distinguish **fixed-capacity feasibility**, **required communication burden**, and **transition-state cost**. A guard cannot manufacture capacity, a larger transition bundle must still traverse the available opportunities, and aggregate capacity alone does not capture when opportunity arrives relative to compromise and recovery deadlines.

The external SatNOGS layer strengthens the timing relevance of this systems argument without converting public observation data into operational command-contact or throughput evidence. Operational conclusions will require a future evidence layer with mission-specific contact schedules, directional links, protocol framing, onboard cryptographic execution, RF behavior, and independent implementation or flight validation.

## Declarations

### Funding

No external funding was received for this study.

### Competing interests

The author declares no competing interests.

### Author contributions

Aman Kumar Singh is the sole author and was responsible for conceptualization, methodology, software, validation, formal analysis, investigation, data curation, writing, visualization planning, and research governance.

### Ethics

The studies use deterministic modeled data and public technical data sources. No human participants, animal subjects, or personal data were involved.

### Artificial-intelligence assistance

AI-assisted tools were used as research-support tools for code review, documentation, literature-search assistance, manuscript editing, and consistency checking. Scientific protocols, execution authorizations, frozen evidence, result interpretation, and final authorship responsibility remain with the author.
