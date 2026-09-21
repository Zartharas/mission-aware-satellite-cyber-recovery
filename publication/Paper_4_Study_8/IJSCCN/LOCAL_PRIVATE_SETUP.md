# Local-Only IJSCCN Submission Materials

This repository intentionally keeps private author-contact data, the author photograph, and upload-ready personalized submission documents out of Git.

## Ignored local directories

Use these paths only on the author's local workstation:

- `publication/Paper_4_Study_8/IJSCCN/_local_private/`
- `publication/Paper_4_Study_8/IJSCCN/_local_submission/`

Both directories are ignored by the repository-level `.gitignore`.

## One-time local setup

1. Create the private directory:

   ```bash
   mkdir -p publication/Paper_4_Study_8/IJSCCN/_local_private
   ```

2. Copy `AUTHOR_PRIVATE.template.json` to the ignored private directory as:

   ```text
   publication/Paper_4_Study_8/IJSCCN/_local_private/author_private.json
   ```

3. Fill that local JSON file with the submission-only author metadata.

4. Save the recent professional author photograph in the same ignored directory using one of these names:

   ```text
   author_photo.png
   author_photo.jpg
   author_photo.jpeg
   author_photo.tif
   author_photo.tiff
   ```

5. Build the local personalized submission package:

   ```bash
   python3 publication/Paper_4_Study_8/IJSCCN/build_ijsccn_package.py
   ```

When `author_private.json` exists, the builder writes personalized output only to:

```text
publication/Paper_4_Study_8/IJSCCN/_local_submission/build/
```

The ignored local output contains the upload-ready manuscript/supporting documents. If an author photograph is present, it is copied into the local build as `AUTHOR_PHOTOGRAPH.<ext>`.

## GitHub behavior

When the private metadata file is absent, the builder uses non-private placeholder metadata and writes only a public-safe QA build to the normal ignored `build/` directory. GitHub Actions must never receive the local private directory.

Before any commit or push, verify:

```bash
git check-ignore -v publication/Paper_4_Study_8/IJSCCN/_local_private/author_private.json
git check-ignore -v publication/Paper_4_Study_8/IJSCCN/_local_private/author_photo.png
git check-ignore -v publication/Paper_4_Study_8/IJSCCN/_local_submission/build/MANUSCRIPT_IJSCCN.docx
git status --short
```

The first three commands should report matching ignore rules. Private files must never appear in `git status --short`.

## Scientific boundary

This privacy overlay changes submission metadata handling only. It does not change Study 8, Study 8E, TRACE-002, Results-002, manuscript scientific claims, numerical values, or the Paper 4 / Paper 5 separation.

## Governance authority

Privacy handling is governed by:

`publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_LOCAL_PRIVATE_SUBMISSION_PRIVACY_GATE_2026-09-21.md`
