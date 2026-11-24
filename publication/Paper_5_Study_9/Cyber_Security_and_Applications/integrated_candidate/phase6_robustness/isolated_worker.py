"""Prepared local Docker worker isolation. No container is launched by import or engineering CI."""
import json, os, re, shutil, subprocess, tempfile
from pathlib import Path
from integrity import HERE
def candidate_batch(image,payloads):
    if not re.fullmatch(r"[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}",image):
        raise ValueError("PINNED_LOCAL_IMAGE_DIGEST_REQUIRED")
    docker=shutil.which("docker")
    if not docker:raise ValueError("LOCAL_DOCKER_UNAVAILABLE")
    raw=json.dumps(payloads,allow_nan=False,separators=(",",":")).encode()
    if len(raw)>2_000_000:raise ValueError("INPUT_SIZE_LIMIT")
    # Only two code files in this read-only mount; no gold, routing, telemetry or Docker socket.
    with tempfile.TemporaryDirectory(prefix="p5-p6-worker-") as tmp:
        os.chmod(tmp,0o755)
        for name in ("candidate_worker.py","evaluator.py"):
            src=HERE/name
            if src.is_symlink() or not src.is_file():raise ValueError("INVALID_WORKER_SOURCE")
            dest=Path(tmp)/name;shutil.copyfile(src,dest);os.chmod(dest,0o444)
        cmd=[docker,"run","--rm","--pull","never","--network","none","--read-only","--cap-drop","ALL",
             "--security-opt","no-new-privileges","--pids-limit","32","--memory","128m","--cpus","1",
             "--user","65534:65534","--mount",f"type=bind,src={tmp},dst=/app,readonly",
             "--workdir","/app","--entrypoint","python3","-i",image,"-B","-S","/app/candidate_worker.py"]
        p=subprocess.run(cmd,input=raw,capture_output=True,timeout=120,check=False)
        if p.returncode or len(p.stdout)>2_000_000:
            raise RuntimeError("ISOLATED_WORKER_FAILURE:"+str(p.returncode)+":"+p.stderr.decode(errors="replace")[:300])
        out=json.loads(p.stdout)
        if set(out)!={"results","error"} or type(out["results"]) is not list or len(out["results"])>len(payloads):
            raise ValueError("INVALID_WORKER_RESPONSE")
        if out["error"] is None and len(out["results"])!=len(payloads):raise ValueError("INCOMPLETE_WORKER_RESPONSE")
        return out
