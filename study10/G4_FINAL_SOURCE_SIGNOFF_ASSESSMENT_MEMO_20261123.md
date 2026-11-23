# Study 10 — final source-specific rights signoff assessment (NOT a signoff)

**Study:** S10-RSEI-001; standalone research paper.  
**Review date:** 2026-11-23 UTC.  
**Outcome:** `DOCUMENTARY_ASSESSMENT_COMPLETE; FINAL_SOURCE_USE_SIGNOFF_WITHHELD`.

The sole author approved performing the source-specific **assessment** in this chat. No separate, explicit approval was provided to assert absent third-party rights, accept all unknown restrictions, clear frozen Option B gates, run G4-06, merge PRs, contact source owners, publish, or redistribute source data.

## Governing decision and exactly what was checked

The frozen receipt `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`, binds the policy `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD` and explicitly records `rights_clearance_for_source_data=false`. Pre-G4 requirements include (i) ESA v2 exact-release and third-party file-rights signoff; (ii) ESA v1 release rights/attribution **if** used; (iii) OPS-SAT v2 license notices and embedded third-party exceptions; (iv) pinned version identity and all notices; and (v) **separate** G4 scientific execution and source-use authorization.

Source documents inspected in GitHub include the exact PR #243 per-source residual-rights decision (Git blob `1593d5db46ce2741da46bd58ecbcd89af38848b2`) and the prospective notice template (Git blob `f475c5591457ecfbf731e932e43e65bd99b17cf9`). The first-party ESA repository LICENSE `e9603f00725a6580a4c82ac6ada160a13f53f323`, exact ESA v2 dataset metadata `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`, and OPS-SAT dataset LICENSE `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11` were reread from their GitHub sources.

The uploaded small, sanitized V2 report was independently matched to SHA-256 `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb`; the V3 terminal report hash `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8` remains **author-reported only**. Combined inspections covered **26 of 26 identified bounded leading CSV prefixes**, reporting **zero recognized rights-marker categories**. Prefix inspection explicitly stopped before interpreting CSV data rows. This establishes only the defined bounded test, not the absence of late notices, third-party rights, proprietary components, operational sensitivity, or reconstructability risk. No original telemetry bytes or V3 JSON report were uploaded in this assessment.

## Source-by-source proposed disposition

| Gate | Exact dataset | Supported permission and intended use | Unresolved **pre-G4** decision | Proposed outcome |
|---|---|---|---|---|
| **G4-01** | ESA Anomaly Dataset **v2**, DOI `10.5281/zenodo.15237121` (Missions 1–3) | Version-linked first-party **CC BY 3.0 IGO**. Three primary descriptive within-family mission strata. Local only, no raw rehosting or implied ESA endorsement. | Document exact intended member-level scope and any third-party exceptions; source-specific author signoff accepting only defensible residual risk; verify local source identity and applicable internal notices. | **HOLD**, not an assertion of conflicting license |
| **G4-02** | ESA Anomaly Dataset **v1**, DOI `10.5281/zenodo.12528696` | Official ESA README/license supports **CC BY 3.0 IGO**. Optional RQ-E3 paired `(mission, channel, metadata field)` sensitivity, never another spacecraft or fifth primary stratum. | If used: sign off v1 release/member rights and attribution. If not cleared, do not execute optional comparison; document pre-execution source ineligibility instead of altering primary outcomes. | **HOLD_IF_USED** |
| **G4-03** | OPS-SAT-AD **v2**, DOI `10.5281/zenodo.15108715` | Exact versioned **MIT License for OPS-SAT Dataset**, `Copyright (c) 2024 KP Labs`, expressly covering data. Fourth descriptive source stratum, local use, no original-CSV rehosting. | Explicit disposition of possible CSV member-level terms/third-party rights and author source-use signoff. Preserve applicable MIT and dataset DOI acknowledgement plan. | **HOLD** |

