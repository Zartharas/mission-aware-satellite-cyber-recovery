# S7E-AERC-MODEL-FREEZE-001 frozen model package

This directory is the durable repository equivalent of the reviewed model-freeze candidate.

- The two `.joblib.b64` files decode to the exact primary runtime bytes produced by candidate-of-record run 35939164352.
- Primary and audit runtime bytes were byte-identical per learner during the review.
- The semantic JSON files are the authoritative behavioral model identities.
- `dependency_inventory.json`, `prefit_binding.json`, `candidate_payload.json`, and `training_execution_record.json` preserve the execution provenance needed to verify the freeze.
- Do not deserialize the joblib payloads merely to verify the freeze. Hash verification is sufficient.
- Any future loading must use a trusted source, verify the decoded SHA-256 first, and use the bound compatible environment.
- E1/E2/C0 held-out inference is not authorized by this freeze.
