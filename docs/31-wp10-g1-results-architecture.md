# WP10-G1 Results Architecture

**Date:** 2026-08-29  
**Status:** Results-section architecture locked for manuscript drafting  
**Claim control:** `docs/30-wp10-g1-claim-to-evidence-matrix.md`  
**Scientific findings authority:** `docs/28-wp10-integrated-findings-freeze.md`

## Purpose

This document defines the manuscript Results architecture before prose is written. Its purpose is to preserve the frozen scientific record, prevent selective emphasis, and ensure that null, supported, bounded, conditional, and sensitivity findings are reported in the order needed for reviewer reconstruction.

The section numbering below is provisional and may be adapted to the target journal. The scientific ordering and claim boundaries are not provisional.

## Results-section design principles

1. Lead with the frozen analysis population and proposition summary rather than the strongest positive effect.
2. Report P1’s null result before P2–P5 positive or conditional findings.
3. Keep Results descriptive and inferential; literature comparison and broader meaning belong in Discussion.
4. Report absolute counts/denominators with ratios where applicable.
5. For M04/M05, state the RMST horizon (`τ = 30 s`) and right-censoring rule.
6. Do not introduce p-values; the retained analyses use exact counts/intervals and seed-block bootstrap intervals as applicable.
7. P5 intervals are marginal percentile intervals, not simultaneous Pareto-confidence regions.
8. Never convert P5 into a weighted score or global policy ranking.
9. Preserve A16/A17 as P6 requested/effective-policy cases even though P6 delegates to the P5 rollback mechanism after synthetic authorization.
10. Preserve execution-provenance wording: 1 / 9 / 710 VALID observations across the three historical execution commits.

## Recommended main Results structure

### 4.1 Frozen analysis population and endpoint integrity

**Purpose:** Establish what was analyzed and the endpoint/provenance constraints before proposition results.

**Claim IDs:** C00, C22, C23, C24.

**Must report:**

- `720` frozen VALID observations from `24 × 30` balanced cells/seeds;
- exclusion of the 9 ledgered INVALID attempts and non-analysis pre-runtime/quarantined evidence from statistical membership;
- M05 explicit event/censor binding: `180` observed recovery events and `540` right-censored observations at `30 s`;
- M03 structural zero across the 720-run locked extraction;
- concise execution-provenance statement, with detail deferred to Section 4.7.

**Recommended display:** `Table R1 — Frozen analysis population and proposition outcome summary`.

**Keep out of this subsection:** detailed invalid-attempt chronology, runtime debugging history, or discussion of why the null/supported results matter.

### 4.2 P1 — Mission-state dependence was not demonstrated on the predeclared primary outcomes

**Purpose:** Report the predeclared null result without rescue analysis.

**Claim ID:** C01.

**Must report:**

- P1 primary endpoints: M01, M02, M03, M06;
- applicable policy/mission contrasts and interactions were exactly `0`;
- P1 therefore was not supported on the predeclared primary outcomes.

**Recommended display:** compact row in `Table R1`; no dedicated figure is required unless the target journal strongly prefers a complete endpoint graphic.

**Keep out:** M07 as a substitute P1 endpoint, post-hoc alternative hypotheses, or language implying that mission state had no possible effect outside the tested design.

### 4.3 P2 — Modeled contact delay selectively affected the ground-authorized recovery path

**Purpose:** Present the strongest timing interaction with exact bounded language.

**Claim IDs:** C02–C07.

**Must report:**

#### M04 containment RMST

- P6 C1−C0: `+10.0831 s`, 95% CI `[9.8304, 10.3735]`;
- P7 C1−C0: `−0.0425 s`, 95% CI `[-0.1977, 0.0899]`;
- interaction: `+10.1256 s`, 95% CI `[9.7859, 10.5176]`.

#### M05 verified-recovery RMST

- P6 C1−C0: `+10.4246 s`, 95% CI `[9.6567, 11.3598]`;
- P7 C1−C0: `−0.1808 s`, 95% CI `[-0.7194, 0.2767]`;
- interaction: `+10.6054 s`, 95% CI `[9.5343, 11.9023]`.

#### M07 state-divergence duration

- P6 C1−C0: `+10.0676 s`, 95% CI `[9.8438, 10.3260]`;
- P7 C1−C0: `−0.0390 s`, 95% CI `[-0.1690, 0.0709]`;
- interaction: `+10.1066 s`, 95% CI `[9.8135, 10.4499]`.

**Required semantic note:** C1 is a modeled missed contact window. A16/A17 remain P6 cases; P6 waits for synthetic ground authorization before delegating the rollback action to the P5 mechanism.

**Recommended display:**

- `Table R2 — P2 contact-condition RMST/divergence contrasts`;
- `Figure R1 — Contact-condition effect plot` showing P6 and P7 C1−C0 estimates and 95% intervals for M04/M05/M07, plus interactions if visually legible.

**Keep out:** real ground-station/operator timing claims, universal P7 superiority, or relabeling P6 cells as P5.

### 4.4 P3 — Degraded policy-visible evidence created a recovery vulnerability for P7

