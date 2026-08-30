# WP11 Responsible Artifact Release Plan

**Date:** 2026-08-29  
**Status:** Release tooling prepared; local candidate generation and audit required before upload  
**Scientific manuscript authority:** `docs/28`–`docs/37`  
**Raw campaign authority:** local `results/wp9/campaign/attempt-history.json` and frozen campaign tree  
**Primary archive target:** Zenodo

## Purpose

WP11 creates a durable, citable research release without weakening the frozen scientific record or silently publishing material that has not passed licensing, privacy/secrets, reproducibility, and misuse-risk review.

The release process is deliberately staged:

1. verify the local frozen source identities;
2. create deterministic archives outside the repository;
3. re-verify that packaging did not change the source evidence;
4. audit the candidate archives;
5. review rights, access visibility, and metadata;
6. create a Zenodo draft/reserve DOI if desired;
7. upload only the audited candidate objects;
8. verify uploaded/downloaded object checksums;
9. publish the record;
10. capture the version DOI and concept DOI and update the manuscript/repository.

No stage may silently repair, remove, rewrite, or regenerate raw scientific evidence.

## Frozen source identities

The local release tooling fails closed unless it re-observes:

- authoritative ledger SHA-256: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`;
- ledger records: `729` = `720 VALID + 9 INVALID`;
- 720-valid analysis-membership SHA-256: `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`;
- complete local campaign-tree file count: `17182`;
- complete deterministic campaign-tree SHA-256: `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`;
- integrity-freeze bundle checksum-file SHA-256: `696bc615c1f227320aced30c1c88f4664f62def0cfbb454209e6068785e2d819`.

The campaign is hashed before and after packaging. Any source-tree, ledger, file-count, or Git-worktree change aborts the release-candidate process.

## Deterministic local release candidate

Run `scripts/prepare_wp11_release_candidate.py` only from a clean local `main` that contains the audited WP10-G7 manuscript commit.

The default output is a new directory under Downloads and contains only upload-candidate objects:

1. `01-wp9-campaign-raw.tar.gz` — complete frozen local WP9 campaign tree, including the ledger, VALID/INVALID evidence, pre-runtime/unledgered evidence, and preserved quarantine partition as present in the frozen tree;
2. `02-wp9-integrity-freeze.tar.gz` — publication-grade integrity-freeze bundle;
3. `03-publication-and-provenance.tar.gz` — tracked manuscript, publication tables/figures, research documentation, references, and selected tracker/repository records; it intentionally excludes source/runtime/config/test code from this data/publication archive;
4. `RELEASE_MANIFEST.json`;
5. `README_RELEASE.txt`;
6. `RELEASE_CHECKSUMS.sha256`.

Archive generation normalizes gzip/tar timestamps, uid/gid, names, modes, and file order to support deterministic reproduction. The raw source files themselves are read only.

## Candidate audit

Run `scripts/audit_wp11_release_candidate.py <candidate-directory>` after packaging.

The audit report is written **beside** the candidate directory, not inside it, so auditing cannot change the exact upload object set.

The automated audit checks:

- release checksums;
- manifest source identities;
- expected three-archive structure;
- exactly `17182` regular files in the raw campaign archive;
- no absolute/path-traversal/nonregular archive members;
- high-confidence private-key/AWS/GitHub/Slack-token patterns in text-sized members;
- filenames associated with credentials/private keys;
- no raw campaign/source/runtime/config/test paths in the publication/provenance archive;
- current default Zenodo file-count/storage gates.

`REVIEW_REQUIRED` is not authorization to delete or modify raw evidence. Any candidate finding must be investigated against the source and resolved through release scope/visibility decisions or a separately documented sanitized derivative, while preserving the original frozen evidence.

## Misuse-risk review

Automated secrets scanning is necessary but not sufficient. Before public visibility is selected, manually confirm that the candidate does not disclose:

- operational credentials, tokens, private keys, or real account identifiers;
- non-public satellite/ground-station addresses, endpoints, schedules, or identifiers;
- live RF parameters intended to enable interference;
- partner-sensitive vulnerabilities or proprietary telemetry;
- classified/export-controlled technical data;
- human-subject/interview content;
- third-party copyrighted data whose redistribution is not permitted;
- detailed offensive instructions materially beyond the already public/synthetic laboratory scope.

The experiment itself remains a defensive, researcher-controlled software-in-the-loop study. If a raw artifact is scientifically important but unsuitable for general public distribution, prefer Zenodo restricted-file visibility or a documented sanitized derivative rather than altering the frozen source.

## Licensing and rights gate

Zenodo requires a license field and currently defaults new records to CC BY 4.0. **Do not accept that default automatically for this mixed research object.**

Before publication, review rights separately for:

- researcher-authored documentation/tables/figures;
- source code already governed by repository/software licenses;
- raw generated campaign evidence;
- bundled third-party text/data, if any;
- external software that is referenced but should not be redistributed;
- third-party datasets whose selected-record license may restrict redistribution.

If files in one record are governed by different licenses, Zenodo supports multiple/custom rights statements. The final metadata must describe the rights actually applicable to the uploaded content.

## Zenodo capacity and visibility

Checked against Zenodo Help on 2026-08-29:

- each record has a default storage quota of `50 GB`;
- Zenodo supports additional storage allocation subject to account quota, but this workflow uses `50 GB` as the conservative default gate;
- the packaging design produces far fewer than 100 top-level upload objects;
- record metadata remains public after publication;
- files can be public or restricted, and restricted files can later be shared or placed under embargo/access controls.

The packaging scripts do not choose public versus restricted visibility. That choice occurs only after the local audit and rights/misuse review.

## DOI workflow

Zenodo registers a DOI when a record is published. Zenodo also permits reserving the DOI while the record is still a draft. If a DOI is reserved, it may be inserted into release/manuscript metadata before publication, but the record must not be described as published until the Zenodo publish action completes.

For later versions, cite the specific version DOI for reproducibility and also retain the concept DOI when applicable for the evolving research object.

## Data Availability update rule

The current manuscript correctly states that the DOI-bearing archive is pending.

Only after upload, checksum verification, and Zenodo publication may the repository/manuscript be updated to state that the release is publicly available or restricted at a DOI. The update must record:

- Zenodo record URL;
- version DOI;
- concept DOI, when provided;
- file visibility (public/restricted/embargoed);
- release-object SHA-256 values;
- date of checksum verification;
- exact Git commit/tag corresponding to the archived publication/provenance package.

## GitHub release/tag boundary

Do not create a final publication tag/release until the local candidate and upload audit are complete. The final tag should identify the repository state corresponding to the archived publication/provenance object and should not imply that raw campaign evidence is committed to Git.

## Current authorization boundary

WP11 release preparation is authorized. The repository tooling/docs may be merged now.

The next execution step genuinely requires the researcher's local files because `results/wp9/campaign/` and the integrity-freeze directory are intentionally not available through GitHub. After the local packaging/audit output is reviewed, Zenodo draft/upload/publication remains an authenticated archive action and must not be claimed as performed until it actually occurs.