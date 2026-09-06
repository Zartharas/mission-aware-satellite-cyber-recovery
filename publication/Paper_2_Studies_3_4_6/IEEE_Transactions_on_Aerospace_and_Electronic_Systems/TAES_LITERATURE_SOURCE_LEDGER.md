# TAES Paper 2 Literature Source Ledger

**Status:** `ACTIVE_MANUSCRIPT_SOURCE_LEDGER__LIVE_RECHECKED_2026-09-06`  
**Target:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Paper:** Studies 3 + 4 + 6 only  
**Last live literature review:** 2026-09-06

## Purpose

This ledger records the external sources used to position Paper 2. It is not itself a manuscript section. The manuscript may cite only claims supported by the cited source. Internet-Drafts and preprints must be identified as such. Standards, frameworks, and taxonomies are prior art or contextual motivation only. They do not validate the frozen studies and do not establish standards compliance.

## Core sources for Sections I and II

### [1] Space-cybersecurity operating context

R. Thummala, E. Rice, and G. Falco, "Why is Space Cybersecurity Unique?" NDSS SpaceSec 2026, 2026.

Official landing page: https://www.ndss-symposium.org/ndss-paper/auto-draft-645/

Live-verified support:
- communication gaps can mandate autonomous decisions;
- mission continuity and availability are treated as first-order space-security concerns;
- permanent loss of hardware access and tight subsystem dependencies are identified as distinctive interacting constraints.

Do not use this source to claim that Study 3's K4 schedule represents an orbit or operational contact geometry.

### [2] Satellite flight-software trust boundaries

J. Vanlyssel, G.-C. Roman, K. Cook, S. Rahaman, and A. Anwar, "Trust Without Boundaries: An Architectural Analysis of Satellite Flight Software," arXiv:2608.14532, Aug. 2026. Preprint.

Source: https://arxiv.org/abs/2608.14532

Live-verified support:
- modular flight-software components can operate with broad legitimate authority;
- a compromised component can abuse legitimate architectural privileges;
- internal satellite flight-software trust boundaries are an active research problem.

Do not present the preprint as peer-reviewed evidence.

### [3] Testable cyber requirements for flight software

J. Curbo and G. Falco, "Testable Cyber Requirements for Space Flight Software," in Proc. 2025 IEEE Aerospace Conference, 2025, doi: 10.1109/AERO63441.2025.11068629.

Live verification:
- title, authors, conference, year, and DOI were corroborated through the authors' publication page and 2025 IEEE Aerospace Conference proceedings metadata;
- secure-by-design and cyber-resilience requirements for spacecraft flight software are established context.

Do not imply that the present studies implement or validate the authors' architecture.

### [4] SPARTA

The Aerospace Corporation, "Space Attack Research and Tactic Analysis (SPARTA)," current online matrix and countermeasures.

Main source: https://sparta.aerospace.org/

Direct cyber-safe-mode source: https://sparta.aerospace.org/countermeasures/CM0044

Live-verified support:
- cyber-safe mode uses an integrity-protected, validated software and configuration baseline;
- updates, where permitted, use separately authorized and integrity-verified maintenance that preserves a recoverable trusted version;
- cyber-safe recovery is therefore established spacecraft-security context.

Do not claim SPARTA compliance or validation.

### [5] IETF RATS architecture

H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, "Remote ATtestation procedureS (RATS) Architecture," RFC 9334, Jan. 2023, doi: 10.17487/RFC9334.

Official source: https://www.rfc-editor.org/rfc/rfc9334.html

Live-verified support:
- Evidence, Attester, Verifier, Relying Party, Attestation Results, and appraisal policies are established concepts;
- freshness is an explicit appraisal concern;
- RFC 9334 explicitly notes a race condition in which the Attester state can change immediately after Evidence or an Attestation Result is generated, so freshness narrows recentness rather than guaranteeing instantaneous synchronization.

Novelty implication:
- Paper 2 must not claim evidence appraisal or freshness as new concepts.

### [6] Multiple-verifier RATS work

Y. Deshpande, J. Zhang, H. Labiod, and H. Birkholz, "Remote Attestation with Multiple Verifiers," draft-ietf-rats-multi-verifier-00, IETF RATS Working Group, May 2026. Work in progress.

Official source: https://datatracker.ietf.org/doc/draft-ietf-rats-multi-verifier/

Live-verified status and support:
- active RATS Working Group Internet-Draft, published 5 May 2026;
- describes hierarchical, cascaded, and hybrid multi-Verifier patterns;
- multiple Verifiers can appraise Partial Evidence and produce Partial Attestation Results that are combined into aggregated results.

Required distinction:
- Study 4 models multiple evidence producers and q-of-N/provenance qualification rules, not multiple Verifiers appraising a Composite Attester.

### [7] Byzantine quorum systems

D. Malkhi and M. Reiter, "Byzantine quorum systems," Distributed Computing, vol. 11, no. 4, pp. 203-213, 1998, doi: 10.1007/s004460050050.

Live-verified bibliographic record:
- Distributed Computing 11(4), 203-213, 1998;
- DOI confirmed;
- quorum systems for consistency and availability under Byzantine repository failures are established prior art.

Required distinction:
- Study 4 is a recovery-evidence qualification experiment, not a Byzantine consensus, replicated-state-machine, or distributed-agreement protocol.

