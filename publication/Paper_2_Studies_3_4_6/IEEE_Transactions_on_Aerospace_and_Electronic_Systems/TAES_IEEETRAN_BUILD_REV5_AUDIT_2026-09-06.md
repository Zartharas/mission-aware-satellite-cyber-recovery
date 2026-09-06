# TAES IEEEtran Revision 5 Build Audit

**Audit date:** 2026-09-06  
**Build role:** Development-only two-column IEEEtran formatting audit  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Canonical Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`  
**Canonical Figure 1 PNG SHA-256:** `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

## Result

Revision 5 compiled successfully after correction of an endpoint-separator guard. The build remained development-only and did not change the canonical Markdown manuscript or any frozen study result.

Observed build values supplied from the canonical Mac checkout:

- pages: `18`
- estimated pages beyond 10: `8`
- page size: `612 x 792 pts (letter)`
- text width: `7.100 in`
- column gap: `0.200 in`
- column width: `3.450 in`
- text height: `9.000 in`
- fonts reported: `13`
- all fonts embedded: `PASS`
- LaTeX warning count: `0`
- overfull hboxes: `7`
- overfull vboxes: `18`
- underfull hboxes: `25`
- underfull vboxes: `2`
- layout warning gate: `REVIEW_REQUIRED`

Generated artifact hashes:

- TEX: `e51f4ca8a83fe357d7d96bcacb4daa4a025af40b08e7f88d99f51a94c04d5ef2`
- PDF: `5d89c7114a5dd49806fd65b01f0467ed2b9b48bd89ae46a7fa88441aebe5a655`
- LOG: `31522ece153ad48bcb5bcaedebfd20afea7969a67ce6be504816b9783dba55c4`
- build audit: `7dad87cf7fd5b5e6c883891fa55f0503412a883fcd0ff2a6d067eaff5e335df0`

## Revision 5 interventions

Revision 5 deliberately started from revision 3 rather than revision 4, so the visually unacceptable localized `\\sloppy` treatment was not inherited.

The generated LaTeX applied two formatting-only changes:

1. thirteen common-framework notation conversions to proper LaTeX math, including `Q_j(E_j)`, `T_j`, `U_j`, `C_j`, `Q_3/T_3`, `Q_4/T_4`, `Q_6/T_6`, and the Paper-2 `N` symbol;
2. eleven targeted `\\linebreak[2]` incentives at natural separator points in the four previously identified horizontal-overflow locations.

Reported revision controls:

- `r5_base=REVISION_3_NO_SLOPPY`
- `common_framework_math_conversions=13`
- `targeted_linebreak_incentives=11`
- `common_framework_math_typesetting=LATEX_MATH`
- `localized_sloppy_blocks=0`
- `global_geometry_changed=NO`
- `science_or_manuscript_source_changed=NO`

## Math-rendering result

The generated TeX now contains proper math-mode notation for the common framework, including:

- `\\[Q_j(E_j)\\in\\{0,1\\}\\]`
- `\\[U_j = 1[Q_j(E_j)=1 \\land T_j=0].\\]`
- `\\[C_j = 1[Q_j(E_j)=0 \\land T_j=1].\\]`
- inline math for `Q_3/T_3`, `Q_4/T_4`, and `Q_6/T_6`.

The font count increased from 9 to 13 because Computer Modern mathematical fonts were added. All 13 fonts were embedded.

## Horizontal-overflow result

The eleven `\\linebreak[2]` incentives did not materially change the line-breaking outcome. The same seven overfull hboxes remained at the same four generated-TeX locations and with the same reported widths as revision 3:

1. Study 3 frozen-primary-endpoints paragraph: `4.01677`, `24.26808`, `25.46812`, and `41.00798` pt;
2. Study 6 G4/G5 gate-definition list: `5.10483` pt;
3. Study 6 G1 target-digest paragraph: `11.00798` pt;
4. Study 6 assurance-signal limitations paragraph: `14.89772` pt.

This shows that penalty-based targeted break incentives alone are insufficient. The remaining condition is paragraph-justification pressure around long technical identifiers rather than missing math conversion or global geometry error.

## Typography interpretation

Revision 5 is preferable to revision 4 as a base because:

- no `\\sloppy` formatting is present;
- underfull hboxes decreased from 39 in revision 4 to 25;
- proper mathematical notation is restored;
- all TAES geometry values remain unchanged;
- all fonts remain embedded.

Revision 5 is not yet suitable for publisher-facing freeze because the seven horizontal overflows remain.

## Next action

Revision 6 should preserve revision 5 math rendering but remove the ineffective `\\linebreak[2]` experiment. It may apply only modest, localized `\\emergencystretch` values to the four affected blocks, tuned by problem severity. It must not use `\\sloppy`, change global geometry, edit canonical manuscript prose, abbreviate identifiers, remove table rows, or alter frozen science.

The repeated vertical warnings remain visually classified from revision 4 as not causing clipping or margin intrusion and must not be addressed by changing the mandated 9-inch text height.

**Verdict:** `PASS_REVISION5_MATH_CORRECTED_NO_SLOPPY__HORIZONTAL_OVERFLOW_UNCHANGED__REVISION6_REQUIRED`
