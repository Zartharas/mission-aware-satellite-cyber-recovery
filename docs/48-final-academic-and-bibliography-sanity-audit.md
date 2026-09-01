# Final Academic and Bibliography Sanity Audit

**Audit date:** 2026-08-31 (America/Chicago) / 2026-09-01 UTC  
**Audit baseline:** `a5cce8ad09ae6e3225e9dd253731a2298285b33c`  
**Scope:** manuscript-facing academic claims, bibliography metadata, submission guidance, and regression controls after the repository-wide technical hardening merge.  
**Scientific boundary:** no campaign runtime, seed consumption, evidence mutation, frozen result change, or new Study-1 statistical analysis.

## Outcome

The audit found no evidence that the frozen 720-observation Study-1 analysis population, proposition-level conclusions, provenance hashes, or Zenodo v1.0.0 evidence-of-record require scientific revision.

The audit did identify correctable academic/repository issues:

1. one NOS3 bibliography record contained an unrelated DOI and incorrect article metadata;
2. the ACM cyber-physical recovery survey had incorrect/incomplete author metadata;
3. the final Wanninger FDIR issue metadata had advanced beyond the earlier online-first description;
4. CuCD-ID had advanced from reviewed v2 to v3 with an explicit CC BY 4.0 license;
5. ESA Anomaly Dataset and OPSSAT-AD metadata could be made more faithful to their authoritative data-repository records;
6. the P5 provenance-sensitivity sentence could be misread as claiming P7 was on the Pareto front in 9/9 groups rather than that the membership/non-membership classification was unchanged in every group;
7. the P3 Results heading used `vulnerability`, a stronger security characterization than the controlled T1 omission/reduction manipulation itself establishes;
8. `post-publication reconstruction` could be misread as post-journal-publication rather than after campaign/Zenodo v1.0.0 publication and before journal submission;
9. the Introduction's `unresolved comparison problem` language was stronger than a finite literature review can establish globally;
10. the target-neutral keyword list contained 11 items, including platform names and more indexing terms than necessary for a conservative cross-guide submission set;
11. bibliography syntax/key checks could not detect a syntactically valid DOI attached to the wrong work.

These items were repaired on the academic-hardening branch without changing frozen scientific quantities.

## Bibliography verification method

The 31 active bibliography keys were reviewed by source class. Source priority was:

1. publisher/official publication page or DOI-registration-backed metadata;
2. official conference/proceedings page;
3. authoritative dataset repository;
4. NIST/agency/software project authority;
5. live SPARTA technique/countermeasure page;
6. author/institutional bibliographic page or established bibliographic index as corroboration.

Search-engine snippets and secondary aggregators were not treated as sole authority when a stronger source was available.

### Peer-reviewed and formal research records

| Key | Audit result | Authority used |
|---|---|---|
| `bakirtzis2026missionaware` | metadata/DOI consistent | DOI `10.1002/sys.70018`; institutional publication record |
| `thangavel2024trusted` | metadata/DOI consistent; complete seven-author list restored | Elsevier / Progress in Aerospace Sciences, DOI `10.1016/j.paerosci.2023.100960` |
| `wanninger2025fdir` | corrected to final issue metadata: vol. 18, pp. 991–1004, 2026 | Springer, DOI `10.1007/s12567-025-00651-6` |
| `geletko2019nos3` | **corrected** from unrelated Aerospace DOI/article to the peer-reviewed JoSS NOS3 case study, vol. 7(3), pp. 789–800, 2018 | Journal of Small Satellites issue record; NASA corroboration |
| `idan2025aegissat` | metadata/DOI consistent | official NDSS/SpaceSec 2025 program and paper, DOI `10.14722/spacesec.2025.23069` |
| `chan2026hades` | metadata/DOI consistent | ECCWS publisher page, DOI `10.34190/eccws.25.1.4647` |
| `lu2024attackrecovery` | **corrected** author metadata; journal issue/pages/DOI verified | Crossref-backed/author/DBLP records, DOI `10.1145/3653974` |
| `sarri2026juice` | metadata/DOI consistent; no speculative author-order change made | Springer, DOI `10.1007/s11214-026-01289-4` |
| `driouch2024cansatids` | metadata/DOI consistent | Elsevier / Computers & Security, DOI `10.1016/j.cose.2024.104033` |
| `casaril2024satcom` | metadata/DOI consistent | Elsevier / Computers & Security, DOI `10.1016/j.cose.2024.103799` |
| `casaril2026attack_surface` | metadata/DOI consistent | Elsevier / Computers & Security, DOI `10.1016/j.cose.2026.104848` |
| `dambrosio2025scass` | metadata/DOI consistent | Elsevier / Computers & Security, DOI `10.1016/j.cose.2025.104315` |

