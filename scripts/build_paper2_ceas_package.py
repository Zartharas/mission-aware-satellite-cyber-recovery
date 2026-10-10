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
FIGURE=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_CEAS_FIG1_TRUST_BOUNDARIES_R5.svg"
IMAGE_REL="figures/PAPER2_CEAS_FIG1_TRUST_BOUNDARIES_R5.svg"
FIGURE_ALT="Three nonpooled trust boundaries: Study 3 validly signed false producer evidence with S3X timing proxy; Study 4 vote and synthetic provenance composition; Study 6 an approved bad-source artifact with S6X functional adjudication outside the six-signal gate."
FIGURE_ALT_TITLE="Figure 1: Residual trust boundaries in satellite cyber-recovery qualification"

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
    """Edit only Word layout. Fail closed on unexpected Pandoc OOXML structure."""
    import re
    from zipfile import ZipFile

    # Each width tuple sums to 9360 twips (6.5in); cells and manuscript values
    # are preserved. The two dense tables use 9pt rather than default text size.
    widths = (
        (2189, 2016, 2419, 2736),
        (2304, 1800, 2808, 2448),
        (1440, 4032, 3888),
        (1008, 1944, 2880, 3528),
        (3600, 5760),
    )
    def font_size(run, half_points):
        tag = f'<w:sz w:val="{half_points}" />'
        if '<w:rPr>' in run:
            return run.replace('<w:rPr>', '<w:rPr>' + tag, 1)
        return run.replace('<w:r>', '<w:r><w:rPr>' + tag + '</w:rPr>', 1)

    with ZipFile(doc, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    output = []
    for info, data in members:
        if info.filename == "word/document.xml":
            xml = data.decode("utf-8")
            require(all(len(re.findall(r'>Table '+str(n)+r'</w:t>', xml)) == 1
                        for n in range(1, 6)),
                    "five_table_captions_missing_or_ambiguous")
            def paragraph_edit(match):
                para = match.group(0)
                if re.search(r'>Table [1-5]</w:t>', para):
                    require('<w:pPr>' in para, "table_caption_properties_missing")
                    # Keep each table caption with the following table; avoid
                    # unconditional page breaks that create large blank regions.
                    para = para.replace('<w:pageBreakBefore />', '')
                    return para.replace('<w:pPr>', '<w:pPr><w:keepNext />', 1)
                if re.search(r'>\[\d{1,2}\] ', para):
                    require('<w:pPr>' in para, "reference_paragraph_properties_missing")
                    para = para.replace(
                        '<w:pPr>',
                        '<w:pPr><w:spacing w:before="0" w:after="50" '
                        'w:line="240" w:lineRule="auto" />', 1)
                    return re.sub(r'<w:r>.*?</w:r>',
                                  lambda r: font_size(r.group(0), 20),
                                  para, flags=re.DOTALL)
                return para
            require(len(re.findall(r'>\[\d{1,2}\] ', xml)) == 19,
                    "expected_19_numbered_reference_paragraphs")
            xml = re.sub(r'<w:p>.*?</w:p>', paragraph_edit,
                         xml, flags=re.DOTALL)

            index = [0]
            def table_edit(match):
                i = index[0]
                index[0] += 1
                table = match.group(0)
                require(i < 5, "more_than_five_tables")
                require('<w:tblPr>' in table, "table_properties_missing")
                table = table.replace('<w:tblPr>',
                                      '<w:tblPr><w:tblLayout w:type="fixed" />', 1)
                old_grid = re.search(r'<w:tblGrid>.*?</w:tblGrid>',
                                     table, flags=re.DOTALL)
                require(old_grid is not None, "table_grid_missing")
                grid = '<w:tblGrid>' + ''.join(
                    f'<w:gridCol w:w="{w}" />' for w in widths[i]
                ) + '</w:tblGrid>'
                table = table.replace(old_grid.group(0), grid, 1)
                rows = re.findall(r'<w:tr>.*?</w:tr>',
                                  table, flags=re.DOTALL)
                require(rows, "empty_table")
                for row in rows:
                    cells = re.findall(r'<w:tc>.*?</w:tc>',
                                       row, flags=re.DOTALL)
                    require(len(cells) == len(widths[i]),
                            "unexpected_table_column_count")
                    updated_row = row
                    for col, cell in enumerate(cells):
                        require('<w:tcPr />' in cell,
                                "unexpected_pandoc_cell_properties")
                        replacement = cell.replace(
                            '<w:tcPr />',
                            f'<w:tcPr><w:tcW w:w="{widths[i][col]}" '
                            'w:type="dxa" /></w:tcPr>', 1)
                        if i in (0, 1):
                            replacement = re.sub(
                                r'<w:r>.*?</w:r>',
                                lambda r: font_size(r.group(0), 18),
                                replacement, flags=re.DOTALL)
                        if i == 1:
                            require('<w:pPr>' in replacement and
                                    '<w:spacing ' not in replacement,
                                    "table2_unexpected_cell_paragraph_format")
                            replacement = replacement.replace(
                                '</w:pPr>',
                                '<w:spacing w:before="0" w:after="0" '
                                'w:line="221" w:lineRule="auto" /></w:pPr>')
                        updated_row = updated_row.replace(cell, replacement, 1)
                    if i == 1:
                        if '<w:trPr>' in updated_row:
                            updated_row = updated_row.replace(
                                '<w:trPr>', '<w:trPr><w:cantSplit />', 1)
                        else:
                            updated_row = updated_row.replace(
                                '<w:tr>',
                                '<w:tr><w:trPr><w:cantSplit /></w:trPr>', 1)
                    if i == 4 and row != rows[-1]:
                        require('<w:keepNext' not in updated_row and
                                '<w:p><w:pPr>' in updated_row,
                                "table5_unexpected_keep_together_structure")
                        # Let Word keep Table 5 with its caption when space is
                        # insufficient; no hard-coded page break or text edit.
                        updated_row = updated_row.replace(
                            '<w:p><w:pPr>',
                            '<w:p><w:pPr><w:keepNext />')
                    table = table.replace(row, updated_row, 1)
                return table
            xml = re.sub(r'<w:tbl>.*?</w:tbl>', table_edit,
                         xml, flags=re.DOTALL)
            require(index[0] == 5, "expected_five_word_tables")
            # Image bytes unchanged; apply accessibility metadata in DrawingML.
            props = re.findall(r'<wp:docPr\\b[^>]*/>', xml)
            require(len(props) == 1 and 'descr=""' in props[0] and 'title=""' in props[0],
                    "expected_one_unannotated_figure_drawing")
            require('"' not in FIGURE_ALT and '&' not in FIGURE_ALT and
                    '"' not in FIGURE_ALT_TITLE and '&' not in FIGURE_ALT_TITLE,
                    "figure_alt_xml_escape_required")
            modified = props[0].replace('descr=""', 'descr="' + FIGURE_ALT + '"', 1)
            modified = modified.replace('title=""', 'title="' + FIGURE_ALT_TITLE + '"', 1)
            xml = xml.replace(props[0], modified, 1)
            require(xml.count('descr="' + FIGURE_ALT + '"') == 1 and
                    xml.count('title="' + FIGURE_ALT_TITLE + '"') == 1,
                    "figure_alt_text_not_inserted_once")
            data = xml.encode("utf-8")
        output.append((info, data))
    with tempfile.NamedTemporaryFile(prefix="ceas-layout-", suffix=".docx",
                                     delete=False, dir=str(doc.parent)) as tmp:
        staged = Path(tmp.name)
    try:
        with ZipFile(staged, "w") as dest:
            for info, data in output:
                dest.writestr(info, data)
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
    require(FIGURE.is_file(),"ceas_authorized_figure_derivative_missing")
    require(IMAGE_REL==str(FIGURE.relative_to(SOURCE.parent)),"figure_path_and_markdown_reference_diverged")
    require(SOURCE.read_text(encoding="utf-8").count("![]("+IMAGE_REL+")")==1,
            "approved_figure_reference_not_exactly_once")
    if a.check:
        print("CEAS_FIGURE_SOURCE_BINDING=PASS")
        print("CEAS_PACKAGE_RENDER=NOT_EXECUTED")
        return
    require(a.out_dir is not None,"external_out_dir_required")
    out=Path(a.out_dir).expanduser().resolve()
    require(not out.exists(),"refuse_existing_output_directory")
    require(ROOT != out and ROOT not in out.parents,"refuse_repository_output")
    require(shutil.which("pandoc") is not None,"pandoc_required")
    require(find_soffice() is not None,"libreoffice_required_for_pdf")
    require(FIGURE.is_file(),"ceas_authorized_figure_derivative_missing")
    try:import cairosvg
    except ImportError:raise SystemExit("PAPER2_CEAS_PACKAGE_HOLD=python_cairosvg_required")
    content=SOURCE.read_text(encoding="utf-8")
    require(IMAGE_REL in content,"expected_approved_figure_reference_missing")
    require(IMAGE_REL==str(FIGURE.relative_to(SOURCE.parent)),"figure_path_and_markdown_reference_diverged")
    require(content.count("![]("+IMAGE_REL+")")==1,"figure_reference_not_exactly_once")
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
        with __import__("zipfile").ZipFile(doc, "r") as checked:
            word_xml = checked.read("word/document.xml").decode("utf-8")
            require(word_xml.count('descr="' + FIGURE_ALT + '"') == 1 and
                    word_xml.count('title="' + FIGURE_ALT_TITLE + '"') == 1,
                    "figure_accessibility_not_verified_in_docx")
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
                "ceas_figure1_svg_sha256":hash_file(FIGURE),
                "corresponding_email_author_confirmed":"aman.singh2406@live.com",
                "figure1_word_alt_text":FIGURE_ALT,
                "figure1_word_accessibility_qa":"PASS_DOCX_OOXML",
                "figure1_author_approved_for_draft_integration":True,
                "previous_visual_qa_not_transferable":True,
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
