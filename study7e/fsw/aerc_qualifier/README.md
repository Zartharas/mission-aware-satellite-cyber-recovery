# AERC Pre-Canonical Evidence Qualifier

This cFS application implements the author-approved pre-canonical qualifier semantics against the 64-byte signed-evidence v2 candidate.

Current engineering registry entries are deliberately non-final:

- primary source/key IDs: 0x1001 / 0x2001;
- corroborator source/key IDs: 0x1002 / 0x2002;
- public keys: RFC 8032 Section 7.1 Ed25519 public test keys 1 and 2.

No private keys are present. Timing threshold, epoch mapping, and registry values remain configurable engineering values and are not frozen protocol values.

The qualifier emits the already-established 9-feature base and 16-feature corroborated snapshot messages. This is a pre-canonical implementation binding only; it is not a canonical protocol freeze.