**Purpose:** Show the recovery outcome change and preserve the distinction between the supported broader finding and the absent narrower anticipated mechanism.

**Claim IDs:** C08–C10.

**Must report:**

- A14 P5/T0 trusted recovery `30/30`;
- A15 P5/T1 trusted recovery `30/30`;
- A11 P7/T0 trusted recovery `30/30`;
- A13 P7/T1 trusted recovery `0/30`, recovery failed `30/30`;
- the narrower restoration-without-verification mechanism was not observed.

**Recommended display:**

- `Table R3 — P3/P4 evidence-condition outcome and selected-path summary`;
- `Figure R2 — Trusted-recovery outcome by policy and evidence condition`, using counts/proportions rather than decorative effect scoring.

**Optional supporting text:** M07 evidence-sensitive divergence may be reported as supporting timing evidence, provided it does not replace the terminal/recovery result.

**Keep out:** claims that all degraded evidence causes adaptive recovery failure or that fixed P5 is universally immune to evidence quality.

### 4.5 P4 — Degraded evidence changed actual policy/action selection and downstream consequences

**Purpose:** Separate observed selection mechanics from any unobserved correctness oracle.

**Claim IDs:** C11–C15.

**Must report:**

#### E1 pathway

- full-evidence P7: P2 / `RESTRICT_HIGH_RISK_COMMANDS`;
- degraded-evidence P7: P4 / `ENTER_SAFE_MODE`;
- M02 change `−0.5`;
- M06 change `+1.0`;
- no observed M03 safety-invariant violation or mission-loss event.

#### E3 pathway

- full-evidence P7: P5 verified rollback;
- degraded-evidence P7: `evidence_insufficient` basis → P2 restriction;
- trusted recovery `30/30 → 0/30`;
- recovery failure `0/30 → 30/30`;
- M02 change `−0.5`;
- no observed M03 safety-invariant violation or mission-loss event.

**Recommended display:**

- reuse `Table R3` for cell-level path/outcome summary;
- `Figure R3 — Evidence-to-selection-to-consequence pathway`, a simple deterministic flow diagram for E1 and E3. It must label `ENTER_SAFE_MODE` as an experimental modeled action, not native spacecraft safe mode.

**Keep out:** “correct/incorrect policy” labels, ground-truth-as-runtime-oracle language, or causal claims beyond the deterministic controlled pathway observed in the tested cells.

### 4.6 P5 — Mission-aware benefit was condition-specific rather than universal

**Purpose:** Present the multidimensional Pareto result without a global score.

**Claim IDs:** C16–C20.

**Must report:**

- P7 on the point-estimate Pareto front in `5/9` groups;
- P7 point-dominated in G04, G05, G06, G09;
- G01–G03 are primarily empirical ties/equivalence cases and must not be counted as adaptive wins;
- marginal intervals support comparator dominance in G04, G06, G09;
- marginal intervals support P7 dominance in G05 vs A10/P2, G07 vs A17/P6, and G08 vs A19/P0;
- G05 P7/A11 vs A14/P5 is point-estimate dominated through M05 (`3.9819393339 s` vs `3.8009359910 s`) but classified uncertain/tied under marginal intervals.

**Recommended display:**

- `Table R4 — Condition-specific P7 Pareto status and marginal uncertainty classification`;
- `Figure R4 — P7 condition-specific Pareto status matrix`, using categories such as P7-supported dominance, empirical tie/equivalence, comparator-supported dominance, and mixed/uncertain. A five-dimensional weighted projection is prohibited.

**Required note:** `5/9` is a front-membership count, not a success rate.

**Keep out:** weighted composites, an overall winner, rank ordering P0–P7, or simultaneous 95% dominance claims.

### 4.7 Robustness and execution-provenance sensitivity

**Purpose:** Demonstrate that the P5 structure is not an artifact of the ten VALID observations from the two earlier execution commits.

**Claim IDs:** C21–C23.

**Must report:**

- primary execution-provenance distribution: `1 / 9 / 710` VALID observations across commits A/B/C;
- completed E0 analytical-exchangeability classification;
- final-commit complete-block sensitivity: seeds `10002`–`10030`, `29` seeds / `696` observations;
- P7 front membership stable in all `9/9` groups;
- pairwise Pareto relations stable in all groups;
- primary-metric directions stable in all groups;
- sensitivity does not replace the 720-run primary population.

**Recommended display:** concise text in the main paper plus `Table S1 — Execution provenance and final-commit sensitivity` in supplementary material unless the target journal requests all robustness results in the main text.

**Keep out:** implying the first ten VALID observations are invalid or excluded, or stating all 720 runs used final commit C.

### 4.8 Results synopsis

**Purpose:** Close Results with a neutral factual synthesis before Discussion.

**Claim ID:** C25, constrained by all preceding rows.

**Recommended factual synthesis:**

