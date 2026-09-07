# TAES Paper 2 Length-Reduction Feasibility Audit R2

**Audit date:** 2026-09-06  
**Target journal:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Manuscript type:** Regular Paper  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Current formatted candidate:** IEEEtran R7  
**R7 PDF SHA-256:** `b4726622cb2769055c0541b773ccddcbf84163462e3fdbe16d6fc6933b7b60be`  
**R7 page count:** `18`  
**R7 format / visual QA:** PASS  
**Scientific rerun authorized or required:** No  
**Manuscript edit performed by this audit:** No  
**Verdict:** `PASS_MODERATE_SECOND_COMPRESSION_FEASIBLE__TARGET_15_PAGES_PREFERRED__14_PAGES_STRETCH`

## 1. Purpose

This audit determines how far Paper 2 can be shortened after the first completed compression pass without weakening the frozen scientific record, null findings, prior-art positioning, interpretation controls, or study separation. It is a read-only editorial feasibility audit. It does not modify the canonical manuscript or any Study 3, Study 4, or Study 6 evidence.

## 2. TAES length context

Current TAES author instructions state that Regular Papers have no formal manuscript-page limit, but unnecessarily long manuscripts may receive unfavorable reviews. Accepted Regular Papers incur mandatory overlength charges of USD 200 for each final printed page beyond ten. The final printed-page count is determined from IEEE production proofs; the required two-column/single-spaced manuscript is the best estimate before acceptance.

The current R7 development manuscript is 18 pages. If final IEEE production pagination were also 18 pages, the corresponding overlength amount would be approximately USD 1,600. This is an estimate, not a frozen charge.

## 3. Prior compression already completed

Compression Pass 1 reduced the manuscript body by 2,298 words, approximately 16.5 percent of its prior body length. It intentionally edited only Sections I, III, and VII:

- Introduction: 1,223 -> 720 words;
- Section III: 1,681 -> 707 words;
- Section VII: 1,734 -> 913 words.

Sections IV, V, VI, and VIII were intentionally left unchanged. This matters for R2: the already-compressed framing sections should not be treated as the primary source of further reduction.

## 4. Current section-size profile

The R7 PDF text extraction gives the following approximate section sizes. These figures are used for prioritization only; the canonical manuscript audit remains authoritative for total word count.

| Section | Approx. extracted words | R2 compression priority |
|---|---:|---|
| Abstract / Index Terms | ~228 | Preserve |
| I. Introduction | ~721 | Low, already compressed |
| II. Related Work | ~1,398 | Medium |
| III. Common Framework | ~690 | Low, already compressed |
| IV. Study 3 | ~1,848 | High |
| V. Study 4 | ~1,887 | Very high |
| VI. Study 6 | ~1,694 | Very high |
| VII. Synthesis | ~1,048 including figure-extracted text | Low to medium, already compressed |
| VIII. Validity / Aerospace Boundaries | ~1,797 | Very high |
| IX. Conclusion | ~462 | Medium |
| Acknowledgment | 74 | Preserve |
| References | ~331 extracted / 348 canonical | Preserve |

The dominant editable mass is therefore Sections IV, V, VI, and VIII, with Section II as a secondary opportunity.

## 5. Safe consolidation opportunities

### Section II, Related Work

**Safe opportunity:** roughly 150-250 words.

Preserve all 13 reference anchors, the satellite-specific context, RATS distinction, quorum prior art, Space Fabric positioning, in-toto/TUF/SLSA positioning, and the bounded literature-gap statement. Compression can focus on repeated explanations that individual mechanisms are not new and on repeated descriptions of Study 4 / Study 6 scope that are restated later.

### Section IV, Study 3

**Safe opportunity:** roughly 200-300 words.

Preserve the 1,380-trajectory population, 46 onset phases, K0/K4 definitions, V0/V4/V5 semantics, one-shot/persistent distinction, all Table II values, PRE_ONSET_CACHE versus V5_AFFECTED_RECORD origin distinction, B2 structural-zero qualification, and logical-time limitation.

Compression can consolidate repeated statements that K4 is not orbital contact, logical seconds are not operational time, V5 is validly signed rather than post-signature tampering, and the same non-generalization controls that are comprehensively restated in Section VIII.

### Section V, Study 4

**Safe opportunity:** roughly 300-450 words.

This is the strongest study-section compression opportunity because Table III already preserves the complete 18-rule first/systematic threshold map. The prose currently walks through several individual table cells after the exact map is already visible.

Preserve the seven-producer 3/2/2 domain allocation, registered-producer denominator, two separate exhaustive blocks, 128 subsets per block/rule, 4,608 population, first versus systematic failure definitions, Q3_D3 key example, Q4_D3 / Q5_D3 conditional effects, null/equal-threshold cases, and the no-global-best interpretation.

Compression should group repeated high-threshold examples, use Table III rather than narrating every threshold, and shorten the second explanation that the model is not Byzantine consensus.

### Section VI, Study 6

**Safe opportunity:** roughly 250-350 words.

Table IV already preserves the G0-G5 residual-state frontier and benign-loss counts. The prose can therefore be compressed without deleting any state identity.

Preserve all six signals, all six gates, 36 + 384 = 420 population, separate adversarial / benign blocks, G3-versus-G4 residual identity, G5 APPROVED_BAD_SOURCE residual state, 32/64 -> 63/64 benign-loss progression, and the observability-boundary interpretation.

Compression can group G0-G2 and G3-G4 descriptions, avoid repeating the complete residual state lists already in Table IV, and state the SLSA malicious-producer limitation once authoritatively rather than in both Related Work and the Study 6 discussion.

