# S10-RSEI-001 — G2 Canonical Preregistration Protocol Candidate

**Working title:** Recovery-State Semantic Observability Across Public Real-Flight and Space-Cyberchallenge Records  
**Status:** `G2_CANDIDATE_UNFROZEN_NOT_PREREGISTERED`  
**Date of candidate preparation:** 2026-11-21  
**G1 basis:** Sole-author conditional acceptance `AUTHOR_ACCEPT_G1_FOR_G2_CONSIDERATION`, PR #228 reviewed at `7fc0ee788cf69e4955abb5354fcc100b43ca4b9a`, approved-record head `6cb2d1976f65cef0509329c59207b0e9d5c47681`.  
**Frozen comparator:** Study 9 and Study 2 contracts at main commit `5ee451c2a739cbca7dc948d49239d985c6b4cc07`. These files are **read-only**, not newly frozen here.

> **This is a prospective draft for the author's next decision, not an executed study or a protocol freeze.** Prior schema, counts, headers and release-metadata exposure occurred before this proposed freeze and must be disclosed. No selector test or dataset endpoint is computed in this phase.

## 1. Aim, scope and scientific boundary

Evaluate whether four **descriptive source strata** provide operationally interpretable native fields for the eight recovery-state variables from frozen Study 9. This assesses **semantic observability/structural applicability**, not spacecraft recovery safety, cryptographic assurance, actual cyberattack detection, authorization success, or population-generalized mission efficacy. All-zero, absent, ambiguous, unknown and not-evaluable outcomes are valid results; the protocol must never be modified to increase favorable coverage after looking at source-field outcomes.

The original merged `study10/PROSPECTIVE_PROTOCOL_DRAFT_20261121.md` was **not** preregistered or frozen. It used the provisional phrase “Candidate independent real-flight cohort” for OPS-SAT and discussed two human reviewers or a checker “where feasible.” Those phrases are **superseded** for this future candidate: OPS-SAT is a **distinct named source family with unverified independence from anonymized ESA missions**, and **sole-author signed review plus a separately implemented technical checker** is the internal governance model. Keep the original historical draft unchanged.

## 2. Frozen-candidate cohort definitions and descriptive units (not yet frozen)

| Proposed stratum | Release and source | Reported channels | Design unit | Independence interpretation |
|---|---|---:|---|---|
| ESA-ADB mission 1 | v2 `10.5281/zenodo.15237121` | 76 | One eight-variable semantic classification vector | Same curated ESA source family |
| ESA-ADB mission 2 | Same v2 release | 100 | One eight-variable vector | Same curated ESA source family |
| ESA-ADB mission 3 | Same v2 release | 48 | One eight-variable vector | Same curated ESA source family |
| OPS-SAT-AD | **v2** `10.5281/zenodo.15108715` | 9 | One eight-variable vector for the source stratum; 2,123 reported segments and 303,493 samples are **not** independent semantic trials | Named separate source; mission/telemetry overlap with anonymized ESA archives **unverified** |

There are **4 proposed strata × 8 variables = 32 prospective classification slots**, NOT independent samples/experiments. The ESA three mission strata total **224 reported channels**. No across-source pooled denominator, confidence interval, hypothesis test, or spacecraft-independent replication claim is permitted. Keep all four strata even if any yield zero direct operational fields, subject only to **pre-result** eligibility and rights decisions.

**Paired sensitivity:** ESA-ADB v1 `10.5281/zenodo.12528696` only as matched `(mission, channel, metadata field)` comparison against ESA v2; no independent trial count. **Secondary:** Hack-A-Sat 4 contest files at Git commit `2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1`, unpooled and not presumed flight telemetry. **Deferred:** NASA SMAP/MSL. No post-outcome cohort substitution without a dated protocol amendment and separate approval.

## 3. Research questions and fixed observation hierarchy

Retain the research questions from the original draft, **RQ-E1** native semantic observability, **RQ-E2** descriptive source-family contrast, **RQ-E3** matched ESA release sensitivity, **RQ-E4** conditional bounded action identifiability, and **RQ-E5** synthetic-control correctness. The RQ-E2 contrast is explicitly descriptive, **not** an independently sampled flight-mission population estimate.

