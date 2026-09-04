# Study-2 Phase-6 Responsible Release

**Status:** `PUBLIC_DURABLE_ARCHIVE_PUBLISHED_AND_PUBLIC_BYTES_VERIFIED`

This directory records the responsible-release review and durable public-archive closeout for the exact frozen Study-2 Phase-6 source-evidence artifact for experiment `S2-AEATR-001`.

The source evidence itself remains intentionally **not committed to GitHub**. The evidence-of-record is the exact frozen ZIP:

`study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac.zip`

SHA-256:

`195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

The responsible-release review concluded that the exact ZIP was suitable for public durable archiving with a provenance/safety wrapper. No source-evidence record was edited, regenerated, redacted, normalized, or re-zipped by the review or publication step.

## Review result

- decision: `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`
- 3,872 VALID observations
- 0 INVALID attempts
- 85 frozen cells
- ledger/observation identity mismatches: 0
- recomputed observation-hash mismatches: 0
- recorded file-hash mismatches: 0
- credentials/tokens/private keys found: 0
- email addresses/URLs/IP addresses/local absolute paths found: 0
- operational spacecraft/RF/proprietary mission data found: 0
- human-subject data found: 0
- ZIP path-traversal findings: 0
- campaign runtime performed by review: false
- frozen science modified by review: false

See `RESPONSIBLE_RELEASE_REVIEW.md` and `RELEASE_MANIFEST.json` for the release boundary and exact identities.

## Published Zenodo dataset

The exact approved ZIP is now published as a separate Study-2 Zenodo dataset:

- record: `https://zenodo.org/records/22289114`
- version DOI: `10.5281/zenodo.22289114`
- concept DOI: `10.5281/zenodo.22289113`
- version: `1.0.0`
- publication date: `2026-09-04`
- resource type: `Dataset`
- license: `CC BY 4.0`

The publicly served ZIP was independently re-downloaded and recomputed as:

`195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

This exactly matches the frozen Phase-6 source identity.

Current verification authorities:

- [`ZENODO_PUBLICATION_VERIFICATION.md`](ZENODO_PUBLICATION_VERIFICATION.md) — human-readable publication/checksum closeout;
- [`ZENODO_PUBLICATION_VERIFICATION.json`](ZENODO_PUBLICATION_VERIFICATION.json) — machine-readable DOI/public-file identity record.

Historical pre-publication handoff records are retained unchanged as provenance:

- [`ZENODO_DEPOSIT_READY.md`](ZENODO_DEPOSIT_READY.md);
- [`ZENODO_DEPOSIT_METADATA.json`](ZENODO_DEPOSIT_METADATA.json).

## Journal gate

The Study-2 durable DOI archive and public-byte verification gate is **complete**. The remaining journal work is publication-package integration and final submission-day validation:

1. insert the verified Study-2 version DOI/checksum identity into Data Availability and target-specific submission materials;
2. rerun repository and exact-export audits;
3. recheck live journal/portal requirements on the actual submission date;
4. create the final submission export only after those checks pass.

The Study-1 DOI remains a separate Study-1 evidence record and is not reused for Study 2.