### Section VIII, Validity / Aerospace Interpretation

**Safe opportunity:** roughly 350-500 words.

This is the largest prose-only consolidation opportunity. Section VIII must remain the authoritative validity firewall, but it currently repeats several controls already stated in the individual study sections.

Preserve: only Study 3 models contact; logical time is not spacecraft time; Study 4 provenance domains are synthetic; Study 6 is an abstract Boolean model; no flightworthiness, certification, mission-availability, RF, CPU, energy, operational-attack-rate, or operational-recovery-probability claim; no pooled N; same-repository reproducibility is not external replication; framework mentions do not establish standards compliance; no integrated three-layer experiment was performed.

Compression can consolidate repeated per-study lists into one common external-validity paragraph plus one compact paragraph per study, while retaining all distinct construct boundaries.

### Sections I, III, VII

**Safe opportunity:** only about 30-80 words each unless a specific duplicate is identified.

These sections already absorbed the 2,298-word first compression pass and should be protected from another broad cut. Any R2 edits here should be sentence-level consolidation only.

### Section IX, Conclusion

**Safe opportunity:** roughly 100-150 words.

The conclusion can retain one compact result sentence per study plus the cross-study observability conclusion. It does not need to restate the full interpretation and limitation language already established in Sections IV-VIII.

## 6. Cross-section redundancy patterns identified

High-similarity pairs in the current R7 text include:

- Study 6 and Section VIII both state that APPROVED_BAD_SOURCE has all gate-visible signals true while objective correctness is false;
- Study 4 and Section VIII both state that compromise and benign-unavailability blocks are separate and do not model the joint condition;
- Related Work and Study 6 both restate the SLSA limitation for intentionally malicious producers;
- Section III and Section VIII both restate the distinct Study 3 / Study 4 / Study 6 units and the reason populations cannot be pooled;
- Section VII and Section IX both restate that residual identity matters rather than only aggregate count or duration;
- Section VII and Section VIII both restate the need to map the abstract producers, domains, timing, gates, and failure states to a real mission before operational generalization.

These are consolidation candidates, not deletion instructions. At least one authoritative occurrence of every scientific control must remain.

## 7. Reduction scenarios

### Scenario A: conservative

Target reduction: ~1,200-1,500 words.  
Expected formatted range: roughly 16 pages.  
Scientific risk: very low.  
Likely estimated overlength exposure if final proof were 16 pages: ~USD 1,200.

### Scenario B: preferred moderate compression

Target reduction: ~1,700-2,200 words.  
Expected formatted range: roughly 15 pages, potentially 14 depending on reflow.  
Scientific risk: low if the protected-content controls below pass.  
Likely estimated overlength exposure if final proof were 15 pages: ~USD 1,000; if 14 pages: ~USD 800.

### Scenario C: aggressive stretch

Target reduction: ~2,700-3,300 words plus possible table / layout compaction.  
Expected formatted range: roughly 13-14 pages.  
Scientific risk: moderate.  
This level begins to pressure method reproducibility, null-result interpretation, and validity detail. It is not the preferred first move.

### Scenario D: force ten pages

Not recommended. Reaching ten pages from the current 18-page R7 layout would likely require removal or severe compression of scientifically useful methods, interpretation controls, tables / figure content, or prior-art positioning. The journal does not require a ten-page submission, so zero-overlength pagination is not a sufficient scientific reason to weaken the manuscript.

## 8. Protected-content controls for any R2 edit

A second compression pass must not remove or weaken:

1. separate frozen populations and units for Studies 3, 4, and 6;
2. no pooled N / common effect / global rank;
3. Study 3 as the only contact model;
4. K4 as synthetic contact rather than orbital access;
5. logical seconds as model time only;
6. V4 affected records rejected for invalid signature versus V5 false-but-valid signed producer evidence;
7. PRE_ONSET_CACHE versus V5_AFFECTED_RECORD origin separation;
8. B2 zero as structural / conditional rather than immunity or global superiority;
9. Study 4 registered-producer denominator and separate safety / benign blocks;
10. first versus systematic failure and all null / equal-threshold cases;
11. synthetic provenance domains as labels, not demonstrated independence;
12. Study 4 as qualification rather than Byzantine consensus;
13. Study 6 G0-G5 residual identities, especially G3 versus G4;
14. APPROVED_BAD_SOURCE as a frozen-model observability boundary, not theorem or prevalence estimate;
15. assurance-signal unavailability as distinct from contact loss and mission availability;
16. qualification as distinct from completed recovery;
17. no flight safety, flightworthiness, certification, RF, CPU, energy, thermal, mission availability, or operational probability claims;
18. same-repository audit / reproduction as reproducibility, not external replication;
19. no integrated three-layer experiment;
20. substantive IEEE AI-use acknowledgment;
21. reference set and TUF v1.0.36 correction unless a separately documented reference update is required.

## 9. Recommendation

Proceed with **Scenario B**, a controlled second compression pass targeting approximately 1,700-2,200 words, with a preferred formatted objective of **15 pages** and **14 pages treated as a stretch success rather than a mandatory requirement**.

The reduction should prioritize, in order:

1. Section V;
2. Section VIII;
3. Section VI;
4. Section IV;
5. Section II;
6. Section IX;
7. only surgical edits to Sections I, III, and VII.

After the text candidate is assembled, rerun the scientific-claim, population-separation, reference-order, boundary-language, IEEEtran build, font-embedding, and full PDF visual-QA gates. No study rerun is warranted.
