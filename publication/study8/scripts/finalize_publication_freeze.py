#!/usr/bin/env python3
"""Single-use Study-8 publication-only correction and hash-freeze operation.

This script is intentionally publication-scoped. It does not execute the Study-8
model, statistical implementations, or derive new scientific summaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "publication" / "study8"
AUTH_PATH = ROOT / "study8" / "PHASE8_9_PUBLICATION_PACKAGE_FREEZE_AUTHORIZATION.json"
STATUS_PATH = PUB / "PUBLICATION_DEVELOPMENT_STATUS.json"
MANIFEST_PATH = PUB / "PUBLICATION_PACKAGE_FREEZE_MANIFEST.json"
REVIEW_PATH = PUB / "FINAL_ADVERSARIAL_REVIEW.md"
SUMS_PATH = PUB / "SHA256SUMS.txt"

CORE_FROZEN_FILES = [
    "publication/study8/manuscript/manuscript.md",
    "publication/study8/references/references.bib",
    "publication/study8/claim-traceability.csv",
    "publication/study8/author-submission-metadata.md",
    "publication/study8/tables/table-s8-1-design.csv",
    "publication/study8/tables/table-s8-2-primary-profile.csv",
    "publication/study8/tables/table-s8-3-p3-vs-p1-strata.csv",
    "publication/study8/tables/table-s8-4-policy-tradeoffs.csv",
    "publication/study8/figures/figure-s8-1-profile-success.svg",
    "publication/study8/figures/figure-s8-2-regime-success.svg",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one replacement target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: Path, marker: str, line: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        raise SystemExit(f"{label}: marker already present")
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")


def require_authorization() -> dict:
    if not AUTH_PATH.is_file():
        raise SystemExit("publication freeze authorization is missing")
    auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    expected = {
        "authorization_id": "S8-PUBFREEZE-001",
        "publication_package_freeze_authorized": True,
        "final_adversarial_review_authorized": True,
        "publication_only_corrections_authorized": True,
        "prepare_pull_request_for_merge_authorized": True,
        "scientific_reexecution_authorized": False,
        "statistical_reanalysis_authorized": False,
        "frozen_science_modification_authorized": False,
        "pull_request_merge_authorized": False,
        "publication_submission_authorized": False,
        "publisher_portal_action_authorized": False,
        "single_use": True,
        "consumed": False,
    }
    for key, value in expected.items():
        if auth.get(key) != value:
            raise SystemExit(f"authorization mismatch: {key}={auth.get(key)!r}, expected {value!r}")

    branch = os.environ.get("GITHUB_REF_NAME", git("branch", "--show-current"))
    if branch != auth["required_branch"]:
        raise SystemExit(f"wrong branch: {branch}")

    trigger = os.environ.get("GITHUB_SHA", git("rev-parse", "HEAD"))
    if trigger != git("rev-parse", "HEAD"):
        raise SystemExit("GITHUB_SHA does not match checked-out trigger head")
    parent = git("rev-parse", "HEAD^")
    if parent != auth["authorized_parent_commit"]:
        raise SystemExit(f"authorization parent mismatch: {parent}")
    changed = git("diff", "--name-only", "HEAD^", "HEAD").splitlines()
    if changed != ["study8/PHASE8_9_PUBLICATION_PACKAGE_FREEZE_AUTHORIZATION.json"]:
        raise SystemExit(f"trigger commit must contain only the authorization file: {changed}")

    if os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise SystemExit("single-use publication freeze rejects GitHub rerun attempts")
    return auth


def apply_publication_corrections() -> None:
    manuscript = PUB / "manuscript" / "manuscript.md"
    replace_once(
        manuscript,
        "A separately implemented reference model reproduced all 3,456 canonical rows exactly, and an independent statistical implementation reproduced the frozen findings byte-for-byte.",
        "A separately implemented same-repository reference model reproduced all 3,456 canonical rows exactly, and a separate same-repository statistical implementation reproduced the frozen machine-readable findings byte-for-byte.",
        "AR-01 external-replication ambiguity",
    )
    replace_once(
        manuscript,
        "The results indicate that, in this frozen logical-contact model, contact-aware guarding does not create recovery capacity; standardized cryptographic-object size, temporal contact structure, and deadline dominate recovery feasibility, while transition policy primarily governs security-state and availability tradeoffs.",
        "The results indicate that, in this frozen logical-contact model, contact-aware guarding does not create recovery capacity; standardized cryptographic-object size, logical contact structure, and deadline account for the observed feasibility differences, while transition policy primarily governs security-state and availability tradeoffs.",
        "AR-02 abstract dominance wording",
    )
    replace_once(
        manuscript,
        "Thus equal total-cycle capacity did not imply equal deadline-constrained feasibility; the temporal placement of capacity mattered in the frozen model.",
        "Thus equal total-cycle capacity did not imply equal deadline-constrained feasibility; how that capacity was partitioned among contacts and placed across logical slots mattered in the frozen model.",
        "AR-03 contact-regime interpretation",
    )
    replace_once(
        manuscript,
        "Their different success proportions therefore isolate the temporal distribution of capacity within the frozen abstraction.",
        "Their different success proportions therefore show that equal complete-cycle total capacity does not erase differences created by how capacity is partitioned among contacts and placed across logical slots.",
        "AR-04 isolation overclaim",
    )
    replace_once(
        manuscript,
        "### Artificial-intelligence assistance\n\nAny journal-specific AI-use declaration will be finalized against the selected publisher's current policy at the separate submission-package gate. Scientific results, frozen evidence identities, and claim boundaries are repository-controlled and independently auditable.",
        "### Artificial-intelligence assistance\n\nGenerative-AI language assistance was used during manuscript development and publication-package review. The author retains responsibility for review and final approval. No new Study-8 scientific execution was authorized or performed in this publication phase, and the frozen scientific results, evidence identities, and claim boundaries were not altered. Any journal-specific disclosure will be aligned to the selected publisher's current policy at the separate submission-package gate.",
        "AR-05 AI-use provenance",
    )

    trace = PUB / "claim-traceability.csv"
    replace_once(
        trace,
        'S8-C06,Results 4.3,"R1/R2/R3/R4 success differs despite equal 65536-byte complete-cycle capacity","study8/STUDY8_CONTACT_MODEL.md; study8/analysis/results/primary_findings.json","temporal contact distribution conditions modeled deadline feasibility","orbital geometry measured; RF scheduling measured; real contact-duration result"',
        'S8-C06,Results 4.3,"R1/R2/R3/R4 success differs despite equal 65536-byte complete-cycle capacity","study8/STUDY8_CONTACT_MODEL.md; study8/analysis/results/primary_findings.json","partitioning and logical-slot placement of equal complete-cycle capacity condition modeled deadline feasibility","orbital geometry measured; RF scheduling measured; real contact-duration result"',
        "AR-06 traceability contact-structure wording",
    )
    append_once(
        trace,
        "S8-C16,",
        'S8-C16,Abstract/Limitations,"Primary/reference model and statistical reproduction are same-repository implementation-separated checks","study8/results/S8-PQC-ICR-001/independent_audit_summary.json; study8/analysis/results/findings_audit.json; study8/analysis/results/interpretation_audit.json","separately implemented same-repository reproduction/audit","external laboratory replication; independent human replication; empirical validation"',
        "AR-07 reproduction-boundary traceability",
    )

    figure1 = PUB / "figures" / "figure-s8-1-profile-success.svg"
    replace_once(
        figure1,
        "Bar chart showing 93.75 percent success for PROFILE_512_44, 64.9306 percent for PROFILE_768_65, and 61.8056 percent for PROFILE_1024_87 across the frozen 3456-position deterministic population.",
        "Bar chart showing 93.75 percent success for PROFILE_512_44, 64.9306 percent for PROFILE_768_65, and 61.8056 percent for PROFILE_1024_87 within each profile's 1,152 equally weighted frozen positions.",
        "AR-08 figure denominator clarity",
    )

    figure2 = PUB / "figures" / "figure-s8-2-regime-success.svg"
    replace_once(
        figure2,
        "Synthetic logical contact timing only; no orbital-geometry, RF-throughput, or physical-duration interpretation.",
        "Synthetic logical contact structure only; no orbital-geometry, RF-throughput, or physical-duration interpretation.",
        "AR-09 figure contact-structure wording",
    )

    author_meta = PUB / "author-submission-metadata.md"
    replace_once(
        author_meta,
        "## AI-use declaration placeholder\n\nThe final declaration must be matched to the selected venue's live policy at submission time. Manuscript development may use language assistance, but frozen scientific results, exact statistics, hashes, and claim boundaries remain repository-controlled and independently auditable. Do not finalize publisher-specific wording until the submission gate.",
        "## AI-use provenance for publication development\n\nOpenAI ChatGPT was used for language/drafting assistance during manuscript development and publication-package review. The author retains responsibility for review and final approval. This assistance did not authorize or perform new Study-8 scientific execution, change frozen results, or alter the frozen statistical findings. The exact publisher-facing declaration must still be matched to the selected venue's live policy at the separate submission gate.",
        "AR-10 author-metadata AI provenance",
    )

    projection = PUB / "scripts" / "check_publication_projection.py"
    replace_once(projection, "require(len(trace) == 15, f\"expected 15 claim-traceability rows, found {len(trace)}\")", "require(len(trace) == 16, f\"expected 16 claim-traceability rows, found {len(trace)}\")", "projection trace row count")
    replace_once(projection, "require(len({r[\"claim_id\"] for r in trace}) == 15, \"claim IDs are not unique\")", "require(len({r[\"claim_id\"] for r in trace}) == 16, \"claim IDs are not unique\")", "projection unique trace count")


def write_review(auth: dict, now: str, trigger: str) -> None:
    REVIEW_PATH.write_text(
        f"""# Study 8 Final Manuscript Adversarial Review\n\n**Review ID:** `S8-PUB-AR-001`  \n**Freeze authorization:** `{auth['authorization_id']}`  \n**Trigger commit:** `{trigger}`  \n**Review time (UTC):** `{now}`  \n**Scope:** publication layer only; frozen Study-8 science remained read-only.\n\n## Disposition\n\n`PASS_PUBLICATION_ONLY_CORRECTIONS_APPLIED_READY_FOR_HASH_FREEZE`\n\n## Adversarial findings corrected\n\n1. **External-replication ambiguity.** Abstract wording was changed from an unqualified “independent statistical implementation” to explicit same-repository, separately implemented reproduction language.\n2. **Contact-structure overstatement.** Wording that could imply isolation of timing alone was corrected to describe partitioning of fixed total-cycle capacity among contacts and placement across logical slots.\n3. **Dominance wording.** The abstract no longer says the profile/contact/deadline factors “dominate” recovery feasibility; it states that they account for the observed feasibility differences in the frozen model.\n4. **Figure denominator clarity.** The profile figure now states that each bar is based on that profile's 1,152 frozen positions rather than ambiguously referring to all 3,456 positions.\n5. **Reproduction traceability.** A dedicated claim-traceability row now prohibits external-laboratory or independent-human-replication language.\n6. **AI-use provenance.** Development metadata and the manuscript now truthfully record generative-AI language assistance while preserving author responsibility and the frozen-science boundary.\n\n## Claims re-audited and retained\n\n- Negative primary result remains prominent: all four policies `635/864`; P3-P1 exactly `0.000000` percentage points.\n- All 14 prespecified P3-versus-P1 strata remain reported as exact zero contrasts.\n- Profile results remain `1080/1152`, `748/1152`, and `712/1152`; matched non-increasing ordering remains `1152/1152`.\n- Logical slots remain nonphysical ordering units; no conversion to seconds, orbital periods, or real mission recovery time is permitted.\n- Modeled cryptographic bytes remain standardized-object budget only; no RF, CPU, energy, certificate/framing, or flight-performance claim is introduced.\n- Structural zeros remain invariant checks, not treatment-effect evidence.\n- ML-KEM/ML-DSA are not claimed as operational CCSDS-standardized PQC suites.\n- Same-repository reproduction is not external replication or empirical validation.\n- Studies 1-7 remain unpooled with Study 8.\n\n## Gate boundary\n\nThis review authorizes and records the publication-package freeze only. PR #92 merge is **not** authorized by this gate. Publisher submission and publisher-portal actions remain **not authorized**.\n""",
        encoding="utf-8",
    )


