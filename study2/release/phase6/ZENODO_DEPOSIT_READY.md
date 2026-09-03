# Study-2 Phase-6 DOI Deposit Handoff

**State:** `DEPOSIT_READY_EXTERNAL_AUTHENTICATED_PUBLICATION_REQUIRED`  
**Prepared:** 2026-09-03  
**Experiment:** `S2-AEATR-001`

This handoff closes every repository-side prerequisite for a durable DOI-bearing release of the exact Study-2 Phase-6 source-evidence ZIP. It does **not** claim that a DOI already exists.

## Exact object to publish

- filename: `study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac.zip`
- SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- GitHub Actions run: `33547420437`
- GitHub Actions artifact ID: `9816191406`
- artifact name: `study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac`
- artifact digest reported by GitHub: `sha256:195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- artifact expiry reported by GitHub: `2026-11-30T19:05:03Z`

The repository responsible-release review already approved this exact byte sequence with disposition:

`APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`

Do not regenerate, normalize, edit, redact, rename internally, or re-zip the evidence before deposit. If the local downloaded filename includes a wrapper-directory or browser-added suffix, the byte content must still hash to the exact SHA-256 above before upload.

## Deposit metadata

Use `ZENODO_DEPOSIT_METADATA.json` as the reviewed metadata handoff. The intended resource type is **dataset** and the recommended license is **CC BY 4.0**.

The creator identity is drawn from the repository citation record:

- Aman Singh
- ORCID `0009-0008-9752-3743`
- affiliation: Independent Researcher

## Authenticated Zenodo procedure

Zenodo requires the account holder to create/publish the record. The repository automation does not have authority to perform that external account action.

1. Sign in to Zenodo and create a **new upload**.
2. Upload the exact ZIP identified above.
3. Set resource type to **Dataset**.
4. Enter the reviewed metadata from `ZENODO_DEPOSIT_METADATA.json`.
5. Set the recommended license to **Creative Commons Attribution 4.0 International (CC BY 4.0)** unless the repository release decision is intentionally superseded by a separately reviewed change.
6. Do **not** enter the Study-1 DOI as the DOI for this upload.
7. Because this Study-2 object does not already have a DOI, either reserve a new DOI in the draft or allow Zenodo to assign one at publication.
8. Preview the record and confirm that the title, creator, resource type, description, license, and file are correct.
9. Publish the record.
10. Record the actual **version DOI** and, if Zenodo exposes one, the **concept DOI**.

Zenodo's current documentation states that a DOI is registered when the record is published; a DOI may also be reserved while the upload is still a draft.

## Mandatory post-publication verification

Before inserting the DOI into the manuscript:

1. download the publicly served Study-2 ZIP from the published record;
2. compute SHA-256;
3. require exact equality with:

   `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

4. verify that the record identifies the object as Study-2 / `S2-AEATR-001`, not Study 1;
5. verify the record exposes the intended license and creator identity;
6. only then update Data Availability, `CITATION.cff` references if appropriate, submission materials, and release-gate expectations with the real DOI.

If the publicly served bytes do not match, stop. Do not alter the frozen source evidence to make it match the deposit. Correct the external draft/record according to repository governance and re-verify.

## Current DOI state

`PENDING_EXTERNAL_DURABLE_ARCHIVE_PUBLICATION`

No DOI is claimed by this handoff.
