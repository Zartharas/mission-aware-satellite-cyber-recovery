# Study 10 — approved prospective G4_RIGHTS_STANDARD_R1 and source-by-source eligibility

**Study:** S10-RSEI-001; standalone Paper 5 research.  
**Approval record date:** 2026-11-23 UTC (day precision only).  
**Current result:** `R1_APPROVED_PROSPECTIVELY; THREE_SOURCE_LICENSE_ELIGIBILITY_CONDITIONAL_PASS; G4_05_PARTIAL; G4_06_NOT_AUTHORIZED`.  
**Change scope:** New additive documentary prospective standard and adjudication only. No edits to frozen G2/G3, original source telemetry, research results, old rights matrix or future manuscript.

## 1. Exact author approval, instrument and non-authorization

Sole-author response, verbatim:

> I approve the prospective G4_RIGHTS_STANDARD_R1 evidence standard for future source-rights eligibility decisions, while preserving the original frozen G2 record. I do not authorize G4-06 or PR merges.

This explicitly approves the proposed `G4_RIGHTS_STANDARD_R1` in `study10/G4_PROSPECTIVE_MEMBER_RIGHTS_EVIDENCE_STANDARD_CANDIDATE_20261123.json`, pinned Git blob SHA-1 `bed4f5969467f38801f4ad21b0e9ca0976a933c2` from draft PR #247. This is a **new** prospective evidence-standard decision, not another request to approve the already-signed limited source-use attestation. The author's earlier approval of narrow scope and uncertain third-party rights was separately recorded in `study10/G4_LIMITED_SOURCE_USE_AUTHOR_ATTESTATION_APPROVAL_20261123.json`, Git blob `92d0bfc3d6b52d2e0d78169577c8e4a433bafd54`, draft PR #246.

**Author expressly withheld G4-06 execution and all PR merges.** The statement does not authorize source-semantic telemetry processing, synthetic G3 runs, raw-data distribution, rights-holder contact, manuscript submission or science results. No rights from external licensors are invented.

## 2. Frozen receipt preservation and exact prospective effect

Original frozen receipt: `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`, original Option B `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`, original `rights_clearance_for_source_data=false`. **The original receipt and old gate matrices remain unmodified.** Nothing is retroactively described as cleared at the original G2 freeze.

For **future** rights eligibility decisions only, the approved R1 clarification establishes a **different evidence threshold**. It permits a qualified local-use decision on a precise versioned source if all of the following are supported: trusted publisher/maintainer; positive first-party data-level license; match to exact published release/file identity; explicit treatment of all **identified** restrictive notices; limitation of negative-marker statements to the scope observed; exact signed sole-author restricted-use/risk and stop-condition acceptance; applicable attribution/notice plan; mandatory local identity check and separate G4-06 authorization at the execution boundary; and strict stop-on-new-rights-conflict/security/privacy/hash failures.

R1 **does not require impossible universal proof** that no undiscovered exception exists, **but** this change cannot override a real third-party restriction, prove chain of title for independently owned data or create any permission. An identified source-member conflict is a hard stop until specifically resolved. The boundary is **non-redistributing, local/offline analysis**, not spacecraft operations or generalized license clearance.

This decision is recorded **in an unmerged GitHub draft branch**. Its effect is prospective author-approved research-governance evidence and a draft source rights verdict, **not a main-branch deployment or merge**.

## 3. Source-specific R1 evidence outcome

| Source, exact release | Positive file/release license provenance | Approved documentary rights status under R1 | Remaining boundary |
| --- | --- | --- | --- |
| **G4-01 ESA v2**: DOI `10.5281/zenodo.15237121`; three original mission ZIPs | Author-maintained ESA-ADB Croissant metadata directly links **CC BY 3.0 IGO** to v2 Zenodo DOI and all three exact ZIP MD5s; ESA publisher/ESOC, KP Labs and Airbus creators | `R1_EVIDENCE_PASS_CONDITIONAL` | Local hashes, release check and applicable notices immediately before any later separately approved G4 execution; stop on any positive conflicting member restriction |
| **G4-02 ESA v1**: DOI `10.5281/zenodo.12528696` | Official ESA repository LICENSE specifies **CC BY 3.0 IGO**, and its README points to exact v1 release; author accepted v1 **only for optional RQ-E3 paired release sensitivity** | `R1_EVIDENCE_PASS_CONDITIONAL_IF_USED` | Pre-result optional inclusion, version/hash preflight if used, v1 attribution; never treat as fifth primary source or replication |
| **G4-03 OPS-SAT v2**: DOI `10.5281/zenodo.15108715`, only `dataset.csv`, `segments.csv`, `LICENSE` | Exact v2 deposited LICENSE is **MIT License for OPS-SAT Dataset, Copyright (c) 2024 KP Labs**, expressly licensing `software, data and associated documentation`; published MD5s link version and files; public paper corroborates ESA-associated data acquisition | `R1_EVIDENCE_PASS_CONDITIONAL` | No proof of every member's exception-free rights or ESA→KP Labs title chain; respect any newly observed conflict, preserve MIT notice when copies/substantial covered material are distributed in a separately authorized future artifact |

