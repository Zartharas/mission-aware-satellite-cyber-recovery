# Target-Neutral Manuscript Assembly

**Assembly status:** WP10-G6 candidate  
**Scientific evidence audit:** `docs/35-wp10-g5-manuscript-evidence-audit.md` — PASS  
**Quantitative authority:** `docs/28`–`docs/34` and `publication/tables/`  
**Target journal:** Not yet selected / not required for scientific assembly

## Authoritative manuscript order

1. `00-title-abstract.md` — title, abstract, keywords
2. `01-introduction.md` — problem, gap, contributions, scope
3. `02-background-and-related-work.md` — Mission Aware, FDIR/autonomy, cyber resilience, trusted recovery, testbeds/detection, targeted gap
4. `03-methods.md` — testbed boundary, frozen design, policies, outcomes, validity, final analysis, provenance, reproducibility
5. `04-results.md` — evidence-locked proposition results
6. `05-discussion.md` — bounded interpretation and limitations
7. `06-conclusion.md` — conclusions and future work
8. `07-declarations-and-availability.md` — ethics, responsible-research boundary, data/code availability, reproducibility, submission placeholders

## Main publication displays

- Table R1: `../tables/table-r1-proposition-summary.csv`
- Table R2: `../tables/table-r2-p2-contact-effects.csv`
- Table R3: `../tables/table-r3-p3-p4-evidence-pathways.csv`
- Table R4: `../tables/table-r4-p5-pareto-status.csv`
- Figure R1: `../figures/figure-r1-p2-contact-effects.svg`
- Figure R2: `../figures/figure-r2-p3-trusted-recovery.svg`
- Figure R3: `../figures/figure-r3-p4-selection-pathway.svg`
- Figure R4: `../figures/figure-r4-p5-pareto-status.svg`

Supplementary provenance table:

- Table S1: `../tables/table-s1-execution-provenance-sensitivity.csv`

## Scientific non-negotiables for any journal export

Any combined DOCX/LaTeX/PDF or journal-specific rewrite must preserve:

- exactly 720 VALID primary analysis observations;
- P1 unsupported on predeclared M01/M02/M03/M06 outcomes;
- C1 described as synthetic/modelled contact only;
- A16/A17 retained as P6, with post-authorization delegation to the P5 rollback mechanism;
- M05 explicit event/censor representation and 30-s horizon;
- P3 broader evidence-dependent finding while the narrower restoration-without-verification mechanism remains absent;
- P4 as actual selection/action/consequence, with no objective correctness oracle;
- `ENTER_SAFE_MODE` as an experimental modeled action;
- M03 structural zero as an observed result, not proof of universal safety;
- P5 as condition-specific, with no 5/9 success-rate language, no weighted score, and no global policy rank;
- execution provenance 1/9/710 across commits A/B/C and the 29-seed/696-observation final-C sensitivity as sensitivity only;
- no operational spacecraft, real RF, real operator timing, flightworthiness, or certification claim.

## Items legitimately pending user/venue input

The scientific manuscript can be assembled without these items, but final submission cannot be completed until applicable information is supplied or selected:

- final author list and affiliations;
- corresponding-author details;
- funding statement;
- competing-interest statement;
- acknowledgments;
- target journal/conference and article type;
- journal word/table/figure/reference limits;
- required generative-AI disclosure language, if any;
- final Zenodo DOI(s) after WP11 deposit.

## Assembly rule

The component files above are the manuscript source of truth. Do not maintain a second manually copied full-text file before target-journal export, because duplicate prose copies can drift. A journal-specific export should be generated from these components only after the pre-submission audit passes.