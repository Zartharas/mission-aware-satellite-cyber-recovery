# Study 8 Claim Boundary

**Experiment:** `S8-PQC-ICR-001`  
**Phase:** 8.0  
**Status:** `BOUNDARY_LOCK_CANDIDATE_RUNTIME_NOT_AUTHORIZED`

## Permitted scientific quantities

Phase 8 may report only quantities produced by the frozen deterministic model:

- logical contact slots and contact opportunities;
- synthetic contact capacity expressed in bytes;
- NIST-standardized cryptographic-object sizes;
- cryptographic bytes scheduled or transferred by the model;
- logical recovery completion slot;
- number of logical contacts consumed;
- logical predecessor/legacy exposure slots;
- logical control-unavailable slots;
- transition attempt count;
- rollback/fallback invocation;
- stale-epoch acceptance or rejection;
- terminal protocol state;
- finite-population counts, proportions, contrasts, and exact deterministic summaries.

## Explicitly prohibited empirical interpretations

The Phase-8 model must not be described as directly measuring or estimating:

- spacecraft processor latency;
- onboard ML-KEM or ML-DSA execution time;
- cryptographic accelerator performance;
- RF throughput, RF propagation delay, BER, packet loss, modulation, coding, or link margin;
- ground-station processing time;
- orbital contact duration or orbit geometry;
- flight-computer memory consumption;
- power, thermal, or energy consumption;
- actual CCSDS frame overhead;
- operational certificate-chain overhead;
- real mission availability, safety, survivability, or recovery time.

Logical slots have no conversion factor to seconds or milliseconds.

## Standards boundary

FIPS 203 and FIPS 204 are used only for standardized algorithm/object definitions and byte sizes. NIST standardization does not make the Phase-8 transition protocol NIST-approved.

CCSDS algorithm independence supports an architectural crypto-agility question. It does not establish ML-KEM or ML-DSA as a CCSDS-approved operational space-link suite.

ESA, GSMA, and academic sources establish relevance and prior work. They do not validate the Phase-8 contact model or outcomes.

## Cryptographic-security boundary

The adversary may replay, duplicate, delay, reorder, or drop transition material only as specified by the frozen disruption schedule. The study will not model or claim:

- signature forgery;
- private-key recovery;
- KEM break;
- quantum cryptanalysis;
- side-channel exploitation;
- fault injection;
- cryptographic implementation vulnerabilities;
- adaptive attack optimization.

A valid stale object may be replayed. A cryptographically forged object may not be created.

## Recovery boundary

`TRUST_RESTORED` is a modeled protocol terminal state. It means only that the frozen model reached all required successor-epoch conditions before the selected logical deadline without stale/compromised epoch acceptance.

It must not be translated into “spacecraft recovered,” “mission recovered,” “satellite secured,” or equivalent operational language.

## Publication and pooling boundary

- Phase 8 is a separate companion-publication line.
- Study 1 and Study 2 Computers & Security science remains frozen.
- Studies 1–7 remain frozen and unpooled with Study 8.
- No Phase-8 result may be retrospectively inserted into the frozen Study-1/Study-2 statistical record.

## Runtime gate

The following remain false until a later explicit authorization after independent design review and pre-runtime validation:

```text
runtime_authorized=false
canonical_execution_authorized=false
implementation_creation_authorized=false
results_directory_authorized=false
campaign_authorization_present=false
```
