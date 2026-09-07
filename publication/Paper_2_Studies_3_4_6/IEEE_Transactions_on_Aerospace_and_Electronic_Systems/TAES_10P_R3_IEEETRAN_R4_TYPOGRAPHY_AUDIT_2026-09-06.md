# TAES Paper 2 short-track R4 typography audit

Date: 2026-09-06
Branch: `paper2/taes-10-page-compression`

## Scope

This record preserves the outcome of `TAES_BUILD_10P_R3_IEEETRAN_R4.py`. R4 began from the balanced R3 source and the R2 discretionary-break strategy, removed the ineffective R3 weak line-break hints, and added two strong generated-LaTeX line-break incentives in the first Study-6 paragraph.

No canonical manuscript prose, Study 3/4/6 science file, table value, reference, supplement, geometry setting, or frozen R9 publisher-facing artifact was changed.

## Bound identities

- Balanced R3 manuscript SHA-256: `7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909`
- Frozen R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- Supplement SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`

## R4 result

- Pages: `8`
- Estimated pages over 10: `0`
- Page target decision: `PREFERRED_BUFFER_TARGET`
- Letter geometry: PASS
- Font embedding: PASS
- LaTeX warnings: `0`
- Overfull hboxes: `2`
- Overfull vboxes: `8`
- Underfull hboxes: `12`
- Underfull vboxes: `0`
- `\sloppy`: absent
- Breakable code tokens: `166`
- Strong Study-6 linebreaks: `2`
- Weak R3 linebreak hints retained: `NO`
- Manuscript source changed: `NO`
- Supplement changed: `NO`
- Science changed: `NONE`
- Study rerun: `NO`

R4 development PDF SHA-256: `9c6c562dca6fe681fecc0ce8c91cef25d3ba4ecae7f03d7ac18b4725aa3bb7ea`

## Remaining typography issue

Both remaining horizontal overflows are confined to the first Study-6 state-definition paragraph:

1. `8.70802 pt` in the segment containing `SOURCE_REVIEW_BYPASS` and `APPROVED_BAD_SOURCE`.
2. `7.96706 pt` in the following sentence containing `objective_baseline_correct`.

The page count and all protected identities remain stable. The two forced breaks changed TeX's line allocation but did not clear the paragraph completely.

## Decision

Do not alter manuscript content and do not add further forced line breaks. The next typography attempt may use one localized `\raggedright` group around this single Study-6 paragraph only, while preserving the validated breakable-identifier strategy, global TAES geometry, and prohibition on `\sloppy`.

Verdict: `PASS_PAGINATION_AND_SCIENCE__R4_HORIZONTAL_OVERFLOW_REMAINS_LOCALIZED`
