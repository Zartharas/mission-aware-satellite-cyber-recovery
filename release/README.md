# Responsible Release Workflow

This directory contains repository-side templates and checklists for WP11 responsible artifact release. It does **not** contain the raw WP9 campaign and it does not indicate that a Zenodo deposit has been published.

## Local release sequence

1. Synchronize a clean local `main` to the WP11-preparation merge commit.
2. Confirm that the frozen raw campaign remains at `results/wp9/campaign/` and that the WP9 integrity-freeze directory is available locally.
3. Run:

   ```bash
   python3 scripts/prepare_wp11_release_candidate.py
   ```

4. Review the decisive status. Do not continue if any frozen identity, file count, source-immutability, or size/file-count gate fails.
5. Audit the generated candidate:

   ```bash
   python3 scripts/audit_wp11_release_candidate.py \
     "$HOME/Downloads/WP11_RELEASE_CANDIDATE_<HEAD7>"
   ```

6. Review the audit JSON written beside the candidate directory. `PASS` is necessary but does not replace manual rights/misuse review.
7. Complete `UPLOAD_CHECKLIST.md` and `ZENODO_METADATA_TEMPLATE.md` before creating/publishing the archive record.
8. Do not alter files inside the audited candidate. If the candidate must change, create a **new** candidate directory and repeat verification/audit.

## Candidate object set

The packager creates:

- `01-wp9-campaign-raw.tar.gz`
- `02-wp9-integrity-freeze.tar.gz`
- `03-publication-and-provenance.tar.gz`
- `RELEASE_MANIFEST.json`
- `README_RELEASE.txt`
- `RELEASE_CHECKSUMS.sha256`

The audit report is deliberately outside this directory so the upload-candidate object set remains immutable after preparation.

## What the tooling does not do

The tooling does not:

- run a scientific experiment;
- consume campaign seeds;
- modify `results/wp9/campaign/`;
- delete/quarantine evidence;
- stage, commit, or push Git changes;
- choose a license or public/restricted visibility;
- upload files;
- publish a Zenodo record;
- assign or reserve a DOI.

## Failure handling

A packaging or audit failure is evidence to investigate, not permission to modify the frozen scientific source. Preserve failed candidate directories and audit output until the discrepancy is understood. If release scope must change, document the decision and create a fresh candidate from the unchanged frozen source.