# Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems

**Aman Kumar Singh, MS, DSc**  
Independent Researcher, The Woodlands, Texas, United States  
ORCID: https://orcid.org/0009-0008-9752-3743

## Abstract

Long-lived space systems must be able to change cryptographic state without assuming continuously available connectivity. Post-quantum migration intensifies this systems problem because standardized public keys, ciphertexts, and signatures can impose materially different byte burdens even before implementation, framing, or certificate overhead is considered. This paper evaluates trusted post-compromise cryptographic transition as a deterministic finite systems problem rather than as an onboard performance benchmark. A frozen `3 × 4 × 4 × 4 × 6 × 3` factorial model crosses three exact ML-KEM/ML-DSA algorithm-pair profiles, four transition policies, four intermittent-contact regimes with equal full-cycle nominal byte capacity, four bounded non-cryptanalytic disruptions, six compromise phase offsets, and three logical recovery deadlines, yielding 3,456 modeled positions. The prespecified primary endpoint is trusted recovery before the deadline; the complete finite population is summarized by exact counts and proportions without sampling p-values or confidence intervals. A separately implemented same-repository reference model reproduced all 3,456 canonical rows exactly, and a separate same-repository statistical implementation reproduced the frozen machine-readable findings byte-for-byte.

All four transition policies achieved the same primary success proportion, `635/864` (`73.4954%`), so the prespecified contact-aware staged-versus-staged risk difference was exactly `0.000000` percentage points in the marginal population and every prespecified regime, profile, disruption, and deadline stratum. In contrast, success varied sharply with standardized cryptographic-object burden: `93.7500%` for ML-KEM-512/ML-DSA-44, `64.9306%` for ML-KEM-768/ML-DSA-65, and `61.8056%` for ML-KEM-1024/ML-DSA-87. Across all 1,152 matched non-profile positions, success was never higher for a larger frozen object bundle. Deadline and contact timing also conditioned feasibility despite equal complete-cycle contact capacity. Policy choice instead redistributed modeled availability, predecessor exposure, overlap, transfer burden, transition attempts, and failure classification. The results indicate that, in this frozen logical-contact model, contact-aware guarding does not create recovery capacity; standardized cryptographic-object size, logical contact structure, and deadline account for the observed feasibility differences, while transition policy primarily governs security-state and availability tradeoffs.

**Keywords:** cryptographic agility; post-quantum cryptography; ML-KEM; ML-DSA; satellite cybersecurity; space systems; post-compromise recovery; intermittent connectivity; systems modeling

---

## 1. Introduction

Space systems combine long service lives, constrained opportunities for maintenance, geographically and temporally intermittent communications, and increasingly explicit cybersecurity requirements. Those properties make cryptographic transition a systems problem rather than a simple algorithm-replacement task. NIST defines crypto agility as the capability to replace or adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving security and ongoing operations [@NIST_CSWP39_2026]. In parallel, NIST FIPS 203 and FIPS 204 standardize ML-KEM and ML-DSA, respectively [@NIST_FIPS203_2024; @NIST_FIPS204_2024], while SP 800-227 emphasizes that safe KEM use depends on surrounding protocol and system conditions rather than on algorithm selection alone [@NIST_SP800227_2025].

The space context makes these transition questions particularly consequential. Recent institutional and academic work already addresses post-quantum cryptography (PQC) for non-terrestrial networks, hybrid migration, protocol adaptation, space-system crypto agility, secure software update, and hardware/software implementation [@GSMA_PQ07_2026; @Mahn_Muller_Zielinski_2025; @Wildfeuer_etal_2025; @Robles_etal_2025; @Kim_2026_PQCSpace]. The 2026 IEEE Standard for Space System Cybersecurity Design further reflects the growing emphasis on cybersecurity controls spanning the ground, space-vehicle, link, and integration layers [@IEEE3536_2026]. This body of work means that “PQC for satellites,” “crypto agility for space,” “hybrid migration,” or “PQC bandwidth overhead” are not defensible novelty claims by themselves.

