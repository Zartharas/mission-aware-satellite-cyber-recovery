# S10-RSEI-001 — G1 semantic contract and synthetic-control design (REVIEW DRAFT)

**Status:** `PRE_EXECUTION_SEMANTIC_REVIEW_DRAFT_NOT_FROZEN`. No actual source row, native field-to-variable mapping matrix, selector run, endpoint, synthetic control execution, or independent external reviewer decision has been produced.

**Normative sources (unchanged):** `study9/RECOVERY_STATE_MAPPING_RUBRIC.json`, `study9/SEMANTIC_ADJUDICATION_FREEZE.json`, `study9/STUDY9_PROTOCOL.json`; downstream `study2/src/study2_security/selectors.py` frozen selector contract SHA-256 `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505`. The new study must separately pin its exact commit/hash when freezing; the frozen Study 9 registry stays unchanged.

## 1. Required semantics and negative-control substitutions

| Variable | Proof necessary for `DIRECT` | Forbidden shortcut / synthetic negative control |
|---|---|---|
| `signature_valid` | Dataset-native cryptographic signature-verification outcome, tied to known source public key and decision context. | CRC/FECF valid does **not** verify a cryptographic signature. |
| `source_trusted` | Operational membership decision against verifier trust set, not identifier alone. | CCSDS APID, mission name, or sender ID does not prove trust. |
| `fresh` | Evidence issue time, validity interval and decision time under a specified comparison contract. | Timestamp, packet arrival, segment timestamp or sequence alone does not establish freshness. |
| `epoch_valid` | Evidence epoch and expected epoch for same subject with an equality rule. | CCSDS counter, version or orbit epoch alone does not suffice. |
| `contradictory` | Accepted and current competing claims about identical subject/key/epoch, with different values. | Dissimilar sensor measurements or anomaly labels alone do not establish contradictory accepted claims. |
| `minimum_evidence_complete` | Presence of each of the ten frozen accepted recovery criteria, not packet quality. | Complete CSV, telemetry restoration, link quality or error counters alone are insufficient. |
| `security_signal` | Operationally visible native guard/security signal at the decision point. | Offline anomaly/attack labels or inferred attack truth cannot be used as runtime guard state. |
| `authorization_available` | Operational availability of authorized command/contact path at decision point. | A command, `SCRIPT_STATUS`, mission identifier or nominal label is not authorization availability. |

The **ten** minimum-evidence criteria are `approved_version`, `integrity_measurement_valid`, `authorization_valid`, `measured_state_current`, `authorized_command_path_restored`, `ground_spacecraft_state_agreed`, `required_telemetry_restored`, `health_checks_passed`, `no_residual_unauthorized_state`, `recovery_manifest_complete`.

## 2. Adjudication classes and visibility

Use frozen classes `DIRECT`, `DERIVABLE_BY_PREDECLARED_RULE`, `AMBIGUOUS`, `ABSENT`; visibility `OPERATIONAL_NATIVE`, `OFFLINE_GROUND_TRUTH_ONLY`, `EXPERIMENT_METADATA_ONLY`, `DOCUMENTATION_ONLY`.

A mapping requires `(source_id, exact native field(s), provenance/citation, decision-time visibility, class, visibility role, rule ID if applicable, rationale, ambiguity)`. `DIRECT` requires actual operational semantics; `DERIVABLE_BY_PREDECLARED_RULE` requires executable or unambiguous, independently justified derivation **approved before results**. Default new-study derivation registry: **empty**. **No equivalence-by-lexical-name**, **no correlation**, **no default values**, **no inferred authorization**. When uncertain, assign less-assertive class with reason. A schema field not documented to be operationally available at a recovery decision cannot count toward operational coverage.

No new operational mapping verdict for ESA, OPS-SAT or Hack-A-Sat is in this draft. Schema/header inspection to date does not establish any of the eight variables' dataset-native coverage.

## 3. Proposed synthetic positive fixture — specification only