- **Tier A primary:** `(source family, release, stratum, recovery-state variable)` mapping class and source-visibility role. Emit the eight-element vector, `DIRECT` count (0–8), `DIRECT+DERIVABLE_BY_PREDECLARED_RULE` count (0–8), each fraction with denominator eight, and `AMBIGUOUS`/`ABSENT` counts. Do not conflate ambiguity with a known-false Boolean.
- **Tier B paired sensitivity:** Per-mission matched channel/metadata differences, with counts predeclared; a changed outer ZIP CRC/size does **not** prove nested payload byte change. Keep paired data release comparisons within family.
- **Tier C conditional:** Only if a native decision-point and evidence validity window are defensible, enumerate the admissible Boolean completions and action sets **separately for each of four primary policies**. A singleton action set indicates only *structural identifiability*, not correct/safe recovery. Unsupported decision time yields `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION`, without row-level identifiability percentages.
- **Tier D methodology only:** Compare future synthetic mapping/selector implementation with a separately implemented technical oracle. Synthetic cases do not contribute to Tier A/B/C empirical denominators.

Reporting is finite-population and descriptive unless a **pre-outcome** author amendment supplies defensible sampling assumptions. No significance test or source-family generalization is preregistered.

## 4. Frozen semantic contract (reuse without modification)

Use exactly the eight interface values in this order:

`signature_valid`, `source_trusted`, `fresh`, `epoch_valid`, `contradictory`, `minimum_evidence_complete`, `security_signal`, `authorization_available`.

Use exactly the four frozen adjudication classes `DIRECT`, `DERIVABLE_BY_PREDECLARED_RULE`, `AMBIGUOUS`, `ABSENT`. Visibility: `OPERATIONAL_NATIVE`, `OFFLINE_GROUND_TRUTH_ONLY`, `EXPERIMENT_METADATA_ONLY`, `DOCUMENTATION_ONLY`. The proposed deterministic-derivation registry is **empty**; any addition requires separate prospective rule, justification and pre-results author approval.

All **ten** `minimum_evidence_complete` criteria from the frozen Study 9 semantic file must be present, current and accepted. The exact list and meanings are pinned in the manifest, not reinterpreted as CSV completeness. Do not infer signature validity from CRC, trust from APID, freshness from timestamp alone, epoch from sequence, contradiction from sensor anomaly, native security signals from offline labels, or authorization from command presence. An `unknown` is not `false` and must not be coerced to an input Boolean. No operational source adjudication is asserted by this draft.

A future source-to-variable record must preserve all nine frozen rubric fields (source/dataset, variable, mapping class, evidence role, exact native fields, source schema citation, derivation rule if any, rationale, uncertainty). Operational availability must be **at the documented decision point**; if absent, forbid a row-level action conclusion.

## 5. Primary policy selector contract and controls

Four primary policies only, in frozen Study 9 order: `S2_B0_FAIL_CLOSED`, `S2_B1_FAIL_OPERATIONAL`, `S2_B2_RISK_THRESHOLD`, `S2_S1_EVIDENCE_AWARE`. Exclude `S2_ABL_NO_FRESHNESS`, `S2_ABL_NO_CONTRADICTION`, `S2_ABL_NO_EPOCH`, and `S2_ABL_NO_SIGNATURE_TRUST` from all primary endpoints. Do not pool or average policy-specific action identifiability.

Retain `S10_SYN_P0_V3_DRAFT`: ten distinct **synthetically assumed** accepted current claims linked one-to-one to ten required values, all eight expected normalized inputs; inclusive synthetic verifier temporal rule `issued_at_s <= now_s <= issued_at_s + valid_for_s`. **This is a state-interface stub, not a performed Ed25519 verification**. Retain all **18 prospectively specified G1 positive, negative and boundary cases**; the exact rows are in the pinned G1 semantic-control document. Six manually reasoned selector-action scenarios are static *expected cases*, **not** separate implementation or test success.

**Future G3, not executed now:** A standalone oracle written without importing the frozen selector, then an explicit comparison to that selector and fail-closed tests for missing/unknown/contradictory inputs, complete mutation set, eight-value order and four-policy enumerations. Require parity and traceable discrepancies before source-data/G4 work. No external human reviewer is required by the solo-author internal governance.

## 6. Data handling, rights and preexisting evidence

The companion G2 rights document defines release-specific CC BY 3.0 IGO author statements for ESA and the data-inclusive MIT notice for OPS-SAT v2; **v2 ESA metadata rights scope and final citation/notices remain pending**. No original telemetry ZIP/CSV/third-party material is committed or redistributed. Prior OSS release MD5 and author-reported SHA evidence, and existing schema/count exposure, are explicitly nonblind pre-freeze evidence. The OPS paper/intake 1,494 versus 1,594 training-segment discrepancy remains open; do not change counts to fit the source prose. Verify rights and dataset identities before use; prevent source mixing and accidental cross-family pooling.

