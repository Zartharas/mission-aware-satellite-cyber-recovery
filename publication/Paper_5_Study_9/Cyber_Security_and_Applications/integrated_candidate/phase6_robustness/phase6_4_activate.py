"""Single authorized Phase 6.4 attempt. No automatic execution, reruns, pulls or publication."""
import argparse, hashlib, json, os, re, shutil, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PREFLIGHT_HEAD="d2bcaf82e08b751f7e49332e489d96f749cbdd14"
GATE5_SHA="4d3e5218a1477860067bdc30d32cb9f32d0743f394674b2c1f7260195b4664b6"
AUTH_NAME="PHASE6_4_SINGLE_ATTEMPT_AUTHORIZATION.json"
ATTEMPT_ID="P5_PHASE6_4_CANONICAL_ATTEMPT_001"
PREFLIGHT_HASHES={"attempt.json":"bb82d96be7a9708d32b55f4cb4c16caa7e4d7568e5982431df29b5780f6c92be","report.json":"79b431e88e48dc34123ebfd7f841e8cae6f6e1e8cbc288f6e75948bb608d1bb9","SHA256_MANIFEST.json":"e93ef23e9093f833201dd867d80b510763e227630ada2fcea90115446f55bf6f"}
def require(ok,reason):
    if not ok:raise ValueError(reason)
def digest(p):
    require(p.is_file() and not p.is_symlink(),"MISSING_OR_UNSAFE_FILE:"+p.name)
    return hashlib.sha256(p.read_bytes()).hexdigest()
def verified_gate5():
    require(sys.flags.isolated and sys.dont_write_bytecode and not sys.flags.optimize,"USE_PYTHON_I_B")
    require(digest(HERE/"gate5_launcher.py")==GATE5_SHA,"GATE5_LAUNCHER_DRIFT")
    sys.path.insert(0,str(HERE))
    import gate5_launcher as g
    return g
def check_authorization(g):
    a=g.decode(g.read(HERE/AUTH_NAME))
    require(a["record"]=="PAPER5_PHASE6_4_SINGLE_ATTEMPT_AUTHORIZATION" and a["attempt_id"]==ATTEMPT_ID and a["preflight_head"]==PREFLIGHT_HEAD and a["qualified_payload"]==g.QUALIFIED and a["launcher_sha256"]==GATE5_SHA and a["preflight_evidence_sha256"]==PREFLIGHT_HASHES,"AUTHORIZATION_DRIFT")
    require(a["governance"]=={"canonical_execution_authorized_conditionally":True,"canonical_execution_performed":False,"automatic_rerun":False,"original_data_access":False,"protocol_change":False,"merge":False,"publication":False,"submission":False},"AUTHORIZATION_SCOPE_DRIFT")
    require(a["design"]=={"controls":72,"mapping":64,"ledger":8,"metamorphic_groups":17,"transformed_evaluations":25,"logical_endpoints":78732},"AUTHORIZATION_DESIGN_DRIFT")
    require(a["ci"]==[{"id":45306612104,"conclusion":"success"},{"id":45306612083,"conclusion":"success"},{"id":45306612258,"conclusion":"success"}],"AUTHORIZATION_CI_DRIFT")
    return a
def check_preflight(g,work,static):
    directory=work/"gate5_local_preflight_001"
    require(directory.is_dir() and not directory.is_symlink(),"PREFLIGHT_DIRECTORY_MISSING")
    actual={n:digest(directory/n) for n in PREFLIGHT_HASHES}
    require(actual==PREFLIGHT_HASHES,"PREFLIGHT_EVIDENCE_DRIFT")
    a=g.decode(g.read(directory/"attempt.json"));r=g.decode(g.read(directory/"report.json"));m=g.decode(g.read(directory/"SHA256_MANIFEST.json"))
    require(a=={"canonical_execution_authorized":False,"checkout":PREFLIGHT_HEAD,"scope":"PHASE6_3_1_GATE5_LOCAL_PREFLIGHT"},"PREFLIGHT_ATTEMPT_DRIFT")
    require(r["status"]==m["status"]=="PASS" and r["checkout"]==PREFLIGHT_HEAD and r["canonical_execution"] is False and r["scope"]=="READ_ONLY_PREFLIGHT_NO_SCIENTIFIC_EXECUTION","PREFLIGHT_SCOPE_DRIFT")
    require(m["files"]=={n:actual[n] for n in ("attempt.json","report.json")},"PREFLIGHT_MANIFEST_DRIFT")
    for key,value in static.items():
        if key!="checkout":require(r[key]==value,"PREFLIGHT_STATIC_MISMATCH:"+key)
    return actual,r
