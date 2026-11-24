"""Gate 5 non-study tests. No scientific evaluator, selector, or model calls."""
import sys,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import gate5_launcher as g
def main():
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HERE,text=True).strip()
    m,r=g.static_preflight(head)
    assert len(r["qualified_file_sha256"])==18 and r["canonical_execution"] is False
    assert set(r["archived_F0_reference"])==set(g.POLICIES)
    # Fabricated comparison rows using archived reference as a schema-level positive control;
    # no evaluation, no selector invocation, no scientific state enumeration.
    rows=[]
    for policy,entry in r["archived_F0_reference"].items():
        rows.append({"model":"F0","policy":policy,"observation":[None]*8,**entry})
    assert g.compare_f0(rows,r["archived_F0_reference"])
    altered=[dict(x) for x in rows];altered[0]["actions"]=["TOY_WRONG"]
    try:g.compare_f0(altered,r["archived_F0_reference"])
    except ValueError:pass
    else:raise AssertionError("ARCHIVE_ACTION_MUTATION_ACCEPTED")
    altered=[dict(x) for x in rows];altered[0]["minima"]=[[99]]
    try:g.compare_f0(altered,r["archived_F0_reference"])
    except ValueError:pass
    else:raise AssertionError("ARCHIVE_MINIMA_MUTATION_ACCEPTED")
    try:g.static_preflight("0"*40)
    except ValueError:pass
    else:raise AssertionError("WRONG_HEAD_ACCEPTED")
    with tempfile.TemporaryDirectory() as directory:
        try:g.local_evidence(m,directory)
        except ValueError:pass
        else:raise AssertionError("MISSING_LOCAL_EVIDENCE_ACCEPTED")
    p=subprocess.run([sys.executable,"-I","-B",str(HERE/"gate5_launcher.py"),"--execute"],capture_output=True,text=True)
    assert p.returncode!=0 and "PHASE6_4_EXECUTION_NOT_AUTHORIZED" in p.stderr
    assert "runner" not in sys.modules and "selector_pinned" not in sys.modules and "evaluator" not in sys.modules
    print("PHASE6_3_1_GATE5_ENGINEERING_PASS_NO_CANONICAL_EXECUTION")
if __name__=="__main__":main()
