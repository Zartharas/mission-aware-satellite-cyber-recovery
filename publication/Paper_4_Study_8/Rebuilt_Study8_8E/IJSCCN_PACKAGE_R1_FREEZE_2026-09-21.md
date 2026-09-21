# Paper 4 — IJSCCN Core Submission Package R1 Freeze

**Freeze date:** 2026-09-21  
**Freeze ID:** `P4-IJSCCN-PKG-R1-FREEZE-001`  
**Status:** `CORE_PACKAGE_FROZEN__AUTHOR_PHOTO_PENDING__PUBLISHER_SUBMISSION_NOT_AUTHORIZED`

## 1. Scope

This record closes the authorized IJSCCN venue-specific package-preparation phase for rebuilt Paper 4.

It binds the repository-generated core submission package for:

**International Journal of Satellite Communications and Networking (Wiley)**

This freeze does not authorize Wiley portal entry or publisher submission.

## 2. Frozen package source

Package directory:

`publication/Paper_4_Study_8/IJSCCN/`

Authoritative package-source commit:

`6553be414fd1bc598218501971872ff644dee8c8`

The package-source commit contains the final package content and package-status closure before the artifact build bound below.

No Study 8 or Study 8E scientific file was modified by package preparation.

## 3. Final exact-head package build

Workflow:

`Build Paper 4 IJSCCN package`

Workflow run:

`35632266523`

Workflow head:

`6553be414fd1bc598218501971872ff644dee8c8`

Result:

`COMPLETED / SUCCESS`

Artifact:

- ID: `10655615285`
- name: `paper4-ijsccn-submission-package-r1`
- artifact digest: `sha256:ddc3642d936df1c596cc759ee52c4236b337b52a39aa07410505af88f5713b37`
- artifact retention expiry reported by GitHub: 2026-10-21

The artifact is the final build of the package content at the frozen package-source commit.

## 4. Package QA already completed

The package QA record is:

`publication/Paper_4_Study_8/IJSCCN/PACKAGE_QA_R1_2026-09-21.md`

The completed QA includes:

- 213-word abstract, within the journal's 250-word limit;
- 8 keywords;
- 63-character short title;
- title page;
- cover letter;
- Data Availability Statement;
- Wiley-aligned AI Use Declaration;
- author biography;
- GTOC text and artwork;
- separate manuscript figures;
- numbered reviewer-facing citations/reference list;
- reproducible package builder and workflow;
- 25-page rendered-manuscript visual inspection;
- 600-dpi TIFF verification;
- reference-rendering QA;
- GTOC visual QA;
- no scientific reanalysis.

Intermediate presentation defects identified during QA were corrected before the frozen package-source commit.

## 5. Scientific integrity boundary

The package freeze preserves:

### Study 8

- `S8-PQC-ICR-001`;
- 3,456 deterministic positions;
- 635/864 = 73.4954% success per policy;
- P3 − P1 = 0.000000 percentage points;
- frozen profile-success values;
- no logical-slot-to-physical-time conversion.

### Study 8E

- `S8E-ECTV-001`;
- corrected freeze `S8E-CANON-RESULTS-002-FREEZE-001`;
- 20 traces;
- 476 source rows;
- 454 eligible anchors;
- 65,376 cases;
- 17,640 finite / 47,736 non-finite;
- threshold min/median/max 48 / 345 / 57,727 bit/s;
- 4,410/4,410 both-finite P3/P1 threshold differences = 0 bit/s;
- 21,792/21,792 preserved profile-burden ordering.

The Study 8 and Study 8E populations remain separate and unpooled.

No new experiment, rerun, TRACE-002 acquisition, endpoint, or scientific interpretation was introduced during package preparation.

## 6. External author-supplied items not frozen in the repository

The following are intentionally not fabricated or inferred:

1. **recent author photograph** requested by IJSCCN;
2. **corresponding-author telephone number**, only if the Wiley portal requests it.

These external items do not invalidate the repository-generated core package freeze.

## 7. Authorization boundary

At this freeze:

- IJSCCN venue lock: authorized and complete;
- venue-specific package preparation: authorized and complete;
- repository-generated core package: frozen;
- publisher submission: **not authorized**;
- Wiley portal entry/final submission: **not authorized**.

## 8. Governance note

This freeze record is stored outside `publication/Paper_4_Study_8/IJSCCN/` so that binding the final artifact does not alter the package inputs and trigger a new self-referential artifact build.

Any commits after the package-source commit are acceptable only if they modify governance/state records outside the frozen IJSCCN package directory.

## 9. Next gate

`AUTHOR_PACKAGE_REVIEW_AND_PHOTO__THEN_SEPARATE_WILEY_PORTAL_SUBMISSION_AUTHORIZATION`

No new publication or scientific phase should begin until the current PR is merged and post-merge `main` CI is verified.
