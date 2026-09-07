# Paper 3 / Study 7 — R2 Sections IV-VI Scientific Claim Audit

**Audit date:** 2026-09-07  
**Audited artifact:** `PAPER3_TECHNICAL_NOTE_DRAFT_R2_SECTIONS_IV_VI.md`  
**Status:** `PASS_WITH_ONE_PRECISION_CORRECTION__NO_NUMERICAL_DEFECT`

## 1. Block-A numerical audit

Frozen `policy_summary.csv`:

- D0: 256 observations; 0 objective-decision errors; 0 unsafe proceeds; 0 false-conservative holds; 3 proceed decisions.
- L0: 256 observations; 0 objective-decision errors; 0 unsafe proceeds; 0 false-conservative holds; 3 proceed decisions.

R2 reports these values exactly.

**Audit:** PASS.

The interpretation that L0 reproduces the full visible-state boundary is supported because all 256 eight-feature states are evaluated and L0 has zero error across the complete lattice.

## 2. Block-B numerical and row-level audit

Frozen `policy_summary.csv`:

- L1: 512 observations;
- 2 objective-decision errors;
- 1 unsafe proceed;
- 1 false-conservative hold;
- 6 proceed decisions.

R2 reports these values exactly.

The two error rows in the accepted `observations.csv` were checked directly:

1. all six evidence-quality bits = 1, `security_signal=1`, visible authorization = 0, corroboration = 1, hidden authorization = 0 -> L1 proceeds -> unsafe proceed = 1;
2. all six evidence-quality bits = 1, `security_signal=1`, visible authorization = 1, corroboration = 0, hidden authorization = 1 -> L1 holds -> false-conservative hold = 1.

R2 describes both rows correctly.

**Audit:** PASS.

## 3. Block-C row-level audit

All nine accepted Block-C rows were checked directly.

### SAFE_CORROBORATED

- eight base inputs all 1;
- hidden authorization = 1;
- L1 corroboration = 1;
- objective = proceed;
- D0/L0/L1 all proceed safely.

R2: exact.

### V5_INDEPENDENT_DISAGREEMENT

- eight base inputs all 1;
- visible authorization = 1;
- hidden authorization = 0;
- L1 corroboration = 0;
- objective = hold;
- D0 = unsafe proceed;
- L0 = unsafe proceed;
- L1 = hold, unsafe proceed 0.

R2: exact.

### V5_CORRELATED_FALSE_CORROBORATION

- eight base inputs all 1;
- visible authorization = 1;
- hidden authorization = 0;
- L1 corroboration = 1;
- objective = hold;
- D0/L0/L1 all proceed unsafely.

R2: exact.

**Audit:** PASS.

## 4. RQ answer audit

R2's two-part answer is supported:

- exact visible-rule learning does not resolve the hidden-truth collision when the visible inputs are identical;
- adding corroboration resolves the prespecified disagreement case but not the correlated-false-corroboration case.

The additional statement that the complete corroboration lattice exposes a safety/availability trade-off is supported by exactly one unsafe proceed and one false-conservative hold.

**Audit:** PASS.

## 5. Interpretation-boundary audit

R2 correctly avoids:

- percentages presented as operational error rates;
- confidence intervals or p-values;
- ML-superiority claims;
- certification claims;
- detector-performance claims;
- operational spacecraft or flight claims;
- pooling any earlier study population.

**Audit:** PASS.

## 6. Precision correction required

R2 states that the `independent_corroboration` variable "is independent by experimental construction." The protocol names the feature `independent_corroboration` and the prespecified disagreement case models a genuinely independent corroboration path, but the study does not empirically establish independence in a real mission architecture.

To eliminate any risk that the wording is read as operational validation, R2A must state:

> The corroboration input is designed to represent an independent evidence path in the prespecified model; its operational independence is an assumption of the modeled scenario, not an empirical finding.

This is a wording precision issue only. It does not change any result.

## 7. Limitation-language cleanup

R2 lists several unmodeled operational phenomena. To keep every negative claim tightly within the frozen protocol, R2A should group them more conservatively as:

- no operational spacecraft/RF validation;
- no stochastic learning;
- no continuous/noisy evidence model or distribution-shift experiment;
- no detector-performance evaluation;
- no empirically established mission-level corroboration independence.

This is editorial tightening, not a scientific correction.

## 8. Audit disposition

**Numerical integrity:** PASS.  
**Row-level fidelity:** PASS.  
**RQ answer:** PASS.  
**Claim boundary:** PASS after one corroboration-independence wording correction.  
**Scientific rerun required:** NO.  
**Result reanalysis required:** NO.

A corrected R2A may be created from the same frozen evidence. After R2A verification, Sections I-VI can be assembled into the first complete Technical Note draft for length/compression and title review.