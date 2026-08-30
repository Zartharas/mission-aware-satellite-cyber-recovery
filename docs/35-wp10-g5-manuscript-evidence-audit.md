# WP10-G5 Manuscript Evidence Audit

**Date:** 2026-08-29  
**Status:** Manuscript scientific-evidence audit complete  
**Audited manuscript sections:** `publication/manuscript/04-results.md`, `publication/manuscript/05-discussion.md`  
**Primary findings authority:** `docs/28-wp10-integrated-findings-freeze.md`  
**Claim authority:** `docs/30-wp10-g1-claim-to-evidence-matrix.md`  
**Results architecture:** `docs/31-wp10-g1-results-architecture.md`  
**Post-results reconciliation:** `docs/32-wp10-g2-empirical-reconciliation.md`  
**Publication displays:** `docs/34-wp10-g3-publication-tables-and-figures.md`

## Purpose

This audit tests whether the current Results and Discussion drafts remain inside the frozen scientific evidence and claim boundaries. It is not a new analysis and does not alter any proposition, endpoint, estimate, model, or analysis membership.

The audit deliberately separates two questions:

1. **Scientific traceability:** Is each material empirical/manuscript claim supported by the frozen WP10 record?
2. **Bibliographic readiness:** Are all external literature citations fully normalized and ready for a target journal's reference style?

A bibliographic formatting or metadata task is not treated as a scientific-evidence failure when the underlying source and claim are valid.

## Overall verdict

**Scientific manuscript evidence audit: PASS.**

The G4 Results and Discussion drafts preserve the frozen P1–P5 findings, quantitative anchors, censoring rules, execution provenance, and external-validity boundaries. No post-hoc proposition repair, weighted score, global policy ranking, new p-value, or new runtime-derived claim was found.

**Bibliographic assembly: OPEN / non-blocking for scientific freeze.**

The repository's current `references/references.bib` contains only a subset of the works cited or discussed in G2/G4. Core named 2025–2026 references were rechecked against publisher/government/preprint records during G5; the bibliography should be expanded and normalized during G6 full-manuscript assembly and then formatted to the selected journal style.

## Scientific audit checks

| Audit control | Verdict | Evidence / disposition |
|---|---|---|
| Analysis membership | PASS | Results state 720 frozen VALID observations; INVALID/pre-runtime/quarantined evidence remains outside statistical membership. |
| P1 null preserved | PASS | Results and Discussion both state that mission-state dependence was not demonstrated on the predeclared M01/M02/M03/M06 outcomes. No M07 rescue analysis is used. |
| P2 numerical fidelity | PASS | All M04/M05/M07 P6, P7, and interaction estimates/intervals match the integrated findings freeze and Table R2. |
| Contact semantics | PASS | C1 is consistently described as one synthetic/modelled missed-contact window, not real ground-station/operator/RF timing. |
| P6/P5 semantics | PASS | A16/A17 remain P6; text states that P6 waits for modeled authorization and then delegates the verified-rollback mechanism associated with P5. |
| M05 censoring | PASS | Manuscript records 180 observed recoveries, 540 right-censored observations, and the frozen 30-s horizon; censored runs are not called observed recoveries. |
| P3 broader/narrower distinction | PASS | Evidence-dependent P7 recovery vulnerability is reported while the anticipated restoration-without-verification mechanism remains explicitly absent. |
| P4 correctness boundary | PASS | Manuscript reports actual effective-policy/action pathways and observed consequences; it explicitly rejects an independent post-hoc objective correctness oracle. |
| Safe-mode wording | PASS | `ENTER_SAFE_MODE` is labeled an experimental modeled action, not native spacecraft safe mode. |
| M03 structural zero | PASS | No observed frozen invariant violations is reported without converting the zero count into a universal safety claim. |
| P5 front count | PASS | `5/9` is reported as point-estimate front membership and explicitly not as a success rate. |
| P5 equivalence cases | PASS | G01–G03 are reported as ties/delegation equivalence rather than adaptive wins. |
| P5 disadvantages retained | PASS | G04, G05, G06, and G09 point-dominated status is retained; comparator-supported disadvantages are not hidden. |
| G05 uncertainty | PASS | A14/P5 point advantage through M05 is distinguished from the uncertain/tied marginal interval classification. |
| No weighted/global rank | PASS | No weighted P5 score or overall P0–P7 rank appears in Results or Discussion. |
| Marginal-CI boundary | PASS | Manuscript does not make a simultaneous 95% Pareto-dominance claim. |
| Execution provenance | PASS | 1/9/710 VALID distribution is retained and the manuscript does not state all 720 ran at commit C. |
| Sensitivity role | PASS | 29-seed/696-observation final-C analysis is identified as robustness/sensitivity, not a replacement primary population. |
| Raw/runtime boundary | PASS | G4 adds manuscript text only; no new campaign runtime, seed consumption, raw-evidence mutation, or new analysis is represented. |
| External validity | PASS | NOS3/Fortytwo SIL scope, no RF/operational-spacecraft claim, no human/operator findings, bounded event/state coverage, and evidence-model limitations are explicit. |

## Results-section audit

### Section 4.1 — population and endpoint integrity

PASS. Population, M05 censoring, M03 structural zero, and execution provenance match the frozen authorities.

### Section 4.2 — P1