### Author-approved Option B — design freeze is separate from rights-to-use clearance

The sole author selected `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD` on November 21, 2026 local (November 22 UTC), **solely as the G2 rights-gating policy**. A future, independently authorized G2 freeze may lock the **prospective design** notwithstanding unresolved file-specific source-rights questions, **only if** the frozen protocol retains these unresolved matters as hard, fail-closed **pre-G4** conditions. This selection does **not** freeze the current candidate, make a legal determination, approve original telemetry access, authorize G3 synthetic execution, authorize G4 processing or publication, or permit either draft PR to merge. Source release identity, exact versioned license scope, third-party exceptions, attribution/notice requirements, and separately approved G4 scientific execution must be confirmed **before any real dataset inspection/processing beyond the already disclosed historical intake**. If any condition cannot be satisfied, stop and seek a prospective amendment and separate author approval.

## 7. Exclusion, stopping, deviation, and reproducibility rules

Stop before source-row observation or action endpoint if source ZIP/CSV identity changes; nested archive validation fails; license/rights applicability is unresolved; exact release source differs from manifest; a native decision point is missing for Tier C; a frozen rubric/policy/source hash changes; synthetic positive or negative controls fail future G3; an unauthorized derivation is proposed; or a new cohort is contemplated after G2.

For an ambiguous or absent field, record a supported verdict and justification; **do not discard the source** to raise coverage. For source or method adjustments after G2, preserve the previous freeze record and create a dated, separately authorized prospective deviation. No undocumented retroactive edits after endpoint exposure.

A reproducibility record for future G2 must pin exact repository commit, Git blob identities for each normative file, the dataset/version MD5 and user-reported SHA identifiers with their provenance, exact fixture and 18-case set, environment and tool versions (future G3), and required author signoff. Git blob SHA-1 values identify Git objects, **not** independently computed SHA-256 file digests. The companion manifest is a **candidate, not immutable freeze**.

## 8. Solo-author review and sequential gates

- **G1:** `AUTHOR_ACCEPT_G1_FOR_G2_CONSIDERATION` **conditional** for A1–A5, based on PR #228. This is not a source-license sign-off, final population freeze or G2 signature.
- **G2:** `HOLD`. Author must review exact rights/notice and cohort treatment, confirm this canonical candidate and manifest, identify remaining conditions, pin new immutable candidate content/UTC timestamp, and **separately approve** a freeze action.
- **G3:** `CLOSED`. Separate future authorization for *synthetic-only* implementation and parity checks, before real source data.
- **G4:** `CLOSED`. Separate authorization for source-field semantic adjudication after G2/G3; with source rights and operational-visibility evidence.
- **G5/G6:** `CLOSED`. Conditional row-level work and publication each require further authorization and claim-boundary audits.
- **PR merge:** `NOT AUTHORIZED`. This document branch must not bypass G1's four-file PR scope or merge itself into `main`.

**Freeze decision requested by this document:** `NONE`. **Author freeze authorization:** `FALSE`. **Scientific execution:** `FALSE`. **Publication submission:** `FALSE`. No dataset semantic result or recovery-safety finding has been produced.

## 9. Pre-freeze methods and reporting contract — candidate for separate author decision

This section makes the already proposed estimands and boundaries operationally checkable **before future source-row or mapping endpoint inspection**. It is **not a freeze** and does not establish that any ESA, OPS-SAT or Hack-A-Sat field actually satisfies the rules. The sole author must explicitly accept the final version of these commitments in a later G2 decision.

### 9.1 Fixed analysis frames and count rules

| Tier | Prospective input frame | Required primary output | Valid denominator and limitations |
|---|---|---|---|
| A, primary | Four candidate source strata × the exact eight frozen variables | Eight mapping-class/visibility-role records per stratum; counts of `DIRECT`, `DERIVABLE_BY_PREDECLARED_RULE`, `AMBIGUOUS` and `ABSENT` | For **operational direct coverage**, numerator is the count of `DIRECT` with role `OPERATIONAL_NATIVE`; for operational direct-or-derivable, include `DERIVABLE_BY_PREDECLARED_RULE` **only** with `OPERATIONAL_NATIVE`; denominator **8 within each stratum**. These are **32 classification slots**, not independent spacecraft trials |
| B, sensitivity | ESA v1 and v2 channel metadata paired by matching (mission, channel identifier) | Channel matching and metadata-change count, semantic change only when documented meaning changes | Within-mission paired metadata records; never count paired releases as replicated spacecraft or infer nested telemetry-byte equality from ZIP directory metadata |
| C, gated | Only a later-authorized, native, decision-time documented state projection | Per `(source stratum, primary policy)`, full admissible action set and singleton/ambiguous outcome | **No** operational-row denominator or action-identifiability rate where native decision time or required variable semantics are unsupported. A singleton reachable-action set is structural, not safe or correct recovery |
| D, synthetic-only | The ten-claim positive fixture and the **18 total proposed control cases (including the unchanged P0 baseline)** | Later G3 mapping/selector outputs against a separately implemented oracle and explicit failure trace | Never counted toward Tier A/B/C source coverage or actual flight evidence |