A narrower systems question remains important after compromise: if predecessor credentials or cryptographic state can no longer be trusted, can a system establish and confirm a successor epoch within the contact opportunities that remain before a recovery deadline? The answer depends not only on which algorithms are selected, but also on how much cryptographic material must move, when contact capacity becomes available, which transition state is accepted at each point, and how bounded disruption interacts with those constraints. Larger post-quantum objects can matter even if cryptographic computation is assumed instantaneous, because finite contact budgets can determine whether required transition material reaches the modeled protocol state machine in time. Eichen et al. likewise identify larger PQ authentication artifacts and intermittent or bandwidth-constrained non-terrestrial connectivity as practical key-management concerns [@Eichen_etal_2026].

This study isolates that systems interaction using a deterministic finite logical-contact model. It asks:

> **How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?**

The contribution is deliberately narrower than prior PQC-for-space work. The study jointly evaluates (i) exact NIST-standardized cryptographic-object byte burdens, (ii) intermittent contact opportunities with controlled total-cycle capacity but different temporal distributions, (iii) explicit logical recovery deadlines, (iv) four transition policies with different predecessor/successor acceptance semantics, (v) epoch-safety invariants, and (vi) bounded non-cryptanalytic disruption. It then separates two questions that are often conflated: whether a transition policy changes **recovery feasibility**, and whether it changes the **security-state and availability costs** incurred while pursuing the same feasibility objective.

The study produces a negative primary policy result and preserves it as such. The contact-aware policy does not improve trusted-recovery success relative to ordinary staged cutover in the frozen population. The strongest feasibility differences instead align with cryptographic-object burden, contact timing, and deadline. Policy choice remains relevant because it redistributes logical control unavailability, predecessor exposure, dual-epoch overlap, modeled transfer use, transition attempts, and terminal failure classification.

## 2. Related Work and Standards Context

### 2.1 Post-quantum cryptography and migration in space systems

Kim's 2026 systematic survey synthesizes space-oriented PQC research across algorithms, hardware implementation, software integration, protocol adaptation, hybrid migration, crypto agility, and CCSDS-related gaps [@Kim_2026_PQCSpace]. Ghosh and Nath evaluate lattice-based PQC in satellite-communication settings and discuss implementation and migration considerations [@Ghosh_Nath_2026]. GSMA PQ.07 identifies high latency, constrained processing, long satellite lifecycles, interoperability, PKI, and phased or hybrid migration as relevant PQC concerns for non-terrestrial networks [@GSMA_PQ07_2026]. Eichen et al. focus specifically on the bandwidth, memory, computation, and energy pressure created by post-quantum authentication artifacts in constrained or non-terrestrial networks and motivate alternative key-management architectures [@Eichen_etal_2026].

These works establish that PQC deployment pressure and cryptographic-object growth in satellite or NTN environments are active research topics. The present study does not claim that larger post-quantum objects are a newly discovered concern. Instead, it asks how standardized object sizes interact with a frozen post-compromise state transition and finite logical-contact schedule.

### 2.2 Crypto agility and secure transition

NIST's crypto-agility guidance treats cryptographic replacement as a cross-layer operational capability involving mechanisms, dependencies, and transition planning [@NIST_CSWP39_2026]. Space-focused work by Mähn, Müller, and Zielinski develops crypto-agility terminology and addresses remote update, failure, attack, and fallback concerns [@Mahn_Muller_Zielinski_2025]. ESA work has also examined quantum-safe satellite data-link architecture and high-assurance PQC for software-defined payloads [@Wildfeuer_etal_2025; @Robles_etal_2025], while the ACES activity demonstrates continuing institutional interest in advanced and post-quantum security-by-design for satellite communications [@ESA_ACES_2026].

The CCSDS data-link security architecture is relevant because its algorithm-independent orientation supports asking how cryptographic algorithms may change without assuming that a specific PQC algorithm pair is already an operational CCSDS-approved suite [@CCSDS_SDLS]. The present study therefore uses CCSDS only as architectural context. It does not claim ML-KEM or ML-DSA conformance to an operational CCSDS PQC profile.

### 2.3 Satellite cybersecurity systems context

Satellite cybersecurity literature has long emphasized the dependence of space missions on trustworthy communications and software-controlled infrastructure [@HousenCouriel_2016; @Falco_2019]. Security mechanisms for federated satellite systems have also been evaluated experimentally at the protocol and platform level [@vonMaurich_Golkar_2018]. The present work complements, rather than replaces, such physical or implementation-oriented evidence. It deliberately removes processor, RF, orbital, energy, and framing effects to isolate a finite systems question: whether standardized transition-object bytes can traverse a particular logical contact schedule before a deadline while the protocol preserves frozen epoch-state rules.

