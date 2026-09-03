# Study 8 Companion Publication

**Experiment:** `S8-PQC-ICR-001`  
**Publication-development authorization:** `S8-PUBDEV-001`  
**Publication-freeze authorization:** `S8-PUBFREEZE-001`  
**Current status:** `PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`

## Working title

**Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems**

This directory is the separate Study-8 companion-paper publication package. It does not modify, pool with, or silently extend the existing Study-1/Study-2 journal manuscript.

## Current publication-package closeout

The manuscript package was developed from frozen Study-8 evidence only, adversarially reviewed, and hash-frozen under `S8-PUBFREEZE-001`.

Publication package provenance:

- frozen-package commit: `cbad15227bf99d1b7b19d95b0581196d78208f95`
- final exact-content review head: `75c98356751087dd648684ade7cb973c166cbce0`
- publication-package PR: `#92`
- squash merge commit on `main`: `87bcec000d278aeffef1222ce814098c93ada362`
- post-merge Study-8 results-freeze run: `33781901833` — `SUCCESS`
- post-merge repository validation run: `33781901724` — `SUCCESS`

The authoritative current machine-readable state is [`PUBLICATION_DEVELOPMENT_STATUS.json`](PUBLICATION_DEVELOPMENT_STATUS.json). The historical Phase-8.9 freeze records intentionally retain the authorization state that existed before PR #92 was merged; they are provenance and are not the current merge state.

## Frozen scientific sources

- Canonical observations: `study8/results/S8-PQC-ICR-001/canonical_observations.csv`
- Canonical dataset SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- Statistical analysis plan: `study8/analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json`
- Primary findings: `study8/analysis/results/primary_findings.json`
- Primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- Interpretation audit: `study8/analysis/results/interpretation_audit.json`
- Interpretation-audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`
- Technical close: `study8/STUDY8_TECHNICAL_CLOSE.json`

The companion publication may project these frozen quantities into venue-formatted prose and submission materials. It may not recompute the canonical campaign, rerun the statistical analysis, change the findings, rescue the null primary contrast, or introduce sampling inference.

## Publication thesis

The manuscript is organized around three frozen results:

1. **Negative primary policy result:** all four policies restore modeled trust in `635/864` positions (`73.4954%`), and the prespecified P3-minus-P1 risk difference is exactly `0/1` (`0.000000` percentage points), including every prespecified regime/profile/disruption/deadline stratum.
2. **Cryptographic-object budget result:** marginal modeled success is `1080/1152` (`93.7500%`) for `PROFILE_512_44`, `748/1152` (`64.9306%`) for `PROFILE_768_65`, and `712/1152` (`61.8056%`) for `PROFILE_1024_87`; success is non-increasing with increasing frozen object budget in all `1152/1152` matched non-profile positions.
3. **State/resource tradeoff result:** policy changes logical availability, predecessor exposure, overlap, modeled bytes/contacts, transition attempts, and failure classification even though it does not change the primary success proportion.

## Claim boundary

Logical slots are ordering units with **no conversion to seconds, milliseconds, orbital time, or physical latency**. Byte values are NIST-standardized cryptographic-object sizes and modeled transition-object transfer only. The paper does not report measured spacecraft CPU, RF throughput, ground-station performance, energy, flight behavior, actual CCSDS framing overhead, or operational CCSDS approval of ML-KEM/ML-DSA.

`TRUST_RESTORED` is a modeled protocol state, not a claim that a real satellite or mission recovered. Same-repository independently written reproduction is not external laboratory or independent-human replication.

## Hash-frozen publication artifacts

The Phase-8.9 manifest binds exactly 11 publication artifacts:

- `manuscript/manuscript.md`
- `references/references.bib`
- `claim-traceability.csv`
- `author-submission-metadata.md`
- `tables/table-s8-1-design.csv`
- `tables/table-s8-2-primary-profile.csv`
- `tables/table-s8-3-p3-vs-p1-strata.csv`
- `tables/table-s8-4-policy-tradeoffs.csv`
- `figures/figure-s8-1-profile-success.svg`
- `figures/figure-s8-2-regime-success.svg`
- `FINAL_ADVERSARIAL_REVIEW.md`

See [`PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`](PUBLICATION_PACKAGE_FREEZE_MANIFEST.json) and [`SHA256SUMS.txt`](SHA256SUMS.txt). This repository-state closeout does not modify any of those 11 files.

## Other publication controls

- `venue-fit.md` — venue assessment; IEEE Systems Journal is the current shaping candidate, not a committed submission venue
- `literature-verification.md` — current literature/standards metadata verification record
- `scripts/check_publication_projection.py` — checks publication numbers against frozen findings without executing scientific analysis
- `scripts/check_publication_literature.py` — checks verified literature metadata
- `scripts/check_publication_freeze.py` — verifies the hash-frozen package and current merge state

## Next gate

The next gate is **venue-specific submission-package preparation**: choose/lock a venue, adapt formatting and submission materials to live venue requirements, and validate the exact venue package against the frozen manuscript/evidence boundaries.

Publisher submission, publisher-portal actions, scientific re-execution, statistical reanalysis, and frozen-science modification remain **not authorized**.
