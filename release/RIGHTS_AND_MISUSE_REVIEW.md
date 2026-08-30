# WP11 Rights, Privacy, and Misuse Review

**Status:** `REVIEW_REQUIRED_BEFORE_ARCHIVE_PUBLICATION`
**Applies to:** the exact audited WP11 release candidate
**Archive target:** Zenodo
**Publication authorization:** not granted by this document alone

## Purpose

This control records the manual review that must occur after deterministic
release-candidate generation and automated audit, but before any public,
restricted, or embargoed archive publication decision.

The frozen WP9 scientific source must not be edited to satisfy this review.
If a source artifact cannot responsibly or lawfully be distributed, preserve
the frozen source and resolve distribution through access controls or a
separately documented derivative.

## Candidate identity

Complete only after the local WP11 candidate and audit exist.

- Release candidate directory: `<REQUIRED>`
- Repository commit: `<REQUIRED>`
- `RELEASE_CHECKSUMS.sha256` SHA-256: `<REQUIRED>`
- Local audit report: `<REQUIRED>`
- Automated audit status: `<REQUIRED>`
- Review date: `<REQUIRED>`
- Reviewer: `<REQUIRED>`

## Credentials and secrets

Confirm the candidate contains no unintended:

- [ ] passwords;
- [ ] API tokens;
- [ ] access tokens;
- [ ] private cryptographic keys;
- [ ] cloud credentials;
- [ ] SSH credentials;
- [ ] `.env` or equivalent secret stores;
- [ ] authentication cookies/session material;
- [ ] other operational credentials.

Evidence/notes:

`<REQUIRED>`

## Operational privacy

Confirm the candidate does not unintentionally disclose non-public:

- [ ] operational spacecraft identifiers;
- [ ] ground-station identifiers;
- [ ] production network addresses/endpoints;
- [ ] operator identities or account identifiers;
- [ ] mission schedules/contact schedules;
- [ ] partner/customer-sensitive telemetry;
- [ ] internal infrastructure details unrelated to reproducibility.

Evidence/notes:

`<REQUIRED>`

## RF and misuse boundary

Confirm that publication does not provide operational material intended to
enable interference or unauthorized control, including:

- [ ] live RF parameters suitable for interference;
- [ ] operational command credentials;
- [ ] operational TT&C endpoints;
- [ ] non-public exploitation instructions for a real system;
- [ ] instructions materially exceeding the controlled synthetic laboratory
      scope required for scientific reproducibility.

Evidence/notes:

`<REQUIRED>`

## Human-subject boundary

Confirm:

- [ ] no interview transcripts are included;
- [ ] no interview recordings are included;
- [ ] no participant-identifiable human-subject data are included;
- [ ] no consent-restricted qualitative data are included.

Evidence/notes:

`<REQUIRED>`

## Third-party rights

Review every artifact class for redistribution authority.

- [ ] researcher-authored documentation/tables/figures reviewed;
- [ ] generated campaign evidence reviewed;
- [ ] third-party software content reviewed;
- [ ] third-party datasets/data fragments reviewed;
- [ ] external documentation/text reviewed;
- [ ] applicable software/data licenses identified;
- [ ] no license is inferred solely from repository availability;
- [ ] Zenodo license/rights selection matches the actual uploaded content.

Evidence/notes:

`<REQUIRED>`

## Export-control / proprietary / classified boundary

Confirm the candidate contains no material known to be:

- [ ] classified;
- [ ] export-controlled beyond authorized distribution;
- [ ] proprietary and unauthorized for redistribution;
- [ ] contractually restricted;
- [ ] partner-sensitive and unauthorized for redistribution.

Evidence/notes:

`<REQUIRED>`

## Experimental-claim boundary

Confirm archive metadata and included documentation preserve these boundaries:

- [ ] controlled NOS3/Fortytwo/cFS software-in-the-loop study;
- [ ] no operational spacecraft access;
- [ ] no operational ground-station access;
- [ ] no RF transmission/interference experiment;
- [ ] no native spacecraft safe-mode claim;
- [ ] modeled/synthetic timing is not represented as operational timing;
- [ ] raw expected values are not represented as observed measurements;
- [ ] INVALID attempts remain provenance rather than statistical observations.

Evidence/notes:

`<REQUIRED>`

## Access decision

Select exactly one only after all preceding sections are complete.

- [ ] Public files
- [ ] Restricted files
- [ ] Embargoed/restricted until: `<DATE>`
- [ ] Publication blocked pending remediation/review

Access conditions, if restricted:

`<REQUIRED_OR_N/A>`

## Final rights/misuse decision

Decision:

`<APPROVED_FOR_PUBLICATION | APPROVED_WITH_RESTRICTIONS | BLOCKED>`

Rationale:

`<REQUIRED>`

Reviewer:

`<REQUIRED>`

Date:

`<REQUIRED>`

This review does not publish a Zenodo record, reserve a DOI, modify the frozen
campaign, or authorize alteration of scientific evidence.
