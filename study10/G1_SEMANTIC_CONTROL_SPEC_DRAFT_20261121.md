# S10-RSEI-001 — G1 semantic contract and synthetic-control design (REVIEW DRAFT)

**Status:** `PRE_EXECUTION_SEMANTIC_REVIEW_DRAFT_NOT_FROZEN`. No actual source row, native field-to-variable mapping matrix, selector run, endpoint, synthetic control execution, or completed author sign-off has been produced.

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
This is a **mapping-oracle candidate**, not a selector-output oracle, proof of recovery safety, real dataset evidence, or computed endpoint. Expected selector outcomes must be documented against the pinned selector using a separate, non-circular specification. A standalone implementation must later be checked for parity after G3 approval; no external reviewer is required.

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

## 5. Solo-author review and quality gates

**G1 draft review now:** compare this table word-for-word with frozen Study 9 target semantics; flag ambiguous source provenance, decision-time assumptions, absent criteria, and any direct-rule exception without independent basis. This is an internal analytical aid to the sole author, not independent human review. External human review is not a project gate.

**G2 future freeze (HOLD):** pin dataset rights/release IDs, exact primary cohorts, schemas, Study 9 rubric/selector SHA-256, new derivation registry (empty unless explicit amendment), ten criteria, synthetic fixture serialized inputs, exact expected outputs, exclusion/stop rules and a dated solo-author review decision and a separate technical-oracle implementation plan; no external human reviewer is required. Obtain author approval at this new freeze gate. Distinguish a newly created preregistration timestamp from earlier source exposure; never claim complete pre-exposure blinding.

**G3 future synthetic implementation (HOLD):** code only after separate authorization; test fail-closed boundary, fixture invariants, no real-dataset paths, output manifest reproducibility and separately implemented oracle parity. A failure blocks G4.

**G4+ future source semantics/selector access (HOLD):** require rights clearance, G2/G3 pass, separate execution authorization and audit. When native decision time is not defensible, emit `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` and **no** row-level identifiability percentage.

## 6. Claim boundary

No anomaly label is a verified cyberattack; no telemetry status flag is cryptographic trust or command authorization; no structural identifiability is proof of safe recovery. No transferability, mission-scale effect, detector performance, or operational efficacy claim is authorized.

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
| MEDIUM | Candidate positive fixture has no independently calculated selector-output oracle. | Derive and review expected output from the **exact** pinned selector specification without executing it, compare only after future G3 implementation approval, and preserve any mismatches. |
| MEDIUM | Negative controls lack explicit boundary-value tests for time validity and epoch/claim relations. | Add unexecuted cases `S10_SYN_N_FUTURE_ISSUE`, `S10_SYN_N_EXPIRED`, `S10_SYN_N_EPOCH_MISMATCH`, `S10_SYN_N_CLAIM_EPOCH`, `S10_SYN_N_UNKNOWN_FALSE`. |
| MEDIUM | A failed source-origin/decision-time mapping should not be silently dropped from denominators or assigned a favorable state. | Freeze separate `AMBIGUOUS`/`ABSENT` coverage versus `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` row-level action status, with precise counting denominator and reason. |

**Review disposition:** `INTERNAL_STATIC_ADVERSARIAL_REVIEW_COMPLETE_WITH_OPEN_FINDINGS`. This is **not** a second independent expert review, an independently executed test oracle, or final approval of semantic mappings. All listed concerns must be resolved or explicitly excluded before G2; unresolved high-severity items block freeze. No author sign-off, external peer review or scientific outcome is inferred from this assessment.

## 8. Tightened synthetic fixture contract (proposed, **not executed or frozen**)

The following **v3 draft**, superseding the earlier one-claim v2 proposal, expands `S10_SYN_P0` into an explicit synthetic-only source-state contract. It is not a real satellite record, does not bind to ESA, OPS-SAT, Hack-A-Sat or any actual cryptographic key, and does not execute the frozen selector. The asserted `signature_valid` value is an **interface-level test stub**; testing signature verification cryptography requires a separate G3 test-key and verifier oracle after approval.

