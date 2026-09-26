# Paper 2 Post-Rejection Rebuild

**Status:** `PHASE1_AUTHORIZED__DESIGN_AND_FORMAL_ANALYSIS_ONLY__NO_NEW_EXECUTION`  
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

## Current gate

`AUTHOR_REVIEW_BEFORE_S3X_LOCAL_SOURCE_INSPECTION_OR_S6X_INVARIANT_FIXTURE_DESIGN`

The author must separately authorize implementation/execution of any prospective extension after reviewing the protocols and their overlap/validity implications.


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
