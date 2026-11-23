# Study 10 (S10-RSEI-001) — rights-preamble V2/V3 evidence and residual source-use signoff review

**Record date:** 2026-11-23 UTC  
**Status:** `BOUNDED_RIGHTS_PREAMBLE_CHECK_COMPLETE; SOURCE_USE_SIGNOFF_WITHHELD`  
**Scope:** metadata-only, additive review of author-performed offline V2 and V3 rights-preamble inspection; no new source payload access or upload, no scientific semantic analysis.  
**Author instruction:** expressly authorizes this evidence addendum and review of remaining source-rights and citation requirements. It **does not** authorize G4-06, merging, source data redistribution or manuscript submission.

## 1. Exact evidence provenance and confidence

### V2 report — bytes independently received and hashed

- Uploaded, sanitized V2 JSON report: `Study10_G4_Rights_Preamble_Only.json`.
- **SHA-256 independently recomputed:** `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb` (**MATCH** with user terminal output).
- Local JSON record time: `2026-11-23T03:50:15.501942+00:00`. Source report claims prior nested metadata report SHA-256 `b9486430f6a2c25384d105fe96296411df4b2e4526a6d0e759a8c960e3b28584` was checked.
- Status: `INCOMPLETE_OR_BOUNDED`. Report lists nine source records but `source_count_scanned=6`, with **three** `PREAMBLE_SAMPLE_PARTIAL` ESA v2 records; this is not equivalent to only six entries in the source list.
- Original six ESA ZIP nested directories previously enumerated: **2,090**; this total is metadata for nested ZIP containers, **not** 2,090 payload notices inspected.
- Inspection of candidate CSV **leading comment/notice prefixes**: **23 examined out of 26**; **3 unsupported compression methods** remained, exactly one `channels.csv` preamble in each ESA v2 mission. All 23 examined prefixes reported **zero comment lines and zero detected notice-marker categories**.
- V2 OPS-SAT `LICENSE` row: `LICENSE_IDENTITY_CONFIRMED_NOT_REPUBLISHED`; full license is not reproduced in the uploaded JSON.
- The V2 report asserts `telemetry_semantic_analysis_performed=false`, `file_specific_rights_clearance=false`, `author_G4_06_execution_authorized=false`, and `PR_merge_authorized=false`.
- **No original telemetry/archive bytes were supplied to or inspected by this assistant.** Only the small sanitized JSON file was received. Report text and local run statistics are an author's locally generated evidence artifact, not a reproduction of the full scan by this assistant.

### V3 targeted completion — terminal attestation only

- Author's Mac terminal shows exact ZIP SHA-256 check **OK** for `Study10_G4_V2_Deflate64_Preamble_Bundle.zip`. The same ZIP's SHA-256 was independently computed against the available package: `20fb0ef2ed659fe12f7a61b5acc1e9c358a8d2354c145bce9d3ee885b1714232`.
- Author's terminal shows internal file hashes **OK**, **14/14 synthetic unit tests PASS**, V2 report hash verification **OK**.
- The V3 tool identifies only `ESA_M1_v2`, `ESA_M2_v2`, `ESA_M3_v2` as target sources. Each terminal row reports **one** bounded prefix inspected; `failure_code=NONE`; `markers={}`; `PREAMBLE_SAMPLE_DONE_NOT_RIGHTS_CLEARED`.
- Terminal status: `THREE_V2_PREFIX_GAPS_EXAMINED_RIGHTS_UNRESOLVED`, footer `RIGHTS_DEFLATE64_PREAMBLES_BOUNDED_COMPLETE`.
- Local V3 report basename: `Study10_G4_V2_Deflate64_Rights_Preamble_Only.json`.
- **Author-reported V3 report SHA-256:** `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8`. The V3 JSON bytes **were not uploaded or independently hashed**. Do not label this result independently verified.
- V3 terminal indicates the new targeted rights-prefix step succeeded, **not** that the data have no license exceptions. No broad repeat scan was performed or requested.

### Combined bounded-prefix coverage

| Dataset stratum / local source | V2 inspected | V3 recovered | Combined inspected / candidates | Recognized rights-prefix markers |
| --- | ---: | ---: | ---: | ---: |
| ESA Mission 1, v1 | 4 | 0 | 4/4 | 0 |
| ESA Mission 1, v2 | 3 | 1 | 4/4 | 0 |
| ESA Mission 2, v1 | 5 | 0 | 5/5 | 0 |
| ESA Mission 2, v2 | 4 | 1 | 5/5 | 0 |
| ESA Mission 3, v1 | 3 | 0 | 3/3 | 0 |
| ESA Mission 3, v2 | 2 | 1 | 3/3 | 0 |
| OPS-SAT v2 `dataset.csv` | 1 | 0 | 1/1 | 0 |
| OPS-SAT v2 `segments.csv` | 1 | 0 | 1/1 | 0 |
| **Total** | **23** | **3** | **26/26** | **0** |

