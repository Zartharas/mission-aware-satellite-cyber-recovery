# S7E-AERC-001 Candidate Stack Compatibility Decision

**Decision ID:** `S7E-AERC-STACK-COMPAT-001`  
**Date:** 2026-09-22  
**State:** `ALTERNATIVE_CANDIDATES__CANONICAL_STACK_NOT_SELECTED`  
**Scientific execution:** NOT AUTHORIZED

## 1. Problem

The design phase identified both NASA cFS v7.0.1 and NASA NOS3 v1.7.5 as candidate environments.

They must not be treated as a single interchangeable dependency set.

The cFS v7.0.1 bundle pins, among others:

- cFE `c5fb2b4d540bd55eb6c3707da7dd13eee679d4dd`;
- OSAL `d2d877a69cff47452bcca274b309147d48e6c16f`;
- PSP `c4b3b0b65b119e106481ad8e20976ae4d7f554e3`;
- SBN `3b7b37572d63c3f8e85b1f0fa95853c1b78dcf96`.

NOS3 v1.7.5 pins its own nasa-itc flight-software stack, including:

- cFE `87e273743f3d07ed9216462b461e9f398ff96c87`;
- OSAL `08a79bb6ac02b9ced8aa555853ecdd96e5ebc1a7`;
- PSP `d0a5d6fa4093d473a929fde42a0983e489d89d4a`;
- SBN `240f90f56641d43e5db1dae457d7ef8772a1c659`.

Therefore replacing NOS3's pinned cFS-family submodules with the standalone cFS v7.0.1 revisions without a separate compatibility study is prohibited.

## 2. Candidate A: standalone cFS v7.0.1

Use when the experiment can be implemented as a controlled multi-instance cFS research testbed with SBN and does not require NOS3's dynamics/hardware/ground integration.

Advantages:

- official cFS release;
- smaller qualification surface;
- direct cFE/SBN control;
- easier deterministic build/replay boundary.

Required proof before selection:

- custom app build/load;
- two-instance communication;
- SBN behavior needed by T3/T4;
- deterministic scenario control and telemetry capture.

## 3. Candidate B: NOS3 v1.7.5 native pinned stack

Use when NOS3's integrated ground/dynamics/hardware-model environment materially strengthens architecture validity.

Advantages:

- integrated cFS-based spacecraft software environment;
- operator/ground system;
- simulation and hardware-model infrastructure;
- existing SBN integration in the release family.

Required proof before selection:

- reproducible supported Linux/VM build;
- exact recursive submodule capture;
- custom application integration;
- deterministic non-canonical scenario control;
- required multi-instance/SBN topology;
- no uncontrolled network dependency during canonical execution.

## 4. Selection rule

After both feasibility gates are reviewed:

- choose exactly one canonical environment baseline;
- freeze that environment and its full dependency graph;
- document why the selected stack provides the minimum architecture fidelity needed to answer the CEAS criticism;
- retain the unselected stack only as feasibility/reference evidence.

No canonical Study-7E execution is permitted before this selection is explicitly approved and frozen.
