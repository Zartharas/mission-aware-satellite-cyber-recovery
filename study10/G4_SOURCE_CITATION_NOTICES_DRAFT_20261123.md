# Study 10 — release-specific citation, attribution and notices (prospective draft)

**Research output:** standalone scientific paper, not a dissertation.
**Decision:** `G4-SCOPE-POLICY-01` approves the prospective **non-raw descriptive use and attribution plan**, not the rights holder's actual permissions for every file. This document is **NOT a submission or a rights-clearance certificate**. All text in this section must be adapted to whether the dataset was **actually** used in a later separately authorized G4 run.

## Suggested source-specific dataset citations

| Planned role | Versioned dataset citation draft | Evidence and caveats |
|---|---|---|
| Primary ESA Mission 1, 2, 3 (three descriptive strata) | De Canio, G., Kotowski, K., and Haskamp, C. (2025). *ESA Anomaly Dataset* (Version v2) [Dataset]. European Space Agency / Zenodo. https://doi.org/10.5281/zenodo.15237121 | Verified public v2 creator list, publication date, record and three ZIP identities. The **v2 Zenodo Rights field does not render a license value**. Prior author-paper review documented dataset CC BY 3.0 IGO; the current OpenReview PDF fetch is challenged. Do not represent ESA-ADB benchmark MIT *software* as a data license. |
| Conditional ESA v1 paired-release sensitivity | De Canio, G., Kotowski, K., and Haskamp, C. (2024). *ESA Anomaly Dataset* (Version 1.0) [Dataset]. European Space Agency / Zenodo. https://doi.org/10.5281/zenodo.12528696 | First-party `esa/anomaly-dataset` repository v1 README links this DOI and the pinned LICENSE identifies CC BY 3.0 IGO. This version is a **paired sensitivity comparator**, not independent flight replication. |
| Primary OPS-SAT-AD v2 (one descriptive stratum) | Ruszczak, B. (2024). *OPSSAT-AD - anomaly detection dataset for satellite telemetry* (Version v2) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.15108715 | Creator formatting is normalized from the Zenodo contributor list, but the Zenodo display shows “Bogdan, Ruszczak.” Validate against the versioned **Zenodo citation export** before manuscript formatting. Exact release `LICENSE` is directly readable and data-inclusive MIT. |

The associated scientific works should **also** be cited where their methodology is discussed. OPS-SAT's record identifies *The OPS-SAT benchmark for detecting anomalies in satellite telemetry* (Scientific Data article DOI `10.1038/s41597-025-05035-3`) and the 2023 ICCS paper (DOI `10.1007/978-3-031-35995-8_21`). The ESA datasets' authors separately describe the benchmark and expanded-release methodology; verify final bibliographic metadata rather than inventing a publication title or author order.

## Proposed notices for a future journal manuscript

