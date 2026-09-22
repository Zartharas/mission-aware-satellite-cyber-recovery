# Paper 4 — IJSCCN Submission Package and R5 Rebuild State

Target journal: **International Journal of Satellite Communications and Networking (Wiley)**

This directory is a venue-specific derivative of the frozen/reviewed Paper 4 manuscript. The venue-neutral source remains authoritative for scientific content.

## Current author-review state — 2026-09-21

The repository-generated **R1 package remains historical/frozen provenance**, but it is **not the current publisher-upload candidate**.

Local-only R4.x personalized packages were generated under the ignored `_local_submission/` privacy boundary. During direct author review in Microsoft Word, the author identified unacceptable journal-manuscript presentation defects, including a Symbol/private-use bullet rendering failure and broader page-composition problems. A later local R4.3 formatting repair corrected the obvious glyph defect but did not meet the author's publication-quality benchmark.

**Decision:** do not upload R4.3. Rebuild the publisher-facing manuscript and submission documents as a new **R5** derivative before any Wiley upload.

R5 is a presentation/submission-document rebuild only. It must preserve all frozen Study 8 and Study 8E science, results, hashes, citations, claim boundaries, and the separation of the two study populations. No new scientific execution or statistical reanalysis is authorized.

The exact rejected Acta Astronautica manuscript remains immutable historical provenance. It may be inspected as a **visual-quality benchmark** for scholarly typography, spacing, page rhythm, headings, lists, captions, and overall professionalism, but its scientific scope and venue-specific structure must not be copied blindly into IJSCCN.

### R5 live-policy validation sources

Before rebuilding R5, re-check the current journal-specific and Wiley-wide requirements, following all relevant linked pages:

- IJSCCN Author Guidelines: https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html
- Wiley Prepare hub: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/index.html
- Wiley Manuscript Preparation Guidelines: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/index.html
- Wiley Submission and Peer Review: https://authors.wiley.com/author-resources/Journal-Authors/submission-peer-review/index.html

Journal-specific IJSCCN instructions take precedence over generic Wiley guidance when the two differ. Live portal requirements take precedence for fields and certifications actually presented during submission.

### R5 public-policy audit status

The exhaustive public-source audit is complete and recorded in:

- `R5_WILEY_IJSCCN_EVIDENCE_AUDIT_2026-09-22.md`
- `R5_LIVE_POLICY_REQUIREMENT_MATRIX_2026-09-21.md`
- `R5_MANUSCRIPT_DESIGN_SPEC_2026-09-21.md`

**Public-policy evidence gate: PASS.**

The audit corrected three earlier overstatements: literal IMRaD heading names are not proven mandatory, initial Free Format does not absolutely require separated tables/figures, and the dedicated post-References Figure Legends section is a Wiley-preferred presentation rather than an IJSCCN-specific initial-submission mandate. R5 will still use the stricter, revision-ready presentation as a deliberate design choice.

The remaining unknowns are submission-instance portal details such as anonymization mode, exact file designations, CRediT/editor-reviewer fields, and certain certifications. These must be checked when the live Research Exchange draft is reopened and do not block the source-manuscript rebuild.

### R5 design gate

The next submission candidate must pass all of the following before portal upload:

1. current IJSCCN/Wiley policy audit with citations and conflict reconciliation;
2. professional single-column reviewer-manuscript layout appropriate for initial submission;
3. figure and table treatment that follows IJSCCN-specific instructions;
4. required GTOC, biography/photo, declarations, Data Availability Statement, AI disclosure, funding, and competing-interest content;
5. zero em dashes, per author requirement;
6. scientific-preservation comparison against frozen authorities;
7. page-by-page visual inspection at normal reading scale;
8. local-only privacy validation for personalized metadata/photo;
9. exact portal-file mapping;
10. separate author authorization before final publisher submission.


## Package contents

- `MANUSCRIPT_IJSCCN.md` — IJSCCN-adapted manuscript source.
- `TITLE_PAGE.md` — title-page metadata.
- `COVER_LETTER.md` — submission cover-letter source.
- `DATA_AVAILABILITY_STATEMENT.md` — Wiley-required data availability.
- `AI_USE_DECLARATION.md` — Wiley-aligned AI disclosure.
- `AUTHOR_BIOGRAPHY.md` — <=200-word biography.
- `GTOC.md` — Graphical Table of Contents text/graphic specification.
- `SUBMISSION_CHECKLIST.md` — live author-guideline compliance checklist.
- `REFERENCES.bib` — derivative bibliography copied from the reviewed venue-neutral manuscript.
- `figures/` — source/high-resolution figures.
- `PACKAGE_STATUS.json` — package governance state.
- `AUTHOR_PRIVATE.template.json` — placeholder-only template for local private metadata.
- `LOCAL_PRIVATE_SETUP.md` — local-only privacy/build instructions.

## Frozen boundaries

This package does not alter Study 8, Study 8E, TRACE-002, Results-002, or the rejected Acta package.

Study 8 and Study 8E remain separate finite populations. No pooled denominator, logical-slot-to-hours conversion, operational-command-contact claim, or measured-throughput claim is permitted.

## Local-only privacy boundary

Private submission metadata and the recent author photograph must be stored only under the ignored local path:

`publication/Paper_4_Study_8/IJSCCN/_local_private/`

Personalized upload-ready files must be generated only under:

`publication/Paper_4_Study_8/IJSCCN/_local_submission/`

Neither directory may be tracked or uploaded as a GitHub Actions artifact. The tracked package sources contain template tokens instead of private contact values. GitHub Actions builds only a public-safe QA package with placeholder author metadata.

See `LOCAL_PRIVATE_SETUP.md` for the local build procedure.

## Submission authorization

Package preparation is authorized.

Publisher submission is **not authorized**.
