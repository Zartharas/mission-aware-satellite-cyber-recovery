# Paper 3 — Live Literature and Reference Audit — 2026-09-24

**Audit ID:** `PAPER3-S7-S7E-LIVE-LIT-REF-AUDIT-001`  
**Scope:** rebuilt Paper 3 / Study 7 + Study 7E  
**Basis PR:** #168  
**Basis head:** `28077469a60250dd8f65345dacce245f80e54926`  
**Audit state:** `COMPLETE__R2_REFERENCE_AND_POSITIONING_CHANGES_REQUIRED`  
**Venue lock:** NOT AUTHORIZED BY THIS AUDIT  
**Publisher submission:** NOT AUTHORIZED

## 1. Purpose and method

This audit rechecked the 13 references in venue-neutral R1 against primary, publisher, conference, or institutional records where available and conducted a fresh targeted literature search through 2026-09-24.

The search focused on:

- satellite cyber recovery;
- spacecraft software resiliency and secure architecture;
- NASA cFS security and trust boundaries;
- satellite ML assurance and adversarial ML;
- partial observability and latent-variable safety;
- satellite anomaly detection as adjacent upstream work.

A negative search result is not proof of novelty. The audit therefore records only what was located and narrows claims where adjacent work exists.

## 2. Reference-by-reference R1 disposition

| R1 ref. | Disposition | Audit result |
|---|---|---|
| [1] SPARTA Cyber-safe Mode | RETAIN | Current SPARTA countermeasure remains appropriate antecedent context. |
| [2] Study-2 Zenodo DOI 10.5281/zenodo.22289114 | RETAIN WITH REPOSITORY AUTHORITY | DOI is bound in repository provenance. This web session could not independently resolve the DOI; no evidence was found that it is invalid. Do not replace it from inference. |
| [3] NASA TM 20240006865 | RETAIN | NTRS verifies title, document ID, authors, and publication date 2024-06-07. |
| [4] OPS-SAT benchmark | RETAIN | Scientific Data 12, article 710 (2025), DOI verified. A later correction exists; the article remains the valid cited benchmark. |
| [5] Fejjari et al. | RETAIN | Acta Astronautica 238 Part A, 739-745 (2026), DOI verified. |
| [6] Kuhn et al. | RETAIN | Acta Astronautica 249, 971-985 (2026), DOI verified. |
| [7] partial-observability AAAI paper | CORRECT | First author is **Hai S. Le**, not "T. Le"; AAAI 38(18), 20159-20167; DOI 10.1609/aaai.v38i18.29995. |
| [8] latent-variable ICML paper | CORRECT | First author is **Haoming Jing**, not "Y. Jing"; PMLR 267:28288-28303 (2025). |
| [9] NASA cFS | RETAIN | Official NASA cFS capability/catalog sources support platform-independent reusable flight-software framework description. |
| [10] cFE | STRENGTHEN | Replace repo-only citation with NASA Software Catalog GSC-18128-1, which explicitly lists Software Bus, Time, Event, Executive, Table, and File services. |
| [11] cFS HS | RETAIN | NASA Software Catalog GSC-18476-1 verifies application/event monitoring, watchdog, execution-counter, and CPU-aliveness functions. |
| [12] cFS SBN | RETAIN | NASA Software Catalog GSC-16917-1 verifies cross-process/processor message transfer and peer subscriptions. |
| [13] NOS3 | STRENGTHEN | Use official NASA Software Catalog GSC-17737-1 for NASA Operational Simulator for Small Satellites; repository links may remain supplemental. |

## 3. Material adjacent literature identified

### Secure spacecraft recovery and software resiliency

Juliato and Gebotys (2017) already propose secure spacecraft recovery using a trusted hardware platform and recovery protocols. Therefore Paper 3 must not claim to originate secure spacecraft recovery.

Phillips, Mazzuchi, and Sarkani (2018) present an architecture/system-engineering approach to space-system software resiliency. Driouch, Bah, and Guennoun (2023) present a mission-specific defensible cybersecurity architecture. Broad claims that Paper 3 newly introduces architectural cyber resilience are therefore unsupported.

### cFS and flight-software security

Curbo and Falco (IEEE SMC-IT 2024) analyze spacecraft flight-software attack surface and secure architectural principles.

McAmis et al. (SpaceSec 2026) use cFS to demonstrate the security/reliability dilemma of compromised satellite peripherals.

Vanlyssel et al. (arXiv:2608.14532, 2026) analyze cFS authority, identity, communication, observability, and persistence and report malicious-component experiments. This source is a contemporaneous **preprint**, not treated here as peer-reviewed validation.

These sources make any broad "first cFS trust-boundary study" claim unsafe.

### Satellite ML security

Shigol et al. (SpaceSec 2026) provide a satellite-specific adversarial-ML risk assessment.

Belali et al. (IJCIP 2026) propose S-LARF, an architectural adversarial-resilience framework around spaceborne anomaly detection, with real telemetry and FPGA evaluation.

These works mean Paper 3 should not claim to originate system-level satellite ML security or architectural controls around ML.

## 4. Defensible novelty boundary after live search

The literature audit supports a narrower novelty position.

The search did **not locate** a publication combining all of:

1. downstream satellite **cyber-recovery authorization**, rather than detector performance alone;
2. deterministic-versus-learned **equal-information pairs** with byte-identical policy-visible input checks;
3. explicit source/key/execution/transport/authority domain-alias topologies;
4. prospectively frozen common-cause fault transformations;
5. learned models frozen before held-out unseen-fault and held-out-topology evaluation;
6. exact finite-population unsafe-proceed and false-conservative-hold endpoints.

This is a negative targeted-search observation, **not proof of novelty, priority, or literature completeness**.

## 5. Required R2 changes

R2 should:

- correct [7] and [8];
- strengthen official NASA citations [10] and [13];
- add the secure-recovery/software-resiliency/cFS-security/ML-security literature above;
- explicitly disclaim novelty for secure recovery, resilient spacecraft architecture, cFS security, and generic satellite ML security;
- retain the narrower equal-information/trust-topology/held-out-transfer contribution;
- keep Vanlyssel et al. explicitly labeled as a preprint;
- retain R1 scientific results without change.

## 6. Scientific impact

**No frozen scientific result changes.**

The audit changes literature positioning and bibliographic precision only. It does not alter:

- Study 7 population or results;
- Study 7E population or results;
- model freeze;
- result freeze;
- hypothesis disposition;
- claim ledger quantitative values.

## 7. Audit decision

`PASS_WITH_REQUIRED_LITERATURE_POSITIONING_REVISION`

R2 may be created venue-neutrally.

No venue is locked by this audit.
