#!/usr/bin/env python3
from __future__ import annotations

import argparse, base64, hashlib, importlib.metadata, json, platform, sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

from study7e.feasibility.qualifier_fault.qualifier_fault_model import Evidence, PathState, QualifierContext, qualify_stream
from study7e.src.aerc_design import BASE_FEATURES, EXTENDED_FEATURES, affected_paths, build_scenario_manifest, d0_base, d1_corroborated, domain_map, objective_action

EID="S7E-AERC-001"; FID="S7E-AERC-FREEZE-001"; MFID="S7E-AERC-MODEL-FREEZE-001"
PID="S7E-AERC-HELDOUT-PLAN-001"; AID="S7E-AERC-HELDOUT-AUTH-001"; XID="S7E-AERC-HELDOUT-EXEC-001"
HELD={"E1","E2","C0"}; POLICIES=("D0_BASE","L0_BASE","D1_CORROBORATED","L1_CORROBORATED")
AUTH=ROOT/"study7e/HELD_OUT_EVALUATION_AUTHORIZATION.json"
PLAN=ROOT/"study7e/configs/held_out_evaluation_plan_001.json"
FREEZE=ROOT/"study7e/FREEZE_MANIFEST_001.json"
MF=ROOT/"study7e/MODEL_FREEZE_MANIFEST_001.json"
FROZEN=ROOT/"study7e/frozen_models/S7E-AERC-MODEL-FREEZE-001"

def cj(x:object)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def fhash(p:Path)->str:return h(p.read_bytes())

def registry(labels:Iterable[str],ns:str)->dict[str,int]:
    used=set(); out={}
    for label in sorted(set(labels)):
        retry=0
        while True:
            v=int.from_bytes(hashlib.sha256(f"{EID}|{ns}|{label}|{retry}".encode()).digest()[:4],"big")
            if v and v not in used: used.add(v); out[label]=v; break
            retry+=1
    return out

def registries()->dict[str,dict[str,int]]:
    manifest=build_scenario_manifest(); aliases={ns:set() for ns in ("source","key","authority")}
    for r in manifest:
        m=domain_map(r.topology)
        for path in ("primary","corroborator"):
            for ns in aliases: aliases[ns].add(m[path][ns])
    return {"scenario":registry((r.scenario_id for r in manifest),"scenario"),**{ns:registry(v,ns) for ns,v in aliases.items()}}

def context(sid:int,epoch:int,tick:int,max_age:int,path:str,source:int,key:int)->QualifierContext:
    return QualifierContext(sid,epoch,tick,max_age,{path:frozenset({source})},{path:frozenset({key})})

def held_rows()->list[Any]:
    rows=[r for r in build_scenario_manifest() if r.block in HELD]
    order={"E1":0,"E2":1,"C0":2}
    rows.sort(key=lambda r:(order[r.block],int(r.scenario_id.rsplit("-",1)[1])))
    counts={b:sum(r.block==b for r in rows) for b in ("E1","E2","C0")}
    if counts!={"E1":84,"E2":104,"C0":8} or len(rows)!=196: raise RuntimeError(f"held-out cardinality drift: {counts}")
    return rows

def nominal(path:str,s:Any,regs:dict[str,dict[str,int]],p:dict[str,Any])->Evidence:
    aliases=domain_map(s.topology); sid=regs["scenario"][s.scenario_id]
    return Evidence(path,sid,path,int(s.true_authorization),regs["source"][aliases[path]["source"]],regs["authority"][aliases[path]["authority"]],regs["key"][aliases[path]["key"]],int(p["evidence_epoch"]),int(p["nominal_issue_tick"]),1,1,True)

