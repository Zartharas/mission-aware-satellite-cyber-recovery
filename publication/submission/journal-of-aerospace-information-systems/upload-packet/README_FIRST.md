# JAIS Paper 1 Upload Packet

**Status:** `STAGING_PACKET__FINAL_MANUSCRIPT_AND_LIVE_SCHOLARONE_LOCK_PENDING`

This folder is the operational handoff point for the AIAA *Journal of Aerospace Information Systems* submission. It does not create a publisher submission and it does not alter frozen Study 1 or Study 2 science.

## What is actually required or expected for initial submission

### Core manuscript upload

AIAA's current public journal guidance requires upload of a **double-spaced manuscript** through ScholarOne. The manuscript must meet the current AIAA journal requirements, including English/American spelling, 10-point type, single-column presentation, a title of no more than 12 words with no acronyms/abbreviations, and a one-paragraph 100-200 word abstract with no numerical references, acronyms, or abbreviations.

**Current Paper-1 status:** the exact final JAIS manuscript export is still pending AIAA reference conversion, final formatting, equivalent-word-count review, citation/DOI audit, and frozen-claim audit. Do not upload an interim manuscript as the final submission.

### Cover letter

A JAIS-specific cover letter is prepared at:

`../cover-letter.md`

Whether ScholarOne requests it as a file, a text field, or an optional item must be confirmed in the live workflow. Do not assume a file designation that the portal does not show.

### ScholarOne metadata and declarations

The following are primarily portal-entry items rather than separate upload files:

- article type;
- title;
- abstract;
- keywords/classifications;
- author/contact and affiliation information;
- funding;
- competing-interest declaration;
- unclassified/public-release and exclusivity attestations;
- artificial-intelligence disclosure;
- suggested reviewers and any reviewer exclusions;
- ethics/human-subject questions, if presented;
- data/code or prior-dissemination fields, if presented;
- copyright/clearance attestations.

Prepared values and unresolved fields are maintained in:

`../scholarone-field-map.md`

and summarized for convenient entry in:

`PORTAL_ENTRY_VALUES.md`

### Figures and tables

AIAA allows figures to be positioned in the manuscript or grouped at the end. PDF artwork is acceptable for peer review. Separate production-grade image files are principally an acceptance/production concern unless ScholarOne explicitly requests them at initial submission.

Tables should remain editable rather than embedded as images.

### Supplemental material

Supplemental material is optional. AIAA states that the article must stand on its own and that acceptance is based on the article itself. The public Zenodo and GitHub research records should therefore **not** be redundantly uploaded as supplemental files by default. See `OPTIONAL_SUPPLEMENTAL.md`.

## Source-of-truth file map

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
- Study 2 remains 3,872 VALID observations across 85 frozen cells.
- The two populations remain separate and are not pooled.
- Study 8 is excluded from Paper 1.
- No new Paper-1 experiment is required or authorized by this packaging work.

## Stop rule

This packet is for preparation and upload readiness only. Do not complete the final ScholarOne submission until:

1. the production ScholarOne fields are captured and locked;
2. the final JAIS manuscript export exists;
3. AIAA reference/citation/DOI and equivalent-word audits pass;
4. Study-1 and Study-2 frozen-claim audits pass;
5. the final package is frozen; and
6. the author separately authorizes actual submission.