All 26 identified CSV candidates' **bounded leading prefixes** were inspected according to the combined V2 independently hashed report and V3 author-attested terminal execution. There are **zero unsupported-prefix exceptions remaining** in this defined sampling scope. This is **not** a full content, copyright, security or privacy audit. Original CSV rows/segments, later in-band notices, file-level third-party rights and unobserved caveats remain outside this check. The scanners stop at the first non-comment line and do not interpret telemetry semantics.

## 2. Source licensing and decisions, without silently clearing gates

### G4-01 — ESA Anomaly Dataset v2 (three primary descriptive strata)

Official exact v2 record: https://zenodo.org/records/15237121, **April 17, 2025**, three archive MD5 identifiers already pinned in frozen G2 and in the previous evidence review. Dataset creators: **Gabriele De Canio, Krzysztof Kotowski, Christoph Haskamp**. Direct first-party v2-linked dataset metadata declares **CC BY 3.0 IGO**, and the dataset-author preprint explicitly identifies the dataset's CC BY 3.0 IGO licensing rather than the benchmark software's MIT license. The display of an empty Zenodo Rights field is not contradictory evidence and does **not** require an ESA email merely to verify the license name; the author expressly declined routine contact.

**Remaining:** Explicit source-specific signoff for intended local use; acceptance or justified disposition of unobserved member/in-band/third-party rights and mission-sensitive content; final CC BY attribution/license URI/modification disclosure/non-endorsement in actual outputs. **G4-01 remains HOLD.**

### G4-02 — ESA Anomaly Dataset v1 (conditional paired sensitivity only)

Official exact v1 record: https://zenodo.org/records/12528696, **June 25, 2024**. The pinned official ESA repository's README links v1, and its LICENSE says **CC BY 3.0 IGO**. The author approved v1 **only** as RQ-E3 matched `(mission, channel identifier, metadata field)` paired release sensitivity, **not** a fifth stratum nor independent spacecraft/trial. Bounded prefix coverage is complete (12/12) across v1, but this cannot prove no later in-band conditions.

**Remaining:** Conditional source-use exception and attribution signoff, only if v1 is actually used. **G4-02 remains HOLD_IF_USED.**

### G4-03 — OPS-SAT-AD v2 (fourth primary descriptive stratum)

Official versioned v2 record: https://zenodo.org/records/15108715, **Published June 24, 2024**, and exact `LICENSE` https://zenodo.org/records/15108715/files/LICENSE?download=1. It is the **MIT License for OPS-SAT Dataset**, **Copyright (c) 2024 KP Labs**, expressly applicable to **software, data and associated documentation**. The author's approved plan prohibits original telemetry redistribution; if any licensed copies/substantial portions are later distributed under a separately approved publication, preserve the full original MIT copyright/permission notice. The two allowlisted CSV leading-prefix checks are complete but do not inspect late in-band rights statements or contents.

**Citation metadata issue (not grounds to fabricate authorship):** the v2 Zenodo page currently displays primary creator as `Bogdan, Ruszczak` but lists a contributor as `Ruszczak, Bogdan`. The associated 2025 *Scientific Data* paper identifies **Bogdan Ruszczak**. A draft dataset citation such as `Ruszczak, B. (2024)` is **provisional** until the exact **v2** citation export or DataCite field order is checked. The page displays **Published June 24, 2024** but separately **Created March 30, 2025**; do not conflate display fields or silently change the cited edition/year. The corresponding benchmark methods article is DOI `10.1038/s41597-025-05035-3`; its correction is DOI `10.1038/s41597-025-05751-w`. A correction to an article does not show the data's MIT license was revoked.

**Remaining:** Exact versioned citation-export verification; separate disposition of original CSV member-specific/in-band/third-party exceptions; final actual-output notice audit and explicit author signoff. **G4-03 remains HOLD.**

## 3. Prospective final publication notice checklist

This checklist is a **prospective control**, not an assertion of real-source use or completed manuscript changes.

