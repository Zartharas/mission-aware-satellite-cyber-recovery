# TAES Paper 2 Figures and Tables Review

**Review date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Preferred manuscript commit:** `41a18e6e4cb8672645d7ebf018e6ff77c5bebf20`  
**Preferred assembled SHA-256:** `c49697da4f1f9225b078308107cbdbc260ce9110274919edd08d87419f5dc99c`  
**Scientific rerun authorized or required:** No  
**Current status:** `ACTIVE_DISPLAY_DESIGN_DECISIONS_RECORDED__FIGURE_1_CREATION_PENDING`

## 1. Review objective

This gate determines which displays belong in the TAES main paper and how they should be represented before two-column formatting. The review must improve readability without changing any frozen Study 3, Study 4, or Study 6 result.

IEEE Author Center guidance distinguishes the functions of tables and figures: tables are best when exact values matter, whereas figures are useful for trends or other visual relationships. IEEE graphics are normally sized to one-column or two-column width, with vector graphics preferred where possible. TAES requires a two-column, single-spaced manuscript for submission and page-length estimation.

Official sources reviewed:

- TAES Information for Authors: https://ieee-aess.org/publications/transactions-aes/author-information
- IEEE graphics guidance: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/
- IEEE resolution and size guidance: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/
- IEEE file formatting guidance: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/

## 2. Current display inventory

The compressed manuscript currently contains five tables and no figures.

### Table I. Study-specific realizations

Purpose:
- preserves the three-study separation;
- identifies each study's qualification layer, research-only adjudication variable, visible evidence, frozen population, and contact-model status.

Decision: **RETAIN IN MAIN PAPER.**

Rationale:
- this table is the most compact visual control against accidental pooling or contact-model leakage;
- exact population identities and the Study-3-only contact distinction matter;
- replacing it with prose would increase length and weaken scanability.

Expected formatting:
- likely two-column width because of six columns and long evidence descriptions;
- wording may be shortened during template formatting, but no field may be removed if that removal obscures population separation or the contact-model distinction.

### Table II. Selected Study-3 residual-boundary results

Purpose:
- preserves exact selected Study-3 values for persistent V5 under K0/K4, B2 structural-zero cells, and the truthful V0/K4/B0 cache boundary.

Decision: **RETAIN IN MAIN PAPER.**

Rationale:
- exact values are central to the temporal contribution;
- a chart would add visual interpolation without improving the interpretation of a small set of exact finite-model values;
- the table keeps the 46/46 trajectory counts and exact logical-time means explicit.

Mandatory retained entries include:
- persistent V5/K0 B0 and S1: 46/46, 122.500 logical s;
- persistent V5/K0 B2: 0/46, 0;
- persistent V5/K4 B0: 46/46, 55.326;
- persistent V5/K4 S1: 46/46, 49.022;
- persistent V5/K4 B2: 0/46, 0;
- truthful V0/K4/B0: 3/46, 0.326;
- truthful V0/K4 S1/B2 zero cells.

Expected formatting:
- likely two-column width because the interpretation column is scientifically useful and prevents overreading;
- no conversion of logical seconds to operational spacecraft time.

### Table III. Study-4 first and systematic failure thresholds

Purpose:
- reports the complete 18-rule frozen threshold map.

Decision: **RETAIN IN MAIN PAPER.**

Rationale:
- the complete threshold map is a core Study-4 contribution, not supplementary detail;
- exact first/systematic values matter more than a visual trend;
- keeping the null/equal-threshold rows in the main paper is necessary to prevent a monotonic provenance-benefit narrative.

Mandatory retained structure:
- all 18 rules from Q1_D1 through Q7_D3;
- separate unsafe-qualification and false-conservative columns;
- first/systematic notation retained or equivalently explained.

Expected formatting:
- trial both one-column and two-column placement in the TAES template;
- do not delete null rows merely to save space.

### Table IV. Study-6 residual incorrect states and benign assurance loss

Purpose:
- preserves both aggregate unsafe counts and residual-state identity for G0 through G5;
- preserves benign-loss counts 32/64, 48/64, 48/64, 56/64, 56/64, 63/64.

Decision: **RETAIN IN MAIN PAPER.**

Rationale:
- exact residual-state identity is scientifically essential because G3 and G4 have equal counts but different surviving states;
- a simple numeric plot would erase that distinction;
- the table directly supports the claim that APPROVED_BAD_SOURCE remains under G5.

Expected formatting:
- likely two-column width because of the residual-state column;
- abbreviations may be defined for display efficiency only if the mapping to the frozen state names remains explicit.

### Table V. Cross-study residual-boundary comparison

Purpose:
- qualitatively compares the three separately frozen studies across observed evidence, research-only truth, residual boundary, and effect of stronger composition.