- P1 was not supported on its predeclared primary outcomes;
- P2 showed a strong modeled contact-delay effect on the ground-authorized path but not the autonomous P7 path;
- P3 showed evidence-dependent P7 recovery vulnerability while the narrower anticipated mechanism was absent;
- P4 showed deterministic evidence-dependent selection/action changes with measurable downstream consequences;
- P5 showed conditional dominance, equivalence, and disadvantage rather than a universal policy winner.

This paragraph should not compare the findings with prior work; that begins the Discussion.

## Planned main-paper tables

### Table R1 — Frozen population and proposition outcome summary

Minimum columns:

- proposition;
- predeclared endpoint(s);
- analysis block/cells;
- principal result;
- frozen proposition status.

P1’s null result must appear with equal prominence to supported propositions.

### Table R2 — P2 timing contrasts

Minimum columns:

- endpoint;
- P6 C1−C0 estimate;
- P6 95% CI;
- P7 C1−C0 estimate;
- P7 95% CI;
- interaction estimate;
- interaction 95% CI.

Header/footnote must state modeled contact condition and `τ = 30 s` for M04/M05 RMST.

### Table R3 — P3/P4 evidence-condition outcomes and selection pathways

Minimum columns:

- event family;
- cell;
- evidence condition;
- requested policy;
- effective policy;
- selected action/basis;
- mission completion;
- trusted recovery count;
- recovery-failed count;
- legitimate-command rejection where applicable.

### Table R4 — P5 condition-specific Pareto findings

Minimum columns:

- group;
- condition;
- P7 cell/effective policy;
- point-estimate front status;
- comparator relation(s);
- marginal uncertainty classification;
- bounded interpretation.

No score, rank, or “wins” column is permitted.

## Planned main-paper figures

### Figure R1 — P2 modeled contact-delay effect plot

Forest/effect plot of C1−C0 estimates and 95% intervals for P6 and P7 on M04, M05, and M07. If interaction estimates are included, visually distinguish them without implying cross-endpoint pooling.

### Figure R2 — P3 evidence-dependent trusted recovery

Simple count/proportion display for A11/A13/A14/A15. The graphic must expose `30/30` and `0/30` directly and should avoid unnecessary smoothing or model-generated probabilities.

### Figure R3 — P4 selection/consequence pathways

Two-panel deterministic pathway diagram:

- E1: T0 P7→P2 restriction vs T1 P7→P4 `ENTER_SAFE_MODE`;
- E3: T0 P7→P5 rollback vs T1 `evidence_insufficient`→P2 restriction.

The figure caption must preserve experimental-action and correctness-oracle boundaries.

### Figure R4 — P5 condition-specific status matrix

Rows G01–G09; columns may show P7 effective policy, front membership, pairwise relation category, and uncertainty class. Use categorical status rather than dimensionality-reducing scores.

## Main text versus supplementary material

Recommended main text:

- all P1–P5 proposition outcomes;
- P2 quantitative timing contrasts;
- P3 exact recovery counts;
- P4 core selection/consequence transitions;
- P5 group-level status and supported pairwise comparisons;
- concise provenance sensitivity statement.

Recommended supplementary material:

- complete cell-level descriptive estimates;
- full pairwise P5 marginal interval table;
- execution-provenance detail;
- exact zero-event upper bounds and full M03 reporting;
- expanded analysis-artifact/checksum register;
- additional M07 diagnostics where they are supporting rather than central.

Moving material to the supplement must not be used to hide P1 null findings, P5 disadvantage groups, or P3’s absent narrower mechanism.

## Statistical presentation rules

- Report the seed-block bootstrap interval as a `95% CI` and identify the bootstrap unit as campaign seed where space allows.
- Do not invent p-values from intervals.
- For P5, state that the uncertainty classifications use marginal percentile intervals and do not constitute simultaneous confidence for the full five-dimensional Pareto relation.
- For M04/M05, state `RMST through 30 s` or `RMST, τ = 30 s`.
- Report M05 event/censor counts at least once in Methods or Results.
- Report structural-zero M03 as observed counts/appropriate bounds, not as evidence of guaranteed absence.
- Keep sign conventions explicit when reporting contrasts (`C1−C0`, `T1−T0`, or P7 benefit orientation).

## Drafting order

The safest manuscript drafting sequence is:

1. build Tables R1–R4 from frozen claims/artifacts;
2. build Figures R1–R4 from the same table values;
3. draft Sections 4.1–4.7 from the displays and claim IDs;
4. draft the neutral Section 4.8 synopsis;
5. run a quantitative trace audit against `docs/30-wp10-g1-claim-to-evidence-matrix.md`;
6. only then begin Discussion and literature reconciliation.

This order prevents prose from becoming the source of truth.

## G1 acceptance gate

WP10-G1 is complete when:

- the claim-to-evidence matrix is merged;
- this Results architecture is merged;
- every main Results subsection has explicit claim IDs;
- planned tables/figures do not introduce new estimands;
- null and unfavorable outcomes remain visible;
- no Results sentence requires literature interpretation to be scientifically meaningful;
- WP10 tracker state points next to G2 empirical reconciliation of WP1–WP3 and subsequent evidence-locked Results drafting.