```json
{
  "id": "S10_SYN_P0_V3_DRAFT",
  "role": "SYNTHETIC_ONLY",
  "purpose": "State-interface mapping oracle; NOT a cryptographic-verifier test nor a real-flight observation",
  "decision_point": {
    "subject": "SAT_TEST_A",
    "time": 1050,
    "clock": "SYNTHETIC_INTEGER_TIMELINE"
  },
  "cryptographic_check": {
    "state": "known_true",
    "basis": "synthetic_assumed_verifier_outcome",
    "real_signature_verified": false
  },
  "trusted_source": {
    "source_id": "SYN_SOURCE_A",
    "membership": "known_true",
    "membership_set_complete": true
  },
  "freshness": {
    "issue_time": 1000,
    "valid_from": 1000,
    "valid_through": 1100,
    "decision_time": 1050,
    "known_valid": true,
    "interval_boundary_convention": "INCLUSIVE_BOTH_ENDS_PER_FROZEN_EVIDENCE_VERIFIER_SYNTHETIC_FIXTURE_ONLY",
    "valid_for_s": 100,
    "now_s": 1050,
    "authoritative_rule": "issued_at_s <= now_s <= issued_at_s + valid_for_s"
  },
  "evidence_epoch": {
    "claimed": 7,
    "expected": 7,
    "same_subject": true,
    "known_equal": true
  },
  "accepted_claims": {
    "inventory_complete": true,
    "as_of": 1050,
    "subject": "SAT_TEST_A",
    "claims": [
      {
        "claim_id": "S10_SYN_CLAIM_01",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "approved_version",
        "epoch": 7,
        "sequence": 1,
        "value": "SYNTHETIC_APPROVED_VERSION_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_02",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "integrity_measurement_valid",
        "epoch": 7,
        "sequence": 2,
        "value": "SYNTHETIC_INTEGRITY_MEASUREMENT_VALID_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_03",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "authorization_valid",
        "epoch": 7,
        "sequence": 3,
        "value": "SYNTHETIC_AUTHORIZATION_VALID_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_04",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "measured_state_current",
        "epoch": 7,
        "sequence": 4,
        "value": "SYNTHETIC_MEASURED_STATE_CURRENT_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_05",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "authorized_command_path_restored",
        "epoch": 7,
        "sequence": 5,
        "value": "SYNTHETIC_AUTHORIZED_COMMAND_PATH_RESTORED_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_06",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "ground_spacecraft_state_agreed",
        "epoch": 7,
        "sequence": 6,
        "value": "SYNTHETIC_GROUND_SPACECRAFT_STATE_AGREED_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_07",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "required_telemetry_restored",
        "epoch": 7,
        "sequence": 7,
        "value": "SYNTHETIC_REQUIRED_TELEMETRY_RESTORED_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_08",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "health_checks_passed",
        "epoch": 7,
        "sequence": 8,
        "value": "SYNTHETIC_HEALTH_CHECKS_PASSED_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_09",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "no_residual_unauthorized_state",
        "epoch": 7,
        "sequence": 9,
        "value": "SYNTHETIC_NO_RESIDUAL_UNAUTHORIZED_STATE_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      },
      {
        "claim_id": "S10_SYN_CLAIM_10",
        "source_id": "SYN_SOURCE_A",
        "subject": "SAT_TEST_A",
        "key": "recovery_manifest_complete",
        "epoch": 7,
        "sequence": 10,
        "value": "SYNTHETIC_RECOVERY_MANIFEST_COMPLETE_EVIDENCE",
        "issued_at": 1000,
        "valid_through": 1100,
        "accepted": true,
        "current": true,
        "acceptance_basis": "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "issued_at_s": 1000,
        "valid_for_s": 100,
        "timing_semantics": "INCLUSIVE_SYNTHETIC_VERIFIER_TIME_BOUNDARY"
      }
    ],
    "no_other_accepted_current_claims_for_subject_key_epoch": true,
    "contradictory": "known_false",
    "no_other_accepted_current_claims_in_relevant_scope": true,
    "current_claims_count": 10,
    "claim_inventory_interpretation": "EXHAUSTIVE_SYNTHETIC_LEDGER_ONLY"
  },
  "accepted_recovery_criteria": {
    "approved_version": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_01",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "integrity_measurement_valid": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_02",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "authorization_valid": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_03",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "measured_state_current": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_04",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "authorized_command_path_restored": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_05",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "ground_spacecraft_state_agreed": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_06",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "required_telemetry_restored": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_07",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "health_checks_passed": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_08",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "no_residual_unauthorized_state": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_09",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    },
    "recovery_manifest_complete": {
      "present": true,
      "accepted": true,
      "as_of": 1050,
      "claim_id": "S10_SYN_CLAIM_10",
      "acceptance_provenance": "SYNTHETIC_INTERFACE_STUB_NOT_REAL_ATTESTATION"
    }
  },
  "operational_guard": {
    "state": "known_false",
    "native_visibility": "SYNTHETIC_TEST_ONLY",
    "offline_ground_truth_substitute": false
  },
  "authorization_path": {
    "state": "known_true",
    "available_at": 1050,
    "authorized_contact_path": "SYNTHETIC_PATH_A"
  },
  "expected_normalized_mapping": {
    "signature_valid": true,
    "source_trusted": true,
    "fresh": true,
    "epoch_valid": true,
    "contradictory": false,
    "minimum_evidence_complete": true,
    "security_signal": false,
    "authorization_available": true
  },
  "downstream_selector_expected_action": "UNDEFINED_PENDING_INDEPENDENT_EXACT_SELECTOR_ORACLE",
  "effect": "DRAFT_SPECIFICATION_ONLY_NO_EXECUTION_NO_REAL_DATA",
  "safety_contract": {
    "no_real_signature_verification": true,
    "no_cryptographic_acceptance_claim": true,
    "no_telemetry_data_used": true,
    "no_selector_executed": true,
    "no_policy_oracle_validated": true,
    "unknown_must_not_coerce_to_false": true,
    "outcome_is_prospective_not_observed": true
  },
  "synthetic_requirements_equality_contract": {
    "api_reference": "study2/src/study2_security/evidence.py::AttestationResult.requirements_satisfied",
    "meaning": "Synthetic accepted current values must match every explicitly required value, not merely be present",
    "required_values": {
      "approved_version": "SYNTHETIC_APPROVED_VERSION_EVIDENCE",
      "integrity_measurement_valid": "SYNTHETIC_INTEGRITY_MEASUREMENT_VALID_EVIDENCE",
      "authorization_valid": "SYNTHETIC_AUTHORIZATION_VALID_EVIDENCE",
      "measured_state_current": "SYNTHETIC_MEASURED_STATE_CURRENT_EVIDENCE",
      "authorized_command_path_restored": "SYNTHETIC_AUTHORIZED_COMMAND_PATH_RESTORED_EVIDENCE",
      "ground_spacecraft_state_agreed": "SYNTHETIC_GROUND_SPACECRAFT_STATE_AGREED_EVIDENCE",
      "required_telemetry_restored": "SYNTHETIC_REQUIRED_TELEMETRY_RESTORED_EVIDENCE",
      "health_checks_passed": "SYNTHETIC_HEALTH_CHECKS_PASSED_EVIDENCE",
      "no_residual_unauthorized_state": "SYNTHETIC_NO_RESIDUAL_UNAUTHORIZED_STATE_EVIDENCE",
      "recovery_manifest_complete": "SYNTHETIC_RECOVERY_MANIFEST_COMPLETE_EVIDENCE"
    },
    "all_ten_present_and_value_equal_is_assumed_in_this_synthetic_fixture": true,
    "real_dataset_assurance": false,
    "mutation_test_requirement": "If a current accepted claim is absent or its latest accepted value differs from the required value, expected requirements_satisfied=false within a complete synthetic claim ledger",
    "no_actual_attestation_performed": true
  }
}
```