PASS. The null result is presented before positive findings and is not reframed as partial support.

### Section 4.3 — P2

PASS. All nine retained effect/interval values match Table R2 and the integrated freeze. P6/P5 terminology and modeled-contact language are preserved.

### Section 4.4 — P3

PASS. Absolute denominators are retained (`30/30`, `0/30`, `30/30 failed`), and the narrower absent mechanism is named.

### Section 4.5 — P4

PASS. The manuscript describes deterministic selection/action pathways and consequences without manufacturing an “incorrect action” variable.

### Section 4.6 — P5

PASS. Front membership, point dominance, marginal support, equivalence, mixed G05 interpretation, and the non-ranking boundary all match the frozen record.

### Section 4.7 — provenance sensitivity

PASS. The complete-block final-commit sensitivity is correctly described as 29 seeds / 696 observations and does not exclude the earlier VALID runs from the primary result.

### Section 4.8 — synopsis

PASS. The synopsis is neutral and preserves the mixed P1–P5 outcome pattern.

## Discussion audit

### Theory interpretation

PASS. Mission Aware is treated as the design/analysis lens rather than a general theory empirically “confirmed” by P1.

### Mechanism interpretation

PASS. The P2 timing effect is attributed to the implemented ground-authorization dependency under the controlled contact model, not generalized into universal autonomous superiority.

### Evidence interpretation

PASS. P3/P4 discussion distinguishes evidence-qualified trusted recovery from nominal operation and treats evidence-insufficient fallback as a policy choice with measurable cost rather than inherently correct behavior.

### P5 interpretation

PASS. The Discussion treats conditional Pareto behavior as more informative than a single winner and explicitly rejects redefining “mission-aware” to mean “superior.”

### Practical implications

PASS WITH BOUNDED INTERPRETATION. The design implications are presented as factors for simulation, assurance, and systems-engineering evaluation rather than flight/deployment prescriptions.

### Limitations

PASS. SIL fidelity, synthetic contact, bounded coverage, deterministic P7, evidence abstraction, censoring, structural-zero M03, versioned provenance, and no-human-study limitations are explicit.

## Bibliographic verification status

The following external sources named or directly relied upon in the current Discussion/G2 reconciliation were checked against current publisher/government/preprint records during G5:

- Bakirtzis et al., **Mission Aware Cyber-Physical Security**, *Systems Engineering*, DOI `10.1002/sys.70018`; publisher record lists first online publication 10 December 2025 and journal volume 29 (2026).
- NIST SP 800-160 Vol. 2 Rev. 1, **Developing Cyber-Resilient Systems: A Systems Security Engineering Approach**, December 2021.
- Harshvardhan Chunawala, AWS Public Sector Blog, **An incident response playbook for satellite operations on AWS (Part-2): Automated response and recovery**, 19 June 2026.
- Shiqi Liu and Kun Sun, **Temporal Risk on Satellites**, arXiv:2608.20575, 20 August 2026.
- Van Le, Trevor Tran, and Tan Le, **TinyML-Driven Cybersecurity for Autonomous Spacecraft: Latency-Accuracy Analysis for SPARTA RF and Cyber Threat Detection**, arXiv:2606.05779, 4 June 2026.
- Charbel Mattar et al., **What is Cybersecurity in Space?**, arXiv:2509.05496, 5 September 2025.
- Giuseppe Sarri et al., **The JUICE Spacecraft System Design**, *Space Science Reviews* 222, article 35 (2026), DOI `10.1007/s11214-026-01289-4`, published 1 April 2026.

The existing bibliography also contains verified DOI records for the Mission Aware article, Thangavel et al. trusted autonomy review, Wanninger FDIR article, NIST SP 800-115, and the selected dataset records. Final author lists, issue/page/article metadata, access dates for web resources, and target-journal style remain a G6/reference-assembly task.

### Wanninger year convention

The Wanninger FDIR article has a 2025 DOI suffix and was published online in 2025, while the journal volume is a 2026 volume. The existing BibTeX uses year 2025. This is not a scientific issue; the final bibliography should follow the selected journal's convention for online-first versus issue year and use that convention consistently.

## Non-findings deliberately retained

The following absences are part of the manuscript evidence and must survive future editing:

- no supported P1 mission-state effect on the predeclared outcomes;
- no P3 nominal-restoration-without-verification case in A13;
- no observed M03 frozen safety-invariant violation;
- no P4 mission-loss event in the retained P4 cells;
- no independent P4 objective correctness label;
- no universal P7 superiority;
- no weighted P5 score or global rank;
- no operational spacecraft, RF, or human/operator evidence.

## G5 disposition

**G5 scientific evidence audit: PASS.**

The Results and Discussion drafts may advance to full manuscript assembly without new statistical analysis. Any future textual edit that changes a numerical value, proposition status, P6/P5 semantics, P4 correctness framing, P5 rank/dominance meaning, censoring rule, or external-validity boundary must be re-audited against `docs/28`–`docs/34`.

**Next phase: WP10-G6 — target-neutral full manuscript assembly and bibliography expansion.**

G6 may draft/assemble the remaining manuscript components (title/abstract, Introduction, Methods, Conclusion, data/code availability, ethics/responsible-use statement, references) from existing frozen repository evidence. Journal-specific formatting can remain pending until a venue decision is required.