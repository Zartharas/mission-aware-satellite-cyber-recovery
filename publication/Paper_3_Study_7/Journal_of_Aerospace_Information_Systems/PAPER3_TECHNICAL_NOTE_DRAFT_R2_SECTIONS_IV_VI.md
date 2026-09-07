# Paper 3 / Study 7 — Technical Note Draft R2, Sections IV-VI

**Companion to:** `PAPER3_TECHNICAL_NOTE_DRAFT_R1A_SECTIONS_I_III.md`  
**Status:** `R2__SECTIONS_IV_VI__FROZEN_RESULTS_ONLY__CLAIM_AUDIT_REQUIRED`

## IV. Results

### A. Visible-State Equivalence

Block A evaluates the fixed visible-only comparator (`D0_S1_VISIBLE_ONLY`) and the visible-only learned selector (`L0_ERM_VISIBLE_ONLY`) on every one of the 256 possible eight-feature policy-visible states. Each policy therefore contributes 256 observations to the block.

Both policies produced zero objective-decision errors over the complete visible-state lattice. Each policy proceeded in exactly three of the 256 states and held in the remaining 253. Neither policy produced an unsafe proceed or a false-conservative hold in Block A. Thus, `L0_ERM_VISIBLE_ONLY` reproduced the complete visible decision boundary used by the deterministic comparator, not merely the 10 prototypes used during deterministic ERM training.

This result establishes visible-state equivalence within the frozen model. It does not establish correctness against truth that is absent from those eight inputs. That distinction is tested separately in Block C.

### B. Corroboration-Aware State Space

Block B evaluates `L1_ERM_WITH_INDEPENDENT_CORROBORATION` over all 512 combinations of the eight base features and the additional corroboration bit. The learned selector produced six proceed decisions and 506 holds. Across the complete lattice, it made exactly two objective-decision errors: one unsafe proceed and one false-conservative hold.

Both errors occurred in the fully qualifying evidence-quality state with `security_signal=1`, where the visible authorization and corroboration bits disagreed. When `authorization_available=0` but `independent_corroboration=1`, L1 proceeded although the adjudicated objective was false, producing the single unsafe proceed. When `authorization_available=1` but `independent_corroboration=0`, L1 held although the adjudicated objective was true, producing the single false-conservative result. These are exact finite-state outcomes, not estimated error rates.

Table II summarizes the complete block-level counts.

**Table II. Exact finite-population outcomes**

| Block | Policy | N | Objective-decision errors | Unsafe proceed | False-conservative hold | Proceed decisions |
|---|---|---:|---:|---:|---:|---:|
| A | `D0_S1_VISIBLE_ONLY` | 256 | 0 | 0 | 0 | 3 |
| A | `L0_ERM_VISIBLE_ONLY` | 256 | 0 | 0 | 0 | 3 |
| B | `L1_ERM_WITH_INDEPENDENT_CORROBORATION` | 512 | 2 | 1 | 1 | 6 |
| C | `D0_S1_VISIBLE_ONLY` | 3 | 2 | 2 | 0 | 3 |
| C | `L0_ERM_VISIBLE_ONLY` | 3 | 2 | 2 | 0 | 3 |
| C | `L1_ERM_WITH_INDEPENDENT_CORROBORATION` | 3 | 1 | 1 | 0 | 2 |

### C. Hidden-Truth Collision Cases

Block C holds the original eight policy-visible inputs fixed at the same fully qualifying vector in all three scenarios. `signature_valid`, `source_trusted`, `fresh`, `epoch_valid`, `noncontradictory`, `minimum_evidence_complete`, `security_signal`, and `authorization_available` are all equal to one. Only research-only hidden authorization and, for L1, the corroboration bit distinguish the scenarios.

In `SAFE_CORROBORATED`, hidden authorization is true and corroboration is positive. The adjudicated objective is therefore safe-to-proceed. D0, L0, and L1 all proceed, and all three decisions are correct.

In `V5_INDEPENDENT_DISAGREEMENT`, policy-visible authorization remains true but hidden authorization is false. D0 and L0 receive exactly the same eight visible inputs as in the safe case and both proceed, producing one unsafe proceed each. L1 receives the additional corroboration value of zero and holds, matching the adjudicated objective and avoiding the unsafe proceed.

In `V5_CORRELATED_FALSE_CORROBORATION`, hidden authorization remains false, but the corroboration bit is set to one along with the already false policy-visible authorization. D0 and L0 again proceed unsafely. L1 also proceeds, restoring the unsafe outcome seen in the visible-only policies.

**Table III. Prespecified hidden-truth collision scenarios**

| Scenario | Visible authorization | Hidden authorization | L1 corroboration | Objective | D0 | L0 | L1 |
|---|---:|---:|---:|---:|---|---|---|
| `SAFE_CORROBORATED` | 1 | 1 | 1 | Proceed | Proceed | Proceed | Proceed |
| `V5_INDEPENDENT_DISAGREEMENT` | 1 | 0 | 0 | Hold | Proceed (unsafe) | Proceed (unsafe) | Hold |
| `V5_CORRELATED_FALSE_CORROBORATION` | 1 | 0 | 1 | Hold | Proceed (unsafe) | Proceed (unsafe) | Proceed (unsafe) |