The internal citation keys `geletko2019nos3`, `wanninger2025fdir`, and `opssat_ad_2025` are retained for manuscript/history stability even though corrected reader-visible metadata uses different final publication years. BibTeX keys are internal identifiers and are not represented as bibliographic facts.

### Standards, guidance, software, and current technical sources

| Key/group | Audit result | Authority used |
|---|---|---|
| `nist800160v2r1` | title/authors/year/DOI consistent | NIST CSRC, DOI `10.6028/NIST.SP.800-160v2r1` |
| `nist800115` | title/authors/year/DOI consistent | NIST CSRC, DOI `10.6028/NIST.SP.800-115` |
| `nist80061r3` | final April 2025 status/title/authors/DOI consistent | NIST CSRC, DOI `10.6028/NIST.SP.800-61r3` |
| `nasa_nos3` | current repository title `NASA Operational Simulator for Space Systems (NOS3)` verified | NASA GitHub repository |
| `nasa_cfs` | current cFS repository identity verified | NASA GitHub repository |
| `chunawala2026satelliteir` | title/author/date/source consistent | AWS Public Sector Blog, 19 June 2026 |
| six SPARTA entries | identifiers/titles/current pages verified | live Aerospace Corporation SPARTA pages |

The historical JoSS article uses the older expansion `NASA Operational Simulator for Small Satellites`; the current NASA repository uses `NASA Operational Simulator for Space Systems`. Both are correct in their respective bibliographic contexts and must not be normalized into one another.

### Datasets and preprints

| Key | Audit result | Authority used |
|---|---|---|
| `esa_anomaly_2024` | publisher/version metadata strengthened | Zenodo record `10.5281/zenodo.12528696` |
| `opssat_ad_2025` | creator/year/version metadata strengthened to the authoritative dataset record | Zenodo record `10.5281/zenodo.15108715`, version v2 |
| `cucdid_2026` | **updated** to reviewed v3 DOI and license state | Mendeley Data `10.17632/7n2d42pm3n.3`, CC BY 4.0 |
| `liu2026temporal` | title/authors/arXiv identity consistent | arXiv `2608.20575` |
| `le2026tinyml` | title/authors/arXiv identity consistent | arXiv/DBLP `2606.05779` |
| `mattar2025spacecyber` | title/authors/arXiv identity consistent | arXiv `2509.05496` |

The externally screened AegisSat/CuCD-ID/telemetry datasets remain **contextual prior-art sources**, not statistical inputs to frozen Study 1. Updating a source's bibliographic/license metadata does not change Study-1 evidence membership.

## Manuscript semantic repairs

### P5 provenance sensitivity

The primary result remains unchanged: P7 is a point-estimate Pareto-front member in 5 of 9 frozen groups and point-dominated in 4 groups. The 696-observation final-execution-commit sensitivity did **not** turn this into 9/9 front membership. It preserved each group's membership/non-membership classification and pairwise relations.

The Results and WP10 artifact register now state this explicitly.

### P3 security language