`S10_SYN_P0`, role `SYNTHETIC_ONLY`, no empirical source association, uses a test-only verifier state:
- synthetic issuer and a known testing public key produce a documented simulated signature-check outcome of `true`; do not claim real cryptographic assurance unless a cryptographic verification is actually implemented and tested;
- verifier's explicit trusted-source membership lookup returns `true`;
- synthetic evidence issue time `1000`, validity interval `[1000,1100]`, decision time `1050`: `fresh=true`;
- claimed and expected evidence epochs both `7`: `epoch_valid=true`;
- exactly one accepted current claim per subject/key/epoch: `contradictory=false`;
- accepted state lists **all ten named recovery criteria**: `minimum_evidence_complete=true`;
- synthetic native guard source reports a known **negative** security flag: `security_signal=false` (known false, not missing);
- test authorization/contact path explicitly available: `authorization_available=true`.

Expected normalized 8-variable fixture in frozen order:
```json
{
  "signature_valid": true,
  "source_trusted": true,
  "fresh": true,
  "epoch_valid": true,
  "contradictory": false,
  "minimum_evidence_complete": true,
  "security_signal": false,
  "authorization_available": true
}
```
This is a **mapping-oracle candidate**, not a selector-output oracle, proof of recovery safety, real dataset evidence, or computed endpoint. Independent expected selector outcomes must be established from the exact pinned frozen selector before any evaluator execution is authorized.

## 4. Proposed failure/negative-control matrix (not executed)

| Fixture ID | Withheld or conflicting evidence | Mandatory rejection invariant |
|---|---|---|
| `S10_SYN_N_CRC` | CRC only; no signature-verification result | `signature_valid` **not** `DIRECT` or `DERIVABLE` from CRC |
| `S10_SYN_N_APID` | APID/sender identity only; no trust membership | `source_trusted` not operationally covered |
| `S10_SYN_N_TIME` | timestamp only, no validity/decision-time context | `fresh` not operationally covered |
| `S10_SYN_N_EPOCH` | sequence or TLE epoch alone; no expected evidence epoch | `epoch_valid` not operationally covered |
| `S10_SYN_N_DISAGREE` | disagreement without accepted claim identity/epoch | `contradictory` cannot be asserted true |
| `S10_SYN_N_CRITERIA` | nine of ten accepted criteria, one absent | `minimum_evidence_complete` cannot be true |
| `S10_SYN_N_LABEL` | retrospective anomaly/attack label only | `security_signal` not operationally covered |
| `S10_SYN_N_COMMAND` | command/script status only, no authorization-path state | `authorization_available` not operationally covered |
| `S10_SYN_N_MISSING` | all state missing | all unresolved values remain unknown, never coerced to false |
| `S10_SYN_N_MIXING` | ESA v1/v2 or Hack data passed as independent flight cohorts | source-independence guard rejects improper pooling |

**Oracle restraint:** the negative tests reject invalid mappings; they **do not** assume the precise `AMBIGUOUS` versus `ABSENT` class until a documented synthetic source schema is frozen. A fixture with missing data cannot yield a quantified recovery-action identifiability rate.

## 5. Independent review and quality gates

**G1 draft review now:** compare this table word-for-word with frozen Study 9 target semantics; flag ambiguous source provenance, decision-time assumptions, absent criteria, and any direct-rule exception without independent basis. This analysis is *not* independent external peer review.

**G2 future freeze (HOLD):** pin dataset rights/release IDs, exact primary cohorts, schemas, Study 9 rubric/selector SHA-256, new derivation registry (empty unless explicit amendment), ten criteria, synthetic fixture serialized inputs, exact expected outputs, exclusion/stop rules and independent reviewer identity or independent implementation plan. Obtain author approval at this new freeze gate. Distinguish a newly created preregistration timestamp from earlier source exposure; never claim complete pre-exposure blinding.

**G3 future synthetic implementation (HOLD):** code only after separate authorization; test fail-closed boundary, fixture invariants, no real-dataset paths, output manifest reproducibility and independent checker parity. A failure blocks G4.

