# 7. Declarations, Data Availability, and Reproducibility

## Ethics and human participants

The reported software-in-the-loop studies used no human participants and collected no human-subject data. They used synthetic identities, commands, mission states, evidence conditions, adversary states, and software-emulated contact behavior. Any future reuse of interview data or study of operator behavior is outside the present experiments and would require the applicable institutional determination before inclusion.

## Responsible-research and operational boundary

The experiments were conducted on researcher-controlled computing infrastructure using public/research software and isolated software networking. They did not access an operational spacecraft or ground station, use operational or stolen credentials, transmit or interfere with RF, intercept non-public communications, or use classified/proprietary mission telemetry. The studies do not authorize or demonstrate operational satellite exploitation, jamming, spoofing, flight certification, or production autonomous recovery.

Study-2 evidence-compromise conditions are bounded synthetic experiments. Producer compromise is represented through frozen research keys and software-generated evidence. The work does not evaluate real key theft, cryptanalytic strength, operational certificate infrastructure, or compromise of a real mission organization.

## Data availability

### Study 1

The complete responsible-release package supporting Study 1 is publicly available on Zenodo as **Version 1.0.0**:

**Version DOI:** <https://doi.org/10.5281/zenodo.22181540>  
**Concept DOI:** <https://doi.org/10.5281/zenodo.22181539>

The version-specific DOI identifies the exact archived Study-1 file set. The archive contains the frozen raw WP9 campaign evidence, publication-grade cryptographic integrity freeze, manuscript-facing publication/provenance artifacts, release documentation, manifest, and checksums.

The authoritative Study-1 campaign ledger contains 729 retained records: 720 VALID observations in the primary statistical population and 9 INVALID attempts retained as provenance but excluded from statistical membership. The 720-run statistical membership SHA-256 is:

`a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The authoritative Study-1 attempt-history ledger SHA-256 is:

`92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`

The deterministic complete Study-1 campaign-tree SHA-256 is:

`ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`

The Study-1 raw campaign is intentionally not duplicated in GitHub; Zenodo v1.0.0 remains its public evidence-of-record.

### Study 2

Study 2 has a separate frozen population of **3,872 VALID observations**, **0 INVALID attempts**, and **85 cells**. The immutable Phase-6 source-evidence artifact is identified by:

- GitHub Actions artifact ID: `9816191406`;
- artifact ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`;
- observations SHA-256: `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`;
- attempt-ledger SHA-256: `755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5`;
- trial-manifest SHA-256: `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`.

The exact source ZIP has completed responsible-release review with disposition **`APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`**. The review verified the 3,872-row ledger/observation membership and per-observation/file hash identities with zero mismatches and found no credentials, tokens, private keys, email addresses, URLs, IPv4 addresses, local absolute paths, human-subject data, operational spacecraft/RF data, proprietary mission telemetry, or unsafe ZIP paths. The review performed no campaign runtime and modified no frozen source-evidence record or scientific result. The repository-side review record is retained under `study2/release/phase6/`.

The source artifact remains a campaign-evidence object, not merely a manuscript table. The responsible-release review portion is complete; because the original Actions retention is temporary, the remaining archive requirement is a **responsible-release-reviewed, DOI-bearing durable archive** containing the exact approved Study-2 source ZIP. The journal submission package is not considered archive-complete until that ZIP is deposited, the publicly served ZIP checksum is independently verified, and the actual DOI/checksum identity is inserted here. The existing Study-1 Zenodo v1.0.0 record must not be described as containing Study 2, and no Study-2 DOI is claimed before it actually exists.

The frozen Study-2 Phase-7 statistical result ZIP is already retained durably in repository history at:

`study2/evidence/phase7/archive/study2-phase7-results-60f64327c45efda24cbb5b342f9d0eac908e1934.zip`

Its SHA-256 is:

`0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`

That ZIP contains the frozen cell summaries, primary contrasts, secondary contrasts, terminal-state summaries, generated analysis report, analysis summary, and output-hash manifest. It is an analysis-output archive and does not substitute for the separate source-evidence archive required above.

## Code availability

The research repository is publicly available at:

<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery>

Study-1 submission preparation retains the historical reproducibility-hardened snapshot:

<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/tree/99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc>

