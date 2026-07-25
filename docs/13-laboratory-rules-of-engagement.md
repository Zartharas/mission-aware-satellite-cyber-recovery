# Laboratory Rules of Engagement — Draft 0.1

## Status

Draft for a software-only academic research environment. This document defines the authority, constraints, stop conditions, and evidence-handling rules for controlled testing. It is not legal advice and does not authorize testing of any external or operational system.

## Purpose

The laboratory will evaluate synthetic cyber-response and trusted-recovery scenarios in an isolated small-satellite simulation. NIST SP 800-115 defines Rules of Engagement as detailed guidelines and constraints established before a security test that provide authority for defined activities. This ROE adopts that control principle for the project.

## Authorized owner and environment

- Asset owner: Researcher-owned local computing environment
- Project repository: `Zartharas/mission-aware-satellite-cyber-recovery`
- Local project root: `/Users/zarthras/Documents/Development Projects/Satellite-Cybersecurity-Research/mission-aware-satellite-cyber-recovery`
- Execution environment: Dedicated Linux virtual machine or container environment on researcher-owned hardware
- Network scope: Host-only or otherwise isolated virtual network
- Simulator scope: Publicly licensed software pinned to recorded versions
- Data scope: Synthetic data and separately licensed public datasets used according to recorded terms

## Authorized activities

The following activities are authorized only inside the defined isolated environment:

- Execute nominal command and telemetry workflows
- Create synthetic identities, keys, certificates, commands, telemetry, software packages, and mission states
- Inject frozen event families E1, E4, and E6
- Emulate delay, loss, ordering changes, and missed contact windows in software
- Suppress or stale selected synthetic telemetry and trust evidence
- Trigger bounded safe-mode and rollback workflows
- Record commands, state transitions, resource values, response actions, and recovery evidence
- Reset the environment to a clean, verified snapshot
- Analyze sanitized generated results

## Prohibited activities

- Accessing any operational spacecraft, satellite service, ground station, user terminal, or mission network
- Live RF transmission, intentional interference, jamming, spoofing, overshadowing, or unauthorized reception
- Use of production or stolen credentials, keys, certificates, firmware, or telemetry
- Scanning or testing public or third-party systems
- Use of classified, export-controlled, leaked, proprietary, or unlawfully obtained data
- Circumvention of access controls outside the isolated laboratory
- Testing against employer, university, cloud, or partner systems without separate written authorization
- Publishing sensitive exploit procedures that materially enable abuse of operational systems
- Modifying the immutable experiment-control zone during a trial

## Authorized event scope

| Event | Authorized implementation | Prohibited implementation |
|---|---|---|
| E1 Unauthorized/replayed command | Synthetic identity and laboratory command catalogue | Real credentials or operational command formats obtained without authorization |
| E4 Modified/unauthorized update | Synthetic package, test signing authority, version downgrade, interrupted transfer | Proprietary firmware, production signing keys, operational update service |
| E6 Telemetry suppression | Software drop/delay/staleness in virtual data path | RF interference, interception, or operational telemetry manipulation |

## Test roles

A single researcher may perform multiple roles during development, but the records must identify the role for each action.

- Test director: Approves campaign scope and stop conditions
- Environment owner: Controls the host, VM/container, and snapshots
- Scenario operator: Starts trials and event injection
- Evidence custodian: Preserves raw logs, manifests, and checksums
- Analyst: Performs statistical and qualitative failure analysis
- Red-team reviewer: Challenges assumptions and confirms that scenarios do not encode the intended conclusion

Before the final campaign, at least one independent review should cover the threat model, policy logic, and exclusion rules.

## Pre-test requirements

A trial or campaign may begin only when:

- The repository working tree is clean or the exact development commit is recorded
- Simulator and flight-software commits are pinned
- The VM/container or snapshot identifier is recorded
- The experiment configuration validates against `configs/experiment_run.schema.json`
- The network is confirmed isolated
- No real credentials or secrets are present
- The event and response policy are within the frozen catalogue
- Stop conditions and expected duration are configured
- Available disk space is sufficient for immutable logs
- System time and run identifier are recorded

## Execution constraints

- Scenario order must follow the randomized campaign schedule.
- The event orchestrator and append-only ground-truth log remain inaccessible to the modeled adversary.
- P7 may use only declared policy-visible inputs, not immutable ground truth.
- No manual correction of policy decisions is allowed during a scored run.
- Manual emergency termination is allowed and must be logged.
- Trial settings cannot be changed after event activation.
- Failed runs cannot be silently rerun or deleted; they receive a terminal classification and reason.

## Stop conditions

Immediately terminate the trial or campaign when:

- Any process attempts to connect outside the authorized virtual network
- An antenna, SDR transmit path, or intentional radiator becomes involved
- A real credential, proprietary artifact, or sensitive data source is discovered
- The event orchestrator or immutable log is modified unexpectedly
- Host stability or storage integrity is at risk
- The simulator enters an unbounded loop not covered by the configured trial limit
- Snapshot restoration cannot be verified
- A trial produces effects outside the declared synthetic environment
- A license, export, human-subjects, or data-use concern arises that is not covered by the current record

A stopped run is classified `RUN_INVALID` unless the stop was a modeled scientific terminal event already defined as `MISSION_LOSS` or `RECOVERY_FAILED`.

## Emergency shutdown

The environment must support:

1. Stop the experiment orchestrator
2. Stop or pause the VM/container
3. Disable the virtual network
4. Preserve logs and volatile diagnostics where safe
5. Record the reason and operator action
6. Restore only from the approved clean snapshot

Emergency shutdown commands will be documented after the WP4 platform is selected.

## Data handling

- Raw third-party datasets remain outside Git and follow their licenses.
- Generated raw trial logs remain in ignored storage.
- Every released data product receives a manifest, checksum, license, and provenance note.
- Secrets, private keys, and credentials are synthetic and must not be committed.
- The public artifact will exclude information that creates unnecessary operational misuse risk.
- Raw runs are append-only after completion.
- Corrections are represented as new derived artifacts, not edits to original raw records.

## Incident handling

An incident is any unexpected access, network connection, data exposure, secret discovery, license concern, or escape from the declared environment.

Response steps:

1. Stop testing
2. Isolate the environment
3. Preserve evidence
4. Record date, time, affected assets, and actions
5. Rotate any potentially exposed non-synthetic credential
6. Notify the relevant owner or institution when applicable
7. Obtain review before resuming

## Publication and disclosure

Before making the repository or artifacts public:

- Complete a license audit
- Complete a secrets scan
- Confirm that no third-party raw datasets are redistributed without permission
- Review event-injection and recovery code for misuse risk
- Remove system-specific identifiers and local paths where inappropriate
- Document external-validity limits
- Coordinate disclosure for any previously unknown issue in third-party software
- Confirm whether export-control or institutional review is required

## Scope changes requiring a new ROE

A new or amended ROE is mandatory before adding:

- Human participants or operator-performance measurements
- Reanalysis of non-public interview transcripts
- Physical spacecraft hardware
- SDR hardware or any RF path
- Cloud or institutional systems
- Proprietary software, firmware, or telemetry
- External collaborators with access to controlled technical material
- New event families beyond the frozen catalogue

## Approval record

This draft becomes operational only after the researcher records approval in `tracker/decision_log.csv` and the WP4 environment-specific shutdown commands and network-isolation checks are added.
