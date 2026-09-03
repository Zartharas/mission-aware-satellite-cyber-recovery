# Study 7 — Learned Selector Observability

**Experiment:** `S7-LSO-001`  
**Current status:** `CANONICAL_RESULTS_FROZEN_MERGED`  
**Canonical results merge:** PR #87 / `f582c36cc5747a6703ec651bb957bbfea5852a7e`  
**Accepted execution:** run `33689625480` / commit `f1530b0b2e81a5916adaf7ce808075156424dfb5`  
**Frozen population:** 1,033 exact observations (512 visible-state lattice + 512 corroboration lattice + 9 hidden-truth collision cases)  
**Independent audit:** PASS  
**Publication disposition:** separate AI/autonomy-compatible paper stream; not part of the current Computers & Security manuscript.  

Study 7 is a separate companion study. It does not modify or pool Studies 1–6 and is not part of the current Computers & Security manuscript.

The experiment asks whether a learned recovery selector can overcome the information boundary exposed by Study 2 V5 when the learned model receives exactly the same policy-visible inputs as the deterministic S1 selector. A second learned model receives one additional, explicitly independent corroboration bit.

The learner is deliberately transparent: deterministic empirical-risk minimization over a small integer linear-threshold hypothesis class. No neural network, reinforcement-learning environment, online exploration, attack optimizer, or external ML library is used.

The finite evaluation has three blocks:

- Block A exhausts all 256 eight-feature policy-visible states for the deterministic S1-equivalent binary decision and the visible-only learned selector.
- Block B exhausts all 512 nine-feature states for the corroboration-aware learned selector.
- Block C holds the eight-feature base state constant while changing hidden authorization truth and independent corroboration, including a V5-like signed-but-false collision and a correlated-corroboration failure case.

The research-only hidden authorization value is used only for adjudicating the objective endpoint. It is never supplied to D0, L0, or L1.

This study does not implement adversarial ML attacks, optimize perturbations, claim operational spacecraft autonomy, or establish that one ML architecture is globally superior. Because AI/ML is a significant scientific component, Study 7 is intended for a separate AI/autonomy-compatible venue rather than the current Computers & Security submission.
