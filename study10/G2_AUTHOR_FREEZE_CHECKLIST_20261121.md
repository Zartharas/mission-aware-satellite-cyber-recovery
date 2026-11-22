# S10-RSEI-001 — G2 Pre-freeze Author Decision Checklist

**Status:** `CHECKLIST_OPEN_NO_FREEZE_DECISION`. Use together with the G2 protocol candidate and manifest on the separate **stacked** draft PR. The author is the sole reviewer; no external reviewer is required for this internal research process. All unchecked items below are future actions or review questions, not performed work.

## Source and rights
- [ ] Confirm ESA v2 exact release and scope of its author-declared CC BY 3.0 IGO rights for intended **local analysis** and future publication; record any exceptions and the required contributor attribution.
- [ ] Confirm release-specific notices for ESA v1, OPS-SAT v2 (data-inclusive MIT), and path-level Hack-A-Sat secondary data if used.
- [ ] Confirm six ESA reported ZIP checksums and OPS-SAT v2 local CSV checksum identities are the **prospective selected files**, while openly documenting no exhaustive inner archive integrity testing.
- [ ] Preserve the existing OPS-SAT article/data discrepancy (1,494 vs 1,594 training segments), without resolving it opportunistically.

## Cohort and semantics
- [ ] Explicitly adopt four descriptive source strata, **not** four independent spacecraft replications; no pooling or cross-source mission-level confidence intervals.
- [ ] Keep matched ESA v1 release sensitivity separate, Hack-A-Sat secondary unpooled, NASA SMAP/MSL deferred.
- [ ] Agree that unknown source semantics, inaccessible decision times and zero coverage do not justify post-hoc source exclusions.
- [ ] Affirm the eight frozen Study 9 variable meanings, the ten required recovery criteria, four mapping classes, source-visibility roles, **empty derivation registry**, and four frozen primary Study 2 policies.
- [ ] Confirm `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` rule and policy-stratified action estimands; no inferred native decision time.

## Synthetic technical control and provenance
- [ ] Approve the precise `S10_SYN_P0_V3_DRAFT` *state-interface-only* premise as **synthetic** (not a cryptographic attestation or empirical output).
- [ ] Approve the 18 cases and expected static action table as a **future test plan**, retaining tri-state unknown/false differentiation.
- [ ] Agree that future G3 test oracle must be separate code, and any failed parity will halt G4. G3 has **not** been authorized or run.
- [ ] Pin the eventual candidate source/code/spec file digests, generator and environment versions, source dataset identities and exact UTC freeze timestamp. The current JSON file contains preliminary Git blob SHA-1 IDs; a future atomic freeze must pin its own immutable content.

## Protocol integrity and authorization
- [ ] Disclose prior source metadata/labels/schema exposure. Never represent G2 as preregistered before those earlier inspections.
- [ ] Review stop rules, expected denominator, exclusion rules, protocol deviation policy and source-rights controls.
- [ ] Record a separate **explicit G2 author decision** (approve freeze / revise / block) after all G2 prerequisites; the conditional G1 approval does not do this.
- [ ] Independently authorize any future G3 code execution, G4 source-field adjudication, dataset access, PR merge or publication. No such authorization is inferred here.

**Current overall G2 readiness:** `HOLD`. This checklist was drafted, not completed or signed. Nothing here authorizes data extraction, source telemetry processing, synthetic selector execution, repository merges, Study 9 changes or manuscript submission.

## Internal G2 pre-freeze assessment (static assistant review, NOT sole-author sign-off)

**Review target:** PR #229 candidate at `8c4bae227073f24fc66e7d3bda0ac5d6dca37f6b` (prior to this assessment-only documentation update), stacked on G1 head `6cb2d1976f65cef0509329c59207b0e9d5c47681`. **Assessment date:** 2026-11-21. This is analytical preparation requested by the author. It does not select `APPROVE_G2_FREEZE`, and it does not change any unchecked author-decision items above.

