# TAES 10-Page Track Official Requirements Audit

**Date checked:** 2026-09-06

**Official source:** https://ieee-aess.org/publications/transactions-aes/author-information

**Status:** `PASS_OFFICIAL_REQUIREMENTS_BOUND_TO_SHORT_TRACK`

The live IEEE AESS Information for Authors page was rechecked after the author supplied the official URL during the 10-page compression track.

## Requirements controlling this track

1. The manuscript type remains `Regular Paper`.
2. TAES states there is no formal manuscript-page limit, but unnecessarily long manuscripts may receive unfavorable reviews.
3. Publication of an accepted Regular Paper requires USD 200 for each printed page beyond 10.
4. The billable page count is taken from the final proof created by IEEE production.
5. The required two-column, single-spaced TAES submission version is the most accurate estimate of final page count.
6. The submission file must be PDF in the required 10-point, two-column geometry.
7. Supplementary material is allowed, including PDF documents, data, code, images, and multimedia.
8. TAES encourages submission of materials necessary to recreate results.
9. Supplementary material must be referenced in the main paper.
10. A README should describe the supplementary materials.
11. Supplementary material is technical content and must be available for peer review during article submission.
12. Open Access fees do not replace or waive overlength page charges.
13. AI-generated content must be disclosed in the Acknowledgments, identifying the AI system, affected content, and level of use.

## Engineering consequence

The short-track submission PDF should not merely target exactly 10 pages. Because IEEE production pagination controls the final overlength charge, the engineering target remains approximately 9.0-9.5 TAES-formatted pages when this can be achieved without scientific weakening.

The main article must remain a well-rounded treatment understandable without undue effort. Supplementary material may carry expanded finite maps, reproducibility detail, and secondary boundary conditions, but it may not be used to hide limitations needed to interpret the main claims.

## Frozen fallback

The R9 16-page package on `main` remains untouched as the audited fallback. This official-requirements audit authorizes no scientific change and no merge from the short track to `main`.