T1 removed/reduced selected policy-visible evidence fields. It did not independently implement stale, forged, contradictory, or probabilistically corrupted evidence. The Results heading therefore now reports the observed fact—P7 recovery failure under degraded evidence in the tested block—rather than labeling the condition a general `vulnerability`.

### Reconstruction chronology

Where reviewer-facing/current documentation could be misread, reconstruction language now states that the executable WP10 reconstruction was prepared **after the campaign and Zenodo v1.0.0 publication, but before journal submission**. It remains explicitly distinct from unrecovered original WP10 executable analysis source.

### Novelty calibration

The Introduction now describes the controlled post-detection multi-policy comparison as `comparatively under-studied` rather than universally `unresolved`. This preserves the contribution while avoiding an absolute literature-absence claim that a finite search cannot prove.

### Keywords and highlights

The target-neutral keyword list was reduced from 11 to a conservative six-item set: `satellite cybersecurity`, `mission-aware cybersecurity`, `cyber resilience`, `trusted recovery`, `software-in-the-loop`, and `cyber incident response`. Platform names remain fully described and cited in the manuscript rather than occupying indexing slots. Six keywords are compatible with the accessible current Elsevier guidance surface that caps keywords at six and with the older Computers & Security author-information pack that requested 5–10; the exact live journal Guide/portal remains authoritative at export time.

The five Computers & Security highlights were separately checked against Elsevier's general highlights guidance: five bullets, each <=85 characters, with no internal P-codes or unexplained acronyms. No content change was required.

## Computers & Security scope and policy state

The current Elsevier shop text continues to position Computers & Security around leading-edge information-security research plus practical security guidance, and continues to display exclusions for cryptology as a principal component and a moratorium statement for AI/ML-significant submissions.

A live sanity check also found 2026 Computers & Security content involving AI/GenAI, including content labeled as a Full Length Article. This creates a policy-surface nuance that should not be resolved by speculation. The project therefore records both facts and treats the **submission-day journal Guide for Authors/Aims & Scope/editorial portal** as authoritative for current article-type/editorial rules.

This nuance does not alter the manuscript's scientific scope: Study 1's P7 is a frozen deterministic rule-based selector, not an AI/ML model. The separate use of generative AI in manuscript/reproducibility preparation is disclosed under Elsevier's author policy.

## Elsevier-wide checks retained for final export

Current Elsevier-wide pages verify that:

- academic-thesis publication is generally not treated as prior publication, subject to journal-specific exceptions;
- highlights are generally 3–5 bullets, <=85 characters including spaces, and should avoid jargon/acronyms;
- substantive generative-AI use in manuscript preparation requires a separate disclosure with tool/purpose/human oversight, while AI use in the research process belongs in Methods.

These general publisher facts do **not** replace the live Computers & Security portal/Guide for Authors check on the actual submission date.

## New regression protection

`scripts/audit_bibliography_metadata.py` now provides an offline fail-closed guard for:

- duplicate DOI values;
- the unrelated DOI formerly attached to the NOS3 case study;
- the superseded CuCD-ID v2 DOI;
- return of temporary bibliography notes;
- canonical metadata fragments for the records corrected during this audit.

The exhaustive GitHub Actions gate invokes this audit on every pull request and every push to `main`. The script intentionally makes no network requests and therefore does not claim to establish future publisher-page freshness.

## Scientific closeout statement

No change was made or authorized to the frozen 720 VALID observations, 9 retained INVALID attempts, campaign seeds, primary analysis membership, authoritative attempt ledger, frozen hashes, P1–P5 statistical estimates, P7 deterministic rule logic, 1/9/710 execution provenance, 696-observation sensitivity population, or Zenodo v1.0.0.

The next scientifically legitimate gate remains the **exact submission export**: assemble the files that will actually be uploaded, then rerun citation/reference, claim-to-frozen-result, scope, declaration, figure/table, and portal-policy checks against those exact files.
