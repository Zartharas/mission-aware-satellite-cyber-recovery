# TAES IEEEtran Revision 7 Build Audit

**Audit date:** 2026-09-06  
**Build role:** Development-only two-column IEEEtran formatting audit  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Canonical Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`  
**Canonical Figure 1 PNG SHA-256:** `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

## Result

Revision 7 compiled successfully and remains development-only.

Observed build values supplied from the canonical Mac checkout:

- pages: `18`
- estimated pages beyond 10: `8`
- page size: `612 x 792 pts (letter)`
- text width: `7.100 in`
- column gap: `0.200 in`
- column width: `3.450 in`
- text height: `9.000 in`
- font count: `13`
- all fonts embedded: `PASS`
- LaTeX warnings: `0`
- overfull hboxes: `0`
- overfull vboxes: `18`
- underfull hboxes: `30`
- underfull vboxes: `2`
- automated layout gate: `REVIEW_REQUIRED` pending exact PDF visual QA

Generated artifact hashes:

- TEX: `671074fed8047780b3bcfd4497973038b8e9a875f8ca5b7516ecff2ff58bcd7d`
- PDF: `b4726622cb2769055c0541b773ccddcbf84163462e3fdbe16d6fc6933b7b60be`
- LOG: `1e95b842fcf17d8469483ba9455eb2a40dd6c2e5a14b767e45ce468678769e6f`
- build audit: `201543d4d749b998235adbbd3e96682be9f2e220cd33cd60ce8833c336473821`

## Revision 7 intervention

Revision 7 preserves revision 5's proper common-framework mathematical notation and revision 6's three localized Study-6 emergency-stretch blocks while replacing the Study-3 endpoint paragraph stretch with one localized ragged-right typesetting block.

Reported controls:

- `endpoint_raggedright_blocks=1`
- `endpoint_terminal_s_break=SUPPRESSED`
- `preserved_study6_emergencystretch_blocks=3`
- gate-list emergency stretch: `0.60em`
- G1 emergency stretch: `0.90em`
- assurance-limit emergency stretch: `1.20em`
- common-framework math typesetting inherited from R5
- localized sloppy blocks: `0`
- global geometry changed: `NO`
- science or manuscript source changed: `NO`

The endpoint paragraph retains the exact visible scientific identifiers and text. The final `s` in `unsafe_qualified_exposure_s` is protected from becoming a one-character continuation after the final underscore. The paragraph is separated from the following justified prose so the ragged-right treatment does not leak beyond the endpoint-list sentence.

## Comparative automated result

Relative to revision 6:

- overfull hboxes remain `0`;
- underfull hboxes decrease from `35` to `30`;
- page count remains `18`;
- all geometry and font-embedding checks remain unchanged;
- no `\\sloppy` formatting is present;
- proper mathematical rendering remains present.

This is the strongest automated build result to date, but the exact PDF must still be visually inspected before the formatting gate can close.

## Remaining visual QA target

Revision 6 failed visual QA only for the Study-3 endpoint paragraph at the top of page 6. Revision 7 is specifically intended to correct that one localized defect while preserving all previously passing pages.

The exact R7 PDF with SHA-256 `b4726622cb2769055c0541b773ccddcbf84163462e3fdbe16d6fc6933b7b60be` must therefore be rendered and visually checked, with special attention to page 6 and a final all-page regression sweep.

The repeated approximately 4.77 pt vertical warnings remain classified provisionally as visually harmless based on prior full-PDF inspection, but that classification must be confirmed on the exact R7 PDF before publisher-facing freeze.

**Verdict:** `PASS_REVISION7_AUTOMATED_BUILD__EXACT_PDF_VISUAL_QA_REQUIRED`
