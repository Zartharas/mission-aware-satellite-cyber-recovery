# Paper 3 / IJCIP R3 — final pre-submission evidence and unresolved-gate audit

**Audit date:** 2026-10-20  
**Scope:** Paper 3 as a distinct full research manuscript synthesizing Study 7 (`S7-LSO-001`) and separately frozen Study 7E (`S7E-AERC-001`). No mixed population or third study is claimed.  
**Authority:** live `main` `1590fb97c854b4c60aae2fcb105cbc511e10043f`; separate draft PR #168 at `375aa5bc5808ddace8bb124df73eb184a61b9765`; stacked draft PR #223 at `77242e95a3b121ff116aec668f67cf9f7c8ac6d7` immediately before this audit addition. Draft PR #222 remains separate.  
**Decision:** `MANUSCRIPT_EVIDENCE_REVIEW_PASSED__PUBLISHER_SPECIFIC_AND_AUTHOR_GATE_OPEN__NOT_SUBMISSION_AUTHORIZED`.

## Publisher evidence — confirmed, provisional, blocked

| Item | Level of confirmation | Consequence |
|---|---|---|
| IJCIP publisher and scientific scope | **Official Elsevier journal profile, verified 2026-10-20**: https://shop.elsevier.com/journals/international-journal-of-critical-infrastructure-protection/1874-5482 | The journal explicitly includes security principles, engineering techniques, critical-infrastructure continuity, and infrastructure interdependencies. Paper 3 addresses a possible space-enabled infrastructure assurance mechanism, but has not measured cross-sector effects. Scope fit is arguable, not guaranteed. |
| Journal-specific Guide for Authors | **Blocked:** https://www.sciencedirect.com/journal/international-journal-of-critical-infrastructure-protection/publish/guide-for-authors returned HTTP 403 in independent web review | Do not assert any journal-specific rule, file classification, peer-review model or length as officially established. Obtain accessible PDF/screenshot or authorized portal display before final upload. |
| Research article, 250-word abstract, 10,000-word length, at most six keywords, numbered references | **Secondary-source indications only:** https://scispace.com/templates/international-journal-of-critical-infrastructure-protection-template-b02ppwd9iz6wxjg and https://scraiber.com/journals/international-journal-of-critical-infrastructure-protection | R3 is preliminarily compatible. These sources are not Elsevier and must never silently become journal-specific authority. |
| Editorial Manager submission flow | **Elsevier general guidance:** https://www.elsevier.com/researcher/author/login-to-editorial-manager and https://service.elsevier.com/app/answers/detail/a_id/8000/supporthub/assessment-builder/ | Use only the actual Submit Your Article entry on the journal site. Do not assume the precise submission system, reviewer model, or required upload slot list. |
| General Elsevier AI, declaration, artwork and highlights guidance | **Publisher-wide supporting guidance**, not a substitute for IJCIP Guide | Retain substantive research-methods and writing/figure-code AI declarations; confirm portal disclosures and whether figures should be uploaded separately. |

## Exact research boundary — not subject to editorial optimization

- Study 7 frozen `S7-LSO-001`: 1,033 modeled observations (512 A + 512 B + 9 C), with the exact information-sufficiency/correlated-corroboration limits retained.
- Study 7E `S7E-AERC-RESULT-FREEZE-001`: 196 held-out architecture scenarios (E1=84, E2=104, C0=8), 784 policy decisions, zero invalid scenarios and zero auditor mismatches.
- D0/L0 and D1/L1 paired policy inputs are byte-identical within each pair. The two studies do not have interchangeable statistical units and must not be pooled.
- Exact overall Study 7E unsafe proceeds: D0 9, L0 21, D1 4, L1 31. False-conservative holds: D0 31, L0 26, D1 45, L1 12. Retain F12 adverse learned transfer, F10 common-authority failure, and C0 no-signal all-HOLD control.
- cFS v7.0.1 engineering qualification is separate from the Python-based frozen held-out model execution. No integrated onboard learned selector, flight qualification, operational ground-to-space transfer, RF performance, outage probability or cross-sector consequence is claimed.

## Reviewer-readable submission artifact checks

