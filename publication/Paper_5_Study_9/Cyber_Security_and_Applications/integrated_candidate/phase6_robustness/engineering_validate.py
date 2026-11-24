"""Engineering-only integrity, syntax and toy checks. Does not evaluate frozen cases or models."""
import ast, hashlib, json, subprocess, sys
from pathlib import Path
from integrity import HERE, verify_all, read_verified
def canon(obj):
    return (json.dumps(obj,ensure_ascii=True,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
def blob(b):return hashlib.sha1(("blob %d\0"%len(b)).encode()+b).hexdigest()
def main():
    m=verify_all()
    root=HERE.parent
    receipt=json.loads((root/"PHASE6_2_IMMUTABLE_PROTOCOL_FREEZE_RECEIPT.json").read_bytes())
    for entry in receipt["frozen_payload"]["files"]:
        p=root/Path(entry["path"]).name
        if p.is_symlink() or blob(p.read_bytes())!=entry["git_blob_sha1"]:raise ValueError("FROZEN_DESIGN_DRIFT")
    spec=json.loads((root/"PHASE6_1_CONTROL_INPUT_SPEC_CANDIDATE.json").read_bytes())
    gold=json.loads((root/"PHASE6_1_CONTROL_EXPECTATIONS_CANDIDATE.json").read_bytes())
    manifest=json.loads((root/"PHASE6_1_CANDIDATE_PROTOCOL_MANIFEST.json").read_bytes())
    assert len(spec["inputs"])==len(gold["expected"])==72
    cases=[];refs=[];routes=[]
    for idx,(a,b) in enumerate(zip(spec["inputs"],gold["expected"]),1):
        assert a["case_id"]==b["case_id"]
        key=f"R{idx:03d}"
        cases.append({"routing_key":key,"payload":{k:v for k,v in a.items() if k not in ("case_id","family")}})
        refs.append({"routing_key":key,"expectation":{k:v for k,v in b.items() if k!="case_id"}})
        routes.append({"routing_key":key,"case_id":a["case_id"],"family":a["family"]})
    assert len({r["case_id"] for r in routes})==72
    assert canon({"status":"FROZEN_DESIGN_MATERIALIZED_NOT_EXECUTED","cases":cases})==read_verified("runtime_inputs.json")
    assert canon({"status":"PRESPECIFIED_NOT_OBSERVED","rows":refs})==read_verified("reference_expectations.json")
    assert canon({"cases":routes,"perturbations":manifest["cases"]["perturbations"]})==read_verified("routing_manifest.json")
    for name in ("evaluator.py","reference_oracle.py","state_model.py","runner.py","integrity.py","selector_pinned.py","candidate_worker.py","isolated_worker.py","evidence_writer.py","engineering_mutations.py"):
        ast.parse((HERE/name).read_text(),filename=name)
    # No scientific-case calls. Tiny non-study truth tables exercise algorithms only.
    from state_model import partition_minima,endpoint
    from reference_oracle import conflict_minima
    states=[(False,False),(False,True),(True,False),(True,True)]
    actions=["left","left","right","right"]
    assert partition_minima(states,actions,(0,1))==[(0,)]
    assert conflict_minima(states,actions,(0,1))==[(0,)]
    assert partition_minima([],[],(0,1)) is None and conflict_minima([],[],(0,1)) is None
    assert endpoint([],[],(None,None))["min_size"] is None
    assert partition_minima(states,["same"]*4,(0,1))==[()]
    assert conflict_minima(states,["same"]*4,(0,1))==[()]
    from evaluator import integer
    assert integer(0) and not integer(True) and not integer(-1) and not integer(0,1)
    p=subprocess.run([sys.executable,"-B",str(HERE/"runner.py")],capture_output=True,text=True,timeout=10)
    assert p.returncode!=0 and "PHASE6_4_EXECUTION_NOT_AUTHORIZED" in p.stderr
    from engineering_mutations import run
    run()
    print("PHASE6_3_ENGINEERING_ONLY_PASS_NO_CANONICAL_EXECUTION")
if __name__=="__main__":main()
