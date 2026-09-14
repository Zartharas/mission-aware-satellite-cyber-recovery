from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


class DeterministicOutputError(RuntimeError):
    """Raised when canonical output constraints are violated."""


def integer_fraction(numerator: int, denominator: int) -> dict[str, int]:
    if type(numerator) is not int or type(denominator) is not int:
        raise DeterministicOutputError("fraction numerator and denominator must be integers")
    if denominator <= 0:
        raise DeterministicOutputError("fraction denominator must be positive")
    if numerator < 0 or numerator > denominator:
        raise DeterministicOutputError("fraction numerator must be within [0, denominator]")
    return {"numerator": numerator, "denominator": denominator}


def canonical_json_bytes(value: object) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise DeterministicOutputError(f"value is not canonical-JSON serializable: {exc}") from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha256(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def build_output_sha256_manifest(artifacts: Mapping[str, bytes]) -> dict[str, object]:
    names = tuple(artifacts)
    if len(names) != len(set(names)):
        raise DeterministicOutputError("output artifact names must be unique")
    if any(not name or Path(name).is_absolute() or ".." in Path(name).parts for name in names):
        raise DeterministicOutputError("output artifact names must be safe relative paths")
    return {
        "schema": 1,
        "algorithm": "sha256",
        "artifacts": [
            {
                "path": name,
                "size_bytes": len(artifacts[name]),
                "sha256": sha256_bytes(artifacts[name]),
            }
            for name in sorted(names)
        ],
    }


def write_canonical_json(path: Path, value: object) -> str:
    data = canonical_json_bytes(value)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    except OSError as exc:
        raise DeterministicOutputError(f"cannot write canonical output {path}: {exc}") from exc
    return sha256_bytes(data)
