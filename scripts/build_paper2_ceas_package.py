#!/usr/bin/env python3
"""Build an external CEAS draft DOCX/PDF from tracked R5 Markdown. No science/runtime."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md"
AUDIT=ROOT/"scripts/audit_paper2_ceas_r5.py"
FIGURE=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
IMAGE_REL="figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"

def require(cond,msg):
    if not cond:raise SystemExit("PAPER2_CEAS_PACKAGE_HOLD="+msg)
def hash_file(p):
    h=hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def find_soffice():
    return (shutil.which("soffice") or
            ("/Applications/LibreOffice.app/Contents/MacOS/soffice"
             if Path("/Applications/LibreOffice.app/Contents/MacOS/soffice").exists() else None))

def format_docx_table_pagination(doc):
    """Presentation-only Word pagination; preserve table cells and scientific values."""
    import re
    from zipfile import ZipFile
    with ZipFile(doc, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    updated = []
    for info, data in members:
        if info.filename == "word/document.xml":
            xml = data.decode("utf-8")
            for number in (4, 5):
                marker = f">Table {number}</w:t>"
                matches = [p for p in re.findall(r"<w:p>.*?</w:p>", xml, re.DOTALL) if marker in p]
                require(len(matches) == 1, f"table_{number}_caption_missing_or_ambiguous")
                paragraph = matches[0]
                require("<w:pPr>" in paragraph, f"table_{number}_caption_properties_missing")
                xml = xml.replace(paragraph, paragraph.replace("<w:pPr>",
                                  "<w:pPr><w:pageBreakBefore />", 1), 1)
            def adjust_table(match):
                def adjust_row(row_match):
                    row = row_match.group(0)
                    if "<w:cantSplit" in row:
                        return row
                    if "<w:trPr>" in row:
                        return row.replace("<w:trPr>", "<w:trPr><w:cantSplit />", 1)
                    return row.replace("<w:tr>", "<w:tr><w:trPr><w:cantSplit /></w:trPr>", 1)
                return re.sub(r"<w:tr>.*?</w:tr>", adjust_row, match.group(0), flags=re.DOTALL)
            xml, count = re.subn(r"<w:tbl>.*?</w:tbl>", adjust_table, xml, flags=re.DOTALL)
            require(count == 5, "expected_five_word_tables_for_pagination")
            data = xml.encode("utf-8")
        updated.append((info, data))
    with tempfile.NamedTemporaryFile(prefix="ceas-layout-", suffix=".docx",
                                     delete=False, dir=str(doc.parent)) as tmp:
        staged = Path(tmp.name)
    try:
        with ZipFile(staged, "w") as output:
            for info, data in updated:
                output.writestr(info, data)
        staged.replace(doc)
    finally:
        staged.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--draft-preview",action="store_true")
    ap.add_argument("--out-dir")
    a=ap.parse_args()
    require(a.check != a.draft_preview,"choose_exactly_one_of_check_or_draft_preview")
    r=subprocess.run(["python3",str(AUDIT)],cwd=ROOT,check=False,capture_output=True,text=True)
    require(r.returncode==0,"static_audit:"+r.stdout+r.stderr)
    print(r.stdout,end="")
    if a.check:
        print("CEAS_PACKAGE_RENDER=NOT_EXECUTED")
        return
    require(a.out_dir is not None,"external_out_dir_required")
    out=Path(a.out_dir).expanduser().resolve()
    require(not out.exists(),"refuse_existing_output_directory")
    require(ROOT != out and ROOT not in out.parents,"refuse_repository_output")
    require(shutil.which("pandoc") is not None,"pandoc_required")
    require(find_soffice() is not None,"libreoffice_required_for_pdf")
    require(FIGURE.is_file(),"canonical_figure_missing")
    try:import cairosvg
    except ImportError:raise SystemExit("PAPER2_CEAS_PACKAGE_HOLD=python_cairosvg_required")
    content=SOURCE.read_text(encoding="utf-8")
    require(IMAGE_REL in content,"expected_canonical_figure_reference_missing")
    with tempfile.TemporaryDirectory(prefix="p2-ceas-stage-") as root:
        stage=Path(root)
        img=stage/"ceas_figure_1.png"
        cairosvg.svg2png(url=str(FIGURE),write_to=str(img),output_width=2400)
        md=stage/"source.md"
        md.write_text(content.replace(IMAGE_REL,str(img)),encoding="utf-8")
        doc=stage/"PAPER2_CEAS_R5_DRAFT.docx"
        subprocess.run(["pandoc",str(md),"--from=markdown","--to=docx",
                        "--standalone","--output",str(doc)],check=True)
        format_docx_table_pagination(doc)
        subprocess.run([find_soffice(),"--headless","--convert-to","pdf",
                        "--outdir",str(stage),str(doc)],check=True)
        pdf=doc.with_suffix(".pdf")
        require(doc.is_file() and pdf.is_file(),"docx_pdf_missing")
        require(doc.stat().st_size>40000 and pdf.stat().st_size>40000,
                "docx_pdf_too_small")
        out.mkdir(parents=True,exist_ok=False)
        shutil.copy2(doc,out/doc.name)
        shutil.copy2(pdf,out/pdf.name)
        shutil.copy2(FIGURE,out/FIGURE.name)
        report={"classification":"DRAFT_PREVIEW__NOT_SUBMISSION_READY",
                "r4_immutable_git_blob":"069e319864b1f5c1ee201b31872fea1923",
                "source_sha256":hash_file(SOURCE),
                "artifacts":{p.name:hash_file(p) for p in out.iterdir()},
                "required_human_qa":["inspect_every_rendered_pdf_page",
                                     "confirm_corresponding_email_and_declarations",
                                     "finalize_data_code_availability",
                                     "verify_references_and_figure",
                                     "resolve_author_portal_fields"]}
        (out/"BUILD_AUDIT.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("CEAS_PREVIEW_RENDERED=YES")
    print("CEAS_SUBMISSION_READY=NO")
    print("OUTPUT_DIRECTORY="+str(out))
if __name__=="__main__":main()
