# CEAS R5 reference verification ledger — 2026-10-09

Preserves the **original 20-entry** reference screen and its mapping to the **19-entry edited R5**. Evidence levels are explicitly listed; a resolved URL is **not** complete bibliographic verification. Original automated retraction screen reported zero results, but no independent current retraction check is claimed.

| Original | Current | Evidence/remaining caveat | Link |
|---:|---:|---|---|
| 1 | 1 | NDSS original proceedings, title/authors/DOI checked | https://www.ndss-symposium.org/ndss-paper/auto-draft-645/ |
| 2 | 2 | arXiv 2608.14532 indexed with five named authors; preprint | https://arxiv.org/abs/2608.14532 |
| 3 | 3 | Authors/title/2025 IEEE Aerospace Conference and DOI independently corroborated by author publication record, author-posted paper and proceedings table of contents; publisher-primary metadata/pagination check still required | https://curbo.space/publications/ |
| 4 | 4 | official SPARTA CM0044 item checked | https://sparta.aerospace.org/countermeasures/CM0044 |
| 5 | 5 | RFC Editor primary source, informational RFC 9334, DOI and author order verified | https://www.rfc-editor.org/info/rfc9334/ |
| 6 | removed | IETF Internet-Draft, May 5 2026; not finalized, publication reference removed | https://datatracker.ietf.org/doc/html/draft-ietf-rats-multi-verifier-00 |
| 7 | 6 | Author-hosted published journal PDF confirms Malkhi/Reiter, *Distributed Computing* 11, 203–213 (1998); DOI/title/issue independently corroborated by Reiter's publication list and Duke bibliographic record | https://doi.org/10.1007/s004460050050 |
| 8 | 7 | Springer publisher article independently rechecked: Alpos/Cachin/Tackmann/Zanolini, published online 28 May 2024, volume 37 pp. 247–277 (2024), DOI matches | https://link.springer.com/article/10.1007/s00446-024-00469-1 |
| 9 | 8 | arXiv 2603.23745 three authors verified via dblp; preprint | https://arxiv.org/abs/2603.23745 |
| 10 | 9 | USENIX primary: five authors, venue, 2019 pages 1393–1410 | https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias |
| 11 | 10 | TUF official v1.0.36 text identifies last-modified 5 Aug 2026; upstream specification GitHub Release v1.0.36 shows publication 10 Aug 2026; R5 reference uses release date, now corroborated | https://theupdateframework.github.io/specification/v1.0.36/ |
| 12 | 11 | SLSA v1.2 official source requirements | https://slsa.dev/spec/v1.2/source-requirements |
| 13 | 12 | SLSA v1.2 official Threats & mitigations page; heuristic title mismatch false alarm | https://slsa.dev/spec/v1.2/threats |
| 14 | 13 | ESA Zenodo v2 April 2025 DOI and authors verified; reuse/access check remains | https://zenodo.org/records/15237121 |
| 15 | 14 | arXiv preprint 2603.10388 verified; IEEE DOI and published pagination unresolved | https://arxiv.org/abs/2603.10388 |
| 16 | 15 | IEEE Xplore 27(1) pp 372–425, DOI verified | https://ieeexplore.ieee.org/abstract/document/10546924/authors |
| 17 | 16 | Aerospace 13(3) article 249 DOI verified via publisher | https://doi.org/10.3390/aerospace13030249 |
| 18 | 17 | NIST IR 8270 2023 authors/DOI verified | https://www.nist.gov/publications/introduction-cybersecurity-commercial-satellite-operations |
| 19 | 18 | SciTePress original conference vol 2 pages 133–140 DOI verified | https://www.scitepress.org/PublishedPapers/2025/131032/ |
| 20 | 19 | NASA Rev B primary PDF January 19 2024 verified | https://swehb.nasa.gov/spaces/SWEHBVD/pages/146540183/7.22+-+Space+Security+Best+Practices+Guide |

## Open gates