def validate(expected_head):
    g=verified_gate5()
    a=check_authorization(g)
    m,static=g.static_preflight(expected_head)
    return g,a,m,static
def execute(expected_head,work,offline_confirmed):
    require(offline_confirmed,"OFFLINE_OPERATOR_CONFIRMATION_REQUIRED")
    work=Path(work).resolve()
    require(work.is_dir() and (work/"repo").resolve() in HERE.parents,"WORK_DIRECTORY_MISMATCH")
    require(not (work/ATTEMPT_ID).exists() and not (work/ATTEMPT_ID).is_symlink(),"ATTEMPT_ALREADY_EXISTS_NO_RERUN")
    g,a,m,static=validate(expected_head)
    from evidence_writer import preserve_attempt
    from datetime import datetime,timezone
    meta={"scope":"PHASE6_4_CANONICAL_SYNTHETIC_ONLY","attempt_id":ATTEMPT_ID,"canonical_execution_authorized":True,"checkout":expected_head,"preflight_head":PREFLIGHT_HEAD,"qualified_payload":g.QUALIFIED,"activation_sha256":digest(Path(__file__).resolve()),"authorization_sha256":digest(HERE/AUTH_NAME),"offline_operator_confirmed":True,"started_utc":datetime.now(timezone.utc).isoformat()}
    def operation(progress):
        progress.update(static)
        progress["canonical_execution"]=False
        progress["stage"]="PRE_EXECUTION_CHECKS"
        hashes,preflight=check_preflight(g,work,static)
        require(not (work/"runtime_qualification_attempt_003").is_symlink(),"QUALIFICATION_DIRECTORY_SYMLINK")
        qhash,report=g.local_evidence(m,work/"runtime_qualification_attempt_003")
        environment=g.check_environment(m,report)
        require(environment==preflight["environment"],"ENVIRONMENT_PREFLIGHT_DRIFT")
        progress["preflight_evidence_sha256"]=hashes
        progress["qualification_evidence_sha256"]=qhash
        progress["environment"]=environment
        require(shutil.disk_usage(work).free>=256*1024*1024,"INSUFFICIENT_OUTPUT_SPACE")
        progress["stage"]="CANONICAL_SCIENTIFIC_EXECUTION"
        progress["canonical_execution"]=True
        # The qualified candidate worker performs its isolation checks before input.
        # No canonical call occurs until all preceding checks pass.
        g._dormant_scientific_operation(m["runtime"]["image"],progress,static["archived_F0_reference"])
        progress["stage"]="COMPLETE"
    return preserve_attempt(work/ATTEMPT_ID,meta,operation)
def main():
    p=argparse.ArgumentParser()
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate-only",action="store_true")
    modes.add_argument("--execute-once",action="store_true")
    p.add_argument("--expected-head",required=True)
    p.add_argument("--work")
    p.add_argument("--offline-confirmed",action="store_true")
    args=p.parse_args()
    if args.validate_only:
        validate(args.expected_head)
        print("PHASE6_4_ACTIVATION_STATIC_PASS_NO_EXECUTION")
        return 0
    require(args.work is not None,"WORK_REQUIRED")
    status=execute(args.expected_head,args.work,args.offline_confirmed)
    print("PHASE6_4_CANONICAL_"+status)
    return 0 if status=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
