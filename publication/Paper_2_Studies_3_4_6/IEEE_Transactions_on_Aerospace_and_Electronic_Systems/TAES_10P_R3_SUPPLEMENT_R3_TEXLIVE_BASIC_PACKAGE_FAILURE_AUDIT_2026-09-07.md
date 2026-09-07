# TAES Paper 2 Short Track: Supplement R3 TeX Live Basic Package Failure Audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_FAILURE_ISOLATED_ENVIRONMENT_ONLY`

Supplement R3 successfully passed the earlier GFM/Pandoc figure handling and semantic-marker-order gates and reached `pdflatex`. Compilation then stopped before producing a PDF because the local TeX Live 2026 Basic installation does not provide `enumitem.sty`.

Exact reported failure:

```text
! LaTeX Error: File `enumitem.sty' not found.
...
ERROR: command failed (12): latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R3_DEV.tex
```

## Scientific and artifact controls

- Supplementary Markdown changed: NO
- Supplementary README changed: NO
- Figure S1 asset changed: NO
- R8 main article changed: NO
- Frozen R9 fallback changed: NO
- Study 3 rerun: NO
- Study 4 rerun: NO
- Study 6 rerun: NO
- Science files changed: NONE
- Supplement PDF produced: NO
- Publisher-facing artifact produced: NO

Protected identities reported by the run remained:

- R8 main PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- Supplement Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- Supplement README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- Frozen R9 PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

## Root cause

The R1 preamble loads `enumitem`, but the generated supplement does not use any `enumitem`-specific list customization. TeX Live Basic therefore fails on an unused optional dependency before the document body is compiled.

The same preamble also loads `caption`, `xurl`, and `float`, although this supplement does not use their package-specific commands. To avoid repeated environment failures on a minimal TeX installation, the next builder may remove these unused optional dependencies while preserving the generated document body, figure block, tables, hyperlinks, margins, and scientific content.

## Authorized next action

Create a Basic-compatible R4 supplement builder that preserves the exact R3 conversion and content pipeline but removes only unused optional preamble package loads. Do not modify supplementary source text, figure assets, results, main article, frozen R9 fallback, or study files.
