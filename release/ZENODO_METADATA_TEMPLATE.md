# Zenodo Metadata Template — WP11

**Status:** Template only — do not treat placeholders as publication metadata  
**Archive target:** Zenodo  
**Record publication:** Pending

## Record title

Candidate:

> Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Evidence Constraints — Research Data and Reproducibility Artifacts

Final wording may be adjusted to the selected journal/article title, but the archive should remain identifiable as the data/reproducibility object rather than the journal article itself.

## Resource type

**Candidate:** Dataset or Other/Research data, depending on final Zenodo field options and release scope.

Do not misclassify the record as the journal article if it primarily contains campaign data, integrity evidence, and publication/reproducibility artifacts.

## Publication date

`<ZENODO_PUBLICATION_DATE>`

Use the actual date on which the Zenodo draft is published.

## Creators

**USER INPUT REQUIRED.** Use the final scholarly author/creator list and order approved for the archive.

For each creator capture:

- family name;
- given name(s);
- ORCID if applicable and verified;
- affiliation(s) if applicable and verified.

Do not infer creators from Git commit authorship.

## Description

Candidate description:

> This research object supports a controlled software-in-the-loop study of satellite cyber response and trusted recovery. The release preserves the frozen WP9 campaign evidence, the publication-grade cryptographic integrity freeze, and the manuscript-facing aggregate/provenance artifacts used for WP10 analysis and reporting. The final statistical population contains 720 VALID observations from 24 frozen cells and 30 campaign seeds; nine additional INVALID attempts are retained as provenance but are not members of the statistical analysis. The experiment used a researcher-controlled NOS3/Fortytwo/cFS-based software-in-the-loop environment with synthetic cyber events, policy-visible evidence conditions, and modeled contact behavior. It did not access operational spacecraft or ground stations and did not transmit or interfere with RF. See the included release manifest, checksum file, repository documentation, and associated manuscript for scope and claim boundaries.

Before publication, update this description with the repository tag/commit and article citation if available.

## Keywords

Candidate keywords:

- satellite cybersecurity
- mission-aware cybersecurity
- cyber resilience
- trusted recovery
- spacecraft autonomy
- software-in-the-loop
- NOS3
- cFS
- cyber incident response
- reproducibility
- Pareto analysis

## License / rights

**REVIEW REQUIRED — DO NOT ACCEPT ZENODO'S DEFAULT LICENSE WITHOUT REVIEW.**

Zenodo requires a license field and currently defaults to CC BY 4.0. The release contains mixed artifact classes, so final rights must be chosen after reviewing:

- researcher-authored manuscript/docs/tables/figures;
- raw generated campaign evidence;
- repository/software licenses applicable to code references;
- any third-party content included in the archives;
- any dataset-specific redistribution restrictions.

Final decision:

`<LICENSE_OR_RIGHTS_STATEMENT>`

If multiple licenses/custom rights are necessary, record them explicitly in Zenodo and in the release notes.

## File visibility

Choose only after the local automated audit and manual rights/misuse review:

- `<PUBLIC>`
- `<RESTRICTED>`
- `<RESTRICTED_WITH_EMBARGO_UNTIL_DATE>`

Zenodo record metadata is public even when files are restricted.

If restricted, document access conditions:

`<ACCESS_CONDITIONS>`

## DOI

### Reserved DOI, if created before publication

`<RESERVED_VERSION_DOI>`

A reserved DOI is not evidence that the record has been published.

### Published version DOI

`<VERSION_DOI>`

### Concept DOI

`<CONCEPT_DOI>`

Use the specific version DOI in the manuscript/Data Availability statement for reproducibility. Retain the concept DOI as the identifier for the evolving record family when Zenodo provides it.

## Related identifiers

Populate only when verified:

- GitHub repository/tag URL: `<GITHUB_RELEASE_OR_TAG_URL>`
- manuscript/article DOI: `<ARTICLE_DOI_IF_AVAILABLE>`
- ORCID/project identifiers: `<VERIFIED_IDENTIFIERS>`

Suggested relation for the eventual paper: dataset `isSupplementTo` or other relation supported by the selected metadata model, based on the final article/deposit relationship.

## Version

Candidate initial release version:

`1.0.0`

Do not create a new version solely to fix metadata that Zenodo permits editing on the same record. Use record versioning when the archived files materially change.

## Language

`English`

## Funding

**USER INPUT REQUIRED IF APPLICABLE.**

`<FUNDING / GRANT METADATA OR NONE DECLARED>`

Do not infer grants or funders.

## Contributors

Optional and only if verified:

`<DATA CURATION / SOFTWARE / SUPERVISION / OTHER CONTRIBUTORS>`

Do not infer contributor roles from repository activity.

## Notes before Publish

Before clicking Publish, confirm:

- uploaded filenames and byte sizes match the local candidate;
- uploaded/downloaded SHA-256 checksums match `RELEASE_CHECKSUMS.sha256`;
- final license/rights and visibility choices are deliberate;
- the record title/description do not claim operational spacecraft/RF evidence;
- the version DOI is captured exactly;
- the concept DOI is captured when available;
- the manuscript Data Availability statement is updated only after publication.