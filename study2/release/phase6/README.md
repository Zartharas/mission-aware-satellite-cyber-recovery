# Study-2 Phase-6 Responsible Release

**Status:** `RESPONSIBLE_RELEASE_REVIEW_PASS_DOI_DEPOSIT_PENDING`

This directory records the responsible-release review of the exact frozen Study-2 Phase-6 source-evidence artifact for experiment `S2-AEATR-001`.

The source evidence itself is intentionally **not committed to GitHub**. The evidence-of-record for the planned public release remains the exact frozen ZIP:

`study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac.zip`

SHA-256:

`195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

The responsible-release review concluded that the exact ZIP is suitable for public durable archiving with a provenance/safety wrapper. No source-evidence record was edited, regenerated, redacted, normalized, or re-zipped by the review.

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

## Remaining journal gate

The review is complete, but the Study-2 source archive is **not yet DOI-complete**. Before journal submission:

1. deposit the exact approved source ZIP to a new durable DOI-bearing Study-2 dataset record;
2. verify the publicly served ZIP SHA-256 against the frozen source identity above;
3. record the actual version DOI (and concept DOI if assigned);
4. insert the verified DOI/checksum identity into manuscript Data Availability and target-specific submission materials;
5. rerun the repository and exact-export audits.

Do not reuse the Study-1 DOI and do not invent a Study-2 DOI before publication.
