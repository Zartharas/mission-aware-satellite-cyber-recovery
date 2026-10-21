# Study 7E Signed-Evidence v2 Engineering Feasibility

This directory validates the **draft**, non-frozen 64-byte signed-evidence candidate outside cFS flight software.

The gate uses:

- explicit fixed-width big-endian serialization;
- Monocypher 4.0.3 at the selected pinned commit;
- RFC 8032 Section 7.1 Test 1 seed/public key as public engineering test-vector material;
- no final experiment key registry;
- no policy-feature binding;
- no Study-7E scientific scenario execution.

The private seed appears only in this host-side engineering test because RFC 8032 publishes it as a standard test vector. It is not experiment production key material and is not compiled into cFS flight software.
