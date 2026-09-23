# AERC Ed25519 cFS Engineering Probe

This engineering-only app exercises the selected Monocypher verification boundary through cFE Software Bus.

It verifies:

- RFC 8032 Test 1 empty-message signature succeeds;
- a mutated signature is rejected;
- an all-zero signature is rejected;
- the same signature against a changed message is rejected;
- malformed cFE framing, wrong wire version, wrong key ID, oversized message length, and nonzero inactive message bytes produce no verification result;
- malformed requests do not advance the verification-result sequence.

It uses no signing/secret key and does not populate Study-7E policy authorization fields.
