# Zenodo Metadata Record — WP11

**Status:** `PUBLISHED — VERSION 1.0.0`  
**Archive target:** Zenodo  
**Publication date:** 2026-08-30  
**Historical note:** This file began as the pre-publication metadata template. The resolved fields below now record the published outcome.

## Record title

> Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Evidence Constraints — Research Data and Reproducibility Artifacts

## Resource type

**Dataset**

The record represents campaign data, integrity evidence, and publication/reproducibility artifacts. It is not the journal article itself.

## Creator

- **Aman Singh**
- affiliation: **Independent Researcher**
- ORCID: <https://orcid.org/0009-0008-9752-3743>
- contact person: yes

No additional contributors were declared for this archive record.

## Description of record scope

The published research object provides data, integrity evidence, and reproducibility artifacts supporting a controlled software-in-the-loop study of mission-aware satellite cyber response and trusted recovery under contact and evidence constraints.

The archived experiment contains 720 VALID observations covering 24 frozen experimental cells across 30 campaign seeds. Nine additional INVALID attempts are retained as provenance and are not members of the statistical analysis.

The study was conducted in a researcher-controlled NOS3/Fortytwo/cFS-based software-in-the-loop environment using synthetic cyber events, synthetic mission states and synthetic telemetry, policy-visible evidence conditions, and modeled communication-contact behavior. The experiment did not access operational spacecraft or ground stations, did not use operational credentials or proprietary mission telemetry, and did not transmit, interfere with, jam, or spoof radio-frequency communications.

The release includes the frozen raw campaign evidence, publication-grade cryptographic integrity freeze, manuscript-facing publication/provenance artifacts, release manifest, and cryptographic checksums. The archived release candidate was generated from repository commit `eb3be7aaaed9e60c54843d9a7b9ace1a0fa5812e`. Responsible-release closeout before external publication was recorded at `00acf169afe83fa433b10f88d53fa3228e5de103`.

The statistical and scientific claim boundaries documented in the manuscript and provenance records remain authoritative. The work was conducted independently and received no external funding.

## Keywords

- satellite cybersecurity
- mission-aware cybersecurity
- spacecraft cybersecurity
- cyber resilience
- trusted recovery
- satellite cyber incident response
- software-in-the-loop
- NOS3
- Core Flight System
- cFS
- spacecraft autonomy
- cyber-physical systems
- reproducible research
- mission resilience

## License / rights

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

Copyright statement recorded in Zenodo:

`Copyright © 2026 Aman Singh`

This license applies to the published research dataset/archive as recorded by Zenodo. It does not relicense separately obtained third-party software merely referenced by the project.

## Visibility

**Public**

The exact six-object candidate had already received the responsible-release disposition:

- `PUBLIC_FILES`
- `APPROVED_FOR_PUBLICATION`

## DOI

### Version DOI

`10.5281/zenodo.22181540`

<https://doi.org/10.5281/zenodo.22181540>

### Concept DOI

`10.5281/zenodo.22181539`

<https://doi.org/10.5281/zenodo.22181539>

Use the **version DOI** in the manuscript/Data Availability statement when reproducibility depends on the exact v1.0.0 file set.

## Related work

GitHub repository:

<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery>

Zenodo relation recorded as the dataset being **supplemented by** the software repository.

A future journal-article DOI should be added as a related work when it exists.

## Version

`1.0.0`

A new archive-file version should be created if the archived files materially change. Metadata-only corrections should follow Zenodo's supported metadata-editing behavior without changing the frozen v1.0.0 file identities.

## Language

`English`

## Funding

**No external funding.**

No grant/award metadata were entered.

## Contributors

None declared for the archive record.

## Exact published files

1. `01-wp9-campaign-raw.tar.gz`
2. `02-wp9-integrity-freeze.tar.gz`
3. `03-publication-and-provenance.tar.gz`
4. `README_RELEASE.txt`
5. `RELEASE_CHECKSUMS.sha256`
6. `RELEASE_MANIFEST.json`

See [`../docs/40-zenodo-publication-closeout.md`](../docs/40-zenodo-publication-closeout.md) for SHA-256 identities and publication closeout.

## Historical pre-publication rules retained

The following governance remains applicable to any future archive version:

- do not infer creators from Git commit authorship;
- do not accept a default license without checking the actual release content;
- uploaded filenames, sizes, and checksums must match the audited candidate;
- archive metadata must preserve the controlled SIL / no-operational-spacecraft / no-RF claim boundary;
- use a version DOI for exact reproducibility;
- do not mutate a previously audited candidate and continue to call it the same object;
- a new file set requires a new candidate, audit, rights/misuse review, and archive-version decision.