Confirm original [3] publisher-primary pagination and original [15] IEEE publisher bibliographic metadata; original [7] author/publisher-concordant reference and original [11] TUF version-release date now cross-checked; complete final 19-reference formatting and claim-support verification, including original [13] SLSA official content. Verify ESA data licensing and precise access for frozen and ignored artifacts. Preserve original R4 and TAES R10 unchanged. Do not record `bibliography_final_pass` until this work is completed.

## 2026-10-09 additional primary-source reconciliation (editorial only)

- **Current [6]** (original [7]): Author-hosted full published *Distributed Computing* paper (1998), and Michael Reiter's original publication record, confirm authors, title, 11(4), pages 203–213, and DOI 10.1007/s004460050050. This is a bibliographic cross-check only; Study-4 results and their trust assumptions are unchanged. Sources: https://users.ece.cmu.edu/~reiter/papers/1998/DC.pdf and https://reitermk.github.io/papers/byYear.html
- **Current [7]** (original [8]): Publisher record confirms 28 May 2024 online publication, volume 37, pages 247–277, and named authors. Source: https://link.springer.com/article/10.1007/s00446-024-00469-1
- **Current [10]** (original [11]): Versioned TUF official source header says last modified 5 August 2026, whereas upstream signed GitHub release v1.0.36 is dated 10 August 2026; the manuscript's **Aug. 10, 2026 release date is supported**. Sources: https://theupdateframework.github.io/specification/v1.0.36/ and https://github.com/theupdateframework/specification/releases
- **Current [3]** (original [3]): IEEE Aerospace Conference 2025 paper's authors/title/DOI independently corroborated by Curbo's publication list, author-posted full paper, ResearchGate DOI metadata and publisher proceedings table of contents. Still withhold full bibliographic completion until IEEE primary record/pagination are checked. Sources: https://curbo.space/publications/ , https://www.researchgate.net/publication/388733648_Testable_Cyber_Requirements_for_Space_Flight_Software , https://www.proceedings.com/content/081/081100webtoc.pdf

**Submission gate remains CLOSED:** these spot checks do not amount to all nineteen references' claim-to-source verification, retraction screening, DOI/style validation, source-license confirmation, or reviewer-access QA. Do not change original 20-entry screening counts or mark manual QA complete. No P2X reuse or study result mutation.

## 2026-10-09 continuing primary-origin review (not a complete manual bibliography certification)

Additional original publication pages inspected for current R5 references:

| Current R5 | Primary source examined | What is supported | Open caveat |
|---:|---|---|---|
| 1 | https://www.ndss-symposium.org/wp-content/uploads/spacesec26-55.pdf | NDSS SpaceSec 2026 proceedings PDF identifies Thummala/Rice/Falco, title, date and DOI | Final sentence-by-sentence claim alignment and current correction/retraction screen |
| 2 | https://arxiv.org/abs/2608.14532 | Original arXiv preprint confirms named authors and subject | Preprint/non-peer-reviewed status must remain explicit; journal reference policy review |
| 4 | https://sparta.aerospace.org/countermeasures/CM0044 | CM0044 is the official SPARTA Cyber-safe Mode countermeasure | Avoid treating countermeasure guidance as an observed experiment |
| 5 | https://www.rfc-editor.org/info/rfc9334/ | Published RFC 9334 author order and RATS evidence/appraisal architecture | Informational RFC; avoid implying Standards Track |
| 8 | https://arxiv.org/abs/2603.23745 | Original arXiv Space Fabric preprint and three authors | Preprint/non-peer-reviewed status and CEAS published-only bibliography policy review |
| 9 | https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias | Original USENIX title, five authors, proceedings pages 1393–1410 | Claim-context verification still required |
| 11 | https://slsa.dev/spec/v1.2/source-requirements | Approved SLSA v1.2 source-track requirements | Cite as specification, not as validation of Paper 2 compliance |
| 12 | https://slsa.dev/spec/v1.2/threats | Approved SLSA v1.2 threats and mitigations | Full claim-context verification still required |
| 13 | https://zenodo.org/records/15237121 | Original ESA dataset v2 record, publisher/creator identities, DOI and April 2025 date | Dataset distribution/reuse rights and source-derived trace access pending |
| 15 | https://ieeexplore.ieee.org/abstract/document/10546924/authors | IEEE original bibliographic page: title, DOI, vol. 27 no. 1, pp. 372–425 | Recheck cited claim against full work |
| 16 | https://www.mdpi.com/2226-4310/13/3/249 | Publisher version: *Aerospace* 13(3), 249 (2026), Wang et al. | Review article, not recovery-gate experimental validation |
| 17 | https://www.nist.gov/publications/introduction-cybersecurity-commercial-satellite-operations | NIST IR 8270, Scholl/Suloway, July 2023, DOI | Do not inflate general risk-management report into recovery experiment |
| 18 | https://www.scitepress.org/PublishedPapers/2025/131032/ | SciTePress original ICISSP 2025, authors, pp. 133–140, DOI | Related-work comparator; not direct equivalent of R5 gates |

