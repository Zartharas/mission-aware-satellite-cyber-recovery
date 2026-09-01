#!/usr/bin/env bash
set -euo pipefail

echo "study2_validation_scope=ASSURANCE_ONLY_NO_CAMPAIGN_RUNTIME"
python --version
java -version

echo "study2_compile=START"
python -m compileall -q study2/src study2/scripts study2/tests
echo "study2_compile=PASS"

echo "study1_policy_conformance=START"
python study2/scripts/check_study1_policy_conformance.py

echo "study2_security_tests=START"
python -m unittest discover -s study2/tests -p 'test_*.py' -v
echo "study2_security_tests=PASS"

echo "study2_tla_model_check=START"
(
  cd study2/formal
  java -cp /opt/tla2tools.jar tla2sany.SANY Study1P7.tla
  java -XX:+UseParallelGC -Xmx512m -jar /opt/tla2tools.jar \
    -workers 1 -config Study1P7.cfg Study1P7.tla
  java -cp /opt/tla2tools.jar tla2sany.SANY TrustedRecovery.tla
  java -XX:+UseParallelGC -Xmx512m -jar /opt/tla2tools.jar \
    -workers 1 -config TrustedRecovery.cfg TrustedRecovery.tla
)
echo "study2_tla_model_check=PASS"

echo "study2_assurance_validation=PASS"
