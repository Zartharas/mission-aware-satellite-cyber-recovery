# TAES Paper 2 Scientific Claim Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Paper:** Studies 3 + 4 + 6 only  
**Verdict:** `PASS_WITH_EDITORIAL_CORRECTIONS_APPLIED__ASSEMBLY_AUDIT_STILL_REQUIRED`

## 1. Audit scope

This audit checks the component-complete TAES development draft against the frozen scientific records for:

- exact population identities and units;
- exact numeric results used in manuscript prose and tables;
- endpoint meaning;
- null, negative, structural-zero, and conditional results;
- cross-study separation;
- interpretation boundaries;
- prohibited operational extrapolations.

Audited manuscript components:

- `TAES_ABSTRACT_KEYWORDS.md`
- `TAES_SECTION_I_INTRODUCTION.md`
- `TAES_MANUSCRIPT_SOURCE.md` Sections II-III
- `TAES_SECTION_IV_STUDY3.md`
- `TAES_SECTION_V_STUDY4.md`
- `TAES_SECTION_VI_STUDY6.md`
- `TAES_SECTION_VII_SYNTHESIS.md`
- `TAES_SECTION_VIII_VALIDITY.md`
- `TAES_SECTION_IX_CONCLUSION.md`

Authoritative science remains under `study3/`, `study4/`, and `study6/`. Manuscript files are projections of those frozen records and do not replace them.

## 2. Population audit

PASS.

- Study 3: exactly 1,380 deterministic trajectories.
- Study 4: exactly 4,608 exact rule-by-subset observations.
- Study 6: exactly 420 exact observations.
- Study 5 is not a Paper-2 core population.
- No manuscript section defines the arithmetic sum 6,408 as a pooled sample size.
- Study-3 epoch states are explicitly kept separate from the trajectory statistical unit.

## 3. Study-3 claim audit

Authoritative sources checked:

- `study3/STUDY3_PROTOCOL.json`
- `study3/results/CANONICAL_FINDINGS.md`
- frozen canonical Study-3 outputs and audit records.

PASS.

Verified manuscript claims include:

- 240-logical-second horizon, five-logical-second epochs, five-logical-second evidence validity;
- 46 onset phases from 10 through 235 logical seconds;
- K0 continuous contact and exact K4 windows `[25,35]`, `[75,90]`, `[145,165]`, `[220,240]`;
- V0 truthful evidence, V4 post-signature manipulation with invalid signature, V5 false but validly signed trusted-producer evidence;
- 30 cells, 1,380 trajectories, 67,620 epoch states;
- persistent V5/K0 B0 = 46/46, mean exposure 122.5 logical seconds;
- persistent V5/K0 S1 = 46/46, mean exposure 122.5;
- persistent V5/K0 B2 = 0/46, mean exposure 0;
- persistent V5/K4 B0 = 46/46, mean exposure approximately 55.326 logical seconds, with V5 increment 55.0;
- persistent V5/K4 S1 = 46/46, mean exposure approximately 49.022 logical seconds;
- persistent V5/K4 B2 = 0/46;
- S1 persistent-V5/K4 exposure approximately 6.304 logical seconds lower than B0, without immunity language;
- V4 affected records never qualify;
- truthful V0/K4/B0 false qualification = 3/46 onset phases, mean 0.326 logical seconds, attributed to `PRE_ONSET_CACHE`;
- truthful V0/K4 S1 and B2 = zero false qualification;
- one-shot V5 K0 B0/S1 mean exposure = five logical seconds across all 46 onset phases.

Interpretation controls PASS:

- K4 is called synthetic/flapping/intermittent modeled contact, never an orbital pass schedule.
- logical seconds are not converted to operational time.
- B2 structural zeros are preserved but not called immunity or global superiority.
- V4/V5 are used to distinguish record alteration from semantic trusted-producer falsity; manuscript does not say cryptography failed.
- `unsafe_permissive` is not presented as completed recovery.

Editorial correction applied during audit:

The initial abstract/conclusion wording "post-signature manipulation is rejected" was tightened to state that the **affected V4 manipulated records** are rejected. This preserves the separate B0/K4 pre-onset-cache false-qualification mechanism and avoids an overbroad treatment-level claim.

## 4. Study-4 claim audit

Authoritative sources checked:

- `study4/STUDY4_PROTOCOL.json`
- `study4/results/CANONICAL_FINDINGS.md`
- `study4/results/canonical/thresholds.csv`
- frozen Study-4 audit records.

PASS.

Verified design claims:

- seven producers;
- synthetic provenance allocation 3/2/2;
- 18 rules over total vote threshold 1-7 and domain threshold 1 through `min(3,q)`;
- registered-producer denominator;
- separate safety and benign availability blocks;
- 128 subsets per rule per block;
- exact population 4,608.

The complete threshold table in Section V matches the canonical threshold file:

