# Rebuilt Paper 4 Literature Verification — 2026-09-21

**Purpose:** current-source verification for the venue-neutral Study 8 + Study 8E manuscript.

This record verifies citation identity and framing only. It does not alter frozen Study 8 or Study 8E science.

## Verified standards and authoritative technical sources

### NIST FIPS 203

- Title: *Module-Lattice-Based Key-Encapsulation Mechanism Standard*
- Identifier: FIPS 203
- Final: 2024-08-13
- DOI: `10.6028/NIST.FIPS.203`
- Current NIST page: https://csrc.nist.gov/pubs/fips/203/final
- Relevance: authoritative ML-KEM parameter-set and object-size source.

### NIST FIPS 204

- Title: *Module-Lattice-Based Digital Signature Standard*
- Identifier: FIPS 204
- Final: 2024-08-13
- DOI: `10.6028/NIST.FIPS.204`
- Current NIST page: https://csrc.nist.gov/pubs/fips/204/final
- Relevance: authoritative ML-DSA parameter-set and object-size source.
- Current page includes a 2026-07-31 planning note for minor future errata; the final standard remains the cited authority.

### NIST SP 800-227

- Title: *Recommendations for Key-Encapsulation Mechanisms*
- Final: 2025-09
- DOI: `10.6028/NIST.SP.800-227`
- Current NIST page: https://csrc.nist.gov/pubs/sp/800/227/final
- Relevance: KEM usage and system-context guidance.

### NIST CSWP 39-upd1

- Title: *Considerations for Achieving Crypto Agility: Strategies and Practices*
- Identifier: CSWP 39-upd1
- Updated/final publication: 2026-06-29
- DOI: `10.6028/NIST.CSWP.39-upd1`
- Current NIST page: https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final
- Relevance: current NIST crypto-agility definition and transition framing.
- Important: CSWP 39-upd1 supersedes the December 2025 CSWP 39 release.

### IEEE 3536-2026

- Title: *IEEE Standard for Space System Cybersecurity Design*
- Published: 2026-07-24
- Status: active standard
- Current IEEE page: https://standards.ieee.org/ieee/3536/11916/
- Relevance: current system-level space cybersecurity context.

### SatNOGS Network API

- Documentation: https://docs.satnogs.org/projects/satnogs-network/en/latest/api.html
- Observations endpoint: `/api/observations/`
- Data license: CC BY-SA per documentation.
- Relevance: authoritative source identity for Study 8E public observation-opportunity timing.
- Manuscript boundary: API observation fields are source timing/provenance fields; they do not establish authenticated command contact or measured recovery throughput.

## Verified recent satellite / NTN PQC literature

### Kim (2026)

*Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey.*

- Journal: *Acta Astronautica*
- Volume 246, pp. 863–886
- DOI: `10.1016/j.actaastro.2026.04.041`
- Relevance: broad survey showing that space PQC, implementation benchmarking, protocol adaptation, hybrid migration, and CCSDS gaps are established research areas.
- Framing consequence: rebuilt Paper 4 must not claim novelty for “PQC for satellites” generally.

### Ghosh and Nath (2026)

*Secure Satellite Communication in the Post-Quantum Era: A Lattice-Based Cryptographic Approach.*

- Journal: *International Journal of Satellite Communications and Networking*
- DOI: `10.1002/sat.70041`
- First published: 2026-03-18
- Relevance: lattice-based PQC performance/security analysis in satellite context.

### Eichen et al. (2026)

*Practical Post-Quantum Cryptography for Bandwidth Constrained or Non-Terrestrial Networks, and Power Constrained Devices.*

- arXiv:2607.23007
- Status: preprint as verified on 2026-09-21.
- Relevance: bandwidth, memory, computation, and energy pressure from PQ authentication in constrained/NTN environments.
- Manuscript rule: label explicitly as a preprint.

### De Zuane et al. (2026)

*Efficient and Quantum-Safe Internet Key Exchange Protocols for Satellite Communications.*

- Conference: IEEE LANMAN 2026
- DOI: `10.1109/LANMAN69841.2026.11623493`
- Relevance: design/experimental quantum-safe IKE and hybrid transition in satellite communications.
- Distinction: handshake/protocol efficiency work; not post-compromise trusted epoch-transition feasibility under the Paper-4 model.

### Mähn, Müller, and Zielinski (2025)

*Crypto Agility Definitions for Space Systems.*

- ESA Security for Space Systems (3S) 2025.
- Relevance: space-specific crypto-agility terminology, update, failure, and fallback concerns.

### GSMA PQ.07 (2026)

*Post Quantum Cryptography for Non-Terrestrial Networks.*

- Published: 2026-02-06.
- Relevance: NTN migration constraints and phased transition context.

## Novelty position after verification

The defensible narrow contribution remains:

> a two-study analysis of trusted post-compromise cryptographic state transition under intermittent opportunity, separating fixed-capacity recovery feasibility from minimum modeled rate burden, with frozen transition-state semantics and a prospectively governed public observation-opportunity timing extension.

Do not claim novelty for:

- PQC in satellite systems;
- larger PQC objects;
- crypto agility generally;
- hybrid migration;
- quantum-safe satellite handshakes;
- SatNOGS itself.

## Source-quality rule

Use standards, publisher pages, peer-reviewed papers, institutional sources, and SatNOGS documentation for core claims. Press releases or commercial announcements may inform background awareness but are not required for the manuscript's scientific argument.
