# S10-RSEI-001 — G2 Source Rights and Attribution Candidate (NOT SIGNED OFF)

**Status:** `G2_NOTICE_AND_RIGHTS_CANDIDATE_NOT_FROZEN`. **Evidence basis:** G1 conditional author acceptance on PR #228 at `6cb2d1976f65cef0509329c59207b0e9d5c47681`, source rights file Git blob `2b94f9f4e1d8deba41bf99371fef0142bd7fcd37`. No original third-party data are copied here. This is not a legal opinion.

## Release-specific citation and rights commitments

| Role | Exact source identity | Source-specific rights evidence | Required before local source use or dissemination |
|---|---|---|---|
| Primary ESA-ADB v2, three anonymized missions | https://zenodo.org/records/15237121 — `10.5281/zenodo.15237121` | Authors' v2 manuscript identifies **CC BY 3.0 IGO**; the rendered Zenodo Rights field has not independently supplied an exact license value in this review | Before source-derived work, confirm exact v2-bundle grant and any per-file exceptions; cite v2 record and official contributor attribution. For shared derivatives, link license, mark transformations and avoid implying ESA endorsement |
| Paired ESA-ADB v1 sensitivity | https://zenodo.org/records/12528696 — `10.5281/zenodo.12528696` | Authors' 2024 paper identifies **CC BY 3.0 IGO** for this exact deposit | Preserve v1 citation/identity and authors; license link and modification notice; assess embedded third-party restrictions. Never call v1 an independent mission replicate |
| Primary OPS-SAT-AD **v2**, not v1 | https://zenodo.org/records/15108715 — `10.5281/zenodo.15108715` | Bundled `LICENSE` has the data-inclusive **MIT License for OPS-SAT Dataset**, copyright **2024 KP Labs**; v2 license MD5 matches upstream; user-local CSV checksums match v2 | Cite v2 data DOI and related article/correction as applicable; include complete MIT copyright and permission notice with substantial redistribution; verify any distinct third-party rights. This research-prep phase does not authorize dataset redistribution |
| Secondary Hack-A-Sat 4 contest context | `cromulencellc/hackasat-finals-2023` commit `2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1` | General repo MIT notice with **component-level exceptions**; game scoring input provenance only | No assumption of spacecraft-flight origin; examine path and embedded tar-member licenses before any reuse. Keep completely unpooled. |
| NASA SMAP/MSL | Deferred | Not in this candidate population | Requires new prospective authorization and population amendment before inclusion |

### ESA-ADB exact record creator/contributor attribution (official Zenodo metadata reviewed)

**Record creators on both v1 `12528696` and v2 `15237121`:**
1. Gabriele De Canio (contact; ESA/ESOC)
2. Krzysztof Kotowski (KP Labs)
3. Christoph Haskamp (Airbus, Germany)

**Additional named research contributors on both records:** Jacek Andrzejewski, Bogdan Ruszczak, Jakub Nalepa, Daniel Lakey, Peter Collins, Aybike Kolmas, Mauro Bartesaghi, and Jose Martínez-Heras.

The two official records both identify **European Space Agency** as publisher and list the contributor groups separately from the **three creators**. Cite the exact dataset DOI/version and give creators the dataset-author credit according to the eventual venue style; do not automatically insert all contributors into the byline or omit required acknowledgments. These exact names came from https://zenodo.org/records/12528696 and https://zenodo.org/records/15237121 as publicly rendered on the 2026-11-21 review. The **Rights > License** headings still did not expose a specific license value in the rendered landing-page text. The CC BY 3.0 IGO evidence continues to rest on the authors' publication statements and should not be misrepresented as directly visible metadata.

**Attribution/citation draft, not final venue formatting:** De Canio, G.; Kotowski, K.; Haskamp, C. *ESA Anomaly Dataset* [dataset], European Space Agency, **v2 (2025)** DOI: https://doi.org/10.5281/zenodo.15237121. A separate citation to the **v1 (2024)** DOI must be used for the paired-sensitivity source. Verify preferred Zenodo citation export and journal style before release. OPS-SAT v2 notice must retain the data-inclusive MIT copyright terms when required.

