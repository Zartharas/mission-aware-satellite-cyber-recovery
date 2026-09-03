from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    binding = json.loads(
        (ROOT / "study8/PRE_RUNTIME_HASH_BINDING.json").read_text(encoding="utf-8")
    )
    assert binding["binding_id"] == "S8-HASH-BIND-001"
    assert binding["experiment_id"] == "S8-PQC-ICR-001"
    assert binding["algorithm"] == "SHA-256"
    assert binding["source_ci_run_id"] == 33710856522
    assert binding["source_ci_conclusion"] == "success"
    assert binding["canonical_execution_authorized"] is False
    assert binding["campaign_authorization_present"] is False
    assert binding["results_generation_authorized"] is False

    mismatches: list[str] = []
    for relative, expected in binding["bound_files"].items():
        path = ROOT / relative
        if not path.is_file():
            mismatches.append(f"missing:{relative}")
            continue
        actual = sha256(path)
        if actual != expected:
            mismatches.append(f"sha256:{relative}:{actual}:{expected}")

    assert not mismatches, "\n".join(mismatches)
    print(f"phase8_hash_binding_files={len(binding['bound_files'])}")
    print("phase8_hash_binding=PASS")
    print("canonical_execution=PROHIBITED")


if __name__ == "__main__":
    main()
