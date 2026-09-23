# Paper 4 IJSCCN R5 Visual and Publisher QA

**QA date:** 2026-09-22  
**Branch:** `paper4/ijsccn-r5-policy-design-20260921`  
**Exact artifact source head:** `a78a9206c4fd1e3134aec286b1e715185fd44791`  
**Artifact:** GitHub Actions artifact `10699407513`, `paper4-ijsccn-r5-public-safe-qa`  
**Artifact digest:** `sha256:e0e7871420f4e8f34a831502db869b02aaeb50e24793a6a287a3f7e5586d0a3e`  
**Scientific effect:** None. No scientific execution, reanalysis, endpoint change, population change, or claim expansion was performed.

## 1. Scope

This QA evaluates the public-safe R5 publisher-facing package after reconciliation against the final Wiley/IJSCCN evidence matrix.

The QA covers:

- manuscript DOCX rendering and page-by-page inspection;
- auxiliary DOCX rendering;
- scientific figure and GTOC inspection;
- Word structural integrity;
- table semantics and accessibility;
- privacy-safe placeholder behavior;
- zero-em-dash requirement;
- package/build integrity.

The public-safe build intentionally uses placeholder author metadata and excludes the local author photograph.

## 2. Manuscript page-by-page render review

The exact R5 manuscript rendered to **18 pages**.

All 18 pages were inspected individually at normal reading scale.

### Pages 1-3

- title hierarchy is compact and scholarly;
- author/contact placeholders are clearly separated from article content;
- abstract fits cleanly with no clipping;
- keywords and Introduction transition are readable;
- no oversized blank title-page region;
- Introduction and transition into Methods maintain consistent page rhythm.

**Status:** PASS.

### Pages 4-7

- Methods hierarchy is clear and restrained;
- long frozen identifiers wrap without clipping or margin overflow;
- Study 8 and Study 8E remain visually and conceptually separated;
- strict-before-horizon bound is readable in prose;
- Methods AI disclosure is contained in the intended methods section;
- no orphan headings or malformed glyphs.

**Status:** PASS.

### Pages 8-10

- Study 8 and Study 8E Results are clearly separated;
- numerical density remains readable;
- cross-study synthesis is not visually presented as pooled analysis;
- Discussion begins cleanly without a poor page break.

**Status:** PASS.

### Pages 11-13

- Discussion section hierarchy is consistent;
- limitation language remains readable despite high technical density;
- Data, Code, and Reproducibility section displays hashes without overflow;
- Conclusions remain compact and evidence bounded.

**Status:** PASS.

### Pages 14-16

- Funding, Conflict of Interest, Author Contributions, Ethics, and DAS render cleanly;
- References use consistent numbered presentation and hanging indentation;
- De Zuane et al. appears as the peer-reviewed IEEE LANMAN 2026 record;
- Figure Legends are grouped after References;
- no malformed URLs or reference clipping was observed.

**Status:** PASS.

### Page 17

- Table 1 appears on a separate page after References;
- header row is visually distinct;
- all cells fit inside page margins;
- the logical-time note is clear and separated from the table.

**Status:** PASS.

### Page 18

- Table 2 appears on a separate page;
- all corrected Study 8E anchors fit without clipping;
- the modeled-rate interpretation note is visible and complete.

**Status:** PASS.

## 3. Auxiliary-document render review

The exact-head public-safe auxiliary documents were rendered and inspected.

| File | Pages | Visual result |
| --- | ---: | --- |
| `COVER_LETTER_IJSCCN_R5.docx` | 1 | PASS |
| `TITLE_PAGE_IJSCCN_R5.docx` | 1 | PASS after compacting duplicate declarations |
| `AUTHOR_BIOGRAPHY_R5.docx` | 1 | PASS |
| `AI_USE_DECLARATION_R5.docx` | 1 | PASS after compacting the prior sparse second page |
| `GTOC_IJSCCN_R5.docx` | 1 | PASS |

The earlier two-page title-page spill and one-line second page in the AI declaration were corrected before this record.

## 4. GTOC QA

The final public-safe GTOC entry contains:

- manuscript title;
- author placeholder with corresponding-author asterisk;
- a purpose-built abstract figure;
- a summary within the journal's 80-word / 3-sentence limit.

The abstract figure itself no longer duplicates the title and author. It communicates:

- the common frozen recovery mechanism;
- Study 8 fixed-capacity analysis;
- Study 8E public observation-opportunity timing analysis;
- separate evidence populations and no pooling;
- no Study 8 slot-to-seconds conversion;
- the P3 versus P1 negative feasibility result;
- the bounded role of transition-object burden, timing, and horizon;
- the SatNOGS timing-proxy restriction.

**Status:** PASS.

## 5. Scientific-figure QA

### Figure 1

The state-machine schematic is publication-clean, monochrome, high contrast, and readable. The flow direction is unambiguous and the figure makes no operational-protocol claim.

**Status:** PASS.

### Figure 2

The Study 8 profile-success bar chart uses restrained grayscale styling, clean axes, direct numeric labels, and no decorative plot title. Values remain exactly:

- 93.7500%;
- 64.9306%;
- 61.8056%.

**Status:** PASS.

### Figure 3

The Study 8E horizon finite-fraction chart uses the same restrained style and retains exactly:

- 5.2863%;
- 20.5947%;
- 55.0661%.

The x-axis explicitly identifies elapsed-time horizon.

**Status:** PASS.

### Artwork resolution

The R5 workflow enforces the 800 dpi target for the three scientific TIFF figures and the GTOC TIFF.

No raster upsampling was used to claim resolution. The figures are regenerated from source.

**Status:** PASS.

## 6. Word structural and accessibility QA

The exact-head manuscript DOCX was inspected structurally.

- comments part: absent;
- tracked insertions: 0;
- tracked deletions: 0;
- hidden text markers: 0;
- em-dash characters: 0;
- repeating/header table rows: 2, one for each table;
- accessibility audit: 0 high, 0 medium, 0 low findings.

All publisher-facing public-safe DOCX files inspected contain zero comments, tracked revisions, hidden text, and em dashes.

**Status:** PASS.

## 7. Privacy and metadata boundary

The public-safe package contains only placeholder author metadata:

- `AUTHOR_LOCAL_ONLY`;
- `LOCATION_LOCAL_ONLY`;
- `EMAIL_LOCAL_ONLY`;
- `ORCID_LOCAL_ONLY`.

The build manifest records:

- `private_submission_overlay_used = false`;
- `author_photo_included = false`;
- `output_scope = PUBLIC_SAFE_QA`;
- `publisher_submission_authorized = false`.

Private author metadata and the author photograph remain outside the public-safe artifact and must remain under ignored local-only paths.

**Status:** PASS.

## 8. Visual defects found and corrected during R5 QA

The following defects were identified during exact-artifact inspection and corrected:

1. table first rows were not marked as Word table headers;
2. the original R5 bar figures retained default plotting aesthetics;
3. the first R5 GTOC design was visually plain;
4. the combined GTOC DOCX duplicated title and author inside the embedded graphic;
5. the separate title page spilled onto a sparse second page;
6. the standalone AI declaration produced a nearly empty second page.

All six issues were corrected and re-rendered.

## 9. Acta visual-benchmark gate

The immutable historical benchmark is:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_ASTRONAUTICA_MANUSCRIPT.docx`

The exact submitted Acta manuscript was retrieved through a temporary short-lived CI QA artifact without modifying the binary. Its local SHA-256 was verified as:

`ef551a52c2df65c1db68fa6188b22bf216e10aefdc6b7e8d0de00e3fb95d7411`

This matches the frozen submitted-package authority.

The Acta manuscript rendered to **8 pages**, and every page was inspected directly. The comparison was used only as a visual-quality benchmark. IJSCCN requirements continue to control where the two venues differ.

### Direct comparison

- **Title-page restraint:** R5 uses a smaller, more conventional journal title hierarchy and avoids the oversized title treatment visible in the Acta manuscript. PASS.
- **Section hierarchy:** Acta is compact but dense. R5 uses fewer visible heading levels than the rejected R4.x source while preserving clearer section transitions and more consistent reviewer navigation. PASS.
- **Body typography:** Acta is more tightly set. R5 deliberately uses the IJSCCN-preferred 12-point reviewer style and therefore has more vertical space. The added space is controlled rather than slide-like. PASS.
- **Paragraph rhythm:** R5 provides more consistent inter-paragraph and heading spacing while retaining scholarly density. PASS.
- **Tables:** Acta embeds multiple dense tables within the running article. R5 moves its two justified tables to separate post-References pages, which follows the conservative IJSCCN revision-ready design and produces cleaner main-text rhythm. PASS.
- **Figures:** Acta contains in-manuscript figure-placement placeholders with separate vector artwork. R5 supplies separate high-resolution regenerated figures plus dedicated post-References legends and avoids placeholder text in the manuscript. PASS.
- **References:** Both use numbered scholarly references. R5 provides more consistent hanging indentation and explicitly incorporates the reconciled peer-reviewed De Zuane LANMAN record. PASS.
- **Professional coherence:** R5 is longer because it combines Study 8 with the separately governed Study 8E extension and uses IJSCCN-preferred 12-point presentation. Page count is therefore not used as a quality metric. At normal reading scale, R5 is at least as professionally organized as the immutable Acta benchmark and is better aligned to the current target venue. PASS.

No Acta submitted binary was edited, regenerated, or replaced.

**Acta direct render-to-render comparison gate:** PASS.

## 10. Current gate status

- Wiley/IJSCCN policy evidence: **PASS**
- scientific source preservation: **PASS**
- citation/reference integrity: **PASS**
- Paper 4 / Paper 5 non-overlap: **PASS**
- exact-head public-safe build: **PASS**
- 18-page manuscript visual QA: **PASS**
- auxiliary-document visual QA: **PASS**
- scientific figure QA: **PASS**
- GTOC QA: **PASS**
- Word structural/a11y QA: **PASS**
- public-safe privacy boundary: **PASS**
- Acta direct render comparison: **PASS**
- personalized local-only package: **NOT YET FINALIZED**
- live Research Exchange upload map: **PENDING PORTAL REOPEN**
- final Wiley submission: **NOT AUTHORIZED**

**R5 public-safe independent visual/publisher QA: PASS.**

**PR #164 remains draft and unmerged. The remaining gates are the personalized local-only package, live Research Exchange upload-map verification, and separate final publisher-submission authorization.**