**Supporting publication/license references:** https://arxiv.org/pdf/2406.17826; https://openreview.net/pdf/eda113f9ebd4aa45678a791e19b33c8bdefd0e15.pdf; https://github.com/kplabs-pl/OPS-SAT-AD/blob/main/LICENSE; https://creativecommons.org/licenses/by/3.0/igo/.

## Prior release-identity evidence, not new checks

- ESA-ADB v1/v2: six versioned mission ZIPs matched reported official MD5 identifiers and author-reported local SHA-256s; **outer ZIP-directory metadata inspected only**, not exhaustive inner telemetry validation. Exact identities are in the companion manifest.
- OPS-SAT-AD v2: local `dataset.csv` MD5 `5246fdc5e4630a4cecbf7fb6bc8b795e`; `segments.csv` MD5 `72f109630abb933a386106897a631188`; both matched v2 and prior reported SHA-256s. The JSON terminal report and original files were **not** independently rehashed in this GitHub-preparation step.
- OPS-SAT v1 Zenodo record `12588359` is a **different release** and is not the selected primary source. A third-party CC BY 4.0 claim for v1 does not relicense v2.
- The original source intake reports a **source article inconsistency** in OPS-SAT training count: article 1,494 versus data/component count 1,594. Record this as a pre-existing source discrepancy; do not silently substitute either in outcome computation.

## First-party ESA license reconciliation (2026-11-22 UTC; document-level evidence)

**Distinct evidence for v1 and v2 must not be conflated.**

- **ESA v1, exact source line:** The ESA-owned public repository `https://github.com/esa/anomaly-dataset`, pinned at Git commit `a969698e464788c961dbb646d3da24595c7c7a2b`, contains a standalone `LICENSE` with exactly `CC BY 3.0 IGO` and the official legal-code URL `https://creativecommons.org/licenses/by/3.0/igo/legalcode.en` (Git blob SHA-1 `e9603f00725a6580a4c82ac6ada160a13f53f323`). Its `README.md` (Git blob SHA-1 `76f66a4550d0d8d3910b595d1c968bde9bbabed6`) expressly links dataset DOI `10.5281/zenodo.12528696`. This is **first-party dataset-project licensing evidence**, considerably stronger than inferring rights from a separate benchmark software MIT license. It does not prove that every file in the linked Zenodo archive lacks third-party restrictions.
- **ESA v2, exact release line:** In their author-authored manuscript `https://openreview.net/pdf/eda113f9ebd4aa45678a791e19b33c8bdefd0e15.pdf`, the authors explicitly identify newly introduced dataset record `15237121` and state in the asset-license disclosure (Appendix/reproducibility questionnaire, lines 755–758) that the **dataset is distributed under CC BY 3.0 IGO** while benchmark **code is MIT**. This is a direct author statement for the v2 source line, not a license inferred from v1. The public v2 Zenodo record `https://zenodo.org/records/15237121` still displays a Rights/License heading without the license name in rendered text. Therefore **author-stated v2 dataset license evidence = AFFIRMATIVE** and **independently identified v2 record Rights-field value = UNRESOLVED**; these are different facts.
- **License terms:** The official deed `https://creativecommons.org/licenses/by/3.0/igo/` permits sharing and adaptation of the **licensed** work with credit, license link and modification notice, without suggesting licensor endorsement; its legal code governs. Separate third-party rights are not magically licensed through the dataset statement. The Zenodo site-wide CC BY 4.0 default is **not** the exact dataset's rights grant, and the MIT license of `kplabs-pl/ESA-ADB` applies to its **software**, not automatically to ESA telemetry.
- **Result:** `ESA_V1_FIRST_PARTY_CC_BY_3_0_IGO_LICENSE_FILE_PASSED`; `ESA_V2_AUTHOR_ASSERTED_CC_BY_3_0_IGO_EXACT_RELEASE_EVIDENCE_PASSED`; `ESA_V2_ZENODO_RIGHTS_FIELD_NOT_RESOLVED`; `FINAL_AUTHOR_SCOPE_AND_REUSE_SIGNOFF_PENDING`. Do not convert this evidence into a statement that an attorney, ESA rights-holder or author has independently cleared all embedded material.

## OPS-SAT v2 record citation and use notice (proposed, not published)

