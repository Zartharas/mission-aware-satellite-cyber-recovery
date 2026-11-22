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
