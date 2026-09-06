# TAES Upload Files - Paper 2

**Status:** `DEVELOPMENT_PLACEHOLDER__NOT_READY_FOR_PORTAL_UPLOAD`  
**Portal:** IEEE Atypon ReX for TAES

This file is the future upload manifest. Do not upload files from this directory merely because they exist. Only files marked `FROZEN_FOR_SUBMISSION` after final QA and explicit author authorization may be uploaded.

All publisher-facing upload files will live directly in this canonical TAES directory. Do not create a separate Downloads copy, desktop copy, or `PORTAL_UPLOAD` staging directory. At submission time, select the frozen files directly from this repository folder in the local Git clone.

## Initial-submission files

### Required by public TAES instructions

| File | Role | Current state |
|---|---|---|
| `TAES_MANUSCRIPT.pdf` | Regular Paper manuscript in TAES two-column format | NOT CREATED |

### Conditional

| File | Role | Current state |
|---|---|---|
| `TAES_SUPPLEMENTARY_MATERIAL.zip` | Frozen reproducibility/support package, if selected | NOT DECIDED |
| `TAES_SUPPLEMENTARY_README.pdf` or `.txt` | Supplementary-material description/instructions | NOT CREATED |
| Essential reference material | Only if essential for review and otherwise unavailable | NOT EXPECTED |
| Cover letter | Only if the live Atypon ReX workflow presents a requirement or useful optional field | LIVE PORTAL RECHECK REQUIRED |

## Internal files that are not publisher uploads

Unless the live portal specifically requests them, do not upload:

- `README_SUBMISSION.md`
- `TAES_AIMS_SCOPE_REQUIREMENTS.md`
- `TAES_COMPLIANCE_CHECKLIST.md`
- `TAES_PORTAL_FIELD_MAP.md`
- `TAES_MANUSCRIPT_DEVELOPMENT.md`
- `TAES_ORIGINALITY_AI_SUPPLEMENTARY_CONTROL.md`
- `TAES_PACKAGE_STATUS.json`
- `TAES_LOCAL_SYNC.sh`
- future `SHA256SUMS.txt`
- future internal final-authorization/proof-QA records

These files exist to control the submission process and preserve provenance.

## File-freeze sequence

Before a file changes to `FROZEN_FOR_SUBMISSION`:

1. manuscript scientific audit PASS;
2. citation and originality audit PASS;
3. TAES format audit PASS;
4. page-by-page PDF visual QA PASS;
5. AI disclosure verified;
6. supplementary decision finalized;
7. upload filenames stabilized;
8. SHA-256 checksums generated;
9. portal values reviewed against canonical files;
10. explicit final author submission authorization received.

## After submission

After successful TAES submission, append:

- exact uploaded filenames;
- file sizes;
- SHA-256 identities;
- manuscript ID;
- submission timestamp;
- portal proof identity, if one is generated;
- dashboard status;
- confirmation-email record.
