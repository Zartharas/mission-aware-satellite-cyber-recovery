# AERC Pre-Canonical Evidence Producer Bridge

This cFS application is a private-key-free producer bridge.

It accepts already-signed 64-byte evidence envelopes on the engineering ingress MID and forwards them to the qualifier MID after exact cFE packet-length validation.

The signing boundary is external to cFS. This application contains no private key, signing seed, signing API, topology label, fault label, or research-truth field.