## 3. Methods

### 3.1 Study design and finite population

Experiment `S8-PQC-ICR-001` is a deterministic finite modeled-contact crypto-agility recovery study. The frozen factorial population crosses:

- 3 cryptographic profiles;
- 4 recovery policies;
- 4 contact regimes;
- 4 disruption schedules;
- 6 compromise phase offsets; and
- 3 logical recovery deadlines.

The complete Cartesian population therefore contains `3 × 4 × 4 × 4 × 6 × 3 = 3,456` observations. Every factor position occurs exactly once. The canonical observations were independently recomputed by a separately implemented same-repository reference model; all 3,456 rows matched exactly, with zero mismatches. The canonical dataset SHA-256 is `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`.

Because the object of inference is the entire frozen deterministic population rather than a random sample from a superpopulation, the analysis reports exact finite-population counts, proportions, differences, medians, and arithmetic means. Sampling p-values, sampling confidence intervals, bootstrap inference, and permutation inference were prespecified as unsupported.

### 3.2 Cryptographic-object profiles

FIPS 203 defines ML-KEM public-key and ciphertext sizes, and FIPS 204 defines ML-DSA public-key and signature sizes [@NIST_FIPS203_2024; @NIST_FIPS204_2024]. Three exact algorithm-pair identifiers were frozen:

- `PROFILE_512_44`: ML-KEM-512 + ML-DSA-44;
- `PROFILE_768_65`: ML-KEM-768 + ML-DSA-65; and
- `PROFILE_1024_87`: ML-KEM-1024 + ML-DSA-87.

The identifiers name exact algorithm pairs only; they are not asserted to be matched NIST security-category profiles.

Each transition uses seven modeled cryptographic objects in fixed priority order: a recovery-authority assertion signature, successor KEM encapsulation key, successor signature-verification key, KEM ciphertext, transition-proof signature, new-epoch commit signature, and post-commit confirmation signature. Private keys are never transmitted. The resulting base transition-object budgets are 12,560 bytes, 17,460 bytes, and 24,236 bytes for the three profiles, respectively. These totals include standardized cryptographic-object bytes only. They exclude certificates, transport headers, CCSDS framing, coding overhead, implementation metadata, and private keys.

### 3.3 Recovery policies

The four policies use the same required object bundle and common deterministic byte scheduler. Their treatment difference is the predecessor/successor acceptance state and, for P3, a pre-commit contact-budget guard.

**P0 — Hard cutover.** Predecessor control acceptance is revoked at recovery start. Successor acceptance begins at new-epoch commit, and trust restoration requires post-commit confirmation.

**P1 — Staged cutover.** Predecessor acceptance remains during staging. At commit, predecessor revocation and successor acceptance occur atomically. Trust restoration again requires confirmation.

**P2 — Hybrid overlap.** Predecessor acceptance remains during staging; successor acceptance begins after the transition proof is accepted; predecessor revocation occurs at commit. A design amendment added `dual_epoch_overlap_slots` so this pre-commit overlap is explicitly observable.

**P3 — Contact-aware staged.** P3 uses P1's staged semantics plus a deterministic pre-commit guard. The guard may inspect only the frozen contact schedule, phase offset, deadline, selected profile object sizes, bytes already delivered, and current protocol state. It may not inspect future disruptions or outcomes. Commit is permitted only when nominal scheduled capacity strictly before the deadline is sufficient for the remaining new-epoch commit and post-commit confirmation bytes.

### 3.4 Logical contact model

Logical time is represented by integer slots `0..47`. A slot is an ordering unit only and has no physical duration. Every contact is one logical slot wide and supplies a synthetic upper bound on cryptographic-object bytes that can be transferred in that opportunity.

All four regimes contain exactly 65,536 nominal bytes over the complete 48-slot cycle, controlling total-cycle capacity while changing its temporal distribution:

- `R1_FREQUENT_SMALL`: 16 contacts × 4,096 bytes;
- `R2_PERIODIC_MEDIUM`: 8 contacts × 8,192 bytes;
- `R3_SPARSE_LARGE`: 4 contacts × 16,384 bytes;
- `R4_CLUSTERED_MEDIUM`: 8 contacts × 8,192 bytes arranged in four two-contact clusters.

