# TAES Paper 2 Short-Track Supplement R4 Longtable Caption-Type Failure Audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`FAIL_BUILD_ENVIRONMENT_COMPATIBILITY_ONLY__NO_SCIENCE_OR_SOURCE_CHANGE`

## Observed failure

Supplement R4 successfully passed the prior GFM reader, Figure S1 reinjection, semantic-marker, discretionary-break, and TeX Live Basic package-compatibility gates and reached `pdflatex`.

Compilation then stopped at the first generated `longtable` with:

```text
LaTeX Error: No counter 'none' defined.
...
\begin{longtable}[]{@{}lrrl@{}}
```

The R4 log also showed that Supplementary Fig. S1 had already been embedded before the failure.

## Root cause

The installed Pandoc version emits captionless longtables inside a wrapper using:

```latex
\def\LTcaptype{none}
```

Current LaTeX `longtable` interprets `\LTcaptype` as the name of a counter when it is nonempty. Because no counter named `none` exists, compilation stops.

This is a generated-LaTeX compatibility issue. It is not a supplementary-source, table-value, figure, manuscript, or scientific-content defect.

## Safe correction

For the three captionless supplementary tables, normalize only the generated Pandoc wrapper from:

```latex
\def\LTcaptype{none}
```

to:

```latex
\def\LTcaptype{}
```

The current TeX Live 2026 `longtable` implementation supports an empty `\LTcaptype` for an unnumbered/captionless longtable. This preserves the intended no-table-counter behavior without introducing a dummy semantic counter.

The correction must be applied only after Pandoc conversion and before compilation. It must not alter Markdown, visible table content, captions represented as surrounding text, Figure S1, study results, or the eight-page main article.

## Protected artifacts

The user-reported R4 run retained:

- paired R8 main article: 8 pages, US Letter
- R8 PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- supplementary Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- supplementary README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- frozen R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

No study rerun occurred. No science file changed. No publisher-facing artifact was replaced.
