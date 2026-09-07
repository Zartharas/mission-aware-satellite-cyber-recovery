# TAES Paper 2 Short Track: Supplement R2 Marker-Guard Failure Audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_FAILURE_ISOLATED_TO_POSTCONVERSION_MARKER_GUARD_ORDER`

Supplement R2 successfully bypassed the unsupported Pandoc `gfm+raw_tex` reader combination by keeping the GFM reader and reinjecting the generated Fig. S1 raw-LaTeX block after Pandoc conversion. It then stopped before TeX materialization with:

`ERROR: expected supplement marker missing after Pandoc: S3-K4E-001`

## Root cause

The R2 Pandoc function restores the Fig. S1 LaTeX block and then runs the breakable-identifier transformation before returning generated body TeX to the R1 pipeline. The breakable transformation changes internal LaTeX representations such as:

`S3-K4E-001`

to a visually equivalent representation containing discretionary break commands, for example:

`S3-\allowbreak{}K4E-\allowbreak{}001`

R1 subsequently checks for the pre-break literal string `S3-K4E-001`. The visible identifier has not changed, but the guard runs against the post-break internal representation and therefore fails.

The same ordering risk applies to the frozen Study 4 and Study 6 identifiers.

## Scope

This is a build-validation ordering defect only.

- Supplementary Markdown changed: NO
- Supplementary README changed: NO
- Fig. S1 asset changed: NO
- R8 main article changed: NO
- Frozen R9 fallback changed: NO
- Study 3/4/6 science files changed: NONE
- Study rerun: NO
- Supplement PDF created: NO
- Publisher-facing artifact changed: NO

Protected identities observed in the failed run remained:

- R8 main PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- Supplement Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- Supplement README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- Frozen R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

## R3 correction rule

R3 may change build mechanics only:

1. keep Pandoc reader `gfm`;
2. keep the R2 Fig. S1 placeholder/reinjection strategy;
3. return pre-break generated LaTeX to the R1 semantic marker gate;
4. after those semantic markers pass, insert discretionary breaks into `\texttt{}` identifiers;
5. preserve all bound source hashes and all existing science controls.

No manuscript, supplement, result, table, figure, or reference content is authorized to change.
