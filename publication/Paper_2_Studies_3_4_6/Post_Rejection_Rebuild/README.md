# Paper 2 Post-Rejection Rebuild

**Status:** `PHASE5C_AUTHORIZED__P99_X10_GAP_RULE_FROZEN__NO_TRACE_EXTRACTION__NO_SCIENTIFIC_EXECUTION`  
**Authorization date:** 2026-09-26  
**Branch:** `paper2/post-rejection-rebuild`  
**Branch base:** `972a273f699cc1df39597f358e0fdb5369de342a`

Paper 2 remains scientifically limited to the frozen Studies 3, 4, and 6 as its original evidence foundation.

The rejected TAES R10 submission remains immutable provenance under:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

TAES manuscript ID: `TAES-2026-4182`.

## Phase-1 objective

Translate the TAES editorial diagnosis into a stronger scientific and manuscript architecture before selecting a new venue.

Phase 1 permits read-only analysis of frozen Study-3/4/6 evidence, algebraic derivation from frozen model definitions, manuscript/readability audit, prospective validation design, public-source screening, and non-overlap controls.

Phase 1 does **not** permit modifying or rerunning `S3-K4E-001`, `S4-MPQ-001`, or `S6-SCTR-001`; changing frozen results; executing a new extension; importing Studies 1/2/5/7/7E/8/8E/9 as Paper-2 experimental evidence; pooling populations; locking a new journal; or creating a publisher-facing resubmission package.

## Phase-1 records

1. `R10_EDITORIAL_DIAGNOSIS_2026-09-26.md`
2. `CROSS_STUDY_THEORY_DERIVATION_R1_2026-09-26.md`
3. `PHASE1_THEORY_VERIFICATION_AUDIT_2026-09-26.md`
4. `PAPER2_EXTERNAL_VALIDATION_OPTIONS_R1_2026-09-26.md`
5. `PAPER2_NONOVERLAP_GATE_2026-09-26.md`
6. `S3X_ETA_PROTOCOL_DRAFT_R1_2026-09-26.md`
7. `S4X_JCU_PROTOCOL_DRAFT_R1_2026-09-26.md`
8. `S6X_EAP_PROTOCOL_DRAFT_R1_2026-09-26.md`
9. `verify_phase1_theory.py`
10. `PAPER2_REBUILD_STATUS.json`
11. `PHASE1_ADVERSARIAL_PROTOCOL_REVIEW_R1_2026-09-26.md`
12. `S3X_SOURCE_SCREENING_R1_2026-09-26.md`
13. `S6X_CFS_ENVIRONMENT_SCREENING_R1_2026-09-26.md`

## Phase-1 gate

`AUTHOR_REVIEW_BEFORE_S3X_LOCAL_SOURCE_INSPECTION_OR_S6X_INVARIANT_FIXTURE_DESIGN`

The author separately authorized later controlled phases; the historical Phase-1 gate remains preserved here as provenance.


## Phase-2 branch-local design work

The author authorized a second, still non-executing design step on 2026-09-26. It is isolated on:

`paper2/post-rejection-phase2-design`

Branch base:

`db744891dc9a726ad51b25543c5f3ee90c0ce4e7`

PR #172 post-merge validation run `36267400739` / run `1205` completed successfully before this branch-local design record was finalized.

Phase-2 records:

1. `S3X_METADATA_SCHEMA_INSPECTION_R2_2026-09-26.md`
2. `S3X_SOURCE_FREEZE_CANDIDATE_R1.json`
3. `S6X_INVARIANT_FIXTURE_DESIGN_R2_2026-09-26.md`
4. `S6X_SOURCE_PIN_CANDIDATE_R1.json`
5. `PHASE2_DESIGN_GATE_R1_2026-09-26.md`
6. `PAPER2_PHASE2_DESIGN_STATUS.json`
7. `scripts/inspect_s3x_esa_schema.py`
8. `scripts/audit_paper2_post_rejection_phase2_design.py`

This phase does not authorize S3X source freeze, trace extraction, recovery replay, S6X checkout/build/source mutation, manuscript rewriting, venue locking, or publisher submission.

Branch-local next gate:

`AUTHOR_REVIEW_BEFORE_S3X_FINAL_SOURCE_FREEZE_OR_S6X_IMPLEMENTATION_WORKSPACE`


## Phase-3 pre-execution implementation

The author authorized the next controlled phase after PR #173 completed CI and was merged.

Predecessor:

- PR #173 merge: `a2b6f2e02c4075d2e9cd1976888dae38464a11c1`
- PR CI run: `36268050167` / run `1208` / success
- post-merge CI run: `36268665292` / run `1209` / success

Branch:

`paper2/post-rejection-phase3-preexecution`

Authorized work:

- `study3x/`: local ESA-v2 archive verification and source-identity freeze workflow only;
- `study6x/`: implementation workspace and static/pre-runtime validation only.

Still closed:

- S3X gap-rule freeze, trace extraction, recovery-policy replay, and scientific results;
- S6X build, fixture application to a build, artifact signing, independent rebuild, gate execution, and scientific results;
- Paper-2 manuscript rewrite, venue lock, and publisher submission.

Phase-3 status authority:

`PAPER2_PHASE3_PREEXECUTION_STATUS.json`

Current gate:

`AUTHOR_REVIEW_AFTER_PHASE3_CI_AND_LOCAL_S3X_SOURCE_FREEZE_OUTPUT_BEFORE_ANY_BUILD_OR_SCIENTIFIC_EXECUTION`


## Phase-4 local validation

Phase 4 prepared and executed the author-approved local verification workflows.

Completed local evidence includes:

