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

It contains the experiment design, software-in-the-loop policy/event implementation history, campaign governance records, analysis/manuscript controls, tests, reproducibility tooling, and aggregate publication artifacts. Raw `results/wp9/campaign/` evidence remains outside GitHub by design and is distributed through the Zenodo dataset above.

Repository-level environment and test instructions are maintained in `docs/REPRODUCIBILITY_GUIDE.md`. Third-party research infrastructure remains subject to its upstream licenses; repository licensing is documented in `LICENSE` and `NOTICE.md`.

## Reproducibility

Reproducibility controls include frozen campaign cells and seeds, exact run IDs, version-pinned execution provenance, immutable per-run plans, an append-only authoritative attempt ledger, retained invalid attempts, explicit right-censoring, analysis-membership checksums, publication-output checksums, and a final-commit complete-block sensitivity analysis. The primary statistical population remains all 720 frozen VALID observations; the 696-observation final-commit analysis is a sensitivity check only.

The published Zenodo v1.0.0 archive is the evidence-of-record for this study phase. Any new experimental execution constitutes a new reproduction/replication and must not be represented as part of the original 720-observation statistical population.

## Funding

This research was conducted independently and received **no external funding**.

## Competing interests

**To be completed by the author(s) before journal submission.** No competing-interest declaration is inferred by this repository.

## Author contributions

**To be completed after the final journal author list and target-journal contribution taxonomy are known.** The repository does not infer contribution credit beyond the verified archive creator metadata.

## Acknowledgments

**To be completed before journal submission.** Any acknowledgment of software projects, institutional resources, colleagues, reviewers, or infrastructure should be verified by the author(s) and should not imply endorsement.

## Use of generative AI / editorial assistance

Journal policies differ on disclosure of generative-AI-assisted drafting or editing. The final submission package should be checked against the selected journal's current policy and include any required disclosure. Scientific claims, numerical results, and source references remain subject to author verification regardless of editorial tooling.