Six deterministic compromise offsets (`0..5`) shift the post-compromise contact schedule. Three deadlines are used: D12, D24, and D48. Recovery is on time only if `TRUST_RESTORED` is reached at a slot strictly less than the selected deadline.

The transmission scheduler repeatedly moves bytes from the highest-priority ready incomplete object during a contact. Partial bytes persist unless a disruption explicitly discards them. Newly unlocked objects may use remaining capacity in the same contact. A pre-runtime amendment clarified that for A2, the contact in which the transition proof first becomes ready is itself the single withheld opportunity; proof bytes cannot use that contact's remaining capacity.

### 3.5 Bounded disruption model

Four disruption schedules are crossed with every other factor:

- `A0_NONE`: no transport disruption;
- `A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT`: the first allocation to the earliest highest-priority object tied for largest size is lost once, consuming its contact capacity;
- `A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT`: the first proof-ready contact is withheld for the proof;
- `A3_STALE_EPOCH_REPLAY_AT_COMMIT`: a previously valid stale commit is presented at the first commit opportunity and must be rejected by the monotonic epoch check, consuming that logical opportunity without adding standardized cryptographic-object bytes.

The adversary cannot forge ML-DSA signatures, recover private keys, break ML-KEM, perform quantum cryptanalysis, adapt its disruption schedule to observed outcomes, or modify the frozen contact/deadline design.

### 3.6 Endpoints and statistical plan

The primary endpoint is binary modeled trusted recovery before the selected deadline without stale or compromised epoch acceptance. The primary estimand is the exact marginal success proportion for each policy across its 864 equally weighted frozen factor positions. The prespecified primary contrast is P3 minus P1 because P3 adds contact awareness to P1's staged-cutover semantics.

Prespecified stratified P3-minus-P1 contrasts were required by contact regime, cryptographic profile, disruption schedule, and deadline. Secondary summaries include recovery completion slot among successes, contacts consumed, modeled cryptographic bytes transferred, transition attempts, legacy exposure slots, control-unavailable slots, P2 dual-epoch overlap slots, rollback invocation, stale-epoch acceptance, and terminal state.

The analysis plan was locked before scientific outcome values were inspected. Primary and independent statistical implementations then produced byte-identical machine-readable findings with SHA-256 `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`.

## 4. Results

### 4.1 Primary policy result: exact null contrast

All four transition policies achieved modeled trusted recovery in exactly `635/864` positions (`73.4954%`). Consequently, all six unordered pairwise policy success differences were exactly zero. The prespecified P3-minus-P1 primary risk difference was `0/1`, or `0.000000` percentage points.

The null P3-minus-P1 result also held in **every prespecified stratum**. By deadline, P1 and P3 each succeeded in `94/288` (`32.6389%`) positions at D12, `253/288` (`87.8472%`) at D24, and `288/288` (`100%`) at D48. By contact regime, both policies achieved `171/216` (`79.1667%`) in R1, `173/216` (`80.0926%`) in R2, `166/216` (`76.8519%`) in R3, and `125/216` (`57.8704%`) in R4. By disruption, both achieved `163/216` (`75.4630%`) under A0, `160/216` (`74.0741%`) under A1, and `156/216` (`72.2222%`) under each of A2 and A3. By profile, P1 and P3 were also identical within each exact algorithm pair.

These results do not support a claim that the contact-aware guard increases the probability of modeled trusted recovery in the frozen population.

### 4.2 Cryptographic-object burden

Success varied substantially across the three standardized-object profiles. `PROFILE_512_44` succeeded in `1080/1152` positions (`93.7500%`), `PROFILE_768_65` in `748/1152` (`64.9306%`), and `PROFILE_1024_87` in `712/1152` (`61.8056%`). Relative to `PROFILE_512_44`, the exact finite-population success difference was `-28.819444` percentage points for `PROFILE_768_65` and `-31.944444` percentage points for `PROFILE_1024_87`. The `PROFILE_1024_87` minus `PROFILE_768_65` difference was `-3.125000` percentage points.

The matched-profile check strengthens the finite-model interpretation without introducing sampling inference. Across all 1,152 identical policy/regime/disruption/phase/deadline positions, success was non-increasing as the frozen standardized object budget increased. The exact outcome patterns were:

- `111`: 712 positions — all three profiles succeed;
- `110`: 36 positions — the two smaller profiles succeed;
- `100`: 332 positions — only `PROFILE_512_44` succeeds;
- `000`: 72 positions — none succeeds.

