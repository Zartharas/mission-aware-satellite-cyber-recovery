# Study 10 — targeted file-rights provenance and exception-disposition evidence

**Study:** S10-RSEI-001; standalone research paper.  
**Record date:** 2026-11-23 UTC (date-only).  
**Status:** `TARGETED_FIRST_PARTY_PROVENANCE_REVIEW_COMPLETE; FILE_RIGHTS_SIGNOFF_HOLD`.  
**Authorization:** The sole author authorized targeted resolution of the outstanding member-specific rights evidence condition, **or preparation** of a prospective governance change if that condition could not be satisfied. The authorization did **not** approve a specific new policy text, remove a frozen gate, permit original-source semantics, external rights-holder outreach, PR merge, or manuscript submission.

## Controlling distinction

The immutable G2 Option B receipt, `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac`, records `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`, `rights_clearance_for_source_data=false`, and requires (1) ESA v2 release/file rights signoff, (2) ESA v1 signoff **only if its optional paired comparison runs**, (3) OPS-SAT v2 data rights/third-party notices disposition, (4) versioned source identity and notices, and (5) separate G4-06 execution authorization.

The sole author's **completed, exact** limited-use/residual-uncertainty acceptance is recorded in draft PR #246, `study10/G4_LIMITED_SOURCE_USE_AUTHOR_ATTESTATION_APPROVAL_20261123.json`, Git blob SHA-1 `92d0bfc3d6b52d2e0d78169577c8e4a433bafd54`. The author **explicitly declined G4-06** and will not be asked to repeat this same attestation.

This targeted review seeks **positive, file-and-release-linked licensing/provenance authority** in the official published materials, not impossible proof from a negative string search that no restriction could exist anywhere.

## Evidence by exact published release

### G4-01 — ESA Anomaly Dataset v2: strong direct release provenance

**Exact versioned release:** https://zenodo.org/records/15237121, DOI `10.5281/zenodo.15237121`; public metadata displays **European Space Agency** as the publisher, with three source creators tied to **ESA/ESOC**, **KP Labs** and **Airbus**:

- De Canio, Gabriele (ESA/ESOC), Kotowski, Krzysztof (KP Labs), Haskamp, Christoph (Airbus Germany).
- `ESA-Mission1.zip` MD5 `9770ad12ed730238f37c42d5c27ab436`.
- `ESA-Mission2.zip` MD5 `bfc72012691427d9327eb41f726ce45e`.
- `ESA-Mission3.zip` MD5 `d63943f09c81378acd9fc5e565ecc66e`.

The official ESA repository `esa/anomaly-dataset` README at pinned commit `a969698e464788c961dbb646d3da24595c7c7a2b` (README blob `76f66a4550d0d8d3910b595d1c968bde9bbabed6`) states that the dataset comes from the ESA/ESOC, Airbus and KP Labs consortium and is provided for academic and industrial research. Its LICENSE Git blob `e9603f00725a6580a4c82ac6ada160a13f53f323` identifies **CC BY 3.0 IGO** and the README links the **v1** DOI; those v1 files alone would not prove v2.

**Crucial direct v2 link:** the project-maintained `kplabs-pl/ESA-ADB/data/preprocessed/esa-anomaly-dataset-metadata.json` (Git blob `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`) declares **CC BY 3.0 IGO** for the dataset and explicitly identifies the **v2** Zenodo DOI and **the same three original v2 ZIP MD5s**. The dataset-author paper independently describes data-level CC BY 3.0 IGO rather than erroneously adopting the benchmark software's MIT terms. This is direct affirmative dataset/release/file-identity evidence, not merely an “open” badge or inferred software license.

**Remaining uncertainty:** No official source checked here expressly warrants that **every embedded ZIP member** is exception-free from third-party rights or operational/contractual caveats. The version-linked project declaration covers the **dataset as publicly published**; its ability to confer permission for independently held third-party material cannot be proved by this source-document review. There is **no identified contrary notice** in the bounded local checks. Do not equate `NO_CONTRARY_NOTICE_FOUND_IN_BOUNDED_SCOPE` with `EXCEPTIONS_ABSENT_PROVEN`.

