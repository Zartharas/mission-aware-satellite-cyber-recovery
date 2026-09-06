# TAES IEEEtran Development Build Revision 4 Audit

**Audit date:** 2026-09-06  
**Builder:** `TAES_BUILD_IEEETRAN_R4.py`  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Canonical Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`  
**Scientific rerun authorized or performed:** No  
**Publisher-facing status:** No  
**Submission authorized:** No

## 1. Revision objective

Revision 4 preserved the canonical manuscript, Tables I-IV, Figure 1, all frozen Study 3, Study 4, and Study 6 results, and all TAES geometry settings. It changed only generated-LaTeX line-breaking behavior in four identifier-dense blocks after Revision 3 showed that explicit identifier break opportunities alone did not eliminate the remaining horizontal overflow.

Revision 4 used localized relaxed paragraph line breaking in exactly four generated-TeX blocks. It did not change the Markdown manuscript source, scientific wording, frozen identifiers, table rows, figure content, font size, page size, text width, column width, column separation, or text height.

## 2. Build result

The user-executed macOS build reported:

- `TAES_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY`
- pages: `18`
- estimated pages over 10: `8`
- page size: `612 x 792 pts (letter)`
- text width: `7.100 in`
- column separation: `0.200 in`
- column width: `3.450 in`
- text height: `9.000 in`
- overfull hboxes: `0`
- overfull vboxes: `18`
- underfull hboxes: `39`
- underfull vboxes: `2`
- LaTeX warnings: `0`
- fonts: `9`
- all fonts embedded: `PASS`
- layout warning gate: `REVIEW_REQUIRED`

Revision-specific output reported:

- `TAES_IEEETRAN_BUILD_REVISION=4`
- `breakable_code_strategy=R3_EXPLICIT_DISCRETIONARY_BREAKS_PLUS_LOCALIZED_SLOPPY`
- `localized_sloppy_blocks=4`
- `global_geometry_changed=NO`
- `science_or_manuscript_source_changed=NO`
- `TAES_IEEETRAN_R4_OVERFULL_CONTEXT_BEGIN`
- `NONE`
- `TAES_IEEETRAN_R4_OVERFULL_CONTEXT_END`

## 3. Development artifact hashes

Revision-4 development artifacts reported:

- TeX SHA-256: `6a8701bbb4fdba42503e02efb5cb5064204b740f128d54315f55db6a5c557ba0`
- PDF SHA-256: `7964e8dd9460ca1863a46365a474a05b226b3bc5bd8eb2af6a9d1a82814a5e35`
- log SHA-256: `cdb0e572d0475a428756e28ddbc2f16d4c4d69f7b6cf50ee5ff8030f147112ff`
- build-audit SHA-256: `2478d61e2dd5f87741794daeff0a7b0d1b61e6f62ba486c7eed548cbc4446511`

These development artifacts remain untracked locally and are not publisher-facing files.

## 4. Horizontal layout verdict

`PASS_HORIZONTAL_LAYOUT_CLEAN`

Revision 4 eliminated all recorded horizontal overflow without changing manuscript source or TAES geometry. The horizontal-layout subgate is therefore complete for the development build.

## 5. Vertical warning status

The build still reports 18 overfull vboxes, usually approximately `4.77391 pt`, plus 2 underfull vboxes. These warnings remain unresolved for final format approval because they must be correlated with rendered page content and physical page margins before any geometry change is considered.

The repeated small vertical excess is consistent with an IEEEtran column-grid/text-height interaction, but that interpretation is not sufficient to mark the warnings harmless. The exact PDF must be rendered and visually inspected page by page. No text-height, top-margin, bottom-margin, or baseline-grid adjustment is authorized solely to suppress the log messages.

## 6. Page-count interpretation

The 18-page count is now a stable development baseline across multiple increasingly clean builds:

- initial complete build: 18 pages, 24 overfull hboxes;
- Revision 2: 18 pages, 7 overfull hboxes;
- Revision 3: 18 pages, 7 overfull hboxes;
- Revision 4: 18 pages, 0 overfull hboxes.

Because horizontal overflow was eliminated without reducing the page count, the 18-page count should no longer be treated as a line-breaking artifact. It remains a development estimate, not an accepted-paper billing determination.

No scientific content should be removed merely to reach 10 pages. Any later compression must preserve all mandatory null findings, exact frozen boundaries, study-separation controls, limitations, and residual-state identities.

## 7. Current gate decision

`PASS_HORIZONTAL_LAYOUT__PDF_VISUAL_QA_AND_VERTICAL_MARGIN_VERIFICATION_PENDING`

Required next actions:

1. inspect the exact Revision-4 PDF with SHA-256 `7964e8dd9460ca1863a46365a474a05b226b3bc5bd8eb2af6a9d1a82814a5e35`;
2. render all 18 pages and visually inspect title/author block, abstract, two-column flow, Tables I-IV, Figure 1, references, acknowledgment, and page bottoms;
3. verify that the repeated vertical box warnings do not cause clipping, overlap, or violation of the required top/bottom margins;
4. only after visual evidence, decide whether a vertical-grid adjustment is needed;
5. keep publisher-facing PDF freeze and portal submission blocked until the remaining mandatory gates pass.
