# TAES Paper 2 short-track Supplement R8 final visual QA audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Artifact identity

Exact uploaded supplementary PDF visually reviewed:

- `TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.pdf`
- SHA-256: `097d35c8696c676cac7a210ed7283982f04dad4a72f82dbd02f5cc83fc12fa3f`
- Pages: 12
- Page size: 612 x 792 pt, US Letter
- PDF version: 1.7

The uploaded identity matches the successful local R8 previsual gate output.

## Mechanical evidence carried into visual QA

The local R8 previsual gate reported:

- overfull hboxes: 0
- overfull vboxes: 0
- underfull hboxes: 10
- underfull vboxes: 0
- LaTeX warnings: 0
- font count: 4
- all reported fonts embedded: PASS
- Fig. S1 embedded: YES
- Appendices A-E text gate: PASS
- Tables S1-S3 text gate: PASS
- supplement content changed: NO
- science files changed: NONE
- study rerun: NO
- main article appended: NO
- main article page count changed: NO

Protected paired artifacts remained:

- R8 main article SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- frozen R9 fallback SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- supplement Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- supplement README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- Fig. S1 PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

## Render-and-review method

The exact uploaded PDF was rendered to raster images at 180 dpi. All 12 pages were reviewed in sequence, with additional full-page inspection of pages containing the figure and supplementary tables.

## Page-by-page result

### Page 1
PASS.

- Supplement title and author block are centered, readable, and unclipped.
- Introductory supplement-purpose paragraph is readable and correctly separated from the figure.
- Fig. S1 is sharp and legible across all three panels.
- The figure caption is present, readable, and does not imply an integrated experiment.
- Appendix A begins cleanly below the figure.
- No overlap, clipping, broken glyphs, or margin intrusion observed.

### Pages 2-3
PASS.

- Study-3 text is readable and consistently justified.
- Long identifiers wrap without clipping.
- Table S1 spans pages 2-3 cleanly.
- Column headings repeat/read coherently across the page break.
- All rows remain aligned and visible.
- No horizontal overflow or orphaned table content observed.

### Page 4
PASS.

- Appendix B heading hierarchy is clear.
- Table S2 is fully contained within the text area.
- All 18 rules are legible and aligned.
- No table clipping, overlap, or excessive compression observed.

### Page 5
PASS.

- Study-4 continuation is visually consistent.
- Long identifiers remain readable.
- No anomalous spacing, clipping, or page-break defect observed.

### Pages 6-7
PASS.

- Appendix C starts cleanly.
- Study-6 artifact-state and assurance-signal identifiers wrap correctly.
- Numbered and bulleted lists are readable with normal indentation.
- No visible replacement characters, black boxes, or broken glyphs observed.

### Page 8
PASS.

- Table S3 is readable at the selected fixed-width layout.
- Gate names, residual-state names, unsafe counts, and benign-loss counts remain legible.
- No cell overlap, clipping, or horizontal overflow observed.
- Text below the table resumes cleanly.

### Pages 9-11
PASS.

- Appendix D sections are continuous and visually stable.
- Long technical identifiers and hyphenated terms wrap acceptably.
- Heading hierarchy, paragraph spacing, and margins remain consistent.
- No clipping, overlap, or malformed page transitions observed.

### Page 12
PASS.

- Appendix D concludes naturally before Appendix E.
- Appendix E text is complete and unclipped.
- Large residual white space is a natural consequence of the document ending and is not a visual defect.
- Page number is present and correctly positioned.

## Cross-document visual controls

PASS:

- No page shows content outside the printable text area.
- No figure or table crosses the page edge or gutter.
- No text overlaps another object.
- No broken or substituted glyphs are visible in rendered pages.
- All page numbers 1-12 are present and consistently positioned.
- Figure and table captions are visually distinct from body text.
- Section order is continuous: Supplementary Fig. S1, Appendix A, Appendix B, Appendix C, Appendix D, Appendix E.

## Scientific presentation controls

PASS:

- Only Study 3 is described as modeling contact.
- Study 4 producer unavailability is not visually or textually collapsed into contact loss.
- Study 6 assurance-signal unavailability is not visually or textually collapsed into contact loss.
- No pooled three-study N or pooled success measure is introduced.
- Fig. S1 remains explicitly a qualitative synthesis rather than an integrated experimental architecture.
- The supplement retains model-boundary language and does not visually overstate operational, flight, certification, or mission-level claims.

## Decision

`PASS_FINAL_SUPPLEMENT_VISUAL_QA`

The exact PDF with SHA-256 `097d35c8696c676cac7a210ed7283982f04dad4a72f82dbd02f5cc83fc12fa3f` is visually acceptable as the short-track peer-review supplement candidate.

No further supplement typography or content changes are authorized unless a later science-preservation/package audit identifies a concrete defect.

Next required gates are science-preservation proof, superseding supplement-decision record, and short-track package freeze. No publisher upload is authorized by this visual-QA record alone.
