# Related-work firewall: separate TT&C post-compromise resynchronization study

**Recorded:** 2026-11-18. **Scope:** research provenance/overlap notice only, not a new mission-aware experiment, manuscript revision, submission-status change, or new scientific result.

## Authority and snapshot

This repository's `main` was observed at `7fd87eb1bbfb5ec811bb1f8ec29b4532ac5ff425`. `docs/CURRENT_PUBLICATION_STATE.md`, `README.md`, published/frozen experiment records and issue-specific publication trackers remain the authority for this repository. Nothing here supersedes them.

Separate research repository: [Zartharas/satcom-ttc-post-compromise-recovery](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery), `main` `1bda511862f104e82bddcbf95db1ee97702e6c02` at this snapshot. Its authoritative [new-chat handoff](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery/blob/handoff/taes-branch2-20261118/paper/submission/TAES_BRANCH2_NEXT_CHAT_HANDOFF_2026-11-18.md), [tracking issue #29](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery/issues/29) and draft PRs [#26](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery/pull/26), [#27](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery/pull/27), [#28](https://github.com/Zartharas/satcom-ttc-post-compromise-recovery/pull/28) govern its IEEE TAES preparation, not this mission-aware program.

## Differentiation and non-overlap

| Mission-aware repository | Separate TT&C paper | Forbidden substitution |
|---|---|---|
| Mission response selection, trust evidence qualification and temporal/sufficiency methods (Studies 1-9, S3X/S6X and separate extensions) | Frozen deterministic synthetic TT&C key-state resynchronization control under intermittent contacts, bounded retries, endpoint activation/verification and restart, Studies A-D | Do not relabel mission-aware schedules, ESA traces, external datasets, cFS/COSMOS fixtures or results as new TT&C experiment evidence. |
| Mission-aware P2X PRs #214/#215 are unmerged, governed separately, and contain NOS3/COSMOS/cFS exploratory work | Prospective `TTCSIL-SA-RST-001` SA/epoch restart and independently authenticated TC/TM extension | Existing nominal cFS/COSMOS NOOP or fixture work is **not** evidence for new TT&C SA recovery and may not be re-counted or repackaged. |
| Distinct submitted/rejected journal packages and frozen author decisions | Current TT&C manuscript is not yet submitted or fully publisher-format certified | Do not interpret this repo's historical Paper 2 TAES rejection (different manuscript, `TAES-2026-4182`) as a rejection of the TT&C manuscript. |

The mission-aware Paper 2 RevB CEAS Space Journal receipt/technical check described in the current status file remains independent; the historical TAES package is immutable. The mission-aware Paper 1 JAIS, Paper 3, Paper 4, Paper 5 and JSSE or other paper work must not be retroactively altered by this TT&C handoff.

## Release/safety boundary

- Do not share source evidence rows, unpublished raw retained bundles, private author details, journal correspondence or restricted derivative data between repositories without explicit rights and provenance clearance.
- Do not pool denominator populations, compare counts as if independent, silently reuse figures or claim independent replication by merely porting software.
- CCSDS 350.5-G-2 prior-art Recovery SA is acknowledged in the TT&C manuscript; neither program owns the concept of a Recovery SA.
- TT&C F1-F4 integration runtime remains **HOLD** pending exact NOS3/CryptoLib/cFE dependency graph, expected GVCID/SPI binding, message-length validation, process restart proof, dual-endpoint authentic evidence, and independent oracle. No joint deployment, RF, mission keys or unsafe simulator integration.
- This document **does not** modify any active publisher-facing package, frozen experiment, existing publication tracker, PR #214/#215 or journal deadline.

**Cross-chat action:** At the start of any related follow-up, refresh both live repository heads and publication states, use the TT&C issue #29 as the external anchor, and run a fresh comparison before treating a future TT&C extension as novel. Keep the original program's scientific and publication approvals independent.
