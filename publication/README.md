# Publication Package

This directory is the human-facing publication layer of the repository. The files retain stable names for provenance, but this index provides the recommended reading and reuse order.

## 1. Manuscript order

Read the target-neutral manuscript components in this sequence:

1. [`manuscript/00-title-abstract.md`](manuscript/00-title-abstract.md) — title, abstract, keywords, running-title candidate
2. [`manuscript/01-introduction.md`](manuscript/01-introduction.md) — problem, motivation, contributions, research framing
3. [`manuscript/02-background-and-related-work.md`](manuscript/02-background-and-related-work.md) — related literature and novelty boundary
4. [`manuscript/03-methods.md`](manuscript/03-methods.md) — experimental design, testbed, treatments, metrics, analysis methods
5. [`manuscript/04-results.md`](manuscript/04-results.md) — empirical results
6. [`manuscript/05-discussion.md`](manuscript/05-discussion.md) — interpretation, limitations, implications
7. [`manuscript/06-conclusion.md`](manuscript/06-conclusion.md) — bounded conclusions
8. [`manuscript/07-declarations-and-availability.md`](manuscript/07-declarations-and-availability.md) — ethics, data/code availability, funding, declarations

Assembly and submission controls:

- [`manuscript/MANUSCRIPT-ASSEMBLY.md`](manuscript/MANUSCRIPT-ASSEMBLY.md)
- [`manuscript/claim-traceability.csv`](manuscript/claim-traceability.csv)
- [`manuscript/citation-readiness.csv`](manuscript/citation-readiness.csv)
- [`manuscript/submission-inputs.csv`](manuscript/submission-inputs.csv)

The current manuscript is deliberately target-neutral. Journal-specific formatting, author declarations, conflict-of-interest language, AI/editorial-assistance disclosure, reference style, and submission-system metadata remain part of the journal-submission phase.

## 2. Figures

<table>
  <tr>
    <td width="50%"><img src="figures/figure-r1-p2-contact-effects.svg" alt="P2 modeled contact effects" /></td>
    <td width="50%"><img src="figures/figure-r2-p3-trusted-recovery.svg" alt="P3 trusted recovery" /></td>
  </tr>
  <tr>
    <td align="center"><strong>Figure R1</strong><br/>P2 modeled-contact effects</td>
    <td align="center"><strong>Figure R2</strong><br/>P3 trusted-recovery behavior</td>
  </tr>
  <tr>
    <td width="50%"><img src="figures/figure-r3-p4-selection-pathway.svg" alt="P4 evidence-driven selection pathway" /></td>
    <td width="50%"><img src="figures/figure-r4-p5-pareto-status.svg" alt="P5 Pareto status" /></td>
  </tr>
  <tr>
    <td align="center"><strong>Figure R3</strong><br/>P4 evidence-driven selection pathway</td>
    <td align="center"><strong>Figure R4</strong><br/>P5 condition-specific Pareto status</td>
  </tr>
</table>

The SVG files are the tracked publication graphics. Do not reinterpret the visual labels outside the corresponding Results/Discussion text; claim boundaries remain governed by the manuscript and WP10 evidence audit.

## 3. Tables

Use the tables in this order:

1. [`tables/table-r1-proposition-summary.csv`](tables/table-r1-proposition-summary.csv) — proposition-level summary
2. [`tables/table-r2-p2-contact-effects.csv`](tables/table-r2-p2-contact-effects.csv) — P2 modeled-contact effects
3. [`tables/table-r3-p3-p4-evidence-pathways.csv`](tables/table-r3-p3-p4-evidence-pathways.csv) — P3/P4 evidence and pathway results
4. [`tables/table-r4-p5-pareto-status.csv`](tables/table-r4-p5-pareto-status.csv) — P5 Pareto status
5. [`tables/table-s1-execution-provenance-sensitivity.csv`](tables/table-s1-execution-provenance-sensitivity.csv) — execution-provenance sensitivity analysis

## 4. DOI-bearing research data

The complete public raw campaign/integrity/reproducibility package is archived in Zenodo, not duplicated inside GitHub:

- **Version 1.0.0 DOI:** <https://doi.org/10.5281/zenodo.22181540>
- **Concept DOI:** <https://doi.org/10.5281/zenodo.22181539>

For exact scientific reproducibility, cite the version DOI.

## 5. Key interpretation boundaries

Keep these boundaries attached to any reuse of the publication artifacts:

- the primary statistical population is 720 VALID observations;
- the 9 INVALID attempts are provenance, not statistical observations;
- the 696-observation final-commit complete-block analysis is a sensitivity analysis only;
- P1's null result is retained;
- modeled-contact timing is not operational ground-contact timing;
- P7's 5-of-9 point-estimate Pareto-front presence is not a success rate;
- no weighted global P5 score or universal policy ranking is supported;
- no simultaneous 95% Pareto-dominance claim is made;
- `ENTER_SAFE_MODE` is an experimental effect, not a claim of native spacecraft safe-mode actuation;
- the study used no operational spacecraft, ground station, RF interference, or real mission telemetry.

## 6. Reproduction and citation

- Environment/test instructions: [`../docs/REPRODUCIBILITY_GUIDE.md`](../docs/REPRODUCIBILITY_GUIDE.md)
- Citation metadata: [`../CITATION.cff`](../CITATION.cff)
- Zenodo publication closeout: [`../docs/40-zenodo-publication-closeout.md`](../docs/40-zenodo-publication-closeout.md)
- Security/responsible disclosure: [`../SECURITY.md`](../SECURITY.md)
