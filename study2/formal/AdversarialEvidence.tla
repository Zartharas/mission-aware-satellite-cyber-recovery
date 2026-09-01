---- MODULE AdversarialEvidence ----
EXTENDS Naturals, TLC

EvidenceConditions == {"V0", "V1", "V2", "V3", "V4", "V5"}
Adversaries == {"A0", "A1", "A2", "A3"}
Contacts == {"K0", "K1", "K2", "K3", "K4"}

VARIABLES phase, evidenceCondition, adversary, contact,
          authenticated, complete, fresh, epochValid, sequenceValid,
          contradiction, evidenceQualified,
          oracleVisibleToPolicy, groundTruthToken, seedToken, treatmentToken,
          verifierCompromised, independentTrustAnchor, hiddenTruthfulEvidence,
          trustedRecovery

vars == <<phase, evidenceCondition, adversary, contact,
          authenticated, complete, fresh, epochValid, sequenceValid,
          contradiction, evidenceQualified,
          oracleVisibleToPolicy, groundTruthToken, seedToken, treatmentToken,
          verifierCompromised, independentTrustAnchor, hiddenTruthfulEvidence,
          trustedRecovery>>

Init ==
  /\ phase = "READY"
  /\ evidenceCondition \in EvidenceConditions
  /\ adversary \in Adversaries
  /\ contact \in Contacts
  /\ authenticated = FALSE
  /\ complete = FALSE
  /\ fresh = FALSE
  /\ epochValid = FALSE
  /\ sequenceValid = FALSE
  /\ contradiction = FALSE
  /\ evidenceQualified = FALSE
  /\ oracleVisibleToPolicy = FALSE
  /\ groundTruthToken = "GT"
  /\ seedToken = "SEED"
  /\ treatmentToken = evidenceCondition
  /\ verifierCompromised = FALSE
  /\ independentTrustAnchor = TRUE
  /\ hiddenTruthfulEvidence = (evidenceCondition # "V5")
  /\ trustedRecovery = FALSE

ApplyEvidence ==
  /\ phase = "READY"
  /\ phase' = "OBSERVED"
  /\ CASE evidenceCondition = "V0" ->
            /\ authenticated' = TRUE /\ complete' = TRUE /\ fresh' = TRUE
            /\ epochValid' = TRUE /\ sequenceValid' = TRUE /\ contradiction' = FALSE
          [] evidenceCondition = "V1" ->
            /\ authenticated' = TRUE /\ complete' = FALSE /\ fresh' = TRUE
            /\ epochValid' = TRUE /\ sequenceValid' = TRUE /\ contradiction' = FALSE
          [] evidenceCondition = "V2" ->
            /\ authenticated' = TRUE /\ complete' = TRUE /\ fresh' = FALSE
            /\ epochValid' = TRUE /\ sequenceValid' = FALSE /\ contradiction' = FALSE
          [] evidenceCondition = "V3" ->
            /\ authenticated' = TRUE /\ complete' = TRUE /\ fresh' = TRUE
            /\ epochValid' = TRUE /\ sequenceValid' = TRUE /\ contradiction' = TRUE
          [] evidenceCondition = "V4" ->
            /\ authenticated' = FALSE /\ complete' = TRUE /\ fresh' = TRUE
            /\ epochValid' = TRUE /\ sequenceValid' = TRUE /\ contradiction' = FALSE
          [] evidenceCondition = "V5" ->
            /\ authenticated' = TRUE /\ complete' = TRUE /\ fresh' = TRUE
            /\ epochValid' = TRUE /\ sequenceValid' = TRUE /\ contradiction' \in BOOLEAN
  /\ evidenceQualified' = authenticated' /\ complete' /\ fresh' /\ epochValid' /\ sequenceValid' /\ ~contradiction'
  /\ UNCHANGED <<evidenceCondition, adversary, contact, oracleVisibleToPolicy,
                  groundTruthToken, seedToken, treatmentToken, verifierCompromised,
                  independentTrustAnchor, hiddenTruthfulEvidence, trustedRecovery>>

Decide ==
  /\ phase = "OBSERVED"
  /\ phase' = "DECIDED"
  /\ trustedRecovery' = evidenceQualified
  /\ UNCHANGED <<evidenceCondition, adversary, contact, authenticated, complete,
                  fresh, epochValid, sequenceValid, contradiction, evidenceQualified,
                  oracleVisibleToPolicy, groundTruthToken, seedToken, treatmentToken,
                  verifierCompromised, independentTrustAnchor, hiddenTruthfulEvidence>>

Terminal == /\ phase = "DECIDED" /\ UNCHANGED vars
Next == ApplyEvidence \/ Decide \/ Terminal
Spec == Init /\ [][Next]_vars

TypeOK ==
  /\ phase \in {"READY", "OBSERVED", "DECIDED"}
  /\ evidenceCondition \in EvidenceConditions
  /\ adversary \in Adversaries
  /\ contact \in Contacts
  /\ authenticated \in BOOLEAN /\ complete \in BOOLEAN /\ fresh \in BOOLEAN
  /\ epochValid \in BOOLEAN /\ sequenceValid \in BOOLEAN /\ contradiction \in BOOLEAN
  /\ evidenceQualified \in BOOLEAN /\ oracleVisibleToPolicy \in BOOLEAN
  /\ verifierCompromised \in BOOLEAN /\ independentTrustAnchor \in BOOLEAN
  /\ hiddenTruthfulEvidence \in BOOLEAN /\ trustedRecovery \in BOOLEAN

OracleIsolation == oracleVisibleToPolicy = FALSE
TreatmentImmutability == /\ groundTruthToken = "GT" /\ seedToken = "SEED" /\ treatmentToken = evidenceCondition
VerifierBoundary == verifierCompromised = FALSE
A3TrustAnchor == adversary = "A3" => independentTrustAnchor
QualificationSoundness == evidenceQualified => authenticated /\ complete /\ fresh /\ epochValid /\ sequenceValid /\ ~contradiction
KnownInvalidConditionsDoNotQualify == evidenceCondition \in {"V1", "V2", "V3", "V4"} => ~evidenceQualified
DetectedContradictionBlocksRecovery == contradiction => ~trustedRecovery
TrustedRecoverySoundness == trustedRecovery => evidenceQualified
====