**Three affirmative findings:** source identity/documents are release-linked; dataset-level public license evidence exists; no specific conflicting license was observed in the 26 tested leading prefixes. **Three distinctions that must remain:** unknown rights are not verified absent; sole-author acceptance is not a grant from third-party owners; a non-redistribution plan does not make a future sensitive derived output automatically safe.

## Signoff decision rule — what author acceptance can and cannot do

An internal final source-use signature may approve an appropriately scoped, versioned research-use plan, assign responsibility for CC BY/MIT compliance, and document **residual unverified notices as uncertainty** where a legitimate source license covers the intended use and the controlling frozen conditions have an evidence-supported disposition. The sole author **cannot** transform unknown third-party rights into permissions or waive a positive material restriction. Under the current frozen Option B receipt, a missing, mandatory exact-member exception signoff remains a hold unless it is independently satisfied or a clearly dated, prospectively authorized change to the governing rights criteria is separately approved before semantic outcome inspection. This assessment does **not** amend those requirements.

**Stop conditions before any future original-source semantic analysis:** mismatch against frozen DOI or local file digests; newly identified restrictive/member license or proprietary third-party condition without a valid disposition; unauthorized source family, files or rights scope; missing operative attribution obligations; no G4-06 explicit execution approval. If a source is ineligible, record its ineligibility **before** learning the intended scientific endpoint. Do not replace the source post hoc to improve favorable coverage.

## Requirements that belong at publication time, not automatic local-use vetoes

The prospective notices are already drafted but have **not** been inserted into an actual post-study paper. Before submitting or publishing an eventual manuscript, cite only dataset versions actually used; credit ESA creators and license link and disclose relevant changes; verify OPS-SAT **v2** citation author metadata; cite the corresponding 2025 *Scientific Data* methodology DOI `10.1038/s41597-025-05035-3` and consider its correction DOI `10.1038/s41597-025-05751-w`; and retain the **full MIT copyright and permission notice** in any future copies or substantial portions of covered material. Independently screen every prospective non-raw result, table, figure or supplement for sensitive operational disclosure and source reconstruction. The absence of a final manuscript today is not proof that source-specific licensing permits scientific analysis; equally, there is no reason to pretend the future manuscript already exists.

## OPS-SAT versioned citation status

The exact Zenodo v2 page at https://zenodo.org/records/15108715 currently presents `Bogdan, Ruszczak` as the **creator** and `Ruszczak, Bogdan` as a **contributor**. Its methods paper gives **Bogdan Ruszczak**. The v2 citation/export API could not be retrieved through the available public interface during this assessment, so the current draft `Ruszczak, B.` remains **PROVISIONAL**. Record the inconsistency; do not silently swap metadata or invent an official export. Citation export resolution is required before final journal-ready references, but the creator display ambiguity is not by itself a new license prohibition.

## Explicit decisions still missing

1. **Source-specific residual-risk and member-rights disposition**, naming all three exact source DOIs, the limited local workflow, attribution requirements, any credible additional rights exception evidence and how each mandatory frozen condition is satisfied. A yes to **review** is not that independent signature.
2. If such a disposition cannot be supported, retain the hold, propose a narrowly scoped evidence check or separately authorized **prospective** amendment, and do not certify source rights as clear. No broad archive rescans or ESA email to reconfirm the dataset license name are required by this review.
3. **Only after the applicable pre-G4 requirements are actually satisfied**, obtain a new **explicit G4-06 scientific execution** approval. PR merge, new external outreach and manuscript submission are independently controlled.

The accompanying machine-readable record is `study10/G4_FINAL_SOURCE_SPECIFIC_SIGNOFF_ASSESSMENT_20261123.json`, with all six G4 gates `cleared=false`. The original frozen G2/G3 and every earlier draft PR remain unchanged. No original telemetry was processed for research, no dataset was published, no PR merged, and no scientific result claimed.

**Final disposition:** `FINAL_ASSESSMENT_COMPLETE; RELEASE_SPECIFIC_RIGHTS_SIGNOFF_NOT_ESTABLISHED; G4_06_NOT_AUTHORIZED`.

This is a documentary research-governance assessment, not a legal opinion or a third-party permission grant.
