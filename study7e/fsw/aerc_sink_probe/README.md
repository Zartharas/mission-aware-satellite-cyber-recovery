# AERC Recovery Sink Engineering Probe

This app exists only to qualify the pre-canonical recovery-action sink in CI.

It sends two fixed engineering requests, one for each allowed action, and verifies the sink's returned record preserves the fixed scenario ID, policy ID, action, and monotonic receipt sequence.

The probe does not execute a Study-7E scientific scenario and does not claim either requested action is correct.
