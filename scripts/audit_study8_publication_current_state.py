#!/usr/bin/env python3
"""Fail-closed audit for the current Study-8 publication and submitted state.

Historical Study-8 technical-close, source-publication freeze, and Acta package-freeze
artifacts retain their stage-local wording. This checker verifies that those frozen
records remain intact while the repository's live current-state surfaces correctly
record the later Acta Astronautica submission.

The checker never executes scientific analysis and never modifies frozen evidence,
statistics, or publisher-facing files.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_STATUS_PATH = ROOT / "publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json"
SOURCE_FREEZE_CHECKER = ROOT / "publication/study8/scripts/check_publication_freeze.py"
SUBMISSION_STATUS_PATH = ROOT / "publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json"
ACTA_DIR = ROOT / "publication/Paper_4_Study_8/Acta_Astronautica"

SOURCE_STATUS = "PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED"
SOURCE_PR_NUMBER = 92
SOURCE_REVIEWED_HEAD = "75c98356751087dd648684ade7cb973c166cbce0"
SOURCE_FROZEN_PACKAGE_COMMIT = "cbad15227bf99d1b7b19d95b0581196d78208f95"
SOURCE_MERGE_COMMIT = "87bcec000d278aeffef1222ce814098c93ada362"
SOURCE_RESULTS_FREEZE_CI = 33781901833
SOURCE_REPOSITORY_CI = 33781901724
SOURCE_MANUSCRIPT_SHA = "efbe78c43c44cde057637fc1744746d0ab4da8aed71e30d709aedd7dbdef13d6"

ACTA_MANUSCRIPT_ID = "AA-D-26-02872"
ACTA_SUBMISSION_DATE = "2026-09-06"
ACTA_CURRENT_STATUS = "With Editor"
ACTA_PACKAGE_FREEZE_ID = "S8-ACTA-PKGFREEZE-002"
ACTA_SUBMITTED_PACKAGE_COMMIT = "f5e9a1d4553737e534821bf647463abfd44fa0dd"

EXPECTED_SUBMITTED_FILES = {
    "ACTA_ASTRONAUTICA_MANUSCRIPT.docx": "ef551a52c2df65c1db68fa6188b22bf216e10aefdc6b7e8d0de00e3fb95d7411",
    "ACTA_ASTRONAUTICA_COVER_LETTER.docx": "d45ab72b8434efa30da7f2048bb0b09c7b38b7d2ec8085def92b1bb491bae787",
    "ACTA_ASTRONAUTICA_HIGHLIGHTS.docx": "f42762a23a71c37955789d93340033f55326f13ff734327dab68c0dccc6b466d",
    "FIGURE_1_PROFILE_SUCCESS.pdf": "041b67a75daeb3a07336beb7d8f02f3a41455f1489e0d14ece13eb5e97a91a63",
    "FIGURE_2_CONTACT_REGIME_SUCCESS.pdf": "e527830c31fc25f28e3eae8272b4e00e92722ac451ef3d363d475a41e978bcbb",
}

CURRENT_DOCS = {
    "docs/CURRENT_PUBLICATION_STATE.md": {
        "required": (
            ACTA_MANUSCRIPT_ID,
            ACTA_CURRENT_STATUS,
            "Paper 2: Studies 3 + 4 + 6",
            "2026-09-I012066",
        ),
        "forbidden": (
            "publisher submission and portal action remain separately gated",
            "The next gate is venue-specific submission-package preparation",
        ),
    },
    "docs/PUBLICATION_PHASE_MAP.md": {
        "required": (
            ACTA_MANUSCRIPT_ID,
            ACTA_CURRENT_STATUS,
            "NEXT ACTIVE DEVELOPMENT PRIORITY",
            "Studies 3 + 4 + 6",
        ),
        "forbidden": (
            "publisher submission and portal action remain separately gated",
            "Acta-specific package preparation and audit; submission separately gated",
        ),
    },
    "publication/README.md": {
        "required": (
            ACTA_MANUSCRIPT_ID,
            ACTA_CURRENT_STATUS,
            "Next publication-development priority",
            "S8-ACTA-PKGFREEZE-002",
        ),
        "forbidden": (
            "Publisher submission and Editorial Manager actions remain later explicit authorization gates",
            "Scientific reexecution, statistical reanalysis, publisher submission, and publisher-portal action are not authorized",
        ),
    },
    "study8/README.md": {
        "required": (
            SOURCE_STATUS,
            ACTA_MANUSCRIPT_ID,
            "ACTA_SUBMITTED__WITH_EDITOR",
            "Studies 3 + 4 + 6 synthesis",
        ),
        "forbidden": (
            "The next Study-8 work is **venue-specific submission-package preparation**",
        ),
    },
    "publication/study8/README.md": {
        "required": (
            SOURCE_STATUS,
            ACTA_MANUSCRIPT_ID,
            "ACTA_SUBMITTED__WITH_EDITOR",
            "Studies 3 + 4 + 6 synthesis",
        ),
        "forbidden": (
            "The next gate is **venue-specific submission-package preparation**",
        ),
    },
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing current-state file: {rel}")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_source_freeze() -> None:
    if not SOURCE_STATUS_PATH.is_file():
        fail("missing Study-8 source-publication current-state JSON")

    status = json.loads(SOURCE_STATUS_PATH.read_text(encoding="utf-8"))
    if status.get("schema") != 2:
        fail(f"unexpected source current-state schema: {status.get('schema')!r}")
    if status.get("status") != SOURCE_STATUS:
        fail(f"source publication status drift: {status.get('status')!r}")
    if status.get("phase") != "8.10-post-publication-package-merge-repository-closeout":
        fail(f"source publication phase drift: {status.get('phase')!r}")
    if status.get("publication_package_frozen") is not True:
        fail("source publication package is not recorded as frozen")

    merge = status.get("publication_package_merge", {})
    expected_merge = {
        "completed": True,
        "pull_request": SOURCE_PR_NUMBER,
        "reviewed_head": SOURCE_REVIEWED_HEAD,
        "frozen_package_commit": SOURCE_FROZEN_PACKAGE_COMMIT,
        "main_merge_commit": SOURCE_MERGE_COMMIT,
    }
    for key, expected in expected_merge.items():
        if merge.get(key) != expected:
            fail(f"source publication merge {key} drift: {merge.get(key)!r} != {expected!r}")

    for key, run_id in (
        ("post_merge_results_freeze_ci", SOURCE_RESULTS_FREEZE_CI),
        ("post_merge_repository_ci", SOURCE_REPOSITORY_CI),
    ):
        ci = merge.get(key, {})
        if ci.get("run_id") != run_id or ci.get("conclusion") != "success":
            fail(f"source publication merge {key} identity/conclusion drift")

    gates = status.get("gate_state", {})
    for key in (
        "scientific_reexecution_authorized",
        "statistical_reanalysis_authorized",
        "frozen_science_modification_authorized",
        "publication_submission_authorized",
        "publisher_portal_action_authorized",
    ):
        if gates.get(key) is not False:
            fail(f"historical source-package gate unexpectedly changed: {key}")

    manifest = json.loads((ROOT / "publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    frozen_files = manifest.get("frozen_files", {})
    if len(frozen_files) != 11:
        fail(f"expected 11 hash-frozen source publication artifacts, found {len(frozen_files)}")
    if frozen_files.get("publication/study8/manuscript/manuscript.md") != SOURCE_MANUSCRIPT_SHA:
        fail("frozen source manuscript SHA drift")

    freeze = subprocess.run(
        [sys.executable, str(SOURCE_FREEZE_CHECKER)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if freeze.returncode != 0:
        fail("Study-8 source publication-freeze checker failed:\n" + freeze.stdout.rstrip())
    if "study8_publication_freeze=PASS" not in freeze.stdout:
        fail("Study-8 source publication-freeze checker did not emit PASS")


def check_acta_submission() -> None:
    if not SUBMISSION_STATUS_PATH.is_file():
        fail("missing Acta submitted-state JSON")

    status = json.loads(SUBMISSION_STATUS_PATH.read_text(encoding="utf-8"))
    expected = {
        "manuscript_id": ACTA_MANUSCRIPT_ID,
        "submission_date": ACTA_SUBMISSION_DATE,
        "current_publisher_status": ACTA_CURRENT_STATUS,
        "package_freeze_id": ACTA_PACKAGE_FREEZE_ID,
        "submitted_package_source_commit": ACTA_SUBMITTED_PACKAGE_COMMIT,
        "publisher_portal_action_completed": True,
        "publisher_submission_completed": True,
        "scientific_reexecution_performed": False,
        "statistical_reanalysis_performed": False,
        "frozen_science_modified": False,
        "publisher_facing_files_modified_after_submission": False,
    }
    for key, value in expected.items():
        if status.get(key) != value:
            fail(f"Acta submitted-state {key} drift: {status.get(key)!r} != {value!r}")

    recorded_hashes = status.get("submitted_files_sha256", {})
    if recorded_hashes != EXPECTED_SUBMITTED_FILES:
        fail("Acta submitted-state file-hash map drift")

    for name, expected_hash in EXPECTED_SUBMITTED_FILES.items():
        path = ACTA_DIR / name
        if not path.is_file():
            fail(f"missing submitted publisher-facing file: {name}")
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            fail(f"submitted publisher-facing hash drift for {name}: {actual_hash} != {expected_hash}")
        print(f"[OK] Acta submitted file hash: {name}")

    for required in (
        "README_CURRENT.md",
        "SUBMISSION_CONFIRMED_2026-09-06.md",
        "EDITORIAL_MANAGER_SUBMITTED_VALUES_2026-09-06.md",
        "FINAL_SUBMISSION_AUTHORIZATION_2026-09-06.md",
    ):
        if not (ACTA_DIR / required).is_file():
            fail(f"missing Acta post-submission record: {required}")


def check_current_docs() -> None:
    for rel, rules in CURRENT_DOCS.items():
        text = read(rel)
        for token in rules["required"]:
            if token not in text:
                fail(f"{rel}: required current-state token missing: {token!r}")
        for token in rules["forbidden"]:
            if token in text:
                fail(f"{rel}: stale current-state wording present: {token!r}")
        print(f"[OK] Study-8/Acta current-state wording: {rel}")


def main() -> int:
    check_source_freeze()
    check_acta_submission()
    check_current_docs()

    print("study8_publication_current_state=PASS")
    print(f"source_publication_status={SOURCE_STATUS}")
    print(f"source_publication_merge_commit={SOURCE_MERGE_COMMIT}")
    print(f"acta_manuscript_id={ACTA_MANUSCRIPT_ID}")
    print(f"acta_submission_date={ACTA_SUBMISSION_DATE}")
    print(f"acta_current_status={ACTA_CURRENT_STATUS}")
    print("acta_submission_completed=true")
    print("scientific_reexecution_performed=false")
    print("statistical_reanalysis_performed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
