# TAES PDF Visual QA R9

Date: 2026-09-06 (author local publication-control date)

## Scope

This record documents render-first visual QA of the exact Revision-9 IEEEtran development PDF for Paper 2 after the controlled Pass-2 R2 compression.

The review is visual/formatting QA only. It does not rerun, alter, enlarge, or reinterpret Studies 3, 4, or 6 and does not change the canonical manuscript source.

## Exact bindings

- Canonical manuscript SHA-256: `802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48`
- Canonical manuscript tracking commit: `710a72af05fb418a0d82a659198a677b9e2a8948`
- R9 development PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- R9 generated TeX SHA-256: `381e687bbdc1ccc409ed54bc189d2cfd31b846487bd7e2ae03cc105d0e720557`
- R9 log SHA-256: `5a85f848ccaf5274a8830624ef667b768f27dbe103e751597cd317a7b4e196d2`
- R9 build-audit SHA-256: `c4c475d76bf90e548ee3e67621a6de36a02406cb5feac4960e3b6a04784001c6`
- Figure 1 PDF SHA-256: `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`
- Figure 1 PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

The uploaded R9 PDF was independently hash-checked before rendering and matched the expected R9 PDF SHA-256 exactly.

## Automated build state reviewed

- Pages: 16
- Estimated pages beyond 10: 6
- US Letter: PASS
- Text width: 7.10 in
- Column separation: 0.20 in
- Column width: 3.45 in
- Text height: 9.00 in
- Overfull hboxes: 0
- Overfull vboxes: 16
- Underfull hboxes: 28
- Underfull vboxes: 1
- LaTeX warnings: 0
- Fonts: 13
- All fonts embedded: PASS
- `\sloppy`: absent
- Common-framework math conversions: 13
- Study-3 endpoint ragged-right block: 1
- Terminal `_s` isolation in `unsafe_qualified_exposure_s`: suppressed
- Preserved Study-6 local emergency-stretch blocks: 3
- Geometry changed from approved TAES target: NO
- Science/manuscript source changed by R9 builder: NO

## Render-first inspection

All 16 pages were rendered and inspected. The following page-level checks were completed.

### Page 1

PASS. Title, author line, affiliation, Abstract, Index Terms, and beginning of Section I render cleanly. No clipping, overlap, broken glyphs, or margin intrusion was observed.

### Pages 2-3

PASS. Introduction and Related Work flow normally in two columns. Citation rendering and subsection hierarchy are visually consistent. No abnormal spacing or column collision was observed.

### Page 4

PASS. The common trust-qualification mathematical notation renders as mathematical notation rather than monospaced ASCII. `Q_j(E_j)`, `U_j`, `C_j`, and inline `Q_3/T_3`, `Q_4/T_4`, and `Q_6/T_6` usages are visually correct. No clipping or equation-column intrusion was observed.

### Page 5

PASS. Table I is fully visible and uncropped. The compressed Study-3 primary-endpoint sentence uses the single localized ragged-right treatment cleanly. The endpoint identifiers remain readable, no terminal `s` is isolated from `unsafe_qualified_exposure_s`, and normal IEEE-style justification resumes immediately in the following explanatory sentence. No exaggerated interword spacing was observed.

### Page 6

PASS. Study-3 results and limitations render cleanly. No residual endpoint overflow, clipping, or column imbalance requiring intervention was observed.

### Page 7

PASS. Table II is complete, aligned, legible, and inside the text area. All nine reported rows are present, including the structural-zero cells and truthful K4 controls. Surrounding Study-4 prose is visually clean.

### Page 8

PASS. Table III is complete and uncropped. All 18 Study-4 rules are present and legible. The transition into Study 6 does not create overlap or abnormal whitespace.

### Pages 9-10

PASS. Study-6 state, signal, and gate prose renders cleanly. Long monospaced identifiers break without horizontal intrusion. The three preserved localized Study-6 typography treatments do not create the stretched-spacing defects seen in the historical R4 build.

### Page 11

PASS. Table IV is complete, aligned, and uncropped. Residual state names, unsafe counts, and benign-loss counts are readable. The transition to Section VII is clean.

### Page 12

PASS. Figure 1 is fully visible, centered, uncropped, and legible. All three parallel panels are present; caption and boundary statement are intact. No figure-to-text collision or margin intrusion was observed.

### Pages 13-14

PASS. Cross-study synthesis and validity sections render normally. No clipping, overlap, broken glyphs, or abnormal column spacing was observed.

### Page 15

PASS. Validity/future-evaluation text, Section IX conclusion, and the IEEE AI-use acknowledgment all render cleanly. The acknowledgment remains complete and unobstructed.

### Page 16

PASS. References [1]-[13] are present and legible. Reference [11] identifies The Update Framework Specification v1.0.36 and its GitHub release record. No reference clipping or margin intrusion was observed. The unused lower/right page area is normal end-of-manuscript whitespace, not a layout defect.

## Margin and clipping verification

Rendered-page content bounds were checked across all 16 pages. Left and right content margins were consistent page to page, and top/bottom content stayed within the approved page area. No evidence of content touching or crossing the physical page edge was observed.

## Vertical-box warnings

The build reports repeated approximately 4.77 pt overfull-vbox diagnostics. In the rendered PDF these warnings do not produce visible clipping, overlap, bottom-margin intrusion, or lost text. They are therefore classified as visually harmless for this exact R9 PDF and do not justify changing the approved 9.00-in TAES text height.

## Comparison with prior development state

- R7 visual-QA-passed baseline: 18 pages.
- Pass-2 R2 compressed canonical manuscript: 1,918-word controlled reduction.
- R9: 16 pages.
- Horizontal overflow: R7 0, R8 2, R9 0.
- R9 preserves the approved common-framework math and Study-6 typography while adapting the Study-3 endpoint treatment to the compressed prose.

The 1,918-word controlled editorial reduction therefore produced a real two-page reduction without a detected visual or scientific-format regression.

## Verdict

`TAES_PDF_VISUAL_QA_R9=PASS_ALL_16_PAGES`

`TAES_R9_FORMAT_QA=PASS`

`R9_EXACT_PDF_SHA256=a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

`CANONICAL_MANUSCRIPT_SHA256=802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48`

`SCIENCE_CHANGED=NO`

`MANUSCRIPT_SOURCE_CHANGED_BY_VISUAL_QA=NO`

`PUBLISHER_FACING=NO_PENDING_FILE_FREEZE_AND_REMAINING_PACKAGE_GATES`

## Editorial length recommendation

The 16-page R9 build is a scientifically defensible stopping point for compression. Further compression is not recommended solely to remove one additional page unless a separate editorial review identifies genuine redundancy. The preferred next action is to freeze the 16-page R9 manuscript/PDF package, then complete the portal-field, supplementary-material, and final upload-manifest/hash gates.
