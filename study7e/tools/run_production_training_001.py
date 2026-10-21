#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, importlib.metadata, json, platform, subprocess, sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study7e.feasibility.qualifier_fault.qualifier_fault_model import Evidence, PathState, QualifierContext, qualify_stream
from study7e.models.training_contracts import make_training_record, validate_training_partition
from study7e.src.aerc_design import BASE_FEATURES, EXTENDED_FEATURES, affected_paths, build_scenario_manifest, domain_map, objective_action

EID, FID, PID, AID = "S7E-AERC-001", "S7E-AERC-FREEZE-001", "S7E-AERC-TRAINPLAN-001", "S7E-AERC-TRAIN-AUTH-001"
CID = "S7E-AERC-MODEL-FREEZE-CANDIDATE-001"
TRAIN = {"TR0", "TR1"}
HELD = {"E1", "E2", "C0"}
AUTH = ROOT / "study7e/configs/production_training_authorization_001.json"
PLAN = ROOT / "study7e/configs/production_training_run_plan_001.json"
FREEZE = ROOT / "study7e/FREEZE_MANIFEST_001.json"
LEARNER = ROOT / "study7e/configs/frozen_learner_protocol_001.json"
REQ = {"pip", "numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl"}


def cj(x: object) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text())


def registry(labels: Iterable[str], ns: str) -> dict[str, int]:
    used, out = set(), {}
    for label in sorted(set(labels)):
        retry = 0
        while True:
            v = int.from_bytes(hashlib.sha256(f"{EID}|{ns}|{label}|{retry}".encode()).digest()[:4], "big")
            if v and v not in used:
                used.add(v); out[label] = v; break
            retry += 1
    return out


def registries() -> dict[str, dict[str, int]]:
    manifest = build_scenario_manifest()
    aliases = {ns: set() for ns in ("source", "key", "authority")}
    for r in manifest:
        m = domain_map(r.topology)
        for path in ("primary", "corroborator"):
            for ns in aliases:
                aliases[ns].add(m[path][ns])
    return {
        "scenario": registry((r.scenario_id for r in manifest), "scenario"),
        **{ns: registry(labels, ns) for ns, labels in aliases.items()},
    }


def context(sid: int, epoch: int, tick: int, max_age: int, path: str, source: int, key: int) -> QualifierContext:
    return QualifierContext(sid, epoch, tick, max_age, {path: frozenset({source})}, {path: frozenset({key})})


def snapshot(s: Any, regs: dict[str, dict[str, int]], p: dict[str, Any]) -> dict[str, int]:
    if s.block not in TRAIN or s.fault_profile not in {"F0","F1","F2","F3","F4","F5"}:
        raise ValueError("non-training scenario rejected")
    aliases, affected, sid = domain_map(s.topology), affected_paths(s.topology, s.fault_profile), regs["scenario"][s.scenario_id]
    q = {}
    for path in ("primary", "corroborator"):
        src = regs["source"][aliases[path]["source"]]
        key = regs["key"][aliases[path]["key"]]
        authority = regs["authority"][aliases[path]["authority"]]
        claim = int(s.true_authorization)
        if s.fault_profile in {"F1","F2","F3","F4"} and path in affected:
            claim = 1 - claim
        ev = Evidence(path, sid, path, claim, src, authority, key, int(p["evidence_epoch"]), int(p["nominal_issue_tick"]), 1, 1, True)
        tick = int(p["stale_fault_evaluation_tick"]) if s.fault_profile == "F5" and path in affected else int(p["nominal_evaluation_tick"])
        q[path], _ = qualify_stream([ev], context(sid, int(p["evidence_epoch"]), tick, int(p["freshness_max_age_ticks"]), path, src, key), PathState())
    out = {
        "primary_signature_valid": q["primary"]["signature_valid"], "primary_source_trusted": q["primary"]["source_trusted"],
        "primary_fresh": q["primary"]["fresh"], "primary_epoch_valid": q["primary"]["epoch_valid"],
        "primary_noncontradictory": q["primary"]["noncontradictory"], "primary_complete": q["primary"]["complete"],
        "primary_authorization": q["primary"]["authorization"], "health_ready": int(s.true_health_ready), "security_signal": int(s.security_signal),
        "corr_signature_valid": q["corroborator"]["signature_valid"], "corr_source_trusted": q["corroborator"]["source_trusted"],
        "corr_fresh": q["corroborator"]["fresh"], "corr_epoch_valid": q["corroborator"]["epoch_valid"],
        "corr_noncontradictory": q["corroborator"]["noncontradictory"], "corr_complete": q["corroborator"]["complete"],
        "corr_authorization": q["corroborator"]["authorization"],
    }
    if set(out) != set(EXTENDED_FEATURES):
        raise AssertionError("feature schema drift")
    return out


