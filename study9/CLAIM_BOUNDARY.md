# Study 9 Claim Boundary

**Study:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Status:** `BOUNDARY_DRAFT_BEFORE_SCHEMA_LOCK`

## Permitted scientific claim classes

If later supported by frozen Study 9 results, the study may report:

- whether a required recovery-state variable is directly represented, deterministically derivable under a preregistered rule, ambiguous, or absent in an included dataset;
- exact per-dataset recovery-state coverage counts and fractions under the Study 9 rubric;
- which recovery-state semantics are commonly missing across the included independent datasets;
- the size of the set of downstream recovery actions that remains admissible when unresolved decision state is left unknown;
- the fraction of analyzed native records or states for which the bounded downstream action is uniquely identifiable;
- the minimal additional state variables required to make that bounded downstream action uniquely identifiable;
- exact finite-population contrasts among the included source datasets;
- negative and null findings, including zero direct coverage for any recovery variable or persistent action ambiguity.

These claims apply only to the frozen Study 9 interface, included datasets, artifact versions, and preregistered derivation rules.

## Claims that are explicitly prohibited

Study 9 must not be described as directly measuring or establishing:

- intrusion-detection accuracy, precision, recall, F1, false-positive rate, false-negative rate, ROC-AUC, or classifier calibration;
- detector portability or learned-model generalization merely because multiple datasets are compared;
- operational spacecraft recovery effectiveness;
- on-orbit or flight validation;
- mission safety, survivability, availability, or mission success probability;
- real spacecraft authorization, cryptographic trust, command legitimacy, or recovery completion unless those are genuinely present in an included native artifact and satisfy the rubric;
- attack prevalence in operational satellite systems;
- causal effects of an attack on a spacecraft or mission;
- superiority of AI, machine learning, a recovery policy, a dataset, or a testbed unless measured in a separately preregistered experiment;
- validation by an external organization, spacecraft operator, standards body, publisher, or dataset author;
- representativeness of all satellite cybersecurity datasets or all space systems;
- independence of two datasets that share a testbed, simulator, collection campaign, or derived source population unless that dependence has been explicitly evaluated and modeled.

## Ground-truth label boundary

Published attack and scenario labels are valuable metadata, but in Study 9 primary endpoints they are offline ground truth rather than operational recovery evidence.

A label may be used for source accounting or descriptive stratification. It may not be converted into an operational `security_signal`, mission authorization, trust decision, freshness state, epoch-validity state, contradiction state, evidence-completeness state, or downstream action for the primary analysis.

This restriction directly prevents the Study 5 oracle-alarm simplification from becoming the central mechanism of Study 9.

## Semantic inference boundary

Statistical correlation is not semantic observability.

A telemetry feature may correlate strongly with attack state, authorization state, trust, or evidence quality and still be classified `AMBIGUOUS` or `ABSENT` for the recovery interface. The Study 9 mapping asks what the field semantically establishes at decision time, not what a later model might predict from it.

No missing recovery variable may be assigned a benign, adverse, or preferred default merely to force a downstream action.

## Recovery-decision boundary

The frozen Study 2 selector is used only as a bounded downstream decision interface. Study 9 does not reopen, retrain, optimize, or revalidate the frozen Study 2 mechanism.

A uniquely identifiable action means only that all admissible completions of unresolved Study 9 interface state yield the same action under the frozen selector. It does not mean that the action is operationally optimal, safe for every spacecraft, endorsed by a mission operator, or proven effective in flight.

## Cross-dataset boundary

The study concerns **semantic interoperability**, not conventional cross-dataset machine-learning transfer.

Accordingly:

- datasets remain separate finite source populations;
- poor or zero semantic coverage is not a dataset quality failure;
- common missing state is a property of the selected schemas and decision interface, not proof that every future space-cyber dataset has the same limitation;
- a shared source dependency must not be counted as an independent replication.

## Relationship to Study 5 and submitted papers

- Study 5 is frozen and not modified.
- Study 5's 0/8 direct-coverage result, 80 deterministic decisions, 16/16 attack-subtype invariance, action counts, and audit statements are not Study 9 observations.
- Study 9 must independently establish artifact identity, schema, mapping, and endpoint values.
- Papers 1 through 4 remain frozen and unpooled.
- Study 9 must not restate the broad idea that "missing state matters" as if that alone were novel. Its candidate contribution is the reproducible cross-dataset semantic-interface analysis and identifiability framework.

## Venue boundary

The intended target is **Cyber Security and Applications**, but venue fit does not authorize changing inclusion rules, endpoints, exclusions, or interpretation after results are known.

The target venue's current author guidance permits Research Articles and Short Communications and requires declaration of generative AI use in manuscript preparation when applicable. Those are submission requirements, not scientific evidence.

## Current authorization gate

No dataset ingestion, implementation, row-level analysis, canonical execution, results generation, manuscript drafting, or submission is authorized by this file.
