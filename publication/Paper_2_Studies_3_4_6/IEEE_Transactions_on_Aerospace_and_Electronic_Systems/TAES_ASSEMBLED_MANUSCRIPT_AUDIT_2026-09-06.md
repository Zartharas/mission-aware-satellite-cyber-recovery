# TAES Paper 2 Assembled Manuscript Audit - 2026-09-06

**Target:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Paper:** Studies 3 + 4 + 6 only  
**Audit object:** first locally assembled development draft  
**First assembled SHA-256:** `dcbc2aac36ac06be16fd89a073c0997c3e604e5381df759c103d328f28b021b7`  
**Verdict:** `PASS_SCIENTIFICALLY__EDITORIAL_CORRECTIONS_APPLIED__REASSEMBLY_REQUIRED`  
**Submission status:** `NOT_SUBMITTED`

## 1. Scope

This audit reviews the manuscript as one paper rather than as isolated study components. It checks:

- title, abstract, research-question, contribution, and conclusion consistency;
- exact Study-3, Study-4, and Study-6 numerical traceability;
- preservation of separate frozen populations and units;
- contact-model boundaries;
- first-versus-systematic Study-4 thresholds;
- Study-6 residual-state identities and benign assurance-loss counts;
- cross-study synthesis limits;
- prior-art and novelty positioning;
- IEEE citation-number first-use order;
- terminology consistency;
- overclaim and pooled-population controls;
- TAES prescreening coherence.

The first assembled draft was generated locally from the canonical component files by `TAES_ASSEMBLE_MANUSCRIPT.py`. The two generated files were intentionally left untracked pending this audit.

## 2. Scientific result audit

### Study 3 - PASS

Verified manuscript results remain consistent with the frozen Study-3 record:

- frozen population remains 1,380 trajectories;
- 67,620 epoch states are not treated as independent observations;
- persistent V5/K0 B0 = 46/46, mean exposure 122.5 logical seconds;
- persistent V5/K0 S1 = 46/46, mean exposure 122.5 logical seconds;
- persistent V5/K0 B2 = 0/46, mean exposure 0;
- persistent V5/K4 B0 = 46/46, mean exposure approximately 55.326 logical seconds;
- persistent V5/K4 S1 = 46/46, mean exposure approximately 49.022 logical seconds;
- persistent V5/K4 B2 = 0/46;
- truthful V0/K4/B0 remains 3/46 with mean 0.326 logical seconds and `PRE_ONSET_CACHE` origin;
- affected V4 records have invalid signatures and do not qualify;
- persistent V4 adds no V4-attributable false qualification;
- V5 remains a validly signed false trusted-producer claim rather than a cryptographic break;
- K4 remains a synthetic contact schedule and logical seconds remain model time.

No scientific correction or rerun is required.

### Study 4 - PASS

The full 18-rule threshold table in the manuscript matches the frozen Study-4 threshold map. In particular:

- Q1_D1 = safety 1/1, availability 7/7;
- Q2_D2 = safety 2/4, availability 4/6;
- Q3_D3 = safety 3/6, availability 2/5;
- Q4_D3 = safety 4/6, availability 2/4;
- Q5_D3 = safety 5/6, availability 2/3;
- Q6 D1/D2/D3 = safety 6/6, availability 2/2;
- Q7 D1/D2/D3 = safety 7/7, availability 1/1.

The manuscript preserves the null/equal-threshold cases at Q4_D1 vs Q4_D2, Q5_D1 vs Q5_D2, all Q6 variants, and all Q7 variants. First and systematic failure remain distinct. The safety and benign-unavailability blocks remain separate. Study 4 is not described as a Byzantine consensus experiment and does not contain a contact model.

No scientific correction or rerun is required.

### Study 6 - PASS

The manuscript matches the frozen Study-6 residual-state and benign-loss frontier:

- G0 = 4/5 incorrect states qualified; 32/64 benign-loss subsets;
- G1 = 3/5; 48/64;
- G2 = 3/5; 48/64;
- G3 = 2/5; 56/64;
- G4 = 2/5; 56/64;
- G5 = 1/5; 63/64.

Residual-state identity is preserved:

- G3 leaves `SOURCE_REVIEW_BYPASS` and `APPROVED_BAD_SOURCE`;
- G4 leaves `TRUSTED_BUILDER_COMPROMISE` and `APPROVED_BAD_SOURCE`;
- G5 leaves only `APPROVED_BAD_SOURCE`.

The manuscript does not interpret 4/5 or 1/5 as detection rates, nor 63/64 as an operational outage probability. `APPROVED_BAD_SOURCE` remains a structural observability boundary of the frozen model, not a theorem or universal impossibility result.

No scientific correction or rerun is required.

## 3. Cross-study synthesis audit - PASS

The synthesis is bounded appropriately:

- no common statistical unit is created;
- no pooled success rate, common effect size, or end-to-end recovery probability is defined;
- the three studies are not called an integrated experiment;
- the layered interpretation is explicitly post hoc at the manuscript synthesis level;
- only Study 3 models intermittent contact;
- Study 4 producer unavailability and Study 6 assurance-signal unavailability remain distinct constructs;
- same-repository independent reconstruction is described as reproducibility/audit rather than external replication;
- stronger composition is interpreted as moving or narrowing specific modeled residual boundaries, not as establishing universal superiority.

The central systems claim remains supportable:

> stronger trust composition can close or narrow specified modeled failure pathways without automatically making policy-visible evidence equivalent to hidden or objective truth.

## 4. Editorial/control corrections identified and applied

### A. Remove combined Paper-2 arithmetic total

The first assembled draft contained an explicit arithmetic sum of the three separate population counts only to state that it was not a pooled `N`. Although scientifically negative, this wording creates unnecessary pooled-population risk and violates the stricter Paper-2 claim firewall.

Correction applied to `TAES_MANUSCRIPT_SOURCE.md`:

- the combined arithmetic total is removed entirely;
- the manuscript now states only that the three counts are not summed or reported as a manuscript sample size.

The assembler now fails if the combined total appears anywhere in the assembled manuscript.

### B. IEEE citation first-use order

The first assembled Introduction cited reference numbers out of sequential first-appearance order because the numbering originated in the Related Work draft.

Correction applied to `TAES_SECTION_I_INTRODUCTION.md`:

- references [1] through [12] are now first introduced sequentially in the Introduction;
- no source identity or claim basis was changed.

The assembler now audits the first-use sequence of numeric IEEE references and fails if first appearance is not sequential.

### C. Producer-composition terminology

The title and synthesis are being standardized on **Producer Composition** rather than **Producer Quorums**. Study 4 uses vote thresholds and synthetic provenance-domain constraints but is not a Byzantine quorum protocol or consensus experiment.

Corrections applied:

- assembler title uses `Producer Composition`;
- `TAES_MANUSCRIPT_SOURCE.md` title uses `Producer Composition`;
- Introduction contribution language uses `producer-composition rule`;
- cross-study synthesis avoids presenting an operational "quorum choice" as the manuscript's design recommendation.

Quorum-system terminology remains appropriate in the Related Work discussion of actual prior art.

## 5. Title/abstract/RQ traceability - PASS

Current title candidate:

**Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance**

The title maps directly to the three study layers.

The abstract remains within the IEEE 150-250-word requirement under the repository tokenizer and reports all three study populations separately.

RQ traceability:

- RQ1 -> Study 3 temporal evidence and persistence/contact results;
- RQ2 -> Study 4 first/systematic compromise and benign-unavailability thresholds;
- RQ3 -> Study 6 residual artifact states and assurance-signal-loss frontier;
- systems synthesis question -> Section VII qualitative residual-boundary comparison only.

No unsupported RQ is introduced.

## 6. TAES prescreening assessment

### Strengths

- aerospace application is explicit from the first paragraph;
- the paper is framed as a systems-level trust-qualification problem rather than a generic cybersecurity enumeration;
- all three studies are tied to one bounded systems question;
- novelty is distinguished from established attestation, quorum, provenance, and trusted-recovery foundations;
- the paper preserves negative/null findings rather than optimizing for venue fit;
- limitations are unusually explicit about contact, logical time, real independence, standards compliance, and operational generalization.

### Main remaining editorial risk

The development draft is intentionally comprehensive and likely longer than the most effective TAES submission. Repeated claim-boundary statements appear in the Introduction, Section III, each study section, Section VII, Section VIII, and the Conclusion.

This repetition is currently useful for auditability, but the final manuscript should be compressed after a clean reassembly. Compression must not remove scientifically necessary distinctions, especially:

- qualification versus completed recovery;
- only Study 3 models contact;
- logical time is not operational time;
- synthetic provenance domains are not demonstrated independence;
- Study-4 blocks are separate;
- Study-6 blocks are separate;
- no pooled population;
- no global best rule/gate;
- `APPROVED_BAD_SOURCE` remains;
- same-repository reproducibility is not external replication.

## 7. Next gate

The first assembled draft hash is superseded by the component corrections above.

Required next action:

1. pull current `main`;
2. rerun `TAES_ASSEMBLE_MANUSCRIPT.py` in the canonical TAES directory;
3. verify assembly PASS, abstract word count, citation first-use order, and new SHA-256;
4. keep the regenerated assembled draft and manifest untracked until the regenerated manuscript is rechecked;
5. only after regenerated-pass approval should the derived manuscript and manifest be tracked.

## 8. Current verdict

**PASS SCIENTIFICALLY.**

The first assembled manuscript revealed editorial-control issues but no defect in Studies 3, 4, or 6 and no unsupported cross-study scientific conclusion. The identified issues have been corrected at the component/assembler level. A clean reassembly is required before the assembled source becomes a tracked manuscript artifact.
