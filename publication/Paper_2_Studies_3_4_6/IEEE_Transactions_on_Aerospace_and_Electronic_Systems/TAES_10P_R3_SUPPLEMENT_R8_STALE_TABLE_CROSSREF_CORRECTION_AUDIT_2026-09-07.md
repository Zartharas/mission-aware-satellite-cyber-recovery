# TAES Paper 2 short-track Supplement R8 stale table cross-reference correction audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`CORRECTION_REQUIRED__EDITORIAL_CROSS_REFERENCE_ONLY`

## Trigger

After the exact Supplement R8 PDF passed mechanical and visual-layout QA, a science-preservation/cross-reference review identified four inherited R9 table-number references that were no longer correct after the tables were relocated into supplementary material.

The rendered supplementary tables are correctly labeled:

- Study 3: `Table S1`
- Study 4: `Table S2`
- Study 6: `Table S3`

However, prose inherited from the full R9 sections still contained:

1. `Table II values are logical model time...`
2. `Table III gives the complete frozen map as first/systematic counts.`
3. `Table IV reports the canonical gate summary.`
4. `Again, the denominators in Table IV are finite model populations.`

These refer to the original full-manuscript R9 numbering and are stale in the short-track supplement.

## Required correction

Only the four local cross-references are authorized to change:

- `Table II` -> `Table S1` in the Study-3 supplement discussion.
- `Table III` -> `Table S2` in the Study-4 supplement discussion.
- both `Table IV` references -> `Table S3` in the Study-6 supplement discussion.

No table label, row, value, endpoint, population, interpretation, citation, figure, manuscript text, experimental result, or study artifact is authorized to change.

## Scientific impact

None.

The defect is editorial only. It does not alter:

- Study 3 population, endpoints, contact treatments, exposure values, or origin decomposition;
- Study 4 producer population, 18-rule threshold map, first/systematic definitions, or null results;
- Study 6 state/gate definitions, residual-state identities, or benign-loss counts;
- the no-pooling rule;
- the rule that only Study 3 models contact;
- qualification-versus-recovery-completion boundaries;
- external-validity controls;
- R8 main article content or pagination;
- frozen R9 fallback.

## Historical preservation

The R8 visual-layout PASS record remains historically valid for layout/appearance of the exact R8 PDF. This correction record does not rewrite that audit. Because visible supplement prose will change, the corrected supplement must receive a new artifact identity and a focused re-QA before package freeze.

## Protected pre-correction identities

- Supplement R8 PDF SHA-256: `097d35c8696c676cac7a210ed7283982f04dad4a72f82dbd02f5cc83fc12fa3f`
- Supplement pre-correction Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- R8 main article SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- frozen R9 fallback SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

## Next gate

Apply a deterministic four-replacement source patch, rebuild the supplement with a new revision identity, verify mechanical gates, then perform focused visual/cross-reference QA before the science-preservation and package-freeze records are finalized.
