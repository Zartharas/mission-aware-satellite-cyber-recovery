# S10-RSEI-001 — G4 final documentary source-rights review (no source-use clearance)

**Review scope:** Public first-party dataset/repository records, official license terms, prior frozen G2 rights policy, and author-reported metadata-only inventory. No original ESA/OPS telemetry content, source rows, anomaly labels, or command semantics were accessed in this review.

**Research deliverable:** Standalone scientific paper (Paper 5, Study 10), not the user's dissertation.

**Documentary-review outcome:** `DOCUMENTATION_COMPLETE_FOR_CURRENT_PUBLIC_EVIDENCE; RIGHTS_SIGNOFF_NOT_GRANTED; G4_06_HOLD`. This is a final *documentary evidence review*, **not** a legal opinion, unconditional dataset clearance, G4 authorization, manuscript submission, or permission to merge.

## 1. Binding study design and use classification

The **frozen G2 Option B** policy (`B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`) allows the protocol design to remain frozen while **all six pre-G4 conditions remain hard fail-closed**. Exact supporting receipt: `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json` (Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`).

Planned, **not yet executed**, source roles:
- ESA Anomaly Dataset **v2** Missions 1, 2, 3: three **distinct descriptive strata**; **not independent spacecraft replications** and not pooled as independent validation.
- OPS-SAT-AD **v2**: a fourth, separate primary descriptive stratum.
- ESA Anomaly Dataset **v1**: **optional paired-release sensitivity comparator only**. No treating v1 and v2 observations as independent replication.
- Hack-A-Sat 4: **excluded from initial source use** and retained only as a conditional, unpooled secondary candidate if separately authorized later.

Intended operations: bounded local research use, future description and evaluation of signal-to-semantics feasibility, provenance-aware derivations if separately authorized. Intended distribution: manuscript citations, method descriptions and reviewed non-raw reproducibility outputs, **not original telemetry archives, raw rows, source snippets, or rehosted copies**. The frozen method must not be retroactively changed based on observed source outcomes.

Prior permitted **integrity and rights-directory checks** do not authorize research on native telemetry semantics. The publication notices below remain **prospective**, and MUST NOT say the study used data or generated results until actual use occurs under separate approval.

## 2. Release-specific source evidence and limits

### G4-01: ESA Anomaly Dataset v2 (primary)

- Exact release: https://zenodo.org/records/15237121 ; DOI `10.5281/zenodo.15237121`; version **v2**, published April 17, 2025.
- Creator order on versioned record: **De Canio, Gabriele; Kotowski, Krzysztof; Haskamp, Christoph**. Publisher: **European Space Agency**.
- Versioned source ZIPs and published MD5:
  - `ESA-Mission1.zip`: `9770ad12ed730238f37c42d5c27ab436`
  - `ESA-Mission2.zip`: `bfc72012691427d9327eb41f726ce45e`
  - `ESA-Mission3.zip`: `d63943f09c81378acd9fc5e565ecc66e`
- **Direct version-linked, project-maintained machine-readable evidence:** `https://github.com/kplabs-pl/ESA-ADB/blob/main/data/preprocessed/esa-anomaly-dataset-metadata.json`, Git blob SHA-1 `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`. Its license object names **Attribution 3.0 IGO (CC BY 3.0 IGO)** with canonical https://creativecommons.org/licenses/by/3.0/igo/; its distribution explicitly contains all three exact v2 Zenodo archive URLs and published MD5 values. It lists `dateModified=2025-04-17`; its internal `version=1` and `datePublished=2024-06-25` **must not** be represented as the version/date of the linked Zenodo **v2** release.
- Independent earlier G4 review documented an author paper describing v2 dataset as CC BY 3.0 IGO; this review did not re-fetch the challenged OpenReview PDF. Do **not** replace that evidence with an unverifiable first-person statement.
- **Conflict/limitation:** The exact Zenodo v2 public Rights panel presents a `License` heading **without a value**. The repository metadata provides stronger dataset-level corroboration but is not the same as an explicit, versioned Zenodo rights-panel grant.
- No concluded coverage for: every embedded payload, separately held rights, in-band notices or terms, or operational-security/privacy restrictions. A rights-marker filename scan cannot answer these.
- **Decision:** `G4-01=HOLD`. Project-level v2 attribution evidence is substantial; **final version/member scope signoff has not been obtained**. Do not infer authorization solely from the word “Open” on Zenodo.

### G4-02: ESA Anomaly Dataset v1 (paired-release sensitivity, optional)

- Exact release: https://zenodo.org/records/12528696 ; DOI `10.5281/zenodo.12528696`; version **1.0**, published June 25, 2024.
- Same three Zenodo dataset creators, and same ESA publisher, but the three **v1** ZIP hashes differ from v2:
  - Mission1 `80750189d171f5f398fb3d96c49df12b`
  - Mission2 `0b7505b7f0731ca037ee889ca2a520ce`
  - Mission3 `34b8a8857e2242fb1f00b368b7421595`
- First-party `esa/anomaly-dataset` repository at pinned commit `a969698e464788c961dbb646d3da24595c7c7a2b` links the **v1 DOI** in README (`76f66a4550d0d8d3910b595d1c968bde9bbabed6`), and `LICENSE` (Git blob `e9603f00725a6580a4c82ac6ada160a13f53f323`) explicitly names **CC BY 3.0 IGO**.
- Exact v1 Zenodo Rights section also renders a blank license value. The project-file grant supports v1 project-level licensing but does not independently certify each embedded file.
- **Decision:** `G4-02=HOLD_IF_USED`. Exclude the v1 sensitivity analysis until its optional-source rights, notices, and exceptions are explicitly reviewed. Exclusion leaves the pre-frozen v2 + OPS primary design intact; do not silently redefine a planned primary cohort.

### G4-03: OPS-SAT-AD v2 (primary fourth stratum)

- Exact record: https://zenodo.org/records/15108715 ; DOI `10.5281/zenodo.15108715`; version **v2**, record displays June 24, 2024.
- Record creator is **displayed** as `Bogdan, Ruszczak`, while research contributors and the related 2025 benchmark article identify **Ruszczak, Bogdan**. Use provisional normalized `Ruszczak, B.` only after versioned citation export/creator authority confirmation.
- Original source files included in frozen G2 intake: `dataset.csv`, `segments.csv`, `LICENSE`. Published `LICENSE` MD5 `ea8befa9af2b37b7a54b5a16fc3712b0`.
- **Exact Zenodo v2 `LICENSE`, independently opened**: https://zenodo.org/records/15108715/files/LICENSE?download=1 . It names **“MIT License for OPS-SAT Dataset”**, **Copyright (c) 2024 KP Labs**, and its scope expressly includes **software, data and associated documentation**. Author-local integrity audit earlier reported exact license MD5 match. Upstream GitHub `kplabs-pl/OPS-SAT-AD/LICENSE` Git blob `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11` contains the same substantive wording.
- This data-inclusive license is stronger than MIT licensing of benchmark code alone. It requires retaining the full copyright and permission notice for copies/substantial portions of the licensed material. Merely citing the DOI is not a substitute if licensed code/data is actually redistributed; conversely, no raw redistribution is planned.
- The two original CSVs' **in-band** rights notices and any third-party content claims have not been inspected under the permitted rights-metadata review. Do not assert their absence.
- Scientific methods citation: **Ruszczak, Kotowski, Evans and Nalepa (2025)**, *The OPS-SAT benchmark for detecting anomalies in satellite telemetry*, *Scientific Data* **12**, 710, DOI `10.1038/s41597-025-05035-3`; correction DOI `10.1038/s41597-025-05751-w` (August 2025). The accessible corrected article notes an authorship affiliation update, **not proof of a data-license change**. Verify journal citation export before final reference rendering.
- **Decision:** `G4-03=HOLD_FINAL_NOTICE_AND_EMBEDDED_EXCEPTION_SIGNOFF`. The versioned data license is directly verified; final proposed publication notice and unknown embedded exceptions must still be adjudicated.

### G4-04: Hack-A-Sat 4 (excluded)

No new file-level review or new source-use approval. Known differing component-license pathways remain unresolved. `G4-04=EXCLUDED_BLOCKED_IF_USED`.

## 3. CC BY 3.0 IGO and MIT obligations for the planned use

**CC BY 3.0 IGO:** legal code: https://creativecommons.org/licenses/by/3.0/igo/legalcode.en ; deed: https://creativecommons.org/licenses/by/3.0/igo/. For distribution/public performance/adaptations of a covered work, preserve applicable author and work attribution, available license URI and notices, identify modifications, and **avoid suggesting ESA/consortium approval**. The original license has no-additional-restrictions provisions; do not label all original data or unrelated proprietary components as newly licensed by this study. The IGO terms include dispute-resolution provisions, and no rights beyond the covered work are necessarily conferred.

**OPS-SAT MIT:** the **source-specific** terms in the exact versioned `LICENSE` control, not generic software-only language. If copies or substantial portions of covered material (including code/data) are later included in any supplement, retain the full required copyright and permission notice. Journal methods-level citation and acknowledgement are scholarly expectations even when the paper shares no original dataset. Keep the original text available through the versioned Zenodo LICENSE URL; do not claim its full notice was included in a particular future artifact unless that artifact is checked.

**Operational controls beyond license:** The presence of public telemetry does not certify lack of privacy, third-party intellectual-property, security-sensitive operational, export or contractual restrictions. Raw datasets are not to be rehosted. Non-raw semantic mappings and figures need separate screening for reconstructability and operationally sensitive details. Citation ≠ a data license, and repository code license ≠ permission for arbitrary dataset members.

## 4. Author-reported local metadata inventory evidence

- Prior source integrity: **9/9** author-reported hash/archive checks, independently unverified original local bytes.
- Top-level rights filename report: SHA-256 `1b15ca458ce1f85ee4730e1b267dae4f023e60bf90689575b03930cd02fc00b5` (author-reported).
- Nested rights filename report: SHA-256 `b9486430f6a2c25384d105fe96296411df4b2e4526a6d0e759a8c960e3b28584` (author-reported; assistant did not read original JSON).
- User-reported scan: six outer archives, **2,090** nested ZIP central directories, **zero** recognized rights marker *filenames*, zero reported errors, zero deeper ZIPs. Breakdown: ESA v1/v2 M1 `774/774`, M2 `223/223`, M3 `48/48`.
- Important negative-evidence caveat: **zero matching filename markers is not evidence that no license conditions, in-band notices, separately owned data or exceptions exist**. This scan did not read original nested telemetry members.

## 5. Gate disposition after review (no transition to PASS)

| Gate | Disposition | Exact condition remaining |
| --- | --- | --- |
| G4-01 ESA v2 | **HOLD** | Final explicit author/source-scope decision for v2 and any file-specific exceptions; the blank Zenodo Rights value must not be silently converted to clearance |
| G4-02 ESA v1 | **HOLD_IF_USED** | Decide whether optional sensitivity is retained; if retained, sign off v1 versioned rights and notices before source-semantic use |
| G4-03 OPS-SAT v2 | **HOLD** | Sign off data-inclusive MIT citation/notice implementation and disposition of unexamined in-band/third-party exceptions |
| G4-04 Hack-A-Sat 4 | **EXCLUDED** | Separate component rights review and explicit approval if inclusion is ever proposed |
| G4-05 identity + notices | **PARTIAL** | Local integrity and filename checks recorded, final notice implementation and rights exceptions remain unsigned |
| G4-06 scientific execution | **NOT AUTHORIZED** | Separate explicit author permission for source-semantic mapping and execution after other mandatory gates pass |

None of these holds are resolved merely by approval to perform this documentary review. The authorization to **review** licenses is not authorization to **assert final rights signoff**, use real telemetry for semantic research, submit the manuscript, or merge PRs.

## 6. Forward actions and decision rules

1. Preserve the source-linked review and the **prospective** publication notices as an additive draft PR stacked on draft PR #236; frozen G2/G3 remain unchanged.
2. Make a deliberate source-scope decision on ESA v2 using the exact versioned Zenodo record, project's linked CC BY 3.0 IGO metadata, and evidence of applicable file exceptions. If its blank Zenodo Rights value remains materially ambiguous for the contemplated publication, request an explicit rights-holder clarification *after separate authorization to contact them*.
3. For optional ESA v1, either keep excluded or review and sign off the paired-release sensitivity scope before accessing source-semantic content.
4. For OPS-SAT v2, review publication notice implementation and any file-specific restrictions without assuming that two CSV files lack in-band notices; avoid re-running large archive scans.
5. Only **after** source-rights signoff, notice implementation, and a separately recorded G4-06 author authorization may a new source-semantic execution be considered. A future PR merge still requires distinct approval.

**This review is an evidence-based research governance assessment, not legal advice or a third-party rights-holder permission letter.**
