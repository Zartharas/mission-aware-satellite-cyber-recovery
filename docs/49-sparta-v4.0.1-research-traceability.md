# SPARTA v4.0.1 Research Traceability — Study 1 and Study 2

**Status:** `CURRENT_PUBLICATION_TRACEABILITY_NON_CAUSAL_NON_COMPLIANCE`

**Review date:** 2026-09-02  
**SPARTA version used for this publication crosswalk:** v4.0.1  
**Frozen Study-1/Study-2 science modified:** no  
**Campaign runtime performed:** no

## Purpose

This document provides a publication-current crosswalk between the two frozen studies and the current SPARTA vocabulary. It is a traceability/positioning artifact only. It does not alter the frozen Study-1 event catalog, retrofit new attack mechanisms into either completed campaign, establish SPARTA compliance, or claim that a complete operational attack chain was reproduced.

The frozen Study-1 event catalog remains historical design provenance. Its original SPARTA identifiers are preserved exactly in `configs/wp5_event_catalog.json`. This document separately records how those mappings should be interpreted against SPARTA v4.0.1 and how the richer Study-2 evidence/adversary/contact factors relate—or do not relate—to the taxonomy.

## Version authority

The Aerospace Corporation's SPARTA update page identifies v4.0.1, beginning 2026-08-24, as the current version. The immediately preceding v4.0 release added and revised impact-oriented technique vocabulary, including `IMP-0010` Data Manipulation and `IMP-0011` Command and Data Flow Manipulation.

Authoritative public sources reviewed for this crosswalk include:

- https://sparta.aerospace.org/resources/updates-current
- https://sparta.aerospace.org/resources/updates/v4.0
- https://sparta.aerospace.org/technique/SPARTA
- individual technique pages identified below.

## Mapping rules

Four relationship labels are used:

1. **Direct behavioral correspondence** — the frozen laboratory event closely matches the behavior named by the SPARTA technique, while still omitting operational prerequisites or delivery details.
2. **Strong/qualified correspondence** — the experimental mechanism closely matches a SPARTA behavior/effect, but the study abstracts or does not instantiate part of the SPARTA causal chain.
3. **Conceptual adjacency** — SPARTA addresses a related behavior, impact, or defensive concept, but the experiment did not implement the technique as defined.
4. **Not a SPARTA technique** — the study factor is an experimental condition, adversary budget, contact regime, policy, or analysis construct rather than an attacker technique.

These labels prevent taxonomy matching from becoming a source of invented experimental detail.

## Study-1 frozen event families

### E1 — unauthorized valid command

- **Frozen mapping:** `IA-0007.02`, Malicious Commanding via Valid GS.
- **v4.0.1 interpretation:** direct behavioral correspondence.
- **Boundary:** Study 1 uses a valid synthetic command path and unauthorized command truth. It does not compromise a mission-owned ground station, use operational credentials, reproduce RF commanding, or instantiate SPARTA's complete initial-access chain.

### E2 — replayed command

- **Frozen mapping:** `EX-0001.01`, Replay — Command Packets.
- **v4.0.1 interpretation:** direct behavioral correspondence.
- **Additional v4 adjacency:** `IMP-0011`, Command and Data Flow Manipulation, now describes manipulation of command/data timing, sequence, duplication, delivery, and availability. This is an impact/effect adjacency and does not replace the more specific frozen replay mapping.
- **Boundary:** the study replays a previously valid laboratory command; it does not capture or retransmit real spacecraft traffic.

### E3 — compromised synthetic update

- **Frozen mappings:** `IA-0007.01`, Compromise On-Orbit Update; `EX-0004`, Compromise Boot Memory.
- **v4.0.1 interpretation:** `IA-0007.01` remains a direct behavioral correspondence for a manipulated synthetic update. `EX-0004` is retained as a **historical/conditional** frozen mapping rather than treated as a direct description of every E3 trial, because current SPARTA defines it specifically around compromise of boot memory/configuration and early boot execution.
- **Additional v4 adjacency:** `IMP-0012`, Software, Firmware, or Programmable Logic Manipulation, is conceptually adjacent to malicious software/firmware alteration, but the frozen E3 mechanism must not be retroactively relabeled as that technique.
- **Boundary:** E3 uses controlled synthetic approved/tampered update artifacts; no real boot ROM, bootloader, flight image, production signing key, or operational update service was compromised.

### E4 — telemetry/observability degradation

- **Frozen mapping:** `DE-0003.06`, Telemetry Downlink Modes.
- **v4.0.1 interpretation:** strong/qualified behavioral correspondence to reduced policy-visible telemetry/evidence.
- **Additional v4 adjacency:** `DE-0003.13`, Trusted Process Reporting Suppression, describes malicious suppression/delay/filtering inside trusted reporting processes. It is only conceptual adjacency here because E4 does not perform process injection or compromise a trusted telemetry process.
- **Boundary:** E4 deterministically suppresses/reduces selected software-visible evidence while immutable research truth remains available; it does not jam RF, intercept operational telemetry, or install malicious reporting code.