**Mapping-class handling:** `AMBIGUOUS` is not `DIRECT` or `ABSENT` by default. An `ABSENT` verdict requires a reproducible **frozen schema inventory**, not merely failure to search for a field. Presence of a source `security_signal`-like label is insufficient without a documented operational guard. The derivation registry stays **empty** unless prospectively amended **before** the relevant source-field endpoint inspection, with explicit author approval; adding a favorable derivation post hoc is prohibited. Frozen Study 9 semantic rules are reused for their meaning, but the external Study 10 datasets require their own later evidence-based classifications; **Study 9 per-dataset results must not be copied as Study 10 outcomes**.

### 9.2 Dataset eligibility and missingness

Eligibility is decided from an exact *versioned source identity*, availability of a reliable published schema and a lawful intended use, all before semantic outcome inspection. Missing permission or unreadable/invalid original files must be recorded as a **pre-execution failure** and may lead only to an author-approved prospective source amendment. Lack of the eight recovery-state fields is a **legitimate source result**, never a reason to drop a source after examining semantic coverage. No rescue by external telemetry joins, synthetic metadata, inaccessible provider claims, or retrospective attack labels. Report the complete per-stratum classification vector and missingness rationale even for zero-coverage source strata whenever legally eligible.

### 9.3 Future bounded-action evaluation

Use the four primary frozen selector policies in their exact order without pooling. For any genuinely eligible decision-time state, let unresolved fields take every admissible Boolean completion consistent with **documented operational evidence**, and calculate the **set of distinct actions** for each policy; do not project a unique action if multiple completions disagree. **UNKNOWN** is retained at the Study 10 evidence interface and never silently passed as `False` to the Boolean Study 2 selector. If an operational decision time is absent, report `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` instead of computing fictitious row-level rates; mathematical all-unknown state sensitivity may be discussed only as explicitly synthetic/theoretical.

### 9.4 Audit and preregistration timing

The previously inspected ESA ZIP directory metadata and OPS-SAT schema, counts and anomaly labels predate the proposed G2 freeze. They are **declared exposure**, not prospective blind outcomes. This protocol is **not preregistered retroactively**. The future freeze record must capture an actual post-approval UTC timestamp, protocol content identity and commit/tag pins, and preserve all older draft Git histories. Publish/report any future source exclusion, stop, deviation, method change or unexpected license restriction without altering an existing frozen record.

**Current disposition:** `PROPOSED_FOR_G2_AUTHOR_REVIEW`. No endpoint computed; no immutable freeze created; no source-use approval granted.

## 10. Sole-author paper framing and G2 method acceptance (not a protocol freeze)

**Intended scholarly output:** This study is a **standalone research paper** for a potential peer-reviewed journal or conference, **not** a dissertation, thesis, dissertation chapter or doctoral degree deliverable. The project workspace name does not define the scientific output. Study 2 and Study 9 provide pinned, cited conceptual and implementation dependencies; this paper has its own RQ-E1–RQ-E5, prospective methods, dataset rights, observations and limitations. It must not reuse earlier results as if newly observed. The target journal/conference remains unselected and no submission is authorized.

**Recorded author decision:** In response to an explicit recommendation to accept `G2-P01` through `G2-P09` as the prospective methodological contracts (with approved Option B rights-gating retained, and separate `G2-P10` approval for actual freezing), the sole author answered: **“Yes, I approve.”** The author additionally confirmed the **research-paper, not dissertation** framing. Approval is recorded as of **2026-11-22 UTC (date-only)**.

**Effect:** `G2-P01`–`G2-P09` are **accepted as the candidate design and future freeze procedure**, without treating any deferred rights, integrity, immutable-hash or executable test as completed. `G2-P09` acceptance applies to the procedure for a future acyclic receipt, **not** to a receipt already created. `G2-P10` remains **unapproved**. The live Git draft is still mutable and unfrozen. G3 and all real-data/source, redistribution, merge and publication gates remain closed.
