# Cyber Security and Applications — Live Requirements Snapshot

Verified: 2026-09-15

Journal homepage:
https://www.keaipublishing.com/en/journals/cyber-security-and-applications

Journal guide:
https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/

Editorial Manager LaTeX guide:
https://www.ariessys.com/wp-content/uploads/EM_PM_LaTeX_Guide.pdf

## Journal and article fit

- Research Article is an accepted article type.
- The journal scope includes cyber attacks, software/hardware security, machine-learning mechanisms for cyber security, modern cyber-defense tools, emerging cyber-security methods, and cyber security in IoT/ICT contexts.
- The Paper 5 manuscript is positioned as a cyber-security semantic-interface and downstream recovery-decision identifiability study, not as a spacecraft flight-performance or mission-certification paper.
- Review model: single anonymized.
- Suitable submissions are typically sent to at least two independent reviewers.
- The live journal homepage currently reports CiteScore 17.8.
- Current APC shown in the live guide: USD 0 excluding taxes.

## Ethics and submission declaration

- Submission implies that the work has not been published previously except in permitted forms, is not under consideration elsewhere, is approved by all authors, and will not be republished in the same form without permission if accepted.
- KeAi submissions are automatically screened using iThenticate/CrossCheck; high-similarity manuscripts may be desk rejected.
- ORCID is encouraged at submission; the Paper 5 corresponding-author ORCID is already recorded.
- The corresponding author must remain the journal contact and keep contact details current throughout review/publication.
- Competing interests must be disclosed; the Elsevier declarations tool should always be completed and the generated Word file uploaded.
- For manuscripts submitted after 2026-01-01, authors are requested to consider potentially relevant employment, funding, or other relationships within three years of beginning the work.
- Funding disclosure is required. If no funding was provided, the guide recommends: "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
- Generative-AI use in manuscript preparation must be declared when applicable in a separate section before the references; the author remains responsible for verification, editing, originality, and the final content.

## Writing and manuscript structure

- LaTeX is recommended; editable source is required and PDF alone is not an acceptable source.
- Title page requires article title, author name(s), affiliation(s), corresponding-author details, email, and the full postal address of each affiliation including country.
- Abstract maximum: 350 words.
- Keywords: 3-6 in English.
- Highlights: encouraged; 3-5 bullets; <=85 characters each; separate editable file with "highlights" in the file name.
- Graphical abstract: encouraged, not mandatory.
- Main manuscript sections should be clearly defined and numbered; the abstract is not part of the section numbering.
- Tables must remain editable, be cited in text, numbered in appearance order, and include captions; vertical rules and shading should be avoided.
- Figures/artwork, if used, have separate file, resolution, caption, and permissions requirements. The current Paper 5 manuscript does not rely on external figure files.
- SI units are required where physical units are used.

## References

- Every reference cited in text must appear in the reference list and vice versa.
- References are indicated by numbers in square brackets and numbered in order of appearance.
- DOI inclusion is recommended where available.
- Journal names should follow LTWA abbreviations in final typeset reference formatting.
- Underlying/relevant datasets are encouraged to be cited as data references when a suitable repository/version/persistent identifier exists.
- The current Paper 5 package uses `elsarticle-num`, has an exact citation/BibTeX key match, and has an external source-existence audit PASS for all 11 bibliography entries.

## Research data

- CSA applies Elsevier Research Data Option A guidance.
- Authors are encouraged to deposit relevant research data/materials in an appropriate repository and cite deposited datasets where applicable.
- A data-availability statement is encouraged at submission and may explain why data cannot be redistributed.
- Research data under the policy can include software, code, models, algorithms, protocols, and methods in addition to observational/experimental data.
- The Paper 5 package provides a public repository containing the protocol, schema, mapping records, code, tests, derived outputs, independent audit outputs, and cryptographic identities.
- Third-party raw dataset bytes are not redistributed by this project; the manuscript records provenance and cites the source publications. No dataset citation metadata will be invented where a verified persistent dataset identifier is not available.

## Submission checklist from the live guide

Before completing submission:

- designate one corresponding author and provide/maintain full contact details;
- upload all applicable files, including any artwork, supplementary material, captions, tables, and footnotes;
- complete spelling and grammar checks;
- ensure every in-text reference is present in the reference list and vice versa;
- obtain permission for any copyrighted third-party material used;
- verify all required editable source files are present;
- understand the open-access/APC terms shown by the submission system.

## Editorial Manager LaTeX constraints incorporated into this package

- EM documents TeX Live 2024 and supports LaTeX/pdfLaTeX/pdfTeX/TeX/XeLaTeX.
- Compressed LaTeX submissions must contain all LaTeX source files at one folder level; subfolders are not supported.
- Recommended source order is primary `.tex`, bibliography files, optional style files, nomenclature files, then figures.
- `.tex`, `.bib`, and `.bbl` are LaTeX manuscript-source item types, not Supplemental items.
- EM uses BibTeX/BibTeX8 by default.
- EM warns against uploading multiple files with the same base filename even when their extensions differ.
- The final EM upload archive for Paper 5 will therefore contain `CSA_MANUSCRIPT_SUBMISSION.tex` and `references.bib` at the archive root; the tracked `.bbl` is retained as build evidence but is not planned for portal upload.
- `elsarticle.cls` is listed as installed in EM's Elsevier TeX environment, so no custom copy is bundled unless the journal portal specifically requests one.
- Portal manuscript metadata must exactly match the TeX manuscript for article type, title, author details, abstract, keywords, funding, and other requested fields.
- Editorial Manager generates the reviewer PDF; the locally compiled PDF is for pre-submission validation, not a substitute for editable source.

See `EDITORIAL_MANAGER_LATEX_UPLOAD.md` for the upload plan.

## Pending before submission-ready lock

1. Author-supplied full postal affiliation address.
2. Elsevier declarations-tool `.doc`/`.docx`.
3. Final author reconfirmation of originality/non-concurrent consideration and approval of submitted version.
4. Final spelling/grammar and similarity-risk review before portal completion.
5. Portal-only fields visible only after starting Editorial Manager.
6. Final portal metadata-to-TeX equality check.
7. Author inspection and approval of the PDF generated by Editorial Manager.
