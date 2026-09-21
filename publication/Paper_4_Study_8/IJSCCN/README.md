# Paper 4 — IJSCCN Submission Package R1

Target journal: **International Journal of Satellite Communications and Networking (Wiley)**

This directory is a venue-specific derivative of the frozen/reviewed Paper 4 manuscript. The venue-neutral source remains authoritative for scientific content.

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
