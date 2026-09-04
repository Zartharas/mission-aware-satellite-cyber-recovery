# Final JAIS Manuscript — Content Ready

**Gate:** `JAIS_MANUSCRIPT_CONTENT_READY__SCHOLARONE_FIELD_LOCK_PENDING`

The JAIS publisher-facing manuscript has completed the content/export, reference, repository-validation, and visual-layout gates. This status does **not** authorize or record a publisher submission.

## Frozen manuscript identity

- Generation commit: `506c3d26d812709efec86c856514d541343c0b57`
- GitHub Actions workflow: `JAIS Export Audit`
- Workflow run: `33907150553`
- Workflow artifact: `jais-paper1-export-506c3d26d812709efec86c856514d541343c0b57`
- Artifact ID: `9949926197`
- Artifact ZIP SHA-256: `8f8171f4f2619595631829b5c17c58a8e88cacbe9604e05413562181d53a213f`
- Publisher manuscript filename: `JAIS_MANUSCRIPT.docx`
- Publisher manuscript SHA-256: `30910535075c3c8d13f501d721e46dd8537774c2d366ca858cdd71222d9edf64`
- Generated manuscript Markdown SHA-256: `3d0fdf4b14a5485396b98fed2e0e44ea5fe763213502be65f3b9fe678a12193c`

## Export and reference gates

- Title: 12 / 12 words — PASS.
- Abstract: 171 words, one paragraph, third person, no citation markers — PASS.
- Text words excluding table-cell text: 7,058.
- AIAA table-equivalent words: 1,250.
- Estimated AIAA equivalent words: 8,308 / 12,000 — PASS.
- Numbered references: 20.
- Missing citation keys: none.
- AIAA reference archivality/completeness gate: PASS.
- DOI URLs rendered where available: PASS.
- Dynamic web-only references excluded from the numbered list: PASS.

## Frozen-science gates

- Study 1 remains exactly 720 VALID observations across 24 frozen cells — PASS.
- Study 2 remains exactly 3,872 VALID observations across 85 frozen cells with zero INVALID attempts — PASS.
- Study 1 and Study 2 remain separate and are not pooled — PASS.
- Study-1 P1 null boundary preserved — PASS.
- Study-2 Block-C structural label-invariance boundary preserved — PASS.
- K4 intermittent/flapping-contact boundary preserved — PASS.
- A2/K2 coupled producer-compromise/contact-loss boundary preserved — PASS.
- Logical software-time boundary preserved — PASS.
- No weighted global policy rank — PASS.
- Study 8 excluded — PASS.

## Word-manuscript visual QA

The exact CI-generated `JAIS_MANUSCRIPT.docx` was rendered and inspected across all 25 pages.

- 10-point Times New Roman body, double-spaced, single column — PASS.
- Title/front matter presentation — PASS.
- Black headings with no theme-color residue — PASS.
- Markdown-only backticks absent from Word output — PASS.
- Tables remain editable — PASS.
- Repeating table headers on continuation pages — PASS.
- Compact JAIS-facing Tables 3–5 remain derived from the frozen source CSVs — PASS.
- No clipping, overlap, broken rows, or unreadable table-column artifacts — PASS.
- Reference wrapping/pagination — PASS.

## Repository validation

The repository validation workflow at the generation commit completed successfully, including repository release-gate audit, bibliography metadata integrity, JSON/schema validation, Python compilation/tests, shell syntax validation, frozen WP10 reproduction, reconstruction regression tests, and no tracked-file drift.

## Remaining gate before package freeze

Only the authenticated JAIS ScholarOne schema remains to be locked. The author must enter the production ScholarOne workflow without completing submission and capture the exact fields presented for article type, classifications/keywords, author/affiliation metadata, reviewers, declarations, data/code, artificial-intelligence disclosure, ethics/rights, and file designations.

After those fields are reconciled, the exact upload package can be frozen. Actual publisher submission still requires a separate explicit author authorization.
