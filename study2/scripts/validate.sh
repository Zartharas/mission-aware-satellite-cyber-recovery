#!/usr/bin/env bash
set -euo pipefail

echo "study2_validation_scope=ASSURANCE_PROTOCOL_AND_PHASE5_RUNTIME_FREEZE_NO_CAMPAIGN_RUNTIME"
python --version
java -version

echo "study2_compile=START"
python -m compileall -q study2/src study2/scripts study2/tests
echo "study2_compile=PASS"

echo "study1_policy_conformance=START"
python study2/scripts/check_study1_policy_conformance.py

echo "study2_protocol_freeze=START"
python study2/scripts/check_protocol_freeze.py
echo "study2_protocol_freeze=PASS"

echo "study2_phase5_runtime_freeze=START"
python study2/scripts/check_phase5_runtime_freeze.py
echo "study2_phase5_runtime_freeze=PASS"

echo "study2_deterministic_security_tests=START"
python -m unittest discover -s study2/tests -p 'test_evidence.py' -v
python -m unittest discover -s study2/tests -p 'test_recovery_gate.py' -v
python -m unittest discover -s study2/tests -p 'test_protocol.py' -v
python -m unittest discover -s study2/tests -p 'test_treatments.py' -v
python -m unittest discover -s study2/tests -p 'test_ambiguity.py' -v
python -m unittest discover -s study2/tests -p 'test_selectors.py' -v
python -m unittest discover -s study2/tests -p 'test_adjudication.py' -v
python -m unittest discover -s study2/tests -p 'test_cell_matrix.py' -v
python -m unittest discover -s study2/tests -p 'test_mutation_assay.py' -v
python -m unittest discover -s study2/tests -p 'test_trial_manifest.py' -v
python -m unittest discover -s study2/tests -p 'test_runtime_freeze.py' -v
python -m unittest discover -s study2/tests -p 'test_attempt_ledger.py' -v
python -m unittest discover -s study2/tests -p 'test_context_ablations.py' -v
python -m unittest discover -s study2/tests -p 'test_runtime_engine.py' -v
echo "study2_deterministic_security_tests=PASS"

echo "study2_property_tests=START"
python -m unittest discover -s study2/tests -p 'test_properties.py' -v
python -m unittest discover -s study2/tests -p 'test_protocol_properties.py' -v
echo "study2_property_tests=PASS"

echo "study2_tla_model_check=START"
(
  cd study2/formal
  java -cp /opt/tla2tools.jar tla2sany.SANY Study1P7.tla
  java -XX:+UseParallelGC -Xmx512m -jar /opt/tla2tools.jar -workers 1 -config Study1P7.cfg Study1P7.tla
  java -cp /opt/tla2tools.jar tla2sany.SANY TrustedRecovery.tla
  java -XX:+UseParallelGC -Xmx512m -jar /opt/tla2tools.jar -workers 1 -config TrustedRecovery.cfg TrustedRecovery.tla
  java -cp /opt/tla2tools.jar tla2sany.SANY AdversarialEvidence.tla
  java -XX:+UseParallelGC -Xmx512m -jar /opt/tla2tools.jar -workers 1 -config AdversarialEvidence.cfg AdversarialEvidence.tla
)
echo "study2_tla_model_check=PASS"

echo "study2_assurance_validation=PASS"