- S6X pre-runtime source/materialization validation PASS at pinned cFS and LC commits, with no build and no scientific execution;
- S3X ESA-v2 source identity freeze PASS across 76 Mission-1 and 100 Mission-2 channels;
- source-freeze record `S3X-ESA-V2-SOURCE-FREEZE-001`;
- cadence-review CSV SHA-256 `7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`.

Phase-4 status authority:

`PAPER2_PHASE4_LOCAL_VALIDATION_STATUS.json`

## Phase-5 read-only cadence sensitivity

The author authorized a strictly diagnostic cadence/gap-threshold sensitivity phase on 2026-09-26.

Branch:

`paper2/post-rejection-phase5-cadence-sensitivity`

Authorized:

- read-only positive inter-sample delta analysis against the frozen ESA-v2 local bytes;
- exact channel-archive SHA-256 rebinding before analysis;
- fixed candidate threshold sensitivity;
- aggregate exceedance counts, fractions, durations, and cadence classes;
- top positive-delta frequency summaries.

Still closed:

- gap-rule selection or freeze;
- timestamp-level gap-trace emission;
- trace-population freeze;
- recovery-policy execution;
- S3X scientific results;
- S6X build/scientific execution;
- S4X execution;
- Paper-2 manuscript claims, venue lock, or submission based on the extension.

Phase-5 status authority:

`PAPER2_PHASE5_CADENCE_SENSITIVITY_STATUS.json`

Historical Phase-5 gate:

`AUTHOR_REVIEW_OF_GAP_SENSITIVITY_BEFORE_ANY_GAP_RULE_SELECTION`


## Phase-5A sensitivity output correction

The author authorized Phase 5A after the successful Phase-5 local run and review of its three generated outputs.

The R1 run completed with 176 channels, 8 candidate rules, and 1,408 sensitivity rows. The post-run Git working tree was clean. No gap rule was selected or frozen, no timestamp-level traces were emitted, and no recovery or scientific execution occurred.

A representation defect was identified in `S3X_GAP_SENSITIVITY_001.csv`: cadence summary fields and exceedance-distribution fields reused generic metric names, so dictionary expansion overwrote the cadence values in the exported row. Independent recomputation of all 1,408 thresholds against the separately preserved cadence review found zero threshold-formula mismatches.

Phase 5A therefore:

- preserves the historical R1 analyzer and runner;
- separates corrected `cadence_*` and `exceedance_*` fields;
- produces versioned R2 local outputs;
- binds both R2 CSV SHA-256 values into the R2 summary JSON;
- adds regression tests preventing recurrence of the field collision;
- does not change the candidate formulas or source population.

Phase-5A status authority:

`PAPER2_PHASE5A_SENSITIVITY_OUTPUT_FIX_STATUS.json`

Historical Phase-5A gate:

`AUTHOR_REVIEW_OF_CORRECTED_R2_OUTPUTS_BEFORE_ANY_GAP_RULE_SELECTION`


## Phase-5B P99_X10 pre-freeze validation

The author authorized Phase 5B after the corrected Phase-5A R2 local run completed successfully with a clean Git worktree.

Bound R2 evidence:

- `S3X_GAP_SENSITIVITY_002.csv`: `f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e`
- `S3X_DELTA_FREQUENCIES_002.csv`: `1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349`
- `S3X_GAP_SENSITIVITY_SUMMARY_002.json`: `c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6`

`P99_X10` advances only to pre-freeze validation. It is not selected and is not frozen.

The validation target is:

- 176 channel-level `P99_X10` rows;
- `threshold_seconds = 10 * channel-specific cadence_p99_seconds`;
- strict `delta > threshold` comparison semantics;
- 1,919 aggregate exceedances;
- 171 channels with at least one exceedance;
- five zero-exceedance channels;
- canonical 176-channel projection SHA-256 `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`.

The validator consumes only the three already generated R2 aggregate artifacts. It does not read source telemetry archives and does not emit timestamp-level intervals.

Phase-5B status authority:

`PAPER2_PHASE5B_P99X10_PREFREEZE_STATUS.json`

Historical Phase-5B gate:

`AUTHOR_REVIEW_OF_P99_X10_PRE_FREEZE_VALIDATION_BEFORE_GAP_RULE_FREEZE_OR_TIMESTAMP_TRACE_EXTRACTION`


## Phase-5C P99_X10 gap-rule freeze

The author authorized the Phase-5C rule freeze after successful Phase-5B local pre-freeze validation.

Bound pre-freeze validation:

- `S3X_P99_X10_PREFREEZE_VALIDATION_001.json`
- SHA-256 `cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0`
- channels: 176
- aggregate exceedances: 1,919
- nonzero channels: 171
- zero-exceedance channels: 5
- canonical channel projection SHA-256 `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`

The frozen rule is:

`P99_X10`

with:

`threshold_seconds = 10 * channel-specific cadence_p99_seconds`

and strict:

`positive inter-sample delta > threshold_seconds`

The freeze is explicitly characterized as a data-informed selection from the already evaluated Phase-5 candidate family. It is not represented as a rule prespecified before cadence inspection.

The machine-readable freeze authority is:

`study3x/config/S3X_GAP_RULE_FREEZE_001.json`

After this freeze, timestamp-level extraction must use this exact rule. Retuning after inspecting extracted timestamps is prohibited unless a new versioned protocol is separately authorized.

Still closed:

- timestamp-level gap-trace extraction;
- trace-population freeze;
- recovery-policy execution;
- S3X scientific execution;
- manuscript claims based on S3X;
- venue lock or publisher submission.

Phase-5C status authority:

`PAPER2_PHASE5C_P99X10_GAP_RULE_FREEZE_STATUS.json`

Current gate:

`AUTHOR_REVIEW_BEFORE_PHASE6_TIMESTAMP_LEVEL_TRACE_EXTRACTION_DESIGN`
