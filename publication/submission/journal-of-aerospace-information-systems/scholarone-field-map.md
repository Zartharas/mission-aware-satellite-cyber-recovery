# JAIS ScholarOne Field Map

**Status:** `AUTHENTICATED_SCHOLARONE_FIELD_LOCK_IN_PROGRESS`

This file separates fields confirmed by current public AIAA guidance from fields read directly from the live JAIS ScholarOne submission workflow. Portal-only requirements are not inferred.

## Publicly confirmed and live-locked submission information

| Area | Verified requirement / live portal label | Paper-1 value/status |
|---|---|---|
| Journal | AIAA Journal of Aerospace Information Systems | Primary target authorized |
| Manuscript type | **Full Paper** — exact authenticated ScholarOne label confirmed 2026-09-04 | **LOCKED: Full Paper** |
| Title | REQUIRED; maximum 12 words | Prepared 12-word JAIS title — PASS |
| Abstract portal entry | OPTIONAL; maximum 200 words | Final 171-word JAIS abstract prepared |
| File count | REQUIRED; minimum 1, maximum 5 | Plan: one Main Document unless live upload screen requires otherwise |
| Total upload size | Maximum 390 MB | Frozen manuscript is well within limit |
| Main Document designation | OPTIONAL on requirements overview | Intended designation for audited `JAIS_MANUSCRIPT.docx`; confirm behavior on upload screen |
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

The requirements overview has resolved high-level required/optional status. The following exact values/options still need to be copied from the production JAIS ScholarOne workflow before final submission freeze:

1. Exact title and abstract entry behavior on Step 1.
2. Exact file-upload behavior/designation workflow on Step 2, including confirmation that the audited Word manuscript should be designated `Main Document`.
3. Exact Subject Index Category list and Paper-1 selection of 1–3 categories on Step 3.
4. Exact affiliation/institution/postal fields for an Independent Researcher on Step 4.
5. Exact submitting-agent and author-verification behavior on Step 4.
6. Exact reviewer-entry fields, conflict instructions, and at least three preferred-reviewer identities on Step 5.
7. Exact opposed-reviewer fields, if used.
8. Exact preferred/opposed editor choices and whether leaving them blank is permitted.
9. Exact Clearance wording and answer choices.
10. Exact Artificial Intelligence-Content wording/options.
11. Exact No-Infringement Statement wording/attestation.
12. Exact Publication History wording/options.
13. Exact AI-Content wording/options.
14. Exact Ethical Standards acknowledgment behavior.
15. Exact Artificial Intelligence-Language wording/options.
16. Exact AI-Language wording/options.
17. Exact AI Confirmation Statement wording/options.
18. Any additional data/code, ethics, prior-publication, open-access, copyright, or rights fields revealed within or after Step 6.
19. Final proof/preview behavior and generated submission PDF checks.
20. Final submission action wording.

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
