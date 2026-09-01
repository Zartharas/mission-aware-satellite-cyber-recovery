---- MODULE Study1P7 ----
EXTENDS TLC

Events == {"E1", "E2", "E3", "E4"}
Missions == {"M0", "M2", "M4"}
Contacts == {"C0", "C1"}
EvidenceConditions == {"T0", "T1"}
Policies == {"P0", "P1", "P2", "P4", "P5"}
Actions == {
    "OBSERVE_ONLY",
    "ISOLATE_MODELED_SOURCE",
    "RESTRICT_HIGH_RISK_COMMANDS",
    "ENTER_SAFE_MODE",
    "REQUEST_VERIFIED_ROLLBACK"
}

EvidenceSufficient(e, t) ==
    CASE e = "E1" -> t = "T0"
      [] e = "E2" -> t = "T0"
      [] e = "E3" -> t = "T0"
      [] e = "E4" -> FALSE
      [] OTHER -> FALSE

InsufficientPolicy(m, c) ==
    CASE <<m, c>> = <<"M0", "C0">> -> "P2"
      [] <<m, c>> = <<"M0", "C1">> -> "P2"
      [] <<m, c>> = <<"M2", "C0">> -> "P4"
      [] <<m, c>> = <<"M2", "C1">> -> "P4"
      [] <<m, c>> = <<"M4", "C0">> -> "P2"
      [] <<m, c>> = <<"M4", "C1">> -> "P4"
      [] OTHER -> "P0"

SufficientPolicy(e, m, c) ==
    CASE <<e, m, c>> = <<"E1", "M0", "C0">> -> "P1"
      [] <<e, m, c>> = <<"E1", "M0", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E1", "M2", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E1", "M2", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E1", "M4", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E1", "M4", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E2", "M0", "C0">> -> "P1"
      [] <<e, m, c>> = <<"E2", "M0", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E2", "M2", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E2", "M2", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E2", "M4", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E2", "M4", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E3", "M0", "C0">> -> "P5"
      [] <<e, m, c>> = <<"E3", "M0", "C1">> -> "P5"
      [] <<e, m, c>> = <<"E3", "M2", "C0">> -> "P5"
      [] <<e, m, c>> = <<"E3", "M2", "C1">> -> "P5"
      [] <<e, m, c>> = <<"E3", "M4", "C0">> -> "P5"
      [] <<e, m, c>> = <<"E3", "M4", "C1">> -> "P5"
      [] <<e, m, c>> = <<"E4", "M0", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E4", "M0", "C1">> -> "P2"
      [] <<e, m, c>> = <<"E4", "M2", "C0">> -> "P4"
      [] <<e, m, c>> = <<"E4", "M2", "C1">> -> "P4"
      [] <<e, m, c>> = <<"E4", "M4", "C0">> -> "P2"
      [] <<e, m, c>> = <<"E4", "M4", "C1">> -> "P4"
      [] OTHER -> "P0"

ExpectedPolicy(e, m, c, t) ==
    IF EvidenceSufficient(e, t)
    THEN SufficientPolicy(e, m, c)
    ELSE InsufficientPolicy(m, c)

PolicyAction(p) ==
    CASE p = "P0" -> "OBSERVE_ONLY"
      [] p = "P1" -> "ISOLATE_MODELED_SOURCE"
      [] p = "P2" -> "RESTRICT_HIGH_RISK_COMMANDS"
      [] p = "P4" -> "ENTER_SAFE_MODE"
      [] p = "P5" -> "REQUEST_VERIFIED_ROLLBACK"
      [] OTHER -> "OBSERVE_ONLY"

VARIABLES event, mission, contact, evidenceCondition,
          evidenceSufficient, delegatedPolicy, selectedAction,
          oracleVisibleToPolicy

vars == <<event, mission, contact, evidenceCondition,
          evidenceSufficient, delegatedPolicy, selectedAction,
          oracleVisibleToPolicy>>

Init ==
    /\ event \in Events
    /\ mission \in Missions
    /\ contact \in Contacts
    /\ evidenceCondition \in EvidenceConditions
    /\ evidenceSufficient = EvidenceSufficient(event, evidenceCondition)
    /\ delegatedPolicy = ExpectedPolicy(event, mission, contact, evidenceCondition)
    /\ selectedAction = PolicyAction(delegatedPolicy)
    /\ oracleVisibleToPolicy = FALSE

Next == UNCHANGED vars

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ event \in Events
    /\ mission \in Missions
    /\ contact \in Contacts
    /\ evidenceCondition \in EvidenceConditions
    /\ evidenceSufficient \in BOOLEAN
    /\ delegatedPolicy \in Policies
    /\ selectedAction \in Actions
    /\ oracleVisibleToPolicy \in BOOLEAN

OracleIsolation == ~oracleVisibleToPolicy

EvidenceAssessmentConformance ==
    evidenceSufficient = EvidenceSufficient(event, evidenceCondition)

P7DecisionConformance ==
    /\ delegatedPolicy = ExpectedPolicy(event, mission, contact, evidenceCondition)
    /\ selectedAction = PolicyAction(delegatedPolicy)

====