def materialize_snapshot(s:Any,regs:dict[str,dict[str,int]],p:dict[str,Any])->tuple[dict[str,int],dict[str,Any]]:
    affected=set(affected_paths(s.topology,s.fault_profile)); streams={path:[nominal(path,s,regs,p)] for path in ("primary","corroborator")}
    ticks={path:int(p["nominal_evaluation_tick"]) for path in streams}
    fp=s.fault_profile
    if fp in {"F1","F2","F3","F4","F10"}:
        for path in affected: streams[path]=[replace(streams[path][0],authorization=1-int(s.true_authorization))]
    elif fp in {"F5","F6"}:
        for path in affected: ticks[path]=int(p["stale_fault_evaluation_tick"])
    elif fp in {"F7","F8"}:
        for path in affected: streams[path]=[]
    elif fp=="F9":
        for path in affected: streams[path]=[replace(streams[path][0],epoch=int(p["evidence_epoch"])^1,signature_valid=0)]
    elif fp=="F11":
        for path in affected: streams[path]=[replace(streams[path][0],authorization=1-int(s.true_authorization),epoch=int(p["evidence_epoch"])^1,signature_valid=0)]
    elif fp=="F12":
        for path in affected:
            first=streams[path][0]; streams[path]=[first,replace(first,authorization=1-int(s.true_authorization))]
    elif fp!="F0": raise KeyError(fp)

    observed=set()
    for path in ("primary","corroborator"):
        if streams[path]!=[nominal(path,s,regs,p)] or ticks[path]!=int(p["nominal_evaluation_tick"]): observed.add(path)
    if observed!=affected: raise RuntimeError(f"fault instrumentation mismatch {s.scenario_id}: expected={sorted(affected)} observed={sorted(observed)}")

    q={}
    aliases=domain_map(s.topology); sid=regs["scenario"][s.scenario_id]
    for path in ("primary","corroborator"):
        src=regs["source"][aliases[path]["source"]]; key=regs["key"][aliases[path]["key"]]
        q[path],_=qualify_stream(streams[path],context(sid,int(p["evidence_epoch"]),ticks[path],int(p["freshness_max_age_ticks"]),path,src,key),PathState())
    snap={
      "primary_signature_valid":q["primary"]["signature_valid"],"primary_source_trusted":q["primary"]["source_trusted"],
      "primary_fresh":q["primary"]["fresh"],"primary_epoch_valid":q["primary"]["epoch_valid"],
      "primary_noncontradictory":q["primary"]["noncontradictory"],"primary_complete":q["primary"]["complete"],
      "primary_authorization":q["primary"]["authorization"],"health_ready":int(s.true_health_ready),"security_signal":int(s.security_signal),
      "corr_signature_valid":q["corroborator"]["signature_valid"],"corr_source_trusted":q["corroborator"]["source_trusted"],
      "corr_fresh":q["corroborator"]["fresh"],"corr_epoch_valid":q["corroborator"]["epoch_valid"],
      "corr_noncontradictory":q["corroborator"]["noncontradictory"],"corr_complete":q["corroborator"]["complete"],
      "corr_authorization":q["corroborator"]["authorization"]
    }
    if tuple(snap)!=EXTENDED_FEATURES: raise RuntimeError("feature order/schema drift")
    return snap,{"affected_paths":sorted(affected),"observed_changed_paths":sorted(observed),"fault_confirmation":True,"domain_alias_map_sha256":h(cj(domain_map(s.topology)))}

def decode_frozen_model(policy:str,out:Path,manifest:dict[str,Any])->Path:
    info=manifest["preservation"]["runtime_artifacts"][policy]; src=ROOT/info["path"]
    raw=base64.b64decode("".join(src.read_text().split()),validate=True)
    if h(raw)!=info["decoded_sha256"]: raise RuntimeError(f"{policy} frozen runtime hash mismatch")
    p=out/f"{policy}.joblib"; p.write_bytes(raw); return p

def validate_environment(manifest:dict[str,Any])->dict[str,str]:
    dep=FROZEN/"dependency_inventory.json"
    if fhash(dep)!=manifest["runtime_binding"]["dependency_inventory_sha256"]: raise RuntimeError("frozen dependency inventory hash mismatch")
    d=load(dep); expected=d["required_versions"]; actual={k:importlib.metadata.version(k) for k in expected}
    if platform.python_version()!=manifest["runtime_binding"]["python"]: raise RuntimeError("python version drift")
    if actual!=expected: raise RuntimeError(f"dependency version drift expected={expected} actual={actual}")
    return actual

def semantic(policy:str,manifest:dict[str,Any])->dict[str,Any]:
    info=manifest["authoritative_semantic_identity"][policy]; p=ROOT/info["path"]; obj=load(p)
    if h(cj(obj))!=info["sha256"]: raise RuntimeError(f"{policy} semantic hash mismatch")
    return obj

def semantic_predict(model:dict[str,Any],vector:tuple[int,...])->str:
    t=model["tree"]; node=0
    feat=t["feature"]["values"]; left=t["children_left"]["values"]; right=t["children_right"]["values"]; thr=t["threshold"]["values"]
    while int(feat[node])>=0:
        threshold=float.fromhex(thr[node]) if isinstance(thr[node],str) else float(thr[node])
        node=int(left[node]) if vector[int(feat[node])]<=threshold else int(right[node])
    vals=t["value"]["values"]; n=len(model["classes"]["values"]); start=node*n
    scores=[float.fromhex(v) if isinstance(v,str) else float(v) for v in vals[start:start+n]]
    idx=max(range(n),key=lambda i:(scores[i],-i))
    return str(model["classes"]["values"][idx])

