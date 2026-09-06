# TAES IEEEtran Revision 6 PDF Visual QA

**Audit date:** 2026-09-06  
**Build role:** Development-only TAES/IEEEtran visual QA  
**Exact PDF SHA-256:** `a3df38376833234786fc5c0cbb59813e96bedc56e05f2df4f1c4357f818ccf37`  
**Pages:** `18`  
**Page size:** `612 x 792 pts (US Letter)`  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Canonical Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`

## Automated build state

Revision 6 compiled successfully with:

- `overfull_hbox_count=0`;
- `overfull_vbox_count=18`;
- `underfull_hbox_count=35`;
- `underfull_vbox_count=2`;
- `latex_warning_count=0`;
- all 13 fonts embedded;
- exact TAES geometry retained;
- no `\\sloppy`;
- revision-5 `\\linebreak[2]` hints retired;
- common-framework mathematical notation preserved in LaTeX math mode;
- no scientific or canonical Markdown manuscript change.

## Render-first visual inspection

The exact PDF was rendered page by page at 180 dpi and all 18 pages were inspected.

### Global findings

PASS:

- no clipped text;
- no overlapping text, tables, figure, or captions;
- no broken or missing glyphs;
- no visible side-margin or top/bottom-margin intrusion;
- title, author, abstract, and index terms are intact;
- Tables I-IV are complete and remain inside the page width;
- Figure 1 is complete, readable, and uncropped;
- corrected TUF v1.0.36 reference is present;
- IEEE AI-use acknowledgment is present;
- references [1]-[13] are present;
- page 4 common-framework expressions now render as mathematical notation rather than literal monospaced ASCII;
- Study-6 gate-definition and G1 paragraphs on page 11 are visually acceptable;
- Study-6 assurance-signal limitation paragraph on page 16 is visually acceptable.

The repeated approximately 4.77-pt overfull-vbox condition does not produce a visible clipping or margin defect in the rendered pages. The required 9.00-in text height should therefore not be changed merely to suppress that diagnostic.

### Remaining defect

FAIL, localized typography only:

The Study-3 frozen-primary-endpoints paragraph at the top of page 6 remains visibly uneven. The local 1.50-em emergency stretch removes horizontal overflow but produces conspicuous interword gaps in the endpoint-list sentence. In addition, `unsafe_qualified_exposure_s` breaks with the terminal `s` isolated on the next line. This is visually inferior to normal IEEE body typography even though no content is clipped.

No other page-level blocker was identified.

## Interpretation

Revision 6 is the strongest development build so far and establishes that the 18-page count is stable under mechanically clean horizontal layout. The remaining defect is not scientific and does not justify manuscript compression, endpoint abbreviation, geometry changes, or any frozen-study modification.

A revision 7 may alter only generated-LaTeX formatting for the Study-3 endpoint-list sentence while preserving:

- the exact endpoint names and punctuation;
- all manuscript prose and scientific claims;
- revision-5 mathematical notation corrections;
- revision-6 Study-6 localized emergency-stretch settings;
- Tables I-IV and Figure 1;
- TAES geometry;
- canonical manuscript and figure hashes.

**Verdict:** `PASS_ALL_PAGES_EXCEPT_LOCALIZED_STUDY3_ENDPOINT_LIST_TYPOGRAPHY__REVISION7_REQUIRED`
