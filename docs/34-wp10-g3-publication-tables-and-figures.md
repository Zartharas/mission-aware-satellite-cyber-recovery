# WP10-G3 Publication Tables and Figures

**Date:** 2026-08-29  
**Status:** Publication-display package locked from frozen WP10 results  
**Scientific authority:** `docs/28-wp10-integrated-findings-freeze.md`  
**Claim control:** `docs/30-wp10-g1-claim-to-evidence-matrix.md`  
**Results architecture:** `docs/31-wp10-g1-results-architecture.md`  
**Empirical reconciliation:** `docs/32-wp10-g2-empirical-reconciliation.md`

## Purpose

This package converts already-frozen WP10 findings into publication-ready tables and descriptive figures. It introduces **no new endpoint, model fit, hypothesis test, p-value, weighted score, global policy rank, imputation, or valid-run exclusion**.

All quantitative values below are copied from the integrated findings freeze and authoritative WP10 analyses already recorded in the repository. The publication displays are presentation artifacts, not new scientific analyses.

## Display inventory

### Main-paper tables

- `publication/tables/table-r1-proposition-summary.csv` — frozen population and P1–P5 outcome summary.
- `publication/tables/table-r2-p2-contact-effects.csv` — P2 modeled contact-condition contrasts and 95% seed-block bootstrap intervals.
- `publication/tables/table-r3-p3-p4-evidence-pathways.csv` — P3/P4 evidence-condition recovery and selected-path summary.
- `publication/tables/table-r4-p5-pareto-status.csv` — P5 condition-specific P7 Pareto status and bounded uncertainty interpretation.

### Supplementary table

- `publication/tables/table-s1-execution-provenance-sensitivity.csv` — execution-provenance distribution and 29-seed final-commit complete-block sensitivity.

### Main-paper figures

- `publication/figures/figure-r1-p2-contact-effects.svg` — forest-style effect display for M04, M05, and M07 under P6, P7, and their interaction.
- `publication/figures/figure-r2-p3-trusted-recovery.svg` — trusted-recovery proportions for fixed P5 and P7 under T0/T1 in the retained E3/M4/C0 block.
- `publication/figures/figure-r3-p4-selection-pathway.svg` — deterministic evidence → effective-policy/action → consequence pathway for P7 in E1 and E3.
- `publication/figures/figure-r4-p5-pareto-status.svg` — condition-specific P7 Pareto-status matrix across G01–G09.

## Table R1 — Frozen population and proposition outcome summary

The table must report the primary population (`720` VALID observations; `24 × 30`), M05 censoring (`180` observed recovery events, `540` right-censored at `30 s`), and M03 structural zero before the proposition rows.

P1 must appear with equal prominence to supported propositions. The table must not imply that a null proposition was omitted from the study narrative.

## Table R2 — P2 modeled contact effects

The retained estimates are:

| Endpoint | P6 C1−C0 | 95% CI | P7 C1−C0 | 95% CI | Interaction | 95% CI |
|---|---:|---|---:|---|---:|---|
| M04 containment RMST | +10.0831 s | [9.8304, 10.3735] | −0.0425 s | [−0.1977, 0.0899] | +10.1256 s | [9.7859, 10.5176] |
| M05 verified-recovery RMST | +10.4246 s | [9.6567, 11.3598] | −0.1808 s | [−0.7194, 0.2767] | +10.6054 s | [9.5343, 11.9023] |
| M07 state divergence | +10.0676 s | [9.8438, 10.3260] | −0.0390 s | [−0.1690, 0.0709] | +10.1066 s | [9.8135, 10.4499] |

For M04/M05, `τ = 30 s`. C1 is a **synthetic/modelled missed-contact window**, not measured operator or ground-station latency.

## Table R3 — P3/P4 evidence pathways

The main table uses the minimum cells necessary to reconstruct the evidence-dependent claims without overwhelming the paper:

- E3 fixed P5: A14/T0 and A15/T1, both `30/30` trusted recovery;
- E3 P7: A11/T0 `30/30` trusted recovery versus A13/T1 `0/30` trusted recovery and `30/30` recovery failed;
- E1 P7: A04/T0 effective P2 / `RESTRICT_HIGH_RISK_COMMANDS` versus A09/T1 effective P4 / `ENTER_SAFE_MODE`, with M02 `0.5 → 0.0` and M06 `0.0 → 1.0`;
- E3 P7: A11/T0 effective P5 rollback versus A13/T1 `evidence_insufficient` → P2 restriction, with M02 `1.0 → 0.5` and trusted recovery `30/30 → 0/30`.

`ENTER_SAFE_MODE` must be captioned as an **experimental modeled action**, not a native spacecraft safe-mode implementation.

## Table R4 — P5 condition-specific Pareto findings

