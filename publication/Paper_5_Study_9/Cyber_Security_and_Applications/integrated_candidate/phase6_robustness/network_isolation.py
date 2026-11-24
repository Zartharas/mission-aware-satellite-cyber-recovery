"""Linux-only isolation observations. No packets sent or configuration changed."""
import errno, fcntl, ipaddress, os, socket, struct, sys
from pathlib import Path

def validate_network(interfaces,ipv4_routes,ipv6_routes):
    names={x["name"] for x in interfaces}
    if len(names)!=len(interfaces) or "lo" not in names:
        raise ValueError("LOOPBACK_MISSING_OR_DUPLICATE_INTERFACE")
    for x in interfaces:
        name=x["name"]; flags=x["flags"]
        if name=="lo":
            if not flags&1 or not flags&8:raise ValueError("LOOPBACK_NOT_UP")
            if any(not ipaddress.ip_address(a).is_loopback for a in x["addresses"]):
                raise ValueError("NON_LOOPBACK_ADDRESS_ON_LO")
        else:
            if flags&1:raise ValueError("NON_LOOPBACK_INTERFACE_UP:"+name)
            if x["addresses"]:raise ValueError("NON_LOOPBACK_ADDRESS_ASSIGNED:"+name)
    for routes in (ipv4_routes,ipv6_routes):
        for row in routes:
            if row["interface"] not in names:raise ValueError("ROUTE_INTERFACE_UNKNOWN")
            if row["interface"]!="lo" and not row["flags"]&0x200:
                raise ValueError("NON_LOOPBACK_ROUTE:"+row["interface"])

def observe_network():
    if not sys.platform.startswith("linux"):raise ValueError("LINUX_PROBE_REQUIRED")
    # Enumerate actual interfaces rather than sysfs attributes such as bonding_masters.
    entries=[]
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
        for _,name in sorted(socket.if_nameindex(),key=lambda x:x[1]):
            encoded=name.encode("ascii")
            if len(encoded)>15:raise ValueError("INVALID_INTERFACE_NAME")
            request=struct.pack("256s",encoded)
            flags=struct.unpack_from("H",fcntl.ioctl(s.fileno(),0x8913,request),16)[0]
            addresses=[]
            try:
                addr=fcntl.ioctl(s.fileno(),0x8915,request)
            except OSError as exc:
                if exc.errno!=errno.EADDRNOTAVAIL:raise
            else:
                addresses.append(socket.inet_ntoa(addr[20:24]))
            entries.append({"name":name,"flags":flags,"addresses":addresses})
    by_name={x["name"]:x for x in entries}
    p=Path("/proc/net/if_inet6")
    if p.exists():
        for line in p.read_text().splitlines():
            cols=line.split()
            if len(cols)!=6 or cols[5] not in by_name:raise ValueError("INVALID_IPV6_ADDRESS_RECORD")
            by_name[cols[5]]["addresses"].append(str(ipaddress.IPv6Address(int(cols[0],16))))
    v4=[]
    for line in Path("/proc/net/route").read_text().splitlines()[1:]:
        cols=line.split()
        if len(cols)!=11:raise ValueError("INVALID_IPV4_ROUTE_RECORD")
        v4.append({"interface":cols[0],"destination":cols[1],"mask":cols[7],"flags":int(cols[3],16)})
    v6=[]
    p6=Path("/proc/net/ipv6_route")
    if p6.exists():
        for line in p6.read_text().splitlines():
            cols=line.split()
            if len(cols)!=10:raise ValueError("INVALID_IPV6_ROUTE_RECORD")
            v6.append({"interface":cols[9],"destination":cols[0],"prefix":int(cols[1],16),"flags":int(cols[8],16)})
    evidence={"interfaces":entries,"ipv4_routes":v4,"ipv6_routes":v6,"ipv6_address_table_present":p.exists(),"ipv6_route_table_present":p6.exists()}
    try:validate_network(entries,v4,v6)
    except ValueError as exc:
        raise ValueError(str(exc)+":"+repr(evidence)) from exc
    return evidence

def verify_isolation(worker=False):
    if os.getuid()!=65534 or os.geteuid()!=65534:raise ValueError("UNEXPECTED_UID")
    if Path("/var/run/docker.sock").exists() or Path("/run/docker.sock").exists():raise ValueError("DOCKER_SOCKET_VISIBLE")
    for name in ("reference_expectations.json","runtime_inputs.json","routing_manifest.json"):
        if (Path("/app")/name).exists():raise ValueError("CANONICAL_INPUT_OR_REFERENCE_VISIBLE")
    status=dict(line.split(":",1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    if status["NoNewPrivs"].strip()!="1" or any(int(status[k].strip(),16)!=0 for k in ("CapEff","CapPrm","CapBnd")):
        raise ValueError("CAPABILITY_OR_NO_NEW_PRIVILEGES_FAILURE")
    mounts={}
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        cols=line.split()
        if len(cols)<7:raise ValueError("INVALID_MOUNTINFO")
        mounts[cols[4]]=cols[5].split(",")
    if "ro" not in mounts.get("/",[]):raise ValueError("ROOT_MOUNT_NOT_READONLY")
    if worker:
        if "ro" not in mounts.get("/app",[]):raise ValueError("WORKER_MOUNT_NOT_READONLY")
        if set(os.listdir("/app"))!={"candidate_worker.py","evaluator.py","strict_json.py","network_isolation.py"}:
            raise ValueError("UNEXPECTED_WORKER_MOUNT_CONTENT")
    return {"uid":os.getuid(),"python":sys.version,"readonly":True,"no_new_privileges":True,"capabilities_dropped":True,"worker_mount_verified":worker,**observe_network()}
