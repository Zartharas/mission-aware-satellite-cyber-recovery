"""Gate 5 preflight and dormant Phase 6.4 adapter. No execution CLI until explicit authorization.

Only standard-library imports before integrity checks. Run with python3 -I -B.
Static preflight hashes existing data; it never calls evaluator, selector or model enumeration.
"""
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL="publication/Paper_5_Study_9/Cyber_Security_and_Applications/integrated_candidate/phase6_robustness"
MANIFEST="PHASE6_3_1_QUALIFIED_IMPLEMENTATION_AND_ENVIRONMENT_MANIFEST.json"
MANIFEST_BLOB="0d91f0c0f9d9c099d1d380998d4608217ed1102b"
QUALIFIED="23e36944b03c6b45e2bf6c0eda0bdb480d03e3d5"
FREEZE_RECEIPT="PHASE6_2_IMMUTABLE_PROTOCOL_FREEZE_RECEIPT.json"
ARCHIVE="study9/results/S9-RTSI-001_CANONICAL_RUN_20260914"
ARCHIVE_PINS={"policy_strata.json":"44509b11c481f5d6b38a37df1e5cacac4638576a","guaranteed_sidecar.json":"78bdbf8aae88c3095b1bf15d10bbaca6f31ce544"}
POLICIES=("S2_B0_FAIL_CLOSED","S2_B1_FAIL_OPERATIONAL","S2_B2_RISK_THRESHOLD","S2_S1_EVIDENCE_AWARE")
FIELDS=("signature_valid","source_trusted","fresh","epoch_valid","contradictory","minimum_evidence_complete","security_signal","authorization_available")

def require(condition,reason):
    if not condition:raise ValueError(reason)

def read(path):
    require(not path.is_symlink() and path.is_file() and path.stat().st_size<=2_000_000,"UNSAFE_OR_MISSING_FILE:"+path.name)
    return path.read_bytes()

def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(("blob %d\0"%len(b)).encode()+b).hexdigest()
def decode(b):
    def pairs(items):
        out={}
        for k,v in items:
            require(k not in out,"DUPLICATE_JSON_KEY")
            out[k]=v
        return out
    def bad(v):raise ValueError("NONFINITE_JSON_NUMBER")
    return json.loads(b,object_pairs_hook=pairs,parse_constant=bad)
def cmd(args,cwd=None):
    env=dict(os.environ,GIT_NO_LAZY_FETCH="1",GIT_OPTIONAL_LOCKS="0")
    return subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=45,check=True).stdout.strip()

def safe_path(root,relative):
    p=root/relative
    require(not Path(relative).is_absolute() and ".." not in Path(relative).parts,"UNSAFE_RELATIVE_PATH")
    require(p.resolve()==p and root in p.parents,"SYMLINK_OR_PATH_ESCAPE")
    return p

