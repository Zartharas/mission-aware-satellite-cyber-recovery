# S7E-AERC-001 Author Approval — 2026-09-23

**Approval scope:** AR-1 through AR-5  
**Authorization:** pre-canonical implementation only  
**Protocol freeze:** NO  
**Environment freeze:** NO  
**Canonical scientific execution:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED

The author explicitly approved:

> AR-1 through AR-5 for pre-canonical implementation only, subject to the boundaries in the author-review package.

Approved implementation decisions:

1. **AR-1:** 64-byte signed-evidence v2 layout.
2. **AR-2:** deterministic external/host-side test signing boundary with no private keys in cFS FSW.
3. **AR-3:** T4 authority representation using signed opaque authority ID plus research-only provenance, without a second authority-signature hierarchy.
4. **AR-4:** qualifier semantics covering structural completeness, independent authorization extraction, controlled logical time, duplicate handling, rollback/replay, and path-local equivocation.
5. **AR-5:** current F0-F12 transformation semantics.

This approval is intentionally narrower than a protocol freeze.

The following remain unresolved/unfrozen:

- final numeric freshness threshold;
- final epoch mapping;
- final scenario/source/key/authority registry values;
- final experiment key material and hashes;
- final byte-transform freeze;
- production L0/L1 training/freeze;
- canonical execution authorization;
- PR merge.

The approved next activity is continued pre-canonical producer/qualifier implementation and engineering qualification.
