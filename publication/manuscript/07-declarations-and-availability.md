# 7. Declarations, Data Availability, and Reproducibility

## Ethics and human participants

The reported software-in-the-loop experiment used no human participants and collected no human-subject data. It used synthetic identities, commands, mission states, telemetry/evidence conditions, and software-emulated contact behavior. Any future reuse of interview data or study of operator behavior is outside the present experiment and would require the applicable institutional determination before inclusion.

## Responsible-research and operational boundary

The experiment was conducted on researcher-controlled computing infrastructure using public/research software and isolated software networking. It did not access an operational spacecraft or ground station, use operational or stolen credentials, transmit or interfere with RF, intercept non-public communications, or use classified/proprietary mission telemetry. The study does not authorize or demonstrate operational satellite exploitation, jamming, spoofing, flight certification, or production autonomous recovery.

## Data availability

The complete responsible-release package supporting the reported WP9 experiment is publicly available on Zenodo as **Version 1.0.0**:

**Version DOI:** <https://doi.org/10.5281/zenodo.22181540>  
**Concept DOI:** <https://doi.org/10.5281/zenodo.22181539>

The version-specific DOI identifies the exact archived file set used for reproducibility. The archive contains the frozen raw WP9 campaign evidence, the publication-grade cryptographic integrity freeze, manuscript-facing publication/provenance artifacts, release documentation, manifest, and cryptographic checksums.

The authoritative campaign ledger contains 729 retained records: 720 VALID observations in the primary statistical population and 9 INVALID attempts retained as provenance but excluded from statistical membership. The 720-run statistical membership is identified by SHA-256:

`a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The authoritative attempt-history ledger SHA-256 is:

`92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`

The deterministic complete campaign-tree SHA-256 is:

`ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`

The raw campaign is intentionally not duplicated in the GitHub repository. The DOI-bearing Zenodo record is the public archive/evidence-of-record for those files.

## Code availability

The research repository is publicly available at:

<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery>

The reproducibility-hardened repository snapshot used for submission preparation is permanently identified by commit:

<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/tree/99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc>

It contains the experiment design, software-in-the-loop policy/event implementation history, campaign governance records, analysis/manuscript controls, tests, reproducibility tooling, and aggregate publication artifacts. Raw `results/wp9/campaign/` evidence remains outside GitHub by design and is distributed through the Zenodo dataset above.

Repository-level environment and test instructions are maintained in `docs/REPRODUCIBILITY_GUIDE.md`. Third-party research infrastructure remains subject to its upstream licenses; repository licensing is documented in `LICENSE` and `NOTICE.md`.

An executable reconstruction of the frozen WP10 statistical analysis is maintained under `analysis/`. It was prepared after the campaign and Zenodo v1.0.0 publication but before journal submission. The original WP10 analysis source was not preserved; the reconstruction is explicitly labeled as such and regression-validates the manuscript-facing statistical contracts against preserved authoritative outputs without rerunning the experiment or changing Zenodo v1.0.0.

## Reproducibility

Reproducibility controls include frozen campaign cells and seeds, exact run IDs, version-pinned execution provenance, immutable per-run plans, an append-only authoritative attempt ledger, retained invalid attempts, explicit right-censoring, analysis-membership checksums, publication-output checksums, and a final-commit complete-block sensitivity analysis. The primary statistical population remains all 720 frozen VALID observations; the 696-observation final-commit analysis is a sensitivity check only.

The published Zenodo v1.0.0 archive is the evidence-of-record for this study phase. Any new experimental execution constitutes a new reproduction/replication and must not be represented as part of the original 720-observation statistical population.

## Funding

This research was conducted independently and received **no external funding**.

## Competing interests

The author declares no competing financial or non-financial interests.

## Author contributions

**Aman Kumar Singh:** Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing – original draft; Writing – review & editing; Visualization; Project administration.

`Funding acquisition` is omitted because the study reports no external funding. `Supervision` is not assigned because this is a single-author independent study.

## Acknowledgments

The author has no acknowledgments to add for this manuscript.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, the author used **OpenAI ChatGPT** to assist with manuscript organization, literature/source checking, editorial refinement, consistency checking, reproducibility documentation, and preparation of journal-submission materials. The author reviewed and edited the resulting content, independently checked scientific quantities and source claims against the frozen research record and cited sources, and takes full responsibility for the content of the publication.

OpenAI ChatGPT was also used after the experimental campaign and historical WP10 statistical findings had been frozen—and after the research-data package was published as Zenodo v1.0.0, but before journal submission—to assist with reconstructing, reviewing, and testing a public statistical reproducibility implementation from preserved derived inputs, outputs, and provenance records. The original executable WP10 analysis source was not recovered. This reconstruction did **not** generate campaign observations, consume campaign seeds, modify the 720-VALID statistical population, alter frozen WP9 evidence, or change historical statistical outputs. The reconstructed implementation was regression-validated against preserved reference artifacts and tested for reference-tamper rejection; it is identified as an independently reconstructed reproducibility implementation rather than the original analysis code.

The experimental P7 response mechanism itself is a frozen deterministic rule-based selector and does not use generative AI or machine learning.
