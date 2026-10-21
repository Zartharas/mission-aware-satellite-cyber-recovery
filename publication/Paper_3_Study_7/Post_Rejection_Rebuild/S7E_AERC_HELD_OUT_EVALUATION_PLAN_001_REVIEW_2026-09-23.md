# S7E-AERC-001 Held-Out Evaluation Plan 001 — Technical Review

**Plan ID:** `S7E-AERC-HELDOUT-PLAN-001`  
**Protocol freeze:** `S7E-AERC-FREEZE-001`  
**Model freeze:** `S7E-AERC-MODEL-FREEZE-001`  
**Review state:** reviewed; static qualification pending  
**Held-out inference:** NOT AUTHORIZED

## Review conclusion

The plan is suitable for static qualification and later separate author consideration for held-out inference.

It preserves the prospective Study 7E protocol rather than introducing a post-training analysis scheme.

## Population

The held-out population remains exactly:

- E1 unseen faults: 84 scenarios;
- E2 held-out topologies: 104 scenarios;
- C0 held-out-topology/no-signal control: 8 scenarios;
- total: 196 scenarios;
- four policy decisions per scenario;
- total: 784 held-out policy-decision observations.

TR0/TR1 remain training-only and are never pooled into held-out results.

## Policy comparison

Each scenario is processed in fixed order by:

1. `D0_BASE`
2. `L0_BASE`
3. `D1_CORROBORATED`
4. `L1_CORROBORATED`

D0/L0 must receive byte-identical base vectors. D1/L1 must receive byte-identical extended vectors. A mismatch invalidates the scenario.

## Frozen learned-policy handling

If later separately authorized:

- primary L0/L1 inference uses the hash-verified frozen joblib payloads under the exact bound runtime/dependency environment;
- independent audit inference uses a separately implemented pure semantic-tree interpreter over the frozen canonical semantic JSON;
- the audit does not deserialize joblib;
- every learned-policy primary action must equal its independent-audit action.

No model fitting, tuning, or model alteration is permitted.

## Primary endpoints

The plan preserves the protocol's primary endpoints:

- objective decision error;
- unsafe proceed;
- false-conservative hold;
- exact action counts;
- D0/L0 paired disagreement;
- D1/L1 paired disagreement;
- topology-stratified unsafe/false-conservative changes;
- corroboration deltas within deterministic and learned classes;
- F10/F11 common-cause behavior.

All are exact finite-population counts. Descriptive proportions may be reported with exact numerators and denominators.

No significance test, global policy ranking, or operational-spacecraft probability interpretation is permitted.

## Secondary endpoints

The plan preserves:

- topology-specific confusion tables;
- fault-profile-specific action tables;
- policy disagreement by topology/fault;
- frozen learner structure/depth and feature-use trace;
- training error reported separately;
- E1 exact unseen-fault error;
- E2 exact held-out-topology error;
- C0 spurious recovery entries.

## Validity / abort rule

A complete-population result package requires **zero invalid scenarios**.

If any scenario is invalid:

- the attempt and reason remain in the ledger;
- no hidden retry or replacement occurs;
- final 196-scenario aggregate results are not released from that execution;
- a later campaign requires a new execution identifier and retains prior provenance.

This is stricter than selectively dropping invalid observations and is appropriate for the fully enumerated finite population.

## Leakage controls

Research-only truth, topology, fault identity, and domain map are not policy inputs. Objective truth is joined only after policy input capture and decision emission.

The plan-qualification phase creates no held-out authorization file and no executable held-out workflow, ensuring that E1/E2/C0 cannot be inferred merely by qualifying this plan.

## Review verdict

**PASS FOR STATIC QUALIFICATION.**

There are no blocking technical findings. The next scientific gate remains a separate explicit authorization before any E1/E2/C0 feature materialization for inference or any model prediction.
