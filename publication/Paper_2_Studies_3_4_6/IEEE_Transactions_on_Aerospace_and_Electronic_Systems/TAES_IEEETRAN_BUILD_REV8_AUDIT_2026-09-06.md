# TAES IEEEtran Revision 8 Build Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Build revision:** 8  
**Canonical compressed manuscript commit:** `710a72af05fb418a0d82a659198a677b9e2a8948`  
**Canonical manuscript SHA-256:** `802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48`  
**Verdict:** `PASS_PAGINATION_WITH_ONE_LOCAL_TYPOGRAPHY_BLOCKER`

## 1. Purpose

Revision 8 was the first IEEEtran development build after the controlled Pass-2 R2 manuscript compression. The compression changed Sections IV, V, and IX only and removed 1,918 manuscript words relative to the prior compliance-corrected manuscript while preserving the frozen studies and required claim controls.

R8 intentionally retired the old Study-3 endpoint ragged-right workaround so the compressed Section IV could first be typeset naturally. It retained the 13 common-framework math conversions and the three Study-6 localized emergency-stretch blocks that passed the R7 visual QA.

## 2. Build result

The build completed successfully with:

- pages: 16;
- estimated pages beyond 10: 6;
- page size: 612 x 792 pt, US Letter;
- text width: 7.100 in;
- column gap: 0.200 in;
- column width: 3.450 in;
- text height: 9.000 in;
- overfull hboxes: 2;
- overfull vboxes: 16;
- underfull hboxes: 29;
- underfull vboxes: 1;
- LaTeX warnings: 0;
- fonts: 13;
- all fonts embedded: PASS;
- localized sloppy blocks: 0.

The prior R7 baseline was 18 pages. R8 therefore demonstrates an actual two-page reduction from the controlled 1,918-word manuscript compression.

## 3. Exact development-artifact hashes

- TeX SHA-256: `27968471505df88e10907206029998099cc7aaca427d45a301f60153b877a64e`
- PDF SHA-256: `9914ceeb2165d6cd1bb2bc9a4e0299c28e1d5ea0aa4a680d3940e365f5c17fc2`
- log SHA-256: `20b17deaff557c50bb5edc9763d6d3d9d24e0a9a6ecfb0955ddbd89caea0f0f1`
- build-audit SHA-256: `ee4e9b563821e8b3a1452547578b0247044abcddc5c8d824df15f7dddf5c4339`

These generated artifacts remain development-only and are not frozen publisher-facing files.

## 4. Horizontal-overflow diagnosis

Both R8 overfull hboxes arise from the same compressed Study-3 primary-endpoints paragraph in generated TeX lines 211-212. Reported widths were:

- 25.46812 pt;
- 41.00798 pt.

The paragraph begins `Primary endpoints are` and contains the six long monospaced endpoint identifiers. No other paragraph produced an overfull hbox.

This is therefore one localized typography problem rather than a manuscript-wide layout defect.

## 5. Preserved controls

R8 retained:

- canonical compressed manuscript SHA binding;
- Figure 1 PDF and PNG bindings;
- all four tables;
- 13 proper common-framework math conversions;
- no `\\sloppy`;
- no Revision-5 linebreak hints;
- three previously visually approved Study-6 emergency-stretch blocks;
- TAES geometry;
- font embedding;
- author submission authorization recorded as granted on 2026-09-06 while effective submission remained blocked by remaining package gates.

No scientific file, frozen study output, population, table value, citation, Figure 1 asset, or canonical manuscript prose was changed by the build.

## 6. Vertical diagnostics

The repeated approximately 4.77-pt overfull-vbox pattern remains materially the same systematic condition previously inspected across R7. R8 has not yet received a full page-by-page visual QA, so the vertical diagnostics remain subject to visual confirmation for the new 16-page pagination rather than being automatically waived.

## 7. Decision

Do not perform additional scientific compression in response to the two R8 horizontal overflows. The next revision should address only the compressed Study-3 primary-endpoints sentence in generated LaTeX, preserving normal IEEE justification for the following explanatory prose.

The preferred treatment is the same localized strategy that passed R7 visual QA: ragged-right only for the endpoint-list sentence, plus suppression of the discretionary break immediately before the terminal `s` in `unsafe_qualified_exposure_s`.

R8 is retained as the first verified 16-page pagination baseline but is not a visual-QA-passing submission candidate.
