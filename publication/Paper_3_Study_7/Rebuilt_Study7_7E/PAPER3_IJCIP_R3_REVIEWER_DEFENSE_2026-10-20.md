# Paper 3 IJCIP R3 — rejection-informed reviewer-risk and cross-paper firewall

**Review date:** 2026-10-20  
**Source:** PR #168 exact head `375aa5bc5808ddace8bb124df73eb184a61b9765` and live `main` `1590fb97c854b4c60aae2fcb105cbc511e10043f`.  
**Publication:** Paper 3 alone; Study 7 / `S7-LSO-001` and Study 7E / `S7E-AERC-001` are two separately frozen populations, presented in one distinct manuscript.  
**Scope:** Editorial display, scientific claim preservation and read-only validation only; **NO new scientific observation**, rerun, new comparator, new model, or change to frozen endpoints.  
**Authorization:** Draft review work authorized. PR merges and publisher submission **NOT GRANTED**.

## Direct CEAS Paper 3 handling-editor feedback

The September 22, 2026 CEAS rejection audit documented four handling-editor concerns. Their corresponding Study 7E scientific responses were completed before the R3 manuscript and are not new results of this enhancement.

| Recorded concern | Already completed scientific response | This enhancement's reviewer-facing response |
|---|---|---|
| Study 7 hidden-input conclusion too direct | Prospective Study 7E cross-topology/fault outcomes | Findings-first statement focusing on non-monotonic selector and architecture interaction |
| No concrete spacecraft recovery architecture | Standalone cFS v7.0.1 qualified engineering path | Figure 1 separates actual bounded engineering evidence from Python canonical held-out policy evaluation |
| Independence assumptions unvalidated | Five explicit modeled trust domains and common-cause faults | Figure 1 names domains and expressly refuses operational/organizational independence claims |
| No equal-information deterministic corroboration comparator | Frozen D0/L0 and D1/L1 paired comparisons | Figure 2 visualizes distinct error types; existing hashes and 67/196, 72/196 disagreements remain in R3 |

Authoritative record: `publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`. This is *not* an assertion that the CEAS editor evaluated Study 7E.

## Lessons from other editorial decisions, not imported science

- **Paper 2 — IEEE TAES September 26, 2026:** the editorial pre-screen (no external reviewer reports) criticized narrow perceived importance, hard-to-read prose, unclear question/gap and emphasis on experiments performed rather than useful aerospace findings. We apply **writing and presentation lessons only**: clearer primary finding, accessible figure, bounded contribution and journal-context explanation. Paper 2's Study 3/4/6, S3X, S6X results, external timing and cFS source-artifact outcomes are not Paper 3 evidence. Record: `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_EDITORIAL_DECISION_2026-09-26.md`.
- **Paper 4 — Acta Astronautica:** the decision did *not* specify particular method criticisms. The September 19, 2026 internal forensic audit (not an editorial review) advised improved mechanism diagrams, more direct framing and visible null/negative results. We adopt those *editorial practices*, not Paper 4 methods or results. Record: `publication/Paper_4_Study_8/POST_REJECTION_FORENSIC_AUDIT_2026-09-19.md`.
- **Paper 4 — IJSCCN September 24, 2026:** the sole stated editorial reason was **out of scope**, without technical criticism or peer review. This cautions us to verify the actual IJCIP Guide and fit; it does not impugn the experimental results. Record: `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`.

None of these editorial decisions should be represented as external validation of Paper 3 or cited as new scientific data in the manuscript.

## Separate scientific identities and prohibited migration

| Publication | Scope boundary that must remain independent |
|---|---|
| Paper 1, Studies 1+2 | Deterministic mission-aware recovery; V5 problem is antecedent only, no reused Paper 1 observations |
| Paper 2, Studies 3+4+6/S3X/S6X | Evidence freshness, provenance/quorums, artifact assurance, ESA timing and cFS/LC fixture validation; no migration of their observations, figures, formulas or claims as Paper 3 findings |
| Paper 2 P2X, draft PRs #214/#215 | NOS3/COSMOS experiment design is separately unmerged, not onboard or ground validation of Study 7E |
| Paper 4, Studies 8+8E | PQC transition costs and contact feasibility, not a source of Study 7E endpoints or SatNOGS traces |
| Paper 5, Study 9 | CuCD-ID/AegisSat/UNSW-IoTSAT semantic portability; no dataset imported |
| Separate lifecycle repository | Independent software supply-chain study; no transferred results |

**No population pooling:** Study 7 = 1,033 modeled policy observations; Study 7E = 196 held-out architecture scenarios with four policies each = 784 decisions. These are not a combined sample or a third new study. This is one independent Paper 3 publication with two explicitly distinct scientific populations.

## Enhancement content and evidence ceiling

1. Figure 1 illustrates five modeled domains, cFS engineering qualification and separately frozen Python held-out inference. Its two lanes are not a live integrated runtime; research-only truth remains excluded from policy inputs.
2. Figure 2 uses only the original `study7e/results/S7E-AERC-HELDOUT-EXEC-001/exact_endpoint_counts.json` and matching result checkpoint. Unsafe proceeds: D0 9, L0 21, D1 4, L1 31. False-conservative holds: D0 31, L0 26, D1 45, L1 12. The exact F12 adverse and C0 all-HOLD null findings remain visible in the body.
3. The read-only validation gate checks manuscript counts, figure data bindings, frozen population IDs, retained limitations/disclosures and evidence identity. It does NOT retrain, simulate, reclassify or authorize anything.

## Remaining blockers

- IJCIP-specific article type, word/abstract limits, artwork and graphical-abstract rules, and submission portal file classification require authoritative live verification (the earlier Guide returned HTTP 403).
- The sole independent author must reconfirm correspondence/affiliation, funding, conflicts, licensing, data availability and substantive AI-use wording before submission.
- Vector SVG figures need rendered visual, accessibility and exact PDF placement QA before publisher files.
- PR #168 and PR #222 are not authorized to merge, and no journal submission is authorized by this enhancement.
