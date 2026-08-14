# Mission-Aware Satellite Cyber Response and Trusted Recovery

Controlled software-in-the-loop research comparing cyber-response and trusted-recovery policies under spacecraft mission-state, contact, and evidence constraints.

## Research question

How do alternative cyber-response strategies affect containment, verified trusted recovery, safety, and mission continuity when the same synthetic cyber event occurs under different spacecraft states, telemetry conditions, and ground-contact conditions?

## Contribution

The simulator is infrastructure, not the contribution. The study contributes:

1. a reproducible satellite-specific response/recovery benchmark;
2. an evidence-based trusted-recovery model; and
3. comparative measurements of security-versus-mission trade-offs.

## Current status

- WP1 — literature/novelty: ready for final review
- WP2 — theoretical/conceptual model: ready for final review
- WP3 — threat/mission model: ready for final review
- WP4 — testbed selection and architecture: complete
- WP5 — deterministic event library: in progress
- WP6 — response policies: pending
- WP7 — trusted recovery: pending
- WP8 — pilot: pending
- WP9 — frozen experiment campaign: pending
- WP10 — analysis/manuscript: pending

## Safety and scope

Experiments use researcher-controlled software simulation only. No operational spacecraft, production credentials, live RF transmission, jamming, spoofing, or real satellite access is part of the experiment.

## Reproducibility foundation

- exact NOS3 and recursive-submodule identities;
- exact Fortytwo identity;
- pinned NOS3 container image digest;
- deterministic/network-disabled build controls;
- isolated Docker networking;
- bounded testbed verification and cleanup;
- machine-readable experiment schema;
- immutable-ground-truth / policy-visible-evidence separation.

See `docs/14-testbed-and-reproducibility.md`.
