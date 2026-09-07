# TAES Paper 2 short-track Supplement R9 correction readiness audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_READY_FOR_ONE_LOCAL_CORRECTED_BUILD_GATE`

## Purpose

This audit confirms that the only remaining supplement-content correction before package-preservation review is the four stale table-number cross-references identified after Supplement R8 visual QA.

## Verified correction scope

The four pre-correction strings were verified against the tracked R9-derived section sources and the rendered R8 supplementary PDF:

1. Study 3 legacy `Table II` prose reference -> `Table S1`.
2. Study 4 legacy `Table III` prose reference -> `Table S2`.
3. Study 6 legacy `Table IV` gate-summary reference -> `Table S3`.
4. Study 6 legacy `Table IV` denominator reference -> `Table S3`.

No table caption itself is wrong. Tables are already rendered as S1, S2, and S3. The correction changes cross-reference labels only.

## Tracked correction controls

The branch now contains:

- `TAES_APPLY_SUPPLEMENT_R9_CROSSREF_FIX.py`
  - binds to the exact pre-correction supplement Markdown SHA-256 `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`;
  - applies exactly four replacements;
  - records the resulting corrected source SHA locally;
  - fails on any unexpected source identity or replacement count;
  - does not modify study or main-article files.

- `TAES_BUILD_10P_SUPPLEMENT_R9.py`
  - binds the corrected source identity from the local correction audit;
  - preserves the R8/R7 conversion and fixed-width-table pipeline;
  - requires corrected S1/S2/S3 visible references in the generated PDF;
  - rejects the four legacy II/III/IV references;
  - preserves the paired main R8 and frozen R9 hashes;
  - requires zero overfull hboxes, zero LaTeX warnings, embedded fonts, and US-Letter output.

- `TAES_RUN_SUPPLEMENT_R9_CORRECTED_FINAL_GATE.sh`
  - applies the authorized correction and performs the corrected build in one invocation;
  - verifies visible cross-references, mechanical gates, protected identities, and audit markers;
  - ends with `TAES_SUPPLEMENT_R9_CORRECTED_FINAL_GATE=PASS` only if every required assertion passes.

## Protected unchanged artifacts

- Main R8 PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- Frozen R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- Supplement README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- Fig. S1 PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

The corrected supplement source and PDF will intentionally receive new SHA-256 identities because four visible labels change.

## Scientific impact

`NONE`

The authorized correction does not change:

- any Study 3 result, endpoint, treatment, population, origin category, or logical-time value;
- any Study 4 rule, threshold, producer assignment, population, null result, or first/systematic definition;
- any Study 6 state, gate, residual-state identity, population, or benign-loss count;
- any citation or literature-positioning claim;
- any cross-study synthesis claim;
- the no-pooling rule;
- the contact-model boundary;
- the qualification-versus-recovery-completion boundary;
- the main article;
- any frozen study artifact;
- the frozen 16-page R9 fallback.

## Why one more local build is necessary

The corrected supplement Markdown is an intentionally untracked development file on the author's canonical local repository, and the authoritative build environment is the author's Pandoc/TeX Live installation. Therefore the correction and regenerated PDF must be materialized once in that environment before the new PDF identity can be frozen and visually rechecked.

This is a final materialization gate, not an exploratory diagnostic iteration.

## Next step after local PASS

If the one-shot runner passes, perform a focused visual/cross-reference regression on the corrected PDF, then complete the R9-to-short-main-plus-supplement science-preservation proof, additive superseding supplement decision, and short-track package freeze.