- Q1_D1: safety 1/1, availability 7/7
- Q2_D1: 2/2, 6/6
- Q2_D2: 2/4, 4/6
- Q3_D1: 3/3, 5/5
- Q3_D2: 3/4, 4/5
- Q3_D3: 3/6, 2/5
- Q4_D1: 4/4, 4/4
- Q4_D2: 4/4, 4/4
- Q4_D3: 4/6, 2/4
- Q5_D1: 5/5, 3/3
- Q5_D2: 5/5, 3/3
- Q5_D3: 5/6, 2/3
- Q6_D1/D2/D3: 6/6, 2/2
- Q7_D1/D2/D3: 7/7, 1/1.

Interpretation controls PASS:

- first and systematic failure are both reported where subset composition matters;
- provenance nulls at Q4_D1/D2, Q5_D1/D2, Q6 variants, and Q7 variants are preserved;
- provenance diversity is not presented as monotonic or universally beneficial;
- synthetic provenance domains are not treated as demonstrated real independence;
- subset fractions are not probabilities;
- producer unavailability is not contact loss or mission availability;
- Study 4 is explicitly distinguished from Byzantine consensus/distributed agreement;
- no globally best quorum or rule is claimed.

## 5. Study-6 claim audit

Authoritative sources checked:

- `study6/STUDY6_PROTOCOL.json`
- `study6/results/CANONICAL_FINDINGS.md`
- `study6/results/CANONICAL_GATE_SUMMARY.csv`
- frozen Study-6 audit records.

PASS.

Verified design claims:

- six artifact states, one correct and five incorrect;
- six visible assurance signals;
- six frozen gates;
- Block A = 36 observations;
- Block B = 384 observations;
- total = 420 observations;
- adversarial artifact states and benign assurance unavailability remain separate blocks.

Verified gate frontier:

- G0: 4/5 incorrect states qualified, benign loss 32/64;
- G1: 3/5, 48/64;
- G2: 3/5, 48/64;
- G3: 2/5, 56/64;
- G4: 2/5, 56/64;
- G5: 1/5, 63/64;
- minimum missing required signal for benign loss = one for every gate.

Residual-state identity PASS:

- G0 residual set is correct;
- G1/G2 residual sets are correct;
- G3 leaves `SOURCE_REVIEW_BYPASS` plus `APPROVED_BAD_SOURCE`;
- G4 leaves `TRUSTED_BUILDER_COMPROMISE` plus `APPROVED_BAD_SOURCE`;
- G5 leaves only `APPROVED_BAD_SOURCE`.

Interpretation controls PASS:

- 4/5 and 1/5 are not called empirical rates or detector performance;
- `APPROVED_BAD_SOURCE` is described as a structural observability boundary, not a theorem;
- G1/G2 and G3/G4 equal aggregate counts are not converted to operational equivalence;
- stronger gates are not called globally best;
- modeled "independent" signals are not treated as proof of independent real infrastructures;
- assurance-signal unavailability is not contact loss or mission availability;
- no real malware, exploit, key compromise, flight artifact, or operational supply-chain claim is made.

## 6. Cross-study synthesis audit

PASS WITH REQUIRED LABELING ALREADY PRESENT.

The manuscript explicitly states that:

- Studies 3, 4, and 6 were independently designed and frozen;
- the common residual-trust framework is a manuscript-level post hoc synthesis;
- the studies do not form one integrated experiment;
- there is no causal sequence Study 3 -> Study 4 -> Study 6;
- no common effect size, success probability, pooled population, or end-to-end recovery probability is defined;
- only Study 3 directly models intermittent contact.

The synthesis is mechanism-level only: policy-visible evidence can remain insufficient to reveal research-only truth when the relevant mismatch lies outside the visible evidence set.

## 7. Operational overclaim audit

PASS.

The component draft does not claim measured:

- flight safety;
- flightworthiness;
- mission availability;
- RF performance;
- orbit performance;
- processor performance;
- energy or thermal performance;
- ground-station performance;
- real operator latency;
- certification or framework compliance;
- operational attack prevalence;
- operational recovery probability.

## 8. Null, negative, and conditional findings audit

PASS.

The draft preserves:

- Study-3 B2 structural zero without global-superiority language;
- Study-3 V4 negative control;
- Study-3 V0 cache boundary;
- Study-4 provenance null/equal-threshold results;
- Study-4 benign-availability cost;
- Study-6 G1/G2 equality;
- Study-6 G3/G4 equal counts with different residual states;
- Study-6 `APPROVED_BAD_SOURCE` residual state;
- Study-6 benign assurance-unavailability cost.

## 9. Remaining scientific gates

This audit is performed on component files. Before manuscript freeze, repeat the audit against the **assembled single manuscript source** to detect any assembly drift, duplicated text, changed numbers, broken cross-references, or reference-number changes.

Still required:

1. single-source manuscript assembly;
2. assembled-manuscript scientific claim audit;
3. assembled-manuscript citation audit;
4. final terminology/style audit;
5. TAES formatting and PDF visual QA.

No scientific defect was found that justifies rerunning, enlarging, or modifying Studies 3, 4, or 6.
