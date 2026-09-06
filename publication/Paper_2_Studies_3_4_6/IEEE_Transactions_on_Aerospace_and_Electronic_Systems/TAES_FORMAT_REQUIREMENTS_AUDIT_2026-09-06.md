# TAES Paper 2 Formatting Requirements Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Manuscript type:** Regular Paper  
**Canonical Figure-1-integrated manuscript commit:** `cd78f9867e7811fd19c880736bf2ea5526c20d43`  
**Canonical assembled SHA-256:** `dde7d9c6ab4efb1c6f567937dd1c28c904baeb713dc960b716eae1b15ef5e709`  
**Scientific rerun authorized or required:** No

## 1. Live TAES submission-format requirements

The official TAES Information for Authors page was rechecked on 2026-09-06.

For a Regular Paper, the initial submission manuscript must be a PDF in the following format:

- two columns;
- single spaced;
- 10-point font;
- 1 in (25 mm) top margin;
- 1 in (25 mm) bottom margin;
- 0.7 in (18 mm) left margin;
- 0.7 in (18 mm) right margin;
- 3.45 in (88 mm) column width;
- 0.2 in (5 mm) spacing between columns.

TAES states that this version is required so the author can estimate possible overlength charges. Regular Papers have no formal manuscript page limit, but unnecessarily long papers can receive unfavorable reviews, and accepted Regular Papers incur a mandatory $200 charge for each printed page beyond 10 pages.

Official source:

- https://ieee-aess.org/publications/transactions-aes/author-information

## 2. IEEE authoring-tool controls

The IEEE Author Center currently provides Word and LaTeX article templates and recommends use of the publication-specific template selector. It also provides tools for LaTeX validation, reference validation, and PDF checking.

Official sources:

- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/

## 3. Formatting strategy for Paper 2

The controlled formatting path will use an IEEEtran-based LaTeX development source because:

1. TAES explicitly provides a LaTeX template for its required two-column version.
2. IEEE states that article templates are intended to help authors prepare a peer-review draft and estimate page count.
3. The existing Paper-2 manuscript is already source-controlled and contains equations, four exact-value tables, and one vector figure.
4. A deterministic LaTeX build permits reproducible page count, overfull-box detection, figure binding, and PDF hashing.

This is a formatting transformation only. The Markdown manuscript remains the authoritative scientific prose source until the LaTeX conversion is audited and frozen.

## 4. Scientific controls during typesetting

The formatting pass must not:

- rerun Studies 3, 4, or 6;
- alter any frozen numeric result;
- pool the three populations;
- convert logical time into operational spacecraft time;
- convert finite model counts into probabilities or rates;
- remove Study-4 null/equal-threshold rows;
- remove Study-6 residual-state identity;
- imply that Studies 3, 4, and 6 form one integrated experiment;
- imply that Study 4 or Study 6 model contact;
- introduce a global-best-policy or global-best-gate claim.

Tables I-IV remain main-paper displays. Figure 1 revision 2 remains the only figure and is qualitative synthesis only.

## 5. Build prerequisites to audit

Before generating a two-column candidate, the local canonical checkout should be checked for:

- `pandoc`;
- `pdflatex`;
- `latexmk`;
- `kpsewhich` with `IEEEtran.cls` resolvable;
- `pdfinfo` for page and page-size inspection;
- `pdffonts` for font embedding inspection;
- canonical manuscript and Figure 1 hashes matching the tracked values.

If the LaTeX toolchain is missing, do not silently substitute a different formatter. Record the missing prerequisite and select a controlled alternative only after review.

## 6. Formatting gate sequence

1. local environment/prerequisite audit;
2. deterministic generation of a TAES/IEEEtran `.tex` source;
3. LaTeX compilation to a development two-column PDF;
4. automated PDF audit for page size, page count, fonts, required text, and LaTeX overfull/underfull diagnostics;
5. render every PDF page to images and perform visual QA;
6. only then decide whether any page-driven table or prose adjustment is required;
7. freeze the publisher-facing manuscript PDF only after all format/visual controls pass.

## 7. Current gate verdict

`TAES_FORMAT_REQUIREMENTS=PASS__LOCAL_TOOLCHAIN_AUDIT_PENDING`

No publisher-facing PDF or portal submission is authorized by this requirements audit.
