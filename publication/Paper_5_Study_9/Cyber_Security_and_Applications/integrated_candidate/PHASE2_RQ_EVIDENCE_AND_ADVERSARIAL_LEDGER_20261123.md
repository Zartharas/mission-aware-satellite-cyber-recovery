# Paper 5 Phase 2: nine-question evidence traceability and adversarial checks

**Recorded:** 2026-11-23  
**Approved phase:** Phase 2 manuscript/evidence presentation, after Phase 0 protection and Phase 1 editorial framing.  
**Source PR:** #255 (draft; no merge, no submission).  
**Boundary:** Retain frozen Study 9 and Study 10 results; no original telemetry, field re-adjudication, G5, or post hoc policy runs.

## Question-to-evidence crosswalk

| Research question | Protected evidence | Supported disposition | Unresolved inference or risk |
|---|---|---|---|
| RQ1 | `study9/results/S9-RTSI-001_CANONICAL_RUN_20260914/mapping_matrix.json`: 24 mappings | 0 direct/derived; classifications 4/4, 5/3, 5/3 ambiguous/absent | Operational evidence admission is narrower than field similarity |
| RQ2 | `policy_strata.json` under the same canonical run | Three one-group projections; all four policy action sets non-singleton; 0 unique-action row-weighted fraction | 567,763 row records are not independent recovery decisions |
| RQ3 | Frozen policy sidecar requirements in `policy_strata.json` | Guaranteed minima 6/7/7/8 for B0/B1/B2/S1 | Selector-specific, not mission-universal minimum |
| RQ4 | Intersection across the 24 frozen source mappings | Eight recovery predicates unresolved in every Study 9 source | Source-specific class differences remain; zero coverage does not mean absent telemetry |
| RQ-E1 | Archived `study10_derived/S10_G4_TierA_32Slot_PublishedSchema.json` | 32 slots = 14 ambiguous, 18 absent, 0 direct/derived | Source-schema only; no nested pickle/flight-series inspection |
| RQ-E2 | Same four Tier A descriptive strata | ESA v2 Mission 1/2/3 and OPS-SAT v2 contrasts only | **Partially addressed** versus original source-type contrast including Hack-A-Sat; no Hack-A-Sat adjudication in Tier A |
| RQ-E3 | Archived `study10_derived/S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json` | 224 matched channels, 842/896 shared metadata cells equal, 54 changed Physical Unit annotations, 224 v2-only Categorical entries | Metadata contrast does not establish v1/v2 recovery mapping transitions, nested byte equivalence, or unit conversions |
| RQ-E4 | Archived `study10_derived/S10_G4_TierC_16_StratumPolicy_NonEvaluable.json` | 16 operational stratum-policy results NOT_EVALUABLE | No native decision instant / evidence validity; action-set size is null, not zero |
| RQ-E5 | Frozen synthetic harness/oracle validation receipts cited in manuscript | 18 synthetic cases, 22 repository tests, 1,024 independent-oracle parity comparisons, zero mismatches | Technical parity does not verify signatures, authorization, or real spacecraft recovery |

## Reproducible research presentation

- The manuscript's Table `tab:phase2rq` is the nine-question crosswalk; Figure `fig:phase2gates` uses only native LaTeX primitives and has no external image dependency.
- Appendix `app:fieldledger` is generated solely from the existing 24-row Study 9 matrix and archived 32-row Study 10 Tier A JSON. It preserves mapping classes, named candidates, exclusions and the Study 10 documented evidence-role categories.
- The Phase 2 validator checks field names and classes against those repository source files. This is an editorial provenance check, not new semantic adjudication or new scientific execution.
- Original source schema and derived-evidence JSON are left byte-for-byte untouched. The Study 10 detail CSV and original ESA/OPS-SAT records remain outside the review branch.

## Independent adversarial re-review backlog

1. **Central editorial novelty objection remains:** the all-unknown action ambiguity is a consequence of the frozen eight-variable interface and selector, not an independent new recovery-control result.
2. **RQ-E2 completeness:** the original prospective source-type contrast included Hack-A-Sat. Treat the evaluated four strata as the completed evidence, never silently claim full competition-source coverage.
3. **RQ-E3 semantic transition:** all reported paired differences are metadata annotations; without full v1 field re-adjudication and nested-source evidence, do not assert class transitions or telemetry conversions.
4. **Evidence granularity:** field names, source rows, schema slots, matched metadata cells, and synthetic fixtures are not exchangeable statistical units.
5. **Flight relevance and authority:** no verified operator, verifier, mission recovery gate or operational decision time is supplied by the published sources.
6. **Provenance limitations:** the author-local ESA outer-layout JSON digest was not independently rehashed from uploaded bytes.
7. **External work and journal suitability:** Phase 1 cited close methods and limits; CSA novelty and length judgments require independent editorial review. No submission claim.

**Disposition:** Phase 2 editorial additions are manuscript-candidate work only. Phase 0 science protection remains effective. Pending exact-head build, independent adversarial re-review, author attestations and separate publication authorization.
