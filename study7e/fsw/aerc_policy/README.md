# AERC Deterministic Policy Adapter

This pre-canonical cFS component consumes the shared policy-visible Study-7E snapshot contract and implements only the deterministic comparators:

- `D0_BASE`
- `D1_CORROBORATED`

The snapshot has 16 fixed binary feature slots. Base snapshots expose the first 9 features and require the remaining 7 slots to be zero. Corroborated snapshots expose all 16 features.

The same snapshot message bytes are intended to be the future paired input surface for `L0_BASE` and `L1_CORROBORATED`. No learned policy is implemented here.

The app rejects malformed sizes, contract drift, non-binary feature values, nonzero reserved bytes, and nonzero unused base slots. It contains no research-only truth, fault identity, topology identity, objective/correct action, production model, or canonical-execution logic.