def compare_archive(policy_bytes,sidecar_bytes):
    # Read-only reconciliation of historical reference sets, not selector execution.
    p=decode(policy_bytes)["datasets"];s=decode(sidecar_bytes)["datasets"]
    require(len(p)==len(s)==3,"ARCHIVE_DATASET_COUNT")
    require({x["dataset_id"] for x in p}=={x["dataset_id"] for x in s}=={"CUCD_ID_V3","AEGISSAT_2025","UNSW_IOTSAT_2026"},"ARCHIVE_DATASET_IDS")
    expected={}
    for dataset in p:
        match=[x for x in s if x["dataset_id"]==dataset["dataset_id"]]
        require(len(match)==1 and dataset["native_state_group_count"]==1,"ARCHIVE_GROUP_COUNT")
        require(len(dataset["policy_strata"])==len(match[0]["policy_strata"])==4,"ARCHIVE_POLICY_COUNT")
        require({x["policy"] for x in dataset["policy_strata"]}=={x["policy"] for x in match[0]["policy_strata"]}==set(POLICIES),"ARCHIVE_POLICY_IDS")
        for row in dataset["policy_strata"]:
            policy=row["policy"];other=[x for x in match[0]["policy_strata"] if x["policy"]==policy]
            require(len(other)==1 and len(row["group_results"])==len(other[0]["groups"])==1,"ARCHIVE_STRATUM_COUNT")
            a=row["group_results"][0];b=other[0]["groups"][0]
            require(a["group_index"]==b["group_index"]==0 and a["guaranteed_sidecar_sets"]==b["guaranteed_sidecar_sets"] and a["guaranteed_sidecar_cardinality"]==b["guaranteed_sidecar_cardinality"],"ARCHIVE_SIDECAR_DISAGREEMENT")
            entry={"actions":sorted(a["reachable_actions"]),"minima":sorted([sorted(FIELDS.index(field) for field in subset) for subset in a["guaranteed_sidecar_sets"]]),"min_size":a["guaranteed_sidecar_cardinality"],"action_count":a["action_set_cardinality"]}
            require(len(entry["actions"])==entry["action_count"] and all(len(x)==entry["min_size"] for x in entry["minima"]),"ARCHIVE_CARDINALITY")
            if policy in expected:require(expected[policy]==entry,"ARCHIVE_DATASET_DISAGREEMENT")
            expected[policy]=entry
    return expected

def static_preflight(expected_head):
    require(sys.flags.isolated and sys.dont_write_bytecode and sys.flags.optimize==0,"USE_PYTHON_ISOLATED_NO_BYTECODE_NO_OPTIMIZATION")
    require(re.fullmatch(r"[0-9a-f]{40}",expected_head) is not None,"FULL_HEAD_REQUIRED")
    root=Path(cmd(["git","rev-parse","--show-toplevel"],HERE)).resolve()
    require(HERE==root/REL,"WRONG_REPOSITORY_PATH")
    require(cmd(["git","rev-parse","HEAD"],root)==expected_head,"CHECKOUT_HEAD_DRIFT")
    require(not cmd(["git","status","--porcelain","--untracked-files=all"],root),"DIRTY_CHECKOUT")
    # Reject ignored extra files and stale pyc inside the implementation directory.
    tracked=set(cmd(["git","ls-tree","--name-only",expected_head+":"+REL],root).splitlines())
    require(set(x.name for x in HERE.iterdir())==tracked,"IMPLEMENTATION_DIRECTORY_DRIFT")
    require(all(x.is_file() and not x.is_symlink() for x in HERE.iterdir()),"UNEXPECTED_IMPLEMENTATION_ENTRY")
    raw=read(HERE/MANIFEST);require(blob(raw)==MANIFEST_BLOB,"QUALIFICATION_RECEIPT_DRIFT")
    m=decode(raw)
    require(m["status"]=="QUALIFIED_PAYLOAD_PINNED_EXECUTION_HOLD" and m["governance"]["canonical_execution_authorized"] is False and m["qualified_payload"]["commit"]==QUALIFIED,"QUALIFICATION_STATUS_DRIFT")
    require(len(m["qualified_payload"]["files"])==18 and len(m["frozen_design"]["files"])==5,"PIN_COUNT_DRIFT")
    checked={}
    for entry in m["qualified_payload"]["files"]:
        path=safe_path(root,entry["path"]);data=read(path)
        require(path.parent==HERE and blob(data)==entry["git_blob_sha1"] and sha(data)==entry["sha256"],"QUALIFIED_FILE_DRIFT:"+path.name)
        require(path.name not in checked,"DUPLICATE_FILE_PIN")
        checked[path.name]=sha(data)
    require(len(checked)==18,"QUALIFIED_PIN_COUNT")
    for entry in m["frozen_design"]["files"]:
        path=safe_path(root,entry["path"])
        require(path.parent==HERE.parent and blob(read(path))==entry["git_blob_sha1"],"FROZEN_DESIGN_DRIFT:"+path.name)
    require(blob(read(HERE.parent/FREEZE_RECEIPT))==m["frozen_design"]["receipt_blob"],"FREEZE_RECEIPT_DRIFT")
    archives={}
    for n,pin in ARCHIVE_PINS.items():
        data=read(safe_path(root,ARCHIVE+"/"+n))
        require(blob(data)==pin,"HISTORICAL_REFERENCE_DRIFT:"+n)
        archives[n]=data
    expected=compare_archive(archives["policy_strata.json"],archives["guaranteed_sidecar.json"])
    # Static routing/count checks only, no candidate calls.
    inputs=decode(read(HERE/"runtime_inputs.json"))["cases"]
    refs=decode(read(HERE/"reference_expectations.json"))["rows"]
    routes=decode(read(HERE/"routing_manifest.json"))
    ids=[x["routing_key"] for x in inputs]
    require(len(ids)==len(set(ids))==len(refs)==len(routes["cases"])==72,"ROUTING_COUNT_DRIFT")
    require(ids==[x["routing_key"] for x in refs]==[x["routing_key"] for x in routes["cases"]],"ROUTING_ALIGNMENT_DRIFT")
    require(sum(x["payload"]["target"] is None for x in inputs)==8 and len(routes["perturbations"])==17,"ENDPOINT_COUNT_DRIFT")
    mapping=[x["expectation"] for x in refs if "diagnostics" not in x["expectation"]]
    require(len(mapping)==64 and sum(x["admission"]=="ADMIT" for x in mapping)==23,"REFERENCE_DENOMINATOR_DRIFT")
    result={"checkout":expected_head,"qualified_payload":QUALIFIED,"qualification_manifest_sha256":sha(raw),"launcher_sha256":sha(read(Path(__file__).resolve())),"qualified_file_sha256":checked,"frozen_design_count":5,"archive_sha256":{k:sha(v) for k,v in archives.items()},"archived_F0_reference":expected,"canonical_execution":False}
    return m,result

