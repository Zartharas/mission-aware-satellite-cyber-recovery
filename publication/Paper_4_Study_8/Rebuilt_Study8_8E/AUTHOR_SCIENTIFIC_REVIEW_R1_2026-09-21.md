# Rebuilt Paper 4 — Author / Scientific Review R1

**Review date:** 2026-09-21  
**Scope:** venue-neutral rebuilt Paper 4, Study 8 + Study 8E  
**Review status:** PASS_WITH_CONTROLLED_LANGUAGE_REFINEMENTS__NO_SCIENTIFIC_CHANGE

## 1. Review objective

Perform the explicitly authorized focused author/scientific review of the merged venue-neutral rebuilt Paper 4 before any live venue assessment or venue lock.

The review checks:

- frozen Study 8 and Study 8E numerical fidelity;
- finite-population inference language;
- cross-study synthesis boundaries;
- SatNOGS interpretation boundaries;
- current literature and standards metadata;
- Paper 4 / Paper 5 non-overlap;
- author metadata consistency within the Paper 4 lineage;
- novelty wording;
- venue-neutral editorial coherence.

No new scientific execution, reanalysis, endpoint, subgroup, or trace acquisition is authorized or performed.

## 2. Scientific review decision

**PASS.**

The integrated two-study architecture is scientifically coherent and materially stronger than the rejected Study-8-only manuscript because it now separates and then synthesizes two complementary estimands:

1. Study 8 — fixed modeled contact-capacity feasibility; and
2. Study 8E — minimum modeled rate under independently sourced public observation-opportunity timing.

The studies remain separate finite populations and are not pooled.

The strongest manuscript-level conceptual distinction remains:

> fixed-capacity feasibility asks whether the transition fits; solved-rate burden asks what modeled communication rate would make it fit.

The P3/P1 null structure is preserved exactly in both evidence layers without being described as external replication.

## 3. Controlled language refinements applied

Eight prose refinements were made. None changes a number, endpoint, factor, result, or interpretation boundary.

### 3.1 Deterministic finite-population wording

Changed:

- “did not increase the probability of modeled trusted recovery”

to:

- “did not increase the modeled trusted-recovery proportion”

Reason: Study 8 exhaustively evaluates a frozen deterministic finite population; “proportion” is the correct descriptive quantity.

### 3.2 Removed unneeded superlative wording

Changed:

- “The strongest fixed-capacity differences…”

to:

- “The fixed-capacity results instead varied…”

Reason: avoids an unnecessary comparative superlative that was not itself a frozen endpoint.

### 3.3 Bounded equal-capacity timing conclusion

The Study 8 equal-capacity statement is now explicitly scoped to the frozen model:

> equal aggregate capacity does not uniquely determine deadline feasibility within the frozen Study 8 model.

### 3.4 Bounded Study 8E disruption interpretation

The A0/A1 versus A2/A3 result is now reported directly as a difference in the frozen finite-threshold set rather than as a broad claim that disruption “materially restricts” real opportunity.

### 3.5 Bounded external-timing synthesis

The cross-study timing sentence now says that Study 8E **supports representing temporal opportunity explicitly** rather than claiming a broader external validation.

### 3.6 Bounded future-policy mechanism claim

The future-policy statement is now restricted to “within this model family.”

### 3.7 Bounded timing mechanism wording

The Study 8E Discussion now states that observation timing is **one of the frozen inputs determining whether the model yields a finite threshold**, rather than saying timing “materially determines” recovery in general.

### 3.8 Bounded engineering implication

The statement that a policy must change a feasibility-driving mechanism is now explicitly restricted to “within this modeled framework.”

## 4. Literature and standards verification

A targeted live verification was performed on 2026-09-21.

### NIST crypto agility

Verified current authority:

- NIST CSWP 39upd1, *Considerations for Achieving Crypto Agility: Strategies and Practices*
- final update: 2026-06-29
- supersedes CSWP 39
- DOI: 10.6028/NIST.CSWP.39-upd1
- URL: https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final

Bibliographic correction applied:

- NIST lists coauthor **Lily Chen**.
- The derivative BibTeX incorrectly contained “Lidong Chen.”
- REFERENCES.bib was corrected to “Chen, Lily.”

### IEEE space cybersecurity

Verified:

- IEEE 3536-2026
- *IEEE Standard for Space System Cybersecurity Design*
- status: Active Standard
- published: 2026-07-24
- URL: https://standards.ieee.org/ieee/3536/11916/

### SatNOGS

Verified current documentation:

- SatNOGS Network API access is open;
- API data are distributed under CC BY-SA;
- observation records expose start/end, ground-station, and NORAD-identification fields used for the frozen timing projection.

URL:
https://librespacefoundation.gitlab.io/satnogs/satnogs-network/api.html

This review does not reopen or reinterpret the frozen POP-002 / TRACE-002 acquisition decisions.

### CCSDS

Verified that the CCSDS Space Data Link Layer Security Working Group describes its link-layer security protocol as independent from any specific cryptographic algorithm.

URL:
https://ccsds.org/about/

The manuscript correctly avoids claiming that ML-KEM/ML-DSA are approved operational CCSDS PQC profiles.

### Closest 2026 literature

Current records remain consistent with manuscript positioning:

- Kim 2026 — broad systematic space-PQC survey, Acta Astronautica 246, 863–886.
- Ghosh & Nath 2026 — lattice-based PQC satellite analysis, IJSCN 44(5), 524–543.
- GSMA PQ.07 — PQC for NTNs, February 2026.
- De Zuane et al. 2026 — quantum-safe satellite IKE, arXiv preprint.
- Eichen et al. 2026 — bandwidth/power-constrained PQ authentication/NTN work, arXiv preprint.

A targeted current search did not identify a directly matching study combining explicit post-compromise epoch-transition semantics, a complete fixed-capacity logical-contact population, and a separately governed public observation-timing minimum-rate threshold analysis.

**No “first,” “only,” or priority claim is added.**

## 5. Numerical and claim-boundary review

The prior integrated-manuscript QA remains valid.

Review reconfirmed that the manuscript preserves:

### Study 8

- 3,456 positions;
- 635/864 = 73.4954% for every policy;
- P3-P1 = 0.000000 percentage points;
- profile success 93.7500%, 64.9306%, 61.8056%;
- 1,152/1,152 non-increasing matched profile-success ordering;
- exact deadline and regime strata;
- frozen policy-state/resource tradeoffs.

### Study 8E

- 20 traces;
- 476 source rows;
- 454 eligible anchors;
- 65,376 cases;
- 17,640 finite / 47,736 non-finite;
- finite fraction 0.269824;
- finite modeled thresholds 48 / 345 / 57,727 bit/s min/median/max;
- 6 h / 12 h / 24 h finite fractions 0.052863 / 0.205947 / 0.550661;
- A0/A1 = 0.405286;
- A2/A3 = 0.134361;
- every policy 4,410/16,344 finite;
- every profile 5,880/21,792 finite;
- 4,410 both-finite P3/P1 comparisons all exactly 0 bit/s difference;
- 21,792/21,792 preserved profile burden orderings;
- zero rollback/stale-epoch structural sums.

No Results-001 scientific value is used.

## 6. Cross-study synthesis review

The synthesis remains valid because it does not:

- pool populations;
- combine denominators;
- compute a common effect size;
- map logical slots to physical time;
- equate fixed-capacity success with solved-rate feasibility;
- describe Study 8E as external empirical replication.

The central combined interpretation is retained:

> P3 does not improve the respective feasibility endpoint because the guard does not add communication opportunity, increase capacity, or reduce the required transition-object bundle.

This statement is model-bounded and supported by the two frozen result sets.

## 7. Paper 5 non-overlap review

No Paper 5 experimental evidence appears in the rebuilt Paper 4 manuscript.

Absent from Paper 4:

- CuCD-ID;
- AegisSat;
- UNSW-IoTSAT;
- 0/8 semantic-coverage results;
- action-identifiability results;
- guaranteed sidecar-state results;
- B0/B1/B2/S1 selector evidence.

The Paper 4 / Paper 5 publication-independence gate remains intact.

### Administrative metadata note

Repository search found a cross-paper author-degree formatting inconsistency:

- the Paper 4 lineage and already submitted Paper 1 records use **Aman Kumar Singh, MS, DSc**;
- publication/Paper_5_Study_9/Cyber_Security_and_Applications/AUTHOR_METADATA.md currently uses **Aman Kumar Singh, MS, PhD**.

No Paper 5 file is modified in this review because that is outside the Paper 4 scientific-review scope. The inconsistency should be checked separately before Paper 5 submission metadata is finalized.

## 8. Editorial assessment

### Title

Current working title remains scientifically accurate and appropriately cautious:

**Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing**

No title lock is made by this review.

### Abstract

The abstract presents:

- the two-study design;
- separate populations;
- exact Study 8 null;
- Study 8E finite-rate result;
- profile-burden distinction;
- SatNOGS boundary.

No immediate scientific rewrite is required before venue assessment.

### Introduction / novelty

The current Introduction avoids claiming novelty for:

- satellite PQC generally;
- crypto agility generally;
- post-quantum bandwidth overhead;
- quantum-safe satellite IKE;
- use of SatNOGS itself.

The narrower post-compromise transition-feasibility contribution is defensible.

### Discussion

After the R1 language refinements, the Discussion appropriately distinguishes:

- mechanism from policy ranking;
- fixed capacity from solved rate;
- modeled timing from operational contact;
- structural consistency from replication.

## 9. Remaining work before submission readiness

The manuscript is scientifically ready for **live venue assessment**, but not yet for publisher submission.

Still pending:

1. live venue/scope/author-guideline assessment;
2. venue selection and explicit venue lock;
3. venue-specific length and formatting adaptation;
4. final figure generation and placement;
5. final table selection/formatting;
6. venue-specific reference style;
7. venue-specific AI-assistance disclosure policy;
8. final title/abstract/keyword lock;
9. publisher-facing package freeze;
10. separate explicit publisher-submission authorization.

## 10. Decision

AUTHOR_SCIENTIFIC_REVIEW_R1_PASS__READY_FOR_SEPARATE_LIVE_VENUE_ASSESSMENT_GATE

No new scientific analysis is required to proceed to venue assessment.

No venue is selected or locked by this review.

No publisher submission is authorized.