No matched position showed a larger profile succeeding when a smaller profile failed. This is evidence about the frozen byte-budget/contact interaction, not measured ML-KEM/ML-DSA execution speed or spacecraft hardware performance.

### 4.3 Contact timing and recovery horizon

The contact-regime result is notable because all four regimes contain the same 65,536 nominal bytes over a complete 48-slot cycle. For P1 and P3, R2 periodic-medium had the highest success (`80.0926%`), followed by R1 frequent-small (`79.1667%`), R3 sparse-large (`76.8519%`), and R4 clustered-medium (`57.8704%`). Thus equal total-cycle capacity did not imply equal deadline-constrained feasibility; how that capacity was partitioned among contacts and placed across logical slots mattered in the frozen model.

The deadline gradient was larger: P1/P3 success increased from `32.6389%` at D12 to `87.8472%` at D24 and `100%` at D48. These quantities are logical deadline effects only. They cannot be converted into real time because a slot has no physical duration.

### 4.4 Policy-state and resource tradeoffs

Although policy did not change the primary success proportion, it changed modeled state exposure and resource use.

P0 hard cutover had zero predecessor/legacy exposure by construction, but mean logical control unavailability was `10537/864 = 12.195602` slots. P1 staged cutover had zero control-unavailable slots and the complementary mean predecessor exposure of `10537/864 = 12.195602` logical slots. P2 hybrid overlap preserved the P1-like predecessor exposure and added mean dual-epoch overlap of `2941/864 = 3.403935` logical slots (median 3, maximum 15), again without any primary success advantage.

P3 contact-aware staged cutover retained the zero-control-unavailability property of P1 but increased mean predecessor exposure to `5399/432 = 12.497685` logical slots. Relative to P1, P3 used `1/48 = 0.020833` fewer contacts on average, `124909/288 = 433.711806` fewer modeled cryptographic bytes on average, and `101/864 = 0.116898` fewer transition attempts on average. These are deterministic finite-population differences in the model, not measurements of network traffic, physical bandwidth, or operator workload.

Terminal-state distributions also changed. P1 and P2 each produced 52 `EPOCH_DIVERGENCE` and 177 `INSUFFICIENT_MATERIAL_TRANSFER` outcomes, whereas P3 produced 148 `CONTACT_BUDGET_EXHAUSTED` and 81 `INSUFFICIENT_MATERIAL_TRANSFER` outcomes, with the same 635 successes. The frozen analysis does not perform a post-hoc row-level transition mapping between those failure labels, so only the aggregate distributions are reported.

Rollback invocation and stale-epoch acceptance were zero throughout the frozen factor lattice. Those structural zeros are safety/invariant checks under the modeled schedules; they are not treatment-effect evidence.

## 5. Discussion

### 5.1 Contact awareness did not increase modeled recovery feasibility

The central negative result is exact: P3's contact-aware pre-commit guard did not improve trusted-recovery success over P1 staged cutover, either marginally or in any prespecified stratum. This result should not be reframed as a hidden policy advantage. P3 can decide not to commit when nominal remaining contact capacity is insufficient for commit-plus-confirmation, but it cannot create new contact opportunities or reduce the required successor cryptographic-object bundle. In the frozen model, the guard therefore changes when resources are consumed and how failures are classified rather than enlarging the feasible set of successful positions.

The broader policy equivalence is also consistent with the design. P0, P1, and P2 use the same required object bundle and common byte scheduler; their primary treatment differences concern predecessor/successor acceptance state. P2's amendment-added overlap endpoint makes that state difference observable, but no policy-specific byte advantage is introduced. The null primary result is consequently a model-specific finding about these four mechanisms, not evidence that cryptographic transition policy is generally irrelevant.

### 5.2 Standardized object size was a dominant feasibility constraint

The profile result is the strongest quantitative pattern in the study. Moving from the 12,560-byte base transition bundle to 17,460 and 24,236 bytes corresponded to large reductions in the finite-population success proportion. More importantly, all 1,152 matched non-profile positions followed a non-increasing success ordering as the object budget increased.

The correct interpretation is narrow but operationally useful for design reasoning: if a recovery protocol must move a fixed set of cryptographic objects through finite intermittent opportunities, larger standardized objects can eliminate deadline-feasible positions even when cryptographic execution itself is not modeled. This complements prior NTN/PQC work that identifies bandwidth and handshake-size pressure [@Eichen_etal_2026; @GSMA_PQ07_2026], while avoiding claims about CPU time, energy, certificate size, or real radio performance that this study did not measure.

