# Responsible Release and Published Archive

This directory contains repository-side controls for the WP11 responsible-release process and the now-completed Zenodo publication.

## Published record

The exact six-object WP11 release candidate was published publicly on Zenodo on 2026-08-30 as **Version 1.0.0**:

- version DOI: <https://doi.org/10.5281/zenodo.22181540>
- concept DOI: <https://doi.org/10.5281/zenodo.22181539>
- resource type: Dataset
- license: CC BY 4.0
- creator: Aman Singh, Independent Researcher, ORCID <https://orcid.org/0009-0008-9752-3743>

Repository-side publication closeout: [`../docs/40-zenodo-publication-closeout.md`](../docs/40-zenodo-publication-closeout.md).

## What is in this directory?

- [`RIGHTS_AND_MISUSE_REVIEW.md`](RIGHTS_AND_MISUSE_REVIEW.md) — the pre-publication review template/control used to govern rights, privacy, misuse, and access decisions. The completed external review evidence was retained outside the six-object candidate; the final decision for the exact candidate was `PUBLIC_FILES` / `APPROVED_FOR_PUBLICATION`.
- [`UPLOAD_CHECKLIST.md`](UPLOAD_CHECKLIST.md) — pre-publication upload/integrity checklist.
- [`ZENODO_METADATA_TEMPLATE.md`](ZENODO_METADATA_TEMPLATE.md) — the pre-publication metadata template, now marked as historical/superseded by the published record.

This directory does **not** duplicate the raw WP9 campaign. The raw public evidence is in the Zenodo record.

## Exact published candidate object set

The published v1.0.0 archive contains exactly:

1. `01-wp9-campaign-raw.tar.gz`
2. `02-wp9-integrity-freeze.tar.gz`
3. `03-publication-and-provenance.tar.gz`
4. `README_RELEASE.txt`
5. `RELEASE_CHECKSUMS.sha256`
6. `RELEASE_MANIFEST.json`

The ordering above is the recommended human reading/verification order: raw evidence → integrity freeze → publication/provenance → release instructions → checksums → machine-readable manifest.

The exact SHA-256 identities are recorded in [`../docs/40-zenodo-publication-closeout.md`](../docs/40-zenodo-publication-closeout.md).

## Local release sequence retained for reproducibility

The original preparation workflow remains useful for auditing how the candidate was produced:

1. Synchronize a clean local `main` to the intended release-preparation baseline.
2. Confirm the frozen raw campaign remains at `results/wp9/campaign/` and the WP9 integrity-freeze directory is available locally.
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
7. Complete the rights/privacy/misuse and metadata checks before any new archive publication.
8. Do not alter files inside an audited candidate. If a candidate must change, create a **new** candidate and repeat verification/audit.

## What the tooling does not do

The preparation/audit tooling does not:

- run a scientific experiment;
- consume campaign seeds;
- modify `results/wp9/campaign/`;
- delete/quarantine evidence;
- stage, commit, or push Git changes;
- choose a license or visibility decision;
- authenticate to Zenodo;
- upload files;
- publish a Zenodo record;
- assign or reserve a DOI.

The Zenodo publication was a separate authenticated human-authorized action after the candidate passed the release gates.

## Versioning rule after publication

Zenodo v1.0.0 is now the published evidence-of-record for this study phase. Do not mutate local copies and describe them as the same archived object.

If the archived **files** need to change, use a new Zenodo version and document the relationship. If only metadata needs correction and Zenodo permits an in-place metadata edit, preserve the exact v1.0.0 file identities and the scientific claim boundary.

## Failure handling for future releases

A packaging or audit failure is evidence to investigate, not permission to modify frozen scientific source. Preserve failed candidate directories and audit output until the discrepancy is understood. If release scope changes, document the decision and create a fresh candidate from the unchanged frozen source.