The Study-2 Phase-7 statistical implementation was frozen on `main` at:

`18207460fc5d419ad6a940f00db2df8610a5e5a0`

The canonical Phase-7 results were merged at:

`49c62cbed3fb8fc318e44d696faba1854ed6c21a`

The canonical Phase-7 closeout state was merged at:

`2bd3fb34ca709127e45ea9bffa8f516846d6c4b5`

The final journal-submission repository snapshot will be recorded after Study-2 source-evidence DOI publication/checksum verification and final submission-export validation. Later manuscript/release-documentation commits do not alter the frozen Study-1 or Study-2 statistical populations.

Repository-level environment and test instructions are maintained in `docs/REPRODUCIBILITY_GUIDE.md`. Third-party research infrastructure remains subject to its upstream licenses; repository licensing is documented in `LICENSE` and `NOTICE.md`.

## Reproducibility

Study-1 reproducibility controls include frozen campaign cells/seeds, exact run IDs, append-only attempt history, retained invalid attempts, explicit right censoring, analysis-membership checksums, publication-output checksums, and the 29-seed/696-observation final-commit sensitivity analysis. The primary Study-1 statistical population remains all 720 frozen VALID observations.

An executable reconstruction of the frozen Study-1 WP10 statistical analysis is maintained under `analysis/`. The original WP10 analysis source was not preserved. The reconstruction was prepared after the campaign and Zenodo v1.0.0 publication, starts from frozen derived analysis inputs, and regression-validates manuscript-facing statistical contracts against preserved authoritative outputs without rerunning the experiment or changing the historical population.

Study-2 reproducibility uses a different chain. The primary Phase-7 analyzer was hash-frozen before aggregate analysis. The immutable Phase-6 evidence ZIP was verified by SHA-256 before analysis. A separate standard-library auditor then recomputed the statistical outputs directly from the immutable observations without importing or invoking the primary analyzer. It reproduced all 85 numerical cell summaries, all 162 primary contrasts, all 432 secondary contrasts, all 432 Holm adjustments/rejection flags, and all 85 terminal-state distributions with **zero mismatches**. The independent auditor is retained as `study2/scripts/audit_phase7_independent.py` with SHA-256 `3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d`.

Neither study should be extended by appending new observations to its frozen population. Any new experimental execution constitutes a new study, replication, or validation phase and requires a separately frozen protocol and evidence identity.

## Funding

This research was conducted independently and received **no external funding**.

## Competing interests

The author declares no competing financial or non-financial interests.

## Author contributions

**Aman Kumar Singh:** Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing – original draft; Writing – review & editing; Visualization; Project administration.

`Funding acquisition` is omitted because the research reports no external funding. `Supervision` is not assigned because this is a single-author independent research program.

## Acknowledgments

The author has no acknowledgments to add for this manuscript.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During preparation of this journal work, the author used **OpenAI ChatGPT** to assist with manuscript organization, literature/source checking, editorial refinement, consistency checking, reproducibility documentation, repository/audit workflow support, and preparation of journal-submission materials. The author reviewed and edited the resulting content, checked scientific quantities and source claims against the frozen research record and cited sources, and takes responsibility for the publication.

For Study 1, OpenAI ChatGPT was used after the experimental campaign and historical WP10 statistical findings had been frozen—and after the Study-1 data package was published as Zenodo v1.0.0—to assist with reconstructing, reviewing, and testing a public statistical reproducibility implementation from preserved derived inputs, outputs, and provenance records. That reconstruction did not generate campaign observations, consume campaign seeds, change statistical membership, alter frozen WP9 evidence, or change historical statistical outputs.

For Study 2, ChatGPT-assisted workflow support was used after the campaign evidence and prospective Phase-7 analysis implementation were frozen to assist with executing the hash-bound analysis workflow, independently auditing/reproducing the generated statistical tables, reviewing claim boundaries, responsible-release review/documentation, and integrating the frozen results into the journal manuscript. These activities used the immutable observation artifact and did not generate or replace observations, alter seeds, change exclusions, modify the frozen analyzer, provide input to the experimental response policies, or authorize a new campaign.

The experimental Study-1 P7 and Study-2 response mechanisms are frozen deterministic rule-based research policies. They do not use generative AI or machine learning as a scientific response mechanism.
