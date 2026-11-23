# Integrated Paper 5 manuscript candidate: Study 9 + Study 10

Status: **DRAFT / EDITORIAL_VALIDATION_IN_PROGRESS / NO_SUBMISSION**. Study 9 original author manuscript and both frozen scientific studies remain unmodified. This review branch is not merged or publication-approved.

## Identity and integration

- Study 9 (S9-RTSI-001) owns the existing Paper 5 study, its frozen three-dataset population and original RQ1-RQ4. The original source manuscript Git blob is `f8822caa7142b925ce80e26013013f055fa3e491`; its original bibliography Git blob is `3b640dc46f81dbb0e2ebebbff6e9dac7caad1411`.
- Study 10 (S10-RSEI-001) is a separate, later-frozen study included in this *post-results* integrated manuscript. Its four descriptive primary strata are ESA Anomaly Dataset v2 Missions 1/2/3 and OPSSAT-AD v2. ESA v1 is only an optional paired sensitivity comparator, not a fifth stratum.
- Both designs retain their own protocol and outcome definitions; no preregistered combined experiment or spacecraft recovery efficacy claim is made.

## Protected results

Study 9: 25,000 / 137,965 / 404,798 original source rows, 0/8 operational direct/derivable coverage per dataset, zero unique-action fraction for four frozen policies, minimum guaranteed policy-specific sidecar cardinalities 6, 7, 7, 8.

Study 10: 32 published-schema-level classification slots = 14 AMBIGUOUS plus 18 ABSENT; each descriptive stratum 0/8 direct/derivable; all 16 operational stratum-policy questions NOT_EVALUABLE. Synthetic G3: 18 cases, 22 repository tests, 1,024 independent-oracle comparisons. Optional matched ESA v1/v2 metadata: 224 matched channels, 896 shared-field cells, 842 equal/54 different (`Physical Unit` only); v2-only `Categorical` field for 224 channels. No nested telemetry inspected and no evidence of semantic unit conversion.

## Study 10 derived evidence archive

The subfolder `study10_derived/` contains exactly three author-uploaded derived JSON outputs and `README_MANIFEST.json` with original input SHA-256 hashes and provenance limits. No original dataset, telemetry sample, nested ZIP/pickle, unhashed channel identifier, or original ESA paired-detail CSV was uploaded. The local detail CSV remains excluded by author instruction. The archived Tier C JSON reflects its original pre-RQ-E3 snapshot; the separate later RQ-E3 aggregate JSON records completed paired sensitivity.

The author-terminal-reported ESA nested layout JSON has not been independently uploaded or rehashed. The original schema and boundary JSON sources were independently rehashed in earlier checkpoints. This difference in evidence provenance remains explicit.

## Source rights and publisher notices

- ESA v2 DOI 10.5281/zenodo.15237121 and v1 DOI 10.5281/zenodo.12528696: version-linked first-party evidence identifies CC BY 3.0 IGO; the legible v2 Zenodo Rights field is blank. This paper retains creator credit, license link, transformations/limitations and non-endorsement. Member-specific exception absence is not proven.
- OPSSAT-AD v2 DOI 10.5281/zenodo.15108715: versioned source `LICENSE` states MIT for software, data and documentation, copyright (c) 2024 KP Labs. The source DOI and full-license URL are credited; no original licensed content or substantial excerpt was reproduced.
- Original G4 Rights Standard R1 is conditional, not universal third-party permission or a license-clearance certificate. Final source-rights and publication notices still need author review.
- Separate associated OPS-SAT Scientific Data methods descriptor (2025, DOI 10.1038/s41597-025-05035-3) was added to the manuscript bibliography with correction DOI 10.1038/s41597-025-05751-w in the note.
- Original Study 9 eleven citations remain; three versioned datasets plus one associated methods reference have been added, making fifteen entries.

## Journal formatting and validation

Target venue candidate: *Cyber Security and Applications*; verify its live instructions again at final submission. Manuscript: LaTeX elsarticle class; abstract <=350 words; keywords 3-6; companion `CSA_S9_S10_INTEGRATED_HIGHLIGHTS.txt` contains five items <=85 characters (excluding bullet prefix).

The dedicated PR-only workflow `.github/workflows/paper5-s9-s10-draft-latex-ci.yml` compiles with `latexmk` and no shell escape, checks citations, and stores PDF/log as review artifacts. Earlier exact-head CI commit `52a810d3ed366c4d843ad0e5742bb33b7447da28` compiled 21 pages, zero overfull boxes and no unresolved references. The **newest editorial/archive revision requires a fresh exact-head CI pass** before claiming that result applies to it. The AegisSat proceedings source gives no confirmed conventional page interval; retain honest metadata rather than inventing pages to suppress BibTeX's nonfatal missing-pages warning.

## Publication gates

- Author to verify title, academic affiliation, corresponding email and ORCID, funding/conflicts, source-specific rights/credits, original research exclusivity, editorial statements and citations.
- Author to review the new integrated manuscript and its AI-assistance declaration before any submission.
- The non-raw G4 archive is presently a GitHub PR review-branch artifact, not a separately versioned stable data repository.
- G5, original-source redistribution, merging PR #255, journal submission and publication are **not authorized** by this editorial scope.
