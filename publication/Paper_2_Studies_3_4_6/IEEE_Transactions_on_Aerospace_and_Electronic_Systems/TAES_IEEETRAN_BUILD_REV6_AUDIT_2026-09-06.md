# TAES IEEEtran Development Build Revision 6 Audit

**Audit date:** 2026-09-06  
**Status:** `PASS_COMPILED_DEVELOPMENT_ONLY__AUTOMATED_LAYOUT_BEST_CANDIDATE__VISUAL_QA_REQUIRED`  
**Publisher-facing:** No  
**Submission authorized:** No

## Canonical input bindings

- Canonical manuscript SHA-256: `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`
- Figure 1 PDF SHA-256: `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`
- Figure 1 PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`
- Scientific or manuscript-source change by revision 6: No

## Revision-6 deterministic build result

The local canonical checkout completed revision 6 successfully.

Reported build values:

- pages: `18`
- estimated pages beyond 10: `8`
- page size: `612 x 792 pts (letter)`
- text width: `7.100 in`
- column separation: `0.200 in`
- column width: `3.450 in`
- text height: `9.000 in`
- fonts reported: `13`
- all fonts embedded: `PASS`
- LaTeX warnings: `0`
- overfull hboxes: `0`
- overfull vboxes: `18`
- underfull hboxes: `35`
- underfull vboxes: `2`
- layout warning gate: `REVIEW_REQUIRED`

Generated artifact hashes:

- TEX: `29a2a5505158fdd23deb454f236a1f325115a95a5c1984f8815d6e7fdf1a4083`
- PDF: `a3df38376833234786fc5c0cbb59813e96bedc56e05f2df4f1c4357f818ccf37`
- LOG: `8e78d2ebcd1aff1999aa4d8446d67a85c9711c8d37b8d7d4329bdd386eabc344`
- build audit: `c11406bfa73f66b7e607f4202d6871918ca27b13c3a2cb4360c1dd169f9ffa10`

## Revision-6 intervention

Revision 6 preserved revision 5's proper LaTeX math rendering for the common qualification framework, retired all 11 ineffective revision-5 `\\linebreak[2]` hints, and applied localized `\\emergencystretch` only to the four previously identified problem blocks.

Reported localized settings:

- Study-3 endpoint paragraph: `1.50em`
- Study-6 gate-definition list: `0.60em`
- Study-6 G1 paragraph: `0.90em`
- Study-6 assurance-signal limitations paragraph: `1.20em`

Controls:

- `localized_sloppy_blocks=0`
- `global_geometry_changed=NO`
- `science_or_manuscript_source_changed=NO`
- R5 linebreak hints retired: `PASS`
- common-framework math inherited from R5: `PASS`

## Automated-layout interpretation

Revision 6 is the strongest automated development-format candidate to date because it combines:

1. proper mathematical notation in the common framework;
2. zero overfull hboxes;
3. no `\\sloppy` intervention;
4. correct TAES geometry;
5. embedded fonts; and
6. an unchanged, stable 18-page development page count.

The cost is 35 underfull hboxes, including several badness-10000 lines in the locally relaxed blocks. This count is lower than revision 4's 39 underfull hboxes but higher than revision 5's 25. The numeric warning count alone is not sufficient to accept or reject the visual result.

## Vertical warnings

Eighteen repeated overfull-vbox warnings remain, predominantly approximately 4.77391 pt. Revision-4 page-by-page visual QA previously found no visible clipping or margin intrusion from the same systematic condition. Revision 6 does not alter TAES geometry, so those warnings remain provisionally classified as a baseline-grid/text-height interaction pending confirmation from the exact revision-6 PDF.

## Required next gate

The exact revision-6 PDF with SHA-256 `a3df38376833234786fc5c0cbb59813e96bedc56e05f2df4f1c4357f818ccf37` must be attached and visually reviewed. Priority comparison pages are 4, 5, 11, and 16, followed by confirmation of all 18 pages if those corrections are acceptable.

No revision 7, substantive compression, or publisher-facing freeze is authorized before that visual comparison.

**Verdict:** `PASS_REVISION6_AUTOMATED_BUILD__CURRENT_BEST_CANDIDATE__PDF_VISUAL_QA_REQUIRED`
