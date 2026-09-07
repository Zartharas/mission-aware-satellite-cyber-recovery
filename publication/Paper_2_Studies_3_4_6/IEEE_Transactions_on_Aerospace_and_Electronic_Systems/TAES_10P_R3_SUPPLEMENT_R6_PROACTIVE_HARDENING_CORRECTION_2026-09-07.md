# TAES Paper 2 short track: Correction to R6 proactive hardening audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`
Scope: generated supplementary-PDF build tooling only

## Correction status

`CORRECTION_RECORDED_NO_SCIENCE_OR_SOURCE_CHANGE`

The earlier proactive R6 hardening audit correctly identified the PDF text-gate and font-embedding parser issues, but its first finding overstated a potential table-font scope problem.

## Corrected finding: R6 table font and spacing are already scoped

Pandoc 3.8 emits each captionless longtable inside a brace group beginning with the `LTcaptype` compatibility wrapper, structurally of the form:

```tex
{\def\LTcaptype{none}
...
\begin{longtable}...
...
\end{longtable}
}
```

R5 changes only `\def\LTcaptype{none}` to `\def\LTcaptype{}`. R6 inserts `\small` and the local `\tabcolsep` adjustment immediately before each `\begin{longtable}` while remaining inside that existing Pandoc brace group. Therefore the table-local font and spacing declarations do **not** leak into following supplement prose.

No additional grouping transformation is required. A later builder should instead assert that all three R6 longtables remain inside the Pandoc captionless-table group.

## Findings that remain valid

1. PDF text extraction can split identifiers at discretionary `\allowbreak{}` locations, so the text gate should compare normalized visible text rather than literal raw extraction strings.
2. The inherited `pdffonts` parser checks the wrong trailing field; the actual `emb` field should be used.
3. Final overfull-box, LaTeX-warning, and font-embedding conditions should be hard gates before requesting author review.

## Protected content

No supplement Markdown, README, figure, main article, frozen R9 fallback, study record, population, endpoint, result, claim, or reference is modified by this correction.

`science_files_changed=NONE`
`study_rerun=NO`
`publisher_facing=NO`
`author_local_run_requested=NO`
