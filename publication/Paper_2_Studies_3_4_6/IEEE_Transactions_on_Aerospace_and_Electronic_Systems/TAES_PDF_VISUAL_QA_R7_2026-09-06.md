# TAES Paper 2 IEEEtran R7 PDF Visual QA

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Manuscript type:** Regular Paper  
**R7 builder:** `TAES_BUILD_IEEETRAN_R7.py`  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`  
**Figure 1 PNG SHA-256:** `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`  
**R7 TeX SHA-256:** `671074fed8047780b3bcfd4497973038b8e9a875f8ca5b7516ecff2ff58bcd7d`  
**R7 PDF SHA-256:** `b4726622cb2769055c0541b773ccddcbf84163462e3fdbe16d6fc6933b7b60be`  
**R7 log SHA-256:** `1e95b842fcf17d8469483ba9455eb2a40dd6c2e5a14b767e45ce468678769e6f`  
**Pages:** 18  
**Page size:** 612 x 792 pt, US Letter  
**Scientific-result changes:** None  
**Submission authorized:** No  

## 1. Automated build state

The R7 development build completed successfully with the canonical manuscript and Figure 1 bindings intact.

- TAES geometry: PASS
- text width: 7.10 in
- column width: 3.45 in
- column gap: 0.20 in
- text height: 9.00 in
- overfull hboxes: 0
- underfull hboxes: 30
- overfull vboxes: 18
- underfull vboxes: 2
- LaTeX warnings: 0
- embedded fonts: 13/13 PASS
- `\\sloppy`: absent
- common-framework math: proper LaTeX math
- page count: stable at 18

R7 preserves R5's corrected mathematical notation and the three visually acceptable Study-6 localized emergency-stretch blocks from R6. It replaces the R6 Study-3 endpoint emergency-stretch block with a local ragged-right treatment and suppresses the isolated terminal-`s` break in `unsafe_qualified_exposure_s`.

## 2. Render-first visual inspection

The exact R7 PDF byte stream with SHA-256 `b4726622cb2769055c0541b773ccddcbf84163462e3fdbe16d6fc6933b7b60be` was rendered at 200 dpi. All 18 pages were inspected visually.

### Page 6 endpoint correction

PASS.

The Study-3 endpoint list is now readable and visually controlled. The prior R6 defect is resolved:

- `unsafe_qualified_exposure_s` no longer leaves an isolated terminal character;
- no exaggerated interword spacing is present;
- the ragged-right endpoint block is limited to the long identifier list and reads as an intentional local formatting treatment;
- subsequent prose returns to normal justified IEEEtran layout;
- no horizontal intrusion or clipping is visible.

### Page 4 common-framework math

PASS.

`Q_j(E_j)`, `T_j`, `U_j`, `C_j`, and the Study-specific `Q_3/T_3`, `Q_4/T_4`, and `Q_6/T_6` notation render as mathematical notation rather than monospaced ASCII.

### Study-6 pages 11 and 16

PASS.

The R6/R7 localized emergency-stretch treatment does not produce the objectionable wide spacing seen in R4. Identifier-dense paragraphs remain legible and professionally justified.

## 3. Full 18-page sweep

PASS.

The full rendered manuscript was checked for publisher-facing layout defects.

- title, author, and affiliation block: PASS
- abstract and Index Terms: PASS
- two-column layout: PASS
- section ordering I-IX: PASS
- Table I: PASS, no clipping or overflow
- Table II: PASS, no clipping or overflow
- Table III: PASS, no clipping or overflow
- Table IV: PASS, no clipping or overflow
- Fig. 1: PASS, readable, centered, caption intact, no clipping
- equations and mathematical notation: PASS
- monospaced technical identifiers: PASS
- acknowledgment and IEEE AI-use disclosure: PASS, present once
- references [1]-[13]: PASS
- TUF reference [11] v1.0.36: PASS
- page numbers: PASS
- broken glyphs or black boxes: NONE
- text overlap: NONE
- figure/table overlap: NONE
- horizontal clipping: NONE
- bottom-margin intrusion: NONE
- blank or malformed pages: NONE

## 4. Repeated vertical box warnings

The build continues to report 18 overfull-vbox diagnostics, approximately one per page and generally about 4.77 pt. The rendered PDF shows no corresponding clipping or margin intrusion. All page content remains visibly inside the intended text area.

These diagnostics are therefore classified for this R7 build as:

`PASS_NO_VISIBLE_CLIPPING_OR_MARGIN_INTRUSION`

The TAES-required 9-inch text height must not be changed merely to silence these diagnostics.

## 5. Format and visual-QA verdict

`TAES_IEEETRAN_R7_FORMAT_QA=PASS`

`TAES_PDF_VISUAL_QA_R7=PASS_ALL_18_PAGES`

The exact R7 development PDF is a visually acceptable formatting baseline for the manuscript. This audit closes the TAES formatting and PDF visual-QA gates for R7.

It does **not** make the file publisher-facing and does **not** authorize submission. The next manuscript-level decision is the separate 18-page length/overlength review. Final author metadata, supplementary-material decision, portal-field audit, upload manifest/hashes, and explicit final author submission authorization remain unresolved.
