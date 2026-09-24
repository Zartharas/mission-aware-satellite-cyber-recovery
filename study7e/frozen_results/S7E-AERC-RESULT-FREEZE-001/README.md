# S7E-AERC-RESULT-FREEZE-001 durable raw artifact

This directory durably preserves the byte-exact GitHub Actions artifact for the sole scientific held-out execution of record, `S7E-AERC-HELDOUT-EXEC-001`.

The original Actions artifact ID is `10787499194`. Its ZIP SHA-256 is:

`cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`

The ZIP is stored as five ordered base64 text chunks so repository ignore rules for generated `*.zip` archives do not weaken the existing archive boundary. This is an encoding-only preservation transform; it does not alter the archive bytes.

Reconstruct and verify with Python:

```python
from pathlib import Path
import base64
import hashlib

root = Path("study7e/frozen_results/S7E-AERC-RESULT-FREEZE-001")
parts = sorted(root.glob("S7E-AERC-HELDOUT-EXEC-001.actions-artifact.zip.b64.part-*"))
encoded = b"".join(p.read_bytes() for p in parts)
archive = base64.b64decode(encoded)

assert len(archive) == 29892
assert hashlib.sha256(archive).hexdigest() == "cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35"

Path("/tmp/S7E-AERC-HELDOUT-EXEC-001.zip").write_bytes(archive)
print("S7E_AERC_DURABLE_ARTIFACT_RECONSTRUCTION=PASS")
```

`study7e/RESULT_FREEZE_MANIFEST_001.json` additionally binds every member of the reconstructed ZIP by SHA-256.

This preservation is provenance only. It does not authorize a scientific rerun, PR #167 merge, or manuscript/publication result claims.
