# S7E-AERC-001 Architecture Source Ledger

**Research date:** 2026-09-22  
**Purpose:** primary-source basis for the prospective Study-7E architecture.  
**Status:** design support only; no execution result.

## NASA core Flight System

### cFS Framework

Official NASA Software Catalog:  
https://software.nasa.gov/software/GSC-18719-1

Design use:

- supports cFS as a reusable, platform-independent embedded framework;
- confirms layered architecture with cFE, OSAL, PSP;
- confirms example CI/TO/Scheduler lab implementations.

Boundary:

NASA states the bundle contains example implementations. The study must not describe the research configuration as a NASA flight distribution.

### Core Flight Executive

Official NASA repository:  
https://github.com/nasa/cFE

NASA Software Catalog:  
https://software.nasa.gov/software/GSC-18128-1

Design use:

- cFE provides Software Bus, Time, Event, Executive, Table, and File services;
- supports portable application development and desktop testing before embedded-port verification.

### Health & Safety

Official NASA Software Catalog:  
https://software.nasa.gov/software/GSC-18476-1

Design use:

- HS supports application monitoring, event monitoring, watchdog servicing, execution-counter reporting, and CPU aliveness indication;
- used only as a cFS-native health/readiness source or adapter basis.

Boundary:

Study 7E does not infer complete spacecraft safety from HS.

### Software Bus Network

Official NASA Software Catalog:  
https://software.nasa.gov/software/GSC-16917-1

Design use:

- SBN transfers messages across process/processor interfaces;
- provides the mechanism for T3/T4 cross-instance execution/transport separation.

## NASA Operational Simulator for Space Systems (NOS3)

Official NASA repository:  
https://github.com/nasa/nos3

NASA Small Spacecraft Systems Virtual Institute tools page:  
https://www.nasa.gov/smallsat-institute/space-mission-design-tools/

Design use:

- NOS3 supports software development, I&T, mission operations/training, V&V, and systems check-out;
- provides multi-target builds, ground/operator interface, dynamics/environment simulation, and software hardware models;
- is a candidate canonical integration environment.

NOS3 simulator documentation:  
https://github.com/nasa/nos3/blob/main/docs/wiki/NOS3_Simulators.md

Design use:

- NOS Engine abstracts common hardware-bus connections;
- simulator documentation explicitly discusses future/modeling capability for hardware faulting and bus dropouts/errors;
- supports the engineering plausibility of controlled transport/device-fault injection.

NOS3 ground-system documentation:  
https://github.com/nasa/nos3/blob/main/docs/wiki/NOS3_Ground_Software.md

Design use:

- documents cFS CI/TO command/telemetry connectivity in NOS3;
- documents available ground software and CCSDS-formatted communications;
- warns that NOS3 CI/TO UDP paths are not intended for flight operations.

## Research-use interpretation

These sources justify the **architecture substrate**, not the scientific conclusions.

Study 7E must independently demonstrate:

- its actual topology implementation;
- fault propagation;
- policy input equivalence;
- decision outcomes;
- audit reproducibility.

No source above establishes that the proposed trust domains are operationally independent, that the resulting system is flightworthy, or that the study is NASA-validated.
