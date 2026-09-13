# CEAS Space Journal Cover Letter - Paper 3

**Date:** September 13, 2026
**Editor:** Professor Franco Bernelli, Editor-in-Chief
**Article type:** Original Research Article / Original Paper

Dear Professor Bernelli and Editors,

I am pleased to submit the manuscript entitled **"Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence"** for consideration as an Original Research Article in *CEAS Space Journal*. I am the sole author and an independent researcher.

The manuscript addresses a space-systems assurance question at the intersection of cybersecurity and artificial intelligence in space. It asks whether a learned satellite cyber-recovery selector can make the correct recovery decision when trusted-looking evidence may itself be false, and how that boundary changes when corroborating evidence is independently informative versus correlated with the compromised path. This fits the journal's coverage of space systems, cybersecurity for space systems, and artificial intelligence in space.

The study reports experiment `S7-LSO-001`, a separately frozen deterministic finite assurance experiment comprising exactly **1,033 modeled observations**. It exhaustively evaluates the complete eight-feature visible-state lattice for a deterministic comparator and visible-only learner, the complete nine-feature lattice for a corroboration-aware learner, and nine prespecified hidden-truth collision observations. The central result is deliberately bounded: exact learning of a visible decision boundary does not establish correctness when decisive truth is absent from the learner's observables; corroboration can change the decision boundary, but correlated false corroboration restores the unsafe decision. The accepted execution and core outputs are hash-frozen, and a separately implemented repository auditor reconstructs all 1,033 policy decisions with zero mismatches without importing or invoking the primary analyzer.

The manuscript also distinguishes itself from recent CEAS work on spacecraft fault detection, isolation and recovery and AI-supported diagnosis/reconfiguration. Those studies address fault representation, detection, diagnosis, or recovery implementation. Study 7 instead evaluates the trust and information sufficiency of the evidence feeding a cyber-recovery authorization decision under an adversarial evidence model.

For transparency, this manuscript belongs to a broader independent satellite-cybersecurity research program with related manuscripts under consideration elsewhere. None of those manuscripts uses Study 7's 1,033-observation population as experimental evidence. The relationships are:

- **AIAA Journal of Aerospace Information Systems manuscript 2026-09-I012066:** Studies 1 and 2; response/recovery under contact and adversarial-evidence constraints. Study-2 V5 is antecedent motivation only.
- **IEEE Transactions on Aerospace and Electronic Systems:** Studies 3, 4, and 6; temporal evidence, producer composition, and artifact assurance.
- **Acta Astronautica manuscript AA-D-26-02872:** Study 8; contact-aware cryptographic agility.
- **Journal of Space Safety Engineering manuscript "Measuring Software Supply-Chain Assurance for Spacecraft Flight Software: A Controlled, Comparative Evaluation":** separate repository and software supply-chain experiment; no Study-7 data, model, or endpoints.

The present manuscript is original, has not been published previously, and is not under consideration by another journal. No text, tables, figures, or experimental observations from the related manuscripts are reused as Paper-3 evidence beyond properly cited background or antecedent material.

OpenAI ChatGPT, accessed through the ChatGPT web interface, was used as an interactive assistant during Study 7 development and manuscript preparation. Before the results freeze, it assisted with protocol refinement, code and test drafting, repository and audit documentation, and verification review. After the freeze, it assisted with manuscript organization and drafting, literature-source verification, compliance checking, and language refinement. I made and approved the research decisions, controlled the repository and experimental execution, reviewed the code and text changes, and verified the frozen outputs and numerical claims. This use is disclosed in Methods Section 3.5.

The manuscript includes the required Statements and Declarations, including funding, competing interests, author contributions, ethics/consent, data availability, and code availability. The public repository contains the protocol, implementation, frozen result records, and separately implemented audit materials. The exact accepted Study-7 evidence is permanently archived on Zenodo at https://doi.org/10.5281/zenodo.22732060 (concept DOI https://doi.org/10.5281/zenodo.22732059).

Thank you for considering this work for *CEAS Space Journal*. I believe its focus on the assurance boundary of learned cyber-recovery decisions will be relevant to readers working on spacecraft autonomy, cybersecurity, fault management, dependable AI, and mission assurance.

Sincerely,
**Aman Kumar Singh, M.S., D.Sc.**
Independent Researcher
The Woodlands, Texas, United States
ORCID: 0009-0008-9752-3743
Email: asingh65430@ucumberlands.edu
