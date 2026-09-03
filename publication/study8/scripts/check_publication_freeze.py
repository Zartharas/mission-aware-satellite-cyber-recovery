#!/usr/bin/env python3
"""Validate the Study-8 publication-package freeze without scientific execution."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUTH = ROOT / "study8" / "PHASE8_9_PUBLICATION_PACKAGE_FREEZE_AUTHORIZATION.json"
PUB = ROOT / "publication" / "study8"
MANIFEST = PUB / "PUBLICATION_PACKAGE_FREEZE_MANIFEST.json"
STATUS = PUB / "PUBLICATION_DEVELOPMENT_STATUS.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def die(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    if not AUTH.exists():
        print("study8_publication_freeze=NOT_AUTHORIZED_YET")
        return 0

    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    if auth.get("authorization_id") != "S8-PUBFREEZE-001":
        die("unexpected Study-8 publication-freeze authorization id")
    if auth.get("publication_package_freeze_authorized") is not True:
        die("publication-package freeze is not authorized")
    for key in (
        "scientific_reexecution_authorized",
        "statistical_reanalysis_authorized",
        "frozen_science_modification_authorized",
        "pull_request_merge_authorized",
        "publication_submission_authorized",
        "publisher_portal_action_authorized",
    ):
        if auth.get(key) is not False:
            die(f"prohibited gate unexpectedly open: {key}")

    if auth.get("consumed") is not True:
        if MANIFEST.exists():
            die("freeze manifest exists while authorization remains unconsumed")
        print("study8_publication_freeze=AUTHORIZED_PENDING_SINGLE_USE_EXECUTION")
        return 0

    if not MANIFEST.exists():
        die("consumed publication-freeze authorization has no manifest")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("freeze_id") != "S8-PUBFREEZE-001":
        die("unexpected publication freeze id")
    if manifest.get("status") != "PUBLICATION_PACKAGE_HASH_FROZEN_ADVERSARIAL_REVIEW_PASS":
        die("publication freeze status is not PASS")

    frozen_files = manifest.get("frozen_files", {})
    if not frozen_files:
        die("publication freeze manifest has no frozen files")
    for rel, expected in sorted(frozen_files.items()):
        path = ROOT / rel
        if not path.is_file():
            die(f"missing frozen publication artifact: {rel}")
        actual = sha256(path)
        if actual != expected:
            die(f"publication freeze hash mismatch: {rel}: {actual} != {expected}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    gates = status.get("gate_state", {})
    if gates.get("manuscript_freeze_authorized") is not True:
        die("status does not record manuscript freeze authorization")
    if status.get("publication_package_frozen") is not True:
        die("status does not record frozen publication package")
    for key in (
        "scientific_reexecution_authorized",
        "statistical_reanalysis_authorized",
        "frozen_science_modification_authorized",
        "publication_submission_authorized",
        "publisher_portal_action_authorized",
    ):
        if gates.get(key) is not False:
            die(f"status unexpectedly opens prohibited gate: {key}")

    bindings = status.get("scientific_source_bindings", {})
    if bindings != manifest.get("scientific_source_bindings", {}):
        die("scientific source bindings drift between status and freeze manifest")

    print(f"publication_frozen_files={len(frozen_files)}")
    print("scientific_reexecution=PROHIBITED")
    print("publication_submission=PROHIBITED")
    print("pull_request_merge=NOT_AUTHORIZED")
    print("study8_publication_freeze=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
