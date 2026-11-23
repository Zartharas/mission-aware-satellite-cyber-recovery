# Study 10 (S10-RSEI-001) — source-by-source intended-use and residual-rights decisions

**Record date:** 2026-11-23 UTC  
**Disposition:** `CONDITIONAL_INTENDED_USE_RECORDED; FINAL_RIGHTS_SIGNOFF_WITHHELD`  
**Scope:** Standalone Paper 5 / Study 10 paper; documentary governance review only; no new raw telemetry or semantics processed.  
**Authority:** the sole author stated **“yes, I authorize”** in response to the recommendation to document a **source-by-source residual-rights and intended-use decision** after the G4 V2/V3 evidence addendum. This authorizes recording these prospective scope decisions and review findings. It does **not** imply the author specifically accepted unknown legal restrictions, certified third-party rights, approved G4-06, or permitted merging or external correspondence.

## 1. Controlling protocol and evidentiary separation

The controlling G2 Option B rights policy is `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`, recorded in `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json` (Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac`). Its hard fail-closed requirements include exact ESA v2 release scope and third-party file rights signoff, ESA v1 rights/attribution **if used**, OPS-SAT v2 notices and third-party exceptions, versioned identity checks, and **separate explicit G4 scientific execution and source-use approval**. The policy's `rights_clearance_for_source_data=false` is not replaced by an informal statement that open-source licenses exist.

The existing prospective research unit remains **four descriptive primary source strata × eight recovery-state variables = 32 classification slots**. ESA v2 Missions 1–3 are within the same curated source family. OPS-SAT is a distinct named source family, **not proven an independent spacecraft sample from anonymized ESA missions**. ESA v1 is **not** another stratum, only conditional RQ-E3 paired release sensitivity. Unfavorable/absent semantic outcomes cannot justify post-outcome dropping a primary stratum; eligibility/right-to-use questions must be decided before semantic outcome exposure.

The documentary sources support **ESA dataset-level CC BY 3.0 IGO** for both releases and a **data-inclusive MIT license** for OPS-SAT v2. They do not prove all contained materials lack third-party restrictions, privacy concerns, operational security limitations, or source-member-specific notices.

## 2. Evidence from completed bounded local checks

- **V2 uploaded report:** independently verified SHA-256 `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb`. The JSON states 23 of 26 leading CSV prefixes examined, zero recognized license-notice markers, and three ESA v2 Deflate64 codec gaps.
- **V3 Mac terminal output:** author reported three specific v2 Deflate64 prefixes successfully examined; all show `failure_code=NONE`, `markers={}`, and `PREAMBLE_SAMPLE_DONE_NOT_RIGHTS_CLEARED`. Its JSON SHA-256 `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8` is **author-reported only** because V3 report bytes were not provided. The recorded V3 ZIP package SHA-256 is a different artifact and does not independently verify the V3 JSON.
- Combined **26/26 identified leading CSV prefixes** were examined to the permitted bounded limit: ESA v1 12/12, ESA v2 12/12, OPS-SAT v2 2/2. No recognized marker categories appeared in these prefixes; **zero is a bounded observation, not universal proof of unrestricted use**.
- The earlier 2,090 nested ZIP count is **directory inventory**, not inspection of every payload member. The new decision does **not** require a repeat of prior large-file scans or access to real telemetry.

Thus, there is **no positive conflicting license statement detected within this narrow review scope**, but **unknown embedded notice status remains unknown**. No statement of exception-free rights is supportable.

## 3. Decision G4-01 — ESA Anomaly Dataset v2

**Exact source and scientific role**

- DOI: https://doi.org/10.5281/zenodo.15237121; official release published April 17, 2025; source creators Gabriele De Canio, Krzysztof Kotowski, Christoph Haskamp; publisher European Space Agency.
- Three pinned original ZIPs: `ESA-Mission1.zip` MD5 `9770ad12ed730238f37c42d5c27ab436`, `ESA-Mission2.zip` MD5 `bfc72012691427d9327eb41f726ce45e`, `ESA-Mission3.zip` MD5 `d63943f09c81378acd9fc5e565ecc66e`.
- **Conditional intended use:** after all source-rights and G4 execution gates are satisfied, locally analyze only the frozen versioned source/schemas for the eight native operational recovery-state fields; output source-specific descriptive classification and absent/unknown limitations, not mission safety or active-operations claims.
- No raw-data rehosting, unauthorized cross-dataset joins, synthetic substitution into native-evidence claims, or independent-mission replication assertion.

**License and applicable conditions**

First-party ESA-ADB machine-readable metadata (Git blob SHA-1 `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`) directly links the **three v2 ZIP filenames and MD5s** to **CC BY 3.0 IGO**, https://creativecommons.org/licenses/by/3.0/igo/; dataset authors independently identify the dataset-level license in their preprint. This is stronger evidence than merely the older ESA v1 repository LICENSE. The v2 Zenodo Rights UI rendering is blank and does not itself defeat this affirmative record. The author has **rejected routine rights-holder contact solely to re-confirm the license name**.

Cite the exact v2 creators/title/DOI, link the CC BY 3.0 IGO license, give changes/derivatives disclosure where applicable and full methodological transformation disclosure, preserve source notices and avoid any implication ESA or consortium endorses this research. The license does not by itself confer separately held privacy, moral or third-party intellectual-property rights. Do not silently change CC BY 3.0 IGO to a different Creative Commons version.

**Residual-rights decision:** `RETAIN_AS_PRIMARY_DESIGN_CONDITIONALLY; SOURCE_USE_HOLD`. No conflicting terms observed in inspected leading prefixes, but member-level and late in-band notices remain unassessed; output sensitivity and reidentification/reconstructability review will be required. No final release/member rights signoff is recorded.

## 4. Decision G4-02 — ESA Anomaly Dataset v1

**Exact source and scientific role**

- DOI: https://doi.org/10.5281/zenodo.12528696; v1 release June 25, 2024.
- Official ESA repository `esa/anomaly-dataset`, pinned commit `a969698e464788c961dbb646d3da24595c7c7a2b`, README specifically links the v1 DOI and its `LICENSE` (Git blob SHA-1 `e9603f00725a6580a4c82ac6ada160a13f53f323`) specifies **CC BY 3.0 IGO**.
- **Conditional intended use:** RQ-E3 paired `(mission, channel identifier, metadata field)` v1–v2 release sensitivity only; no independent mission or sample count; no fifth primary stratum.
- The author expressly approved retaining this optional comparator in draft PR #239, but **did not approve processing source semantics or claim complete file-specific rights clearance**.

**Residual-rights decision:** `RETAIN_OPTIONAL_PAIRED_COMPARATOR_CONDITIONALLY; HOLD_IF_USED`. The v1 leading prefixes have no recognized markers within the bounded scan, but late/in-band exceptions remain unknown. If v1 cannot satisfy its applicable rights/notice conditions, **do not run v1 sensitivity**. Such exclusion must be documented as a pre-execution eligibility result, not hidden, treated as a new independent sample, or used to improve primary outcomes. No retrospective cohort substitution.

## 5. Decision G4-03 — OPS-SAT-AD v2

**Exact source and scientific role**

- DOI: https://doi.org/10.5281/zenodo.15108715; displayed as version v2. Four-stratum primary design uses OPS-SAT as the **fourth distinct source-family stratum**, but does not assume population-independent spacecraft replication from the anonymized ESA archives.
- Frozen local source allowlist: `dataset.csv`, `segments.csv`, and `LICENSE` only; the Zenodo deposited record additionally lists `dataset_generator.ipynb`, `modeling_examples.ipynb`, and `requirements.txt`. Their availability is **not** authorization to add them to the study.
- Explicitly no raw OPS-SAT original telemetry rehosting and no automatic publication of non-raw but potentially reconstructable operational material.

**License and scholarly notices**

The exact v2 `LICENSE`, https://zenodo.org/records/15108715/files/LICENSE?download=1, mirrored in the upstream GitHub `LICENSE` (Git blob SHA-1 `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`), is titled **MIT License for OPS-SAT Dataset**, `Copyright (c) 2024 KP Labs`; it explicitly covers software, **data** and associated documentation. It requires the original **full copyright and permission notice** in copies or substantial portions of covered material; DOI credit alone is not a substitute if such material is distributed. Journal methodological paper: https://doi.org/10.1038/s41597-025-05035-3; related correction: https://doi.org/10.1038/s41597-025-05751-w. These are **paper citations**, not substitutes for the dataset license.

The author's existing draft PR #240 approved the **prospective MIT attribution and no-raw-redistribution plan**, not data processing, original CSV exception clearance, or manuscript publication.

**Versioned citation anomaly:** Zenodo v2 currently displays creator `Bogdan, Ruszczak`, contributor `Ruszczak, Bogdan`, whereas the methods paper identifies **Bogdan Ruszczak**. The normalized draft author form `Ruszczak, B.` is plausible but is explicitly **provisional**. An accessible, exact v2 Zenodo/DataCite citation export has **not** yet been independently obtained; do not misrepresent journal-ready metadata. The record's display `Published June 24, 2024` and technical `Created March 30, 2025` are distinct fields, not evidence that the dataset year was authoritatively corrected.

**Residual-rights decision:** `RETAIN_AS_PRIMARY_DESIGN_CONDITIONALLY; SOURCE_USE_HOLD`. The two CSV leading preambles contained no recognized notice markers; this does not eliminate later in-band restrictions, special third-party rights or sensitive telemetry risks. Internal attribution, complete notice inclusion when relevant, versioned citations and an output-specific reconstructability/security review are all required. No final source-use signoff is recorded.

## 6. Explicit adversarial and compliance assessment

| Failure mode | Present evidence | Mandatory handling |
| --- | --- | --- |
| A restrictive notice appears later in a CSV or nested member | Bounded preambles cannot rule it out | Never claim zero exceptions; classify `UNKNOWN`; stop and escalate a **positive** conflicting notice before reading further or claiming reuse |
| Dataset license is confused with benchmark-software license | ESA authors distinguish data CC BY vs code MIT | Keep source-specific licenses pinned; never apply MIT code license to ESA telemetry |
| Privacy, aerospace operational sensitivity or reconstructable derived data | Open license does not prove safe disclosure | Local use scope only after rights gates; independent actual-figure/table/supplement publication check |
| Researcher's risk acceptance is mistaken for a third-party license grant | No rights-holder-specific member signoff exists | Author may approve a documented residual risk treatment **only where the frozen rights requirements and legitimate license scope are supported**; author assent cannot manufacture rights |
| Dataset version/filename/hash drift | Frozen manifest and source hashes exist | Recheck exact frozen identities before any future G4 scientific execution |
| Weak or false independent-replication inference | ESA missions same source; OPS source independence unverified | Maintain 4×8 descriptive units; no pooled independent-spacecraft claims |
| Versioned author metadata discrepancy | OPS record internally inconsistent | Pin discrepancy and verify exact version citation export before final bibliography; do not silently “correct” |
| Attribution prewritten as if experiment already executed | Notices remain prospective | Never claim telemetry was analyzed or results produced in current paper; check any actual manuscript after authorized G4 |

There is **no need for another broad nested archive or original-data scan at this checkpoint**. If a narrowly defined, genuinely necessary file-member exception check is proposed in future, separately authorize that bounded content access and preserve evidence provenance. A rights-gate signoff must not be obtained by declaring all unknowns `NONE`.

## 7. Signoff status and exact next decision

| Gate | Decision | Cleared? |
| --- | --- | --- |
| G4-01 | `HOLD` — v2 ESA documentary license confirmed; exact member-rights and residual-risk acceptance not signed | **No** |
| G4-02 | `HOLD_IF_USED` — v1 paired comparator conditionally retained; rights not signed for use | **No** |
| G4-03 | `HOLD` — OPS v2 data MIT and notice plan supported; CSV exceptions and author acceptance outstanding | **No** |
| G4-04 | `EXCLUDED_BLOCKED_IF_USED` — Hack-A-Sat optional secondary excluded | **No** |
| G4-05 | `PARTIAL` — 26/26 **bounded-prefix** subcheck complete; actual notices/signoff not final | **No** |
| G4-06 | `NOT_AUTHORIZED` — no real-source semantic experiment without separate author approval | **No** |

**What has been decided:** The intended limited-use roles remain fixed and conditional; observed licensing evidence is supported; author approval to document this residual-rights decision is recorded; no observed contrary rights statement in tested prefixes. **What has not been decided:** Unqualified source-use acceptance under frozen G2, whether unexamined file rights meet its strict exception clearance criteria, whether any final manuscript actually satisfies notice rules, or a new G4-06 grant.

A future author signoff should explicitly identify **each source DOI, permissible local use, attribution and no-raw-redistribution commitment, known restrictions (none detected in bounded scope), unknown exceptions (not proven absent), and why that disposition satisfies—not bypasses—the frozen pre-G4 source-rights requirements**. If no defensible disposition is available, keep the source-specific hold and document a prospective pre-result amendment or exclusion without outcome manipulation. A separate explicit G4-06 authorization and a separate PR merge authorization remain mandatory.

**Final status:** `DOCUMENTARY_SOURCE_BY_SOURCE_DECISIONS_RECORDED; NO_SOURCE_RIGHTS_GATE_CLEARED`.

**Linked evidence:** `study10/G4_V2_V3_RIGHTS_PREAMBLE_EVIDENCE_METADATA_20261123.json`, `study10/G4_V2_V3_RIGHTS_EVIDENCE_AND_RESIDUAL_SIGNOFF_REVIEW_20261123.md`, and the prior author approvals in draft PRs #238–#240. No raw data, complete local reports, secrets, or unpublished original members are included.

*Research governance and license-documentary analysis only; not a legal opinion or assertion of new rights granted by third parties.*
