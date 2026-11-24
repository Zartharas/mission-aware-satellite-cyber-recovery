"""Controlled-contract evaluator. Pure functions; no filesystem, case IDs or reference imports."""
from __future__ import annotations

DIRECT = {
    "signature_valid": ("VERIFIER", "Known-key cryptographic verification outcome for the evidence bundle at the decision; synthetic premise, not actual crypto verification."),
    "source_trusted": ("TRUST_REGISTRY", "Membership of the evidence source in the current verifier trusted-source set."),
    "fresh": ("TIME_AUTHORITY", "Evidence issue time and positive validity interval contain the decision instant, evaluated under the same authoritative clock."),
    "epoch_valid": ("EPOCH_AUTHORITY", "Claimed evidence epoch equals the expected evidence epoch for the same subject at the decision."),
    "contradictory": ("LEDGER_AUTHORITY", "Competing values among latest accepted current claims for identical subject, key and epoch in the complete declared scope."),
    "minimum_evidence_complete": ("LEDGER_AUTHORITY", "All ten required keys present among accepted current nonconflicting values; presence, not required-value satisfaction; complete declared scope."),
    "security_signal": ("GUARD_AUTHORITY", "Native operational security/anomaly guard result available at the decision, not retrospective truth."),
    "authorization_available": ("COMMAND_AUTHORITY", "Availability of a mission-authorized recovery command/contact path at the decision."),
}
RULES = {
    "fresh": ("D_FRESH", "TIME_AUTHORITY", {
        "issued_at_s": ("Evidence issue time for the stated evidence and decision, integer seconds.", "NONNEGATIVE_INTEGER"),
        "decision_time_s": ("Authoritative decision time, same clock.", "NONNEGATIVE_INTEGER"),
        "valid_for_s": ("Positive validity duration for the same evidence.", "POSITIVE_INTEGER")}),
    "epoch_valid": ("D_EPOCH", "EPOCH_AUTHORITY", {
        "claimed_epoch": ("Claimed evidence epoch for same subject at decision.", "NONNEGATIVE_INTEGER"),
        "expected_epoch": ("Authoritative expected evidence epoch for same subject at decision.", "NONNEGATIVE_INTEGER")}),
}
CRITERIA = frozenset(["approved_version","integrity_measurement_valid","authorization_valid","measured_state_current","authorized_command_path_restored","ground_spacecraft_state_agreed","required_telemetry_restored","health_checks_passed","no_residual_unauthorized_state","recovery_manifest_complete"])
CONTEXT = {"subject", "decision_id", "decision_time_s", "epoch", "clock", "snapshot_id", "source_id", "evidence_id"}
SCHEMA = {"name", "meaning", "authority", "visibility", "subject_scope", "decision_scope", "clock_scope", "domain", "source_scope", "evidence_scope", "native_field"}
CLAIM = {"claim_id", "source_id", "subject_id", "key", "epoch", "sequence", "value", "issued_at_s", "valid_for_s", "signature_valid", "source_trusted", "sequence_valid"}
LEDGER = {"kind", "inventory_complete", "scope", "known_trust_sources", "claims", "contact_available", "expected_epoch", "decision_time_s", "minimum_sequence_by_source_epoch"}
DIAG = ("M_present", "Q_satisfied", "contradictory", "signature_valid", "source_trusted", "fresh", "epoch_valid", "authorization_available")
def exact(obj, keys):
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError("INVALID_OBJECT_KEYS")
def integer(v, minimum=0):
    return type(v) is int and v >= minimum
def context_ok(c):
    exact(c, CONTEXT)
    if not all(type(c[k]) is str and c[k] for k in CONTEXT - {"decision_time_s","epoch"}) or not all(integer(c[k]) for k in ("decision_time_s","epoch")):
        raise ValueError("INVALID_CONTEXT")
def result(cls, status, value, reason, role="OPERATIONAL_NATIVE", rule=None, release="NOT_ASSESSED"):
    return dict(classification=cls, visibility=role, admission=status, value=value, reason=reason, rule_id=rule, release_domain=release)
def scope_diff(s, c):
    pairs = (("subject_scope","subject"),("decision_scope","decision_id"),("clock_scope","clock"),("source_scope","source_id"),("evidence_scope","evidence_id"))
    return {a for a,b in pairs if s[a] != c[b]}
