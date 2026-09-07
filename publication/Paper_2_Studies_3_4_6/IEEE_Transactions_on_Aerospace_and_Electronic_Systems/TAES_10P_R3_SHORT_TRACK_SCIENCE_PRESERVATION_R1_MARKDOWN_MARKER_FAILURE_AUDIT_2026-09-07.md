# TAES Paper 2 Short-Track Science-Preservation R1 Markdown-Marker Failure Audit

**Date:** 2026-09-07  
**Branch:** `paper2/taes-10-page-compression`  
**Status:** `FAIL_AUDIT_IMPLEMENTATION_ONLY__SCIENCE_AND_R9_SUPPLEMENT_BUILD_UNAFFECTED`

## Trigger

The corrected Supplement R9 build completed successfully, including the four authorized table cross-reference corrections, but the subsequent read-only science-preservation audit stopped with:

```text
ERROR: science-preservation marker missing [STUDY4_BOUNDARY]: 4,608 exact observations
```

## Root cause

This is a source-marker implementation defect, not a scientific-content defect.

The frozen Study-4 source states the exact population as:

```markdown
Every producer subset is evaluated: 128 subsets per block per rule, for `18 x 2 x 128 = 4,608` exact observations.
```

The R1 audit searched for the raw source substring:

```text
4,608 exact observations
```

The closing Markdown code delimiter immediately after `4,608` means that raw substring is not present even though the visible rendered text is exactly `4,608 exact observations`.

## Evidence already passed before this audit failure

The corrected R9 supplement build reported:

- 12 pages, US Letter
- zero overfull hboxes
- zero overfull vboxes
- zero LaTeX warnings
- all reported fonts embedded
- Figure S1 embedded
- Appendices A-E text gate PASS
- Tables S1-S3 text gate PASS
- stale Table II/III/IV cross-reference gate PASS
- supplement table values changed: NO
- experimental results changed: NO
- science files changed: NONE
- study rerun: NO
- main article changed: NO
- frozen R9 fallback changed: NO

## Corrective action

A Revision-2 read-only science-preservation wrapper will normalize Markdown inline-code delimiters for textual marker matching while retaining all R1 hash, complete-row, population-separation, reference, AI-disclosure, and branch-scope checks.

No manuscript, supplement, table value, figure, experiment, or frozen science file is changed by this correction.

## Decision

`R1_SCIENCE_AUDIT_FAILURE_CLASSIFICATION=FALSE_NEGATIVE_MARKDOWN_DELIMITER_MATCH`

`SCIENTIFIC_DEFECT=NO`

`SUPPLEMENT_REBUILD_REQUIRED=NO`

`READ_ONLY_AUDIT_RERUN_REQUIRED=YES`
