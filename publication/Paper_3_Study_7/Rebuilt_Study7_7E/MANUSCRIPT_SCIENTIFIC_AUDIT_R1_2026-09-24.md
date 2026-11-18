# Rebuilt Paper 3 — Venue-Neutral R1 Scientific Audit

**Audit ID:** `PAPER3-S7-S7E-MANUSCRIPT-AUDIT-R1-001`  
**Date:** 2026-09-24  
**Manuscript:** `PAPER3_REBUILT_MANUSCRIPT_R1.md`  
**Basis commit:** `4b14d4a69ac8d6d0ddb85eb6d32045b0d1fe04c2`  
**Result:** **PASS**

## 1. Scope

This audit checks whether the first complete venue-neutral Study 7 + Study 7E manuscript accurately reports the frozen scientific evidence and preserves the cross-study and publication boundaries.

It does not perform a live venue selection, current journal-guideline audit, publisher formatting pass, or publisher submission.

## 2. Manuscript inventory

- approximate manuscript word count: 5,984;
- references: 13;
- article form: venue-neutral full research article;
- Study 7 and Study 7E are presented as separate studies;
- no combined sample size or pooled error metric is reported.

## 3. Study-7 checks

Verified against `study7/results/RESULTS_FREEZE.json` and `study7/results/CANONICAL_FINDINGS.md`:

- total population = 1,033 observations;
- Block A = 512;
- Block B = 512;
- Block C = 9;
- L0 visible-state lattice error = 0;
- L1 corroboration-lattice errors = 2;
- independent-disagreement unsafe proceed: D0 = 1, L0 = 1, L1 = 0;
- correlated-false-corroboration unsafe proceed: D0 = 1, L0 = 1, L1 = 1;
- Study-7 claims remain information-sufficiency claims rather than ML-superiority claims.

**Disposition:** PASS.

## 4. Study-7E population and integrity checks

Verified against the frozen held-out checkpoint and result-freeze records:

- E1 = 84 scenarios;
- E2 = 104;
- C0 = 8;
- total held-out scenarios = 196;
- policies per scenario = 4;
- total policy decisions = 784;
- invalid scenarios = 0;
- audit mismatches = 0;
- equal-information paired hashes verified = true;
- result freeze remains active.

**Disposition:** PASS.

## 5. Study-7E quantitative checks

Exact aggregate manuscript table matches the frozen result checkpoint:

| Policy | Errors | Unsafe | FCH | ENTER | HOLD |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

Verified additional manuscript values:

- D0/L0 disagreement = 67/196;
- D1/L1 disagreement = 72/196;
- deterministic corroboration delta = unsafe -5 / FCH +14;
- learned corroboration delta = unsafe +10 / FCH -14;
- common F6-F12 L1 T0 = 5/3/2 error/unsafe/FCH;
- common F6-F12 L1 T4 = 8/6/2;
- F12 adverse transfer retained;
- C0 null result retained.

**Disposition:** PASS.

## 6. Interpretation-boundary checks

The manuscript explicitly preserves:

- no global policy ranking;
- no global ML superiority;
- no universal corroboration benefit;
- no monotonic trust-separation benefit;
- no operational spacecraft probability interpretation;
- no flight qualification or certification-sufficiency claim;
- no NASA endorsement;
- no pooled Study-7/Study-7E population.

An initial automated string check looked for the exact phrase "does not support a global policy ranking" and returned false because the manuscript wording is "These counts do not support a global policy ranking." Manual semantic review confirms the required prohibition is present. No manuscript change is required for this checker-string mismatch.

**Disposition:** PASS.

## 7. Architecture-grounding check

The manuscript correctly distinguishes:

- cFS engineering/runtime qualification of producer, signed-evidence qualifier, deterministic D0/D1 policy binding, and recovery sink; from
- canonical held-out learned inference using frozen hash-verified joblib models under the bound Python/scikit-learn environment plus an independent semantic-tree audit.

The manuscript does not describe Study 7E as flight-certified, NASA-validated, or an end-to-end onboard ML deployment.

**Disposition:** PASS.

## 8. Cross-publication overlap check

The manuscript architecture and non-overlap gate keep Paper 3 distinct from:

- Paper 1 — deterministic mission-aware response/recovery and V5 antecedent;
- Paper 2 — temporal/provenance/quorum/artifact assurance;
- Paper 4 — cryptographic transition burden and contact/timing feasibility;
- Paper 5 — semantic interoperability and public-dataset decision identifiability.

No frozen observations from those publication lines are imported as Paper-3 evidence.

**Disposition:** PASS.

## 9. Reference status

The 13 references are inherited from repository-vetted Study-7/Paper-3 sources and the Study-7E architecture source ledger. Their scientific roles are appropriate for R1.

A fresh live DOI/URL/journal-metadata verification has **not** yet been performed for the rebuilt R1. That check should be performed together with the next live literature and venue-fit stage rather than silently treating historical metadata as current.

## 10. Audit decision

**PASS — venue-neutral R1 is scientifically consistent with the frozen Study-7 and Study-7E evidence and is suitable for repository review/CI.**

Next actions:

1. expose the branch through a review PR;
2. require repository CI to remain green;
3. do not merge the manuscript integration PR yet without a later explicit author merge authorization;
4. after repository validation, perform a live literature/reference and venue-fit assessment before locking a target journal;
5. publisher submission remains separately prohibited.