def mapping(target, schema, record, requested_context):
    if target not in DIRECT or type(schema) is not list or len(schema)>16:
        raise ValueError("INVALID_MAPPING_INPUT")
    context_ok(requested_context)
    exact(record, {"context","values"}); context_ok(record["context"])
    values=record["values"]
    if type(values) is not dict: raise ValueError("INVALID_VALUES")
    for s in schema:
        exact(s, SCHEMA)
        if type(s["native_field"]) is not bool or not all(type(s[k]) is str and s[k] for k in SCHEMA-{"native_field"}):
            raise ValueError("INVALID_SCHEMA")
    names=[s["name"] for s in schema]
    if len(names)!=len(set(names)) or not set(values)<=set(names):
        raise ValueError("UNKNOWN_OR_DUPLICATE_FIELD")
    native=[s for s in schema if s["native_field"] and s["visibility"]=="OPERATIONAL_NATIVE"]
    if not native:
        roles={s["visibility"] for s in schema}
        if "OFFLINE_GROUND_TRUTH_ONLY" in roles:
            return result("ABSENT","UNKNOWN",None,"OFFLINE_TRUTH_NOT_OPERATIONAL","OFFLINE_GROUND_TRUTH_ONLY")
        if "DOCUMENTATION_ONLY" in roles:
            return result("ABSENT","UNKNOWN",None,"DOCUMENTATION_ONLY_NOT_NATIVE","DOCUMENTATION_ONLY")
        return result("ABSENT","UNKNOWN",None,"NO_RELEVANT_OPERATIONAL_FIELD",None)
    authority,meaning=DIRECT[target]
    ds=[s for s in native if (s["authority"],s["meaning"],s["domain"])==(authority,meaning,"BOOLEAN_LITERAL")]
    if len(ds)>1: raise ValueError("MULTIPLE_DIRECT_CANDIDATES_OUTSIDE_DESIGN")
    if ds:
        s=ds[0]
        if scope_diff(s,requested_context):
            return result("AMBIGUOUS","UNKNOWN",None,"SCHEMA_SCOPE_MISMATCH")
        if record["context"]!=requested_context:
            return result("DIRECT","UNKNOWN",None,"STALE_DECISION_WITNESS")
        key=s["name"]
        if key not in values or values[key] is None:
            return result("DIRECT","UNKNOWN_MISSING",None,"MISSING_ROW_VALUE",release="MISSINGNESS_HOLD")
        if type(values[key]) is not bool:
            return result("DIRECT","REJECT_INVALID",None,"INVALID_BOOLEAN_LITERAL",release="DOMAIN_VIOLATION_HOLD")
        return result("DIRECT","ADMIT",values[key],"QUALIFIED_DIRECT")
    if target in RULES:
        rule,auth,required=RULES[target]; available={s["name"]:s for s in native}
        if set(required)<=available.keys() and all((available[k]["meaning"],available[k]["domain"],available[k]["authority"])==(*required[k],auth) for k in required):
            differences=set().union(*(scope_diff(available[k],requested_context) for k in required))
            if differences:
                reason="RULE_CLOCK_MISMATCH" if "clock_scope" in differences else "RULE_SUBJECT_MISMATCH" if "subject_scope" in differences else "RULE_SCOPE_MISMATCH"
                return result("AMBIGUOUS","UNKNOWN",None,reason)
            cls="DERIVABLE_BY_PREDECLARED_RULE"
            if record["context"]!=requested_context:
                return result(cls,"UNKNOWN",None,"STALE_DECISION_WITNESS",rule=rule)
            if any(k not in values or values[k] is None for k in required):
                return result(cls,"UNKNOWN_MISSING",None,"MISSING_RULE_INPUT",rule=rule,release="MISSINGNESS_HOLD")
            if not all(integer(values[k],1 if k=="valid_for_s" else 0) for k in required):
                return result(cls,"REJECT_INVALID",None,"INVALID_RULE_DOMAIN",rule=rule,release="DOMAIN_VIOLATION_HOLD")
            if rule=="D_FRESH":
                if values["decision_time_s"]!=requested_context["decision_time_s"]: return result(cls,"UNKNOWN",None,"RULE_CONTEXT_MISMATCH",rule=rule)
                value=values["issued_at_s"]<=values["decision_time_s"]<=values["issued_at_s"]+values["valid_for_s"]
            else:
                if values["expected_epoch"]!=requested_context["epoch"]: return result(cls,"UNKNOWN",None,"RULE_CONTEXT_MISMATCH",rule=rule)
                value=values["claimed_epoch"]==values["expected_epoch"]
            return result(cls,"ADMIT",value,"QUALIFIED_DERIVATION",rule=rule)
    # Bounded synthetic proxy contracts: related proxy authority, never a target-name proof.
    if any(s["authority"]=="UNQUALIFIED_PROXY" for s in native):
        return result("AMBIGUOUS","UNKNOWN",None,"NON_EQUIVALENT_PROXY")
    if all(s["authority"]=="NONE" for s in native):
        return result("ABSENT","UNKNOWN",None,"NO_RELEVANT_OPERATIONAL_FIELD",None)
    return result("AMBIGUOUS","UNKNOWN",None,"NON_EQUIVALENT_PROXY")
