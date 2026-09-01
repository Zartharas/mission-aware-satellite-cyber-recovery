# Target-Neutral Journal Manuscript Assembly

**Assembly status:** Study-1 manuscript frozen; Study-2 Phase-7 evidence frozen; two-study journal integration in progress  
**Study-1 evidence audit:** `docs/35-wp10-g5-manuscript-evidence-audit.md` — PASS  
**Study-2 statistical freeze:** `../../study2/docs/PHASE7_RESULTS_FREEZE.md` — `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`  
**Study-2 independent reproduction:** PASS, 0 mismatches  
**Primary target journal:** Computers & Security (Elsevier), Full Length Article  
**Backup targets:** AIAA Journal of Aerospace Information Systems; IEEE Transactions on Aerospace and Electronic Systems  
**Author-attestation gate:** PASS  
**Current submission state:** **two-study journal integration / Study-2 source-evidence release gate**

## Scientific architecture of the article

The article reports **two separately frozen empirical studies**. They share a post-detection satellite cyber-response/trusted-recovery research problem but have different frozen designs, populations, endpoints, and provenance. They must never be represented as one pooled experiment.

- **Study 1:** 24 cells × 30 repetitions = **720 VALID observations**, with 9 retained INVALID attempts outside statistical membership.
- **Study 2:** 85 cells = **3,872 VALID observations**, 0 INVALID attempts.

Study 1 remains the original comparative response/recovery experiment. Study 2 is a prospectively specified adversarial evidence-aware generalization with additional evidence mechanisms, adversary budgets, contact regimes, ambiguity controls, and selector/context ablations.

## Authoritative manuscript order

1. `00-title-abstract.md` — two-study title, abstract, keywords
2. `01-introduction.md` — cybersecurity problem, two-study contributions, scope
3. `02-background-and-related-work.md` — Mission Aware, FDIR/autonomy, cyber resilience, trusted recovery, venue-adjacent work, SPARTA correspondence, NIST lifecycle positioning
4. `03-methods.md` — **Study-1** adversary/knowledge model, trust boundaries, design, policies, outcomes, validity, statistics, provenance, reproducibility
5. `03-study2-methods-extension.md` — **Study-2** frozen protocol, adversary/evidence/contact factors, policy family, runtime/evidence boundary, endpoints, multiplicity, provenance
6. `04-results.md` — **Study-1** evidence-locked P1–P5 results
7. `04-study2-results-extension.md` — **Study-2** evidence-locked RQ1–RQ5 results and interpretation limits
8. `05-discussion.md` — cross-study synthesis, cybersecurity implications, limitations, next research questions
9. `06-conclusion.md` — bounded two-study conclusions and remaining validation path
10. `07-declarations-and-availability.md` — ethics, responsible-research boundary, separate Study-1/Study-2 data availability, reproducibility, funding, declarations

No secondary full-text copy should be manually maintained. Journal-specific exports must be generated from these components so scientific wording does not drift.

## Quantitative authority

### Study 1

Study-1 quantitative authority remains the frozen WP10 record in `docs/28`–`docs/34`, `publication/tables/`, and the independently reconstructed/regression-tested `analysis/` reproduction package. The original WP10 executable analysis source was not preserved; the later reconstruction is explicitly labeled and does not redefine the historical analysis.

Study-1 public evidence-of-record:

- Zenodo version DOI `10.5281/zenodo.22181540`
- Zenodo concept DOI `10.5281/zenodo.22181539`
- 720-membership SHA-256 `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`
- attempt-ledger SHA-256 `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- campaign-tree SHA-256 `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`

### Study 2

Study-2 quantitative authority is the canonical Phase-7 freeze and its immutable Phase-6 evidence bindings:

- `../../study2/PHASE7_RESULTS_FREEZE.json`
- `../../study2/PHASE7_PROVENANCE.json`
- `../../study2/docs/PHASE7_RESULTS_FREEZE.md`
- `../../study2/evidence/phase7/INDEPENDENT_REPRODUCTION_AUDIT.json`
- exact Phase-7 result ZIP retained under `../../study2/evidence/phase7/archive/`

Frozen identities include:

- 3,872 VALID / 0 INVALID / 85 cells
- Phase-6 artifact ZIP SHA-256 `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- observations SHA-256 `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- trial-manifest SHA-256 `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`
- Phase-7 result ZIP SHA-256 `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`
- 162 primary paired contrasts
- 432 prespecified secondary contrasts
- independent reproduction mismatches: 0

The Phase-7 result ZIP is durable in Git history. The underlying Phase-6 source evidence still requires responsible-release review and a DOI-bearing durable archive before actual journal submission. No Study-2 DOI is invented in advance.

## Main publication displays

### Frozen Study-1 displays

- Table R1: `../tables/table-r1-proposition-summary.csv`
- Table R2: `../tables/table-r2-p2-contact-effects.csv`
- Table R3: `../tables/table-r3-p3-p4-evidence-pathways.csv`
- Table R4: `../tables/table-r4-p5-pareto-status.csv`
- Table R5: `../tables/table-r5-cybersecurity-positioning.csv`
- Table R6: `../tables/table-r6-security-property-mapping.csv`
- Figure R1: `../figures/figure-r1-p2-contact-effects.svg`
- Figure R2: `../figures/figure-r2-p3-trusted-recovery.svg`
- Figure R3: `../figures/figure-r3-p4-selection-pathway.svg`
- Figure R4: `../figures/figure-r4-p5-pareto-status.svg`
- Supplementary Table S1: `../tables/table-s1-execution-provenance-sensitivity.csv`

### Study-2 displays

- Table R7: `../tables/table-r7-study2-prespecified-findings.csv`
- Supplementary Table S2: `../tables/table-s2-study2-secondary-holm.csv`
- Study-2 claim traceability: `study2-claim-traceability.csv`

Study-2 publication tables are manuscript-facing summaries only. The Phase-7 freeze/provenance files remain authoritative for exact statistical identities.

## Scientific non-negotiables for any journal export

### Cross-study

- Do not pool 720 Study-1 observations and 3,872 Study-2 observations into a single statistical population.
- Do not alter either frozen campaign or recalculate frozen estimates to improve presentation.
- Do not compute or report a weighted global policy score or a global policy rank.
- Do not make operational spacecraft, RF, real-link latency, human-operator timing, flightworthiness, or certification claims.
- Deterministic rule-based selectors are not to be described as AI/ML scientific methods.

### Study 1

- exactly 720 VALID primary analysis observations;
- P1 unsupported on predeclared M01/M02/M03/M06 outcomes;
- C1 described as synthetic/modelled contact only;
- A16/A17 retained as P6, with post-authorization delegation to the P5 rollback mechanism;
- M05 explicit event/censor representation and 30-s horizon;
- P3 broader evidence-dependent finding while the narrower restoration-without-verification mechanism remains absent;
- P4 reported as actual selection/action/consequence, with no objective correctness oracle;
- T1 remains omission/reduction of selected policy-visible evidence fields, not a stale/contradictory/forged-evidence experiment;
- P7 remains a frozen deterministic rule-based selector;
- `ENTER_SAFE_MODE` remains an experimental modeled action;
- M03 structural zero is an observed result, not proof of universal safety;
- P5 remains condition-specific, with no 5/9 success-rate framing;
- execution provenance 1/9/710 and the 29-seed/696-observation final-C analysis remain sensitivity/provenance context.

### Study 2

- exactly 3,872 VALID observations, 0 INVALID attempts, 85 cells;
- recovery/containment time-to-event uses the frozen 240-logical-second restriction;
- logical SIL seconds are not spacecraft/network wall-clock latency;
- V5 may produce evidence-qualified recovery while hidden adjudication truth remains false under bounded producer compromise; do not equate evidence qualification with objective correctness;
- Block-C `BENIGN`/`ADVERSARIAL` contrasts are a **structural label-invariance/control result** because the label does not alter hidden truth or generated policy-visible evidence within each ambiguity family;
- do not claim Block C empirically demonstrates discrimination or non-discrimination between genuinely distinct benign/adversarial causal mechanisms;
- K4 remains a separate intermittent/flapping-contact contrast, not ordinal severity 4;
- A2/K2 remains a coupled producer-compromise/contact-loss profile, not an adversary-only causal contrast;
- secondary n=32 blocks remain estimation/sensitivity evidence, not prospectively powered small-effect confirmatory tests;
- context ablations support specific dependencies, not a universal dominant context variable.

## Submission metadata and archive state

The author-owned factual declarations remain closed. The primary target remains Computers & Security. The Study-1 Zenodo identifiers remain fixed and must be labeled Study-1 evidence. The current combined-paper submission cannot advance to final export until:

1. the two-study manuscript integration and claim/citation audits pass;
2. the Study-2 source-evidence package passes responsible-release review and receives a durable DOI-bearing archive;
3. the Computers & Security target package is reconciled to the two-study article;
4. live Guide for Authors/Aims & Scope/Editorial Manager requirements are rechecked on the actual submission date;
5. the exact submission export passes citation/DOI/frozen-claim/scope checks.

An institutional IRB/HRPP identifier remains conditional on a specific applicable portal requirement and must not be invented.

## Assembly rule

The component files above are the manuscript source of truth. Historical Study-1 work-package documents remain provenance and may retain stage-local wording. Current article status is governed by this assembly file, `../../tracker/RESEARCH_TRACKER.md`, and the canonical Study-2 Phase-7 provenance/freeze records.
