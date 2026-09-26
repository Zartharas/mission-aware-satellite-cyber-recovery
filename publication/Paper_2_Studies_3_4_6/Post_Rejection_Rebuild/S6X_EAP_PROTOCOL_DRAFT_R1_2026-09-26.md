# S6X-EAP-001 Protocol Draft R1

**Working title:** Executable Aerospace Artifact-Assurance Validation  
**Status:** `PROTOCOL_DRAFT__NO_IMPLEMENTATION__NO_EXECUTION_AUTHORIZED`

## Research purpose

Test the Study-6 observability finding using a real, researcher-controlled open-source aerospace software build pipeline rather than only Boolean artifact states.

## Candidate substrate

NASA cFS, using a pinned public revision and a non-operational example/application.

No operational spacecraft, production credentials, real signing infrastructure, exploit, malware, or third-party target is permitted.

## Prospective evidence pipeline

Candidate evidence components:

1. source revision identity;
2. source archive/file hashes;
3. reproducible build command and environment identity;
4. artifact SHA-256;
5. signed research manifest using research-only keys;
6. build provenance record;
7. independent rebuild result;
8. source-review attestation;
9. release-approval attestation;
10. executable functional/invariant test used only as research adjudication.

## Candidate controlled artifact states

- clean approved source;
- post-build mutation;
- re-signed altered artifact;
- build-stage source/artifact variation;
- review-bypass state;
- fully approved but functionally incorrect source variant.

All variants must be benign researcher-controlled test fixtures. The final state tests observational equivalence: can all assurance signals remain satisfied while the independent functional/invariant test fails?

## Candidate endpoints

- qualification under each prospectively defined assurance gate;
- objective functional/invariant correctness;
- unsafe qualification;
- benign rejection under intentionally unavailable assurance evidence;
- evidence-vector equivalence classes.

## Independence controls

The correctness test must not be an input to the qualification gate being evaluated. Otherwise the extension would collapse the observability question by supplying hidden adjudication directly to the policy.

## Go/no-go gate

Before execution, freeze the exact cFS revision, application/test fixture, build environment, research signing method, evidence schema, functional/invariant tests, artifact-state construction procedures, and independent audit plan.

Implementation and execution require separate author authorization.
