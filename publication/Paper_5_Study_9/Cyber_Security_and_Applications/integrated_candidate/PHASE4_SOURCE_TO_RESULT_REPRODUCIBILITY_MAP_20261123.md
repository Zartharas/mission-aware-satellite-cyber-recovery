# Paper 5: Source-to-result reproducibility and assurance map

> **Phase 5 immutable pin update:** G3 audit branch resolved to `04317102b87eb63312ba4e1599f87a3971858d03`; the sanitized derived JSON review snapshot is `e8e9bd7a6d60d32eb9a03e83b1eba59a010bb7c1`. See [read-only replay recipe](PHASE5_RETAINED_EVIDENCE_REPLAY_RECIPE_20261123.md) for exact paths, reproduction boundaries and no-redistribution guard.


**Prepared:** 2026-11-23; **purpose:** remedy AR-06 without reopening Study 9 or 10 science, or implying possession of withheld source bytes.  
**Scope:** GitHub-visible scripts and derived records, author-reported original-source verifications, and source release citations.  
**Status:** `REPRODUCIBILITY_PATHS_DOCUMENTED__ORIGINAL_SOURCE_REEXECUTION_NOT_CLAIMED`.  
**Repository:** [Zartharas/mission-aware-satellite-cyber-recovery](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery), draft [PR #255](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/255).

## 1. Strictly separate evidence and validation classes

| Evidence class | What was verified | What is **not** established |
|---|---|---|
| **A. Frozen source of design** | Study 9 protocol, mapping rubric, policy scope and Study 2 selector are pinned in Git history; Study 10 G2 content-addressed receipt identifies its exact design. | A repository branch name by itself is not a protected immutable tag, an external registry timestamp, or evidence that previously inspected schema were blind. |
| **B. Frozen derived evidence** | Study 9 deterministic outputs and Study 10 sanitized JSON hashes, record counts, mapping keys and exclusions are checked in PR CI. | Successful checks against stored JSON do **not** independently reconstruct earlier author-local source inspection or prove the adjudicator's substantive classification correct. |
| **C. Source authenticity** | Source DOIs identify intended ESA/OPS releases; earlier author-local source hashes and bounded archive-directory evidence are recorded with their provenance. | The author-terminal-only ESA outer-layout report hash has not been rehashed from uploaded report bytes. Original nested ESA telemetry, OPS rows, and withheld channel-level matched records are not available to this PR for fresh inspection. |
| **D. Interpretation** | Manuscript explicitly conditions conclusions on the fixed eight-predicate interface, four selector policies and bounded metadata/header audit. | No operational spacecraft recovery decision, authorization effectiveness, all-mission absence, generalization, or cross-source independence is established. |
| **E. Publication readiness** | Exact-head LaTeX, source-label traceability and repository checks can validate the compiled candidate. | Neither PDF build nor AI-assisted critique replaces author's final page proof, content/originality approval or rights and publisher declarations. |

## 2. Exact scientific pins and trace paths

| Role | Link / immutable identifier | Interpretation |
|---|---|---|
| Frozen Study 9/Study 2 repository baseline | [Baseline tree at `5ee451c2a739cbca7dc948d49239d985c6b4cc07`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/tree/5ee451c2a739cbca7dc948d49239d985c6b4cc07) | Prior accepted scientific baseline; **do not mutate**. |
| Study 9 canonical mapping | [`study9/results/S9-RTSI-001_CANONICAL_RUN_20260914/mapping_matrix.json`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/blob/5ee451c2a739cbca7dc948d49239d985c6b4cc07/study9/results/S9-RTSI-001_CANONICAL_RUN_20260914/mapping_matrix.json) | Git blob SHA-1 `d8dc66111c6a7ecb9135028337d0cfc3dbbcff51`, 24 frozen source-predicate rows. Git blob SHA-1 is **not** an independently computed SHA-256 source-file digest. |
| Study 9 controls | `study9/STUDY9_PROTOCOL.json`, `study9/SEMANTIC_ADJUDICATION_FREEZE.json`, `study9/RECOVERY_STATE_MAPPING_RUBRIC.json`, `study9/POLICY_SCOPE_FREEZE.json`, and `study2/src/study2_security/selectors.py`, all from the pinned baseline tree. | Normative decision interface and four frozen policies; source fields cannot be silently promoted after seeing results. |
| Study 10 prospective G2 freeze receipt | [`study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/blob/study10/s10-rsei-001-g2-freeze-receipt-20261122/study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json) | Internally approved freeze receipt points to content-addressed protocol payload `8ed6a2b16233b86bf91672f6f15605dcf906c5eb`. The G2 design froze four ESA-v2/OPS primary descriptive strata; Hack-A-Sat remained secondary and unpooled. |
| Study 10 G3 synthetic/oracle audit | [`study10/s10-rsei-001-g3-post-parity-audit-g4-hold-20261123`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/tree/study10/s10-rsei-001-g3-post-parity-audit-g4-hold-20261123/study10) | 18 synthetic cases, 22 tests and 1,024 policy-oracle input comparisons, **not** flight action testing. Use the immutable commit pinned by the G3 audit if replaying, not an unprotected moving branch. |
| Source-to-mapping supplemental representation | `PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex` and `PHASE2_FIELD_LEVEL_EVIDENCE_SUPPLEMENT.tex` in PR #255. | Editable publication copy of 24+32 mapping/class/evidence-role rows, not a substitute for canonical JSON or independent human adjudication. |

## 3. Three archived Study 10 derived results and exact byte digests

All three files are *verbatim author-uploaded sanitized derived JSON*, with original byte count and SHA-256 recorded in `study10_derived/README_MANIFEST.json`. Git blob SHA is a separate content identity for the repository copy.

| Result | Bytes | Original SHA-256 | Git blob SHA-1 |
|---|---:|---|---|
| `study10_derived/S10_G4_TierA_32Slot_PublishedSchema.json` | 82,059 | `f727bc80823d9fe5a47d44c361b9aefcdadc6b5a144331f2857079ce91508d1c` | `70aeac2fe4c35ad22ea3e1509020945bd939d871` |
| `study10_derived/S10_G4_TierC_16_StratumPolicy_NonEvaluable.json` | 18,060 | `93dd4f92810a33f0dbe13dd11f842f732a4ccc9fac322a762fcab557185623f6` | `92ae9aa1febe6643e23dd4ee9cc17936e22a85b1` |
| `study10_derived/S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json` | 8,206 | `ba343e858b4d54256f8f4d8b118bb87a95a49a0d99baebc394ac5517c418ddc9` | `130654b45349a1c5b75db87cede938860a189522` |

The separate `study10_derived/README_MANIFEST.json` (Git blob SHA-1 `614fb27e5317128ae971a53f6f099d619f02ba1c`) explicitly prohibits uploading original telemetry and the author-local matched metadata-detail CSV. The `validate_phase0_science.py` and `validate_phase2_editorial.py` scripts validate frozen-science anchors and individual source-field/mapping markers, but **do not** authenticate the original ESA data by direct source reexecution.

## 4. Source release/rights and comparison units

| External public source | Role | Unit / access boundary | Rights and identity qualification |
|---|---|---|---|
| [ESA Anomaly Dataset v2](https://doi.org/10.5281/zenodo.15237121) | Three Study 10 primary source strata | 12 versioned metadata tables in total across three missions, bounded outer ZIP directories; no nested telemetry opened. | First-party dataset author/version-linked evidence reports CC BY 3.0 IGO; the readable v2 Zenodo rights panel is not explicit. Dataset-level license statements do not prove absence of third-party file-specific exceptions. |
| [OPS-SAT-AD v2](https://doi.org/10.5281/zenodo.15108715) | One Study 10 primary descriptive source stratum | Two CSV first-line headers only; original rows not inspected for a recovery-state witness. No independence assumption relative to anonymized ESA mission identities. | Source `LICENSE` reports MIT for dataset/software; no original bytes redistributed by this PR. |
| [ESA Anomaly Dataset v1](https://doi.org/10.5281/zenodo.12528696) | Optional within-family paired metadata sensitivity only | 224 matched channels; 896 shared metadata cells (842 equal, 54 different `Physical Unit` annotations). `Categorical` is a v2-only column of 224 observations. | Same released mission lineage, **not** a fifth independent stratum; 54 differences do not prove unit conversion or recovery mapping class change. |
| CuCD-ID v3, AegisSat 2025, UNSW-IoTSAT 2026 | Three frozen Study 9 populations | Exact source populations 25,000 / 137,965 / 404,798 rows; each projects to an all-unknown fixed eight-predicate state. | Canonical source identity/hashes reside in the frozen Study 9 run; third-party raw bytes excluded from this manuscript PR. |

## 5. What a third party could and could not reproduce

**From PR alone:** SHA-256 checks of the archived S10 derived JSON, study-specific frozen count and class assertions, all 56 mapped source-field/class/visibility-role markers, four-policy synthetic result references, and LaTeX source/PDF build. These are genuine *reproducibility-of-records* checks.

**Requires external public data and separate permission:** Obtain exact releases, verify original bytes against source-record/hash evidence, rerun the bounded metadata extraction and source-to-predicate semantic adjudication under the frozen rubric, and compare to the original report. Do not infer that public availability of a release automatically makes every use/redistribution lawful.

**Not reproducible from current project materials:** Original local ESA matched channel-detail CSV, the author terminal-only outer-layout JSON bytes, uninspected nested mission telemetry, inaccessible onboard/ground authorization histories or any real-flight decision time and evidence-validity witness.

**Publication wording rule:** `INDEPENDENTLY_HASHED_ARCHIVED_DERIVED_OUTPUTS` must never be described as `INDEPENDENTLY_REEXECUTED_SOURCE_DATA_EXPERIMENT`; `NOT_EVALUABLE` is not an observed zero operational recovery success rate. No universal claim of dataset inadequacy or spacecraft-security failure follows from this audit.

## 6. Review and approvals

**Reproducibility mapping documentation:** `COMPLETE_WITH_PROVENANCE_EXCEPTIONS`.  
**Independent reconstruction of original author-local inspection:** `NOT_PERFORMED / NOT_CLAIMED`.  
**Original source archive redistribution:** `NOT_AUTHORIZED`.  
**Sole-author scientific acceptance and final source-rights/publisher approval:** `PENDING`.  
**PR merge or journal submission:** `NOT_AUTHORIZED`.