Together, the three blocks answer RQ1 in two parts. First, exact learning of the visible decision boundary did not remove the signed-but-false collision because D0 and L0 were observationally identical across the safe and hidden-false states. Second, adding corroboration changed the available information and resolved the prespecified independent-disagreement case, but the protection disappeared when the corroboration path shared the false state. Block B further shows that making corroboration decision-relevant creates its own safety/availability trade-off when corroboration disagrees with the adjudicated authorization state.

## V. Discussion and Limitations

The central result is an information-sufficiency result rather than a model-performance result. `L0_ERM_VISIBLE_ONLY` achieved zero training error and zero error over all 256 visible states, yet those facts provided no protection in the hidden-truth collision because the relevant distinction was not present in the model input. In the frozen `V5_INDEPENDENT_DISAGREEMENT` case, D0 and L0 saw the same fully qualifying eight-feature vector that they saw in the safe case. Their identical unsafe decisions therefore reflect an observability boundary rather than a failure to fit the visible rule.

`L1_ERM_WITH_INDEPENDENT_CORROBORATION` changed the decision only because the input changed. In the independent-disagreement case, the additional zero-valued corroboration bit distinguished the hidden-false state from the safe corroborated state, allowing L1 to hold. This should not be interpreted as evidence that a learned policy is intrinsically safer than a deterministic one. The result instead shows that decision correctness can depend on whether a trustworthy observable exists for the hidden condition being adjudicated.

The complete nine-feature lattice also prevents a one-sided interpretation of corroboration. L1's two Block-B errors occurred precisely when corroboration and visible authorization disagreed in an otherwise fully qualifying security state. Positive corroboration with false adjudicated authorization produced an unsafe proceed, whereas absent corroboration with true adjudicated authorization produced a false-conservative hold. The added observable therefore shifts part of the trust burden rather than eliminating it. In the correlated-false-corroboration collision, that shifted dependency is exposed directly: when both visible authorization and corroboration assert the same false state, L1 again proceeds unsafely.

For assurance of learned aerospace recovery logic, the implication is that evaluation should trace not only model fit but also the provenance, observability, and failure relationships of decision-relevant evidence. This is consistent with broader aerospace ML-assurance guidance that treats confidence as a lifecycle evidence problem spanning requirements, data/model properties, integration, coverage, traceability, robustness, and V&V [3]. Study 7 does not establish a certification method or sufficient certification evidence. It provides a small, transparent example of why a learned recovery decision can remain bounded by the evidence architecture in which it operates.

Several limitations are deliberate. The learner is a deterministic integer linear-threshold model rather than a neural network or stochastic learner. The state variables are binary, the evaluation space is synthetic and finite, and the study does not introduce measurement noise, distribution shift, timing uncertainty, packet loss, sensor dynamics, or continuously valued evidence. The experiment contains no real spacecraft telemetry, RF activity, hardware-in-the-loop platform, flight software deployment, ground-station experiment, CPU or energy benchmark, or operational latency measurement. It also does not evaluate anomaly-detection performance; `security_signal` is treated as an already available policy input.

Most importantly, the `independent_corroboration` variable is independent by experimental construction, not by empirical demonstration of a real mission architecture. The Block-C correlated-failure case intentionally shows why that distinction matters. A future prospectively designed study could evaluate how corroboration independence is established or degraded across real or high-fidelity evidence producers, noisy observables, learned representations, and mission-specific trust paths. Such work would constitute new evidence and is outside the frozen Study-7 population.

These limitations constrain external validity but do not weaken the finite-population claim itself. Within the frozen model, all possible eight-feature visible states and all possible nine-feature corroboration states are evaluated, and the three prespecified collision scenarios are exact. The appropriate interpretation is therefore exhaustive coverage of the modeled decision spaces, not statistical inference to an operational spacecraft population.

## VI. Conclusion

Study 7 evaluated whether a learned satellite cyber-recovery selector can overcome a signed-but-false evidence boundary using the same policy-visible state as a deterministic comparator, and what changes when an additional corroborating observable is introduced. The visible-only learner exactly reproduced the complete eight-feature decision boundary, but it remained unable to distinguish safe and hidden-false states that were identical in those inputs. Independent disagreement became distinguishable only when corroboration was added; when corroboration shared the false state, the unsafe decision returned.

The assurance implication is bounded but direct: validating the learned decision rule is not sufficient when correctness depends on truth outside the model's observables. Adding evidence can change that boundary, but it also creates a new trust dependency whose failure relationship must itself be justified. These results are exact for the 1,033-position frozen model and do not establish operational spacecraft performance or certification sufficiency. Future work should test the same information-sufficiency question in prospectively designed, higher-fidelity recovery architectures with empirically grounded evidence dependencies.