### Required fail-closed behavior to implement only after G3 approval

1. **Known false versus unknown:** Source-state ingestion must retain a three-way distinction `known_true`, `known_false`, and `unknown` before any admissible completion. `unknown` may not be converted to `false` or `true`, counted as observed, or used to select an action.
2. **Closed-world claims only in the synthetic fixture:** The ten-item, criterion-linked accepted-claims ledger above establishes `contradictory=false` only because `inventory_complete=true` and the explicit absence of other accepted current same-subject/same-key/same-epoch claims is a **synthetic premise**. A real dataset may not inherit this closed-world declaration.
3. **Ten named accepted criteria:** The fixture has an explicit accepted/current `present=true` entry with a unique `claim_id` for each of the ten frozen recovery criteria. The matching ten claim rows are synthetic interface premises, not actual signatures or verified operational claims. The new `synthetic_requirements_equality_contract.required_values` dictionary identifies the exact required value of each criterion, matching the frozen `AttestationResult.requirements_satisfied` API's **key-presence plus expected-value equality** check. This resolves the earlier specification ambiguity without running the API or demonstrating real-world completeness. `S10_SYN_N_CRITERIA` removes **one acceptance/presence entry**, not merely a CSV column; its completeness state becomes known false only when the synthetic inventory is proven complete, otherwise `unknown`.
4. **Temporal semantics:** This positive fixture is strictly internal to the 1000–1100 time window at 1050 and does not depend on boundary inclusion. Negative `S10_SYN_N_FUTURE_ISSUE`, `S10_SYN_N_EXPIRED`, and `S10_SYN_N_EPOCH_MISMATCH` must be specified with exact input mutation and expected error state **before** execution. For this **synthetic verifier fixture only**, the frozen `study2/src/study2_security/evidence.py` rule is `issued_at_s <= now_s <= issued_at_s + valid_for_s` (both endpoints inclusive). Thus at `1000` and `1100` the synthetic time component is fresh, at `999` it is future evidence, and at `1101` it is expired. These are **static expected cases**, not executed tests. This does not create or imply an operational decision time for any ESA/OPS/Hack dataset.
5. **Policy oracle independence:** The `expected_normalized_mapping` is an input mapping oracle only. The `downstream_selector_expected_action` deliberately remains `UNDEFINED_PENDING_INDEPENDENT_EXACT_SELECTOR_ORACLE` as a legacy sentinel meaning *separate implementation parity not yet tested*, not an external human-review requirement. G2 must pin the exact selector SHA-256 and freeze author-reviewed expected policy actions plus a plan for a separately implemented oracle; G3 must check parity and record discrepancies before real-data semantic adjudication.
6. **Dataset exclusion:** No synthetic state, source identity, timestamp, or ground truth participates in the ESA/OPS/Hack empirical denominator, mission-independence claims or external-application outcomes.

