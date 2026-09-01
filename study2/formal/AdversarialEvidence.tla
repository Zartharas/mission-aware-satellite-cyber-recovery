---- MODULE AdversarialEvidence ----
EXTENDS Naturals, TLC

EvidenceConditions == {"V0", "V1", "V2", "V3", "V4", "V5"}
Adversaries == {"A0", "A1", "A2", "A3"}
Contacts == {"K0", "K1", "K2", "K3", "K4"}

VARIABLES phase, evidenceCondition, adversary, contact,
          oracleVisibleToPolicy, groundTruthToken, seedToken,
          treatmentToken, verifierCompromised, independentTrustAnchor,
          evidenceQualified, trustedRecovery

vars == <<phase, evidenceCondition, adversary, contact,
          oracleVisibleToPolicy, groundTruthToken, seedToken,
          treatmentToken, verifierCompromised, independentTrustAnchor,
          evidenceQualified, trustedRecovery>>

Init ==
  /\ phase = "READY"
  /\ evidenceCondition \in EvidenceConditions
  /\ adversary \in Adversaries
  /\ contact \in Contacts
  /\ oracleVisibleToPolicy = FALSE
  /\ groundTruthToken = "GT"
  /\ seedToken = "SEED"
  /\ treatmentToken = evidenceCondition
  /\ verifierCompromised = FALSE
  /\ independentTrustAnchor = TRUE
  /\ evidenceQualified = FALSE
  /\ trustedRecovery = FALSE

ApplyEvidence ==
  /\ phase = "READY"
  /\ phase' = "OBSERVED"
  /\ evidenceQualified' = (evidenceCondition = "V0")
  /\ UNCHANGED <<evidenceCondition, adversary, contact,
                  oracleVisibleToPolicy, groundTruthToken, seedToken,
                  treatmentToken, verifierCompromised,
                  independentTrustAnchor, trustedRecovery>>

Decide ==
  /\ phase = "OBSERVED"
  /\ phase' = "DECIDED"
  /\ trustedRecovery' = evidenceQualified
  /\ UNCHANGED <<evidenceCondition, adversary, contact,
                  oracleVisibleToPolicy, groundTruthToken, seedToken,
                  treatmentToken, verifierCompromised,
                  independentTrustAnchor, evidenceQualified>>

Terminal ==
  /\ phase = "DECIDED"
  /\ UNCHANGED vars

Next == ApplyEvidence \/ Decide \/ Terminal
Spec == Init /\ [][Next]_vars

TypeOK ==
  /\ phase \in {"READY", "OBSERVED", "DECIDED"}
  /\ evidenceCondition \in EvidenceConditions
  /\ adversary \in Adversaries
  /\ contact \in Contacts
  /\ oracleVisibleToPolicy \in BOOLEAN
  /\ verifierCompromised \in BOOLEAN
  /\ independentTrustAnchor \in BOOLEAN
  /\ evidenceQualified \in BOOLEAN
  /\ trustedRecovery \in BOOLEAN

OracleIsolation == oracleVisibleToPolicy = FALSE
TreatmentImmutability == /\ groundTruthToken = "GT" /\ seedToken = "SEED" /\ treatmentToken = evidenceCondition
VerifierBoundary == verifierCompromised = FALSE
A3TrustAnchor == adversary = "A3" => independentTrustAnchor
AdversarialEvidenceNotImplicitlyQualified == evidenceCondition \in {"V1", "V2", "V3", "V4", "V5"} => ~evidenceQualified
TrustedRecoverySoundness == trustedRecovery => evidenceQualified
====
