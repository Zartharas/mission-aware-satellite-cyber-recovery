# Paper 4 — IJSCCN Local-Private Submission Privacy Gate

**Date:** 2026-09-21  
**Status:** `PRIVACY_HARDENING_IMPLEMENTED_ON_BRANCH__MERGE_PENDING__PUBLISHER_SUBMISSION_NOT_AUTHORIZED`

## Purpose

This gate implements the author's requirement that photographs, private contact metadata, and personalized upload-ready submission documents remain only on the author's local workstation and are not committed to or generated as private-data-bearing GitHub artifacts.

## Active privacy boundary

Tracked repository files may contain scientific content, public-safe package structure, and placeholder author metadata only.

The following paths are local-only and ignored by Git:

- `publication/Paper_4_Study_8/IJSCCN/_local_private/`
- `publication/Paper_4_Study_8/IJSCCN/_local_submission/`

The local-private directory is the only authorized repository-local location for:

- the recent author photograph;
- corresponding-author email;
- detailed author location/postal information;
- telephone, if a publisher field requires it;
- other private publisher-submission metadata.

The local-submission directory is the only authorized repository-local location for personalized upload-ready documents.

## GitHub Actions boundary

GitHub Actions builds only a public-safe QA package using placeholder author metadata. It must not receive or upload the ignored local-private or local-submission directories.

The public-safe CI artifact is not a publisher-upload package.

## Scientific integrity

This privacy change does not modify:

- Study 8 frozen science;
- Study 8E frozen science;
- TRACE-002;
- corrected Results-002;
- any endpoint, result, figure value, or claim boundary;
- Paper 4 / Paper 5 scientific separation.

## Historical artifact note

The earlier frozen package artifact produced before this privacy gate was generated from source files that included personalized author contact metadata. It is retained only as historical package provenance and is no longer authorized as the submission artifact.

Because the available GitHub connector does not expose artifact deletion, this gate does not claim that earlier Actions artifacts or Git history have been erased. A separate history/artifact-removal action is required if complete retrospective removal is desired.

## Current gate

1. merge the privacy-hardening PR only after explicit author authorization;
2. copy private author metadata and the photograph into the ignored local-private directory;
3. run and visually inspect the local personalized build;
4. keep Wiley portal entry and publisher submission behind separate explicit authorization.
