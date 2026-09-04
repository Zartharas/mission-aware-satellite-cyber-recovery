# JAIS Paper 1 Upload Manifest

**Package state:** `CONTENT_READY__SCHOLARONE_FIELD_LOCK_PENDING`

This manifest distinguishes files intended for the publisher workflow from internal preparation evidence. It does not authorize publisher submission.

## A. Core publisher submission

| Item | Current source | Status | Initial-submission handling |
|---|---|---|---|
| Final JAIS manuscript | workflow artifact `9949926197` / `JAIS_MANUSCRIPT.docx` | **CONTENT READY** | Core upload after exact ScholarOne file designation is confirmed |
| Manuscript SHA-256 | `30910535075c3c8d13f501d721e46dd8537774c2d366ca858cdd71222d9edf64` | **FROZEN** | Verify local upload copy against this identity |
| Cover letter | `../cover-letter.md` | **PREPARED** | Upload or paste only as ScholarOne requests |
| Title | `../title-page.md` | **PREPARED** | Enter through ScholarOne; 12-word JAIS title |
| Abstract | `../jais-abstract.md` | **PREPARED** | Enter through ScholarOne; final abstract is 171 words |
| Author metadata | `../title-page.md`, `PORTAL_ENTRY_VALUES.md` | **PREPARED/PARTIAL** | Enter through ScholarOne; exact postal fields remain portal-dependent |
| Funding | `PORTAL_ENTRY_VALUES.md` | **PREPARED** | No external funding; enter exact portal response |
| Competing interests | `PORTAL_ENTRY_VALUES.md` | **PREPARED** | No competing financial or non-financial interests |
| AI disclosure | `../ai-disclosure.md` | **PREPARED** | In-manuscript disclosure retained; reconcile exact ScholarOne field |
| Suggested reviewers | none selected | **PENDING LIVE REQUIREMENT** | Select only after exact count/rules are confirmed |
| Rights/clearance attestations | research record summarized in portal sheet | **PENDING LIVE WORDING** | Complete only against exact ScholarOne/AIAA language |

## B. Manuscript audit identity

Generation commit: `506c3d26d812709efec86c856514d541343c0b57`  
JAIS export workflow run: `33907150553` — PASS  
Repository validation workflow run: `33907154052` — PASS  
Artifact ZIP SHA-256: `8f8171f4f2619595631829b5c17c58a8e88cacbe9604e05413562181d53a213f`

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
- 25-page CI-generated Word visual QA: PASS.

Full identity/audit record: `MANUSCRIPT_CONTENT_READY.md`.

## C. Figures and tables

The peer-review manuscript contains editable tables. Wide Tables 3–5 use a JAIS-facing compact display generated deterministically from the frozen manuscript-facing CSV values. The source CSVs and numerical Results are not changed.

Separate production-grade artwork is not required by this staging packet unless the authenticated ScholarOne workflow requests it or the manuscript is accepted.

## D. Supplemental material

Current initial-submission decision: **NONE planned by default.**

See `OPTIONAL_SUPPLEMENTAL.md`.

## E. Internal/supporting files — DO NOT UPLOAD BY DEFAULT

The following are preparation/governance evidence and are not journal supplements unless an editor specifically requests them:

- `MANUSCRIPT_CONTENT_READY.md`
- `../README.md`
- `../live-requirements-2026-09-04.md`
- `../submission-checklist.md`
- `../scholarone-field-map.md`
- `../venue-fit.md`
- generated audit JSON/CSV files
- internal repository audit records
- raw or frozen experiment evidence already published through Zenodo
- internal claim-traceability or release-gate files

## F. Remaining requirements before `SUBMISSION_READY`

The scientific/manuscript-content items below are already closed: final export, AIAA title/abstract/format, citation-order conversion, DOI/reference audit, equivalent-word audit, Study-1 claim boundary, Study-2 claim boundary, cross-study non-pooling, Study-8 exclusion, AI-disclosure inclusion, archive identities, repository validation, and Word visual QA.

The package may move to `SUBMISSION_READY` only after:

1. authenticated live JAIS ScholarOne field/designation lock;
2. reconciliation of exact article type, classifications/keywords, author/affiliation fields, reviewers, declarations, data/code, ethics/rights, and upload designations;
3. verification that the local upload copy matches the frozen manuscript SHA-256;
4. final repository/package snapshot freeze against the locked portal schema; and
5. separate explicit author authorization to submit.
