# TAES Paper 2 Controlled 10-Page Compression Authorization

**Date:** 2026-09-06

**Status:** `AUTHORIZED_CONTROLLED_EDITORIAL_COMPRESSION_TRACK`

The author explicitly authorized creation of a separate controlled compression track for Paper 2 after reviewing the live IEEE TAES page-charge acknowledgment. The objective is to reduce the submission manuscript from the frozen 16-page R9 baseline toward a charge-avoiding submission target while preserving the scientific claims and all frozen experimental evidence.

## Authorized objective

- Preserve the frozen 16-page R9 package on `main` as the audited fallback.
- Develop a separate shorter candidate on branch `paper2/taes-10-page-compression`.
- Engineering target: approximately 9.0-9.5 TAES-formatted submission pages.
- Absolute submission ceiling for the charge-avoidance candidate: 10 TAES-formatted pages.
- Do not merge the shorter candidate to `main` unless it independently passes scientific-preservation audit, deterministic build/hash controls, and full visual QA.

## Scientific controls that remain binding

- Studies 3, 4, and 6 remain frozen. No rerun, enlarged population, altered endpoint, altered treatment, altered statistical unit, or post hoc result modification is authorized.
- No pooled population, common effect, pooled success rate, global policy rank, or integrated three-layer experiment may be introduced.
- Only Study 3 models intermittent contact.
- Logical/model time must not be converted to real spacecraft time.
- Study 4 producer unavailability is not mission availability or contact loss.
- Study 6 assurance-signal unavailability is not contact loss or network outage.
- Qualification is not recovery completion.
- Finite-state and exact-subset counts are not operational probabilities.
- Same-repository independent audits support reproducibility, not external replication.
- Existing null, negative, conditional, and residual-state findings must remain represented.
- The IEEE AI-use disclosure remains mandatory and must remain accurate.

## Protected scientific content

The shorter main article must still preserve, at minimum:

1. Study 3: separate V4 versus V5 semantics, persistent V5 residual qualification, the `PRE_ONSET_CACHE` boundary, the structural B2 zero caveat, K0 versus synthetic K4 distinction, and logical-time limitation.
2. Study 4: complete interpretation of first versus systematic failure, conditional provenance effects, benign-loss cost, null/equal-threshold results, synthetic-domain limitation, and no-global-best conclusion.
3. Study 6: signature-only 4/5 residual state count, G1/G2 equal aggregate result, G3/G4 different residual identities, G5 leaving only `APPROVED_BAD_SOURCE`, benign assurance-loss tradeoff, finite-state/non-probability limitation, and non-compliance/non-operational boundaries.
4. Cross-study synthesis: qualitative only, no pooled experiment, no data flow among studies, residual trust boundary framed as observability/model structure rather than universal theorem.
5. References sufficient to support all retained prior-art positioning.

## Permitted editorial actions

- Compress prose.
- Consolidate repeated limitations while retaining their scientific meaning.
- Replace exhaustive narrative with compact tables where the main claim remains independently understandable.
- Move reproducibility detail, exhaustive finite maps, and secondary diagnostic detail to peer-reviewed supplementary material if needed.
- Retire or relocate Figure 1 if the main article remains fully understandable without it.
- Shorten section structure and combine subsections where doing so does not obscure study separation.

## Not authorized

- Changing frozen science.
- Deleting unfavorable/null findings merely to reduce length.
- Hiding claim limitations only in supplementary material when they are necessary to interpret a main-text claim.
- Shrinking fonts, margins, line spacing, or TAES geometry to evade page charges.
- Replacing exact values with unsupported approximations.
- Merging the new track to `main` before independent QA.

The previously granted final author submission authorization remains associated with the scientifically approved Paper 2 content. A materially changed scientific manuscript would require renewed authorization; editorial compression that preserves the science does not.
