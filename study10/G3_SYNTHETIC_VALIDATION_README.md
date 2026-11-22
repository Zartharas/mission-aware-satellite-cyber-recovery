# Study 10 G3 synthetic-only validation

This phase checks the 18 G1 prospective controls and four Study 2 primary policies in a **synthetic-only** harness. It is not a real satellite dataset study.

The script study10/g3_synthetic_validator.py reads the exact G1 v3 test fixture, Study 2 selector and G2 freeze receipt from the repository. Git blob SHA-1 identities are checked against frozen version pins. A **separately implemented action oracle** is compared against the frozen selector over 256 complete Boolean observations times four primary policies (1,024 comparisons). Six hand-specified selector scenarios are also checked.

The 18 cases include the positive baseline, synthetic time-boundary checks, epoch mismatch/unknown, missing and incorrect recovery-criteria values, incomplete claim ledger, accepted-claim contradiction, CRC/APID/timestamp/label/command non-equivalences, all-unknown inputs, and an invalid cohort-pooling declaration.

Run from the repository root:

    python study10/g3_synthetic_validator.py

Only a successful run emits a JSON report with status PASS. The GitHub workflow preserves the report as a run artifact. The G1 fixture's assumed verification states are **not Ed25519 cryptographic verification**, and they do not establish operational recovery safety.

G4 real telemetry processing, source rights, PR merges and publication remain separately blocked. Do not modify the G2 frozen payload, source data or Study 2/9 contracts to make a test pass. The independently coded oracle is technical implementation separation, **not a second human reviewer**.