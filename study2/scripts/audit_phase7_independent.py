#!/usr/bin/env python3
"""Independent arithmetic audit for frozen Study-2 Phase-7 results.

This script intentionally does not import or invoke analyze_phase7.py.
"""
import argparse,csv,hashlib,json,math,statistics,zipfile
from collections import Counter,defaultdict
from pathlib import Path
Z=1.959963984540054; TAU=240.0
RAW_SHA="195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
RES={"cell_summary.csv":"6995dc69d2652791feee86e5409565b4c87c7a9b3e041de319d240fa30c7f27c","primary_contrasts.csv":"a3d4fd395d88ffe83fa39ded3584120ed0cd1e45f184b5fbd3d37ab49cdd2a52","secondary_contrasts.csv":"9a37c31853c0bfccecd6f66f7701e65dbbbf9e9f9a239479afb770d4bdbe58af","terminal_state_summary.csv":"efbc26efe7c6edc2ef760654bec2f0a3accfcf898fff6bdcc40392b076b3cce7"}
EP={"unsafe_permissive_response_rate":("adjudication_only","unsafe_permissive"),"false_conservative_response_rate":("adjudication_only","false_conservative"),"evidence_qualified_trusted_recovery":("evidence_qualified_trusted_recovery",),"residual_unauthorized_state":("adjudication_only","residual_unauthorized_state"),"legitimate_command_rejection_rate":("adjudication_only","legitimate_command_rejected")}
TIME="time_to_evidence_qualified_trusted_recovery"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with open(p,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def nested(r,path):
    for k in path:r=r[k]
    return r
def bv(r,e):return int(nested(r,EP[e]))
def rt(r):return float(r["time_to_evidence_qualified_trusted_recovery_s"]) if r["evidence_qualified_trusted_recovery"] else TAU
def ct(r):return float(r["time_to_containment_s"]) if r["time_to_containment_s"] is not None else TAU
def val(r,e):return float(bv(r,e)) if e in EP else rt(r)
def stats(v,b=None):
    m=statistics.fmean(v);s=statistics.stdev(v) if len(v)>1 else 0.;q=s/math.sqrt(len(v));lo=m-Z*q;hi=m+Z*q
    if b:lo=max(b[0],lo);hi=min(b[1],hi)
    return m,s,lo,hi
def wilson(k,n):
    p=k/n;z2=Z*Z;d=1+z2/n;c=(p+z2/(2*n))/d;h=Z*math.sqrt((p*(1-p)+z2/(4*n))/n)/d;lo=max(0.,c-h);hi=min(1.,c+h)
    return (0. if k==0 else lo,1. if k==n else hi)
def normalp(v):
    m=statistics.fmean(v);s=statistics.stdev(v) if len(v)>1 else 0.
    if s==0:return 1. if m==0 else 0.
    return math.erfc(abs(m)/(s/math.sqrt(len(v)))/math.sqrt(2))
def mcn(a,b):
    x=sum(u==1 and v==0 for u,v in zip(a,b));y=sum(u==0 and v==1 for u,v in zip(a,b));n=x+y
    if n==0:return 1.
    k=min(x,y);return min(1.,2*sum(math.comb(n,j) for j in range(k+1))/(2**n))
def holm(p):
    o=sorted(range(len(p)),key=lambda i:(p[i],i));a=[0.]*len(p);run=0.;m=len(p)
    for rank,i in enumerate(o):run=max(run,min(1.,(m-rank)*p[i]));a[i]=run
    return a
def eq(a,b):return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)
def slope(y):return sum((x-1.5)*(v-statistics.fmean(y)) for x,v in zip((0.,1.,2.,3.),y))/5.
def audit(zp,rd):
    if sha(zp)!=RAW_SHA:raise SystemExit("phase6 zip hash mismatch")
    for n,h in RES.items():
        if sha(rd/n)!=h:raise SystemExit(f"result hash mismatch: {n}")
    with zipfile.ZipFile(zp) as z:o=[json.loads(x) for x in z.read("observations.jsonl").splitlines() if x.strip()]
    if len(o)!=3872 or any(r["attempt_status"]!="VALID" or r["oracle_was_selector_input"] is not False or float(r["censor_horizon_s"])!=TAU for r in o):raise SystemExit("population integrity mismatch")
    g=defaultdict(list)
    for r in o:g[r["cell_id"]].append(r)
    for q in g.values():q.sort(key=lambda r:r["seed"])
    def pair(a,b):
        x={r["seed"]:r for r in g[a]};y={r["seed"]:r for r in g[b]};s=sorted(set(x)&set(y))
        if len(s)!=len(x) or len(s)!=len(y):raise SystemExit("pair mismatch")
        return [x[i] for i in s],[y[i] for i in s]
    C=rows(rd/"cell_summary.csv");P=rows(rd/"primary_contrasts.csv");S=rows(rd/"secondary_contrasts.csv");T=rows(rd/"terminal_state_summary.csv")
    if tuple(map(len,(C,P,S,T)))!=(85,162,432,85):raise SystemExit("row-count mismatch")
    mis=[]
    for r in C:
        q=g[r["cell_id"]];n=len(q);ck={"n":n}
        for e in EP:
            k=sum(bv(x,e) for x in q);lo,hi=wilson(k,n);ck.update({e+"_count":k,e+"_rate":k/n,e+"_ci95_low":lo,e+"_ci95_high":hi})
        m,s,lo,hi=stats([rt(x) for x in q]);ck.update(recovery_rmst_240_s=m,recovery_rmst_sd_s=s,recovery_rmst_ci95_low_s=lo,recovery_rmst_ci95_high_s=hi)
        m,s,lo,hi=stats([ct(x) for x in q]);ck.update(containment_rmst_240_s=m,containment_rmst_sd_s=s,containment_rmst_ci95_low_s=lo,containment_rmst_ci95_high_s=hi)
        for e in ("ground_spacecraft_state_divergence","response_selection_stability"):
            k=sum(int(x[e]) for x in q);lo,hi=wilson(k,n);ck.update({e+"_count":k,e+"_rate":k/n,e+"_ci95_low":lo,e+"_ci95_high":hi})
        ce=sum(x["time_to_containment_s"] is not None for x in q);re=sum(x["evidence_qualified_trusted_recovery"] for x in q);ck.update(containment_events=ce,containment_right_censored=n-ce,recovery_events=re,recovery_right_censored=n-re)
        for k,v in ck.items():
            if not (int(r[k])==v if isinstance(v,int) else eq(r[k],v)):mis.append("cell:"+r["cell_id"]+":"+k)
    for r in P:
        a,b=pair(r["first_cell"],r["reference_cell"]);d=[val(x,r["endpoint"])-val(y,r["endpoint"]) for x,y in zip(a,b)];m,s,lo,hi=stats(d,(-1.,1.) if r["endpoint"]!=TIME else None)
        for k,v in (("paired_n",len(d)),("effect_first_minus_reference",m),("paired_sd",s),("ci95_low",lo),("ci95_high",hi)):
            if not (int(r[k])==v if k=="paired_n" else eq(r[k],v)):mis.append("primary:"+r["contrast"]+":"+r["endpoint"]+":"+k)
    pv=[]
    for r in S:
        e=r["endpoint"];typ=r["endpoint_type"]
        if typ in ("binary_risk_difference","rmst_240_s_mean_difference"):
            a,b=pair(r["first_cell"],r["reference_cell"]);av=[val(x,e) for x in a];bv0=[val(x,e) for x in b];d=[x-y for x,y in zip(av,bv0)];p=mcn(list(map(int,av)),list(map(int,bv0))) if typ=="binary_risk_difference" else normalp(d)
        elif typ=="per_contact_step_slope":
            mm=[{x["seed"]:x for x in g[c]} for c in r["first_cell"].split("|")];ss=sorted(set.intersection(*(set(x) for x in mm)));d=[slope([val(x[i],e) for x in mm]) for i in ss];p=normalp(d)
        else:
            f1,f0=r["first_cell"].split("|");r1,r0=r["reference_cell"].split("|");mm=[{x["seed"]:x for x in g[c]} for c in (f1,f0,r1,r0)];ss=sorted(set.intersection(*(set(x) for x in mm)));d=[(val(mm[0][i],e)-val(mm[1][i],e))-(val(mm[2][i],e)-val(mm[3][i],e)) for i in ss];p=normalp(d)
        m,s,lo,hi=stats(d,(-1.,1.) if typ=="binary_risk_difference" else None);pv.append(p)
        for k,v in (("paired_n",len(d)),("effect_first_minus_reference",m),("paired_sd",s),("ci95_low",lo),("ci95_high",hi),("raw_p_value",p)):
            if not (int(r[k])==v if k=="paired_n" else eq(r[k],v)):mis.append("secondary:"+r["contrast"]+":"+e+":"+k)
    buckets=defaultdict(list)
    for i,r in enumerate(S):buckets[(r["family"],r["endpoint"])].append(i)
    for ix in buckets.values():
        for i,a in zip(ix,holm([pv[j] for j in ix])):
            if not eq(S[i]["holm_adjusted_p_value"],a) or ((S[i]["holm_reject_alpha_0_05"].lower()=="true")!=(a<=.05)):mis.append("holm:"+S[i]["contrast"]+":"+S[i]["endpoint"])
    tt=defaultdict(list)
    for r in T:tt[r["cell_id"]].append(r)
    for c,q in g.items():
        ex=Counter(x["recovery_terminal_state"] for x in q);ac={x["terminal_state"]:x for x in tt[c]}
        if set(ex)!=set(ac):mis.append("terminal:"+c);continue
        for st,k in ex.items():
            if int(ac[st]["count"])!=k or int(ac[st]["n"])!=len(q) or not eq(ac[st]["proportion"],k/len(q)):mis.append("terminal:"+c+":"+st)
    return {"schema":1,"status":"PASS" if not mis else "FAIL","classification":"STUDY2_PHASE7_INDEPENDENT_ARITHMETIC_REPRODUCTION_AUDIT","valid_observations_recomputed":len(o),"cells_recomputed":len(C),"primary_rows_recomputed":len(P),"secondary_rows_recomputed":len(S),"holm_rows_recomputed":len(S),"terminal_state_cells_recomputed":len(T),"mismatch_count":len(mis),"mismatches":mis,"new_campaign_execution":False,"study1_reanalysis":False,"audit_scope":"Independent standard-library arithmetic recomputation; primary analyzer is neither imported nor invoked."}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--phase6-zip",type=Path,required=True);p.add_argument("--phase7-dir",type=Path,required=True);p.add_argument("--output",type=Path);a=p.parse_args();r=audit(a.phase6_zip,a.phase7_dir);text=json.dumps(r,indent=2,sort_keys=True)+"\n";print(text,end="");a.output and a.output.write_text(text,encoding="utf-8");raise SystemExit(0 if r["status"]=="PASS" else 1)
