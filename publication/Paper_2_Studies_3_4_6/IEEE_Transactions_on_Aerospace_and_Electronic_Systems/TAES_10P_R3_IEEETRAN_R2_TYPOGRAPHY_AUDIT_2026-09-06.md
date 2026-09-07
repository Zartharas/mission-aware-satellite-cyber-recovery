# TAES Paper 2 Balanced R3 IEEEtran R2 Typography Audit

Date: 2026-09-06
Branch: `paper2/taes-10-page-compression`

## Purpose

Record the generated-LaTeX-only R2 typography build for the balanced eight-page TAES Paper 2 candidate and identify the remaining layout blocker before visual QA.

## Protected source bindings

- Balanced R3 manuscript SHA-256: `7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909`
- Frozen 16-page R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- Supplement SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`

All three bindings remained unchanged.

## R2 build result

- Pages: 8
- Estimated pages over 10: 0
- Page target: preferred buffer target
- Geometry: PASS
- Fonts embedded: PASS
- LaTeX warnings: 0
- `\\sloppy`: absent
- Breakable monospaced tokens: 166
- Overfull hboxes: 2
- Overfull vboxes: 8
- Underfull hboxes: 11
- Underfull vboxes: 0

Generated artifact SHA-256 values:

- TeX: `2e09c02467f49f8bdb167d10934423c4743c48d05c6ff1940b27e21db3071571`
- PDF: `f323b55086705b7ad174d4fec8f8246d1feabdf799b04b38fe62067e459b3028`
- Log: `295fc86b7051551723d4202f2848d209bccc4a07842e10fdb0dcf3c07fd3a10c`
- Build audit: `4f0170d9fcb858ce18cfc59edc2aa1c1a32ee8abf9b52ad19396f3592f9cb261`

## Remaining blocker

Both remaining horizontal overflows occur in the same first Study 6 state-definition paragraph. The first is approximately 2.71 pt and the second approximately 30.77 pt. The log associates them with the long visible identifiers around:

- `TRUSTED_BUILDER_COMPROMISE`
- `SOURCE_REVIEW_BYPASS`
- `APPROVED_BAD_SOURCE`
- the following `objective_baseline_correct` oracle sentence

Tables I-III are not implicated. The common-framework equations are not implicated. The page count remains eight.

## Interpretation

The general discretionary-break treatment reduced the horizontal-overflow count from four to two and removed the earlier overflow in the later Study 6 gate paragraph. The remaining issue is localized to one prose list of long monospaced state identifiers. It does not justify changing manuscript prose, table content, geometry, or the eight-page length endpoint.

## Authorized next treatment

Apply generated-LaTeX-only, non-visible line-break incentives at the natural comma and sentence boundaries inside that one Study 6 paragraph. Preserve:

- every visible identifier and punctuation character;
- the exact balanced R3 Markdown source;
- the eight-page geometry;
- the supplement;
- all frozen science;
- the prohibition on `\\sloppy`.

A new visual QA is required after horizontal overflow reaches zero.

## Verdict

`PASS_EIGHT_PAGE_TARGET__TWO_LOCAL_STUDY6_HBOXES_REMAIN`