def training_rows() -> list[Any]:
    rows = [r for r in build_scenario_manifest() if r.block in TRAIN]
    rows.sort(key=lambda r: (0 if r.block == "TR0" else 1, int(r.scenario_id.rsplit("-",1)[1])))
    if len(rows) != 84 or any(r.block in HELD for r in rows):
        raise AssertionError("training partition drift")
    return rows


def datasets() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    p, regs = load(FREEZE)["frozen_execution_parameters"], registries()
    outs = {"L0_BASE": [], "L1_CORROBORATED": []}
    contracts = {"L0_BASE": [], "L1_CORROBORATED": []}
    for s in training_rows():
        snap, target = snapshot(s, regs, p), objective_action(s)
        for policy in outs:
            rec = make_training_record(policy_id=policy, scenario_id=s.scenario_id, block=s.block, snapshot=snap, target=target)
            contracts[policy].append(rec)
            outs[policy].append({"schema":1,"scenario_id":rec.scenario_id,"block":rec.block,"features":list(rec.features),"target":rec.target})
    for records in contracts.values():
        validate_training_partition(records)
    labels = {}
    for r in outs["L0_BASE"]:
        labels[r["target"]] = labels.get(r["target"], 0) + 1
    if labels != {"HOLD":66,"ENTER_RECOVERY_GATE":18}:
        raise AssertionError(f"label drift: {labels}")
    return outs["L0_BASE"], outs["L1_CORROBORATED"]


def jsonl(rows: list[dict[str, Any]]) -> bytes:
    return b"".join(cj(r)+b"\n" for r in rows)


def deps() -> dict[str, Any]:
    ds = sorted(({"name":(d.metadata.get("Name") or "").strip().lower(),"version":d.version} for d in importlib.metadata.distributions() if (d.metadata.get("Name") or "").strip()), key=lambda x:(x["name"],x["version"]))
    versions = {d["name"]:d["version"] for d in ds}
    missing = REQ - versions.keys()
    if missing:
        raise RuntimeError(f"missing dependencies: {sorted(missing)}")
    return {"schema":1,"python_version":platform.python_version(),"python_implementation":platform.python_implementation(),"platform":platform.platform(),"required_versions":{k:versions[k] for k in sorted(REQ)},"distributions":ds}


def arr(a: Any) -> dict[str, Any]:
    import numpy as np
    x=np.asarray(a)
    vals=[float(v).hex() for v in x.reshape(-1)] if x.dtype.kind=="f" else [int(v) if x.dtype.kind in "iub" else str(v) for v in x.reshape(-1)]
    return {"dtype":str(x.dtype),"shape":list(x.shape),"values":vals}


def sem(model: Any, policy: str, features: tuple[str,...]) -> bytes:
    t=model.tree_
    tree={k:arr(getattr(t,k)) for k in ("children_left","children_right","feature","threshold","impurity","n_node_samples","weighted_n_node_samples","value")}
    if hasattr(t,"missing_go_to_left"): tree["missing_go_to_left"]=arr(t.missing_go_to_left)
    return cj({"schema":1,"policy_id":policy,"algorithm":type(model).__name__,"feature_order":list(features),"classes":arr(model.classes_),"n_features_in":int(model.n_features_in_),"tree_meta":{"node_count":int(t.node_count),"capacity":int(t.capacity),"max_depth":int(t.max_depth)},"tree":tree})