**Static design acceptance:** The proposed v3 accepted-claim linkage and fixture can be checked for **schema completeness only**, not correctness of actual cryptographic verification, safe recovery, or behavior of the frozen selector. No external human review is planned, and separate technical-oracle parity has not occurred.


## 9. Static four-policy selector action oracle (review design, **not validated by a separate implementation or executed**)

**Normative source:** exact checked `study2/src/study2_security/selectors.py` on repository `main` at `5ee451c2a739cbca7dc948d49239d985c6b4cc07`, whose selector implementation is pinned in frozen Study 9 with SHA-256 `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505`. Study 9 freezes exactly four **primary** policies in order: `S2_B0_FAIL_CLOSED`, `S2_B1_FAIL_OPERATIONAL`, `S2_B2_RISK_THRESHOLD`, `S2_S1_EVIDENCE_AWARE`. Exclude the four `S2_ABL_*` mechanistic ablations. The results below follow a static manual interpretation of the published selector branches. **No selector function has been executed here.**

Evidence qualifies only when `(signature_valid AND source_trusted) AND fresh AND epoch_valid AND NOT contradictory AND minimum_evidence_complete` is `true`. The selector then uses `security_signal` and `authorization_available` according to the separate policy-specific cases below. Unknown values are **not** admissible Boolean `ObservationSummary` inputs; unknown-state handling is a separate future exhaustively enumerated partial-state wrapper and must not be silently coerced.

| Synthetic state (all deviations from P0 indicated) | Evidence qualified? | B0 fail-closed | B1 fail-operational | B2 risk-threshold | S1 evidence-aware |
|---|---|---|---|---|---|
| P0 qualified, signal=0, authorization=1 | TRUE | PROCEED | PRESERVE | PRESERVE | PROCEED |
| N-FRESH fresh=0, all else P0 | FALSE | RESTRICT | PRESERVE | HOLD | HOLD |
| N-CONTRA contradictory=1, all else P0 | FALSE | RESTRICT | PRESERVE | HOLD | HOLD |
| N-SIGNAL signal=1, authorization=0, evidence qualified | TRUE | PROCEED | RESTRICT | RESTRICT | RESTRICT |
| N-SIGNAL-AUTH signal=1, authorization=1, evidence qualified | TRUE | PROCEED | RESTRICT | RESTRICT | PROCEED |
| N-AUTH signal=0, authorization=0, evidence qualified | TRUE | PROCEED | PRESERVE | PRESERVE | PROCEED |