| Item | Evidence inspected | Analytical finding | Disposition |
|---|---|---|---|
| Canonical cohort interpretation | G2 protocol §2, G1 population decision, earlier non-frozen Study 10 draft | Four proposed source strata correctly separated; ESA v1 paired; Hack-A-Sat contest unpooled; no source-lineage independence assertion | `CONSISTENT_CANDIDATE_NOT_FROZEN` |
| Frozen semantics/policies | Exact frozen Study 9 semantic and policy JSONs, Study 2 file pins | Eight variables, ten required criteria, four primary policies and excluded ablations match source | `STATIC_PARITY_PASS` |
| Source reproducibility pins | All twelve Git blobs fetched from their pinned source commits | **12/12 exact Git blob SHA-1 IDs match**; this is source identity, not SHA-256 independently calculated for the G2 draft or original telemetry bytes | `SOURCE_GIT_BLOB_PIN_PASS` |
| Synthetic P0/mutations | G1 ten-claim fixture, ten required values and eighteen proposed cases | Appropriate as explicitly **unexecuted** design; G3 standalone implementation/parity must precede data work | `DESIGN_ONLY_G3_NOT_RUN` |
| ESA dataset licensing | ESA v1/v2 author license statements; official Zenodo v2 `https://zenodo.org/records/15237121`; official v1 `https://zenodo.org/records/12528696` | Authors' CC BY 3.0 IGO assertions are affirmative evidence; publicly rendered v2 Zenodo Rights section displays `License` **without an identifiable value**. Exact release scope, any exceptions and author acceptance remain unresolved; do not equate blank metadata with a prohibition | `RIGHTS_SCOPE_SIGNOFF_HOLD` |
| Attribution/third-party exceptions | Exact ESA Zenodo creator and contributor lists, G2 rights draft, OPS-SAT v2 MIT license evidence; Hack-A-Sat component exceptions | Creator names are recorded; final notice formatting, subcomponent rights and intended reuse scope not signed off | `ATTRIBUTION_SIGNOFF_HOLD` |
| Telemetry integrity | Published six ESA outer archive MD5s and author-reported SHA-256s, OPS-SAT v2 pair checks, earlier metadata inventory | Prior checks are evidence of source identity. **No exhaustive ESA inner-member integrity validation in this phase**, and OPS-SAT local files were not freshly rehashed by this review | `PRE_EXECUTION_SOURCE_CHECK_PENDING` |
| Prior source exposure and discrepancy | Study 10 historical protocol and provenance | Metadata, schemas, channel counts and offline labels observed prior to this future freeze; OPS-SAT paper's reported 1,494 training count versus prior intake's 1,594 is unresolved and cannot be optimized away | `EXPOSURE_DISCLOSED_DISCREPANCY_OPEN` |
| Atomic preregistration | Draft G2 protocol, candidate manifest, PR #229 branch | No immutable freeze-record SHA-256, exact future freeze commit, UTC decision event or author freeze verdict exists yet | `G2_FREEZE_NOT_AUTHORIZED` |
| CI | G1 run `44967559702`; PR #229 exact head `8c4bae227073f24fc66e7d3bda0ac5d6dca37f6b` GitHub Actions run `44968279176` | Both runs completed successfully at the time of the assessment. Generic CI does **not** test G2 scientific claims or independent selector parity | `REPOSITORY_CI_PASS_NOT_SCIENTIFIC_TEST_PASS` |

**Review recommendation:** `G2_REVIEWED_HOLD_PENDING_CONDITIONS`. The G2 **candidate is internally consistent** on source/policy identities and controls but is **not yet ready to be represented as frozen**. A separate explicit sole-author G2 approval, legally adequate source-use determination, final source/population treatment, and an atomic immutable freeze record are still required. G3 synthetic execution and G4 real-data analysis remain prohibited at this checkpoint.

**No impersonation of author sign-off:** This precheck is not the author's written decision. The user authorized reviewing the G2 candidate; that authorization must not be treated as `APPROVE_G2_FREEZE` or `MERGE_PR229`. All checklist boxes remain unchecked until personally affirmed or supported by a separate authorized validation event.

## G2 scope-sensitive rights decision (Option B policy **APPROVED**, protocol **NOT FROZEN**)

