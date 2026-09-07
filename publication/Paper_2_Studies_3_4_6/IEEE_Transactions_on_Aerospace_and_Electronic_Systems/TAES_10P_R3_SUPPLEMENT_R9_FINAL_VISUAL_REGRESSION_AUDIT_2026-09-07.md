# TAES Paper 2 Short Track - Supplement R9 Final Visual Regression Audit

**Date:** 2026-09-07  
**Branch:** `paper2/taes-10-page-compression`  
**Journal:** IEEE Transactions on Aerospace and Electronic Systems  
**Paper:** *Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance*  
**Status:** `PASS_FINAL_SUPPLEMENT_VISUAL_REGRESSION`

## 1. Artifact identity

Corrected supplementary PDF reviewed:

`TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.pdf`

SHA-256:

`f570dbb7d489e53da74b3942ba08e9cd5008bab4f50e72ddb06e27ba0c1fdabb`

Corrected supplementary source SHA-256:

`c3496de9644be4e9ee38b97f2cb98faf7c1aac2821c5575eb2b9a96f198ce95f`

Paired short main article PDF SHA-256:

`f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`

Frozen 16-page R9 fallback PDF SHA-256:

`a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

## 2. Mechanical gate inherited from R9 build

The local R9 corrected-build evidence reported:

- pages: 12
- page size: US Letter, 612 x 792 pt
- overfull hboxes: 0
- overfull vboxes: 0
- LaTeX warnings: 0
- fonts reported: 4
- all fonts embedded: PASS
- Fig. S1 embedded: YES
- Appendices A-E text gate: PASS
- Tables S1-S3 text gate: PASS
- table cross-reference gate: `PASS_S1_S2_S3_NO_LEGACY_II_III_IV`
- supplement table values changed: NO
- experimental results changed: NO
- science files changed: NONE
- study rerun: NO

## 3. Focused R8-to-R9 visual regression

The exact corrected R9 PDF was rendered and pixel-compared with the previously visually approved R8 supplement at 180 dpi.

Result:

- total pages in each PDF: 12
- changed pages: 3
- unchanged pages: 9

Pixel-identical pages:

`1, 2, 5, 6, 7, 9, 10, 11, 12`

Changed pages:

- page 3: Study-3 prose reference changed from legacy Table II to `Table S1`
- page 4: Study-4 prose reference changed from legacy Table III to `Table S2`
- page 8: two Study-6 prose references changed from legacy Table IV to `Table S3`

No other page changed.

## 4. Visual inspection of changed pages

### Page 3

The sentence following Table S1 now reads `Table S1 values are logical model time...`. The correction is fully readable. No clipping, overlap, line collision, margin violation, table shift, or pagination defect is visible.

### Page 4

The Study-4 threshold section now reads `Table S2 gives the complete frozen map as first/systematic counts.` Table S2 remains fully visible and unchanged in values and structure. No clipping, overlap, table shift, or margin defect is visible.

### Page 8

The Study-6 gate-frontier section now reads `Table S3 reports the canonical gate summary.` The denominator paragraph also correctly refers to `Table S3`. Table S3 remains fully visible and unchanged in values and residual-state identities. No clipping, overlap, line collision, or margin defect is visible.

## 5. Whole-document visual controls

The 12-page supplement remains visually coherent after the four editorial cross-reference corrections. The following remain satisfactory:

- title and author block
- Fig. S1 and caption
- Appendix A Study-3 methods and Table S1
- Appendix B complete Study-4 18-rule threshold map and Table S2
- Appendix C Study-6 definitions and Table S3
- Appendix D validity and aerospace boundaries
- Appendix E non-pooling control
- page numbering and page breaks
- margins and text block placement
- long identifiers and monospaced tokens
- no broken glyphs, black squares, clipping, overlap, or table overflow
- final-page balance is acceptable for the natural end of Appendix E

## 6. Decision

`PASS_FINAL_SUPPLEMENT_VISUAL_REGRESSION`

The corrected R9 supplement is visually approved. The four editorial table cross-reference corrections introduce no scientific change and no unintended layout regression.

No further supplement typography or content changes are authorized absent a newly demonstrated defect.
