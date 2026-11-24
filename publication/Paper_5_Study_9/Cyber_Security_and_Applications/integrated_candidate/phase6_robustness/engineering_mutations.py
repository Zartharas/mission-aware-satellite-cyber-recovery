"""Engineering-only mutation sensitivity on constructed NON-CANONICAL toy inputs.

Source replacements are applied in memory, never to frozen source or canonical fixtures.
No frozen case, complete state enumeration, or original selector is executed.
"""
from pathlib import Path
from copy import deepcopy
import evaluator as ev
import state_model as sm
import reference_oracle as ro
from candidate_worker import handle
from evidence_writer import preserve_attempt
from tempfile import TemporaryDirectory
HERE=Path(__file__).resolve().parent
def mutate(module,old,new):
    source=(HERE/module).read_text()
    if source.count(old)!=1:raise ValueError("MUTATION_MARKER_DRIFT:"+module)
    scope={"__name__":"engineering_mutant"}
    exec(compile(source.replace(old,new),module,"exec"),scope)
    return scope
def check_mutant(module,old,new,probe,expected):
    scope=mutate(module,old,new)
    try: actual=probe(scope)
    except Exception as exc:actual=("ERROR",type(exc).__name__)
    if actual==expected:raise AssertionError("MUTATION_SURVIVED:"+old)
