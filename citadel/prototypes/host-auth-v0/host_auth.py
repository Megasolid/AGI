#!/usr/bin/env python3
"""Host-auth/private-recall prototype (isolated; no live runtime integration).

Implements the critical gates from Kilo's 27-case review: fail-closed revocation, runtime+MCP gating through one
authorize(), empty/no-count denied search, hard private/shared separation, replay/expiry/revocation, audit chain.
"""
import hashlib
import json
import secrets
import threading
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

SKEW = 60


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def keypair():
    k = Ed25519PrivateKey.generate()
    return k, k.public_key()


def raw_pub(pub):
    return pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def b64(b):
    import base64
    return base64.b64encode(b).decode()


def unb64(s):
    import base64
    return base64.b64decode(s)


def sign(key, obj):
    return b64(key.sign(canon(obj).encode()))


def verify(pub, obj, sig):
    try:
        pub.verify(unb64(sig), canon(obj).encode())
        return True
    except Exception:
        return False


class Store:
    def __init__(self, master_priv, master_pub):
        self.master_priv = master_priv
        self.master_pub = master_pub
        self.hosts = {}
        self.grants = {}
        self.revocations = set()
        self.revocation_available = True
        self.nonces = {}
        self.lock = threading.Lock()
        self.private = []
        self.shared = []
        self.audit = []

    def audit_append(self, rec):
        rec = dict(rec)
        rec["seq"] = len(self.audit) + 1
        rec["prev_hash"] = self.audit[-1]["hash"] if self.audit else None
        rec["hash"] = sha(canon({k: v for k, v in rec.items() if k != "hash"}).encode())
        self.audit.append(rec)


def add_host(store, host_id, instance, pub, expires=None, revoked=False):
    rec = {"host_id": host_id, "host_instance_id": instance, "public_key": b64(raw_pub(pub)),
           "expires_at": int(expires if expires is not None else time.time() + 3600), "revoked": revoked}
    rec["master_sig"] = sign(store.master_priv, {k: v for k, v in rec.items() if k != "master_sig"})
    store.hosts[instance] = rec
    return rec


def add_grant(store, instance, organism="ENTL-1", resource_class="memory.private", ops=("recall",),
              visibility=("private",), expires=None, revoked=False):
    if not instance or not resource_class or not ops or not visibility:
        raise ValueError("empty grant")
    if any(v in ("*", "any", "") for v in tuple(ops) + tuple(visibility)):
        raise ValueError("wildcard/ambiguous grant")
    g = {"grant_id": "g-" + secrets.token_hex(6), "host_instance_id": instance, "organism_id": organism,
         "resource_class": resource_class, "permitted_operations": list(ops),
         "allowed_visibility": list(visibility), "expires_at": int(expires if expires is not None else time.time() + 3600),
         "revoked": revoked}
    g["master_sig"] = sign(store.master_priv, {k: v for k, v in g.items() if k != "master_sig"})
    store.grants[instance] = g
    return g


def request(priv, instance, method, args, nonce=None, ts=None):
    payload = {"host_instance_id": instance, "method": method, "args_digest": sha(canon(args).encode()),
               "nonce": nonce or secrets.token_hex(16), "ts": int(ts if ts is not None else time.time())}
    return {**payload, "proof": sign(priv, payload)}


def deny(store, reason, host=None, request_id=None):
    store.audit_append({"decision": "deny", "reason": reason, "host_instance_id": host,
                        "request_id": request_id})
    return {"allowed": False, "reason": reason, "items": [], "count": None, "rank": None}


