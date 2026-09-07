# TAES Paper 2 short track: Supplement R8 previsual readiness audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`
Scope: supplementary-PDF development build before visual QA

## Status

`READY_FOR_ONE_LOCAL_END_TO_END_PREVISUAL_BUILD`

All builder issues that could be diagnosed or reproduced without another author-side run have been addressed before requesting a new local compile.

## Builder chain resolved

- R1: Pandoc `gfm+raw_tex` reader incompatibility identified.
- R2: GFM-safe Fig. S1 placeholder/reinjection implemented.
- R3: semantic marker gate moved before discretionary identifier breaks.
- R4: unused TeX Live optional dependencies removed.
- R5: Pandoc 3.8 captionless-longtable `LTcaptype` compatibility normalized.
- R6: Tables S1-S3 converted to fixed-width local layouts after proactive overflow testing.
- R7: table scope asserted, PDF text gate made whitespace-insensitive, and `pdffonts` embedding parsing corrected.
- R8: final gate policy refined so only strong previsual defects are fatal; vertical-box diagnostics are recorded for visual review rather than forcing automatic iteration.

## Proactive component evidence

The exact Table S1-S3 structures were locally reproduced with:

- fixed-width p-columns,
- table-local small font and `tabcolsep=4pt`,
- breakable monospaced identifiers,
- Pandoc-style captionless-table grouping,
- US-Letter geometry.

The component build passed with:

- overfull hboxes: 0
- LaTeX warnings: 0
- US-Letter page size
- all reported fonts embedded

The single-run shell gate was separately syntax-checked successfully.

## R8 final previsual gates

R8 requires:

- all bound source/artifact hashes from the R1 pipeline,
- Fig. S1 present,
- Appendices A-E present in extracted PDF text,
- Tables S1-S3 present in extracted PDF text,
- zero overfull hboxes,
- zero LaTeX warnings,
- all fonts embedded using the actual `emb` field,
- US-Letter page size.

Overfull vbox and underfull-box counts are retained as diagnostics for the page-by-page visual QA.

## Why one local run is now necessary

The exact generated supplementary Markdown/README and the author's TeX Live 2026/Pandoc 3.8 environment are local untracked development inputs. A complete publisher-candidate supplement PDF cannot be truthfully asserted without compiling those exact local inputs once through R8.

The repository now provides one consolidated runner:

`TAES_RUN_SUPPLEMENT_R8_FINAL_PREVISUAL_GATE.sh`

No incremental diagnostic run is planned before that gate.

## Protected content

No Study 3, 4, or 6 science was changed or rerun. The approved eight-page R8 main article and frozen R9 fallback remain bound and untouched.

`science_files_changed=NONE`
`study_rerun=NO`
`main_article_changed=NO`
`supplement_source_changed=NO`
`publisher_facing=NO`
`visual_qa_required_after_build=YES`