**G4+ future source semantics/selector access (HOLD):** require rights clearance, G2/G3 pass, separate execution authorization and audit. When native decision time is not defensible, emit `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` and **no** row-level identifiability percentage.

## 7. Adversarial semantic-control review (internal static review only; not independent human adjudication)

**Review basis:** `study9/RECOVERY_STATE_MAPPING_RUBRIC.json`, `study9/SEMANTIC_ADJUDICATION_FREEZE.json`, and the unmodified `study2/` selector contract. Review examines the authored proposal for hidden assumptions; **no synthetic fixture, real dataset, mapping classifier, or selector was run**.

| Severity | Proposed control / observed design risk | Required pre-freeze resolution |
|---|---|---|
| HIGH | `S10_SYN_P0` currently represents `signature_valid=true` as an asserted simulated verification result, not a reproducible signature-verifier oracle. | Lock test-key fixture and verifier semantics, or explicitly label as a *synthetic state-interface-only* fixture and forbid cryptographic-verification claims. |
| HIGH | `contradictory=false` is not established merely by seeing one claim unless the complete accepted current claim set at decision time is known. | Freeze an explicit closed-world synthetic accepted-claims ledger with subject/key/epoch, acceptance state, decision time and exhaustive competing-value check. Never transfer this closed-world assumption to a real dataset. |
| HIGH | `minimum_evidence_complete=true` depends on ten accepted, current *recovery* criteria, not ten arbitrary named CSV attributes. | For synthetic positive control, enumerate all ten criteria with acceptance and decision-time availability; remove one accepted criterion in `S10_SYN_N_CRITERIA`. |
| HIGH | False and missing are different states for `security_signal`, `authorization_available` and all other required Boolean interfaces. | Require tri-state input (`known_true`, `known_false`, `unknown`) at the measurement boundary; reject coercion `unknown -> false` or `unknown -> true`. |
| HIGH | Native timestamp or event order cannot by itself define a recovery decision point. | If a source lacks an evidence issue time, validity interval and independently defined decision point, retain `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION`. |
| MEDIUM | Source licenses and anonymized identity limit defensible cross-population replication claims. | Preserve source family and overlap ledger; report ESA Mission1/2/3 as common-curator mission strata, OPS mission overlap unresolved, ESA v1/v2 paired, Hack-A-Sat unpooled. |
| MEDIUM | Candidate positive fixture has no independently calculated selector-output oracle. | Independently specify expected output from the **exact** pinned selector implementation, compare only after future G3 implementation approval, and preserve any mismatches. |
| MEDIUM | Negative controls lack explicit boundary-value tests for time validity and epoch/claim relations. | Add unexecuted cases `S10_SYN_N_FUTURE_ISSUE`, `S10_SYN_N_EXPIRED`, `S10_SYN_N_EPOCH_MISMATCH`, `S10_SYN_N_CLAIM_EPOCH`, `S10_SYN_N_UNKNOWN_FALSE`. |
| MEDIUM | A failed source-origin/decision-time mapping should not be silently dropped from denominators or assigned a favorable state. | Freeze separate `AMBIGUOUS`/`ABSENT` coverage versus `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` row-level action status, with precise counting denominator and reason. |

**Review disposition:** `INTERNAL_STATIC_ADVERSARIAL_REVIEW_COMPLETE_WITH_OPEN_FINDINGS`. This is **not** a second independent expert review, an independently executed test oracle, or final approval of semantic mappings. All listed concerns must be resolved or explicitly excluded before G2; unresolved high-severity items block freeze. No author approval, external peer review or scientific outcome is inferred from this assessment.

## 6. Claim boundary

No anomaly label is a verified cyberattack; no telemetry status flag is cryptographic trust or command authorization; no structural identifiability is proof of safe recovery. No transferability, mission-scale effect, detector performance, or operational efficacy claim is authorized.