Additional first-party evidence was documented in the G2 rights candidate: ESA's own `esa/anomaly-dataset` `LICENSE` identifies CC BY 3.0 IGO and its README points directly to v1; the v2 dataset authors separately state CC BY 3.0 IGO for the introduced dataset. OPS-SAT v2 carries a checksum-matched data-inclusive MIT license. These findings strengthen the source license trail but do not establish complete file-level third-party rights or a completed sole-author sign-off.

**The sole author selected Option B by explicitly replying “yes, I authorize” to the question asking whether Option B should be recorded as the G2 rights-gating policy only.** The selection is recorded with date precision (November 21, 2026 local / November 22 UTC). The research design is **not** frozen and none of the general G2 freeze checklist boxes has been marked completed. The three alternatives are retained below for decision provenance.

| Option | Proposed G2 treatment | Effect on G3 and G4 |
|---|---|---|
| `A_HOLD_ALL_RIGHTS_BEFORE_G2_FREEZE` | Continue **G2 HOLD** until exact ESA v2 rights scope, contributor attribution, and all relevant exceptions are signed off | G3/G4 remain closed |
| `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD` | Permit a future **separately authorized** prospective G2 freeze **only after locking the protocol and immutable version/hash record**, while documenting unresolved archive file-specific rights as *pre-G4* stop rules; **no claim of rights clearance** | G3 synthetic-only work requires its own authorization; G4 source analysis stays blocked until rights and notices are signed off |
| `C_REVISE_OR_EXCLUDE_UNCLEAR_SOURCES` | Revise cohorts prospectively **before outcome inspection**; require new author approval for any exclusions, dependencies, denominators or methodological consequences | All scientific execution stays closed until amended G2 protocol is separately frozen |

**Recorded sole-author choice:** `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD` is **APPROVED AS A POLICY**, not as a freeze, legal clearance or experiment. A separate author G2 approval and immutable freeze artifact remain mandatory. Any G4 access to ESA/OPS-SAT source data remains blocked until the applicable versioned rights, attribution, third-party material and source-identity conditions are signed off, and G4 scientific execution is separately approved. Hack-A-Sat secondary use remains blocked pending file-level exceptions. Option A/C remain historical alternatives, not currently selected.

**Author rights-policy decision:** `B_APPROVED_POLICY_ONLY`. **G2 protocol-freeze approval:** `NOT_GIVEN`. **Source rights approval for actual G4 use:** `NOT_GIVEN`. **G3 synthetic implementation and G4 source execution:** `NOT_AUTHORIZED`. **PR merge:** `NOT_AUTHORIZED`. **Third-party communications:** `NONE`. No generic G2 freeze checkbox above is silently treated as complete.

## G2 freeze-readiness decision matrix (prepared, **no new author sign-off**)

All rows below are **candidate acceptance rules**, not evidence that a G2 freeze has occurred. An `AUTHOR_DECISION_PENDING` row must receive the sole author's separate, attributable disposition before the proposed freeze. `DEFER_TO_G3`/`HARD_PRE_G4` entries are **not approvals to execute**. The already approved Option B is preserved.