def audit_d0(v:tuple[int,...])->str:
    ok=all(v[i]==1 for i in range(6)) and v[6]==v[7]==v[8]==1
    return "ENTER_RECOVERY_GATE" if ok else "HOLD"

def audit_d1(v:tuple[int,...])->str:
    ok=all(v[i]==1 for i in range(6)) and v[6]==v[7]==v[8]==1 and all(v[i]==1 for i in range(9,15)) and v[15]==1
    return "ENTER_RECOVERY_GATE" if ok else "HOLD"

def counts(records:list[dict[str,Any]])->dict[str,Any]:
    n=len(records); enter=sum(r["action"]=="ENTER_RECOVERY_GATE" for r in records); err=sum(r["action"]!=r["objective_action"] for r in records)
    unsafe=sum(r["action"]=="ENTER_RECOVERY_GATE" and r["objective_action"]=="HOLD" for r in records)
    cons=sum(r["action"]=="HOLD" and r["objective_action"]=="ENTER_RECOVERY_GATE" for r in records)
    return {"n":n,"objective_decision_error":err,"unsafe_proceed":unsafe,"false_conservative_hold":cons,"actions":{"HOLD":n-enter,"ENTER_RECOVERY_GATE":enter}}

def write_json(p:Path,x:object)->None:p.write_bytes(cj(x)+b"\n")
def write_jsonl(p:Path,rows:list[dict[str,Any]])->None:p.write_bytes(b"".join(cj(r)+b"\n" for r in rows))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--source-commit",required=True); args=ap.parse_args()
    auth,plan,freeze,mf=load(AUTH),load(PLAN),load(FREEZE),load(MF)
    if auth["state"]!="AUTHORIZED_FOR_EXACT_HELD_OUT_SCIENTIFIC_EVALUATION_ONLY" or auth["execution_id"]!=XID or auth["plan_id"]!=PID: raise RuntimeError("held-out authorization identity/state mismatch")
    if not all(auth["prohibited"].values()): raise RuntimeError("authorization prohibitions incomplete")
    if plan["state"]!="PLAN_QUALIFIED_GREEN__HELD_OUT_INFERENCE_NOT_AUTHORIZED": raise RuntimeError("qualified plan historical state drift")
    if mf["model_freeze_id"]!=MFID or not mf["safety"]["production_models_frozen"]: raise RuntimeError("model freeze inactive")

    rows=held_rows(); manifest_rows=[{"scenario_id":s.scenario_id,"block":s.block,"true_authorization":s.true_authorization,"true_health_ready":s.true_health_ready,"security_signal":s.security_signal,"topology":s.topology,"fault_profile":s.fault_profile} for s in rows]
    manifest_bytes=b"".join(cj(r)+b"\n" for r in manifest_rows); manifest_sha=h(manifest_bytes)

    args.output_dir.mkdir(parents=True,exist_ok=False)
    for d in ("heldout","runtime_models"): (args.output_dir/d).mkdir()
    versions=validate_environment(mf)
    execution_manifest={"schema":1,"experiment_id":EID,"execution_id":XID,"authorization_id":AID,"plan_id":PID,"protocol_freeze_id":FID,"model_freeze_id":MFID,"source_commit":args.source_commit,"scenario_manifest_sha256":manifest_sha,"scenario_counts":{"E1":84,"E2":104,"C0":8,"TOTAL":196},"expected_policy_decisions":784,"policy_order":list(POLICIES),"model_semantic_sha256":{k:v["sha256"] for k,v in mf["authoritative_semantic_identity"].items()},"model_runtime_sha256":{k:v["decoded_sha256"] for k,v in mf["preservation"]["runtime_artifacts"].items()},"dependency_versions":versions,"pre_inference_binding_complete":True}
    write_json(args.output_dir/"heldout/execution_manifest.json",execution_manifest)

    l0p=decode_frozen_model("L0_BASE",args.output_dir/"runtime_models",mf); l1p=decode_frozen_model("L1_CORROBORATED",args.output_dir/"runtime_models",mf)
    import joblib
    l0=joblib.load(l0p); l1=joblib.load(l1p)
    s0=semantic("L0_BASE",mf); s1=semantic("L1_CORROBORATED",mf)
    regs=registries(); params=freeze["frozen_execution_parameters"]

    scenarios=[]; decisions=[]; invalid=[]; input_hashes={}
    for attempt,s in enumerate(rows,1):
        snap,instr=materialize_snapshot(s,regs,params)
        base=tuple(int(snap[x]) for x in BASE_FEATURES); ext=tuple(int(snap[x]) for x in EXTENDED_FEATURES)
        bb=json.dumps(base,separators=(",",":")).encode(); eb=json.dumps(ext,separators=(",",":")).encode()
        bh,eh=h(bb),h(eb); input_hashes[s.scenario_id]={"base_input_sha256":bh,"extended_input_sha256":eh}
        primary={"D0_BASE":d0_base(base),"L0_BASE":str(l0.predict([list(base)])[0]),"D1_CORROBORATED":d1_corroborated(ext),"L1_CORROBORATED":str(l1.predict([list(ext)])[0])}
        audits={"D0_BASE":audit_d0(base),"L0_BASE":semantic_predict(s0,base),"D1_CORROBORATED":audit_d1(ext),"L1_CORROBORATED":semantic_predict(s1,ext)}
        obj=objective_action(s); reasons=[]
        if not instr["fault_confirmation"]: reasons.append("fault_not_confirmed")
        if primary["L0_BASE"]!=audits["L0_BASE"]: reasons.append("L0_audit_mismatch")
        if primary["L1_CORROBORATED"]!=audits["L1_CORROBORATED"]: reasons.append("L1_audit_mismatch")
        if primary["D0_BASE"]!=audits["D0_BASE"]: reasons.append("D0_audit_mismatch")
        if primary["D1_CORROBORATED"]!=audits["D1_CORROBORATED"]: reasons.append("D1_audit_mismatch")
        valid=not reasons
        for policy in POLICIES:
            ph=bh if policy in {"D0_BASE","L0_BASE"} else eh
            decisions.append({"execution_id":XID,"attempt_id":attempt,"scenario_id":s.scenario_id,"block":s.block,"policy_id":policy,"policy_input_sha256":ph,"action":primary[policy],"audit_action":audits[policy],"audit_match":primary[policy]==audits[policy],"objective_action":obj,"true_authorization":s.true_authorization,"true_health_ready":s.true_health_ready,"security_signal":s.security_signal,"topology":s.topology,"fault_profile":s.fault_profile,"valid":valid,"invalid_reason":";".join(reasons)})
        scenarios.append({"execution_id":XID,"attempt_id":attempt,"scenario_id":s.scenario_id,"block":s.block,"topology":s.topology,"fault_profile":s.fault_profile,"domain_alias_map_sha256":instr["domain_alias_map_sha256"],"fault_confirmation":instr["fault_confirmation"],"base_input_sha256":bh,"extended_input_sha256":eh,"four_decisions_present":True,"valid":valid,"invalid_reason":";".join(reasons)})
        if not valid: invalid.append(scenarios[-1])

    write_jsonl(args.output_dir/"heldout/scenario_attempts.jsonl",scenarios); write_jsonl(args.output_dir/"heldout/policy_decisions.jsonl",decisions); write_jsonl(args.output_dir/"heldout/invalid_attempts.jsonl",invalid)
    write_json(args.output_dir/"heldout/input_hash_manifest.json",{"schema":1,"execution_id":XID,"scenario_manifest_sha256":manifest_sha,"inputs":input_hashes})
    write_json(args.output_dir/"heldout/model_and_environment_binding.json",{"schema":1,"model_freeze_id":MFID,"runtime_sha256":{k:v["decoded_sha256"] for k,v in mf["preservation"]["runtime_artifacts"].items()},"semantic_sha256":{k:v["sha256"] for k,v in mf["authoritative_semantic_identity"].items()},"dependency_inventory_sha256":mf["runtime_binding"]["dependency_inventory_sha256"],"actual_required_versions":versions})

    if len(scenarios)!=196 or len(decisions)!=784: raise RuntimeError("output cardinality drift")
    if invalid: raise RuntimeError(f"invalid scenarios present: {len(invalid)}")

    endpoint={"schema":1,"execution_id":XID,"population":{"scenarios":196,"decisions":784},"by_block":{},"overall":{}}
    for block in ("E1","E2","C0"):
        endpoint["by_block"][block]={p:counts([r for r in decisions if r["block"]==block and r["policy_id"]==p]) for p in POLICIES}
    endpoint["overall"]={p:counts([r for r in decisions if r["policy_id"]==p]) for p in POLICIES}
    endpoint["corroboration_deltas"]={}
    for scope in ("E1","E2","C0","ALL"):
        src=endpoint["overall"] if scope=="ALL" else endpoint["by_block"][scope]
        endpoint["corroboration_deltas"][scope]={
          "deterministic_D1_minus_D0":{"unsafe_proceed":src["D1_CORROBORATED"]["unsafe_proceed"]-src["D0_BASE"]["unsafe_proceed"],"false_conservative_hold":src["D1_CORROBORATED"]["false_conservative_hold"]-src["D0_BASE"]["false_conservative_hold"]},
          "learned_L1_minus_L0":{"unsafe_proceed":src["L1_CORROBORATED"]["unsafe_proceed"]-src["L0_BASE"]["unsafe_proceed"],"false_conservative_hold":src["L1_CORROBORATED"]["false_conservative_hold"]-src["L0_BASE"]["false_conservative_hold"]}
        }
    write_json(args.output_dir/"heldout/exact_endpoint_counts.json",endpoint)

    table={}
    for top in ("T0_SHARED_ALL","T1_SEPARATE_SOURCE_EXEC","T2_SEPARATE_SOURCE_KEY_EXEC","T3_SEPARATE_THROUGH_TRANSPORT","T4_SEPARATE_ALL"):
        table[top]={}
        faults=sorted({r["fault_profile"] for r in decisions if r["topology"]==top},key=lambda x:int(x[1:]))
        for fault in faults: table[top][fault]={p:counts([r for r in decisions if r["topology"]==top and r["fault_profile"]==fault and r["policy_id"]==p]) for p in POLICIES}
    common={}
    for p in POLICIES:
        common[p]={}
        for top in table:
            rs=[r for r in decisions if r["policy_id"]==p and r["topology"]==top and r["fault_profile"] in {"F6","F7","F8","F9","F10","F11","F12"}]
            if rs: common[p][top]=counts(rs)
        base=common[p]["T0_SHARED_ALL"]
        common[p]["delta_vs_T0"]={top:{"unsafe_proceed":v["unsafe_proceed"]-base["unsafe_proceed"],"false_conservative_hold":v["false_conservative_hold"]-base["false_conservative_hold"]} for top,v in common[p].items() if top!="T0_SHARED_ALL"}
    commoncause={p:{top:{f:counts([r for r in decisions if r["policy_id"]==p and r["topology"]==top and r["fault_profile"]==f]) for f in ("F10","F11")} for top in table} for p in POLICIES}
    write_json(args.output_dir/"heldout/topology_fault_tables.json",{"schema":1,"execution_id":XID,"by_topology_fault":table,"common_fault_subset_F6_F12_by_topology":common,"common_cause_F10_F11":commoncause})

    pd={"schema":1,"execution_id":XID,"pairs":{}}
    for pair,a,b in (("D0_vs_L0","D0_BASE","L0_BASE"),("D1_vs_L1","D1_CORROBORATED","L1_CORROBORATED")):
        pd["pairs"][pair]={}
        for scope in ("E1","E2","C0","ALL"):
            sids=[s.scenario_id for s in rows if scope=="ALL" or s.block==scope]; disagree=[]
            for sid in sids:
                x=next(r for r in decisions if r["scenario_id"]==sid and r["policy_id"]==a)["action"]; y=next(r for r in decisions if r["scenario_id"]==sid and r["policy_id"]==b)["action"]
                if x!=y: disagree.append(sid)
            pd["pairs"][pair][scope]={"n":len(sids),"disagreement_count":len(disagree),"scenario_ids":disagree}
    write_json(args.output_dir/"heldout/paired_disagreements.json",pd)
    write_json(args.output_dir/"heldout/audit_reconciliation.json",{"schema":1,"execution_id":XID,"policy_decisions":784,"audit_matches":sum(r["audit_match"] for r in decisions),"audit_mismatches":sum(not r["audit_match"] for r in decisions),"invalid_scenarios":0,"all_actions_reconciled":all(r["audit_match"] for r in decisions)})

    files=[p for p in sorted((args.output_dir/"heldout").glob("*")) if p.is_file() and p.name!="output_hash_manifest.json"]
    hashes={p.name:fhash(p) for p in files}
    write_json(args.output_dir/"heldout/output_hash_manifest.json",{"schema":1,"execution_id":XID,"files":hashes})

    print(f"scenario_manifest_sha256={manifest_sha}"); print("held_out_scenarios=196"); print("policy_decisions=784"); print("invalid_scenarios=0"); print("audit_mismatches=0")
    for p in POLICIES:
        c=endpoint["overall"][p]; print(f"{p}_objective_decision_error={c['objective_decision_error']}"); print(f"{p}_unsafe_proceed={c['unsafe_proceed']}"); print(f"{p}_false_conservative_hold={c['false_conservative_hold']}")
    print("held_out_evaluation_executed=true"); print("canonical_results_generated=true"); print("pr_merge_authorized=false"); print("publication_or_result_claims_authorized=false"); print("study7e_held_out_evaluation=PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
