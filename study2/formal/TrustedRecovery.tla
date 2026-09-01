---- MODULE TrustedRecovery ----
EXTENDS TLC

Phases == {"RESPONDING", "RECOVERY_PENDING", "TRUSTED_RECOVERY_CONFIRMED", "RECOVERY_FAILED"}
DecisionPaths == {"UNSELECTED", "EVIDENCE_SUFFICIENT", "FALLBACK"}

VARIABLES phase,
          evidenceAuthenticated,
          evidenceFresh,
          evidenceComplete,
          evidenceContradictory,
          authorizationValid,
          residualUnauthorizedState,
          oracleVisibleToPolicy,
          decisionPath,
          groundTruthToken

vars == <<phase,
          evidenceAuthenticated,
          evidenceFresh,
          evidenceComplete,
          evidenceContradictory,
          authorizationValid,
          residualUnauthorizedState,
          oracleVisibleToPolicy,
          decisionPath,
          groundTruthToken>>

EvidenceQualified ==
    evidenceAuthenticated
    /\ evidenceFresh
    /\ evidenceComplete
    /\ ~evidenceContradictory

Init ==
    /\ phase = "RESPONDING"
    /\ evidenceAuthenticated \in BOOLEAN
    /\ evidenceFresh \in BOOLEAN
    /\ evidenceComplete \in BOOLEAN
    /\ evidenceContradictory \in BOOLEAN
    /\ authorizationValid \in BOOLEAN
    /\ residualUnauthorizedState \in BOOLEAN
    /\ oracleVisibleToPolicy = FALSE
    /\ decisionPath = "UNSELECTED"
    /\ groundTruthToken = "IMMUTABLE_GROUND_TRUTH"

ChangeEvidence ==
    /\ phase \in {"RESPONDING", "RECOVERY_PENDING"}
    /\ \E ea, ef, ec, ex \in BOOLEAN:
        /\ <<ea, ef, ec, ex>> #
           <<evidenceAuthenticated, evidenceFresh,
             evidenceComplete, evidenceContradictory>>
        /\ evidenceAuthenticated' = ea
        /\ evidenceFresh' = ef
        /\ evidenceComplete' = ec
        /\ evidenceContradictory' = ex
    /\ decisionPath' = "UNSELECTED"
    /\ UNCHANGED <<phase, authorizationValid, residualUnauthorizedState,
                    oracleVisibleToPolicy, groundTruthToken>>

SelectDecision ==
    /\ phase \in {"RESPONDING", "RECOVERY_PENDING"}
    /\ decisionPath = "UNSELECTED"
    /\ decisionPath' = IF EvidenceQualified
                       THEN "EVIDENCE_SUFFICIENT"
                       ELSE "FALLBACK"
    /\ UNCHANGED <<phase, evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    authorizationValid, residualUnauthorizedState,
                    oracleVisibleToPolicy, groundTruthToken>>

BeginRecovery ==
    /\ phase = "RESPONDING"
    /\ decisionPath # "UNSELECTED"
    /\ phase' = "RECOVERY_PENDING"
    /\ UNCHANGED <<evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    authorizationValid, residualUnauthorizedState,
                    oracleVisibleToPolicy, decisionPath, groundTruthToken>>

GrantAuthorization ==
    /\ phase = "RECOVERY_PENDING"
    /\ ~authorizationValid
    /\ authorizationValid' = TRUE
    /\ UNCHANGED <<phase, evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    residualUnauthorizedState, oracleVisibleToPolicy,
                    decisionPath, groundTruthToken>>

ClearResidualUnauthorizedState ==
    /\ phase = "RECOVERY_PENDING"
    /\ residualUnauthorizedState
    /\ residualUnauthorizedState' = FALSE
    /\ UNCHANGED <<phase, evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    authorizationValid, oracleVisibleToPolicy,
                    decisionPath, groundTruthToken>>

ConfirmTrustedRecovery ==
    /\ phase = "RECOVERY_PENDING"
    /\ decisionPath = "EVIDENCE_SUFFICIENT"
    /\ EvidenceQualified
    /\ authorizationValid
    /\ ~residualUnauthorizedState
    /\ ~oracleVisibleToPolicy
    /\ phase' = "TRUSTED_RECOVERY_CONFIRMED"
    /\ UNCHANGED <<evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    authorizationValid, residualUnauthorizedState,
                    oracleVisibleToPolicy, decisionPath, groundTruthToken>>

FailRecovery ==
    /\ phase = "RECOVERY_PENDING"
    /\ phase' = "RECOVERY_FAILED"
    /\ UNCHANGED <<evidenceAuthenticated, evidenceFresh,
                    evidenceComplete, evidenceContradictory,
                    authorizationValid, residualUnauthorizedState,
                    oracleVisibleToPolicy, decisionPath, groundTruthToken>>

Next ==
    \/ ChangeEvidence
    \/ SelectDecision
    \/ BeginRecovery
    \/ GrantAuthorization
    \/ ClearResidualUnauthorizedState
    \/ ConfirmTrustedRecovery
    \/ FailRecovery

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ phase \in Phases
    /\ evidenceAuthenticated \in BOOLEAN
    /\ evidenceFresh \in BOOLEAN
    /\ evidenceComplete \in BOOLEAN
    /\ evidenceContradictory \in BOOLEAN
    /\ authorizationValid \in BOOLEAN
    /\ residualUnauthorizedState \in BOOLEAN
    /\ oracleVisibleToPolicy \in BOOLEAN
    /\ decisionPath \in DecisionPaths
    /\ groundTruthToken = "IMMUTABLE_GROUND_TRUTH"

OracleIsolation == ~oracleVisibleToPolicy

GroundTruthImmutable == groundTruthToken = "IMMUTABLE_GROUND_TRUTH"

EvidenceSufficientBranchIntegrity ==
    decisionPath = "EVIDENCE_SUFFICIENT" => EvidenceQualified

EvidenceFallbackIntegrity ==
    decisionPath = "FALLBACK" => ~EvidenceQualified

TrustedRecoverySoundness ==
    phase = "TRUSTED_RECOVERY_CONFIRMED" =>
        /\ EvidenceQualified
        /\ authorizationValid
        /\ ~residualUnauthorizedState
        /\ decisionPath = "EVIDENCE_SUFFICIENT"
        /\ ~oracleVisibleToPolicy

====
