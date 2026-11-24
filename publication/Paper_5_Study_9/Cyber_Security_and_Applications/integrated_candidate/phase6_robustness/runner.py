"""Prepared scientific implementation. Entry point hard-blocked pending separate author execution authorization."""
from __future__ import annotations
import copy, json
from collections import Counter
from itertools import product
from pathlib import Path
import evaluator
import reference_oracle
import state_model
from integrity import read_verified, verify_all
FIELDS=tuple(["signature_valid","source_trusted","fresh","epoch_valid","contradictory","minimum_evidence_complete","security_signal","authorization_available"])
POLICIES=reference_oracle.POLICIES
def baseline(payload, mode):
    target=payload["target"]; vals=payload["record"]["values"]
    fields=[s for s in payload["schema"] if s["native_field"] and s["name"]==target]
    if mode=="always_unknown" or len(fields)!=1:return ("ABSENT","UNKNOWN",None)
    if target not in vals:return ("DIRECT","UNKNOWN_MISSING",None)
    return ("DIRECT","ADMIT",vals[target]) if type(vals[target]) is bool else ("DIRECT","REJECT_INVALID",None)
def signature(out):return (out["classification"],out["admission"],out["value"])
def metrics(pairs):
    counts=Counter()
    confusion=Counter()
    for actual,expected in pairs:
        a,b=actual,expected; confusion[(b[0],a[0])]+=1
        counts["cases"]+=1; counts["exact_class"]+=a[0]==b[0]; counts["exact_admission_value"]+=a[1:]==b[1:]
        counts["false_admission"]+=a[1]=="ADMIT" and b[1]!="ADMIT"
        counts["false_rejection"]+=a[1]!="ADMIT" and b[1]=="ADMIT"
        counts["wrong_admitted_value"]+=a[1]==b[1]=="ADMIT" and a[2] is not b[2]
        counts["known_false_to_unknown"]+=b[2] is False and a[2] is None
        counts["unknown_to_false"]+=b[2] is None and a[2] is False
    return {"counts":dict(counts),"expected_admissible":sum(b[1]=="ADMIT" for _,b in pairs),"expected_nonadmissible":sum(b[1]!="ADMIT" for _,b in pairs),"classification_confusion":[[x,y,n] for (x,y),n in sorted(confusion.items())]}
def perturb(payload,spec):
    x=copy.deepcopy(payload); pid=spec["id"]
    if pid.startswith("P-RENAME-"):
        name=x["schema"][0]["name"]; new="neutral_"+pid.rsplit("-",1)[1]; x["schema"][0]["name"]=new; x["record"]["values"][new]=x["record"]["values"].pop(name)
        return [x]
    if pid.startswith("P-ORDER-"):
        s=copy.deepcopy(x["schema"][0]); s.update(name="unrelated_test_counter",meaning="Unrelated fixture bookkeeping; no recovery semantics.",authority="NONE",domain="INTEGER")
        x["schema"].append(s); x["record"]["values"][s["name"]]=17
        y=copy.deepcopy(x);y["schema"].reverse();y["record"]["values"]=dict(reversed(list(y["record"]["values"].items())))
        return [x,y]
    if pid=="P-OFFLINE-LABEL":
        x["record"]["values"]["attack_label"]=not x["record"]["values"]["attack_label"];return [x]
    raise ValueError("UNKNOWN_PERTURBATION")
