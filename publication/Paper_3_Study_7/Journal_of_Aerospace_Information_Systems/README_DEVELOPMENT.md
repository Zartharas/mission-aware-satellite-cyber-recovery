# Paper 3 / Study 7 — JAIS Technical Note Development Track

**Development status:** `FIRST_COMPLETE_R3_DRAFT_AUDITED__TITLE_LOCKED__SUBMISSION_NOT_AUTHORIZED`  
**Study:** Study 7 / `S7-LSO-001`  
**Target journal:** AIAA *Journal of Aerospace Information Systems* (JAIS)  
**Target article form:** Technical Note  
**Locked title:** **Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**  
**Scoped branch:** `publication/paper3-study7-boundary-audit`  
**Clean-main base:** `3b02edc3dfe75ab64a42adc6b10d1acb3089c96e`

This directory is the controlled development surface for Paper 3. Study 7 was selected after a read-only candidate audit and publication-boundary/originality gate. The manuscript is intentionally a concise JAIS Technical Note rather than a full-length paper.

## Current manuscript authority

First complete audited draft:

`PAPER3_TECHNICAL_NOTE_DRAFT_R3_FULL.md`

Whole-manuscript audit:

`PAPER3_R3_WHOLE_MANUSCRIPT_AND_TITLE_AUDIT.md`

Title lock:

`PAPER3_TITLE_LOCK_2026-09-07.md`

Pre-draft controls remain authoritative for their respective stages:

- `PAPER3_MANUSCRIPT_ARCHITECTURE.md` — RQ, contribution ledger, evidence boundary, display inventory, word budget, overlap controls;
- `PAPER3_SOURCE_LEDGER.md` — verified publisher, prior-work, and literature sources;
- `../../../../docs/PAPER3_STUDY7_PUBLICATION_BOUNDARY_AND_ORIGINALITY_GATE_2026-09-07.md` — candidate selection and immutable evidence boundary.

Earlier R1/R1A/R2/R2A drafts and audits are retained as development provenance. They are not the current complete manuscript authority.

## Scientific evidence boundary

Paper 3 uses **Study 7 only** as new experimental evidence.

Frozen population: exactly **1,033 observations**:

- Block A: 512 observations;
- Block B: 512 observations;
- Block C: 9 observations.

Accepted execution:

- workflow run `33689625480`;
- execution commit `f1530b0b2e81a5916adaf7ce808075156424dfb5`;
- artifact ID `9869488192`;
- artifact SHA-256 `26b522d2692516aa1b4ae62d032a9a909dbaccd7ef1a74104080c39bdf3a091b`;
- independent audit: PASS, 1,033 observations, 0 mismatches.

No Study-1, Study-2, Study-3, Study-4, Study-5, Study-6, or Study-8 observation may be treated as Paper-3 experimental evidence. Study 5 remains deferred and must not be combined with Study 7.

## Locked research question

**RQ1. How does policy-visible evidence constrain the adjudicated correctness of a learned satellite cyber-recovery selector under signed-but-false evidence, and how does adding a corroborating observable change that boundary when corroboration is independent versus correlated with the compromised evidence path?**

The R3 manuscript remains an information-sufficiency/assurance paper. It is not an ML-superiority, anomaly-detection, certification, or operational-spacecraft-performance paper.

## Venue and article-form boundary

Target remains:

**AIAA Journal of Aerospace Information Systems — Technical Note.**

The article form is intentionally concise. No unrelated study may be imported merely to increase manuscript length. AIAA Technical Note requirements and exact formatted word/page limits must be rechecked when the publisher template is instantiated.

## Related-publication safeguard

Paper 1 (`2026-09-I012066`) is already under JAIS consideration and is scientifically related through the Study-2 V5 antecedent. Paper-3 submission must disclose Paper 1 and explain the non-overlap in evidence population, mechanism, endpoint, and contribution. Paper-1 manuscript wording, tables, figures, and observations must not be recycled into Paper 3.

Paper 2 (TAES Research Exchange UUID `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`) must also be screened for related-work disclosure because it addresses residual trust composition/provenance, although Studies 3, 4, and 6 remain entirely outside the Paper-3 evidence population.

Roadmap Paper 4 / Study 8 (`AA-D-26-02872`) remains a separate cryptographic-agility publication line.

If JAIS guidance does not clearly resolve concurrent consideration of a related manuscript while Paper 1 remains active, obtain editorial guidance before Paper-3 submission.

## Evidence preservation requirement

The accepted Study-7 GitHub Actions artifact is currently recorded to expire on **2026-12-01**. Before expiry, create a permanent provenance-preserving archive of the exact accepted evidence bytes without rerunning or regenerating the experiment. This archival action requires its own controlled authorization and hash verification.

## Current next actions

Development may continue on this branch with:

1. instantiate the JAIS/AIAA Technical Note manuscript format from R3;
2. perform exact reference-style and author-metadata QA;
3. perform exact formatted length/page compliance checks;
4. preserve the accepted Study-7 evidence bytes in a permanent archive before Actions expiry;
5. complete final scientific, ethics, related-manuscript, and submission-package audits.

**Publisher submission remains a separate explicit final author-authorization gate.**

Do not merge this development branch to `main` merely because R3 is complete; merge requires a separate repository-governance decision after the development artifacts are ready.