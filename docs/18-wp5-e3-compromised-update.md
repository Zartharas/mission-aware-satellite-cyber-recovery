# WP5 E3 — Compromised Update Artifact

## Evidence basis

SPARTA `IA-0007.01` describes compromise of an on-orbit update through manipulation of source, build/configuration, onboard table or memory values, or replacement of compiled update artifacts. `EX-0004` additionally motivates integrity and downgrade controls around persistent boot/update material.

The pinned NOS3 revision provides a concrete spacecraft-patching workflow in `docs/wiki/Scenario_Patching.md`. It identifies a built RTS at `fsw/build/exe/cpu1/cf/sc_rts006.tbl`, then describes CFDP upload to the cFS/operator path `/cf/sc_rts006.tbl`. The pinned cFS startup configuration loads both CF and FM.

In the validated Docker runtime the NOS3 tree is mounted at `/work/nos3`. Therefore E3 treats:

- cFS virtual/operator path: `/cf/mission-aware-e3-candidate.pkg`
- Linux backing path: `/work/nos3/fsw/build/exe/cpu1/cf/mission-aware-e3-candidate.pkg`

The backing directory is verified at runtime before staging.

## Canonical WP5 variant

E3 uses a non-executable synthetic mission-table package:

- approved version: `2.0.0`;
- candidate claims the same version;
- candidate payload bytes are modified;
- immutable manifest retains the approved SHA-256;
- the approved package validates;
- the modified package is rejected for `sha256_mismatch`.

A downgrade package is also covered by unit tests and must fail both approved-version and minimum-version checks.

## Simulator adapter

The runtime adapter reuses the accepted nominal NOS3 topology.

It stages the approved control artifact into the Linux backing path for cFS `/cf`, proves the in-container SHA-256 equals the approved manifest, removes the control, then stages the tampered artifact at the same backing path and proves:

1. the simulator contains exactly the tampered bytes;
2. the tampered hash differs from the approved hash; and
3. the research verifier rejects the candidate.

Direct Docker staging is an experiment-injection mechanism. It does not claim that Docker access models an attacker or that the file was transported by CFDP. NOS3's documented CFDP workflow establishes that `/cf` is a legitimate patch destination; transport-specific testing is not required for the WP5 integrity event.

## Pre-stage development abort

An earlier development run passed local approved/tampered artifact checks but aborted before simulator staging because the harness incorrectly tested for literal Linux directory `/cf`. That run contributes artifact-validation evidence only and is not counted as the E3 runtime result.

## Why WP5 does not activate the tampered artifact

The compromised artifact is non-executable and is removed without rebooting cFE or loading it. WP5 needs a deterministic compromised-update event and observable integrity failure.

Activation, rollback, approved-version restoration, and independent trusted-recovery verification belong to WP7, where they directly test the paper's recovery hypotheses.
