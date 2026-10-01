# Editorial Manager LaTeX Upload Plan

Verified: 2026-09-15

Primary platform guide reviewed:
https://www.ariessys.com/wp-content/uploads/EM_PM_LaTeX_Guide.pdf

Guide revision: March 2025.

## Upload archive policy

The LaTeX archive intended for Editorial Manager must be flat. Do not place the manuscript or bibliography inside subfolders in the upload ZIP.

Planned LaTeX source upload members:

1. `CSA_MANUSCRIPT_SUBMISSION.tex`
2. `references.bib`

The highlights file should be uploaded separately as the journal's editable highlights item:

- `CSA_HIGHLIGHTS_SUBMISSION.txt`

The repository retains `CSA_MANUSCRIPT_SUBMISSION.bbl` as deterministic build evidence, but it is not planned for the Editorial Manager LaTeX upload. Editorial Manager uses BibTeX/BibTeX8 by default, the manuscript already references `references.bib`, and the platform guide warns against uploading multiple files with the same base filename even when extensions differ. This avoids pairing `CSA_MANUSCRIPT_SUBMISSION.tex` with `CSA_MANUSCRIPT_SUBMISSION.bbl` in the portal upload.

## Platform compatibility

- Editorial Manager currently documents TeX Live 2024 for its PDF builder.
- pdfLaTeX is supported and is the default PDF-oriented engine.
- `elsarticle.cls` is listed among the Elsevier class files installed in the Editorial Manager TeX environment.
- No custom class or custom macro package is used by the Paper 5 submission manuscript.
- No shell-escape-dependent package, Python code, external program, TikZ externalization, or pgfplots externalization is used.
- The manuscript uses a separate BibTeX database, which Editorial Manager supports.

## Portal file handling

- Upload the primary `.tex` as a Manuscript item.
- Upload bibliography source as a Manuscript/LaTeX supporting item, following the item names exposed by the journal portal.
- Do not classify LaTeX source files as Supplemental items.
- Keep any compressed LaTeX source archive flat with no directory hierarchy.
- Do not upload the locally generated manuscript PDF as a replacement for the editable LaTeX source; Editorial Manager builds its own reviewer PDF.
- After Editorial Manager builds the PDF, inspect and approve the generated PDF before completing submission.

## Metadata consistency gate

Before publisher submission, confirm that the following portal fields exactly match the TeX manuscript and final package record:

- article type;
- title;
- author name and spelling;
- author order;
- abstract;
- keywords;
- funding information;
- corresponding-author details.

## Artifact status

The original r2 editable-source ZIP was a local draft artifact and used an internal `source/` folder. It is **not** the archive to upload to Editorial Manager. The final private submission package will regenerate a flat EM-ready archive after the author-supplied postal affiliation is injected.

## Authorization boundary

This upload plan prepares files for Editorial Manager only. It does not authorize publisher submission.
