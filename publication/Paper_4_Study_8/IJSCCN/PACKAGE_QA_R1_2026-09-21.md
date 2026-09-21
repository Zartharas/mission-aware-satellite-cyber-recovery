# IJSCCN Package QA R1 — 2026-09-21

**Package:** Rebuilt Paper 4 / Study 8 + Study 8E  
**Target journal:** International Journal of Satellite Communications and Networking (Wiley)  
**Status:** `CORE_PACKAGE_QA_PASS__AUTHOR_PHOTO_PENDING__PUBLISHER_SUBMISSION_NOT_AUTHORIZED`

## 1. Authoritative journal guidance

Primary journal instructions:

https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html

Verified for this package on 2026-09-21.

The derivative package implements the currently relevant initial-submission requirements, including:

- satellite component central to the manuscript;
- abstract <=250 words;
- no more than 8 keywords;
- short title <=70 characters;
- corresponding-author and ORCID metadata;
- Data Availability Statement;
- author biography;
- Graphical Table of Contents material;
- editable manuscript source;
- separate figure files;
- Wiley-aligned AI-use disclosure.

Free-format initial submission is used where permitted; no unnecessary publisher-layout conversion is imposed before editorial review.

## 2. IJSCCN derivative manuscript

Source:

`publication/Paper_4_Study_8/IJSCCN/MANUSCRIPT_IJSCCN.md`

Current IJSCCN abstract:

- 213 words;
- self-contained;
- no literature citations;
- within the 250-word limit.

Keywords:

- 8;
- within the journal limit.

Short title:

**Post-Quantum Satellite Recovery Under Intermittent Connectivity**

- 63 characters;
- within the 70-character limit.

## 3. Frozen scientific fidelity

No scientific reanalysis was performed.

The IJSCCN derivative preserves:

### Study 8

- experiment `S8-PQC-ICR-001`;
- 3,456 deterministic positions;
- each policy 635/864 = 73.4954%;
- P3-P1 = 0.000000 percentage points;
- profile success 93.7500%, 64.9306%, 61.8056%;
- no logical-slot-to-physical-time conversion.

### Study 8E

- experiment `S8E-ECTV-001`;
- corrected freeze `S8E-CANON-RESULTS-002-FREEZE-001`;
- 20 traces;
- 476 source rows;
- 454 eligible anchors;
- 65,376 cases;
- 17,640 finite / 47,736 non-finite;
- modeled threshold min/median/max 48 / 345 / 57,727 bit/s;
- all 4,410 both-finite P3/P1 comparisons = 0 bit/s;
- 21,792/21,792 preserved profile-burden ordering.

The Study 8 and Study 8E populations remain separate and unpooled.

## 4. Generated submission files

The reproducible package builder generates:

- `MANUSCRIPT_IJSCCN.docx`;
- `TITLE_PAGE_IJSCCN.docx`;
- `COVER_LETTER_IJSCCN.docx`;
- `AUTHOR_BIOGRAPHY.docx`;
- `AI_USE_DECLARATION.docx`;
- Figure 1 state-machine TIFF/PNG;
- Figure 2 Study 8 profile-result TIFF/PNG;
- Figure 3 Study 8E horizon-result TIFF/PNG;
- IJSCCN GTOC TIFF/PNG/SVG;
- build manifest;
- ZIP submission bundle.

Builder:

`publication/Paper_4_Study_8/IJSCCN/build_ijsccn_package.py`

Workflow:

`.github/workflows/paper4_ijsccn_package.yml`

## 5. Visual QA

The candidate manuscript DOCX was rendered with the repository DOCX QA workflow and inspected visually.

Result:

- 25 rendered pages;
- no clipping;
- no overlapping body text;
- no broken headings;
- no missing glyphs in the final inspected build;
- figure captions remain attached to readable figures;
- reference pages fit inside page boundaries.

Presentation defects found during intermediate QA were corrected before this final gate:

1. duplicated manuscript metadata page removed;
2. heading color normalized to black;
3. Figure 1 state-machine layout enlarged and made readable;
4. BibTeX LaTeX accent escapes converted to rendered Unicode;
5. IEEE 3536 entry normalized from unsupported `@standard` to a compatible source entry;
6. journal issue-number duplication removed from formatted references;
7. NIST corporate author rendering normalized;
8. GTOC center content simplified to remove overlap.

## 6. Figure QA

Separate TIFF files were verified at 600 dpi:

- Figure 1: 5460 × 3060 px, 600 dpi;
- Figure 2: 4014 × 2458 px, 600 dpi;
- Figure 3: 4015 × 2455 px, 600 dpi;
- GTOC: 5940 × 2820 px, 600 dpi.

All four were visually inspected.

No figure introduces a new scientific endpoint.

## 7. Reference QA

The submission DOCX uses numbered in-text citations and a numbered reference list.

The final candidate reference pages were visually inspected for:

- escaped LaTeX characters;
- malformed corporate authors;
- duplicated issue/standard numbers;
- missing IEEE standard metadata;
- page overflow.

Final inspected candidate: PASS.

## 8. AI-use disclosure

The package contains a Wiley-aligned AI Use Declaration identifying:

- OpenAI ChatGPT / GPT-5.6 Sol;
- drafting, structural editing, literature-navigation support, package review, and presentation-layer figure preparation;
- independent author verification;
- no AI generation or alteration of frozen Study 8/Study 8E scientific data, canonical results, hashes, or endpoints.

Publisher submission remains subject to the live Wiley portal disclosure fields presented at submission time.

## 9. External author-supplied items still pending

The repository cannot legitimately create these on the author's behalf:

1. **recent author photograph** requested by IJSCCN;
2. **corresponding-author telephone number**, only if the Wiley portal requires it.

The package intentionally does not invent either item.

## 10. Publisher-submission boundary

Package preparation is authorized.

Publisher submission is **not authorized**.

This QA record does not authorize:

- upload to Wiley Research Exchange;
- completion of portal metadata;
- final review/submit action;
- any scientific rerun.

## 11. Decision

`IJSCCN_CORE_PACKAGE_QA_PASS__FINAL_EXACT_HEAD_BUILD_REQUIRED`

The branch must now complete one final exact-head package workflow run after this QA record. If that run succeeds, the resulting artifact is eligible for package-review/freeze handoff.

The author photograph remains a separate external upload requirement.
