# TAES Paper 2 Short-Track Supplement Table Layout Proactive Audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_PROACTIVE_LAYOUT_ENGINEERING__NO_SOURCE_OR_SCIENCE_CHANGE`

## Reason for proactive audit

After the Supplement R4 run exposed Pandoc's captionless-longtable `LTcaptype=none` compatibility problem, the three supplementary table structures were independently reproduced in a local LaTeX test before requesting another author-side build.

The purpose was to avoid another unnecessary user-run iteration if Pandoc's default natural-width longtables would later overflow the single-column supplement.

## Tables tested

The local test reproduced the exact visible structures of:

- Table S1: selected Study-3 residual-boundary results, four columns
- Table S2: complete Study-4 first/systematic threshold map, three columns
- Table S3: Study-6 residual incorrect states and benign assurance loss, five columns

The test preserved the same table text and long identifiers used by the frozen supplementary source.

## Baseline Pandoc layout result

Pandoc's natural-width column specifications produced material horizontal overflow in the local test, including approximately:

- 137.5 pt for the four-column Study-3 table alignment
- 420.4 pt for the five-column Study-6 table alignment

This confirms that simply fixing the `LTcaptype` counter issue would not be sufficient for a readable peer-review supplement.

## Safe fixed-width layout

A generated-LaTeX-only treatment was tested using:

- `\small` inside each Pandoc table wrapper
- local `\tabcolsep=4pt`
- fixed-width `p{}` columns sized as fractions of `\textwidth`
- `\raggedright\arraybackslash` for prose/code-heavy columns
- centered fixed-width columns for numeric threshold/count fields
- the existing discretionary `\allowbreak{}` opportunities inside long monospaced identifiers

The tested width allocations were:

### Table S1

- evidence/contact/policy: 0.25 `\textwidth`
- unsafe-qualified trajectories: 0.14
- mean exposure: 0.18
- interpretation: 0.32

### Table S2

- rule: 0.14 `\textwidth`
- unsafe qualification threshold: 0.36
- false-conservative rejection threshold: 0.40

### Table S3

- gate: 0.23 `\textwidth`
- required signals: 0.10
- residual incorrect states: 0.35
- unsafe count: 0.08
- benign-loss subsets: 0.10

## Local validation result

With the fixed-width layouts and breakable identifiers, the three-table local test compiled successfully with:

- overfull hboxes: 0
- LaTeX warnings: 0 after `latexmk` convergence

The table contents were not edited, abbreviated, reordered, or numerically changed.

## Scope control

This audit authorizes only generated-LaTeX table layout normalization for the separate supplementary PDF. It does not alter:

- supplementary Markdown
- table values or labels
- Study 3, 4, or 6 populations/results
- Fig. S1
- the visually approved eight-page R8 main article
- the frozen 16-page R9 fallback

No study rerun occurred. No publisher-facing artifact is created by this audit.