def estimator(spec: dict[str, Any]) -> Any:
    from sklearn.tree import DecisionTreeClassifier
    return DecisionTreeClassifier(**dict(spec["hyperparameters"]))


def xy(rows: list[dict[str, Any]]) -> tuple[list[list[int]],list[str]]:
    return [r["features"] for r in rows],[r["target"] for r in rows]


def blob(path: Path) -> str:
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path.relative_to(ROOT).as_posix()}"],cwd=ROOT,text=True).strip()


def fhash(path: Path) -> str:
    return h(path.read_bytes())


def validate() -> dict[str, Any]:
    a,p,f,l=load(AUTH),load(PLAN),load(FREEZE),load(LEARNER)
    if (a["experiment_id"],a["freeze_id"],a["plan_id"],a["authorization_id"])!=(EID,FID,PID,AID) or a["state"]!="AUTHORIZED_FOR_DETERMINISTIC_PRODUCTION_TRAINING_ONLY":
        raise RuntimeError("authorization identity/state mismatch")
    if not all(a["authorized"].values()) or not all(a["not_authorized"].values()):
        raise RuntimeError("authorization scope incomplete")
    if p["plan_id"]!=PID or p["freeze_id"]!=FID or f["freeze_id"]!=FID or l["freeze_id"]!=FID:
        raise RuntimeError("frozen binding mismatch")
    import sklearn
    if platform.python_version()!=l["python_version"] or sklearn.__version__!=l["library_version"]:
        raise RuntimeError("learner runtime drift")
    return l


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--source-commit",required=True); a=ap.parse_args()
    spec=validate()
    a.output_dir.mkdir(parents=True,exist_ok=False)
    for name in ("datasets","provenance","models","semantic"): (a.output_dir/name).mkdir()
    l0,l1=datasets(); b0,b1=jsonl(l0),jsonl(l1)
    (a.output_dir/"datasets/L0_BASE.training.jsonl").write_bytes(b0); (a.output_dir/"datasets/L1_CORROBORATED.training.jsonl").write_bytes(b1)
    dh={"L0_BASE":h(b0),"L1_CORROBORATED":h(b1)}
    inv=deps(); ib=cj(inv)+b"\n"; (a.output_dir/"provenance/dependency_inventory.json").write_bytes(ib); ih=h(ib)
    if inv["python_version"]!=spec["python_version"] or inv["required_versions"]["scikit-learn"]!=spec["library_version"]: raise RuntimeError("dependency runtime drift")
    pre={"schema":1,"experiment_id":EID,"freeze_id":FID,"plan_id":PID,"authorization_id":AID,"source_commit":a.source_commit,"training_counts":{"TR0":12,"TR1":72,"TOTAL":84},"label_counts":{"HOLD":66,"ENTER_RECOVERY_GATE":18},"dataset_sha256":dh,"dependency_inventory_sha256":ih,"held_out_blocks_materialized":False,"fit_started":False}
    (a.output_dir/"provenance/prefit_binding.json").write_bytes(cj(pre)+b"\n")
    print("prefit_binding=PASS"); print(f"l0_dataset_sha256={dh['L0_BASE']}"); print(f"l1_dataset_sha256={dh['L1_CORROBORATED']}"); print(f"dependency_inventory_sha256={ih}")
    for k,v in inv["required_versions"].items(): print(f"{k.replace('-','_')}_version={v}")

    x0,y0=xy(l0); x1,y1=xy(l1)
    p0,p1=estimator(spec),estimator(spec); p0.fit(x0,y0); p1.fit(x1,y1)
    r0=[json.loads(x) for x in b0.decode().splitlines()]; r1=[json.loads(x) for x in b1.decode().splitlines()]
    ax0,ay0=xy(r0); ax1,ay1=xy(r1)
    a0,a1=estimator(spec),estimator(spec); a0.fit(ax0,ay0); a1.fit(ax1,ay1)
    semantic={}
    for policy,features,pm,am in (("L0_BASE",BASE_FEATURES,p0,a0),("L1_CORROBORATED",EXTENDED_FEATURES,p1,a1)):
        pb,ab=sem(pm,policy,tuple(features)),sem(am,policy,tuple(features))
        if pb!=ab: raise RuntimeError(f"audit refit mismatch: {policy}")
        sh=h(pb); semantic[policy]={"primary_sha256":sh,"audit_sha256":h(ab)}
        (a.output_dir/f"semantic/{policy}.primary.semantic.json").write_bytes(pb+b"\n"); (a.output_dir/f"semantic/{policy}.audit.semantic.json").write_bytes(ab+b"\n")

    import joblib
    ah={}
    for name,m in {"L0_BASE.primary":p0,"L0_BASE.audit":a0,"L1_CORROBORATED.primary":p1,"L1_CORROBORATED.audit":a1}.items():
        p=a.output_dir/f"models/{name}.joblib"; joblib.dump(m,p,compress=0,protocol=5); ah[name]=fhash(p)

    candidate={"schema":1,"experiment_id":EID,"freeze_id":FID,"plan_id":PID,"authorization_id":AID,"candidate_id":CID,"date":"2026-09-23","state":"MODEL_FREEZE_CANDIDATE__NOT_FROZEN__HELD_OUT_EVALUATION_PROHIBITED","source_training_commit":a.source_commit,"training":{"blocks":["TR0","TR1"],"counts":{"TR0":12,"TR1":72,"TOTAL":84},"label_counts":{"HOLD":66,"ENTER_RECOVERY_GATE":18},"dataset_sha256":dh,"dependency_inventory_sha256":ih,"runtime_versions":inv["required_versions"],"semantic_model_sha256":semantic,"runtime_artifact_sha256":ah,"primary_audit_semantic_identity":True},"provenance":{"freeze_manifest_blob_sha":blob(FREEZE),"frozen_learner_protocol_blob_sha":blob(LEARNER),"training_plan_blob_sha":blob(PLAN),"training_authorization_blob_sha":blob(AUTH),"qualifier_fault_model_blob_sha":blob(ROOT/"study7e/feasibility/qualifier_fault/qualifier_fault_model.py"),"frozen_fault_transformations_blob_sha":blob(ROOT/"study7e/configs/frozen_fault_transformations_001.json")},"gates":{"production_training_authorized":True,"production_models_trained":True,"production_models_frozen":False,"held_out_evaluation_executed":False,"canonical_execution_authorized":False,"canonical_results_generated":False,"pr_merge_authorized":False,"publication_or_result_claims_authorized":False},"next_gate":"separate explicit model-freeze review and authorization; E1/E2/C0 remain prohibited"}
    cb=cj(candidate)+b"\n"; cp=a.output_dir/"model_freeze_candidate_001.json"; cp.write_bytes(cb); ch=h(cb)
    record={"schema":1,"candidate_sha256":ch,"output_files":{str(p.relative_to(a.output_dir)):fhash(p) for p in sorted(a.output_dir.rglob("*")) if p.is_file()},"safety":candidate["gates"]}
    (a.output_dir/"training_execution_record.json").write_bytes(cj(record)+b"\n")
    print(f"l0_semantic_sha256={semantic['L0_BASE']['primary_sha256']}"); print(f"l1_semantic_sha256={semantic['L1_CORROBORATED']['primary_sha256']}")
    print(f"l0_primary_artifact_sha256={ah['L0_BASE.primary']}"); print(f"l1_primary_artifact_sha256={ah['L1_CORROBORATED.primary']}"); print(f"model_freeze_candidate_sha256={ch}")
    print("primary_audit_semantic_identity=true"); print("production_training_authorized=true"); print("production_models_trained=true"); print("production_models_frozen=false")
    print("held_out_evaluation_executed=false"); print("canonical_execution_authorized=false"); print("scientific_results_generated=false"); print("pr_merge_authorized=false"); print("publication_or_result_claims_authorized=false"); print("study7e_production_training=PASS")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
