"""Isolated candidate worker; only supplied JSON payloads, never gold or routing IDs.

Invoked by the separately authorized offline runner. No canonical invocation in Phase 6.3.
"""
import json, sys
from strict_json import loads
from evaluator import evaluate
def handle(payloads):
    if type(payloads) is not list or len(payloads)>128: raise ValueError("INVALID_BATCH")
    results=[]
    for index,payload in enumerate(payloads):
        try: results.append(evaluate(payload))
        except Exception as exc:
            return {"results":results,"error":{"index":index,"type":type(exc).__name__,"reason":str(exc)[:300]}}
    return {"results":results,"error":None}
if __name__=="__main__":
    from network_isolation import verify_isolation
    verify_isolation(worker=True)
    raw=sys.stdin.buffer.read(2_000_001)
    if len(raw)>2_000_000: raise SystemExit("INPUT_SIZE_LIMIT")
    print(json.dumps(handle(loads(raw)),sort_keys=True,allow_nan=False))
