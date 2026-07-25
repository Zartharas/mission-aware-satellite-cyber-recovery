# Mission-Aware Satellite Cyber Response and Trusted Recovery

This repository is the working research environment for a theory-informed, hands-on study of how cyber-response policies affect containment, mission continuity, and trusted recovery in a simulated small-satellite system under intermittent ground contact.

## Current status

- Research topic selected
- Initial novelty and legal scrutiny completed
- Repository scaffold created
- Literature validation and threat/mission modeling in progress
- No operational satellite systems, RF transmissions, proprietary telemetry, or production credentials are in scope

## Core research question

How do different cyber-response strategies affect security containment, trusted recovery, and mission continuity under varying spacecraft states and ground-contact conditions?

## Study design

The study is planned as:

1. A theory-informed design-science investigation grounded in published practitioner findings.
2. A controlled software-in-the-loop experiment using a small-satellite digital twin.
3. A multi-objective evaluation of cybersecurity, safety, mission continuity, and recovery outcomes.
4. A reproducible research artifact containing code, configuration, synthetic data, and analysis scripts.

The study should be called mixed methods only if the paper formally reanalyzes the original interview data and integrates that analysis with the experiment under an appropriate institutional determination. Otherwise, the safer description is **a theory-informed design-science study with controlled simulation evaluation, grounded in prior qualitative findings**.

## Repository policy

- Keep the repository private during early development.
- Do not commit raw third-party datasets.
- Store only download manifests, checksums, citation metadata, and transformation scripts.
- Do not copy NASA NOS3 or cFS source code into this repository.
- Use pinned upstream checkouts or submodules and retain all original licenses.
- Do not publish exploit code that could be directly applied to operational systems.
- No live RF transmission, jamming, spoofing, or operational satellite access.

## Local path

```text
/Users/zarthras/Documents/Development Projects/Satellite-Cybersecurity-Research/mission-aware-satellite-cyber-recovery
```

## Repository structure

```text
docs/        Research design, literature, methodology, legal and data-source records
tracker/     Work-package tracker, risk register, and decision log
references/  BibTeX and citation records
scripts/     Mac bootstrap and environment checks
src/         Project-owned experiment and analysis code
configs/     Versioned non-secret experiment configurations
data/        Ignored local data with manifest only
results/     Ignored raw results with approved summaries only
artifacts/   Reproducibility manifests and release metadata
```

## Immediate priorities

1. Complete the focused literature matrix.
2. Finalize the theoretical and conceptual model.
3. Freeze the threat model, mission states, safety invariants, and response policies.
4. Select and validate the simulator baseline.
5. Run a nominal-operations pilot before implementing cyber-event injection.

See `tracker/RESEARCH_TRACKER.md`.
