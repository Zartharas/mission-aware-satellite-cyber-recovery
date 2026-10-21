# S7E-AERC-001 Qualifier/Fault Host Feasibility Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Qualification head:** `613128f95a33c712dac85c6e458b9fc2f7b5d463`  
**Scope:** host-only contract feasibility  
**Canonical execution:** NOT AUTHORIZED

## Result

**Draft qualifier time/replay and F0-F12 transformation contract harness: PASS**

## Evidence

- workflow: `Study 7E qualifier fault feasibility`
- workflow ID: `365368346`
- run ID: `35898052702`
- job ID: `107306900171`
- artifact ID: `10768381197`
- artifact digest: `sha256:73bb799e199a44dd672e535fd2ec36d178710c55ace354841cc1ac85467ac0be`
- tests: `17` passed
- fault profiles represented: `13`

Observed gate markers:

- `qualifier_fault_contract_tests=PASS`
- `fault_profiles_tested=13`
- `policy_decisions_executed=0`
- `production_models_trained=false`
- `study7e_scientific_scenarios_executed=0`
- `scientific_results_generated=false`

## What the gate checks

- qualifier API excludes research-truth/fault/topology inputs;
- absent and wrong-scenario evidence fail closed;
- structurally complete invalid-signature evidence preserves the independent authorization claim;
- freshness is parameterized by controlled logical time;
- exact duplicates are idempotent;
- same-sequence different-body evidence creates sticky contradiction;
- lower-sequence valid evidence creates replay/ordering inconsistency;
- invalid signatures do not advance authenticated sequence state;
- F5 makes the targeted path stale without changing signature/trust/authorization;
- F9 produces signature-invalid + epoch-invalid structurally complete evidence;
- F11 combines false authorization with transport-induced signature/epoch invalidity;
- F12 produces valid same-sequence equivocation and `noncontradictory=0`;
- T0 shared-domain faults propagate to both paths where defined;
- T4 separate-domain faults remain path-local;
- all 13 profile propagation sets agree with the existing `affected_paths()` implementation.

## Boundary

This is implementation-contract evidence only.

It does not freeze:

- numeric freshness threshold;
- logical-time scale;
- epoch mapping;
- scenario/source/key/authority registries;
- experiment keys;
- F0-F12 byte transformations;
- policy binding;
- learned models;
- protocol/environment;
- canonical execution.

No Study-7E scientific observation or endpoint was computed.
