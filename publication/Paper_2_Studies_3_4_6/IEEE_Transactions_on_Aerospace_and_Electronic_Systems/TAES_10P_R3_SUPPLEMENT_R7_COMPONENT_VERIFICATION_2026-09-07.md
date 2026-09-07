# TAES Paper 2 short track: Supplement R7 component verification

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`
Scope: generated supplementary-PDF build mechanics only

## Status

`PASS_COMPONENT_VERIFICATION`

No author local run was requested for this verification.

## Verification performed

A Pandoc-3.8-style captionless-table scope was reproduced around the exact supplementary Table S1-S3 structures already used for the R6 width audit. The generated-LaTeX test included:

- empty `LTcaptype` compatibility wrapper,
- R6 fixed-width p-columns,
- R6 table-local `\small`,
- R6 table-local `\tabcolsep=4pt`,
- breakable monospaced identifiers,
- US-Letter article geometry.

The component test compiled successfully with:

- pages: 2
- page size: 612 x 792 pts (US Letter)
- overfull hboxes: 0
- LaTeX warnings: 0
- fonts reported by `pdffonts`: 3
- all reported fonts embedded: yes

The test confirms that the table-local declarations remain safely scoped by the Pandoc captionless-table brace group and that the fixed-width table layout remains mechanically clean under that grouping.

## R7 parser/gate verification

The corrected `pdffonts` interpretation was checked against the component PDF. The stable trailing fields are `emb sub uni object ID`, so the embedding value is the fifth token from the end. All component fonts reported `emb=yes`.

The R7 whitespace-insensitive text-gate strategy is intentionally limited to extraction/layout whitespace and soft-hyphen removal; it does not alter visible marker characters.

## Gate-policy refinement

An overfull horizontal box is a strong layout defect signal and should remain fatal before visual QA. An overfull vertical box, however, can arise from output/page-building mechanics without a visible defect and should be reviewed diagnostically rather than automatically forcing another builder revision. The final builder will therefore record vertical-box counts but will not reject solely on that count; visual QA remains authoritative for vertical-page layout.

## Protected content

No supplement source, main article, figure, frozen study, population, result, claim, or reference changed.

`science_files_changed=NONE`
`study_rerun=NO`
`publisher_facing=NO`
`author_local_run_requested=NO`
