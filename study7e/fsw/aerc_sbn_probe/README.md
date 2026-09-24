# AERC cFS Cross-Instance SBN Probe

This is a non-canonical engineering feasibility component for `S7E-AERC-001`.

It is intentionally narrower than the Study-7E architecture. The same app is loaded on cFS CPU1 and CPU2:

1. CPU2 subscribes to a fixed experimental telemetry-form MID.
2. CPU1 sends a fixed scenario ID and marker.
3. SBN transports the message to CPU2.
4. CPU2 validates the fixed payload and emits a fixed sink receipt on a second MID.
5. SBN transports the receipt back to CPU1.
6. CPU1 validates the same scenario ID/marker and the CPU2 sink receipt.

This probe demonstrates only:

- two-instance cFE/SBN transport feasibility;
- deterministic scenario-ID/marker survival across the cross-instance path;
- a deterministic sink-receipt capture path.

It does **not** implement recovery policies, research truth, topology labels, fault injection, model training, canonical Study-7E execution, or spacecraft actuation.
