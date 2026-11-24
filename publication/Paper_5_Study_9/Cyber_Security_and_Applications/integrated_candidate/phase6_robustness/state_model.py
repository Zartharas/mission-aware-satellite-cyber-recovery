"""Conditional logical models; no computation on import."""
from itertools import product, combinations
def assert_nested(f0,f1,f2):
    if not f0 or not f1 or not f2 or not set(f2)<=set(f1)<=set(f0):raise ValueError("MODEL_NESTING_FAIL")
def domains():
    f0=list(product((False,True),repeat=8))
    f1=[x for x in f0 if not x[5] or not x[4]]
    f2=[x for x in f1 if not x[5] or all(x[:4])]
    if [len(x) for x in (f0,f1,f2)]!=[256,192,132]: raise ValueError("MODEL_INVARIANT_FAIL")
    assert_nested(f0,f1,f2)
    return dict(zip(("F0","F1","F2"),(f0,f1,f2)))
def compatible(states,o):
    if len(o)!=8 or any(x is not None and type(x) is not bool for x in o): raise ValueError("INVALID_PARTIAL_STATE")
    return [x for x in states if all(v is None or v==x[i] for i,v in enumerate(o))]
def partition_minima(states,actions,unknown):
    if not states:return None
    for n in range(len(unknown)+1):
        good=[]
        for subset in combinations(unknown,n):
            partition={}; valid=True
            for x,a in zip(states,actions):
                key=tuple(x[i] for i in subset)
                if key in partition and partition[key]!=a: valid=False; break
                partition[key]=a
            if valid:good.append(subset)
        if good:return good
    raise ValueError("NO_SUFFICIENT_SUBSET")
def endpoint(states,actions,o):
    if not states:return {"status":"INCONSISTENT_OBSERVATION","completion_count":0,"actions":None,"action_count":None,"min_size":None,"minima":None}
    minima=partition_minima(states,actions,tuple(i for i,v in enumerate(o) if v is None))
    return {"status":"EVALUABLE_LOGICAL_SLICE","completion_count":len(states),"actions":sorted(set(actions)),"action_count":len(set(actions)),"min_size":len(minima[0]),"minima":minima}
