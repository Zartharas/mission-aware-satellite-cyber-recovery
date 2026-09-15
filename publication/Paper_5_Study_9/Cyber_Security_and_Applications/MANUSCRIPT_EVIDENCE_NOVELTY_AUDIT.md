# Paper 5 Manuscript Evidence and Novelty Audit

**Experiment:** `S9-RTSI-001`<br>
**Target journal:** Cyber Security and Applications<br>
**Audit date:** 2026-09-15<br>
**Scientific record:** frozen and not reopened<br>
**Submission authorization:** false

## Purpose

This publication-development audit checks manuscript claims against frozen Study 9 evidence and constrains novelty language.

## Scientific claim-to-evidence map

| Manuscript claim | Frozen evidence |
| --- | --- |
| 0/8 direct and 0/8 direct-or-derivable coverage for all three datasets | `coverage_summary.json` |
| Mapping-class counts and field-level rationales | `mapping_matrix.json` |
| 25,000 / 137,965 / 404,798 source rows and exact multiplicities | `native_state_groups.json`, `policy_strata.json` |
| One decision-equivalent native-state group per dataset | `native_state_groups.json` |
| Zero uniquely identifiable action fraction for all 12 dataset-policy strata | `policy_strata.json` |
| Reachable action-set cardinality 2 or 3 | `policy_strata.json` |
| Guaranteed sidecar cardinalities 6, 7, 7, and 8 | `policy_strata.json`, `guaranteed_sidecar.json` |
| All eight recovery variables are common unresolved state | `coverage_summary.json` |
| UNSW `Position_Anomaly` is ambiguous after population-wide validation | `mapping_matrix.json`, `study9/PROTOCOL_DEVIATION_UNSW_POSITION_ANOMALY_DOMAIN_20260915.json` |
| Accepted outputs are frozen and independently audited | `study9/results/RESULTS_FREEZE.json`, `independent_audit.json`, `output_sha256_manifest.json` |

## Closest prior-work boundaries

- Public satellite cybersecurity datasets/testbeds already exist: CuCD-ID, AegisSat, and UNSW-IoTSAT.
- Cross-dataset distribution-shift, transfer, and label-harmonization research already exists.
- Akbar et al. (ICISS 2023, DOI `10.1007/978-3-031-49099-6_2`) already uses semantic interoperability to unify heterogeneous cybersecurity resources.
- Bashendy et al. survey intrusion-response systems for cyber-physical systems.
- NIST SP 800-160 Vol. 2 Rev. 1 already frames cyber resilience around recovery and adaptation.
- NIST IR 8441 already applies Detect, Respond, and Recover concepts to hybrid satellite networks and emphasizes interfaces among independently operated segments.
- Sandia AIRSS work (`SAND2021-11864`) already develops real-time space-system cyberattack classification and mitigation-response selection; it is cited directly in the manuscript as prior response-selection work.

Paper 5 therefore does not claim novelty for datasets, cross-dataset evaluation, semantic interoperability, intrusion response, cyber recovery, space cyber resilience, or response selection individually.

## Defensible contribution boundary

> Paper 5 operationalizes a preregistered field-level recovery-state interface across independently sourced public space-cyber datasets, preserves missing decision state as unknown, propagates unresolved state through an exhaustive frozen downstream selector, and computes the minimum sidecar state sufficient to guarantee a unique action.

The reviewed literature did not identify a source combining all of those elements in one public-space-cyber dataset interoperability study. This is not a universal “first” claim.

## Prohibited novelty language

The manuscript must not claim to be the first satellite cybersecurity dataset study, first cross-dataset cybersecurity study, first semantic-interoperability framework, first intrusion-response/recovery framework, first space-system cyber-response mechanism, or first demonstration that missing information can affect security decisions.

## Preregistered RQ traceability

- **RQ1** maps to `Recovery-state coverage (RQ1)`.
- **RQ2** maps to `Policy-stratified action identifiability (RQ2)`.
- **RQ3** maps to `Guaranteed minimal sidecar state (RQ3)`.
- **RQ4** maps to `Cross-dataset common missing semantics (RQ4)`.

The manuscript uses the exact four RQ texts from `study9/STUDY9_PROTOCOL.json`; no research question was added, removed, or reworded for venue fit.

## Claim-boundary outcome

`PASS_WITH_NARROW_NOVELTY_BOUNDARY`

Scientific execution remains closed, frozen Study 9 artifacts remain unchanged, and publisher submission remains unauthorized.