def update_status(auth: dict, now: str, trigger: str) -> dict:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    status["phase"] = "8.9-final-manuscript-adversarial-review-and-freeze"
    status["status"] = "PUBLICATION_PACKAGE_HASH_FROZEN_ADVERSARIAL_REVIEW_PASS_READY_FOR_PR_MERGE_REVIEW"
    status["publication_package_frozen"] = True
    status["freeze_id"] = "S8-PUBFREEZE-001"
    status["freeze_authorization_id"] = auth["authorization_id"]
    status["freeze_trigger_commit"] = trigger
    status["freeze_completed_at_utc"] = now
    status["final_adversarial_review"] = "publication/study8/FINAL_ADVERSARIAL_REVIEW.md"
    status["freeze_manifest"] = "publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json"
    status["gate_state"]["manuscript_freeze_authorized"] = True
    status["gate_state"]["pull_request_merge_authorized"] = False
    status["gate_state"]["publication_submission_authorized"] = False
    status["gate_state"]["publisher_portal_action_authorized"] = False
    status["prepare_pull_request_for_merge_authorized"] = True
    status["next_gate"] = "explicit authorization to merge PR #92 after exact-head CI review; publisher submission remains a later separate authorization"
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return status


def consume_authorization(auth: dict, now: str, trigger: str) -> None:
    auth["consumed"] = True
    auth["consumed_at_utc"] = now
    auth["consumed_trigger_commit"] = trigger
    auth["consumed_by_github_run_id"] = os.environ.get("GITHUB_RUN_ID")
    auth["consumed_by_run_attempt"] = int(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    auth["status"] = "CONSUMED_PUBLICATION_PACKAGE_FREEZE_EXECUTED"
    AUTH_PATH.write_text(json.dumps(auth, indent=2) + "\n", encoding="utf-8")


def write_manifest(auth: dict, status: dict, now: str, trigger: str) -> None:
    frozen = {rel: sha256(ROOT / rel) for rel in CORE_FROZEN_FILES + ["publication/study8/FINAL_ADVERSARIAL_REVIEW.md"]}
    manifest = {
        "schema": 1,
        "freeze_id": "S8-PUBFREEZE-001",
        "experiment_id": "S8-PQC-ICR-001",
        "phase": "8.9-final-manuscript-adversarial-review-and-freeze",
        "authorization_id": auth["authorization_id"],
        "trigger_commit": trigger,
        "completed_at_utc": now,
        "scientific_source_bindings": status["scientific_source_bindings"],
        "required_pre_freeze_ci": auth["required_pre_freeze_ci"],
        "frozen_files": frozen,
        "frozen_file_count": len(frozen),
        "scientific_reexecution_performed": False,
        "statistical_reanalysis_performed": False,
        "frozen_science_modified": False,
        "pull_request_merge_authorized": False,
        "publication_submission_authorized": False,
        "status": "PUBLICATION_PACKAGE_HASH_FROZEN_ADVERSARIAL_REVIEW_PASS",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    SUMS_PATH.write_text("".join(f"{digest}  {rel}\n" for rel, digest in sorted(frozen.items())), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-freeze", action="store_true")
    args = parser.parse_args()
    if not args.execute_freeze:
        raise SystemExit("explicit --execute-freeze is required")

    auth = require_authorization()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    trigger = git("rev-parse", "HEAD")

    apply_publication_corrections()
    write_review(auth, now, trigger)
    status = update_status(auth, now, trigger)
    consume_authorization(auth, now, trigger)
    write_manifest(auth, status, now, trigger)

    print("study8_final_adversarial_review=PASS")
    print("publication_only_corrections=APPLIED")
    print("publication_package_hash_freeze=GENERATED")
    print("scientific_reexecution=NOT_PERFORMED")
    print("statistical_reanalysis=NOT_PERFORMED")
    print("pull_request_merge=NOT_AUTHORIZED")
    print("publication_submission=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