- [x] Manuscript has 27 unique cited sources (26 background sources and a Study 7 Zenodo [dataset] reference) in first-appearance order and numbered bibliography entries. The original 24-source audit is preserved as a versioned historical record; two publisher-verified IJCIP context papers were appended with no numerical or experiment changes. Source DOI/metadata audit exists, with institution-only entries distinguished from scholarly DOI checks.
- [x] Eight Markdown-native data tables have consecutively numbered, descriptive captions in the publication source. Table counts are unchanged; no scientific rows were modified.
- [x] Two evidence-bound SVG figures are inserted: a trust-domain/execution-boundary diagram and a count-only endpoint visualization. The figures are diagrams/plots, not external empirical data or generative images.
- [x] R3 has two AI-use disclosures covering protocol/research assistance and editorial/figure-code assistance; sole-author credit remains unchanged.
- [x] Original CEAS, TAES and IJSCCN rejection records were used only as internal editorial-quality lessons. No statistics, public datasets, formulas, fixtures or outcomes from Paper 1, 2, 4 or 5 / S3X / S4X / S6X / P2X were imported.
- [x] All three CI workflows passed on prior exact review head `f47c4f5f197fac36c20c2dda9f638853e7ec012f` (general run #1504, science/figure #11, export #6). A **new exact-head** run is required for this caption-enhanced candidate. Do not reuse prior-green status for this commit.
- [ ] Reinspect the newly generated DOCX/PDF pages after the eight captions, especially 3.1, 4.1–4.3, 4.6 and 4.8, and confirm that captions stay with their tables and that none crosses pages awkwardly.
- [ ] Confirm the authoritative guide, editorial portal file types, article/abstract length requirements, manuscript style, figures/artwork slots and reviewer/blinding model.
- [ ] Final human verification of all 26 sources' authors/year/volume/DOI/pagination data and journal-title abbreviation policy; references with agency landing pages require agency-specific verification.
- [ ] Confirm the sole-author legal name, independent affiliation, active corresponding email, ORCID and title-page fields as authored in `IJCIP_SUBMISSION_METADATA_DRAFT.md`; this audit deliberately does not repeat personal contact information.
- [ ] Confirm originality, simultaneous-submission status, overlap with the earlier **rejected and unpublished** Study-7 CEAS manuscript, data/code release rights, funding, competing interests, artwork provenance and AI-use declarations.
- [ ] Human review of reviewer PDF, separate cover letter, highlights and title page; then verify portal-generated proof after permitted upload and **before** final Submit.

## Hard separation and authorization

The author permitted controlled manuscript preparation, scientific/visual QA and draft PR changes; this record does **not** authorize modification of frozen Study 7/7E protocols/results, new experiments, migration of unrelated study evidence, PR merge, journal portal upload, or final submission.

Because GitHub API reported repository visibility **public**, the draft manuscript should be assumed publicly accessible. Do not introduce new credentials, confidential correspondence, unpublished personal information or restricted licensed content into tracked files.

**Terminal gate:** `REVIEW_ONLY_NOT_SUBMISSION_READY` until all mandatory publisher/author release checks are actually satisfied.

## Subsequent journal-specific contextual literature addition

Two already-published IJCIP sources were added after the initial 24-item bibliography audit: SCOUT ground-station security DOI `10.1016/j.ijcip.2020.100407` and satellite/CI cyber-attack discussion DOI `10.1016/j.ijcip.2024.100701`. Both passed independent identifier-to-title checks, with no retraction flags as of this audit. They supply venue-contextual prior work only and do **not** enter any experimental endpoint, model, source archive, or frozen claim. Current source bibliography target: **26**.

## Official IJCIP Guide resolution (2026-10-20)

The author supplied the complete 20-page Elsevier Guide, PDF SHA-256 ca09c345cef2c90b1d06432d26551cf08c1e6d7f287aa47e5940827caf7d2a2e. This supersedes the historical HTTP 403 blocker and third-party length estimates. Author-facing data deposit, declarations-tool DOCX, full postal address and final publisher proof remain open. See IJCIP_OFFICIAL_GUIDE_COMPLIANCE_AUDIT_2026-10-20.md. Study 7E has a new independently checksum-verified deposit candidate; it has NOT been uploaded/published and has no new DOI.
