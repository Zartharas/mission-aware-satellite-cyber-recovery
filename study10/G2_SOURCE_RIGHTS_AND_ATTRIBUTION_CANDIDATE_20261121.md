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

## Explicit stop rules / outstanding reviews

1. **HOLD:** ESA v2 release-specific rights/third-party scope, creator/contributor attribution format and permissions for intended derivative uses have not yet been formally signed off; exact creator names are now verified from the two Zenodo records.
2. **HOLD for any raw redistribution:** file-level license scope must be confirmed and all required notices attached. Do not commit raw ESA or OPS-SAT telemetry to this public repository.
3. If source rights are narrower than this candidate assumes, stop *before* examining new results; prepare a dated prospective exclusion or protocol amendment for separate author approval.
4. Source rights evidence does not establish operational recoverability, independent spacecraft observations, or review by external counsel.

**Sole-author rights sign-off:** `PENDING`. This document records notice obligations for G2 consideration only, not completed legal clearance or permission to begin data execution.