The result also argues against treating “stronger profile” selection as a purely local cryptographic choice in a constrained recovery architecture. System designers may need to co-design transition object structure, contact scheduling, authentication architecture, and recovery deadlines. That statement is a design implication, not a recommendation to select a weaker cryptographic algorithm: the study does not compare security strength, threat adequacy, or implementation security among the three algorithm pairs.

### 5.3 Equal total capacity is not equal deadline-constrained opportunity

The four contact regimes were deliberately normalized to the same 65,536 nominal bytes over the full 48-slot cycle. Their different success proportions therefore show that equal complete-cycle total capacity does not erase differences created by how capacity is partitioned among contacts and placed across logical slots. R4's clustered structure was notably less favorable than the other regimes in the prespecified P1/P3 comparison, while R1 and R2 performed similarly despite different contact granularity.

This result supports treating contact timing as an explicit input to cryptographic recovery planning rather than relying only on total expected capacity. The finding is particularly relevant to intermittent systems engineering, but the model stops short of orbital realism: contact slots are synthetic, one-slot windows; there is no line-of-sight geometry, propagation, scheduling contention, fading, coding, or physical contact duration.

### 5.4 Policy choice remains a security-state decision

The null primary outcome does not make the policies equivalent. P0 minimizes modeled predecessor exposure by immediately revoking the predecessor, but pays in modeled control unavailability. P1 preserves availability while accepting predecessor state through staging. P2 adds bounded dual-epoch overlap. P3 retains P1's availability semantics while using slightly fewer modeled contacts, bytes, and attempts at the cost of somewhat longer predecessor exposure and a different failure classification profile.

This separation between **feasibility** and **state cost** is the main policy-design implication. A recovery policy can be valuable because of the state it exposes or avoids even when it does not change the final fraction of successful positions. Crypto-agility mechanisms should therefore be evaluated with both terminal success and transition-state endpoints. NIST's crypto-agility framing similarly emphasizes preserving security and ongoing operations while cryptography changes [@NIST_CSWP39_2026].

### 5.5 Implications for space-system cybersecurity engineering

The study suggests four bounded engineering implications.

First, cryptographic migration planning should include the byte structure of the recovery transition itself, not only steady-state algorithm selection. Second, deadline-sensitive recovery should model the temporal availability of contact capacity rather than only aggregate capacity. Third, policy evaluation should include intermediate acceptance-state metrics such as predecessor exposure, control unavailability, and overlap. Fourth, contact-aware guards should be evaluated for what they actually control: avoiding or reclassifying infeasible commitments may improve resource discipline, but does not necessarily increase the feasible success set.

These implications are consistent with current systems-oriented space cybersecurity activity, including IEEE 3536-2026 and ongoing work on crypto agility and PQC transition [@IEEE3536_2026; @Mahn_Muller_Zielinski_2025; @Kim_2026_PQCSpace]. They should not be interpreted as evidence that the modeled protocol satisfies any particular mission, regulator, CCSDS profile, or hardware platform.

## 6. Limitations and Threats to Validity

The study intentionally isolates one part of a larger engineering problem. Its main limitations are therefore structural rather than incidental.

**Logical rather than physical time.** Slots are ordering indices with no conversion to seconds, milliseconds, orbital periods, propagation time, or real contact duration. Recovery completion and exposure quantities are logical-state summaries only.

**Synthetic contact capacity.** Contact capacities are modeled cryptographic-byte budgets. The model excludes RF throughput, link margin, BER, packet loss beyond the frozen disruptions, modulation, coding, antenna effects, contention, ground-station processing, and orbital geometry.

**Cryptographic-object-only accounting.** Byte budgets use standardized ML-KEM/ML-DSA objects from FIPS 203/204. They exclude certificate chains, transport headers, CCSDS framing, protocol metadata, coding overhead, and implementation-specific encodings. The four logical signature objects are an experimental transition abstraction, not a NIST- or CCSDS-prescribed transition protocol.

**No cryptographic execution benchmarking.** ML-KEM/ML-DSA execution latency, CPU utilization, memory use, accelerator performance, power, energy, thermal behavior, and side-channel behavior are not measured. The profile result must not be reported as algorithm-speed evidence.

