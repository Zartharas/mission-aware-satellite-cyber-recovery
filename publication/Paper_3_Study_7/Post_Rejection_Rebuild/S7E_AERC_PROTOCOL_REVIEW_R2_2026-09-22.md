# S7E-AERC-001 Protocol Review R2

**Review ID:** `S7E-AERC-PROTOCOL-REVIEW-R2`  
**Date:** 2026-09-22  
**Stage:** pre-freeze implementation review  
**Scientific execution:** NOT AUTHORIZED  
**Outcome:** `TRUST_DOMAIN_COVERAGE_DEFECT_FOUND_AND_CORRECTED_BEFORE_EXECUTION`

## Finding

The Study-7E architecture defines five trust domains:

1. source/provenance;
2. signing key;
3. execution process/processor;
4. transport;
5. authorization authority.

The first implementation draft contained direct fault challenges for source, key, transport, and authority domains but no direct execution-domain compromise. That would permit a reviewer to argue that execution-domain separation was declared but not experimentally exercised.

## Correction

Add:

`F12 PRIMARY_EXECUTION_COMPROMISE`

F12 targets the primary execution domain. Its affected evidence paths are derived from execution-domain aliasing in the selected topology.

Examples:

- T0 shares execution, so an F12 primary execution compromise propagates to both logical evidence paths;
- T1 through T4 separate execution, so the same targeted compromise affects only the primary execution path.

The exact cFS/NOS3 byte/message-level implementation of F12 remains to be frozen after external-stack feasibility.

## Revised prospective population

Training remains:

- TR1 = 72;
- TR0 = 12;
- total training = 84.

Evaluation becomes:

- E1 = 84 because unseen faults are now F6-F12 across T0-T2;
- E2 = 104 because all F0-F12 are evaluated across held-out T3-T4;
- C0 = 8;
- total evaluation/control = 196;
- four policies per evaluation scenario = 784 planned policy decisions.

Complete manifest:

`84 + 84 + 104 + 8 = 280` scenarios.

## Governance

This correction occurred before protocol freeze, before model freeze, and before scientific execution. No result was inspected or generated.

Study 7 is unchanged.
