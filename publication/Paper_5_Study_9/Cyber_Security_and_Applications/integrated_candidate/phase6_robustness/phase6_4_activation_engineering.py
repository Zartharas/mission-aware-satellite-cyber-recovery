"""Exercise activation control boundaries, never canonical inputs or scientific calls."""
import subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import phase6_4_activate as a
def main():
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HERE,text=True).strip()
    g,auth,m,static=a.validate(head)
    assert static["canonical_execution"] is False
    assert auth["governance"]["automatic_rerun"] is False
    for f in (lambda:a.execute(head,"/nonexistent",False),lambda:a.validate("0"*40)):
        try:f()
        except ValueError:pass
        else:raise AssertionError("UNSAFE_ACTIVATION_ACCEPTED")
    with tempfile.TemporaryDirectory() as tmp:
        try:a.check_preflight(g,Path(tmp),static)
        except ValueError:pass
        else:raise AssertionError("MISSING_PREFLIGHT_ACCEPTED")
    assert "runner" not in sys.modules and "evaluator" not in sys.modules and "selector_pinned" not in sys.modules
    print("PHASE6_4_ACTIVATION_ENGINEERING_PASS_NO_CANONICAL_EXECUTION")
if __name__=="__main__":main()
