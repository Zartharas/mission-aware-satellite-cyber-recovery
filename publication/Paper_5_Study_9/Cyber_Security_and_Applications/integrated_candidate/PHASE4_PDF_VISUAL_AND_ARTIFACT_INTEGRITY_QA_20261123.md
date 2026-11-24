# Paper 5 Phase 4: visual PDF and GitHub artifact integrity QA

**Review date:** 2026-11-23  
**Manuscript-bearing source SHA:** `b844f92019ae3fce661e7308a24f8f5b04915f56`  
**LaTeX workflow:** [GitHub Actions `45279831571`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45279831571), **SUCCESS**.  
**Artifact:** [`paper5-integrated-draft-latex-qa`, ID `14868614567`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45279831571/artifacts/14868614567), 14-day retention.  
**Purpose:** Close the assistant-executable PDF technical inspection from AR-10; preserve the author-only publication proof as pending.

## 1. Authenticated build and artifact bytes

- **Exact source checkout:** PR head SHA `b844f92019ae3fce661e7308a24f8f5b04915f56` in the reported workflow. Phase 0 frozen-science assertions and Phase 2 nine-question/56-mapping traceability checks all **PASS**.
- **Main PDF:** 33 pages, PDF SHA-256 `800c8f5502579f7cc613b73e44ab75d8d57699edc1b4a416443e782d9eb732c7`, **0 overfull** and **129 underfull** hboxes.
- **Supplement S1:** four pages, PDF SHA-256 `7e7acd18119c39430b8d90ebf5d60c213845f12126d6c2136e40e9640b28a008`, **0 overfull** hboxes.
- **GitHub artifact ZIP:** reported digest `sha256:9b7e3f1512516a8722fba0af701d073ac03f6c2e3dd2c7047b6b6764eb7d4a6b`. The connector-downloaded ZIP was locally hashed and **matched** this exact value.
- **Post-build receipt:** `PDF_REVIEW_SHA256SUMS.txt` was written **after both PDF builds**, included in the ZIP, and verified with `sha256sum -c PDF_REVIEW_SHA256SUMS.txt`. Both original extracted PDF bytes **PASS** and exactly match the runner's printed individual SHA-256 hashes.
- **Transport caveat resolved:** A local attachment/export service later rewrote *separately surfaced copies* of the PDF files; such transformed post-export copies can differ in size and SHA. The pristine PDFs freshly extracted from the validated ZIP match CI. Do not compute a release hash from later converted copies.

## 2. Complete rendered-layout review

**Tool path:** Pulled the actual ZIP from the connected GitHub app; extracted the pristine PDFs in a temporary directory, rendered all 33 main pages and all four supplementary pages with a PDF renderer, examined contact sheets of all pages and specifically inspected the revised native-LaTeX Figure 1 page at closer zoom. Per-page text-block boundaries were validated using PyMuPDF.

| Inspection item | Observed result |
|---|---|
| Main page count / supplement count | **33 + 4**, matches runner logs |
| Missing, empty, damaged or inaccessible pages | **None found**; all 37 pages produced selectable text and rendered |
| Text blocks beyond page boundaries | **0** on all 33 main and four S1 pages |
| Unexpected replacement Unicode or null characters in extracted text | **0** on all pages |
| Overfull LaTeX `hbox` diagnostics | **0** in both final PDFs |
| Main nonfatal underfull `hbox` diagnostics | **129**; typical justification/compact-table spacing, requires author judgment at proof |
| Conceptual Figure 1 | The prior isolated figure-only page was fixed: the diagram and the start of the Results section now share **main page 17**; four blocks and distinct S9/S10 endpoints are visibly present |
| Figures/tables and source-field supplement | No visually obvious clipping/cropping from the all-page review; tables use compact type, especially closest-work comparison and field-level appendix |
| Citations and source counts | 24 distinct cited bibliography items; 24 Study 9 + 32 Study 10 source-field mapping markers validated by exact-head CI |
| Final author acceptance | **NOT GIVEN**; this is a technical/AI-assisted inspection, not author signoff |

## 3. Current visual observations and residuals

- **Page 17:** The replaced explanatory schematic is no longer isolated on a nearly empty page. Both branches remain legible: Study 9's all-unknown finite Boolean completions under frozen selectors, and Study 10's withheld operational action when decision time/validity cannot be established. The caption now discloses the current GPT-6 revision and the unknown older-draft model. **Author must verify** the diagram and disclosure.
- **Main closest-work table (approximately page 9):** compact `\scriptsize` column text is visible in the PDF but small at print scale. Its citations and units are present; author should zoom to normal viewing and decide whether a readability improvement is needed. No overfull-width diagnostic was found.
- **S1 appendix:** the four-page longtable is dense by design; table rows and evidence-role abbreviations appear within page bounds. Author must independently verify domain-specific field-name readability.
- **Citations and page proof:** no unexpected empty page, clipping or inaccessible text was detected. This is not a WCAG/PDF-UA accessibility certification; the PDF is not tagged as an accessible archival PDF, and the publisher may re-typeset after submission.
- **No empirical validation inferred:** the rendered schematic and PDFs do not prove original source classification correctness, operational recovery success, publisher originality acceptance, data rights, or legal disclosures.

## 4. QA disposition

`ASSISTANT_TECHNICAL_PDF_QA_PASS`: Final artifact provenance and screen-based page-level review completed for the named manuscript-bearing SHA, with **no blockingly malformed layouts identified**.  
`AUTHOR_FINAL_VISUAL_PROOF_PENDING`: The sole author must still personally inspect, correct if necessary, and approve the exact final PDFs and title/contact details before any journal upload.  
`PR_255_DRAFT_UNMERGED_NO_SUBMISSION`: No publication or artifact redistribution of third-party source bytes.