**Restricted adversary.** The disruption model is fixed, deterministic, nonadaptive, and non-cryptanalytic. It excludes key recovery, signature forgery, KEM break, quantum cryptanalysis, side channels, fault injection, and adaptive attack scheduling.

**Shared abstract contact budget.** Uplink and downlink are not separated. Directional scheduling, acknowledgments, duplex constraints, and real protocol feedback loops are absent.

**Policy structure.** All policies use the same required object bundle and common scheduler. This intentionally isolates acceptance/revocation semantics but may suppress policy differences that would arise if real transition designs used different messages, retransmission behavior, certificate structures, or fallback mechanisms.

**Structural zeros.** `stale_epoch_acceptance` and `rollback_invoked` are zero under the frozen lattice. These are invariant checks under the modeled schedules, not evidence that real systems cannot accept stale state or require rollback.

**Finite-population scope.** The 3,456 positions are the entire frozen deterministic study population. Exact contrasts describe that population only. The study does not support sampling-based generalization to arbitrary missions, constellations, contact processes, adversaries, or implementation platforms.

**Independent reproduction boundary.** The primary and reference implementations were separately written and reproduced all rows exactly, but both reside in the same repository and were not an external laboratory or independent human replication.

Future work should therefore add physical contact traces, implementation measurements, protocol framing/certificates, directional links, richer recovery mechanisms, and external replication **as new studies**, rather than altering the frozen Study-8 record.

## 7. Conclusion

This study evaluated post-compromise cryptographic transition as a finite systems problem under intermittent logical contact. Across 3,456 frozen factorial positions, the four tested recovery policies achieved exactly the same primary modeled trusted-recovery proportion (`635/864`, `73.4954%`), and the prespecified contact-aware staged-minus-staged difference was zero in every prespecified stratum. The contact-aware guard therefore did not improve primary recovery feasibility in this model.

Feasibility instead varied strongly with standardized cryptographic-object burden, contact timing, and deadline. The smallest frozen ML-KEM/ML-DSA transition bundle succeeded in `93.7500%` of positions, compared with `64.9306%` and `61.8056%` for the larger bundles, and success was non-increasing with object budget in all matched positions. Equal full-cycle capacity also produced different success under different temporal contact distributions, while longer logical deadlines expanded the feasible set.

Policy choice nevertheless mattered for the path to the terminal state: hard cutover exchanged predecessor exposure for control unavailability; staged cutover preserved availability while retaining predecessor acceptance; hybrid overlap added dual-epoch exposure; and contact-aware staging reduced modeled resource use and changed failure classification while slightly extending predecessor exposure. The main systems lesson is therefore not that one transition policy “wins,” but that cryptographic recovery should separate **whether recovery is feasible** from **what security-state and availability costs are incurred while attempting it**.

Within its strict abstraction boundary, the study provides a reproducible basis for that distinction. Extending the result to real spacecraft will require a separate evidence layer incorporating physical contact schedules, protocol framing, onboard cryptographic execution, RF behavior, and mission-specific security requirements.

## Data, Code, and Reproducibility Statement

The complete frozen Study-8 modeled population contains 3,456 canonical observations. The canonical observations SHA-256 is `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`. Primary and independently reproduced statistical findings share SHA-256 `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`. The interpretation audit SHA-256 is `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`.

The technical-close science was merged at commit `63106778559c3127a7d6e8765d52939b73a3f35b`. Publication development consumes those frozen artifacts read-only. Scientific re-execution is not part of manuscript preparation.

## Declarations

### Funding

This research was conducted independently and received no external funding.

### Competing interests

The author declares no competing financial or non-financial interests.

### Author contributions

**Aman Kumar Singh:** Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing – original draft; Writing – review & editing; Visualization; Project administration.

### Ethics

The reported Study-8 experiment is a deterministic software/modeling study and does not involve human participants, identifiable private information, animals, live spacecraft operations, unauthorized access, or radio-frequency experimentation.

### Artificial-intelligence assistance

Generative-AI language assistance was used during manuscript development and publication-package review. The author retains responsibility for review and final approval. No new Study-8 scientific execution was authorized or performed in this publication phase, and the frozen scientific results, evidence identities, and claim boundaries were not altered. Any journal-specific disclosure will be aligned to the selected publisher's current policy at the separate submission-package gate.
