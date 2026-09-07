# TAES 10-page R3 IEEEtran R6 guard-failure audit

Date: 2026-09-06
Branch: `paper2/taes-10-page-compression`

## Result

`FAIL_GUARD_BEFORE_COMPILATION`

R6 stopped with:

`ERROR: R6 expected one localized \\raggedright; found 5`

## Root cause

The R6 localization itself was not shown to be defective. The builder counted every `\\raggedright` command in the generated IEEEtran TeX and required the document-wide count to equal one. The underlying generated TeX already contains four unrelated `\\raggedright` commands, so adding the intended one-paragraph Study-6 wrapper produces a global count of five.

The guard therefore tested the wrong invariant. The correct invariant is that localization increases the pre-existing `\\raggedright` count by exactly one and that the added wrapper structurally encloses the unique first Study-6 state-definition paragraph.

## Protected state

- Balanced R3 manuscript SHA-256 remains `7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909`.
- Supplement SHA-256 remains `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`.
- Frozen 16-page R9 fallback PDF SHA-256 remains `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`.
- No R6 PDF was produced.
- No manuscript source, supplement, study science, table value, reference, or geometry setting changed.
- No study was rerun.

## Next action

R7 will preserve the exact R5/R6 typography transformation but replace the global-count guard with structural verification of one added localized Study-6 wrapper. Compilation and visual QA remain required before any package freeze or merge to `main`.
