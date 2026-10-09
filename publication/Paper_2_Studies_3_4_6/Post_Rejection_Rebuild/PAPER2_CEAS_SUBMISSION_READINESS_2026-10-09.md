# Paper 2 — CEAS Space Journal preparation and fail-closed submission checklist

This package is a **CEAS-specific R5 editorial derivative**, not a previously submitted version and not a completed portal submission. The sole author previously submitted an older TAES R10 version, which received editorial prescreen rejection on 2026-09-26 without external peer review. The immutable R4 source and its frozen Studies 3/4/6 and separately governed S3X/S6X evidence are not modified.

## Journal-specific requirements (official source)

Journal: [CEAS Space Journal](https://link.springer.com/journal/12567). Author instructions: https://link.springer.com/journal/12567/submission-guidelines (accessed 2026-10-09). Article class: **Original Research Article**; the journal's review-article class is invitation-only and is inappropriate here. The journal uses **single-blind** peer review. The journal is **hybrid**, and choosing open access is separate from scientific or submission acceptance.

Verified format: **150–250 abstract words**, **4–6 keywords**, editable Word (.docx) or LaTeX with source files; a PDF accompanies Word. Decimal headings with at most three levels; numbered references [n], numbered Arabic tables, numbered Fig. captions and artwork in the text. Original research requires a **Data Availability Statement**; author contributions and competing-interest information must also be supplied through the submission interface. The journal specifically requires disclosure of substantive LLM-assisted drafting; limited copy editing is treated differently. The R4 disclosure already identifies substantive AI editorial participation and was preserved/adapted. Do not claim the AI use was only copy editing.

## Prepared files

- `PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md`: complete venue-specific R5 editorial source derived from the R4 body; includes reformatted headings, table/figure numbering, 215-word abstract, six keywords, AI disclosure and declarations requiring author confirmation.
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
