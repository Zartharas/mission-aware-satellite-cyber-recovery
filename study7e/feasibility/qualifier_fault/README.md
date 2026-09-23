# Study 7E Qualifier/Fault Engineering Harness

This host-only harness exercises the draft qualifier time/replay semantics and F0-F12 transformation contracts.

It reuses `study7e.src.aerc_design.domain_map()` and `affected_paths()` for topology propagation.

It does not:

- execute D0/D1/L0/L1;
- train a model;
- create canonical Study-7E observations;
- compute scientific endpoints;
- freeze timing, epoch, keys, registries, or fault transforms.

The harness is a contract test only.
