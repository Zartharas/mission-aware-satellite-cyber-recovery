# TAES Paper 2 10-Page Compression Architecture

**Date:** 2026-09-06

**Branch:** `paper2/taes-10-page-compression`

**Status:** `ARCHITECTURE_LOCKED_FOR_LOCAL_CANDIDATE_GENERATION`

## Objective

Develop a scientifically self-contained IEEE TAES Regular Paper that renders below the 10-printed-page overlength threshold with buffer, while preserving the frozen 16-page R9 package on `main` as the audited fallback.

Target engineering range for the new submission-format PDF: **9.0-9.5 pages**. The candidate is not approved merely because it is short; it must pass scientific-preservation, deterministic build, and visual-QA gates.

## Main-article architecture

The main article will retain:

- the current 214-word abstract and five index terms unless later pagination shows a compelling reason to revise them;
- a compressed Introduction with the same scientific identity and all prior-art citation families;
- a compact Related Work section that preserves novelty boundaries and citations [1]-[13];
- the common `E_j`, `Q_j`, `T_j`, `U_j`, and `C_j` qualification abstraction without Table I;
- a compact Study-3 section with a selected exact-result table and the V4/V5/cache distinctions;
- a compact Study-4 section with a selected threshold table and explicit null/equal-threshold results;
- a compact Study-6 section retaining the exact six-gate residual-state/benign-loss frontier;
- a prose-only cross-study synthesis with Figure 1 retired from the main article;
- one consolidated validity/external-validity section;
- a compact conclusion;
- the existing substantive IEEE AI-use acknowledgment;
- the same 13-reference bibliography, including TUF v1.0.36.

## Material relocated to peer-reviewed supplementary material

The supplementary material will preserve expanded detail from the already audited R9 source rather than re-derive it. It will contain:

1. expanded Study-3 design, endpoints, one-shot/persistent treatment details, and the full selected Study-3 result table;
2. expanded Study-4 design and the complete 18-rule first/systematic threshold map;
3. expanded Study-6 state, signal, gate, and benign-unavailability definitions and the complete frontier interpretation;
4. expanded construct, statistical, aerospace-generalization, standards, synthesis, reproducibility, and future-evaluation boundaries.

The generator will source these appendices from the tracked R9 component files and change only appendix/table labels needed to prevent collision with main-text numbering.

## Main-text content that may not be relegated exclusively to the supplement

The main article itself must still state:

- three separate frozen populations and no pooling;
- only Study 3 models contact;
- qualification is not recovery completion;
- logical/model time is not real spacecraft time;
- Study 3 affected V4 records are rejected while V5 can remain false but validly signed;
- the truthful `PRE_ONSET_CACHE` boundary;
- the structural/conditional meaning of the Study-3 B2 zero;
- Study 4 first versus systematic failure and the conditional provenance tradeoff;
- Study 4 null/equal-threshold results and synthetic-domain/non-probability controls;
- Study 6 G0 4/5, G1/G2 3/5, G3/G4 2/5 with different residual identities, and G5 1/5 leaving `APPROVED_BAD_SOURCE`;
- Study 6 benign assurance-loss increase and non-probability interpretation;
- no operational flight, RF, mission-availability, standards-compliance, or global-best claim;
- the synthesis is qualitative and not an integrated experiment.

## Layout actions

Permitted:

- retire Figure 1 from the short main article;
- remove the prior common-framework Table I;
- use three compact main-text tables: Study 3 selected exact results, Study 4 selected threshold structure, Study 6 gate frontier;
- relocate the full 18-rule Study-4 map to supplement;
- consolidate repeated limitations.

Not permitted:

- reducing the required 10-point font;
- shrinking TAES margins or column geometry;
- reducing line spacing below the required format;
- using negative spacing or other layout tricks to evade page charges.

## Decision rule

If the short candidate renders above 10 pages, further reduction may target only demonstrated redundancy or material already preserved in the supplement.

If it renders below 9 pages and the scientific narrative appears overly compressed, detail should be restored selectively until the paper approaches the 9.0-9.5 page engineering range.

The frozen R9 16-page package on `main` remains untouched throughout this track.
