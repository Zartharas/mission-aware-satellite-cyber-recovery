# Study 8 Literature Register

**Study:** S8-PQC-ICR-001  
**Phase:** 8.0 pre-implementation design  
**Verification date:** 2026-09-02  
**Status:** `LITERATURE_VERIFIED_FOR_DESIGN_LOCK_NOVELTY_NOT_FROZEN`

## Purpose

This register records the standards and current literature used to justify the Phase-8 design. It does not assert that post-quantum cryptography (PQC), hybrid cryptography, satellite PQC, or crypto agility are themselves novel. The candidate research contribution is narrower: post-compromise trusted recovery under a deterministic interaction between cryptographic transition policy, standardized cryptographic-object size, finite intermittent-contact opportunity, deadline, and bounded non-cryptanalytic disruption.

## Authoritative standards and institutional sources

### NIST FIPS 203 — ML-KEM

- National Institute of Standards and Technology, *Module-Lattice-Based Key-Encapsulation Mechanism Standard*, FIPS 203, 13 Aug. 2024.
- Publication: https://csrc.nist.gov/pubs/fips/203/final
- DOI: https://doi.org/10.6028/NIST.FIPS.203
- Design use: defines ML-KEM-512, ML-KEM-768, and ML-KEM-1024 and the byte sizes used in `STUDY8_CRYPTO_OBJECT_BUDGETS.json`.
- Boundary: FIPS 203 supplies algorithm definitions and standardized object sizes; it does not supply spacecraft, RF-link, contact-window, latency, energy, or mission-performance measurements.

### NIST FIPS 204 — ML-DSA

- National Institute of Standards and Technology, *Module-Lattice-Based Digital Signature Standard*, FIPS 204, 13 Aug. 2024.
- Publication: https://csrc.nist.gov/pubs/fips/204/final
- DOI: https://doi.org/10.6028/NIST.FIPS.204
- Design use: defines ML-DSA-44, ML-DSA-65, and ML-DSA-87 and the public-key/signature byte sizes used in the frozen candidate budget.
- Boundary: FIPS 204 does not validate the Phase-8 transition protocol or any satellite implementation.

### NIST SP 800-227 — Recommendations for Key-Encapsulation Mechanisms

- National Institute of Standards and Technology, *Recommendations for Key-Encapsulation Mechanisms*, SP 800-227, Sep. 2025.
- Publication: https://csrc.nist.gov/pubs/sp/800/227/final
- DOI: https://doi.org/10.6028/NIST.SP.800-227
- Design use: supports treating KEM usage as a protocol/system-design question with explicit security conditions rather than assuming that use of ML-KEM alone guarantees overall-system security.

### NIST CSWP 39upd1 — Crypto Agility

- National Institute of Standards and Technology, *Considerations for Achieving Crypto Agility: Strategies and Practices*, CSWP 39upd1, published 19 Dec. 2025 and updated 29 Jun. 2026.
- Publication: https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final
- Design use: supports the environment-specific study of mechanisms for replacing/adapting cryptography while preserving security and ongoing operation.
- Boundary: NIST crypto-agility guidance does not prescribe the Phase-8 state machine or contact model.

### CCSDS Space Data Link Layer Security Working Group

- CCSDS Space Link Services / Space Data Link Layer Security Working Group.
- Source: https://ccsds.org/publications/sls/
- Relevant institutional statement: the data-link security protocol is intended to be compatible with TM, TC, and AOS protocols and independent of any specific cryptographic algorithm.
- Design use: supports studying algorithm transition as an architectural concern without claiming that ML-KEM or ML-DSA are currently standardized CCSDS operational suites.
- Boundary: Phase 8 must not describe NIST PQC profiles as CCSDS-approved operational algorithms unless a later standards source explicitly establishes that fact.

### ESA ACES

- European Space Agency, *ACES — Advanced Cryptography and Secured by Design for 5G/6G Satellite Communication Systems*.
- Source: https://resilience.esa.int/archives/projects/aces
- Status observed: ongoing, status date 2026-05-06.
- Design use: establishes that ESA is actively developing lightweight/post-quantum security-by-design approaches for satellite networks and end-to-end satellite communications.
- Boundary: ACES does not validate the Phase-8 modeled contact budgets or recovery outcomes.

## Space/PQC and crypto-agility literature

### Mähn, Müller, and Zielinski — Crypto Agility Definitions for Space Systems