**Legend:** `PROCEED` = `PROCEED_TO_RECOVERY_GATE`; `PRESERVE` = `PRESERVE_LIMITED_OPERATION`; `RESTRICT` = `RESTRICT_AND_REQUEST_AUTHORIZATION`; `HOLD` = `HOLD_AND_REQUIRE_EVIDENCE`.

The table is intentionally **not** an empirical result or a safety recommendation. It reflects that:
- B0 proceeds whenever evidence qualifies, **irrespective** of signal or contact-path availability;
- B1 preserves limited operations unless evidence qualifies **and** security signal is true; authorization availability is not directly consulted;
- B2 holds if evidence fails; otherwise it restricts only when security signal is true; it likewise does not consult authorization availability;
- S1 holds if evidence fails; if evidence qualifies, it restricts only when **both** security signal is true and authorization is unavailable.

These policy definitions have intentionally different behavior, including cases that might appear operationally counterintuitive. **Do not change the policies to align with expected safety intuition**; the purpose of the draft oracle is to pin expectations from the existing frozen code.

**Separate-oracle readiness gate:** The solo researcher must prepare a standalone implementation that derives all four policy outputs **without importing or calling the production selector**, pin its code or derivation, and compare it with the frozen selector on a synthetic fixture suite only after authorization for G3. Any mismatch blocks execution. This static table is an internal self-review artifact, not proof that such independent testing occurred, and **does not** establish a validated oracle. G2 may freeze a documented, author-reviewed expected-output contract and test plan; actual parity testing remains a later G3 prerequisite before real-data work.

**Negative evidence-only fixtures:** For a single bad signature, untrusted source, stale time, epoch mismatch, contradictory accepted claims, or missing accepted recovery criterion, set the corresponding **known** value to failure and recompute `evidence_qualified=false`. This rule does *not* apply when the value is unknown or when the source lacks decision-time observability; those cases are `UNKNOWN`/`NOT_EVALUABLE`, not an observed failure.


## 10. Solo-author review checklist (G1 preparation only; author sign-off pending)

The sole author must review (a) the exact immutable repository commit and Git blob IDs for the Study 2 selector and frozen Study 9 criteria, (b) the G1 v3 synthetic fixture and all proposed negative-control mutations, and (c) the license and cohort provenance ledger **before** any scientific trial results are available. Record reviewer role **SOLE_AUTHOR**, date, version, disclosed lack of personnel independence, evidence references and an explicit attributable decision. Do not claim independent human verification from this checklist.

The sole author should record explicit, falsifiable verdicts with citations for:

1. **Exact eight-value interface:** all variable definitions and all four policy IDs match the frozen Study 9 contracts, and the excluded ablations remain excluded.
2. **Accepted claims and completeness:** each of the ten named criteria is linked to one accepted current *synthetic* claim. The ledger covers the entire relevant source/subject/key/epoch scope for this artificial fixture. No real-data closed-world assumption is licensed by the test.
3. **Truth provenance:** `signature_valid=known_true` and `accepted=true` are synthetic state assumptions, not outputs of `verify_signed_evidence`; a separate real Ed25519 test fixture would require explicit implementation authorization.
4. **Tri-state information preservation:** `unknown` remains distinguishable from `known_false` and `known_true`. The selector consumes only completed Boolean observations; never pass an unknown straight into the selector or default it to false.
5. **Decision-time contract:** evidence validity and source trust are available at the same synthetic decision point, with explicit inclusive/exclusive interval convention agreed before execution.
6. **Policy oracle reproducibility:** a separately written oracle (not importing or calling the production selector) must eventually derive the exact actions for the four primary policies; this means technical implementation separation, not a second reviewer. Compare to the six expected-state cases and a *future* exhaustive 256-complete-state truth table per policy. This paragraph is a proposed test plan, **not** an executed result.
7. **Partial-observation action sets:** only when a real future protocol defines a defensible decision point may a separate wrapper enumerate all admissible completions of unresolved variables; do not report a unique action if multiple completions disagree.
8. **Source independence and rights:** source population overlap is unresolved; ESA mission strata cannot be treated as replicated independent spacecraft, and OPS-SAT v2 source rights and all attribution notices must be preserved.
9. **Negative control failure behavior:** CRC-to-signature, APID-to-trust, timestamp-to-freshness, abnormal-label-to-security-signal, and command-to-authorization substitutions must be rejected without correction to an inferred Boolean.
10. **Gate disposition:** the sole author must choose `AUTHOR_ACCEPT_G1_FOR_G2_CONSIDERATION`, `REVISE_G1`, or `BLOCK` with written reasons. A design-review PASS is **not** a data-use approval, formal preregistration, G3 implementation authorization, G4 mapping authorization, or empirical validation.

