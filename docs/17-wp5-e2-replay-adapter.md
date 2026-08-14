# WP5 E2 — Command Replay Adapter

## Evidence basis

SPARTA `EX-0001.01` defines command-packet replay as resending authentic-looking telecommands that were previously accepted. E2 models that behavior without operational captures or real spacecraft traffic.

## Controlled implementation

E2 reuses the same harmless pinned `SAMPLE_NOOP_CC` and the same accepted nominal NOS3 runtime used by E1.

The sequence is:

1. establish a quiet NOOP-marker baseline;
2. send one valid NOOP as a setup/control command;
3. persist the setup-send evidence and prove exactly one Sample acceptance increment;
4. establish a second quiet baseline;
5. resend the exact same eight packet bytes once as E2;
6. persist replay-send evidence;
7. require setup and replay packet SHA-256 values to be identical;
8. prove exactly one additional Sample acceptance increment;
9. require the nominal runtime to finish PASS.

The setup command is not E2. The second byte-identical datagram is the replay event.

## Invalid development run

The development run preceding the corrected adapter was classified `INVALID_HARNESS_SETUP_SEND_UNPROVEN`: the setup container used `python3 -` with a heredoc while `docker run` omitted `-i`. No setup evidence file was produced, so its setup marker change could not be causally attributed to the harness. That run is not scientific evidence and is not included in analysis.

## Claim boundary

WP5 establishes that a deterministic, byte-identical replay can be generated and observed in the controlled simulator. It does not evaluate operational anti-replay protections or response-policy effectiveness; those comparisons belong to WP6-WP9.