- **Version-specific DOI and creators:** cite only the v2/v1 datasets actually used. ESA primary uses DOI `10.5281/zenodo.15237121`; optional ESA v1 paired sensitivity DOI `10.5281/zenodo.12528696`; OPS-SAT v2 DOI `10.5281/zenodo.15108715`.
- **ESA CC BY 3.0 IGO:** credit creators and ESA publisher, link https://creativecommons.org/licenses/by/3.0/igo/, identify qualifying changes and adaptations, maintain notices, and never imply ESA/consortium endorsement.
- **OPS-SAT data-inclusive MIT:** give versioned dataset citation and KP Labs copyright as part of the prospective plan; preserve the **complete** MIT copyright and permission notice where a future approved artifact contains copies/substantial licensed material. A mere DOI citation is not sufficient for that redistribution scenario.
- **Methods papers:** distinguish dataset-specific DOIs from papers describing methodology; use correct published/corrected article metadata, not the deposited readme's older preprint year as a substitute.
- **Data availability:** identify third-party source archives only after use; no original telemetry rehosting; check any non-raw derived release for sensitive operational details, privacy and reconstruction of original data.
- **Actual manuscript and supplements:** proof every implementation against the actual final file; no premature claims of data usage, measured results or completed publication.
- **OPS-SAT creator anomaly:** preserve explicit `VERSIONED_CITATION_EXPORT_NOT_VERIFIED` until a usable versioned citation export is obtained or otherwise resolved by authoritative metadata; no automated silent name correction.

Original prospective notice template is `study10/G4_PROSPECTIVE_PUBLICATION_SOURCE_NOTICES_20261123.md` (Git blob SHA-1 `f475c5591457ecfbf731e932e43e65bd99b17cf9`). That file is **unchanged** by this review.

## 4. What remains genuinely undecided, and suitable decision path

The completed bounded checks found **no recognized leading-prefix restriction markers**; there is **no positive finding of an additional conflicting license** in those tested prefixes. This lowers one specific concern but does **not** prove none could occur later or in separately owned members.

A defensible next governance decision is an explicit, version-by-version **author source-use/residual risk determination**, based on the first-party dataset-level licenses, precise study purpose, no raw-data redistribution, bounded negative-marker evidence, and a transparent acknowledgment of unexamined scopes. That decision must distinguish **unknown exceptions** from **known conflicting terms** and retain escalation if a real restrictive notice is encountered later. If the controlling frozen Option B receipt requires specific member-level review or third-party exception signoff beyond what current evidence proves, it cannot be waived merely by relabelling a bounded report "complete." No routine rights-holder contact is required for the already verified ESA license name, and no additional broad source scan is recommended.

The exact OPS-SAT **versioned citation export** may be checked using public record metadata without original telemetry or further local Mac execution; the creator-field discrepancy must not be silently “corrected.” The V3 full sanitized report **could** be independently hashed only if the author elects to provide it safely; its current author-reported hash remains explicitly distinguished and does not block documenting the author's terminal result.

**No PR or manuscript was merged/submitted, no original dataset was uploaded, no scientific findings were created, and no rights holder was contacted.**

## 5. Preserved G2/G3 and G4 gate state

| Gate | Status after V2/V3 addendum | Reason |
| --- | --- | --- |
| G4-01 ESA v2 | `HOLD` | Final source-use / applicable member exception signoff pending |
| G4-02 ESA v1 | `HOLD_IF_USED` | Paired comparator only, final release rights and notices if actually used |
| G4-03 OPS-SAT v2 | `HOLD` | CSV rights exception disposition, final creator citation, notice audit |
| G4-04 Hack-A-Sat 4 | `EXCLUDED_BLOCKED_IF_USED` | Excluded; no component license signoff |
| G4-05 identity/notices | `PARTIAL` | `BOUNDED_PREFIX_INSPECTION_COMPLETE` subcheck; actual notice implementation and signoff not complete |
| G4-06 original-source scientific execution | `NOT_AUTHORIZED` | Separate explicit author permission after mandatory rights gates |

Controlling frozen G2 Option B source-rights policy is `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`, pinned in `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac`. The primary descriptive design remains **four strata × eight recovery-state variables = 32 classification slots**. Source-rights clearance is not inferred from directory or prefix scans; source-use and G4-06 approval are separate.

**Disposition:** `V2_V3_BOUNDED_TECHNICAL_CHECK_COMPLETE; ALL_SOURCE_RIGHTS_AND_EXECUTION_GATES_UNCHANGED`.

This is an academic research-governance evidence assessment, not a legal opinion or an independent rights-holder clearance.
