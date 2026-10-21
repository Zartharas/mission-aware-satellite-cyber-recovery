# Paper 2 External Validation Options R1

**Status:** `DESIGN_OPTIONS_ONLY__NO_EXECUTION_AUTHORIZED`

## Priority A — S3X empirical telemetry-availability replay

Candidate source: ESA Anomaly Dataset, DOI `10.5281/zenodo.12528696`.

Repository-approved role: calibration of telemetry missingness, anomaly duration, and operational data characteristics. Use timestamp/availability structure only. Do not relabel anomalies as cyberattacks.

Goal: test whether the Study-3 qualitative temporal finding survives on empirically observed telemetry-availability traces rather than only the hand-designed K4 schedule.

Recommended status: **high priority**.

## Priority B — S6X executable cFS artifact-assurance validation

Candidate substrate: NASA cFS, already registered in `docs/04-data-source-register.md`.

Use a pinned public revision and a researcher-controlled non-operational example/application. No operational spacecraft, production key, exploit, malware, or third-party target.

Goal: adjudicate objective correctness with a prospectively frozen executable functional/invariant test while separately generating real hashes, manifests, provenance, rebuild evidence, review attestation, and approval metadata.

Recommended status: **high priority**.

## Optional — S4X joint compromise/unavailability robustness

Goal: evaluate a prospectively defined producer state space where compromised and unavailable producers can coexist.

Recommended status: **hold pending design review**, because the analytical Study-4 generalization may provide most of the needed strengthening without another experiment.

## Sources deliberately excluded as new Paper-2 evidence

- Study 5 / CuCD-ID results;
- Study 7 / Study 7E;
- Study 8 / Study 8E and SatNOGS/OPS-SAT re-entry trace evidence;
- Study 9 evidence;
- Paper-1 Studies 1 and 2.

A public dataset is useful only if it supplies a construct needed by the prospective validation. Missing trust, authorization, provenance, or correctness variables must never be fabricated from telemetry features.