**Unfinished source checks:** current [3] primary IEEE record pagination, current [14] IEEE primary author/title/pagination, current [19] NASA full document revision/date, final source-to-claim alignment for all references, two arXiv preprint publishing-status compliance, verified source-data reuse license, and independent current correction/retraction checks. Previously supported original [6], [7], [10] metadata notes remain in the preceding ledger entries. All substantive research claims, figures, numbers and study populations remain untouched; this is bibliography evidence only.

## 2026-10-10 focused original-record bibliography and data-licence crosscheck — open gates

- **[3]** Current author/title and IEEE 2025 Aerospace proceedings DOI `10.1109/AERO63441.2025.11068629` corroborated by the indexed IEEE DOI secondary entry (https://www.researchgate.net/publication/393690452_Testable_Cyber_Requirements_for_Space_Flight_Software). The older author preprint has a distinct ResearchGate DOI and is **not** proof of IEEE official `pp. 1–20`. **IEEE primary proceedings pagination and exact claim alignment still open.**
- **[14]** Original 2026 *Silent Subversion* arXiv abstract https://arxiv.org/abs/2603.10388 (Vanlyssel, Roman, Anwar) supports the scope of onboard component-origin false telemetry accepted by the ground station; secondary IEEE-proceedings entry https://eurekamag.com/research/107/646/107646176.php corroborates conference DOI `10.1109/AERO66936.2026.11519913`. **IEEE primary page extent and author-order/published-version metadata not independently confirmed.** A ten-page preprint does not establish the final IEEE page range.
- **[13]** Official ESA `esa/anomaly-dataset` GitHub `LICENSE` says **CC BY 3.0 IGO**, see https://github.com/esa/anomaly-dataset/blob/main/LICENSE and formal obligations https://creativecommons.org/licenses/by/3.0/igo/legalcode.en. Its own README references earlier Zenodo record `12528696`; CEAS R5 cites v2 record `15237121` (https://zenodo.org/records/15237121), whose crawled Rights/License field did not expose an explicit licence value. **Treat exact v2 data-license crosswalk and terms for derived 1,919-interval CSV as UNVERIFIED; do not equate accessible dataset bytes with authorized derivative redistribution.** CC licence attribution/change/no-endorsement obligations are potentially applicable only after the source/version rights are established.
- **CEAS** official author guide https://link.springer.com/journal/12567/submission-guidelines requires source data/code availability statements reflecting real access and terms; 19-item original-source claim-by-claim review is **not completed**. This ledger entry records a targeted check only; historical 20-entry automated screen remains a different scope.

No science claim, numerical result, reference metadata or manuscript bibliography entry has been silently changed by this licensing examination.

## 2026-10-10 primary-origin source-to-claim spot audit for all 19 references (not final bibliography certification)

Controlled Paper 2 R5 reference scope: 19 entries. Original publisher, standards author, government or dataset records were checked where accessible; separate preprint/secondary-only limitations are explicit. This table **does not certify** every manuscript assertion or reference formatting field, and does not supersede the preserved 20-entry earlier automated screening.

| R5 reference | Original or authoritative record | Verified audit class | Manuscript claim checked / supported | Outstanding limitation |
|---|---|---|---|---|
| [1] | NDSS 2026 SpaceSec PDF | PRIMARY_SOURCE_CLAIM_SPOT_CHECK | The spacecraft-specific communication gaps, lack of physical access, and mission-continuity constraints stated in Introduction/Related Work match the primary text. | Complete line-by-line context/corrections review pending |
| [2] | arXiv 2608.14532 | ORIGINAL_PREPRINT_CLAIM_SPOT_CHECK | Original authors and architectural cFS internal-trust boundary/legitimate privilege use align with manuscript. | Preprint only; final publication status and retraction review open |
| [3] | Curbo/Falco 2025 IEEE Aero | SECONDARY_METADATA__PRIMARY_BLOCKED | Authors/title/DOI 10.1109/AERO63441.2025.11068629 corroborated via author bibliography and indexed record; testable requirements claim plausible. | Official IEEE primary inaccessible to automated check; pp 1–20 and exact claim passage UNVERIFIED |
| [4] | SPARTA CM0044 cyber-safe mode | PRIMARY_SOURCE_CLAIM_SPOT_CHECK | Official cyber-safe-mode countermeasure explicitly calls for validated, protected recovery baseline. | Countermeasure guidance, NOT new spacecraft experiment; final full-source review pending |
| [5] | IETF RFC 9334 (RATS) | PRIMARY_SOURCE_CLAIM_SPOT_CHECK | RFC Section 10 explicitly discusses freshness, cached attestations, and race conditions after evidence creation; roles distinct. | Informational RFC; final full-source claim context open |
| [6] | Malkhi/Reiter Byzantine quorum systems | INSTITUTIONAL_METADATA_AND_ORIGINAL_AUTHOR_PAPER | Duke author institutional record corroborates 1998 Distributed Computing 11(4):203–213, DOI 10.1007/s004460050050. Original author's paper available at https://malkhi.com/files/byzquorums-STOC1997.pdf for conceptual consistency. | The author-hosted PDF is a different 1997 conference version; do NOT claim exact 1998 publisher PDF checked |
| [7] | Asymmetric distributed trust, Distributed Computing 2024 | PUBLISHER_SOURCE_CLAIM_SPOT_CHECK | Publisher paper 37:247–277 discusses asymmetric Byzantine quorum systems and consistency/availability assumptions. | No operational source independence inferred |
| [8] | Space Fabric, arXiv 2603.23745 | ORIGINAL_PREPRINT_CLAIM_SPOT_CHECK | Authors and Satellite Execution Assurance Protocol Byzantine endorsement quorum confirmed in original abstract. | Preprint, not peer-reviewed journal evidence; publication status pending |
| [9] | in-toto, USENIX Security 2019 | PUBLISHER_SOURCE_CLAIM_SPOT_CHECK | Author list and supply-chain cryptographic integrity mechanism supported by original conference page. | Precise page extent requires final bibliography sweep |
| [10] | TUF Specification v1.0.36 | OFFICIAL_STANDARD_CONTENT_CHECK | Official versioned spec describes signed metadata/update roles, expiry, hashes, threshold mechanisms. | Version release date originally corroborated separately; recheck release tag at final certification |
| [11] | SLSA Source v1.2 requirements | OFFICIAL_STANDARD_CONTENT_CHECK | Approved source-track requirements cover source history, provenance and controls. | No claim Paper 2 itself satisfies SLSA levels |
| [12] | SLSA Threats & Mitigations v1.2 | OFFICIAL_STANDARD_CONTENT_CHECK | Published threats text supports limits of build/source assurance. | No guarantee against malicious approved-source semantics |
| [13] | ESA Anomaly Dataset Zenodo v2 | ORIGINAL_DATASET_METADATA__RIGHTS_HOLD | v2, 2025-04-17, DOI 10.5281/zenodo.15237121, ESA publisher, Missions 1–3 dataset available. S3X uses Missions 1/2 timestamps as proxies only. | Exact v2 redistribution terms not displayed; NIH dataset catalog says rights information unavailable; do not release derived intervals |
| [14] | Silent Subversion IEEE Aero 2026 | ORIGINAL_PREPRINT_CLAIM_SPOT_CHECK__IEEE_FINAL_BLOCKED | Original authors/paper abstract confirms NASA NOS3 simulated compromised component produced legitimate-looking telemetry accepted by COSMOS ground software. | IEEE DOI 10.1109/AERO66936.2026.11519913 indexed elsewhere, but publisher pagination pp 1–10 UNVERIFIED |
| [15] | Salim/Moustafa/Reisslein satellite survey | PUBLISHER_METADATA_AND_ABSTRACT_CHECK | IEEE 27(1):372–425 (2025), DOI 10.1109/COMST.2024.3408277, surveys space/ground/link threats. | Review work, not the three frozen experiment results |
| [16] | Wang et al. satellite networks review | PUBLISHER_SOURCE_CLAIM_SPOT_CHECK | Aerospace 13(3):249 (2026), survey of satellite network threat/defense layers. | Review/survey, not empirical recovery-gate replication |
| [17] | NIST IR 8270 commercial satellite cybersecurity | GOVERNMENT_PRIMARY_METADATA_AND_SCOPE | Scholl/Suloway 2023 NIST IR 8270 addresses risk management for satellite operations. | Does not independently validate any Paper 2 finite-model outcome |
| [18] | ICISSP 2025 zero trust satellite controls | PUBLISHER_SOURCE_METADATA_AND_ABSTRACT_CHECK | Publisher confirms title, all four authors, pp 133–140, DOI 10.5220/0013103200003899. | Selected laboratory use cases are not an equivalence of R5 qualification gates |
| [19] | NASA Space Security Best Practices Guide Rev B | NASA_PRIMARY_REV_DATE_VERIFIED | Official NASA Rev B guide, issued 2024-01-19, covers mission security guidance including secure recovery. | Page-specific prevention/recovery wording and complete original-source citation audit pending |

### Original-source URLs mapped to the 19 entries

- [1] https://www.ndss-symposium.org/wp-content/uploads/spacesec26-55.pdf
- [2] https://arxiv.org/abs/2608.14532
- [3] https://ieeexplore.ieee.org/document/11068629
- [4] https://sparta.aerospace.org/countermeasures/CM0044
- [5] https://www.rfc-editor.org/info/rfc9334/
- [6] https://scholars.duke.edu/publication/1493996
- [7] https://link.springer.com/article/10.1007/s00446-024-00469-1
- [8] https://arxiv.org/abs/2603.23745
- [9] https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias
- [10] https://theupdateframework.github.io/specification/v1.0.36/
- [11] https://slsa.dev/spec/v1.2/source-requirements
- [12] https://slsa.dev/spec/v1.2/threats
- [13] https://zenodo.org/records/15237121
- [14] https://arxiv.org/abs/2603.10388
- [15] https://ieeexplore.ieee.org/abstract/document/10546924/citations
- [16] https://www.mdpi.com/2226-4310/13/3/249
- [17] https://www.nist.gov/publications/introduction-cybersecurity-commercial-satellite-operations
- [18] https://www.scitepress.org/PublishedPapers/2025/131032/
- [19] https://swehb.nasa.gov/spaces/SWEHBVD/pages/146540183/7.22+-+Space+Security+Best+Practices+Guide

### Release blockers and editorial safeguards

- **[3], [14]:** Do not certify 2025/2026 IEEE conference page ranges by applying preprint page counts or relying on index snippets. The official IEEE landing pages return a JavaScript/robot barrier in available tools. Obtain final IEEE publisher BibTeX/RIS or PDF from the author's lawful access, or omit unverified page ranges in a journal-compliant style after policy review.
- **[13]:** Original Zenodo record v2 has a Rights/License heading but no human-readable licence identifier in retrieved HTML. The U.S. NLM dataset catalog for DOI 10.5281/zenodo.15237121 explicitly states Rights: No information provided; contact repository owner (https://datasetcatalog.nlm.nih.gov/dataset?q=0002296812). Separate official ESA GitHub `LICENSE` has CC BY 3.0 IGO but its README links older record 12528696, so version-specific v2 terms remain unresolved. Do not assume original timestamp trace redistribution allowed solely from an open download.
- **Claim classification:** [1], [2], [4], [5], [7], [8], [9], [11], [12], [14], [16] have bounded source-content spot checks; [3], [6], [10], [13], [15], [17], [18], [19] have a mixture of metadata, defined scope, or original-revision checks. A full sentence-by-sentence claim-to-source audit, amendment/retraction check and consistent Springer bibliography format are still open.
- **Novelty boundary:** no source independently establishes that Paper 2's finite-model outputs, S3X external timing proxies, or S6X test fixture are an operational flight recovery demonstration; preserve frozen populations separately and do not misrepresent reviews/specifications as validating novel results.

Review performed through publicly accessible first-party pages and identified institutional indexes. Unavailable primary full text was not guessed or replaced. No manuscript numerical results, experiments, or bibliography entries were changed.

## 2026-10-10 independent indexed-citation and editorial-notice screen (19)

An additional **19-entry batch check** was performed using Scholar Sidekick's identifier/title matcher with correction/retraction screening enabled. Results: **14 matched / 1 apparent mismatch / 4 not found / 0 ambiguous / 0 errors / 0 reported retractions**. These are **database coverage and citation-identity signals**, not conclusive proof of all original-source facts, complete publisher metadata, or a universal absence of editorial notices.

| Reference | Batch verdict | Source-level adjudication |
|---|---|---|
| [1], [2], [3], [5], [6], [7], [8], [9], [13], [14], [15], [16], [17], [18] | MATCHED (14) | Identifier/title identity corroborated; the conference pagination and claim alignment holds [3]/[14] remain separately open. |
| [4] SPARTA CM0044 | NOT_FOUND | Non-journal, official dynamic online countermeasure; actual URL and content confirmed directly at https://sparta.aerospace.org/countermeasures/CM0044 . Do not call fabricated. |
| [10] TUF v1.0.36 | NOT_FOUND | Versioned project technical specification, https://theupdateframework.github.io/specification/v1.0.36/ ; not necessarily indexed as a scholarly DOI. |
| [11] SLSA Source v1.2 | NOT_FOUND | Official approved standards/specification document: https://slsa.dev/spec/v1.2/source-requirements . |
| [12] SLSA Threats & mitigations v1.2 | APPARENT MISMATCH | The title-only matcher linked an unrelated DOI 10.1201/9780429053603-4 (*Threat Mitigation*). This is **automated false association**, because the manuscript actually cites https://slsa.dev/spec/v1.2/threats and attributes it to SLSA v1.2; do not replace original source with the unrelated DOI. |
| [19] NASA Space Security guide Rev B | NOT_FOUND | Original NASA site and Rev B publicly released document verify this government guide. Not finding a journal DOI is expected for this technical guide and not evidence of fabrication. |

**Editorial notices:** no checked index entry returned a retraction flag. An index-negative result is NOT a guarantee that there is no notice or later correction; make a final publisher/author-page amendment check before journal submission. The original tracked 20-reference screening is preserved separately; this is a new 19-entry check against R5 bibliography. No manuscript reference numbers, URLs, research claims or frozen data have been changed.


## 2026-10-10 exact author-host Crossref + Zenodo API receipt (post-screen reconciliation)

The author uploaded `PAPER2_CEAS_METADATA_20261010T202420Z.json` from the approved metadata-only probe. Its **original bytes were independently rehashed**: **3,804 bytes**, SHA-256 `760c449e973334050a1bb8b4f98e740723c61d5a9f7a8f847dd8dae69bcd5065`; this **matches the author-host stdout**. Probe time `2026-10-10T20:24:20.124327+00:00`; two Crossref DOI records and one Zenodo record fetched, `errors={}`. It performed no experiment, git mutation, raw-telemetry download, external data release, or submission.

| Manuscript entry | Crossref publisher-deposited DOI metadata | Author/title and original bibliography comparison | Remaining claim gate |
|---|---|---|---|
| **[3]** Curbo and Falco | DOI `10.1109/aero63441.2025.11068629`; publisher IEEE; `2025 IEEE Aerospace Conference`; issued `2025-03-01`; `page=1-20` | James Curbo; Gregory Falco; *Testable Cyber Requirements for Space Flight Software*. Existing R5 `pp. 1–20` **EXACT MATCH to Crossref page field** | **CROSSREF BIBLIOGRAPHIC METADATA MATCH**; does **not** independently inspect IEEE publisher PDF or verify full text claim passage |
| **[14]** Vanlyssel, Roman and Anwar | DOI `10.1109/aero66936.2026.11519913`; publisher IEEE; `2026 IEEE Aerospace Conference`; issued `2026-03-07`; `page=1-10` | Jack Vanlyssel; Gruia-Catalin Roman; Afsah Anwar; *Silent Subversion: Sensor Spoofing Attacks via Supply Chain Implants in Satellite Systems*. Existing R5 `pp. 1–10` **EXACT MATCH to Crossref page field** | **CROSSREF BIBLIOGRAPHIC METADATA MATCH**; publisher PDF/claim-by-claim check still open |

Crossref's `page` field is **publisher-deposited bibliographic metadata**, not a page-number extracted from an independently reviewed final IEEE PDF. The long-standing [3]/[14] *metadata pagination discrepancy* is resolved at the Crossref level; **do not claim verified final-publisher PDF full-text or complete claim-level certification**. No reason to amend the already matching R5 reference entries.

**[13] ESA Anomaly Dataset:** Zenodo public REST record `15237121` confirmed DOI `10.5281/zenodo.15237121`, title *ESA Anomaly Dataset*, resource type `dataset`, publication date `2025-04-17`, `access_right=open`, while `metadata.license=null`, `metadata.rights=null` and `metadata.version=null`. The Zenodo human-readable landing page labels the record **v2**, which is **not** the same as having a nonnull API `version` field. `open` is an access condition, **not proof of adaptation or derivative redistribution rights**. The probe's `derived_data_redistribution_authorized=false` is a deliberately conservative **output-policy field** and is not evidence that a legal licence forbids all reuse. Direct source: https://zenodo.org/records/15237121 ; independent missing-rights index: https://datasetcatalog.nlm.nih.gov/dataset?q=0002296812 .

Official ESA repository `https://github.com/esa/anomaly-dataset/blob/main/LICENSE` identifies **CC BY 3.0 IGO** and README links the older `https://zenodo.org/records/12528696`; a separate ESA dataset Kaggle challenge page describes its challenge materials as CC BY 3.0 IGO (https://www.kaggle.com/c/esa-adb-challenge/). These signals strengthen the case for asking the data steward about v2 reuse, but **do not provide explicit version-specific terms for the S3X 1,919 derived intervals**, and the older dataset may have different file checksums. No data file was downloaded or inspected during this metadata probe.

**Disposition:** [3]/[14] **CROSSREF_PAGINATION_MATCHED** (upgrade from secondary/preprint page evidence); their IEEE original full-text checks remain open. [13] **ZENODO_V2_LICENSE_METADATA_ABSENT__DATA_RELEASE_HOLD**. The whole 19-entry reference-to-manuscript-claim review, publisher editorial-notice checks, ESA v2 rights crosswalk, reviewer evidence access and submission remain **NOT CERTIFIED**. No frozen science, tables, figures or manuscript references changed.