def prepare_analysis():
    # Called only by a future separately approved launcher; no executable main path.
    verify_all()
    inputs=json.loads(read_verified("runtime_inputs.json"))["cases"]
    outcomes=[]
    # Candidate pure function receives payload only. No expected outcomes loaded yet.
    for case in inputs:
        outcomes.append({"routing_key":case["routing_key"],"actual":evaluator.evaluate(case["payload"])})
    refs=json.loads(read_verified("reference_expectations.json"))["rows"]
    routes=json.loads(read_verified("routing_manifest.json"))
    if len(inputs)!=72 or [x["routing_key"] for x in outcomes]!=[x["routing_key"] for x in refs]:raise ValueError("ROUTING_DRIFT")
    rows=[]; by_family={}; failures=[]
    for case,observed,ref,route in zip(inputs,outcomes,refs,routes["cases"]):
        if not case["routing_key"]==route["routing_key"]==ref["routing_key"]:raise ValueError("ROUTE_MISMATCH")
        a=observed["actual"]; e=ref["expectation"]; payload=case["payload"]
        row={**route,"actual":a,"expected":e,"match":a==e}
        if a!=e:failures.append(route["case_id"])
        if payload["target"] is None:
            row["ledger_oracle"]=reference_oracle.ledger_reference(payload["diagnostic"],payload["requested_context"])
            if row["ledger_oracle"]!=e["diagnostics"]:failures.append(route["case_id"]+":LEDGER_ORACLE")
        else:
            row["baselines"]={k:baseline(payload,k) for k in ("always_unknown","name_only")}
            for k in ("candidate","always_unknown","name_only"):
                v=signature(a) if k=="candidate" else row["baselines"][k]
                for family in (route["family"],"ALL_MAPPING"):
                    by_family.setdefault((family,k),[]).append((v,signature(e)))
        rows.append(row)
    lookup={r["case_id"]:(x["payload"],a["actual"]) for r,x,a in zip(routes["cases"],inputs,outcomes)}
    metamorphic=[]
    for spec in routes["perturbations"]:
        payload,original=lookup[spec["base_case"]]
        observed=[signature(evaluator.evaluate(v)) for v in perturb(payload,spec)]
        ok=all(v==signature(original) for v in observed)
        metamorphic.append({"id":spec["id"],"match":ok,"observed":observed})
        if not ok:failures.append(spec["id"])
    return {"rows":rows,"metrics":[{"family":family,"method":k,**metrics(v)} for (family,k),v in sorted(by_family.items())],"metamorphic":metamorphic,"failures":failures}
def logical_analysis():
    # Never call with incomplete observations at the actual selector.
    verify_all()
    import selector_pinned as sel
    models=state_model.domains()
    labels={}
    for x in models["F0"]:
        for policy in POLICIES:
            a=sel.select_action(sel.Study2Policy(policy),sel.ObservationSummary(**dict(zip(FIELDS,x)))).value
            b=reference_oracle.policy(policy,x)
            if a!=b:raise ValueError("BOOLEAN_ORACLE_MISMATCH")
            labels[(policy,x)]=a
    primary=(None,)*8; records=[]
    for o in (primary,*[x for x in product((None,False,True),repeat=8) if x!=primary]):
        slices={k:state_model.compatible(v,o) for k,v in models.items()}
        for policy in POLICIES:
            previous=None
            for k,states in slices.items():
                actions=[labels[(policy,x)] for x in states]
                e=state_model.endpoint(states,actions,o)
                minima=reference_oracle.conflict_minima(states,actions,tuple(i for i,v in enumerate(o) if v is None))
                if e["minima"]!=minima:raise ValueError("SIDECAR_ORACLE_MISMATCH")
                if previous is not None and states:
                    if previous["actions"] is None or not set(e["actions"])<=set(previous["actions"]) or e["min_size"]>previous["min_size"]:raise ValueError("NESTING_INVARIANT_FAIL")
                previous=e
                records.append({"model":k,"policy":policy,"observation":o,**e})
    primary_rows=[z for z in records if z["model"]=="F0" and z["observation"]==primary]
    if [z["action_count"] for z in primary_rows]!=[2,2,3,3] or [z["min_size"] for z in primary_rows]!=[6,7,7,8]:raise ValueError("ARCHIVED_F0_MISMATCH")
    return records
if __name__=="__main__":
    raise SystemExit("PHASE6_4_EXECUTION_NOT_AUTHORIZED: no experiment launched")
