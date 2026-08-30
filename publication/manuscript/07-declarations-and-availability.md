# 7. Declarations, Data Availability, and Reproducibility

## Ethics and human participants

The reported software-in-the-loop experiment used no human participants and collected no human-subject data. It used synthetic identities, commands, mission states, telemetry/evidence conditions, and software-emulated contact behavior. Any future reuse of interview data or study of operator behavior is outside the present experiment and would require the applicable institutional determination before inclusion.

## Responsible-research and operational boundary

The experiment was conducted on researcher-controlled computing infrastructure using public/research software and isolated software networking. It did not access an operational spacecraft or ground station, use operational or stolen credentials, transmit or interfere with RF, intercept non-public communications, or use classified/proprietary mission telemetry. The study does not authorize or demonstrate operational satellite exploitation, jamming, spoofing, flight certification, or production autonomous recovery.

## Data availability

The complete raw WP9 campaign evidence is not stored in the GitHub repository. The authoritative local campaign ledger and raw per-attempt tree were cryptographically frozen after campaign completion. The ledger contains 729 retained records (720 VALID and 9 INVALID), and the 720-run statistical membership is identified by SHA-256:

`a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The authoritative attempt-history ledger SHA-256 is:

`92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`

The deterministic complete local campaign-tree SHA-256 is:

`ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`

Aggregate publication tables, figures, study contracts, provenance records, and manuscript claim controls are maintained in the project repository. A DOI-bearing archive deposit of the responsible release package is planned through Zenodo. This statement must be updated with the final version DOI/concept DOI and verified archive checksums before journal submission. Until that deposit is completed, the manuscript must not state that the full raw campaign is publicly available.

## Code availability

The research repository contains the experiment design, software-in-the-loop policy/event implementation history, campaign governance records, analysis/manuscript controls, and aggregate publication artifacts. Raw `results/wp9/campaign/` evidence remains outside GitHub under the repository's raw-results boundary. The release scope of event-injection and runtime artifacts remains subject to WP11 licensing, secrets, misuse-risk, and responsible-release review.

## Reproducibility

Reproducibility controls include frozen campaign cells and seeds, exact run IDs, version-pinned execution provenance, immutable per-run plans, an append-only authoritative attempt ledger, retained invalid attempts, explicit right-censoring, analysis-membership checksums, publication-output checksums, and a final-commit complete-block sensitivity analysis. The primary statistical population remains all 720 frozen VALID observations; the 696-observation final-commit analysis is a sensitivity check only.

## Funding

**To be completed from author/project funding information before submission.** No funding source is inferred by this repository.

## Competing interests

**To be completed by the author(s) before submission.** No competing-interest declaration is inferred by this repository.

## Author contributions

**To be completed after the final author list and target-journal contribution taxonomy are known.** The repository does not infer authorship or contribution credit.

## Acknowledgments

**To be completed before submission.** Any acknowledgment of software projects, institutional resources, colleagues, reviewers, or infrastructure should be verified by the author(s) and should not imply endorsement.

## Use of generative AI / editorial assistance

Journal policies differ on disclosure of generative-AI-assisted drafting or editing. The final submission package should be checked against the selected journal's current policy and include any required disclosure. Scientific claims, numerical results, and source references remain subject to author verification regardless of editorial tooling.