def local_evidence(m,evidence):
    evidence=Path(evidence).resolve()
    attempt=[x for x in m["attempt_evidence"] if x["attempt"]==3]
    require(len(attempt)==1 and attempt[0]["status"]=="PASS","QUALIFICATION_ATTEMPT_DRIFT")
    data={n:read(evidence/n) for n in ("attempt.json","report.json","SHA256_MANIFEST.json")}
    hashes={n:sha(b) for n,b in data.items()}
    require(hashes==attempt[0]["sha256"],"LOCAL_EVIDENCE_DIGEST_DRIFT")
    a=decode(data["attempt.json"]);report=decode(data["report.json"]);manifest=decode(data["SHA256_MANIFEST.json"])
    require(a["canonical_execution_authorized"] is False and report["canonical_execution"] is False and report["status"]==manifest["status"]=="PASS","LOCAL_EVIDENCE_SCOPE_DRIFT")
    require(manifest["files"]=={n:hashes[n] for n in ("attempt.json","report.json")},"LOCAL_EVIDENCE_MANIFEST_DRIFT")
    return hashes,report

def check_environment(m,report):
    runtime=m["runtime"];image=runtime["image"]
    require(not os.environ.get("DOCKER_HOST") and not os.environ.get("DOCKER_CONTEXT"),"DOCKER_ENV_OVERRIDE")
    require(sys.version==report["environment"]["host_python"] and platform.platform()==report["environment"]["host"],"HOST_ENVIRONMENT_DRIFT")
    require(cmd(["docker","context","show"])==runtime["docker_context"],"DOCKER_CONTEXT_DRIFT")
    context=decode(cmd(["docker","context","inspect"]).encode())[0]
    require(context["Name"]==runtime["docker_context"] and context["Endpoints"]["docker"]["Host"].startswith("unix://"),"NONLOCAL_DAEMON")
    meta=decode(cmd(["docker","image","inspect",image]).encode())[0]
    require(image in meta.get("RepoDigests",[]) and meta["Id"]==runtime["image_id"] and meta["Os"]+"/"+meta["Architecture"]==runtime["platform"],"IMAGE_DRIFT")
    version=decode(cmd(["docker","version","--format","{{json .}}"]).encode())
    require(version==report["environment"]["docker_version"],"DOCKER_VERSION_DRIFT")
    return {"image":image,"image_id":meta["Id"],"platform":runtime["platform"],"docker_context":context["Name"],"docker_client":version["Client"]["Version"],"docker_server":version["Server"]["Version"],"kernel":version["Server"]["KernelVersion"],"host_python":sys.version,"host":platform.platform()}

