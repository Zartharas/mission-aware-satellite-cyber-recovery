"""Non-study runtime qualification only. No import of scientific runner or gold."""
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys
from pathlib import Path
from isolated_worker import candidate_batch
from evidence_writer import preserve_attempt
from strict_json import equal
HERE=Path(__file__).resolve().parent
def call(cmd):
    return subprocess.run(cmd,capture_output=True,text=True,timeout=45,check=True).stdout
def qualification(image,progress):
    if not re.fullmatch(r"[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}",image):raise ValueError("PINNED_LOCAL_IMAGE_DIGEST_REQUIRED")
    if not shutil.which("docker"):raise ValueError("DOCKER_UNAVAILABLE")
    if os.environ.get("DOCKER_HOST"):raise ValueError("EXPLICIT_DOCKER_HOST_NOT_ALLOWED")
    ctx=json.loads(call(["docker","context","inspect"]))
    if not ctx[0]["Endpoints"]["docker"]["Host"].startswith("unix://"):raise ValueError("LOCAL_UNIX_DAEMON_REQUIRED")
    meta=json.loads(call(["docker","image","inspect",image]))[0]
    if image not in (meta.get("RepoDigests") or []):raise ValueError("IMAGE_DIGEST_NOT_VERIFIED")
    progress["environment"]={"image":image,"image_id":meta["Id"],"os":meta["Os"],"architecture":meta["Architecture"],"docker_version":json.loads(call(["docker","version","--format","{{json .}}"])),"host":platform.platform(),"host_python":sys.version,"docker_context":ctx[0]["Name"],"endpoint_type":"local_unix"}
    if meta["Os"]!="linux":raise ValueError("LINUX_IMAGE_REQUIRED")
    script="import os,sys,json\nassert os.getuid()==65534\nassert not os.path.exists('/var/run/docker.sock')\nassert not os.path.exists('/app/reference_expectations.json')\nassert not os.path.exists('/app/runtime_inputs.json')\ntry:\n open('/qualification_probe','w').close()\nexcept OSError: pass\nelse: raise AssertionError('root filesystem writable')\nassert set(os.listdir('/sys/class/net')) <= {'lo'}\nprint(json.dumps({'uid':os.getuid(),'interfaces':os.listdir('/sys/class/net'),'python':sys.version,'readonly':True}))"
    raw=call(["docker","run","--rm","--pull","never","--network","none","--read-only","--cap-drop","ALL","--security-opt","no-new-privileges","--pids-limit","32","--memory","128m","--cpus","1","--user","65534:65534","--entrypoint","python3",image,"-B","-S","-c",script])
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
