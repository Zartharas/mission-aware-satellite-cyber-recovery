# Study 10 — G4-05 current identity and prospective-notice preflight result

**Study:** S10-RSEI-001 (Paper 5).  
**Local check timestamp from report:** 2026-11-23T05:21:59.653981+00:00 (2026-11-22 23:21:59 CST).  
**Result:** `G4_05_CURRENT_CHECK_PASS_NOT_EXECUTION_AUTHORIZED`.  
**Scope:** Read-only local dual-hash identity and prospective notice-plan check, **not** G4-06 scientific source processing, archive member inspection, final publication notice attestation, or PR merge.

## 1. Evidence provenance — independent report hashing vs Mac execution

The author executed the previously approved G4-05 standalone bundle from the Mac against a clean, detached GitHub checkout of exact PR #248 head `dfce2b9a620cd93911b0729462664b3b6b4560ea`. The terminal shows the bundle's SHA-256 verified `a4694ff9acd3c99f63850361fcc653ec940ce2a08e6ba59c8b836153896fcdf3`; internal file hashes passed; all **15 synthetic tests passed**. It then reported **9/9** source file dual-hash identity PASS and **10/10** documentary notice-plan checks passing.

The sole author supplied the **sanitized local JSON report** to ChatGPT, `Study10_G4_05_Identity_Notice_Current_Preflight.json`. The assistant independently read the uploaded file and recomputed its **exact SHA-256** as:

`4a035980a8f10e60f5a645071761088e45e062827c4e974d3fca43a1d26f7bfc` (**MATCH** with the author's Mac `shasum` output).

The JSON is 2,917 bytes. An independent structural validation of these **received JSON bytes** passed: exact study/schema, expected status, all nine expected source identifiers/statuses, every `MD5_and_SHA256_match_frozen_G2=true`, exact ten notice checks and their truth values, expected pinned Git document identities, and all non-execution/future-recheck safeguards.

**Critical provenance limit:** The original nine source ZIP/CSV/LICENSE files remain only on the author's Mac. The assistant **did not** independently read or rehash the original dataset files, witness the Mac's system execution, independently validate the local disk state, or receive raw dataset bytes. The verified local JSON **reports** these check results; its exact bytes and consistency are independently verified. Do not describe the Mac-source hash results as independently reproduced in the assistant's environment. The complete sanitized local report is **not committed** to GitHub; only this report SHA-256, aggregate results and source IDs are committed. No personal Mac source file paths are committed.

## 2. Nine original G2 source identities — Mac report

| Source file identifier | Whole-file published MD5 + frozen author SHA-256 match |
| --- | --- |
| `ESA_M1_v1` | `PASS_FROZEN_DUAL_HASH` |
| `ESA_M1_v2` | `PASS_FROZEN_DUAL_HASH` |
| `ESA_M2_v1` | `PASS_FROZEN_DUAL_HASH` |
| `ESA_M2_v2` | `PASS_FROZEN_DUAL_HASH` |
| `ESA_M3_v1` | `PASS_FROZEN_DUAL_HASH` |
| `ESA_M3_v2` | `PASS_FROZEN_DUAL_HASH` |
| `OPS_V2_dataset.csv` | `PASS_FROZEN_DUAL_HASH` |
| `OPS_V2_segments.csv` | `PASS_FROZEN_DUAL_HASH` |
| `OPS_V2_LICENSE` | `PASS_FROZEN_DUAL_HASH` |

**Reported: 9/9.** The report records `original_archive_members_decompressed=false`, `original_csv_rows_parsed=false`, `original_payload_uploaded=false`, and `scientific_analysis_approved=false`. This is a whole-file byte-identity check, **not a new analysis of individual archive members**.

The author-local source-check tool also matched the exact frozen G2 manifest SHA-256 `2eb2cb1ec3a49de3ff61bd7bb1a4d186a45d6fddf7da98ec79d18f0dee9b4210`, frozen G2 receipt Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`, approved prospective R1 record Git blob `812fd538b0fa5e8970996a8224c424d8dc8b7342`, signed limited-use author attestation Git blob `92d0bfc3d6b52d2e0d78169577c8e4a433bafd54`, and prospective source-notice plan Git blob `f475c5591457ecfbf731e932e43e65bd99b17cf9`.

## 3. Ten current prospective-notice-plan checks

The local JSON lists **all ten** documentary checklist checks as `true`: ESA CC BY 3.0 IGO license URI; ESA non-endorsement and disclosure of changes; ESA v1 conditional DOI; ESA v2 DOI; OPS-SAT MIT copyright; full MIT permission notice if redistribution of copies or substantial portions ever occurs; OPS-SAT v2 DOI; future manuscript publication audit reserved; no premature assertion of actual dataset use; and a no-raw-telemetry-redistribution plan.

This establishes that the **pinned prospective notice plan** contains those provisions. It does **not** establish license exception-free content, complete legal rights, final bibliographic correctness, or notices in an actual manuscript. The source-use dataset-level rights evidence is already conditionally assessed using the separately approved prospective `G4_RIGHTS_STANDARD_R1`; that decision is not altered here.

## 4. G4 gates following this current checkpoint

| Gate | Current reported status | Future requirement |
| --- | --- | --- |
| `G4-01` ESA v2 | `R1_EVIDENCE_PASS_CONDITIONAL` | Stop for any newly observed conflicting restriction; keep version/notice identity |
| `G4-02` ESA v1 | `R1_EVIDENCE_PASS_CONDITIONAL_IF_USED` | Only optional matched release sensitivity; not an additional primary stratum |
| `G4-03` OPS-SAT v2 | `R1_EVIDENCE_PASS_CONDITIONAL` | Respect data-inclusive MIT and no original telemetry redistribution |
| `G4-04` Hack-A-Sat 4 | `EXCLUDED_BLOCKED_IF_USED` | Do not add without separate authorization |
| `G4-05` identity/notices | **CURRENT PREFLIGHT PASS at 2026-11-23 05:21:59 UTC; gate still partial** | Exact source/hash and notice **recheck at any future separately authorized execution boundary**; actual publication notice review later |
| `G4-06` scientific execution | **`NOT_AUTHORIZED`** | A new, separate explicit author approval required; none inferred |
| GitHub PR merges | **NOT AUTHORIZED** | Independent explicit approval; no merge or deployment |

**Why G4-05 stays partial:** A point-in-time PASS is meaningful and should not be discarded or re-run needlessly now. It **cannot** prove file identity at an unknown future time, final manuscript notice implementation, source-member exception-free rights or independent scientific validation. It records a completed **current checkpoint**, not a lifetime grant.

Original frozen G2 Option B receipt and G3 are unchanged. Prospective experimental design: **four primary descriptive strata × eight recovery-state variables = 32 slots**; ESA v1 is optional paired-release sensitivity, not a fifth independent stratum. No source-to-variable classification, scientific observations, G3 parity test, telemetry export, PR merge, publication or submission was performed.

**Final:** `CURRENT_G4_05_EVIDENCE_VERIFIED; FUTURE_EXECUTION_BOUNDARY_RECHECK_REQUIRED; G4_06_BLOCKED`.

Record companion: `study10/G4_05_CURRENT_PREFLIGHT_VERIFIED_LOCAL_EVIDENCE_METADATA_20261123.json`.

This document is a scoped evidence and research-governance record, not a legal opinion, a license grant, or a claim that original telemetry content is exception-free.
