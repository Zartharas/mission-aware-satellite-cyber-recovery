"""Independent reference algorithms. No evaluator or frozen selector imports."""
from itertools import groupby, combinations
KEYS = frozenset(["approved_version","integrity_measurement_valid","authorization_valid","measured_state_current","authorized_command_path_restored","ground_spacecraft_state_agreed","required_telemetry_restored","health_checks_passed","no_residual_unauthorized_state","recovery_manifest_complete"])
POLICIES = tuple(["S2_B0_FAIL_CLOSED","S2_B1_FAIL_OPERATIONAL","S2_B2_RISK_THRESHOLD","S2_S1_EVIDENCE_AWARE"])
DIAGNOSTICS=("M_present","Q_satisfied","contradictory","signature_valid","source_trusted","fresh","epoch_valid","authorization_available")
def policy(p,x):
    if p not in POLICIES or len(x)!=8 or any(type(v) is not bool for v in x): raise ValueError("INVALID_POLICY_OBSERVATION")
    s,t,f,e,c,m,g,a=x
    qualified=s and t and f and e and not c and m
    hold="HOLD_AND_REQUIRE_EVIDENCE"; preserve="PRESERVE_LIMITED_OPERATION"; restrict="RESTRICT_AND_REQUEST_AUTHORIZATION"; proceed="PROCEED_TO_RECOVERY_GATE"
    if p==POLICIES[0]: return (restrict,proceed)[qualified]
    if p==POLICIES[1]: return (preserve,restrict)[qualified and g]
    if p==POLICIES[2]: return hold if not qualified else restrict if g else preserve
    return hold if not qualified else restrict if g and not a else proceed
def ledger_reference(d,ctx):
    # Independent grouping path over the frozen valid-schema inputs.
    rows=d["claims"]; ids=[r["claim_id"] for r in rows]; seqs=[(r["source_id"],r["epoch"],r["sequence"]) for r in rows]
    if len(ids)!=len(set(ids)) or len(seqs)!=len(set(seqs)):
        return dict(zip(DIAGNOSTICS,[None]*8))
    if not d["inventory_complete"]:
        return dict(zip(DIAGNOSTICS,[None]*7+[d["contact_available"]]))
    def fresh(r): return 0<=ctx["decision_time_s"]-r["issued_at_s"]<=r["valid_for_s"]
    def epoch(r): return r["epoch"]==ctx["epoch"]
    def valid(r): return r["signature_valid"] and r["source_id"] in d["known_trust_sources"] and fresh(r) and epoch(r) and r["sequence_valid"] and r["sequence"]>d["minimum_sequence_by_source_epoch"]
    def issuer(r): return (r["source_id"],r["subject_id"],r["key"],r["epoch"])
    accepted=sorted(filter(valid,rows),key=lambda r:(issuer(r),r["sequence"]))
    latest=[list(group)[-1] for _,group in groupby(accepted,key=issuer)]
    values={k:{r["value"] for r in latest if r["key"]==k} for k in {r["key"] for r in latest}}
    consistent={k for k,v in values.items() if len(v)==1}
    aggregates=[bool(rows) and not any(not fn(r) for r in rows) for fn in (lambda r:r["signature_valid"],lambda r:r["source_id"] in d["known_trust_sources"],fresh,epoch)]
    return dict(zip(DIAGNOSTICS,[KEYS<=consistent,all(values.get(k)=={True} for k in KEYS),any(len(v)>1 for v in values.values()),*aggregates,d["contact_available"]]))
def conflict_minima(states, actions, unknown):
    if not states: return None
    conflicts={frozenset(i for i in unknown if a[i]!=b[i]) for (a,aa),(b,ba) in combinations(zip(states,actions),2) if aa!=ba}
    if frozenset() in conflicts: raise ValueError("INCONSISTENT_ACTIONS")
    # Remove redundant supersets; hitting all minimal conflict sets is equivalent.
    minimal=[c for c in sorted(conflicts,key=lambda c:(len(c),tuple(sorted(c)))) if not any(k<c for k in conflicts)]
    for n in range(len(unknown)+1):
        good=[s for s in combinations(unknown,n) if all(set(s)&c for c in minimal)]
        if good:return good
    raise ValueError("NO_SUFFICIENT_SUBSET")

def domain_member(model,x):
    if len(x)!=8 or any(type(v) is not bool for v in x):raise ValueError("INVALID_DOMAIN_STATE")
    if model not in ("F0","F1","F2"):raise ValueError("INVALID_MODEL")
    if model=="F0" or x[5] is False:return True
    if x[4]:return False
    return model=="F1" or not any(v is False for v in x[:4])
def logical_domains():
    # Integer decoding independent of candidate Cartesian product.
    states=[tuple(bool(n & (1 << (7-i))) for i in range(8)) for n in range(256)]
    return {k:{x for x in states if domain_member(k,x)} for k in ("F0","F1","F2")}
