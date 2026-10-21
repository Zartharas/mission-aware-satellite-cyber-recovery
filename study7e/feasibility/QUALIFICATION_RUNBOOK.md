# Study 7E External-Stack Feasibility Qualification Runbook

**Experiment:** `S7E-AERC-001`  
**Phase:** implementation/feasibility only  
**Canonical scientific execution:** PROHIBITED

This runbook qualifies candidate upstream environments. It does not run the Study-7E scientific campaign and must not create canonical result files.

## 1. Candidate identities

### cFS

- tag: `v7.0.1`
- tag commit: `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`
- documented build:
  - `make native_std.prep`
  - `make native_std.install`
  - `make native_std.runtest`

### NOS3

- tag: `v1_07_05`
- version: 1.7.5
- tag commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- documented setup/build:
  - `make prep`
  - `make`

`make launch` is intentionally outside the first qualification script. Simulation launch is deferred until the implementation topology exists and a separate non-canonical integration-test plan has been reviewed.

## 2. macOS note

The cFS `native_std` quick start is documented for pc-linux. On macOS, use a Linux VM/container for the build qualification rather than treating a native macOS failure as evidence that the release is unusable.

NOS3 documents two paths:

- Vagrant + VirtualBox; or
- an existing Linux environment with Docker and Docker Compose.

The author workstation is macOS, so the expected NOS3 feasibility route is Vagrant/VirtualBox or another controlled Linux VM unless an existing Linux/Docker environment is already available.

## 3. Qualification order

1. Run repository pre-canonical tests:
   `python -m unittest study7e.tests.test_design_contracts -v`
2. Run governance validator:
   `python study7e/validation/validate_precanonical.py`
3. Run `resolve_external_candidates.sh` to clone exact tags and capture recursive submodule SHAs.
4. Run cFS build qualification in Linux.
5. Run NOS3 prerequisite and build qualification in its supported Linux/VM environment.
6. Save the generated feasibility reports outside `study7e/results/`.
7. Review reports before adding any cFS custom applications.
8. Do not run any canonical Study-7E workflow.

## 4. Success criteria

### cFS

PASS requires:

- exact top-level commit;
- clean recursive submodule checkout;
- `native_std.prep` success;
- `native_std.install` success;
- `native_std.runtest` success.

### NOS3

Initial build feasibility PASS requires:

- exact top-level commit;
- recursive submodule checkout captured;
- supported Linux/VM prerequisites;
- `make prep` success;
- `make` success.

Launching NOS3 is not required for the initial build-feasibility gate.

## 5. Evidence boundary

Feasibility logs are engineering qualification evidence. They are not scientific observations and must never be counted in the 188-scenario Study-7E evaluation population.
