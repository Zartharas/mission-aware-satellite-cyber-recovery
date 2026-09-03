# Study 8 Literature and Venue Verification

**Verification date:** 2026-09-03  
**Purpose:** publication-context verification only. This record does not modify, rerun, or reinterpret the frozen Study-8 scientific dataset.

## Primary standards and guidance

| Key | Verification source | Verified publication/context fact | Publication use |
|---|---|---|---|
| `NIST_FIPS203_2024` | https://csrc.nist.gov/pubs/fips/203/final | FIPS 203 standardizes ML-KEM. | Exact standardized KEM object sizes and algorithm names only. |
| `NIST_FIPS204_2024` | https://csrc.nist.gov/pubs/fips/204/final | FIPS 204 standardizes ML-DSA. | Exact standardized signature/public-key sizes and algorithm names only. |
| `NIST_SP800227_2025` | https://csrc.nist.gov/pubs/sp/800/227/final | NIST guidance for safe use of KEMs in surrounding protocols/systems. | Systems/protocol context; not spacecraft performance evidence. |
| `NIST_CSWP39_2026` | https://www.nist.gov/publications/considerations-achieving-crypto-agility-strategies-and-practices-0 | Updated NIST crypto-agility guidance. | Defines the broader operational transition problem. |
| `IEEE3536_2026` | https://standards.ieee.org/ieee/3536/11916/ | IEEE 3536-2026 is the active Space System Cybersecurity Design standard. | Current space-cybersecurity systems context only. |
| `CCSDS_SDLS` | https://ccsds.org/publications/sls/ | CCSDS maintains Space Link Services/security architecture publications. | Architecture context only; **not** evidence that CCSDS standardizes ML-KEM or ML-DSA. |

## Space/PQC and crypto-agility related work

| Key | Exact metadata verified | Source | Boundary relevance |
|---|---|---|---|
| `Mahn_Muller_Zielinski_2025` | Jannik Mähn, Matthias Müller, Karin Zielinski, “Crypto Agility Definitions for Space Systems.” | https://security4space.esa.int/2025/papers/41/ | Confirms that space-specific crypto agility and secure update/fallback concepts are prior work. |
| `Wildfeuer_etal_2025` | Christoph Wildfeuer, Timeo Jauslin, Alain Lavoyer, Milenko Starcik, Afonso Serra, Laszlo Etesi, Valentina Tamburello, Bruno Huttner, “End-to-End Quantum-Safe Security for Satellite Data Links (E2EQSS).” | https://security4space.esa.int/2025/papers/15/ | Confirms practical PQC data-link architecture work is prior art. |
| `Robles_etal_2025` | Virgile Robles, Karthikeyan Bhargavan, Franziskus Kiefer, Thomas Gazagnaire, “Secure Satellite Software-Defined Payloads with High-Assurance Post-Quantum Cryptography.” | https://security4space.esa.int/2025/papers/47/ | Confirms high-assurance PQC integration/update work for satellite software-defined payloads. |
| `ESA_ACES_2026` | ESA ACES, “Advanced Cryptography and Secured by Design for 5G/6G Satellite Communication Systems,” ongoing; status date 2026-05-06. | https://resilience.esa.int/archives/projects/aces | Confirms ongoing institutional PQC/security-by-design activity for satellite/NTN systems. |
| `Ghosh_Nath_2026` | Tutan Ghosh and Ira Nath, IJSCN 44(5), 524–543, DOI `10.1002/sat.70041`; first published 2026-03-18. | https://onlinelibrary.wiley.com/doi/10.1002/sat.70041 | Confirms lattice-based PQC for satellite communication is already published and cannot be claimed as the novelty by itself. |
| `Kim_2026_PQCSpace` | Hyunmin Kim, Acta Astronautica 246, 863–886, DOI `10.1016/j.actaastro.2026.04.041`. | https://www.sciencedirect.com/science/article/pii/S0094576526002730 | Current systematic survey establishing a broad PQC-for-space research base and design constraints. |
| `Eichen_etal_2026` | Elliot Eichen, Sylvia Llosa, Yueqi Chen, Sangtae Ha, arXiv:2607.23007. | https://arxiv.org/abs/2607.23007 | Establishes constrained/NTN PQC bandwidth and key-management pressure as prior work. |
| `Falco_2019` | Gregory Falco, Journal of Aerospace Information Systems 16(2), 61–70, DOI `10.2514/1.I010693`. | https://doi.org/10.2514/1.I010693 | General satellite/space cybersecurity design context. |

## Novelty boundary after verification

The publication does **not** claim novelty for any of the following in isolation:

- post-quantum cryptography for satellites;
- lattice/PQC satellite communications;
- hybrid PQC migration;
- crypto agility for space systems;
- PQC bandwidth/object-size overhead;
- secure post-quantum software updates;
- CCSDS adaptation discussions.

The defensible contribution remains the narrower frozen Study-8 combination: a deterministic finite post-compromise trusted-recovery model that jointly varies transition policy, exact standardized cryptographic-object byte burden, temporal intermittent-contact opportunity, logical recovery deadline, epoch-safety invariants, and bounded non-cryptanalytic disruption, while separately measuring terminal feasibility and transition-state/availability costs.

## Venue verification

### IEEE Systems Journal — primary shaping target

Current scope explicitly includes systems thinking for complex cyber-physical systems and themes including modeling, analysis, simulation, mission assurance, robustness, reliability, availability, communications, security, and standards. Regular papers may be up to 12 pages during review.

- Scope: https://ieeesystemscouncil.org/publication/ieee-systems-journal
- Instructions: https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

### Acta Astronautica — strong aerospace-domain alternative

The International Academy of Astronautics describes Acta Astronautica as covering the conception, design, development, and operation of space-borne/Earth-based systems, including space technology and system development and space-system operation/utilization. Its publication record now includes the 2026 Kim PQC-for-space survey.

- Scope: https://iaaspace.org/publications/acta-astronautica/
- Current PQC survey: https://doi.org/10.1016/j.actaastro.2026.04.041

### International Journal of Satellite Communications and Networking — direct satellite-network alternative

Current Wiley scope covers satellite systems/networks, performance analysis, interoperability, standards/regulation, and network protocols, and the journal published Ghosh and Nath's PQC satellite paper in 2026.

- Scope: https://onlinelibrary.wiley.com/page/journal/15420981/homepage/aims.htm
- Related paper: https://doi.org/10.1002/sat.70041

### Computers & Security — not recommended for Study 8

The current journal scope explicitly excludes submissions in which cryptology is a principal component. The existing Study-1/Study-2 submission package remains separate; Study 8 should not be folded into it.

- Scope: https://shop.elsevier.com/journals/computers-and-security/0167-4048

## Verification status

`PUBLICATION_CONTEXT_VERIFIED_NO_SCIENTIFIC_REEXECUTION`
