# S10-RSEI-001 - G4 author source-use readiness checklist (NOT APPROVED)

**State:** `HOLD`. The sole author authorized preparation of this review, not original source processing. Checkboxes below are intentionally not marked as completed by an assistant's interpretation of a general authorization.

## Completed documentary evidence (not a source-use grant)

- G2 author-approved protocol and separate receipt are pinned to their exact Git commits.
- G3 synthetic-only workflow 44995819254 passed 18 controls, 1,024 selector parity comparisons, three evidence API cases; repository workflow 44995819176 passed.
- Version-specific ESA v1 first-party CC BY 3.0 IGO and OPS-SAT v2 data-inclusive MIT evidence have been located.
- ESA v2 license statement from the dataset authors is recorded in G2; the publicly accessible Zenodo Rights section does not display a license value.
- Hack-A-Sat pinned README's `LICENSE.md` target is absent; `.LICENSE` exists; component-specific rights exceptions remain.

## Requirements before any G4 original-data access or use

- [ ] **G4-01 ESA v2:** Author records release-specific permission/scope, third-party-file exception review, exact versioned creator credits and future derivative publication notices.
- [ ] **G4-02 ESA v1:** If paired sensitivity is used, author separately confirms v1 release rights, acknowledgments and file-family exceptions.
- [ ] **G4-03 OPS-SAT v2:** Author records exact data-inclusive MIT copyright/permission notice plan, the v2 file scope and any third-party exceptions.
- [ ] **G4-04 Hack-A-Sat (secondary only):** Do not process unless author specifically elects to include contest files after resolving actual root `.LICENSE`, missing `LICENSE.md` reference, file-level exceptions and non-flight provenance limits.
- [ ] **G4-05 source identity:** Only after source-use authorization, re-hash the exact original archive/CSV bytes locally and perform complete ESA archive-member integrity checks in a bounded isolated environment. Preserve method, hashes, paths and all source attribution notices.
- [ ] **G4-06 execution decision:** Obtain a separate, explicit author G4 source-use and semantic-adjudication authorization referencing the exact source rights/identity evidence and approved G2/G3 record. A generic continuation statement for G4 *readiness* is insufficient.

## Follow-up sole-author decision package (review completed; checkboxes NOT cleared)

The source-rights review has now supplied an exact v2 ESA manuscript-based license statement, first-party v1 license evidence, an OPS-SAT data-inclusive MIT notice, and the Hack-A-Sat document-link discrepancy. These are **evidence findings**, not a verified absence of all third-party exceptions or approval for source-byte access.

**Proposed G4 rights scope for a later explicit author decision:** local research on **ESA-ADB v2 primary** (three separate mission strata) and **OPS-SAT-AD v2 primary** for descriptive native semantic observability only; **ESA-ADB v1 paired-sensitivity** only after version-specific notices/signoff; **Hack-A-Sat game data excluded from initial G4 execution pending separate path-level review** (without deleting the frozen secondary protocol context). Future publication would share only cited **non-raw semantic classifications and aggregate descriptive results**, not rehost the original archives/CSV files. The full license obligations and any source-file exceptions must still be reviewed.

| Future decision | Evidence now available | Author decision status |
|---|---|---|
| `R01`: ESA v2 intended use and notice | v2 author statement, official DOI/creator and MD5 metadata, CC BY 3.0 IGO terms | `PENDING_EXPLICIT_SIGNOFF_AND_FILE_RIGHTS_REVIEW` |
| `R02`: ESA v1 paired comparison | Official first-party `LICENSE`, README ↔ exact v1 DOI | `PENDING_IF_USED` |
| `R03`: OPS-SAT v2 intended use and notice | v2 DOI/creator/files, data-inclusive MIT text and license MD5 | `PENDING_EXPLICIT_SIGNOFF_AND_EXCEPTIONS` |
| `R04`: Hack-A-Sat secondary | README + mismatched license filename + real `.LICENSE` | `BLOCKED_IF_USED` |
| `R05`: actual original-file integrity | Earlier user-reported checksums, not freshly checked | `PENDING_NARROW_LOCAL_BYTE_ACCESS_AUTHORIZATION_AND_EXECUTION` |
| `R06`: G4 scientific execution | G2 internal freeze, G3 PASS, G4 fail-closed preflight PASS | `NOT_AUTHORIZED` |

**Explicit separation:** This turn authorizes checklist/right-scope **review and evidence documentation only**. It does not select `APPROVE_RIGHTS_SCOPE`, `AUTHORIZE_LOCAL_SOURCE_CHECKSUMS`, or `AUTHORIZE_G4_SCIENTIFIC_EXECUTION`. No checkbox earlier in this document is marked complete and the existing `G4_READINESS_HOLD` is unchanged.

## Recorded sole-author G4-SCOPE-POLICY-01 decision (approved policy only)

**Decision accepted:** The author approved the proposed **local, non-raw descriptive intended-use and attribution plan** on 2026-11-22 (UTC date precision; exact reply “yes, I authorize”). This applies to ESA-ADB v2's three separate mission strata and OPS-SAT-AD v2 as the fourth primary stratum; ESA-ADB v1 remains paired-sensitivity-only; Hack-A-Sat 4 remains barred from initial source processing until separately assessed. This is **not** approval for file-level rights exceptions, original-file access, data processing, redistribution, or manuscript submission.

**Plan commitments:** exact versioned dataset DOI and creator credit, license link and changes/no-endorsement notices for licensed ESA material, complete KP Labs MIT copyright and permission notice if applicable, relevant associated-publication citations, and no raw telemetry dissemination.

**Remaining author and technical decisions (all unchanged):** `G4-01/G4-02/G4-03` rights file-level and attribution-implementation signoff; `G4-04` Hack-A-Sat secondary file licenses if ever included; `G4-05` separately authorized, resource-bounded local checksum/full archive integrity validation; `G4-06` explicit G4 source access and scientific execution authorization. **All six original checkbox requirements above remain unchecked.**

**Decision flags:** `INTENDED_USE_ATTRIBUTION_POLICY_APPROVED=true`; `FINAL_SOURCE_RIGHTS_CLEARED=false`; `LOCAL_INTEGRITY_CHECK_AUTHORIZED=false`; `G4_EXECUTION_AUTHORIZED=false`; `PR_MERGE_AUTHORIZED=false`.

## Additional scientific safeguards

- [ ] Make a separately auditable, version-pinned G3 result-freeze receipt or justify why the existing immutable workflow run and artifact are adequate. Do not rewrite G2.
- [ ] Retain four descriptive strata × eight variables = 32 classification slots, with no pooled independent spacecraft effect estimate.
- [ ] Preserve `AMBIGUOUS`, `ABSENT`, `UNKNOWN` and `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` distinctions.
- [ ] Record local testing environment and exact used dataset version/DOI, provenance, checksum algorithm, integrity scope, access restrictions and any excluded file.
- [ ] Confirm no raw telemetry will enter a public GitHub branch, GitHub Actions log, AI connector, external service, or journal supplement without distinct permission and notices.

**Decision field:** `SOLE_AUTHOR_G4_SOURCE_USE_APPROVAL = NOT_PROVIDED`.
**Real source processing:** `NOT_AUTHORIZED`.
**G4 scientific execution:** `NOT_AUTHORIZED`.
**PR merging:** `NOT_AUTHORIZED`.

**Review disposition:** G4 readiness documentation complete for the presently available metadata, but the **gate remains HOLD**.
