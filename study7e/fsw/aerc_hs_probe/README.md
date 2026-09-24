# AERC cFS HS Observation Probe

This is a non-canonical engineering feasibility component for `S7E-AERC-001`.

It verifies one narrow implementation seam required by the Study-7E implementation plan:

1. subscribe to the pinned cFS Health & Safety (HS) housekeeping telemetry topic;
2. send the pinned HS housekeeping-request command;
3. receive an actual HS housekeeping packet;
4. expose the observed HS application-monitor, event-monitor, aliveness, CPU-hog, and status-flag fields in an engineering PASS marker.

The probe does not compute the Study-7E research truth variable `true_health_ready`, does not define the eventual evidence-qualifier readiness rule, and does not run any Study-7E scientific scenario.