def local_preflight(expected_head,evidence,output):
    m,result=static_preflight(expected_head)
    require(Path(output).resolve().parent!=HERE and HERE not in Path(output).resolve().parents,"OUTPUT_INSIDE_IMPLEMENTATION")
    sys.path.insert(0,str(HERE))
    from evidence_writer import preserve_attempt
    def operation(progress):
        progress.update(result)
        hashes,report=local_evidence(m,evidence)
        progress["qualification_evidence_sha256"]=hashes
        progress["environment"]=check_environment(m,report)
        progress["scope"]="READ_ONLY_PREFLIGHT_NO_SCIENTIFIC_EXECUTION"
    return preserve_attempt(output,{"scope":"PHASE6_3_1_GATE5_LOCAL_PREFLIGHT","canonical_execution_authorized":False,"checkout":expected_head},operation)

def compare_f0(records,expected):
    rows=[x for x in records if x["model"]=="F0" and all(v is None for v in x["observation"])]
    require(len(rows)==4 and {x["policy"] for x in rows}==set(POLICIES),"F0_REFERENCE_ROW_COUNT")
    for row in rows:
        e=expected[row["policy"]]
        a={"actions":sorted(row["actions"]),"minima":sorted([sorted(s) for s in row["minima"]]),"min_size":row["min_size"],"action_count":row["action_count"]}
        require(a==e,"ARCHIVED_F0_EXACT_SET_MISMATCH:"+row["policy"])
    return True

def _dormant_scientific_operation(image,progress,archived_reference):
    """Future separately approved wrapper only. NEVER called by preflight or current CLI."""
    import runner
    report=runner.prepare_analysis(image,progress)
    progress["mapping_report"]=report
    require(len(report["rows"])==72 and len(report["metamorphic"])==17 and sum(len(x["observed"]) for x in report["metamorphic"])==25,"ENDPOINT_COMPLETENESS_FAILURE")
    require(not report["failures"],"SEMANTIC_CONTROL_OR_ORACLE_FAILURE")
    rows=runner.logical_analysis(progress)
    require(len(rows)==78732,"LOGICAL_ROW_COUNT_MISMATCH")
    progress["archived_F0_exact_match"]=compare_f0(rows,archived_reference)

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--static-preflight",action="store_true")
    mode.add_argument("--local-preflight",action="store_true")
    mode.add_argument("--execute",action="store_true")
    ap.add_argument("--expected-head")
    ap.add_argument("--qualification-evidence")
    ap.add_argument("--output")
    args=ap.parse_args()
    if args.execute:raise SystemExit("PHASE6_4_EXECUTION_NOT_AUTHORIZED")
    require(args.expected_head is not None,"EXPECTED_HEAD_REQUIRED")
    if args.static_preflight:
        _,result=static_preflight(args.expected_head)
        print(json.dumps(result,sort_keys=True))
        print("PHASE6_3_1_GATE5_STATIC_PREFLIGHT_PASS_NO_EXECUTION")
        return 0
    require(args.qualification_evidence and args.output,"LOCAL_PREFLIGHT_ARGUMENTS_REQUIRED")
    status=local_preflight(args.expected_head,args.qualification_evidence,args.output)
    print("PHASE6_3_1_GATE5_LOCAL_PREFLIGHT_"+status)
    return 0 if status=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