def authorize(store, req, resource_class, op):
    if not store.revocation_available:
        return deny(store, "revocation-state-unavailable", (req or {}).get("host_instance_id"),
                    (req or {}).get("nonce"))
    if not req:
        return deny(store, "missing-host-authorization")
    inst = req.get("host_instance_id")
    host = store.hosts.get(inst)
    if not host:
        return deny(store, "unknown-host", inst, req.get("nonce"))
    if not verify(store.master_pub, {k: v for k, v in host.items() if k != "master_sig"}, host["master_sig"]):
        return deny(store, "bad-host-authorization-signature", inst, req.get("nonce"))
    if host["revoked"] or host["expires_at"] <= time.time() or inst in store.revocations:
        return deny(store, "revoked-or-expired-host", inst, req.get("nonce"))
    pub = Ed25519PublicKey.from_public_bytes(unb64(host["public_key"]))
    payload = {k: req[k] for k in ("host_instance_id", "method", "args_digest", "nonce", "ts")}
    if not verify(pub, payload, req.get("proof", "")):
        return deny(store, "bad-request-proof", inst, req.get("nonce"))
    if abs(int(time.time()) - int(req.get("ts", 0))) > SKEW:
        return deny(store, "clock-skew", inst, req.get("nonce"))
    with store.lock:
        if req.get("nonce") in store.nonces:
            return deny(store, "replay", inst, req.get("nonce"))
        store.nonces[req["nonce"]] = time.time()
    grant = store.grants.get(inst)
    if not grant:
        return deny(store, "missing-grant", inst, req.get("nonce"))
    if not verify(store.master_pub, {k: v for k, v in grant.items() if k != "master_sig"}, grant["master_sig"]):
        return deny(store, "bad-grant-signature", inst, req.get("nonce"))
    if grant["revoked"] or grant["expires_at"] <= time.time():
        return deny(store, "revoked-or-expired-grant", inst, req.get("nonce"))
    if resource_class not in (grant["resource_class"], grant["resource_class"].rsplit(".", 1)[0]):
        return deny(store, "resource-class-denied", inst, req.get("nonce"))
    if op not in grant["permitted_operations"]:
        return deny(store, "operation-denied", inst, req.get("nonce"))
    return {"allowed": True, "host_instance_id": inst, "grant": grant, "audit_id": len(store.audit) + 1}


def recall(store, req, resource_class="memory.private", op="recall", items=None):
    items = store.private if items is None else items
    auth = authorize(store, req, resource_class, op)
    if not auth["allowed"]:
        return auth
    vis = set(auth["grant"]["allowed_visibility"])
    out = []
    for it in items:
        if it.get("visibility", "private") not in vis:
            continue
        if it["visibility"] == "private" and it.get("origin_host_instance") != auth["host_instance_id"]:
            continue
        if it["visibility"] == "shared_authorized":
            if it.get("approved_recipient") != auth.get("host_instance_id"):
                continue
            if "shared_authorized" not in vis:
                continue
        out.append({k: it[k] for k in ("id", "kind", "visibility", "memory_class", "trust", "body")})
    store.audit_append({"decision": "allow", "op": op, "host_instance_id": auth["host_instance_id"],
                        "request_id": req.get("nonce"), "returned": len(out)})
    return {"allowed": True, "items": out, "count": len(out), "audit_id": len(store.audit)}


def export_metadata(store, req):
    auth = authorize(store, req, "memory.metadata", "export")
    if not auth["allowed"]:
        return auth
    allow = ("id", "kind", "visibility", "memory_class", "trust", "source", "ts")
    rows = [{k: x.get(k) for k in allow} for x in store.private + store.shared]
    return {"allowed": True, "items": rows, "count": len(rows), "private_bodies": False, "audit_id": len(store.audit)}


def shared_recall(store, req, recipient):
    auth = authorize(store, req, "memory.shared", "recall")
    if not auth["allowed"]:
        return auth
    out = [x for x in store.shared if x.get("approved_recipient") == recipient and recipient == auth["host_instance_id"]]
    return {"allowed": True, "items": out, "count": len(out)}


def adapter_export(store, req):
    # adapters never get private bodies; metadata-only shared/public
    res = shared_recall(store, req, req.get("host_instance_id") if req else None)
    if not res.get("allowed"):
        return res
    return {"allowed": True, "items": [{k: x[k] for k in ("id", "visibility", "body")}
                                       for x in res["items"] if x.get("visibility") == "shared_authorized"]}
