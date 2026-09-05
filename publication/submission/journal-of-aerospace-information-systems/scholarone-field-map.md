# JAIS ScholarOne Field Map

**Status:** `AUTHENTICATED_SCHOLARONE_FIELD_LOCK_IN_PROGRESS`

This file separates fields confirmed by current public AIAA guidance from fields read directly from the live JAIS ScholarOne submission workflow. Portal-only requirements are not inferred.

## Publicly confirmed and live-locked submission information

| Area | Verified requirement / live portal label | Paper-1 value/status |
|---|---|---|
| Journal | AIAA Journal of Aerospace Information Systems | Primary target authorized |
| Manuscript type | **Full Paper** — exact authenticated ScholarOne label confirmed 2026-09-04 | **LOCKED: Full Paper** |
| Title | REQUIRED; maximum 12 words | Prepared 12-word JAIS title; live counter shows **12 OUT OF 12 WORDS** |
| Abstract portal entry | OPTIONAL; maximum 200 words | Final 171-word JAIS abstract entered; live counter shows **171 OUT OF 200 WORDS** |
| Virtual Collection | Live Step-1 selector present; portal says Virtual Collections designated as “invited” are by invitation only | No collection has been identified for Paper 1; leave unselected unless a specific applicable collection is intentionally chosen |
| Plain Language Summary | Live Step-1 text area present; described as a short, non-technical/lay summary that may be made available through Kudos after publication | No required asterisk observed in captured Step-1 screen; optionality/validation to be confirmed by save/continue behavior |
| File count | REQUIRED; minimum 1, maximum 5 | **LOCKED: upload one manuscript file for Paper 1** |
| Total upload size | Maximum 390 MB | Frozen manuscript is well within limit |
| Original-submission manuscript format | Live Step-2 instructions allow either a PDF or Word DOCX containing all main manuscript content, including figures and tables | **LOCKED: use audited Word DOCX** |
| Main Document designation | Live Step-2 instructions explicitly state that the main body of the manuscript should be designated `Main Document` | **LOCKED: `JAIS_MANUSCRIPT.docx` → Main Document** |
| Reviewer-proof inclusion | Live Step-2 instructions state that all files listed on the upload page will be included in the proofs sent to reviewers | Upload only the audited manuscript on Step 2; do not place internal audit/support files here |
| Image | OPTIONAL file designation | None planned separately |
| TeX/LaTeX Suppl File | OPTIONAL file designation | None planned |
| Supplemental Materials | OPTIONAL file designation | None planned by default |
| Updated Copyright Form | OPTIONAL file designation | None planned unless requested |
| Subject Index Category | REQUIRED; minimum 1, maximum 3; select from list | Taxonomy/selection pending live Attributes screen |
| Authors | REQUIRED; at least one | Aman Kumar Singh; sole author |
| Submitting Agent | Enabled | Exact behavior pending live Authors & Institutions screen |
| ORCID for Submitting Author | OPTIONAL | 0009-0008-9752-3743 available |
| Preferred Reviewers | REQUIRED; minimum 3 | Must select at least three conflict-checked reviewers |
| Opposed Reviewers | OPTIONAL | None assumed; live field available |
| Preferred Editors | OPTIONAL | None assumed; live field available |
| Opposed Editors | OPTIONAL | None assumed; live field available |
| Cover Letter | REQUIRED; text entry or file upload | JAIS cover letter prepared |
| Funding Information | OPTIONAL | No external funding |
| Clearance | REQUIRED | Exact wording/options pending |
| Artificial Intelligence-Content | REQUIRED | Exact wording/options pending; disclosure required |
| No-Infringement Statement | REQUIRED | Exact wording/options pending |
| Publication History | REQUIRED | Exact wording/options pending; ProQuest relationship must be handled transparently if relevant |
| AI-Content | REQUIRED | Exact wording/options pending |
| Ethical Standards acknowledgment | REQUIRED | Exact portal acknowledgment behavior pending |
| Artificial Intelligence-Language | REQUIRED | Exact wording/options pending |
| AI-Language | REQUIRED | Exact wording/options pending |
| AI Confirmation Statement | REQUIRED | Exact wording/options pending |

### Authenticated ScholarOne requirements evidence

The live `Full Paper` requirements page captured on 2026-09-04 is recorded in:

`scholarone-live-requirements-2026-09-04.md`

Authenticated JAIS ScholarOne manuscript-type choices displayed:

- Full Paper
- Technical Note
- Technical Comment
- Survey Paper
- Lecture
- History of Key Technologies
- Announcement
- Introduction

Paper 1 uses **Full Paper**.

### Live Step-1 evidence — 2026-09-04

The authenticated `Step 1: Type, Title, & Abstract` screen showed:

- Title field with Paper-1 target title populated and counter `12 OUT OF 12 WORDS`.
- A red validation message `Title is missing.` remained visible despite the populated 12-word value. This is recorded as a portal validation-state anomaly; the title content itself matches the locked target title and word limit. Re-trigger field validation before advancing.
- Abstract field populated with the final JAIS abstract and counter `171 OUT OF 200 WORDS`.
- A Virtual Collection selector with help text stating that Virtual Collections previously were called Special Issue/Special Section and that collections designated “invited” are by invitation only.
- A Plain Language Summary field with help text describing a short, non-technical or lay summary that may be made available through Kudos after publication.

### Live Step-2 evidence — 2026-09-04

The authenticated `Step 2: File Upload` screen showed:

- Validation notice that the minimum number of files has not yet been uploaded.
- For an **original submission**, the portal instructs the author to provide either a **PDF or Word DOCX** containing all main manuscript content, including figures and tables.
- The portal asks the author to choose a file designation that best describes each upload.
- The instructions explicitly state that the main body of the manuscript should be designated **`Main Document`**.
- Five upload slots are visible, consistent with the previously captured 1–5-file limit.
- The portal states that **all files listed on this page will be included in the proofs sent to reviewers**.

Paper-1 upload decision:

- Upload exactly one file: `JAIS_MANUSCRIPT.docx`.
- Designate it **Main Document**.
- Use frozen visual-QA SHA-256 `30910535075c3c8d13f501d721e46dd8537774c2d366ca858cdd71222d9edf64`.
- Do not upload the audit ZIP, audit reports, repository governance files, title-page source, cover letter, Zenodo evidence, or supplemental material on Step 2.
- Cover letter remains for Step 6 where ScholarOne explicitly requests it.

## Manuscript metadata prepared

| Field concept | Prepared value |
|---|---|
| JAIS title | Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints |
| Authoritative source title | Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints: Two Controlled Software-in-the-Loop Studies |
| JAIS abstract | Final 171-word one-paragraph, third-person target abstract in `jais-abstract.md` |
| Candidate keywords | satellite cybersecurity; mission-aware cybersecurity; cyber resilience; trusted recovery; software-in-the-loop; cyber incident response |
| Funding | No external funding |
| Competing interests | No competing financial or non-financial interests |
| Data availability | Separate Study-1 and Study-2 Zenodo archives documented in manuscript |
| Code availability | Public GitHub repository documented in manuscript |
| Human participants | None |
| Operational/classified data | None |
| Prior dissertation relationship | ProQuest relationship disclosed transparently |
| Artificial-intelligence use | Full target-specific disclosure in `ai-disclosure.md` |
| Publisher manuscript | `JAIS_MANUSCRIPT.docx`, frozen visual-QA SHA-256 `30910535075c3c8d13f501d721e46dd8537774c2d366ca858cdd71222d9edf64` |

## Live-portal field-level capture remaining

The requirements overview and Steps 1–2 have resolved manuscript type, title/abstract counters, and the manuscript-upload designation. The following exact values/options still need to be copied from the production JAIS ScholarOne workflow before final submission freeze:

1. Confirm Step 2 successfully accepts the exact audited `JAIS_MANUSCRIPT.docx` as `Main Document` and displays the expected uploaded filename/designation.
2. Exact Subject Index Category list and Paper-1 selection of 1–3 categories on Step 3.
3. Exact affiliation/institution/postal fields for an Independent Researcher on Step 4.
4. Exact submitting-agent and author-verification behavior on Step 4.
5. Exact reviewer-entry fields, conflict instructions, and at least three preferred-reviewer identities on Step 5.
6. Exact opposed-reviewer fields, if used.
7. Exact preferred/opposed editor choices and whether leaving them blank is permitted.
8. Exact Clearance wording and answer choices.
9. Exact Artificial Intelligence-Content wording/options.
10. Exact No-Infringement Statement wording/attestation.
11. Exact Publication History wording/options.
12. Exact AI-Content wording/options.
13. Exact Ethical Standards acknowledgment behavior.
14. Exact Artificial Intelligence-Language wording/options.
15. Exact AI-Language wording/options.
16. Exact AI Confirmation Statement wording/options.
17. Any additional data/code, ethics, prior-publication, open-access, copyright, or rights fields revealed within or after Step 6.
18. Final proof/preview behavior and generated submission PDF checks.
19. Final submission action wording.

## Capture rule

For every live field, record:

- exact field label;
- exact help text when material;
- required versus optional status;
- allowed values/dropdown choices;
- Paper-1 proposed response;
- evidence screenshot or portal note where useful;
- whether the response is scientific, administrative, legal/rights, or editorial metadata.

Do not enter an institutional-review identifier, grant number, reviewer identity, conflict, classification authority, postal code, or other factual value unless it is supported by the research record or supplied/approved by the author.

## Submission stop rule

Opening, inspecting, and completing draft ScholarOne fields is authorized for this pre-submission phase. Do not press the final action that transmits the manuscript as a completed publisher submission until the submission-ready package is frozen and separate explicit authorization is given.
