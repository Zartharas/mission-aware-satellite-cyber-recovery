# Security and Responsible Disclosure

This repository supports **controlled defensive research** in a software-in-the-loop environment. It is not an operational spacecraft exploitation project and must not be used as authority to test systems without permission.

## Supported security scope

Security reports are appropriate when they concern this repository itself, for example:

- an exposed credential or secret accidentally committed here;
- a dependency/configuration issue that materially affects the reproducibility environment;
- a defect that can cause the project's isolation or cleanup controls to fail;
- a repository script that can affect resources outside the documented project boundary;
- a privacy, rights, or archive-integrity problem in a published research artifact.

The current `main` branch is the supported repository state. The Zenodo v1.0.0 files are an immutable research record; file-level corrections to that archive should be handled as a new archive version rather than silently replacing the historical object.

## Do not submit sensitive material in public issues

Do **not** post any of the following in a public GitHub issue, discussion, pull request, or commit:

- real spacecraft, ground-station, or TT&C credentials;
- API tokens, cloud credentials, SSH keys, cookies, or session material;
- proprietary or non-public telemetry;
- classified, export-controlled, contract-restricted, or partner-sensitive information;
- production endpoints, network maps, mission schedules, or operator identities;
- unpublished vulnerabilities in operational spacecraft or ground systems;
- live RF interference, jamming, spoofing, or unauthorized command procedures;
- exploit material intended to enable unauthorized access to a real system.

If you discover such material in this repository, stop redistributing it and report it privately.

## How to report a repository security concern

Prefer GitHub's private security-reporting / security-advisory channel for this repository when the **Security** tab offers that option. If that option is not available, contact the repository owner privately through the GitHub profile rather than opening a public issue with sensitive details.

Include only the information needed to reproduce and contain the repository problem:

1. affected file, commit, release, or component;
2. concise description of the issue;
3. impact within the repository/research environment;
4. minimal reproduction steps using synthetic/local data;
5. suggested containment or remediation, if known;
6. whether you believe a secret or already-published artifact is affected.

Do not attach real operational credentials, proprietary telemetry, or unnecessary sensitive data as proof.

## Research isolation boundary

The reported experiment was designed around these constraints:

- researcher-controlled software simulation;
- isolated/project-labeled Docker resources;
- no operational spacecraft access;
- no operational ground-station access;
- no live RF transmission or interference experiment;
- no operational/stolen credentials;
- no classified or proprietary mission telemetry;
- synthetic/modelled mission, evidence, telemetry, and contact conditions.

A security report should preserve those boundaries. If reproducing a repository issue requires access to a real target, do not perform that test under this project's name or instructions.

## Secrets and accidental disclosure

If a credential or private key is found in Git history or an archive, deletion from the latest branch is not sufficient remediation. Treat the credential as compromised, revoke/rotate it at the authoritative service, preserve only the minimum evidence needed for the incident record, and coordinate any Git-history/archive correction separately.

The published Zenodo dataset should not be modified in place to conceal a problem. If an archive-level correction is required, use Zenodo's supported correction/versioning process and document the relationship between versions.

## Vulnerabilities in third-party projects

NOS3, cFS-related components, Fortytwo/42, Docker, Python packages, and other upstream projects are third-party dependencies or references. Report vulnerabilities in those projects through their own responsible-disclosure channels unless the issue is specifically caused by this repository's integration/configuration.

Do not publish an operationally sensitive upstream vulnerability here as a convenience issue.

## Public discussion after remediation

After a repository concern is contained, public documentation should disclose only what is necessary for transparency and reproducibility. It should not expose credentials, private infrastructure, or operational attack instructions.

## Related controls

- [`docs/05-legal-ethical-boundaries.md`](docs/05-legal-ethical-boundaries.md)
- [`docs/13-laboratory-rules-of-engagement.md`](docs/13-laboratory-rules-of-engagement.md)
- [`docs/13a-docker-roe-controls.md`](docs/13a-docker-roe-controls.md)
- [`release/RIGHTS_AND_MISUSE_REVIEW.md`](release/RIGHTS_AND_MISUSE_REVIEW.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
