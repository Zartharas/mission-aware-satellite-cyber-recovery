# Study 7 Canonical Findings

**Experiment:** `S7-LSO-001`  
**Status:** `CANONICAL_RESULTS_FROZEN`

## Findings

1. **Learning alone did not overcome the Study-2 V5 observability limit.** The visible-only ERM learner (`L0`) recovered an exact S1-equivalent binary decision boundary with zero training error and zero error across all 256 possible eight-feature visible states. In the hidden-truth collision block, however, `D0` and `L0` both proceeded for the safe and V5 signed-but-false states because those states are identical in the eight policy-visible inputs.

2. **Independent corroboration changed the available information, not merely the model class.** The corroboration-aware learner (`L1`) withheld recovery in the `V5_INDEPENDENT_DISAGREEMENT` scenario and therefore avoided the unsafe proceed recorded for `D0` and `L0`.

3. **Corroboration introduced its own safety/availability boundary.** Across the exhaustive 512-state extended lattice, `L1` made exactly two objective decision errors: one unsafe proceed when corroboration was positive while objective authorization was false, and one false-conservative hold when corroboration was absent/negative while objective authorization was true.

4. **Correlated false corroboration restored the original failure.** When the V5 hidden authorization was false but both the ordinary policy-visible authorization and the additional corroboration signal asserted authorization, all three policies proceeded. Independent corroboration is therefore useful only to the extent that its trust failure is not correlated with the compromised evidence path.

5. **The result is an observability argument, not an ML superiority claim.** A learned selector cannot infer hidden truth from inputs that are observationally identical. Improving robustness requires additional trustworthy observables, trust diversity, or a different recovery architecture; increasing model complexity alone does not resolve the structural ambiguity represented here.

## Scope

The study is a deterministic finite ML-assurance experiment. It did not implement adversarial attack optimization, reinforcement-learning exploration, operational spacecraft autonomy, RF activity, or external targeting. The hidden authorization variable was used only for research adjudication. No global model ranking is claimed.

Because AI/ML is a significant scientific component, these findings remain a separate companion-study line and are not incorporated into the current Computers & Security manuscript.