Decision: **CONVERT TO FIGURE 1, THEN REMOVE TABLE V AFTER FIGURE QA.**

Rationale:
- unlike Tables I-IV, Table V is qualitative rather than a repository of exact numerical results;
- its six-column layout is poorly suited to the TAES two-column format;
- the cross-study mechanism is more naturally communicated visually.

## 3. Figure 1 design decision

### Figure 1 concept

Working caption:

`Fig. 1. Parallel residual trust boundaries across the three separately frozen studies. The panels summarize a qualitative manuscript-level synthesis only; no experimental data flow or integrated three-layer architecture connects Studies 3, 4, and 6.`

The figure must use **three parallel panels**, not a serial pipeline and not arrows from one study into another.

Required panel content:

#### Study 3: Temporal runtime evidence

Visible to gate:
- signature validity;
- freshness;
- received authorization evidence;
- contact-dependent record availability;
- security signal.

Research-only truth:
- hidden authorization truth.

Residual boundary:
- fresh valid evidence can remain false under compromised trusted-producer V5;
- truthful pre-onset cache can briefly lag a state change.

Composition effect:
- contact-aware restriction reduces selected K4 exposure but does not eliminate persistent V5 qualification for B0/S1.

#### Study 4: Producer composition

Visible to gate:
- signed producer claims;
- vote threshold;
- synthetic provenance-domain count.

Research-only truth:
- hidden authorization truth.

Residual boundary:
- same-size compromised subsets can differ in whether they satisfy the rule.

Composition effect:
- provenance requirements can delay systematic unsafe qualification while causing earlier false-conservative rejection for selected benign-loss subsets;
- null threshold effects remain part of the result.

#### Study 6: Recovery-artifact assurance

Visible to gate:
- signature;
- digest;
- provenance;
- reproduced-build match;
- source-review attestation;
- release approval.

Research-only truth:
- objective baseline correctness.

Residual boundary:
- APPROVED_BAD_SOURCE remains observationally qualified when all six visible signals are true.

Composition effect:
- additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss.

### Mandatory anti-overclaim labels

The figure must visibly state:

- `Three separately frozen experiments`;
- `Qualitative synthesis only`;
- `No pooled population`;
- `No experimental data flow between panels`.

The visual must not imply:

- an integrated recovery architecture;
- a causal sequence from Study 3 to Study 4 to Study 6;
- that Study 4 or Study 6 model intermittent contact;
- that the three populations share a common unit;
- that stronger composition is globally superior.

## 4. No additional result plots in this gate

Decision: **DO NOT ADD NUMERIC CHARTS FOR STUDIES 3, 4, OR 6 AT THIS STAGE.**

Rationale:
- the current exact tables communicate the registered finite values more faithfully;
- plotting finite threshold or state counts could encourage readers to infer continuity, probabilities, or operational rates that the studies do not estimate;
- additional figures would increase page burden without adding a distinct scientific result.

This decision can be revisited only if two-column formatting demonstrates that a specific table is materially less readable than a rigorously equivalent figure.

## 5. Supplementary-material implications

No current main-paper table is designated for supplementary-only relocation in this review.

Reasons:
- Table I is necessary for study separation;
- Table II carries the selected temporal result values;
- Table III is the complete central Study-4 threshold map;
- Table IV preserves Study-6 residual-state identity;
- Table V will be replaced by Figure 1 rather than moved to supplementary material.

The broader supplementary-material decision remains a separate mandatory gate. TAES states that supplementary materials intended to support review should be submitted with the original manuscript and referenced in the paper.

## 6. IEEE production controls for Figure 1

Preferred master format:
- vector PDF for the canonical figure master;
- a PNG preview may be retained for local inspection, but the vector PDF should be the primary submission-quality graphic.

IEEE guidance reviewed:
- vector graphics are preferred for scalable line art;
- typical display widths are 3.5 in for one column and 7.16 in for two columns;
- type should remain approximately 9-10 pt at final display size;
- graphics should remain interpretable without depending solely on color;
- accepted graphics formats include PDF, EPS, PS, PNG, and TIFF.

Figure 1 should be designed for two-column width because three parallel panels are unlikely to remain readable at one-column width.

## 7. Gate decision

Current figures/tables gate verdict:

`PASS_DISPLAY_INVENTORY_AND_DESIGN_DECISIONS__FIGURE_1_CREATION_AND_VISUAL_QA_PENDING`

Next required actions:

1. create Figure 1 from the approved parallel-panel specification;
2. visually inspect the figure at two-column width and grayscale-equivalent readability;
3. replace Table V with the figure reference/caption only after figure QA passes;
4. reassemble the manuscript;
5. verify that no scientific result or limitation changed;
6. then mark the figures/tables gate complete and proceed to TAES two-column formatting.

No portal submission is authorized by this review.