def run():
    # Distinct toy decision values, not the frozen input specifications.
    ctx=dict(subject="TOY",decision_id="D",decision_time_s=11,epoch=2,clock="CLOCK",snapshot_id="T",source_id="ISSUER",evidence_id="E")
    def field(name,meaning,authority,domain="BOOLEAN_LITERAL",**overrides):
        return dict(name=name,meaning=meaning,authority=authority,visibility="OPERATIONAL_NATIVE",subject_scope=ctx["subject"],decision_scope=ctx["decision_id"],clock_scope=ctx["clock"],domain=domain,source_scope=ctx["source_id"],evidence_scope=ctx["evidence_id"],native_field=True,**overrides)
    def payload(target,schema,values):
        return dict(target=target,schema=schema,record=dict(context=ctx,values=values),requested_context=ctx)
    def sig(x):return (x["classification"],x["admission"],x["value"])
    proxy=payload("signature_valid",[field("check","CRC result only","UNQUALIFIED_PROXY")],{"check":True})
    false=payload("source_trusted",[field("member",ev.DIRECT["source_trusted"][1],"TRUST_REGISTRY")],{"member":False})
    offline=payload("security_signal",[field("truth","offline only","EXPERIMENTER")],{"truth":False});offline["schema"][0]["visibility"]="OFFLINE_GROUND_TRUTH_ONLY"
    rule=ev.RULES["fresh"][2]; sch=[field(k,m,"TIME_AUTHORITY",domain) for k,(m,domain) in rule.items()]
    wrong=payload("fresh",deepcopy(sch),{"issued_at_s":8,"decision_time_s":11,"valid_for_s":5});wrong["schema"][0]["clock_scope"]="OTHER_CLOCK"
    zero=payload("fresh",deepcopy(sch),{"issued_at_s":11,"decision_time_s":11,"valid_for_s":0})
    probes=[
      ("CRC",proxy,("AMBIGUOUS","UNKNOWN",None),'return result("AMBIGUOUS","UNKNOWN",None,"NON_EQUIVALENT_PROXY")\n    if all','return result("DIRECT","ADMIT",True,"QUALIFIED_DIRECT")\n    if all'),
      ("FALSE",false,("DIRECT","ADMIT",False),'if key not in values or values[key] is None:','if key not in values or not values[key]:'),
      ("OFFLINE",offline,("ABSENT","UNKNOWN",None),'return result("ABSENT","UNKNOWN",None,"OFFLINE_TRUTH_NOT_OPERATIONAL","OFFLINE_GROUND_TRUTH_ONLY")','return result("DIRECT","ADMIT",False,"QUALIFIED_DIRECT")'),
      ("CLOCK",wrong,("AMBIGUOUS","UNKNOWN",None),'if differences:\n                reason=','if differences - {"clock_scope"}:\n                reason='),
      ("DURATION",zero,("DERIVABLE_BY_PREDECLARED_RULE","REJECT_INVALID",None),'integer(values[k],1 if k=="valid_for_s" else 0)','integer(values[k],0)')
    ]
    for name,p,expected,old,new in probes:
        assert sig(ev.evaluate(p))==expected,name
        check_mutant("evaluator.py",old,new,lambda s:sig(s["evaluate"](p)),expected)
    assert handle([proxy,false])["error"] is None
    # Non-study ledger: different times, sequences, false criterion and unrelated key.
    # Scope string is the declared artificial architecture; the toy ledger values differ.
    c=dict(ctx,subject="SYN_SUBJECT_A",epoch=7,decision_time_s=77)
    criteria=sorted(ev.CRITERIA)
    def claim(key,n,value=True,src="TOY_A",sig=True):
        return dict(claim_id=f"TOY_{src}_{n}",source_id=src,subject_id=c["subject"],key=key,epoch=7,sequence=n,value=value,issued_at_s=70,valid_for_s=20,signature_valid=sig,source_trusted=True,sequence_valid=True)
    rows=[claim(k,20+i,i!=0) for i,k in enumerate(criteria)]
    def ledger(rows):return dict(kind="LEDGER_DIAGNOSTIC",inventory_complete=True,scope="ALL_KEYS_SUBJECT_A_EPOCH_7_DECISION_1",known_trust_sources=["TOY_A","TOY_B"],claims=rows,contact_available=True,expected_epoch=7,decision_time_s=77,minimum_sequence_by_source_epoch=0)
    def mq(o):return o["diagnostics"]["M_present"],o["diagnostics"]["Q_satisfied"]
    d=ledger(rows)
    assert mq(ev.ledger(d,c))==(True,False)
    assert ev.ledger(d,c)["diagnostics"]==ro.ledger_reference(d,c)
    check_mutant("evaluator.py","[m,q,c,*agg,contact]","[q,q,c,*agg,contact]",lambda s:mq(s["ledger"](d,c)),(True,False))
    unrelated=ledger(rows+[claim("toy_mode",51),claim("toy_mode",52,False,"TOY_B")])
    assert ev.ledger(unrelated,c)["diagnostics"]["contradictory"] is True
    assert ev.ledger(unrelated,c)["diagnostics"]==ro.ledger_reference(unrelated,c)
    check_mutant("evaluator.py","c=bool(conflicts)","c=bool(conflicts&CRITERIA)",lambda s:s["ledger"](unrelated,c)["diagnostics"]["contradictory"],True)
    rejected=ledger(rows+[claim("toy_extra",60,sig=False)])
    assert ev.ledger(rejected,c)["diagnostics"]["signature_valid"] is False
    assert ev.ledger(rejected,c)["diagnostics"]==ro.ledger_reference(rejected,c)
    check_mutant("evaluator.py","flags.append(row_flags)","if all(row_flags): flags.append(row_flags)",lambda s:s["ledger"](rejected,c)["diagnostics"]["signature_valid"],False)
    assert sm.endpoint([],[],(None,None))["min_size"] is None
    check_mutant("state_model.py",'"min_size":None,"minima":None','"min_size":0,"minima":[]',lambda s:s["endpoint"]([],[],(None,None))["min_size"],None)
    # One hand-specified non-study Boolean policy probe, no frozen selector invocation.
    x=(True,True,True,True,False,True,False,False)
    expected="PRESERVE_LIMITED_OPERATION"
    assert ro.policy(ro.POLICIES[2],x)==expected
    check_mutant("reference_oracle.py","if p==POLICIES[2]: return hold if not qualified else restrict if g else preserve","if p==POLICIES[2]: return hold if not qualified else restrict",lambda s:s["policy"](ro.POLICIES[2],x),expected)
    def nested(fn):
        try:fn([0,1],[0],[2]);return "ACCEPT"
        except ValueError:return "REJECT"
    assert nested(sm.assert_nested)=="REJECT"
    check_mutant("state_model.py","if not f0 or not f1 or not f2 or not set(f2)<=set(f1)<=set(f0):","if False:",lambda s:nested(s["assert_nested"]),"REJECT")
    with TemporaryDirectory() as tmp:
        out=Path(tmp)/"toy_attempt"
        def fail(progress):
            progress["toy"]=17
            raise ValueError("TOY_FAILURE")
        assert preserve_attempt(out,{"toy":True},fail)=="FAIL"
        assert (out/"report.json").exists() and (out/"SHA256_MANIFEST.json").exists()
        try: preserve_attempt(out,{"toy":True},fail)
        except FileExistsError:pass
        else:raise AssertionError("ATTEMPT_OVERWRITE")
    print("11_ENGINEERING_MUTATIONS_DETECTED_NO_CANONICAL_EXECUTION")
if __name__=="__main__":run()
