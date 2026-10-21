# Paper 2 Rebuild R2 - Figure 1 Visual and Scientific QA

**QA date:** 2026-09-28  
**Authoritative manuscript:** `PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md`  
**R2 manuscript blob:** `9e3f345a3a16102c39bb978f4e522c261e80cfb4`  
**Authoritative base commit:** `ccef12d6f0c09fe48d795735726c964d8daad561`  
**Scientific rerun:** none  
**Current verdict:** `PASS_REVISION_3_FIGURE_SOURCE_AND_VISUAL_QA__MANUSCRIPT_INSERTION_NOT_YET_AUTHORIZED`

## 1. Scope

This phase creates and visually/scientifically validates the R2 residual-trust-boundary figure specified by the authoritative R2 display plan. It does not modify the authoritative R2 manuscript, rerun any experiment, alter any result, pool Study 3 with S3X, or lock a venue.

The canonical tracked figure source is SVG. The generator produces a 7.16-in vector PDF and a 2148 x 1740 PNG preview for placement and visual QA. The SVG is the canonical byte-bound source; the PNG is byte-reproducible in repeated checks. The PDF is a controlled visual render, but its byte stream is not treated as canonical across separate Cairo processes.

## 2. Revision history

### Revision 1 - rejected

The first R2 render preserved the three-panel architecture and S3X inset, but the S3X footer extended below the Study-3 panel and collided with the global footer.

Verdict:

`REVISION_1_REJECTED__S3X_INSET_FOOTER_OVERFLOW`

No scientific content changed.

### Revision 2 - rejected

The second render corrected the footer collision but placed the top of the S3X inset over the final lines of the Study-3 "Effect of stronger composition" text.

Verdict:

`REVISION_2_REJECTED__STUDY3_TEXT_INSET_OVERLAP`

No scientific content changed.

### Revision 3 - pass

Revision 3 moved and compacted the S3X inset while preserving all mandatory labels. Both the native PNG and an independent 200-dpi render of the generated PDF were inspected. PDF preflight then detected that the initial CairoSVG export constants produced a 5.37-in page; the export contract was corrected from point-valued output dimensions to the CSS-pixel dimensions CairoSVG expects, producing the intended 7.16 x 5.80-in page without changing the SVG layout.

Verdict:

`PASS_REVISION_3_FIGURE_SOURCE_AND_VISUAL_QA`

## 3. Revision-3 generation record

Tracked SVG source:

- dimensions: 1432 x 1160 SVG units;
- SHA-256: `adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc`.

QA PDF render:

- preflight page size: 516 x 418 pt (7.16 x 5.80 in, rounded);
- CairoSVG output dimensions: 687.36 x 556.80 CSS px;
- `SOURCE_DATE_EPOCH=1790553600`;
- inspected QA-render SHA-256: `30fe410d4f432333463140ece3070f74351b26d626bbcefc1900df631fd89c2c`.

PNG visual-QA preview:

- 2148 x 1740 pixels;
- SHA-256: `fe554420795c6bf460c6010555a18e928ba09d90adbffde74f2e01e1713d8f5c`.

The PNG render is byte-reproducible in repeated checks. `SOURCE_DATE_EPOCH` is fixed to reduce PDF metadata variability, but separate Cairo processes can still produce visually identical PDFs with different byte hashes. Therefore the PDF SHA-256 above identifies the inspected QA render only; it is not a canonical cross-process byte identity. The tracked SVG SHA-256 is the canonical figure-source binding.

## 4. Visual QA

Revision 3, after the PDF export-scale correction, passes the following checks:

- PDF preflight confirms the intended 7.16 x 5.80-in two-column page size;\n- no text clipping at the page edge;
- no text crosses a panel boundary;
- no S3X inset text overlaps Study-3 text;
- no inset footer collides with the global footer;
- no arrows, connectors, or serial-pipeline cues appear;
- three main panels remain visually parallel;
- S3X is visually subordinate to Study 3 rather than presented as a fourth peer experiment;
- grayscale readability is intrinsic because the figure uses black text/borders, white space, and light-gray headers;
- `APPROVED_BAD_SOURCE` remains explicit in Study 6;
- provenance conditionality and null threshold effects remain explicit in Study 4;
- persistent V5 and the K4 limitation remain explicit in Study 3;
- top-level anti-pooling and no-data-flow labels remain visible at two-column width.

## 5. S3X scientific controls

The inset visibly states:

- 1,919 P99_X10 timestamp intervals;
- empirical hiatus versus matched q=0 refresh;
- +1 cadence-unit B0 cache contrast in 5,757 comparisons;
- V4 affected record non-qualification;
- V5 first-refresh B0/S1 qualification and B2 non-qualification;
- timing changes q, not classification.

The inset also visibly preserves:

- `K4 = synthetic contact modeling`;
- `S3X = timing proxy, not observed RF/contact loss`;
- `Not external empirical replication of Study 3`.

The figure therefore does not relabel ESA timestamp intervals as observed RF contact loss, ground-station visibility loss, command-path outage, spacecraft outage, cyberattack truth, or operational recovery latency.

## 6. Cross-study scientific controls

The figure presents three separately evaluated experiments and a qualitative synthesis only.

It does not imply:

- a pooled population;
- a common experimental unit;
- experimental data flow from Study 3 to Study 4 to Study 6;
- a serial recovery architecture;
- that Study 4 or Study 6 model contact;
- that stronger composition is globally superior;
- that B2 is a globally preferred recovery policy.

## 7. Manuscript state

The authoritative R2 manuscript remains unchanged during this phase.

Figure 1 insertion into R2, caption integration, table/figure numbering reconciliation, and the final manuscript-plus-figure pre-venue audit remain closed pending a subsequent author gate.

## 8. Next gate

`AUTHOR_REVIEW_AFTER_R2_FIGURE1_PR_AND_PREMERGE_CI_BEFORE_MERGE`
