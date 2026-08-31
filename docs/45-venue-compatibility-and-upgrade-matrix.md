# Venue Compatibility and Research-Upgrade Matrix

## Status

`CURRENT_2026-08-31_SCOPE_REVIEW`

This document is a research-planning aid, not an immigration-law designation or publisher acceptance prediction. Journal quartile/reputation may change over time; the live journal scope must be rechecked before each submission.

## Study 1 — current frozen paper

### Computers & Security — primary target

**Scope alignment:** very high.

The journal emphasizes leading-edge information-security research with practical security value. Recent issues include space-sector attack-surface research, SatCom cybersecurity, satellite intrusion detection, and cyber-physical security-testbed work.

Current paper alignment:

- applied cybersecurity response/recovery problem — strong;
- controlled cyber-physical experimentation — strong;
- practical security/availability implications — strong;
- satellite-specific context — already represented in venue literature;
- public reproducibility — strong;
- threat/adversary framing — upgraded in current PR;
- trust/evidence model — upgraded in current PR;
- closest-work differentiation — upgraded in current PR.

**Remaining Study 1 work before submission:** editorial integration, bibliography merge, final citation/claim audit, final live Guide for Authors check, and unresolved author attestations. No new campaign observations are required merely to increase sample size.

Official journal page: https://shop.elsevier.com/journals/computers-and-security/0167-4048

## Study 2 — generalization/security methodology

### IEEE Transactions on Dependable and Secure Computing (TDSC) — primary higher-bar target

**Scope alignment:** high if Study 2 adds general security/dependability methodology.

Relevant scope themes include secure/dependable system design and evaluation, recovery/survivability, attack models, experimental testbeds, statistical methods, safety-critical computing, cyber-physical systems, and aerospace/satellite contexts.

Required upgrade beyond Study 1:

- formal adversary/observation model;
- multiple evidence-failure mechanisms;
- multiple connectivity regimes;
- fault-versus-attack ambiguity;
- selector ablation;
- stronger policy baselines;
- formal assurance/model checking;
- broader estimands showing a methodology transferable beyond one frozen satellite campaign.

Study 2 design candidate: `docs/44-study2-secure-response-generalization-design.md`.

Official journal/topics page: https://www.computer.org/digital-library/journals/tq/tdsc-topics

### ACM Transactions on Privacy and Security (TOPS) — strong alternative

**Scope alignment:** high if the work is generalized as system security rather than solely aerospace engineering.

TOPS explicitly includes authentication/authorization, recovery and survivable operation, risk analysis, assurance/formal methods, specialized secure systems, application-specific threats/trade-offs, and integrity/availability/survivability policy trade-offs.

Required upgrade beyond Study 1:

- explicit trust/adversary model;
- formal security properties and policy semantics;
- adversarial observation/evidence model;
- assurance argument or formal verification;
- generalizable secure-response mechanism/method rather than only a satellite-specific comparative result.

Official topics page: https://www.tissec.hosting.acm.org/content/process/topics-of-interest/

## Study 3 — aerospace engineering validation

### IEEE Transactions on Aerospace and Electronic Systems (TAES)

**Scope alignment:** high after increased aerospace-system realism.

TAES covers organization, design, development, integration, and operation of complex aerospace systems including spacecraft, telemetry, automated testing, command/control, and fault-tolerant systems. Its fault-tolerant area explicitly includes rollback recovery, fault containment, and reliability analysis.

Required upgrade beyond Study 2:

- modeled orbital/access contact schedules rather than one abstract outage;
- flight-like resource/performance measurements;
- spacecraft mission-phase profiles;
- representative HIL validation;
- systems-level V&V and transfer analysis;
- continued avoidance of flight-certification claims.

Official pages:

- https://ieee-aess.org/publications/taes
- https://ieee-aess.org/publications/transactions-aes/technical-areas-editors/descriptions

### AIAA Journal of Aerospace Information Systems (JAIS)

**Scope alignment:** very high for an aerospace-information-systems/HIL version.

JAIS seeks original work in aerospace computing, information systems, software engineering, embedded-system verification and validation, autonomous systems, systems health management, systems engineering, safety, resilience, and mission assurance.

Required upgrade beyond Study 1/2:

- clearer response-software architecture and state-machine presentation;
- V&V traceability;
- mission-assurance/system-health linkage;
- system-performance characterization;
- optionally HIL validation with flight-like compute while remaining entirely researcher-controlled and RF-free.

Official scope page: https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/

## Compatibility matrix

| Research capability | C&S Study 1 | TDSC Study 2 | TOPS Study 2 | TAES Study 3 | JAIS Study 3 |
|---|---:|---:|---:|---:|---:|
| Frozen multi-policy SIL campaign | Core | Foundation | Foundation | Foundation | Core |
| Formal adversary model | Strongly useful | Required-level value | Required-level value | Useful | Useful |
| Trust/evidence boundary model | Strongly useful | Core | Core | Useful | Useful |
| SPARTA behavioral mapping | Strongly useful | Useful | Useful | Useful | Useful |
| NIST incident-response mapping | Strongly useful | Useful | Useful | Limited | Limited |
| Multiple evidence-failure mechanisms | Future | Core | Core | Useful | Useful |
| Multiple contact regimes | Future | Core | Useful | Core | Core |
| Fault/attack ambiguity | Future | Core | Useful | Core | Core |
| Selector ablation | Future | Core | Core | Useful | Useful |
| Strong non-adaptive baselines | Useful | Core | Core | Useful | Useful |
| Formal verification/model checking | Optional | Core differentiator | Core differentiator | Strong | Strong |
| Orbital/access realism | Not required | Useful | Limited | Core | Core |
| Flight-like resource measurements | Not required | Useful | Limited | Core | Core |
| HIL subset | Not required | Useful | Optional | Core | Core |

## Publication-program rule

Do not expand Study 1 after the fact simply to make it look larger. New adversarial, contact, fault, formal-verification, or HIL evidence should be produced under separately frozen Study 2/Study 3 designs. This preserves the integrity of the current 720-observation paper while creating genuinely distinct future contributions suitable for different high-quality venues.
