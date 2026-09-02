# Study 5 — CuCD-ID cross-testbed portability

**Experiment:** `S5-CUCD-001`  
**Status:** design freeze candidate; no canonical result is claimed until the dedicated and repository-wide gates pass.

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
