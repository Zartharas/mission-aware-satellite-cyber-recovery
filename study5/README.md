# Study 5 — CuCD-ID cross-testbed portability

**Experiment:** `S5-CUCD-001`  
**Current status:** `CANONICAL_RESULTS_FROZEN_MERGED`  
**Canonical results merge:** PR #83 / `6415a391dc2337c51ce72442ac7d86a25b4fbc02`  
**Validated canonical head:** `9149ea900a6681ff55cd5c702f6194d50bb0e89d`  
**Dedicated validation:** run `33663897775` — PASS  
**Repository validation:** run `33663897772` — PASS  
**Independent audit mismatches:** 0  
**Frozen portability population:** 80 deterministic context × policy decisions; 8 input-sufficiency rows; 5 transferability rows.  

The stage-local status inside `results/RESULTS_FREEZE.json` records the pre-merge freeze gate and is preserved as historical provenance. This README is the current repository-status surface.

## Purpose

This study asks whether the externally published CuCD-ID NOS3/cFS intrusion-detection dataset can validly exercise the repository's frozen trusted-recovery selectors.

The answer is tested in two layers:

1. **Input sufficiency and taxonomy transferability.** The published CuCD-ID schema/labels are compared with the eight inputs required by the frozen Study-2 selectors. Missing mission, authorization, signature/trust, freshness, epoch, contradiction, and evidence-completeness state is never imputed from packet features.
2. **Oracle-alarm response portability.** The external scenario label is used only as an offline alarm oracle (`NORMAL` = no security signal; four attack labels = security signal). That alarm is crossed with four controlled recovery-evidence contexts and the four frozen Study-2 baseline policies, yielding 80 deterministic decisions.

## External source

CuCD-ID Version 3: DOI `10.17632/7n2d42pm3n.3`; published data article DOI `10.1016/j.dib.2026.112598`. The source manifest records the published v3 file hashes, class counts, label schema, SPARTA relationships, and CC BY 4.0 dataset-license status already reconciled in the repository.

Raw third-party dataset files are **not committed**. Study 5 intentionally does not perform a row-level policy benchmark because CuCD-ID packet rows do not contain the recovery-policy prerequisites needed to do so without fabrication.

## Claim boundary

Study 5 can support claims about:

- cross-testbed scenario/taxonomy coverage;
- whether the external dataset schema is sufficient for direct trusted-recovery policy execution;
- deterministic response-policy portability when an external scenario label is supplied as an offline alarm oracle.

It cannot support claims about:

- CuCD-ID intrusion-detection accuracy, recall, or false-positive rate;
- P0-P7 or Study-2 policy performance on individual CuCD-ID packet rows;
- operational attack prevalence;
- operational spacecraft, RF, or flight assurance.

Studies 1–4 remain frozen and are not pooled with Study 5.
