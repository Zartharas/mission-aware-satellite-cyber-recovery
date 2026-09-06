# TAES Paper 2 Citation and Prior-Art Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Verdict:** `PASS_WITH_BIBLIOGRAPHIC_FINALIZATION_PENDING`

## 1. Purpose

This audit verifies that the external literature used in the component manuscript supports the claims assigned to it and that prior art is not converted into a manuscript novelty claim. It does not replace the final IEEE reference-format audit after single-source assembly.

## 2. Space cybersecurity context

PASS.

`Why is Space Cybersecurity Unique?` supports the manuscript's contextual statements that space cybersecurity is shaped by coupled constraints including permanent hardware inaccessibility after launch, communication gaps that mandate autonomous decisions, tight subsystem dependencies, and mission continuity/availability concerns.

The manuscript correctly does **not** use this source to claim that Study 3's K4 schedule is an orbit or real ground-contact model.

The 2026 `Trust Without Boundaries` preprint supports the claim that modular satellite flight-software components can possess broadly shared legitimate authority and that a compromised component can abuse legitimate architectural privileges. It remains explicitly identified as a preprint.

The Curbo/Falco 2025 IEEE Aerospace Conference paper's title, authors, conference identity, and DOI were corroborated. It is used only as context for testable secure-by-design/cyber-resilience requirements.

## 3. SPARTA

PASS.

The current SPARTA `CM0044 Cyber-safe Mode` page directly describes an integrity-protected, validated software/configuration baseline and a separately authorized, integrity-verified maintenance process preserving a recoverable trusted version.

The manuscript correctly treats SPARTA as design motivation/prior art and makes no compliance claim.

## 4. RATS architecture and freshness

PASS.

RFC 9334 directly supports:

- the Attester/Evidence/Verifier/Relying-Party vocabulary;
- appraisal policy concepts;
- explicit freshness evaluation;
- the limitation that a race remains possible because the Attester state or appraisal policy can change immediately after Evidence or an Attestation Result is generated.

This is appropriate support for the manuscript's claim that freshness narrows recentness but does not guarantee instantaneous synchronization with hidden state.

The manuscript does not claim that Study 3 invented freshness or evidence appraisal.

## 5. RATS multi-verifier work

PASS.

`draft-ietf-rats-multi-verifier-00` is an active RATS Working Group Internet-Draft dated 5 May 2026. It describes hierarchical, cascaded, and hybrid topologies; Partial Evidence; Partial Attestation Results; and aggregated attestation results across multiple Verifiers.

The manuscript preserves the critical distinction:

- RATS multi-verifier: multiple **Verifiers/appraisers** coordinating over a composite Attester;
- Study 4: multiple **evidence producers** whose claims are evaluated by a deterministic recovery-qualification rule.

The draft is labeled work in progress and is not treated as an RFC.

## 6. Distributed quorum prior art

PASS.

Malkhi and Reiter's `Byzantine quorum systems` bibliographic record was verified as Distributed Computing 11(4), 203-213 (1998), DOI `10.1007/s004460050050`.

Alpos, Cachin, Tackmann, and Zanolini's `Asymmetric distributed trust` was verified as Distributed Computing 37, 247-277 (2024), DOI `10.1007/s00446-024-00469-1`.

These sources support the prior-art position that quorum systems, arbitrary-fault tolerance, and asymmetric trust assumptions are established foundations.

The manuscript correctly does not claim new quorum theory, Byzantine consensus, or heterogeneous-trust theory.

## 7. Satellite quorum overlap

PASS.

The 2026 `Space Fabric` preprint explicitly uses a Byzantine-tolerant endorsement quorum of distributed ground stations and two secure elements that co-sign attestation evidence.

The manuscript therefore correctly avoids claiming that "satellite + quorum + diversified trust" is itself novel. `Space Fabric` remains labeled as a preprint and is distinguished from Study 4's finite recovery-evidence threshold model.

## 8. Software-supply-chain prior art

PASS.

The USENIX 2019 in-toto publication record and page range were verified. It supports the statement that cryptographically verifiable software-supply-chain provenance predates Study 6.

The official TUF specification repository states that its `master` branch points to the latest stable specification. The retrieved current page did not expose a stable numeric version. The source ledger was therefore corrected to keep TUF version-neutral rather than asserting an unverified numeric version.

SLSA v1.2 Source Requirements is currently marked Approved. Its Threats & Mitigations text explicitly states that an intentionally malicious producer cannot be directly mitigated through SLSA controls and that consumers must establish some basis for trusting the software producer.

This directly constrains interpretation of Study 6's `APPROVED_BAD_SOURCE` state. The manuscript correctly presents that state as a finite observability boundary, not as discovery of a previously unknown provenance limitation.

## 9. Novelty audit

PASS WITH NARROW CLAIM.

The manuscript does not claim novelty for:

- freshness;
- evidence appraisal;
- attestation;
- cyber-safe recovery;
- trusted baselines;
- quorum systems;
- asymmetric trust;
- satellite endorsement quorums;
- provenance;
- target hashes;
- reproducible builds;
- the general fact that a trusted producer can intentionally produce harmful or semantically bad content.

The supportable manuscript contribution remains:

1. exact temporal residual-boundary characterization in Study 3;
2. exact first-versus-systematic producer/provenance threshold mapping in Study 4;
3. exact artifact residual-state and benign-unavailability mapping in Study 6;
4. bounded mechanism-level synthesis across the three separately frozen models.

The sentence stating that the reviewed literature did not identify a directly matching spacecraft cyber-recovery study is retained only as a bounded literature-positioning statement. It must not be strengthened to "first," "first-ever," or equivalent priority language.

## 10. Bibliographic issues still pending

Before submission:

- convert all references to final IEEE style;
- verify all author names, titles, publication venues, years, volumes/issues/pages, DOIs, and URLs in the assembled manuscript;
- identify preprints and Internet-Drafts consistently;
- add access dates where appropriate for online standards/framework sources;
- recheck that any Internet-Draft version cited is still the intended version at the date of submission;
- ensure reference numbering remains consistent after final manuscript assembly.

## 11. Final citation-audit verdict

The literature currently supports the manuscript's scientific positioning and novelty firewall. No literature conflict was identified that requires changing or rerunning a frozen study.

Final citation PASS remains conditional on the assembled manuscript reference list and line-by-line citation placement review.
