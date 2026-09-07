#!/usr/bin/env python3
"""Materialize the frozen R9 TAES initial-submission package locally.

This script performs packaging only. It does not modify manuscript science,
rerun Studies 3/4/6, change the canonical Markdown manuscript, or submit to
IEEE. It verifies the exact frozen R9 PDF before renaming it to the publisher-
facing filename, updates TAES_PACKAGE_STATUS.json to the R9 freeze state, and
removes regenerated development-only TEX/audit files that are no longer needed
for the publisher-facing package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
DEV_PDF = ROOT / "TAES_MANUSCRIPT_IEEETRAN_DEV.pdf"
FINAL_PDF = ROOT / "TAES_MANUSCRIPT.pdf"
DEV_TEX = ROOT / "TAES_MANUSCRIPT_IEEETRAN_DEV.tex"
DEV_AUDIT = ROOT / "TAES_IEEETRAN_BUILD_AUDIT.txt"
STATUS = ROOT / "TAES_PACKAGE_STATUS.json"
AUDIT = ROOT / "TAES_R9_PACKAGE_MATERIALIZATION_AUDIT.txt"

EXPECTED_MANUSCRIPT_SHA = "802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48"
EXPECTED_PDF_SHA = "a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319"
EXPECTED_PAGES = 16


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing {label}: {path.name}")
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(
            f"ERROR: {label} SHA mismatch: expected={expected} actual={actual}"
        )


def materialize_pdf() -> str:
    require_hash(MANUSCRIPT, EXPECTED_MANUSCRIPT_SHA, "canonical manuscript")

    if FINAL_PDF.exists():
        actual = sha256(FINAL_PDF)
        if actual != EXPECTED_PDF_SHA:
            raise SystemExit(
                "ERROR: TAES_MANUSCRIPT.pdf already exists with a non-frozen SHA: " + actual
            )
        if DEV_PDF.exists():
            require_hash(DEV_PDF, EXPECTED_PDF_SHA, "R9 development PDF")
            DEV_PDF.unlink()
        return "EXISTING_FINAL_PDF_VERIFIED"

    require_hash(DEV_PDF, EXPECTED_PDF_SHA, "R9 development PDF")
    DEV_PDF.replace(FINAL_PDF)
    require_hash(FINAL_PDF, EXPECTED_PDF_SHA, "publisher-facing R9 PDF")
    return "RENAMED_DEV_PDF_TO_TAES_MANUSCRIPT_PDF"


def update_status() -> None:
    if not STATUS.is_file():
        raise SystemExit("ERROR: TAES_PACKAGE_STATUS.json missing")

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    if data.get("paper_id") != "PAPER2_STUDIES_3_4_6":
        raise SystemExit("ERROR: unexpected package-status paper_id")

    data["status"] = "R9_16_PAGE_PUBLISHER_FACING_CANDIDATE_FROZEN__PREPORTAL_READY"
    data["submission_authorized"] = False
    data["explicit_final_author_submission_authorization"] = True
    data["explicit_final_author_submission_authorization_date"] = "2026-09-06"
    data["effective_portal_submission_authorization"] = False
    data["effective_portal_submission_blockers"] = [
        "authenticated_atypon_rex_live_field_capture",
        "portal_generated_submission_proof_qa_before_submit_action"
    ]

    dev = data.setdefault("manuscript_development", {})
    dev["current_canonical_assembled_sha256"] = EXPECTED_MANUSCRIPT_SHA
    dev["current_canonical_tracking_commit"] = "710a72af05fb418a0d82a659198a677b9e2a8948"
    dev["current_total_words_including_references"] = 10119
    dev["compression_pass2_r2"] = "PASS_1918_WORD_CONTROLLED_REDUCTION_SCIENCE_PRESERVED"
    dev["r9_builder"] = "TAES_BUILD_IEEETRAN_R9.py"
    dev["r9_development_pdf_sha256"] = EXPECTED_PDF_SHA
    dev["r9_page_count"] = EXPECTED_PAGES
    dev["r9_overfull_hbox_count"] = 0
    dev["r9_font_embedding"] = "PASS_13_OF_13_EMBEDDED"
    dev["taes_format_audit_pass"] = "PASS_R9_IEEETRAN_FORMAT_QA_2026-09-06"
    dev["pdf_visual_qa_pass"] = "PASS_ALL_16_PAGES_R9_2026-09-06"
    dev["style_and_taes_format_audit"] = "PASS_R9_FORMAT_AND_VISUAL_QA_2026-09-06"
    dev["publisher_facing_freeze"] = "TAES_R9_PUBLISHER_FACING_FREEZE_2026-09-06.md"
    dev["supplementary_material_decision"] = "TAES_SUPPLEMENTARY_MATERIAL_DECISION_2026-09-06.md__NO_SEPARATE_INITIAL_UPLOAD"
    dev["portal_field_audit"] = "TAES_PORTAL_FIELD_AUDIT_R1_2026-09-06.md__PASS_PREPORTAL_READY_FOR_LIVE_CAPTURE"
    dev["upload_manifest"] = "TAES_INITIAL_SUBMISSION_UPLOAD_MANIFEST_2026-09-06.json__SHA256_FROZEN"

    pub = data.setdefault("publisher_facing_files", {})
    pub["manuscript_pdf"] = (
        "TAES_MANUSCRIPT.pdf__FROZEN_R9_16_PAGES__SHA256_" + EXPECTED_PDF_SHA
    )
    pub["supplementary_material"] = "FROZEN_NONE_FOR_INITIAL_REVIEW"
    pub["supplementary_readme"] = "NOT_APPLICABLE"
    pub["cover_letter"] = "NOT_PUBLICLY_REQUIRED__LIVE_PORTAL_RECHECK"

    gates = data.setdefault("mandatory_final_gates", [])
    # Preserve the historical gate list. Detailed gate dispositions are recorded
    # in the dedicated R9 freeze/audit files rather than replacing this list.
    if "taes_format_audit_pass" not in gates:
        gates.insert(0, "taes_format_audit_pass")

    notes = data.setdefault("notes", [])
    additions = [
        "The current canonical manuscript is the controlled Pass-2 R2 version tracked at commit 710a72af05fb418a0d82a659198a677b9e2a8948 with SHA-256 802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48.",
        "The current manuscript contains 10,119 words including references and renders to 16 TAES-formatted pages in R9.",
        "R9 IEEEtran formatting QA and all-16-page visual QA passed. The frozen publisher-facing PDF is TAES_MANUSCRIPT.pdf with SHA-256 a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319.",
        "The supplementary-material decision is frozen as no separate supplementary upload for initial review unless the live portal, editor, or reviewer requires specific material.",
        "The initial upload manifest is frozen and contains only TAES_MANUSCRIPT.pdf as the required portal upload file.",
        "Effective portal submission remains blocked only for authenticated live-field capture and portal-generated proof QA before the final Submit action."
    ]
    for note in additions:
        if note not in notes:
            notes.append(note)

    STATUS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cleanup_dev_files() -> list[str]:
    removed: list[str] = []
    for path in (DEV_TEX, DEV_AUDIT):
        if path.exists():
            path.unlink()
            removed.append(path.name)
    return removed


def main() -> None:
    action = materialize_pdf()
    update_status()
    removed = cleanup_dev_files()

    require_hash(MANUSCRIPT, EXPECTED_MANUSCRIPT_SHA, "canonical manuscript after packaging")
    require_hash(FINAL_PDF, EXPECTED_PDF_SHA, "publisher-facing PDF after packaging")

    audit_lines = [
        "TAES_R9_PACKAGE_MATERIALIZATION=PASS",
        f"pdf_action={action}",
        f"publisher_facing_pdf={FINAL_PDF.name}",
        f"publisher_facing_pdf_sha256={sha256(FINAL_PDF)}",
        f"canonical_manuscript_sha256={sha256(MANUSCRIPT)}",
        f"pages={EXPECTED_PAGES}",
        "supplementary_material=NONE_INITIAL_REVIEW",
        "initial_upload_manifest=TAES_INITIAL_SUBMISSION_UPLOAD_MANIFEST_2026-09-06.json",
        "portal_field_audit=PASS_PREPORTAL_READY_FOR_LIVE_CAPTURE",
        "author_submission_authorization=GRANTED_2026-09-06",
        "effective_portal_submission_authorization=NO_PENDING_LIVE_CAPTURE_AND_PROOF_QA",
        "science_changed=NO",
        "study_rerun=NO",
        "removed_development_files=" + (",".join(removed) if removed else "NONE"),
    ]
    AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print("TAES_R9_PACKAGE_MATERIALIZATION=PASS")
    print(f"pdf_action={action}")
    print(f"publisher_facing_pdf={FINAL_PDF}")
    print(f"publisher_facing_pdf_sha256={sha256(FINAL_PDF)}")
    print(f"canonical_manuscript_sha256={sha256(MANUSCRIPT)}")
    print(f"pages={EXPECTED_PAGES}")
    print("supplementary_material=NONE_INITIAL_REVIEW")
    print("package_status=UPDATED_TO_R9_PREPORTAL_READY")
    print("science_changed=NO")
    print("study_rerun=NO")
    print("removed_development_files=" + (",".join(removed) if removed else "NONE"))
    print(f"audit={AUDIT}")


if __name__ == "__main__":
    main()
