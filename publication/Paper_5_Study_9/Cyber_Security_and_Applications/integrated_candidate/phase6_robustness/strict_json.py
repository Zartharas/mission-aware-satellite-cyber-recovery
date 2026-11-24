"""Literal JSON comparison; distinguish Boolean from integer and reject duplicate keys."""
import json
def equal(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b
def loads(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError("DUPLICATE_JSON_KEY")
            out[k]=v
        return out
    def bad(s):raise ValueError("NONFINITE_JSON_NUMBER")
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