The table reports point-estimate front membership separately from marginal bootstrap support. `5/9` is a front-membership count and **must not be described as a P7 success rate**.

Frozen group interpretation:

- G01: P7/A02 → P1, front, empirical tie with A01/P1.
- G02: P7/A04 → P2, front, empirical ties with A03/P1 and A07/P2.
- G03: P7/A06 → P2, front, empirical tie with A05/P1.
- G04: P7/A09 → P4, off front, dominated by A08/P2; marginal intervals support comparator dominance.
- G05: P7/A11 → P5, off front; dominates A10/P2 and A16/P6; point-dominated by A14/P5 because M05 RMST is `3.9819393339 s` versus `3.8009359910 s`; the A14 comparison is uncertain/tied under marginal intervals; marginal intervals support P7 dominance versus A10/P2.
- G06: P7/A13 → P2, off front; tied with A12/P2 and dominated by A15/P5; marginal intervals support comparator dominance versus A15/P5.
- G07: P7/A18 → P5, unique front member; dominates A17/P6; marginal intervals support P7 dominance.
- G08: P7/A21 → P1, front; dominates A19/P0 and ties A20/P1; marginal intervals support P7 dominance versus A19/P0.
- G09: P7/A24 → P4, off front; ties A23/P4 and is dominated by A22/P0; marginal intervals support comparator dominance versus A22/P0.

No simultaneous 95% Pareto-dominance claim is permitted because the retained P5 intervals are marginal percentile intervals.

## Figure R1 — P2 contact-condition effect plot

The plot uses a zero-reference vertical line and displays estimate ± 95% interval for the P6 contact effect, P7 contact effect, and P6-minus-P7 interaction for M04, M05, and M07.

Interpretation is limited to the controlled contact model. A16/A17 remain P6 cases; P6 waits for modeled ground authorization before delegating the verified rollback mechanism.

## Figure R2 — P3 trusted-recovery outcome

The figure displays trusted-recovery proportion in the E3/M4/C0 block:

- fixed P5 / T0: `30/30`;
- fixed P5 / T1: `30/30`;
- P7 / T0: `30/30`;
- P7 / T1: `0/30` trusted, `30/30` failed.

The caption must state that the narrower anticipated restoration-without-verification mechanism was not observed.

## Figure R3 — P4 selection/consequence pathway

The deterministic flow diagram has two rows:

### E1

- T0 → P7 effective P2 → `RESTRICT_HIGH_RISK_COMMANDS` → M02 `0.5`, M06 `0.0`.
- T1 → P7 effective P4 → `ENTER_SAFE_MODE` → M02 `0.0`, M06 `1.0`.

### E3

- T0 → P7 effective P5 → verified rollback → trusted recovery `30/30`, M02 `1.0`.
- T1 → `evidence_insufficient` → P7 effective P2 → restriction → recovery failed `30/30`, M02 `0.5`.

The diagram shows observed selection and consequence. It does not label any action objectively correct or incorrect.

## Figure R4 — P5 condition-specific Pareto-status matrix

The matrix uses four descriptive categories:

1. `TIE / EQUIVALENCE` — G01, G02, G03;
2. `COMPARATOR-SUPPORTED DISADVANTAGE` — G04, G06, G09;
3. `MIXED` — G05;
4. `P7-SUPPORTED BENEFIT` — G07, G08.

This categorical display is intentionally not a weighted projection of the five Pareto dimensions and is not an overall policy rank.

## Supplementary Table S1 — execution provenance and robustness

Primary analysis retains all 720 VALID observations:

- commit A `aae2239753119c92e7633db3b6c73aee94c7b6dd`: `1` VALID;
- commit B `97074d0cdc4261de02bc6f618e891a88f45f9cfc`: `9` VALID;
- commit C `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`: `710` VALID.

The final-commit complete-block sensitivity uses seeds `10002`–`10030` (`29` seeds / `696` observations) and preserves P7 front membership, pairwise Pareto relation, and primary-metric direction in all `9/9` groups.

## Caption language controls

Every figure/table caption must preserve these boundaries where relevant:

- controlled NOS3/Fortytwo software-in-the-loop environment;
- synthetic/modelled contact condition;
- no operational spacecraft or RF claim;
- no native spacecraft safe-mode claim;
- no objective P4 correctness oracle;
- no weighted P5 score/global rank;
- no claim that all 720 observations ran at execution commit C;
- M05 censoring remains explicit.

## G3 disposition

G3 is complete when the listed CSV/SVG assets are present, the assets contain only frozen values/relationships, and the repository review confirms that no runtime, raw campaign evidence, model-fitting code, or post-hoc analytic output was added.

The next phase after G3 is **WP10-G4 — evidence-locked Results and Discussion drafting**, beginning with Results and using the G1 claim matrix/G3 publication displays as the only quantitative manuscript authority.