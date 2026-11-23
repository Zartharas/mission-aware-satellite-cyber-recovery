# Study 10 (S10-RSEI-001) — G4 consolidated source-use signoff review

**Date recorded (UTC):** 2026-11-23  
**Decision status:** `REVIEW_COMPLETED_SIGNOFF_WITHHELD`  
**Authorization:** sole author approved the **consolidated rights, attribution, and source-use signoff *review***, not unconditional clearance, a new telemetry read, experimental G4-06 execution, publication, third-party contact, or PR merge.  
**Publication:** standalone Paper 5 / Study 10 research paper, NOT a dissertation.  
**Change scope:** evidence-only addition stacked on draft PR #240. Frozen G2/G3 remain unmodified.

## 1. Authority and controlling safeguards

The frozen, sole-author-approved Option B protocol is `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`. The binding artifact, `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json` (Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac`), explicitly states:

- `rights_clearance_for_source_data=false`;
- ESA v2 exact release scope and third-party file rights signoff **before new source-payload use**;
- ESA v1 rights and attribution **if paired-release sensitivity is used**;
- OPS-SAT v2 rights/notices and embedded third-party exceptions;
- Hack-A-Sat 4 secondary component rights **if processed**;
- versioned source identity checks and all applicable attribution notices;
- **separate explicit G4-06 scientific execution and source-use approval**.

Prior public-license and author approvals are decisions on **documents, data-license identity, source roles, and prospective notices**, not independent rights-holder attestations that every original member is exception-free. There is no basis for revising frozen G2/G3 or increasing primary denominators from the planned **four descriptive strata × eight recovery variables = 32 classification slots**. The four strata are ESA v2 Missions 1–3 and OPS-SAT-AD v2. Conditional ESA v1 is a paired release sensitivity comparison, never a fifth primary stratum or independent replication.

## 2. Decision trace and evidentiary strength

| Gate/source | Recorded author decision | Exact release and positive evidence | Current signoff assessment |
| --- | --- | --- | --- |
| **G4-01 ESA v2** | Dataset-level CC BY 3.0 IGO supported; **no routine contact** necessary merely to reconfirm license name (draft PR #238) | DOI `10.5281/zenodo.15237121`, Apr 17 2025; three v2 ZIP MD5s; authors' release-linked licensing assertion and project-maintained Croissant dataset metadata, Git blob `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`, naming **CC BY 3.0 IGO** | **HOLD** for final release/member-specific scope, intended-use conditions, residual rights/privacy/security considerations and prospective actual-output notices |
| **G4-02 ESA v1** | Keep conditionally for RQ-E3 matched (mission, channel, field) v1–v2 sensitivity, without independent replication or execution (draft PR #239) | DOI `10.5281/zenodo.12528696`, June 25 2024; official `esa/anomaly-dataset` README links v1, LICENSE Git blob `e9603f00725a6580a4c82ac6ada160a13f53f323` states **CC BY 3.0 IGO** | **HOLD_IF_USED** for source-use notices, residual exceptions and separate authorization before optional paired source-semantic use |
| **G4-03 OPS-SAT-AD v2** | Approve prospective MIT attribution and **no raw redistribution** plan, with G4-03 hold explicitly retained (draft PR #240) | DOI `10.5281/zenodo.15108715`; exact versioned `LICENSE` and Git blob `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`: **MIT License for OPS-SAT Dataset**, `Copyright (c) 2024 KP Labs`, explicitly includes data | **HOLD** for original CSV in-band notices/third-party exclusions, final citation-export author metadata, and notice implementation |
| **G4-04 Hack-A-Sat 4** | Excluded from initial G4 research | Secondary component licenses not signed off | **EXCLUDED / BLOCKED IF USED** |
| **G4-05 identity + notices** | Author-reported original-data 9/9 integrity and six-archive rights-directory inventory; citations/notices drafted | Nested rights report author-reported SHA-256 `b9486430f6a2c25384d105fe96296411df4b2e4526a6d0e759a8c960e3b28584`; 2,090 nested directories, zero recognized rights-marker basenames, zero reported errors | **PARTIAL**, not whole-gate PASS; source bytes not independently reviewed here; final implementation/signoff open |
| **G4-06 execution** | **Never authorized under these approvals** | No lawful-path/signoff completion for all mandatory controls | **NOT_AUTHORIZED** |

The three principal author decisions are pinned in:
- `study10/G4_01_ESA_V2_RIGHTS_SCOPE_DECISION_CANDIDATE_20261123.md`, Git blob `6c04c7fc92223888433cface52876a53930f7d78`.
- `study10/G4_02_ESA_V1_CONDITIONAL_PAIRED_SENSITIVITY_AUTHOR_DECISION_20261123.json`, Git blob `786b1cb54d91a1a85183dbc1d84e46595ae00da7`.
- `study10/G4_03_OPS_SAT_V2_ATTRIBUTION_NON_REDISTRIBUTION_AUTHOR_DECISION_20261123.json`, Git blob `1bad49820aa35eeae6a7ef58de1630df68aee1a0`.

## 3. Original-source identity and attribution verification

### ESA v2, primary

The official Zenodo v2 record https://zenodo.org/records/15237121 lists three original archives:
- `ESA-Mission1.zip`: MD5 `9770ad12ed730238f37c42d5c27ab436`
- `ESA-Mission2.zip`: MD5 `bfc72012691427d9327eb41f726ce45e`
- `ESA-Mission3.zip`: MD5 `d63943f09c81378acd9fc5e565ecc66e`

Dataset creators, in recorded order: **De Canio, Gabriele; Kotowski, Krzysztof; Haskamp, Christoph**; dataset publisher **European Space Agency**. Exact project metadata: https://github.com/kplabs-pl/ESA-ADB/blob/main/data/preprocessed/esa-anomaly-dataset-metadata.json (pinned Git blob above) expressly declares **CC BY 3.0 IGO** and identifies those three exact v2 Zenodo file URLs with their published MD5. The Zenodo Rights display contains a license heading but no rendered value; this is a metadata display limitation, **not** stronger negative evidence than the version-linked dataset declaration. No ESA contact is required solely to resolve the license name per the author's instruction. This does **not** prove absence of third-party rights in internal members.

### ESA v1, conditional paired sensitivity

Official Zenodo v1 record https://zenodo.org/records/12528696; release-specific MD5:
- `ESA-Mission1.zip`: `80750189d171f5f398fb3d96c49df12b`
- `ESA-Mission2.zip`: `0b7505b7f0731ca037ee889ca2a520ce`
- `ESA-Mission3.zip`: `34b8a8857e2242fb1f00b368b7421595`

The official repository at pinned commit `a969698e464788c961dbb646d3da24595c7c7a2b` links the exact v1 Zenodo DOI in README and names **CC BY 3.0 IGO** in LICENSE. The author has approved keeping this source **conditionally** for matched metadata comparisons, not executing it now, increasing primary population, or asserting release independence.

### OPS-SAT-AD v2, primary

The official exact versioned Zenodo record https://zenodo.org/records/15108715 lists **six released files**: `dataset.csv`, `segments.csv`, `LICENSE`, `dataset_generator.ipynb`, `modeling_examples.ipynb`, and `requirements.txt`. The existing frozen intake selected **only the first three**; listing the other files as part of the deposited record does not authorize their retrieval, semantic analysis, inclusion in a supplement or reuse.

Within the frozen intake:
- `dataset.csv` MD5 `5246fdc5e4630a4cecbf7fb6bc8b795e`;
- `segments.csv` MD5 `72f109630abb933a386106897a631188`;
- `LICENSE` MD5 `ea8befa9af2b37b7a54b5a16fc3712b0`.

The exact public MIT `LICENSE` applies expressly to `software, data and associated documentation` and is marked **Copyright (c) 2024 KP Labs**. It requires the copyright and permission notice in any copies or substantial portions distributed. The original full license is https://zenodo.org/records/15108715/files/LICENSE?download=1. Repository independent Git reference: https://github.com/kplabs-pl/OPS-SAT-AD/blob/main/LICENSE, blob `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`.

The versioned Zenodo record's **creator display** is `Bogdan, Ruszczak` while **contributor display** is `Ruszczak, Bogdan`; the corresponding 2025 scientific paper uses **Bogdan Ruszczak**. **Author-order/citation formatting remains provisional** because neither the versioned Zenodo citation export nor DataCite record metadata was independently retrievable during this review. The Zenodo page labels the record `Published June 24, 2024`, whereas the technical metadata `Created March 30, 2025`; these different labels are recorded **as displayed**, not automatically reconciled into a new publication date.

Associated methods publication: DOI `10.1038/s41597-025-05035-3`; published correction: DOI `10.1038/s41597-025-05751-w`. The correction is a **scholarly citation context**, not evidence that the versioned dataset MIT terms were replaced.

## 4. License conditions vs. what was actually validated

### Affirmative findings

1. Release-specific file lists, creators, published MD5s, and DOI identities have positive **public first-party documentary** evidence.
2. Dataset-level licensing: ESA v1/v2 **CC BY 3.0 IGO**; OPS-SAT-AD v2 **data-inclusive MIT**. The ESA-ADB benchmark **code's MIT license must not be substituted for ESA dataset rights**.
3. The author affirmatively approved the conditional roles and prospective attribution/no-raw-redistribution plan.
4. The author-reported local metadata-only inventory examined **2,090 nested ZIP central directories** with **zero matching recognized marker basenames** and reported no errors. This supports **only that specific directory-scoped test**, not file-level rights clearance.

### Not tested or not proven

1. ESA v1/v2 individual ZIP payload member **in-band** rights statements and third-party ownership exceptions. The scanner did not open nested data members.
2. OPS-SAT original `dataset.csv` and `segments.csv` **in-band** rights statements and any embedded third-party restrictions. This review did not read either CSV.
3. Whether a future non-raw table, semantic map, figure, code snippet or supplement would reproduce licensed original material, expose mission-sensitive operational information or allow reconstruction. These must be reviewed against the **actual output**.
4. The OPS-SAT v2 deposited dataset citation export author order and final journal citation format.
5. Any actual manuscript publication notice, modification disclosure, contribution/acknowledgment statement, data availability declaration or redistribution artifact. These are all **future/conditional**, not already implemented.
6. Independent rehashing of the author's local original source archives and local nested-report bytes by this assistant; all local results remain **author-reported**.
7. A signed/approved determination of final residual rights scope and pre-G4 source-use eligibility. It has **not** been supplied by the author or rights holder.

A blank Zenodo license display by itself is **not grounds to insist on an ESA email**, and the author expressly does not require routine contact. A future specific, material contradiction or restrictive file notice may still require escalation. **No third party was contacted.**

## 5. Required future attribution and non-redistribution controls

**Only after the dataset is actually used under separately authorized G4 execution**:

- **ESA v2 (and v1 if used):** cite the **exact version-specific dataset DOI**, creator names in source order, publisher, and **CC BY 3.0 IGO** with https://creativecommons.org/licenses/by/3.0/igo/; identify qualifying modifications; retain applicable notices; avoid implied ESA or consortium endorsement. Dataset and scholarly methods papers are separately cited where used. Treat v1–v2 as paired releases, never independent mission replications.
- **OPS-SAT v2:** cite the exact v2 DOI, properly verified author format, MIT dataset license, and `Copyright (c) 2024 KP Labs`. If reproducing **copies or substantial portions** of licensed data/code/documents in a release, retain the **complete original MIT copyright + permission text** in that artifact. Scholarly methodology citation and the correction record are separate from license compliance.
- **Data availability:** point to original Zenodo version-specific releases only for actually used sources; **no raw satellite telemetry rehosting**. No future claim that source data or semantic outputs were used/generated unless that is true.
- **Non-raw outputs:** review every prospective table/figure/lookup/derived mapping for proprietary excerpts, sensitive command paths, reconstructability, security and privacy before approval to publish. "Non-raw" alone does not mean harmless.
- **Paper and supplements:** perform a release-time notice and attribution audit; citations and attribution templates are not evidence of implementation until a real final manuscript/supplement is examined.

Prospective publication text is in `study10/G4_PROSPECTIVE_PUBLICATION_SOURCE_NOTICES_20261123.md`, Git blob `f475c5591457ecfbf731e932e43e65bd99b17cf9`. **Do not modify the manuscript to state data was used before actual source-semantic execution.**

## 6. Signoff determination and fail-closed stop criteria

**Documentary review:** `COMPLETE` for available public license evidence and existing author decisions.  
**Dataset license identity:** `CONFIRMED_AT_DATASET_LEVEL` for ESA v1/v2 and OPS-SAT v2.  
**Author's intended research inclusion:** `POLICY_APPROVED_CONDITIONALLY` as above.  
**File-specific exception disposition:** `UNRESOLVED`; no claim of zero exceptions.  
**Actual publication notices:** `NOT_IMPLEMENTED`; prospective draft only.  
**Source-use eligibility under frozen G2:** `NOT_SIGNED_OFF`.  
**G4 scientific execution:** `NOT_AUTHORIZED`.  
**All PRs:** draft and unmerged; no merge or branch activation authorized.

**Stop before any new real-source semantic processing** if the exact source version is unverified, any applicable file rights are materially contradictory or unassessed, required notices cannot be implemented, sensitive operational disclosures are not controlled, or no explicit subsequent G4-06 authorization exists. An unresolved license-field rendering by itself does not disprove positive first-party dataset-level CC BY evidence; nevertheless it also cannot erase unexamined file-level conditions.

**Future minimum signoff evidence:**
1. Source/version identity confirmation and documented disposition of any file-specific/in-band notices **by a separately authorized, minimal rights-only process** or equally reliable first-party evidence. **No new source payload access is performed here.**
2. Final author approval of the actual intended limited source use, applicable attributions and accepted residual risk under the frozen protocol. This approval must name each source/version and optional ESA v1 inclusion.
3. For any future publication, real-artifact notice, citation, data-availability and security/reconstructability checks.
4. Separate G4-06 execution authorization **after** the mandatory rights/notice gate. A PR merge is a distinct approval decision.

**Disposition:** `SOURCE_USE_SIGNOFF_REVIEW_RECORDED_BUT_ALL_EXISTING_G4_HOLDS_PRESERVED`.

This source-review is a research-governance assessment, not a legal opinion or a new copyright permission grant.
