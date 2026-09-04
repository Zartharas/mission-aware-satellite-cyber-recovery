# JAIS Paper 1 Upload Packet

**Status:** `JAIS_MANUSCRIPT_CONTENT_READY__SCHOLARONE_FIELD_LOCK_PENDING`

This folder is the operational handoff point for the AIAA *Journal of Aerospace Information Systems* submission. It does not create a publisher submission and it does not alter frozen Study 1 or Study 2 science.

## Core manuscript upload

The publisher-facing JAIS manuscript has now completed its export, reference, scientific-boundary, repository-validation, and visual-layout gates.

**Frozen generation record:**

- generation commit: `506c3d26d812709efec86c856514d541343c0b57`;
- workflow run: `33907150553`;
- workflow artifact ID: `9949926197`;
- manuscript filename: `JAIS_MANUSCRIPT.docx`;
- manuscript SHA-256: `30910535075c3c8d13f501d721e46dd8537774c2d366ca858cdd71222d9edf64`;
- artifact ZIP SHA-256: `8f8171f4f2619595631829b5c17c58a8e88cacbe9604e05413562181d53a213f`.

The exact record and completed checks are maintained in `MANUSCRIPT_CONTENT_READY.md`.

Current manuscript audit state:

- 12-word JAIS title — PASS;
- 171-word, one-paragraph, third-person AIAA abstract — PASS;
- 10-point Times New Roman, double-spaced, single-column Word presentation — PASS;
- numerical AIAA citation/reference order — PASS;
- 20 reviewed numbered references with DOI URLs where available — PASS;
- equivalent length: 8,308 / 12,000 words — PASS;
- frozen Study-1/Study-2 claim boundaries — PASS;
- Study-8 exclusion — PASS;
- exact CI-generated 25-page Word-manuscript visual QA — PASS;
- broader repository validation and frozen WP10 reproduction — PASS.

Do not substitute the target-neutral manuscript or an older JAIS artifact for this frozen publisher-facing manuscript.

## Cover letter

A JAIS-specific cover letter is prepared at `../cover-letter.md`.

Whether ScholarOne requests it as a file, text field, or optional item must be confirmed in the authenticated production workflow. Do not assume a file designation that the portal does not show.

## ScholarOne metadata and declarations

The remaining pre-freeze blocker is the **exact authenticated ScholarOne schema**. The following must be captured from the production workflow rather than inferred:

- exact article-type dropdown label;
- title and abstract validation behavior;
- keyword/classification controls;
- author/contact, affiliation, and postal fields;
- funding and competing-interest fields;
- unclassified/public-release and exclusivity attestations;
- artificial-intelligence disclosure field;
- suggested-reviewer count/rules and reviewer exclusions, if offered;
- ethics/human-subject questions, if presented;
- data/code or prior-dissemination fields, if presented;
- copyright/clearance attestations;
- file-upload item labels, designations, and ordering;
- final review/build/submit steps.

Prepared values and unresolved fields are maintained in `../scholarone-field-map.md` and summarized for entry in `PORTAL_ENTRY_VALUES.md`.

## Figures and tables

For peer review, the manuscript contains editable tables. The JAIS-facing display form of the wide result tables is derived deterministically from the frozen manuscript-facing CSVs; the source tables and frozen numerical Results are unchanged.

Separate production-grade artwork is not part of the initial packet unless the authenticated ScholarOne workflow explicitly requests it.

## Supplemental material

Current initial-submission decision: **none planned by default**. The article stands on its own, while the public Zenodo and GitHub records provide the research evidence and reproducibility materials. See `OPTIONAL_SUPPLEMENTAL.md`.

## Source-of-truth file map

- Content-ready manuscript identity: `MANUSCRIPT_CONTENT_READY.md`
- Upload manifest: `UPLOAD_MANIFEST.md`
- Portal entry sheet: `PORTAL_ENTRY_VALUES.md`
- Target package overview: `../README.md`
- Current AIAA requirements evidence: `../live-requirements-2026-09-04.md`
- JAIS abstract: `../jais-abstract.md`
- Title/author/funding metadata: `../title-page.md`
- Cover letter: `../cover-letter.md`
- AIAA artificial-intelligence disclosure: `../ai-disclosure.md`
- ScholarOne field map: `../scholarone-field-map.md`
- Submission checklist: `../submission-checklist.md`
- Venue-fit/risk review: `../venue-fit.md`

## Frozen-science boundary

- Study 1 remains 720 VALID observations across 24 frozen cells.
- Study 2 remains 3,872 VALID observations across 85 frozen cells with zero INVALID attempts.
- The two populations remain separate and are not pooled.
- Study 8 is excluded from Paper 1.
- No new Paper-1 experiment is required or authorized by this packaging work.

## Stop rule

The manuscript-content gate is closed. **Do not complete the final ScholarOne submission yet.** Next:

1. inspect the authenticated production ScholarOne workflow without submitting;
2. record and reconcile every exact portal field/designation;
3. freeze the exact upload package and repository snapshot against that schema; and
4. obtain separate explicit author authorization for the final publisher submission.