def diag(status, reason, values):
    return {**result("NOT_A_MAPPING_ENDPOINT",status,None,reason,None), "diagnostics":dict(zip(DIAG,values))}
def ledger(d, ctx):
    context_ok(ctx); exact(d,LEDGER)
    if d["kind"]!="LEDGER_DIAGNOSTIC" or d["scope"]!="ALL_KEYS_SUBJECT_A_EPOCH_7_DECISION_1" or type(d["inventory_complete"]) is not bool or type(d["contact_available"]) is not bool or d["decision_time_s"]!=ctx["decision_time_s"] or d["expected_epoch"]!=ctx["epoch"] or not integer(d["minimum_sequence_by_source_epoch"]):
        raise ValueError("INVALID_LEDGER_CONTEXT")
    rows=d["claims"]; trust=d["known_trust_sources"]
    if type(rows) is not list or len(rows)>64 or type(trust) is not list or not all(type(t) is str and t for t in trust): raise ValueError("INVALID_LEDGER_DOMAIN")
    seen=set(); ids=set(); latest={}; flags=[]
    for c in rows:
        exact(c,CLAIM)
        if any(type(c[k]) is not bool for k in ("value","signature_valid","source_trusted","sequence_valid")) or any(not integer(c[k],1 if k=="valid_for_s" else 0) for k in ("epoch","sequence","issued_at_s","valid_for_s")) or any(type(c[k]) is not str or not c[k] for k in ("claim_id","source_id","subject_id","key")) or c["subject_id"]!=ctx["subject"] or c["source_trusted"]!=(c["source_id"] in trust):
            raise ValueError("INVALID_CLAIM")
        identity=(c["source_id"],c["epoch"],c["sequence"])
        if identity in seen or c["claim_id"] in ids:
            return diag("REJECT_INVALID","DUPLICATE_SOURCE_EPOCH_SEQUENCE",[None]*8)
        seen.add(identity); ids.add(c["claim_id"])
        row_flags=(c["signature_valid"],c["source_trusted"],c["issued_at_s"]<=d["decision_time_s"]<=c["issued_at_s"]+c["valid_for_s"],c["epoch"]==d["expected_epoch"])
        flags.append(row_flags)
        if all(row_flags) and c["sequence_valid"] and c["sequence"]>d["minimum_sequence_by_source_epoch"]:
            key=(c["source_id"],c["subject_id"],c["key"],c["epoch"])
            if key not in latest or c["sequence"]>latest[key]["sequence"]: latest[key]=c
    contact=d["contact_available"]
    if not d["inventory_complete"]: return diag("UNKNOWN","INCOMPLETE_LEDGER_INVENTORY",[None]*7+[contact])
    grouped={}
    for c in latest.values(): grouped.setdefault((c["subject_id"],c["key"],c["epoch"]),set()).add(c["value"])
    conflicts={key[1] for key,vs in grouped.items() if len(vs)>1}
    current={key[1]:next(iter(vs)) for key,vs in grouped.items() if key[1] not in conflicts}
    m=CRITERIA<=current.keys(); q=m and all(current[k] is True for k in CRITERIA); c=bool(conflicts)
    agg=[bool(flags) and all(x[i] for x in flags) for i in range(4)]
    rejected=any(not all(fl) or not rr["sequence_valid"] or rr["sequence"]<=d["minimum_sequence_by_source_epoch"] for fl,rr in zip(flags,rows))
    reason=("REQUIRED_KEY_CONFLICT" if conflicts&CRITERIA else "UNRELATED_KEY_CONFLICT" if c else "REJECTED_EXTRA_ROW_AGGREGATE_INVALID" if rejected else "CLOSED_LEDGER_REQUIRED_KEY_MISSING" if not m else "PRESENCE_NOT_SATISFACTION" if not q else "ACCEPTED_AUTHORIZATION_NOT_LIVE_CONTACT" if not contact else "QUALIFIED_LEDGER")
    return diag("DIAGNOSTIC",reason,[m,q,c,*agg,contact])
def evaluate(payload):
    if payload.get("target") is None:
        exact(payload,{"target","schema","record","requested_context","diagnostic"})
        return ledger(payload["diagnostic"],payload["requested_context"])
    exact(payload,{"target","schema","record","requested_context"})
    return mapping(**payload)
