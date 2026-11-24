"""Exclusive attempt directories and atomic result/failure evidence. No automatic execution."""
import hashlib,json,os
from pathlib import Path
def write_new(path,obj):
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    raw=(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    temp=path.with_name("."+path.name+".tmp")
    with temp.open("xb") as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    # Hard link provides no-overwrite atomic publication on the same filesystem.
    os.link(temp,path);temp.unlink()
    return hashlib.sha256(raw).hexdigest()
def preserve_attempt(output,run_metadata,operation):
    root=Path(output)
    root.mkdir(mode=0o700,parents=False,exist_ok=False)
    hashes={}
    hashes["attempt.json"]=write_new(root/"attempt.json",run_metadata)
    completed={}
    try:
        operation(completed)
        status="FAIL" if completed.get("failures") else "PASS"
    except (Exception, KeyboardInterrupt) as exc:
        status="FAIL"
        completed["failure"]={"type":type(exc).__name__,"reason":str(exc)[:500]}
    hashes["report.json"]=write_new(root/"report.json",{"status":status,**completed})
    write_new(root/"SHA256_MANIFEST.json",{"status":status,"files":hashes})
    return status
