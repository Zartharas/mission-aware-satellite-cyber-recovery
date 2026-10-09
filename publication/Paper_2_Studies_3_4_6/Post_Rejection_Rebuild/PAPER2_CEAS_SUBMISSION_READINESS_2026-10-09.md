# Paper 2 — CEAS Space Journal preparation and fail-closed submission checklist

This package is a **CEAS-specific R5 editorial derivative**, not a previously submitted version and not a completed portal submission. The sole author previously submitted an older TAES R10 version, which received editorial prescreen rejection on 2026-09-26 without external peer review. The immutable R4 source and its frozen Studies 3/4/6 and separately governed S3X/S6X evidence are not modified.

## Journal-specific requirements (official source)

Journal: [CEAS Space Journal](https://link.springer.com/journal/12567). Author instructions: https://link.springer.com/journal/12567/submission-guidelines (accessed 2026-10-09). Article class: **Original Research Article**; the journal's review-article class is invitation-only and is inappropriate here. The journal uses **single-blind** peer review. The journal is **hybrid**, and choosing open access is separate from scientific or submission acceptance.

Verified format: **150–250 abstract words**, **4–6 keywords**, editable Word (.docx) or LaTeX with source files; a PDF accompanies Word. Decimal headings with at most three levels; numbered references [n], numbered Arabic tables, numbered Fig. captions and artwork in the text. Original research requires a **Data Availability Statement**; author contributions and competing-interest information must also be supplied through the submission interface. The journal specifically requires disclosure of substantive LLM-assisted drafting; limited copy editing is treated differently. The R4 disclosure already identifies substantive AI editorial participation and was preserved/adapted. Do not claim the AI use was only copy editing.

## Prepared files

- `PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md`: complete venue-specific R5 editorial source derived from the R4 body; includes reformatted headings, table/figure numbering, 228-word abstract, six keywords, AI disclosure and declarations requiring author confirmation.
- `PAPER2_CEAS_TITLE_PAGE_DRAFT_2026-10-09.md`: verified sole-author identity carried from prior Paper-2 submission; confirm correspondence email and final author statements.
- `PAPER2_CEAS_COVER_LETTER_DRAFT_2026-10-09.md`: venue-specific contribution and scope summary, marked unsent.
- `PAPER2_CEAS_JOURNAL_COMPLIANCE_GATE_2026-10-09.json`: machine-readable status, exact submission holds and immutable source binding.
- `scripts/audit_paper2_ceas_r5.py`: fail-closed static manuscript gate; it checks frozen R4 blob, abstract/keywords, tables/figure, study boundaries and prohibited actions.
- `scripts/build_paper2_ceas_package.py`: `--check` checks tracked source **only** in CI; `--draft-preview --out-dir <new external directory>` uses local pandoc, CairoSVG and LibreOffice to create a Word/PDF draft outside the repo. No runtime or scientific execution; it must never claim submission readiness without manual PDF layout review.

## Must clear before submission

1. Corresponding email, full legal author name display, affiliation, competing interests, support/funding, third-party data permissions and any acknowledgments need explicit final author confirmation.
2. Decide a truthful and reviewer-accessible **Data Availability** and **Code Availability** statement; a private repository cannot be presented as publicly downloadable.
3. Verify all 20 reference entries/DOIs against cited originals and current CEAS reference style, and independently review figure alt/caption, five table legibility and rights.
4. Execute the local Word/PDF *draft preview* command after exact-head CI, then inspect every rendered PDF page. The preview is **not** submission-ready.
5. Finalize declarations, generate a clean manuscript without placeholders, prepare upload files and portal field map, then request an explicit **final submit** instruction. No submission or merge is authorized by this preparation work.

**No** P2X v2f runtime, COSMOS, faults, manuscript scientific recomputation, or PR #215 merge is required for CEAS editorial submission; the separate P2X validation track remains closed and its 55 inventory hash variances are not paper results.

## 2026-10-09 CEAS first-pass terminology and citation correction

The CEAS-specific abstract has 228 whitespace-delimited words. It replaces S3X/S6X/cFS/ESA shorthands with descriptive phrases so an editor can read the abstract without undefined project-specific abbreviations. The canonical Fig. 1 caption drops terminal punctuation under the journal's published artwork rule; its scientific content and original vector source remain unchanged.

Reference **[6]** is the IETF `draft-ietf-rats-multi-verifier-00` Internet-Draft (published online 2026-05-05, expires 2026-11-06) and was a work-in-progress document at the source-review checkpoint. CEAS instructs authors to list published or accepted works in References and otherwise use text mentions for unpublished works. **Do not silently treat this draft as a peer-reviewed or finalized standard.** Before submission either substantiate an allowable published-version citation or modify the relevant in-text context/references with a claim-preserving editorial check. DOI/reference validation for the other entries remains separately required.

## Bibliography source screen

The separate [CEAS reference-integrity record](PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.md) audits all 20 references by identifier lookup and known official sources, preserving ambiguities and the IETF Internet-Draft HOLD. This is NOT final bibliographic verification and does not change frozen claims.

## 2026-10-09 bounded reference-resolution and repository-access update

Exact pre-edit head `1ee5f22ddb4c29b9f09e14bb7ed041ca2879d3c1` passed workflow #1435 (`37939755849`). Original 20-reference automated screening results remain historical; following primary-source checks, the unpublished IETF Internet-Draft [6] was removed from R5, the applicable RATS architectural distinction was referenced to published RFC 9334 [5], and original [7]–[20] were renumbered as [6]–[19]. Source-to-claim semantics remain narrow. The current manuscript contains 19 entries; the separately prepared source ledger records the original 20-reference screening population and remaining metadata gaps. The final bibliographic gate is still HOLD.

The GitHub API currently returns repository visibility `public`; the earlier assertion of a `private` repository was not accurate for this verified state. Public repository visibility does not prove that separately preserved ignored canonical outputs and external inputs are reviewer-accessible. The data/code statements therefore remain explicitly conditional on author confirmation.

The author-host rendering attempt failed closed at `libreoffice_required_for_pdf`, so DOCX/PDF page-layout QA and final portal readiness remain unverified.

## 2026-10-09 uploaded 32-page preview QA — NOT APPROVED

The uploaded exact-head draft from `a979b28e690b462cb7e9e01196e6ca0a28784406` rendered to **32 US-letter pages** with DOCX SHA-256 `20dc7b505fa8746ebf2b06993fe832da720112a85d8c98f3490cea64a3789b58` and PDF SHA-256 `28553bf0fc7be0500978d15c6dbc497384014cd1eddc8b75cb1a06fe75c1cdf5`. `BUILD_AUDIT.json` matched; Git worktree was clean. All 32 PDF pages were inspected in rendered contact sheets. **Visual QA FAIL:** unreadable six-column Table 1 on pages 8–9; wrapped gate identifiers in Table 4 on pages 19–20; duplicate Figure 1 caption with small embedded labels on page 10; literal Markdown `### 2.2` on page 5; tables 2/3/5 split across pages 14–15, 16–17, 21–22; unresolved declarations on pages 1 and 29–30. This is a *previous preview* baseline, not a current approved output.

The CEAS-only R5 edit reduces Table 1 from six to four columns and Table 2 from five to four without deleting any data rows or changing values. Table 4 uses G0–G5 short labels with an explicit gate-name legend. Figure 1 uses a single caption, and heading 2.2 is separated. The existing local builder adds Word page breaks before tables 4 and 5 plus no-split row controls using the standard library. **New-head document rendering and full-page QA remain mandatory.** R4, frozen studies, Figure 1 source SVG, and TAES R10 are unmodified.

### 2026-10-09 second preview QA (31 pages) and bounded layout reflow

The **second** uploaded author-host preview was rendered at `41cf5b8f4b128b7eeb07a36063b14b0f6c2fa513`; exact-head workflow #1438, run `37972985997`, is **completed SUCCESS**. The output is 31 US-letter pages; uploaded SHA-256 DOCX `0aeb2c3b0ae80b829fffe60670d19410c1cc90ea392928308ccb562e583210ef`; PDF `3d925eeaaed21b3b7ed70d6b9c308a737c01bc3cf8b5c1d3cc9f4eaad804d111`. The uploaded `BUILD_AUDIT.json` matches both. All 31 PDF pages were reviewed in rendered contact sheets; **SECOND_VISUAL_QA=HOLD**: heading 2.2 and Figure 1 duplicate caption are fixed, Table 4 is now legible, and Table 5 fits on one page, but Table 1 has an orphan caption on page 7 and narrow technical labels on page 8, Table 2 splits over pages 13–14 with awkward labels, and the only material on page 31 is reference [19]. Figure 1 text remains too small at journal print size, and declarations/access placeholders remain.

A **local-only** experiment on the uploaded Word file applied just OOXML layout properties: caption keep-with-next; proportionate explicit widths and 9-point cell text for dense Tables 1–2; removal of unconditional Table 4/5 page breaks; tighter 10-point reference text/spacing. The experimental LibreOffice PDF rendered as **29 pages**. Independent `python-docx` comparison confirmed `WORD_CONTENT_PARITY=PASS` and `TABLE_CELLS_PARITY=PASS` for all five tables, with no image or scientific text edits. This does not establish author-host parity or final visual approval. The standalone corrected builder is committed for a fresh exact-head preview after CI. No private local draft binaries are committed; original first and second hashes remain retained as rejected-preview evidence.

## 2026-10-09 third uploaded preview: 29-page visual QA and bounded table-layout regression

The third author-host preview was successfully generated from exact head `35f035f79f4335811a4f048ab01732adc1c4f011`, with CI workflow #1439 (run `37974650149`) completed **success**. Uploaded DOCX SHA-256 `3067cd516a5e0dd4f51e14a57a27f886f8549225b252624ebcfdb94f35438eb9` and PDF SHA-256 `06236cb2092fc2f1020a84d78cb2b0f627f490359da14790b1431b8400310d7e` each match the uploaded `BUILD_AUDIT.json`; PDF 29 letter pages and five DOCX tables (6×4, 12×4, 19×3, 7×4, 8×2). All 29 PDF pages were reviewed in rendered contact sheets. Every one of the 253 substantive Word-body paragraphs was found in normalized PDF text; this is textual evidence, not full bibliographic validation.

Third-preview layout **HOLD**: Table 1, Table 3, Table 4, and Table 5 now fit legibly on single pages; Figure 1 has only one caption, but image-internal labels remain too small at final-size viewing on page 9. **Table 2 still splits its final row from page 13 onto page 14** (including a repeated header); the body of page 14 starts with that single-row fragment. The title-page contact email, funding/conflict/ethics declarations, and data/code reviewer access still show unresolved author placeholders. The reference list fills pages 28–29; [19] is no longer stranded alone.

A controlled off-repository test using the *uploaded* Word file added paragraph spacing (0 before/after and 0.92× line height) and `w:cantSplit` only within Table 2. The test PDF stayed at 29 pages; all Table 2 rows remained together on page 13; Word paragraph text and all five tables' cell texts remained **exactly unchanged**. The OOXML equivalent of this bounded test is now applied to the **draft builder only** (no changes to R5 Markdown, frozen R4, Figure 1 source, scientific counts or P2X). A new author-host build and every-page regression check remain necessary. Figure legibility and publication declarations are still HOLD, irrespective of that pagination fix.