| Decision ID | Required prospective contract | Current state | Latest permissible gate |
|---|---|---|---|
| `G2-P01` | Freeze exactly ESA v2 M1/M2/M3 and OPS-SAT v2 as **four descriptive, potentially dependent source strata**; ESA v1 paired-only, Hack-A-Sat secondary-only, NASA deferred | `AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P02` | Fix all eight frozen Study 9 variable meanings, ten criteria, four mapping classes and four visibility roles without modifying the frozen Study 9 files | `STATIC_SOURCE_CONTRACT_ALIGNED_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P03` | Keep `permitted_deterministic_derivation_rules=[]`, with no undocumented post-result additions | `EMPTY_CANDIDATE_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P04` | Fix 8-per-stratum operational coverage denominators; output 32 classification slots as finite-population descriptive records, **not 32 independent observations** | `STATIC_METHOD_DEFINED_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P05` | Fix `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` and explicit unknown/false handling, four-policy action-set stratification and no source pooling | `STATIC_METHOD_DEFINED_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P06` | Freeze the `S10_SYN_P0_V3_DRAFT` synthetic interface premise and **18 total prospective test cases including P0**, with a separate G3 technical oracle and stop-on-failure rule | `SPECIFIED_NOT_EXECUTED_AUTHOR_DECISION_PENDING` | **G2** design; **G3** actual tests |
| `G2-P07` | Disclose prior ESA/OPS metadata, headers, labels and count exposure and the OPS-SAT 1,494/1,594 training-segment discrepancy | `DOCUMENTED_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P08` | Adopt Option B as already approved; **unresolved ESA/OPS/Hack-A-Sat file-level rights remain hard pre-G4 source-use stops** | `OPTION_B_POLICY_APPROVED_G4_RIGHTS_NOT_CLEARED` | **G2** policy; **G4** file/notice sign-off |
| `G2-P09` | Fix exact source identifiers and Git source pins; create a separate, immutable freeze receipt with actual candidate content digests and post-approval UTC time; never self-hash an in-progress manifest | `FREEZE_RECEIPT_NOT_CREATED_AUTHOR_DECISION_PENDING` | **G2** |
| `G2-P10` | Record final **explicit** author verdict `APPROVE_G2_FREEZE`, `REVISE`, or `BLOCK` with the reviewed immutable candidate commit; stop until received | `AUTHOR_G2_FREEZE_VERDICT_NOT_PROVIDED` | **G2** |
| `G3-T01` | Implement/test independent-code oracle, synthetic positive, negative and boundary suite; fail on parity divergence | `NOT_EXECUTED_NOT_AUTHORIZED` | **G3** after separate approval |
| `G4-R01` | Confirm source version checks, exact ESA/OPS dataset reuse scope and all attribution/third-party exceptions, before *new* real-data payload access or analysis | `HARD_PRE_G4_NOT_CLEARED` | **G4** plus distinct source-use approval |
| `G4-R02` | Verify nested payload integrity and any dataset-native decision-time/authorization-field lineage before source-specific operational estimands | `HARD_PRE_G4_NOT_CLEARED` | **G4/G5** after separate approval |

### Future immutable freeze procedure (documentation plan only)

1. **Before signing:** Resolve `G2-P01`–`G2-P09` with explicit author-reviewed decisions, including any Option B conditions deferred **only** to G4; decide and pin exactly which G2 documents and baseline frozen Study 9/Study 2 sources are normative.
2. **Author decision:** Record `APPROVE_G2_FREEZE` expressly against the final candidate Git head and condition matrix. Do not infer approval from a generic continuation message. Record the actual UTC timestamp of the decision/receipt.
3. **Immutable payload:** In a separately authorized action, create the final **content-stable** G2 protocol/rights/methodology/manifest files and a commit with exact Git blob IDs; compute SHA-256 of their actual bytes, with a deterministic UTF-8/newline convention. Preserve Git history and the prior draft unchanged.
4. **Acyclic receipt:** Create a separate freeze-receipt file/commit referencing the already-existing payload commit, per-file SHA-256 digests, author decision and actual freeze timestamp. **Do not include the receipt's own hash in itself**. Prefer a protected immutable tag or archival release reference. No record is considered frozen until the receipt is committed and its references can be reopened and checked.
5. **Post-freeze controls:** Retain G3/G4/G5/G6 as separately closed gates. Any later deviation is a new, timestamped amendment; never overwrite, rebase away or quietly repair the frozen receipt. Do not treat GitHub CI as independent scientific parity.

**Pre-freeze data-integrity limitation:** Six earlier ESA ZIP and two OPS-SAT CSV identities are primarily **author-reported local intake checks**, with ESA inner members not fully checked. Their archived integrity and any legal permission remain separate hard **pre-G4** conditions under approved Option B. No source payload execution is part of this checklist.

**Overall candidate recommendation:** `AUTHOR_G2_METHOD_DECISIONS_PENDING; OPTION_B_APPROVED; G2_HOLD`. This prepares a future decision; it does not issue one.
