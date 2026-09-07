# TAES Paper 2 short track: Supplement R6 proactive hardening audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`
Scope: generated supplementary-PDF build tooling only

## Status

`PASS_WITH_PREEMPTIVE_BUILDER_HARDENING_REQUIRED`

No R6 end-to-end local-author build was requested from the author. This audit was performed before asking for another local run.

## Findings

1. **R6 table font and spacing scope**
   - R6 prepends `\small\setlength{\tabcolsep}{4pt}` directly before each `longtable`.
   - Those declarations are not locally grouped in the generated TeX.
   - As written, the first table can leave `\small` and the reduced `\tabcolsep` active for following supplement prose and later sections.
   - This is a layout-only defect in generated TeX, not a supplement-source or science defect.

2. **PDF text gate is too literal for discretionary identifier breaks**
   - The build intentionally inserts `\allowbreak{}` into monospaced identifiers.
   - A rendered identifier such as `PRE_ONSET_CACHE` or `APPROVED_BAD_SOURCE` may therefore be split across PDF text-extraction line boundaries while remaining visually unchanged.
   - R1's literal substring text gate can falsely reject a correct PDF.
   - The safe gate is whitespace-insensitive comparison of visible markers after PDF extraction.

3. **Font-embedding parser should use the `emb` field, not a positional proxy for `sub`**
   - `pdffonts` ends each row with `emb sub uni object ID`.
   - The stable embedding field is the fifth token from the end (`parts[-5]`), while the inherited R1 parser checks `parts[-4]`.
   - R7 will use the actual `emb` field and make embedding a hard post-build gate.

4. **Final mechanical gates should be enforced before author review**
   - R7 will fail the development build if the final log has any overfull hbox, overfull vbox, or LaTeX warning, or if any font is not embedded.
   - Underfull boxes remain diagnostic rather than fatal.

## Local component verification

The exact supplementary Table S1-S3 structures used by R6 were reproduced locally with the fixed-width column specifications and breakable identifiers. The table-only test compiled with:

- overfull hboxes: 0
- LaTeX warnings: 0

The grouping correction does not alter any visible table value or identifier; it only restores normal document typography after each table.

## Protected content

This hardening does not modify:

- `TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md`
- `TAES_10P_R3_SUPPLEMENTARY_README.txt`
- Supplementary Fig. S1
- the approved R8 eight-page main article
- the frozen R9 fallback
- Studies 3, 4, or 6
- any frozen population, endpoint, result, claim, or reference

`science_files_changed=NONE`
`study_rerun=NO`
`publisher_facing=NO`
`author_local_run_requested=NO`
