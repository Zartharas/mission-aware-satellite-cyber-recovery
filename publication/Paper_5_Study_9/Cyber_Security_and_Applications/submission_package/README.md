# Paper 5 — CSA Submission Package

This is a **submission-package preparation workspace**, not authorization to submit.

Included:
- `CSA_MANUSCRIPT_SUBMISSION.tex`
- `references.bib`
- `CSA_MANUSCRIPT_SUBMISSION.bbl` (tracked build evidence; not planned for EM upload)
- `CSA_HIGHLIGHTS_SUBMISSION.txt`
- `COVER_LETTER_DRAFT.md`
- `DATA_CODE_AVAILABILITY.md`
- `DECLARATIONS_AND_DISCLOSURES.md`
- `SUBMISSION_FORM_RESPONSES.md`
- `JOURNAL_REQUIREMENTS_20260915.md`
- `EDITORIAL_MANAGER_LATEX_UPLOAD.md`
- `REFERENCE_AUDIT_20260915.md`
- `CSA_SUBMISSION_CHECKLIST.md`
- `SUBMISSION_PACKAGE_STATUS.json`

Generated PDF/ZIP build artifacts are emitted to Downloads and are intentionally not committed.

## Editorial Manager upload shape

The actual LaTeX archive uploaded to Editorial Manager must be flat, with no subfolders. The planned archive-root members are:

- `CSA_MANUSCRIPT_SUBMISSION.tex`
- `references.bib`

`CSA_HIGHLIGHTS_SUBMISSION.txt` should be uploaded separately as the journal's editable highlights file.

The tracked `.bbl` remains useful reproducibility/build evidence, but it is deliberately excluded from the planned Editorial Manager upload because it shares the primary manuscript base filename and EM warns against same-base filenames across extensions.

The locally compiled PDF is a validation artifact only. Editorial Manager will build its own reviewer PDF from the editable source.

Submission-package creation is authorized. Publisher submission is not.