## Study-2 evidence mechanisms

Study 2 uses `V0`–`V5` as experimental evidence conditions/mechanisms. They are not a SPARTA tactic ladder.

- **V0 complete/current evidence:** not an adversary technique; reference condition.
- **V1 omission:** not a technique by itself. It may resemble the observable consequence of reporting suppression or flow manipulation, but Study-2 V1/A0 does not prescribe an adversarial delivery mechanism.
- **V2 stale/replayed evidence:** strong conceptual correspondence to replay/sequence/timing manipulation (`EX-0001` family and `IMP-0011`) when adversarially caused; the frozen treatment itself is an evidence-state mechanism rather than a complete SPARTA attack path.
- **V3 contradictory independent evidence:** not a technique by itself. If generated by an attacker, falsification could align with `IMP-0010` Data Manipulation, but frozen Block-A V3/A0 represents source disagreement without producer compromise.
- **V4 post-signature manipulation:** strong behavioral correspondence to `IMP-0010` Data Manipulation because the policy-visible information is deliberately altered after signing. The experiment is synthetic and does not claim a specific operational delivery or access technique.
- **V5 bounded producer compromise:** `IMP-0010` is strongly relevant to the **effect semantics** when a controlled producer emits false policy-visible information. The initial-access route to that producer is intentionally outside the frozen Study-2 treatment, so V5 must not be mapped automatically to `IA-0009` Trusted Relationship, `IA-0007` Compromise Ground System, supply-chain compromise, credential theft, or another unmodeled access mechanism.

The v4.0.1 distinction between information-content change (`IMP-0010`) and movement/delivery/timing/sequence/duplication change (`IMP-0011`) is useful for interpreting Study 2 without collapsing distinct V-family mechanisms.

## Study-2 adversary budgets

`A0`–`A3` are **not SPARTA techniques**. They specify how many policy-visible evidence producers, if any, are within the synthetic adversary budget while the verifier, independent trust anchor, experiment truth, and adjudication controls remain outside that budget.

- `A0`: no controlled policy-visible evidence producer.
- `A1`: exactly one controlled producer.
- `A2`: one controlled producer plus modeled contact loss; this remains a coupled profile.
- `A3`: two or more controlled policy-visible producers while the verifier and independent trust anchor remain outside the budget.

SPARTA can help name plausible real-world access paths in future studies, but the completed Study-2 campaign does not identify which SPARTA initial-access technique produced A1/A2/A3.

## Study-2 contact regimes

`K0`–`K4` are **not SPARTA techniques**. They are deterministic software-in-the-loop contact/authorization availability profiles. In particular:

- K0–K3 form the frozen ordered outage series;
- K4 is a separate intermittent/flapping profile;
- none is evidence of RF jamming, downlink denial, ground-station compromise, or another adversarial communications technique.

A future study may causally instantiate a SPARTA communications-disruption mechanism, but that mechanism must not be inferred retroactively from the frozen contact schedule.

## Response/recovery mechanisms and SPARTA countermeasures

Study-1/Study-2 response and recovery mechanisms are policies, not attacker TTPs. They are conceptually adjacent to SPARTA recovery and cyber-safe concepts such as Cyber-safe Mode (`CM0044`) and verified software/update recovery practices, but the experiments do not implement the complete SPARTA countermeasure definitions and do not establish compliance.

The V5 result also sharpens a defensive interpretation: signature/currentness qualification of an evidence claim does not establish that its authorized producer is uncompromised or that its statement is objectively true. That result is consistent with distinguishing integrity/authentication checks from evidence-source trust, but it should not be represented as a validation or invalidation of any SPARTA countermeasure.

## Publication use

The manuscript may state that the frozen event families and Study-2 evidence mechanisms have been cross-walked to SPARTA v4.0.1 using conservative relationship labels. Supplementary Table S4 is the manuscript-facing compact form of this document.

The crosswalk supports three reviewer-facing points:

1. the experiments are anchored in recognized spacecraft-cyber behaviors rather than invented labels;
2. the paper distinguishes experimental factors from attacker techniques instead of forcing every factor into a framework ID; and
3. taxonomy correspondence does not expand the empirical scope of either frozen study.

## Explicit non-claims

This crosswalk does **not** claim:

- SPARTA compliance or certification;
- exhaustive mapping of every tactic, technique, countermeasure, or attack path;
- that A0–A3 or K0–K4 are SPARTA techniques;
- that contact loss was caused by jamming or compromise;
- that V5 identifies a specific real-world initial-access route;
- that E3 compromised boot memory in every trial;
- that E4 implemented trusted-process injection/suppression;
- that a SPARTA mapping validates the empirical results;
- that the studies used operational spacecraft, real RF, production credentials, or proprietary mission data.

## Supersession rule

This document is publication-current traceability as of 2026-09-02. If SPARTA changes again before journal submission, the live version must be checked and any publication-facing version claim updated without changing the frozen experiment definitions or results.