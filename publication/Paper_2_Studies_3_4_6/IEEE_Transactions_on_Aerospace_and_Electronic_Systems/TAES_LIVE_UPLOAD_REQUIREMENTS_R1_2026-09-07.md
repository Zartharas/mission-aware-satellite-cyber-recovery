# TAES Authenticated Upload Requirements R1

**Paper:** Paper 2, Studies 3, 4, and 6  
**Journal:** IEEE Transactions on Aerospace and Electronic Systems  
**Portal:** IEEE Atypon ReX / Research Exchange  
**Capture date:** 2026-09-07  
**Status:** `LIVE_UPLOAD_REQUIREMENTS_CAPTURED__R10_ADAPTATION_REQUIRED`

This record captures only requirements visible on the authenticated TAES Upload Manuscript screen. It supersedes pre-portal assumptions where the live workflow is more specific.

## 1. Workflow state

- Article Type step: complete.
- Upload Manuscript step: active.
- Later steps shown by the portal: Title, Abstract, Authors, Affiliations, Author Details, Match Organizations, Additional Information, Final Review.

## 2. Main Manuscript

The authenticated screen states:

- Main Manuscript: Required.
- Accepted manuscript source category shown by the portal: MS Word or LaTeX.
- Maximum: 1 Main Manuscript.
- The page text says the main manuscript may include embedded figures and tables but should not include supplementary materials.
- The page also states that LaTeX manuscript files may be bundled in a single archive including LaTeX, BibTeX, figures, tables, classes/packages, and other material belonging to the main manuscript.

### Consequence

The frozen R9 `TAES_MANUSCRIPT.pdf` remains the approved visual/scientific baseline, but the PDF-only pre-portal upload manifest is no longer sufficient for this authenticated workflow. A portal-compatible LaTeX package must be materialized and verified against the frozen baseline.

## 3. Conflict of Interest

The authenticated screen states:

- Conflict of Interest: Required.
- If any author has a conflict, a single conflict-of-interest document must be uploaded.
- The conflict-of-interest statement must also be disclosed within the manuscript.
- The screen provides a checkbox labeled `None of the authors have a conflict of interest to disclose`.

### Current control

The repository did not freeze a Paper-2 conflict-of-interest value before authenticated portal capture. The current truthful author declaration therefore remains required before the manuscript statement and portal checkbox can be finalized. Do not infer this value from another paper.

## 4. Optional file categories shown

The screen presents the following categories as optional:

- Main Document - Tracked Changes.
- Supplementary Material for Review.
- Previously Rejected Files.
- Image.
- Previously Published - Statement.
- Previously Published - Files.
- LaTeX Supplementary File.

Current Paper-2 controls remain:

- initial submission, so no tracked-changes manuscript;
- no separate supplementary material for initial review;
- no known previous rejection of this Paper-2 manuscript;
- no previous publication of this Paper-2 manuscript;
- Figure 1 belongs to the main manuscript package and is not a separate supplementary upload;
- Paper 1 / JAIS is a separate Studies-1-and-2 manuscript and must not be uploaded under any Paper-2 previously published or previously rejected category.

## 5. Cover Letter / Comments

The file category is visually marked `Optional`, but the accompanying authenticated instructions expressly state: `A cover letter is required.`

The instructions further state that if a paper was previously rejected from this or another journal, the cover letter must declare the journal, paper ID, rejection date, number of review rounds, and include a rebuttal to the last review round, with the previously rejected manuscript also uploaded. They also require disclosure and explanation if the manuscript is based on previously published work.

### Current Paper-2 application

Repository evidence supports that this Paper-2 manuscript:

- has not previously been rejected by TAES or another journal;
- has not been previously published;
- is not concurrently under review elsewhere;
- is distinct from Paper 1 / JAIS, which uses Studies 1 and 2 only.

Therefore a normal initial-submission cover letter is required, but no rejection rebuttal, previously rejected manuscript, previously published statement, or previously published file is currently applicable.

## 6. R10 adaptation boundary

The R10 adaptation is limited to:

1. portal-compatible LaTeX packaging of the frozen manuscript;
2. the live-required conflict-of-interest statement after author attestation;
3. a TAES cover letter;
4. regenerated format/hash/proof QA and updated upload manifest.

No scientific rerun, reanalysis, new study, new coauthor, supplementary package, or substantive manuscript rewrite is authorized by this portal adaptation.

**Verdict:** `PASS_LIVE_UPLOAD_CAPTURE__WAITING_AUTHOR_COI_ATTESTATION_AND_R10_MATERIALIZATION`
