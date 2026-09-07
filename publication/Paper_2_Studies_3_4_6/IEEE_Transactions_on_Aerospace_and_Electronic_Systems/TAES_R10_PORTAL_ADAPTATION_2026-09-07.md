# TAES R10 Live-Portal Adaptation Record - 2026-09-07

**Paper:** Paper 2, Studies 3, 4, and 6  
**Journal:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Platform:** IEEE Author Portal / Research Exchange (Atypon ReX)  
**Author:** Aman Kumar Singh, sole author and corresponding author  
**Status:** `AUTHORIZED_PORTAL_ONLY_ADAPTATION__SCIENCE_FROZEN`

## Author authorization

On 2026-09-07, the author explicitly authorized the narrow R10 adaptation required by the authenticated TAES upload screen. This authorization does not reopen any frozen experiment, statistical result, scientific claim, title, abstract, bibliography, figure, table, study population, or cross-study interpretation.

The author also explicitly confirmed on 2026-09-07:

> I have no conflict of interest to disclose for this manuscript.

The resulting manuscript declaration is therefore:

> The author declares no conflict of interest.

## Live portal requirements newly resolved

The authenticated Upload Manuscript screen establishes the following requirements or workflow facts that were not fully resolvable from the public pre-portal instructions:

1. Main Manuscript is required and the accepted main-document route presented by the portal is MS Word or LaTeX; for LaTeX, manuscript files may be bundled as a single archive.
2. The Conflict of Interest area requires disclosure in the manuscript. Because the sole author has confirmed no conflict of interest, the portal's no-conflict checkbox is the applicable route and no separate conflict document is expected.
3. The Cover letter / Comments area contains explicit prose stating that a cover letter is required, even though the left-side field badge is labelled optional. The conservative submission decision is to provide a cover letter.
4. Main Document - Tracked Changes is not applicable to this initial submission.
5. Supplementary Material for Review remains omitted under the previously frozen no-separate-supplementary-material decision.
6. Previously Rejected Files is not applicable because this Paper-2 manuscript has no recorded prior rejection.
7. Image upload is not required because Figure 1 is bound inside the manuscript/source package.
8. Previously Published - Statement and Previously Published - Files are not applicable because this manuscript has not previously been published.
9. LaTeX Supplementary File is not applicable because no separate supplementary LaTeX material is being submitted.

## R10 adaptation boundary

R10 is a submission-interface adaptation only. The canonical R9 manuscript content remains the scientific baseline. The generated R10 LaTeX source is required to differ from the approved R9 generated LaTeX by exactly one inserted unnumbered section immediately before the existing Acknowledgment:

```latex
\section*{Conflict of Interest}
The author declares no conflict of interest.
```

No other generated-LaTeX difference is authorized.

## Sole-author control

The manuscript and all submission metadata remain single-author:

- Aman Kumar Singh - sole author;
- Independent Researcher;
- corresponding author: yes;
- no coauthors may be added or implied.

## Package rule

The R10 portal package must be built from the unchanged frozen canonical Markdown manuscript using the already approved R9 IEEEtran transformation, followed only by the exact conflict-of-interest insertion above. The LaTeX upload archive must contain the generated main `.tex` file and the already approved Figure 1 PDF needed to compile it. Standard IEEEtran/LaTeX packages are system dependencies rather than research artifacts.

A build/audit must verify that removing the R10 conflict-of-interest block from the R10 generated LaTeX yields byte-for-byte the R9 generated LaTeX. This is the principal no-science-change control for the portal adaptation.

## Submission gate

This authorization permits generation and QA of the R10 upload files. The final Research Exchange Submit action remains gated on review of the portal-generated proof/final-review screen against the frozen submission values and sole-author metadata.
