# Rebuilt Paper 3 — Frozen Claim Ledger R1

**Paper:** Paper 3  
**Studies:** S7-LSO-001 and S7E-AERC-001  
**Purpose:** source-bind every central manuscript claim before venue-specific editing.

| ID | Allowed manuscript claim | Frozen authority | Prohibited escalation |
|---|---|---|---|
| S7-C1 | L0 reproduced the complete Study-7 visible decision boundary with zero training error and zero error across all 256 visible states. | study7/results/RESULTS_FREEZE.json; CANONICAL_FINDINGS.md | Do not claim general ML correctness. |
| S7-C2 | In the hidden-truth collision, D0 and L0 could not distinguish safe and signed-but-false states with identical eight-feature inputs. | Study-7 Block C | Do not claim a new general theorem of partial observability. |
| S7-C3 | L1 avoided the unsafe proceed in V5_INDEPENDENT_DISAGREEMENT because the corroboration input changed the observable state. | Study-7 Block C | Do not attribute this to learned-policy superiority. |
| S7-C4 | Correlated false corroboration restored unsafe proceed for D0, L0, and L1. | Study-7 Block C | Do not infer real-world compromise probabilities. |
| S7E-C1 | D0/L0 and D1/L1 received byte-identical paired policy-visible inputs in all 196 held-out scenarios. | S7E result checkpoint + input hashes | Do not claim all implementations are otherwise identical. |
| S7E-C2 | The held-out execution contained 196 valid scenarios and 784 policy decisions with zero invalid scenarios and zero audit mismatches. | S7E-AERC-HELDOUT-RESULTS-001 | Do not pool these with Study 7. |
| S7E-C3 | Overall exact counts were D0 40/9/31, L0 47/21/26, D1 49/4/45, L1 43/31/12 for error/unsafe/FCH. | exact_endpoint_counts.json | Do not rank policies globally. |
| S7E-C4 | D0/L0 disagreed in 67/196 and D1/L1 in 72/196 despite equal paired inputs. | paired_disagreements.json | Do not claim learned or deterministic superiority. |
| S7E-C5 | D1 reduced aggregate unsafe proceeds by 5 relative to D0 while adding 14 false-conservative holds; L1 increased unsafe proceeds by 10 relative to L0 while reducing false-conservative holds by 14. | result checkpoint | Do not collapse to a scalar utility score. |
| S7E-C6 | In common F6-F12 topology-controlled scenarios, D1 removed one unsafe proceed only at T4; L1 unsafe proceeds rose from 3/28 at T0 to 6/28 at T4. | topology_fault_tables.json | Do not claim monotonic benefit from separation. |
| S7E-C7 | F10 shows deterministic common-cause collapse while authority remains shared T0-T3 and one unsafe-proceed reduction at authority-separated T4. | topology_fault_tables.json | Do not generalize F10 to every common-cause fault. |
| S7E-C8 | F12 is an adverse learned-transfer case: L0 remains error-free while L1 incurs one unsafe proceed at each T1-T4. | topology_fault_tables.json | Do not hide or relabel as improvement. |
| S7E-C9 | C0 has all four policies HOLD in all eight no-signal scenarios with zero error. | exact_endpoint_counts.json | Do not omit because it is null. |
| SYN-C1 | Study 7 establishes an information-sufficiency boundary; Study 7E shows that architecture and selector behavior jointly determine how added information behaves under compromise. | Both frozen studies | Interpretive synthesis only; no pooled statistic. |
| SYN-C2 | Corroboration is not a universal safety mechanism; its effect depends on selector behavior and failure relationships among trust domains. | Study 7 correlated case + Study 7E stratified results | Do not claim corroboration is generally harmful or beneficial. |
| SYN-C3 | Greater experimental trust-domain separation is not monotonically associated with better policy-level outcomes in Study 7E. | common F6-F12 table | Do not infer real deployed-system monotonicity. |

## Frozen hypothesis disposition for Study 7E

- H1: SUPPORTED
- H2: PARTIALLY SUPPORTED
- H3: PARTIALLY SUPPORTED
- H4: PARTIALLY SUPPORTED
- H5: SUPPORTED

## Global prohibited claims

The rebuilt manuscript must not assert:

- a global policy winner;
- global ML superiority or inferiority;
- universal corroboration benefit;
- monotonic safety benefit from greater trust separation;
- operational spacecraft safety/failure/recovery probabilities;
- flight qualification or certification sufficiency;
- NASA endorsement;
- measured RF-link, CPU, energy, latency, or hardware performance;
- trust-domain independence beyond the instantiated experimental identities;
- external replication merely from same-repository independent auditing.
