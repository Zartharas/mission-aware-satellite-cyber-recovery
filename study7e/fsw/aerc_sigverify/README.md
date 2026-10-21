# AERC Ed25519 Verification Boundary

This is an engineering-only pre-canonical cFS verifier for `S7E-AERC-001`.

It uses the selected Monocypher 4.0.3 verification subset at exact commit
`ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`.

The app:

- verifies signatures only;
- contains a fixed RFC 8032 Test 1 public key for this engineering gate;
- contains no signing/secret key;
- enforces exact cFE packet framing, wire version, key ID, message capacity, reserved bytes, and zero padding before calling Monocypher;
- emits verification results only for structurally valid requests.

This gate is intentionally not bound to the Study-7E authorization features. A later gate must define canonical authorization-message serialization and production public-key provenance before any authorization bit can be populated from this verifier.
