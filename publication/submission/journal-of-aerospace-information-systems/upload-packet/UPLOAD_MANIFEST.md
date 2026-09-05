# JAIS Paper 1 Upload Manifest

**Package state:** `CONTENT_READY__SCHOLARONE_FIELD_LOCK_IN_PROGRESS`

This manifest distinguishes files intended for the publisher workflow from internal preparation evidence. It does not authorize publisher submission.

## A. Core publisher submission

| Item | Current source | Status | Initial-submission handling |
|---|---|---|---|
| Final JAIS manuscript | workflow artifact `9962030843` / `JAIS_MANUSCRIPT.docx` | **CONTENT READY** | Upload in ScholarOne Step 2 as **Main Document** |
| Manuscript SHA-256 | `e6a1d5023031296da658e6959fe6dc135d42592094267d06c6d4f7d8a2efc2bc` | **FROZEN** | Verify the exact upload copy against this identity |
| Cover letter | `../cover-letter.md` | **PREPARED / HUMANIZED** | Required in Step 6; paste or upload only through the Cover Letter control |
| Title | `../title-page.md` | **PREPARED** | Entered through ScholarOne; 12-word JAIS title |
| Abstract | `../jais-abstract.md` | **PREPARED** | Entered through ScholarOne; final abstract is 171 words |
| Author metadata | `../title-page.md`, `PORTAL_ENTRY_VALUES.md` | **PREPARED/PARTIAL** | Enter through ScholarOne; exact institution/postal behavior remains to be captured |
| Funding | `PORTAL_ENTRY_VALUES.md` | **PREPARED** | No external funding |
| Competing interests | `PORTAL_ENTRY_VALUES.md` | **PREPARED** | No competing financial or non-financial interests |
| AI disclosure | `../ai-disclosure.md` | **PREPARED / HUMANIZED / TRANSPARENT** | In-manuscript disclosure retained; reconcile exact Step-6 AI questions |
| Preferred reviewers | none selected | **REQUIRED / PENDING** | Minimum three; select only after conflict and field review |
| Rights/clearance attestations | research record summarized in portal sheet | **REQUIRED / PENDING EXACT WORDING** | Complete only against exact ScholarOne/AIAA language |

## B. Final manuscript audit identity

Generation commit: `6e0f801fc8c8ac2a498a7cac9234bbbfa0ba7bc3`  
JAIS export workflow run: `33941696440` - PASS  
Workflow artifact ID: `9962030843`  
Artifact ZIP SHA-256: `9b85281ed7a1a5eeb190bb72d61667128e30334d3913a46c3720745f09855685`  
Final DOCX SHA-256: `e6a1d5023031296da658e6959fe6dc135d42592094267d06c6d4f7d8a2efc2bc`

Final measured state:

- title: 12 / 12 words;
- abstract: 171 words;
- text excluding table-cell text: 7,058 words;
- AIAA table-equivalent allowance: 1,250 words;
- estimated AIAA equivalent length: 8,308 / 12,000;
- numbered references: 20;
- unresolved citations: none;
- scientific/export gate: PASS;
- AIAA reference gate: PASS;
- submission-facing style gate: PASS;
- final manuscript em-dash count: 0;
- tracked changes: none;
- Word comments: none;
- accessibility audit: 0 high, 0 medium, 0 low findings;
- final 25-page Word visual QA: PASS.

Full identity/audit record: `MANUSCRIPT_CONTENT_READY.md`.

## C. ScholarOne Step 2 upload decision

The authenticated Step-2 instructions state that an original submission should provide either a PDF or Word DOCX containing all main manuscript content, including figures and tables, and that the main body should be designated **Main Document**. Files uploaded on Step 2 are included in the reviewer proof.

Therefore upload **one file only** on Step 2:

- `JAIS_MANUSCRIPT.docx` -> **Main Document**

Do not upload the cover letter, title-page source, audit reports, workflow ZIP, Zenodo archives, repository evidence, or internal checklists on Step 2.

## D. Figures and tables

The peer-review manuscript contains editable tables. Wide Tables 3-5 use a JAIS-facing compact display generated deterministically from frozen manuscript-facing CSV values. The source CSVs and numerical Results are unchanged.

No separate image upload is planned for the initial submission.

## E. Supplemental material

Current initial-submission decision: **NONE planned by default.**

See `OPTIONAL_SUPPLEMENTAL.md`.

## F. Internal/supporting files - DO NOT UPLOAD BY DEFAULT

The following are preparation/governance evidence and are not journal supplements unless an editor specifically requests them:

- `MANUSCRIPT_CONTENT_READY.md`
- `../README.md`
- `../live-requirements-2026-09-04.md`
- `../scholarone-live-requirements-2026-09-04.md`
- `../submission-checklist.md`
- `../scholarone-field-map.md`
- `../venue-fit.md`
- generated audit JSON/CSV files
- GitHub Actions export ZIPs
- internal repository audit records
- raw or frozen experiment evidence already published through Zenodo
- internal claim-traceability or release-gate files

## G. Remaining requirements before `SUBMISSION_READY`

The scientific/manuscript-content items are closed. The package may move to `SUBMISSION_READY` only after:

1. complete authenticated JAIS ScholarOne field lock;
2. selection of 1-3 Subject Index Categories;
3. verification of author/institution controls;
4. entry and conflict review of at least three preferred reviewers;
5. exact Step-6 clearance, publication-history, no-infringement, ethics, and AI responses;
6. final ScholarOne proof/preview verification;
7. final repository/package snapshot freeze; and
8. separate explicit author authorization to submit.
