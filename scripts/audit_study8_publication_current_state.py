#!/usr/bin/env python3
"""Fail-closed audit for the current Study-8 publication-package repository state.

Historical Study-8 technical-close and Phase-8.9 freeze artifacts are provenance and
may retain stage-local authorization wording. This checker governs only current-state
surfaces after the authorized PR #92 merge. It never executes scientific analysis or
modifies frozen evidence/publication artifacts.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json"
FREEZE_CHECKER = ROOT / "publication/study8/scripts/check_publication_freeze.py"

CURRENT_STATUS = "PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED"
PR_NUMBER = 92
REVIEWED_HEAD = "75c98356751087dd648684ade7cb973c166cbce0"
FROZEN_PACKAGE_COMMIT = "cbad15227bf99d1b7b19d95b0581196d78208f95"
MERGE_COMMIT = "87bcec000d278aeffef1222ce814098c93ada362"
RESULTS_FREEZE_CI = 33781901833
REPOSITORY_CI = 33781901724
MANUSCRIPT_SHA = "efbe78c43c44cde057637fc1744746d0ab4da8aed71e30d709aedd7dbdef13d6"

CURRENT_DOCS = {
    "README.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            str(RESULTS_FREEZE_CI),
            str(REPOSITORY_CI),
            "publication/study8/",
        ),
        "forbidden": (
            "Its publication integration has not started",
            "**Study 8 is not yet integrated into `publication/`.**",
        ),
    },
    "study8/README.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            "venue-specific submission-package preparation",
            "publication/study8/",
        ),
        "forbidden": (
            "**Technical status:** `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED`",
            "The next work is **publication integration only**",
        ),
    },
    "publication/README.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            "Study-8 companion displays",
            "venue-specific Study-8 submission package",
        ),
        "forbidden": (
            "A later explicit publication-integration gate is required before a Study-8 companion-paper package is created",
            "No Study-8 figure/table is part of this directory yet",
            "The Study-8 companion paper requires a separate publication/submission package after an explicit publication-integration gate",
        ),
    },
    "publication/study8/README.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            "11 publication artifacts",
            "venue-specific submission-package preparation",
        ),
        "forbidden": (
            "PHASE8_8_PUBLICATION_DEVELOPMENT_IN_PROGRESS_FROZEN_SCIENCE_ONLY",
            "This phase authorizes development only",
        ),
    },
    "tracker/RESEARCH_TRACKER.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            str(RESULTS_FREEZE_CI),
            str(REPOSITORY_CI),
            "venue-specific submission-package preparation",
        ),
        "forbidden": (
            "A later explicit publication-integration gate is required before Study-8 manuscript or submission work begins",
            "Study 8 is **not yet integrated into `publication/`**",
            "only after repository synchronization is complete, open a separate publication-integration gate",
        ),
    },
    "docs/REPRODUCIBILITY_GUIDE.md": {
        "required": (
            CURRENT_STATUS,
            MERGE_COMMIT,
            str(RESULTS_FREEZE_CI),
            str(REPOSITORY_CI),
            "11 publication artifacts",
        ),
        "forbidden": (
            "publication integration has not started",
            "A later publication gate may create a dedicated companion-paper manuscript",
            "publication integration and scientific re-execution remain unauthorized",
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


def main() -> int:
    if not STATUS_PATH.is_file():
        fail("missing Study-8 publication current-state JSON")
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))

    if status.get("schema") != 2:
        fail(f"unexpected current-state schema: {status.get('schema')!r}")
    if status.get("status") != CURRENT_STATUS:
        fail(f"current publication status drift: {status.get('status')!r}")
    if status.get("phase") != "8.10-post-publication-package-merge-repository-closeout":
        fail(f"current publication phase drift: {status.get('phase')!r}")
    if status.get("publication_package_frozen") is not True:
        fail("publication package is not recorded as frozen")

    merge = status.get("publication_package_merge", {})
    expected_merge = {
        "completed": True,
        "pull_request": PR_NUMBER,
        "reviewed_head": REVIEWED_HEAD,
        "frozen_package_commit": FROZEN_PACKAGE_COMMIT,
        "main_merge_commit": MERGE_COMMIT,
    }
    for key, expected in expected_merge.items():
        if merge.get(key) != expected:
            fail(f"publication merge {key} drift: {merge.get(key)!r} != {expected!r}")

    for key, run_id in (
        ("post_merge_results_freeze_ci", RESULTS_FREEZE_CI),
        ("post_merge_repository_ci", REPOSITORY_CI),
    ):
        ci = merge.get(key, {})
        if ci.get("run_id") != run_id or ci.get("conclusion") != "success":
            fail(f"publication merge {key} identity/conclusion drift")

    gates = status.get("gate_state", {})
    for key in (
        "scientific_reexecution_authorized",
        "statistical_reanalysis_authorized",
        "frozen_science_modification_authorized",
        "publication_submission_authorized",
        "publisher_portal_action_authorized",
    ):
        if gates.get(key) is not False:
            fail(f"current prohibited gate unexpectedly open: {key}")
    if gates.get("pull_request_merge_completed") is not True:
        fail("current status does not record completed PR #92 merge")
    if gates.get("pull_request_merge_authorization_consumed") is not True:
        fail("current status does not record consumed PR #92 merge authorization")
    if gates.get("pull_request_merge_authorized") is not False:
        fail("a new pending publication-package PR merge is unexpectedly authorized")

    venue = status.get("venue_development", {})
    if venue.get("final_venue_committed") is not False:
        fail("final Study-8 venue unexpectedly committed")
    if venue.get("venue_specific_submission_preparation_authorized") is not False:
        fail("venue-specific submission preparation unexpectedly authorized")
    if "venue-specific submission-package preparation" not in status.get("next_gate", ""):
        fail("current next gate is not venue-specific submission-package preparation")

    manifest = json.loads((ROOT / "publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    frozen_files = manifest.get("frozen_files", {})
    if len(frozen_files) != 11:
        fail(f"expected 11 hash-frozen publication artifacts, found {len(frozen_files)}")
    if frozen_files.get("publication/study8/manuscript/manuscript.md") != MANUSCRIPT_SHA:
        fail("frozen manuscript SHA drift")

    for rel, rules in CURRENT_DOCS.items():
        text = read(rel)
        for token in rules["required"]:
            if token not in text:
                fail(f"{rel}: required current-state token missing: {token!r}")
        for token in rules["forbidden"]:
            if token in text:
                fail(f"{rel}: stale current-state wording present: {token!r}")
        print(f"[OK] Study-8 publication current-state wording: {rel}")

    freeze = subprocess.run(
        [sys.executable, str(FREEZE_CHECKER)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if freeze.returncode != 0:
        fail("Study-8 publication-freeze checker failed:\n" + freeze.stdout.rstrip())
    if "study8_publication_freeze=PASS" not in freeze.stdout:
        fail("Study-8 publication-freeze checker did not emit PASS")
    if "publication_package_merge=COMPLETED" not in freeze.stdout:
        fail("Study-8 publication-freeze checker did not confirm completed merge")

    print("study8_publication_current_state=PASS")
    print(f"publication_package_merge_commit={MERGE_COMMIT}")
    print(f"post_merge_results_freeze_ci={RESULTS_FREEZE_CI}:SUCCESS")
    print(f"post_merge_repository_ci={REPOSITORY_CI}:SUCCESS")
    print("venue_specific_submission_preparation_authorized=false")
    print("publication_submission_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
