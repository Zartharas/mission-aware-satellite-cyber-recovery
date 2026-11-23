# Study 10 — G4-01 ESA Anomaly Dataset v2 source-rights scope decision candidate

**State:** `ESA_V2_DATASET_CC_BY_3_0_IGO_STRONGLY_CORROBORATED; RELEASE_LEVEL_SCOPE_CLARIFICATION_PENDING; G4_01_HOLD`

**Scope:** First of three source-rights decisions, for ESA Anomaly Dataset **v2 only**. This is a documentary rights assessment, not a copyright grant, source execution authorization, manuscript submission, or PR merge. No original satellite telemetry was read or uploaded.

## Source identity and study role

- Record: https://zenodo.org/records/15237121
- Exact DOI: `10.5281/zenodo.15237121`, published **April 17, 2025**, version **v2**
- Creators: **Gabriele De Canio, Krzysztof Kotowski, Christoph Haskamp**
- Publisher: **European Space Agency (ESA)**
- Three exact original archive names, MD5 values:
  - `ESA-Mission1.zip`: `9770ad12ed730238f37c42d5c27ab436`
  - `ESA-Mission2.zip`: `bfc72012691427d9327eb41f726ce45e`
  - `ESA-Mission3.zip`: `d63943f09c81378acd9fc5e565ecc66e`
- Planned role under frozen G2: **three descriptive strata**, not three independent replicated clinical/engineering evaluations; no pooled independent-spacecraft inference; no original telemetry redistribution.
- No new original dataset scan is requested or performed under this candidate decision.

## A. Verified affirmative license evidence

1. **Dataset authors' direct public paper statement**, `https://openreview.net/pdf/eda113f9ebd4aa45678a791e19b33c8bdefd0e15.pdf`, section **NeurIPS paper checklist, “Licenses for existing assets”**, printed page 17: the authors expressly say the dataset introduced is released as **CC BY 3.0 IGO**, while **benchmark code is MIT**. The opening/abstract expressly links the introduced dataset to `zenodo.org/records/15237121`. This is a dataset-level license declaration by source authors, rather than an inference from benchmark software licensing. The paper is a publicly accessible preprint; it is **not** a signed license specific to every archived member.
2. **Version-specific Croissant machine-readable dataset metadata** in project-maintained `kplabs-pl/ESA-ADB`, `data/preprocessed/esa-anomaly-dataset-metadata.json`, Git blob SHA-1 `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`: declares `Attribution 3.0 IGO (CC BY 3.0 IGO)` and points to `zenodo.org/records/15237121` and the **exact three v2 archive URLs and MD5 values**. This is stronger than an unversioned license claim. Its internal Croissant `version=1` and `datePublished=2024-06-25` refer to metadata history and **must not be mistaken** for the official v2 Zenodo version/date.
3. **ESA project repository v1 LICENSE**, `esa/anomaly-dataset` pinned `a969698e464788c961dbb646d3da24595c7c7a2b`, Git blob SHA-1 `e9603f00725a6580a4c82ac6ada160a13f53f323`, names CC BY 3.0 IGO. Its README links specifically to ESA **v1** (DOI `10.5281/zenodo.12528696`). This corroborates project licensing practice; it is not independently proof of all v2 members.

## B. Negative evidence and remaining ambiguity

- **Zenodo v2 Rights license value absent in rendered record**, despite the record being labelled `Open`. Zenodo's own FAQ says record permissions depend on record license and are normally shown in the Rights panel; the “Open” badge is not a substitute for a license.
- **Author-reported G4 metadata checks:** nine-file integrity passed within defined scope, six ESA outer directories examined, **2,090 nested ZIP directories** examined, **zero matching license-marker filenames**, zero errors, zero deeper nested ZIPs. Source hashes and report hash were reported from the author's Mac; original report/source bytes were not independently read in this review. `Study10_G4_Nested_License_Markers_Only.json` reported SHA-256: `b9486430f6a2c25384d105fe96296411df4b2e4526a6d0e759a8c960e3b28584`.
- Zero matching filename markers **does not establish** the absence of in-band rights notices, bespoke contractual/operational/security conditions, separately held intellectual property, or unadvertised exceptions.
- Authors assert dataset originated from ESA internal data, but the direct paper statement and public source metadata are **not identical to explicit confirmation that every member of the three v2 archives carries that same permission without exception**.
- The license text of CC BY 3.0 IGO (https://creativecommons.org/licenses/by/3.0/igo/legalcode.en) covers applicable authorized reuse/adaptation and conditions including attribution, license link, marking changes, preserving notices, avoiding implied endorsement; it does not automatically confer rights not held by the licensor.

## C. Rights decision recommendation, without silent clearance

**Recommended documentary conclusion:** `ESA_V2_DATASET_LEVEL_LICENSE_CC_BY_3_0_IGO_SUPPORTED_BY_TWO_DIRECT_VERSION_LINKED_FIRST_PARTY_SOURCES`.

**Governance decision:** `G4-01 = HOLD_PENDING_SCOPE_CONFIRMATION_AND_AUTHOR_FINAL_SIGNOFF`; **do not claim “third-party embedded exceptions have been cleared.”** Strong evidence supports a local-attributed, non-redistributing academic research-use scenario *if the documented license covers the intended files*. The frozen G2 policy still requires a separately recorded source-use rights decision. The permitted directory-only scan did not fully resolve embedded rights.

**Minimum focused clarification to the v2 dataset's identified contact author**, if the sole author explicitly authorizes external correspondence:
- Does **CC BY 3.0 IGO** apply to the **three exact v2 ZIPs** at DOI `10.5281/zenodo.15237121`, including telemetry channel samples, event/label/annotation CSVs and metadata?
- Are there any **member-level third-party license exceptions, special attribution requirements, contractual limitations, or operational restrictions** relevant to local noncommercial academic research and publication of non-raw aggregate derived results?
- The v2 Zenodo Rights panel displays a license heading with no value. Is this only missing metadata, and should the record specify CC BY 3.0 IGO (or another version-specific license)?

This is a narrow clarification request, **not** a request for special permission to publish raw telemetry, endorse the study, or authorize active spacecraft operations. No email has been sent and no rights-holder has been contacted.

## D. Unchanged guards and next evidence

- **G4-01:** HOLD until source-scope decision and final sole-author signoff.
- **G4-02:** HOLD_IF_USED; ESA v1 optional paired sensitivity **not adjudicated here**.
- **G4-03:** HOLD; OPS-SAT v2 MIT notices/CSV exceptions **not adjudicated here**.
- **G4-04:** Excluded (Hack-A-Sat 4).
- **G4-05:** Partial only (identity/inventory documented; notices signoff pending).
- **G4-06:** NOT_AUTHORIZED; no source-semantic telemetry processing.
- **PR merges, dataset redistribution, manuscript submission and third-party outreach:** NOT AUTHORIZED under this review.
- The initial evaluation plan and frozen G2 and G3 evidence remain unchanged. Do not amend the protocol retroactively or infer scientific evidence from rights metadata.

**Targeted next step:** an explicitly approved email to the identified ESA v2 dataset contact, or a separately documented sole-author determination of sufficient public source-use evidence against the frozen decision threshold. Record any response as source-linked evidence; do not self-certify on their behalf.

This is an academic research-governance review and not a legal opinion or rights-holder authorization.
