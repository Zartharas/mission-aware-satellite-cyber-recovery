# Study 8 Companion Publication

**Experiment:** `S8-PQC-ICR-001`  
**Publication-development authorization:** `S8-PUBDEV-001`  
**Status:** `PHASE8_8_PUBLICATION_DEVELOPMENT_IN_PROGRESS_FROZEN_SCIENCE_ONLY`

## Working title

**Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems**

This directory develops a separate companion paper from the technically closed Study-8 evidence. It does not modify or pool the existing Study-1/Study-2 journal manuscript.

## Frozen scientific sources

- Canonical observations: `study8/results/S8-PQC-ICR-001/canonical_observations.csv`
- Canonical dataset SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- Statistical analysis plan: `study8/analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json`
- Primary findings: `study8/analysis/results/primary_findings.json`
- Primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- Interpretation audit: `study8/analysis/results/interpretation_audit.json`
- Interpretation-audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`
- Technical close: `study8/STUDY8_TECHNICAL_CLOSE.json`

The publication-development phase may project those frozen quantities into prose, tables, and figures. It may not recompute the canonical campaign, rerun the statistical analysis, change the findings, rescue the null primary contrast, or introduce sampling inference.

## Publication thesis

The manuscript is organized around three frozen results:

1. **Negative primary policy result:** all four policies restore modeled trust in `635/864` positions (`73.4954%`), and the prespecified P3-minus-P1 risk difference is exactly `0/1` (`0.000000` percentage points), including every prespecified regime/profile/disruption/deadline stratum.
2. **Cryptographic-object budget result:** marginal modeled success is `1080/1152` (`93.7500%`) for `PROFILE_512_44`, `748/1152` (`64.9306%`) for `PROFILE_768_65`, and `712/1152` (`61.8056%`) for `PROFILE_1024_87`; success is non-increasing with increasing frozen object budget in all `1152/1152` matched non-profile positions.
3. **State/resource tradeoff result:** policy changes logical availability, predecessor exposure, overlap, modeled bytes/contacts, transition attempts, and failure classification even though it does not change the primary success proportion.

## Claim boundary

Logical slots are ordering units with **no conversion to seconds, milliseconds, orbital time, or physical latency**. Byte values are NIST-standardized cryptographic-object sizes and modeled transition-object transfer only. The paper does not report measured spacecraft CPU, RF throughput, ground-station performance, energy, flight behavior, actual CCSDS framing overhead, or operational CCSDS approval of ML-KEM/ML-DSA.

`TRUST_RESTORED` is a modeled protocol state, not a claim that a real satellite or mission recovered.

## Development artifacts

- `manuscript/manuscript.md` — integrated article draft
- `references/references.bib` — Study-8-specific bibliography
- `tables/` — frozen-result publication tables
- `figures/` — frozen-result publication figures
- `claim-traceability.csv` — claim-to-evidence and overclaim-control register
- `venue-fit.md` — current venue assessment
- `author-submission-metadata.md` — author/declaration metadata for later venue adaptation
- `scripts/check_publication_projection.py` — publication projection validator; does not execute scientific analysis

## Publication gate

This phase authorizes development only. Publisher submission, final venue commitment, manuscript freeze, DOI/archive release, and any scientific re-execution remain separately gated.