**Current disposition:** `SOLE_AUTHOR_IDENTIFIED; AUTHOR_REVIEW_PENDING` and `NO_SEPARATE_ORACLE_EXECUTION`. Identifying the reviewer role is not a review verdict. A later G2 freeze requires separate explicit author approval, pinned artifacts, and resolved methodology/rights decisions. Until then `PREREGISTRATION_FREEZE=HOLD`.

## 11. Prospective negative-control mutation ledger (unexecuted G1 design)

All cases below are **proposals for a future G3 synthetic-only test harness**. They name a single change relative to the `S10_SYN_P0_V3_DRAFT` baseline unless stated otherwise. Do **not** run them as part of G1 or reinterpret synthetic expected outcomes as empirical data. Unknown means an unavailable/undecidable interface value, **not** a negative verdict; no unknown may be passed directly to the frozen Boolean selector.

| Case ID | Exact prospective mutation or source limitation | Expected observation-state outcome | Selector/coverage boundary |
|---|---|---|---|
| `P0_BASE` | No change to v3 P0 fixture | Eight known expected Boolean inputs; ten accepted current claims match ten required values, as a synthetic premise | Only a synthetic mapping-oracle candidate; action oracle is unexecuted |
| `S10_SYN_T_LOWER` | Within an **isolated freshness-verifier test**, set `now_s=1000`, retaining `issued_at_s=1000`, `valid_for_s=100`; do not present the unchanged full P0 accepted-claim snapshot (`as_of=1050`) as valid at this different time | `fresh=known_true` under frozen inclusive verifier rule | Boundary check only |
| `S10_SYN_T_UPPER` | Within an isolated freshness-verifier test, set `now_s=1100`, retaining issue/duration; do not assert the full fixture's accepted-claim/authorization snapshot (`as_of=1050`) is contemporaneous | `fresh=known_true` | Boundary check only |
| `S10_SYN_N_FUTURE_ISSUE` | Within an isolated freshness-verifier test, set `now_s=999`, `issued_at_s=1000`, `valid_for_s=100` | `fresh=known_false` for a **fully specified synthetic verification attempt** | Do not confuse with missing decision time |
| `S10_SYN_N_EXPIRED` | Within an isolated freshness-verifier test, set `now_s=1101`, issue `1000`, valid-for `100` | `fresh=known_false` for a fully specified synthetic verification attempt | No real dataset decision point implied |
| `S10_SYN_N_EPOCH_MISMATCH` | Expected epoch changes to `8`, claimed epoch stays `7` for subject `SAT_TEST_A` | `epoch_valid=known_false` | Exact expected epoch is available in this synthetic case |
| `S10_SYN_N_EPOCH_UNKNOWN` | Withhold expected epoch and any documented verifier result | `epoch_valid=unknown` as Study 10 source-data *observability* | Do not impute known false from the absence of an expected epoch; Study 2 verifier's internal missing-epoch rejection is not an observed source field |
| `S10_SYN_N_CRITERIA` | Remove claim `S10_SYN_CLAIM_10`, update `current_claims_count=9`, and mark the corresponding synthetic `accepted_recovery_criteria.recovery_manifest_complete` as `present=false`/`accepted=false`; keep inventory exhaustive | `minimum_evidence_complete=known_false`, because one requirement is absent in a complete synthetic ledger | No recovery-complete status inferred from the other nine |
| `S10_SYN_N_CRITERIA_VALUE` | Keep claim 10 accepted but change only its `value` to `UNEXPECTED_TEST_VALUE`; preserve expected required-value map and the acceptance record so that **presence/acceptance alone does not imply requirements satisfaction** | Synthetic `requirements_satisfied=false` by key/value mismatch | Requires future independent oracle to check the equality API |
| `S10_SYN_N_LEDGER_INCOMPLETE` | Mark `inventory_complete=false`, omit claim 10, set `current_claims_count=9`, and mark criterion 10 state `unknown` pending completeness evidence, rather than asserting `present=false` for the full source | `minimum_evidence_complete=unknown` | Cannot assert known false from an incomplete source |
| `S10_SYN_N_CONTRADICTION` | Add source `SYN_SOURCE_B` to the **synthetically** trusted-source set; add a second synthetically accepted current claim with a **distinct source** and different value for `(subject=SAT_TEST_A, key=approved_version, epoch=7)`, sequence unique within that source/epoch; set exhaustive ledger `current_claims_count=11` and retain all original ten. These premises do not establish real signatures | `contradictory=known_true` by same-subject/key/epoch differing values across accepted sources | A second claim with no accepted-source semantics is insufficient |
| `S10_SYN_N_CRC` | Replace signature-verifier outcome evidence with a packet CRC-valid flag only | `signature_valid=unknown`, not false or true | `DIRECT`/`DERIVABLE` signature mapping must be rejected |
| `S10_SYN_N_APID` | Withhold trust-set membership, leave APID/source identifier only | `source_trusted=unknown` | Identifier is not trust evidence |
| `S10_SYN_N_TIME` | Withhold validity interval and decision-time reference, retain timestamp alone | `fresh=unknown`; action `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` | Do not use telemetry time as a fabricated decision point |
| `S10_SYN_N_LABEL` | Withhold native guard and retain retrospective anomaly/attack label only | `security_signal=unknown` | Offline truth is not an operational security guard |
| `S10_SYN_N_COMMAND` | Withhold authorized-contact-path status, retain command or script status only | `authorization_available=unknown` | Command presence does not imply authority |
| `S10_SYN_N_MISSING` | Remove all operational evidence fields and their verifier outcomes | All eight recovery-state variables `unknown` | No completed Boolean selector call or fabricated action rate |
| `S10_SYN_N_MIXING` | Declare paired ESA v1/v2 files or Hack-A-Sat competition scoring as independent ESA flight replicates | Provenance classification rejected | No pooling, no spurious independent-study denominator |

