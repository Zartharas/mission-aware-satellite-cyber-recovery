"""Non-study runtime qualification only. No import of scientific runner or gold."""
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys
from pathlib import Path
from isolated_worker import candidate_batch
from evidence_writer import preserve_attempt
from strict_json import equal
HERE=Path(__file__).resolve().parent
def call(cmd,progress=None,stage="COMMAND"):
    # Retain bounded subprocess diagnostics in local evidence before raising.
    # Do not include the full command or arbitrary environment variables.
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,errors="replace",timeout=45,check=False)
    except subprocess.TimeoutExpired as exc:
        if progress is not None:
            def bounded(value):
                if isinstance(value,bytes):value=value.decode("utf-8",errors="replace")
                return (value or "")[:8192]
            progress["command_failure"]={"stage":stage,"timeout":True,"stdout":bounded(exc.stdout),"stderr":bounded(exc.stderr)}
        raise RuntimeError(stage+"_TIMEOUT") from exc
    if result.returncode:
        if progress is not None:
            progress["command_failure"]={"stage":stage,"exit_code":result.returncode,"stdout":result.stdout[:8192],"stderr":result.stderr[:8192]}
        raise RuntimeError(stage+"_NONZERO_EXIT_"+str(result.returncode))
    return result.stdout
def qualification(image,progress):
    if not re.fullmatch(r"[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}",image):raise ValueError("PINNED_LOCAL_IMAGE_DIGEST_REQUIRED")
    if not shutil.which("docker"):raise ValueError("DOCKER_UNAVAILABLE")
    if os.environ.get("DOCKER_HOST"):raise ValueError("EXPLICIT_DOCKER_HOST_NOT_ALLOWED")
    ctx=json.loads(call(["docker","context","inspect"],progress,"DOCKER_CONTEXT"))
    if not ctx[0]["Endpoints"]["docker"]["Host"].startswith("unix://"):raise ValueError("LOCAL_UNIX_DAEMON_REQUIRED")
    meta=json.loads(call(["docker","image","inspect",image],progress,"IMAGE_INSPECT"))[0]
    if image not in (meta.get("RepoDigests") or []):raise ValueError("IMAGE_DIGEST_NOT_VERIFIED")
    progress["environment"]={"image":image,"image_id":meta["Id"],"os":meta["Os"],"architecture":meta["Architecture"],"docker_version":json.loads(call(["docker","version","--format","{{json .}}"],progress,"DOCKER_VERSION")),"host":platform.platform(),"host_python":sys.version,"docker_context":ctx[0]["Name"],"endpoint_type":"local_unix"}
    if meta["Os"]!="linux":raise ValueError("LINUX_IMAGE_REQUIRED")
    script=(HERE/"network_isolation.py").read_text()+"\nimport json\nprint(json.dumps(verify_isolation(),sort_keys=True))\n"
    raw=call(["docker","run","--rm","--pull","never","--network","none","--read-only","--cap-drop","ALL","--security-opt","no-new-privileges","--pids-limit","32","--memory","128m","--cpus","1","--user","65534:65534","--entrypoint","python3",image,"-B","-S","-c",script],progress,"ISOLATION_PROBE")
    progress["isolation_probe"]=json.loads(raw)
    context=dict(subject="QUAL_TOY",decision_id="TOY_9",decision_time_s=31,epoch=3,clock="TOY_CLOCK",snapshot_id="TOY_SNAPSHOT",source_id="TOY_ISSUER",evidence_id="TOY_EVIDENCE")
    descriptor=dict(name="toy_membership",meaning="Membership of the evidence source in the current verifier trusted-source set.",authority="TRUST_REGISTRY",visibility="OPERATIONAL_NATIVE",subject_scope=context["subject"],decision_scope=context["decision_id"],clock_scope=context["clock"],source_scope=context["source_id"],evidence_scope=context["evidence_id"],domain="BOOLEAN_LITERAL",native_field=True)
    def payload(v):return dict(target="source_trusted",schema=[descriptor],record=dict(context=context,values={"toy_membership":v}),requested_context=context)
    batch=candidate_batch(image,[payload(False),payload(True),payload(1)])
    progress["toy_worker_response"]=batch
    if batch["error"] is not None or not equal([(x["admission"],x["value"]) for x in batch["results"]],[("ADMIT",False),("ADMIT",True),("REJECT_INVALID",None)]):raise ValueError("TOY_WORKER_MISMATCH")
    progress["implementation_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}
    progress["canonical_execution"]=False
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--image",required=True);ap.add_argument("--output",required=True);args=ap.parse_args()
    status=preserve_attempt(args.output,{"scope":"PHASE6_3_1_NON_STUDY_RUNTIME_QUALIFICATION","canonical_execution_authorized":False},lambda p:qualification(args.image,p))
    print("PHASE6_3_1_RUNTIME_"+status)
    raise SystemExit(0 if status=="PASS" else 1)
