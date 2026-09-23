# Study 7E Ed25519 dependency feasibility

This directory contains engineering-only proof-before-selection tests for the Study-7E signature-verification dependency.

The gate is **verification only**. No signing key is introduced into Study-7E flight software.

Both finalist tests use RFC 8032 Section 7.1 Test 1 and require:

1. the valid empty-message signature to verify;
2. a one-bit signature mutation to be rejected;
3. an all-zero signature to be rejected;
4. the same signature against a changed message to be rejected.

Candidate selection is intentionally separate from this feasibility gate. These tests produce no Study-7E scientific results.
