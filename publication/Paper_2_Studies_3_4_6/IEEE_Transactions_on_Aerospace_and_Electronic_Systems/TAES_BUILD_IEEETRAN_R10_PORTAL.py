#!/usr/bin/env python3
"""R10 portal-adaptation builder for TAES Paper 2.

R10 is intentionally narrow. It inherits the visually approved R9 IEEEtran
rendering from the frozen canonical Paper-2 manuscript and injects only the
live Research Exchange conflict-of-interest declaration required on
2026-09-07:

    The author declares no conflict of interest.

The canonical manuscript Markdown, Studies 3/4/6, experimental populations,
results, citations, title, abstract, index terms, figures, tables, and AI-use
acknowledgment are not modified. The generated R10 TeX/PDF and upload archive
must undergo fresh format and visual QA before portal upload.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R8 as r8
import TAES_BUILD_IEEETRAN_R9 as r9

ROOT = Path(__file__).resolve().parent
OUT_TEX = ROOT / "TAES_MANUSCRIPT_R10_PORTAL.tex"
OUT_PDF = ROOT / "TAES_MANUSCRIPT_R10_PORTAL.pdf"
OUT_LOG = ROOT / "TAES_MANUSCRIPT_R10_PORTAL.log"
OUT_AUDIT = ROOT / "TAES_R10_PORTAL_BUILD_AUDIT.txt"

COI_HEADING = r"\section*{Conflict of Interest}"
COI_TEXT = "The author declares no conflict of interest."


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_tex_r10(md: str) -> str:
    tex = r9.make_tex_r9(md)

    if COI_TEXT in tex or COI_HEADING in tex:
        raise SystemExit("ERROR: conflict-of-interest declaration already present before R10 injection")

    marker = r"\begin{thebibliography}{13}"
    if tex.count(marker) != 1:
        raise SystemExit("ERROR: R10 expected exactly one bibliography insertion point")

    block = COI_HEADING + "\n" + COI_TEXT + "\n\n"
    tex = tex.replace(marker, block + marker, 1)

    if tex.count(COI_TEXT) != 1 or tex.count(COI_HEADING) != 1:
        raise SystemExit("ERROR: R10 conflict-of-interest declaration insertion failed")
    if "—" in tex:
        raise SystemExit("ERROR: em dash entered generated R10 TeX")
    return tex


def write_audit(result: dict[str, str | int | float | bool]) -> None:
    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )
    lines = [
        "TAES_R10_PORTAL_BUILD_AUDIT",
        "revision=R10_PORTAL_ADAPTATION",
        f"canonical_manuscript_sha256={r8.EXPECTED_COMPRESSED_MANUSCRIPT}",
        f"canonical_manuscript_tracking_commit={r8.EXPECTED_MANUSCRIPT_TRACKING_COMMIT}",
        f"figure1_pdf_sha256={base.EXPECTED_FIG_PDF}",
        f"figure1_png_sha256={base.EXPECTED_FIG_PNG}",
        "science_changed=NO",
        "canonical_markdown_changed=NO",
        "title_changed=NO",
        "abstract_changed=NO",
        "references_changed=NO",
        "authorship=SOLE_AUTHOR_AMAN_KUMAR_SINGH",
        "portal_required_coi_statement=The author declares no conflict of interest.",
        f"tex_sha256={result['tex_sha256']}",
        f"pdf_sha256={result['pdf_sha256']}",
        f"log_sha256={result['log_sha256']}",
        f"pages={result['pages']}",
        f"page_size={result['page_size']}",
        f"overfull_hbox_count={result['overfull_hbox_count']}",
        f"overfull_vbox_count={result['overfull_vbox_count']}",
        f"latex_warning_count={result['latex_warning_count']}",
        f"font_count={result['font_count']}",
        f"font_embedding_all_yes={'PASS' if result['font_embedding_all_yes'] else 'FAIL'}",
        f"layout_warning_gate={'PASS' if layout_clean else 'REVIEW_REQUIRED'}",
        "live_portal_coi_author_confirmation=YES_2026-09-07",
        "author_portal_adaptation_authorization=GRANTED_2026-09-07",
        "publisher_facing=NO_PENDING_R10_VISUAL_QA_AND_UPLOAD_MANIFEST_FREEZE",
    ]
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    # The canonical Markdown file is intentionally unchanged, so the historical
    # binding and tracking-commit gates remain valid.
    r8.verify_manuscript_tracking_commit()
    base.EXPECTED_MANUSCRIPT = r8.EXPECTED_COMPRESSED_MANUSCRIPT

    base.OUT_TEX = OUT_TEX
    base.OUT_PDF = OUT_PDF
    base.OUT_LOG = OUT_LOG
    base.OUT_AUDIT = OUT_AUDIT
    base.make_tex = make_tex_r10

    result = base.build_and_audit()
    write_audit(result)

    tex = OUT_TEX.read_text(encoding="utf-8")
    if tex.count(COI_TEXT) != 1:
        raise SystemExit("ERROR: generated R10 TeX does not contain exactly one COI declaration")

    print("TAES_R10_PORTAL_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("science_changed=NO")
    print("canonical_markdown_changed=NO")
    print("authorship=SOLE_AUTHOR_AMAN_KUMAR_SINGH")
    print("coi_declaration=PASS_SINGLE_OCCURRENCE")
    print(f"pages={result['pages']}")
    print(f"page_size={result['page_size']}")
    print(f"overfull_hbox_count={result['overfull_hbox_count']}")
    print(f"overfull_vbox_count={result['overfull_vbox_count']}")
    print(f"latex_warning_count={result['latex_warning_count']}")
    print(f"font_embedding_all_yes={'PASS' if result['font_embedding_all_yes'] else 'FAIL'}")
    print(f"tex={OUT_TEX.name}")
    print(f"tex_sha256={sha256(OUT_TEX)}")
    print(f"pdf={OUT_PDF.name}")
    print(f"pdf_sha256={sha256(OUT_PDF)}")
    print(f"audit={OUT_AUDIT.name}")
    print("publisher_facing=NO_PENDING_R10_VISUAL_QA_AND_UPLOAD_MANIFEST_FREEZE")


if __name__ == "__main__":
    main()