### [8] Asymmetric distributed trust

O. Alpos, C. Cachin, B. Tackmann, and L. Zanolini, "Asymmetric distributed trust," Distributed Computing, vol. 37, pp. 247-277, 2024, doi: 10.1007/s00446-024-00469-1.

Official source: https://link.springer.com/article/10.1007/s00446-024-00469-1

Live-verified support:
- published 28 May 2024 in volume 37, pages 247-277;
- quorum systems are explicitly described as an abstraction for capturing trust assumptions;
- asymmetric/subjective trust assumptions are established prior art.

Novelty implication:
- Paper 2 must not claim to introduce heterogeneous trust or quorum trust theory.

### [9] Satellite trust architecture using quorum endorsement

F. Rezabek, D. Malkhi, and A. Yahalom, "Space Fabric: A Satellite-Enhanced Trusted Execution Architecture," arXiv:2603.23745, Mar. 2026. Preprint.

Source: https://arxiv.org/abs/2603.23745

Live-verified support:
- architecture binds workload execution to a satellite using a Byzantine-tolerant endorsement quorum of distributed ground stations;
- the architecture also uses two secure elements that both co-sign attestation evidence.

Novelty implication:
- "satellite + quorum + diversified trust" is not by itself a novel contribution of Study 4.

Required distinction:
- Space Fabric is a trusted-execution and attestation architecture; Study 4 is an exact finite recovery-evidence qualification threshold model.

Do not present this preprint as peer-reviewed evidence.

### [10] in-toto

S. Torres-Arias, H. Afzali, T. K. Kuppusamy, R. Curtmola, and J. Cappos, "in-toto: Providing farm-to-table guarantees for bits and bytes," in Proc. 28th USENIX Security Symposium, pp. 1393-1410, 2019.

Official source: https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias

Live-verified support:
- USENIX Security 2019 proceedings record and page range confirmed;
- in-toto provides cryptographic verification of the software supply chain.

Novelty implication:
- Study 6 does not introduce software-supply-chain provenance.

### [11] The Update Framework

The Update Framework, "The Update Framework Specification, v1.0.33," latest stable specification.

Official specification page: https://theupdateframework.io/spec/

Live-verified status and support:
- the official specification page identifies v1.0.33 as the latest stable specification as of 2026-09-06;
- signed metadata, trusted roles, target hashes, thresholds, versions, and expiration are established update-security mechanisms.

Novelty implication:
- Study 6 does not introduce target-hash binding, threshold-signature concepts, or trusted update roles.

### [12] SLSA v1.2 Source Requirements

SLSA, "Source: Requirements for producing source," approved v1.2 specification.

Official source: https://slsa.dev/spec/v1.2/source-requirements

Live-verified support:
- the page is marked Approved;
- the Source track defines increasing levels of trustworthiness and completeness in how source revisions are created;
- source provenance and controlled review are established assurance mechanisms.

Novelty implication:
- Study 6 does not introduce source provenance or source-process assurance requirements.

### [13] SLSA v1.2 Threats & Mitigations

SLSA, "Threats & mitigations," approved v1.2 specification.

Official source: https://slsa.dev/spec/v1.2/threats

Live-verified support:
- the page is marked Approved;
- the threat model explicitly states that intentionally malicious software produced by the producer cannot be directly mitigated through SLSA controls;
- consumers must establish some independent basis for trusting the producer.

Novelty implication:
- Study 6's `APPROVED_BAD_SOURCE` state must not be presented as the discovery that provenance or process conformance can fail to establish benevolent source intent.

## Current-context source not required for the core reference list

### Application-level evidence composition over RATS

A. Sokolov, "Composing Application-Layer Action Evidence with Remote Attestation Procedures," draft-sokolov-rats-aep-composition-05, Aug. 2026. Individual Internet-Draft, no formal IETF standing.

Source: https://datatracker.ietf.org/doc/draft-sokolov-rats-aep-composition/05/

This source shows current interest in composing application action evidence with platform attestation and freshness binding. Because it is an individual Internet-Draft rather than an adopted Working Group document, cite it only if the final manuscript specifically needs this current context.

## Novelty firewall derived from the reviewed literature

Paper 2 must not claim novelty for:

- evidence freshness;
- evidence appraisal;
- remote attestation;
- trusted-baseline recovery;
- cyber-safe mode;
- quorum systems;
- heterogeneous or asymmetric distributed trust;
- satellite architectures that use endorsement quorums;
- supply-chain provenance;
- target hashes or signed update metadata;
- reproducible-build concepts;
- the general fact that a trusted or approved producer can still produce semantically bad software.

The supportable contribution is narrower:

1. exact temporal characterization of false recovery qualification across the frozen Study-3 contact/evidence model, including explicit separation of cache-origin and compromised-producer-origin false qualification;
2. exact first-versus-systematic failure mapping across Study-4 quorum and synthetic provenance-domain rules under separately exhaustive compromise and benign-unavailability populations;
3. exact residual-state and benign-unavailability mapping across Study-6 artifact-assurance gates;
4. a bounded cross-study synthesis of the residual qualification boundaries across these three separate frozen experiments.

Do not use "first," "first-ever," "novel framework," or equivalent priority language unless a later literature audit produces evidence sufficient to support such wording.