**ESA-ADB dataset credit, only if used:** “This study uses [specify v2 and any paired v1 version] of the ESA Anomaly Dataset (De Canio, Kotowski, and Haskamp; version-specific Zenodo DOI listed in the References). The applicable dataset licensing evidence identifies Creative Commons Attribution 3.0 IGO (CC BY 3.0 IGO; https://creativecommons.org/licenses/by/3.0/igo/). Any transformations undertaken for this study are the authors' own and are described in the Methods. This is independent research; the European Space Agency and contributing organizations have not endorsed the analyses or conclusions.” **Do not insert this wording into a submitted paper until the v2 record/license applicability and data exception scope have been checked and actual source use has occurred.**

**OPS-SAT-AD dataset credit, only if used:** “This study uses version v2 of the OPSSAT-AD dataset (Ruszczak, version-specific Zenodo DOI listed in the References). The versioned `LICENSE` names *MIT License for OPS-SAT Dataset*, Copyright (c) 2024 KP Labs, and explicitly includes data and associated documentation. This study does not redistribute the original telemetry files.” Follow the original MIT requirement to retain its **full copyright and permission notice** in any copies or substantial portions of the licensed material; the complete first-party notice is available at https://zenodo.org/records/15108715/files/LICENSE?download=1. Do not falsely claim compliance with future publication obligations before those artifacts exist.

**Changes/derived-work statement:** Describe the precise signal-to-semantic transformations, exclusion decisions, evaluation times, provenance annotations and uncertainty handling actually performed. Do not claim a new license over third-party telemetry or alter the original source license. Never imply that the original providers endorse this paper.

**Data availability, prospective:** “The study's third-party input datasets are available from their original version-specific Zenodo records [list only sources actually used]. Original satellite telemetry will not be re-hosted with this paper. Non-raw study-specific semantic classification tables and reproducibility code will be shared only after rights, privacy, operational-security and publication review.” This is **future policy text**, not a declaration that any semantic results currently exist.

## File-specific exception handling and status

1. **ESA v2:** Public Zenodo record is open, with fixed release DOI/creators/hashes, but its Rights/License value is blank in the readable interface. The prior source-author paper's CC BY 3.0 IGO statement and the first-party repository v1 license are affirmative evidence, **not exhaustive version-specific ZIP-member clearance**. Keep `G4-01=HOLD`.
2. **ESA v1:** Official v1 repository LICENSE and exact linked record support CC BY 3.0 IGO, but actual embedded exceptions are not affirmatively excluded. Keep `G4-02=HOLD_IF_USED`.
3. **OPS-SAT v2:** The exact public Zenodo `LICENSE` was directly reopened and confirms MIT **software, data and documentation** with KP Labs copyright (2024). The author's local LICENSE MD5 matches the official versioned download. The upstream public source tree contains a single LICENSE file; this does **not** establish that in-band rights in the two telemetry CSVs have been exhaustively reviewed. Keep `G4-03=HOLD_NOTICE_AND_EXCEPTION_SIGNOFF`.
4. **Hack-A-Sat 4:** Optional, unpooled secondary contest context; excluded from initial G4 processing. Pinned README says MIT unless exceptions but references missing `LICENSE.md` while root `.LICENSE` exists. Component NOSA/GPL/LGPL exclusions and any file-level rights still require separate review. Keep `G4-04=BLOCKED_IF_USED`.
5. **G4-05:** The author's local integrity run passed 9/9 within its configured archive CRC scope. The retained report is locally SHA-256 identified as `49f52bdc00145bc7a68c5a91e204faf394d8137e043bd2bf59906573b6c70164`, **author-supplied, not independently rehashed**. The notices and exceptions part of G4-05 remains open.
6. **G4-06:** No approval to inspect real telemetry semantics, determine evidence roles, execute policy classifications, upload original source files, publish, or merge PRs.

## Next rights-only evidence step

Inspect **only ZIP directory metadata** locally for potential `LICENSE`, `COPYING`, `NOTICE`, `COPYRIGHT`, `THIRD_PARTY` and `TERMS` names using the accompanying `g4_license_metadata_inventory.py` script. Do **not** upload raw ZIP/CSV/metadata containing telemetry paths. The script outputs only aggregate marker basenames and member counts and leaves nested ZIP file-specific exceptions explicitly **unexamined**.

A missing marker **does not mean there are no exceptions**. Do not mark the G4 gates clear without a documented, positive release-specific rights decision and the later separate G4-06 author execution approval.

## First-party evidence references

- ESA v2: https://zenodo.org/records/15237121
- ESA v1: https://zenodo.org/records/12528696
- ESA v1 repository LICENSE: https://github.com/esa/anomaly-dataset/blob/a969698e464788c961dbb646d3da24595c7c7a2b/LICENSE
- OPS-SAT v2: https://zenodo.org/records/15108715
- OPS-SAT original versioned LICENSE: https://zenodo.org/records/15108715/files/LICENSE?download=1
- OPS-SAT upstream LICENSE: https://github.com/kplabs-pl/OPS-SAT-AD/blob/main/LICENSE (Git blob `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11` at review)
- CC BY 3.0 IGO: https://creativecommons.org/licenses/by/3.0/igo/ and https://creativecommons.org/licenses/by/3.0/igo/legalcode.en
- Hack-A-Sat public pinned README: https://github.com/cromulencellc/hackasat-finals-2023/blob/2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1/README.md

**Current disposition:** `ATTRIBUTION_AND_RIGHTS_NOTICE_DRAFT_PREPARED; PRIMARY_SOURCE_FILE_EXCEPTION_CLEARANCE_PENDING; G4_06_EXECUTION_HOLD`.
