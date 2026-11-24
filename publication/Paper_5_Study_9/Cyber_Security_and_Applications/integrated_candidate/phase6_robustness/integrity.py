"""Fixed-path integrity and materialization checks; no evaluator or selector execution."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
LIMIT=2_000_000
FILES={"runtime_inputs.json","reference_expectations.json","routing_manifest.json","selector_pinned.py"}
def safe_read(name):
    if name not in FILES|{"MATERIALIZATION_MANIFEST.json"}:raise ValueError("PATH_NOT_ALLOWLISTED")
    p=HERE/name
    if p.is_symlink() or not p.is_file() or p.resolve().parent!=HERE or p.stat().st_size>LIMIT:raise ValueError("UNSAFE_INPUT")
    return p.read_bytes()
def digest(b):return hashlib.sha256(b).hexdigest()
def read_verified(name):
    m=json.loads(safe_read("MATERIALIZATION_MANIFEST.json"))
    if set(m["files"])!=FILES or name not in FILES:raise ValueError("MANIFEST_FILE_SET")
    b=safe_read(name)
    if digest(b)!=m["files"][name]:raise ValueError("DIGEST_MISMATCH:"+name)
    return b
def verify_all():
    for name in sorted(FILES):read_verified(name)
    m=json.loads(safe_read("MATERIALIZATION_MANIFEST.json"))
    if m["frozen_payload"]!="b61eacc4c9791c2767bb3699597e51db2ee13592" or m["execution_authorized"] is not False:raise ValueError("AUTHORIZATION_OR_PAYLOAD_DRIFT")
    if digest(read_verified("selector_pinned.py"))!="3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505":raise ValueError("SELECTOR_SHA_MISMATCH")
    return m
