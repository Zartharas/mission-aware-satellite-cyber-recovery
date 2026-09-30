#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from study6x.audit.reference_gate_evaluator import evaluate_gate_reference
from study6x.runtime.gate_evaluator import SIGNALS

def digest(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--run-dir",required=True); args=ap.parse_args()
    root=Path(args.run_dir); obs=root/"S6X_GATE_OBSERVATIONS_002.csv"
    summary=root/"S6X_SUMMARY_002.json"; evidence=root/"S6X_EVIDENCE_RECORDS_002.json"
    rows=list(csv.DictReader(obs.open(encoding="utf-8")))
    if len(rows)!=396: raise SystemExit("observation count mismatch")
    a=[r for r in rows if r["block"]=="A_PAIRED_ARTIFACT_OBSERVABILITY"]
    b=[r for r in rows if r["block"]=="B_CLEAN_ARTIFACT_ASSURANCE_UNAVAILABILITY"]
    if len(a)!=12 or len(b)!=384: raise SystemExit("block count mismatch")
    mismatches=0
    for row in rows:
        e={name:row[name]=="1" for name in SIGNALS}
        if int(evaluate_gate_reference(row["gate"],e))!=int(row["reference_qualified"]): mismatches+=1
        if row["primary_qualified"]!=row["reference_qualified"]: mismatches+=1
    s=json.loads(summary.read_text())
    if s["primary_reference_gate_mismatches"]!=0 or mismatches!=0: raise SystemExit("gate evaluator mismatch")
    ev=json.loads(evidence.read_text())["records"]
    clean=next(x for x in ev if x["state_id"]=="CLEAN_APPROVED")
    bad=next(x for x in ev if x["state_id"]=="APPROVED_BAD_SOURCE")
    if not clean["objective_baseline_correct"] or bad["objective_baseline_correct"]:
        raise SystemExit("objective correctness polarity mismatch")
    names=["S6X_GATE_OBSERVATIONS_002.csv","S6X_SUMMARY_002.json","S6X_EVIDENCE_RECORDS_002.json"]
    hashes={name:digest(root/name) for name in names}
    vp=root/"S6X_INDEPENDENT_VALIDATION_002.json"
    vp.write_text(json.dumps({"schema":1,"experiment_id":"S6X-EAP-001","independent_validation":"PASS",
        "observations":396,"block_a_rows":12,"block_b_rows":384,"gate_mismatches":0,
        "result_freeze_authorized":False,"manuscript_claim_use_authorized":False,
        "artifacts":hashes},indent=2,sort_keys=True)+"\n")
    hashes[vp.name]=digest(vp)
    mp=root/"S6X_RESULTS_HASH_MANIFEST_002.json"
    mp.write_text(json.dumps({"schema":1,"experiment_id":"S6X-EAP-001","artifacts":hashes,
        "result_freeze_authorized":False,"manuscript_claim_use_authorized":False},
        indent=2,sort_keys=True)+"\n")
    print("S6X_INDEPENDENT_VALIDATION=PASS"); print("observations=396"); print("gate_mismatches=0")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
