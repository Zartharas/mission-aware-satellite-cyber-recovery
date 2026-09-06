# TAES IEEEtran Revision 4 PDF Visual QA

**Audit date:** 2026-09-06  
**Build role:** Development-only TAES/IEEEtran visual-format audit  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Revision-4 PDF SHA-256:** `7964e8dd9460ca1863a46365a474a05b226b3bc5bd8eb2af6a9d1a82814a5e35`  
**Pages:** `18`  
**Publisher-facing:** No  
**Submission authorized:** No

## 1. Visual-QA method

The exact revision-4 PDF was rendered page by page at 180 dpi and all 18 pages were inspected for clipping, overlap, margin intrusion, broken glyphs, table/figure integrity, column flow, excessive spacing, title/abstract presentation, acknowledgment, and references.

A supplementary raster bounding-box check was also performed on all 18 rendered pages using a near-white threshold. The measured ink bounds were approximately consistent with the intended 0.7 in side margins and 1.0 in top/bottom margins. Pages 1-17 retained approximately 0.97 in of bottom whitespace in the rendered images; page 18 retained approximately 1.17 in. These raster measurements are supportive visual evidence, not a replacement for the TeX geometry audit.

## 2. Items that passed visual inspection

- No page shows clipped body text, tables, figure content, captions, acknowledgment text, or references.
- No page shows text or graphics extending visibly into the required side or bottom margins.
- No black squares, missing glyph boxes, or obvious font-substitution artifacts were observed.
- The title, author line, affiliation, abstract, and index terms on page 1 are intact and legible.
- Tables I-IV are fully visible and preserve their rows and exact-value content. No table is cropped or overlaps body text.
- Figure 1 is fully visible on page 14, preserves all three panels, and does not overlap the caption or surrounding text.
- The AI-use acknowledgment on page 18 is present, readable, and separated from the references.
- References [1]-[13], including the corrected TUF v1.0.36 reference, are present and not clipped.
- The repeated approximately 4.77 pt `Overfull \\vbox` messages do not correspond to visible clipping or bottom-margin intrusion in the rendered PDF. They are therefore classified as a systematic IEEEtran/text-height grid diagnostic rather than a demonstrated visual overflow defect for this build.

## 3. Visual defects requiring revision

### 3.1 Excessive interword spacing introduced by localized `\\sloppy`

Revision 4 eliminated all horizontal overflow, but the localized `\\sloppy` intervention produces visibly poor justification in several locations.

The most obvious defects are:

1. **Page 5, Study-3 endpoint paragraph.** The paragraph beginning `The frozen primary endpoints are` contains very large gaps between identifiers and words. Several endpoint names are split in a visually awkward manner, including a line containing an isolated `s,` from `unsafe_qualified_exposure_s`.
2. **Page 11, Study-6 gate and G1 paragraphs.** Spacing around long gate/state identifiers is uneven and noticeably looser than surrounding body text. The problem is less severe than pages 5 and 16 but remains visible.
3. **Page 16, Study-6 assurance-signal limitations paragraph.** The paragraph beginning `The six assurance signals are also modeled Boolean variables` has severe stretched spacing between long monospaced identifiers and ordinary prose. This is not acceptable as publisher-facing typography.

The revision-4 log is consistent with these visual findings: overfull hboxes are zero, while underfull hboxes increase to 39, including multiple badness-10000 lines in the localized relaxed blocks.

### 3.2 Common-framework notation is rendered as monospaced ASCII instead of mathematical notation

On page 4, the common trust-qualification framework displays expressions such as:

- `Q_j(E_j) in {0,1}`
- `T_j in {0,1}`
- `U_j = 1[Q_j(E_j) = 1 and T_j = 0]`
- `C_j = 1[Q_j(E_j) = 0 and T_j = 1]`

as monospaced literal text. The intended manuscript-level mathematical abstraction should be typeset using mathematical symbols, subscripts, set braces, and `\\in`, with the logical conditions rendered in math notation. This is a formatting/presentation defect only. No scientific definition or endpoint may change.

Related notation such as `E_j`, `Q_j`, `T_j`, `Q_3`, `T_3`, `Q_4`, `T_4`, `Q_6`, and `T_6` should be rendered consistently as mathematical variables in the common-framework section rather than as code identifiers.

## 4. Page-count interpretation

The page count remained `18` after horizontal-overflow removal, so `18` is now treated as the stable development-format baseline for the current 12,037-word manuscript and four-table/one-figure layout.

This audit does not authorize scientific deletion or compression merely to reach 10 pages. TAES has no formal Regular Paper page limit, although accepted pages beyond 10 incur overlength charges and unnecessary length may affect review. Any later compression must remain science-preserving and separately audited.

## 5. Gate decision

- Horizontal overflow subgate: `PASS` (`overfull_hbox_count=0`).
- Geometry and font embedding: `PASS`.
- Vertical-warning visual classification: `PASS_NO_VISIBLE_CLIPPING_OR_MARGIN_INTRUSION`.
- Table integrity: `PASS`.
- Figure 1 integrity: `PASS`.
- Acknowledgment/reference integrity: `PASS`.
- Publisher-facing visual typography: `FAIL_R4_LOCALIZED_SLOPPY_SPACING_AND_ASCII_MATH`.
- Overall PDF visual QA: `FAIL__REVISION_5_REQUIRED`.

## 6. Required next action

Revision 5 must remain a generated-LaTeX formatting intervention only. It should:

1. start from revision 3 rather than retaining revision 4's localized `\\sloppy` blocks;
2. replace the four affected blocks with a more conservative local line-breaking strategy that does not create visibly stretched lines;
3. typeset the common-framework notation as proper LaTeX math without changing its scientific meaning;
4. preserve the canonical Markdown manuscript, all frozen study results, Tables I-IV, Figure 1, references, acknowledgment, and TAES geometry;
5. compile to a new development PDF and undergo another full page-by-page visual QA before any publisher-facing freeze.

**Verdict:** `R4_VISUAL_QA_FAIL__NO_CLIPPING__R5_REQUIRED_FOR_TYPOGRAPHY_AND_MATH_PRESENTATION`
