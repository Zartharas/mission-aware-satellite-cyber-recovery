# Post-Publication Repository Cleanup and Backup Record

**Status:** cleanup candidate prepared after Zenodo publication and repository publication closeout  
**Published dataset:** Zenodo v1.0.0 — <https://doi.org/10.5281/zenodo.22181540>  
**Pre-cleanup repository commit:** `eab939b1ff440899853a04d80e31a6abf011c6ea`  
**Pre-cleanup repository tree:** `7d2a2b6d146a25d250f7bc17ab6ef608da0b85cb`  
**Backup branch:** `archive/pre-journal-cleanup-eab939b`

## Purpose

After publication of the DOI-bearing research-data/reproducibility record, the repository was reviewed for presentation clutter, obsolete local-development helpers, generated local artifacts, and scripts that could be mistaken for supported public entry points.

The cleanup is deliberately conservative. It does not rewrite frozen evidence, statistical outputs, publication figures/tables, experiment configurations, source implementation, or the published Zenodo files.

## Backup boundary

Before any active-branch cleanup, the exact publication-ready repository state was preserved as the GitHub branch:

`archive/pre-journal-cleanup-eab939b`

That branch points to:

`eab939b1ff440899853a04d80e31a6abf011c6ea`

Therefore every tracked file removed by this cleanup remains recoverable from:

1. the backup branch;
2. normal Git history; and
3. the published repository's commit graph.

The Zenodo v1.0.0 archive is separate and is not modified by this repository cleanup.

## Tracked-file cleanup

Four high-confidence obsolete/orphaned helpers are removed from the active branch:

### `scripts/bootstrap_macos.sh`

Reason for removal:

- contained an old researcher-specific absolute macOS development path;
- attempted legacy repository/bootstrap behavior no longer appropriate for a public repository;
- superseded by the portable setup instructions in `docs/REPRODUCIBILITY_GUIDE.md` and `CONTRIBUTING.md`;
- no current repository reference was found during cleanup review.

### `scripts/benign_plaintext_transport_relay.py`

Reason for removal:

- belonged to the earlier WP4 benign transport-observability diagnostic branch;
- that diagnostic branch was explicitly discontinued after the accepted bounded runtime-preflight evidence was sufficient for the paper;
- it is not part of the current public reproduction path;
- no current repository reference was found during cleanup review.

### `scripts/prepare_runtime_radio_config.py`

Reason for removal:

- was a WP4 radio-interface preparation helper for the discontinued diagnostic branch;
- it is not required by the published setup/reproduction path;
- no current repository reference was found during cleanup review.

### `scripts/verify_benign_ground_probe.sh`

Reason for removal:

- was an obsolete verifier for the earlier WP4 diagnostic path;
- it referenced `scripts/benign_ground_probe.py`, which is absent from the publication baseline;
- the verifier therefore cannot serve as a valid current repository entry point;
- no current repository reference was found during cleanup review.

## Files deliberately retained

The cleanup does **not** remove the historical WP5-WP9 scripts simply because the campaign is complete. Those scripts remain valuable as scientific provenance and implementation evidence for the mechanisms used during development, pilot validation, and the frozen experiment campaign.

Retained categories include:

- experiment schema/configuration validation;
- NOS3/Fortytwo preparation and deterministic build tooling;
- bounded nominal runtime preflight and cleanup;
- WP5 event adapters/runtime tests;
- WP6 response-policy mechanism tests;
- WP7 trusted-recovery validation;
- WP8 pilot/preflight tooling;
- WP9 mechanism/campaign tooling;
- WP11 release-candidate preparation and audit tooling;
- `nos3_runtime_material.py` historical runtime support material.

A new `scripts/README.md` classifies supported user-facing entry points versus historical/provenance tooling.

## Git-ignore hardening

`.gitignore` is expanded for local-only material that should not be accidentally committed:

- Python type/lint/test caches and coverage output;
- notebook checkpoints;
- Python package metadata;
- local profiling output;
- local backup directories/files and Git bundles;
- common editor recovery files;
- generated local archive formats (`.tar`, `.tar.gz`, `.tgz`, `.zip`).

Existing exclusions for raw research data, experiment results, runtime evidence, external simulator checkouts, credentials/secrets, and review evidence remain intact.

The ignore rules do not retroactively remove tracked files; they prevent future accidental additions of local/generated material.

## Scientific and publication integrity

This cleanup does not:

- run any WP9 campaign trial;
- create a new scientific observation;
- modify `results/wp9/campaign/`;
- modify the frozen 720-VALID statistical membership;
- alter the 9 retained INVALID attempts;
- alter campaign/integrity checksums;
- modify the DOI-bearing Zenodo v1.0.0 files;
- change manuscript results, figures, tables, or conclusions;
- change the approved MIT + CC BY 4.0 split-license model.

The publication baseline remains recoverable at `eab939b1ff440899853a04d80e31a6abf011c6ea`, and the archived dataset remains identified by version DOI `10.5281/zenodo.22181540`.

## Local-machine cleanup boundary

GitHub cannot see ignored/untracked files on a researcher's local workstation. Local cleanup should therefore be performed separately after creating a local Git bundle and/or filesystem backup. In particular, raw campaign evidence should not be deleted merely because it is ignored by Git; preserve a verified backup before reclaiming local storage.

The recommended local audit is:

1. confirm a clean tracked worktree;
2. create a Git bundle of all refs;
3. inventory untracked and ignored files;
4. distinguish regenerable caches/build output from unique evidence;
5. delete only regenerable material after backup verification.

No local-machine deletion is authorized by this repository-side cleanup record alone.