**First-party file pins, rechecked:** ESA v2 Croissant metadata Git blob `9da81fadbaf96cdfd2c7d8c5b906f4d45f80f461`; official ESA v1 LICENSE `e9603f00725a6580a4c82ac6ada160a13f53f323` and README `76f66a4550d0d8d3910b595d1c968bde9bbabed6`; OPS-SAT project MIT LICENSE `6cba1d0ee3e2c245b7664a3bcb169afd3297ab11`. The public v2 Zenodo pages display the exact dataset DOIs and file hashes: https://zenodo.org/records/15237121 and https://zenodo.org/records/15108715.

**Bounded local notice evidence:** 26/26 known candidate **leading CSV prefixes** examined by the prior local V2/V3 rights-only program, zero recognized markers in that bounded region. The sanitized V2 JSON hash `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb` was independently checked; the V3 JSON hash `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8` is **author-reported only**. Do not claim every original file or third-party right was examined. The officially published source/license plus signed limited-use attestation, **not a negative prefix scan**, are the affirmative basis for conditional R1 documentary eligibility.

**OPS-SAT methodological caution:** its upstream README points at an earlier concept/deposit DOI; for v2 use the exact Zenodo v2 DOI and pinned deposited `LICENSE`, not a generic repo link or code-only MIT presumption. The Zenodo creator/contributor displayed name order for OPS-SAT remains inconsistent; `Ruszczak, B.` is provisional pending a trustworthy version-specific export before journal-ready references. This is a **citation** gate, not by itself a file-rights restriction.

## 4. Historical gates versus new prospective R1 findings

| Gate | Historical frozen-G2 state (still recorded unchanged) | Prospective R1 documentary adjudication | Does this authorize original-source semantic work? |
| --- | --- | --- | --- |
| G4-01 | `HOLD` | `R1_EVIDENCE_PASS_CONDITIONAL` | **No** |
| G4-02 | `HOLD_IF_USED` | `R1_EVIDENCE_PASS_CONDITIONAL_IF_USED` | **No** |
| G4-03 | `HOLD` | `R1_EVIDENCE_PASS_CONDITIONAL` | **No** |
| G4-04 | `EXCLUDED_BLOCKED_IF_USED` | **Excluded**, unchanged | **No** |
| G4-05 | `PARTIAL` | `PARTIAL_PREFLIGHT_AND_ACTUAL_NOTICE_SCOPE_PENDING` | **No** |
| G4-06 | `NOT_AUTHORIZED` | **NOT_AUTHORIZED**, expressly rejected in latest approval | **No** |

The term `R1_EVIDENCE_PASS_CONDITIONAL` means the **rights-documentation evidence threshold is satisfied for limited prospective eligibility under the newly approved R1 standard**. It does **not** mean unconditional permission for all contents, completion of the **G4-05 execution identity preflight**, retroactive clearance of frozen G2, or scientific execution.

## 5. Mandatory stops and subsequent checkpoints

1. Before any separately authorized source-semantic execution, recheck exact locally available frozen source identities, archived MD5/SHA-256, code/source pins and applicable internal attribution/notice requirements. If the identity or license scope changes, **stop**; do not use an unapproved newer release as a substitute.
2. If a new file-level restrictive notice, credible ESA/KP Labs third-party rights conflict, private operational content, reconstructability/privacy risk or source mismatch appears, **stop the affected source** and record a new, evidenced disposition. Author risk acceptance never overrides third-party rights.
3. **G4-05 remains partial** until the future execution-boundary identity/notice preflight is actually evidenced. A proposed or approved plan is not a completed future preflight.
4. **G4-06 is not authorized.** No original telemetry schema/row semantic analysis, source-to-eight-variable classification, or operational recovery outcomes can be computed now. The original G2 receipt also records G3 synthetic parity as unexecuted; this R1 decision does not silently approve or execute G3.
5. Later scholarly publication requires precise versioned citations, appropriate CC BY 3.0 IGO attribution/non-endorsement and changes notice, OPS-SAT MIT copyright/permission compliance if substantial material is distributed, a source-data availability statement grounded in **actually used** releases, and a separate sensitive output review. No manuscript has been submitted or authorized for submission.
6. Keep **four primary descriptive strata × eight variables = 32 prospective classification slots**; ESA v1 is conditional paired release sensitivity, not an extra independent sample.

**Final result:** The sole author has approved the *prospective* R1 rights evidence standard. Three source releases meet its **documentary license-level eligibility conditions, conditionally**. The source execution identity/notice preflight and all scientific/performance questions remain untouched. No GitHub PR is merged, no frozen G2/G3 artifact is changed, and no G4-06 approval is inferred.

This is research-governance evidence, not an independent legal opinion, rightsholder warranty or grant of third-party rights.