**Assessment:** `PUBLISHED_RELEASE_AND_LICENSE_GRANT_STRONGLY_SUPPORTED; MEMBER_RIGHTS_EXCEPTION_DISPOSITION_NOT_UNCONDITIONALLY_ESTABLISHED`. No further routine ESA request merely to confirm the CC BY license name is needed or authorized. **G4-01 HOLD.**

### G4-02 — ESA Anomaly Dataset v1: first-party release plus explicit repository license

**Exact version:** https://zenodo.org/records/12528696; DOI `10.5281/zenodo.12528696`. The official ESA README at the pinned commit explicitly links this DOI to the three-mission dataset, identifies the consortium's provenance, and the co-located `LICENSE` specifies **CC BY 3.0 IGO**. Source authorship and dataset provenance therefore have affirmative public, first-party support, distinct from code licensing. Existing frozen local integrity/rights directory reports are scoped to the source's three version-pinned archives.

**Remaining uncertainty:** The direct project license is broad but does not provide a third-party ownership/exception warranty for every ZIP member. Optional ESA v1 is still **only** `RQ-E3` paired mission/channel/field release sensitivity; it does not add primary strata, independent spacecraft, or independent trials.

**Assessment:** `PUBLIC_LICENSE_LEVEL_ELIGIBILITY_SUPPORTED; MEMBER_EXCEPTION_DISPOSITION_PENDING_IF_USED`. **G4-02 HOLD_IF_USED**; it cannot be silently converted into a fifth primary stratum or used without the applicable pre-G4 rights conditions.

### G4-03 — OPS-SAT-AD v2: exact file names, data-inclusive MIT and ESA-involved acquisition

**Exact versioned release:** https://zenodo.org/records/15108715, DOI `10.5281/zenodo.15108715`. The public description **distinguishes**:

- `segments.csv`: telemetry signals acquired on ESA-operated OPS-SAT, published MD5 `72f109630abb933a386106897a631188`.
- `dataset.csv`: derived/extracted synthetic features over manually split and labeled telemetry segments, MD5 `5246fdc5e4630a4cecbf7fb6bc8b795e`.
- `LICENSE`: published MD5 `ea8befa9af2b37b7a54b5a16fc3712b0`.
- The versioned record also publishes `dataset_generator.ipynb`, `modeling_examples.ipynb` and `requirements.txt` **outside the frozen Study 10 allowlist**. Do not add or retrieve them merely because public.

The actual published `LICENSE` in the **same v2 deposit**, also mirrored by `kplabs-pl/OPS-SAT-AD/LICENSE` Git blob `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`, reads **MIT License for OPS-SAT Dataset**, `Copyright (c) 2024 KP Labs`, and the permission expressly applies to **“software, data and associated documentation.”** This is significantly stronger than inferring rights from a software-only GitHub MIT badge. Full copyright-and-permission text is required for any future distributions of copies or substantial portions of covered material.

The benchmark paper's first-party author-contributions statement identifies **B.R. and D.E. as having acquired the source data**. Its affiliations identify **D.E. with European Space Agency/ESOC**, and its acknowledgements describe ESA-funded projects. The paper documents operator-assisted selection/curation and public deposition of the nine telemetry channels. This corroborates **ESA-involved creation/public research dissemination**, not a separately signed NASA/ESA/KP Labs licensing or ownership transfer. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12041257/ (Data Records, Acknowledgements, Author contributions, Code availability); official deposit as above.

**Material caveat:** Acquired raw OPS-SAT `segments.csv` comes from an **ESA-operated spacecraft**, while the explicit data-inclusive MIT text names **KP Labs**. ESA team participation and public deposit make licensed distribution plausible but do **not independently establish the full chain of title**, or a separate assignment from ESA to KP Labs, for all raw telemetry. The publication's MIT **code-availability** sentence must **not** replace the more applicable deposit's data-inclusive license. The publisher article's CC BY 4.0 license covers the *article*, **not automatically the dataset**.

