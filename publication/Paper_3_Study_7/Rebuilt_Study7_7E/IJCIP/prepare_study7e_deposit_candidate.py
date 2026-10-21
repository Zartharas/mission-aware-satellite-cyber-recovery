#!/usr/bin/env python3
"""Prepare a non-published Study 7E dataset-deposit candidate from frozen bytes.

Reconstructs the original held-out GitHub Actions ZIP byte-for-byte.
Only reads source; does not run a model, alter results, or publish a dataset.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile

AREA = Path(__file__).resolve().parent
ROOT = AREA.parents[3]
STUDY = ROOT / "study7e"
TARGET = ROOT / "artifacts/paper3_ijcip_review_only"
OUTPUT = TARGET / "STUDY7E_ZENODO_DEPOSIT_CANDIDATE_NOT_PUBLISHED.zip"


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def member(name, data):
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o644 << 16
    return entry, data


def main():
    manifest_file = STUDY / "RESULT_FREEZE_MANIFEST_001.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    freeze = manifest["durable_raw_artifact"]
    parts = []
    for item in freeze["chunks"]:
        source = ROOT / item["path"]
        raw = source.read_bytes()
        assert len(raw) == item["chars"], "frozen base64 chunk length changed"
        parts.append(raw)
    encoded = b"".join(parts)
    assert len(encoded) == freeze["encoded_chars_including_terminal_newline"], "encoded size drift"
    original = base64.b64decode(encoded.strip(), validate=True)
    assert len(original) == freeze["decoded_bytes"], "original ZIP size drift"
    assert digest(original) == freeze["decoded_sha256"], "original ZIP SHA256 drift"
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        assert z.testzip() is None, "invalid original actions ZIP"
        assert set(z.namelist()) == set(freeze["archive_member_sha256"]), "raw artifact members changed"
        for name, expected in freeze["archive_member_sha256"].items():
            assert digest(z.read(name)) == expected, "raw member digest mismatch: " + name
    assert manifest["execution_id"] == "S7E-AERC-HELDOUT-EXEC-001"
    assert manifest["freeze_id"] == "S7E-AERC-RESULT-FREEZE-001"
    preface = (
        "# Study 7E immutable held-out evidence — DOI deposit candidate only\n\n"
        "This bundle carries the original GitHub Actions result artifact "
        "reassembled byte-for-byte from the seven preservation chunks in the "
        "separately frozen Study 7E result manifest. It has NOT been deposited "
        "to Zenodo and has NO dataset DOI at this stage.\n\n"
        "Science record: S7E-AERC-RESULT-FREEZE-001; "
        "execution: S7E-AERC-HELDOUT-EXEC-001. "
        "196 finite held-out scenarios, 784 policy decisions, with the exact "
        "original null and adverse results. Study 7 remains a different population.\n\n"
        "Original Actions ZIP SHA256: " + freeze["decoded_sha256"] + "\n"
        "Use the original archive plus manifest for independent verification. "
        "No model inference or experiment is performed during packaging.\n\n"
        "Publication/DOI, license, rights and metadata remain subject to the "
        "sole author's approval. Do not cite this candidate as a published dataset.\n"
    ).encode("utf-8")
    selected = {
        "README_NOT_PUBLISHED.md": preface,
        "ORIGINAL_S7E_HELDOUT_ACTIONS_ARTIFACT.zip": original,
        "study7e/RESULT_FREEZE_MANIFEST_001.json": manifest_file.read_bytes(),
        "study7e/RESULT_FREEZE_STATE.json": (STUDY / "RESULT_FREEZE_STATE.json").read_bytes(),
        "study7e/results/S7E-AERC-HELDOUT-EXEC-001/exact_endpoint_counts.json":
            (STUDY / "results/S7E-AERC-HELDOUT-EXEC-001/exact_endpoint_counts.json").read_bytes(),
        "study7e/results/S7E-AERC-HELDOUT-EXEC-001/result_checkpoint.json":
            (STUDY / "results/S7E-AERC-HELDOUT-EXEC-001/result_checkpoint.json").read_bytes(),
        "study7e/README.md": (STUDY / "README.md").read_bytes(),
    }
    receipt = {
        "status": "AUTHOR_REVIEW__NOT_PUBLISHED__NO_DOI",
        "freeze_id": manifest["freeze_id"],
        "execution_id": manifest["execution_id"],
        "original_actions_zip_sha256": digest(original),
        "members_sha256": {name: digest(data) for name, data in sorted(selected.items())},
        "no_scientific_reexecution": True,
        "author_release_approval": False,
    }
    selected["DEPOSIT_PROVENANCE_AND_SHA256.json"] = (json.dumps(receipt, indent=2) + "\n").encode()
    TARGET.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as z:
        for name, data in sorted(selected.items()):
            info, data = member(name, data)
            z.writestr(info, data)
    with zipfile.ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(selected)
        for name, contents in selected.items():
            assert z.read(name) == contents
    print("S7E_ORIGINAL_HELDOUT_ACTIONS_SHA256=" + digest(original))
    print("S7E_DATASET_DEPOSIT_CANDIDATE=PASS_NOT_PUBLISHED")
    print("S7E_DATASET_DOI=NOT_ASSIGNED")


if __name__ == "__main__":
    main()