The versioned `https://zenodo.org/records/15108715` record identifies its dataset creator as **Bogdan Ruszczak** (rendered `Bogdan, Ruszczak`) and lists research contributors **Bogdan Ruszczak, Krzysztof Kotowski, David Evans, and Jakub Nalepa**; it links the exact CSVs, notebooks and LICENSE. The upstream Git `kplabs-pl/OPS-SAT-AD` `LICENSE` file (blob SHA-1 `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`) explicitly licenses **software, data and associated documentation** under **MIT License for OPS-SAT Dataset**, copyright 2024 KP Labs. Its license MD5 `ea8befa9af2b37b7a54b5a16fc3712b0` matches the exact Zenodo v2 LICENSE listing. This is specific to v2; do not substitute v1 rights claims.

**Proposed dataset attribution, pending style review:** Ruszczak, B. *OPSSAT-AD - anomaly detection dataset for satellite telemetry* (version v2) [dataset], Zenodo. `https://doi.org/10.5281/zenodo.15108715`. Also cite the related research paper and correction when relevant. License/notice: `MIT License for OPS-SAT Dataset; Copyright (c) 2024 KP Labs`; where data or substantial portions are reproduced, retain the **complete** permission/copyright notice rather than citing this shorthand. Creator credit does not automatically make all dataset contributors co-authors of the underlying data record.

## Intended-use rights decision matrix (candidate only)

| Planned operation | Evidence and default constraint | This G2 review's permission status |
|---|---|---|
| G2 source-citation, published DOI, creators and README/license **metadata only** | Official Zenodo metadata reusable; no telemetry payload or adaptation is committed | `DOCUMENTATION_ALLOWED_CURRENT_SCOPE` |
| G3 synthetic fixture and technical selector parity, **without actual third-party dataset bytes** | No ESA/OPS rights need be implied by a fully invented synthetic fixture; later scientific-execution authorization still required | `FUTURE_SEPARATE_G3_AUTHORIZATION_REQUIRED` |
| G4/G5 local ESA v2 or OPS-SAT source processing and publication of source-derived **semantic matrices or statistics** | Author CC BY 3.0 IGO / dataset-specific MIT grants are affirmative evidence; keep versioned attribution, retain modifications and third-party exception checks; apply G4 scientific authorization separately | `HOLD_PENDING_AUTHOR_SOURCE_SCOPE_SIGNOFF_AND_G4_AUTHORIZATION` |
| G4 secondary Hack-A-Sat competition file processing | Path-level license exceptions and flight provenance not established; never pool with ESA/OPS populations | `SECONDARY_USE_BLOCKED_PENDING_FILE_RIGHTS_REVIEW` |
| Uploading/copying raw ESA or OPS-SAT datasets into a public repo or journal supplement | Requires all applicable grants/notices and distinct public redistribution approval, not merely G1/G2 document permission | `NOT_AUTHORIZED` |
| Claiming author/ESA endorsement or verified security recovery | None of the source licenses confers endorsement or validates native recovery states | `PROHIBITED` |

**Freeze policy choice for the sole author (not selected here):** A future G2 freeze could define the study's **prospective design** while retaining hard pre-G4 source-access/license exceptions as execution stop rules, **only if the author explicitly approves that separation**; alternatively, keep the G2 freeze itself on HOLD until each scope question is fully resolved. This candidate does not silently change the original conservative G2 preconditions. No freeze choice or source-use signoff is recorded in this review.

## Explicit stop rules / outstanding reviews

1. **HOLD:** ESA v2 release-specific rights/third-party scope, creator/contributor attribution format and permissions for intended derivative uses have not yet been formally signed off; exact creator names are now verified from the two Zenodo records.
2. **HOLD for any raw redistribution:** file-level license scope must be confirmed and all required notices attached. Do not commit raw ESA or OPS-SAT telemetry to this public repository.
3. If source rights are narrower than this candidate assumes, stop *before* examining new results; prepare a dated prospective exclusion or protocol amendment for separate author approval.
4. Source rights evidence does not establish operational recoverability, independent spacecraft observations, or review by external counsel.

**Sole-author rights sign-off:** `PENDING`. This document records notice obligations for G2 consideration only, not completed legal clearance or permission to begin data execution.