**Assessment:** `DATA_INCLUSIVE_MIT_GRANT_AND_ESA_COAUTHOR_ACQUISITION_PROVENANCE_POSITIVE; MEMBER_THIRD_PARTY_RIGHTS_EXCEPTIONS_NOT_INDEPENDENTLY_CERTIFIED`. No contradiction discovered, but neither an explicit ESA-to-KP Labs data licensing grant nor an exception-free file declaration was found. **G4-03 HOLD.**

## Bounded local evidence and limits

Previous rights-only V2/V3 Mac checks covered **26/26 identified leading CSV preamble candidates** with **zero recognized notice markers**. Their negative finding is valid *only for those comment/prefix regions*. The full V2 sanitized report was independently hashed SHA-256 `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb`; V3 report SHA-256 `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8` remains **author-reported only**. There are no independently verified full-CSV checks for unobserved rights clauses, and no implication that the 2,090 nested container inventory reviewed every member's contents.

The present assessment **did not open any additional original CSV/ZIP telemetry data**, query user-local archives, contact a rights holder, or create new scientific results. Public release pages, first-party GitHub README/license/metadata and the benchmark authors' public manuscript were the evidence searched.

## Resolution decision and next admissible path

1. **Affirmative evidence threshold reached for dataset-license identity and release-linked provenance:** YES for ESA v2, ESA v1 and OPS-SAT v2. Exact versioned files and license links are independently supported; author approval of the planned local, non-redistributing use and residual uncertainty has already been separately signed in PR #246.
2. **Mandatory frozen Option B member/file-specific third-party rights signoff:** **NOT ESTABLISHED BY THESE SOURCES**. There is no *identified* conflicting term, but source-level licenses and an author attestation cannot logically prove the absence of every independently owned embedded item. A strict interpretation requiring an affirmative exception-free warranty cannot be satisfied from this evidence.
3. **Do not repeat the same author attestation or scan the entire archives.** The unresolved issue is *evidence sufficiency*, not missing acceptance of uncertainty, missing license names, or a compression bug.
4. Two permissible next routes exist **only with proper separate authority**:
   - **Evidence-first:** If new first-party, version/file-specific notices or author/rights-holder statements explicitly address an actual material exception or grant, evaluate that narrow evidence; no generic “please confirm license” email is necessary. Do not contact a rights holder without separate authorization.
   - **Prospective governance clarification candidate:** A new, forward-looking signoff standard could accept documented release/file-linked public grants, affirmative provenance, absence of **identified** contradictory terms, sole-author bounded-use acceptance, documented unknowns, and strict stop-on-discovery, **without falsely certifying exception-free content**. This changes the current strict evidence threshold and therefore **cannot be silently activated**. It requires a clearly dated, separate prospective author approval and explicit record of how the frozen rights gate is being amended or superseded for **future** source use. Preserve the original receipt and all prior evidence. A positive identified third-party restriction remains an absolute stop until resolved.

**Recommendation:** The second route is a reasonable candidate for limited local work because exhaustive proof of the nonexistence of every unknown third-party term is generally unattainable by scanning. This is a proposed *research governance evidence standard*, **not a license grant or legal conclusion**. No frozen G2/G3 changes, no gate clearances, no G4-06 authorization, and no publication are made in this PR.

**Gate disposition:** G4-01 `HOLD`; G4-02 `HOLD_IF_USED`; G4-03 `HOLD`; G4-04 `EXCLUDED_BLOCKED_IF_USED`; G4-05 `PARTIAL`; G4-06 `NOT_AUTHORIZED`.

**Design safeguards:** Four primary descriptive strata × eight variables = 32 classification slots; optional ESA v1 adds no trial and no independent replication. No retrospective cohort substitution.

This is a documentary research-governance and provenance assessment, not a legal opinion or independently issued permission by third-party owners.
