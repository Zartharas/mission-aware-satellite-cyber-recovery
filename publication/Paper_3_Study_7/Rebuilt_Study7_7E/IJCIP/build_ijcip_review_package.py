#!/usr/bin/env python3
"""Review-only Paper 3 DOCX/PDF export; never submits or re-runs science."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import cairosvg

AREA = Path(__file__).resolve().parent
REPO = AREA.parents[3]
OUT = REPO / "artifacts/paper3_ijcip_review_only"

def run(args):
    subprocess.run(args, check=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    for exe in ("pandoc", "libreoffice", "pdftotext", "pdfinfo"):
        if shutil.which(exe) is None:
            raise RuntimeError("Missing export executable: " + exe)
    source = AREA / "PAPER3_IJCIP_MANUSCRIPT_R3.md"
    manuscript = source.read_text(encoding="utf-8")
    if manuscript.count("## Abstract\n") != 1 or not manuscript.startswith("# "):
        raise AssertionError("invalid source structure")
    body = manuscript.splitlines()[0] + "\n\n## Abstract\n" + manuscript.split("## Abstract\n",1)[1]
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        (tmp / "figures").mkdir()
        for name in ("PAPER3_IJCIP_FIG1_ARCHITECTURE", "PAPER3_IJCIP_FIG2_ENDPOINTS"):
            svg = AREA / "figures" / (name + ".svg")
            png = tmp / "figures" / (name + ".png")
            cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=2400)
            shutil.copyfile(png, OUT / (name + "_REVIEW.png"))
            body = body.replace("figures/" + name + ".svg", "figures/" + name + ".png")
        markdown = tmp / "manuscript.md"
        markdown.write_text(body, encoding="utf-8")
        docx = OUT / "PAPER3_IJCIP_MANUSCRIPT_REVIEW_ONLY.docx"
        run(["pandoc","--from=gfm","--to=docx","--standalone","--resource-path",str(tmp),"-o",str(docx),str(markdown)])
        for filename,outname,fmt in (
            ("IJCIP_COVER_LETTER_AUTHOR_REVIEW_DRAFT_2026-10-20.md","IJCIP_COVER_LETTER_REVIEW_ONLY.docx","gfm"),
            ("IJCIP_HIGHLIGHTS_R1.txt","IJCIP_HIGHLIGHTS_REVIEW_ONLY.docx","markdown")
        ):
            run(["pandoc","-f",fmt,"-t","docx","--standalone","-o",str(OUT/outname),str(AREA/filename)])
        meta = (AREA/"IJCIP_SUBMISSION_METADATA_DRAFT.md").read_text(encoding="utf-8")
        title = tmp/"title.md"
        title.write_text("# Author details — author verification only\n\n"+meta+"\n",encoding="utf-8")
        run(["pandoc","-f","gfm","-t","docx","--standalone","-o",str(OUT/"IJCIP_TITLE_PAGE_REVIEW_ONLY.docx"),str(title)])
        run(["libreoffice","-env:UserInstallation="+(tmp/"lo_profile").as_uri(),"--headless","--convert-to","pdf","--outdir",str(OUT),str(docx)])
        pdf = OUT/"PAPER3_IJCIP_MANUSCRIPT_REVIEW_ONLY.pdf"
        if not pdf.is_file() or pdf.stat().st_size<5000:
            raise AssertionError("no PDF")
        extract=tmp/"check.txt"
        run(["pdftotext","-layout",str(pdf),str(extract)])
        readback=extract.read_text(encoding="utf-8")
        for term in ("196","784","F12","C0","References"):
            if term not in readback:
                raise AssertionError("PDF missing text: "+term)
        run(["pdfinfo",str(pdf)])
        receipt={"status":"REVIEW_ONLY_NOT_PUBLISHER_READY","source_sha256":digest(source),
                 "source_head":os.environ.get("PAPER3_SOURCE_HEAD","NOT_BOUND"),
                 "new_experiment":False,"journal_specific_rules_verified":False,
                 "author_confirmation":False,"visual_qa":False,"artifacts":{}}
        for artifact in sorted(OUT.iterdir()):
            if artifact.is_file() and artifact.name!="REVIEW_ONLY_SHA256_MANIFEST.json":
                receipt["artifacts"][artifact.name]={"sha256":digest(artifact),"bytes":artifact.stat().st_size}
        (OUT/"REVIEW_ONLY_SHA256_MANIFEST.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("PAPER3_IJCIP_SOURCE_TO_WORD_AND_PDF=PASS_REVIEW_ONLY")
    print("PAPER3_IJCIP_SUBMISSION_AUTHORIZED=NO")

if __name__=="__main__":
    main()
