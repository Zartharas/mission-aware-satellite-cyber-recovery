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
