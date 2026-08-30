# WP11 Archive Upload and Verification Checklist

Use this checklist only after the local release candidate exists and `scripts/audit_wp11_release_candidate.py` returns `PASS` or a separately reviewed release decision explicitly resolves every `REVIEW_REQUIRED` finding.

## A. Local source/candidate gate

- [ ] Local repository is on clean `main` at the WP11-preparation merge commit or a documented descendant.
- [ ] Authoritative ledger SHA-256 equals `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`.
- [ ] Campaign tree contains exactly `17182` files.
- [ ] Campaign tree SHA-256 equals `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`.
- [ ] Integrity-freeze checksum bundle verifies.
- [ ] Release candidate was created in a new directory; no object was overwritten.
- [ ] `RELEASE_CHECKSUMS.sha256` verifies locally.
- [ ] Local release audit is `PASS`.
- [ ] Audit report is outside the immutable candidate directory.
- [ ] Packaging re-verification reports `source_campaign_unchanged=true` and `git_worktree_unchanged=true`.

## B. Manual rights/privacy/misuse gate

- [ ] `release/RIGHTS_AND_MISUSE_REVIEW.md` completed.
- [ ] No operational credentials/tokens/private keys.
- [ ] No non-public operational satellite/ground-station identifiers/endpoints/schedules.
- [ ] No live RF parameters intended to enable interference.
- [ ] No proprietary/classified/export-controlled material.
- [ ] No human-subject/interview content.
- [ ] No third-party data redistributed beyond its actual license/terms.
- [ ] Release of raw laboratory evidence is consistent with responsible-use goals.
- [ ] If any file should not be public, Zenodo restricted visibility/access conditions are selected rather than altering the frozen source.

## C. Zenodo draft setup

- [ ] Create a **draft**, not a published record.
- [ ] Record type selected appropriately for the research data/reproducibility object.
- [ ] Creators and order verified by the author(s).
- [ ] Affiliations/ORCIDs verified; none inferred.
- [ ] Title and description copied/reconciled with `ZENODO_METADATA_TEMPLATE.md`.
- [ ] Keywords reviewed.
- [ ] License/rights explicitly selected after review; Zenodo default is not accepted accidentally.
- [ ] File visibility deliberately set to public/restricted/embargoed as applicable.
- [ ] Funding/contributors entered only when verified.
- [ ] DOI reserved only if useful for pre-publication metadata; reserved DOI recorded separately from publication status.

## D. Upload identity verification

Upload only the exact candidate objects unless a new candidate is deliberately generated and re-audited:

- [ ] `01-wp9-campaign-raw.tar.gz`
- [ ] `02-wp9-integrity-freeze.tar.gz`
- [ ] `03-publication-and-provenance.tar.gz`
- [ ] `RELEASE_MANIFEST.json`
- [ ] `README_RELEASE.txt`
- [ ] `RELEASE_CHECKSUMS.sha256`

For each object:

- [ ] Filename matches exactly.
- [ ] Local byte count recorded.
- [ ] Local SHA-256 recorded.
- [ ] Upload completes without pending/error state.
- [ ] Uploaded byte size matches local byte size.

Before publication, download or otherwise retrieve the uploaded objects back from the draft when feasible and verify:

- [ ] SHA-256 of each retrieved object matches `RELEASE_CHECKSUMS.sha256`.
- [ ] `RELEASE_MANIFEST.json` source identities are unchanged.
- [ ] Archive object count remains within the planned Zenodo record limits.

## E. Pre-publication preview

- [ ] Preview the record landing page.
- [ ] Confirm title/creator order.
- [ ] Confirm license/rights and file visibility.
- [ ] Confirm no text claims the experiment involved operational spacecraft, RF testing, native spacecraft safe mode, or real operator/contact timing.
- [ ] Confirm P7 is not described as universally superior.
- [ ] Confirm Data Availability wording is accurate for chosen visibility.
- [ ] Confirm reserved DOI, if any, is transcribed exactly.

## F. Publication and post-publication capture

Only after A–E pass:

- [ ] Publish the Zenodo record.
- [ ] Capture published version DOI.
- [ ] Capture concept DOI when provided.
- [ ] Capture permanent record URL.
- [ ] Record publication date and file visibility.
- [ ] Re-open/download published objects and verify checksums again when feasible.
- [ ] Create/finalize the matching GitHub publication tag/release only after the archive identity is known.
- [ ] Update manuscript Data Availability and Code Availability statements.
- [ ] Update `docs/27-wp9-cryptographic-integrity-freeze.md` or a new WP11 closeout record with DOI/checksum identities without rewriting the historical freeze evidence.
- [ ] Update `tracker/work_packages.csv` WP11 to complete only after DOI/checksum capture.

## Stop conditions

Do not publish if:

- any checksum differs;
- the release candidate changed after audit;
- rights/license are uncertain;
- public visibility would expose material identified for restricted handling;
- creator/author metadata is unresolved;
- the record description overstates the experimental boundary;
- the draft files differ from the audited local candidate.

A stop condition should lead to investigation or a new audited release candidate, never silent modification of the frozen WP9 source.