- ESA Security for Space Systems (3S), 2025.
- Source: https://security4space.esa.int/2025/papers/41/
- Design relevance: directly addresses crypto-agility terminology for space systems, remote update initialization, failure/attack concerns, and fallback.
- Novelty consequence: “crypto agility for space systems” cannot be claimed as novel by Phase 8.

### Wildfeuer et al. — End-to-End Quantum-Safe Security for Satellite Data Links

- ESA Security for Space Systems (3S), 2025.
- Source: https://security4space.esa.int/2025/papers/15/
- Design relevance: demonstrates active work on extending satellite data-link security architectures with ML-KEM/ML-DSA and hybrid quantum-safe approaches.
- Novelty consequence: satellite ML-KEM/ML-DSA integration and hybrid transition are not Phase-8 novelty claims.

### Robles et al. — High-Assurance PQC for Satellite Software-Defined Payloads

- ESA Security for Space Systems (3S), 2025.
- Source: https://security4space.esa.int/2025/papers/47/
- Design relevance: shows formally verified PQC and signed-update work in a satellite software context.
- Novelty consequence: secure PQC-enabled software update mechanisms are not sufficient novelty by themselves.

### GSMA PQ.07 — Post-Quantum Cryptography for Non-Terrestrial Networks

- GSMA, 6 Feb. 2026.
- Source: https://www.gsma.com/solutions-and-impact/technologies/security/gsma_resources/post-quantum-cryptography-for-non-terrestrial-networks-pq-07/
- Design relevance: identifies high latency, constrained onboard processing, satellite lifecycles, interoperability, PKI, and phased/hybrid transition as PQC migration concerns in NTN environments.
- Novelty consequence: PQC migration challenges in NTN environments are already an active industry topic.

### Eichen, Llosa, Chen, and Ha — Practical PQC for Bandwidth-Constrained or Non-Terrestrial Networks

- arXiv:2607.23007, 25 Jul. 2026.
- Source: https://arxiv.org/abs/2607.23007
- Design relevance: explicitly discusses larger PQ authentication artifacts, intermittent connectivity, bandwidth-constrained satellite-to-ground links, and key rotation/key management.
- Novelty consequence: bandwidth/contact pressure from PQC artifacts is not novel by itself.

### Ghosh and Nath — Secure Satellite Communication in the Post-Quantum Era

- *International Journal of Satellite Communications and Networking*, 2026.
- DOI: https://doi.org/10.1002/sat.70041
- Design relevance: surveys/evaluates lattice-based PQC in satellite contexts and discusses implementation, bandwidth, memory, energy, and cryptographic agility.
- Boundary: Phase 8 will not reuse external hardware/runtime benchmark values as its own evidence.

### Kim — Systematic Survey of PQC for Space Systems

- Hyunmin Kim, *Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey*, *Acta Astronautica* 246 (2026), 863–886.
- DOI: https://doi.org/10.1016/j.actaastro.2026.04.041
- Design relevance: synthesizes algorithm suitability, implementation, protocol adaptation, hybrid migration, crypto agility, and CCSDS gaps across space-PQC work.
- Novelty consequence: any Phase-8 novelty statement must be narrower than “PQC for space,” “PQC migration,” “hybrid PQC,” “CCSDS adaptation,” or “crypto agility.”

## Candidate gap statement

The literature above establishes substantial prior work on space-system PQC, crypto agility, hybrid migration, protocol adaptation, constrained links, secure updates, and key management. The Phase-8 candidate gap is therefore limited to the following conjunction:

> A deterministic, finite post-compromise trusted-recovery study in which cryptographic transition policy is evaluated jointly with NIST-standardized cryptographic-object byte budgets, synthetic intermittent-contact opportunities, explicit recovery deadlines, epoch-safety invariants, and bounded non-cryptanalytic disruption.

This is a **candidate gap statement**, not a frozen novelty claim. It must remain qualified until the dedicated adversarial literature/design review is complete.

## Prohibited novelty statements

Phase 8 must not claim any of the following:

- first PQC study for satellites;
- first ML-KEM or ML-DSA use in satellite communications;
- first hybrid cryptography proposal for space systems;
- first crypto-agility work for space systems;
- first study of PQC bandwidth overhead in NTN/satellite environments;
- first CCSDS/PQC integration study;
- first secure-update or rollback mechanism for space crypto agility.