**Scope clarification:** The four time-only rows target the frozen evidence verifier's freshness predicate, *not* a complete eight-value observation or selector output. A later full-state temporal test must update every synthetic `as_of`, evidence validity, trust-set snapshot, guard status and authorization-path availability coherently at the chosen decision time, or mark unproven values `unknown`. For the claim-removal and contradiction rows, the claim ledger count and criterion linkage must be mutated together; mismatches should fail schema checks rather than be silently repaired.

**Two separate distinctions must survive G2:** (1) an **observed, documented negative verifier result** versus an unknown variable because a source has no verifier output; and (2) a **fully specified synthetic** negative-time/epoch test versus a real telemetry sample without operational decision time. The frozen Study 2 verifier can return `False` for an unprovided expected epoch; that behavior must not be imported as an observed negative label for OPS-SAT or ESA data.

**Solo-author review obligations:** The author must assess these mutation semantics and the expected-value comparator before a future G2 freeze. No external human reviewer is required. A separately implemented oracle and actual selector parity remain **unexecuted G3 work**. No mutation IDs in this table are experimental outcomes.

## 12. Solo-researcher governance decision (author statement; review verdict pending)

**Investigator structure:** `SOLE_AUTHOR`. The study author has explicitly stated that the research is being conducted solo and does **not** require an independent external human reviewer as a G1/G2 internal gate. The previous draft requirement for a second human reviewer is superseded by this governance decision.

**Safeguards retained:**
- The author performs and records a dated, evidence-referenced G1 review, with an explicit disposition `AUTHOR_ACCEPT_G1_FOR_G2_CONSIDERATION`, `REVISE_G1`, or `BLOCK`. The self-review and lack of personnel independence must be disclosed.
- Exact dataset/version and code identities, clear population and license constraints, stopping rules, and the negative control cases remain documented.
- A **separately written technical oracle**, not importing/calling the production selector, remains a reproducibility check; actual synthetic parity testing is future G3 implementation work subject to authorization. This is implementation independence, **not** independent human review.
- G2 protocol freeze remains a *distinct future* author authorization. G3 implementation, G4 dataset-specific semantic adjudication, real-data execution, publisher submission, and repository merge are not authorized by this governance decision.
- Any independent peer review required later by a journal, institution, or publication process remains outside this internal study-design policy.

**Status:** `SOLO_AUTHOR_ROLE_RECORDED; AUTHOR_G1_VERDICT_PENDING; EXTERNAL_HUMAN_REVIEW_NOT_REQUIRED; G2_FREEZE_HOLD`.
